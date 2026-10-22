# Robot Design: How the Robot Gets and Runs Orders

This document explains how the delivery robot (Elephant Robotics LIMO with an M5 arm) connects to the system, receives instructions, and carries them out.

## Overview

The robot is a separate Python program that runs continuously. It never connects to the database. Instead it asks the web server for work over HTTPS and proves who it is with an API key.

```
Robot (Python)                          Hostinger server
     |                                        |
     |-- GET /api/robot/?action=next-order -->|
     |   Header: X-API-Key: <key>             |-- 1. Compare key to $robotApiKey in config.php
     |                                        |-- 2. Wrong key? 401 and stop
     |                                        |-- 3. Right key? claim a Pending order in MySQL
     |<-- JSON: order, items, locations ------|
     |                                        |
     | (drives, picks up items, delivers)     |
     |                                        |
     |-- POST /api/robot/?action=update-status|
     |   Header: X-API-Key: <key>             |
     |   Body: {"orderID": 4, "status": "Delivered"}
     |<-- JSON: {"ok": true} -----------------|
```

Only the server's PHP code touches MySQL. The database password never leaves the server.

## The API key

The API key is a long random secret that only the server and the robot know. It is free, and you create it yourself.

**Generate one:**
```
php -r "echo bin2hex(random_bytes(32));"
```

**Where it lives:**

| Place | Holds | Committed to Git? |
|---|---|---|
| Server `includes/config.php` | `$robotApiKey` plus the DB password | No (gitignored) |
| Robot `robot_config.py` | API URL plus the same key | No (gitignored) |

The robot only **sends** the key. The comparison happens on the server, in `requireRobotKey()`:

```php
function requireRobotKey() {
    global $robotApiKey;
    $sent = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';
    if (!hash_equals($robotApiKey, $sent)) {
        http_response_code(401);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'unauthorized']);
        exit;
    }
}
```

It is called once at the top of `api/robot/index.php`, so every robot route is protected. If the key leaks, generate a new one and update `config.php` and the robot. Nothing else changes.

Keep the key out of anything a browser can download (such as `robot.js`), and use HTTPS so the key is not sent in plain text.

## How the robot gets instructions

The `next-order` response contains everything needed for one order. The server joins the tables, so the robot receives a single JSON document:

```json
{
  "order": {
    "orderID": 4,
    "items": [
      {"productID": 1, "Location": "box1", "instruction": "FRAGILE"},
      {"productID": 3, "Location": "box2", "instruction": "NORMAL"}
    ]
  }
}
```

The database says **what** to do (a keyword) and the robot's code decides **how** to do it. The robot never runs SQL. It compares values the server handed to it.

```
MySQL:   Items.Location = "box1"
   |     (the server's next-order endpoint reads it)
   v
JSON:    {"Location": "box1", ...}
   |     (the robot receives it)
   v
Robot:   if location == "box1": run the box1 movement code
```

### Keyword to action table

```python
LOCATIONS = {
    "box1": drive_to_box1,
    "box2": drive_to_box2,
}

def handle_item(item):
    move = LOCATIONS.get(item["Location"])
    if move is None:
        raise ValueError(f"Unknown location: {item['Location']}")
    move()                 # drive to the box
    arm_pick()             # pick up the item
    drive_to_dropoff()     # bring it back
```

An if/elif chain does the same job, but the dictionary lets you add a new location with one function and one line. Unknown keywords raise an error so the order is marked `Failed` instead of the robot guessing.

### Database conventions

- Store exact, fixed keywords in `Items.Location` (lowercase, no spaces: `box1`, `box2`). `"Box 1"` and `"box1"` would be different keys.
- `Instructions.details` is free text for people. Add a short code column for the robot:

```sql
ALTER TABLE Instructions ADD COLUMN code VARCHAR(20) NOT NULL DEFAULT 'NORMAL';
UPDATE Instructions SET code = 'FRAGILE'    WHERE instructionID = 1;
UPDATE Instructions SET code = 'TWO_HANDED' WHERE instructionID = 4;
```

The `next-order` endpoint returns `code` as the `instruction` field.

## Order status flow

```
Pending -> Claimed -> InProgress -> Delivered
                  \-> Failed
Pending -> Cancelled
```

- **Claiming** uses one atomic `UPDATE ... WHERE status = 'Pending' ... LIMIT 1`, so two robots (or two overlapping polls) can never take the same order.
- This needs two new columns on `Order`: `claimedBy VARCHAR(45)` and `updatedAt TIMESTAMP`. The timestamp lets the server reset stale `Claimed` or `InProgress` orders back to `Pending` if a robot loses power mid-delivery.
- `update-status` should refuse invalid jumps, such as marking a `Pending` order `Delivered`.

## One program, several files

The robot runs one continuous program, but the code is split into modules so each part can be tested alone:

```
robot/
├── main.py            <- the loop: poll, handle order, report status
├── api_client.py      <- talks to the server (next-order, update-status)
├── movement.py        <- LIMO driving: drive_to_box1(), drive_to_dropoff()
├── arm.py             <- M5 arm: pick(), release(), home()
├── vision.py          <- object detection (from detect_obj_img.py)
├── locations.py       <- the LOCATIONS table
└── robot_config.py    <- API URL + API key (gitignored)
```

### The main loop

```python
from api_client import get_next_order, set_status
from locations import handle_item
import time

while True:
    order = get_next_order()
    if order:
        set_status(order["orderID"], "InProgress")
        try:
            for item in order["items"]:
                handle_item(item)
            set_status(order["orderID"], "Delivered")
        except Exception as e:
            print("Order failed:", e)
            set_status(order["orderID"], "Failed")
    time.sleep(3)
```

```
loop forever:
    ask the server for a Pending order
    none?    -> sleep 3 seconds, ask again
    got one? -> do the work, report status, go back to asking
```

The robot handles one order at a time because the work happens inside the loop body. It does not ask for another order until the current one finishes, so threads are not needed.

### api_client.py

```python
import requests
from robot_config import API, API_KEY

HEADERS = {"X-API-Key": API_KEY}

def get_next_order():
    try:
        r = requests.get(f"{API}/robot/?action=next-order", headers=HEADERS, timeout=10)
        return r.json().get("order") if r.ok else None
    except requests.RequestException as e:
        print("Server unreachable, retrying:", e)   # keep running if wifi drops
        return None

def set_status(order_id, status):
    try:
        requests.post(f"{API}/robot/?action=update-status",
                      headers=HEADERS,
                      json={"orderID": order_id, "status": status}, timeout=10)
    except requests.RequestException as e:
        print("Could not report status:", e)
```

```python
# robot_config.py (gitignored)
API = "https://rds.etowndb.com/api"
API_KEY = "paste-the-same-64-char-string"
```

Keep the trailing slash in `/api/robot/?action=...`. Without it a redirect can turn a POST into a GET.

## Writing the movement code

The functions behind `drive_to_box1()`, `arm_pick()` and similar are the hardware-specific part. Check the exact function names and parameters against the Elephant Robotics documentation before relying on them. In general:

- **Arm (M5 myCobot):** usually controlled with the `pymycobot` library using joint angles or coordinates plus gripper open and close commands. A common technique is to move the arm to each pose you need (above the box, down, gripped, raised), record those angles, and use them as constants in your functions.
- **LIMO (driving):**
  1. *Open-loop moves* (drive forward for N seconds, turn 90 degrees). Simple and good for a demo with a fixed, flat layout, but it drifts and is not very repeatable.
  2. *ROS navigation* with a saved map. More setup, but far more reliable. `"box1"` would map to a stored position and heading, and only the body of `drive_to_box1()` changes.

For a class demo, open-loop moves with fixed distances are usually enough.

## Running it

- **During development:** run `python3 main.py` in a terminal and stop it with Ctrl+C.
- **Automatically at boot:** a systemd service starts the script when the robot powers on and restarts it if it crashes. Save as `/etc/systemd/system/delivery-robot.service`, adjusting the user and path to your setup (and source the ROS environment if you use it):

```ini
[Unit]
Description=Delivery robot
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/robot/main.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable with `sudo systemctl enable --now delivery-robot`.

## Safety and reliability checklist

- Wrap every server call in try/except so a dropped connection retries instead of crashing the loop.
- On any exception, stop the motors and park the arm before marking the order `Failed`.
- Use Python's `logging` module to write to a file so you can see which step failed.
- Test each movement function alone on the robot before connecting it to the server.
- Start with one box and one full cycle (order on the website, drive to `box1`, pick, drop off, status `Delivered`) before adding more locations.
- Keep a physical way to cut power.

## Still to build

1. The `api/robot/index.php` endpoints: `next-order` (with the SQL join and atomic claim) and `update-status`.
2. The `claimedBy` and `updatedAt` columns on `Order`, and the `code` column on `Instructions`.
3. The robot modules above, with the hardware functions filled in from the Elephant Robotics documentation.
4. A cleanup job that resets stale `Claimed` and `InProgress` orders.

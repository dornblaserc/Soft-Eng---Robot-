"""
robot.py - base file for testing robot <-> server communication.

All movement functions just print for now. Once the order flow works end to end,
replace the bodies of the placeholder functions with real LIMO / M5 arm code.

Setup:
    pip install requests
    edit robot_config.py (API URL + API key)

Run:
    python robot.py          # runs forever (Ctrl+C to stop)
    python robot.py --once   # handles one pass and exits (good for first tests)
"""
import sys
import time

import requests

from robot_config import API, API_KEY, POLL_SECONDS

HEADERS = {"X-API-Key": API_KEY}
TIMEOUT = 10  # seconds


# ---------------------------------------------------------------------------
# Hardware placeholders: replace the prints with real movement code later
# ---------------------------------------------------------------------------
def drive_to_box1():
    print("    [robot] driving to box1")


def drive_to_box2():
    print("    [robot] driving to box2")


def arm_pick():
    print("    [robot] arm: picking up item")


def drive_to_dropoff():
    print("    [robot] driving to drop-off point")


# Items.Location in the database must match these keys exactly
LOCATIONS = {
    "box1": drive_to_box1,
    "box2": drive_to_box2,
}


def handle_item(item):
    location = item["Location"]
    move = LOCATIONS.get(location)
    if move is None:
        # Fail loudly instead of guessing, so a typo in the DB can't cause odd movement
        raise ValueError("Unknown location: %r" % location)

    print("  Item %s at %s (note: %s)" % (item["productID"], location, item.get("instruction")))
    move()
    arm_pick()
    drive_to_dropoff()


# ---------------------------------------------------------------------------
# Server communication
# ---------------------------------------------------------------------------
def get_next_order():
    """Returns an order dict, or None if there is nothing to do or the call failed."""
    try:
        r = requests.get(API + "/robot/?action=next-order", headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        print("Server unreachable, will retry:", e)
        return None

    if r.status_code == 401:
        print("401 unauthorized: the API key does not match the server's config.php")
        return None
    if not r.ok:
        print("Unexpected response %s: %s" % (r.status_code, r.text[:200]))
        return None

    return r.json().get("order")


def set_status(order_id, status):
    """status must be 'Delivered' or 'Failed'. Returns True if the server accepted it."""
    try:
        r = requests.post(API + "/robot/?action=update-status", headers=HEADERS,
                          json={"orderID": order_id, "status": status}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print("Could not report status (%s): %s" % (status, e))
        return False

    if not r.ok:
        print("Server rejected status update: %s %s" % (r.status_code, r.text[:200]))
        return False
    return True


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def run_once():
    order = get_next_order()
    if order is None:
        print("No order waiting.")
        return

    # The server already marked this order InProgress when it handed it to us
    print("Got order #%s with %d item(s)" % (order["orderID"], len(order["items"])))

    try:
        for item in order["items"]:
            handle_item(item)
    except Exception as e:
        print("Order #%s FAILED: %s" % (order["orderID"], e))
        # TODO: stop motors and park the arm here before reporting
        set_status(order["orderID"], "Failed")
        return

    if set_status(order["orderID"], "Delivered"):
        print("Order #%s delivered." % order["orderID"])


def main():
    once = "--once" in sys.argv
    print("Robot started. Server: %s" % API)

    while True:
        run_once()
        if once:
            break
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")

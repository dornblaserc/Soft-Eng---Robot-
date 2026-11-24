# Etown Robotic Delivery Systems

A website-controlled delivery robot built for our Software Engineering course at Elizabethtown College.

A customer logs into our website and orders an item. An AgileX LIMO robot with an Elephant Robotics myCobot 280 M5 arm picks up the order, drives to the bin the item is stored in, grabs it with the arm, brings it back, and reports the order as delivered. The customer sees the order status change on their profile page.

```
 Customer ──> Website (PHP) ──> MySQL database <── Robot API (PHP) <── LIMO robot + arm (Python / ROS)
              places an order    order: Pending     robot asks for work   drives, picks, delivers
                                 order: Delivered   robot reports done
```

## How it works

1. **Order:** A logged-in user picks an item on `order.php`. The website saves a new order in the database with status `Pending`.
2. **Hand-off:** The robot program asks the server for work every 3 seconds through a small HTTPS API protected by an API key. The server gives it the oldest `Pending` order and marks it `InProgress`. The robot never connects to the database directly.
3. **Delivery:** Each item has a `Location` (`box1`, `box2`, `box3`). The robot drives to that bin, picks up the item with the arm, drives back, and places it in its carrying box.
4. **Report:** The robot tells the server the order is `Delivered` (or `Failed` if something went wrong), and the website shows the update.

See [docs/WEBSITE_OVERVIEW.md](docs/WEBSITE_OVERVIEW.md) for the full walkthrough, including the database design and the robot API.

## Hardware

| Part | Role |
|---|---|
| AgileX LIMO | Mobile base; runs Ubuntu with ROS Noetic (ROS 1) |
| Elephant Robotics myCobot 280 M5 | 6-axis arm with adaptive gripper, connected over USB (`/dev/ttyACM0`) |
| Orbbec DaBai camera | Depth camera on the LIMO, used for ball detection (in progress) |

## Repository layout

```
api/robot/          Robot API: the robot fetches orders and reports status here
includes/           Shared PHP: config, database wrapper, repository classes
website/            Website pages, styles, and images
src/run_robot/      The robot program that runs on the LIMO (start here)
src/Tests/          Small scripts for testing the arm and driving on their own
src/Tests/in_progress/  Vision-guided pickup work that is not yet part of the main program
src/Legacy/         Example scripts from the manufacturer, kept for reference
docs/               Design documents, ERDs, requirements, and user stories
```

## Documentation

| Document | What's in it |
|---|---|
| [docs/WEBSITE_OVERVIEW.md](docs/WEBSITE_OVERVIEW.md) | Website pages, database design, robot API, and how they connect |
| [docs/ROBOT_WORKFLOW.md](docs/ROBOT_WORKFLOW.md) | Original design plan for how the robot gets and runs orders |
| [docs/LIMO_AND_ARM_BASICS.md](docs/LIMO_AND_ARM_BASICS.md) | Starter commands for the LIMO (ROS) and the arm (`pymycobot`) |
| [docs/Requirements.txt](docs/Requirements.txt) | Project requirements with priority weights |
| [docs/User_Stories/](docs/User_Stories/) | User stories and acceptance criteria |
| [docs/ERDs/](docs/ERDs/) | Database diagrams |

## Setup

### Website and API (web server)

Requirements: PHP 7.4 or newer with PDO MySQL, and a MySQL database.

1. Upload `website/`, `includes/`, and `api/` to the server, side by side.
2. Copy `includes/config_sample.php` to `includes/config.php` and fill in the database login and `$robotApiKey`. `config.php` is gitignored; never commit it.
3. Create the tables shown in [docs/ERDs/RDS_ERD.png](docs/ERDs/RDS_ERD.png) and add items whose `Location` matches the robot's locations (`box1`, `box2`, `box3`).

Generate an API key with:

```
php -r "echo bin2hex(random_bytes(32));"
```

### Robot (on the LIMO)

The LIMO already has ROS Noetic installed. When the terminal asks which ROS version to use, choose **1** (Noetic).

```
git clone https://github.com/dornblaserc/Soft-Eng---Robot-
sudo apt update
sudo apt install ros-noetic-geometry-msgs ros-noetic-cv-bridge
pip3 install pymycobot requests opencv-python numpy
```

Then edit `src/run_robot/robot_config.py`:

```python
API = "https://rds.etowndb.com/api"   # your server
API_KEY = "same key as $robotApiKey in config.php"
POLL_SECONDS = 3
```

## Running the robot

```
cd Soft-Eng---Robot-/src/run_robot
bash setup.sh
```

`setup.sh` starts the LIMO base driver and the camera driver, waits until both are ready, and then runs `robot.py`. Press **Ctrl+C** to stop; the script shuts down the drivers for you.

To test a single pass (handle one order, or report that none is waiting, then exit), start the drivers and run:

```
python3 robot.py --once
```

### Driving manually

The LIMO can also be driven by hand with the **AgileX** app (search "AgileX" in the App Store).

## Project status

| Feature | Status |
|---|---|
| Register, log in, log out | Done |
| Place an order and track its status | Done |
| Robot API with API-key authentication | Done |
| Robot fetches orders and reports Delivered / Failed | Done |
| Driving to bins and picking with fixed arm positions | Done |
| Home page | In progress |
| Camera-based ball detection and pickup | In progress (`src/Tests/in_progress/`) |

## Team

| Name | Focus |
|---|---|
| Chase Dornblaser | Website and website-to-robot connection |
| Brandon Short | Robot arm functionality |
| Chris Mensah | Robot movement functionality |
| Noah Peiffer | Robot movement functionality |

## License

See [LICENSE](LICENSE).

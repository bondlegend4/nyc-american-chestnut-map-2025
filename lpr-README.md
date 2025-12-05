# LPR - NYC Webcam Vehicle Analysis

This project analyzes images from NYC Traffic Management Center (TMC) webcams (via `https://webcams.nyctmc.org/api`) to detect vehicles, identify their colors, and estimate their direction of travel based on road geometry and lane markings. It also includes tools for managing camera data, configuring road boundaries, and visualizing geofences.

## Overview

The system performs the following main tasks:
1.  **Data Management**:
    * Fetches and stores metadata about available NYC webcams in a SQLite database (`webcams.db`).
    * Allows manual marking of boundary cameras and their lock status via `manage_boundaries.py` or a web interface via `boundary_server.py`.
2.  **Camera Operations**:
    * Identifies active cameras near a specified geographic location using `location.py` or as part of `find_colored_car.py`.
    * Downloads live images from cameras or processes saved local images.
3.  **Image Processing & Analysis**:
    * Uses YOLO object detection to find vehicles (cars, trucks, buses, etc.).
    * Applies K-Means clustering to determine the dominant color of detected vehicles.
    * Analyzes road geometry using configured polygons (`road_segments`) and defined lane divider curves (`lane_divider_curves`) from `camera_config.json` to estimate vehicle direction.
    * Filters out known static obstructions based on configuration.
4.  **Configuration**:
    * Allows configuration of road segments (polygons defining road areas and direction) and lane divider curves (defined by 3 points) via a PySide6 GUI (`generate_road_configs_psides.py`) or, less reliably, through automatic detection (`generate_road_configs.py`).
    * Configurations are stored in `camera_config.json`.
5.  **Geofencing & Visualization**:
    * Identifies potential "Named Boundaries" (e.g., bridges, tunnels) based on camera name keywords and calculates convex hulls for these groups.
    * Iteratively creates "Normal Camera Geofences" for other cameras by grouping nearby unassigned cameras and calculating their convex hull, with validation to prevent overlap with other zones.
    * Saves geofence polygon data (with camera IDs, names, and coordinates) to `geofences.json`.
    * Generates an interactive HTML map (`geofence_map.html`) using Leaflet.js to visualize all cameras (grouped by borough and boundary status) and the defined geofence polygons. This map allows users to manually update a camera's boundary status and create new named geofence boundaries via a Flask server (`boundary_server.py`).

## Included Scripts

* **`scrape.py`** (located in `lpr copy/old/`):
    * Fetches camera metadata from the NYC TMC API.
    * Creates/updates a SQLite database (`webcams.db`) to store this information. Run this first to populate the camera database.
* **`location.py`**:
    * Takes a street address as input.
    * Uses geocoding to find the coordinates of the address.
    * Queries the `webcams.db` database.
    * Lists the closest active cameras to the input address.
* **`road_analyzer.py`**:
    * Contains the `RoadSegment` class and helper functions for defining and managing road segment polygons (boundaries and direction).
    * Handles loading road segment data from `camera_config.json`.
    * Includes a basic placeholder function for attempting automatic detection of road boundaries.
* **`find_colored_car.py`**:
    * The main script for real-time analysis of nearby active cameras.
    * Takes an address and target vehicle color as input.
    * Downloads current images for nearby cameras.
    * Loads camera configurations (static obstructions, road segments, lane curves) from `camera_config.json`.
    * If road segments or lane curves are missing, it attempts automatic detection/fitting and can update the configuration file.
    * Performs vehicle detection, color analysis, and direction estimation.
    * Saves original and annotated images.
    * Includes interactive prompts to mark static objects or clear bad curve definitions from the config.
* **`process_offline_image.py`**:
    * Processes a single, pre-existing image file.
    * Attempts to extract the camera ID from the filename to load its specific configuration.
    * Performs detection, analysis, and saves an annotated image.
* **`generate_road_configs_psides.py`**:
    * Provides a PySide6 GUI for visually defining and editing road segment polygons and 3-point lane divider curves for cameras.
    * Loads camera data from `webcams.db` and existing configurations from `camera_config.json`.
    * Saves changes back to `camera_config.json`.
* **`generate_road_configs.py`**:
    * A command-line script that attempts *automatic* road segment detection for cameras.
    * Lacks robust review/editing capabilities compared to the PySide GUI; `generate_road_configs_psides.py` is recommended for reliable configuration.
* **`create_geofence_data.py`**:
    * Processes cameras marked as `is_boundary_marker` to create "Named Boundaries" (e.g., bridges) by calculating convex hulls and stores them in `geofences.json` using rich camera info (ID, name, coords).
    * Processes "Normal Cameras" (not boundary markers, not in named boundaries) to create "Normal Camera Geofences" by grouping an anchor camera with its K closest neighbors (within a max distance), calculating a convex hull, and validating that this hull doesn't contain other unassociated cameras. These are also stored in `geofences.json`.
    * Uses SciPy for Convex Hull calculations if available.
* **`visualize_geofence.py`**:
    * Identifies potential boundary cameras based on keywords (e.g., bridge names in `constants.py`) and updates their `is_boundary_marker` status in the database (only for unlocked cameras).
    * Reads named boundary polygon data (with camera details) from `geofences.json`.
    * Generates an interactive HTML map (`geofence_map.html`) from `map_template.html`, visualizing all cameras (grouped by borough and status) and the geofence polygons.
* **`boundary_server.py`**:
    * A simple Flask web server that handles requests from the `geofence_map.html`.
    * Allows users to update the `is_boundary_marker` and `boundary_status_locked` status of cameras in the database.
    * Allows users to create new named geofence boundaries by selecting cameras on the map; these are then processed (convex hull) and saved to `geofences.json`.
* **`manage_boundaries.py`**:
    * A command-line tool to manually set or unset the `is_boundary_marker` flag for cameras in the database. This directly interacts with `db_manager.py`.
* **Utility Modules**:
    * **`constants.py`**: Shared constants for file paths, API URLs, keywords, processing parameters, and colors.
    * **`db_manager.py`**: Handles all interactions with the SQLite database (`webcams.db`), including initialization, fetching camera data, and updating boundary/lock statuses.
    * **`config_manager.py`**: Handles loading and saving of the `camera_config.json` file.
    * **`image_utils.py`**: Utility functions for downloading images from URLs and finding local copies.
    * **`geo_utils.py`**: Provides functions for geocoding addresses to coordinates and calculating distances between coordinates.
    * **`yolo_loader.py`**: Loads the YOLO object detection model and class names.
    * **`image_processor.py`**: Contains the core image processing logic used by `find_colored_car.py` and `process_offline_image.py`. This includes YOLO inference, NMS, static obstruction filtering, color analysis (K-Means), curve fitting, and direction estimation relative to road segments and lane curves.

## Configuration Files

* **`webcams.db`**: SQLite database storing camera metadata (ID, name, location, image URL, status, boundary marker status, lock status). Created/updated by `scrape.py` and `db_manager.py`.
* **`camera_config.json`**: Stores camera-specific configurations:
    * `static_obstructions`: A list of dictionaries, each with `"label"` (string) and `"box"` (`[x, y, w, h]`) for known static objects to be ignored during analysis.
    * `road_segments`: A list of dictionaries, each defining a road area with:
        * `polygon`: A list of `[x, y]` integer vertices.
        * `direction`: A string indicating the cardinal direction (e.g., "N", "SOUTHBOUND", "UNKNOWN").
    * `lane_divider_curves`: A list of curve definitions. Each definition is a dictionary:
        * `label`: A string identifier for the curve (e.g., "Main Lane", "Fitted Curve").
        * `points`: A list of exactly 3 `[x, y]` integer points (start, middle, end) that define the quadratic curve `x = ay^2 + by + c`.
* **`geofences.json`**: Stores named geofence boundaries. Each key is a boundary name (e.g., "Queensboro Bridge"), and the value is a list of camera objects that form the convex hull of that boundary. Each camera object includes its `id`, `name`, and `coords` (`[lat, lon]`). Normal camera zones are also stored here with names like `NORMAL_ZONE_<camera_id>`.
* **YOLO Files** (typically in a `yolov3/` subdirectory):
    * `yolov3.weights` (or tiny version): Pre-trained model weights. (Needs to be downloaded separately).
    * `yolov3.cfg` (or tiny version): Model configuration file.
    * `coco.names`: List of object class names the YOLO model can detect.
* **`map_template.html`**: Base HTML structure used by `visualize_geofence.py` to generate the `geofence_map.html`.

## Dependencies

The primary dependencies are listed in `requirements.txt`. Key libraries include:
* Python 3.x
* OpenCV (`opencv-python`)
* NumPy (`numpy`)
* Requests (`requests`)
* Geopy (`geopy`)
* PySide6 (`PySide6`) - For the `generate_road_configs_psides.py` GUI.
* Pillow (`Pillow`) - Used by PySide6 for image handling in the GUI.
* Flask (`Flask`) - For `boundary_server.py`.
* Flask-CORS (`Flask-CORS`) - For `boundary_server.py`.
* SciPy (`scipy`) - For Convex Hull and Delaunay triangulation in `create_geofence_data.py` and `boundary_server.py`.

Install dependencies using pip:
```bash
pip install -r requirements.txt
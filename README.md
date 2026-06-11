# rakevet-trips 🚂📜

A Python script that fetches Israel Public Transportaion GTFS data, then parses and structures it into a JSON train schedule.
focus now is only on trains, not buses or other modes or public transport

## Why this exists
Sometimes you just need a full train schedule. As the official website does not offer one,
This script does the job of going through the GTFS files and building it in a comfortable json format.

## Project Architecture
1. **Fetch**: Weekly, a job triggers and downloads the raw GTFS zip binary from `gtfs.mot.gov.il`.
2. **Process**: A pandas pipeline filters out everything except train agency data (`agency_id: 2`), mapping calendars, routes, trips, and stop sequences.
3. **Deploy**: The script nests stops efficiently inside each trip object, outputs a static `train_schedule.json`, and deploys it automatically to GitHub Pages.

## Tech Stack
* **Language:** Python
* **Data Processing:** Pandas, NumPy
* **Package Manager & Runtime:** `uv` (Astral)
* **Automation & Hosting:** GitHub Actions + GitHub Pages

## Data Schema (Output)
The pipeline outputs a highly optimized JSON array. Each trip object follows this structure:

```json
[
    {
        "route_long_name": "מודיעין מרכז-מודיעין מכבים רעות<->נהריה-נהריה",
        "service_days": ["sunday", "monday", "tuesday", "wednesday", "thursday"],
        "trip_id": "1_470863",
        "start_station": {
            "stop_sequence": 1,
            "stop_name": "מודיעין מרכז",
            "arrival_time": "07:48:00",
            "stop_type": "תחנה ראשונה"
        },
        "end_station": {
            "stop_sequence": 12,
            "stop_name": "נהריה",
            "arrival_time": "10:13:00",
            "stop_type": "תחנה אחרונה"
        },
        "stops": [
            // all stops along the route
        ]
    }
]
```

## Usage
As this script is automatically run and have its output deployed on github's servers, you can access the json at all times from [link-to-pages]

or, for autmation you can ```curl [link-to-pages]```

## Local Development

just clone the repo and work on it. This project also supports `uv`.
   ```bash
   uv run main.py
   ```
(dependencies will be handled automatically by `uv` thanks to PEP 723 metadata)

## License
This project is licensed under the MIT License.
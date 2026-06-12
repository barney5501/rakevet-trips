# rakevet-trips 🚂📜
## Static railway schedule

A Python script that fetches Israel Public Transportaion GTFS data, then parses and structures it into a JSON train schedule.
focus now is only on trains, not buses or other modes of public transport.

Available at [https://barney5501.github.io/rakevet-trips/](https://barney5501.github.io/rakevet-trips/), The dataset automatically updates **every Monday at 03:00 UTC**.

## Why this exists
Sometimes you just need a full train schedule. As the official website does not offer one,
This script does the job of going through the GTFS files and building it in a comfortable json format.

## Project Architecture
1. **Fetch**: Weekly, a job triggers and downloads the raw GTFS zip binary from a `gtfs.mot.gov.il` mirror.
2. **Process**: A pandas pipeline filters out everything except train agency data (`agency_id: 2`), mapping calendars, routes, trips, and stop sequences.
3. **Deploy**: The script nests stops efficiently inside each trip object, outputs a static `train_schedule.json`, and deploys it automatically to GitHub Pages.

### A note on deployment
since the script runs on GitHub's servers (outside Israel), `gtfs.mot.gov.il` cannot be reached.

It is possible to fetch the GTFS files from a global mirror, like the one kindly provided by [MobilityDatabase](https://mobilitydatabase.org/).

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
As this script is automatically run and has its output deployed on github's servers, you can access the json at all times [here](https://barney5501.github.io/rakevet-trips/)

or, for autmation you can use ```curl https://barney5501.github.io/rakevet-trips/```

Would also probably recommend using `jq`.

## Example
```bash
user@pc:~/trains$ curl https://barney5501.github.io/rakevet-trips | jq '.[] |
select(.start_station.stop_name | contains("תל אביב"))
select(.end_station.stop_name | contains("באר שבע"))' > output.json
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 2868k  100 2868k    0     0  1363k      0  0:00:02  0:00:02 --:--:-- 1363k
user@pc:~/trains$ head output.json
{
  "route_long_name": "תל אביב מרכז-תל אביב יפו<->באר שבע מרכז-באר שבע",
  "service_days": [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday"
  ],
  "trip_id": "1_470874",
  ```

## Local Development

just clone the repo and work on it. This project also supports `uv`.
   ```bash
   uv run main.py
   ```
(dependencies will be handled automatically by `uv` thanks to PEP 723 metadata)

## Running Outside Israel / CI (Using international mirror)
as mentioned, since `https://gtfs.mot.gov.il/` is blocked outside of Israel, 
To run (or deploy) abroad simply [create a MobilityDatabase account](https://mobilitydatabase.org/sign-up), get a refresh-token for the API and set it as
`MOBILITY_TOKEN` in your environments variables. the script will automatically detect and use your token to fetch the dataset from the mirror.

## License
This project is licensed under the MIT License.

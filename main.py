import pandas as pd
import numpy as np
import json

TRAIN_AGENCY_CODE = 2

"""
general flow:
1. calendar.txt   -> active days per service_id.
2. routes.txt     -> Filter by train agency_id. used to translate route id to name.
3. trips.txt      -> Filter by train routes. represents an execution in a route at a specific
                     time, active on specific days represented by service_id.
4. stops.txt      -> Map stop id to stop name.
5. stop_times.txt -> Filter by train trips, contains each stop in a trip.
6. Merge          -> Efficiently nest stops data into each trip object using an in-place loop.
JSON Output Description:
[
    {
        "route_long_name": "מודיעין מרכז-מודיעין מכבים רעות<->נהריה-נהריה",
        "service_days": [...],
        "trip_id": "1_470863",
        "stops": [
            {
                "stop_sequence": 1,
                "stop_name": "מודיעין מרכז",
                "arrival_time": "07:48:00",
                "stop_type": "תחנה ראשונה"
            },
            {
                "stop_sequence": 2,
                "stop_name": "פאתי מודיעין",
                "arrival_time": "07:54:00",
                "stop_type": "תחנת ביניים"
            },
            ...
        ]
    },
    ...
]
"""

# zip extraction and cleaning

extracted_dir_name = "israel-public-transportation"

calendar_df = pd.read_csv(f"{extracted_dir_name}/calendar.txt")
calendar_df = calendar_df.drop(columns=["start_date", "end_date"])
calendar_df = calendar_df.melt(id_vars=["service_id"])
calendar_df = calendar_df.loc[calendar_df.value == 1]
calendar_df = calendar_df.groupby("service_id")["variable"].agg(list).reset_index()
calendar = dict(calendar_df.values)


routes_df = pd.read_csv(
    f"{extracted_dir_name}/routes.txt",
    usecols=["route_id", "route_long_name", "agency_id"],
)
routes_df = routes_df.loc[routes_df["agency_id"] == TRAIN_AGENCY_CODE]
routes_names = dict(routes_df[["route_id", "route_long_name"]].values)

trips_df = pd.read_csv(
    f"{extracted_dir_name}/trips.txt", usecols=["route_id", "service_id", "trip_id"]
)
trips_df = trips_df.loc[trips_df["route_id"].isin(routes_names.keys())]
trips_df["route_id"] = trips_df["route_id"].map(routes_names)
trips_df["service_id"] = trips_df["service_id"].map(calendar)
trips_df.columns = ["route_long_name", "service_days", "trip_id"]


stops_df = pd.read_csv(
    f"{extracted_dir_name}/stops.txt", usecols=["stop_id", "stop_name"]
)
stops = dict(stops_df.values)

stop_times_df = pd.read_csv(
    f"{extracted_dir_name}/stop_times.txt",
    usecols=[
        "trip_id",
        "arrival_time",
        "stop_id",
        "stop_sequence",
        "pickup_type",
        "drop_off_type",
    ],
)
stop_times_df = stop_times_df.loc[stop_times_df["trip_id"].isin(trips_df["trip_id"])]
stop_times_df["stop_id"] = stop_times_df["stop_id"].map(stops)
stop_times_df["stop_type"] = np.select(
    condlist=[stop_times_df["drop_off_type"] == 1, stop_times_df["pickup_type"] == 1],
    choicelist=["תחנה ראשונה", "תחנה אחרונה"],
    default="תחנת ביניים",
)
stop_times_df = stop_times_df.drop(columns=["pickup_type", "drop_off_type"])
stop_times_df = stop_times_df.rename(columns={"stop_id": "stop_name"})


trips_stops = (
    stop_times_df.groupby("trip_id")[
        ["stop_sequence", "stop_name", "arrival_time", "stop_type"]
    ]
    .apply(lambda r: r.to_dict(orient="records"))
    .to_dict()
)
trips_days = trips_df.to_dict(orient="records")

for trip in trips_days:
    trip["start_station"] = trips_stops[trip["trip_id"]][0]
    trip["end_station"] = trips_stops[trip["trip_id"]][-1]
    trip["stops"] = trips_stops[trip["trip_id"]]


with open("trips_days.json", "w", encoding="UTF-8") as f:
    json.dump(trips_days, f, ensure_ascii=False, indent=4)

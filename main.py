# /// script
# dependencies = [
# "pandas",
# "numpy",
# "requests",
# ]
# ///

import requests
from zipfile import ZipFile
import pandas as pd
import numpy as np
import json

TRAIN_AGENCY_CODE = 2
GTFS_URL = "https://gtfs.mot.gov.il/gtfsfiles"
GTFS_FILE = "israel-public-transportation.zip"
EXTRACTED_DIR_NAME = "israel-public-transportation"

# zip extraction and cleaning
gtfs_response = requests.get(f"{GTFS_URL}/{GTFS_FILE}", stream=True)
with open(GTFS_FILE, "wb") as zf:
    zf.write(gtfs_response.content)
with ZipFile(GTFS_FILE, "r") as zf:
    zf.extractall(EXTRACTED_DIR_NAME)

calendar_df = pd.read_csv(f"{EXTRACTED_DIR_NAME}/calendar.txt")
calendar_df = calendar_df.drop(columns=["start_date", "end_date"])
calendar_df = calendar_df.melt(id_vars=["service_id"])
calendar_df = calendar_df.loc[calendar_df.value == 1]
calendar_df = calendar_df.groupby("service_id")["variable"].agg(list).reset_index()
calendar = dict(calendar_df.values)


routes_df = pd.read_csv(
    f"{EXTRACTED_DIR_NAME}/routes.txt",
    usecols=["route_id", "route_long_name", "agency_id"],
)
routes_df = routes_df.loc[routes_df["agency_id"] == TRAIN_AGENCY_CODE]
routes_names = dict(routes_df[["route_id", "route_long_name"]].values)

trips_df = pd.read_csv(
    f"{EXTRACTED_DIR_NAME}/trips.txt", usecols=["route_id", "service_id", "trip_id"]
)
trips_df = trips_df.loc[trips_df["route_id"].isin(routes_names.keys())]
trips_df["route_id"] = trips_df["route_id"].map(routes_names)
trips_df["service_id"] = trips_df["service_id"].map(calendar)
trips_df.columns = ["route_long_name", "service_days", "trip_id"]


stops_df = pd.read_csv(
    f"{EXTRACTED_DIR_NAME}/stops.txt", usecols=["stop_id", "stop_name"]
)
stops = dict(stops_df.values)

stop_times_df = pd.read_csv(
    f"{EXTRACTED_DIR_NAME}/stop_times.txt",
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

with open("train_schedule.json", "w", encoding="UTF-8") as f:
    json.dump(trips_days, f, ensure_ascii=False, indent=4)

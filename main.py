import pandas as pd
import numpy as np
import json

TRAIN_AGENCY_CODE = 2

"""
general flow
routes.txt -> route_id, route_name
trips.txt -> route_id, trip_id
stop_times.txt -> trip_id, stop_id, arrival_time, departure_time
stops.txt -> stop_id, stop_name

final result object description:
trip : {
    id:int,
    days:list,
    departure:{
        station:
        time:
    }
    arrival:{
        station:
        time:
    }
    stops:[
        {
            station:
            time:
        }
    ]
}
"""


"""
route_id. from routes.txt we just need the route name
trip_id. each trip is a combination of a route and the days it's available in.
stop_times. all of the stops in a 
"""

"""
agg method:
trips.gruopby(route_id) -> dict of {route_id: {days: [service_id], trip_stops: [trip_id] }}
then
replace service_id with the days list
replace trip_id in trip_stops with another aggregated
stop_times_df.groupby('trip_id') -> dict of {trip_id: [
                                                {
                                                'stop_name': stop_name,
                                                'time': time,
                                                'seq: seq,
                                                'type': type //:first|last|through
                                                }
                                            ]}

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
    trip["stops"] = trips_stops[trip["trip_id"]]


with open("trips_days.json", "w", encoding="UTF-8") as f:
    json.dump(trips_days, f, ensure_ascii=False, indent=4)
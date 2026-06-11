import pandas as pd
TRAIN_AGENCY_CODE = 2

'''
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
'''


'''
route_id. from routes.txt we just need the route name
trip_id. each trip is a combination of a route and the days it's available in.
stop_times. all of the stops in a 
'''

'''
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

'''

# zip extraction and cleaning

extracted_dir_name = 'israel-public-transportation'

routes_df = pd.read_table(f'{extracted_dir_name}/routes.txt', sep=',', usecols=['route_id','route_long_name','agency_id'])
routes_df = (
    routes_df.loc[routes_df['agency_id'] == TRAIN_AGENCY_CODE]
    .drop(columns=['agency_id'])
)


trips_df = pd.read_table(f'{extracted_dir_name}/trips.txt', sep=',')
trips_df = trips_df[['route_id','service_id','trip_id']]
trips_df = trips_df.loc[trips_df['route_id'].isin(routes_df['route_id'])]

stop_times_df = pd.read_table(f'{extracted_dir_name}/stop_times.txt', sep=',')
stop_times_df = stop_times_df[['trip_id',
                               'arrival_time',
                               'stop_id',
                               'stop_sequence',
                               'pickup_type',
                               'drop_off_type']]

calendar_df = pd.read_table(f'{extracted_dir_name}/calendar.txt', sep=',')
calendar_df = calendar_df.drop(columns=['start_date','end_date'])
calendar_df = calendar_df.melt(id_vars=['service_id'])
calendar_df = calendar_df.loc[calendar_df.value == 1]
calendar_df = calendar_df.groupby('service_id')['variable'].agg(list).reset_index()
calendar = dict(calendar_df.values)

stops_df = pd.read_table(f'{extracted_dir_name}/stops.txt', sep=',')
stops_df = stops_df[['stop_id','stop_name']]
stops = dict(stops_df.values)

output_df = (
    routes_df
    .merge(trips_df, on="route_id")
    .merge(stop_times_df, on="trip_id")
)
output_df['stop_id'] = output_df['stop_id'].map(stops)
output_df['service_id'] = output_df['service_id'].map(calendar)
# output_df = output_df.explode('service_id')
keep_columns = ['route_id','route_long_name','service_id','arrival_time','stop_id','stop_sequence','pickup_type','drop_off_type']
output_df = output_df[keep_columns]
output_df.columns = ['route_id', 'route_name', 'day', 'station_time', 'station_name', 'stop_number', 'IS_LAST', 'IS_FIRST']
output_df['stop_type'] = output_df.apply(lambda r: 'תחנה ראשונה' if r['IS_FIRST']==1 else 'תחנה אחרונה' if r['IS_LAST']==1 else 'תחנת ביניים',axis=1)
output_df = output_df.drop(columns=['IS_LAST','IS_FIRST'])
# output_df = output_df.drop_duplicates()
output_df.to_csv('o.csv')
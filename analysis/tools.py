from dateutil import parser
from datetime import datetime, timedelta

def aggregate_times_by_carraige_flow(df):
    df = df.groupby('Local Time')
    dates = {}

    for time, name in df:
        mean = name['Total Carriageway Flow'].mean(skipna = True)
        
        if mean > 0:
            tm = parser.parse(time)
            tm = tm - timedelta(minutes=tm.minute % 20,
                                seconds=tm.second)

            tm_str = tm.strftime("%H:%M:%S")
            if tm_str in dates:
                dates[tm_str].append(mean)
            else:
                dates[tm_str] = [mean]

    for d in dates.keys():
        dates[d] = sum(dates[d]) / len(dates[d])

    return dates
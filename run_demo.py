import json
from task3b import compute_schedule, to_dataframe

trajet = ["Depart", "R3", "R1", "R5"]
affect = {"R3": ["Alice", "Charlie"], "R1": ["Bob"], "R5": ["Diane", "Eve"]}
temps = {"Depart": {"R3": 5}, "R3": {"R1": 7}, "R1": {"R5": 10}}

sched = compute_schedule(trajet, affect, temps, start_time="08:00", stop_time_per_passenger_min=1)

try:
    df = to_dataframe(sched)
    print(df.to_string(index=False))
except Exception as e:
    print("PANDAS_ERROR:", e)
    print(json.dumps(sched, indent=2, ensure_ascii=False))


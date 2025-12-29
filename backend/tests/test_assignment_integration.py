import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pickup_scheduler import validate_inputs, determine_stop_point_per_passenger, compute_schedule


def test_assignment_json_integration():
    # load the consolidated assignment produced by pickup_schedulerA
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "data", "assignment.json")
    assert os.path.exists(path), f"Expected assignment.json at {path}"

    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    trajet = d.get("TRAJET_ORDRE")
    affect = d.get("AFFECTATIONS_PAR_POINT")
    temps = d.get("TEMPS_TRAJET_MIN")
    z = d.get("Z_optimal")

    # basic validation should not raise
    validate_inputs(trajet, affect, temps, Z_optimal=z)

    # stops per passenger should match expected structure
    stops = determine_stop_point_per_passenger(affect)

    expected_names = set(["Alice", "Charlie", "Bob", "Diane", "Eve"])
    assert set(stops.keys()) == expected_names
    assert stops["Alice"]["board"] == "R3"
    assert stops["Charlie"]["board"] == "R3"
    assert stops["Bob"]["board"] == "R1"
    assert stops["Diane"]["board"] == "R5"
    assert stops["Eve"]["board"] == "R5"

    # compute schedule and verify final cumulative equals Z_optimal
    sched = compute_schedule(trajet, affect, temps, start_time="08:00", stop_time_per_passenger_min=1)
    assert isinstance(sched, list)
    assert len(sched) == len(trajet)
    assert sched[-1]["cumulative"] == z

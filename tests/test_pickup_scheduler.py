import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest

from pickup_scheduler import (
    validate_inputs,
    determine_stop_point_per_passenger,
    compute_schedule,
    to_dataframe,
)


def test_assignment_json_end_to_end():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, "data", "assignment.json")
    assert os.path.exists(path), f"Expected assignment.json at {path}"

    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    trajet = d.get("TRAJET_ORDRE")
    affect = d.get("AFFECTATIONS_PAR_POINT")
    temps = d.get("TEMPS_TRAJET_MIN")
    z = d.get("Z_optimal")

    # validate should not raise
    validate_inputs(trajet, affect, temps, Z_optimal=z)

    # check stops mapping
    stops = determine_stop_point_per_passenger(affect)
    expected = {"Alice": "R3", "Charlie": "R3", "Bob": "R1", "Diane": "R5", "Eve": "R5"}
    for name, board in expected.items():
        assert name in stops
        assert stops[name]["board"] == board

    # compute schedule
    sched = compute_schedule(trajet, affect, temps, start_time="08:00", stop_time_per_passenger_min=1)
    assert isinstance(sched, list)
    assert len(sched) == len(trajet)
    assert sched[-1]["cumulative"] == z

    # to_dataframe: if pandas present, convert and check columns; otherwise ensure ImportError is raised when called
    try:
        df = to_dataframe(sched)
        assert "arrival" in df.columns and "departure" in df.columns
    except ImportError:
        pytest.skip("pandas not installed; skipping DataFrame check")


def test_missing_travel_time_raises():
    trajet = ["A", "B", "C"]
    affect = {"A": ["P1"], "B": ["P2"], "C": []}
    temps_bad = {"A": {"B": 5}, "B": {}}  # missing B->C and symmetric C->B
    with pytest.raises(ValueError, match="Missing travel time"):
        validate_inputs(trajet, affect, temps_bad, default_travel_min=None)


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pickup_scheduler import validate_inputs, compute_schedule


def demo_data():
    trajet = ["Depart", "R3", "R1", "R5"]
    affect = {
        "R3": ["Alice", "Charlie"],
        "R1": ["Bob"],
        "R5": ["Diane", "Eve"],
    }
    temps = {
        "Depart": {"R3": 5},
        "R3": {"R1": 7},
        "R1": {"R5": 10},
    }
    return trajet, affect, temps


def test_validate_inputs_and_compute_schedule_valid():
    trajet, affect, temps = demo_data()
    # should not raise
    validate_inputs(trajet, affect, temps, Z_optimal=5)
    sched = compute_schedule(trajet, affect, temps, start_time="08:00", stop_time_per_passenger_min=1)
    assert isinstance(sched, list)
    # final cumulative equals 5
    assert sched[-1]["cumulative"] == 5
    # schedule has an entry per trajet point
    assert len(sched) == len(trajet)


def test_validate_missing_travel_time_raises():
    trajet, affect, temps = demo_data()
    # remove a travel entry to simulate missing travel time
    temps_bad = {"Depart": {"R3": 5}, "R3": {}}
    with pytest.raises(ValueError, match="Missing travel time"):
        validate_inputs(trajet, affect, temps_bad, default_travel_min=None)


def test_validate_extra_affect_point_raises():
    trajet, affect, temps = demo_data()
    affect_bad = dict(affect)
    affect_bad["R_X"] = ["Z"]
    with pytest.raises(ValueError, match="not present in TRAJET_ORDRE"):
        validate_inputs(trajet, affect_bad, temps)


def test_validate_zoptimal_mismatch_raises():
    trajet, affect, temps = demo_data()
    # Z_optimal intentionally wrong
    with pytest.raises(ValueError, match="Z_optimal=4 but found 5"):
        validate_inputs(trajet, affect, temps, Z_optimal=4)


if __name__ == "__main__":
    pytest.main(["-q"])

# ok

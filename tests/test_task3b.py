import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from task3b import determine_stop_point_per_passenger


def test_list_affectations():
    affect = {
        "R3": ["Alice", "Charlie"],
        "R1": ["Bob"],
        "R5": ["Diane", "Eve"],
    }
    res = determine_stop_point_per_passenger(affect)
    assert res["Alice"]["board"] == "R3" and res["Alice"]["alight"] is None
    assert res["Charlie"]["board"] == "R3"
    assert res["Bob"]["board"] == "R1"
    assert res["Diane"]["board"] == "R5"
    assert res["Eve"]["board"] == "R5"


def test_dict_board_alight():
    affect = {
        "R2": {"board": ["X"], "alight": ["Y"]},
        "R3": {"board": ["Y"]},
    }
    res = determine_stop_point_per_passenger(affect)
    assert res["X"]["board"] == "R2"
    assert res["X"]["alight"] is None
    assert res["Y"]["board"] == "R3"
    assert res["Y"]["alight"] == "R2"


def test_repeated_entries_first_occurrence():
    affect = {
        "R1": ["A"],
        "R2": {"board": ["A"]},
    }
    res = determine_stop_point_per_passenger(affect)
    assert res["A"]["board"] == "R1"


def test_ignore_ints_and_unknowns():
    affect = {
        "R1": 3,
        "R2": ["B"],
    }
    res = determine_stop_point_per_passenger(affect)
    assert "B" in res and "R1" not in res.get("B").values()


if __name__ == "__main__":
    pytest.main(["-q"])

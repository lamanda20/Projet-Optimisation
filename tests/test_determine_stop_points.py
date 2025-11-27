import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task3 import determine_stop_point_per_passenger


def test_list_and_dict_formats():
    affect = {
        "R1": ["Alice", "Bob"],
        "R2": {"board": ["Charlie"], "alight": ["Bob"]},
    }
    res = determine_stop_point_per_passenger(affect)
    assert res["Alice"]["board"] == "R1" and res["Alice"]["alight"] is None
    assert res["Bob"]["board"] == "R1" and res["Bob"]["alight"] == "R2"
    assert res["Charlie"]["board"] == "R2"


def test_alight_before_board_sets_both():
    # alight appears before board; first occurrence wins per field but board can be set later
    affect = {
        "R1": {"alight": ["X"]},
        "R2": ["X"],
    }
    res = determine_stop_point_per_passenger(affect)
    # alight first at R1, then board at R2 -> result should have both set
    assert res["X"]["alight"] == "R1"
    assert res["X"]["board"] == "R2"


def test_repeated_board_first_occurrence_wins():
    affect = {
        "R1": ["A"],
        "R2": ["A"],
        "R3": {"board": ["A"]},
    }
    res = determine_stop_point_per_passenger(affect)
    assert res["A"]["board"] == "R1"


def test_ignore_integers_and_unknowns():
    affect = {
        "R1": 3,
        "R2": ["B"],
        "R3": {"board": "not-a-list", "alight": None},
    }
    res = determine_stop_point_per_passenger(affect)
    # integer ignored, B present
    assert "B" in res and res["B"]["board"] == "R2"
    # malformed board value should not crash and should ignore the non-list
    assert isinstance(res, dict)


def test_no_entries_returns_empty():
    affect = {}
    res = determine_stop_point_per_passenger(affect)
    assert res == {}


if __name__ == "__main__":
    import pytest
    pytest.main(["-q"])

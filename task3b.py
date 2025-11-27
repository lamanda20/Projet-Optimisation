from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional
import argparse
import json
import logging


# configure basic logging
logging.basicConfig(level=logging.INFO)


def _parse_time(t: Union[str, datetime]) -> datetime:
    if isinstance(t, datetime):
        return t
    try:
        return datetime.fromisoformat(t)
    except Exception:
        parts = t.split(":")
        if len(parts) == 2:
            now = datetime.now()
            return datetime(now.year, now.month, now.day, int(parts[0]), int(parts[1]))
        raise


def _get_travel_time(a: str, b: str, temps: Dict[str, Dict[str, int]], default_travel_min: Optional[int] = None) -> int:
    # try direct
    if a in temps and b in temps[a]:
        return int(temps[a][b])
    # try symmetric
    if b in temps and a in temps[b]:
        return int(temps[b][a])
    if default_travel_min is not None:
        logging.warning(f"Missing travel time between '{a}' and '{b}' — using default {default_travel_min} min")
        return int(default_travel_min)
    raise ValueError(f"Missing travel time between '{a}' and '{b}' in TEMPS_TRAJET_MIN")


def _count_board_alight(point: str, affectations: Dict[str, Any]) -> (int, int, List[str]):
    # affectations may be: list of passenger names, or dict { 'board': [names] ,'alight': [names] }
    if point not in affectations:
        return 0, 0, []
    val = affectations[point]
    # if it's a dict with 'board'/'alight'
    if isinstance(val, dict):
        board_list = val.get("board", [])
        alight_list = val.get("alight", [])
        # normalize to lists
        board_list = board_list if isinstance(board_list, list) else []
        alight_list = alight_list if isinstance(alight_list, list) else []
        return len(board_list), len(alight_list), board_list
    # if it's a list of names, assume these are boardings at this point
    if isinstance(val, list):
        return len(val), 0, val
    # if it's an integer, interpret as board count
    if isinstance(val, int):
        return int(val), 0, []
    # unknown format
    raise ValueError(f"Unknown affectations format for point '{point}': {type(val)}")


def compute_schedule(
    trajet_ordre: List[str],
    affectations_par_point: Dict[str, Any],
    temps_trajet_min: Dict[str, Dict[str, int]],
    start_time: Union[str, datetime] = "08:00",
    stop_time_per_passenger_min: int = 1,
    default_travel_min: Optional[int] = None,
    lenient: bool = False,
) -> List[Dict[str, Any]]:
    """
    Compute arrival/departure times and running passenger counts for an ordered route.

    Inputs:
    - trajet_ordre: ordered list of points (including start point)
    - affectations_par_point: dict where each key is a point and value is either:
        * a list of passenger names (interpreted as boardings), or
        * a dict with keys 'board' and/or 'alight' mapping to lists of names
        * an int interpreted as number of boardings
    - temps_trajet_min: nested dict with travel minutes between points, e.g. {'A': {'B': 10}, ...}
    - start_time: 'HH:MM' or ISO string or datetime for the departure from the first point
    - stop_time_per_passenger_min: minutes added per boarding or alighting passenger

    Behavior:
    - strict on missing travel times: raises ValueError
    - strict on over-alighting: raises ValueError if trying to alight more than on board

    Returns: list of records per point with keys: point, arrival, departure, board, alight, cumulative, dwell_minutes
    """
    if not trajet_ordre:
        return []

    current_time = _parse_time(start_time)
    records: List[Dict[str, Any]] = []
    cumulative = 0

    # The first point: arrival = start_time (driver is at start), compute board/alight there
    prev_point = trajet_ordre[0]
    # For first point we consider arrival = start_time
    arrival = current_time
    board, alight, boarded_names = _count_board_alight(prev_point, affectations_par_point)
    # alight at start is usually 0, but validate
    if alight > cumulative:
        if lenient:
            logging.warning(f"Alight ({alight}) at '{prev_point}' > currently on board ({cumulative}) — clamping to available")
            alight = min(alight, cumulative)
        else:
            raise ValueError(f"Alight ({alight}) at '{prev_point}' > currently on board ({cumulative})")
    cumulative = cumulative - alight + board
    dwell_minutes = stop_time_per_passenger_min * (board + alight)
    departure = arrival + timedelta(minutes=dwell_minutes)
    records.append({
        "point": prev_point,
        "arrival": arrival.isoformat(),
        "departure": departure.isoformat(),
        "board": board,
        "alight": alight,
        "cumulative": cumulative,
        "dwell_minutes": dwell_minutes,
        "passengers_boarded": boarded_names,
    })

    # iterate remaining legs
    for cur_point in trajet_ordre[1:]:
        # travel time from prev_point to cur_point
        travel_min = _get_travel_time(prev_point, cur_point, temps_trajet_min, default_travel_min)
        arrival = departure + timedelta(minutes=travel_min)
        board, alight, boarded_names = _count_board_alight(cur_point, affectations_par_point)
        if alight > cumulative:
            if lenient:
                logging.warning(f"Alight ({alight}) at '{cur_point}' > currently on board ({cumulative}) — clamping to available")
                alight = min(alight, cumulative)
            else:
                raise ValueError(f"Alight ({alight}) at '{cur_point}' > currently on board ({cumulative})")
        cumulative = cumulative - alight + board
        dwell_minutes = stop_time_per_passenger_min * (board + alight)
        departure = arrival + timedelta(minutes=dwell_minutes)
        records.append({
            "point": cur_point,
            "arrival": arrival.isoformat(),
            "departure": departure.isoformat(),
            "board": board,
            "alight": alight,
            "cumulative": cumulative,
            "dwell_minutes": dwell_minutes,
            "passengers_boarded": boarded_names,
        })
        prev_point = cur_point

    return records


def to_dataframe(schedule: List[Dict[str, Any]]):
    """Convert schedule (list of dicts) to a pandas DataFrame.

    Pandas is imported inside the function to keep it optional at module import time.
    """
    try:
        import pandas as pd
    except Exception as e:
        raise ImportError("pandas is required to convert to DataFrame. Install it or skip this call.") from e

    if not schedule:
        return pd.DataFrame()

    df = pd.DataFrame(schedule)
    # parse datetimes
    df["arrival"] = pd.to_datetime(df["arrival"])
    df["departure"] = pd.to_datetime(df["departure"])
    return df


def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(description="Compute pickup schedule from trajet and affectations (Task3B)")
    p.add_argument("--trajet-file", help="JSON file with trajet_ordre (list)")
    p.add_argument("--affect-file", help="JSON file with affectations_par_point (dict)")
    p.add_argument("--times-file", help="JSON file with TEMPS_TRAJET_MIN (nested dict)")
    p.add_argument("--start-time", default="08:00", help="Start time (HH:MM or ISO)")
    p.add_argument("--stop-min", type=int, default=1, help="Stop time per passenger in minutes")
    p.add_argument("--default-travel-min", type=int, default=None, help="Fallback travel minutes if missing")
    p.add_argument("--lenient", action="store_true", help="Lenient mode: clamp over-alighting and warn instead of error")
    p.add_argument("--output-csv", help="Optional path to write CSV output")
    p.add_argument("--demo", action="store_true", help="Run built-in demo")
    args = p.parse_args(argv)

    if args.demo:
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
    else:
        if not (args.trajet_file and args.affect_file and args.times_file):
            p.error("Either --demo or all of --trajet-file, --affect-file and --times-file must be provided")
        with open(args.trajet_file, "r", encoding="utf-8") as f:
            trajet = json.load(f)
        with open(args.affect_file, "r", encoding="utf-8") as f:
            affect = json.load(f)
        with open(args.times_file, "r", encoding="utf-8") as f:
            temps = json.load(f)

    schedule = compute_schedule(
        trajet,
        affect,
        temps,
        start_time=args.start_time,
        stop_time_per_passenger_min=args.stop_min,
        default_travel_min=args.default_travel_min,
        lenient=args.lenient,
    )

    print(json.dumps(schedule, indent=2, ensure_ascii=False))

    if args.output_csv:
        df = to_dataframe(schedule)
        df.to_csv(args.output_csv, index=False)
        logging.info(f"Wrote CSV to {args.output_csv}")


if __name__ == "__main__":
    import sys

    main()

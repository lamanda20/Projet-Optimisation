from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional, Tuple
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


def _count_board_alight(point: str, affectations: Dict[str, Any]) -> Tuple[int, int, List[str]]:
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


# Helper utilities added to be compatible with the merged branch architecture

def _extract_key_from_dict(obj: Dict[str, Any], candidates: List[str]):
    """Return the first matching key's value from obj, trying several candidate key names (case-sensitive).
    If none match, return None.
    """
    if not isinstance(obj, dict):
        return None
    for key in candidates:
        if key in obj:
            return obj[key]
    return None


def _normalize_trajet(obj: Any) -> List[str]:
    # if file already contains a list
    if isinstance(obj, list):
        return obj
    # if dict, try common key names
    val = _extract_key_from_dict(obj, ["TRAJET_ORDRE", "trajet_ordre", "trajet", "TRJ"])
    if isinstance(val, list):
        return val
    raise ValueError("Unable to extract trajet_ordre from provided JSON file")


def _normalize_affectations(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        # if dict contains top-level AFFECTATIONS_PAR_POINT key
        v = _extract_key_from_dict(obj, ["AFFECTATIONS_PAR_POINT", "affectations_par_point", "affectations", "AFFECTATIONS"])
        if v is not None:
            return v
        # otherwise assume the dict itself is the affectations map
        return obj
    raise ValueError("Unable to extract affectations_par_point from provided JSON file")


def _normalize_temps(obj: Any) -> Dict[str, Dict[str, int]]:
    if isinstance(obj, dict):
        v = _extract_key_from_dict(obj, ["TEMPS_TRAJET_MIN", "temps_trajet_min", "times", "travel_times"])
        if v is not None:
            return v
        return obj
    raise ValueError("Unable to extract TEMPS_TRAJET_MIN from provided JSON file")


def validate_inputs(
    trajet_ordre: List[str],
    affectations_par_point: Dict[str, Any],
    temps_trajet_min: Dict[str, Dict[str, int]],
    Z_optimal: Optional[int] = None,
    default_travel_min: Optional[int] = None,
) -> None:
    """Validate the input structures expected by Task3B.

    Raises ValueError with a clear message when an invariant is violated.
    Checks performed:
    - `trajet_ordre` is a non-empty list
    - `affectations_par_point` is a dict
    - All points referenced in affectations exist in trajet_ordre
    - Travel times exist for consecutive legs (or default_travel_min provided)
    - If Z_optimal provided, number of distinct passenger names equals Z_optimal
    """
    # basic types
    if not isinstance(trajet_ordre, list) or len(trajet_ordre) == 0:
        raise ValueError("TRAJET_ORDRE must be a non-empty list")
    if not isinstance(affectations_par_point, dict):
        raise ValueError("AFFECTATIONS_PAR_POINT must be a dictionary")

    # points consistency
    extra_points = [p for p in affectations_par_point.keys() if p not in trajet_ordre]
    if extra_points:
        raise ValueError(f"Points in AFFECTATIONS_PAR_POINT not present in TRAJET_ORDRE: {extra_points}")

    # check travel times for consecutive legs
    for a, b in zip(trajet_ordre, trajet_ordre[1:]):
        has = False
        if isinstance(temps_trajet_min, dict):
            if a in temps_trajet_min and isinstance(temps_trajet_min[a], dict) and b in temps_trajet_min[a]:
                has = True
            if b in temps_trajet_min and isinstance(temps_trajet_min[b], dict) and a in temps_trajet_min[b]:
                has = True
        if not has and default_travel_min is None:
            raise ValueError(f"Missing travel time between '{a}' and '{b}' and no default_travel_min provided")

    # collect passenger names
    stops = determine_stop_point_per_passenger(affectations_par_point)
    names = set(stops.keys())
    if Z_optimal is not None:
        try:
            z = int(Z_optimal)
        except Exception:
            raise ValueError("Z_optimal must be convertible to int")
        if len(names) != z:
            raise ValueError(f"Z_optimal={z} but found {len(names)} distinct passenger names in affectations")

    return None


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
            raw_trajet = json.load(f)
        with open(args.affect_file, "r", encoding="utf-8") as f:
            raw_affect = json.load(f)
        with open(args.times_file, "r", encoding="utf-8") as f:
            raw_temps = json.load(f)

        # normalize inputs to common internal names used by compute_schedule
        trajet = _normalize_trajet(raw_trajet)
        affect = _normalize_affectations(raw_affect)
        temps = _normalize_temps(raw_temps)

    # validate inputs before computing schedule
    validate_inputs(
        trajet,
        affect,
        temps,
        default_travel_min=args.default_travel_min,
    )

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


def determine_stop_point_per_passenger(affectations_par_point: Dict[str, Any]) -> Dict[str, Dict[str, Optional[str]]]:
    """Return a mapping for each passenger name to their boarding and alighting points.

    Output format:
      { 'Alice': {'board': 'R3', 'alight': None}, 'Bob': {'board': 'R1', 'alight': 'R5'}, ... }

    The function supports affectation formats where values are:
      - list of passenger names -> interpreted as boardings at that point
      - dict with keys 'board' and/or 'alight' mapping to lists of names
      - int -> treated as a count (ignored for passenger names)

    If a passenger appears multiple times for the same action, the first occurrence wins.
    """
    result: Dict[str, Dict[str, Optional[str]]] = {}

    for point, val in affectations_par_point.items():
        # dict with explicit board/alight lists
        if isinstance(val, dict):
            boards = val.get('board', [])
            alights = val.get('alight', [])
            if isinstance(boards, list):
                for name in boards:
                    if name not in result:
                        result[name] = {'board': point, 'alight': None}
                    else:
                        if result[name].get('board') is None:
                            result[name]['board'] = point
            if isinstance(alights, list):
                for name in alights:
                    if name not in result:
                        result[name] = {'board': None, 'alight': point}
                    else:
                        if result[name].get('alight') is None:
                            result[name]['alight'] = point
            continue

        # list of names -> boards
        if isinstance(val, list):
            for name in val:
                if name not in result:
                    result[name] = {'board': point, 'alight': None}
                else:
                    if result[name].get('board') is None:
                        result[name]['board'] = point
            continue

        # integer or unknown -> skip (no passenger names)
        continue

    return result


if __name__ == "__main__":
    main()

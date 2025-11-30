from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional, Tuple
import json
import logging
import os


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
    if isinstance(temps, dict) and a in temps and isinstance(temps[a], dict) and b in temps[a]:
        return int(temps[a][b])
    # try symmetric
    if isinstance(temps, dict) and b in temps and isinstance(temps[b], dict) and a in temps[b]:
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

    Returns a list of records per point with keys:
      point, arrival (ISO), departure (ISO), board, alight, cumulative, dwell_minutes, passengers_boarded
    """
    if not trajet_ordre:
        return []

    current_time = _parse_time(start_time)
    records: List[Dict[str, Any]] = []
    cumulative = 0

    prev_point = trajet_ordre[0]
    arrival = current_time
    board, alight, boarded_names = _count_board_alight(prev_point, affectations_par_point)
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

    for cur_point in trajet_ordre[1:]:
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
    df["arrival"] = pd.to_datetime(df["arrival"])
    df["departure"] = pd.to_datetime(df["departure"])
    return df


# Helper utilities added to be compatible with the merged branch architecture

def _extract_key_from_dict(obj: Dict[str, Any], candidates: List[str]):
    if not isinstance(obj, dict):
        return None
    for key in candidates:
        if key in obj:
            return obj[key]
    return None


def _normalize_trajet(obj: Any) -> List[str]:
    if isinstance(obj, list):
        return obj
    val = _extract_key_from_dict(obj, ["TRAJET_ORDRE", "trajet_ordre", "trajet", "TRJ"])
    if isinstance(val, list):
        return val
    raise ValueError("Unable to extract trajet_ordre from provided JSON file")


def _normalize_affectations(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        v = _extract_key_from_dict(obj, ["AFFECTATIONS_PAR_POINT", "affectations_par_point", "affectations", "AFFECTATIONS"])
        if v is not None:
            return v
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
    if not isinstance(trajet_ordre, list) or len(trajet_ordre) == 0:
        raise ValueError("TRAJET_ORDRE must be a non-empty list")
    if not isinstance(affectations_par_point, dict):
        raise ValueError("AFFECTATIONS_PAR_POINT must be a dictionary")

    extra_points = [p for p in affectations_par_point.keys() if p not in trajet_ordre]
    if extra_points:
        raise ValueError(f"Points in AFFECTATIONS_PAR_POINT not present in TRAJET_ORDRE: {extra_points}")

    for a, b in zip(trajet_ordre, trajet_ordre[1:]):
        has = False
        if isinstance(temps_trajet_min, dict):
            if a in temps_trajet_min and isinstance(temps_trajet_min[a], dict) and b in temps_trajet_min[a]:
                has = True
            if b in temps_trajet_min and isinstance(temps_trajet_min[b], dict) and a in temps_trajet_min[b]:
                has = True
        if not has and default_travel_min is None:
            raise ValueError(f"Missing travel time between '{a}' and '{b}' and no default_travel_min provided")

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


def determine_stop_point_per_passenger(affectations_par_point: Dict[str, Any]) -> Dict[str, Dict[str, Optional[str]]]:
    result: Dict[str, Dict[str, Optional[str]]] = {}

    for point, val in affectations_par_point.items():
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

        if isinstance(val, list):
            for name in val:
                if name not in result:
                    result[name] = {'board': point, 'alight': None}
                else:
                    if result[name].get('board') is None:
                        result[name]['board'] = point
            continue

        continue

    return result


def build_pickup_schedulera_output(trajet_ordre, affectations_par_point, temps_trajet_min, z_optimal=None):
    output = {
        "TRAJET_ORDRE": trajet_ordre,
        "AFFECTATIONS_PAR_POINT": affectations_par_point,
        "TEMPS_TRAJET_MIN": temps_trajet_min,
    }
    if z_optimal is not None:
        output["Z_optimal"] = z_optimal
    return output


def optimize_drop_off_points(passagers_groupe, method="exact", seuil=None):
    if not passagers_groupe:
        return []
    
    if len(passagers_groupe) == 1:
        return [{"point_arret": passagers_groupe[0].pos_arrivee, "passagers": [passagers_groupe[0]]}]
    
    if seuil is None:
        seuil = _calculer_seuil_destinations(passagers_groupe, method)
    
    points_arret = []
    passagers_restants = passagers_groupe.copy()
    
    while passagers_restants:
        if method == "exact":
            passager_ref = passagers_restants[0]
            groupe_arret = [passager_ref]
            passagers_restants.remove(passager_ref)
            
            i = 0
            while i < len(passagers_restants):
                passager = passagers_restants[i]
                dist = _distance_euclidienne(passager_ref.pos_arrivee, passager.pos_arrivee)
                if dist <= seuil:
                    groupe_arret.append(passager)
                    passagers_restants.remove(passager)
                else:
                    i += 1
            
            point_arret = _calculer_centroide_destinations([p.pos_arrivee for p in groupe_arret])
        else:
            passager_central = _trouver_passager_central_destinations(passagers_restants, seuil)
            groupe_arret = [passager_central]
            passagers_restants.remove(passager_central)
            
            voisins = []
            for passager in passagers_restants:
                dist = _distance_euclidienne(passager_central.pos_arrivee, passager.pos_arrivee)
                if dist <= seuil:
                    voisins.append(passager)
            
            groupe_arret.extend(voisins)
            for voisin in voisins:
                passagers_restants.remove(voisin)
            
            point_arret = passager_central.pos_arrivee
        
        points_arret.append({"point_arret": point_arret, "passagers": groupe_arret})
    
    return points_arret

def _calculer_seuil_destinations(passagers, method):
    distances = []
    for i in range(len(passagers)):
        for j in range(i + 1, len(passagers)):
            dist = _distance_euclidienne(passagers[i].pos_arrivee, passagers[j].pos_arrivee)
            distances.append(dist)
    
    if not distances:
        return 8.0
    
    if method == "exact":
        moyenne = sum(distances) / len(distances)
        return max(moyenne * 0.8, 5.0)
    else:
        distances.sort()
        percentile_75_idx = int(len(distances) * 0.75)
        return max(distances[min(percentile_75_idx, len(distances) - 1)], 8.0)

def _trouver_passager_central_destinations(passagers, seuil):
    max_voisins = -1
    passager_central = passagers[0]
    
    for passager in passagers:
        nb_voisins = 0
        for autre in passagers:
            if passager != autre:
                dist = _distance_euclidienne(passager.pos_arrivee, autre.pos_arrivee)
                if dist <= seuil:
                    nb_voisins += 1
        
        if nb_voisins > max_voisins:
            max_voisins = nb_voisins
            passager_central = passager
    
    return passager_central

def _calculer_centroide_destinations(destinations):
    if not destinations:
        return (0, 0)
    
    x_moy = sum(pos[0] for pos in destinations) / len(destinations)
    y_moy = sum(pos[1] for pos in destinations) / len(destinations)
    
    return (round(x_moy), round(y_moy))

def _distance_euclidienne(p1, p2):
    import math
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx**2 + dy**2)

def generate_complete_route(points_ramassage, points_arret, conducteur_pos):
    trajet_ordre = ["Depart"]
    affectations = {}
    temps_trajet = {"Depart": {}}
    
    for i, point in enumerate(points_ramassage):
        point_name = f"R{i+1}"
        trajet_ordre.append(point_name)
        passagers_names = [f"P{p.id}" for p in point['passagers']]
        affectations[point_name] = passagers_names
    
    for i, point in enumerate(points_arret):
        point_name = f"D{i+1}"
        trajet_ordre.append(point_name)
        passagers_names = [f"P{p.id}" for p in point['passagers']]
        affectations[point_name] = {"alight": passagers_names}
    
    for i in range(len(trajet_ordre) - 1):
        current_point = trajet_ordre[i]
        next_point = trajet_ordre[i + 1]
        
        if current_point == "Depart":
            current_pos = conducteur_pos
        elif current_point.startswith("R"):
            idx = int(current_point[1:]) - 1
            current_pos = points_ramassage[idx]['point_ramassage']
        elif current_point.startswith("D"):
            idx = int(current_point[1:]) - 1
            current_pos = points_arret[idx]['point_arret']
        
        if next_point.startswith("R"):
            idx = int(next_point[1:]) - 1
            next_pos = points_ramassage[idx]['point_ramassage']
        elif next_point.startswith("D"):
            idx = int(next_point[1:]) - 1
            next_pos = points_arret[idx]['point_arret']
        
        dist = _distance_euclidienne(current_pos, next_pos)
        
        if current_point not in temps_trajet:
            temps_trajet[current_point] = {}
        temps_trajet[current_point][next_point] = round(dist)
    
    return trajet_ordre, affectations, temps_trajet

def save_output_json(data, filepath="data/assignment.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Wrote pickup_schedulerA output to {filepath}")

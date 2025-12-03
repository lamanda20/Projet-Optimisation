import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.exact.clustering_exact import phase1_clustering_double
from algorithms.exact.selection_exact import selection_exact
from utils.distance import distance_grille

from pickup_scheduler import validate_inputs, determine_stop_point_per_passenger, compute_schedule


def make_passagers():
    # create 6 passagers with positions that form clusters
    # ids 1..6, names mapping below
    p1 = Passager(1, (0,0), (10,10))  # cluster A
    p2 = Passager(2, (1,0), (11,11))  # cluster A
    p3 = Passager(3, (0,1), (10,11))  # cluster A
    p4 = Passager(4, (50,50), (60,60))  # cluster B
    p5 = Passager(5, (51,50), (61,60))  # cluster B
    p6 = Passager(6, (200,200), (210,210))  # noise / far
    return [p1,p2,p3,p4,p5,p6]


def test_algos_to_pickup_end_to_end():
    """End-to-end test: prefer using existing data/assignment.json if present; otherwise generate assignment from algos."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assignment_path = os.path.join(repo_root, "data", "assignment.json")

    if os.path.exists(assignment_path):
        import json
        with open(assignment_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        trajet = d.get("TRAJET_ORDRE")
        affect = d.get("AFFECTATIONS_PAR_POINT")
        temps = d.get("TEMPS_TRAJET_MIN")
        z_optimal = d.get("Z_optimal")
    else:
        # fallback: generate synthetic data from algorithms
        passagers = make_passagers()
        conducteur = Conducteur(position=(0,0), capacite=4)

        # run exact clustering
        groupes = phase1_clustering_double(passagers, conducteur, R_dest=5.0, R_depart=5.0)
        assert isinstance(groupes, list)
        assert len(groupes) > 0

        # select best group using selection_exact (not strictly needed for assignment but kept for coverage)
        _ = selection_exact(groupes, conducteur)

        # build a simple AFFECTATIONS_PAR_POINT by assigning each group's passagers to a label R{i}
        affect = {}
        trajet = ["Depart"]
        temps = {}
        label_idx = 1
        name_map = {1: "P1", 2: "P2", 3: "P3", 4: "P4", 5: "P5", 6: "P6"}

        for g in groupes:
            label = f"R{label_idx}"
            trajet.append(label)
            names = [name_map[p.id] for p in g["passagers"]]
            affect[label] = names
            # compute travel times between previous point and this label using centre_depart
            if label_idx == 1:
                prev = "Depart"
                centre_prev = conducteur.position
            else:
                prev = f"R{label_idx-1}"
                prev_group = groupes[label_idx-2]
                centre_prev = prev_group["centre_depart"]

            centre_cur = g["centre_depart"]
            if prev not in temps:
                temps[prev] = {}
            mins = int(round(distance_grille(centre_prev, centre_cur)))
            temps[prev][label] = mins
            label_idx += 1

        z_optimal = sum(len(v) for v in affect.values())

    # validate and run pickup scheduler
    validate_inputs(trajet, affect, temps, Z_optimal=z_optimal, default_travel_min=5)

    stops = determine_stop_point_per_passenger(affect)
    assert isinstance(stops, dict)

    sched = compute_schedule(trajet, affect, temps, start_time="08:00", stop_time_per_passenger_min=1, default_travel_min=5)
    assert isinstance(sched, list)
    assert sched[-1]["cumulative"] == z_optimal


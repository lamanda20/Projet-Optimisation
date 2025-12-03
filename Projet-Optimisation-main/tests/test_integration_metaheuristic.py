import pytest
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.phase2_integrator import phase2_solve, generate_affectations_par_point
from pickup_scheduler import validate_inputs, compute_schedule, determine_stop_point_per_passenger


def test_integration_metaheuristic_simple():
    """Integration test: heuristic pipeline -> phase2 integrator -> pickup scheduler

    Creates 4 passengers arranged into two nearby clusters so the heuristic creates
    two pickup points. Verifies that all passengers are assigned, boarded and that
    the final cumulative count equals the number of passengers.
    """
    p1 = Passager(1, (1, 1), (5, 5))
    p2 = Passager(2, (1, 2), (6, 6))
    p3 = Passager(3, (10, 10), (12, 12))
    p4 = Passager(4, (10, 11), (13, 13))
    passagers = [p1, p2, p3, p4]

    conducteur = Conducteur((0, 0), capacite=4)

    # Run phase2 integrator with heuristic method
    trajet_ordre, temps_trajet, groupes = phase2_solve(passagers, conducteur, R_dest=5, R_depart=3, method='heuristic')

    # Basic sanity
    assert isinstance(trajet_ordre, list) and len(trajet_ordre) >= 1
    assert trajet_ordre[0] == 'Depart'

    # Generate affectations as Phase2 would
    affectations = generate_affectations_par_point(groupes, trajet_ordre)

    # Validate inputs (allow a default travel time if some edges missing)
    validate_inputs(trajet_ordre, affectations, temps_trajet, Z_optimal=len(passagers), default_travel_min=1)

    # Compute schedule
    schedule = compute_schedule(trajet_ordre, affectations, temps_trajet, start_time="08:00", stop_time_per_passenger_min=1, default_travel_min=1)

    # All passengers should be boarded exactly once
    total_boarded = sum(item['board'] for item in schedule)
    assert total_boarded == len(passagers)

    # Final cumulative must match total passengers
    assert schedule[-1]['cumulative'] == len(passagers)

    # Determine stop points mapping and ensure all expected passenger IDs present
    mapping = determine_stop_point_per_passenger(affectations)
    expected_names = {f"P{i}" for i in range(1, 5)}
    assert set(mapping.keys()) == expected_names

    # Each mapping should have a 'board' assigned (heuristic creates boardings)
    for v in mapping.values():
        assert v.get('board') is not None


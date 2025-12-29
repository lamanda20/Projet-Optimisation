from algorithms.heuristic.selection_heuristic import selection_heuristic
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic

if __name__ == "__main__":
    conducteur = Conducteur((30, 40), 5)
    passagers=[
        Passager(1, (10, 14), (82, 88)),
        Passager(2, (12, 18), (81, 86)),
        Passager(3, (15, 20), (84, 90)),
        Passager(4, (18, 22), (79, 85)),
        Passager(5, (17, 19), (83, 87)),
        Passager(6, (42, 48), (25, 33)),
        Passager(7, (45, 50), (22, 27)),
        Passager(8, (47, 55), (30, 28)),
        Passager(9, (52, 57), (33, 26)),
        Passager(10, (58, 60), (35, 30)),
        Passager(11, (70, 75), (55, 58)),
        Passager(12, (72, 78), (52, 56)),
        Passager(13, (76, 82), (59, 54)),
        Passager(14, (80, 85), (57, 60)),
        Passager(15, (78, 83), (53, 57)),
        Passager(16, (10, 15), (80, 85)),
        Passager(17, (12, 18), (82, 87)),
        Passager(18, (45, 50), (20, 25)),
        Passager(19, (47, 52), (22, 27)),
        Passager(20, (11, 16), (81, 86)),
    ]

    groupes = phase1_clustering_heuristic(passagers, conducteur, R_dest=20, R_depart=10)

    for i, groupe in enumerate(groupes):
        print(f"\nGroupe {i+1}:")
        print(f"  Taille: {groupe['taille']}")
        print(f"  Centre départ: {groupe['centre_depart']}")
        print(f"  Centre arrivée: {groupe['centre_arrivee']}")
        print(f"  Passagers: {[p.id for p in groupe['passagers']]}")

    groupe_optimale = selection_heuristic(groupes, conducteur)

    print("\nGroupe optimal :")
    for p in groupe_optimale:
        print(f"Passager {p.id} : départ {p.pos_depart}, arrivée {p.pos_arrivee}")

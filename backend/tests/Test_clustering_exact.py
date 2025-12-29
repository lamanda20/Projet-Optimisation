import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.exact.clustering_exact import phase1_clustering_double

if __name__ == "__main__":
    
    # Données de test 1
    passagers = [ 
        Passager(1, (10, 15), (80, 85)), 
        Passager(2, (12, 18), (82, 87)), 
        Passager(3, (45, 50), (20, 25)), 
        Passager(4, (47, 52), (22, 27)), 
        Passager(5, (11, 16), (81, 86)), 
        ]

    
    # Données de test 2
    passagers2 = [   
        Passager(1,  (10, 14), (82, 88)),
        Passager(2,  (12, 18), (81, 86)),
        Passager(3,  (15, 20), (84, 90)),
        Passager(4,  (18, 22), (79, 85)),
        Passager(5,  (17, 19), (83, 87)),
        Passager(6,  (42, 48), (25, 33)),
        Passager(7,  (45, 50), (22, 27)),
        Passager(8,  (47, 55), (30, 28)),
        Passager(9,  (52, 57), (33, 26)),
        Passager(10, (58, 60), (35, 30)),
        Passager(11, (70, 75), (55, 58)),
        Passager(12, (72, 78), (52, 56)),
        Passager(13, (76, 82), (59, 54)),
        Passager(14, (80, 85), (57, 60)),
        Passager(15, (78, 83), (53, 57)),
    ]

    
    conducteur = Conducteur((30, 40), 5)
    

    # Tests 1
    print("=== Phase 1 Clustering : Test 1 ===")
    
    # Exécution Phase 1
    groupes = phase1_clustering_double(passagers, conducteur, R_dest=20, R_depart=10)
    
    # Affichage résultats
    print(f"Nombre de groupes valides trouvés: {len(groupes)}")
    for i, groupe in enumerate(groupes):
        print(f"\nGroupe {i+1}:")
        print(f"  Taille: {groupe['taille']}")
        print(f"  Centre départ: {groupe['centre_depart']}")
        print(f"  Centre arrivée: {groupe['centre_arrivee']}")
        print(f"  Passagers: {[p.id for p in groupe['passagers']]}")



    
    # Tests 2
    print("=== Phase 1 Clustering : Test 2 ===")
    
    # Exécution Phase 1
    groupes2 = phase1_clustering_double(passagers2, conducteur, R_dest=20, R_depart=10)

    # Affichage résultats
    print(f"\nNombre de groupes valides trouvés (Test 2): {len(groupes2)}")
    for i, groupe in enumerate(groupes2):
        print(f"\nGroupe {i+1}:")
        print(f"  Taille: {groupe['taille']}")
        print(f"  Centre départ: {groupe['centre_depart']}")
        print(f"  Centre arrivée: {groupe['centre_arrivee']}")
        print(f"  Passagers: {[p.id for p in groupe['passagers']]}")

    


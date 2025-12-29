import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic

if __name__ == "__main__":
    # Création des passagers de test
    passagers = [
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
    
    # Création du conducteur
    conducteur = Conducteur((30, 40), 5)
    
    # Paramètres de clustering
    R_dest = 20.0
    R_depart = 10.0
    
    print("=== Test Phase 1 - Méthode Heuristique ===")
    
    print(f"Nombre de passagers: {len(passagers)}")
    print(f"Capacité conducteur: {conducteur.capacite}")
    print(f"R_dest: {R_dest}, R_depart: {R_depart}")
    
    # Exécution de la phase 1
    groupes = phase1_clustering_heuristic(passagers, conducteur, R_dest, R_depart)
    
    print(f"\nNombre de groupes formés: {len(groupes)}")
    
    for i, groupe in enumerate(groupes):
        print(f"\nGroupe {i+1}:")
        print(f"  Taille: {groupe['taille']}")
        print(f"  Centre départ: {groupe['centre_depart']}")
        print(f"  Centre arrivée: {groupe['centre_arrivee']}")
        print(f"  Passagers: {[p.id for p in groupe['passagers']]}")

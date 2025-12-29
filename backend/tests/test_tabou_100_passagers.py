import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.metaheuristic.selection_metaheuristic import (
    phase1_clustering_metaheuristic,
    calculer_cout_groupe
)
import random
import time

def generer_100_passagers() -> List[Passager]:
    """Générer 100 passagers répartis en zones géographiques"""
    passagers = []

    zones = [
        {"depart": (5, 15), "arrivee": (75, 85), "nb": 18},
        {"depart": (75, 85), "arrivee": (15, 25), "nb": 16},
        {"depart": (25, 35), "arrivee": (60, 70), "nb": 17},
        {"depart": (60, 70), "arrivee": (25, 35), "nb": 15},
        {"depart": (10, 20), "arrivee": (80, 90), "nb": 17},
        {"depart": (80, 90), "arrivee": (10, 20), "nb": 17}
    ]

    id_passager = 1
    for zone in zones:
        for _ in range(zone["nb"]):
            depart = (
                zone["depart"][0] + random.randint(-8, 8),
                zone["depart"][1] + random.randint(-8, 8)
            )
            arrivee = (
                zone["arrivee"][0] + random.randint(-8, 8),
                zone["arrivee"][1] + random.randint(-8, 8)
            )

            depart = (max(0, min(100, depart[0])), max(0, min(100, depart[1])))
            arrivee = (max(0, min(100, arrivee[0])), max(0, min(100, arrivee[1])))

            passagers.append(Passager(id_passager, depart, arrivee))
            id_passager += 1

    return passagers


def test_tabou_100_passagers():
    """Test pytest pour la recherche tabou avec 100 passagers"""
    print("=== TEST RECHERCHE TABOU – 100 PASSAGERS ===")

    passagers = generer_100_passagers()
    conducteur = Conducteur((50, 50), capacite=8)

    R_dest = 40.0
    R_depart = 35.0

    print(f"Passagers: {len(passagers)}")
    print(f"Conducteur: position={conducteur.position}, capacité={conducteur.capacite}")
    print(f"Paramètres: R_dest={R_dest}, R_depart={R_depart}")

    start_time = time.time()

    # 🔹 Recherche tabou uniquement
    meilleur_groupe = phase1_clustering_metaheuristic(
        passagers,
        conducteur,
        R_dest,
        R_depart
    )

    temps_exec = time.time() - start_time

    # Assertions pytest
    assert meilleur_groupe is not None, "Aucun groupe trouvé"
    assert meilleur_groupe['taille'] > 0, "Groupe vide"
    assert meilleur_groupe['taille'] <= conducteur.capacite, f"Groupe trop grand: {meilleur_groupe['taille']} > {conducteur.capacite}"
    assert temps_exec < 30.0, f"Trop lent: {temps_exec:.3f}s"
    
    cout = calculer_cout_groupe(meilleur_groupe, conducteur)

    print("\n✅ RÉSULTAT FINAL (TABOU)")
    print(f"Taille du groupe: {meilleur_groupe['taille']}")
    print(f"Coût (distance): {cout:.2f}")
    print(f"Temps d'exécution: {temps_exec:.3f}s")
    print(f"Passagers sélectionnés: {[p.id for p in meilleur_groupe['passagers']]}")


if __name__ == "__main__":
    test_tabou_100_passagers()

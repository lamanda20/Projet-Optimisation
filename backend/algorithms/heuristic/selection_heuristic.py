from typing import List, Dict
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille

def selection_heuristic(groupes_valides: List[Dict], conducteur: Conducteur) -> List[Passager]:

    # Aucun groupe valide
    if not groupes_valides:
        return []

    # Critère 1 : sélectionner les groupes avec le plus de passagers
    taille_max = max(g["taille"] for g in groupes_valides)
    groupes_max = [g for g in groupes_valides if g["taille"] == taille_max]

    # Critère 2 : parmi eux, choisir le groupe le plus proche du conducteur
    groupe_optimal = min(
        groupes_max,
        key=lambda g: distance_grille(conducteur.position, g["centre_depart"])
    )

    return groupe_optimal["passagers"]

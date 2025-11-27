from typing import List, Dict
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille

def selection_exact(groupes_valides: List[Dict], conducteur: Conducteur) -> List[Passager]:
    # Aucun groupe valide
    if not groupes_valides:
        return []

    # Critère 1 : trouver la taille maximale avec boucle
    taille_max = 0
    for g in groupes_valides:
        if g["taille"] > taille_max:
            taille_max = g["taille"]

    # Filtrer les groupes avec taille maximale
    groupes_max = []
    for g in groupes_valides:
        if g["taille"] == taille_max:
            groupes_max.append(g)

    # Critère 2 : trouver le groupe avec distance minimale au conducteur
    distance_min = float('inf')
    groupe_optimal = None

    for g in groupes_max:
        dist = distance_grille(conducteur.position, g["centre_depart"])
        if dist < distance_min:
            distance_min = dist
            groupe_optimal = g

    # Retourner les passagers du groupe optimal
    if groupe_optimal:
        return groupe_optimal["passagers"]
    else:
        return []
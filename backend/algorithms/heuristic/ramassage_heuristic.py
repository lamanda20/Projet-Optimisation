from typing import List, Dict, Tuple
from models.Passager import Passager
from utils.distance import distance_grille
import math

def ramassage_heuristic(passagers: List[Passager], max_walk_distance: float = 100.0) -> List[Dict]:
    """
    Détermine les points de ramassage avec contrainte de distance de marche maximale.
    
    Args:
        passagers: Liste des passagers du groupe optimal
        max_walk_distance: Distance maximale de marche autorisée (défaut: 100m)
    
    Returns:
        Liste des points de ramassage avec leurs passagers assignés
    """
    if not passagers:
        return []
    
    if len(passagers) == 1:
        return [{
            "point_ramassage": passagers[0].pos_depart,
            "passagers": [passagers[0]]
        }]
    
    # Utiliser la contrainte de marche comme seuil maximum
    seuil = min(_calculer_seuil_heuristique(passagers), max_walk_distance)
    
    points_ramassage = []
    passagers_restants = passagers.copy()
    
    while passagers_restants:
        # Trouver le passager avec le plus de voisins dans le seuil contraint
        passager_central = _trouver_passager_central(passagers_restants, seuil)
        groupe_ramassage = [passager_central]
        passagers_restants.remove(passager_central)
        
        # Ajouter seulement les voisins dans la distance de marche autorisée
        voisins = []
        for passager in passagers_restants:
            dist = distance_grille(passager_central.pos_depart, passager.pos_depart)
            if dist <= seuil:
                voisins.append(passager)
        
        groupe_ramassage.extend(voisins)
        for voisin in voisins:
            passagers_restants.remove(voisin)
        
        # Point de ramassage = position du passager central
        point_ramassage = passager_central.pos_depart
        
        points_ramassage.append({
            "point_ramassage": point_ramassage,
            "passagers": groupe_ramassage
        })
    
    return points_ramassage

def _calculer_seuil_heuristique(passagers: List[Passager]) -> float:
    """Calcule le seuil avec approche heuristique basée sur la densité"""
    distances = []
    
    for i in range(len(passagers)):
        for j in range(i + 1, len(passagers)):
            dist = distance_grille(passagers[i].pos_depart, passagers[j].pos_depart)
            distances.append(dist)
    
    if not distances:
        return 8.0
    
    distances.sort()
    # Seuil plus généreux basé sur le 75e percentile
    percentile_75_idx = int(len(distances) * 0.75)
    seuil_calcule = distances[min(percentile_75_idx, len(distances) - 1)]
    return max(seuil_calcule, 8.0)  # Au minimum 8.0 pour l'heuristique

def _trouver_passager_central(passagers: List[Passager], seuil: float) -> Passager:
    """Trouve le passager avec le plus de voisins dans le seuil"""
    max_voisins = -1
    passager_central = passagers[0]
    
    for passager in passagers:
        nb_voisins = 0
        for autre in passagers:
            if passager != autre:
                dist = distance_grille(passager.pos_depart, autre.pos_depart)
                if dist <= seuil:
                    nb_voisins += 1
        
        if nb_voisins > max_voisins:
            max_voisins = nb_voisins
            passager_central = passager
    
    return passager_central
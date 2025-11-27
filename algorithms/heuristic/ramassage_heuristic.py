from typing import List, Dict, Tuple
from models.Passager import Passager
from utils.distance import distance_grille
import math

def ramassage_heuristic(passagers: List[Passager]) -> List[Dict]:
    """
    Détermine les points de ramassage avec approche heuristique basée sur la densité.
    
    Args:
        passagers: Liste des passagers du groupe optimal
        seuil: Distance seuil pour regrouper les passagers (auto-calculé si None)
    
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
    
    # Auto-calcul du seuil avec approche heuristique
    seuil = _calculer_seuil_heuristique(passagers)
    
    points_ramassage = []
    passagers_restants = passagers.copy()
    
    while passagers_restants:
        # Trouver le passager avec le plus de voisins (densité maximale)
        passager_central = _trouver_passager_central(passagers_restants, seuil)
        groupe_ramassage = [passager_central]
        passagers_restants.remove(passager_central)
        
        # Ajouter tous les voisins dans le seuil
        voisins = []
        for passager in passagers_restants:
            dist = distance_grille(passager_central.pos_depart, passager.pos_depart)
            if dist <= seuil:
                voisins.append(passager)
        
        groupe_ramassage.extend(voisins)
        for voisin in voisins:
            passagers_restants.remove(voisin)
        
        # Point de ramassage = position du passager central (heuristique)
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
        return 1.0
    
    distances.sort()
    # Seuil = médiane des distances (plus robuste aux outliers)
    mediane_idx = len(distances) // 2
    return distances[mediane_idx]

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
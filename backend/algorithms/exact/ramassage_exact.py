from typing import List, Dict, Tuple
from models.Passager import Passager
from utils.distance import distance_grille

def ramassage_exact(passagers: List[Passager]) -> List[Dict]:
    """
    Détermine les points de ramassage optimaux pour un groupe de passagers.
    
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
    
    # Auto-calcul du seuil optimal
    seuil = _calculer_seuil_optimal(passagers)

    
    points_ramassage = []
    passagers_restants = passagers.copy()
    
    while passagers_restants:
        # Prendre le premier passager comme référence
        passager_ref = passagers_restants[0]
        groupe_ramassage = [passager_ref]
        passagers_restants.remove(passager_ref)
        
        # Trouver tous les passagers dans le seuil
        i = 0
        while i < len(passagers_restants):
            passager = passagers_restants[i]
            dist = distance_grille(passager_ref.pos_depart, passager.pos_depart)
            
            if dist <= seuil:
                groupe_ramassage.append(passager)
                passagers_restants.remove(passager)
            else:
                i += 1
        
        # Calculer le point de ramassage optimal (centroïde)
        point_ramassage = _calculer_centroide([p.pos_depart for p in groupe_ramassage])
        
        points_ramassage.append({
            "point_ramassage": point_ramassage,
            "passagers": groupe_ramassage
        })
    
    return points_ramassage

def _calculer_seuil_optimal(passagers: List[Passager]) -> float:
    """Calcule le seuil optimal basé sur la distribution des distances"""
    distances = []
    
    for i in range(len(passagers)):
        for j in range(i + 1, len(passagers)):
            dist = distance_grille(passagers[i].pos_depart, passagers[j].pos_depart)
            distances.append(dist)
    
    if not distances:
        return 5.0
    
    # Seuil plus généreux pour regrouper plus de passagers
    moyenne = sum(distances) / len(distances)
    return max(moyenne * 0.8, 5.0)  # Au minimum 5.0 pour garantir des regroupements

def _calculer_centroide(positions: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Calcule le centroïde d'un groupe de positions"""
    if not positions:
        return (0, 0)
    
    x_moy = sum(pos[0] for pos in positions) / len(positions)
    y_moy = sum(pos[1] for pos in positions) / len(positions)
    
    return (round(x_moy), round(y_moy))
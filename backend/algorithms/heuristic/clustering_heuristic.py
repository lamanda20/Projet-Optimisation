from typing import List, Dict, Tuple
import numpy as np
from sklearn.cluster import DBSCAN
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille
from utils.centroide import calculer_centroide_grille

def clustering_destinations_heuristic(passagers: List[Passager], R_dest: float) -> Dict[int, List[Passager]]:
    """Phase 1.1: Clustering destinations avec DBSCAN"""
    destinations = np.array([[p.pos_arrivee[0], p.pos_arrivee[1]] for p in passagers])
    
    labels_dest = DBSCAN(eps=R_dest, min_samples=2, metric='euclidean').fit_predict(destinations)
    
    clusters_dest = {}
    for i, label in enumerate(labels_dest):
        if label == -1:  # Bruit
            continue
        if label not in clusters_dest:
            clusters_dest[label] = []
        clusters_dest[label].append(passagers[i])
    
    return clusters_dest

def clustering_departs_heuristic(clusters_dest: Dict[int, List[Passager]], R_depart: float, capacite: int) -> List[Dict]:
    """Phase 1.2: Clustering départs par cluster destination avec DBSCAN"""
    groupes_valides = []
    
    for cluster_id, passagers_cluster in clusters_dest.items():
        if len(passagers_cluster) < 2:
            continue
        
        departs = np.array([[p.pos_depart[0], p.pos_depart[1]] for p in passagers_cluster])
        
        labels_depart = DBSCAN(eps=R_depart, min_samples=2, metric='euclidean').fit_predict(departs)
        
        for sous_id in np.unique(labels_depart):
            if sous_id == -1:
                continue
            
            passagers_sous = [passagers_cluster[i] 
                            for i, lab in enumerate(labels_depart) 
                            if lab == sous_id]
            
            n = len(passagers_sous)
            if 2 <= n <= capacite:
                centre_depart = calculer_centroide_grille([p.pos_depart for p in passagers_sous])
                centre_arrivee = calculer_centroide_grille([p.pos_arrivee for p in passagers_sous])
                
                groupes_valides.append({
                    'passagers': passagers_sous,
                    'taille': n,
                    'centre_depart': centre_depart,
                    'centre_arrivee': centre_arrivee
                })
    
    return groupes_valides

def phase1_clustering_heuristic(passagers: List[Passager], conducteur: Conducteur, 
                               R_dest: float, R_depart: float) -> List[Dict]:
    """Phase 1 complète: Clustering heuristique avec DBSCAN"""
    clusters_dest = clustering_destinations_heuristic(passagers, R_dest)
    groupes_valides = clustering_departs_heuristic(clusters_dest, R_depart, conducteur.capacite)
    return groupes_valides


def nearest_neighbor_tsp(points: List[Tuple[int, int]], start_point: Tuple[int, int]) -> List[int]:
    """
    TSP solver using Nearest Neighbor heuristic
    
    Args:
        points: Liste des coordonnées (x, y) des points de ramassage
        start_point: Coordonnée du point de départ
    
    Returns:
        Ordre des indices des points (0-indexed) selon l'heuristique du plus proche voisin
    """
    if len(points) <= 1:
        return list(range(len(points)))
    
    unvisited = set(range(len(points)))
    current_pos = start_point
    order = []
    
    while unvisited:
        # Trouver le point non visité le plus proche
        nearest_idx = min(unvisited, key=lambda idx: distance_grille(current_pos, points[idx]))
        order.append(nearest_idx)
        current_pos = points[nearest_idx]
        unvisited.remove(nearest_idx)
    
    return order


def generate_trajet_and_temps_heuristic(groupes: List[Dict], conducteur: Conducteur) -> Tuple[List[str], Dict[str, Dict[str, int]]]:
    """
    Génère TRAJET_ORDRE et TEMPS_TRAJET_MIN à partir des groupes de clustering (méthode heuristique)
    
    Args:
        groupes: Liste des groupes valides du clustering
        conducteur: Objet conducteur (pour la position de départ)
    
    Returns:
        Tuple (TRAJET_ORDRE, TEMPS_TRAJET_MIN)
    """
    if not groupes:
        return ["Depart"], {}
    
    # Récupérer les centres de ramassage uniques
    centres_ramassage = {}
    for idx, groupe in enumerate(groupes):
        centre_key = f"R{idx + 1}"
        centres_ramassage[centre_key] = groupe['centre_depart']
    
    # Résoudre TSP avec heuristique du plus proche voisin
    points_coords = list(centres_ramassage.values())
    order_indices = nearest_neighbor_tsp(points_coords, conducteur.position)
    
    # Construire TRAJET_ORDRE
    trajet_ordre = ["Depart"]
    ordered_centres = []
    for idx in order_indices:
        centre_key = f"R{idx + 1}"
        trajet_ordre.append(centre_key)
        ordered_centres.append((centre_key, centres_ramassage[centre_key]))
    
    # Construire TEMPS_TRAJET_MIN
    temps_trajet = {}
    
    if len(trajet_ordre) > 1:
        # Temps depuis Depart vers premier point
        depart_pos = conducteur.position
        first_centre_key = trajet_ordre[1]
        first_centre_pos = centres_ramassage[first_centre_key]
        temps_depart = round(distance_grille(depart_pos, first_centre_pos))
        
        temps_trajet["Depart"] = {first_centre_key: temps_depart}
        
        # Temps entre les points de ramassage successifs
        for i in range(len(trajet_ordre) - 2):
            current_key = trajet_ordre[i + 1]
            next_key = trajet_ordre[i + 2]
            current_pos = centres_ramassage[current_key]
            next_pos = centres_ramassage[next_key]
            travel_time = round(distance_grille(current_pos, next_pos))
            
            if current_key not in temps_trajet:
                temps_trajet[current_key] = {}
            temps_trajet[current_key][next_key] = travel_time
    
    return trajet_ordre, temps_trajet
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict, Tuple
from itertools import permutations
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille
from utils.centroide import calculer_centroide_grille

def clustering_destinations(passagers: List[Passager], R_dest: float) -> List[List[Passager]]:
    """Phase 1.1: Clustering par destinations proches"""
    clusters_destinations = []
    passagers_traites = set()
    
    for p in passagers:
        if p.id in passagers_traites:
            continue
            
        cluster = [p]
        passagers_traites.add(p.id)
        
        for q in passagers:
            if q.id not in passagers_traites:
                dist = distance_grille(p.pos_arrivee, q.pos_arrivee)
                if dist <= R_dest:
                    cluster.append(q)
                    passagers_traites.add(q.id)
        
        if len(cluster) >= 2:
            clusters_destinations.append(cluster)
    
    return clusters_destinations

def clustering_departs(clusters_destinations: List[List[Passager]], R_depart: float, capacite: int) -> List[Dict]:
    """Phase 1.2: Clustering par départs proches dans chaque cluster destination"""
    groupes_valides = []
    
    for cluster_dest in clusters_destinations:
        passagers_traites_depart = set()
        
        for p in cluster_dest:
            if p.id in passagers_traites_depart:
                continue
                
            sous_groupe = [p]
            passagers_traites_depart.add(p.id)
            
            for q in cluster_dest:
                if q.id not in passagers_traites_depart:
                    dist = distance_grille(p.pos_depart, q.pos_depart)
                    if dist <= R_depart:
                        sous_groupe.append(q)
                        passagers_traites_depart.add(q.id)
            
            n = len(sous_groupe)
            if 2 <= n <= capacite:
                groupes_valides.append({
                    'passagers': sous_groupe,
                    'taille': n,
                    'centre_depart': calculer_centroide_grille([p.pos_depart for p in sous_groupe]),
                    'centre_arrivee': calculer_centroide_grille([p.pos_arrivee for p in sous_groupe])
                })
    
    return groupes_valides

def phase1_clustering_double(passagers: List[Passager], conducteur: Conducteur, 
                           R_dest: float, R_depart: float) -> List[Dict]:
    """
    Phase 1 complète: Clustering double (destinations puis départs)
    
    Returns: Liste des groupes valides avec leurs métadonnées
    """
    # 1.1 Clustering destinations
    clusters_destinations = clustering_destinations(passagers, R_dest)
    
    # 1.2 Clustering départs
    groupes_valides = clustering_departs(clusters_destinations, R_depart, conducteur.capacite)
    
    return groupes_valides


def tsp_exact_solver(points: List[Tuple[int, int]], start_point: Tuple[int, int]) -> List[int]:
    """
    Exact TSP solver using brute force permutations
    
    Args:
        points: Liste des coordonnées (x, y) des points de ramassage
        start_point: Coordonnée du point de départ (Depart)
    
    Returns:
        Ordre des indices des points (0-indexed) qui minimise la distance totale
    """
    if len(points) <= 1:
        return list(range(len(points)))
    
    min_distance = float('inf')
    best_order = None
    
    # Brute force: essayer toutes les permutations
    for perm in permutations(range(len(points))):
        total_distance = distance_grille(start_point, points[perm[0]])
        
        for i in range(len(perm) - 1):
            total_distance += distance_grille(points[perm[i]], points[perm[i+1]])
        
        if total_distance < min_distance:
            min_distance = total_distance
            best_order = perm
    
    return list(best_order) if best_order else list(range(len(points)))


def generate_trajet_and_temps_exact(groupes: List[Dict], conducteur: Conducteur) -> Tuple[List[str], Dict[str, Dict[str, int]]]:
    """
    Génère TRAJET_ORDRE et TEMPS_TRAJET_MIN à partir des groupes de clustering
    
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
    
    # Résoudre TSP pour l'ordre optimal des points de ramassage
    points_coords = list(centres_ramassage.values())
    order_indices = tsp_exact_solver(points_coords, conducteur.position)
    
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
from typing import List, Dict
import numpy as np
from sklearn.cluster import DBSCAN
from models.Passager import Passager
from models.Conducteur import Conducteur
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
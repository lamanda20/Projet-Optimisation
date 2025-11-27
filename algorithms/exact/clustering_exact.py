import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict
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
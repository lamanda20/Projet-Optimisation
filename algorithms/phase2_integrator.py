"""
Phase 2 Integrator - Génère TRAJET_ORDRE et TEMPS_TRAJET_MIN
Consolide les résultats des deux méthodes (exacte et heuristique)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple, Optional, Literal
import json
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.exact.clustering_exact import (
    phase1_clustering_double,
    generate_trajet_and_temps_exact
)
from algorithms.heuristic.clustering_heuristic import (
    phase1_clustering_heuristic,
    generate_trajet_and_temps_heuristic
)


def phase2_solve(
    passagers: List[Passager],
    conducteur: Conducteur,
    R_dest: float,
    R_depart: float,
    method: Literal["exact", "heuristic"] = "heuristic"
) -> Tuple[List[str], Dict[str, Dict[str, int]], List[Dict]]:
    """
    Résout la Phase 2: Clustering + TSP pour générer trajet et temps
    
    Args:
        passagers: Liste des passagers
        conducteur: Objet conducteur
        R_dest: Rayon de clustering pour destinations
        R_depart: Rayon de clustering pour départs
        method: "exact" (brute force TSP) ou "heuristic" (nearest neighbor)
    
    Returns:
        Tuple (TRAJET_ORDRE, TEMPS_TRAJET_MIN, groupes)
    """
    if method == "exact":
        groupes = phase1_clustering_double(passagers, conducteur, R_dest, R_depart)
        trajet_ordre, temps_trajet = generate_trajet_and_temps_exact(groupes, conducteur)
    elif method == "heuristic":
        groupes = phase1_clustering_heuristic(passagers, conducteur, R_dest, R_depart)
        trajet_ordre, temps_trajet = generate_trajet_and_temps_heuristic(groupes, conducteur)
    else:
        raise ValueError(f"Method must be 'exact' or 'heuristic', got {method}")
    
    return trajet_ordre, temps_trajet, groupes


def generate_affectations_par_point(
    groupes: List[Dict],
    trajet_ordre: List[str]
) -> Dict[str, List[str]]:
    """
    Génère AFFECTATIONS_PAR_POINT à partir des groupes
    
    Args:
        groupes: Liste des groupes valides
        trajet_ordre: Ordre des points de ramassage
    
    Returns:
        Dict mappant points -> liste des noms de passagers
    """
    affectations = {}
    
    for idx, groupe in enumerate(groupes):
        centre_key = f"R{idx + 1}"
        if centre_key in trajet_ordre:
            # Récupérer les noms/IDs des passagers
            passager_names = [f"P{p.id}" for p in groupe['passagers']]
            affectations[centre_key] = passager_names
    
    return affectations


def export_phase2_json(
    output_path: str,
    trajet_ordre: List[str],
    affectations: Dict[str, List[str]],
    temps_trajet: Dict[str, Dict[str, int]],
    Z_optimal: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> None:
    """
    Exporte les résultats de Phase 2 en JSON
    
    Args:
        output_path: Chemin du fichier JSON de sortie
        trajet_ordre: TRAJET_ORDRE
        affectations: AFFECTATIONS_PAR_POINT
        temps_trajet: TEMPS_TRAJET_MIN
        Z_optimal: Nombre total de passagers (optionnel)
        metadata: Métadonnées supplémentaires
    """
    output = {
        "TRAJET_ORDRE": trajet_ordre,
        "AFFECTATIONS_PAR_POINT": affectations,
        "TEMPS_TRAJET_MIN": temps_trajet
    }
    
    if Z_optimal is not None:
        output["Z_optimal"] = Z_optimal
    
    if metadata:
        output["metadata"] = metadata
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Exported Phase 2 results to {output_path}")


def load_phase2_json(file_path: str) -> Tuple[List[str], Dict[str, List[str]], Dict[str, Dict[str, int]], Optional[int]]:
    """
    Charge les résultats Phase 2 depuis un JSON
    
    Returns:
        Tuple (TRAJET_ORDRE, AFFECTATIONS_PAR_POINT, TEMPS_TRAJET_MIN, Z_optimal)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    trajet = data.get("TRAJET_ORDRE", [])
    affect = data.get("AFFECTATIONS_PAR_POINT", {})
    temps = data.get("TEMPS_TRAJET_MIN", {})
    z_opt = data.get("Z_optimal")
    
    return trajet, affect, temps, z_opt


if __name__ == "__main__":
    print("Phase 2 Integrator - Exemple d'utilisation")
    print("Cet module consolide les résultats de clustering et TSP")
    print("Pour utiliser: from algorithms.phase2_integrator import phase2_solve")

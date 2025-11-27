from typing import List, Dict, Any
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille
import logging


def selection_exact(groupes_valides: List[Dict[str, Any]], conducteur: Conducteur) -> List[Passager]:
    """
    Select the best group from `groupes_valides` for the given conducteur.

    Selection rules (in order):
    1. Keep only groups with the maximum 'taille'.
    2. Among those, select the group whose 'centre_depart' is closest to conducteur.position
       (uses utils.distance.distance_grille). If centre_depart is missing/malformed, that group
       is treated as having infinite distance and thus deprioritized.

    Expected group structure:
      {
        'passagers': List[Passager],
        'taille': int,
        'centre_depart': (x, y)  # optional but recommended
      }

    Returns the list of Passager objects for the chosen group, or an empty list if none.
    """
    if not groupes_valides:
        return []

    # Filter out malformed groups (must have integer 'taille' and a 'passagers' list)
    groupes_clean: List[Dict[str, Any]] = []
    for g in groupes_valides:
        try:
            taille = g.get("taille")
            passagers = g.get("passagers")
        except Exception:
            continue
        if not isinstance(taille, int):
            logging.debug("Ignoring group without integer 'taille': %s", g)
            continue
        if not isinstance(passagers, list):
            logging.debug("Ignoring group with invalid 'passagers' field: %s", g)
            continue
        groupes_clean.append(g)

    if not groupes_clean:
        return []

    # Find maximum size
    taille_max = max(g["taille"] for g in groupes_clean)
    groupes_max = [g for g in groupes_clean if g["taille"] == taille_max]

    # Helper to compute distance; malformed centre -> +inf
    def _dist_to_conducteur(g: Dict[str, Any]) -> float:
        centre = g.get("centre_depart")
        if centre is None:
            return float("inf")
        try:
            # ensure centre is a tuple-like of numbers
            return float(distance_grille(conducteur.position, tuple(centre)))
        except Exception:
            logging.debug("Invalid centre_depart for group (treated as inf): %s", g)
            return float("inf")

    # Choose the group with minimal distance (ties broken by order)
    groupe_optimal = min(groupes_max, key=_dist_to_conducteur)

    # Return the passagers list (ensured to be a list earlier)
    return groupe_optimal.get("passagers", [])

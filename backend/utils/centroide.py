from typing import Tuple
from typing import List

def calculer_centroide_grille(positions: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Calcule le centroïde et le borne à [0, 100]"""
    x_moy = round(sum(p[0] for p in positions) / len(positions))
    y_moy = round(sum(p[1] for p in positions) / len(positions))
    return (max(0, min(100, x_moy)), max(0, min(100, y_moy)))
import math
from typing import List, Tuple, Dict

def distance_grille(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """Distance euclidienne sur grille discrète"""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx**2 + dy**2)
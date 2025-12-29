from typing import Tuple

class Conducteur:
    def __init__(self, position: Tuple[int, int], capacite: int):
        self.position = position
        self.capacite = capacite
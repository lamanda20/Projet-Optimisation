from typing import Tuple

class Passager:
    def __init__(self, id: int, pos_depart: Tuple[int, int], pos_arrivee: Tuple[int, int]):
        self.id = id
        self.pos_depart = pos_depart
        self.pos_arrivee = pos_arrivee

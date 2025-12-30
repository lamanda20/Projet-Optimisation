"""
Utility to generate clustered passengers for tests and examples.
Generates passengers grouped around departure/arrival centers with variable cluster sizes (6-9).
Defaults: R_depart=10, R_arrivee=30

Usage: run as script to print / save JSON for sample sizes 10,20,50,100
"""
import random
import json
from typing import List, Tuple


class Passager:
    def __init__(self, id: int, pos_depart: Tuple[int, int], pos_arrivee: Tuple[int, int]):
        self.id = id
        self.pos_depart = pos_depart
        self.pos_arrivee = pos_arrivee

    def __repr__(self):
        return f"P{self.id}(D={self.pos_depart}, A={self.pos_arrivee})"

    def to_dict(self):
        return {
            "id": self.id,
            "pos_depart": self.pos_depart,
            "pos_arrivee": self.pos_arrivee,
        }


def point_dans_rayon(centre: Tuple[int, int], rayon: int) -> Tuple[int, int]:
    """Return a point (x,y) within square radius around centre (inclusive).
    Values are clipped to 0..99 to stay in grid bounds.
    """
    x = centre[0] + random.randint(-rayon, rayon)
    y = centre[1] + random.randint(-rayon, rayon)
    # clip to grid 0..99
    x = max(0, min(99, x))
    y = max(0, min(99, y))
    return (x, y)


def generer_passagers_clusterises(
    nb_passagers: int,
    rayon_depart: int = 10,
    rayon_arrivee: int = 30,
    cluster_sizes: List[int] = None,
    seed: int = None,
) -> List[Passager]:
    """Generate clustered passengers.

    - Each cluster gets a random size chosen from cluster_sizes (default [6,7,8,9]).
    - For each cluster we pick a departure center and an arrival center (both in 0..99 grid).
    - Passengers are placed with random offsets inside the respective radii.
    - Stops when nb_passagers have been generated.
    """
    if cluster_sizes is None:
        cluster_sizes = [6, 7, 8, 9]

    if seed is not None:
        random.seed(seed)

    passagers: List[Passager] = []
    id_passager = 1

    # To avoid too many tiny clusters in a row, we select cluster centers that are reasonably separated
    centers_taken = []

    while len(passagers) < nb_passagers:
        # choose a cluster size
        taille_cluster = random.choice(cluster_sizes)
        taille_cluster = min(taille_cluster, nb_passagers - len(passagers))

        # pick departure and arrival centers
        # ensure centers are not too close to previously chosen ones (for variety)
        # try a few times to find a center sufficiently separated
        def pick_center(existing, attempts=20, min_separation=15):
            for _ in range(attempts):
                c = (random.randint(5, 94), random.randint(5, 94))
                if all(((c[0]-e[0])**2 + (c[1]-e[1])**2) >= min_separation**2 for e in existing):
                    return c
            return (random.randint(5, 94), random.randint(5, 94))

        centre_depart = pick_center(centers_taken)
        # for arrival center we allow it to be different; can be far from depart
        centre_arrivee = pick_center(centers_taken + [centre_depart])

        centers_taken.append(centre_depart)
        centers_taken.append(centre_arrivee)

        for _ in range(taille_cluster):
            pos_depart = point_dans_rayon(centre_depart, rayon_depart)
            pos_arrivee = point_dans_rayon(centre_arrivee, rayon_arrivee)

            passagers.append(Passager(id_passager, pos_depart, pos_arrivee))
            id_passager += 1

            if len(passagers) >= nb_passagers:
                break

    return passagers


def _example_and_maybe_save(n, filename=None, seed=None):
    p = generer_passagers_clusterises(n, rayon_depart=10, rayon_arrivee=30, seed=seed)
    print(f"Generated {len(p)} passengers (sample): {p[:3]} ... {p[-1]}")
    if filename:
        data = [pp.to_dict() for pp in p]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved to {filename}")
    return p


if __name__ == '__main__':
    print("Generating sample datasets:\n")
    p10 = _example_and_maybe_save(10, filename='data/passagers_10.json', seed=1)
    p20 = _example_and_maybe_save(20, filename='data/passagers_20.json', seed=2)
    p50 = _example_and_maybe_save(50, filename='data/passagers_50.json', seed=3)
    p100 = _example_and_maybe_save(100, filename='data/passagers_100.json', seed=4)
    print('\nDone')

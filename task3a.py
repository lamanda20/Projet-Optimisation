import json
import os

def build_task3a_output(trajet_ordre, affectations_par_point, temps_trajet_min, z_optimal=None):

    output = {
        "TRAJET_ORDRE": trajet_ordre,
        "AFFECTATIONS_PAR_POINT": affectations_par_point,
        "TEMPS_TRAJET_MIN": temps_trajet_min
    }

    if z_optimal is not None:
        output["Z_optimal"] = z_optimal

    return output


def save_output_json(data, filepath="data/assignment.json"):

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✔ Fichier généré : {filepath}")


if __name__ == "__main__":
    # ⚠️ EXEMPLE TEMPORAIRE (à remplacer par vos vraies valeurs)
    trajet_ordre = ["Depart", "R3", "R1", "R5"]

    affectations_par_point = {
        "R3": ["Alice", "Charlie"],
        "R1": ["Bob"],
        "R5": ["Diane", "Eve"]
    }

    temps_trajet_min = {
        "Depart": {"R3": 5},
        "R3": {"R1": 7},
        "R1": {"R5": 10}
    }

    z_optimal = 5

    data = build_task3a_output(
        trajet_ordre,
        affectations_par_point,
        temps_trajet_min,
        z_optimal
    )

    save_output_json(data)

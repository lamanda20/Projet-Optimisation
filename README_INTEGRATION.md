README d'intégration — Projet d'Optimisation
=============================================

But
---
Ce document résume l'état actuel du projet, précise ce qui est implémenté, ce qui manque pour chaque partie (Partie 1, Partie 2, Tâche 3A, Tâche 3B) et décrit le contrat d'échange attendu entre les tâches. Il liste aussi les fonctions à implémenter/adapter et les tests disponibles.

Résumé rapide (état actuel)
--------------------------
- Partie 1 (optimisation du nombre de passagers) : logique/algorithme présent (dans `algorithms/`), produit un entier Z_optimal (attendu). ✅
- Partie 2 (affectation + trajet) : algorithmes heuristiques et exacts présents (`algorithms/exact`, `algorithms/heuristic`) pour proposer groupes et centres ; il manque la partie qui construit et normalise la sortie finale (points de ramassage visités et `v_r`) si nécessaire. ⚠️
- Tâche 3A (Consolidation des affectations) : NON fournie (attendue de votre collègue) — doit produire `AFFECTATIONS_PAR_POINT` et `TRAJET_ORDRE` + `TEMPS_TRAJET_MIN` en format convenu. ❌
- Tâche 3B (votre partie : détermination des points d'arrêt par passager + planning horaire) : implémentée dans `task3b.py` avec :
  - `compute_schedule(...)` — calcule horaires et cumul de passagers, compatible avec les structures normalisées.
  - `determine_stop_point_per_passenger(...)` — retourne, pour chaque passager, point de montée et descente (si fourni).
  - `validate_inputs(...)` — vérifie la cohérence des données entrantes (points hors-trajet, temps manquants, Z_optimal mismatch).
  - Tests unitaires et d'intégration ajoutés sous `tests/`. ✅

Contrat d'entrée (ce que doit livrer Tâche 3A => consommé par Tâche 3B)
------------------------------------------------------------------------
Tâche 3A doit livrer (fichier JSON ou objets équivalents) :

1) TRAJET_ORDRE (list of strings)
   - Exemple : ["Depart", "R3", "R1", "R5"]
   - Signification : ordre exact des points que le conducteur va visiter.

2) AFFECTATIONS_PAR_POINT (dict)
   - Clé : nom du point (string), Valeur : l'une de :
     - list[str] : liste des noms des passagers qui montent à ce point (ex: ["Alice","Bob"]) ;
     - dict{"board": list[str], "alight": list[str]} : remontées/descendes explicites ;
     - int : nombre de passagers (utilisé seulement si on ne fournit pas de noms) — NOTE : Tâche 3B nécessite normalement des noms pour produire les arrêts par passager.
   - Exemple : {"R3": ["Alice","Charlie"], "R1": ["Bob"], "R5": ["Diane","Eve"]}

3) TEMPS_TRAJET_MIN (dict de dict)
   - Structure: { pointA: { pointB: minutes, ... }, ... }
   - Supporte asymétrie ; s'il manque une entrée pour une paire consécutive, `default_travel_min` doit être fourni.
   - Exemple : {"Depart": {"R3": 5}, "R3": {"R1": 7}, "R1": {"R5": 10}}

4) Optionnel : Z_optimal (int)
   - Le nombre total de passagers retenus (issu de Partie 1). Si fourni, `validate_inputs` vérifie que le nombre de noms distincts dans AFFECTATIONS_PAR_POINT correspond.

Forme JSON minimale attendue (exemple)
-------------------------------------
{
  "TRAJET_ORDRE": ["Depart","R3","R1","R5"],
  "AFFECTATIONS_PAR_POINT": {"R3": ["Alice","Charlie"], "R1": ["Bob"], "R5": ["Diane","Eve"]},
  "TEMPS_TRAJET_MIN": {"Depart": {"R3": 5}, "R3": {"R1": 7}, "R1": {"R5": 10}},
  "Z_optimal": 5
}

Points d'intégration et validations en place dans `task3b.py`
-------------------------------------------------------------
- Normalisation des clés JSON entrantes via `_normalize_trajet/_normalize_affectations/_normalize_temps`.
- `validate_inputs(trajet, affect, temps, Z_optimal=None, default_travel_min=None)` lève `ValueError` si :
  - `TRAJET_ORDRE` n'est pas une liste non-vide,
  - une clef dans `AFFECTATIONS_PAR_POINT` n'appartient pas à `TRAJET_ORDRE`,
  - pour une étape consécutive du trajet il manque le temps et `default_travel_min` n'est pas fourni,
  - `Z_optimal` est fourni mais ne correspond pas au nombre de noms distincts.
- `determine_stop_point_per_passenger(affect)` produit le mapping passager->(board,alight).
- `compute_schedule(...)` produit une liste d'entrées horodatées (arrival/departure/board/alight/cumulative/dwell_minutes).

Tests fournis
-------------
- `tests/test_task3b.py` : tests unitaires pour `determine_stop_point_per_passenger` (formats liste/dict/int).
- `tests/test_integration_task3b.py` : tests d'intégration pour `validate_inputs` et `compute_schedule`.

Commandes utiles (PowerShell)
-----------------------------
- Lancer tous les tests :
```powershell
py -m pytest -q
```
- Lancer seulement le test d'intégration Task3B :
```powershell
py -m pytest tests/test_integration_task3b.py -q
```
- Lancer la démo CLI de Task3B :
```powershell
py run_demo.py
```

Manque / tâches à accomplir par partie
-------------------------------------
- Partie 1 :
  - Livrer/enregistrer `Z_optimal` (int) si disponible. (Si non fourni, Task3B fonctionne sans mais perd la vérification).
  - (Optionnel) ajouter un export JSON standardisé contenant Z_optimal.

- Partie 2 :
  - Fournir l'ordre final des points visités `TRAJET_ORDRE` (résultat TSP / route optimisée). Cette info est critique.
  - Fournir la liste des points à visiter `v_r==1` sous une forme exploitable (souvent équivalente à la liste des clés d'AFFECTATIONS_PAR_POINT mais doit être cohérente avec TRAJET_ORDRE).
  - (Optionnel) centraliser `TEMPS_TRAJET_MIN` calculés (ou laisser Tâche3A le faire).

- Tâche 3A (Consolidation des affectations) — À FAIRE (par votre collègue) :
  - Obligations : produire un JSON ou dict Python contenant exactement :
    - `TRAJET_ORDRE` (list[str])
    - `AFFECTATIONS_PAR_POINT` (dict comme décrit)
    - `TEMPS_TRAJET_MIN` (nested dict) ou indiquer `default_travel_min`
    - (Optionnel) `Z_optimal`
  - Règles :
    - Toutes les clefs dans `AFFECTATIONS_PAR_POINT` doivent exister dans `TRAJET_ORDRE`.
    - Lorsque les noms des passagers sont fournis, ils doivent être uniques (ou basés sur un identifiant si vous utilisez des objets). Si vous utilisez des objets `Passager`, fournir un champ `id` et/ou `name` et normaliser via Tâche3A.
  - Format de sortie attendu par Tâche3B : JSON simple (voir exemple ci-dessus).

- Tâche 3B (implémentée) :
  - Détermine pour chaque passager son point de montée/descente (`determine_stop_point_per_passenger`).
  - Calcule les horaires et produce la sortie JSON/CSV (`compute_schedule` + `to_dataframe`).

Propositions d'améliorations/étapes recommandées (prioritaires)
----------------------------------------------------------------
1. Rédiger et committer ce README (fichier créé : `README_INTEGRATION.md`). ✅
2. Faire produire par la personne en charge de Tâche 3A un exemple JSON conforme (avec noms, TRAJET_ORDRE et TEMPS_TRAJET_MIN) et le placer dans `data/` pour tests et intégration. (Priorité haute)
3. Ajouter un adaptateur si Tâche 3A renvoie des objets `Passager` (mapper `Passager.id` ou `Passager.name` aux clés attendues). (Priorité moyenne)
4. Ajouter un mode `lenient` plus global pour `validate_inputs` (pourtransformer certains errors en warnings quand souhaité).
5. Ajouter CI (GitHub Actions) pour exécuter `pytest` sur chaque PR. (Priorité haute)

Exemple d'appel (workflow d'intégration)
---------------------------------------
1. Partie1 et Partie2 produisent leurs résultats.
2. Tâche3A consolide en JSON (voir forme ci-dessus) et place le fichier `data/assignment.json`.
3. Tâche3B (vous) exécute :
```powershell
py task3b.py --trajet-file data/trajet.json --affect-file data/assignment.json --times-file data/times.json
```
Si la validation échoue, `task3b.py` lève une `ValueError` avec un message précis expliquant la correction nécessaire.

Contact et responsabilités
--------------------------
- Tâche 3A (consolidation) : responsable = votre collègue (doit respecter le contrat ci-dessus).
- Tâche 3B : responsable = vous (implémentation déjà en place dans `task3b.py` ; assurer l'intégration finale et tests).

Si vous voulez, je peux :
- Commiter et pousser `README_INTEGRATION.md` sur une branche (proposé : `doc/integration-contract`) et créer la PR. Indiquez si je dois le faire.
- Ajouter l'adaptateur `Passager -> noms/ids` et modifier les tests pour couvrir ce cas.
- Écrire un exemple `data/assignment.json` conforme pour que votre collègue puisse s'en inspirer.

Fin du README d'intégration.

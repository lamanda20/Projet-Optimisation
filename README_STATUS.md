README_STATUS — État actuel et points manquants par partie
=============================================================

But
---
Ce fichier résume l'état du projet et liste précisément ce qui manque encore (par Partie / Tâche). Il propose des actions concrètes, priorités et fichiers à ajouter/modifier pour finaliser l'intégration complète.

Rappel rapide de l'architecture
------------------------------
- Partie 1 : optimisation du nombre de passagers (Z_optimal)
- Partie 2 : affectation + choix des points de ramassage et calcul du trajet (TSP)
- Tâche 3A : consolidation des affectations (regroupe les sorties des parties 1+2 en un JSON exploitable)
- Tâche 3B : votre partie — détermination des points d'arrêt par passager + planning horaire (implémentée dans `task3b.py`)

Status actuel (implémenté)
--------------------------
- `algorithms/` contient des implémentations heuristiques et exactes pour le clustering (Partie 1/2).
- `models/` contient `Passager` et `Conducteur`.
- `task3b.py` (Tâche 3B) :
  - `determine_stop_point_per_passenger(...)` (OK),
  - `compute_schedule(...)` (OK),
  - `validate_inputs(...)` (OK),
  - normaliseurs `_normalize_*` (OK),
  - `to_dataframe(...)` pour exporter le DataFrame (optionnel si pandas installé).
- Tests : unitaires et d'intégration pour Task3B :
  - `tests/test_task3b.py`, `tests/test_integration_task3b.py`, `tests/test_assignment_integration.py` — passent localement.
- `task3a.py` a été ajouté (exemple de consolidation) et `data/assignment.json` fournit un exemple conforme.

Ce qui manque (par partie) — priorités et détails
------------------------------------------------
Partie 1 — (Z_optimal)
- Statut : algorithmes existent (clustering) mais il manque un export formel/standardisé de `Z_optimal` (entier) comme artefact.
- Pourquoi c'est important : `Z_optimal` est utilisé par Task3B pour vérifier le nombre total de passagers attendus.
- Action recommandée (priorité : moyenne) :
  - Ajouter dans l'algorithme une étape d'export : `data/z_optimal.json` ou inclure `Z_optimal` dans la sortie de Tâche3A.
  - Interface : simple int, ou {"Z_optimal": 4}.

Partie 2 — (Affectation + Trajet / TSP)
- Statut : implémentations d'algorithmes (heuristique/exact) prêtes, MAIS :
  - Il manque un module qui prend les groupes produits par l'algorithme et :
    - calcule la liste exacte des points à visiter `v_r == 1`,
    - résout le TSP (ou ordonne les points) pour produire `TRAJET_ORDRE` final,
    - calcule `TEMPS_TRAJET_MIN` (ou fournit les distances/temps entre points visités).
- Pourquoi c'est important : Task3B s'appuie sur `TRAJET_ORDRE` et `TEMPS_TRAJET_MIN` pour calculer les horaires.
- Action recommandée (priorité : haute) :
  - Implémenter un petit module `algorithms/route_planner.py` qui :
    - prend une liste de points (centres de ramassage) et le point de départ du conducteur,
    - calcule une séquence minimale (simple heuristique TSP greedy suffira pour démarrer),
    - renvoie `TRAJET_ORDRE` (incluant le départ) et `TEMPS_TRAJET_MIN` (estimation en minutes).
  - Tests : ajouter `tests/test_route_planner.py`.

Tâche 3A — (Consolidation des affectations) — responsabilité collègue
- Statut : `task3a.py` a été ajouté mais c'est un exemple. Il faut :
  - s'assurer que la version finale prend en entrée la sortie des algorithmes de Partie1+2 (objets `Passager` / groupes) et produit un JSON conforme aux spécifications :
    - `TRAJET_ORDRE` (list[str])
    - `AFFECTATIONS_PAR_POINT` (dict point -> list/noms ou dict board/alight)
    - `TEMPS_TRAJET_MIN` (nested dict)
    - (optionnel) `Z_optimal` (int)
- Pourquoi c'est important : c'est la « plomberie » qui relie modèles/algos à l'exécution réelle (Task3B).
- Action recommandée (priorité : très haute) :
  - Finaliser `task3a.py` pour :
    - accepter objets `Passager` et extraire `id` ou `name` (normalisation),
    - garantir unicité des identifiants, gérer collisions,
    - valider que tous les points d'affectation sont dans `TRAJET_ORDRE`,
    - écrire le JSON dans `data/assignment.json` automatiquement.

Autres améliorations transverses (facultatives mais utiles)
-----------------------------------------------------------
- Adapter Task3B pour accepter `Passager` objects (IDs) au lieu de noms string (si vos algos utilisent les objets) — priorité : moyenne.
- Ajouter vérification de la capacité du conducteur dans `validate_inputs` ou via un check séparé (éviter surbooking) — priorité : moyenne.
- Plusieurs conducteurs / multi-vehicle scenario : étendre le format d'entrée pour supporter plusieurs conducteurs et affectations par conducteur — priorité : basse/si besoin.
- Mettre en place CI (GitHub Actions) pour exécuter `pytest` automatiquement sur chaque PR — priorité : haute.
- Ajouter `data/` de scénarios de tests (exemples réels, edge cases) pour faciliter l'intégration et la revue — priorité : moyenne.

Fichiers recommandés à ajouter
------------------------------
- `algorithms/route_planner.py` (basic TSP / ordering + travel time estimator)
- `task3a_final.py` (version finale de Tâche3A : consomme algos, produit JSON normalisé)
- `tests/test_route_planner.py` (unit tests pour le route planner)
- `data/` : jeux d'exemples supplémentaires (small, medium, edgecases)
- `.github/workflows/python-app.yml` : CI pour lancer pytest

Étapes parfaitement reproductibles pour finaliser la partie 3 (workflow suggéré)
---------------------------------------------------------------------------------
1. Partie1 (ou vous) : s'assurer d'exporter `Z_optimal` (ou l'inclure dans the Task3A output).
2. Partie2 : générer les points de ramassage et appeler `algorithms/route_planner.py` pour obtenir `TRAJET_ORDRE` et `TEMPS_TRAJET_MIN`.
3. Tâche3A : regrouper les affectations par point et écrire `data/assignment.json` (format attendu).
4. Tâche3B : exécuter `py task3b.py --trajet-file data/trajet.json --affect-file data/assignment.json --times-file data/times.json` (ou importer `task3b` functions depuis votre pipeline Python) et produire le planning.

Commandes utiles (PowerShell)
-----------------------------
- Lancer tests :
  py -m pytest -q
- Exécuter la demo Task3B :
  py run_demo.py
- Valider l'assignment.json via Task3B validate :
  py -c "import json; from task3b import validate_inputs; d=json.load(open('data/assignment.json')); validate_inputs(d['TRAJET_ORDRE'], d['AFFECTATIONS_PAR_POINT'], d['TEMPS_TRAJET_MIN'], Z_optimal=d.get('Z_optimal')); print('VALID')"

Proposition de priorités (concrètes)
-----------------------------------
1) (haut) Finaliser Tâche3A pour produire `data/assignment.json` automatiquement (format conforme).  
2) (haut) Implémenter `algorithms/route_planner.py` pour produire `TRAJET_ORDRE` (TSP approximation).  
3) (haut) Mettre en place CI (pytest).  
4) (moyen) Adapter Task3B à accepter objets `Passager`/IDs.  
5) (moyen) Ajouter vérification de capacité/overbooking.  
6) (bas) Support multi-conducteurs.

Besoin d'aide ?
---------------
Je peux :
- implémenter `algorithms/route_planner.py` (heuristique nearest neighbor) et ajouter tests ;
- finaliser `task3a.py` pour accepter objets `Passager` et produire `data/assignment.json` ;
- ajouter CI workflow ;
- commit+push et créer PRs.

Dis‑moi quelle action précise tu veux que je réalise en priorité et je m'en occupe (implémentation + tests + push/PR si demandé).

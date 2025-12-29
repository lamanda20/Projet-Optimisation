README — État du projet : résumé clair et actions
=================================================

Objectif
--------
Ce document donne un état clair et actionnable du projet : ce qui est implémenté et validé, ce qui manque encore (par Partie), les responsabilités et les prochaines étapes recommandées.

Synthèse rapide
---------------
- Partie 1 (clustering / définition des points de ramassage) : implémentée et opérationnelle (algorithmes exacts et heuristiques).
- Partie 2 (affectation finale et ordonnancement du trajet — TSP) : en attente / fournie par un collègue ; il faut s'assurer qu'elle produit le format attendu.
- Partie 3 (consolidation + détermination des points d'arrêt + planning horaire) : TERMINÉE et testée (`pickup_scheduler.py`).

Détails par partie
------------------
Partie 1 — Définir les points de ramassage (implémenté)
- Ce qui existe :
  - Clustering destinations et départs (heuristique et exact) :
    - `algorithms/exact/clustering_exact.py`
    - `algorithms/heuristic/clustering_heuristic.py`
  - Sélection du groupe optimal :
    - `algorithms/exact/selection_exact.py` (vérifié et renforcé)
    - `algorithms/heuristic/selection_heuristic.py`
- Statut : prêt pour l'intégration. Il reste à exporter proprement `Z_optimal` / liste d'IDs si besoin.

Partie 2 — Affectation finale & ordonnancement du trajet (TSP) (à livrer)
- Ce qui est attendu (contract) :
  - `TRAJET_ORDRE` : liste ordonnée des points visités (ex. `["Depart","R3","R1","R5"]`).
  - `AFFECTATIONS_PAR_POINT` : mapping point -> passagers (liste de noms) ou dict {board/alight}.
  - `TEMPS_TRAJET_MIN` : nested dict des temps entre points (minutes) ou fournir `default_travel_min`.
- Statut : l'infrastructure de test et Task3 attend ce JSON (`data/assignment.json` est fourni comme exemple). La brique automatique qui produit ce JSON à partir des algorithmes doit être fournie par la Partie 2 (ou on peut l'implémenter ici).

Partie 3 — Consolidation & planning (implémenté)
- Fichier principal : `pickup_scheduler.py` (consolidation + planning)
- Fonctions clés :
  - `build_pickup_schedulera_output(...)`, `save_output_json(...)` — helpers consolidation.
  - `determine_stop_point_per_passenger(...)` — mapping passager -> {board, alight}.
  - `validate_inputs(...)` — vérifications du format (TRAJET_ORDRE / AFFECTATIONS_PAR_POINT / TEMPS_TRAJET_MIN / Z_optimal).
  - `compute_schedule(...)` — calcule arrival/departure/dwell/cumulative.
  - `to_dataframe(...)` — conversion optionnelle en pandas DataFrame.
- Tests : plusieurs tests unitaires et d’intégration couvrent Task3 et passent localement.

Quelles vérifications sont déjà automatisées
-------------------------------------------
- Les tests pytest couvrent :
  - la fonction de détermination des points d'arrêt,
  - la validation d'entrées,
  - le calcul des horaires,
  - l'intégration simple Partie1 -> adaptateur de test -> Partie3.
- Commande : `py -m pytest -q` (les tests passent localement dans cet environnement).

Points manquants / risques
--------------------------
1. Partie 2 doit livrer un output conforme (voir "Ce qui est attendu"). Sans cela, l'intégration E2E dépendra d'un adaptateur manuel.
2. Si la Partie 2 renvoie des objets `Passager` (instances) au lieu de noms/IDs, il faut un adaptateur pour normaliser en chaînes/IDs uniques.
3. Cas limites non couverts : multi‑conducteurs, contraintes de capacité avancées, gros volumes (performances), entrée corrompue. Tests actuels valident le comportement fonctionnel courant.
4. Avertissement tiers (dateutil) : non bloquant, filtré dans la configuration de test.

Prochaines étapes recommandées (priorités)
------------------------------------------
- Priorité haute : obtenir de la Partie 2 un JSON conforme (`data/assignment.json`) ou implémenter `algorithms/route_planner.py` pour produire `TRAJET_ORDRE` + `TEMPS_TRAJET_MIN` automatiquement.
- Priorité haute : ajouter CI (GitHub Actions) pour exécuter `pytest` sur chaque PR.
- Priorité moyenne : ajouter un adaptateur pour objets `Passager` -> noms/IDs.
- Priorité moyenne : étendre les tests aux cas limites (overbooking, passager sans alight, IDs non uniques).

Commandes utiles (PowerShell)
-----------------------------
Exécuter les tests :

py -m pytest -q

Lancer la démo :

py run_demo.py

Valider un assignment.json manuellement :

py -c "import json; from pickup_scheduler import validate_inputs; d=json.load(open('data/assignment.json')); validate_inputs(d['TRAJET_ORDRE'], d['AFFECTATIONS_PAR_POINT'], d['TEMPS_TRAJET_MIN'], Z_optimal=d.get('Z_optimal')); print('VALID')"

Responsabilités
----------------
- Partie 1 (clustering / sélection) : équipe A (vous).  
- Partie 2 (affectation finale + route planning) : collègue — doit livrer JSON conforme ou module capable de produire la structure attendue.  
- Partie 3 (consolidation + planning) : vous — implémentée dans `pickup_scheduler.py`.

Souhaites‑tu que j'implémente pour toi :
- a) un `algorithms/route_planner.py` heuristique (nearest‑neighbor) ; ou
- b) un adaptateur qui transforme la sortie actuelle des algorithmes en `data/assignment.json` ; ou
- c) la mise en place d'un workflow CI pour lancer pytest automatiquement.

Fin du rapport de statut.


README_BACKEND — Description pas-à-pas du backend (Task3B)
=========================================================

Objectif
--------
Ce document explique en détail le code backend principal du projet, fichier par fichier et fonction par fonction, pour faciliter la compréhension et l'intégration entre les parties (Partie1, Partie2, Tâche3A, Tâche3B).

Fichiers clés
-------------
- `task3b.py` : l'implémentation principale de la Tâche 3B (détermination des points d'arrêt par passager et calcul du planning horaire).
- `algorithms/` : contient la logique de clustering (exact/heuristic) utilisée par les Parties 1 et 2.
- `models/` : classes légères `Passager` et `Conducteur`.
- `utils/` : fonctions utilitaires (ex: `distance.py`, `centroide.py`).
- `tests/` : tests unitaires et d'intégration.

But de `task3b.py`
------------------
Task3B prend en entrée :
- `TRAJET_ORDRE` (liste ordonnée de points à visiter),
- `AFFECTATIONS_PAR_POINT` (qui indique pour chaque point quels passagers montent/descendent),
- `TEMPS_TRAJET_MIN` (matrice / dictionnaire des temps de trajet entre points).

Elle produit :
- pour chaque point, l'heure d'arrivée/départ, le nombre de passagers qui montent/descendent, le cumul de passagers embarqués,
- un mapping passager -> point de montée / point de descente.

Fonction par fonction (lecture de `task3b.py`)
-----------------------------------------------
Je décris ci-dessous chaque fonction utile et ce qu'elle fait, en expliquant les entrées, sorties et comportements importants.

1) _parse_time(t: Union[str, datetime]) -> datetime
   - But : normaliser une chaîne ou un datetime en un objet `datetime`.
   - Accepts :
     - ISO8601 (ex: "2025-11-27T08:00:00")
     - Horaire court "HH:MM" (ex: "08:00") — le jour courant est appliqué.
   - Retour : objet `datetime`.
   - Erreurs : lève si le format est invalide.

2) _get_travel_time(a: str, b: str, temps: Dict[str, Dict[str, int]], default_travel_min: Optional[int]) -> int
   - But : récupérer le temps de trajet (en minutes) entre deux points.
   - Comportement : recherche d'abord `temps[a][b]`, puis `temps[b][a]` (symétrie), puis retourne `default_travel_min` si fourni.
   - Erreurs : si aucune info trouvée et pas de `default_travel_min`, lève `ValueError`.

3) _count_board_alight(point: str, affectations: Dict[str, Any]) -> (board:int, alight:int, boarded_names:List[str])
   - But : pour un point donné, renvoyer combien montent, combien descendent, et la liste des noms embarqués (si fournie).
   - Accepté : valeur associée au point peut être :
     - une liste de noms (interprétée comme boardings),
     - un dict {"board": [...], "alight": [...]},
     - un int (nombre) — la fonction retourne le nombre en tant que board, mais sans noms.
   - Erreurs : si le format est inconnu, lève `ValueError`.

4) compute_schedule(trajet_ordre, affectations_par_point, temps_trajet_min, start_time="08:00", stop_time_per_passenger_min=1, default_travel_min=None, lenient=False)
   - But : calculer pour chaque point la date/heure d'arrivée et de départ, le nombre de board/alight, le cumul de passagers, et le temps d'arrêt (dwell_minutes).
   - Entrées clefs :
     - `trajet_ordre` : liste des points (inclut le point de départ),
     - `affectations_par_point` : mapping point->valeur (voir _count_board_alight),
     - `temps_trajet_min` : nested dict des temps.
   - Logique principale :
     - Démarre à `start_time` pour le premier point (arrivée = départ = start_time + dwell).
     - Pour chaque étape suivante, ajoute le temps de trajet entre points, puis calcule dwell = stop_time_per_passenger_min * (board + alight).
     - Met à jour le cumul (cumulative = cumulative - alight + board).
   - Erreurs et modes :
     - Si un alight > cumulative :
       - en `lenient=False` : lève `ValueError` (erreur d'intégrité),
       - en `lenient=True` : clamp (réduit) l'alight au cumul et log un warning.
     - Si travel time manquant et default_travel_min absent : `_get_travel_time` lève `ValueError`.
   - Sortie : liste d'objets dict :
     - { point, arrival (iso str), departure (iso str), board, alight, cumulative, dwell_minutes, passengers_boarded }

5) to_dataframe(schedule)
   - But : convertir la sortie de `compute_schedule` en `pandas.DataFrame`.
   - Remarque : `pandas` est importé à l'intérieur pour garder la dépendance optionnelle.
   - Erreurs : lève `ImportError` si `pandas` absent.

6) _extract_key_from_dict(obj, candidates)
   - Utilisé pour les normalisations : cherche la première clé parmi `candidates` dans `obj` et renvoie sa valeur.

7) _normalize_trajet / _normalize_affectations / _normalize_temps
   - But : supporter des entrées JSON qui peuvent contenir des clés différentes (ex: `TRAJET_ORDRE` ou `trajet_ordre` ou `trajet`).
   - Retourne les structures normalisées attendues par les fonctions internes.
   - Lève `ValueError` si l'extraction échoue.

8) validate_inputs(trajet_ordre, affectations_par_point, temps_trajet_min, Z_optimal=None, default_travel_min=None)
   - But : valider le contrat d'entrée entre Tâche 3A et 3B.
   - Vérifie :
     - `trajet_ordre` est une liste non-vide,
     - `affectations_par_point` est un dict,
     - toutes les clefs de `affectations_par_point` existent dans `trajet_ordre` (sinon lève),
     - pour chaque paire consécutive (a,b) dans `trajet_ordre` on a un temps (ou `default_travel_min`).
     - si `Z_optimal` fourni, vérifie que le nombre de noms distincts dans affectations == Z_optimal.
   - Retour : None; lève ValueError si violation.

9) determine_stop_point_per_passenger(affectations_par_point)
   - But : construire un mapping par nom de passager : {name: {"board": point_or_None, "alight": point_or_None}}
   - Règles : si le même passager apparaît plusieurs fois pour un même rôle, la première occurrence est retenue.
   - Formats acceptés : identiques à `_count_board_alight` (list, dict(board/alight), int).
   - Utile pour : produire la correspondance attendue par le rapport final et la logique de bord/descente.

Entrées/Sorties JSON attendues
------------------------------
Exemple minimal que Tâche 3A doit fournir pour que Task3B fonctionne immédiatement :

{
  "TRAJET_ORDRE": ["Depart","R3","R1","R5"],
  "AFFECTATIONS_PAR_POINT": {"R3": ["Alice","Charlie"], "R1": ["Bob"], "R5": ["Diane","Eve"]},
  "TEMPS_TRAJET_MIN": {"Depart": {"R3": 5}, "R3": {"R1": 7}, "R1": {"R5": 10}},
  "Z_optimal": 5
}

Flux d'exécution (comment les parties s'articulent)
--------------------------------------------------
1) Partie1 (optimisation du nombre de passagers) renvoie `Z_optimal` (int).
2) Partie2 (affectation & route) produit :
   - un ensemble de points de ramassage (points r),
   - l'ordre du trajet `TRAJET_ORDRE` (résultat TSP),
   - éventuellement les temps entre points (`TEMPS_TRAJET_MIN`).
3) Tâche3A consolide ces sorties en `AFFECTATIONS_PAR_POINT` (regroupe passagers par point) et traduit le tout en JSON conforme.
4) Task3B (ce module) :
   - lit et normalise les structures (via `_normalize_*`),
   - appelle `validate_inputs(...)` pour garantir la cohérence,
   - calcule `determine_stop_point_per_passenger(...)` pour retourner la table passager->(board,alight),
   - exécute `compute_schedule(...)` pour obtenir le plan horaire final.

Comment tester localement
-------------------------
- Lancer les tests unitaires et d'intégration :

```powershell
py -m pytest -q
```

- Lancer la démo incluse :

```powershell
py run_demo.py
```

Bonnes pratiques et recommandations
-----------------------------------
- Tâche3A doit fournir des noms/IDs pour les passagers. Si Tâche3A renvoie des objets `Passager`, ajoutez un adaptateur pour extraire `id` ou `name` avant de passer à Task3B.
- Préférez fournir `TEMPS_TRAJET_MIN` explicites ; sinon, fournissez `default_travel_min` pour éviter exceptions.
- Les tests fournis couvrent les cas de base ; ajouter des tests pour :
  - passager avec `alight` mais sans `board` (erreur ou comportement particulier),
  - passager identifié par ID numérique,
  - scenarios où `alight` > `board` et `lenient=True`.

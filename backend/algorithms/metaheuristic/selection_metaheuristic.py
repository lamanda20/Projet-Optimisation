from typing import List, Dict, Set, Tuple
from models.Conducteur import Conducteur
from models.Passager import Passager
from utils.distance import distance_grille
from utils.centroide import calculer_centroide_grille
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic, phase1_clustering_tous_groupes

class TabuSearch:
    def __init__(self, tabu_size: int = 15, max_iterations: int = 40):
        self.tabu_size = tabu_size
        self.max_iterations = max_iterations
        self.tabu_list: List[Tuple[int, int]] = []
    
    def add_to_tabu(self, move: Tuple[int, int]):
        self.tabu_list.append(move)
        if len(self.tabu_list) > self.tabu_size:
            self.tabu_list.pop(0)
    
    def is_tabu(self, move: Tuple[int, int]) -> bool:
        return move in self.tabu_list or (move[1], move[0]) in self.tabu_list

def calculer_cout_groupe(groupe: Dict, conducteur: Conducteur) -> float:
    centre_depart = groupe['centre_depart']
    return distance_grille(conducteur.position, centre_depart)

def generer_mouvements_swap(groupe_actuel: Dict, tous_passagers_groupe: List[Passager], 
                           capacite_conducteur: int) -> List[Tuple[Dict, Tuple[int, int]]]:
    mouvements = []
    passagers_actuels = groupe_actuel['passagers'][:capacite_conducteur]
    
    for i, passager_sortant in enumerate(passagers_actuels):
        for passager_entrant in tous_passagers_groupe:
            if passager_entrant.id not in [p.id for p in passagers_actuels]:
                nouveaux_passagers = passagers_actuels.copy()
                nouveaux_passagers[i] = passager_entrant
                
                nouveau_groupe = {
                    'passagers': nouveaux_passagers,
                    'taille': len(nouveaux_passagers),
                    'centre_depart': calculer_centroide_grille([p.pos_depart for p in nouveaux_passagers]),
                    'centre_arrivee': calculer_centroide_grille([p.pos_arrivee for p in nouveaux_passagers])
                }
                
                mouvement = (passager_sortant.id, passager_entrant.id)
                mouvements.append((nouveau_groupe, mouvement))
    
    return mouvements

def optimiser_groupe_tabu(groupe_initial: Dict, tous_passagers_groupe: List[Passager], 
                          conducteur: Conducteur) -> Dict:
    tabu_search = TabuSearch(tabu_size=5, max_iterations=15)
    
    meilleure_solution = groupe_initial
    meilleur_cout = calculer_cout_groupe(groupe_initial, conducteur)
    solution_courante = groupe_initial
    
    print(f"    Début tabou: {len(tous_passagers_groupe)} passagers disponibles, coût initial: {meilleur_cout:.2f}")
    
    ameliorations = 0
    mouvements_evalues = 0
    
    for iteration in range(tabu_search.max_iterations):
        # Générer tous les swaps possibles
        mouvements = generer_mouvements_swap(solution_courante, tous_passagers_groupe, 
                                           conducteur.capacite)
        
        if not mouvements:
            print(f"    Itération {iteration+1}: Aucun mouvement possible - STOP")
            break
        
        print(f"    Itération {iteration+1}: {len(mouvements)} mouvements générés")
        
        meilleur_mouvement = None
        meilleur_voisin = None
        meilleur_cout_voisin = float('inf')
        mouvements_acceptes = 0
        
        # Évaluer chaque mouvement
        for nouveau_groupe, mouvement in mouvements:
            cout_voisin = calculer_cout_groupe(nouveau_groupe, conducteur)
            mouvements_evalues += 1
            
            # Accepter si non-tabou OU si critère d'aspiration (meilleur que best)
            if not tabu_search.is_tabu(mouvement) or cout_voisin < meilleur_cout:
                mouvements_acceptes += 1
                if cout_voisin < meilleur_cout_voisin:
                    meilleur_voisin = nouveau_groupe
                    meilleur_mouvement = mouvement
                    meilleur_cout_voisin = cout_voisin
        
        print(f"      -> {mouvements_acceptes}/{len(mouvements)} mouvements acceptés (non-tabou)")
        
        if meilleur_voisin is None:
            print(f"    Itération {iteration+1}: Tous mouvements tabous - STOP")
            break
        
        # Mise à jour
        solution_courante = meilleur_voisin
        tabu_search.add_to_tabu(meilleur_mouvement)
        
        print(f"      -> Mouvement: P{meilleur_mouvement[0]} ↔ P{meilleur_mouvement[1]}, coût: {meilleur_cout_voisin:.2f}")
        
        # Nouvelle meilleure solution trouvée
        if meilleur_cout_voisin < meilleur_cout:
            meilleure_solution = meilleur_voisin
            meilleur_cout = meilleur_cout_voisin
            ameliorations += 1
            print(f"      -> ✅ NOUVELLE MEILLEURE SOLUTION: {meilleur_cout:.2f}")
    
    print(f"    Fin tabou: {ameliorations} améliorations, {mouvements_evalues} mouvements évalués")
    
    return meilleure_solution

def recherche_tabou_groupes(groupes_initiaux: List[Dict], conducteur: Conducteur) -> Dict:
    if not groupes_initiaux:
        return None
    
    groupes_optimises = []
    
    for i, groupe in enumerate(groupes_initiaux):
        print(f"\nGroupe {i+1}: {groupe['taille']} passagers")
        cout_initial = calculer_cout_groupe(groupe, conducteur)
        print(f"  Coût initial: {cout_initial:.2f}")
        
        # Tous les passagers du groupe (même zone départ/arrivée)
        tous_passagers_groupe = groupe['passagers']
        
        # Créer solution initiale avec capacité conducteur
        if len(tous_passagers_groupe) <= conducteur.capacite:
            # Groupe plus petit que capacité - prendre tous
            solution_initiale = groupe
        else:
            # Groupe plus grand - sélectionner les meilleurs passagers
            # Critère: passagers les plus proches du centre actuel
            centre_actuel = groupe['centre_depart']
            passagers_tries = sorted(tous_passagers_groupe, 
                                   key=lambda p: distance_grille(p.pos_depart, centre_actuel))
            passagers_selectionnes = passagers_tries[:conducteur.capacite]
            
            solution_initiale = {
                'passagers': passagers_selectionnes,
                'taille': len(passagers_selectionnes),
                'centre_depart': calculer_centroide_grille([p.pos_depart for p in passagers_selectionnes]),
                'centre_arrivee': calculer_centroide_grille([p.pos_arrivee for p in passagers_selectionnes])
            }
        
        # Optimisation tabou avec swaps
        groupe_optimise = optimiser_groupe_tabu(solution_initiale, tous_passagers_groupe, conducteur)
        cout_final = calculer_cout_groupe(groupe_optimise, conducteur)
        
        print(f"  Coût final: {cout_final:.2f}")
        print(f"  Amélioration: {cout_initial - cout_final:.2f}")
        print(f"  Passagers finaux: {[p.id for p in groupe_optimise['passagers']]}")
        
        groupes_optimises.append(groupe_optimise)
    
    # Sélectionner le meilleur: capacité max puis distance min
    meilleur_groupe = max(groupes_optimises, 
                         key=lambda g: (g['taille'], -calculer_cout_groupe(g, conducteur)))
    
    return meilleur_groupe

def phase1_clustering_metaheuristic(passagers: List[Passager], conducteur: Conducteur, 
                                  R_dest: float, R_depart: float) -> Dict:
    # Obtenir TOUS les groupes sans contrainte de capacité
    groupes_initiaux = phase1_clustering_tous_groupes(passagers, R_dest, R_depart)
    
    if not groupes_initiaux:
        return None
    
    print(f"=== Groupes Phase 1 Clustering (TOUS) ===")
    print(f"Nombre de groupes: {len(groupes_initiaux)}")
    for i, groupe in enumerate(groupes_initiaux):
        cout = calculer_cout_groupe(groupe, conducteur)
        print(f"Groupe {i+1}: {groupe['taille']} passagers, coût: {cout:.2f}")
    
    print(f"\n=== Recherche Tabou ===")
    meilleur_groupe = recherche_tabou_groupes(groupes_initiaux, conducteur)
    
    if meilleur_groupe:
        cout_final = calculer_cout_groupe(meilleur_groupe, conducteur)
        print(f"\nGroupe optimal final:")
        print(f"Taille: {meilleur_groupe['taille']}, Coût: {cout_final:.2f}")
        print(f"Passagers: {[p.id for p in meilleur_groupe['passagers']]}")
    
    return meilleur_groupe
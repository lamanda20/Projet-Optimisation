#!/usr/bin/env python3
"""
Exemple avancé Phase 2: Comparaison et optimisation
Montre comment choisir entre exacte et heuristique
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.phase2_integrator import phase2_solve
import time


def benchmark_methods(passagers, conducteur, R_dest, R_depart):
    """Compare exacte vs heuristique"""
    
    print(f"\n{'='*70}")
    print(f"BENCHMARK: {len(passagers)} passagers")
    print(f"{'='*70}\n")
    
    # Exacte
    print("⏱️  Méthode EXACTE (Brute Force TSP)...")
    start = time.time()
    trajet_exact, temps_exact, groupes_exact = phase2_solve(
        passagers, conducteur, R_dest, R_depart, method="exact"
    )
    time_exact = time.time() - start
    
    # Heuristique
    print("⏱️  Méthode HEURISTIQUE (Nearest Neighbor)...")
    start = time.time()
    trajet_heur, temps_heur, groupes_heur = phase2_solve(
        passagers, conducteur, R_dest, R_depart, method="heuristic"
    )
    time_heur = time.time() - start
    
    # Calcul distances
    def total_distance(temps_dict):
        return sum(sum(next_points.values()) for point, next_points in temps_dict.items())
    
    dist_exact = total_distance(temps_exact)
    dist_heur = total_distance(temps_heur)
    
    # Résultats
    print(f"\n{'─'*70}")
    print(f"{'Métrique':<30} {'Exacte':<15} {'Heuristique':<15}")
    print(f"{'─'*70}")
    print(f"{'Distance totale (min)':<30} {dist_exact:<15.1f} {dist_heur:<15.1f}")
    print(f"{'Temps calcul (ms)':<30} {time_exact*1000:<15.2f} {time_heur*1000:<15.2f}")
    print(f"{'Groupes formés':<30} {len(groupes_exact):<15} {len(groupes_heur):<15}")
    
    # Qualité relative
    if dist_exact > 0:
        gap = 100 * (dist_heur - dist_exact) / dist_exact
    else:
        gap = 0
    
    print(f"{'Gap heuristique (%)':<30} {0:<15.1f} {gap:<15.1f}")
    print(f"{'─'*70}")
    
    # Recommandation
    print("\n🎯 Recommandation:")
    if len(passagers) <= 10:
        print("   → Utiliser EXACTE: Petit problème, solution garantie optimale")
    elif gap > 20:
        print("   → Heuristique a large gap, envisager EXACTE si temps le permet")
    else:
        print("   → Utiliser HEURISTIQUE: Bon compromis vitesse/qualité")
    
    return trajet_exact, temps_exact, trajet_heur, temps_heur, dist_exact, dist_heur, time_exact, time_heur


def scenario_1_small():
    """Scénario 1: Petit problème (4 passagers)"""
    print("\n" + "="*70)
    print("SCÉNARIO 1: PETIT PROBLÈME (4 passagers)")
    print("="*70)
    
    passagers = [
        Passager(id=1, pos_depart=(0, 0), pos_arrivee=(10, 10)),
        Passager(id=2, pos_depart=(1, 1), pos_arrivee=(11, 11)),
        Passager(id=3, pos_depart=(50, 50), pos_arrivee=(60, 60)),
        Passager(id=4, pos_depart=(51, 51), pos_arrivee=(61, 61)),
    ]
    conducteur = Conducteur(position=(0, 0), capacite=2)
    
    benchmark_methods(passagers, conducteur, R_dest=15, R_depart=15)


def scenario_2_medium():
    """Scénario 2: Moyen (10 passagers)"""
    print("\n" + "="*70)
    print("SCÉNARIO 2: PROBLÈME MOYEN (10 passagers)")
    print("="*70)
    
    passagers = []
    for i in range(10):
        passagers.append(Passager(
            id=i+1,
            pos_depart=(i*10, (i//2)*20),
            pos_arrivee=(i*10+5, (i//2)*20+10)
        ))
    conducteur = Conducteur(position=(0, 0), capacite=3)
    
    benchmark_methods(passagers, conducteur, R_dest=15, R_depart=15)


def scenario_3_large():
    """Scénario 3: Grand (20+ passagers)"""
    print("\n" + "="*70)
    print("SCÉNARIO 3: GRAND PROBLÈME (20+ passagers)")
    print("="*70)
    
    import random
    random.seed(42)
    
    passagers = []
    for i in range(20):
        depart = (random.randint(0, 200), random.randint(0, 200))
        arrivee = (random.randint(0, 200), random.randint(0, 200))
        passagers.append(Passager(id=i+1, pos_depart=depart, pos_arrivee=arrivee))
    
    conducteur = Conducteur(position=(100, 100), capacite=4)
    
    print("\n⚠️  Pour >15 passagers, EXACTE devient très lent")
    print("   Tentative avec HEURISTIQUE uniquement...\n")
    
    start = time.time()
    trajet, temps, groupes = phase2_solve(
        passagers, conducteur, R_dest=20, R_depart=20, method="heuristic"
    )
    elapsed = time.time() - start
    
    dist = sum(sum(next_points.values()) for _, next_points in temps.items())
    
    print(f"✓ Résolu en {elapsed*1000:.2f} ms")
    print(f"  - {len(groupes)} groupes")
    print(f"  - Distance: {dist} min")
    print(f"  - Trajet: {trajet}")


def interactive_choice():
    """Mode interactif pour choisir la méthode"""
    print("\n" + "="*70)
    print("MODE INTERACTIF: AIDE AU CHOIX DE MÉTHODE")
    print("="*70)
    
    print("\nCombien de passagers avez-vous?")
    try:
        n = int(input("→ "))
    except:
        print("Entrée invalide")
        return
    
    print(f"\nPour {n} passagers:")
    
    if n <= 8:
        print("✅ RECOMMANDÉ: Méthode EXACTE")
        print("   - Solution garantie optimale")
        print("   - Temps calcul: < 100ms")
        print("   - Code: method='exact'")
    elif n <= 15:
        print("⚠️  DÉLICAT: À la limite")
        print("   - EXACTE: ~1-5 secondes (faisable)")
        print("   - HEURISTIQUE: < 10ms (recommandé)")
        print("   - Suggestion: Essayer exacte d'abord, puis heuristique si trop lent")
    else:
        print("⛔ PAS RECOMMANDÉ: Méthode EXACTE")
        print("   - Temps de calcul prohibitif (O(n!))")
        print("   - HEURISTIQUE obligatoire: < 50ms")
        print("   - Code: method='heuristic'")
    
    print("\nComplexité: Exacte = O(n!), Heuristique = O(n²)")
    print(f"Vous avez ~{2**n} permutations à essayer avec exacte")


def main():
    """Menu principal"""
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     PHASE 2: CLUSTERING + TSP - DÉMONSTRATION        ║
    ║            Exacte vs Heuristique                     ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\nChoisissez un scénario:")
        print("1. Petit problème (4 passagers) → Exacte vs Heuristique")
        print("2. Moyen (10 passagers) → Comparaison détaillée")
        print("3. Grand (20+ passagers) → Heuristique seulement")
        print("4. Mode interactif → Aide personnalisée")
        print("5. Quitter")
        
        choice = input("\n→ ").strip()
        
        if choice == "1":
            scenario_1_small()
        elif choice == "2":
            scenario_2_medium()
        elif choice == "3":
            scenario_3_large()
        elif choice == "4":
            interactive_choice()
        elif choice == "5":
            print("\nAu revoir! 👋")
            break
        else:
            print("Option invalide")


if __name__ == "__main__":
    main()

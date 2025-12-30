#!/usr/bin/env python3
"""
Benchmark simple pour comparer les 4 algorithmes
Usage: python benchmark_algorithms.py
"""

import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Conducteur import Conducteur
from models.Passager import Passager
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic
from algorithms.heuristic.selection_heuristic import selection_heuristic
from algorithms.metaheuristic.selection_metaheuristic import phase1_clustering_metaheuristic
from algorithms.genetic.genetic_carpooling import solve_genetic
from utils.distance import distance_grille

def generer_passagers_clusters(nb_passagers):
    """Génère des passagers en clusters pour test optimal"""
    passagers = []
    
    # 4 clusters prédéfinis
    clusters = [
        {"depart": (10, 15), "arrivee": (80, 85)},
        {"depart": (80, 85), "arrivee": (15, 20)},
        {"depart": (20, 25), "arrivee": (70, 75)},
        {"depart": (70, 75), "arrivee": (25, 30)}
    ]
    
    for i in range(nb_passagers):
        cluster = clusters[i % len(clusters)]
        
        # Variation aléatoire autour du cluster
        depart = (
            cluster["depart"][0] + random.randint(-5, 5),
            cluster["depart"][1] + random.randint(-5, 5)
        )
        arrivee = (
            cluster["arrivee"][0] + random.randint(-5, 5),
            cluster["arrivee"][1] + random.randint(-5, 5)
        )
        
        passagers.append(Passager(i+1, depart, arrivee))
    
    return passagers

def tester_algorithme(nom, fonction, passagers, conducteur, R_dest=15, R_depart=15):
    """Teste un algorithme et retourne les résultats"""
    print(f"\n🔄 Test {nom}...")
    
    try:
        start_time = time.time()
        result = None
        cout = 0
        
        if nom == "HEURISTIC":
            groupes = phase1_clustering_heuristic(passagers, conducteur, R_dest, R_depart)
            if groupes:
                result = selection_heuristic(groupes, conducteur)
                if result:
                    # Calculer coût = distance du conducteur au centre du groupe
                    from utils.centroide import calculer_centroide_grille
                    centre = calculer_centroide_grille([p.pos_depart for p in result])
                    cout = distance_grille(conducteur.position, centre)
                    
        elif nom == "TABOU":
            result_dict = phase1_clustering_metaheuristic(passagers, conducteur, R_dest, R_depart)
            if result_dict:
                result = result_dict['passagers']
                cout = distance_grille(conducteur.position, result_dict['centre_depart'])
                
        elif nom == "GENETIC":
            trajet, temps, groupes = solve_genetic(passagers, conducteur, R_dest, R_depart, 
                                                 population_size=50, generations=100, mutation_rate=0.15)
            if groupes:
                result = []
                for groupe in groupes:
                    result.extend(groupe['passagers'])
                result = result[:conducteur.capacite]  # Limiter à la capacité
                if result:
                    from utils.centroide import calculer_centroide_grille
                    centre = calculer_centroide_grille([p.pos_depart for p in result])
                    cout = distance_grille(conducteur.position, centre)
        
        end_time = time.time()
        temps_execution = end_time - start_time
        nb_selectionnes = len(result) if result else 0
        
        return {
            'temps': temps_execution,
            'selectionnes': nb_selectionnes,
            'cout': cout,
            'passagers_ids': [p.id for p in result] if result else [],
            'succes': True
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {
            'temps': -1,
            'selectionnes': 0,
            'cout': 0,
            'passagers_ids': [],
            'succes': False
        }

def main():
    print("🏁 BENCHMARK ALGORITHMES D'OPTIMISATION")
    print("=" * 50)
    
    # Configuration
    conducteur = Conducteur((50, 50), capacite=8)
    test_sizes = [10, 50, 100]
    algorithmes = [
        ("HEURISTIC", None), 
        ("TABOU", None),
        ("GENETIC", None)
    ]
    
    resultats = []
    
    for nb_passagers in test_sizes:
        print(f"\n📊 TEST AVEC {nb_passagers} PASSAGERS (Capacité: 8)")
        print("-" * 40)
        
        # Générer données de test
        passagers = generer_passagers_clusters(nb_passagers)
        R_dest = 20 if nb_passagers <= 10 else 25
        R_depart = R_dest
        
        for nom_algo, fonction in algorithmes:
            resultat = tester_algorithme(nom_algo, fonction, passagers, conducteur, R_dest, R_depart)
            resultat['nb_passagers'] = nb_passagers
            resultat['algorithme'] = nom_algo
            resultats.append(resultat)
            
            if resultat['succes']:
                print(f"✅ {nom_algo}: {resultat['temps']:.3f}s | {resultat['selectionnes']}/{nb_passagers} | Coût: {resultat['cout']:.2f}")
                print(f"    Passagers: {resultat['passagers_ids']}")
            else:
                print(f"❌ {nom_algo}: ÉCHEC")
    
    # Résumé final
    print(f"\n🏆 RÉSUMÉ BENCHMARK")
    print("=" * 50)
    
    for nb_passagers in test_sizes:
        print(f"\n📊 {nb_passagers} Passagers:")
        resultats_taille = [r for r in resultats if r['nb_passagers'] == nb_passagers and r['succes']]
        
        if resultats_taille:
            for r in resultats_taille:
                print(f"  {r['algorithme']}: {r['temps']:.3f}s | {r['selectionnes']} passagers | Coût: {r['cout']:.2f}")
                print(f"    Solution: {r['passagers_ids']}")
        else:
            print("  ❌ Aucun algorithme n'a réussi")

if __name__ == "__main__":
    main()
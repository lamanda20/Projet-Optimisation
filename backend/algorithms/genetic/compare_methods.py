"""
Comparison script to test all three methods on the same dataset
Usage: python compare_methods.py -i data/genetic_input_example.json
"""

import sys
import os
import json
import time
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.genetic.genetic_carpooling import solve_genetic
from algorithms.phase2_integrator import phase2_solve


def load_input_data(input_file: str) -> tuple:
    """Load passengers and driver data from JSON file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conducteur_data = data.get('conducteur', {})
    conducteur = Conducteur(
        position=tuple(conducteur_data.get('position', [0, 0])),
        capacite=conducteur_data.get('capacite', 4)
    )
    
    passagers = []
    for p_data in data.get('passagers', []):
        passager = Passager(
            id=p_data['id'],
            pos_depart=tuple(p_data['depart']),
            pos_arrivee=tuple(p_data['arrivee'])
        )
        passagers.append(passager)
    
    return passagers, conducteur


def calculate_total_distance(temps_trajet: Dict) -> int:
    """Calculate total travel distance from temps_trajet"""
    total = 0
    for point, destinations in temps_trajet.items():
        for dest, time in destinations.items():
            total += time
    return total


def compare_methods(input_file: str, R_dest: float = 5.0, R_depart: float = 5.0):
    """Compare exact, heuristic, and genetic algorithm methods"""
    
    print("="*70)
    print("CARPOOLING METHOD COMPARISON")
    print("="*70)
    print(f"\nInput: {input_file}")
    print(f"Clustering Parameters: R_dest={R_dest}, R_depart={R_depart}\n")
    
    # Load data
    passagers, conducteur = load_input_data(input_file)
    print(f"📊 Dataset: {len(passagers)} passengers, capacity {conducteur.capacite}\n")
    
    results = {}
    
    # Test Exact Method
    print("-" * 70)
    print("1️⃣  EXACT METHOD (Brute Force TSP)")
    print("-" * 70)
    try:
        start = time.time()
        trajet_exact, temps_exact, groupes_exact = phase2_solve(
            passagers, conducteur, R_dest, R_depart, method="exact"
        )
        elapsed = time.time() - start
        
        passengers_served = sum(len(g['passagers']) for g in groupes_exact)
        total_distance = calculate_total_distance(temps_exact)
        
        results['exact'] = {
            'time': elapsed,
            'passengers': passengers_served,
            'clusters': len(groupes_exact),
            'distance': total_distance,
            'stops': len(trajet_exact) - 1
        }
        
        print(f"✓ Time: {elapsed:.3f}s")
        print(f"  Passengers Served: {passengers_served}")
        print(f"  Number of Clusters: {len(groupes_exact)}")
        print(f"  Total Distance: {total_distance}")
        print(f"  Route: {' → '.join(trajet_exact)}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        results['exact'] = None
    
    # Test Heuristic Method
    print("\n" + "-" * 70)
    print("2️⃣  HEURISTIC METHOD (Nearest Neighbor TSP)")
    print("-" * 70)
    try:
        start = time.time()
        trajet_heur, temps_heur, groupes_heur = phase2_solve(
            passagers, conducteur, R_dest, R_depart, method="heuristic"
        )
        elapsed = time.time() - start
        
        passengers_served = sum(len(g['passagers']) for g in groupes_heur)
        total_distance = calculate_total_distance(temps_heur)
        
        results['heuristic'] = {
            'time': elapsed,
            'passengers': passengers_served,
            'clusters': len(groupes_heur),
            'distance': total_distance,
            'stops': len(trajet_heur) - 1
        }
        
        print(f"✓ Time: {elapsed:.3f}s")
        print(f"  Passengers Served: {passengers_served}")
        print(f"  Number of Clusters: {len(groupes_heur)}")
        print(f"  Total Distance: {total_distance}")
        print(f"  Route: {' → '.join(trajet_heur)}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        results['heuristic'] = None
    
    # Test Genetic Algorithm
    print("\n" + "-" * 70)
    print("3️⃣  GENETIC ALGORITHM (Metaheuristic)")
    print("-" * 70)
    try:
        start = time.time()
        trajet_ga, temps_ga, groupes_ga = solve_genetic(
            passagers, conducteur, R_dest, R_depart,
            population_size=100, generations=200, verbose=False
        )
        elapsed = time.time() - start
        
        passengers_served = sum(len(g['passagers']) for g in groupes_ga)
        total_distance = calculate_total_distance(temps_ga)
        
        results['genetic'] = {
            'time': elapsed,
            'passengers': passengers_served,
            'clusters': len(groupes_ga),
            'distance': total_distance,
            'stops': len(trajet_ga) - 1
        }
        
        print(f"✓ Time: {elapsed:.3f}s")
        print(f"  Passengers Served: {passengers_served}")
        print(f"  Number of Clusters: {len(groupes_ga)}")
        print(f"  Total Distance: {total_distance}")
        print(f"  Route: {' → '.join(trajet_ga)}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        results['genetic'] = None
    
    # Summary Comparison
    print("\n" + "="*70)
    print("SUMMARY COMPARISON")
    print("="*70)
    
    print(f"\n{'Method':<20} {'Time (s)':<12} {'Passengers':<12} {'Distance':<12} {'Clusters':<10}")
    print("-" * 70)
    
    for method_name in ['exact', 'heuristic', 'genetic']:
        if results[method_name]:
            r = results[method_name]
            print(f"{method_name.capitalize():<20} {r['time']:<12.3f} {r['passengers']:<12} {r['distance']:<12} {r['clusters']:<10}")
        else:
            print(f"{method_name.capitalize():<20} {'FAILED':<12}")
    
    # Determine winner in each category
    print("\n" + "="*70)
    print("WINNERS BY CATEGORY")
    print("="*70)
    
    valid_results = {k: v for k, v in results.items() if v is not None}
    
    if valid_results:
        # Fastest
        fastest = min(valid_results.items(), key=lambda x: x[1]['time'])
        print(f"⚡ Fastest: {fastest[0].upper()} ({fastest[1]['time']:.3f}s)")
        
        # Most passengers
        most_passengers = max(valid_results.items(), key=lambda x: x[1]['passengers'])
        print(f"👥 Most Passengers: {most_passengers[0].upper()} ({most_passengers[1]['passengers']} passengers)")
        
        # Shortest distance
        shortest_dist = min(valid_results.items(), key=lambda x: x[1]['distance'])
        print(f"🎯 Shortest Route: {shortest_dist[0].upper()} ({shortest_dist[1]['distance']} units)")
        
        # Most efficient clusters
        most_efficient = max(valid_results.items(), 
                            key=lambda x: x[1]['passengers'] / x[1]['clusters'] if x[1]['clusters'] > 0 else 0)
        efficiency = most_efficient[1]['passengers'] / most_efficient[1]['clusters']
        print(f"📊 Best Cluster Efficiency: {most_efficient[0].upper()} ({efficiency:.2f} passengers/cluster)")
    
    print("\n" + "="*70)
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare carpooling optimization methods')
    parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    parser.add_argument('--R-dest', type=float, default=5.0, help='R_dest parameter')
    parser.add_argument('--R-depart', type=float, default=5.0, help='R_depart parameter')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    compare_methods(args.input, args.R_dest, args.R_depart)

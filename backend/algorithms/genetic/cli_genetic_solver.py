"""
CLI Interface for Genetic Algorithm Carpooling Solver
Usage: python cli_genetic_solver.py [options]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import json
from typing import List, Dict
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.genetic.genetic_carpooling import solve_genetic
from algorithms.phase2_integrator import generate_affectations_par_point, export_phase2_json


def load_input_data(input_file: str) -> tuple:
    """
    Load passengers and driver data from JSON file
    
    Expected format:
    {
        "conducteur": {"position": [x, y], "capacite": n},
        "passagers": [
            {"id": 1, "depart": [x1, y1], "arrivee": [x2, y2]},
            ...
        ]
    }
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Parse conducteur
    conducteur_data = data.get('conducteur', {})
    conducteur = Conducteur(
        position=tuple(conducteur_data.get('position', [0, 0])),
        capacite=conducteur_data.get('capacite', 4)
    )
    
    # Parse passagers
    passagers = []
    for p_data in data.get('passagers', []):
        passager = Passager(
            id=p_data['id'],
            pos_depart=tuple(p_data['depart']),
            pos_arrivee=tuple(p_data['arrivee'])
        )
        passagers.append(passager)
    
    return passagers, conducteur


def save_results(
    output_file: str,
    trajet_ordre: List[str],
    affectations: Dict[str, List[str]],
    temps_trajet: Dict[str, Dict[str, int]],
    groupes: List[Dict],
    metadata: Dict = None
):
    """Save results to JSON file"""
    
    # Calculate total passengers
    Z_optimal = sum(len(g['passagers']) for g in groupes)
    
    # Prepare metadata
    if metadata is None:
        metadata = {}
    
    metadata.update({
        'method': 'genetic_algorithm',
        'total_passengers': Z_optimal,
        'num_clusters': len(groupes)
    })
    
    export_phase2_json(
        output_path=output_file,
        trajet_ordre=trajet_ordre,
        affectations=affectations,
        temps_trajet=temps_trajet,
        Z_optimal=Z_optimal,
        metadata=metadata
    )
    
    print(f"\n✓ Results saved to: {output_file}")


def print_solution_summary(
    trajet_ordre: List[str],
    affectations: Dict[str, List[str]],
    temps_trajet: Dict[str, Dict[str, int]],
    groupes: List[Dict]
):
    """Print a human-readable summary of the solution"""
    
    print("\n" + "="*60)
    print("GENETIC ALGORITHM CARPOOLING SOLUTION")
    print("="*60)
    
    total_passengers = sum(len(g['passagers']) for g in groupes)
    print(f"\n📊 Summary:")
    print(f"   Total Passengers Served: {total_passengers}")
    print(f"   Number of Clusters: {len(groupes)}")
    print(f"   Number of Stops: {len(trajet_ordre) - 1}")
    
    print(f"\n🚗 Route Order: {' → '.join(trajet_ordre)}")
    
    print(f"\n👥 Passenger Assignments:")
    for point, passengers in affectations.items():
        print(f"   {point}: {', '.join(passengers)} ({len(passengers)} passengers)")
    
    print(f"\n⏱️  Travel Times (minutes):")
    total_time = 0
    for point, destinations in temps_trajet.items():
        for dest, time in destinations.items():
            print(f"   {point} → {dest}: {time} min")
            total_time += time
    print(f"   Total Travel Time: {total_time} min")
    
    print(f"\n📍 Cluster Details:")
    for i, groupe in enumerate(groupes, 1):
        print(f"   R{i}:")
        print(f"      Size: {groupe['taille']} passengers")
        print(f"      Pickup Centroid: {groupe['centre_depart']}")
        print(f"      Dropoff Centroid: {groupe['centre_arrivee']}")
        passenger_ids = [f"P{p.id}" for p in groupe['passagers']]
        print(f"      Passengers: {', '.join(passenger_ids)}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Genetic Algorithm Solver for Carpooling Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_genetic_solver.py -i data/input.json -o results/genetic_output.json
  python cli_genetic_solver.py -i data/input.json --pop-size 200 --generations 500
  python cli_genetic_solver.py -i data/input.json --R-dest 6.0 --R-depart 4.0
        """
    )
    
    # Input/Output arguments
    parser.add_argument('-i', '--input', required=True,
                        help='Path to input JSON file with passengers and driver data')
    parser.add_argument('-o', '--output', default='results/genetic_solution.json',
                        help='Path to output JSON file (default: results/genetic_solution.json)')
    
    # Genetic Algorithm parameters
    parser.add_argument('--pop-size', type=int, default=100,
                        help='Population size (default: 100)')
    parser.add_argument('--generations', type=int, default=200,
                        help='Number of generations (default: 200)')
    parser.add_argument('--mutation-rate', type=float, default=0.15,
                        help='Mutation rate (default: 0.15)')
    parser.add_argument('--elite-size', type=int, default=10,
                        help='Elite size for elitism (default: 10)')
    parser.add_argument('--tournament-size', type=int, default=5,
                        help='Tournament size for selection (default: 5)')
    
    # Clustering parameters
    parser.add_argument('--R-dest', type=float, default=5.0,
                        help='Maximum distance for destination clustering (default: 5.0)')
    parser.add_argument('--R-depart', type=float, default=5.0,
                        help='Maximum distance for departure clustering (default: 5.0)')
    
    # Display options
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--no-summary', action='store_true',
                        help='Do not print solution summary')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Load input data
    print(f"📂 Loading data from: {args.input}")
    try:
        passagers, conducteur = load_input_data(args.input)
        print(f"   Loaded {len(passagers)} passengers")
        print(f"   Driver capacity: {conducteur.capacite}")
        print(f"   Driver position: {conducteur.position}")
    except Exception as e:
        print(f"❌ Error loading input file: {e}")
        sys.exit(1)
    
    # Run genetic algorithm
    print(f"\n🧬 Running Genetic Algorithm...")
    print(f"   Population Size: {args.pop_size}")
    print(f"   Generations: {args.generations}")
    print(f"   Mutation Rate: {args.mutation_rate}")
    print(f"   R_dest: {args.R_dest}, R_depart: {args.R_depart}")
    
    try:
        trajet_ordre, temps_trajet, groupes = solve_genetic(
            passagers=passagers,
            conducteur=conducteur,
            R_dest=args.R_dest,
            R_depart=args.R_depart,
            population_size=args.pop_size,
            generations=args.generations,
            mutation_rate=args.mutation_rate,
            verbose=not args.quiet
        )
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate affectations
    affectations = generate_affectations_par_point(groupes, trajet_ordre)
    
    # Save results
    metadata = {
        'population_size': args.pop_size,
        'generations': args.generations,
        'mutation_rate': args.mutation_rate,
        'R_dest': args.R_dest,
        'R_depart': args.R_depart
    }
    
    save_results(args.output, trajet_ordre, affectations, temps_trajet, groupes, metadata)
    
    # Print summary
    if not args.no_summary:
        print_solution_summary(trajet_ordre, affectations, temps_trajet, groupes)
    
    print("\n✅ Complete!")


if __name__ == "__main__":
    main()

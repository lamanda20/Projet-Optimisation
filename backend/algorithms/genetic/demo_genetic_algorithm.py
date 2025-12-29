"""
Demonstration script for Genetic Algorithm Carpooling Solver
Shows various usage scenarios and parameter tuning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.genetic.genetic_carpooling import solve_genetic, GeneticCarpoolingSolver


def demo_basic_usage():
    """Demo 1: Basic usage with default parameters"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage")
    print("="*70)
    
    # Create sample data
    conducteur = Conducteur(position=(0, 0), capacite=4)
    passagers = [
        Passager(id=1, pos_depart=(2, 3), pos_arrivee=(15, 18)),
        Passager(id=2, pos_depart=(3, 4), pos_arrivee=(16, 19)),
        Passager(id=3, pos_depart=(8, 2), pos_arrivee=(20, 15)),
        Passager(id=4, pos_depart=(9, 3), pos_arrivee=(21, 16)),
        Passager(id=5, pos_depart=(5, 10), pos_arrivee=(25, 25)),
        Passager(id=6, pos_depart=(6, 11), pos_arrivee=(26, 26)),
    ]
    
    # Solve with default parameters
    trajet, temps, groupes = solve_genetic(
        passagers, conducteur, 
        verbose=True
    )
    
    print(f"\n✓ Served {sum(len(g['passagers']) for g in groupes)} passengers")
    print(f"✓ Created {len(groupes)} clusters")
    print(f"✓ Route: {' → '.join(trajet)}")


def demo_fast_solution():
    """Demo 2: Fast solution with reduced parameters"""
    print("\n" + "="*70)
    print("DEMO 2: Fast Solution (for quick testing)")
    print("="*70)
    
    conducteur = Conducteur(position=(0, 0), capacite=5)
    passagers = [
        Passager(id=i, 
                pos_depart=(i*2, i*3), 
                pos_arrivee=(20+i, 25+i))
        for i in range(1, 11)
    ]
    
    # Fast parameters: small population, few generations
    trajet, temps, groupes = solve_genetic(
        passagers, conducteur,
        population_size=30,
        generations=50,
        verbose=True
    )
    
    print(f"\n✓ Quick solution found!")


def demo_high_quality():
    """Demo 3: High-quality solution with increased parameters"""
    print("\n" + "="*70)
    print("DEMO 3: High-Quality Solution (best results)")
    print("="*70)
    
    conducteur = Conducteur(position=(0, 0), capacite=5)
    passagers = [
        Passager(id=i, 
                pos_depart=(i*2 % 20, i*3 % 20), 
                pos_arrivee=(25+i, 30+i))
        for i in range(1, 16)
    ]
    
    # High-quality parameters: large population, many generations
    trajet, temps, groupes = solve_genetic(
        passagers, conducteur,
        population_size=200,
        generations=300,
        mutation_rate=0.10,  # Lower mutation for exploitation
        verbose=True
    )
    
    print(f"\n✓ Optimized solution!")


def demo_custom_constraints():
    """Demo 4: Custom clustering constraints"""
    print("\n" + "="*70)
    print("DEMO 4: Loose Clustering Constraints")
    print("="*70)
    
    conducteur = Conducteur(position=(0, 0), capacite=6)
    passagers = [
        Passager(id=i, 
                pos_depart=(i*3, i*2), 
                pos_arrivee=(30+i*2, 35+i))
        for i in range(1, 13)
    ]
    
    # Larger clustering radii allow more passengers per cluster
    trajet, temps, groupes = solve_genetic(
        passagers, conducteur,
        R_dest=10.0,   # Larger radius
        R_depart=10.0,  # Larger radius
        verbose=True
    )
    
    print(f"\n✓ With loose constraints, formed {len(groupes)} clusters")


def demo_advanced_usage():
    """Demo 5: Advanced usage with solver object"""
    print("\n" + "="*70)
    print("DEMO 5: Advanced Usage with Custom Solver")
    print("="*70)
    
    conducteur = Conducteur(position=(0, 0), capacite=4)
    passagers = [
        Passager(id=i, 
                pos_depart=(i*2, i*2), 
                pos_arrivee=(20+i*3, 25+i*2))
        for i in range(1, 9)
    ]
    
    # Create solver with custom parameters
    solver = GeneticCarpoolingSolver(
        passagers=passagers,
        conducteur=conducteur,
        population_size=80,
        generations=150,
        mutation_rate=0.20,
        elite_size=15,
        tournament_size=7,
        R_dest=6.0,
        R_depart=6.0,
        verbose=True
    )
    
    # Run the solver
    groupes, trajet, temps = solver.solve()
    
    # Access additional information
    print(f"\n✓ Best fitness achieved: {solver.best_fitness:.2f}")
    print(f"✓ Fitness improved over {len(solver.fitness_history)} generations")
    
    # Show fitness evolution
    if len(solver.fitness_history) > 0:
        print(f"✓ Initial fitness: {solver.fitness_history[0]:.2f}")
        print(f"✓ Final fitness: {solver.fitness_history[-1]:.2f}")
        improvement = solver.fitness_history[0] - solver.fitness_history[-1]
        print(f"✓ Total improvement: {improvement:.2f}")


def demo_parameter_comparison():
    """Demo 6: Compare different parameter settings"""
    print("\n" + "="*70)
    print("DEMO 6: Parameter Sensitivity Analysis")
    print("="*70)
    
    conducteur = Conducteur(position=(0, 0), capacite=4)
    passagers = [
        Passager(id=i, 
                pos_depart=(i % 5 * 3, i // 5 * 3), 
                pos_arrivee=(20 + i % 5 * 2, 25 + i // 5 * 2))
        for i in range(1, 11)
    ]
    
    configurations = [
        {"name": "Small Pop", "pop_size": 30, "generations": 100},
        {"name": "Large Pop", "pop_size": 150, "generations": 100},
        {"name": "Many Gens", "pop_size": 50, "generations": 300},
    ]
    
    print("\nTesting different configurations...")
    results = []
    
    for config in configurations:
        print(f"\n{config['name']}: pop={config['pop_size']}, gen={config['generations']}")
        
        import time
        start = time.time()
        
        trajet, temps, groupes = solve_genetic(
            passagers, conducteur,
            population_size=config['pop_size'],
            generations=config['generations'],
            verbose=False
        )
        
        elapsed = time.time() - start
        passengers_served = sum(len(g['passagers']) for g in groupes)
        
        results.append({
            'config': config['name'],
            'time': elapsed,
            'passengers': passengers_served,
            'clusters': len(groupes)
        })
        
        print(f"  Time: {elapsed:.2f}s, Passengers: {passengers_served}, Clusters: {len(groupes)}")
    
    print("\n" + "-"*70)
    print("Summary:")
    for r in results:
        print(f"  {r['config']:<15} {r['time']:.2f}s  {r['passengers']} passengers  {r['clusters']} clusters")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("GENETIC ALGORITHM CARPOOLING - DEMONSTRATIONS")
    print("="*70)
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Fast Solution", demo_fast_solution),
        ("High Quality", demo_high_quality),
        ("Custom Constraints", demo_custom_constraints),
        ("Advanced Usage", demo_advanced_usage),
        ("Parameter Comparison", demo_parameter_comparison),
    ]
    
    print("\nAvailable demonstrations:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all demos")
    
    try:
        choice = input("\nSelect demo (0-6): ").strip()
        
        if choice == '0':
            for name, demo_func in demos:
                demo_func()
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                demos[idx][1]()
            else:
                print("Invalid choice!")
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

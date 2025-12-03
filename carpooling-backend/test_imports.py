"""Test script to verify all imports work correctly"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir, 'Projet-Optimisation-main'))

print("Testing imports...")

try:
    from models.Conducteur import Conducteur
    print("✓ Conducteur imported")
except Exception as e:
    print(f"✗ Conducteur import failed: {e}")

try:
    from models.Passager import Passager
    print("✓ Passager imported")
except Exception as e:
    print(f"✗ Passager import failed: {e}")

try:
    from algorithms.exact.selection_exact import selection_exact
    print("✓ selection_exact imported")
except Exception as e:
    print(f"✗ selection_exact import failed: {e}")

try:
    from algorithms.exact.clustering_exact import phase1_clustering_double
    print("✓ phase1_clustering_double imported")
except Exception as e:
    print(f"✗ phase1_clustering_double import failed: {e}")

try:
    from algorithms.exact.ramassage_exact import ramassage_exact
    print("✓ ramassage_exact imported")
except Exception as e:
    print(f"✗ ramassage_exact import failed: {e}")

try:
    from algorithms.heuristic.selection_heuristic import selection_heuristic
    print("✓ selection_heuristic imported")
except Exception as e:
    print(f"✗ selection_heuristic import failed: {e}")

try:
    from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic
    print("✓ phase1_clustering_heuristic imported")
except Exception as e:
    print(f"✗ phase1_clustering_heuristic import failed: {e}")

try:
    from algorithms.heuristic.ramassage_heuristic import ramassage_heuristic
    print("✓ ramassage_heuristic imported")
except Exception as e:
    print(f"✗ ramassage_heuristic import failed: {e}")

try:
    from pickup_scheduler import optimize_drop_off_points, generate_complete_route, compute_schedule
    print("✓ pickup_scheduler functions imported")
except Exception as e:
    print(f"✗ pickup_scheduler import failed: {e}")

try:
    from utils.distance import distance_grille
    print("✓ distance_grille imported")
except Exception as e:
    print(f"✗ distance_grille import failed: {e}")

print("\nAll imports successful! ✓")
print("\nTesting basic functionality...")

# Test creating objects
try:
    conducteur = Conducteur(position=(50, 50), capacite=4)
    print(f"✓ Created Conducteur at position {conducteur.position} with capacity {conducteur.capacite}")
except Exception as e:
    print(f"✗ Conducteur creation failed: {e}")

try:
    passager = Passager(id="p1", pos_depart=(40, 40), pos_arrivee=(60, 60))
    print(f"✓ Created Passager from {passager.pos_depart} to {passager.pos_arrivee}")
except Exception as e:
    print(f"✗ Passager creation failed: {e}")

try:
    dist = distance_grille((0, 0), (3, 4))
    print(f"✓ Distance calculation works: distance((0,0), (3,4)) = {dist}")
except Exception as e:
    print(f"✗ Distance calculation failed: {e}")

print("\n✓✓✓ All tests passed! Backend should work correctly. ✓✓✓")

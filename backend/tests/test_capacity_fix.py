"""
Test to verify capacity constraint is properly enforced
Tests that driver with capacity=2 only picks up maximum 2 passengers total
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_capacity_constraint_exact():
    """Test exact mode with 6 passengers and capacity 2"""
    print("\n" + "="*70)
    print("TEST: Capacity Constraint - 6 Passengers, Capacity 2 (EXACT MODE)")
    print("="*70)
    
    payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 2  # CAPACITY = 2
        },
        "passengers": [
            {"id": "p1", "name": "Alice", "pickup_lat": 31.63, "pickup_lon": -7.98, "dest_lat": 31.64, "dest_lon": -7.97},
            {"id": "p2", "name": "Bob", "pickup_lat": 31.632, "pickup_lon": -7.982, "dest_lat": 31.642, "dest_lon": -7.972},
            {"id": "p3", "name": "Charlie", "pickup_lat": 31.628, "pickup_lon": -7.985, "dest_lat": 31.638, "dest_lon": -7.975},
            {"id": "p4", "name": "Diana", "pickup_lat": 31.625, "pickup_lon": -7.988, "dest_lat": 31.635, "dest_lon": -7.978},
            {"id": "p5", "name": "Eve", "pickup_lat": 31.631, "pickup_lon": -7.983, "dest_lat": 31.641, "dest_lon": -7.973},
            {"id": "p6", "name": "Frank", "pickup_lat": 31.627, "pickup_lon": -7.986, "dest_lat": 31.637, "dest_lon": -7.976}
        ],
        "mode": "exact",
        "R_dest": 20,
        "R_depart": 20
    }
    
    response = requests.post(f"{BASE_URL}/api/optimize", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Request succeeded")
        print(f"Algorithm: {data['algorithm']}")
        print(f"Passengers assigned: {data['assignment_count']}")
        print(f"Driver capacity: {data['statistics']['driver_capacity']}")
        
        # Check capacity constraint
        max_in_car = 0
        capacity_violated = False
        
        print("\n📋 Route Schedule:")
        print("-" * 70)
        for stop in data['schedule']:
            in_car = stop.get('passengers_in_car', 0)
            max_in_car = max(max_in_car, in_car)
            
            print(f"{stop['point']:15} | Type: {stop['type']:8} | "
                  f"Passengers: {len(stop.get('passengers', []))} | "
                  f"In car: {in_car}")
            
            if in_car > 2:
                capacity_violated = True
                print(f"  ⚠️  CAPACITY VIOLATION! {in_car} passengers in car (max=2)")
        
        print("-" * 70)
        print(f"\nMax passengers in car at any time: {max_in_car}")
        print(f"Capacity: 2")
        
        if capacity_violated:
            print("\n❌ TEST FAILED: Capacity was violated during route!")
            return False
        elif data['assignment_count'] > 2:
            print(f"\n❌ TEST FAILED: Assigned {data['assignment_count']} passengers but capacity is 2!")
            return False
        else:
            print("\n✅ TEST PASSED: Capacity constraint respected!")
            print(f"   - Only {data['assignment_count']} passengers assigned (capacity=2)")
            print(f"   - Max passengers in car: {max_in_car}")
            return True
            
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        print(response.text)
        return False


def test_capacity_constraint_heuristic():
    """Test heuristic mode with 6 passengers and capacity 2"""
    print("\n" + "="*70)
    print("TEST: Capacity Constraint - 6 Passengers, Capacity 2 (HEURISTIC MODE)")
    print("="*70)
    
    payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 2  # CAPACITY = 2
        },
        "passengers": [
            {"id": "p1", "name": "Alice", "pickup_lat": 31.63, "pickup_lon": -7.98, "dest_lat": 31.64, "dest_lon": -7.97},
            {"id": "p2", "name": "Bob", "pickup_lat": 31.632, "pickup_lon": -7.982, "dest_lat": 31.642, "dest_lon": -7.972},
            {"id": "p3", "name": "Charlie", "pickup_lat": 31.628, "pickup_lon": -7.985, "dest_lat": 31.638, "dest_lon": -7.975},
            {"id": "p4", "name": "Diana", "pickup_lat": 31.625, "pickup_lon": -7.988, "dest_lat": 31.635, "dest_lon": -7.978},
            {"id": "p5", "name": "Eve", "pickup_lat": 31.631, "pickup_lon": -7.983, "dest_lat": 31.641, "dest_lon": -7.973},
            {"id": "p6", "name": "Frank", "pickup_lat": 31.627, "pickup_lon": -7.986, "dest_lat": 31.637, "dest_lon": -7.976}
        ],
        "mode": "heuristic",
        "R_dest": 20,
        "R_depart": 20
    }
    
    response = requests.post(f"{BASE_URL}/api/optimize", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Request succeeded")
        print(f"Passengers assigned: {data['assignment_count']}")
        
        max_in_car = max((stop.get('passengers_in_car', 0) for stop in data['schedule']), default=0)
        
        if max_in_car > 2:
            print(f"\n❌ TEST FAILED: Max {max_in_car} passengers in car (capacity=2)")
            return False
        elif data['assignment_count'] > 2:
            print(f"\n❌ TEST FAILED: Assigned {data['assignment_count']} passengers (capacity=2)")
            return False
        else:
            print(f"\n✅ TEST PASSED: Only {data['assignment_count']} passengers, max in car: {max_in_car}")
            return True
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        return False


def test_capacity_constraint_genetic():
    """Test genetic mode with 6 passengers and capacity 2"""
    print("\n" + "="*70)
    print("TEST: Capacity Constraint - 6 Passengers, Capacity 2 (GENETIC MODE)")
    print("="*70)
    
    payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 2  # CAPACITY = 2
        },
        "passengers": [
            {"id": "p1", "name": "Alice", "pickup_lat": 31.63, "pickup_lon": -7.98, "dest_lat": 31.64, "dest_lon": -7.97},
            {"id": "p2", "name": "Bob", "pickup_lat": 31.632, "pickup_lon": -7.982, "dest_lat": 31.642, "dest_lon": -7.972},
            {"id": "p3", "name": "Charlie", "pickup_lat": 31.628, "pickup_lon": -7.985, "dest_lat": 31.638, "dest_lon": -7.975},
            {"id": "p4", "name": "Diana", "pickup_lat": 31.625, "pickup_lon": -7.988, "dest_lat": 31.635, "dest_lon": -7.978},
            {"id": "p5", "name": "Eve", "pickup_lat": 31.631, "pickup_lon": -7.983, "dest_lat": 31.641, "dest_lon": -7.973},
            {"id": "p6", "name": "Frank", "pickup_lat": 31.627, "pickup_lon": -7.986, "dest_lat": 31.637, "dest_lon": -7.976}
        ],
        "mode": "genetic",
        "R_dest": 20,
        "R_depart": 20,
        "population_size": 50,
        "generations": 100,
        "mutation_rate": 0.15
    }
    
    response = requests.post(f"{BASE_URL}/api/optimize", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Request succeeded")
        print(f"Passengers assigned: {data['assignment_count']}")
        
        max_in_car = max((stop.get('passengers_in_car', 0) for stop in data['schedule']), default=0)
        
        if max_in_car > 2:
            print(f"\n❌ TEST FAILED: Max {max_in_car} passengers in car (capacity=2)")
            return False
        elif data['assignment_count'] > 2:
            print(f"\n❌ TEST FAILED: Assigned {data['assignment_count']} passengers (capacity=2)")
            return False
        else:
            print(f"\n✅ TEST PASSED: Only {data['assignment_count']} passengers, max in car: {max_in_car}")
            return True
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("CAPACITY CONSTRAINT VALIDATION TEST")
    print("="*70)
    print("\nScenario: 6 passengers, driver capacity = 2")
    print("Expected: Driver should pick up MAXIMUM 2 passengers total")
    print("Bug was: Driver was picking up 2, dropping them, picking 2 more, etc.")
    print("="*70)
    
    try:
        results = []
        
        # Test all three modes
        results.append(("Exact", test_capacity_constraint_exact()))
        results.append(("Heuristic", test_capacity_constraint_heuristic()))
        results.append(("Genetic", test_capacity_constraint_genetic()))
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        all_passed = True
        for mode, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{mode:12} - {status}")
            if not passed:
                all_passed = False
        
        print("="*70)
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! Capacity constraint is properly enforced.")
        else:
            print("\n⚠️  SOME TESTS FAILED! Capacity constraint may still have issues.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Make sure FastAPI is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

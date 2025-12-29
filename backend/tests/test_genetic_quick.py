"""
Quick test for the genetic algorithm capacity fix
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_genetic_capacity_2():
    """Test genetic with 6 passengers and capacity 2"""
    print("\n" + "="*70)
    print("GENETIC ALGORITHM - Capacity 2, 6 Passengers")
    print("="*70)
    
    payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 2
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
        "R_dest": 25.0,
        "R_depart": 25.0,
        "population_size": 140,
        "generations": 250,
        "mutation_rate": 0.2
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/api/optimize", json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"  Algorithm: {data['algorithm']}")
        print(f"  Assigned: {data['assignment_count']} passengers")
        print(f"  Capacity: {data['statistics']['driver_capacity']}")
        print(f"  Total passengers: {data['statistics']['total_passengers']}")
        
        print("\n📋 Schedule:")
        for stop in data['schedule']:
            in_car = stop.get('passengers_in_car', 0)
            print(f"  {stop['point']:10} | {stop['type']:8} | In car: {in_car}")
        
        max_in_car = max((s.get('passengers_in_car', 0) for s in data['schedule']), default=0)
        
        if data['assignment_count'] > 2:
            print(f"\n❌ FAILED: Assigned {data['assignment_count']} > capacity 2")
            return False
        elif max_in_car > 2:
            print(f"\n❌ FAILED: Max in car {max_in_car} > capacity 2")
            return False
        else:
            print(f"\n✅ PASSED: Capacity respected!")
            return True
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    try:
        test_genetic_capacity_2()
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

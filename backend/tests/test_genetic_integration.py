"""
Quick test script for Genetic Algorithm integration
Tests that the API can handle genetic algorithm requests
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_genetic_optimization():
    """Test genetic algorithm optimization"""
    print("\n" + "="*60)
    print("Testing Genetic Algorithm Optimization")
    print("="*60)
    
    payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 4
        },
        "passengers": [
            {
                "id": "p1",
                "name": "Alice",
                "pickup_lat": 31.63,
                "pickup_lon": -7.98,
                "dest_lat": 31.64,
                "dest_lon": -7.97
            },
            {
                "id": "p2",
                "name": "Bob",
                "pickup_lat": 31.632,
                "pickup_lon": -7.982,
                "dest_lat": 31.642,
                "dest_lon": -7.972
            },
            {
                "id": "p3",
                "name": "Charlie",
                "pickup_lat": 31.628,
                "pickup_lon": -7.985,
                "dest_lat": 31.638,
                "dest_lon": -7.975
            },
            {
                "id": "p4",
                "name": "Diana",
                "pickup_lat": 31.625,
                "pickup_lon": -7.988,
                "dest_lat": 31.635,
                "dest_lon": -7.978
            }
        ],
        "mode": "genetic",
        "R_dest": 20,
        "R_depart": 20,
        "population_size": 50,
        "generations": 100,
        "mutation_rate": 0.15
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    print(f"\nSending request to {BASE_URL}/api/optimize...")
    response = requests.post(
        f"{BASE_URL}/api/optimize",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"Algorithm: {data.get('algorithm')}")
        print(f"Passengers Assigned: {data.get('assignment_count')}")
        print(f"Pickup Points: {data.get('statistics', {}).get('pickup_points')}")
        print(f"Dropoff Points: {data.get('statistics', {}).get('dropoff_points')}")
        print(f"Total Distance: {data.get('total_distance_km')} km")
        print(f"Total Time: {data.get('total_time_min')} min")
        return True
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {response.text}")
        return False

def test_all_modes():
    """Test all three optimization modes"""
    print("\n" + "="*60)
    print("Testing All Optimization Modes")
    print("="*60)
    
    base_payload = {
        "driver": {
            "lat": 31.6295,
            "lon": -7.9811,
            "capacity": 4
        },
        "passengers": [
            {"id": "p1", "name": "P1", "pickup_lat": 31.63, "pickup_lon": -7.98, "dest_lat": 31.64, "dest_lon": -7.97},
            {"id": "p2", "name": "P2", "pickup_lat": 31.632, "pickup_lon": -7.982, "dest_lat": 31.642, "dest_lon": -7.972},
            {"id": "p3", "name": "P3", "pickup_lat": 31.628, "pickup_lon": -7.985, "dest_lat": 31.638, "dest_lon": -7.975}
        ],
        "R_dest": 20,
        "R_depart": 20
    }
    
    modes = ["heuristic", "exact", "genetic"]
    results = {}
    
    for mode in modes:
        print(f"\n--- Testing {mode.upper()} mode ---")
        payload = base_payload.copy()
        payload["mode"] = mode
        
        if mode == "genetic":
            payload.update({
                "population_size": 50,
                "generations": 100,
                "mutation_rate": 0.15
            })
        
        response = requests.post(f"{BASE_URL}/api/optimize", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            results[mode] = {
                "status": "✅ Success",
                "assigned": data.get("assignment_count"),
                "distance": data.get("total_distance_km"),
                "time": data.get("total_time_min")
            }
            print(f"✅ {mode}: {data.get('assignment_count')} passengers, {data.get('total_distance_km')} km")
        else:
            results[mode] = {"status": "❌ Failed", "error": response.text[:100]}
            print(f"❌ {mode} failed: {response.status_code}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for mode, result in results.items():
        print(f"{mode.upper():12} - {result['status']}")
    
    return all(r.get("status", "").startswith("✅") for r in results.values())

if __name__ == "__main__":
    print("="*60)
    print("GENETIC ALGORITHM INTEGRATION TEST")
    print("="*60)
    print("\nMake sure the FastAPI server is running:")
    print("  cd backend")
    print("  python main.py")
    print("\nThen run this test script.")
    print("="*60)
    
    try:
        # Test 1: Health check
        if not test_health():
            print("\n❌ Health check failed. Is the server running?")
            exit(1)
        
        # Test 2: Genetic optimization
        if not test_genetic_optimization():
            print("\n❌ Genetic optimization test failed")
            exit(1)
        
        # Test 3: All modes
        if not test_all_modes():
            print("\n⚠️ Some modes failed")
            exit(1)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nGenetic Algorithm integration is working correctly!")
        print("You can now use the frontend with genetic mode enabled.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Make sure FastAPI is running on http://localhost:5000")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

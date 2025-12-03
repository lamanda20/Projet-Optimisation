# Carpool Backend API - Bus-Style System

Flask backend API that implements a **bus-style carpool system** using advanced optimization algorithms from Projet-Optimisation-main.

## How It Works

Unlike traditional carpooling where each passenger is dropped at their exact destination, this system works like a bus:

1. **Passenger Grouping**: Groups passengers with similar origins and destinations
2. **Pickup Points**: Creates centralized pickup points where passengers walk to board
3. **Drop-off Points**: Creates centralized drop-off points where passengers walk from
4. **Route Optimization**: Uses TSP (Traveling Salesman Problem) algorithms to optimize the route

This approach:
- ✅ Reduces total driving distance
- ✅ Minimizes detours
- ✅ Increases efficiency for multiple passengers
- ✅ Works better for dense urban areas

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns system status and confirms bus-style mode.

### Main Optimization Endpoint
```
POST /api/optimize
```

**Request Body:**
```json
{
  "driver": {
    "lat": 31.6295,
    "lon": -7.9811,
    "capacity": 4
  },
  "passengers": [
    {
      "id": "p1",
      "name": "Passenger 1",
      "pickup_lat": 31.63,
      "pickup_lon": -7.98,
      "dest_lat": 31.64,
      "dest_lon": -7.97
    }
  ],
  "mode": "heuristic",  // "exact" or "heuristic"
  "R_dest": 15,         // optional, radius for destination clustering
  "R_depart": 15        // optional, radius for pickup clustering
}
```

## Algorithm Modes

- **exact**: Optimal solution using Hungarian algorithm + Branch & Bound TSP
  - Guarantees best solution
  - Best for ≤10 passengers
  - Slower computation

- **heuristic**: Fast solution using Greedy + K-means + Nearest Neighbor TSP
  - ~95% optimal
  - Best for 10+ passengers
  - Very fast computation

## Optimization Phases

The backend runs through 6 phases:

1. **Selection**: Choose optimal passenger subset (Hungarian/Greedy)
2. **Clustering**: Group passengers by destinations (DBSCAN/Distance-based)
3. **Pickup Points**: Determine centralized pickup locations
4. **Drop-off Points**: Determine centralized drop-off locations
5. **Route Planning**: Calculate optimal visit order (TSP)
6. **Scheduling**: Compute arrival/departure times

## Response Format

```json
{
  "success": true,
  "algorithm": "phase1-heuristic",
  "route": [
    {"lat": 31.6295, "lon": -7.9811, "type": "start", "label": "Driver Start"},
    {"lat": 31.63, "lon": -7.98, "type": "pickup", "label": "R1", "passengers": ["p1", "p2"]},
    {"lat": 31.64, "lon": -7.97, "type": "dropoff", "label": "D1", "passengers": ["p1", "p2"]}
  ],
  "pickup_points": [
    {
      "lat": 31.63,
      "lon": -7.98,
      "type": "pickup",
      "label": "Pickup R1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    }
  ],
  "dropoff_points": [
    {
      "lat": 31.64,
      "lon": -7.97,
      "type": "dropoff",
      "label": "Drop-off D1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    }
  ],
  "assigned_passengers": {
    "p1": {
      "name": "Passenger 1",
      "original_pickup": {"lat": 31.6301, "lon": -7.9801},
      "original_destination": {"lat": 31.6401, "lon": -7.9701},
      "assigned_pickup": {"lat": 31.63, "lon": -7.98, "label": "Pickup R1"},
      "assigned_dropoff": {"lat": 31.64, "lon": -7.97, "label": "Drop-off D1"},
      "walk_to_pickup_km": 0.15,
      "walk_from_dropoff_km": 0.12
    }
  },
  "total_distance_km": 12.5,
  "total_time_min": 25,
  "assignment_count": 3,
  "schedule": [
    {
      "point": "Depart",
      "arrival": "2025-12-03T08:00:00",
      "departure": "2025-12-03T08:00:00",
      "board": 0,
      "alight": 0,
      "cumulative": 0,
      "dwell_minutes": 0,
      "passengers_boarded": [],
      "passengers_alighted": []
    }
  ],
  "statistics": {
    "total_passengers": 5,
    "selected_passengers": 3,
    "pickup_points": 2,
    "dropoff_points": 2,
    "total_stops": 4,
    "driver_capacity": 4
  }
}
```

## Configuration Parameters

### R_dest (Destination Radius)
- Distance threshold for grouping similar destinations
- Larger values = fewer drop-off points, longer walks
- Recommended: 15-25 (grid units, ~1.5-2.5km)

### R_depart (Departure Radius)
- Distance threshold for grouping similar pickups
- Larger values = fewer pickup points, longer walks
- Recommended: 15-25 (grid units, ~1.5-2.5km)

## GPS Coordinate System

The system converts between GPS coordinates (lat/lon) and a grid system:

- **Marrakech Bounds**: Lat 31.58-31.68, Lon -8.05 to -7.92
- **Grid Size**: 100x100 (0-99 in each dimension)
- **Conversion**: Automatic, transparent to frontend

"""
Flask Backend API for Marrakech Carpool Application
Bus-style system: Groups passengers and creates pickup/drop-off points
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
from typing import List, Dict, Any, Tuple
import math

# Add parent directory to path to import from Projet-Optimisation-main
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir, 'Projet-Optimisation-main'))

from models.Conducteur import Conducteur
from models.Passager import Passager
from algorithms.exact.selection_exact import selection_exact
from algorithms.exact.clustering_exact import phase1_clustering_double
from algorithms.exact.ramassage_exact import ramassage_exact
from algorithms.heuristic.selection_heuristic import selection_heuristic
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic
from algorithms.heuristic.ramassage_heuristic import ramassage_heuristic
from algorithms.phase2_integrator import phase2_solve, generate_affectations_par_point
from pickup_scheduler import (
    optimize_drop_off_points,
    generate_complete_route,
    compute_schedule,
    determine_stop_point_per_passenger
)
from utils.distance import distance_grille

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# GPS Coordinate Conversion Constants
# Marrakech bounds: lat 31.58-31.68, lon -8.05 to -7.92
MARRAKECH_LAT_MIN = 31.58
MARRAKECH_LAT_MAX = 31.68
MARRAKECH_LON_MIN = -8.05
MARRAKECH_LON_MAX = -7.92
GRID_SIZE = 100  # 100x100 grid


def gps_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    """Convert GPS coordinates to grid coordinates (0-99)"""
    # Normalize lat/lon to 0-1 range
    lat_norm = (lat - MARRAKECH_LAT_MIN) / (MARRAKECH_LAT_MAX - MARRAKECH_LAT_MIN)
    lon_norm = (lon - MARRAKECH_LON_MIN) / (MARRAKECH_LON_MAX - MARRAKECH_LON_MIN)
    
    # Clamp to valid range
    lat_norm = max(0, min(1, lat_norm))
    lon_norm = max(0, min(1, lon_norm))
    
    # Scale to grid size
    x = int(lat_norm * (GRID_SIZE - 1))
    y = int(lon_norm * (GRID_SIZE - 1))
    
    return (x, y)


def grid_to_gps(x: int, y: int) -> Tuple[float, float]:
    """Convert grid coordinates to GPS coordinates"""
    # Normalize grid to 0-1 range
    lat_norm = x / (GRID_SIZE - 1)
    lon_norm = y / (GRID_SIZE - 1)
    
    # Scale to GPS range
    lat = MARRAKECH_LAT_MIN + lat_norm * (MARRAKECH_LAT_MAX - MARRAKECH_LAT_MIN)
    lon = MARRAKECH_LON_MIN + lon_norm * (MARRAKECH_LON_MAX - MARRAKECH_LON_MIN)
    
    return (lat, lon)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Carpool Backend API is running",
        "system": "bus-style with pickup/dropoff points"
    })


@app.route('/api/optimize', methods=['POST'])
def optimize_carpool():
    """
    Main optimization endpoint - creates passenger groups and pickup/dropoff points
    
    Request body:
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
            },
            ...
        ],
        "mode": "exact" | "heuristic",
        "R_dest": 15,  // optional, radius for destination clustering
        "R_depart": 15  // optional, radius for pickup clustering
    }
    """
    try:
        data = request.json
        logger.info(f"Received optimization request with {len(data.get('passengers', []))} passengers")
        
        # Extract parameters
        driver_data = data.get('driver', {})
        passengers_data = data.get('passengers', [])
        mode = data.get('mode', 'heuristic')
        R_dest = data.get('R_dest', 15)
        R_depart = data.get('R_depart', 15)
        
        if not passengers_data:
            return jsonify({"error": "No passengers provided"}), 400
        
        # Convert driver GPS to grid
        driver_lat = driver_data.get('lat', 31.6295)
        driver_lon = driver_data.get('lon', -7.9811)
        driver_grid = gps_to_grid(driver_lat, driver_lon)
        driver_capacity = driver_data.get('capacity', 4)
        
        # Create Conducteur object
        conducteur = Conducteur(
            position=driver_grid,
            capacite=driver_capacity
        )
        
        # Convert passengers GPS to grid and create Passager objects
        passagers = []
        for idx, pax in enumerate(passengers_data):
            pickup_grid = gps_to_grid(pax['pickup_lat'], pax['pickup_lon'])
            dest_grid = gps_to_grid(pax['dest_lat'], pax['dest_lon'])
            
            passager = Passager(
                id=pax.get('id', f"P{idx+1}"),
                pos_depart=pickup_grid,
                pos_arrivee=dest_grid
            )
            passagers.append(passager)
            logger.info(f"Passenger {passager.id}: pickup GPS({pax['pickup_lat']:.6f},{pax['pickup_lon']:.6f}) → grid{pickup_grid}, dest GPS({pax['dest_lat']:.6f},{pax['dest_lon']:.6f}) → grid{dest_grid}")
        
        logger.info(f"Driver: GPS({driver_lat:.6f},{driver_lon:.6f}) → grid{driver_grid}, capacity={driver_capacity}")
        logger.info(f"Using {mode} algorithm with R_dest={R_dest}, R_depart={R_depart}")
        
        # PHASE 1: Clustering - Create valid groups
        if mode == "exact":
            groupes_valides = phase1_clustering_double(passagers, conducteur, R_dest, R_depart)
        else:
            groupes_valides = phase1_clustering_heuristic(passagers, conducteur, R_dest, R_depart)
        
        logger.info(f"Phase 1 clustering result: {len(groupes_valides) if groupes_valides else 0} groups")
        
        if not groupes_valides:
            logger.warning("No valid passenger groups could be formed")
            return jsonify({
                "success": False,
                "error": "No valid passenger groups could be formed. Try adjusting R_dest and R_depart parameters."
            }), 400
        
        logger.info(f"Created {len(groupes_valides)} valid groups")
        
        # PHASE 2: Selection - Choose optimal group
        if mode == "exact":
            groupe_optimal = selection_exact(groupes_valides, conducteur)
        else:
            groupe_optimal = selection_heuristic(groupes_valides, conducteur)
        
        logger.info(f"Phase 2 selection result: {len(groupe_optimal) if groupe_optimal else 0} passengers")
        
        if not groupe_optimal:
            logger.warning("No passengers could be selected from valid groups")
            return jsonify({
                "success": False,
                "error": "No passengers could be selected. Check driver capacity and passenger distribution."
            }), 400
        
        logger.info(f"Selected optimal group with {len(groupe_optimal)} passengers")
        
        # PHASE 3: Determine pickup points for the selected group
        if mode == "exact":
            points_ramassage = ramassage_exact(groupe_optimal)
        else:
            points_ramassage = ramassage_heuristic(groupe_optimal)
        
        logger.info(f"Created {len(points_ramassage)} pickup points")
        
        # PHASE 4: Determine drop-off points
        points_arret = optimize_drop_off_points(groupe_optimal, method=mode)
        
        logger.info(f"Created {len(points_arret)} drop-off points")
        
        # PHASE 5: Generate complete route with TSP optimization
        trajet_complete, affectations_complete, temps_complete = generate_complete_route(
            points_ramassage,
            points_arret,
            driver_grid
        )
        
        logger.info(f"Generated route with {len(trajet_complete)} stops")
        
        # PHASE 6: Compute schedule with times
        schedule = compute_schedule(
            trajet_complete,
            affectations_complete,
            temps_complete,
            start_time="08:00",
            stop_time_per_passenger_min=1,
            default_travel_min=5
        )
        
        # Convert grid coordinates back to GPS for frontend
        route_gps = []
        pickup_points_gps = []
        dropoff_points_gps = []
        
        # Add driver start position
        route_gps.append({
            "lat": driver_lat,
            "lon": driver_lon,
            "type": "start",
            "label": "Driver Start"
        })
        
        # Add pickup points
        for i, point_info in enumerate(points_ramassage):
            point_grid = point_info['point_ramassage']
            lat, lon = grid_to_gps(point_grid[0], point_grid[1])
            
            passenger_ids = [p.id for p in point_info['passagers']]
            
            pickup_points_gps.append({
                "lat": lat,
                "lon": lon,
                "type": "pickup",
                "label": f"Pickup R{i+1}",
                "passengers": passenger_ids,
                "passenger_count": len(passenger_ids)
            })
            route_gps.append({
                "lat": lat,
                "lon": lon,
                "type": "pickup",
                "label": f"R{i+1}",
                "passengers": passenger_ids
            })
        
        # Add drop-off points
        for i, point_info in enumerate(points_arret):
            point_grid = point_info['point_arret']
            lat, lon = grid_to_gps(point_grid[0], point_grid[1])
            
            passenger_ids = [p.id for p in point_info['passagers']]
            
            dropoff_points_gps.append({
                "lat": lat,
                "lon": lon,
                "type": "dropoff",
                "label": f"Drop-off D{i+1}",
                "passengers": passenger_ids,
                "passenger_count": len(passenger_ids)
            })
            route_gps.append({
                "lat": lat,
                "lon": lon,
                "type": "dropoff",
                "label": f"D{i+1}",
                "passengers": passenger_ids
            })
        
        # Calculate statistics
        total_distance_km = 0
        total_time_min = 0
        for point, times in temps_complete.items():
            for next_point, time_val in times.items():
                total_time_min += time_val
        
        # Estimate distance from time (assuming average speed)
        total_distance_km = total_time_min * 0.5  # ~30 km/h average in city
        
        # Build passenger assignments with pickup/dropoff info
        passenger_assignments = {}
        stop_points = determine_stop_point_per_passenger(affectations_complete)
        
        for passenger_id, stops in stop_points.items():
            # Find which pickup and dropoff point this passenger uses
            pickup_point_idx = None
            dropoff_point_idx = None
            
            # Find in pickup points
            for i, point_info in enumerate(points_ramassage):
                if any(p.id == passenger_id for p in point_info['passagers']):
                    pickup_point_idx = i
                    break
            
            # Find in dropoff points
            for i, point_info in enumerate(points_arret):
                if any(p.id == passenger_id for p in point_info['passagers']):
                    dropoff_point_idx = i
                    break
            
            if pickup_point_idx is not None and dropoff_point_idx is not None:
                pickup_gps = pickup_points_gps[pickup_point_idx]
                dropoff_gps = dropoff_points_gps[dropoff_point_idx]
                
                # Find original passenger data
                original_passenger = next((p for p in passengers_data if p.get('id') == passenger_id or p.get('id') == passenger_id[1:]), None)
                
                if original_passenger:
                    passenger_assignments[passenger_id] = {
                        "name": original_passenger.get('name', passenger_id),
                        "original_pickup": {
                            "lat": original_passenger['pickup_lat'],
                            "lon": original_passenger['pickup_lon']
                        },
                        "original_destination": {
                            "lat": original_passenger['dest_lat'],
                            "lon": original_passenger['dest_lon']
                        },
                        "assigned_pickup": {
                            "lat": pickup_gps['lat'],
                            "lon": pickup_gps['lon'],
                            "label": pickup_gps['label']
                        },
                        "assigned_dropoff": {
                            "lat": dropoff_gps['lat'],
                            "lon": dropoff_gps['lon'],
                            "label": dropoff_gps['label']
                        },
                        "walk_to_pickup_km": haversine_distance(
                            original_passenger['pickup_lat'],
                            original_passenger['pickup_lon'],
                            pickup_gps['lat'],
                            pickup_gps['lon']
                        ),
                        "walk_from_dropoff_km": haversine_distance(
                            original_passenger['dest_lat'],
                            original_passenger['dest_lon'],
                            dropoff_gps['lat'],
                            dropoff_gps['lon']
                        )
                    }
        
        # Build response
        response = {
            "success": True,
            "algorithm": f"phase1-{mode}",
            "route": route_gps,
            "pickup_points": pickup_points_gps,
            "dropoff_points": dropoff_points_gps,
            "total_distance_km": round(total_distance_km, 2),
            "total_time_min": total_time_min,
            "assigned_passengers": passenger_assignments,
            "assignment_count": len(groupe_optimal),
            "schedule": schedule,
            "statistics": {
                "total_passengers": len(passagers),
                "selected_passengers": len(groupe_optimal),
                "pickup_points": len(points_ramassage),
                "dropoff_points": len(points_arret),
                "total_stops": len(route_gps) - 1,  # Exclude start
                "driver_capacity": driver_capacity
            }
        }
        
        logger.info(f"Successfully generated route with {len(groupe_optimal)} passengers")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in optimize_carpool: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting Carpool Backend API (Bus-style system)...")
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
FastAPI Backend for Marrakech Carpool Application
Bus-style system: Groups passengers and creates pickup/drop-off points
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
import math
import statistics

from models.Conducteur import Conducteur
from models.Passager import Passager
from algorithms.exact.selection_exact import selection_exact
from algorithms.exact.clustering_exact import phase1_clustering_double, tsp_exact_solver
from algorithms.exact.ramassage_exact import ramassage_exact
from algorithms.heuristic.selection_heuristic import selection_heuristic
from algorithms.heuristic.clustering_heuristic import phase1_clustering_heuristic, nearest_neighbor_tsp
from algorithms.heuristic.ramassage_heuristic import ramassage_heuristic
from algorithms.genetic.genetic_carpooling import solve_genetic
from algorithms.metaheuristic.selection_metaheuristic import phase1_clustering_metaheuristic
from utils.distance import distance_grille
from utils.centroide import calculer_centroide_grille

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Marrakech Carpool API",
    description="Optimization API for bus-style carpooling with pickup/dropoff points",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MARRAKECH_LAT_MIN = 31.58
MARRAKECH_LAT_MAX = 31.68
MARRAKECH_LON_MIN = -8.05
MARRAKECH_LON_MAX = -7.92
GRID_SIZE = 100


# Pydantic Models
class DriverInput(BaseModel):
    lat: float = Field(..., ge=31.58, le=31.68, description="Driver latitude")
    lon: float = Field(..., ge=-8.05, le=-7.92, description="Driver longitude")
    capacity: int = Field(4, ge=1, le=100, description="Vehicle capacity")


class PassengerInput(BaseModel):
    id: str = Field(..., description="Passenger ID")
    name: str = Field(..., description="Passenger name")
    pickup_lat: float = Field(..., ge=31.58, le=31.68)
    pickup_lon: float = Field(..., ge=-8.05, le=-7.92)
    dest_lat: float = Field(..., ge=31.58, le=31.68)
    dest_lon: float = Field(..., ge=-8.05, le=-7.92)


class OptimizationRequest(BaseModel):
    driver: DriverInput
    passengers: List[PassengerInput] = Field(..., min_length=1)
    mode: str = Field("heuristic", pattern="^(exact|heuristic|genetic|tabou)$")
    R_dest: float = Field(1, ge=1, le=100, description="Destination clustering radius")
    R_depart: float = Field(1, ge=1, le=100, description="Pickup clustering radius")
    # Genetic algorithm parameters (only used when mode='genetic')
    population_size: int = Field(100, ge=10, le=500, description="GA population size")
    generations: int = Field(200, ge=10, le=1000, description="GA generations")
    mutation_rate: float = Field(0.15, ge=0.01, le=0.5, description="GA mutation rate")


class HealthResponse(BaseModel):
    status: str
    message: str
    system: str


class GPSPoint(BaseModel):
    lat: float
    lon: float


class RoutePoint(BaseModel):
    lat: float
    lon: float
    type: str
    label: str
    passengers: Optional[List[str]] = None


class PickupDropoffPoint(BaseModel):
    lat: float
    lon: float
    type: str
    label: str
    passengers: List[str]
    passenger_count: int


class AssignedPoint(BaseModel):
    lat: float
    lon: float
    label: str


class PassengerAssignment(BaseModel):
    name: str
    original_pickup: GPSPoint
    original_destination: GPSPoint
    assigned_pickup: AssignedPoint
    assigned_dropoff: AssignedPoint
    walk_to_pickup_km: float
    walk_from_dropoff_km: float


class Statistics(BaseModel):
    total_passengers: int
    selected_passengers: int
    pickup_points: int
    dropoff_points: int
    total_stops: int
    driver_capacity: int


class SchedulePoint(BaseModel):
    point: str
    arrival: str
    departure: str
    passengers: List[str]
    type: str
    passengers_in_car: int = 0  # Current number of passengers in car


class OptimizationResponse(BaseModel):
    success: bool
    algorithm: str
    route: List[RoutePoint]
    pickup_points: List[PickupDropoffPoint]
    dropoff_points: List[PickupDropoffPoint]
    total_distance_km: float
    total_time_min: int
    assigned_passengers: Dict[str, PassengerAssignment]
    assignment_count: int
    schedule: List[SchedulePoint]
    statistics: Statistics


# Utility Functions
def gps_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    """Convert GPS coordinates to grid coordinates (0-99)"""
    lat_norm = (lat - MARRAKECH_LAT_MIN) / (MARRAKECH_LAT_MAX - MARRAKECH_LAT_MIN)
    lon_norm = (lon - MARRAKECH_LON_MIN) / (MARRAKECH_LON_MAX - MARRAKECH_LON_MIN)
    
    lat_norm = max(0, min(1, lat_norm))
    lon_norm = max(0, min(1, lon_norm))
    
    x = int(lat_norm * (GRID_SIZE - 1))
    y = int(lon_norm * (GRID_SIZE - 1))
    
    return (x, y)


def grid_to_gps(x: int, y: int) -> Tuple[float, float]:
    """Convert grid coordinates to GPS coordinates"""
    lat_norm = x / (GRID_SIZE - 1)
    lon_norm = y / (GRID_SIZE - 1)
    
    lat = MARRAKECH_LAT_MIN + lat_norm * (MARRAKECH_LAT_MAX - MARRAKECH_LAT_MIN)
    lon = MARRAKECH_LON_MIN + lon_norm * (MARRAKECH_LON_MAX - MARRAKECH_LON_MIN)
    
    return (lat, lon)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers"""
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def optimize_drop_off_points(passagers_groupe: List[Passager], method: str = "heuristic") -> List[Dict]:
    """Create drop-off points by clustering passenger destinations"""
    if not passagers_groupe:
        return []
    
    if len(passagers_groupe) == 1:
        return [{'point_arret': passagers_groupe[0].pos_arrivee, 'passagers': [passagers_groupe[0]]}]
    
    # Calculate distances
    distances = [
        distance_grille(p1.pos_arrivee, p2.pos_arrivee)
        for i, p1 in enumerate(passagers_groupe)
        for p2 in passagers_groupe[i+1:]
    ]
    
    # Calculate threshold
    if method == "exact":
        distances_sorted = sorted(distances)
        seuil = distances_sorted[len(distances_sorted) // 2] if distances else 10
    else:
        seuil = statistics.quantiles(distances, n=4)[2] if len(distances) >= 4 else (
            max(distances) * 0.75 if distances else 10
        )
    
    # Cluster passengers
    points_arret = []
    passagers_restants = passagers_groupe.copy()
    
    while passagers_restants:
        if method == "exact":
            passager_ref = passagers_restants[0]
        else:
            voisins_count = [
                sum(1 for q in passagers_restants if distance_grille(p.pos_arrivee, q.pos_arrivee) <= seuil)
                for p in passagers_restants
            ]
            passager_ref = passagers_restants[voisins_count.index(max(voisins_count))]
        
        groupe_arret = [passager_ref]
        passagers_restants.remove(passager_ref)
        
        i = 0
        while i < len(passagers_restants):
            if distance_grille(passager_ref.pos_arrivee, passagers_restants[i].pos_arrivee) <= seuil:
                groupe_arret.append(passagers_restants.pop(i))
            else:
                i += 1
        
        centroid = calculer_centroide_grille([p.pos_arrivee for p in groupe_arret])
        points_arret.append({'point_arret': centroid, 'passagers': groupe_arret})
    
    return points_arret


def validate_capacity_constraint(
    trajet_complete: List[str],
    affectations_complete: Dict[str, Dict],
    capacity: int
) -> bool:
    """Validate that capacity is never exceeded during the route"""
    passengers_in_car = set()
    
    for point in trajet_complete:
        if point == "Depart":
            continue
        
        point_data = affectations_complete.get(point, {})
        point_type = point_data.get('type')
        passengers_at_point = point_data.get('passagers', [])
        
        if point_type == 'pickup':
            # Add passengers
            for p in passengers_at_point:
                passengers_in_car.add(p)
            # Check capacity
            if len(passengers_in_car) > capacity:
                return False
        elif point_type == 'dropoff':
            # Remove passengers
            for p in passengers_at_point:
                passengers_in_car.discard(p)
    
    return True


def compute_schedule(
    trajet_complete: List[str],
    affectations_complete: Dict[str, Dict],
    temps_complete: Dict[str, Dict[str, int]],
    start_time: str = "08:00"
) -> List[Dict]:
    """Compute arrival/departure times for the route"""
    schedule = []
    current_time = datetime.strptime(start_time, "%H:%M")
    passengers_in_car = set()
    
    for i, point in enumerate(trajet_complete):
        arrival_time = current_time
        
        num_passengers = len(affectations_complete.get(point, {}).get('passagers', []))
        dwell_minutes = num_passengers * 1
        departure_time = arrival_time + timedelta(minutes=dwell_minutes)
        
        # Track passengers in car
        point_data = affectations_complete.get(point, {})
        if point_data.get('type') == 'pickup':
            for p in point_data.get('passagers', []):
                passengers_in_car.add(p)
        elif point_data.get('type') == 'dropoff':
            for p in point_data.get('passagers', []):
                passengers_in_car.discard(p)
        
        schedule.append({
            'point': point,
            'arrival': arrival_time.strftime("%H:%M"),
            'departure': departure_time.strftime("%H:%M"),
            'passengers': affectations_complete.get(point, {}).get('passagers', []),
            'type': affectations_complete.get(point, {}).get('type', 'start'),
            'passengers_in_car': len(passengers_in_car)  # Track current load
        })
        
        if i < len(trajet_complete) - 1:
            next_point = trajet_complete[i + 1]
            travel_time = temps_complete.get(point, {}).get(next_point, 5)
            current_time = departure_time + timedelta(minutes=travel_time)
    
    return schedule


# API Endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Carpool Backend API is running",
        "system": "bus-style with pickup/dropoff points"
    }


@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_carpool(request: OptimizationRequest):
    """Main optimization endpoint - creates passenger groups and pickup/dropoff points"""
    try:
        logger.info(f"Received optimization request with {len(request.passengers)} passengers")
        
        # Convert driver GPS to grid
        driver_grid = gps_to_grid(request.driver.lat, request.driver.lon)
        conducteur = Conducteur(position=driver_grid, capacite=request.driver.capacity)
        
        # Convert passengers
        passagers = []
        for idx, pax in enumerate(request.passengers):
            pickup_grid = gps_to_grid(pax.pickup_lat, pax.pickup_lon)
            dest_grid = gps_to_grid(pax.dest_lat, pax.dest_lon)
            passagers.append(Passager(id=pax.id, pos_depart=pickup_grid, pos_arrivee=dest_grid))
        
        logger.info(f"Using {request.mode} algorithm with R_dest={request.R_dest}, R_depart={request.R_depart}")
        
        # Validate passenger count vs capacity
        if len(passagers) > conducteur.capacite:
            logger.warning(f"Passenger count ({len(passagers)}) exceeds capacity ({conducteur.capacite}). Will select best {conducteur.capacite} passengers.")
        
        # Phase 1: Clustering or Genetic Algorithm
        use_genetic_route = False  # Flag to track if we use genetic's optimized route
        if request.mode == "genetic":
            # Use genetic algorithm for complete solution
            logger.info(f"Genetic params: pop_size={request.population_size}, gen={request.generations}, mut_rate={request.mutation_rate}")
            trajet_ordre, temps_trajet, groupes = solve_genetic(
                passagers=passagers,
                conducteur=conducteur,
                R_dest=request.R_dest,
                R_depart=request.R_depart,
                population_size=request.population_size,
                generations=request.generations,
                mutation_rate=request.mutation_rate,
                verbose=True
            )
            
            # Count total passengers in genetic solution
            total_genetic_passengers = sum(len(g['passagers']) for g in groupes)
            
            if total_genetic_passengers <= conducteur.capacite:
                # Genetic solution respects capacity - use it fully
                logger.info(f"Genetic solution has {total_genetic_passengers} passengers (within capacity {conducteur.capacite})")
                groupe_optimal = []
                for groupe in groupes:
                    groupe_optimal.extend(groupe['passagers'])
                use_genetic_route = True
            else:
                # Genetic created multiple clusters exceeding capacity
                # Take only the BEST/FIRST cluster up to capacity
                logger.warning(f"Genetic solution has {total_genetic_passengers} passengers across {len(groupes)} clusters, exceeding capacity {conducteur.capacite}")
                logger.warning(f"Will use only the first cluster and rebuild route")
                
                groupe_optimal = []
                for groupe in groupes:
                    for p in groupe['passagers']:
                        if len(groupe_optimal) < conducteur.capacite:
                            groupe_optimal.append(p)
                    if len(groupe_optimal) >= conducteur.capacite:
                        break
                use_genetic_route = False  # Don't use genetic route - rebuild it
        elif request.mode == "tabou":
            groupe_result = phase1_clustering_metaheuristic(passagers, conducteur, request.R_dest, request.R_depart)
            groupe_optimal = groupe_result['passagers'] if groupe_result else []
        elif request.mode == "exact":
            groupes_valides = phase1_clustering_double(passagers, conducteur, request.R_dest, request.R_depart)
        else:
            groupes_valides = phase1_clustering_heuristic(passagers, conducteur, request.R_dest, request.R_depart)
        
        # Fallback and Selection (skip for genetic and tabou as they already have optimal solution)
        if request.mode not in ["genetic", "tabou"]:
            # Fallback: create individual groups if no clusters formed
            if not groupes_valides:
                logger.warning("No valid groups - creating individual passenger groups")
                groupes_valides = [
                    {
                        'passagers': [p],
                        'taille': 1,
                        'centre_depart': p.pos_depart,
                        'centre_arrivee': p.pos_arrivee
                    }
                    for p in passagers
                ]
            
            # Phase 2: Selection
            if request.mode == "exact":
                groupe_optimal = selection_exact(groupes_valides, conducteur)
            else:
                groupe_optimal = selection_heuristic(groupes_valides, conducteur)
            
            if not groupe_optimal:
                raise HTTPException(
                    status_code=400,
                    detail="No passengers could be selected. Check driver capacity and passenger distribution."
                )
            
            # Enforce capacity constraint - limit to capacity
            if len(groupe_optimal) > conducteur.capacite:
                logger.warning(f"Selected group ({len(groupe_optimal)}) exceeds capacity ({conducteur.capacite}). Limiting to capacity.")
                groupe_optimal = groupe_optimal[:conducteur.capacite]
        
        # Phase 3-5: Pickup/Dropoff points and TSP
        if request.mode == "genetic" and use_genetic_route:
            # Genetic algorithm provides optimized groups and route that respect capacity
            # Extract pickup points from groupes
            points_ramassage = []
            for i, groupe in enumerate(groupes):
                points_ramassage.append({
                    'point_ramassage': groupe['centre_depart'],
                    'passagers': groupe['passagers']
                })
            
            # Extract dropoff points
            points_arret = optimize_drop_off_points(groupe_optimal, method="heuristic")
        else:
            # Phase 3: Pickup points (for exact, heuristic, or genetic when capacity exceeded)
            if request.mode == "exact":
                points_ramassage = ramassage_exact(groupe_optimal)
            else:
                points_ramassage = ramassage_heuristic(groupe_optimal)
            
            # Phase 4: Drop-off points
            points_arret = optimize_drop_off_points(groupe_optimal, method=request.mode if request.mode != "genetic" else "heuristic")
        
        # Phase 5: TSP optimization
        if request.mode == "genetic" and use_genetic_route:
            # Use route from genetic algorithm trajet_ordre
            # Build affectations from genetic results
            trajet_complete = trajet_ordre
            affectations_complete = {}
            temps_complete = temps_trajet
            
            # Map trajet points to affectations
            for i, point_label in enumerate(trajet_ordre[1:], 0):  # Skip 'Depart'
                if i < len(groupes):
                    affectations_complete[point_label] = {
                        'type': 'pickup',
                        'passagers': [p.id for p in groupes[i]['passagers']],
                        'position': groupes[i]['centre_depart']
                    }
        else:
            # TSP for exact/heuristic methods
            all_points = []
            point_types = []
            point_data = []
            
            for i, p_info in enumerate(points_ramassage):
                all_points.append(p_info['point_ramassage'])
                point_types.append('pickup')
                point_data.append({'index': i, 'info': p_info, 'label': f'R{i+1}'})
            
            for i, d_info in enumerate(points_arret):
                all_points.append(d_info['point_arret'])
                point_types.append('dropoff')
                point_data.append({'index': i, 'info': d_info, 'label': f'D{i+1}'})
            
            if request.mode == "exact":
                optimal_order = tsp_exact_solver(all_points, driver_grid)
            else:
                optimal_order = nearest_neighbor_tsp(all_points, driver_grid)
            
            # Build route
            trajet_complete = ["Depart"]
            affectations_complete = {}
            temps_complete = {"Depart": {}}
            current_pos = driver_grid
            
            for order_idx in optimal_order:
                point_info = point_data[order_idx]
                label = point_info['label']
                point_pos = all_points[order_idx]
                
                trajet_complete.append(label)
                travel_time = round(distance_grille(current_pos, point_pos))
                
                prev_label = trajet_complete[-2]
                if prev_label not in temps_complete:
                    temps_complete[prev_label] = {}
                temps_complete[prev_label][label] = travel_time
                
                affectations_complete[label] = {
                    'type': point_types[order_idx],
                    'passagers': [p.id for p in point_info['info']['passagers']],
                    'position': point_pos
                }
                current_pos = point_pos
        
        # Validate capacity constraint
        if not validate_capacity_constraint(trajet_complete, affectations_complete, conducteur.capacite):
            raise HTTPException(
                status_code=500,
                detail=f"Route violates capacity constraint (max {conducteur.capacite} passengers). This is a system error."
            )
        
        # Phase 6: Schedule
        schedule = compute_schedule(trajet_complete, affectations_complete, temps_complete)
        
        # Convert to GPS
        route_gps = [{"lat": request.driver.lat, "lon": request.driver.lon, "type": "start", "label": "Driver Start"}]
        pickup_points_gps = []
        dropoff_points_gps = []
        
        for i, point_info in enumerate(points_ramassage):
            lat, lon = grid_to_gps(*point_info['point_ramassage'])
            passenger_ids = [p.id for p in point_info['passagers']]
            
            pickup_points_gps.append({
                "lat": lat, "lon": lon, "type": "pickup",
                "label": f"Pickup R{i+1}", "passengers": passenger_ids,
                "passenger_count": len(passenger_ids)
            })
            route_gps.append({
                "lat": lat, "lon": lon, "type": "pickup",
                "label": f"R{i+1}", "passengers": passenger_ids
            })
        
        for i, point_info in enumerate(points_arret):
            lat, lon = grid_to_gps(*point_info['point_arret'])
            passenger_ids = [p.id for p in point_info['passagers']]
            
            dropoff_points_gps.append({
                "lat": lat, "lon": lon, "type": "dropoff",
                "label": f"Drop-off D{i+1}", "passengers": passenger_ids,
                "passenger_count": len(passenger_ids)
            })
            route_gps.append({
                "lat": lat, "lon": lon, "type": "dropoff",
                "label": f"D{i+1}", "passengers": passenger_ids
            })
        
        # Calculate stats
        total_time_min = sum(time_val for times in temps_complete.values() for time_val in times.values())
        total_distance_km = total_time_min * 0.5
        
        # Build passenger assignments
        passenger_assignments = {}
        for passenger_id in [p.id for p in groupe_optimal]:
            pickup_point_idx = next((i for i, pi in enumerate(points_ramassage) if any(p.id == passenger_id for p in pi['passagers'])), None)
            dropoff_point_idx = next((i for i, pi in enumerate(points_arret) if any(p.id == passenger_id for p in pi['passagers'])), None)
            
            if pickup_point_idx is not None and dropoff_point_idx is not None:
                pickup_gps = pickup_points_gps[pickup_point_idx]
                dropoff_gps = dropoff_points_gps[dropoff_point_idx]
                original = next((p for p in request.passengers if p.id == passenger_id), None)
                
                if original:
                    passenger_assignments[passenger_id] = PassengerAssignment(
                        name=original.name,
                        original_pickup=GPSPoint(lat=original.pickup_lat, lon=original.pickup_lon),
                        original_destination=GPSPoint(lat=original.dest_lat, lon=original.dest_lon),
                        assigned_pickup=AssignedPoint(lat=pickup_gps['lat'], lon=pickup_gps['lon'], label=pickup_gps['label']),
                        assigned_dropoff=AssignedPoint(lat=dropoff_gps['lat'], lon=dropoff_gps['lon'], label=dropoff_gps['label']),
                        walk_to_pickup_km=haversine_distance(original.pickup_lat, original.pickup_lon, pickup_gps['lat'], pickup_gps['lon']),
                        walk_from_dropoff_km=haversine_distance(original.dest_lat, original.dest_lon, dropoff_gps['lat'], dropoff_gps['lon'])
                    )
        
        logger.info(f"Successfully generated route with {len(groupe_optimal)} passengers")
        
        return {
            "success": True,
            "algorithm": f"phase1-{request.mode}",
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
                "total_stops": len(route_gps) - 1,
                "driver_capacity": request.driver.capacity
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in optimize_carpool: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Carpool FastAPI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=5000)

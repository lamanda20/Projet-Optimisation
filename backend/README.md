# Marrakech Carpool Backend - FastAPI

**FastAPI-based optimization engine for bus-style carpooling in Marrakech**

## 🎯 Overview

This is the backend API server that powers the Marrakech Carpool Optimization System. It implements three advanced optimization algorithms (Exact, Heuristic, and Genetic) to group passengers and create efficient routes with centralized pickup/dropoff points.

### Key Features

- ✅ **FastAPI Framework**: Modern, fast, async-capable Python web framework
- ✅ **Three Optimization Modes**: Exact (optimal), Heuristic (fast), Genetic (evolutionary)
- ✅ **Pydantic v2 Validation**: Automatic request/response validation with clear error messages
- ✅ **Interactive API Docs**: Swagger UI at `/docs`, ReDoc at `/redoc`
- ✅ **CORS Support**: Configured for frontend integration
- ✅ **Capacity Enforcement**: Prevents violations with real-time validation
- ✅ **Comprehensive Logging**: Detailed operation logs for debugging

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv ../myenv

# Activate virtual environment
# Windows:
..\myenv\Scripts\activate
# Linux/Mac:
source ../myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Start FastAPI server
python main.py
```

Server runs on `http://localhost:5000`

**Verify**: Visit http://localhost:5000/docs for interactive API documentation

---

## 📂 Project Structure

```
backend/
├── main.py                          # FastAPI application (USE THIS!)
├── app.py                           # Old Flask app (deprecated, for reference)
├── requirements.txt                 # Python dependencies
├── conftest.py                      # Pytest configuration
├── pytest.ini                       # Pytest settings
│
├── algorithms/                      # Optimization algorithms
│   ├── phase2_integrator.py        # Phase 2 integration utilities
│   ├── exact/                      # Exact methods
│   │   ├── clustering_exact.py     # Distance-based clustering
│   │   ├── selection_exact.py      # Optimal passenger selection
│   │   └── ramassage_exact.py      # Centroid-based pickup points
│   ├── heuristic/                  # Heuristic methods
│   │   ├── clustering_heuristic.py # DBSCAN clustering
│   │   ├── selection_heuristic.py  # Greedy selection
│   │   └── ramassage_heuristic.py  # Density-based pickup points
│   └── genetic/                    # Genetic algorithm
│       ├── __init__.py
│       ├── genetic_carpooling.py   # Main genetic solver
│       ├── cli_genetic_solver.py   # CLI interface
│       ├── demo_genetic_algorithm.py # Demo script
│       ├── compare_methods.py      # Comparison utilities
│       └── README_GENETIC_ALGORITHM.md
│
├── models/                          # Data models
│   ├── Conducteur.py               # Driver model
│   └── Passager.py                 # Passenger model
│
├── utils/                           # Utility functions
│   ├── centroide.py                # Centroid calculations
│   ├── distance.py                 # Distance functions (grid-based)
│   └── map_utils.py                # GPS ↔ Grid conversion
│
├── data/                            # Example input files
│   ├── genetic_input_example.json
│   ├── genetic_input_large.json
│   ├── phase2_exact_example.json
│   └── phase2_heuristic_example.json
│
├── results/                         # Output files
│   ├── genetic_solution.json       # Latest genetic algorithm result
│   ├── genetic_output_example.json
│   └── genetic_output_large.json
│
├── tests/                           # Test suite
│   ├── test_capacity_fix.py        # Capacity constraint tests
│   ├── test_genetic_integration.py # Genetic algorithm tests
│   ├── test_genetic_quick.py       # Quick genetic test
│   ├── Test_clustering_exact.py
│   ├── Test_clustering_heuristic.py
│   ├── Test_selection_exact.py
│   ├── Test_selection_heuristic.py
│   └── ... (more test files)
│
└── Documentation Files:
    ├── FASTAPI_MIGRATION.md         # Flask → FastAPI migration guide
    ├── GENETIC_INTEGRATION.md       # Genetic algorithm integration docs
    ├── CAPACITY_FIX_DOCUMENTATION.md # Capacity bug fix details
    └── CAPACITY_FIX_SUMMARY.md      # Quick capacity fix reference
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check

**Endpoint**: `GET /api/health`

**Description**: Check if the API is running

**Response**:
```json
{
  "status": "ok",
  "message": "Carpool Backend API is running",
  "system": "bus-style with pickup/dropoff points"
}
```

### 2. Optimize Route (Main Endpoint)

**Endpoint**: `POST /api/optimize`

**Description**: Optimize carpool route with passenger grouping and pickup/dropoff points

**Request Body**:
```json
{
  "driver": {
    "lat": 31.6295,          // Driver latitude (31.58-31.68)
    "lon": -7.9811,          // Driver longitude (-8.05 to -7.92)
    "capacity": 4            // Vehicle capacity (1-10)
  },
  "passengers": [
    {
      "id": "p1",            // Unique passenger ID
      "name": "Alice",       // Passenger name
      "pickup_lat": 31.63,   // Pickup latitude
      "pickup_lon": -7.98,   // Pickup longitude
      "dest_lat": 31.64,     // Destination latitude
      "dest_lon": -7.97      // Destination longitude
    },
    {
      "id": "p2",
      "name": "Bob",
      "pickup_lat": 31.632,
      "pickup_lon": -7.982,
      "dest_lat": 31.642,
      "dest_lon": -7.972
    }
  ],
  "mode": "heuristic",       // "exact", "heuristic", or "genetic"
  "R_dest": 25,              // Destination clustering radius (1-100, default: 15)
  "R_depart": 25,            // Pickup clustering radius (1-100, default: 15)
  
  // Genetic algorithm parameters (only used when mode="genetic")
  "population_size": 100,    // GA population size (10-500, default: 100)
  "generations": 200,        // GA generations (10-1000, default: 200)
  "mutation_rate": 0.15      // GA mutation rate (0.01-0.5, default: 0.15)
}
```

**Response** (Success - 200 OK):
```json
{
  "success": true,
  "algorithm": "phase1-heuristic",
  "route": [
    {
      "lat": 31.6295,
      "lon": -7.9811,
      "type": "start",
      "label": "Driver Start"
    },
    {
      "lat": 31.6305,
      "lon": -7.9805,
      "type": "pickup",
      "label": "Pickup R1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    },
    {
      "lat": 31.6405,
      "lon": -7.9705,
      "type": "dropoff",
      "label": "Drop-off D1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    }
  ],
  "pickup_points": [
    {
      "lat": 31.6305,
      "lon": -7.9805,
      "type": "pickup",
      "label": "Pickup R1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    }
  ],
  "dropoff_points": [
    {
      "lat": 31.6405,
      "lon": -7.9705,
      "type": "dropoff",
      "label": "Drop-off D1",
      "passengers": ["p1", "p2"],
      "passenger_count": 2
    }
  ],
  "total_distance_km": 3.45,
  "total_time_min": 12,
  "assigned_passengers": {
    "p1": {
      "name": "Alice",
      "original_pickup": {
        "lat": 31.63,
        "lon": -7.98
      },
      "original_destination": {
        "lat": 31.64,
        "lon": -7.97
      },
      "assigned_pickup": {
        "lat": 31.6305,
        "lon": -7.9805,
        "label": "Pickup R1"
      },
      "assigned_dropoff": {
        "lat": 31.6405,
        "lon": -7.9705,
        "label": "Drop-off D1"
      },
      "walk_to_pickup_km": 0.12,
      "walk_from_dropoff_km": 0.15
    },
    "p2": {
      // Similar structure for p2
    }
  },
  "assignment_count": 2,
  "schedule": [
    {
      "point": "Depart",
      "arrival": "08:00",
      "departure": "08:00",
      "passengers": [],
      "type": "start",
      "passengers_in_car": 0
    },
    {
      "point": "Pickup R1",
      "arrival": "08:03",
      "departure": "08:05",
      "passengers": ["p1", "p2"],
      "type": "pickup",
      "passengers_in_car": 2
    },
    {
      "point": "Drop-off D1",
      "arrival": "08:12",
      "departure": "08:14",
      "passengers": ["p1", "p2"],
      "type": "dropoff",
      "passengers_in_car": 0
    }
  ],
  "statistics": {
    "total_passengers": 2,
    "selected_passengers": 2,
    "pickup_points": 1,
    "dropoff_points": 1,
    "total_stops": 2,
    "driver_capacity": 4
  }
}
```

**Response** (Error - 400/500):
```json
{
  "detail": "No passengers could be selected. Check driver capacity and passenger distribution."
}
```

---

## 🧮 Optimization Algorithms

### 1. Exact Mode (`mode="exact"`)

**When to use**: ≤10 passengers, need optimal solution

**Characteristics**:
- **Clustering**: Distance threshold-based grouping
- **Selection**: Optimal passenger selection algorithm
- **Pickup Points**: Centroid-based calculation
- **TSP**: Branch & Bound (exact solution)
- **Time Complexity**: O(n! × m) - exponential
- **Quality**: 100% optimal

**Example**:
```json
{
  "mode": "exact",
  "R_dest": 15,
  "R_depart": 15
}
```

### 2. Heuristic Mode (`mode="heuristic"`)

**When to use**: 10-50 passengers, need fast solution (RECOMMENDED)

**Characteristics**:
- **Clustering**: DBSCAN algorithm
- **Selection**: Greedy selection
- **Pickup Points**: Density-based (central passenger)
- **TSP**: Nearest Neighbor + 2-opt
- **Time Complexity**: O(n² log n)
- **Quality**: ~95% of optimal

**Example**:
```json
{
  "mode": "heuristic",
  "R_dest": 20,
  "R_depart": 20
}
```

### 3. Genetic Mode (`mode="genetic"`)

**When to use**: Complex scenarios, customizable parameters

**Characteristics**:
- **Clustering**: Evolutionary clustering
- **Selection**: Fitness-based
- **Pickup Points**: Cluster centroids
- **TSP**: Genetic algorithm with crossover/mutation
- **Time Complexity**: O(g × p × n²) where g=generations, p=population size
- **Quality**: ~90-95% of optimal

**Parameters**:
- `population_size`: Number of solutions per generation (default: 100)
  - Larger = better quality, slower
  - Recommended: 50-150
- `generations`: Number of evolution iterations (default: 200)
  - More = better convergence
  - Recommended: 100-300
- `mutation_rate`: Probability of random changes (default: 0.15)
  - Higher = more exploration
  - Recommended: 0.10-0.20

**Example**:
```json
{
  "mode": "genetic",
  "R_dest": 25,
  "R_depart": 25,
  "population_size": 100,
  "generations": 200,
  "mutation_rate": 0.15
}
```

---

## 🧩 Core Components

### Models

#### `Conducteur` (Driver)
```python
class Conducteur:
    position: Tuple[int, int]  # Grid coordinates (0-99, 0-99)
    capacite: int              # Maximum passengers
```

#### `Passager` (Passenger)
```python
class Passager:
    id: str                    # Unique identifier
    pos_depart: Tuple[int, int]   # Pickup grid coordinates
    pos_arrivee: Tuple[int, int]  # Destination grid coordinates
```

### Utilities

#### Distance Calculation
```python
from utils.distance import distance_grille

# Calculate grid-based distance
dist = distance_grille(point1, point2)  # Euclidean distance in grid units
```

#### GPS ↔ Grid Conversion
```python
# GPS to grid (31.58-31.68 lat, -8.05 to -7.92 lon → 0-99 x, 0-99 y)
x, y = gps_to_grid(lat, lon)

# Grid to GPS
lat, lon = grid_to_gps(x, y)
```

#### Centroid Calculation
```python
from utils.centroide import calculer_centroide_grille

positions = [(10, 20), (12, 22), (11, 21)]
centroid = calculer_centroide_grille(positions)  # Returns (11, 21)
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=False

# CORS Settings (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Logging Level
LOG_LEVEL=INFO
```

### Constants (main.py)

```python
# GPS Bounds for Marrakech
MARRAKECH_LAT_MIN = 31.58
MARRAKECH_LAT_MAX = 31.68
MARRAKECH_LON_MIN = -8.05
MARRAKECH_LON_MAX = -7.92
GRID_SIZE = 100  # 100x100 grid

# Default clustering radius
DEFAULT_R_DEST = 15
DEFAULT_R_DEPART = 15

# Genetic algorithm defaults
DEFAULT_POPULATION_SIZE = 100
DEFAULT_GENERATIONS = 200
DEFAULT_MUTATION_RATE = 0.15
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_capacity_fix.py -v
```

### Test Individual Components

#### Test Capacity Enforcement
```bash
python test_capacity_fix.py
```

Expected output:
```
TEST: Capacity Constraint - 6 Passengers, Capacity 2 (EXACT MODE)
✅ TEST PASSED: Only 2 passengers assigned (capacity=2)
```

#### Test Genetic Algorithm
```bash
python test_genetic_integration.py
```

#### Quick Genetic Test
```bash
python test_genetic_quick.py
```

### Manual API Testing

#### Using curl:
```bash
# Health check
curl http://localhost:5000/api/health

# Optimize with 2 passengers
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "driver": {"lat": 31.6295, "lon": -7.9811, "capacity": 4},
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
      }
    ],
    "mode": "heuristic",
    "R_dest": 25,
    "R_depart": 25
  }'
```

#### Using Swagger UI:
1. Visit http://localhost:5000/docs
2. Click on `/api/optimize` endpoint
3. Click "Try it out"
4. Modify request body
5. Click "Execute"

---

## 🐛 Debugging

### Enable Debug Mode

```python
# In main.py, change:
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Carpool FastAPI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")  # Add log_level
```

### Logging Levels

```python
# In main.py
import logging

# Set to DEBUG for detailed logs
logging.basicConfig(level=logging.DEBUG)

# Set to INFO for normal operation (default)
logging.basicConfig(level=logging.INFO)

# Set to WARNING for production
logging.basicConfig(level=logging.WARNING)
```

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'algorithms'`

**Solution**:
```bash
# Ensure you're in backend directory
cd backend

# Verify PYTHONPATH includes current directory
python -c "import sys; print(sys.path)"

# Or run with:
PYTHONPATH=. python main.py
```

#### 2. Capacity Violation

**Problem**: `Route violates capacity constraint`

**Solution**: This is prevented by validation. If you see this:
- Check backend logs for details
- Verify request payload
- Ensure passengers count ≤ capacity

#### 3. No Valid Groups

**Problem**: `No passengers could be selected`

**Solution**:
- Increase R_dest and R_depart (try 30-40)
- Check passengers are within Marrakech bounds
- Verify driver capacity is sufficient

---

## 📊 Performance Optimization

### Reduce Response Time

1. **Use Heuristic mode** for 10+ passengers
2. **Lower genetic parameters** if using genetic mode
3. **Enable caching** for repeated requests (TODO)
4. **Use async workers** with Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

### Memory Optimization

For large datasets (50+ passengers):
- Reduce clustering radius
- Use heuristic mode instead of exact
- Limit genetic population_size to 50-100

---

## 🔒 Security Considerations

### Current State (Development)
- ✅ CORS enabled for all origins (*)
- ✅ Basic input validation with Pydantic
- ⚠️ No authentication/authorization
- ⚠️ No rate limiting
- ⚠️ Debug mode enabled

### Production Recommendations

1. **Restrict CORS**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

2. **Add Authentication**:
```python
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
```

3. **Add Rate Limiting**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/optimize")
@limiter.limit("10/minute")
async def optimize_carpool(request: Request, ...):
    ...
```

4. **Disable Debug Mode**:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --no-reload
```

---

## 📦 Dependencies

See [requirements.txt](requirements.txt) for complete list.

### Core Dependencies

- **fastapi** ≥0.104.0 - Web framework
- **uvicorn[standard]** ≥0.24.0 - ASGI server
- **pydantic** ≥2.0.0 - Data validation
- **numpy** ≥1.24.0 - Numerical computations
- **scikit-learn** ≥1.3.0 - DBSCAN clustering
- **requests** ==2.31.0 - HTTP client (for testing)

### Optional Dependencies

- **flask** ==3.0.0 - Old Flask app (deprecated)
- **flask-cors** ==4.0.0 - CORS for Flask
- **customtkinter** ≥5.2.0 - GUI (optional)
- **tkintermapview** ≥1.28 - Map widget (optional)

---

## 📚 Additional Documentation

- [FASTAPI_MIGRATION.md](FASTAPI_MIGRATION.md) - Flask to FastAPI migration guide
- [GENETIC_INTEGRATION.md](GENETIC_INTEGRATION.md) - Genetic algorithm integration details
- [CAPACITY_FIX_DOCUMENTATION.md](CAPACITY_FIX_DOCUMENTATION.md) - Capacity bug fix technical details
- [CAPACITY_FIX_SUMMARY.md](CAPACITY_FIX_SUMMARY.md) - Quick capacity fix reference
- [algorithms/genetic/README_GENETIC_ALGORITHM.md](algorithms/genetic/README_GENETIC_ALGORITHM.md) - Genetic algorithm details

---

## 🤝 Contributing

See main [../README.md](../README.md) for contribution guidelines.

---

## 📄 License

MIT License - See [../LICENSE](../LICENSE) for details.

---

**Questions or issues?** Check the [troubleshooting section](#-debugging) or create an issue in the repository.

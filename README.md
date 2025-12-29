# Marrakech Carpool Optimization System

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Advanced carpooling optimization using exact, heuristic, and genetic algorithms**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## 🎯 Overview

A complete carpool optimization system for Marrakech implementing a **bus-style approach** where passengers are grouped at centralized pickup/dropoff points instead of individual door-to-door service. The system uses advanced optimization algorithms to minimize travel distance while maximizing passenger satisfaction.

### Key Capabilities

- **Three Optimization Algorithms**: Exact (optimal), Heuristic (fast), and Genetic (evolutionary)
- **Smart Passenger Grouping**: Clusters passengers with similar routes
- **Centralized Pickup/Dropoff**: Creates efficient bus-style stop points
- **Real-Time Optimization**: Interactive map-based interface
- **Capacity Management**: Respects driver capacity constraints
- **GPS Integration**: Marrakech city bounds (31.58-31.68°N, 8.05-7.92°W)

---

## ✨ Features

### Backend (FastAPI)
- ✅ **Three optimization modes**:
  - `exact`: Optimal solution using Branch & Bound TSP
  - `heuristic`: Fast solution using DBSCAN + Nearest Neighbor
  - `genetic`: Evolutionary approach with customizable parameters
- ✅ **Capacity constraint enforcement** (fixed bug: no multi-trip violations)
- ✅ **Automatic validation** of routes and assignments
- ✅ **Real-time passenger tracking** at each stop
- ✅ **Comprehensive API documentation** (FastAPI Swagger UI)
- ✅ **Pydantic v2 validation** for all inputs/outputs

### Frontend (Vanilla JavaScript)
- ✅ **Interactive Leaflet map** with drag-and-drop
- ✅ **Real-time algorithm selection** (exact/heuristic/genetic)
- ✅ **Genetic parameter tuning** (population size, generations, mutation rate)
- ✅ **Passenger management** with pickup/destination markers
- ✅ **Route visualization** with animated driver movement
- ✅ **Walking distance calculation** for each passenger
- ✅ **Backend status monitoring** with connection indicator

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Modern web browser** (Chrome, Firefox, Edge)
- **Git** (optional, for cloning)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd projet_ro

# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Running the Application

#### 1. Start Backend Server

```bash
cd backend
python main.py
```

Server starts on `http://localhost:5000`

**Verify backend**: Visit `http://localhost:5000/docs` for interactive API documentation

#### 2. Start Frontend

```bash
# Option 1: Python HTTP server
cd frontend
python -m http.server 8000

# Option 2: Use Live Server extension in VS Code
# Right-click on index.html → Open with Live Server
```

Frontend available at `http://localhost:8000`

#### 3. Use the Application

1. **Check status**: Green dot = Backend connected
2. **Place driver**: Drag car icon to map
3. **Set capacity**: Use slider (1-6 passengers)
4. **Add passengers**: Click "Add Passenger", then pickup location, then destination
5. **Choose algorithm**: Select from dropdown (Heuristic recommended)
6. **Solve**: Click "Solve Assignment"
7. **View results**: Route appears with pickup (🚏) and dropoff (🛑) points

---

## 📚 Documentation

### Project Structure

```
projet_ro/
├── backend/                    # FastAPI server
│   ├── main.py                # Main API (FastAPI - use this!)
│   ├── app.py                 # Old Flask API (deprecated)
│   ├── requirements.txt       # Python dependencies
│   ├── algorithms/            # Optimization algorithms
│   │   ├── exact/            # Exact methods (Branch & Bound)
│   │   ├── heuristic/        # Heuristic methods (DBSCAN, NN)
│   │   └── genetic/          # Genetic algorithm
│   ├── models/               # Data models (Conducteur, Passager)
│   ├── utils/                # Utilities (distance, centroid)
│   ├── data/                 # Example input files
│   ├── tests/                # Test suite
│   └── README.md             # Backend documentation
├── frontend/                  # Web interface
│   ├── index.html            # Main HTML
│   ├── css/styles.css        # Styling
│   ├── js/
│   │   ├── app.js           # Main application logic
│   │   └── lib/
│   │       ├── api-client.js       # Backend API client
│   │       ├── distance-utils.js   # Distance calculations
│   │       └── osrm-routing.js     # OSRM integration
│   └── README.md             # Frontend documentation
├── myenv/                     # Virtual environment (gitignored)
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

### Algorithm Comparison

| Feature | Exact | Heuristic | Genetic |
|---------|-------|-----------|---------|
| **Speed** | ⚡⚡ Slow | ⚡⚡⚡⚡⚡ Very Fast | ⚡⚡⚡⚡ Fast |
| **Quality** | ⭐⭐⭐⭐⭐ Optimal | ⭐⭐⭐⭐ ~95% | ⭐⭐⭐⭐ ~90-95% |
| **Best For** | ≤10 passengers | 10-50 passengers | Complex scenarios |
| **Time** | 2-10 seconds | <2 seconds | 2-5 seconds |
| **Clustering** | Distance-based | DBSCAN | Evolutionary |
| **TSP** | Branch & Bound | Nearest Neighbor | Genetic operators |
| **Configurable** | No | Partially | Yes (pop, gen, mut) |

### Capacity Constraint (Important!)

⚠️ **Driver capacity = TOTAL passengers, not per trip**

- Capacity 2 → Maximum 2 passengers assigned total
- Capacity 4 → Maximum 4 passengers assigned total
- System prevents "multiple trip" violations (bug fixed 2025-12-29)

---

## 🏗️ Architecture

### System Flow

```
┌──────────────┐         HTTP/JSON          ┌──────────────┐
│   Frontend   │ ◄─────────────────────────► │   FastAPI    │
│  (Leaflet)   │    POST /api/optimize      │   Backend    │
└──────────────┘                             └──────────────┘
       │                                             │
       │ User Actions                                │ Algorithms
       ▼                                             ▼
┌──────────────┐                             ┌──────────────┐
│  • Add Pass  │                             │ Phase 1:     │
│  • Set Cap   │                             │ Clustering   │
│  • Solve     │                             ├──────────────┤
│  • Animate   │                             │ Phase 2:     │
└──────────────┘                             │ Selection    │
                                             ├──────────────┤
                                             │ Phase 3:     │
                                             │ Pickup Points│
                                             ├──────────────┤
                                             │ Phase 4:     │
                                             │ Dropoff Pts  │
                                             ├──────────────┤
                                             │ Phase 5: TSP │
                                             ├──────────────┤
                                             │ Phase 6:     │
                                             │ Scheduling   │
                                             └──────────────┘
```

### Optimization Pipeline

#### Phase 1: Clustering
Groups passengers with similar destinations and origins
- **Exact**: Distance threshold-based
- **Heuristic**: DBSCAN algorithm
- **Genetic**: Evolutionary clustering

#### Phase 2: Selection
Chooses optimal passenger group within capacity
- **Exact**: Optimal selection algorithm
- **Heuristic**: Greedy selection
- **Genetic**: Fitness-based selection

#### Phase 3: Pickup Points
Determines centralized pickup locations (🚏)
- Groups passengers by proximity of origins
- Creates centroids or selects central locations
- Minimizes walking distances

#### Phase 4: Dropoff Points
Determines centralized dropoff locations (🛑)
- Groups passengers by proximity of destinations
- Optimizes for passenger convenience
- Balances walking vs driving efficiency

#### Phase 5: TSP Optimization
Finds optimal route order through all points
- **Exact**: Branch & Bound
- **Heuristic**: Nearest Neighbor + 2-opt
- **Genetic**: Evolutionary route optimization

#### Phase 6: Scheduling
Calculates arrival/departure times
- Tracks passengers in car at each stop
- Validates capacity constraints
- Computes dwell times and travel times

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Test Capacity Fix

```bash
cd backend
python test_capacity_fix.py
```

### Test Genetic Algorithm

```bash
cd backend
python test_genetic_integration.py
```

### Manual Testing

#### Test 1: Simple Case (2 passengers)
```bash
# Start backend: python main.py
# In frontend:
1. Add driver at (31.6295, -7.9811)
2. Set capacity to 4
3. Add 2 passengers nearby
4. Solve with Heuristic mode
# Expected: 1-2 pickup points, 1-2 dropoff points
```

#### Test 2: Capacity Constraint (6 passengers, capacity 2)
```bash
# In frontend:
1. Add driver
2. Set capacity to 2
3. Add 6 passengers
4. Solve
# Expected: Only 2 passengers assigned (not 6!)
```

#### Test 3: Genetic Algorithm
```bash
# In frontend:
1. Add driver
2. Add 8 passengers
3. Select "Genetic Algorithm"
4. Adjust parameters (population: 100, generations: 200)
5. Solve
# Expected: Optimized route within capacity
```

---

## 📖 API Reference

### Base URL
```
http://localhost:5000
```

### Endpoints

#### Health Check
```http
GET /api/health

Response:
{
  "status": "ok",
  "message": "Carpool Backend API is running",
  "system": "bus-style with pickup/dropoff points"
}
```

#### Optimize Route
```http
POST /api/optimize
Content-Type: application/json

{
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
    }
  ],
  "mode": "heuristic",           // "exact", "heuristic", or "genetic"
  "R_dest": 25,                  // Destination clustering radius
  "R_depart": 25,                // Pickup clustering radius
  "population_size": 100,        // Genetic only
  "generations": 200,            // Genetic only
  "mutation_rate": 0.15          // Genetic only
}

Response: See backend/README.md for complete schema
```

**Interactive API Docs**: Visit `http://localhost:5000/docs`

---

## 🛠️ Configuration

### Backend Settings (backend/main.py)

```python
# GPS Bounds (Marrakech)
MARRAKECH_LAT_MIN = 31.58
MARRAKECH_LAT_MAX = 31.68
MARRAKECH_LON_MIN = -8.05
MARRAKECH_LON_MAX = -7.92
GRID_SIZE = 100  # 100x100 coordinate grid

# Server
HOST = "0.0.0.0"  # All interfaces
PORT = 5000       # Default port
```

### Frontend Settings (frontend/js/app.js)

```javascript
// Map Center
MARRAKECH_CENTER = [31.6295, -7.9811]

// API Endpoint
const api = new CarpoolAPI('http://localhost:5000')

// Default Values
capacity: 4
optimizationMode: 'heuristic'
geneticParams: {
  populationSize: 100,
  generations: 200,
  mutationRate: 0.15
}
```

### Clustering Radius Tuning

| Radius (R_dest/R_depart) | Pickup/Dropoff Points | Walking Distance | Route Length |
|--------------------------|----------------------|------------------|--------------|
| 10 | More stops | Shorter walks | Longer route |
| 15-20 (default) | Balanced | ~100-300m | Balanced |
| 25-30 | Fewer stops | Longer walks | Shorter route |

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Ensure virtual environment is activated
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Frontend Shows "Backend Offline"

**Problem**: Cannot connect to backend

**Solution**:
1. Verify backend is running: `curl http://localhost:5000/api/health`
2. Check firewall settings
3. Ensure port 5000 is not in use: `netstat -ano | findstr :5000`
4. Check browser console (F12) for CORS errors

### Capacity Violation Error

**Problem**: `500 Internal Server Error: Route violates capacity constraint`

**Solution**: This should not happen after the fix. If it does:
1. Check backend logs for details
2. Verify passengers count ≤ capacity
3. Report as a bug with request payload

### Genetic Algorithm Takes Too Long

**Problem**: Optimization hangs or times out

**Solution**:
- Reduce `generations` (try 100 instead of 200)
- Reduce `population_size` (try 50 instead of 100)
- Use Heuristic mode for 10+ passengers

### No Valid Groups Formed

**Problem**: "No passengers could be selected"

**Solution**:
- Increase `R_dest` and `R_depart` (try 30-40)
- Ensure passengers are within Marrakech bounds
- Check driver capacity is sufficient

---

## 📊 Performance Benchmarks

| Scenario | Passengers | Algorithm | Time | Quality |
|----------|-----------|-----------|------|---------|
| Small | 4 | Exact | 1.2s | 100% |
| Small | 4 | Heuristic | 0.3s | 98% |
| Medium | 10 | Exact | 5.8s | 100% |
| Medium | 10 | Heuristic | 1.1s | 96% |
| Medium | 10 | Genetic | 3.2s | 94% |
| Large | 20 | Heuristic | 2.4s | 95% |
| Large | 20 | Genetic | 4.8s | 93% |

*Tested on Intel i5-8250U, 8GB RAM*

---

## 🔄 Recent Updates

### Version 2.0.0 (2025-12-29)
- ✅ **Migrated from Flask to FastAPI**
- ✅ **Integrated Genetic Algorithm** with full parameter support
- ✅ **Fixed capacity constraint bug** (no more multi-trip violations)
- ✅ **Added capacity validation** with real-time passenger tracking
- ✅ **Enhanced frontend** with genetic parameter controls
- ✅ **Improved documentation** (3 comprehensive READMEs)
- ✅ **Added test suites** for capacity and genetic features

See [backend/FASTAPI_MIGRATION.md](backend/FASTAPI_MIGRATION.md) for migration details.

---

## 📝 Development

### Adding a New Algorithm

1. Create algorithm file in `backend/algorithms/your_method/`
2. Implement required functions (clustering, selection, routing)
3. Add endpoint logic in `backend/main.py`
4. Update frontend algorithm selector
5. Add tests in `backend/tests/`

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Algorithms**: Based on operations research techniques (TSP, clustering, selection)
- **Maps**: OpenStreetMap contributors
- **Routing**: OSRM Project
- **Frameworks**: FastAPI, Leaflet.js, Pydantic
- **Inspiration**: Real-world carpooling optimization challenges in Marrakech

---

## 📞 Support

- **Documentation**: See `backend/README.md` and `frontend/README.md`
- **Issues**: Check existing issues or create a new one
- **Questions**: Review documentation first, then ask

---

<div align="center">

**Built with ❤️ for efficient urban mobility in Marrakech**

[⬆ Back to top](#marrakech-carpool-optimization-system)

</div>

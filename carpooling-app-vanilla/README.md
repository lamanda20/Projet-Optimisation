# Marrakech Carpool - Advanced Route Optimization

A carpooling route optimization application with **backend API integration** using advanced algorithms from `Projet-Optimisation-main`. Built with vanilla HTML, CSS, JavaScript, and Flask backend.

## Features

### Frontend
- **Interactive Map**: Drag and drop drivers, click to add passenger pickup/destination points
- **Multiple Algorithms**: 
  - Simple Greedy (basic, no backend required)
  - Phase 1 Exact (Hungarian + Clustering + Branch & Bound)
  - Phase 1 Heuristic (K-means + Nearest Neighbor + 2-opt)
- **Real Road Routing**: Integrates with OSRM for real road-based navigation
- **Route Animation**: Visualize the complete route with smooth animation
- **Capacity Management**: Set driver capacity (1-6 passengers)
- **Live Backend Status**: Shows connection status to Python backend API

### Backend
- **Flask REST API**: Exposes optimization algorithms via HTTP endpoints
- **Advanced Algorithms**: 
  - Selection (exact & heuristic)
  - Clustering (double-phase: destinations + departures)
  - Pickup point optimization
- **GPS ↔ Grid Conversion**: Handles coordinate system transformations
- **OSRM Integration**: Real road routing for accurate distances

## Architecture

```
┌─────────────────┐         HTTP/JSON          ┌──────────────────┐
│  Frontend App   │ ◄─────────────────────────► │  Flask Backend   │
│  (Vanilla JS)   │                              │    (Python)      │
└─────────────────┘                              └──────────────────┘
        │                                                 │
        │ Leaflet.js                                     │
        ▼                                                 ▼
┌─────────────────┐                              ┌──────────────────┐
│  OpenStreetMap  │                              │ Projet-Optim     │
│     + OSRM      │                              │   Algorithms     │
└─────────────────┘                              └──────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser
- Internet connection (for maps and routing)

### Installation

1. **Install backend dependencies**:
```bash
cd carpooling-backend
pip install -r requirements.txt
```

2. **Start the backend**:
```bash
python app.py
```
Backend runs on `http://localhost:5000`

3. **Start the frontend** (in another terminal):
```bash
cd carpooling-app-vanilla
python -m http.server 8000
```
Frontend available at `http://localhost:8000`

### OR Use the Startup Script (Windows)
```bash
# From the projet_ro directory
start-app.bat
```

## Usage Guide

1. **Check Backend Status**: Look for green dot next to "Backend Connected"
2. **Select Algorithm**: 
   - **Simple Greedy**: Works offline, basic optimization
   - **Phase 1 - Exact**: Requires backend, optimal solution (slower for large datasets)
   - **Phase 1 - Heuristic**: Requires backend, good solution (faster)
3. **Place Driver**: Drag car icon onto map
4. **Set Capacity**: Use slider (1-6 passengers)
5. **Add Passengers**: Click "Add Passenger", then click pickup location, then destination
6. **Solve**: Click "Solve Assignment" - backend will compute optimal route
7. **Animate**: Watch the route animation
8. **Reset**: Start over

## API Endpoints

### Health Check
```http
GET /api/health
Response: {"status": "ok", "message": "Carpool API is running"}
```

### Simple Optimization
```http
POST /api/optimize/simple
Content-Type: application/json

{
  "driver": {"lat": 31.6295, "lon": -7.9811, "capacity": 4},
  "passengers": [
    {
      "id": "p1", "name": "Passenger 1",
      "pickup_lat": 31.63, "pickup_lon": -7.98,
      "dest_lat": 31.64, "dest_lon": -7.97
    }
  ]
}
```

### Phase 1 Optimization
```http
POST /api/optimize/phase1
Content-Type: application/json

{
  "driver": {...},
  "passengers": [...],
  "mode": "exact"  // or "heuristic"
}

Response:
{
  "success": true,
  "algorithm": "phase1-exact",
  "route": [...],
  "road_coordinates": [[31.6295, -7.9811], ...],
  "total_distance": 12.5,
  "total_duration": 25.3,
  "assigned_passengers": [...],
  "assignment_count": 3,
  "pickup_points": 2,
  "groups_found": 4
}
```

## Algorithms Explained

### Simple Greedy (Frontend Only)
1. Calculate cost for each passenger (driver→pickup + pickup→destination)
2. Sort by cost
3. Assign up to capacity
4. Nearest neighbor routing

### Phase 1 - Exact (Backend)
1. **Clustering**: Group passengers by nearby destinations, then nearby departures
2. **Selection**: Choose optimal passenger group using Hungarian-inspired logic
3. **Ramassage**: Determine efficient pickup points
4. **TSP**: Solve traveling salesman for pickup order (Branch & Bound)

### Phase 1 - Heuristic (Backend)
1. **Clustering**: K-means clustering for passenger grouping
2. **Selection**: Greedy selection of best group
3. **Ramassage**: Heuristic pickup point determination  
4. **Routing**: Nearest neighbor + 2-opt improvement

## Performance

| Algorithm | Passengers | Time | Quality |
|-----------|-----------|------|---------|
| Simple | 1-20 | <1s | Good |
| Phase1-Exact | 1-10 | 1-5s | Optimal |
| Phase1-Heuristic | 1-50+ | <2s | Very Good |

## Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Install dependencies
pip install flask flask-cors requests
```

### Frontend shows "Backend Offline"
- Ensure backend is running on port 5000
- Check firewall settings
- Try: `curl http://localhost:5000/api/health`

### CORS errors
- Flask-CORS should be installed
- Check browser console for specific error

### No route displayed
- Check browser console for errors
- Verify OSRM API is accessible
- Try with fewer passengers first

## File Structure

```
carpooling-app-vanilla/
├── index.html              # Main HTML
├── README.md              # This file
├── css/
│   └── styles.css         # All styling
└── js/
    ├── app.js             # Main app logic + backend integration
    └── lib/
        ├── api-client.js         # Backend API client
        ├── distance-utils.js     # Distance calculations
        ├── osrm-routing.js       # OSRM integration
        └── routing-algorithm.js  # Fallback simple algorithm

carpooling-backend/
├── app.py                 # Flask API server
├── requirements.txt       # Python dependencies
└── README.md             # Backend docs
```

## Technologies

### Frontend
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **Leaflet.js**: Interactive maps
- **OpenStreetMap**: Map tiles
- **OSRM API**: Road routing

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin requests
- **Requests**: HTTP client
- **Projet-Optimisation algorithms**: Core optimization logic

## Development

### Adding New Algorithms
1. Implement in `Projet-Optimisation-main/algorithms/`
2. Add endpoint in `carpooling-backend/app.py`
3. Add option in frontend `algorithmSelect`
4. Handle response format in `solveWithBackend()`

### Debugging
```javascript
// Enable verbose logging in app.js
console.log('State:', state);
console.log('API Response:', result);
```

```python
# Enable Flask debug mode in app.py
app.run(debug=True)
```

## License

Demonstration project. Free to use and modify.

## Credits

- Algorithms: Projet-Optimisation-main
- Maps: OpenStreetMap contributors  
- Routing: OSRM Project
- Icons: SVG inline


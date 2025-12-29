# Marrakech Carpool Frontend

**Interactive web interface for carpool route optimization in Marrakech**

## 🎯 Overview

A modern, responsive web application built with vanilla JavaScript that provides an intuitive interface for optimizing carpool routes. Features an interactive Leaflet map, real-time backend integration, and support for three optimization algorithms (Exact, Heuristic, and Genetic).

### Key Features

- ✅ **Interactive Map**: Leaflet.js-based map of Marrakech with drag-and-drop functionality
- ✅ **Three Algorithms**: Switch between Exact, Heuristic, and Genetic optimization modes
- ✅ **Genetic Parameters**: Fine-tune population size, generations, and mutation rate
- ✅ **Real-Time Updates**: Live backend status monitoring with connection indicator
- ✅ **Route Visualization**: Animated driver movement along optimized route
- ✅ **Passenger Management**: Add/remove passengers with visual pickup/destination markers
- ✅ **Walking Distances**: Calculate and display walking distances for each passenger
- ✅ **Responsive Design**: Mobile-friendly interface with clean, modern UI

---

## 🚀 Quick Start

### Prerequisites

- **Web Browser**: Chrome, Firefox, Edge, or Safari (latest versions)
- **Backend Server**: FastAPI backend must be running (see [../backend/README.md](../backend/README.md))

### Running the Application

#### Option 1: Python HTTP Server (Recommended)

```bash
cd frontend
python -m http.server 8000
```

Visit `http://localhost:8000`

#### Option 2: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

#### Option 3: Any HTTP Server

```bash
# Using Node.js http-server
npx http-server -p 8000

# Using PHP
php -S localhost:8000
```

### Verify Setup

1. Open `http://localhost:8000`
2. Check top-left corner for **green dot** = "Backend Connected"
3. If red dot = "Backend Offline", ensure backend is running on port 5000

---

## 📂 Project Structure

```
frontend/
├── index.html              # Main HTML file
├── README.md              # This file
│
├── css/
│   └── styles.css         # All styling (responsive design, animations)
│
└── js/
    ├── app.js             # Main application logic
    └── lib/
        ├── api-client.js        # Backend API communication
        ├── distance-utils.js    # Distance calculations
        ├── osrm-routing.js      # OSRM routing integration
        └── routing-algorithm.js # Fallback algorithms
```

---

## 🎨 User Interface

### Main Components

#### 1. Sidebar (Left Panel)

**Header**:
- Title: "Marrakech Carpool"
- Mode indicator: Shows current action (drag driver, add passenger, etc.)

**Driver Section**:
- Draggable car icon (🚗)
- Capacity slider (1-6 passengers)
- Status badge when driver is placed

**Backend Status**:
- Green dot (●) = Connected
- Red dot (●) = Offline
- Checks connection every 30 seconds

**Algorithm Selection**:
```
┌─────────────────────────┐
│ Algorithm: Heuristic ▼  │
├─────────────────────────┤
│ ○ Exact (Optimal)       │
│ ● Heuristic (Fast)      │  ← Selected
│ ○ Genetic Algorithm     │
└─────────────────────────┘
```

**Genetic Parameters** (shown when Genetic selected):
```
Population Size: [100]  ────────
Generations:     [200]  ────────
Mutation Rate:   [0.15] ────────
```

**Clustering Settings**:
```
Clustering Radius: [25]  ───────
```

**Passengers Section**:
- List of added passengers
- Each shows: Name, Pickup (🚏), Dropoff (🛑), Walking distances
- Delete button (×) for each passenger

**Action Buttons**:
- ➕ Add Passenger
- 🎯 Solve Assignment
- 🎬 Animate Route
- 🔄 Reset All

**Statistics Panel** (after solving):
```
┌──────────────────────────────┐
│ Algorithm: Heuristic         │
│ Distance: 7.4 km             │
│ Time: 17 min                 │
│ Passengers: 4/6              │
│ Pickup Points: 2             │
│ Dropoff Points: 2            │
└──────────────────────────────┘
```

#### 2. Map (Right Panel)

**Map Elements**:
- Base layer: OpenStreetMap tiles
- Center: Marrakech (31.6295°N, 7.9811°W)
- Zoom level: 13 (city view)
- Bounds: Marrakech city limits

**Markers**:
- 🚗 **Driver** (Teal): Draggable, shows current position
- 👤 **Pickup Origins** (Green): Passenger starting points (faded after solve)
- 🏁 **Destinations** (Red): Passenger end points (faded after solve)
- 🚏 **Pickup Points** (Blue, Large): Centralized boarding points
- 🛑 **Dropoff Points** (Orange, Large): Centralized alighting points
- 🚗 **Animated Driver** (Teal): Shows current position during animation

**Route Line**:
- Blue polyline connecting all points
- Displays optimized path

---

## 🎮 Usage Guide

### Step-by-Step Tutorial

#### 1. Place Driver

```
1. Drag the car icon (🚗) from sidebar onto the map
2. Drop it at driver's starting location
3. Badge appears: "Driver is on the map"
```

**Alternative**: Click driver icon, then click map location

#### 2. Set Capacity

```
1. Use the capacity slider
2. Range: 1-6 passengers
3. Default: 4 passengers
```

**Note**: Capacity = maximum TOTAL passengers, not per trip!

#### 3. Choose Algorithm

**Exact Mode** (≤10 passengers):
- Optimal solution
- Slower (2-10 seconds)
- 100% quality

**Heuristic Mode** (10-50 passengers) - **RECOMMENDED**:
- Very fast (<2 seconds)
- ~95% quality
- Best for most use cases

**Genetic Mode** (complex scenarios):
- Configurable parameters
- Medium speed (2-5 seconds)
- ~90-95% quality

#### 4. Add Passengers

```
1. Click "➕ Add Passenger"
2. Mode changes to: "Click on map for pickup location"
3. Click map for pickup point (🟢 green marker appears)
4. Mode changes to: "Click on map for destination"
5. Click map for destination (🔴 red marker appears)
6. Passenger added to list
7. Repeat for more passengers
```

**Passenger Entry Shows**:
```
Passenger 1
├─ 🚏 Pickup: (31.630, -7.980)
└─ 🏁 Destination: (31.640, -7.970)
[×] Delete button
```

#### 5. Solve Optimization

```
1. Click "🎯 Solve Assignment"
2. Request sent to backend
3. Optimization runs (1-10 seconds depending on algorithm)
4. Results displayed:
   - Route line appears on map
   - Pickup points (🚏) shown in blue
   - Dropoff points (🛑) shown in orange
   - Original markers fade
   - Statistics panel updates
```

**After Solving, Passengers Show**:
```
Passenger 1
├─ 🚏 Pickup R1 - 120m walk
└─ 🛑 Drop-off D1 - 150m walk
[×] Delete button
```

#### 6. Animate Route (Optional)

```
1. Click "🎬 Animate Route"
2. Watch driver (🚗) move along route
3. Animation automatically stops at end
4. Click again to restart from beginning
```

#### 7. Reset

```
1. Click "🔄 Reset All"
2. Clears all data:
   - Passengers removed
   - Route cleared
   - Driver remains
   - Map resets
```

---

## ⚙️ Configuration

### Map Settings (js/app.js)

```javascript
const MARRAKECH_CENTER = [31.6295, -7.9811];
const MARRAKECH_BOUNDS = {
    north: 31.68,
    south: 31.58,
    east: -7.92,
    west: -8.05
};
```

### API Settings (js/lib/api-client.js)

```javascript
class CarpoolAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }
}
```

**To change backend URL**:
```javascript
// In app.js
const api = new CarpoolAPI('http://your-backend-url:5000');
```

### Default Values (js/app.js)

```javascript
const state = {
    capacity: 4,
    optimizationMode: 'heuristic',
    geneticParams: {
        populationSize: 100,
        generations: 200,
        mutationRate: 0.15
    }
};
```

---

## 🎨 Styling & Customization

### Color Scheme

```css
:root {
    --primary: #2196F3;      /* Blue - Primary actions */
    --success: #4CAF50;      /* Green - Success states */
    --warning: #FF9800;      /* Orange - Warnings */
    --danger: #F44336;       /* Red - Errors/Delete */
    --background: #f5f5f5;   /* Light gray background */
    --card: #ffffff;         /* White cards */
    --text: #333333;         /* Dark gray text */
    --border: #e0e0e0;       /* Light borders */
}
```

### Responsive Breakpoints

```css
/* Mobile: < 768px */
@media (max-width: 768px) {
    .app-container {
        flex-direction: column;
    }
    .sidebar {
        width: 100%;
        height: auto;
    }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
    .sidebar {
        width: 350px;
    }
}

/* Desktop: > 1024px */
@media (min-width: 1024px) {
    .sidebar {
        width: 400px;
    }
}
```

### Customizing Markers

**Change marker colors** (js/app.js):
```javascript
// Driver marker
L.marker([lat, lng], {
    icon: L.divIcon({
        className: 'driver-marker',
        html: '🚗',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    })
});

// Pickup marker (green)
L.circleMarker([lat, lng], {
    radius: 8,
    fillColor: '#4CAF50',
    color: '#fff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.8
});
```

---

## 🔌 Backend Integration

### API Client (js/lib/api-client.js)

#### Health Check

```javascript
const api = new CarpoolAPI();

async function checkBackend() {
    const result = await api.healthCheck();
    if (result.status === 'ok') {
        console.log('Backend is running');
    }
}
```

#### Optimize Route

```javascript
async function optimizeRoute() {
    const result = await api.optimize(
        driver,          // {lat, lon, capacity}
        passengers,      // [{id, name, pickup_lat, pickup_lon, dest_lat, dest_lon}]
        'heuristic',     // mode: 'exact', 'heuristic', or 'genetic'
        25,              // R_dest: destination radius
        25,              // R_depart: pickup radius
        {                // geneticParams (optional, for genetic mode)
            populationSize: 100,
            generations: 200,
            mutationRate: 0.15
        }
    );
    
    if (result && result.success) {
        // Process result
        displayRoute(result.route);
        displayPickupPoints(result.pickup_points);
        displayDropoffPoints(result.dropoff_points);
        updateStatistics(result.statistics);
    }
}
```

### Response Handling

```javascript
// Success response
{
    success: true,
    algorithm: "phase1-heuristic",
    route: [...],
    pickup_points: [...],
    dropoff_points: [...],
    assigned_passengers: {...},
    total_distance_km: 7.4,
    total_time_min: 17,
    statistics: {...}
}

// Error response
{
    detail: "Error message"
}
```

---

## 🐛 Troubleshooting

### Backend Connection Issues

**Problem**: Red dot showing "Backend Offline"

**Solutions**:
1. Verify backend is running: Visit `http://localhost:5000/api/health`
2. Check browser console (F12) for CORS errors
3. Ensure backend allows CORS from frontend origin
4. Try refreshing the page

### No Map Displayed

**Problem**: Map area is blank

**Solutions**:
1. Check browser console for Leaflet errors
2. Verify internet connection (map tiles load from CDN)
3. Clear browser cache
4. Check if Leaflet CSS is loaded

### Passengers Not Adding

**Problem**: Clicking map doesn't add passenger

**Solutions**:
1. Ensure you clicked "Add Passenger" button first
2. Check mode indicator shows correct state
3. Click within Marrakech bounds (31.58-31.68°N, -8.05 to -7.92°W)
4. Check browser console for errors

### Route Not Displaying

**Problem**: After solving, no route appears

**Solutions**:
1. Check backend returned success response
2. Open browser console (F12) and look for errors
3. Verify passengers were added correctly
4. Ensure driver is placed on map
5. Check statistics panel updated

### Animation Not Working

**Problem**: Animate button doesn't work

**Solutions**:
1. Ensure route has been solved first
2. Check if route data exists in state
3. Look for JavaScript errors in console
4. Try resetting and solving again

### Walking Distances Show as 0

**Problem**: Passenger list shows "0m walk"

**Solutions**:
1. Ensure optimization completed successfully
2. Check backend response includes `assigned_passengers` data
3. Verify pickup/dropoff points were created
4. Look for calculation errors in console

---

## 📊 Performance Optimization

### Reduce Load Time

1. **Minimize HTTP requests**:
   - Use CDN for Leaflet (already done)
   - Bundle JavaScript files (optional)

2. **Optimize images**:
   - Use SVG for icons (already done)
   - Lazy load map tiles

3. **Reduce initial load**:
   ```javascript
   // Defer non-critical scripts
   <script defer src="js/lib/distance-utils.js"></script>
   ```

### Improve Responsiveness

1. **Debounce user inputs**:
   ```javascript
   // Debounce capacity slider
   let capacityTimeout;
   function handleCapacityChange(e) {
       clearTimeout(capacityTimeout);
       capacityTimeout = setTimeout(() => {
           state.capacity = parseInt(e.target.value);
           updateUI();
       }, 300);
   }
   ```

2. **Use requestAnimationFrame for animations**:
   ```javascript
   // Already implemented in animateAlongRoute()
   state.animationFrame = requestAnimationFrame(animateAlongRoute);
   ```

---

## 🧪 Testing

### Manual Testing Checklist

#### Basic Functionality
- [ ] Driver can be dragged onto map
- [ ] Capacity slider works (1-6)
- [ ] Backend status shows green dot
- [ ] Algorithm selector changes mode
- [ ] Add Passenger button triggers pickup mode
- [ ] Clicking map adds pickup marker
- [ ] Clicking map again adds destination marker
- [ ] Passenger appears in list
- [ ] Delete button removes passenger

#### Optimization
- [ ] Solve button sends request to backend
- [ ] Loading indicator appears during request
- [ ] Route line appears on map
- [ ] Pickup points (blue) appear
- [ ] Dropoff points (orange) appear
- [ ] Statistics panel updates
- [ ] Walking distances calculated
- [ ] Original markers fade

#### Animation
- [ ] Animate button starts animation
- [ ] Driver marker moves along route
- [ ] Animation stops at end
- [ ] Button text toggles

#### Reset
- [ ] Reset button clears all data
- [ ] Passengers removed from list
- [ ] Route cleared from map
- [ ] Markers removed
- [ ] Statistics reset

### Browser Testing

Test in multiple browsers:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (responsive design)

---

## 🔧 Development

### Adding New Features

#### Example: Add Export Button

```javascript
// 1. Add button to HTML (index.html)
<button id="exportButton" class="btn btn-secondary">
    📥 Export Results
</button>

// 2. Add event listener (js/app.js)
function initEventListeners() {
    // ... existing listeners
    document.getElementById('exportButton')?.addEventListener('click', handleExport);
}

// 3. Implement handler
function handleExport() {
    const exportData = {
        driver: state.driver,
        passengers: state.passengers,
        route: state.route,
        statistics: state.statistics
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `carpool_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}
```

### Code Style Guidelines

```javascript
// Use const/let, not var
const CONSTANT_VALUE = 100;
let variableValue = 0;

// Use arrow functions
const calculateDistance = (p1, p2) => {
    return Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
};

// Use template literals
console.log(`Passenger ${passenger.id} added`);

// Use async/await
async function fetchData() {
    try {
        const result = await api.optimize(...);
        // Handle result
    } catch (error) {
        console.error('Error:', error);
    }
}

// Add comments for complex logic
// Calculate centroid of passenger pickup points
const centroid = calculateCentroid(pickupPoints);
```

---

## 📚 Additional Resources

### Leaflet.js Documentation
- Official Docs: https://leafletjs.com/reference.html
- Tutorials: https://leafletjs.com/examples.html
- Markers: https://leafletjs.com/reference.html#marker
- Polylines: https://leafletjs.com/reference.html#polyline

### OpenStreetMap
- Tiles: https://wiki.openstreetmap.org/wiki/Tiles
- Usage Policy: https://operations.osmfoundation.org/policies/tiles/

### JavaScript Best Practices
- MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web/JavaScript
- ES6 Features: https://es6-features.org/

---

## 📄 License

MIT License - See [../LICENSE](../LICENSE) for details.

---

## 🤝 Contributing

See main [../README.md](../README.md) for contribution guidelines.

---

**Questions or issues?** Check the [troubleshooting section](#-troubleshooting) or create an issue in the repository.


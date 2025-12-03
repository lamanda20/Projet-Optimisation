// Bus-Style Carpool Application
// Uses pickup/dropoff points instead of individual passenger destinations

// Application State
const state = {
    driver: null,
    passengers: [],
    capacity: 4,
    mode: null, // 'pickup' or 'destination'
    pendingPickup: null,
    route: [],
    pickupPoints: [],
    dropoffPoints: [],
    assignedPassengers: {},
    totalDistance: 0,
    totalTime: 0,
    isAnimating: false,
    animatedPosition: null,
    currentStopIndex: 0,
    isSolved: false,
    animationFrame: null,
    optimizationMode: 'heuristic', // 'exact' or 'heuristic'
    apiConnected: false,
    schedule: [],
    statistics: null
};

// Initialize API client
const api = new CarpoolAPI();

// Map configuration
const MARRAKECH_CENTER = [31.6295, -7.9811];
const MARRAKECH_BOUNDS = {
    north: 31.68,
    south: 31.58,
    east: -7.92,
    west: -8.05
};

// Leaflet map instance
let map = null;
let markers = [];
let polyline = null;
let animatedMarker = null;
let pickupPointMarkers = [];
let dropoffPointMarkers = [];

// Initialize map
function initMap() {
    map = L.map('map').setView(MARRAKECH_CENTER, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Map click handler
    map.on('click', function(e) {
        const { lat, lng } = e.latlng;
        if (lat >= MARRAKECH_BOUNDS.south && lat <= MARRAKECH_BOUNDS.north &&
            lng >= MARRAKECH_BOUNDS.west && lng <= MARRAKECH_BOUNDS.east) {
            handleMapClick(lat, lng);
        }
    });

    // Drag and drop support
    const mapContainer = document.getElementById('map');
    mapContainer.addEventListener('dragover', handleDragOver);
    mapContainer.addEventListener('drop', handleDrop);
}

// Handle map click
function handleMapClick(lat, lng) {
    if (state.mode === 'pickup') {
        state.pendingPickup = [lat, lng];
        state.mode = 'destination';
        updateUI();
        updateMarkers();
    } else if (state.mode === 'destination' && state.pendingPickup) {
        const newPassenger = {
            id: `p${state.passengers.length + 1}`,
            pickup: state.pendingPickup,
            destination: [lat, lng],
            name: `Passenger ${state.passengers.length + 1}`
        };
        state.passengers.push(newPassenger);
        state.pendingPickup = null;
        state.mode = null;
        state.isSolved = false;
        clearSolution();
        updateUI();
        updateMarkers();
    }
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
}

function handleDrop(e) {
    e.preventDefault();
    const data = e.dataTransfer.getData('text/plain');

    if (data === 'driver' && map) {
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const point = map.containerPointToLatLng([x, y]);
        const lat = point.lat;
        const lng = point.lng;

        if (lat >= MARRAKECH_BOUNDS.south && lat <= MARRAKECH_BOUNDS.north &&
            lng >= MARRAKECH_BOUNDS.west && lng <= MARRAKECH_BOUNDS.east) {
            state.driver = { position: [lat, lng], capacity: state.capacity };
            state.isSolved = false;
            clearSolution();
            updateUI();
            updateMarkers();
        }
    }
}

// Create custom marker icon
function createIcon(color, emoji, size = 36) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background: ${color};
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: ${Math.floor(size/2.5)}px;
        ">${emoji}</div>`,
        iconSize: [size, size],
        iconAnchor: [size/2, size/2]
    });
}

// Update markers on map
function updateMarkers() {
    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    // Add driver marker
    if (state.driver) {
        const marker = L.marker(state.driver.position, {
            icon: createIcon('#0d9488', '🚗', 40),
            draggable: true
        }).addTo(map).bindPopup(`<strong>Driver</strong><br/>Capacity: ${state.driver.capacity} passengers`);

        marker.on('dragend', function(e) {
            const { lat, lng } = e.target.getLatLng();
            if (lat >= MARRAKECH_BOUNDS.south && lat <= MARRAKECH_BOUNDS.north &&
                lng >= MARRAKECH_BOUNDS.west && lng <= MARRAKECH_BOUNDS.east) {
                state.driver.position = [lat, lng];
                state.isSolved = false;
                clearSolution();
                updateUI();
            } else {
                marker.setLatLng(state.driver.position);
            }
        });

        markers.push(marker);
    }

    // Add pending pickup marker
    if (state.pendingPickup) {
        const marker = L.marker(state.pendingPickup, {
            icon: createIcon('#22c55e', '📍', 30)
        }).addTo(map).bindPopup('Pending pickup - click destination');
        markers.push(marker);
    }

    // Add passenger origin/destination markers (faded when solved)
    state.passengers.forEach(p => {
        const opacity = state.isSolved ? 0.4 : 1.0;
        
        const pickupMarker = L.marker(p.pickup, {
            icon: createIcon('#22c55e', '👤', 28),
            opacity: opacity
        }).addTo(map).bindPopup(`<strong>${p.name}</strong><br/>Original Pickup`);
        markers.push(pickupMarker);

        const destMarker = L.marker(p.destination, {
            icon: createIcon('#ef4444', '🏁', 28),
            opacity: opacity
        }).addTo(map).bindPopup(`<strong>${p.name}</strong><br/>Original Destination`);
        markers.push(destMarker);
    });

    // Add pickup point markers (bus stops)
    if (state.isSolved && state.pickupPoints.length > 0) {
        pickupPointMarkers.forEach(m => map.removeLayer(m));
        pickupPointMarkers = [];

        state.pickupPoints.forEach((point, idx) => {
            const passengerNames = point.passengers.map(pid => {
                const pax = state.passengers.find(p => p.id === pid);
                return pax ? pax.name : pid;
            }).join(', ');

            const marker = L.marker([point.lat, point.lon], {
                icon: createIcon('#3b82f6', '🚏', 44)
            }).addTo(map).bindPopup(`
                <strong>${point.label}</strong><br/>
                <strong>Pickup Point</strong><br/>
                Passengers: ${passengerNames}<br/>
                Count: ${point.passenger_count}
            `);
            pickupPointMarkers.push(marker);
        });
    }

    // Add dropoff point markers (bus stops)
    if (state.isSolved && state.dropoffPoints.length > 0) {
        dropoffPointMarkers.forEach(m => map.removeLayer(m));
        dropoffPointMarkers = [];

        state.dropoffPoints.forEach((point, idx) => {
            const passengerNames = point.passengers.map(pid => {
                const pax = state.passengers.find(p => p.id === pid);
                return pax ? pax.name : pid;
            }).join(', ');

            const marker = L.marker([point.lat, point.lon], {
                icon: createIcon('#f59e0b', '🛑', 44)
            }).addTo(map).bindPopup(`
                <strong>${point.label}</strong><br/>
                <strong>Drop-off Point</strong><br/>
                Passengers: ${passengerNames}<br/>
                Count: ${point.passenger_count}
            `);
            dropoffPointMarkers.push(marker);
        });
    }
}

// Update route polyline
function updatePolyline() {
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }

    if (state.route.length > 1) {
        const pathCoords = state.route.map(stop => [stop.lat, stop.lon]);
        
        polyline = L.polyline(pathCoords, {
            color: '#3b82f6',
            weight: 4,
            opacity: 0.7
        }).addTo(map);

        // Fit map to show full route
        map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
    }
}

// Update animated marker
function updateAnimatedMarker() {
    if (animatedMarker) {
        map.removeLayer(animatedMarker);
        animatedMarker = null;
    }

    if (state.animatedPosition) {
        animatedMarker = L.marker(state.animatedPosition, {
            icon: createIcon('#f59e0b', '🚗', 40)
        }).addTo(map);
    }
}

// Clear solution data
function clearSolution() {
    state.route = [];
    state.pickupPoints = [];
    state.dropoffPoints = [];
    state.assignedPassengers = {};
    state.totalDistance = 0;
    state.totalTime = 0;
    state.schedule = [];
    state.statistics = null;
    
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }
    
    pickupPointMarkers.forEach(m => map.removeLayer(m));
    pickupPointMarkers = [];
    
    dropoffPointMarkers.forEach(m => map.removeLayer(m));
    dropoffPointMarkers = [];
}

// Update UI elements
function updateUI() {
    // Update passenger count
    document.getElementById('passengerCount').textContent = state.passengers.length;

    // Update mode indicator
    const modeText = document.getElementById('modeText');
    if (!state.driver) {
        modeText.textContent = 'Drag the car onto the map to place driver';
    } else if (state.mode === 'pickup') {
        modeText.textContent = 'Click map for passenger pickup location';
    } else if (state.mode === 'destination') {
        modeText.textContent = 'Click map for passenger destination';
    } else if (state.passengers.length === 0) {
        modeText.textContent = 'Click "Add Passenger" to start';
    } else if (state.isSolved) {
        modeText.textContent = `✓ Route optimized with ${state.statistics?.pickup_points || 0} pickup points`;
    } else {
        modeText.textContent = `Ready to optimize ${state.passengers.length} passenger(s)`;
    }

    // Update driver status
    const driverStatus = document.getElementById('driverStatus');
    const driverBadge = document.getElementById('driverBadge');
    if (state.driver) {
        driverStatus.textContent = 'Placed on map';
        driverBadge.style.display = 'block';
    } else {
        driverStatus.textContent = 'Drag me';
        driverBadge.style.display = 'none';
    }

    // Update pending badge
    const pendingBadge = document.getElementById('pendingBadge');
    pendingBadge.style.display = state.mode === 'destination' ? 'block' : 'none';

    // Update passengers list
    const passengersList = document.getElementById('passengersList');
    if (state.passengers.length === 0) {
        passengersList.innerHTML = '<div class="empty-state">No passengers added</div>';
    } else {
        passengersList.innerHTML = state.passengers.map((p, idx) => {
            const assignment = state.assignedPassengers[p.id];
            let assignmentHtml = '';
            
            if (assignment) {
                assignmentHtml = `
                    <div class="passenger-assignment">
                        <div class="assignment-row">
                            <span>🚏 ${assignment.assigned_pickup.label}</span>
                            <span class="walk-dist">${(assignment.walk_to_pickup_km * 1000).toFixed(0)}m walk</span>
                        </div>
                        <div class="assignment-row">
                            <span>🛑 ${assignment.assigned_dropoff.label}</span>
                            <span class="walk-dist">${(assignment.walk_from_dropoff_km * 1000).toFixed(0)}m walk</span>
                        </div>
                    </div>
                `;
            }
            
            return `
                <div class="passenger-item ${assignment ? 'assigned' : ''}">
                    <div class="passenger-header">
                        <strong>${p.name}</strong>
                        <button class="btn-remove" onclick="removePassenger('${p.id}')">×</button>
                    </div>
                    ${assignmentHtml}
                </div>
            `;
        }).join('');
    }

    // Update solve button
    const solveBtn = document.getElementById('solveBtn');
    solveBtn.disabled = !state.driver || state.passengers.length === 0 || state.isAnimating;

    // Update animate button
    const animateBtn = document.getElementById('animateBtn');
    animateBtn.disabled = !state.isSolved || state.isAnimating;
    
    if (state.isAnimating) {
        animateBtn.innerHTML = `
            <svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
            </svg>
            Pause
        `;
    } else {
        animateBtn.innerHTML = `
            <svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Animate Route
        `;
    }

    // Update stats card
    const statsCard = document.getElementById('statsCard');
    if (state.isSolved && state.statistics) {
        statsCard.style.display = 'block';
        document.getElementById('totalDistance').textContent = `${state.totalDistance.toFixed(2)} km`;
        document.getElementById('assignedCount').textContent = 
            `${state.statistics.selected_passengers}/${state.statistics.total_passengers}`;
        document.getElementById('stopsCount').textContent = state.statistics.total_stops;
        document.getElementById('roadPoints').textContent = 
            `${state.statistics.pickup_points} pickup + ${state.statistics.dropoff_points} dropoff`;
    } else {
        statsCard.style.display = 'none';
    }

    // Update route overlay
    const routeOverlay = document.getElementById('routeOverlay');
    if (state.isAnimating) {
        routeOverlay.style.display = 'flex';
        const routeStatus = document.getElementById('routeStatus');
        if (state.currentStopIndex < state.route.length) {
            const currentStop = state.route[state.currentStopIndex];
            routeStatus.textContent = `At ${currentStop.label || 'stop ' + (state.currentStopIndex + 1)}`;
        }
    } else {
        routeOverlay.style.display = 'none';
    }
}

// Handle add passenger button
function handleAddPassenger() {
    if (!state.driver) {
        alert('Please place the driver on the map first');
        return;
    }
    state.mode = 'pickup';
    updateUI();
}

// Remove passenger
function removePassenger(id) {
    state.passengers = state.passengers.filter(p => p.id !== id);
    state.isSolved = false;
    clearSolution();
    updateUI();
    updateMarkers();
}

// Handle solve button
async function handleSolve() {
    if (!state.driver || state.passengers.length === 0) return;

    const solveBtn = document.getElementById('solveBtn');
    solveBtn.innerHTML = `
        <svg class="icon-small animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"></path>
        </svg>
        Computing...
    `;
    solveBtn.disabled = true;

    try {
        const result = await api.optimize(
            state.driver, 
            state.passengers, 
            state.optimizationMode,
            15, // R_dest
            15  // R_depart
        );
        
        if (result && result.success) {
            state.route = result.route || [];
            state.pickupPoints = result.pickup_points || [];
            state.dropoffPoints = result.dropoff_points || [];
            state.assignedPassengers = result.assigned_passengers || {};
            state.totalDistance = result.total_distance_km || 0;
            state.totalTime = result.total_time_min || 0;
            state.schedule = result.schedule || [];
            state.statistics = result.statistics || null;
            
            state.isSolved = true;
            state.currentStopIndex = 0;
            
            updateMarkers();
            updatePolyline();
            updateUI();
            
            console.log('Optimization result:', result);
        } else {
            throw new Error(result.error || 'Optimization failed');
        }
    } catch (error) {
        console.error('Failed to solve assignment:', error);
        alert('Failed to compute route: ' + error.message);
    } finally {
        solveBtn.innerHTML = `
            <svg class="icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
            </svg>
            Solve Assignment
        `;
        solveBtn.disabled = false;
    }
}

// Animate route
function handleAnimate() {
    if (state.route.length < 2) return;

    state.isAnimating = !state.isAnimating;
    
    if (state.isAnimating) {
        state.currentStopIndex = 0;
        updateUI();
        animateAlongRoute();
    } else {
        if (animatedMarker) {
            map.removeLayer(animatedMarker);
            animatedMarker = null;
        }
        updateUI();
    }
}

// Animation function
function animateAlongRoute() {
    if (!state.isAnimating || state.route.length < 2) {
        state.isAnimating = false;
        updateUI();
        return;
    }

    const duration = 2000; // 2 seconds per segment
    const steps = 50;
    let currentStep = 0;

    function animate() {
        if (!state.isAnimating || state.currentStopIndex >= state.route.length - 1) {
            state.isAnimating = false;
            state.animatedPosition = null;
            updateUI();
            updateAnimatedMarker();
            return;
        }

        const fromStop = state.route[state.currentStopIndex];
        const toStop = state.route[state.currentStopIndex + 1];

        if (currentStep < steps) {
            const ratio = currentStep / steps;
            const lat = fromStop.lat + (toStop.lat - fromStop.lat) * ratio;
            const lon = fromStop.lon + (toStop.lon - fromStop.lon) * ratio;

            state.animatedPosition = [lat, lon];
            updateAnimatedMarker();
            updateUI();

            currentStep++;
            setTimeout(() => animate(), duration / steps);
        } else {
            // Move to next segment
            state.currentStopIndex++;
            currentStep = 0;
            updateUI();
            setTimeout(() => animate(), 500); // Pause at stop
        }
    }

    animate();
}

// Reset all
function handleReset() {
    if (state.animationFrame) {
        cancelAnimationFrame(state.animationFrame);
    }
    
    state.driver = null;
    state.passengers = [];
    state.mode = null;
    state.pendingPickup = null;
    state.isAnimating = false;
    state.animatedPosition = null;
    state.isSolved = false;
    state.currentStopIndex = 0;
    
    clearSolution();
    updateUI();
    updateMarkers();
    updatePolyline();
    
    if (animatedMarker) {
        map.removeLayer(animatedMarker);
        animatedMarker = null;
    }
}

// Check API connection status
async function checkAPIStatus() {
    try {
        const result = await api.healthCheck();
        state.apiConnected = result.status === 'ok';
    } catch (error) {
        state.apiConnected = false;
    }
    
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (state.apiConnected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Backend Connected';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Backend Offline';
    }
}

// Handle algorithm selection change
function handleAlgorithmChange(e) {
    const value = e.target.value;
    if (value === 'exact' || value === 'heuristic') {
        state.optimizationMode = value;
        if (state.isSolved) {
            state.isSolved = false;
            clearSolution();
            updateUI();
            updateMarkers();
        }
    }
}

// Handle capacity change
function handleCapacityChange(e) {
    state.capacity = parseInt(e.target.value);
    document.getElementById('capacityValue').textContent = state.capacity;
    
    if (state.driver) {
        state.driver.capacity = state.capacity;
        if (state.isSolved) {
            state.isSolved = false;
            clearSolution();
            updateUI();
            updateMarkers();
        }
    }
}

// Initialize event listeners
function initEventListeners() {
    document.getElementById('addPassengerBtn').addEventListener('click', handleAddPassenger);
    document.getElementById('solveBtn').addEventListener('click', handleSolve);
    document.getElementById('animateBtn').addEventListener('click', handleAnimate);
    document.getElementById('resetBtn').addEventListener('click', handleReset);
    document.getElementById('algorithmSelect').addEventListener('change', handleAlgorithmChange);
    document.getElementById('capacitySlider').addEventListener('input', handleCapacityChange);
    
    // Make driver draggable
    const driverDragZone = document.getElementById('driverDragZone');
    driverDragZone.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', 'driver');
        e.dataTransfer.effectAllowed = 'copy';
    });
}

// Initialize application
function init() {
    initMap();
    initEventListeners();
    updateUI();
    
    // Check API status on load and periodically
    checkAPIStatus();
    setInterval(checkAPIStatus, 30000); // Every 30 seconds
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

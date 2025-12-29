// OSRM (Open Source Routing Machine) integration for real road-based routing

// Fetch route between two points using OSRM public API
async function getRouteFromOSRM(start, end) {
    try {
        // OSRM uses lng,lat format (opposite of Leaflet's lat,lng)
        const url = `https://router.project-osrm.org/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
            return null;
        }

        const route = data.routes[0];
        // Convert GeoJSON coordinates from [lng, lat] to [lat, lng] for Leaflet
        const coordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);

        return {
            coordinates: coordinates,
            distance: route.distance, // meters
            duration: route.duration  // seconds
        };
    } catch (error) {
        console.error('OSRM routing error:', error);
        return null;
    }
}

// Fetch a complete route through multiple waypoints
async function getFullRouteFromOSRM(waypoints) {
    if (waypoints.length < 2) return null;

    try {
        // Build waypoints string in lng,lat format
        const waypointsStr = waypoints.map(wp => `${wp[1]},${wp[0]}`).join(';');

        const url = `https://router.project-osrm.org/route/v1/driving/${waypointsStr}?overview=full&geometries=geojson`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
            return null;
        }

        const route = data.routes[0];
        // Convert GeoJSON coordinates from [lng, lat] to [lat, lng] for Leaflet
        const coordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);

        return {
            coordinates: coordinates,
            distance: route.distance,
            duration: route.duration
        };
    } catch (error) {
        console.error('OSRM routing error:', error);
        return null;
    }
}

// Get segment routes between each pair of stops
async function getSegmentedRoute(stops) {
    if (stops.length < 2) return null;

    const segments = [];
    const allCoordinates = [];
    let totalDistance = 0;

    for (let i = 0; i < stops.length - 1; i++) {
        const segment = await getRouteFromOSRM(stops[i], stops[i + 1]);
        
        if (!segment) {
            // Fallback to straight line if OSRM fails
            segments.push({
                coordinates: [stops[i], stops[i + 1]],
                distance: 0,
                duration: 0
            });
            if (allCoordinates.length === 0 || allCoordinates[allCoordinates.length - 1] !== stops[i]) {
                allCoordinates.push(stops[i]);
            }
            allCoordinates.push(stops[i + 1]);
        } else {
            segments.push(segment);
            totalDistance += segment.distance;
            
            // Add coordinates, avoiding duplicates at segment boundaries
            segment.coordinates.forEach((coord, idx) => {
                if (idx === 0 && allCoordinates.length > 0) {
                    // Skip first point if it matches the last point we added
                    const last = allCoordinates[allCoordinates.length - 1];
                    if (last[0] === coord[0] && last[1] === coord[1]) return;
                }
                allCoordinates.push(coord);
            });
        }
    }

    return {
        segments: segments,
        totalDistance: totalDistance / 1000, // Convert to km
        allCoordinates: allCoordinates
    };
}

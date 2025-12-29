// Routing algorithm for carpool assignment

// Calculate cost for a passenger (distance from driver to pickup + pickup to destination)
function calculatePassengerCost(driver, passenger) {
    const toPickup = haversineDistance(
        driver.position[0], driver.position[1],
        passenger.pickup[0], passenger.pickup[1]
    );
    const toDestination = haversineDistance(
        passenger.pickup[0], passenger.pickup[1],
        passenger.destination[0], passenger.destination[1]
    );
    return toPickup + toDestination;
}

// Select optimal passengers based on capacity using greedy assignment
function assignPassengers(driver, passengers) {
    if (passengers.length <= driver.capacity) {
        return passengers;
    }

    // Calculate cost for each passenger
    const costs = passengers.map(p => ({
        passenger: p,
        cost: calculatePassengerCost(driver, p)
    }));

    // Sort by cost and take the top N (capacity)
    costs.sort((a, b) => a.cost - b.cost);
    return costs.slice(0, driver.capacity).map(c => c.passenger);
}

// Optimize route using nearest neighbor with pickup-before-dropoff constraint
function optimizeRoute(driver, passengers) {
    if (passengers.length === 0) return [];

    const route = [{ position: driver.position, type: 'driver' }];
    const pickedUp = new Set();
    const droppedOff = new Set();

    // Create all stops
    const pickupStops = passengers.map(p => ({
        position: p.pickup,
        type: 'pickup',
        passengerId: p.id,
        passengerName: p.name
    }));

    const dropoffStops = passengers.map(p => ({
        position: p.destination,
        type: 'dropoff',
        passengerId: p.id,
        passengerName: p.name
    }));

    let currentPos = driver.position;

    // Nearest neighbor with constraint: must pick up before drop off
    while (pickedUp.size < passengers.length || droppedOff.size < passengers.length) {
        let nearestStop = null;
        let nearestDist = Infinity;

        // Check available pickup stops
        for (const stop of pickupStops) {
            if (pickedUp.has(stop.passengerId)) continue;
            const dist = haversineDistance(
                currentPos[0], currentPos[1],
                stop.position[0], stop.position[1]
            );
            if (dist < nearestDist) {
                nearestDist = dist;
                nearestStop = stop;
            }
        }

        // Check available dropoff stops (only if passenger is picked up)
        for (const stop of dropoffStops) {
            if (!pickedUp.has(stop.passengerId) || droppedOff.has(stop.passengerId)) continue;
            const dist = haversineDistance(
                currentPos[0], currentPos[1],
                stop.position[0], stop.position[1]
            );
            if (dist < nearestDist) {
                nearestDist = dist;
                nearestStop = stop;
            }
        }

        if (nearestStop) {
            route.push(nearestStop);
            currentPos = nearestStop.position;
            if (nearestStop.type === 'pickup') {
                pickedUp.add(nearestStop.passengerId);
            } else {
                droppedOff.add(nearestStop.passengerId);
            }
        } else {
            break;
        }
    }

    return route;
}

// Main solving function
async function solveAssignment(driver, passengers) {
    const assignedPassengers = assignPassengers(driver, passengers);
    const route = optimizeRoute(driver, assignedPassengers);

    // Get real road coordinates from OSRM
    const stopPositions = route.map(r => r.position);
    const roadResult = await getSegmentedRoute(stopPositions);

    let totalDistance = 0;
    let roadCoordinates = [];
    let segmentIndices = [0];

    if (roadResult) {
        totalDistance = roadResult.totalDistance;
        roadCoordinates = roadResult.allCoordinates;

        // Calculate segment indices (where in roadCoordinates each stop is)
        let coordIndex = 0;
        for (let i = 0; i < roadResult.segments.length; i++) {
            coordIndex += roadResult.segments[i].coordinates.length - (i > 0 ? 1 : 0);
            segmentIndices.push(Math.min(coordIndex, roadCoordinates.length - 1));
        }
    } else {
        // Fallback to straight lines if OSRM fails
        roadCoordinates = stopPositions;
        segmentIndices = stopPositions.map((_, i) => i);
        for (let i = 0; i < route.length - 1; i++) {
            totalDistance += haversineDistance(
                route[i].position[0], route[i].position[1],
                route[i + 1].position[0], route[i + 1].position[1]
            );
        }
    }

    return {
        assignedPassengers: assignedPassengers,
        route: route,
        totalDistance: totalDistance,
        roadCoordinates: roadCoordinates,
        segmentIndices: segmentIndices
    };
}

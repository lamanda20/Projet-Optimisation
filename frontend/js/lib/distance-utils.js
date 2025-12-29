// Haversine formula to calculate distance between two coordinates in kilometers
function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function toRad(deg) {
    return deg * (Math.PI / 180);
}

// Interpolate between two points for animation
function interpolatePosition(start, end, progress) {
    return [
        start[0] + (end[0] - start[0]) * progress,
        start[1] + (end[1] - start[1]) * progress
    ];
}

// Calculate total route distance
function calculateRouteDistance(route) {
    let total = 0;
    for (let i = 0; i < route.length - 1; i++) {
        total += haversineDistance(
            route[i][0], route[i][1],
            route[i + 1][0], route[i + 1][1]
        );
    }
    return total;
}

// API Client for Carpool Backend - Bus-Style System

class CarpoolAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', message: error.message };
        }
    }

    async optimize(driver, passengers, mode = 'heuristic', R_dest = 25, R_depart = 25) {
        try {
            const response = await fetch(`${this.baseURL}/api/optimize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    driver: {
                        lat: driver.position[0],
                        lon: driver.position[1],
                        capacity: driver.capacity
                    },
                    passengers: passengers.map(p => ({
                        id: p.id,
                        name: p.name,
                        pickup_lat: p.pickup[0],
                        pickup_lon: p.pickup[1],
                        dest_lat: p.destination[0],
                        dest_lon: p.destination[1]
                    })),
                    mode: mode,
                    R_dest: R_dest,
                    R_depart: R_depart
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Optimization failed:', error);
            throw error;
        }
    }
}

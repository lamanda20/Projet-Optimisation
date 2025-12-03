# Marrakech Carpool - Complete Setup Guide

## 🎯 What You Have Now

You now have a **full-stack carpool optimization application** with:

### **Frontend** (`carpooling-app-vanilla/`)
- Vanilla HTML/CSS/JavaScript web app
- Interactive Leaflet map interface
- 3 optimization algorithms to choose from
- Real-time backend connection status

### **Backend** (`carpooling-backend/`)
- Flask REST API server
- Integration with Projet-Optimisation algorithms
- Supports exact and heuristic optimization modes

---

## 🚀 Quick Start

### Option 1: Automated Startup (Windows)

1. Open PowerShell or Command Prompt
2. Navigate to the project folder:
   ```powershell
   cd C:\Users\anass\Desktop\projet_ro
   ```

3. Run the startup script:
   ```powershell
   start-app.bat
   ```

This will:
- Start the Flask backend on port 5000
- Start a web server for the frontend on port 8000
- Open your browser to http://localhost:8000

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```powershell
cd C:\Users\anass\Desktop\projet_ro\carpooling-backend
pip install -r requirements.txt
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\anass\Desktop\projet_ro\carpooling-app-vanilla
python -m http.server 8000
```

**Browser:**
Open http://localhost:8000

---

## 📋 First Time Setup

### 1. Install Python Dependencies

```powershell
cd C:\Users\anass\Desktop\projet_ro\carpooling-backend
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- Requests (HTTP client)

### 2. Verify Installation

Test the backend:
```powershell
cd carpooling-backend
python app.py
```

You should see:
```
Starting Carpool Backend API...
 * Running on http://0.0.0.0:5000
```

Test in another terminal:
```powershell
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status":"ok","message":"Carpool API is running"}
```

---

## 🎮 How to Use the Application

### 1. Check Backend Status
- Look at the top of the sidebar
- **Green dot** = Backend connected (advanced algorithms available)
- **Red dot** = Backend offline (only simple algorithm works)

### 2. Choose an Algorithm

**Simple Greedy** (works offline):
- Basic nearest-neighbor approach
- Fast, good for simple scenarios
- No backend required

**Phase 1 - Exact** (requires backend):
- Hungarian algorithm for optimal assignment
- Double clustering (destinations + departures)
- Branch & Bound for TSP
- Best quality, slower for large datasets

**Phase 1 - Heuristic** (requires backend):
- K-means clustering
- Greedy selection
- Nearest neighbor + 2-opt
- Fast, good quality

### 3. Set Up Your Scenario

1. **Drag the car** from the sidebar onto the map
2. **Adjust capacity** using the slider (1-6 passengers)
3. **Add passengers**:
   - Click "Add Passenger"
   - Click on the map for pickup location (green pin)
   - Click again for destination (red pin)
4. Repeat step 3 for more passengers

### 4. Optimize and Visualize

1. Click **"Solve Assignment"**
   - Backend will compute the optimal route
   - You'll see the blue route line on the map
   - Statistics appear in the sidebar

2. Click **"Animate Route"**
   - Watch the car move along the route
   - See pickup and dropoff notifications

3. Click **"Reset"** to start over

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Error: "No module named 'flask'"**
```powershell
pip install flask flask-cors requests
```

**Import errors from Projet-Optimisation-main**
Make sure the backend is in the correct location:
```
projet_ro/
├── carpooling-backend/
│   └── app.py
└── Projet-Optimisation-main/
    ├── algorithms/
    ├── models/
    └── utils/
```

### Frontend Issues

**"Backend Offline" message**
- Check if backend is running: `curl http://localhost:5000/api/health`
- Check firewall settings
- Verify CORS is enabled in Flask

**Map doesn't load**
- Check internet connection (needs OpenStreetMap tiles)
- Check browser console for errors
- Try refreshing the page

**No route displayed**
- Ensure you have both driver and passengers placed
- Check that backend is connected
- Look at browser console for errors

**OSRM errors**
- OSRM public API may have rate limits
- Route will fallback to straight lines
- Consider running your own OSRM instance

---

## 📊 Algorithm Comparison

| Feature | Simple | Phase1-Exact | Phase1-Heuristic |
|---------|--------|--------------|------------------|
| **Backend Required** | ❌ No | ✅ Yes | ✅ Yes |
| **Speed** | ⚡ Very Fast | 🐌 Slow | ⚡ Fast |
| **Quality** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Optimal | ⭐⭐⭐⭐ Very Good |
| **Max Passengers** | 20+ | 10 | 50+ |
| **Clustering** | ❌ No | ✅ Yes | ✅ Yes |
| **Pickup Points** | Individual | Optimized | Optimized |
| **Best For** | Quick tests | Small, critical | Production use |

---

## 🌐 API Testing

### Test Simple Optimization

```powershell
curl -X POST http://localhost:5000/api/optimize/simple -H "Content-Type: application/json" -d "{\"driver\":{\"lat\":31.6295,\"lon\":-7.9811,\"capacity\":4},\"passengers\":[{\"id\":\"p1\",\"name\":\"Passenger 1\",\"pickup_lat\":31.63,\"pickup_lon\":-7.98,\"dest_lat\":31.64,\"dest_lon\":-7.97}]}"
```

### Test Phase 1 Exact

```powershell
curl -X POST http://localhost:5000/api/optimize/phase1 -H "Content-Type: application/json" -d "{\"driver\":{\"lat\":31.6295,\"lon\":-7.9811,\"capacity\":4},\"passengers\":[{\"id\":\"p1\",\"name\":\"Passenger 1\",\"pickup_lat\":31.63,\"pickup_lon\":-7.98,\"dest_lat\":31.64,\"dest_lon\":-7.97}],\"mode\":\"exact\"}"
```

---

## 📁 Project Structure

```
C:\Users\anass\Desktop\projet_ro\
│
├── carpooling-app-vanilla/        # Frontend Application
│   ├── index.html                 # Main HTML
│   ├── README.md                  # Frontend docs
│   ├── css/
│   │   └── styles.css            # All styling
│   └── js/
│       ├── app.js                # Main logic + backend integration
│       └── lib/
│           ├── api-client.js     # Backend API client
│           ├── distance-utils.js # Haversine distance
│           ├── osrm-routing.js   # OSRM integration
│           └── routing-algorithm.js # Simple algorithm
│
├── carpooling-backend/           # Flask Backend API
│   ├── app.py                    # Main Flask server
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend docs
│
├── Projet-Optimisation-main/    # Algorithm Library
│   ├── algorithms/
│   │   ├── exact/               # Exact algorithms
│   │   └── heuristic/           # Heuristic algorithms
│   ├── models/                  # Data models
│   └── utils/                   # Utilities
│
└── start-app.bat                # Startup script (Windows)
```

---

## 🎓 Next Steps

### For Development:

1. **Add more algorithms**:
   - Implement in `Projet-Optimisation-main/algorithms/`
   - Add endpoint in `carpooling-backend/app.py`
   - Add UI option in frontend

2. **Multi-driver support**:
   - Use `/api/optimize/multi-driver` endpoint
   - Update UI to add multiple drivers

3. **Export features**:
   - Export route to GPX/KML
   - Generate PDF reports
   - Save scenarios

### For Production:

1. **Set up proper OSRM instance** (faster, no rate limits)
2. **Add authentication** to backend API
3. **Use production WSGI server** (Gunicorn, uWSGI)
4. **Add database** for storing scenarios
5. **Deploy to cloud** (Azure, AWS, Google Cloud)

---

## 💡 Tips & Best Practices

1. **Start with Simple algorithm** to verify setup works
2. **Use Phase1-Heuristic** for most scenarios (best balance)
3. **Use Phase1-Exact** only for small, critical assignments
4. **Keep backend running** in background during development
5. **Check browser console** for debugging information
6. **Monitor backend logs** for algorithm performance

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review browser console (F12) for errors
3. Check backend terminal for error messages
4. Verify all dependencies are installed
5. Ensure correct project structure

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Flask backend dependencies installed
- [ ] Backend starts without errors on port 5000
- [ ] Frontend accessible at localhost:8000
- [ ] Backend status shows "Connected" (green dot)
- [ ] Can place driver on map
- [ ] Can add passengers
- [ ] Simple algorithm works
- [ ] Phase 1 algorithms work (if backend connected)
- [ ] Route animation works

---

## 🎉 You're Ready!

Your carpooling optimization application is now fully functional with:
✅ Advanced clustering algorithms
✅ Exact and heuristic optimization modes
✅ Real-time backend integration
✅ Beautiful interactive UI
✅ Real road routing

Happy optimizing! 🚗💨

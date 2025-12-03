# Quick Start - Bus-Style Carpool System

## 🚀 Start the Application

### Windows (Easy Way)
```powershell
cd C:\Users\anass\Desktop\projet_ro
.\start-app.bat
```
This automatically:
- Starts backend on port 5000
- Starts frontend on port 8000
- Opens browser to http://localhost:8000

### Manual Way

**Terminal 1 - Backend:**
```powershell
cd C:\Users\anass\Desktop\projet_ro\carpooling-backend
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\anass\Desktop\projet_ro\carpooling-app-vanilla
python -m http.server 8000
```

**Browser:**
Open http://localhost:8000

## ✅ Verify It's Working

1. Check **Backend Connected** status (should be green dot)
2. Map should show Marrakech
3. Algorithm selector should show "Heuristic" and "Exact"

## 🎯 Try It Out

### Simple Example (2 Passengers)

1. **Place Driver**
   - Drag the car 🚗 icon onto the map
   - Drop it near center of Marrakech

2. **Add First Passenger**
   - Click "Add Passenger" button
   - Click on map for pickup location (e.g., near Medina)
   - Click on map for destination (e.g., Gueliz)
   - You'll see green 👤 and red 🏁 markers

3. **Add Second Passenger**
   - Click "Add Passenger" again
   - Click pickup close to first passenger
   - Click destination close to first passenger's destination

4. **Solve**
   - Click "Solve Assignment"
   - Wait 1-2 seconds
   - Should see:
     - Blue 🚏 markers (pickup points)
     - Orange 🛑 markers (dropoff points)
     - Blue line showing route
     - Original markers become faded

5. **Check Results**
   - Look at passenger list in sidebar
   - Each passenger shows walking distances
   - Click "Animate Route" to see car move

## 🔍 What You'll See

### Before Solving
```
Map shows:
🚗 Driver (teal, large)
👤 Passenger origins (green, small)
🏁 Passenger destinations (red, small)
```

### After Solving
```
Map shows:
🚗 Driver (teal, large)
👤 Passenger origins (green, FADED)
🏁 Passenger destinations (red, FADED)
🚏 Pickup points (blue, LARGE) ← NEW!
🛑 Dropoff points (orange, LARGE) ← NEW!
─── Route line (blue)

Sidebar shows:
Passenger 1
  🚏 Pickup R1 - 120m walk
  🛑 Drop-off D1 - 150m walk
Passenger 2
  🚏 Pickup R1 - 140m walk
  🛑 Drop-off D1 - 130m walk
```

## 🏙️ Example Scenario

**Marrakech Example:**
- Driver at: Jemaa el-Fnaa (31.6258, -7.9891)
- P1: From Medina (31.6291, -7.9934) to Gueliz (31.6463, -8.0089)
- P2: From Kasbah (31.6209, -7.9894) to Gueliz (31.6451, -8.0102)
- P3: From Bab Doukkala (31.6382, -8.0048) to Hivernage (31.6392, -8.0205)

**Result:**
- Pickup R1: Medina area (P1, P2)
- Pickup R2: Bab Doukkala area (P3)
- Dropoff D1: Gueliz center (P1, P2)
- Dropoff D2: Hivernage (P3)

Route: Start → R1 → R2 → D1 → D2

## ⚙️ Settings

### Algorithm Selection
- **Heuristic** (default): Fast, ~95% optimal, best for 10+ passengers
- **Exact**: Slower, 100% optimal, best for ≤10 passengers

### Driver Capacity
- Use slider: 1-6 passengers
- More capacity = more passengers can be grouped
- Less capacity = fewer passengers selected

## 🐛 Troubleshooting

### Backend Not Connected
```powershell
# Check if backend is running
curl http://localhost:5000/api/health

# Should return: {"status":"ok",...}
```

### No Route Appears
- Check browser console (F12) for errors
- Verify you have internet connection (needs OpenStreetMap)
- Try with just 2 passengers first

### "No valid passenger groups could be formed"
- Passengers might be too far apart
- Try adding passengers closer together
- Increase driver capacity

### Walking Distances Too Long
- Normal range: 100-500m
- If >1km, passengers might be too spread out
- Try grouping passengers in same neighborhoods

## 📊 Understanding Results

### Stats Panel Shows:
- **Total Distance**: How far driver travels
- **Assigned**: How many passengers selected / total
- **Stops**: Total number of stops
- **Road Points**: Number of pickup + dropoff points

### Good Results:
✅ Walking distances: 100-300m average
✅ Total distance: <20km for city
✅ Stops: 3-6 for 4 passengers
✅ All or most passengers assigned

### Adjust If:
⚠️ Walking distances >500m → Passengers too spread out
⚠️ Only 1-2 passengers assigned → Increase capacity or add closer passengers
⚠️ Too many stops (>8) → Passengers are very dispersed

## 🎮 Tips

1. **Start Simple**: Try 2-3 passengers first
2. **Group Nearby**: Add passengers in same neighborhood
3. **Watch Animation**: See how route works
4. **Check Walking**: Ensure distances are reasonable
5. **Experiment**: Try different algorithms and capacities

## 📚 Learn More

- **Full Guide**: See BUS_STYLE_GUIDE.md
- **Backend API**: See carpooling-backend/README.md
- **Algorithms**: See Projet-Optimisation-main/README.md

## 🎉 Success!

If you see:
- ✅ Green "Backend Connected" status
- ✅ Blue pickup point markers
- ✅ Orange dropoff point markers
- ✅ Walking distances shown for passengers
- ✅ Route animates smoothly

**You're all set! The bus-style system is working!** 🚌

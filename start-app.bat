@echo off
echo Starting Marrakech Carpool Application...
echo.
echo Starting Backend API Server...
start "Backend API" cmd /k "cd carpooling-backend && python app.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend...
echo Opening http://localhost:8000 in your browser...
start "" "http://localhost:8000/carpooling-app-vanilla"

cd carpooling-app-vanilla
python -m http.server 8000

pause

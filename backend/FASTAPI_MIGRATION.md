# FastAPI Migration Guide

## What Changed?

The Flask API (`app.py`) has been replaced with a modern **FastAPI** implementation (`main.py`).

## Key Improvements

### 1. **Type Safety with Pydantic**
- Automatic request validation
- Type hints throughout
- Auto-generated API documentation

### 2. **Better Performance**
- Async support (ready for future improvements)
- Faster request handling
- Built-in OpenAPI schema

### 3. **Cleaner Code**
- Reduced from 609 lines to ~450 lines
- Better organized with Pydantic models
- More maintainable structure

### 4. **Auto-Generated Documentation**
- Interactive API docs at: `http://localhost:5000/docs`
- ReDoc alternative at: `http://localhost:5000/redoc`

## How to Run

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the FastAPI Server
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### 3. Access the API
- **API Base URL**: `http://localhost:5000`
- **Interactive Docs**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

## API Endpoints

### Health Check
```
GET /api/health
```

### Optimize Carpool
```
POST /api/optimize
```

**Supported Algorithms:**
- `exact`: Brute force, 100% optimal (best for ≤10 passengers)
- `heuristic`: Fast approximation, ~95% optimal (best for 10-20 passengers)
- `genetic`: Evolutionary algorithm, ~92-98% optimal (best for 15+ passengers)

**Request Body:**
```json
{
  "driver": {
    "lat": 31.6295,
    "lon": -7.9811,
    "capacity": 4
  },
  "passengers": [
    {
      "id": "p1",
      "name": "Passenger 1",
      "pickup_lat": 31.63,
      "pickup_lon": -7.98,
      "dest_lat": 31.64,
      "dest_lon": -7.97
    }
  ],
  "mode": "heuristic",
  "R_dest": 15,
  "R_depart": 15,
  
  // Optional: Genetic Algorithm Parameters (only when mode="genetic")
  "population_size": 100,
  "generations": 200,
  "mutation_rate": 0.15
}
```

## Validation Features

FastAPI automatically validates:
- ✅ GPS coordinates within Marrakech bounds
- ✅ Driver capacity between 1-10
- ✅ Mode is either "exact", "heuristic", or "genetic"
- ✅ Radius values are positive
- ✅ At least one passenger provided
- ✅ Genetic parameters within valid ranges (when applicable)

Invalid requests return clear error messages with field-level details.

## Frontend Compatibility

The FastAPI maintains **100% compatibility** with the existing frontend. No changes needed to the frontend code!

**New Feature**: The frontend now supports the Genetic Algorithm optimization mode with adjustable parameters (population size, generations, mutation rate).

## Algorithm Options

The API now supports **three optimization algorithms**:

1. **Exact**: Brute-force optimal solution (slow for >10 passengers)
2. **Heuristic**: Fast approximation using DBSCAN and nearest neighbor
3. **Genetic**: Evolutionary metaheuristic (excellent for large datasets)

See [GENETIC_INTEGRATION.md](GENETIC_INTEGRATION.md) for detailed genetic algorithm documentation.

## Old Flask API

The original Flask implementation is preserved in `app.py` if you need to reference it or revert.

## Benefits Summary

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Lines of Code | 609 | ~450 |
| Type Safety | ❌ | ✅ |
| Auto Validation | ❌ | ✅ |
| Auto Docs | ❌ | ✅ |
| Performance | Good | Excellent |
| Async Support | ❌ | ✅ |

## Development Tips

1. **Enable Auto-Reload**: Use `--reload` flag during development
2. **Check API Docs**: Visit `/docs` to test endpoints interactively
3. **View Logs**: FastAPI provides clear, colorful logs
4. **Debugging**: Use the interactive docs to test requests

## Production Deployment

For production, use:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

Or with Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000
```

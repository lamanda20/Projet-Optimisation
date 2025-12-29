# Genetic Algorithm Quick Reference

## Installation
```bash
cd c:\Users\anass\Desktop\projet_ro\Projet-Optimisation-main
..\myenv\Scripts\Activate.ps1
```

## Basic Commands

### Run Genetic Algorithm
```bash
python cli_genetic_solver.py -i data/genetic_input_example.json
```

### Compare All Methods
```bash
python compare_methods.py -i data/genetic_input_example.json
```

### Interactive Demo
```bash
python demo_genetic_algorithm.py
```

## Common Use Cases

### 1. Default Run
```bash
python cli_genetic_solver.py -i data/input.json -o results/output.json
```

### 2. High Quality (Slow)
```bash
python cli_genetic_solver.py -i data/input.json --pop-size 200 --generations 500
```

### 3. Fast Run (Lower Quality)
```bash
python cli_genetic_solver.py -i data/input.json --pop-size 50 --generations 100
```

### 4. Loose Constraints (More Passengers)
```bash
python cli_genetic_solver.py -i data/input.json --R-dest 8.0 --R-depart 8.0
```

### 5. Quiet Mode
```bash
python cli_genetic_solver.py -i data/input.json -q --no-summary
```

## Parameters Quick Guide

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `--pop-size` | 100 | 30-300 | Population size (larger = better exploration) |
| `--generations` | 200 | 50-1000 | Evolution iterations (more = better convergence) |
| `--mutation-rate` | 0.15 | 0.05-0.30 | Mutation probability (higher = more exploration) |
| `--R-dest` | 5.0 | 3.0-15.0 | Destination clustering radius |
| `--R-depart` | 5.0 | 3.0-15.0 | Departure clustering radius |

## Input File Format

```json
{
  "conducteur": {
    "position": [0, 0],
    "capacite": 4
  },
  "passagers": [
    {"id": 1, "depart": [2, 3], "arrivee": [15, 18]},
    {"id": 2, "depart": [3, 4], "arrivee": [16, 19]}
  ]
}
```

## Output File Format

```json
{
  "TRAJET_ORDRE": ["Depart", "R1", "R2"],
  "AFFECTATIONS_PAR_POINT": {
    "R1": ["P1", "P2"]
  },
  "TEMPS_TRAJET_MIN": {
    "Depart": {"R1": 5}
  },
  "Z_optimal": 2,
  "metadata": {
    "method": "genetic_algorithm",
    "population_size": 100,
    "generations": 200
  }
}
```

## Performance Guide

| Dataset Size | Recommended Settings | Expected Time |
|--------------|---------------------|---------------|
| 5-10 pass. | Default (100, 200) | 2-5s |
| 10-15 pass. | Default or (150, 300) | 5-10s |
| 15-20 pass. | (150, 300) | 10-20s |
| 20+ pass. | (200, 500) | 20-60s |

## Troubleshooting

### Problem: ImportError
**Solution:** Activate virtual environment
```bash
..\myenv\Scripts\Activate.ps1
```

### Problem: No clusters formed
**Solution:** Increase R_dest and R_depart
```bash
--R-dest 8.0 --R-depart 8.0
```

### Problem: Too slow
**Solution:** Reduce population/generations
```bash
--pop-size 50 --generations 100
```

### Problem: Poor quality
**Solution:** Increase population/generations
```bash
--pop-size 200 --generations 500
```

## Files Location

```
Projet-Optimisation-main/
├── algorithms/genetic/genetic_carpooling.py  # Core algorithm
├── cli_genetic_solver.py                     # CLI interface
├── compare_methods.py                        # Comparison tool
├── demo_genetic_algorithm.py                 # Demos
├── data/genetic_input_*.json                 # Test data
└── results/genetic_output_*.json             # Results
```

## Method Comparison

| Criteria | Exact | Heuristic | Genetic |
|----------|-------|-----------|---------|
| Speed | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ |
| Quality | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Scalability | ❌ | ✅ | ✅✅ |
| Flexibility | ⭐ | ⭐⭐ | ⭐⭐⭐ |

## Quick Tips

✅ **DO:**
- Use genetic algorithm for 15+ passengers
- Increase pop-size for better solutions
- Adjust R_dest/R_depart based on data
- Save results to JSON for later analysis

❌ **DON'T:**
- Use on tiny datasets (< 5 passengers)
- Set pop-size too low (< 30)
- Set generations too low (< 50)
- Expect instant results on large datasets

## Help

```bash
python cli_genetic_solver.py --help
```

## Documentation

- Full guide: `README_GENETIC_ALGORITHM.md`
- Summary: `GENETIC_IMPLEMENTATION_SUMMARY.md`
- This file: Quick reference for daily use

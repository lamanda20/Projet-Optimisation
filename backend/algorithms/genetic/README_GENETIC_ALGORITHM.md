# Genetic Algorithm for Carpooling Optimization

## Overview

This implementation uses a **Genetic Algorithm (GA)** metaheuristic to solve the carpooling optimization problem. Unlike exact or heuristic approaches, the genetic algorithm evolves a population of solutions over multiple generations to find near-optimal passenger groupings and routes.

## Key Features

### 🧬 Genetic Algorithm Components

1. **Chromosome Representation**
   - Each chromosome represents a complete carpooling solution
   - Consists of:
     - **Clusters**: Groups of passengers riding together
     - **Route**: Order in which pickup points are visited

2. **Fitness Function**
   - Minimizes total route distance
   - Maximizes number of passengers served
   - Rewards compact clusters (passengers with nearby pickup/dropoff points)
   - Encourages better vehicle capacity utilization

3. **Selection Method**
   - Tournament selection for parent choosing
   - Elitism to preserve best solutions across generations

4. **Crossover Operator**
   - Combines clusters from two parents
   - Validates cluster compatibility (destination/departure proximity)
   - Rebuilds optimal routes for new cluster combinations

5. **Mutation Operators**
   - Route swap: Exchange positions in pickup order
   - Cluster merge: Combine two compatible clusters
   - Cluster split: Divide large clusters into smaller ones
   - Route segment reversal: Reverse part of the route

### 🎯 Advantages Over Other Methods

| Feature | Exact Method | Heuristic Method | Genetic Algorithm |
|---------|-------------|------------------|-------------------|
| Solution Quality | Optimal (small instances) | Good | Very Good to Excellent |
| Scalability | Poor (exponential time) | Good | Excellent |
| Flexibility | Limited | Limited | High (easily customizable) |
| Exploration | Complete | Greedy | Balanced exploration/exploitation |
| Handles Constraints | Rigid | Moderate | Very flexible |

## Installation & Setup

### Prerequisites

```bash
# Ensure you have the virtual environment activated
cd c:\Users\anass\Desktop\projet_ro
.\myenv\Scripts\Activate.ps1
```

### Required Packages

The following packages are already installed in `myenv`:
- `numpy` - Numerical computations
- `scikit-learn` - Used by other clustering methods (imported indirectly)
- `pandas` - Data handling

## Usage

### Basic Command

```bash
python cli_genetic_solver.py -i data/genetic_input_example.json -o results/output.json
```

### All Command-Line Options

```bash
python cli_genetic_solver.py [OPTIONS]

Required Arguments:
  -i, --input PATH          Input JSON file with passengers and driver data

Optional Arguments:
  -o, --output PATH         Output JSON file (default: results/genetic_solution.json)
  
Genetic Algorithm Parameters:
  --pop-size INT           Population size (default: 100)
                           Larger = better exploration, slower
                           
  --generations INT        Number of generations (default: 200)
                           More = better convergence, longer runtime
                           
  --mutation-rate FLOAT    Mutation probability (default: 0.15)
                           Range: 0.0 to 1.0
                           Higher = more exploration
                           
  --elite-size INT         Number of elite solutions preserved (default: 10)
                           
  --tournament-size INT    Tournament selection size (default: 5)

Clustering Parameters:
  --R-dest FLOAT           Max distance for destination clustering (default: 5.0)
  --R-depart FLOAT         Max distance for departure clustering (default: 5.0)

Display Options:
  -q, --quiet              Suppress progress output
  --no-summary             Don't print solution summary
```

### Examples

#### 1. Basic Usage
```bash
python cli_genetic_solver.py -i data/genetic_input_example.json
```

#### 2. High-Quality Solution (More Generations)
```bash
python cli_genetic_solver.py \
  -i data/genetic_input_large.json \
  -o results/high_quality.json \
  --pop-size 200 \
  --generations 500
```

#### 3. Fast Solution (Fewer Resources)
```bash
python cli_genetic_solver.py \
  -i data/genetic_input_example.json \
  -o results/fast.json \
  --pop-size 50 \
  --generations 100
```

#### 4. Loose Clustering Constraints
```bash
python cli_genetic_solver.py \
  -i data/genetic_input_example.json \
  --R-dest 8.0 \
  --R-depart 8.0
```

#### 5. Quiet Mode
```bash
python cli_genetic_solver.py \
  -i data/genetic_input_example.json \
  -q --no-summary
```

## Input Format

The input JSON file should have the following structure:

```json
{
  "conducteur": {
    "position": [x, y],
    "capacite": n
  },
  "passagers": [
    {
      "id": 1,
      "depart": [x1, y1],
      "arrivee": [x2, y2]
    },
    ...
  ]
}
```

### Example Input

```json
{
  "conducteur": {
    "position": [0, 0],
    "capacite": 4
  },
  "passagers": [
    {"id": 1, "depart": [2, 3], "arrivee": [15, 18]},
    {"id": 2, "depart": [3, 4], "arrivee": [16, 19]},
    {"id": 3, "depart": [8, 2], "arrivee": [20, 15]}
  ]
}
```

## Output Format

The output JSON follows the standard Phase 2 format:

```json
{
  "TRAJET_ORDRE": ["Depart", "R1", "R2", "R3"],
  "AFFECTATIONS_PAR_POINT": {
    "R1": ["P1", "P2"],
    "R2": ["P3", "P4"]
  },
  "TEMPS_TRAJET_MIN": {
    "Depart": {"R1": 5},
    "R1": {"R2": 7}
  },
  "Z_optimal": 4,
  "metadata": {
    "method": "genetic_algorithm",
    "population_size": 100,
    "generations": 200,
    "mutation_rate": 0.15,
    "R_dest": 5.0,
    "R_depart": 5.0,
    "total_passengers": 4,
    "num_clusters": 2
  }
}
```

## Algorithm Details

### Chromosome Structure

```python
{
  'clusters': [
    [Passager1, Passager2],  # Cluster 1
    [Passager3, Passager4, Passager5],  # Cluster 2
    ...
  ],
  'route': [0, 2, 1, ...]  # Order to visit clusters
}
```

### Fitness Calculation

The fitness function combines multiple objectives:

```
fitness = route_distance 
          - (passengers_served × 50)
          + (cluster_compactness × 0.5)
          - (capacity_utilization × 20)
```

Lower fitness is better. The algorithm heavily rewards serving more passengers while minimizing travel distance.

### Evolution Process

1. **Initialize** random population of valid solutions
2. **For each generation:**
   - Evaluate fitness of all chromosomes
   - Select best solutions (elitism)
   - Create offspring via:
     - Tournament selection
     - Crossover
     - Mutation (with probability)
   - Replace old population with new generation
3. **Return** best solution found

### Constraint Handling

The algorithm enforces:
- ✅ Passengers in same cluster have destinations within `R_dest`
- ✅ Passengers in same cluster have departures within `R_depart`
- ✅ Cluster size ≤ vehicle capacity
- ✅ Minimum 2 passengers per cluster
- ✅ No passenger assigned to multiple clusters

## Performance Tuning

### For Better Solutions
- ⬆️ Increase `--pop-size` (100 → 200)
- ⬆️ Increase `--generations` (200 → 500)
- ⬇️ Decrease `--mutation-rate` (0.15 → 0.10)

### For Faster Execution
- ⬇️ Decrease `--pop-size` (100 → 50)
- ⬇️ Decrease `--generations` (200 → 100)
- ⬆️ Increase `--mutation-rate` (0.15 → 0.20)

### For More Passengers Served
- ⬆️ Increase `--R-dest` (5.0 → 8.0)
- ⬆️ Increase `--R-depart` (5.0 → 8.0)
- ⬆️ Increase vehicle capacity in input

## Comparison with Other Methods

### Running Different Methods

```bash
# Genetic Algorithm
python cli_genetic_solver.py -i data/input.json -o results/ga_output.json

# Exact Method (for comparison)
python demo_phase2_advanced.py --method exact --input data/input.json

# Heuristic Method (for comparison)
python demo_phase2_advanced.py --method heuristic --input data/input.json
```

### Expected Performance

| Dataset Size | Exact Method | Heuristic | Genetic Algorithm |
|--------------|-------------|-----------|-------------------|
| 5-10 passengers | < 1s | < 1s | 2-5s |
| 10-15 passengers | 1-10s | < 1s | 5-10s |
| 15-20 passengers | 10-60s+ | < 2s | 10-15s |
| 20+ passengers | Too slow | < 5s | 15-30s |

## Test Results

### Example Dataset (10 passengers, capacity 4)

```
Total Passengers Served: 10
Number of Clusters: 4
Total Travel Time: 24 minutes

Clusters:
  R1: 3 passengers (P10, P1, P2)
  R2: 2 passengers (P3, P4)
  R3: 2 passengers (P8, P9)
  R4: 3 passengers (P5, P7, P6)
```

### Large Dataset (15 passengers, capacity 5)

```
Total Passengers Served: 15
Number of Clusters: 5
Total Travel Time: 47 minutes

Clusters:
  R1: 3 passengers
  R2: 3 passengers
  R3: 3 passengers
  R4: 4 passengers
  R5: 2 passengers
```

## Implementation Files

```
Projet-Optimisation-main/
├── algorithms/
│   └── genetic/
│       ├── __init__.py
│       └── genetic_carpooling.py       # Core GA implementation
├── cli_genetic_solver.py                # Command-line interface
├── data/
│   ├── genetic_input_example.json      # Small test dataset
│   └── genetic_input_large.json        # Larger test dataset
└── results/
    ├── genetic_output_example.json     # Example output
    └── genetic_output_large.json       # Large output
```

## Troubleshooting

### Issue: Import Errors
```
Solution: Activate virtual environment
.\myenv\Scripts\Activate.ps1
```

### Issue: Poor Solutions
```
Solution: Increase generations and population size
python cli_genetic_solver.py -i input.json --pop-size 200 --generations 500
```

### Issue: No Clusters Formed
```
Solution: Increase R_dest and R_depart parameters
python cli_genetic_solver.py -i input.json --R-dest 8.0 --R-depart 8.0
```

### Issue: Slow Execution
```
Solution: Reduce population size and generations
python cli_genetic_solver.py -i input.json --pop-size 50 --generations 100
```

## Future Enhancements

Potential improvements:
- [ ] Multi-vehicle support (multiple drivers)
- [ ] Time window constraints (passengers have deadlines)
- [ ] Variable mutation rates (adaptive mutation)
- [ ] Parallel evaluation (multi-threading)
- [ ] Hybrid GA + local search
- [ ] Visualization of solution evolution
- [ ] Real-world distance matrix support

## References

- Holland, J. H. (1992). "Genetic Algorithms"
- Goldberg, D. E. (1989). "Genetic Algorithms in Search, Optimization, and Machine Learning"
- Vehicle Routing Problem (VRP) literature
- Carpooling optimization studies

## Author

Implemented as part of the Projet-Optimisation carpooling system.

## License

Same as parent project.

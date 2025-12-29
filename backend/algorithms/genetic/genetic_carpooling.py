"""
Genetic Algorithm Metaheuristic for Carpooling Optimization
Solves the carpooling problem by evolving populations of solutions that include:
1. Passenger clustering (who rides together)
2. Route optimization (pickup order)
"""

from typing import List, Dict, Tuple, Optional
import random
import numpy as np
from models.Passager import Passager
from models.Conducteur import Conducteur
from utils.distance import distance_grille
from utils.centroide import calculer_centroide_grille


class GeneticCarpoolingSolver:
    """
    Genetic Algorithm solver for carpooling optimization
    
    A chromosome represents a complete solution:
    - Clustering: which passengers are grouped together
    - Route: the order in which pickup points are visited
    """
    
    def __init__(
        self,
        passagers: List[Passager],
        conducteur: Conducteur,
        population_size: int = 100,
        generations: int = 200,
        mutation_rate: float = 0.15,
        elite_size: int = 10,
        tournament_size: int = 5,
        R_dest: float = 5.0,
        R_depart: float = 5.0,
        verbose: bool = True
    ):
        self.passagers = passagers
        self.conducteur = conducteur
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.R_dest = R_dest
        self.R_depart = R_depart
        self.verbose = verbose
        
        self.population = []
        self.best_solution = None
        self.best_fitness = float('inf')
        self.fitness_history = []
        
    def create_chromosome(self) -> Dict:
        """
        Create a random chromosome (solution)
        
        Chromosome structure:
        {
            'clusters': [[p1, p2], [p3, p4, p5], ...],  # Passenger groupings
            'route': [0, 2, 1, ...]  # Order to visit clusters
        }
        """
        # Create random valid clusters
        clusters = self._create_random_clusters()
        
        # Create random route through clusters
        if clusters:
            route = list(range(len(clusters)))
            random.shuffle(route)
        else:
            route = []
        
        return {
            'clusters': clusters,
            'route': route
        }
    
    def _create_random_clusters(self) -> List[List[Passager]]:
        """Create random but valid clusters based on proximity constraints"""
        clusters = []
        available_passagers = self.passagers.copy()
        random.shuffle(available_passagers)
        
        while len(available_passagers) >= 2:
            # Start a new cluster with random passenger
            cluster = [available_passagers.pop(0)]
            
            # Try to add compatible passengers
            i = 0
            while i < len(available_passagers) and len(cluster) < self.conducteur.capacite:
                candidate = available_passagers[i]
                
                # Check if candidate is compatible with cluster
                if self._is_compatible(candidate, cluster):
                    cluster.append(available_passagers.pop(i))
                else:
                    i += 1
            
            # Only add if cluster has at least 2 passengers
            if len(cluster) >= 2:
                clusters.append(cluster)
            elif len(cluster) == 1:
                # Return the single passenger back to available
                available_passagers.append(cluster[0])
                break
        
        return clusters
    
    def _is_compatible(self, candidate: Passager, cluster: List[Passager]) -> bool:
        """Check if a passenger is compatible with a cluster"""
        # Check destination proximity
        for p in cluster:
            if distance_grille(candidate.pos_arrivee, p.pos_arrivee) > self.R_dest:
                return False
        
        # Check departure proximity
        for p in cluster:
            if distance_grille(candidate.pos_depart, p.pos_depart) > self.R_depart:
                return False
        
        return True
    
    def calculate_fitness(self, chromosome: Dict) -> float:
        """
        Calculate fitness of a chromosome (lower is better)
        
        Fitness components:
        1. Total route distance
        2. Number of passengers served (maximize)
        3. Cluster quality (compactness)
        """
        clusters = chromosome['clusters']
        route = chromosome['route']
        
        if not clusters:
            return float('inf')
        
        # Component 1: Route distance
        total_distance = 0
        current_pos = self.conducteur.position
        
        for cluster_idx in route:
            cluster = clusters[cluster_idx]
            # Calculate cluster pickup centroid
            pickup_centroid = calculer_centroide_grille([p.pos_depart for p in cluster])
            
            # Distance from current position to pickup
            total_distance += distance_grille(current_pos, pickup_centroid)
            current_pos = pickup_centroid
        
        # Component 2: Number of passengers served (negative to minimize)
        total_passengers = sum(len(cluster) for cluster in clusters)
        passenger_bonus = -total_passengers * 50  # Heavily reward more passengers
        
        # Component 3: Cluster compactness penalty
        compactness_penalty = 0
        for cluster in clusters:
            # Departure spread
            departure_positions = [p.pos_depart for p in cluster]
            departure_centroid = calculer_centroide_grille(departure_positions)
            departure_spread = sum(distance_grille(p, departure_centroid) for p in departure_positions)
            
            # Destination spread
            destination_positions = [p.pos_arrivee for p in cluster]
            destination_centroid = calculer_centroide_grille(destination_positions)
            destination_spread = sum(distance_grille(p, destination_centroid) for p in destination_positions)
            
            compactness_penalty += departure_spread + destination_spread
        
        # Component 4: Capacity utilization bonus
        capacity_bonus = 0
        for cluster in clusters:
            utilization = len(cluster) / self.conducteur.capacite
            capacity_bonus -= utilization * 20  # Reward better capacity usage
        
        fitness = total_distance + passenger_bonus + compactness_penalty * 0.5 + capacity_bonus
        
        return fitness
    
    def tournament_selection(self, population: List[Tuple[Dict, float]]) -> Dict:
        """Select parent using tournament selection"""
        tournament = random.sample(population, self.tournament_size)
        return min(tournament, key=lambda x: x[1])[0]
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """
        Crossover two parents to create offspring
        
        Strategy: 
        - Inherit some clusters from parent1, some from parent2
        - Rebuild route optimally for the new cluster set
        """
        # Combine clusters from both parents
        all_clusters = parent1['clusters'] + parent2['clusters']
        
        # Remove duplicate passengers and create new valid clusters
        used_passengers = set()
        new_clusters = []
        
        for cluster in all_clusters:
            new_cluster = [p for p in cluster if p.id not in used_passengers]
            if len(new_cluster) >= 2:
                # Verify cluster is still valid
                valid = True
                for i in range(len(new_cluster)):
                    for j in range(i + 1, len(new_cluster)):
                        if distance_grille(new_cluster[i].pos_arrivee, new_cluster[j].pos_arrivee) > self.R_dest:
                            valid = False
                            break
                        if distance_grille(new_cluster[i].pos_depart, new_cluster[j].pos_depart) > self.R_depart:
                            valid = False
                            break
                    if not valid:
                        break
                
                if valid and len(new_cluster) <= self.conducteur.capacite:
                    new_clusters.append(new_cluster)
                    for p in new_cluster:
                        used_passengers.add(p.id)
        
        # If no valid clusters, create random ones
        if not new_clusters:
            remaining = [p for p in self.passagers if p.id not in used_passengers]
            if len(remaining) >= 2:
                new_clusters = self._create_random_clusters_from_list(remaining)
        
        # Create route: use order preference from better parent
        if new_clusters:
            route = list(range(len(new_clusters)))
            # Use greedy nearest neighbor as base
            route = self._greedy_route(new_clusters)
        else:
            route = []
        
        return {
            'clusters': new_clusters,
            'route': route
        }
    
    def _create_random_clusters_from_list(self, passengers: List[Passager]) -> List[List[Passager]]:
        """Create random clusters from a specific list of passengers"""
        clusters = []
        available = passengers.copy()
        random.shuffle(available)
        
        while len(available) >= 2:
            cluster = [available.pop(0)]
            
            i = 0
            while i < len(available) and len(cluster) < self.conducteur.capacite:
                if self._is_compatible(available[i], cluster):
                    cluster.append(available.pop(i))
                else:
                    i += 1
            
            if len(cluster) >= 2:
                clusters.append(cluster)
            else:
                break
        
        return clusters
    
    def _greedy_route(self, clusters: List[List[Passager]]) -> List[int]:
        """Create a greedy nearest-neighbor route through clusters"""
        if not clusters:
            return []
        
        unvisited = set(range(len(clusters)))
        route = []
        current_pos = self.conducteur.position
        
        while unvisited:
            nearest = min(unvisited, key=lambda idx: distance_grille(
                current_pos,
                calculer_centroide_grille([p.pos_depart for p in clusters[idx]])
            ))
            route.append(nearest)
            unvisited.remove(nearest)
            current_pos = calculer_centroide_grille([p.pos_depart for p in clusters[nearest]])
        
        return route
    
    def mutate(self, chromosome: Dict) -> Dict:
        """
        Mutate a chromosome
        
        Mutation operations:
        1. Swap two positions in route
        2. Merge two clusters (if capacity allows)
        3. Split a cluster
        4. Move a passenger between compatible clusters
        """
        mutated = {
            'clusters': [cluster.copy() for cluster in chromosome['clusters']],
            'route': chromosome['route'].copy()
        }
        
        mutation_type = random.random()
        
        if mutation_type < 0.4 and len(mutated['route']) >= 2:
            # Route swap mutation
            i, j = random.sample(range(len(mutated['route'])), 2)
            mutated['route'][i], mutated['route'][j] = mutated['route'][j], mutated['route'][i]
        
        elif mutation_type < 0.6 and len(mutated['clusters']) >= 2:
            # Merge clusters mutation
            i, j = random.sample(range(len(mutated['clusters'])), 2)
            merged = mutated['clusters'][i] + mutated['clusters'][j]
            
            if len(merged) <= self.conducteur.capacite:
                # Check if merged cluster is valid
                valid = True
                for p1 in merged:
                    for p2 in merged:
                        if p1.id != p2.id:
                            if distance_grille(p1.pos_arrivee, p2.pos_arrivee) > self.R_dest:
                                valid = False
                            if distance_grille(p1.pos_depart, p2.pos_depart) > self.R_depart:
                                valid = False
                
                if valid:
                    mutated['clusters'][i] = merged
                    mutated['clusters'].pop(j)
                    # Update route
                    mutated['route'] = [r if r < j else r - 1 for r in mutated['route'] if r != j]
        
        elif mutation_type < 0.8 and mutated['clusters']:
            # Split cluster mutation
            cluster_idx = random.randint(0, len(mutated['clusters']) - 1)
            cluster = mutated['clusters'][cluster_idx]
            
            if len(cluster) >= 4:  # Only split if we can make two valid clusters
                split_point = len(cluster) // 2
                random.shuffle(cluster)
                cluster1 = cluster[:split_point]
                cluster2 = cluster[split_point:]
                
                if len(cluster1) >= 2 and len(cluster2) >= 2:
                    mutated['clusters'][cluster_idx] = cluster1
                    mutated['clusters'].append(cluster2)
                    mutated['route'].append(len(mutated['clusters']) - 1)
        
        else:
            # Reverse segment mutation (for route)
            if len(mutated['route']) >= 2:
                i, j = sorted(random.sample(range(len(mutated['route'])), 2))
                mutated['route'][i:j+1] = reversed(mutated['route'][i:j+1])
        
        return mutated
    
    def solve(self) -> Tuple[List[Dict], List[str], Dict[str, Dict[str, int]]]:
        """
        Run the genetic algorithm
        
        Returns:
            Tuple of (groupes, trajet_ordre, temps_trajet)
        """
        # Initialize population
        if self.verbose:
            print(f"Initializing population of {self.population_size} chromosomes...")
        
        self.population = [self.create_chromosome() for _ in range(self.population_size)]
        
        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            population_with_fitness = [(chrom, self.calculate_fitness(chrom)) for chrom in self.population]
            population_with_fitness.sort(key=lambda x: x[1])
            
            # Track best solution
            current_best_fitness = population_with_fitness[0][1]
            if current_best_fitness < self.best_fitness:
                self.best_fitness = current_best_fitness
                self.best_solution = population_with_fitness[0][0]
            
            self.fitness_history.append(current_best_fitness)
            
            if self.verbose and generation % 20 == 0:
                best_passengers = sum(len(c) for c in population_with_fitness[0][0]['clusters'])
                print(f"Generation {generation}: Best Fitness = {current_best_fitness:.2f}, "
                      f"Passengers = {best_passengers}")
            
            # Selection and reproduction
            new_population = []
            
            # Elitism: keep best solutions
            for i in range(self.elite_size):
                new_population.append(population_with_fitness[i][0])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = self.tournament_selection(population_with_fitness)
                parent2 = self.tournament_selection(population_with_fitness)
                
                # Crossover
                offspring = self.crossover(parent1, parent2)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    offspring = self.mutate(offspring)
                
                new_population.append(offspring)
            
            self.population = new_population
        
        # Final evaluation
        population_with_fitness = [(chrom, self.calculate_fitness(chrom)) for chrom in self.population]
        population_with_fitness.sort(key=lambda x: x[1])
        
        if population_with_fitness[0][1] < self.best_fitness:
            self.best_solution = population_with_fitness[0][0]
            self.best_fitness = population_with_fitness[0][1]
        
        if self.verbose:
            best_passengers = sum(len(c) for c in self.best_solution['clusters'])
            print(f"\n=== Genetic Algorithm Complete ===")
            print(f"Best Fitness: {self.best_fitness:.2f}")
            print(f"Total Passengers Served: {best_passengers}")
            print(f"Number of Clusters: {len(self.best_solution['clusters'])}")
        
        # Convert best solution to expected format
        return self._convert_to_output_format(self.best_solution)
    
    def _convert_to_output_format(self, chromosome: Dict) -> Tuple[List[Dict], List[str], Dict[str, Dict[str, int]]]:
        """Convert chromosome to standard output format"""
        clusters = chromosome['clusters']
        route = chromosome['route']
        
        # Create groupes format
        groupes = []
        for idx, cluster_idx in enumerate(route):
            cluster = clusters[cluster_idx]
            groupes.append({
                'passagers': cluster,
                'taille': len(cluster),
                'centre_depart': calculer_centroide_grille([p.pos_depart for p in cluster]),
                'centre_arrivee': calculer_centroide_grille([p.pos_arrivee for p in cluster])
            })
        
        # Create TRAJET_ORDRE
        trajet_ordre = ["Depart"]
        for i in range(len(groupes)):
            trajet_ordre.append(f"R{i + 1}")
        
        # Create TEMPS_TRAJET_MIN
        temps_trajet = {}
        
        if len(trajet_ordre) > 1:
            # Time from Depart to first pickup
            first_centre = groupes[0]['centre_depart']
            temps_trajet["Depart"] = {trajet_ordre[1]: round(distance_grille(self.conducteur.position, first_centre))}
            
            # Time between consecutive pickups
            for i in range(len(groupes) - 1):
                current_key = trajet_ordre[i + 1]
                next_key = trajet_ordre[i + 2]
                current_centre = groupes[i]['centre_depart']
                next_centre = groupes[i + 1]['centre_depart']
                
                if current_key not in temps_trajet:
                    temps_trajet[current_key] = {}
                temps_trajet[current_key][next_key] = round(distance_grille(current_centre, next_centre))
        
        return groupes, trajet_ordre, temps_trajet


def solve_genetic(
    passagers: List[Passager],
    conducteur: Conducteur,
    R_dest: float = 5.0,
    R_depart: float = 5.0,
    population_size: int = 100,
    generations: int = 200,
    mutation_rate: float = 0.15,
    verbose: bool = True
) -> Tuple[List[str], Dict[str, Dict[str, int]], List[Dict]]:
    """
    Convenience function to solve carpooling with genetic algorithm
    
    Returns:
        Tuple (TRAJET_ORDRE, TEMPS_TRAJET_MIN, groupes)
    """
    solver = GeneticCarpoolingSolver(
        passagers=passagers,
        conducteur=conducteur,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        R_dest=R_dest,
        R_depart=R_depart,
        verbose=verbose
    )
    
    groupes, trajet_ordre, temps_trajet = solver.solve()
    
    return trajet_ordre, temps_trajet, groupes

"""
Test Phase 2: Clustering + TSP (Exact vs Heuristic)
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.phase2_integrator import (
    phase2_solve,
    generate_affectations_par_point,
    load_phase2_json,
    export_phase2_json
)


class TestPhase2Exact:
    """Tests pour la méthode exacte"""
    
    def setup_method(self):
        """Préparation des données de test"""
        self.passagers = [
            Passager(id=1, pos_depart=(0, 0), pos_arrivee=(10, 10)),
            Passager(id=2, pos_depart=(1, 1), pos_arrivee=(11, 11)),
            Passager(id=3, pos_depart=(50, 50), pos_arrivee=(60, 60)),
            Passager(id=4, pos_depart=(51, 51), pos_arrivee=(61, 61)),
        ]
        self.conducteur = Conducteur(position=(0, 0), capacite=2)
    
    def test_phase2_exact_returns_valid_trajet(self):
        """Vérifie que trajet commence par Depart"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="exact"
        )
        
        assert isinstance(trajet, list)
        assert len(trajet) > 0
        assert trajet[0] == "Depart"
        assert all(isinstance(p, str) for p in trajet)
    
    def test_phase2_exact_temps_structure(self):
        """Vérifie la structure de TEMPS_TRAJET_MIN"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="exact"
        )
        
        assert isinstance(temps, dict)
        assert "Depart" in temps
        assert isinstance(temps["Depart"], dict)
        
        # Tous les temps doivent être des entiers positifs
        for point, next_points in temps.items():
            for next_p, travel_time in next_points.items():
                assert isinstance(travel_time, int)
                assert travel_time >= 0
    
    def test_phase2_exact_groupes_formation(self):
        """Vérifie que des groupes sont formés"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="exact"
        )
        
        assert len(groupes) > 0
        for groupe in groupes:
            assert 'passagers' in groupe
            assert 'centre_depart' in groupe
            assert 'centre_arrivee' in groupe
            assert 2 <= len(groupe['passagers']) <= self.conducteur.capacite


class TestPhase2Heuristic:
    """Tests pour la méthode heuristique"""
    
    def setup_method(self):
        """Préparation des données de test"""
        self.passagers = [
            Passager(id=1, pos_depart=(0, 0), pos_arrivee=(10, 10)),
            Passager(id=2, pos_depart=(1, 1), pos_arrivee=(11, 11)),
            Passager(id=3, pos_depart=(50, 50), pos_arrivee=(60, 60)),
            Passager(id=4, pos_depart=(51, 51), pos_arrivee=(61, 61)),
        ]
        self.conducteur = Conducteur(position=(0, 0), capacite=2)
    
    def test_phase2_heuristic_returns_valid_trajet(self):
        """Vérifie que trajet commence par Depart"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="heuristic"
        )
        
        assert isinstance(trajet, list)
        assert len(trajet) > 0
        assert trajet[0] == "Depart"
        assert all(isinstance(p, str) for p in trajet)
    
    def test_phase2_heuristic_temps_structure(self):
        """Vérifie la structure de TEMPS_TRAJET_MIN"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="heuristic"
        )
        
        assert isinstance(temps, dict)
        assert "Depart" in temps
        
        for point, next_points in temps.items():
            for next_p, travel_time in next_points.items():
                assert isinstance(travel_time, int)
                assert travel_time >= 0
    
    def test_phase2_heuristic_groupes_formation(self):
        """Vérifie que des groupes sont formés"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="heuristic"
        )
        
        assert len(groupes) > 0
        for groupe in groupes:
            assert 'passagers' in groupe
            assert 2 <= len(groupe['passagers']) <= self.conducteur.capacite


class TestAffectationsGeneration:
    """Tests pour la génération des affectations"""
    
    def setup_method(self):
        """Préparation des données de test"""
        self.passagers = [
            Passager(id=1, pos_depart=(0, 0), pos_arrivee=(10, 10)),
            Passager(id=2, pos_depart=(1, 1), pos_arrivee=(11, 11)),
            Passager(id=3, pos_depart=(50, 50), pos_arrivee=(60, 60)),
        ]
        self.conducteur = Conducteur(position=(0, 0), capacite=2)
    
    def test_generate_affectations_par_point(self):
        """Vérifie la génération des affectations"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="heuristic"
        )
        
        affectations = generate_affectations_par_point(groupes, trajet)
        
        assert isinstance(affectations, dict)
        assert len(affectations) > 0
        
        # Chaque clé doit être dans trajet
        for point in affectations.keys():
            assert point in trajet
        
        # Chaque valeur doit être une liste
        for point, passengers in affectations.items():
            assert isinstance(passengers, list)
            assert len(passengers) > 0


class TestPhase2Export:
    """Tests pour l'export et import JSON"""
    
    def setup_method(self):
        """Préparation des données de test"""
        self.passagers = [
            Passager(id=1, pos_depart=(0, 0), pos_arrivee=(10, 10)),
            Passager(id=2, pos_depart=(1, 1), pos_arrivee=(11, 11)),
        ]
        self.conducteur = Conducteur(position=(0, 0), capacite=2)
        self.test_file = "/tmp/test_phase2_export.json"
    
    def test_export_and_load_json(self):
        """Vérifie l'export et import JSON"""
        trajet, temps, groupes = phase2_solve(
            self.passagers, self.conducteur, R_dest=15, R_depart=15, method="heuristic"
        )
        
        affectations = generate_affectations_par_point(groupes, trajet)
        
        # Export
        export_phase2_json(
            self.test_file,
            trajet,
            affectations,
            temps,
            Z_optimal=len(self.passagers),
            metadata={"test": True}
        )
        
        assert os.path.exists(self.test_file)
        
        # Load
        loaded_trajet, loaded_affect, loaded_temps, z_opt = load_phase2_json(self.test_file)
        
        assert loaded_trajet == trajet
        assert loaded_affect == affectations
        assert z_opt == len(self.passagers)
        
        # Cleanup
        os.remove(self.test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

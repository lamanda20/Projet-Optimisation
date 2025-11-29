import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.exact.clustering_exact import phase1_clustering_double
from algorithms.exact.selection_exact import selection_exact
from algorithms.exact.ramassage_exact import ramassage_exact
from algorithms.heuristic.ramassage_heuristic import ramassage_heuristic

class InterfaceOptimisation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Projet Optimisation - Interface")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        self.root.state('zoomed')  # Maximiser automatiquement
        
        self.passagers = []
        self.conducteur = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configuration du scrolling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Canvas et scrollbar pour le scrolling
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principal dans le scrollable_frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Placer canvas et scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind mousewheel pour le scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Section Conducteur
        ttk.Label(main_frame, text="CONDUCTEUR", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        ttk.Label(main_frame, text="Position X (0-99):").grid(row=1, column=0, sticky=tk.W)
        self.conducteur_x = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.conducteur_x, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(main_frame, text="Position Y (0-99):").grid(row=1, column=2, sticky=tk.W)
        self.conducteur_y = tk.StringVar(value="0")
        ttk.Entry(main_frame, textvariable=self.conducteur_y, width=10).grid(row=1, column=3, padx=5)
        
        ttk.Label(main_frame, text="Capacité:").grid(row=2, column=0, sticky=tk.W)
        self.capacite = tk.StringVar(value="8")
        ttk.Entry(main_frame, textvariable=self.capacite, width=10).grid(row=2, column=1, padx=5)
        
        # Section Passagers
        ttk.Label(main_frame, text="PASSAGERS", font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=4, pady=(20,5))
        
        # Formulaire ajout passager
        passager_frame = ttk.LabelFrame(main_frame, text="Ajouter un passager", padding="5")
        passager_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(passager_frame, text="Départ X (0-99):").grid(row=0, column=0)
        self.depart_x = tk.StringVar()
        depart_x_entry = ttk.Entry(passager_frame, textvariable=self.depart_x, width=8)
        depart_x_entry.grid(row=0, column=1, padx=2)
        
        ttk.Label(passager_frame, text="Y (0-99):").grid(row=0, column=2)
        self.depart_y = tk.StringVar()
        depart_y_entry = ttk.Entry(passager_frame, textvariable=self.depart_y, width=8)
        depart_y_entry.grid(row=0, column=3, padx=2)
        
        ttk.Label(passager_frame, text="Arrivée X (0-99):").grid(row=0, column=4)
        self.arrivee_x = tk.StringVar()
        arrivee_x_entry = ttk.Entry(passager_frame, textvariable=self.arrivee_x, width=8)
        arrivee_x_entry.grid(row=0, column=5, padx=2)
        
        ttk.Label(passager_frame, text="Y (0-99):").grid(row=0, column=6)
        self.arrivee_y = tk.StringVar()
        arrivee_y_entry = ttk.Entry(passager_frame, textvariable=self.arrivee_y, width=8)
        arrivee_y_entry.grid(row=0, column=7, padx=2)
        
        ttk.Button(passager_frame, text="Ajouter", command=self.ajouter_passager).grid(row=0, column=8, padx=10)
        
        # Liste des passagers
        self.liste_passagers = tk.Listbox(main_frame, height=6)
        self.liste_passagers.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(main_frame, text="Supprimer", command=self.supprimer_passager).grid(row=5, column=3, padx=5)
        
        # Paramètres
        param_frame = ttk.LabelFrame(main_frame, text="Paramètres", padding="5")
        param_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(param_frame, text="R_dest:").grid(row=0, column=0)
        self.r_dest = tk.StringVar(value="15.0")
        ttk.Entry(param_frame, textvariable=self.r_dest, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="R_depart:").grid(row=0, column=2)
        self.r_depart = tk.StringVar(value="20.0")
        ttk.Entry(param_frame, textvariable=self.r_depart, width=8).grid(row=0, column=3, padx=5)
        
        # Choix méthode
        ttk.Label(param_frame, text="Méthode:").grid(row=0, column=4)
        self.methode = tk.StringVar(value="exact")
        ttk.Radiobutton(param_frame, text="Exact", variable=self.methode, value="exact").grid(row=0, column=5)
        ttk.Radiobutton(param_frame, text="Heuristique", variable=self.methode, value="heuristique").grid(row=0, column=6)
        
        # Bouton calcul
        ttk.Button(main_frame, text="CALCULER OPTIMISATION", command=self.calculer, 
                  style="Accent.TButton").grid(row=7, column=0, columnspan=4, pady=20)
        
        # Info grille
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="5")
        info_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(info_frame, text="⚠️ Grille 100x100: Coordonnées de 0 à 99", 
                 foreground="blue").grid(row=0, column=0, sticky=tk.W)
        
        # Zone résultats
        ttk.Label(main_frame, text="RÉSULTATS", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=4)
        
        self.resultats = scrolledtext.ScrolledText(main_frame, height=12, width=80)
        self.resultats.grid(row=10, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Boutons exemple
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Charger Exemple", command=self.charger_exemple).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Effacer Tout", command=self.effacer_tout).pack(side=tk.LEFT, padx=5)
    
    def ajouter_passager(self):
        try:
            depart_x = int(self.depart_x.get())
            depart_y = int(self.depart_y.get())
            arrivee_x = int(self.arrivee_x.get())
            arrivee_y = int(self.arrivee_y.get())
            
            # Validation grille 100x100
            if not (0 <= depart_x <= 99 and 0 <= depart_y <= 99):
                messagebox.showerror("Erreur", "Coordonnées de départ doivent être entre 0 et 99")
                return
            
            if not (0 <= arrivee_x <= 99 and 0 <= arrivee_y <= 99):
                messagebox.showerror("Erreur", "Coordonnées d'arrivée doivent être entre 0 et 99")
                return
            
            passager_id = len(self.passagers) + 1
            passager = Passager(passager_id, (depart_x, depart_y), (arrivee_x, arrivee_y))
            self.passagers.append(passager)
            
            self.liste_passagers.insert(tk.END, f"P{passager_id}: ({depart_x},{depart_y}) -> ({arrivee_x},{arrivee_y})")
            
            # Effacer les champs
            self.depart_x.set("")
            self.depart_y.set("")
            self.arrivee_x.set("")
            self.arrivee_y.set("")
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des coordonnées valides (nombres entiers 0-99)")
    
    def supprimer_passager(self):
        selection = self.liste_passagers.curselection()
        if selection:
            index = selection[0]
            self.liste_passagers.delete(index)
            del self.passagers[index]
            
            # Réorganiser les IDs
            for i, p in enumerate(self.passagers):
                p.id = i + 1
            
            # Recharger la liste
            self.liste_passagers.delete(0, tk.END)
            for p in self.passagers:
                self.liste_passagers.insert(tk.END, f"P{p.id}: {p.pos_depart} -> {p.pos_arrivee}")
    
    def charger_exemple(self):
        self.effacer_tout()
        
        # Exemple COMPLET: 16 passagers en 5 zones pour test approfondi
        exemples = [
            # Zone 1: Nord-Ouest (5-10) - 4 passagers
            Passager(1, (5, 5), (80, 80)),
            Passager(2, (8, 7), (82, 81)), 
            Passager(3, (6, 9), (81, 83)),
            Passager(4, (9, 6), (83, 79)),
            
            # Zone 2: Nord-Est (15-20) - 3 passagers  
            Passager(5, (15, 15), (85, 85)),
            Passager(6, (18, 17), (87, 86)),
            Passager(7, (16, 19), (86, 88)),
            
            # Zone 3: Centre (25-30) - 3 passagers
            Passager(8, (25, 25), (78, 78)),
            Passager(9, (28, 27), (79, 77)),
            Passager(10, (26, 29), (77, 80)),
            
            # Zone 4: Sud-Ouest (35-40) - 3 passagers
            Passager(11, (35, 35), (75, 75)),
            Passager(12, (38, 37), (76, 74)),
            Passager(13, (36, 39), (74, 76)),
            
            # Zone 5: Sud-Est (45-50) - 3 passagers
            Passager(14, (45, 45), (70, 70)),
            Passager(15, (48, 47), (71, 69)),
            Passager(16, (46, 49), (69, 71)),
        ]
        
        self.passagers = exemples
        for p in self.passagers:
            self.liste_passagers.insert(tk.END, f"P{p.id}: {p.pos_depart} -> {p.pos_arrivee}")
    
    def effacer_tout(self):
        self.passagers = []
        self.liste_passagers.delete(0, tk.END)
        self.resultats.delete(1.0, tk.END)
    
    def calculer(self):
        try:
            # Vérifications
            if not self.passagers:
                messagebox.showerror("Erreur", "Ajoutez au moins un passager")
                return
            
            # Validation conducteur
            conducteur_x = int(self.conducteur_x.get())
            conducteur_y = int(self.conducteur_y.get())
            
            if not (0 <= conducteur_x <= 99 and 0 <= conducteur_y <= 99):
                messagebox.showerror("Erreur", "Position conducteur doit être entre 0 et 99")
                return
            
            # Créer conducteur
            conducteur_pos = (conducteur_x, conducteur_y)
            capacite = int(self.capacite.get())
            conducteur = Conducteur(conducteur_pos, capacite)
            
            # Paramètres
            r_dest = float(self.r_dest.get())
            r_depart = float(self.r_depart.get())
            
            # Effacer résultats précédents
            self.resultats.delete(1.0, tk.END)
            
            # Calcul
            self.resultats.insert(tk.END, "=== CALCUL EN COURS ===\n\n")
            self.resultats.insert(tk.END, f"Passagers: {len(self.passagers)}\n")
            self.resultats.insert(tk.END, f"Conducteur: {conducteur_pos}, capacité={capacite}\n")
            self.resultats.insert(tk.END, f"Paramètres: R_dest={r_dest}, R_depart={r_depart}\n\n")
            
            # Clustering avec vérification
            groupes = phase1_clustering_double(self.passagers, conducteur, r_dest, r_depart)
            self.resultats.insert(tk.END, f"--- CLUSTERING ---\n")
            self.resultats.insert(tk.END, f"Groupes valides: {len(groupes)}\n")
            
            # Si aucun groupe valide, ajuster les paramètres automatiquement
            if not groupes:
                self.resultats.insert(tk.END, "AUCUN GROUPE TROUVÉ! Ajustement automatique...\n")
                
                # Augmenter les rayons progressivement
                for multiplier in [2, 3, 5, 10]:
                    new_r_dest = r_dest * multiplier
                    new_r_depart = r_depart * multiplier
                    groupes = phase1_clustering_double(self.passagers, conducteur, new_r_dest, new_r_depart)
                    
                    if groupes:
                        self.resultats.insert(tk.END, f"Groupes trouvés avec R_dest={new_r_dest}, R_depart={new_r_depart}\n")
                        break
                
                # Si toujours rien, créer un groupe artificiel avec tous les passagers compatibles
                if not groupes and len(self.passagers) >= 2:
                    # Prendre les 2 premiers passagers minimum
                    taille_groupe = min(len(self.passagers), capacite)
                    passagers_groupe = self.passagers[:taille_groupe]
                    
                    from utils.centroide import calculer_centroide_grille
                    centre_depart = calculer_centroide_grille([p.pos_depart for p in passagers_groupe])
                    centre_arrivee = calculer_centroide_grille([p.pos_arrivee for p in passagers_groupe])
                    
                    groupes = [{
                        'passagers': passagers_groupe,
                        'taille': taille_groupe,
                        'centre_depart': centre_depart,
                        'centre_arrivee': centre_arrivee
                    }]
                    
                    self.resultats.insert(tk.END, f"Groupe artificiel créé avec {taille_groupe} passagers\n")
            
            for i, groupe in enumerate(groupes):
                ids = [p.id for p in groupe['passagers']]
                self.resultats.insert(tk.END, f"  Groupe {i+1}: {ids} ({groupe['taille']} passagers)\n")
            
            # Sélection avec garantie
            groupe_optimal = selection_exact(groupes, conducteur)
            
            # Si pas de groupe optimal, prendre le premier disponible
            if not groupe_optimal and groupes:
                groupe_optimal = groupes[0]['passagers']
                self.resultats.insert(tk.END, f"\n--- SELECTION (FORCÉE) ---\n")
                self.resultats.insert(tk.END, f"Premier groupe sélectionné: {[p.id for p in groupe_optimal]}\n")
            elif groupe_optimal:
                self.resultats.insert(tk.END, f"\n--- SELECTION ---\n")
                self.resultats.insert(tk.END, f"Groupe optimal: {[p.id for p in groupe_optimal]}\n")
            
            # Si toujours pas de groupe, utiliser tous les passagers
            if not groupe_optimal:
                if len(self.passagers) == 1:
                    groupe_optimal = self.passagers
                    self.resultats.insert(tk.END, f"\n--- SELECTION (PASSAGER UNIQUE) ---\n")
                    self.resultats.insert(tk.END, f"Passager unique sélectionné: {[p.id for p in groupe_optimal]}\n")
                else:
                    self.resultats.insert(tk.END, "\nERREUR: Impossible de former un groupe!\n")
                    return
            
            # Ramassage avec garantie
            methode = self.methode.get()
            self.resultats.insert(tk.END, f"\n--- RAMASSAGE ({methode.upper()}) ---\n")
            
            if methode == "exact":
                points = ramassage_exact(groupe_optimal)
            else:
                points = ramassage_heuristic(groupe_optimal)
            
            # Vérification que les points ne sont pas vides
            if not points:
                # Créer un point de ramassage par défaut
                if groupe_optimal:
                    points = [{
                        'point_ramassage': groupe_optimal[0].pos_depart,
                        'passagers': groupe_optimal
                    }]
                    self.resultats.insert(tk.END, "Point de ramassage par défaut créé\n")
            
            self.resultats.insert(tk.END, f"Points de ramassage: {len(points)}\n\n")
            
            for i, point in enumerate(points):
                ids = [p.id for p in point['passagers']]
                self.resultats.insert(tk.END, f"Point {i+1}: {point['point_ramassage']} -> Passagers {ids}\n")
            
            self.resultats.insert(tk.END, f"\n=== CALCUL TERMINÉ ===\n")
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de saisie: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de calcul: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = InterfaceOptimisation()
    app.run()
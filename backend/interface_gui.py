import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
from models.Passager import Passager
from models.Conducteur import Conducteur
from algorithms.exact.clustering_exact import phase1_clustering_double
from algorithms.exact.selection_exact import selection_exact
from algorithms.exact.ramassage_exact import ramassage_exact
from algorithms.heuristic.ramassage_heuristic import ramassage_heuristic
from pickup_scheduler import compute_schedule, determine_stop_point_per_passenger, validate_inputs

# Optional map widget
try:
    from tkintermapview import TkinterMapView

    MAP_AVAILABLE = True
except Exception as e:
    print(f"Erreur lors de l'importation de tkintermapview : {e}")
    TkinterMapView = None
    MAP_AVAILABLE = False

from utils.map_utils import grid_to_latlon, latlon_to_grid


class InterfaceOptimisation:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Projet Optimisation - Interface Moderne")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        self.passagers = []
        self.conducteur = None

        # Map related
        self.map_widget = None
        self.map_markers = {}
        self.conducteur_marker = None
        self.route_lines = []
        self.map_bbox = {'lat_min': 31.5, 'lat_max': 31.7, 'lon_min': -8.1, 'lon_max': -7.9}
        self.map_available = MAP_AVAILABLE

        # Animation variables
        self.car_marker = None
        self.animation_positions = []
        self.animation_index = 0
        self.animation_steps = 30
        self.current_step = 0
        self.start_pos = None
        self.end_pos = None

        self.setup_ui()

    def setup_ui(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Canvas avec scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Section Conducteur avec style amélioré
        conducteur_frame = ttk.LabelFrame(main_frame, text="🚗 CONDUCTEUR", padding="10")
        conducteur_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(conducteur_frame, text="Position X (0-99):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.conducteur_x = tk.StringVar(value="0")
        conducteur_x_entry = ttk.Entry(conducteur_frame, textvariable=self.conducteur_x, width=10)
        conducteur_x_entry.grid(row=0, column=1, padx=5)
        conducteur_x_entry.bind('<FocusOut>', lambda e: self.update_conducteur_on_map())

        ttk.Label(conducteur_frame, text="Position Y (0-99):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.conducteur_y = tk.StringVar(value="0")
        conducteur_y_entry = ttk.Entry(conducteur_frame, textvariable=self.conducteur_y, width=10)
        conducteur_y_entry.grid(row=0, column=3, padx=5)
        conducteur_y_entry.bind('<FocusOut>', lambda e: self.update_conducteur_on_map())

        ttk.Label(conducteur_frame, text="Capacité:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.capacite = tk.StringVar(value="8")
        ttk.Entry(conducteur_frame, textvariable=self.capacite, width=10).grid(row=0, column=5, padx=5)

        ttk.Button(conducteur_frame, text="📍 Placer sur carte",
                   command=self.update_conducteur_on_map).grid(row=0, column=6, padx=10)

        # Section Passagers
        passager_frame = ttk.LabelFrame(main_frame, text="👥 PASSAGERS", padding="10")
        passager_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        # Formulaire ajout passager
        form_frame = ttk.Frame(passager_frame)
        form_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(form_frame, text="Départ X:").grid(row=0, column=0, padx=2)
        self.depart_x = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.depart_x, width=8).grid(row=0, column=1, padx=2)

        ttk.Label(form_frame, text="Y:").grid(row=0, column=2, padx=2)
        self.depart_y = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.depart_y, width=8).grid(row=0, column=3, padx=2)

        ttk.Label(form_frame, text="Arrivée X:").grid(row=0, column=4, padx=2)
        self.arrivee_x = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.arrivee_x, width=8).grid(row=0, column=5, padx=2)

        ttk.Label(form_frame, text="Y:").grid(row=0, column=6, padx=2)
        self.arrivee_y = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.arrivee_y, width=8).grid(row=0, column=7, padx=2)

        ttk.Button(form_frame, text="➕ Ajouter", command=self.ajouter_passager).grid(row=0, column=8, padx=10)

        # Liste des passagers
        self.liste_passagers = tk.Listbox(passager_frame, height=6)
        self.liste_passagers.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(passager_frame, text="🗑️ Supprimer",
                   command=self.supprimer_passager).grid(row=1, column=3, padx=5)

        # Carte interactive
        map_frame = ttk.LabelFrame(main_frame, text="🗺️ CARTE INTERACTIVE", padding="10")
        map_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        if self.map_available and TkinterMapView is not None:
            try:
                self.map_widget = TkinterMapView(map_frame, width=1100, height=400, corner_radius=10)
                center_lat = (self.map_bbox['lat_min'] + self.map_bbox['lat_max']) / 2
                center_lon = (self.map_bbox['lon_min'] + self.map_bbox['lon_max']) / 2
                self.map_widget.set_position(center_lat, center_lon)
                self.map_widget.set_zoom(12)
                self.map_widget.pack(fill=tk.BOTH, expand=True, pady=5)

                # Clic sur la carte pour ajouter point de départ
                def _on_map_click(coords):
                    lat, lon = coords
                    gx, gy = latlon_to_grid(lat, lon, self.map_bbox)
                    self.depart_x.set(str(gx))
                    self.depart_y.set(str(gy))

                self.map_widget.add_left_click_map_command(_on_map_click)

                # Boutons de contrôle carte
                btn_frame = ttk.Frame(map_frame)
                btn_frame.pack(anchor=tk.W, pady=5)

                ttk.Button(btn_frame, text="🔄 Actualiser",
                           command=self.refresh_all_map_elements).pack(side=tk.LEFT, padx=3)
                ttk.Button(btn_frame, text="🧹 Effacer lignes",
                           command=self.clear_route_lines).pack(side=tk.LEFT, padx=3)
                ttk.Button(btn_frame, text="🗑️ Tout effacer",
                           command=self.clear_all_map_elements).pack(side=tk.LEFT, padx=3)

            except Exception as e:
                print(f"Erreur initialisation carte : {e}")
                self.map_widget = None
                ttk.Label(map_frame, text="❌ Carte non disponible",
                          foreground="red").pack()
        else:
            ttk.Label(map_frame, text="❌ Carte non disponible. Installez 'tkintermapview'",
                      foreground="red").pack()
            ttk.Button(map_frame, text="ℹ️ Aide",
                       command=self.show_map_install_help).pack(pady=5)

        # Paramètres
        param_frame = ttk.LabelFrame(main_frame, text="⚙️ PARAMÈTRES", padding="10")
        param_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(param_frame, text="R_dest:").grid(row=0, column=0, padx=5)
        self.r_dest = tk.StringVar(value="15.0")
        ttk.Entry(param_frame, textvariable=self.r_dest, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(param_frame, text="R_depart:").grid(row=0, column=2, padx=5)
        self.r_depart = tk.StringVar(value="20.0")
        ttk.Entry(param_frame, textvariable=self.r_depart, width=10).grid(row=0, column=3, padx=5)

        ttk.Label(param_frame, text="Méthode:").grid(row=0, column=4, padx=5)
        self.methode = tk.StringVar(value="exact")
        ttk.Radiobutton(param_frame, text="Exact", variable=self.methode,
                        value="exact").grid(row=0, column=5, padx=5)
        ttk.Radiobutton(param_frame, text="Heuristique", variable=self.methode,
                        value="heuristique").grid(row=0, column=6, padx=5)

        # Bouton calcul
        ttk.Button(main_frame, text="🚀 CALCULER OPTIMISATION", command=self.calculer,
                   style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20)

        # Résultats
        ttk.Label(main_frame, text="📊 RÉSULTATS",
                  font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4)

        self.resultats = scrolledtext.ScrolledText(main_frame, height=12, width=100)
        self.resultats.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # Boutons actions
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="📝 Exemple",
                   command=self.charger_exemple).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Effacer",
                   command=self.effacer_tout).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Export JSON",
                   command=self.exporter_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗺️ Visualiser",
                   command=self.visualiser_trajet).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🎬 Animer",
                   command=self.animer_trajet).pack(side=tk.LEFT, padx=5)

        # Initialiser le conducteur sur la carte
        self.update_conducteur_on_map()

    def update_conducteur_on_map(self):
        """Met à jour la position du conducteur sur la carte"""
        if not self.map_widget:
            return

        try:
            x = int(self.conducteur_x.get())
            y = int(self.conducteur_y.get())

            if not (0 <= x <= 99 and 0 <= y <= 99):
                return

            # Supprimer l'ancien marqueur
            if self.conducteur_marker:
                try:
                    self.conducteur_marker.delete()
                except:
                    pass

            # Ajouter nouveau marqueur
            lat, lon = grid_to_latlon(x, y, self.map_bbox)
            self.conducteur_marker = self.map_widget.set_marker(
                lat, lon,
                text="🚗 Conducteur",
                marker_color_circle="#00FF00",
                marker_color_outside="#006400"
            )

            # Dessiner les lignes vers les passagers
            self.draw_lines_to_passengers()

        except ValueError:
            pass

    def draw_lines_to_passengers(self):
        """Dessine des lignes bleues du conducteur vers tous les passagers"""
        if not self.map_widget or not self.conducteur_marker:
            return

        # Effacer les anciennes lignes
        self.clear_route_lines()

        try:
            conducteur_x = int(self.conducteur_x.get())
            conducteur_y = int(self.conducteur_y.get())
            conducteur_lat, conducteur_lon = grid_to_latlon(conducteur_x, conducteur_y, self.map_bbox)

            # Dessiner une ligne vers chaque passager
            for passager in self.passagers:
                pass_lat, pass_lon = grid_to_latlon(
                    passager.pos_depart[0],
                    passager.pos_depart[1],
                    self.map_bbox
                )

                path = self.map_widget.set_path(
                    [(conducteur_lat, conducteur_lon), (pass_lat, pass_lon)],
                    color="#4A90E2",
                    width=2
                )
                self.route_lines.append(path)

        except Exception as e:
            print(f"Erreur dessin lignes: {e}")

    def clear_route_lines(self):
        """Efface toutes les lignes de trajet"""
        for line in self.route_lines:
            try:
                line.delete()
            except:
                pass
        self.route_lines = []

    def clear_all_map_elements(self):
        """Efface tous les éléments de la carte"""
        self.clear_route_lines()
        self.clear_map_markers()
        if self.conducteur_marker:
            try:
                self.conducteur_marker.delete()
            except:
                pass
            self.conducteur_marker = None

    def refresh_all_map_elements(self):
        """Actualise tous les éléments de la carte"""
        self.update_conducteur_on_map()
        self.refresh_map_markers()

    def ajouter_passager(self):
        try:
            depart_x = int(self.depart_x.get())
            depart_y = int(self.depart_y.get())
            arrivee_x = int(self.arrivee_x.get())
            arrivee_y = int(self.arrivee_y.get())

            if not (0 <= depart_x <= 99 and 0 <= depart_y <= 99):
                messagebox.showerror("Erreur", "Coordonnées de départ: 0-99")
                return

            if not (0 <= arrivee_x <= 99 and 0 <= arrivee_y <= 99):
                messagebox.showerror("Erreur", "Coordonnées d'arrivée: 0-99")
                return

            passager_id = len(self.passagers) + 1
            passager = Passager(passager_id, (depart_x, depart_y), (arrivee_x, arrivee_y))
            self.passagers.append(passager)

            self.liste_passagers.insert(tk.END,
                                        f"P{passager_id}: ({depart_x},{depart_y}) → ({arrivee_x},{arrivee_y})")

            # Ajouter marqueur et ligne
            try:
                if self.map_widget:
                    self.add_map_marker_for_passager(passager)
                    self.draw_lines_to_passengers()
            except:
                pass

            # Effacer champs
            self.depart_x.set("")
            self.depart_y.set("")
            self.arrivee_x.set("")
            self.arrivee_y.set("")

        except ValueError:
            messagebox.showerror("Erreur", "Coordonnées invalides")

    def supprimer_passager(self):
        selection = self.liste_passagers.curselection()
        if selection:
            index = selection[0]
            try:
                pid = self.passagers[index].id
            except:
                pid = None

            self.liste_passagers.delete(index)
            del self.passagers[index]

            for i, p in enumerate(self.passagers):
                p.id = i + 1

            self.liste_passagers.delete(0, tk.END)
            for p in self.passagers:
                self.liste_passagers.insert(tk.END,
                                            f"P{p.id}: {p.pos_depart} → {p.pos_arrivee}")

            try:
                if pid:
                    self.remove_map_marker(pid)
                self.draw_lines_to_passengers()
            except:
                pass

    def add_map_marker_for_passager(self, passager):
        """Ajoute un marqueur pour un passager"""
        if not self.map_widget:
            return None
        try:
            lat, lon = grid_to_latlon(
                passager.pos_depart[0],
                passager.pos_depart[1],
                self.map_bbox
            )
            marker = self.map_widget.set_marker(
                lat, lon,
                text=f"P{passager.id}",
                marker_color_circle="#FF6B6B",
                marker_color_outside="#C92A2A"
            )
            marker.position = (lat, lon)
            self.map_markers[passager.id] = marker
            return marker
        except:
            return None

    def remove_map_marker(self, passager_id):
        """Supprime un marqueur de passager"""
        if not self.map_widget:
            return
        marker = self.map_markers.get(passager_id)
        if marker:
            try:
                marker.delete()
            except:
                pass
            try:
                del self.map_markers[passager_id]
            except:
                pass

    def refresh_map_markers(self):
        """Actualise tous les marqueurs"""
        try:
            self.clear_map_markers()
        except:
            pass
        for p in self.passagers:
            try:
                self.add_map_marker_for_passager(p)
            except:
                pass
        self.draw_lines_to_passengers()

    def clear_map_markers(self):
        """Efface tous les marqueurs de passagers"""
        if not self.map_widget:
            self.map_markers = {}
            return
        for pid in list(self.map_markers.keys()):
            try:
                self.remove_map_marker(pid)
            except:
                pass
        self.map_markers = {}

    # Les autres méthodes (calculer, charger_exemple, etc.) restent identiques
    # Je les inclus pour la complétude mais sans modification

    def charger_exemple(self):
        self.effacer_tout()
        exemples = [
            Passager(1, (5, 5), (80, 80)),
            Passager(2, (8, 7), (82, 81)),
            Passager(3, (28, 27), (79, 77)),
            Passager(4, (16, 19), (83, 79)),
        ]

        self.passagers = exemples
        for p in self.passagers:
            self.liste_passagers.insert(tk.END,
                                        f"P{p.id}: {p.pos_depart} → {p.pos_arrivee}")

        try:
            if self.map_widget:
                self.refresh_map_markers()
                self.draw_lines_to_passengers()
        except:
            pass

    def effacer_tout(self):
        self.passagers = []
        self.liste_passagers.delete(0, tk.END)
        self.resultats.delete(1.0, tk.END)
        self.derniers_resultats = None
        try:
            if self.map_widget:
                self.clear_all_map_elements()
                self.update_conducteur_on_map()
        except:
            pass

    def show_map_install_help(self):
        messagebox.showinfo("Installation",
                            "Pour activer la carte:\n\npip install tkintermapview")

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

            # === ETAPE 4: POINTS D'ARRET ===
            self.resultats.insert(tk.END, f"\n--- POINTS D'ARRET ---\n")

            from pickup_scheduler import optimize_drop_off_points
            points_arret = optimize_drop_off_points(groupe_optimal, method=methode)

            self.resultats.insert(tk.END, f"Points d'arrêt: {len(points_arret)}\n\n")

            for i, point in enumerate(points_arret):
                ids = [p.id for p in point['passagers']]
                self.resultats.insert(tk.END, f"Arrêt {i+1}: {point['point_arret']} -> Passagers {ids}\n")

            # === ETAPE 5: PLANIFICATION TEMPORELLE ===
            self.resultats.insert(tk.END, f"\n--- PLANIFICATION TEMPORELLE ---\n")

            schedule = None
            trajet_ordre = None
            affectations = None
            temps_trajet = None

            try:
                # Générer le trajet complet
                from pickup_scheduler import generate_complete_route
                trajet_ordre, affectations, temps_trajet = generate_complete_route(
                    points, points_arret, conducteur_pos
                )

                # Validation des entrées
                validate_inputs(trajet_ordre, affectations, temps_trajet, len(groupe_optimal))

                # Calcul du planning
                schedule = compute_schedule(
                    trajet_ordre,
                    affectations,
                    temps_trajet,
                    start_time="08:00",
                    stop_time_per_passenger_min=2
                )

                self.resultats.insert(tk.END, f"Planning généré avec succès!\n")
                self.resultats.insert(tk.END, f"Trajet: {' -> '.join(trajet_ordre)}\n\n")

                # Afficher le planning détaillé
                self.resultats.insert(tk.END, "HORAIRES DETAILLES:\n")
                for record in schedule:
                    point = record['point']
                    # Extraire seulement HH:MM de l'ISO format
                    arrival_time = record['arrival'].split('T')[1][:5] if 'T' in record['arrival'] else record['arrival'][11:16]
                    departure_time = record['departure'].split('T')[1][:5] if 'T' in record['departure'] else record['departure'][11:16]
                    board = record['board']
                    cumulative = record['cumulative']

                    if point == "Depart":
                        self.resultats.insert(tk.END, f"  {point}: Départ à {departure_time}\n")
                    else:
                        passagers = ', '.join(record.get('passengers_boarded', []))
                        self.resultats.insert(tk.END, f"  {point}: Arrivée {arrival_time}, Départ {departure_time}\n")
                        self.resultats.insert(tk.END, f"    Montée: {board} passagers ({passagers})\n")
                        alighted = ', '.join(record.get('passengers_alighted', []))
                        self.resultats.insert(tk.END, f"    Descente: {record.get('alight', 0)} passagers ({alighted})\n")
                        self.resultats.insert(tk.END, f"    Total à bord: {cumulative}\n")

                # Calcul du temps total du trajet (durée)
                heure_depart = schedule[0]['departure']
                heure_arrivee = schedule[-1]['arrival']

                # Convertir en datetime pour calculer la différence
                from datetime import datetime
                if 'T' in heure_depart:
                    dt_depart = datetime.fromisoformat(heure_depart)
                    dt_arrivee = datetime.fromisoformat(heure_arrivee)
                else:
                    dt_depart = datetime.fromisoformat(f"2025-01-01T{heure_depart}")
                    dt_arrivee = datetime.fromisoformat(f"2025-01-01T{heure_arrivee}")

                duree_totale = dt_arrivee - dt_depart
                minutes_totales = int(duree_totale.total_seconds() / 60)
                heures = minutes_totales // 60
                minutes = minutes_totales % 60

                heure_arrivee_finale = heure_arrivee.split('T')[1][:5] if 'T' in heure_arrivee else heure_arrivee[11:16]

                self.resultats.insert(tk.END, f"\nHeure d'arrivée finale: {heure_arrivee_finale}\n")
                self.resultats.insert(tk.END, f"Durée totale du trajet: {heures}h{minutes:02d}min ({minutes_totales} minutes)\n")

                # Sauvegarder pour export
                if schedule and trajet_ordre and affectations and temps_trajet:
                    self.derniers_resultats = {
                        "TRAJET_ORDRE": trajet_ordre,
                        "AFFECTATIONS_PAR_POINT": affectations,
                        "TEMPS_TRAJET_MIN": temps_trajet,
                        "Z_optimal": len(groupe_optimal),
                        "SCHEDULE": schedule,
                        "POINTS_RAMASSAGE": points,
                        "POINTS_ARRET": points_arret,
                        "metadata": {
                            "methode": methode,
                            "nb_passagers": len(self.passagers),
                            "nb_points_ramassage": len(points),
                            "conducteur_position": conducteur_pos,
                            "parametres": {"R_dest": r_dest, "R_depart": r_depart}
                        }
                    }

            except Exception as e:
                self.resultats.insert(tk.END, f"Erreur planification: {str(e)}\n")
                self.derniers_resultats = None

            self.resultats.insert(tk.END, f"\n=== CALCUL TERMINÉ ===\n")

        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de saisie: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de calcul: {e}")

    def exporter_json(self):
        """Exporte les derniers résultats en JSON"""
        if not hasattr(self, 'derniers_resultats') or not self.derniers_resultats:
            messagebox.showwarning("Attention", "Aucun résultat à exporter. Lancez d'abord un calcul.")
            return

        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exporter les résultats"
            )

            if filename:
                import json
                payload = dict(self.derniers_resultats)
                # include map marker positions if available
                try:
                    if self.map_markers:
                        payload['map_positions'] = {str(k): (m.position[0], m.position[1]) if hasattr(m, 'position') else None for k, m in self.map_markers.items()}
                except Exception:
                    pass

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Succès", f"Résultats exportés vers:\n{filename}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

    def visualiser_trajet(self):
        """Visualiser le trajet sur la carte (si disponible)"""
        if not self.derniers_resultats or 'TRAJET_ORDRE' not in self.derniers_resultats:
            messagebox.showwarning("Attention", "Aucun trajet à visualiser. Effectuez d'abord un calcul.")
            return

        try:
            trajet_ordre = self.derniers_resultats['TRAJET_ORDRE']
            points_ramassage = self.derniers_resultats.get('POINTS_RAMASSAGE', [])
            points_arret = self.derniers_resultats.get('POINTS_ARRET', [])
            conducteur_pos = self.derniers_resultats['metadata']['conducteur_position']

            if not self.map_widget:
                messagebox.showerror("Erreur", "Carte non disponible. Installer 'tkintermapview' si nécessaire.")
                return

            # Effacer les marqueurs et polylignes précédents
            self.clear_map_markers()
            try:
                if hasattr(self.map_widget, 'delete_polyline'):
                    self.map_widget.delete_polyline("trajet_polyline")
            except Exception:
                pass

            # Construire la liste des positions
            positions = []
            for point in trajet_ordre:
                if point == "Depart":
                    positions.append(conducteur_pos)
                elif point.startswith("R"):
                    idx = int(point[1:]) - 1
                    if idx < len(points_ramassage):
                        positions.append(points_ramassage[idx]['point_ramassage'])
                elif point.startswith("D"):
                    idx = int(point[1:]) - 1
                    if idx < len(points_arret):
                        positions.append(points_arret[idx]['point_arret'])

            # Ajouter les marqueurs pour chaque position
            for i, pos in enumerate(positions):
                lat, lon = grid_to_latlon(pos[0], pos[1], self.map_bbox)
                if i == 0:
                    self.map_widget.set_marker(lat, lon, text="🚗 Conducteur", color="green")
                elif i == len(positions) - 1:
                    self.map_widget.set_marker(lat, lon, text="🏁 Arrivée", color="red")
                else:
                    point_type = "Ramassage" if trajet_ordre[i].startswith("R") else "Arrêt"
                    self.map_widget.set_marker(lat, lon, text=f"{point_type} {trajet_ordre[i]}", color="blue")

            # Dessiner une polyline pour le trajet
            if len(positions) > 1:
                latlon_coords = [grid_to_latlon(x, y, self.map_bbox) for x, y in positions]
                self.map_widget.set_polyline(latlon_coords, color="red", width=3, tag="trajet_polyline")

                # Ajuster la vue de la carte pour montrer tout le trajet
                lats, lons = zip(*latlon_coords)
                self.map_widget.set_bounds(min(lats), max(lats), min(lons), max(lons))

            messagebox.showinfo("Visualisation", "Trajet visualisé sur la carte avec le conducteur et les arrêts.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la visualisation du trajet: {e}")

    def animer_trajet(self):
        """Animer le trajet du conducteur sur la carte"""
        if not self.derniers_resultats or 'TRAJET_ORDRE' not in self.derniers_resultats:
            messagebox.showwarning("Attention", "Aucun trajet à animer. Effectuez d'abord un calcul.")
            return

        try:
            # First visualize the route
            self.visualiser_trajet()

            trajet_ordre = self.derniers_resultats['TRAJET_ORDRE']
            conducteur_pos = self.derniers_resultats['metadata']['conducteur_position']

            if not self.map_widget:
                messagebox.showerror("Erreur", "Carte non disponible. Installer 'tkintermapview' si nécessaire.")
                return

            # Effacer le marqueur de voiture précédent s'il existe
            self.clear_car_marker()

            # Initialiser les positions pour l'animation
            self.animation_positions = [conducteur_pos]

            for point in trajet_ordre:
                if point == "Depart":
                    continue
                elif point.startswith("R"):
                    idx = int(point[1:]) - 1
                    if idx < len(self.derniers_resultats.get('POINTS_RAMASSAGE', [])):
                        pos = self.derniers_resultats['POINTS_RAMASSAGE'][idx]['point_ramassage']
                        self.animation_positions.append(pos)
                elif point.startswith("D"):
                    idx = int(point[1:]) - 1
                    if idx < len(self.derniers_resultats.get('POINTS_ARRET', [])):
                        pos = self.derniers_resultats['POINTS_ARRET'][idx]['point_arret']
                        self.animation_positions.append(pos)

            # Lancer l'animation
            self.animation_index = 0
            lat, lon = grid_to_latlon(self.animation_positions[0][0], self.animation_positions[0][1], self.map_bbox)
            self.car_marker = self.map_widget.set_marker(lat, lon, text="🚗 Départ", color="orange")
            self.animate_car_route()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'animation du trajet: {e}")

    def animate_car_route(self):
        """Animer le marqueur de la voiture le long du trajet avec interpolation fluide"""
        if not self.car_marker or self.animation_index >= len(self.animation_positions):
            # Animation terminée
            self.car_marker.set_text("🏁 Arrivée")
            messagebox.showinfo("Animation terminée", "Le trajet a été entièrement animé.")
            self.car_marker = None
            return

        # Si on commence un nouveau segment
        if self.current_step == 0:
            self.start_pos = self.animation_positions[self.animation_index - 1] if self.animation_index > 0 else self.animation_positions[0]
            self.end_pos = self.animation_positions[self.animation_index]

            # Set text for current stop
            if self.animation_index == 0:
                self.car_marker.set_text("🚗 Départ")
            else:
                point = self.derniers_resultats['TRAJET_ORDRE'][self.animation_index]
                affect = self.derniers_resultats['AFFECTATIONS_PAR_POINT'].get(point, {})
                if isinstance(affect, dict):
                    if 'board' in affect and affect['board']:
                        boarded = ', '.join(f"P{p}" for p in affect['board'])
                        self.car_marker.set_text(f"🚗 Ramassage: {boarded}")
                    elif 'alight' in affect and affect['alight']:
                        alighted = ', '.join(f"P{p}" for p in affect['alight'])
                        self.car_marker.set_text(f"🚗 Arrêt: {alighted}")
                    else:
                        self.car_marker.set_text(f"🚗 {point}")
                else:
                    self.car_marker.set_text(f"🚗 {point}")

        # Calculer la position interpolée
        t = self.current_step / self.animation_steps
        current_lat = self.start_pos[0] + t * (self.end_pos[0] - self.start_pos[0])
        current_lon = self.start_pos[1] + t * (self.end_pos[1] - self.start_pos[1])

        lat, lon = grid_to_latlon(current_lat, current_lon, self.map_bbox)

        # Mettre à jour la position du marqueur
        self.car_marker.set_position(lat, lon)

        self.current_step += 1

        if self.current_step > self.animation_steps:
            # Segment terminé, passer au suivant
            self.current_step = 0
            self.animation_index += 1
            # Attendre un peu à l'arrêt
            self.root.after(1500, self.animate_car_route)  # Longer pause to show action
        else:
            # Continuer l'interpolation
            self.root.after(50, self.animate_car_route)

    def clear_car_marker(self):
        """Effacer le marqueur de la voiture s'il existe"""
        if self.car_marker:
            try:
                if hasattr(self.car_marker, 'delete'):
                    self.car_marker.delete()
                elif hasattr(self.map_widget, 'delete_marker'):
                    self.map_widget.delete_marker(self.car_marker)
            except Exception:
                pass
            self.car_marker = None

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = InterfaceOptimisation()
    app.run()
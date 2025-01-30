from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QProgressBar, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QPixmap, QIcon
import os
import time
import traceback
import datetime

class HeatmapWorker(QThread):
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    finished = pyqtSignal(dict)
    frame_generated = pyqtSignal(str)  # Signal pour envoyer le chemin de la frame générée

    def __init__(self, video_path, output_dir):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir

    def run(self):
        try:
            from detection.GenConViT_heatmap.prediction import vids

            self.progress.emit(10)
            time.sleep(0.5)
            self.progress.emit(40)

            root_dir = os.path.dirname(self.video_path)

            def save_frame(image_path):
                """Enregistre et émet chaque frame générée."""
                self.frame_generated.emit(image_path)

            result = vids(
                ed_weight="genconvit_ed_inference",
                vae_weight="genconvit_vae_inference",
                root_dir=root_dir,
                dataset=None,
                num_frames=20,
                net="genconvit",
                fp16=False,
                output_dir=self.output_dir,
                frame_callback=save_frame  # Utiliser le callback pour chaque frame
            )

            self.progress.emit(90)
            time.sleep(0.5)
            self.progress.emit(100)
            self.finished.emit(result)

        except Exception as e:
            error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.error.emit(error_msg)


class HeatmapPage(QWidget):
    def __init__(self, navigate_to, back, video_path=None):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.video_path = video_path

        self.worker = None
        self.output_dir = None
        self.frame_files = []
        self.current_frame_index = 0
        self.init_ui()

        # Vérifier si le dossier existe déjà
        if self.video_path:
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            self.output_dir = os.path.join("heatmaps", video_name)
            if os.path.exists(self.output_dir):
                self.display_existing_frames(auto_play=True)  # Relire automatiquement
            else:
                self.start_heatmap()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Titre
        title_label = QLabel("Génération de Heatmap")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #03224c;
        """)
        main_layout.addWidget(title_label, alignment=Qt.AlignTop)

        # Espace pour afficher les frames
        self.frame_display = QLabel("Aucune frame affichée pour l'instant")
        self.frame_display.setAlignment(Qt.AlignCenter)
        self.frame_display.setStyleSheet("""
            border: 2px solid black; 
            background-color: #e0e0e0;
        """)
        self.frame_display.setFixedSize(800, 600)  # Fixer la taille de l'affichage
        main_layout.addWidget(self.frame_display, alignment=Qt.AlignCenter)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #03224c;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2c3e50;
            }
        """)
        main_layout.addWidget(self.progress_bar, stretch=1)

        # Boutons navigation en haut
        nav_top_layout = QHBoxLayout()
        nav_top_layout.setSpacing(20)

        relire_button = QPushButton("Relire les Frames")
        relire_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #03224c;
            }
        """)
        relire_button.clicked.connect(self.replay_frames)
        nav_top_layout.addWidget(relire_button)

        home_button = QPushButton("Accueil")
        home_button.setStyleSheet(relire_button.styleSheet())
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        nav_top_layout.addWidget(home_button)

        main_layout.addLayout(nav_top_layout)

        # Bouton Retour en bas
        nav_bottom_layout = QHBoxLayout()
        nav_bottom_layout.addStretch()

        back_button = QPushButton()
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)
        back_button.setIcon(QIcon(QPixmap("retour.png")))
        back_button.setIconSize(back_button.sizeHint())
        back_button.clicked.connect(self.back)
        nav_bottom_layout.addWidget(back_button)

        nav_bottom_layout.addStretch()
        main_layout.addLayout(nav_bottom_layout)

        # Appliquer le layout principal
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #ada092;")

    def start_heatmap(self):
        if not self.video_path:
            QMessageBox.warning(self, "Info", "Aucune vidéo disponible pour la Heatmap.")
            return

        # Créer un sous-dossier basé sur le nom de la vidéo
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        self.output_dir = os.path.join("heatmaps", video_name)
        os.makedirs(self.output_dir, exist_ok=True)

        # Barre de progression visible
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        # Créer le worker
        self.worker = HeatmapWorker(self.video_path, self.output_dir)

        # Connecter signaux
        self.worker.progress.connect(self.on_progress)
        self.worker.error.connect(self.on_heatmap_error)
        self.worker.finished.connect(self.on_heatmap_finished)
        self.worker.frame_generated.connect(self.display_frame)

        # Lancer
        self.worker.start()

    def display_existing_frames(self, auto_play=False):
        """Afficher les frames déjà générées."""
        if not os.path.exists(self.output_dir):
            QMessageBox.warning(self, "Info", "Aucune frame existante à afficher.")
            return

        self.frame_files = sorted([
            os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith(".jpg")
        ], key=lambda x: os.path.getctime(x))  # Tri par date de création

        if not self.frame_files:
            QMessageBox.warning(self, "Info", "Aucune frame existante à afficher.")
            return

        if auto_play:
            self.replay_frames()

    def replay_frames(self):
        """Relire les frames enregistrées."""
        if not self.frame_files:
            QMessageBox.warning(self, "Info", "Aucune frame existante à relire.")
            return

        self.current_frame_index = 0

        def update_frame():
            if self.current_frame_index >= len(self.frame_files):
                timer.stop()
                return
            frame_path = self.frame_files[self.current_frame_index]
            pixmap = QPixmap(frame_path)
            self.frame_display.setPixmap(pixmap.scaled(
                self.frame_display.width(),
                self.frame_display.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            self.current_frame_index += 1

        timer = QTimer(self)
        timer.timeout.connect(update_frame)
        timer.start(500)  # Change frames every 500ms

    def on_progress(self, value):
        self.progress_bar.setValue(value)

    def on_heatmap_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erreur Heatmap", error_msg)

    def on_heatmap_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self, "Heatmap terminée",
            f"Les heatmaps ont été générées dans le dossier '{self.output_dir}'."
        )
        self.display_existing_frames(auto_play=True)

    def display_frame(self, frame_path):
        """Affiche une frame dans l'interface."""
        if os.path.exists(frame_path):
            pixmap = QPixmap(frame_path)
            self.frame_display.setPixmap(pixmap.scaled(
                self.frame_display.width(),
                self.frame_display.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
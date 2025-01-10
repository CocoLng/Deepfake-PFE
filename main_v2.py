# -*- coding: utf-8 -*-
"""
Updated on Mon Dec 16 2024

@author: nodie
"""
import sys
#import os

# Forcer le backend Windows Media Foundation
#os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
    QMessageBox
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepFake Application")
        self.setGeometry(100, 100, 1200, 800)

        # Appliquer les styles globaux
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c2f33;
                color: #ffffff;
            }
            QPushButton {
                font-size: 18px;
                padding: 15px;
                border-radius: 10px;
                background-color: #7289da;
                color: white;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
            QLabel {
                font-size: 16px;
                color: #ffffff;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Titre
        title_label = QLabel("DeepFake Generator & Detector")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Section de chargement de vidéo
        load_layout = QHBoxLayout()
        self.video_label = QLabel("Aucune vidéo chargée")
        self.video_label.setStyleSheet("border: 1px solid gray; padding: 10px; font-size: 14px;")
        load_layout.addWidget(self.video_label)

        self.load_button = QPushButton("Charger une vidéo")
        self.load_button.clicked.connect(self.load_video)
        load_layout.addWidget(self.load_button)
        main_layout.addLayout(load_layout)

        # Section de la vidéo
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(900, 500)
        self.video_widget.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.video_widget, alignment=Qt.AlignCenter)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Section des contrôles avec émoticônes
        controls_layout = QHBoxLayout()

        # Sélection du visage
        self.face_selector = QComboBox()
        self.face_selector.addItems(["Célébrité 1", "Célébrité 2", "Célébrité 3", "Célébrité 4"])
        self.face_selector.setStyleSheet("padding: 10px; font-size: 16px;")
        controls_layout.addWidget(QLabel("Visage pré-entraîné :"))
        controls_layout.addWidget(self.face_selector)

        # Bouton de génération avec émoticône 📹
        self.generate_button = QPushButton("📹 Générer le DeepFake")
        self.generate_button.setStyleSheet("font-size: 18px;")
        self.generate_button.clicked.connect(self.generate_deepfake)
        controls_layout.addWidget(self.generate_button)

        # Bouton de détection avec émoticône 🔍
        self.detect_button = QPushButton("🔍 Détecter les parties 'truquées'")
        self.detect_button.setStyleSheet("font-size: 18px;")
        self.detect_button.clicked.connect(self.detect_deepfake)
        controls_layout.addWidget(self.detect_button)

        main_layout.addLayout(controls_layout)
        central_widget.setLayout(main_layout)

    def load_video(self):
        """Charger une vidéo source."""
        video_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une vidéo", "", "Videos (*.mp4 *.avi)")
        if video_path:
            self.video_label.setText(f"Vidéo chargée : {video_path}")
            self.loaded_video_path = video_path
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))

            # Connecter le signal d'erreur pour gérer les éventuelles erreurs de lecture
            self.media_player.error.connect(self.handle_error)
            self.media_player.play()  # Jouer automatiquement la vidéo après le chargement

    def handle_error(self):
        """Afficher les erreurs liées au lecteur multimédia."""
        error_message = self.media_player.errorString()
        QMessageBox.critical(self, "Erreur de lecture vidéo", f"Une erreur s'est produite : {error_message}")

    def generate_deepfake(self):
        """Simuler la génération de DeepFake."""
        if not hasattr(self, 'loaded_video_path'):
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une vidéo.")
            return

        selected_face = self.face_selector.currentText()
        print(f"Visage sélectionné : {selected_face}")  # Log pour test

        self.video_label.setText("DeepFake en cours...")

        # Simuler un délai de génération
        QTimer.singleShot(3000, self.show_generated_video)

    def show_generated_video(self):
        """Afficher la vidéo générée (simulée)."""
        self.video_label.setText("DeepFake terminé. Voici la vidéo générée.")
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.loaded_video_path)))  # Afficher la même vidéo
        self.media_player.play()

    def detect_deepfake(self):
        """Simuler la détection des parties truquées de la vidéo."""
        QMessageBox.information(self, "Détection", "Analyse des parties truquées en cours...")
        QTimer.singleShot(2000, lambda: QMessageBox.information(self, "Détection terminée", "Les parties truquées ont été détectées."))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

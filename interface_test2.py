import sys
import os
import vlc  # Utiliser VLC pour la lecture vidéo

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QColorDialog ,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSlider,
    QComboBox,
    QMessageBox,
    QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer

import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class HomePage(QWidget):
    def __init__(self, navigate_to):
        super().__init__()
        self.navigate_to = navigate_to
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Message de bienvenue
        welcome_label = QLabel("DeepFakeXplorer")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
    font-size: 52px;
    font-weight: bold;
    color: #03224c;  /* Couleur bleu néon */
    text-shadow: 2px 2px 4px #000000;  /* Effet d'ombre portée */
    font-family: 'Segoe UI', Arial, sans-serif;  /* Police moderne */
""")
        layout.addWidget(welcome_label)

        # Fond captivant
        self.setStyleSheet("background-color: #ada092;")

        # Layout horizontal pour les boutons
        buttons_layout = QHBoxLayout()

        # Obtenir le chemin absolu du dossier actuel
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Bouton Génération avec image et texte
        generate_button = QPushButton()
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 300px;
            }
            QPushButton:hover {
                background-color: #03224c;
            }
        """)
        generate_button.clicked.connect(lambda: self.navigate_to("generation"))

        # Layout pour l'image et le texte du bouton Génération
        generate_layout = QVBoxLayout()
        generate_icon = QLabel()
        generate_pixmap = QPixmap(os.path.join(current_dir, "generation.png")).scaled(500, 500, Qt.KeepAspectRatio)
        if generate_pixmap.isNull():
            print("Erreur : L'image 'generation.png' est introuvable.")
        generate_icon.setPixmap(generate_pixmap)
        generate_icon.setAlignment(Qt.AlignCenter)
        generate_label = QLabel("Génération")
        generate_label.setAlignment(Qt.AlignCenter)
        generate_label.setStyleSheet("font-size: 38px; color: #03224c;")
        generate_layout.addWidget(generate_icon)
        generate_layout.addWidget(generate_label)
        generate_button.setLayout(generate_layout)
        buttons_layout.addWidget(generate_button)

        # Bouton Détection avec image et texte
        detect_button = QPushButton()
        detect_button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 300px;
            }
            QPushButton:hover {
                background-color: #03224c;
            }
        """)
        detect_button.clicked.connect(lambda: self.navigate_to("detection"))

        # Layout pour l'image et le texte du bouton Détection
        detect_layout = QVBoxLayout()
        detect_icon = QLabel()
        detect_pixmap = QPixmap(os.path.join(current_dir, "detection.png")).scaled(390, 390, Qt.KeepAspectRatio)
        if detect_pixmap.isNull():
            print("Erreur : L'image 'detection.png' est introuvable.")
        detect_icon.setPixmap(detect_pixmap)
        detect_icon.setAlignment(Qt.AlignCenter)
        detect_label = QLabel("Détection")
        detect_label.setAlignment(Qt.AlignCenter)
        detect_label.setStyleSheet("font-size: 38px; color: #03224c;")
        detect_layout.addWidget(detect_icon)
        detect_layout.addWidget(detect_label)
        detect_button.setLayout(detect_layout)
        buttons_layout.addWidget(detect_button)

        # Étendre les boutons pour couvrir chacun 50% de la largeur
        buttons_layout.setStretch(0, 1)
        buttons_layout.setStretch(1, 1)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

class GenerationPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre
        title_label = QLabel("Génération de Deepfake")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 52px;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 2px 2px 4px #000000;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        layout.addWidget(title_label)

        # Menu déroulant pour sélectionner les vidéos
        video_layout = QHBoxLayout()

        self.video_selector = QComboBox()
        self.video_selector.addItems(["Vidéo 1", "Vidéo 2", "Vidéo 3"])
        self.video_selector.setStyleSheet("padding: 10px; font-size: 16px;")
        video_layout.addWidget(QLabel("Sélectionner une vidéo pré-traitée :"))
        video_layout.addWidget(self.video_selector)

        layout.addLayout(video_layout)

        # Menu déroulant pour le nombre de personnes
        people_layout = QHBoxLayout()
        
        self.people_selector = QComboBox()
        self.people_selector.addItems(["1 personne", "2 personnes", "3 personnes"])
        self.people_selector.setStyleSheet("padding: 10px; font-size: 16px;")
        people_layout.addWidget(QLabel("Nombre de personnes dans la vidéo :"))
        people_layout.addWidget(self.people_selector)

        layout.addLayout(people_layout)

        # Sélection de la personne à modifier
        person_layout = QHBoxLayout()
        
        self.person_selector = QComboBox()
        self.person_selector.addItems(["Personne 1", "Personne 2", "Personne 3"])
        self.person_selector.setStyleSheet("padding: 10px; font-size: 16px;")
        person_layout.addWidget(QLabel("Choisir la personne à modifier :"))
        person_layout.addWidget(self.person_selector)
        
        layout.addLayout(person_layout)

        # Bouton pour générer le DeepFake
        generate_button = QPushButton("Générer le DeepFake")
        generate_button.setStyleSheet("font-size: 18px; padding: 250px;")
        generate_button.clicked.connect(self.generate_deepfake)
        layout.addWidget(generate_button)

        # Navigation
        nav_layout = QHBoxLayout()
        back_button = QPushButton()
        back_button.setStyleSheet("""
    QPushButton {
        background-color: #FF6347;  /* Rouge clair */
        border: none;
        border-radius: 10px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #FF4500;  /* Rouge foncé sur hover */
    }
""")

       # Crée une icône pour le bouton
        icon = QIcon(QPixmap("C:/Users/nodie/Desktop/M2/S1/PFE/Test4/retour.png"))  # Convertit QPixmap en QIcon
        back_button.setIcon(icon)
        back_button.setIconSize(back_button.sizeHint()) 
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(back_button)
        layout.addLayout(nav_layout)

        layout.addStretch()
        self.setLayout(layout)

    def generate_deepfake(self):
        # Vérifier les sélections
        video = self.video_selector.currentText()
        people = self.people_selector.currentText()
        person = self.person_selector.currentText()

        # Chemin de la vidéo en fonction de la sélection
        if video == "Vidéo 1":
            video_path = "exemple_video.mp4"  # Assurez-vous que ce fichier existe
        else:
            video_path = "path/to/another/video.mp4"

        QMessageBox.information(self, "Génération", f"Vidéo : {video}, Personnes : {people}, Modifier : {person}")
        QTimer.singleShot(1000, lambda: self.navigate_to("video_playback", video_generated=True, video_path=video_path))


class DetectionPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("Détection de DeepFake")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; color: #ffffff;")
        layout.addWidget(title_label)
        
        # Menu déroulant pour sélectionner les vidéos DeepFake
        video_layout = QHBoxLayout()
        
        self.deepfake_selector = QComboBox()
        self.deepfake_selector.addItems(["DeepFake 1", "DeepFake 2", "DeepFake 3"])  # Exemple de vidéos DeepFake
        self.deepfake_selector.setStyleSheet("padding: 10px; font-size: 16px;")
        video_layout.addWidget(QLabel("Sélectionner une vidéo DeepFake :"))
        video_layout.addWidget(self.deepfake_selector)
        
        layout.addLayout(video_layout)
        
        # Bouton pour lancer la détection
        detect_button = QPushButton("Détecter les parties 'truquées'")
        detect_button.setStyleSheet("font-size: 18px; padding: 10px;")
        detect_button.clicked.connect(self.detect_deepfake)
        layout.addWidget(detect_button)
        
        # Navigation
        nav_layout = QHBoxLayout()
        home_button = QPushButton("Accueil")
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        back_button = QPushButton("Retour")
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(home_button)
        nav_layout.addWidget(back_button)
        layout.addLayout(nav_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def detect_deepfake(self):
        # Simuler la détection
        QMessageBox.information(self, "Détection", "Analyse des parties truquées en cours...")
        QTimer.singleShot(3000, lambda: self.navigate_to("detection_result"))

class VideoPlaybackPage(QWidget):
    def __init__(self, navigate_to, back, video_path, is_generated=False, is_detection=False):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.video_path = video_path
        self.is_generated = is_generated
        self.is_detection = is_detection
        self.init_ui()
        self.init_player()

    def init_ui(self):
        layout = QVBoxLayout()

        self.video_label = QLabel(f"Lecture de la vidéo : {self.video_path}")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("font-size: 18px; color: #ffffff;")
        layout.addWidget(self.video_label)

        self.video_widget = QWidget(self)
        self.video_widget.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.video_widget.setMinimumSize(900, 500)
        layout.addWidget(self.video_widget)

        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("Pause")
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button)

        # Volume slider
        volume_layout = QVBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setAlignment(Qt.AlignCenter)
        volume_label.setStyleSheet("font-size: 14px; color: #ffffff;")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)  # Set initial volume to 50%
        self.volume_slider.setFixedWidth(200)  # Réduire la largeur du slider
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        controls_layout.addLayout(volume_layout)

        self.rewind_button = QPushButton("Revenir en arrière")
        self.rewind_button.clicked.connect(self.rewind_video)
        controls_layout.addWidget(self.rewind_button)

        home_button = QPushButton("Accueil")
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        controls_layout.addWidget(home_button)

        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def init_player(self):
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        if not os.path.exists(self.video_path):
            QMessageBox.critical(self, "Erreur", f"Le fichier vidéo '{self.video_path}' est introuvable.")
            return

        media = self.vlc_instance.media_new(self.video_path)
        self.media_player.set_media(media)

        if sys.platform.startswith("win"):
            self.media_player.set_hwnd(int(self.video_widget.winId()))
        elif sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(self.video_widget.winId()))
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(self.video_widget.winId()))

        self.media_player.play()
        self.media_player.audio_set_volume(50)  # Set initial volume to 50%

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_video_end)
        self.timer.start()

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def toggle_play(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            if self.media_player.get_state() == vlc.State.Ended:
                self.media_player.set_time(0)
            self.media_player.play()
            self.play_button.setText("Pause")

    def rewind_video(self):
        current_time = self.media_player.get_time()
        self.media_player.set_time(max(current_time - 5000, 0))

    def check_video_end(self):
        if self.media_player.get_state() == vlc.State.Ended:
            self.timer.stop()
            if self.is_detection:
                choice = QMessageBox.question(self, "Détection terminée",
                                              "La détection est terminée. Voulez-vous relire la vidéo ?",
                                              QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    self.media_player.play()
                else:
                    self.navigate_to("home")
            elif self.is_generated:
                choice = QMessageBox.question(self, "DeepFake Généré",
                                              "Voulez-vous continuer avec une détection de DeepFake ?",
                                              QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    self.navigate_to("detection")
                else:
                    self.navigate_to("home")
            else:
                self.navigate_to("home")

    def closeEvent(self, event):
        self.media_player.stop()
        event.accept()

class DetectionResultPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("Résultats de la Détection")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; color: #ffffff;")
        layout.addWidget(title_label)
        
        # Simuler une vidéo avec heatmaps
        self.video_label = QLabel("Vidéo avec heatmaps des zones altérées")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; font-size: 18px; padding: 20px;")
        self.video_label.setMinimumSize(900, 500)
        layout.addWidget(self.video_label)
        
        # Navigation après détection
        nav_layout = QHBoxLayout()
        replay_button = QPushButton("Relire la vidéo")
        replay_button.clicked.connect(lambda: self.navigate_to("video_playback", video_generated=False, is_detection=True))
        home_button = QPushButton("Accueil")
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        nav_layout.addWidget(replay_button)
        nav_layout.addWidget(home_button)
        layout.addLayout(nav_layout)
        
        layout.addStretch()
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepFake Application")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c2f33;
                color: #ffffff;
            }
            QPushButton {
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                background-color: #7289da;
                color: white;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
            QLabel {
                font-size: 16px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #ffffff;
                color: #000000;
            }
        """)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.home_page = HomePage(self.navigate_to)
        self.generation_page = GenerationPage(self.navigate_to, self.go_back)
        self.detection_page = DetectionPage(self.navigate_to, self.go_back)
        self.detection_result_page = DetectionResultPage(self.navigate_to, self.go_back)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.generation_page)
        self.stacked_widget.addWidget(self.detection_page)
        self.stacked_widget.addWidget(self.detection_result_page)

        self.history = []
        self.current_page = "home"

    def navigate_to(self, page, **kwargs):
        if page == "home":
            self.stacked_widget.setCurrentWidget(self.home_page)
        elif page == "generation":
            self.stacked_widget.setCurrentWidget(self.generation_page)
        elif page == "detection":
            self.stacked_widget.setCurrentWidget(self.detection_page)
        elif page == "video_playback":
            video_path = kwargs.get("video_path", "path/to/generated/video.mp4")
            video_generated = kwargs.get("video_generated", False)
            is_detection = kwargs.get("is_detection", False)
            self.video_playback_page = VideoPlaybackPage(
                self.navigate_to,
                self.go_back,
                video_path,
                is_generated=video_generated,
                is_detection=is_detection
            )
            self.stacked_widget.addWidget(self.video_playback_page)
            self.stacked_widget.setCurrentWidget(self.video_playback_page)
        elif page == "detection_result":
            self.stacked_widget.setCurrentWidget(self.detection_result_page)
        else:
            QMessageBox.warning(self, "Navigation", f"Page inconnue : {page}")
            return

        if self.current_page != page:
            self.history.append(self.current_page)
            self.current_page = page

    def go_back(self):
        if self.history:
            previous_page = self.history.pop()
            self.current_page = previous_page
            if previous_page == "home":
                self.stacked_widget.setCurrentWidget(self.home_page)
            elif previous_page == "generation":
                self.stacked_widget.setCurrentWidget(self.generation_page)
            elif previous_page == "detection":
                self.stacked_widget.setCurrentWidget(self.detection_page)
            elif previous_page == "detection_result":
                self.stacked_widget.setCurrentWidget(self.detection_result_page)
            elif previous_page == "video_playback":
                self.stacked_widget.setCurrentWidget(self.video_playback_page)
        else:
            QMessageBox.information(self, "Retour", "Aucune page précédente.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

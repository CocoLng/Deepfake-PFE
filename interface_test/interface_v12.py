import sys
import os
import vlc  # Utiliser VLC pour la lecture vidéo
import math
import shutil

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QProgressBar, 
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSlider,
    QGraphicsOpacityEffect,
    QComboBox,
    QSpacerItem,
    QMessageBox,
    QStackedWidget,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QThread, QRectF, QPropertyAnimation, pyqtSlot, QSize, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter

from detection_page import DetectionWorker
from audio_page import DetectionAudioWorker
from audio_worker import AudioGenerationWorker
from heatmap_page import HeatmapPage
from video_worker import VideoGenerationWorker

#------------------------- Start Page -----------------------#

class StartPage(QWidget):
    def __init__(self, navigate_to, image_path=None):
        super().__init__()
        self.navigate_to = navigate_to
        self.image_path = image_path or self.get_default_image_path()
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Background image
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            print(f"Error: Image '{self.image_path}' not found.")
        else:
            self.image_label.setPixmap(pixmap)
        main_layout.addWidget(self.image_label)

        # Title container
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # Title
        self.title_label = QLabel("DeepFakeXplorer", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            color:rgb(3, 14, 53);
            text-shadow: 4px 4px 8px #000000;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 96px;
            font-weight: bold;
        """)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Spacer to push the title upwards
        spacer = QSpacerItem(20, 1500, QSizePolicy.Minimum, QSizePolicy.Fixed)
        title_layout.addSpacerItem(spacer)

        # Overlay the title layout on the main layout
        main_layout.addLayout(title_layout)

        # Blinking text at the bottom
        self.start_label = QLabel("Appuyez sur une touche", self)
        self.start_label.setAlignment(Qt.AlignCenter)
        self.start_label.setStyleSheet("""
            font-size: 24px;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 10px;
        """)
        main_layout.addWidget(self.start_label, alignment=Qt.AlignBottom)

        # Blinking animation
        self.opacity_effect = QGraphicsOpacityEffect(self.start_label)
        self.start_label.setGraphicsEffect(self.opacity_effect)
        self.text_animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.text_animation.setDuration(2000)
        self.text_animation.setStartValue(0.3)
        self.text_animation.setEndValue(1.0)
        self.text_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.text_animation.setLoopCount(-1)
        self.text_animation.start()

        # Ensure the page captures keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def resizeEvent(self, event):
        # Adjust the image to fill the window
        self.image_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        # Navigate to the home page when a key is pressed
        self.navigate_to("home")

    def mousePressEvent(self, event):
        # Navigate to the home page when the mouse is clicked
        self.navigate_to("home")

    def get_default_image_path(self):
        """Default path for the image if not specified."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "fond_ecran.png")

# ----------------------- HOMEPAGE ------------------------#

class HomePage(QWidget):
    def __init__(self, navigate_to):
        super().__init__()
        self.navigate_to = navigate_to
        self.init_ui()

    def init_ui(self):
        # Layout principal vertical
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # En-tête : Logo Sorbonne (à droite) et titre (au centre)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Logo Sorbonne (en haut à droite)
        sorbonne_logo = QLabel()
        sorbonne_pixmap = QPixmap("Sorbonne.png").scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        sorbonne_logo.setPixmap(sorbonne_pixmap)
        sorbonne_logo.setAlignment(Qt.AlignRight)
        header_layout.addWidget(sorbonne_logo, alignment=Qt.AlignRight)

        # Titre de la page (centré)
        welcome_label = QLabel("DeepFakeXplorer")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("welcome_label")  # Pour styles spécifiques
        main_layout.addWidget(welcome_label)

        # Ajouter le header en premier
        main_layout.addLayout(header_layout)

        # Layout horizontal pour les boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # Obtenir le chemin absolu du dossier actuel
        current_dir = os.path.dirname(os.path.abspath(__file__))

        def create_button(icon_path, label_text, navigate_target, icon_width, icon_height):
            """
            Crée un bouton avec une image, un texte et une taille personnalisée pour l'icône.

            :param icon_path: Chemin de l'image.
            :param label_text: Texte sous l'image.
            :param navigate_target: Fonction cible pour la navigation.
            :param icon_width: Largeur personnalisée de l'image.
            :param icon_height: Hauteur personnalisée de l'image.
            :return: QPushButton configuré.
            """
            button = QPushButton()
            button.setObjectName("menu_button")  # Pour styles spécifiques
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Layout interne du bouton
            button_layout = QVBoxLayout()
            button_layout.setContentsMargins(10, 10, 10, 10)
            button_layout.setSpacing(10)

            # Ajouter l'image
            icon_label = QLabel()
            pixmap = QPixmap(os.path.join(current_dir, icon_path)).scaled(icon_width, icon_height, Qt.KeepAspectRatio)
            if pixmap.isNull():
                print(f"Erreur : L'image '{icon_path}' est introuvable.")
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)

            # Ajouter le texte
            text_label = QLabel(label_text)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setObjectName("button_text")  # Pour styles spécifiques

            button_layout.addWidget(icon_label)
            button_layout.addWidget(text_label)
            button.setLayout(button_layout)

            # Connecter le bouton
            button.clicked.connect(lambda: self.navigate_to(navigate_target))
            return button

        # Créer des boutons avec des tailles d'images personnalisées
        generate_button = create_button("generation_v2.png", "Génération", "generation_option", 300, 300)
        detect_button = create_button("heatmap.jpg", "Détection Vidéo", "detection", 300, 150)
        detect_audio_button = create_button("audio_icon.png", "Détection Audio", "detection_audio", 150, 200)

        # Ajouter les boutons au layout
        buttons_layout.addWidget(generate_button)
        buttons_layout.addWidget(detect_button)
        buttons_layout.addWidget(detect_audio_button)

        # Ajouter la section des boutons au layout principal
         # Add buttons layout to the main layout
        main_layout.addLayout(buttons_layout)

        # Texte de copyright (en bas, centré)
        copyright_label = QLabel("<a href='#'>© 2025 Sorbonne Université. Tous droits réservés.</a>")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            font-size: 18px;
            color: #ffffff;
            text-decoration: underline;
        """)
        copyright_label.setOpenExternalLinks(False)  # Handle navigation internally
        copyright_label.linkActivated.connect(self.show_copyright_page)

        main_layout.addWidget(copyright_label, alignment=Qt.AlignBottom)


        # Appliquer le layout principal à la fenêtre
        self.setMinimumSize(1200, 800)
        self.setLayout(main_layout)

    def show_copyright_page(self):
        """Navigate to the copyright page."""
        self.navigate_to("copyright")


#------------------------- Copyright Page -------------------------------#

class CopyrightPage(QWidget):
    def __init__(self, back):
        super().__init__()
        self.back = back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Copyright & Acknowledgments")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 4px #000000;
        """)
        layout.addWidget(title_label)

        # Content
        content_label = QLabel("""
            <p style="font-size: 18px; color: white;">
            DeepFakeXplorer was created by the following team:
            <ul>
                <li><b>Author 1</b>: Responsible for video detection</li>
                <li><b>Author 2</b>: Responsible for audio detection</li>
                <li><b>Author 3</b>: Responsible for the interface</li>
            </ul>
            Special thanks to the Sorbonne University for their support.
            </p>
        """)
        content_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(content_label)

        # Back button
        back_button = QPushButton("Back")
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
        back_button.clicked.connect(self.back)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        # Set page background color
        self.setStyleSheet("""
            background-color: #1a2b4c;
        """)

        self.setLayout(layout)



# ----------------------- GENERATION OPTION PAGE ------------------------#

class GenerationOptionPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        title_label = QLabel("Options de Génération")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")  # Pour styles spécifiques
        layout.addWidget(title_label)

        # Boutons de génération vidéo et audio
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        generate_video_button = QPushButton("Génération Vidéo")
        generate_video_button.setObjectName("menu_button")
        generate_video_button.clicked.connect(lambda: self.navigate_to("generation_video"))
        buttons_layout.addWidget(generate_video_button)

        generate_audio_button = QPushButton("Génération Audio")
        generate_audio_button.setObjectName("menu_button")
        generate_audio_button.clicked.connect(lambda: self.navigate_to("generation_audio"))
        buttons_layout.addWidget(generate_audio_button)

        layout.addLayout(buttons_layout)

        # Boutons de navigation (Retour et Accueil)
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()

        back_button = QPushButton()
        back_button.setObjectName("back_button")
        back_button.setIcon(QIcon(QPixmap("retour.png")))
        back_button.setIconSize(back_button.sizeHint())
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(back_button)

        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        self.setLayout(layout)


# ----------------------- GENERATION AUDIO PAGE ------------------------#

class GenerationAudioPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.selected_audio_path = None
        self.selected_model = "macron"
        self.transpose_value = 0
        self.output_audio_path = None
        self.init_ui()

        # Thread pour exécuter la génération audio
        self.thread = None
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Titre de la page
        title_label = QLabel("Génération de DeepFake Audio")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")  # Pour styles spécifiques
        layout.addWidget(title_label)

        # Sélection du fichier audio
        file_layout = QHBoxLayout()
        file_label = QLabel("Sélectionner un fichier audio :")
        file_label.setObjectName("label")
        self.file_path_label = QLabel("Aucun fichier sélectionné")
        self.file_path_label.setObjectName("file_label")
        browse_button = QPushButton("Parcourir")
        browse_button.setObjectName("browse_button")
        browse_button.clicked.connect(self.browse_audio)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)

        # Sélection du modèle de voix
        model_layout = QHBoxLayout()
        model_label = QLabel("Choisir le modèle de voix :")
        model_label.setObjectName("label")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Président Emmanuel Macron", "Président Donald Trump", "Président Biden", "Professeur Nicola Obin"])
        self.model_combo.setObjectName("combo_box")
        self.model_combo.currentIndexChanged.connect(self.model_selection_changed)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Sélection de l'octave
        transpose_layout = QHBoxLayout()
        transpose_label = QLabel("Octave de la voix (-12 à 12) :")
        transpose_label.setObjectName("label")
        self.transpose_slider = QSlider(Qt.Horizontal)
        self.transpose_slider.setMinimum(-12)
        self.transpose_slider.setMaximum(12)
        self.transpose_slider.setValue(0)
        self.transpose_slider.setTickInterval(1)
        self.transpose_slider.setTickPosition(QSlider.TicksBelow)
        self.transpose_slider.setObjectName("slider")
        self.transpose_slider.valueChanged.connect(self.transpose_changed)
        self.transpose_value_label = QLabel("0")
        self.transpose_value_label.setObjectName("slider_label")

        transpose_layout.addWidget(transpose_label)
        transpose_layout.addWidget(self.transpose_slider)
        transpose_layout.addWidget(self.transpose_value_label)
        layout.addLayout(transpose_layout)

        # Bouton Générer
        self.generate_button = QPushButton("Générer")
        self.generate_button.setObjectName("generate_button")
        self.generate_button.clicked.connect(self.start_generation)
        layout.addWidget(self.generate_button)

        # Barre de progression (initialement cachée)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Boutons de navigation (Accueil et Retour)
        nav_layout = QHBoxLayout()
        home_button = QPushButton("Accueil")
        home_button.setObjectName("nav_button")
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        back_button = QPushButton("Retour")
        back_button.setObjectName("nav_button")
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(home_button)
        nav_layout.addWidget(back_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def browse_audio(self):
        """Ouvre un QFileDialog pour sélectionner un fichier audio."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audios (*.mp3 *.wav *.flac);;Tous les fichiers (*.*)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.selected_audio_path = selected_file
            self.file_path_label.setText(os.path.basename(selected_file))

    def model_selection_changed(self, index):
        """Met à jour le modèle sélectionné basé sur le choix de l'utilisateur."""
        if index == 0:
            self.selected_model = "macron"
        elif index == 1:
            self.selected_model = "trump"
        elif index == 2:
            self.selected_model = "biden"
        elif index == 3:
            self.selected_model = "obin"

    def transpose_changed(self, value):
        """Met à jour la valeur d'octave sélectionnée."""
        self.transpose_value = value
        self.transpose_value_label.setText(str(value))

    def start_generation(self):
        """Démarre le processus de génération audio."""
        if not self.selected_audio_path:
            QMessageBox.warning(self, "Avertissement", "Aucun fichier audio sélectionné.")
            return

        # Désactiver les contrôles pendant la génération
        self.generate_button.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.transpose_slider.setEnabled(False)

        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Définir le chemin de sortie audio
        input_basename = os.path.splitext(os.path.basename(self.selected_audio_path))[0]
        output_dir = os.path.join(os.getcwd(), "opt", "done")
        os.makedirs(output_dir, exist_ok=True)
        self.output_audio_path = os.path.join(output_dir, f"{input_basename}_converted.wav")

        # Créer le thread de génération audio
        self.thread = QThread()
        self.worker = AudioGenerationWorker(
            model=self.selected_model,
            input_audio=self.selected_audio_path,
            transpose=self.transpose_value,
            output_audio=self.output_audio_path
        )
        self.worker.moveToThread(self.thread)

        # Connecter les signaux
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Lancer le thread
        self.thread.start()

    def on_progress(self, value):
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(value)

    def on_generation_finished(self, output_path):
        """Gestionnaire appelé lorsque la génération est terminée."""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.transpose_slider.setEnabled(True)

        # Naviguer vers la page de lecture audio
        self.navigate_to("audio_playback", audio_path=output_path)

    def on_generation_error(self, error_msg):
        """Gestionnaire appelé en cas d'erreur lors de la génération."""
        QMessageBox.critical(self, "Erreur de Génération", f"Une erreur est survenue :\n{error_msg}")
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.transpose_slider.setEnabled(True)


# ----------------------- AUDIO PLAYBACK PAGE ------------------------#

class AudioPlaybackPage(QWidget):
    def __init__(self, navigate_to, back, audio_path):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.audio_path = audio_path
        self.init_ui()
        self.init_player()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Logo ou image en haut
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("audio_icon.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Titre
        title_label = QLabel("Lecture de l'Audio Généré")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        # Label pour le chemin de l'audio
        self.audio_label = QLabel(f"Chemin de l'audio : {self.audio_path}")
        self.audio_label.setAlignment(Qt.AlignCenter)
        self.audio_label.setObjectName("file_label")
        layout.addWidget(self.audio_label)

        # Widget pour représenter l'audio
        self.audio_widget = QWidget(self)
        self.audio_widget.setObjectName("audio_widget")
        self.audio_widget.setMinimumSize(800, 150)
        layout.addWidget(self.audio_widget, alignment=Qt.AlignCenter)

        # Barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Contrôles audio
        controls_layout = QVBoxLayout()

        # Bouton Play/Pause avec icône
        self.play_button = QPushButton("🎧 Play")
        self.play_button.setObjectName("control_button")
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button, alignment=Qt.AlignCenter)

        # Contrôle du volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setObjectName("label")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(200)
        self.volume_slider.setObjectName("slider")
        self.volume_slider.valueChanged.connect(self.set_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        controls_layout.addLayout(volume_layout)

        # Navigation boutons
        navigation_layout = QHBoxLayout()

        # Bouton Relire avec icône
        replay_button = QPushButton("🔄 Relire")
        replay_button.setObjectName("control_button")
        replay_button.clicked.connect(self.replay_audio)
        navigation_layout.addWidget(replay_button)

        # Bouton Enregistrer avec icône
        save_button = QPushButton("💾 Enregistrer")
        save_button.setObjectName("control_button")
        save_button.clicked.connect(self.save_audio)
        navigation_layout.addWidget(save_button)

        # Bouton Retour avec icône
        back_button = QPushButton("⬅️ Retour")
        back_button.setObjectName("control_button")
        back_button.clicked.connect(self.stop_and_go_back)
        navigation_layout.addWidget(back_button)

        controls_layout.addLayout(navigation_layout)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def init_player(self):
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        if not os.path.exists(self.audio_path):
            QMessageBox.critical(self, "Erreur", f"Le fichier audio '{self.audio_path}' est introuvable.")
            return

        media = self.vlc_instance.media_new(self.audio_path)
        self.media_player.set_media(media)

        if sys.platform.startswith("win"):
            self.media_player.set_hwnd(int(self.audio_widget.winId()))
        elif sys.platform.startswith("linux"):
            self.media_player.set_xwindow(int(self.audio_widget.winId()))
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(self.audio_widget.winId()))

        self.media_player.play()
        self.media_player.audio_set_volume(50)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_audio_end)
        self.timer.start()

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def toggle_play(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText("▶️ Play")
        else:
            if self.media_player.get_state() == vlc.State.Ended:
                self.media_player.set_time(0)
            self.media_player.play()
            self.play_button.setText("⏸️ Pause")

    def replay_audio(self):
        self.media_player.stop()
        self.media_player.play()
        self.play_button.setText("⏸️ Pause")

    def stop_and_go_back(self):
        self.media_player.stop()
        self.back()

    def check_audio_end(self):
        if self.media_player.get_state() == vlc.State.Ended:
            self.timer.stop()
            self.play_button.setText("▶️ Play")

    def save_audio(self):
        """
        Ouvre une boîte de dialogue pour sauvegarder l'audio généré
        dans un chemin choisi par l'utilisateur.
        """
        # Par exemple, on propose un nom de fichier par défaut
        default_filename = os.path.basename(self.audio_path)
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'audio",
            default_filename,  # Chemin par défaut
            "Fichiers audio (*.wav *.mp3 *.flac);;Tous les fichiers (*.*)",
            options=options
        )

        if save_path:
            try:
                shutil.copy(self.audio_path, save_path)
                QMessageBox.information(
                    self,
                    "Audio sauvegardé",
                    f"L'audio a été sauvegardé ici :\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible de sauvegarder l'audio : {e}"
                )


# ----------------------- GENERATION VIDEO PAGE ------------------------#

class GenerationVideoPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back

        self.selected_video_path = None
        self.selected_image_path = None
        self.selected_output_dir = None

        # Thread + Worker
        self.thread = None
        self.worker = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre
        title_label = QLabel("Génération de Deepfake Vidéo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        # Image
        image_label = QLabel()
        gener_pixmap = QPixmap("deepfake_generate.png").scaled(300, 300, Qt.KeepAspectRatio)
        if gener_pixmap.isNull():
            print("Erreur : L'image 'deepfake_generate.png' est introuvable.")
        image_label.setPixmap(gener_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Boutons de sélection
        browse_layout = QVBoxLayout()

        # 1) Bouton pour parcourir la vidéo (target)
        browse_video_btn = QPushButton("Choisir la vidéo (target)")
        browse_video_btn.setObjectName("browse_button")
        browse_video_btn.clicked.connect(self.browse_video)
        browse_layout.addWidget(browse_video_btn)

        # 2) Bouton pour parcourir l’image (source)
        browse_image_btn = QPushButton("Choisir l'image (source)")
        browse_image_btn.setObjectName("browse_button")
        browse_image_btn.clicked.connect(self.browse_image)
        browse_layout.addWidget(browse_image_btn)

        # 3) Bouton pour parcourir le dossier de sortie
        browse_output_btn = QPushButton("Choisir le dossier de sortie")
        browse_output_btn.setObjectName("browse_button")
        browse_output_btn.clicked.connect(self.browse_output_folder)
        browse_layout.addWidget(browse_output_btn)

        layout.addLayout(browse_layout)

        # Bouton Générer
        self.generate_button = QPushButton("Générer")
        self.generate_button.setObjectName("generate_button")
        self.generate_button.clicked.connect(self.start_generation)
        layout.addWidget(self.generate_button, alignment=Qt.AlignCenter)

        # Barre de progression (cachée au début)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Bouton retour
        back_button = QPushButton()
        back_button.setObjectName("back_button")
        back_button.setIcon(QIcon(QPixmap("retour.png")))
        back_button.clicked.connect(self.back)
        layout.addWidget(back_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def browse_video(self):
        """Choisir la vidéo sur laquelle appliquer le deepfake."""
        dlg = QFileDialog()
        dlg.setNameFilter("Vidéos (*.mp4 *.avi *.mov *.mkv);;Tous les fichiers (*.*)")
        if dlg.exec_():
            file_path = dlg.selectedFiles()[0]
            self.selected_video_path = file_path
            QMessageBox.information(self, "Vidéo sélectionnée", f"Vidéo: {file_path}")

    def browse_image(self):
        """Choisir l'image (source)."""
        dlg = QFileDialog()
        dlg.setNameFilter("Images (*.jpg *.jpeg *.png *.bmp);;Tous les fichiers (*.*)")
        if dlg.exec_():
            file_path = dlg.selectedFiles()[0]
            self.selected_image_path = file_path
            QMessageBox.information(self, "Image sélectionnée", f"Image: {file_path}")

    def browse_output_folder(self):
        """Choisir un dossier de sortie."""
        folder_path = QFileDialog.getExistingDirectory(self, "Choisir un dossier de sortie")
        if folder_path:
            self.selected_output_dir = folder_path
            QMessageBox.information(self, "Dossier de sortie sélectionné", f"Dossier: {folder_path}")

    def start_generation(self):
        """
        Lance la génération deepfake dans un thread séparé,
        et affiche la barre de progression.
        """
        if not self.selected_video_path or not self.selected_image_path or not self.selected_output_dir:
            QMessageBox.warning(self, "Attention", 
                                "Veuillez sélectionner la vidéo, l'image et le dossier de sortie.")
            return

        # Désactiver le bouton pendant la génération
        self.generate_button.setEnabled(False)
        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Créer le Worker + Thread
        self.thread = QThread()
        self.worker = VideoGenerationWorker(
            target_path=self.selected_video_path,
            source_path=self.selected_image_path,
            output_dir=self.selected_output_dir
        )
        self.worker.moveToThread(self.thread)

        # Connecter signaux
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)

        # Nettoyage
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        # Lancer le thread
        self.thread.start()

    def on_progress(self, value):
        self.progress_bar.setValue(value)

    def on_generation_finished(self, output_file):
        """
        Appelé quand la génération est terminée avec succès.
        On bascule vers la lecture vidéo.
        """
        QMessageBox.information(self, "Deepfake généré", f"Vidéo générée : {output_file}")
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)

        # Naviguer vers la page de lecture
        self.navigate_to("video_playback", video_path=output_file, is_generated=True)

    def on_generation_error(self, error_msg):
        """
        Appelé quand il y a une erreur dans la génération.
        """
        QMessageBox.critical(self, "Erreur de génération", f"Une erreur est survenue:\n{error_msg}")
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)


# ----------------------- VIDEO PLAYBACK PAGE ------------------------#

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

        # Label pour le chemin de la vidéo
        self.video_label = QLabel(f"Lecture de la vidéo : {self.video_path}")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("file_label")
        layout.addWidget(self.video_label)

        # Widget pour afficher la vidéo
        self.video_widget = QWidget(self)
        self.video_widget.setObjectName("video_widget")
        self.video_widget.setMinimumSize(900, 600)
        layout.addWidget(self.video_widget, alignment=Qt.AlignCenter)

        # Barre de progression (initialement cachée)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Layout pour tous les contrôles
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignCenter)

        # Bouton Pause/Play
        self.play_button = QPushButton("▶️ Play")
        self.play_button.setObjectName("control_button")
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button, alignment=Qt.AlignCenter)

        # Contrôle du volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setObjectName("label")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(200)
        self.volume_slider.setObjectName("slider")
        self.volume_slider.valueChanged.connect(self.set_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        controls_layout.addLayout(volume_layout)

        # Layout pour les boutons supplémentaires
        navigation_layout = QHBoxLayout()

        # Bouton Relire avec icône
        replay_button = QPushButton("🔄 Relire")
        replay_button.setObjectName("control_button")
        replay_button.clicked.connect(self.replay_video )
        navigation_layout.addWidget(replay_button)

        # Bouton Détection
        detection_button = QPushButton("🔍 Détection")
        detection_button.setObjectName("control_button")
        detection_button.clicked.connect(self.start_detection)
        navigation_layout.addWidget(detection_button)

        # Bouton Retour
        back_button = QPushButton("⬅️ Retour")
        back_button.setObjectName("control_button")
        back_button.clicked.connect(self.stop_and_go_back)
        navigation_layout.addWidget(back_button)

        controls_layout.addLayout(navigation_layout)
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
        self.media_player.audio_set_volume(50)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_video_end)
        self.timer.start()

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)

    def toggle_play(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText("▶️ Play")
        else:
            if self.media_player.get_state() == vlc.State.Ended:
                self.media_player.set_time(0)
            self.media_player.play()
            self.play_button.setText("⏸️ Pause")

    def replay_video(self):
        self.media_player.stop()
        self.media_player.play()
        self.play_button.setText("⏸️ Pause")

    def start_detection(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Simuler le chargement progressif
        for i in range(101):
            QTimer.singleShot(i * 30, lambda value=i: self.progress_bar.setValue(value))

        # Naviguer vers la page de détection après simulation
        QTimer.singleShot(3000, lambda: self.navigate_to("detection_result"))

    def stop_and_go_back(self):
        self.timer.stop()
        self.media_player.stop()
        self.media_player.release()
        self.vlc_instance.release()
        self.back()

    def check_video_end(self):
        if self.media_player.get_state() == vlc.State.Ended:
            self.timer.stop()
            self.play_button.setText("▶️ Play")


# ----------------------- DETECTION VIDEO PAGE ------------------------#

class DetectionVideoPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.selected_video_path = None
        self.init_ui()

        # Références pour le thread et le worker
        self.thread = None
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre de la page
        title_label = QLabel("Détection de DeepFake Vidéo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        # Ajouter une image en dessous du titre
        image_label = QLabel()
        detect_pixmap = QPixmap("detect.jpg").scaled(550, 550, Qt.KeepAspectRatio)
        if detect_pixmap.isNull():
            print("Erreur : L'image 'detect.jpg' est introuvable.")
        image_label.setPixmap(detect_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Ajouter un espacement entre l'image et les boutons
        layout.addSpacing(40)

        # Boutons pour parcourir et détecter côte à côte
        button_layout = QHBoxLayout()

        # Bouton pour parcourir le disque et sélectionner une vidéo
        browse_button = QPushButton("Parcourir une vidéo")
        browse_button.setObjectName("browse_button")
        browse_button.clicked.connect(self.browse_video)
        button_layout.addWidget(browse_button)

        # Bouton Détecter avec un texte explicite
        self.detect_button = QPushButton("Lancer la détection")
        self.detect_button.setObjectName("menu_button")
        self.detect_button.clicked.connect(self.start_detection)
        self.detect_button.setEnabled(False)
        button_layout.addWidget(self.detect_button)

        layout.addLayout(button_layout)

        # Barre de progression (initialement cachée)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Navigation : Bouton retour
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()  # Espacement à gauche
        back_button = QPushButton()
        back_button.setObjectName("back_button")
        back_button.setIcon(QIcon(QPixmap("retour.png")))
        back_button.setIconSize(back_button.sizeHint())
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(back_button)
        nav_layout.addStretch()  # Espacement à droite
        layout.addLayout(nav_layout)

        # Définir le layout principal
        self.setLayout(layout)

    def browse_video(self):
        """Ouvre un QFileDialog pour sélectionner une vidéo."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Vidéos (*.mp4 *.avi *.mov *.mkv);;Tous les fichiers (*.*)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.selected_video_path = selected_file
            self.detect_button.setEnabled(True)
            QMessageBox.information(self, "Vidéo sélectionnée", f"Vidéo choisie:\n{selected_file}")

    def start_detection(self):
        """Démarre la détection dans un thread séparé."""
        if not self.selected_video_path:
            QMessageBox.warning(self, "Avertissement", "Aucune vidéo sélectionnée.")
            return

        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Désactiver le bouton pour éviter plusieurs clics
        self.detect_button.setEnabled(False)

        # Créer le Worker et le Thread
        self.worker = DetectionWorker(self.selected_video_path)
        self.thread = QThread()

        # Déplacer le worker dans le thread
        self.worker.moveToThread(self.thread)

        # Connecter les signaux du worker
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.error.connect(self.on_detection_error)

        # Connecter le signal started du thread à la méthode run du worker
        self.thread.started.connect(self.worker.run)

        # Connecter le signal finished/error du worker à quitter le thread
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # Nettoyer les références une fois le thread terminé
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        # Lancer le thread
        self.thread.start()

    def on_progress(self, value):
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(value)

    def on_detection_finished(self, result):
        """Slot appelé quand la détection est terminée."""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.detect_button.setEnabled(True)

        # Extraire la prédiction et la confiance depuis le résultat
        predicted_label, confidence = self.extract_prediction(result)

        # Naviguer vers la page de résultats
        self.navigate_to("detection_result", score=confidence, classification=predicted_label, video_path=self.selected_video_path)

    def on_detection_error(self, error_msg):
        """Slot appelé en cas d'erreur lors de la détection."""
        self.progress_bar.setVisible(False)
        self.detect_button.setEnabled(True)
        QMessageBox.critical(self, "Erreur de détection", f"Une erreur est survenue:\n{error_msg}")

    def extract_prediction(self, result):
        """
        Extrait le label Fake/Real et la confiance depuis le résultat.
        """
        predicted_label = "Inconnu"
        confidence = 0.0

        if ("video" in result and
            "name" in result["video"] and
            "pred_label" in result["video"] and
            "pred" in result["video"]):
            
            # Parcourir toutes les vidéos traitées
            for i, fname in enumerate(result["video"]["name"]):
                # Comparer avec le nom de la vidéo sélectionnée
                if fname == os.path.basename(self.selected_video_path):
                    predicted_label = result["video"]["pred_label"][i]
                    confidence = result["video"]["pred"][i]
                    break

        return predicted_label, confidence


# ----------------------- PROBABILITY BAR ------------------------#

class ProbabilityBar(QWidget):
    def __init__(self, score, classification, parent=None):
        super().__init__(parent)
        self.score = score
        self.classification = classification
        self.cursor_ratio = 1 - score
        self.setMinimumHeight(100)  # Augmentée pour l'axe
        self.setMinimumWidth(300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # Largeur totale
        w = rect.width()
        h = rect.height()

        # Détermine les bornes
        x0 = 0
        x1 = 0.40 * w
        x2 = 0.60 * w
        x3 = w
        bar_height = h - 40  # Réduit la hauteur pour laisser de la place aux axes

        # --- Dessin des segments ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(231, 76, 60))  # Rouge
        painter.drawRect(QRectF(x0, 0, x1 - x0, bar_height))
        painter.setBrush(QColor(100, 100, 100))  # Gris foncé
        painter.drawRect(QRectF(x1, 0, x2 - x1, bar_height))
        painter.setBrush(QColor(46, 204, 113))  # Vert
        painter.drawRect(QRectF(x2, 0, x3 - x2, bar_height))

        # --- Dessin du curseur ---
        cursor_x = int(w * self.cursor_ratio)
        cursor_width = 10  # Épaisseur du curseur
        cursor_rect = QRectF(
            cursor_x - (cursor_width / 2),
            0,
            cursor_width,
            bar_height
        )
        painter.setBrush(QColor(255, 255, 255))  # Curseur blanc
        painter.drawRect(cursor_rect)

        # --- Dessin des lignes reliant les graduations ---
        painter.setPen(QColor(255, 255, 255))  # Couleur blanche pour les lignes
        line_y = int(bar_height + 5)  # Position des lignes sous la barre
        line_length = 10  # Longueur des lignes

        tick_positions = [int(x0), int(w / 2), int(x3)]
        for x_pos in tick_positions:
            painter.drawLine(x_pos, line_y, x_pos, line_y + line_length)

        # --- Dessin des graduations avec les labels -1, 0, 1 ---
        painter.setFont(QFont("Arial", 12, QFont.Bold))  # Police plus grande et en gras
        label_y = line_y + line_length + 5  # Position des labels sous les lignes

        tick_labels = ["-1", "0", "1"]
        label_width = 40  # Largeur réservée pour chaque label
        for i, x_pos in enumerate(tick_positions):
            label = tick_labels[i]
            painter.drawText(
                QRectF(x_pos - label_width // 2, label_y, label_width, 20),  # Ajustement pour centrer les labels
                Qt.AlignCenter,
                label
            )

        # --- Dessin du texte "Neutre" ---
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))  # Blanc
        painter.drawText(
            QRectF(x1, 0, x2 - x1, bar_height),  # Région "Neutre"
            Qt.AlignCenter,
            "Neutre"
        )


# ----------------------- DETECTION RESULT PAGE ------------------------#

class DetectionResultPage(QWidget):
    def __init__(self, navigate_to, back, score=None, classification=None, video_path=None):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.score = score
        self.classification = classification
        self.video_path = video_path  # <-- on stocke la même vidéo que pour la détection

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Titre
        title_label = QLabel("Résultats de la Détection Vidéo")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        main_layout.addWidget(title_label)

        if self.classification is not None and self.score is not None:
            # Exemple de transformation du score (optionnel)
            score_transformed = self.transform(self.score)

            # Calcul du pourcentage
            if self.classification.upper() == "REAL":
                percentage_score = (1 - score_transformed) * 100
            else:  # FAKE
                percentage_score = score_transformed * 100

            # Texte principal
            result_text = (
                f"Classification : {self.classification}\n\n"
                f"La vidéo est {'réelle' if self.classification.upper() == 'REAL' else 'fake'}, "
                f"avec une confiance de {percentage_score:.2f}%."
            )
            result_label = QLabel(result_text)
            result_label.setAlignment(Qt.AlignCenter)
            result_label.setObjectName("result_label")
            main_layout.addWidget(result_label)

            # Ajout du smiley
            smiley_label = QLabel()
            if self.classification.upper() == "REAL":
                smiley_pixmap = QPixmap("real_smiley.png")
            else:
                smiley_pixmap = QPixmap("fake_smiley.png")

            smiley_label.setPixmap(smiley_pixmap)
            smiley_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(smiley_label)

            # Layout horizontal pour FAKE / ProbabilityBar / REAL
            bar_layout = QHBoxLayout()
            bar_layout.setSpacing(10)

            fake_label = QLabel("FAKE")
            fake_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fake_label.setObjectName("fake_label")

            real_label = QLabel("REAL")
            real_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            real_label.setObjectName("real_label")

            probability_bar = ProbabilityBar(score_transformed, self.classification)

            bar_layout.addWidget(fake_label)
            bar_layout.addWidget(probability_bar, stretch=1)
            bar_layout.addWidget(real_label)
            main_layout.addLayout(bar_layout)

        else:
            # Pas de résultat
            no_result_label = QLabel("Aucun résultat à afficher.")
            no_result_label.setAlignment(Qt.AlignCenter)
            no_result_label.setObjectName("no_result_label")
            main_layout.addWidget(no_result_label)

        # --- Boutons (Accueil / Heatmap / Retour) ---
        button_layout = QHBoxLayout()

        home_button = QPushButton("Accueil")
        home_button.setObjectName("nav_button")
        home_button.clicked.connect(lambda: self.navigate_to("home"))

        heatmap_button = QPushButton("Heatmap")
        heatmap_button.setObjectName("nav_button")
        heatmap_button.clicked.connect(self.show_heatmap)  # Méthode ci-dessous

        back_button = QPushButton("Retour")
        back_button.setObjectName("nav_button")
        back_button.clicked.connect(self.back)

        button_layout.addWidget(home_button)
        button_layout.addWidget(heatmap_button)
        button_layout.addWidget(back_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def show_heatmap(self):
        """
        Lorsque l'utilisateur clique sur le bouton "Heatmap",
        on navigue vers la page HeatmapPage en lui passant la même video_path
        que celle détectée.
        """
        if not self.video_path:
            QMessageBox.warning(self, "Info", "Aucune vidéo connue pour la heatmap.")
            return

        # On navigue vers la page "heatmap_page" en passant la vidéo
        self.navigate_to("heatmap_page", video_path=self.video_path)

    def transform(self, x: float) -> float:
        """
        Transforme une valeur x dans [0,1] (ex. votre 'score')
        en amplifiant la séparation autour de la zone neutre [0.35, 0.65].
        """
        center = 0.5
        if x < center:
            if x >= 0.35:
                # Zone neutre basse : [0.35, 0.5] -> [0.15, 0.5]
                return 0.15 + ((x - 0.35) / (0.5 - 0.35)) * (0.5 - 0.15)
            else:
                # Extrême basse : réduction de 15%
                return x * 0.85
        else:
            if x <= 0.65:
                # Zone neutre haute : [0.5, 0.65] -> [0.5, 0.85]
                return 0.5 + ((x - 0.5) / (0.65 - 0.5)) * (0.85 - 0.5)
            else:
                # Extrême haute : augmentation de 15% vers 1
                return x + ((1 - x) * 0.15)


# ----------------------- DETECTION AUDIO PAGE ------------------------#

class DetectionAudioPage(QWidget):
    def __init__(self, navigate_to, back):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.selected_audio_path = None
        self.init_ui()

        # Références pour le thread et le worker
        self.thread = None
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout()

        # Titre de la page
        title_label = QLabel("Détection de DeepFake Audio")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        # Ajouter une image en dessous du titre
        image_label = QLabel()
        detect_audio_pixmap = QPixmap("audio_main.png").scaled(550, 550, Qt.KeepAspectRatio)
        if detect_audio_pixmap.isNull():
            print("Erreur : L'image 'audio_main.png' est introuvable.")
        image_label.setPixmap(detect_audio_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Ajouter un espacement entre l'image et les boutons
        layout.addSpacing(40)

        # Boutons pour parcourir et détecter côte à côte
        button_layout = QHBoxLayout()

        # Bouton pour parcourir le disque et sélectionner un fichier audio
        browse_button = QPushButton("Parcourir un fichier audio")
        browse_button.setObjectName("browse_button")
        browse_button.clicked.connect(self.browse_audio)
        button_layout.addWidget(browse_button)

        # Bouton Détecter avec un texte explicite
        self.detect_button = QPushButton("Lancer la détection")
        self.detect_button.setObjectName("menu_button")
        self.detect_button.clicked.connect(self.start_detection)
        self.detect_button.setEnabled(False)
        button_layout.addWidget(self.detect_button)

        layout.addLayout(button_layout)

        # Barre de progression (initialement cachée)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)

        # Navigation : Bouton retour
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()  # Espacement à gauche
        back_button = QPushButton()
        back_button.setObjectName("back_button")
        back_button.setIcon(QIcon(QPixmap("retour.png")))
        back_button.setIconSize(back_button.sizeHint())
        back_button.clicked.connect(self.back)
        nav_layout.addWidget(back_button)
        nav_layout.addStretch()  # Espacement à droite
        layout.addLayout(nav_layout)

        # Définir le layout principal
        self.setLayout(layout)

    def browse_audio(self):
        """Ouvre un QFileDialog pour sélectionner un fichier audio."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audios (*.mp3 *.wav *.flac);;Tous les fichiers (*.*)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.selected_audio_path = selected_file
            self.detect_button.setEnabled(True)
            QMessageBox.information(self, "Fichier audio sélectionné", f"Fichier choisi:\n{selected_file}")

    def start_detection(self):
        """Démarre la détection audio dans un thread séparé."""
        if not self.selected_audio_path:
            QMessageBox.warning(self, "Avertissement", "Aucun fichier audio sélectionné.")
            return

        # Afficher la barre de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Désactiver le bouton pour éviter plusieurs clics
        self.detect_button.setEnabled(False)

        # Créer le Worker et le Thread
        self.worker = DetectionAudioWorker(self.selected_audio_path)
        self.thread = QThread()

        # Connecter les signaux du worker
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.error.connect(self.on_detection_error)

        # Connecter le signal started du thread à la méthode run du worker
        self.thread.started.connect(self.worker.run)

        # Connecter le signal finished/error du worker à quitter le thread
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # Nettoyer les références une fois le thread terminé
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        # Déplacer le worker dans le thread
        self.worker.moveToThread(self.thread)

        # Lancer le thread
        self.thread.start()

    def on_progress(self, value):
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(value)

    def on_detection_finished(self, score):
        """Slot appelé quand la détection audio est terminée."""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.detect_button.setEnabled(True)

        # Déterminer la classification basée sur le score
        if score < 0.5:
            classification = "REAL"
            confidence = (1 - score) * 100
        else:
            classification = "FAKE"
            confidence = score * 100

        # Naviguer vers la page de résultats
        self.navigate_to("detection_audio_result", score=score, classification=classification)

    def on_detection_error(self, error_msg):
        """Slot appelé en cas d'erreur lors de la détection."""
        self.progress_bar.setVisible(False)
        self.detect_button.setEnabled(True)
        QMessageBox.critical(self, "Erreur de détection", f"Une erreur est survenue:\n{error_msg}")


# ----------------------- DETECTION AUDIO RESULT PAGE ------------------------#

class DetectionAudioResultPage(QWidget):
    def __init__(self, navigate_to, back, score=None, classification=None):
        super().__init__()
        self.navigate_to = navigate_to
        self.back = back
        self.score = score
        self.classification = classification
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Titre
        title_label = QLabel("Résultats de la Détection Audio")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title_label")
        main_layout.addWidget(title_label)

        if self.classification is not None and self.score is not None:
            # Calcul du pourcentage (texte)
            if self.classification.upper() == "REAL":
                percentage_score = (1 - self.score) * 100
            else:  # FAKE
                percentage_score = self.score * 100

            # Label de résultat
            result_text = (
                f"Classification : {self.classification}\n\n"
                f"L'audio est {'réel' if self.classification.upper() == 'REAL' else 'deepfaké'}, "
                f"avec une confiance de {percentage_score:.2f}%."
            )
            result_label = QLabel(result_text)
            result_label.setAlignment(Qt.AlignCenter)
            result_label.setObjectName("result_label")
            main_layout.addWidget(result_label)

            # Ajout du smiley
            smiley_label = QLabel()
            # Sélection du fichier smiley selon la classification
            if self.classification.upper() == "REAL":
                smiley_pixmap = QPixmap("real_smiley.png")  # <-- Mets le chemin correct
            else:
                smiley_pixmap = QPixmap("fake_smiley.png")  # <-- Mets le chemin correct

            # Optionnel : redimensionner le smiley si besoin
            smiley_pixmap = smiley_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            smiley_label.setPixmap(smiley_pixmap)
            smiley_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(smiley_label)

            # Layout horizontal pour FAKE / ProbabilityBar / REAL
            bar_layout = QHBoxLayout()
            bar_layout.setSpacing(10)

            fake_label = QLabel("FAKE")
            fake_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fake_label.setObjectName("fake_label")

            real_label = QLabel("REAL")
            real_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            real_label.setObjectName("real_label")

            probability_bar = ProbabilityBar(self.score, self.classification)

            bar_layout.addWidget(fake_label)
            bar_layout.addWidget(probability_bar, stretch=1)
            bar_layout.addWidget(real_label)
            main_layout.addLayout(bar_layout)
        else:
            # Pas de résultat
            no_result_label = QLabel("Aucun résultat à afficher.")
            no_result_label.setAlignment(Qt.AlignCenter)
            no_result_label.setObjectName("no_result_label")
            main_layout.addWidget(no_result_label)

        # Boutons (accueil / retour)
        button_layout = QHBoxLayout()
        home_button = QPushButton("Accueil")
        home_button.setObjectName("nav_button")
        home_button.clicked.connect(lambda: self.navigate_to("home"))
        back_button = QPushButton("Retour")
        back_button.setObjectName("nav_button")
        back_button.clicked.connect(self.back)

        button_layout.addWidget(home_button)
        button_layout.addWidget(back_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


# ----------------------- MAIN WINDOW ------------------------#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepFake Application")
        self.setGeometry(100, 100, 1200, 800)

        # Styles centralisés
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a2b4c;
                color: #ffffff;
            }
            QPushButton {
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                background-color: #2c3e50;
                color: white;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #03224c;
            }
            QLabel {
                font-size: 30px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #ffffff;
                border-radius: 5px;
                padding: 5px;
            }
            /* Styles spécifiques */
            QLabel#welcome_label {
                font-size: 52px;
                font-weight: bold;
                text-shadow: 2px 2px 4px #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#title_label {
                font-size: 40px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#result_label {
                font-size: 20px;
                color: #ffffff;
            }
            QLabel#fake_label {
                font-size: 18px;
                font-weight: bold;
                color: #e74c3c;
            }
            QLabel#real_label {
                font-size: 18px;
                font-weight: bold;
                color: #2ecc71;
            }
            QLabel#file_label {
                font-size: 16px;
                color: #ffffff;
            }
            QPushButton#menu_button {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 20px;
                font-size: 24px;
                color: white;
            }
            QPushButton#menu_button:hover {
                background-color: #03224c;
            }
            QPushButton#browse_button {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton#browse_button:hover {
                background-color: #03224c;
            }
            QPushButton#generate_button {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 15px;
                font-size: 24px;
                color: white;
            }
            QPushButton#generate_button:hover {
                background-color: #03224c;
            }
            QPushButton#nav_button {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton#nav_button:hover {
                background-color: #03224c;
            }
            QPushButton#back_button {
                background-color: #FF6347;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton#back_button:hover {
                background-color: #FF4500;
            }
            QPushButton#control_button {
                background-color: #2c3e50;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                color: white;
            }
            QPushButton#control_button:hover {
                background-color: #03224c;
            }
            QPushButton#play_button {
                background-color: #1abc9c;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton#play_button:hover {
                background-color: #16a085;
            }
            QProgressBar#progress_bar {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar#progress_bar::chunk {
                background-color: #00d4ff;
                width: 10px;
            }

            QMessageBox {
                background-color: #1a2b4c; /* Fond sombre */
                color: white;             /* Texte en blanc */
                font-size: 16px;          /* Taille de la police */
                border: 2px solid #ffffff;
                border-radius: 10px;
            }

            QMessageBox QLabel {
                color: white;             /* Couleur du texte */
                font-size: 16px;          /* Taille de police pour le label */
            }

            QMessageBox QPushButton {
                background-color: #2c3e50; /* Couleur des boutons */
                color: white;              /* Texte des boutons */
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }

            QMessageBox QPushButton:hover {
                background-color: #03224c; /* Couleur au survol */
            }
        """)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.start_page = StartPage(self.navigate_to, "fond_ecran.png")
        self.stacked_widget.addWidget(self.start_page)
        self.stacked_widget.setCurrentWidget(self.start_page)

        # Définir la page de démarrage comme page initiale
        self.current_page = "start"

        # Initialisation des pages
        self.home_page = HomePage(self.navigate_to)
        self.generation_option_page = GenerationOptionPage(self.navigate_to, self.go_back)
        self.generation_page = GenerationVideoPage(self.navigate_to, self.go_back)
        self.generation_audio_page = GenerationAudioPage(self.navigate_to, self.go_back)
        self.detection_page = DetectionVideoPage(self.navigate_to, self.go_back)
        self.detection_audio_page = DetectionAudioPage(self.navigate_to, self.go_back)
        self.copyright_page = CopyrightPage(self.go_back)
        self.video_playback_page = None
        self.detection_result_page = None
        self.detection_audio_result_page = None
        self.audio_playback_page = None

        # Ajout des pages au QStackedWidget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.generation_option_page)
        self.stacked_widget.addWidget(self.generation_page)
        self.stacked_widget.addWidget(self.generation_audio_page)
        self.stacked_widget.addWidget(self.detection_page)
        self.stacked_widget.addWidget(self.detection_audio_page)
        self.stacked_widget.addWidget(self.copyright_page)
        # Ajoutez les autres pages au besoin

        self.history = []
        self.current_page = "home"

    def navigate_to(self, page, **kwargs):
        if page == "start":
            self.stacked_widget.setCurrentWidget(self.start_page)
        elif page == "home":
            self.stacked_widget.setCurrentWidget(self.home_page)
        elif page == "generation_option":
            self.stacked_widget.setCurrentWidget(self.generation_option_page)
        elif page == "generation_video":
            self.stacked_widget.setCurrentWidget(self.generation_page)
        elif page == "generation_audio":
            self.stacked_widget.setCurrentWidget(self.generation_audio_page)
        elif page == "detection":
            self.stacked_widget.setCurrentWidget(self.detection_page)
        elif page == "copyright":
            self.stacked_widget.setCurrentWidget(self.copyright_page) 
        elif page == "heatmap_page":
            video_path = kwargs.get("video_path", None)
            self.heatmap_page = HeatmapPage(self.navigate_to, self.go_back, video_path=video_path)
            self.stacked_widget.addWidget(self.heatmap_page)
            self.stacked_widget.setCurrentWidget(self.heatmap_page)
        elif page == "detection_audio":
            self.stacked_widget.setCurrentWidget(self.detection_audio_page)
        elif page == "video_playback":
            video_path = kwargs.get("video_path", "exemple_video.mp4")
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
            score = kwargs.get("score", None)
            classification = kwargs.get("classification", None)
            video_path = kwargs.get("video_path", None)
            self.detection_result_page = DetectionResultPage(
                self.navigate_to,
                self.go_back,
                score=score,
                classification=classification,
                video_path=video_path
            )
            self.stacked_widget.addWidget(self.detection_result_page)
            self.stacked_widget.setCurrentWidget(self.detection_result_page)
        elif page == "detection_audio_result":
            score = kwargs.get("score", None)
            classification = kwargs.get("classification", None)
            self.detection_audio_result_page = DetectionAudioResultPage(
                self.navigate_to,
                self.go_back,
                score=score,
                classification=classification
            )
            self.stacked_widget.addWidget(self.detection_audio_result_page)
            self.stacked_widget.setCurrentWidget(self.detection_audio_result_page)
        elif page == "audio_playback":
            audio_path = kwargs.get("audio_path", "")
            self.audio_playback_page = AudioPlaybackPage(
                self.navigate_to,
                self.go_back,
                audio_path
            )
            self.stacked_widget.addWidget(self.audio_playback_page)
            self.stacked_widget.setCurrentWidget(self.audio_playback_page)
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
            elif previous_page == "generation_option":
                self.stacked_widget.setCurrentWidget(self.generation_option_page)
            elif previous_page == "generation_video":
                self.stacked_widget.setCurrentWidget(self.generation_page)
            elif previous_page == "generation_audio":
                self.stacked_widget.setCurrentWidget(self.generation_audio_page)
            elif previous_page == "detection":
                self.stacked_widget.setCurrentWidget(self.detection_page)
            elif previous_page == "detection_audio":
                self.stacked_widget.setCurrentWidget(self.detection_audio_page)
            elif previous_page == "detection_result":
                self.stacked_widget.setCurrentWidget(self.detection_result_page)
            elif previous_page == "detection_audio_result":
                self.stacked_widget.setCurrentWidget(self.detection_audio_result_page)
            elif previous_page == "copyright":
                self.stacked_widget.setCurrentWidget(self.copyright_page) 
            elif previous_page == "video_playback":
                self.stacked_widget.setCurrentWidget(self.video_playback_page)
            elif previous_page == "audio_playback":
                self.stacked_widget.setCurrentWidget(self.audio_playback_page)
            elif previous_page == "heatmap_page":
                self.stacked_widget.setCurrentWidget(self.heatmap_page)
        else:
            QMessageBox.information(self, "Retour", "Aucune page précédente.")


# ----------------------- APPLICATION ------------------------#

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

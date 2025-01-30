from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import time
import traceback


class DetectionWorker(QObject):
    """
    Worker pour exécuter la fonction de détection dans un thread séparé.
    """
    finished = pyqtSignal(dict)  # Signal émis une fois la détection terminée avec les résultats.
    error = pyqtSignal(str)      # Signal émis en cas d'erreur avec un message.
    progress = pyqtSignal(int)   # Signal pour mettre à jour la barre de progression.

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    @pyqtSlot()
    def run(self):
        """
        Méthode appelée automatiquement quand le thread démarre.
        """
        try:
            from detection.GenConViT.prediction import vids
            from detection.GenConViT.model.pred_func import real_or_fake
            import os

            # Définir le chemin racine (dossier de la vidéo)
            root_dir = os.path.dirname(self.video_path)

            # Étape 1 : Chargement des modèles (20% de progression)
            self.progress.emit(10)
            time.sleep(0.5)  # Simulez une petite attente pour voir la progression
            self.progress.emit(20)

            # Étape 2 : Préparation des données (50% de progression)
            time.sleep(0.5)  # Simulez une autre attente
            self.progress.emit(50)

            # Étape 3 : Lancement de la détection
            result = vids(
                ed_weight="genconvit_ed_inference",
                vae_weight="genconvit_vae_inference",
                root_dir=root_dir,
                dataset=None,
                num_frames=20,
                net="genconvit",
                fp16=False
            )
            time.sleep(1)  # Simulez une autre étape pour voir la progression
            self.progress.emit(90)

            # Étape 4 : Finalisation (100% de progression)
            time.sleep(0.5)
            self.progress.emit(100)

            # Émettre les résultats une fois terminé
            self.finished.emit(result)

        except Exception as e:
            # En cas d'erreur, émettez un signal avec le message d'erreur
            error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.error.emit(error_msg)

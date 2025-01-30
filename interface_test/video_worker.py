from PyQt5.QtCore import QObject, pyqtSignal
import subprocess
import shlex
import os

class VideoGenerationWorker(QObject):
    progress = pyqtSignal(int)  # Pour la barre de progression
    finished = pyqtSignal(str)  # Chemin de la vidéo générée
    error = pyqtSignal(str)     # Message d'erreur

    def __init__(self, target_path, source_path, output_dir):
        super().__init__()
        self.target_path = target_path
        self.source_path = source_path
        self.output_dir = output_dir

    def run(self):
        """
        Lance la génération DeepFake vidéo via run.py, en mode unbuffered (-u)
        afin que la sortie standard ne soit pas retardée.
        On lit stdout et stderr en temps réel pour potentiellement mettre à jour
        la barre de progression ou afficher des infos.
        """

        # 1) Construction du nom du fichier de sortie
        base_name = os.path.splitext(os.path.basename(self.target_path))[0]
        output_file = os.path.join(self.output_dir, f"{base_name}_deepfake.mp4")

        # 2) Construction de la commande
        # Remarquez le "python -u" pour éviter les buffers sur la sortie
        command = (
            f"python -u run.py "
            f"--target \"{self.target_path}\" "
            f"--output-video-quality 0 "
            f"--source \"{self.source_path}\" "
            f"-o \"{output_file}\" "
            f"--execution-provider cpu "
            f"--frame-processor face_swapper face_enhancer "
            f"--output-video-encoder libx264 "
            f"--temp-frame-quality 0 "
            f"--skip-audio "
            f"--keep-fps "
            f"--many-faces"
        )

        print("[VideoGenerationWorker] Commande utilisée :", command)

        # 3) Dossier d’exécution (important)
        roop_video_dir = r"C:\Users\khoze\Desktop\M2 ISI\PFE\Deepfake-PFE-generation\generation\Roop_video"

        # 4) Lancement du processus
        process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=roop_video_dir,
        shell=True
    )

        # Au lieu du while True, on attend la fin d’un coup :
        stdout_data, stderr_data = process.communicate()

        # Afficher tout (debug)
        print("===== STDOUT =====\n", stdout_data)
        print("===== STDERR =====\n", stderr_data)

        return_code = process.returncode

        if return_code == 0:
            self.progress.emit(100)
            self.finished.emit(output_file)
        else:
            msg = f"Le processus s'est terminé avec le code {return_code}\n{stderr_data}"
            self.error.emit(msg)

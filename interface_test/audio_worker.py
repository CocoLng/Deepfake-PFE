from PyQt5.QtCore import QObject, pyqtSignal
import subprocess
import shlex
import os

class AudioGenerationWorker(QObject):
    progress = pyqtSignal(int)  # Pour la barre de progression
    finished = pyqtSignal(str)  # Chemin de l'audio généré
    error = pyqtSignal(str)     # Message d'erreur

    def __init__(self, model, input_audio, transpose, output_audio):
        super().__init__()
        self.model = model
        self.input_audio = input_audio
        self.transpose = transpose
        self.output_audio = output_audio

    def run(self):
        
        # Commande à exécuter
        command = f"python -u rvc_inference_v2.py --model \"{self.model}\" --input \"{self.input_audio}\" --transpose \"{self.transpose}\" --output \"{self.output_audio}\""
        print("Command:", command)

        # Démarrer le processus
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=r"C:\Users\khoze\Desktop\M2 ISI\PFE\Deepfake-PFE-generation\generation\Retrieval-based-Voice-Conversion-WebUI"
        )

        # Lire la sortie et les erreurs
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                print("STDOUT:", line.strip())
                # self.progress.emit(...) si vous voulez un avancement simulé

            # Lire stderr aussi, mais de préférence dans un autre thread ou en asynchrone
            err_line = process.stderr.readline()
            if err_line:
                print("STDERR:", err_line.strip())

        rc = process.poll()
        if rc == 0:
            self.finished.emit(self.output_audio)
        else:
            self.error.emit(f"Le processus s'est terminé avec le code {rc}")

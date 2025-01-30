from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class DetectionAudioWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(float)  # Envoie le score de prédiction
    error = pyqtSignal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def run(self):
        try:
            from inference_interface import predict_file
            self.progress.emit(10)
            # Simuler une progression
            QThread.sleep(1)
            self.progress.emit(30)
            result = predict_file(self.audio_path)
            if result is None:
                self.error.emit("La détection a échoué. Veuillez réessayer.")
                return
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

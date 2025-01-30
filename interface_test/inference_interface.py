import numpy as np
import librosa
from tensorflow.keras.models import load_model
import cv2
import argparse

SAMPLE_RATE = 16000
N_MELS = 224

model = load_model("detection_audio/final_model.h5")

def process_audio(file_path):
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    target_length = int(5 * sr)
    audio = audio[:target_length]
    
    mel_spec = librosa.feature.melspectrogram(
    y=audio,
    sr=sr,
    n_mels=224,
    hop_length=358,  # Modifié pour obtenir 224 frames
    n_fft=2048
)
    mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec = np.stack([mel_spec] * 3, axis=-1)
    return mel_spec

def predict_file(file_path):
   try:
       mel_spec = process_audio(file_path)
       if mel_spec is None:
           return None
       mel_spec = np.expand_dims(mel_spec, axis=0)
       prediction = model.predict(mel_spec)
       return prediction[0][1]
       
   except Exception as e:
       print(f"Erreur lors de l'inférence: {e}")
       return None

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Détection de deepfake audio')
   parser.add_argument('fichier_audio', type=str, help='Chemin vers le fichier audio à analyser (.wav, .mp3, .flac)')
   args = parser.parse_args()
   
   if not args.fichier_audio.lower().endswith(('.wav', '.mp3', '.flac')):
       print("Erreur: Le fichier doit être au format .wav, .mp3 ou .flac")
       exit(1)

   result = predict_file(args.fichier_audio)
   if result is not None:
       print(f"Probabilité que l'audio soit un deepfake : {result:.2%}")

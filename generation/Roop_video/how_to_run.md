

# acceder a roop

cd video_generation/roop

# Installer les dépendances
pip install -r requirements.txt


# Télécharger le modèle inswapper_128.onnx
wget https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx -O inswapper_128.onnx

# déplacer le modèle dans models

mv inswapper_128.onnx ./models

# Installer onnxruntime pour GPU

pip uninstall -y -q onnxruntime
pip install /onnxruntime_gpu-1.16.3-cp310-cp310-linux_x86_64.whl



# Lancer le script Python
avant de lancer la commande importer l'image source et la video 

python run.py --target video.mp4 --output-video-quality 0 --source macron.jpg -o /swapped.mp4 --execution-provider cuda --frame-processor face_swapper face_enhancer --output-video-encoder libx264 --temp-frame-quality 0 --skip-audio --keep-fps --many-faces

in --target place the target video
in --source place the source image (an image of macron in our case)
# construire la video a partir des frames resultants

python video.py --images_dir "temp/video" --output_video "/sortie.mp4" --fps 30



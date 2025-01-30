import os
import numpy as np
import cv2
import torch
import dlib
import face_recognition
from torchvision import transforms
from tqdm import tqdm
from detection.GenConViT_heatmap.dataset.loader import normalize_data
from detection.GenConViT_heatmap.model.config import load_config
from detection.GenConViT_heatmap.model.genconvit import GenConViT
from decord import VideoReader, cpu

device = "cuda" if torch.cuda.is_available() else "cpu"


def load_genconvit(config, net, ed_weight, vae_weight, fp16):
    model = GenConViT(
        config,
        ed= ed_weight,
        vae= vae_weight, 
        net=net,
        fp16=fp16
    )

    model.to(device)
    model.eval()
    if fp16:
        model.half()

    return model


def face_rec(frames, p=None, klass=None):
    """
    Detect faces in the given frames, crop them to 224x224 in RGB,
    and also store bounding boxes & the frame index from which each face is extracted.

    Returns:
        (faces_array, boxes, frame_indices) or ([], [], []) if none found.
    """
    temp_face = np.zeros((len(frames), 224, 224, 3), dtype=np.uint8)
    boxes = []         # Will hold (top, right, bottom, left) for each face
    frame_indices = [] # Will hold which frame index (i) the face came from
    count = 0
    mod = "cnn" if dlib.DLIB_USE_CUDA else "hog"

    for i, frame in tqdm(enumerate(frames), total=len(frames)):
        # Convert frame to BGR for face_recognition
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        face_locations = face_recognition.face_locations(
            frame_bgr, number_of_times_to_upsample=0, model=mod
        )

        for face_location in face_locations:
            if count < len(frames):
                top, right, bottom, left = face_location

                # Crop & resize the face region
                face_image = frame_bgr[top:bottom, left:right]
                face_image = cv2.resize(
                    face_image, (224, 224), interpolation=cv2.INTER_AREA
                )
                # Convert back to RGB
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

                temp_face[count] = face_image
                boxes.append((top, right, bottom, left))
                frame_indices.append(i)
                count += 1
            else:
                break

    if count == 0:
        return ([], [], [])
    else:
        return (temp_face[:count], boxes, frame_indices)



def preprocess_frame(frame):
    df_tensor = torch.tensor(frame, device=device).float()
    df_tensor = df_tensor.permute((0, 3, 1, 2))

    for i in range(len(df_tensor)):
        df_tensor[i] = normalize_data()["vid"](df_tensor[i] / 255.0)

    return df_tensor


def pred_vid(df, model):
    with torch.no_grad():
        return max_prediction_value(torch.sigmoid(model(df).squeeze()))


def max_prediction_value(y_pred):
    # Finds the index and value of the maximum prediction value.
    mean_val = torch.mean(y_pred, dim=0)
    return (
        torch.argmax(mean_val).item(),
        mean_val[0].item()
        if mean_val[0] > mean_val[1]
        else abs(1 - mean_val[1]).item(),
    )


def real_or_fake(prediction):
    return {0: "REAL", 1: "FAKE"}[prediction ^ 1]


def extract_frames(video_file, frames_nums=15):
    vr = VideoReader(video_file, ctx=cpu(0))
    step_size = max(1, len(vr) // frames_nums)  # Calculate the step size between frames
    return vr.get_batch(
        list(range(0, len(vr), step_size))[:frames_nums]
    ).asnumpy()  # seek frames with step_size


def df_face(vid, num_frames, net):
    """
    Extract frames from the video, detect faces, and return:
      - all original frames
      - preprocessed face tensor(s)
      - bounding boxes for each face
      - frame indices for each face
    """
    # 1) Extract frames
    frames = extract_frames(vid, num_frames)

    # 2) Detect faces
    face_array, boxes, frame_indices = face_rec(frames)

    # 3) Preprocess if at least one face found
    if len(face_array) > 0:
        # Convert from (count, 224, 224, 3) -> preprocessed tensor
        df = preprocess_frame(face_array)
        return frames, df, boxes, frame_indices
    else:
        # Return empty placeholders
        return [], [], [], []


def is_video(vid):
    print('IS FILE', os.path.isfile(vid))
    return os.path.isfile(vid) and vid.endswith(
        tuple([".avi", ".mp4", ".mpg", ".mpeg", ".mov"])
    )


def set_result():
    return {
        "video": {
            "name": [],
            "pred": [],
            "klass": [],
            "pred_label": [],
            "correct_label": [],
        }
    }


def store_result(
    result, filename, y, y_val, klass, correct_label=None, compression=None
):
    result["video"]["name"].append(filename)
    result["video"]["pred"].append(y_val)
    result["video"]["klass"].append(klass.lower())
    result["video"]["pred_label"].append(real_or_fake(y))

    if correct_label is not None:
        result["video"]["correct_label"].append(correct_label)

    if compression is not None:
        result["video"]["compression"].append(compression)

    return result

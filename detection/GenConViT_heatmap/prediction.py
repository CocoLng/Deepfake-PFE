import os
import argparse
import json
from time import perf_counter
from datetime import datetime
import torch
import torch.nn as nn
import numpy as np
import cv2
from captum.attr import GuidedBackprop
from model.config import load_config
from model.pred_func import load_genconvit, df_face, is_video, set_result, store_result, real_or_fake

class FakeLogitWrapper(nn.Module):
    def __init__(self, original_model, fake_index=1):
        super().__init__()
        self.model = original_model
        self.fake_index = fake_index
    
    def forward(self, x):
        out = self.model(x)
        if isinstance(out, tuple):
            logits = out[0]
        else:
            logits = out
        return logits[:, self.fake_index]

def compute_guided_backprop_saliency(wrapped_model, input_tensor):
    gbp = GuidedBackprop(wrapped_model)
    attributions = gbp.attribute(input_tensor, target=None)
    return attributions[0]

def predict(vid_file, model, net, result, num_frames=15, klass="uncategorized", count=0, accuracy=-1, correct_label=None, compression=None):
    count += 1
    print(f"\n[{count}] Processing: {vid_file}")
    frames, df_tensor, boxes, frame_indices = df_face(vid_file, num_frames, net)
    if len(df_tensor) == 0:
        y, y_val = 0, 0.5
        store_result(result, os.path.basename(vid_file), y, y_val, klass, correct_label, compression)
        if accuracy > -1 and correct_label is not None:
            if correct_label == real_or_fake(y):
                accuracy += 1
        print(f"=> No faces => labeled {real_or_fake(y)}")
        return result, accuracy, count, [y, y_val]
    df_tensor = df_tensor.float()
    with torch.no_grad():
        out = model(df_tensor)
        if isinstance(out, tuple):
            logits = out[0]
        else:
            logits = out
        probs = torch.sigmoid(logits)
        mean_val = probs.mean(dim=0)
        y = torch.argmax(mean_val).item()
        y_val = mean_val[y].item()
    store_result(result, os.path.basename(vid_file), y, y_val, klass, correct_label, compression)
    pred_label = real_or_fake(y)
    print(f"Video => {pred_label} Score={y_val:.3f}")
    if accuracy > -1 and correct_label is not None:
        if correct_label == pred_label:
            accuracy += 1
        print(f"accuracy={accuracy}/{count}")
    is_fake = (pred_label == "FAKE")
    wrapped = FakeLogitWrapper(model)
    os.makedirs("heatmaps", exist_ok=True)
    for i in range(len(df_tensor)):
        face_in = df_tensor[i].unsqueeze(0)
        face_in.requires_grad_()
        attributions = compute_guided_backprop_saliency(wrapped, face_in)
        saliency = attributions.sum(dim=0).abs()
        if is_fake:
            mean_ = saliency.mean().item()
            std_ = saliency.std().item()
            threshold_val = mean_ + 0.5 * std_
            saliency[saliency < threshold_val] = 0.0
            saliency *= 3.0
            sal_np = saliency.cpu().numpy()
            sal_np = cv2.GaussianBlur(sal_np, (15,15), 5.0)
            saliency = torch.from_numpy(sal_np).float().to(saliency.device)
        smin, smax = saliency.min(), saliency.max()
        if smax> smin:
            saliency = (saliency - smin)/(smax - smin)
        sal_np = saliency.cpu().numpy()
        heatmap = cv2.applyColorMap((sal_np*255).astype(np.uint8), cv2.COLORMAP_JET).astype(np.float32)
        top, right, bottom, left = boxes[i]
        frame_idx = frame_indices[i]
        if frame_idx >= len(frames):
            continue
        orig_frame_bgr = cv2.cvtColor(frames[frame_idx], cv2.COLOR_RGB2BGR).astype(np.float32)
        face_bgr = orig_frame_bgr[top:bottom, left:right]
        if face_bgr.size==0:
            continue
        face_h, face_w = face_bgr.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (face_w, face_h), interpolation=cv2.INTER_AREA)
        alpha = 0.8
        overlay = cv2.addWeighted(face_bgr, alpha, heatmap_resized, 1 - alpha, 0)
        overlay = np.clip(overlay, 0, 255).astype(np.uint8)
        orig_frame_bgr[top:bottom, left:right] = overlay
        final_frame = cv2.cvtColor(orig_frame_bgr, cv2.COLOR_BGR2RGB)
        out_name = f"gbmap_{os.path.basename(vid_file)}_vid{count}_face{i}.jpg"
        out_path = os.path.join("heatmaps", out_name)
        cv2.imwrite(out_path, final_frame[..., ::-1])
        print(f"Saved => {out_path}")
    return result, accuracy, count, [y, y_val]

def vids(ed_weight, vae_weight, root_dir="sample_prediction_data", dataset=None, num_frames=15, net=None, fp16=False):
    config = load_config()
    model = load_genconvit(config, net, ed_weight, vae_weight, fp16)
    result = set_result()
    accuracy = 0
    count = 0
    for fname in os.listdir(root_dir):
        path = os.path.join(root_dir, fname)
        if not is_video(path):
            print(f"Skipping non-video: {path}")
            continue
        result, accuracy, count, _ = predict(path, model, net, result, num_frames, klass="uncategorized", count=count, accuracy=accuracy, correct_label=None, compression=None)
    print(f"\nFinished => {count} videos, accuracy={accuracy}/{count}")
    return result

def main():
    parser = argparse.ArgumentParser("Guided Backprop => Full Heatmap for FAKE, Transparent for REAL")
    parser.add_argument("--p", type=str, default="sample_prediction_data")
    parser.add_argument("--f", type=int, default=15)
    parser.add_argument("--d", type=str, default="other")
    parser.add_argument("--e", nargs='?', const='genconvit_ed_inference', default='genconvit_ed_inference')
    parser.add_argument("--v", '--value', nargs='?', const='genconvit_vae_inference', default='genconvit_vae_inference')
    parser.add_argument("--fp16", action="store_true")
    args = parser.parse_args()
    root_dir = args.p
    dataset = args.d
    ed_weight = args.e
    vae_weight = args.v
    fp16 = args.fp16
    num_frames = args.f
    net = 'genconvit'
    if ed_weight and not vae_weight:
        net = 'ed'
    elif vae_weight and not ed_weight:
        net = 'vae'
    result = vids(ed_weight, vae_weight, root_dir, dataset, num_frames, net, fp16)
    os.makedirs("result", exist_ok=True)
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = os.path.join("result", f"prediction_gb_{dataset}_{net}_{now_str}.json")
    with open(out_json, "w") as f:
        json.dump(result, f)
    print(f"\nResults => {out_json}")

if __name__ == "__main__":
    start_t = perf_counter()
    main()
    end_t = perf_counter()
    print(f"\nTotal time: {end_t - start_t:.2f} seconds")

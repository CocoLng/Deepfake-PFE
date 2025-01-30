import os
import sys
import torch
import argparse
from multiprocessing import cpu_count
from scipy.io import wavfile

now_dir = os.getcwd()
sys.path.append(now_dir)

# Import RVC modules
from infer.modules.vc.modules import VC
from configs.config import Config
from fairseq import checkpoint_utils

def get_absolute_path(path):
    """Convert relative path to absolute path if necessary"""
    if os.path.isabs(path):
        return path
    return os.path.join(now_dir, path)

def get_available_models():
    """Get list of available models in the weights directory"""
    weights_dir = os.path.join(now_dir, "assets", "weights")
    if not os.path.exists(weights_dir):
        print(f"Warning: Weights directory not found at {weights_dir}")
        return []
    
    models = [os.path.splitext(f)[0] for f in os.listdir(weights_dir) 
             if f.endswith('.pth')]
    return models

def get_model_paths(model_name):
    """Get model and index paths based on model name"""
    # Base paths
    base_path = os.path.join(now_dir)
    weights_dir = os.path.join(base_path, "assets", "weights")
    logs_dir = os.path.join(base_path, "logs")
    
    # Get available models
    available_models = get_available_models()
    
    if not available_models:
        raise FileNotFoundError("No models found in weights directory")
    
    if model_name not in available_models:
        suggestions = [m for m in available_models if model_name in m]
        error_msg = f"Model '{model_name}' not found.\nAvailable models: {', '.join(available_models)}"
        if suggestions:
            error_msg += f"\nDid you mean: {', '.join(suggestions)}?"
        raise FileNotFoundError(error_msg)
    
    # Model specific paths
    model_path = os.path.join(weights_dir, f"{model_name}.pth")
    model_log_dir = os.path.join(logs_dir, model_name)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Handle different index configurations
    if model_name.lower() == "macron":
        index_path = os.path.join(model_log_dir, f"added_IVF256_Flat_nprobe_1_{model_name}_v2.index")
    elif model_name.lower() == "trump":
        index_path = os.path.join(model_log_dir, f"added_IVF3863_Flat_nprobe_1_{model_name}_v2.index")
    elif model_name.lower() == "biden":
        index_path = os.path.join(model_log_dir, f"added_IVF2606_Flat_nprobe_1_{model_name}_v2.index")
    elif model_name.lower() == "obin":
        index_path = os.path.join(model_log_dir, f"added_IVF2361_Flat_nprobe_1_{model_name}_v2.index")
    else:
        # Try to find any matching index file
        if not os.path.exists(model_log_dir):
            raise FileNotFoundError(f"Model log directory not found: {model_log_dir}")
        
        index_files = [f for f in os.listdir(model_log_dir) if f.endswith('.index') and model_name in f]
        if not index_files:
            raise FileNotFoundError(f"No index file found for model {model_name} in {model_log_dir}")
        
        # Use the first matching index file
        index_path = os.path.join(model_log_dir, index_files[0])
        print(f"Using detected index file: {index_files[0]}")
    
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index file not found: {index_path}")
        
    return model_path, index_path

class InferenceConfig:
    def __init__(self, 
                 transpose=0,
                 input_path=None,
                 index_path=None,
                 f0method="rmvpe",
                 output_path=None,
                 model_path=None,
                 index_rate=0.7,
                 device="cpu",
                 is_half=False):
        self.transpose = transpose
        self.input_path = get_absolute_path(input_path) if input_path else None
        self.index_path = get_absolute_path(index_path) if index_path else None
        self.f0method = f0method
        self.output_path = get_absolute_path(output_path) if output_path else None
        self.model_path = get_absolute_path(model_path) if model_path else None
        self.index_rate = index_rate
        self.device = device
        self.is_half = is_half

class Inference:
    def __init__(self, config):
        self.config = config
        self.rvc_config = Config()
        self.weight_root = os.path.dirname(self.config.model_path)
        self.rvc_config.weight_root = self.weight_root
        
        # Set environment variables
        os.environ["weight_root"] = self.weight_root
        self.index_root = os.path.dirname(os.path.dirname(self.config.index_path))
        os.environ["index_root"] = self.index_root
        os.environ["rmvpe_root"] = os.path.join(now_dir, "assets/rmvpe")
        
        print(f"Environment variables set:")
        print(f"weight_root: {os.environ['weight_root']}")
        print(f"index_root: {os.environ['index_root']}")
        print(f"rmvpe_root: {os.environ['rmvpe_root']}")
        self.vc = VC(self.rvc_config)
        self.hubert_model = None

    def load_hubert(self):
        hubert_path = os.path.join(now_dir, "assets/hubert/hubert_base.pt")
        if not os.path.exists(hubert_path):
            raise FileNotFoundError(f"Hubert model not found at: {hubert_path}")
            
        models, saved_cfg, task = checkpoint_utils.load_model_ensemble_and_task(
            [hubert_path],
            suffix="",
        )
        self.hubert_model = models[0]
        self.hubert_model = self.hubert_model.to(self.config.device)
        if self.config.is_half:
            self.hubert_model = self.hubert_model.half()
        else:
            self.hubert_model = self.hubert_model.float()
        self.hubert_model.eval()

    def run_inference(self):
        print(f"Loading model from: {self.config.model_path}")
        
        if not os.path.exists(self.config.model_path):
            raise FileNotFoundError(f"Model file not found: {self.config.model_path}")
        
        model_filename = os.path.basename(self.config.model_path)
        print(f"Initializing voice conversion with model: {model_filename}")
        self.vc.get_vc(model_filename)

        if self.hubert_model is None:
            self.load_hubert()

        print("Processing audio...")
        print("Input path exists:", os.path.exists(self.config.input_path))
        print("Index path exists:", os.path.exists(self.config.index_path))
        print("RMVPE model exists:", os.path.exists(os.path.join(os.environ["rmvpe_root"], "rmvpe.pt")))
        
        rmvpe_path = os.path.join(os.environ["rmvpe_root"], "rmvpe.pt")
        if not os.path.exists(rmvpe_path):
            raise FileNotFoundError(f"RMVPE model not found at: {rmvpe_path}")
        
        result = self.vc.vc_single(
            0,                      # sid
            self.config.input_path, # input audio path
            self.config.transpose,  # transpose
            None,                   # f0 file (optional)
            self.config.f0method,   # f0 method
            self.config.index_path, # feature index path
            None,                   # feature index path 2 (optional)
            self.config.index_rate, # feature ratio
            3,                      # filter radius (default)
            0,                      # resample sr (default)
            1,                      # rms mix rate (default)
            0.33,                   # protect (default)
        )

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config.output_path), exist_ok=True)
        
        if isinstance(result, tuple):
            status_message, audio_tuple = result
            if isinstance(audio_tuple, tuple) and len(audio_tuple) == 2:
                sr, audio_data = audio_tuple
                if audio_data is not None:
                    wavfile.write(self.config.output_path, sr, audio_data)
                    print(f"Audio saved to {self.config.output_path}")
                    print(f"Status: {status_message}")
                else:
                    print("Error: Audio data is None")
            else:
                print(f"Error: Unexpected audio tuple format: {audio_tuple}")
        else:
            print(f"Error during inference: {result}")

def main():
    # Override sys.argv temporarily to prevent conflict with Config's argument parser
    original_argv = sys.argv
    sys.argv = [sys.argv[0]]  # Keep only the script name
    _ = Config()  # Initialize Config with default arguments
    sys.argv = original_argv  # Restore original arguments

    # Parse our custom arguments
    parser = argparse.ArgumentParser(description='RVC Inference Script')
    parser.add_argument('--model', type=str, required=True, help='Model name (e.g., "trump", "macron")')
    parser.add_argument('--transpose', type=int, default=0, help='Transpose value (default: 0)')
    parser.add_argument('--input', type=str, required=True, help='Input audio file path')
    parser.add_argument('--output', type=str, help='Output audio file path (optional)')
    parser.add_argument('--device', type=str, default='cpu', help='Device to use (default: cpu)')
    parser.add_argument('--half', action='store_true', help='Use half precision')
    args = parser.parse_args()
    
    # Get model and index paths based on model name
    model_path, index_path = get_model_paths(args.model)
    
    # If output path is not specified, create one based on input path
    if args.output is None:
        input_basename = os.path.splitext(os.path.basename(args.input))[0]
        output_dir = os.path.join(now_dir, "opt", "done")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{input_basename}_converted.wav")
    else:
        output_path = args.output

    # Configuration for inference
    config = InferenceConfig(
        transpose=args.transpose,
        input_path=args.input,
        index_path=index_path,
        f0method="rmvpe",
        output_path=output_path,
        model_path=model_path,
        index_rate=0.7,
        device=args.device,
        is_half=args.half
    )

    print("Working directory:", now_dir)
    inferencer = Inference(config)
    print("Weight root:", inferencer.weight_root)
    print("Model file:", config.model_path)
    print("Input path:", config.input_path)
    print("Index path:", config.index_path)
    print("Output path:", config.output_path)

    # Run inference
    inferencer.run_inference()

if __name__ == "__main__":
    main()
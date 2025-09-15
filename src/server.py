import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torch
import os
import time
from .common import VoiceMapper

def main():
    args = parse_args()

    # Normalize potential 'mpx' typo to 'mps'
    if args.device.lower() == "mpx":
        print("Note: device 'mpx' detected, treating it as 'mps'.")
        args.device = "mps"

    # Validate mps availability if requested
    if args.device == "mps" and not torch.backends.mps.is_available():
        print("Warning: MPS not available. Falling back to CPU.")
        args.device = "cpu"

    print(f"Using device: {args.device}")

    # Initialize voice mapper
    voice_mapper = VoiceMapper()
    
    # Check if txt file exists
    if not os.path.exists(args.txt_path):
        print(f"Error: txt file not found: {args.txt_path}")
        return
    
    # Read and parse txt file
    print(f"Reading script from: {args.txt_path}")
    with open(args.txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    voice_path, lang = voice_mapper.get_voice_path_and_lang(args.speaker_name)
    print(f"Speaker '{args.speaker_name}' -> Voice: {os.path.basename(voice_path)}")

    print(f"Loading model")
    model = None
    extra_args = {}
    if lang == 'en':
        model = ChatterboxTTS.from_pretrained(device=args.device)
    else:
        model = ChatterboxMultilingualTTS.from_pretrained(device=args.device)
        extra_args['language_id'] = lang
    
    print(f"Starting generation with cfg_scale: {args.cfg_scale}")

    # Generate audio
    start_time = time.time()
    wav = model.generate(txt_content, audio_prompt_path=voice_path, cfg_weight=args.cfg_scale, **extra_args)
    generation_time = time.time() - start_time
    print(f"Generation time: {generation_time:.2f} seconds")

    ta.save(os.path.join(args.output_dir, "output.wav"), wav, model.sr)
    print(f"Saved output to ${os.path.join(args.output_dir, 'output.wav')}")

if __name__ == "__main__":
    main()

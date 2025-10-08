import os
import json
import uuid
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
import torchaudio as ta

# Try to import actual models, fall back to mock models if not available
try:
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    USE_MOCK = False
    print("Using actual Chatterbox TTS models")
except ImportError:
    print("Chatterbox TTS not available, using mock models")
    from .mock_tts import MockChatterboxTTS as ChatterboxTTS
    from .mock_tts import MockChatterboxMultilingualTTS as ChatterboxMultilingualTTS
    USE_MOCK = True

from .common import VoiceMapper

app = Flask(__name__)
CORS(app)

# Configuration
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(os.path.dirname(__file__), '..', 'outputs'))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize voice mapper
voice_mapper = VoiceMapper()

# Initialize models dictionary to cache models
models = {}

def get_model(device="cpu", lang="en"):
    """Get or initialize TTS model"""
    key = f"{device}_{lang}"
    if key not in models:
        print(f"Initializing model for {lang} on {device}")
        if lang == 'en':
            models[key] = ChatterboxTTS.from_pretrained(device=device)
        else:
            models[key] = ChatterboxMultilingualTTS.from_pretrained(device=device)
    return models[key]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voices')
def get_voices():
    """Get available voices"""
    global voice_mapper
    voices = []
    
    # Debug print to see the structure of voice_presets
    print("Voice presets structure:", type(voice_mapper.voice_presets))
    print("Voice presets keys:", list(voice_mapper.voice_presets.keys())[:5] if voice_mapper.voice_presets else [])
    print("Voice presets first item:", next(iter(voice_mapper.voice_presets.items())) if voice_mapper.voice_presets else None)
    
    # Check if voices directory exists and create it if not
    voices_dir = os.path.join(os.path.dirname(__file__), "voices")
    if not os.path.exists(voices_dir):
        print(f"Creating voices directory at {voices_dir}")
        os.makedirs(voices_dir, exist_ok=True)
        
        # Copy voice files from project root if they exist
        project_voices_dir = os.path.join(os.path.dirname(__file__), "..", "voices")
        if os.path.exists(project_voices_dir):
            print(f"Copying voices from {project_voices_dir} to {voices_dir}")
            import shutil
            for voice_file in os.listdir(project_voices_dir):
                if voice_file.endswith('.wav'):
                    src = os.path.join(project_voices_dir, voice_file)
                    dst = os.path.join(voices_dir, voice_file)
                    shutil.copy2(src, dst)
                    print(f"Copied {src} to {dst}")
    
    # Reinitialize voice mapper to ensure it picks up any new voices
    voice_mapper = VoiceMapper()
    
    try:
        # Handle different possible structures of voice_presets
        for name, value in voice_mapper.voice_presets.items():
            if isinstance(value, tuple) and len(value) == 2:
                # Structure is {name: (path, lang_code)}
                path, lang_code = value
                display_name = name
                if lang_code:
                    display_name = f"{lang_code.upper()} - {name}"
            elif isinstance(value, str):
                # Structure is {name: path}
                path = value
                lang_code = None
                display_name = name
                # Try to extract language code from name
                if '-' in name:
                    parts = name.split('-')
                    lang_code = parts[0]
                    display_name = f"{lang_code.upper()} - {parts[1]}"
            else:
                # Unknown structure, use name as is
                path = str(value)
                lang_code = None
                display_name = name
            
            voices.append({
                'name': name,
                'display_name': display_name,
                'lang': lang_code or 'en'
            })
    except Exception as e:
        import traceback
        print(f"Error processing voices: {e}")
        traceback.print_exc()
        
        # Fallback: Add voices directly from the voices directory
        voices_dir = os.path.join(os.path.dirname(__file__), "voices")
        if os.path.exists(voices_dir):
            for voice_file in os.listdir(voices_dir):
                if voice_file.endswith('.wav'):
                    name = os.path.splitext(voice_file)[0]
                    lang_code = None
                    display_name = name
                    if '-' in name:
                        parts = name.split('-')
                        lang_code = parts[0]
                        display_name = f"{lang_code.upper()} - {parts[1]}"
                    
                    voices.append({
                        'name': name,
                        'display_name': display_name,
                        'lang': lang_code or 'en'
                    })
    
    # If no voices were found, add a default voice
    if not voices:
        voices.append({
            'name': 'default',
            'display_name': 'Default Voice',
            'lang': 'en'
        })
    
    print(f"Returning {len(voices)} voices")
    return jsonify(voices)

@app.route('/generate', methods=['POST'])
def generate_audio():
    """Generate audio from text using Chatterbox TTS"""
    try:
        # Get form data
        text = request.form.get('text', '').strip()
        voice_name = request.form.get('voice', '')
        cfg_scale = float(request.form.get('cfg', 0.4))
        exaggeration = float(request.form.get('exaggeration', 0.3))
        temperature = float(request.form.get('temperature', 0.5))
        seed = int(request.form.get('seed', 0))
        process = request.form.get('process') == 'on'
        
        # Validate input
        if not text:
            return jsonify({
                'success': False, 
                'error_message': 'Text is required',
                'audio_url': ''
            })
        
        if not process:
            return jsonify({
                'success': False, 
                'error_message': 'Processing is disabled',
                'audio_url': ''
            })
        
        # Set device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
        
        print(f"Using device: {device}")
        
        # Get voice path and language
        try:
            result = voice_mapper.get_voice_path_and_lang(voice_name)
            
            # Handle different return types
            if isinstance(result, tuple) and len(result) == 2:
                voice_path, lang = result
            elif isinstance(result, str):
                voice_path = result
                # Try to extract language from voice name
                lang = None
                if '-' in voice_name:
                    lang = voice_name.split('-')[0]
            else:
                # Fallback
                voice_path = str(result)
                lang = None
                
            print(f"Using voice: {os.path.basename(voice_path)}, Language: {lang or 'en'}")
        except Exception as e:
            # Fallback to first available voice file
            print(f"Error getting voice: {e}, falling back to default")
            voices_dir = os.path.join(os.path.dirname(__file__), "voices")
            if os.path.exists(voices_dir):
                wav_files = [f for f in os.listdir(voices_dir) if f.endswith('.wav')]
                if wav_files:
                    voice_path = os.path.join(voices_dir, wav_files[0])
                    lang = None
                    if '-' in wav_files[0]:
                        lang = wav_files[0].split('-')[0]
                    print(f"Fallback voice: {os.path.basename(voice_path)}, Language: {lang or 'en'}")
                else:
                    return jsonify({
                        'success': False, 
                        'error_message': 'No voice files available',
                        'audio_url': ''
                    })
            else:
                return jsonify({
                    'success': False, 
                    'error_message': 'No voices directory found',
                    'audio_url': ''
                })
        
        # Get model
        model = get_model(device=device, lang=lang or 'en')
        
        # Set seed if provided
        if seed > 0:
            torch.manual_seed(seed)
        
        # Generate audio
        print(f"Generating audio with cfg_scale={cfg_scale}, exaggeration={exaggeration}, temperature={temperature}")
        
        extra_args = {}
        if lang and lang != 'en':
            extra_args['language_id'] = lang
        
        # Add exaggeration and temperature parameters if supported
        if hasattr(model, 'generate_with_settings'):
            wav = model.generate_with_settings(
                text, 
                audio_prompt_path=voice_path, 
                cfg_weight=cfg_scale,
                exaggeration=exaggeration,
                temperature=temperature,
                **extra_args
            )
        else:
            # Fallback to standard generate method
            wav = model.generate(
                text, 
                audio_prompt_path=voice_path, 
                cfg_weight=cfg_scale,
                **extra_args
            )
        
        # Generate unique filename
        filename = f"output_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Save audio file
        ta.save(output_path, wav, model.sr)
        print(f"Saved output to {output_path}")
        
        # Return success response with audio URL
        return jsonify({
            'success': True, 
            'error_message': '',
            'audio_url': f'/audio/{filename}'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error_message': str(e),
            'audio_url': ''
        })

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/api/generate', methods=['POST'])
def api_generate_audio():
    """REST API endpoint for generating audio from text using Chatterbox TTS
    
    Accepts JSON data in the request body with the following parameters:
    - text: Text to convert to speech
    - voice: Voice name to use
    - cfg: Classifier-free guidance scale (0-1)
    - exaggeration: Exaggeration level (0-2)
    - temperature: Temperature for generation (0-1)
    - seed: Random seed (0 for random)
    - process: Whether to process the request (true/false)
    
    Returns JSON with:
    - success: true/false
    - error_message: Error message if success is false
    - audio_url: URL to the generated audio file if success is true
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False, 
                'error_message': 'No JSON data provided'
            })
        
        # Extract parameters
        text = data.get('text', '').strip()
        voice_name = data.get('voice', '')
        cfg_scale = float(data.get('cfg', 0.4))
        exaggeration = float(data.get('exaggeration', 0.3))
        temperature = float(data.get('temperature', 0.5))
        seed = int(data.get('seed', 0))
        process = data.get('process', True)
        
        # Validate input
        if not text:
            return jsonify({
                'success': False, 
                'error_message': 'Text is required'
            })
        
        if not process:
            return jsonify({
                'success': False, 
                'error_message': 'Processing is disabled'
            })
        
        # Set device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
        
        print(f"API: Using device: {device}")
        
        # Get voice path and language
        try:
            result = voice_mapper.get_voice_path_and_lang(voice_name)
            
            # Handle different return types
            if isinstance(result, tuple) and len(result) == 2:
                voice_path, lang = result
            elif isinstance(result, str):
                voice_path = result
                # Try to extract language from voice name
                lang = None
                if '-' in voice_name:
                    lang = voice_name.split('-')[0]
            else:
                # Fallback
                voice_path = str(result)
                lang = None
                
            print(f"API: Using voice: {os.path.basename(voice_path)}, Language: {lang or 'en'}")
        except Exception as e:
            # Fallback to first available voice file
            print(f"API: Error getting voice: {e}, falling back to default")
            voices_dir = os.path.join(os.path.dirname(__file__), "voices")
            if os.path.exists(voices_dir):
                wav_files = [f for f in os.listdir(voices_dir) if f.endswith('.wav')]
                if wav_files:
                    voice_path = os.path.join(voices_dir, wav_files[0])
                    lang = None
                    if '-' in wav_files[0]:
                        lang = wav_files[0].split('-')[0]
                    print(f"API: Fallback voice: {os.path.basename(voice_path)}, Language: {lang or 'en'}")
                else:
                    return jsonify({
                        'success': False, 
                        'error_message': 'No voice files available'
                    })
            else:
                return jsonify({
                    'success': False, 
                    'error_message': 'No voices directory found'
                })
        
        # Get model
        model = get_model(device=device, lang=lang or 'en')
        
        # Set seed if provided
        if seed > 0:
            torch.manual_seed(seed)
        
        # Generate audio
        print(f"API: Generating audio with cfg_scale={cfg_scale}, exaggeration={exaggeration}, temperature={temperature}")
        
        extra_args = {}
        if lang and lang != 'en':
            extra_args['language_id'] = lang
        
        # Add exaggeration and temperature parameters if supported
        if hasattr(model, 'generate_with_settings'):
            wav = model.generate_with_settings(
                text, 
                audio_prompt_path=voice_path, 
                cfg_weight=cfg_scale,
                exaggeration=exaggeration,
                temperature=temperature,
                **extra_args
            )
        else:
            # Fallback to standard generate method
            wav = model.generate(
                text, 
                audio_prompt_path=voice_path, 
                cfg_weight=cfg_scale,
                **extra_args
            )
        
        # Generate unique filename
        filename = f"output_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Save audio file
        ta.save(output_path, wav, model.sr)
        print(f"API: Saved output to {output_path}")
        
        # Return success response with audio URL
        return jsonify({
            'success': True,
            'error_message': '',
            'audio_url': f'/audio/{filename}'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error_message': str(e),
            'audio_url': ''
        })

def run_server(host='0.0.0.0', port=9080, debug=False):
    """Run the Flask server"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True)

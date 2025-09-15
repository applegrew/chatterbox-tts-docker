import torch
import numpy as np

class MockTTSBase:
    """Mock TTS class for testing the UI without actual TTS models"""
    
    def __init__(self, device="cpu"):
        self.device = device
        self.sr = 22050  # Sample rate
        print(f"Initialized Mock TTS on {device}")
    
    @classmethod
    def from_pretrained(cls, device="cpu"):
        """Mock from_pretrained method"""
        return cls(device=device)
    
    def generate_sine_wave(self, freq, duration_sec):
        """Generate a simple sine wave"""
        t = np.linspace(0, duration_sec, int(self.sr * duration_sec), endpoint=False)
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        return torch.tensor(wave.reshape(1, -1), dtype=torch.float32)

class MockChatterboxTTS(MockTTSBase):
    """Mock implementation of ChatterboxTTS"""
    
    def generate(self, text, audio_prompt_path=None, cfg_weight=0.4, **kwargs):
        """Generate audio from text"""
        print(f"Generating audio for: '{text[:50]}...' with cfg_weight={cfg_weight}")
        print(f"Using voice prompt: {audio_prompt_path}")
        
        # Text length affects duration
        duration = min(len(text) / 20, 10)  # Max 10 seconds
        duration = max(duration, 1)  # Min 1 second
        
        # Generate different frequencies based on the voice prompt
        if audio_prompt_path and "woman" in audio_prompt_path:
            freq = 440  # A4 - higher pitch for female voices
        else:
            freq = 220  # A3 - lower pitch for male voices
            
        return self.generate_sine_wave(freq, duration)
    
    def generate_with_settings(self, text, audio_prompt_path=None, cfg_weight=0.4, 
                              exaggeration=0.3, temperature=0.5, **kwargs):
        """Generate audio with additional settings"""
        print(f"Generating audio with exaggeration={exaggeration}, temperature={temperature}")
        
        # Exaggeration affects the amplitude
        amp_factor = 0.5 + (exaggeration * 0.5)
        
        # Temperature adds some noise
        noise_factor = temperature * 0.2
        
        # Generate base audio
        audio = self.generate(text, audio_prompt_path, cfg_weight, **kwargs)
        
        # Apply exaggeration (amplitude)
        audio = audio * amp_factor
        
        # Apply temperature (add noise)
        if noise_factor > 0:
            noise = torch.randn_like(audio) * noise_factor
            audio = audio + noise
            
        # Clip to avoid distortion
        audio = torch.clamp(audio, -1.0, 1.0)
        
        return audio

class MockChatterboxMultilingualTTS(MockChatterboxTTS):
    """Mock implementation of ChatterboxMultilingualTTS"""
    
    def generate(self, text, audio_prompt_path=None, cfg_weight=0.4, language_id=None, **kwargs):
        """Generate audio from text with language support"""
        print(f"Generating multilingual audio for language: {language_id}")
        
        # Different frequency based on language
        if language_id == 'zh':
            freq = 330  # Different base frequency for Chinese
        else:
            freq = 220  # Default frequency
            
        # Text length affects duration
        duration = min(len(text) / 20, 10)  # Max 10 seconds
        duration = max(duration, 1)  # Min 1 second
        
        return self.generate_sine_wave(freq, duration)

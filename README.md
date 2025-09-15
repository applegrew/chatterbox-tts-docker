# Chatterbox TTS Web Server

This project provides a web interface for the Chatterbox TTS (Text-to-Speech) system, allowing users to generate speech from text using various voice models.

## Features

- Web-based UI for text-to-speech generation
- Voice selection from available presets
- Adjustable parameters:
  - CFG (Classifier-Free Guidance) scale
  - Exaggeration level
  - Temperature
  - Random seed
- Audio playback in the browser
- Docker support for easy deployment

## Requirements

- Python 3.11+
- Docker (optional, for containerized deployment)

## Installation

### Using Docker (Recommended)

1. Clone this repository
2. Build and run using Docker Compose:

```bash
docker compose up
```

3. Access the web interface at http://localhost:9080

### Manual Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python -m src.main
```

4. Access the web interface at http://localhost:9080

## Usage

1. Select a voice from the dropdown menu
2. Enter the text you want to convert to speech
3. Adjust parameters as needed:
   - CFG: Controls how closely the output follows the voice characteristics (0-1)
   - Exaggeration: Controls the expressiveness of the speech (0-2)
   - Temperature: Controls the randomness/creativity in generation (0-1)
   - Random Seed: Set a specific seed for reproducible results (0 for random)
4. Toggle the "Process" switch to enable/disable processing
5. Click "Generate Audio" to create the speech
6. The generated audio will appear in the Output section for playback

## Voice Files

Voice files are stored in the `voices` directory. The system automatically detects and uses available `.wav` files in this directory.

## License

This project uses the Chatterbox TTS system. Please refer to the Chatterbox license for usage restrictions.
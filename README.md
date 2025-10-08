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

### Web Interface

1. Open the web interface in your browser at http://localhost:9080
2. Select a voice from the dropdown menu
3. Enter the text you want to convert to speech
4. Adjust parameters as needed:
   - CFG: Controls how closely the output follows the voice (0-1)
   - Exaggeration: Controls the expressiveness of the voice (0-2)
   - Temperature: Controls the randomness of the generation (0-1)
   - Random Seed: Set a specific seed for reproducible results (0 for random)
5. Toggle the "Process?" switch to enable/disable automatic generation

### REST API

The server provides a REST API endpoint for programmatic access:

**Endpoint:** `/api/generate`

**Method:** POST

**Content-Type:** application/json

**Request Body:**

```json
{
  "text": "Text to convert to speech",
  "voice": "voice-name",
  "cfg": 0.4,
  "exaggeration": 0.3,
  "temperature": 0.5,
  "seed": 0,
  "process": true
}
```

**Response:**

```json
{
  "success": true,
  "error_message": "",
  "audio_url": "/audio/output_12345678.wav"
}
```

**Example using curl:**

```bash
curl -X POST http://localhost:9080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world", "voice":"en-Carter"}'
```

## Voice Files

Voice files are stored in the `voices` directory. The system automatically detects and uses available `.wav` files in this directory.

## License

This project uses the Chatterbox TTS system. Please refer to the Chatterbox license for usage restrictions.
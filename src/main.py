
import argparse
import os
from .http_server import run_server
from .setup_voices import setup_voices

def parse_args():
    parser = argparse.ArgumentParser(description='Chatterbox TTS Web Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=9080, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode', default=os.getenv('DEBUG', False) == "yes")
    parser.add_argument('--skip-setup', action='store_true', help='Skip voice setup')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Set up the voices directory
    if not args.skip_setup:
        print("Setting up voices directory...")
        setup_voices()
    
    # Ensure output directory exists
    output_dir = os.environ.get('OUTPUT_DIR', os.path.join(os.path.dirname(__file__), '..', 'outputs'))
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    print(f"Starting Chatterbox TTS Web Server on {args.host}:{args.port}")
    run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()

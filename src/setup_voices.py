#!/usr/bin/env python3
import os
import shutil
import sys

def setup_voices():
    """Set up the voices directory for the HTTP server"""
    # Get the source and destination directories
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voices")
    dst_dir = os.path.join(os.path.dirname(__file__), "voices")
    
    print(f"Source voices directory: {src_dir}")
    print(f"Destination voices directory: {dst_dir}")
    
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dst_dir):
        print(f"Creating destination directory: {dst_dir}")
        os.makedirs(dst_dir, exist_ok=True)
    
    # Check if the source directory exists
    if not os.path.exists(src_dir):
        print(f"Source directory does not exist: {src_dir}")
        return False
    
    # Copy the voice files
    voice_files = [f for f in os.listdir(src_dir) if f.endswith('.wav')]
    if not voice_files:
        print("No voice files found in source directory")
        return False
    
    print(f"Found {len(voice_files)} voice files: {', '.join(voice_files)}")
    
    # Copy each voice file
    for voice_file in voice_files:
        src_file = os.path.join(src_dir, voice_file)
        dst_file = os.path.join(dst_dir, voice_file)
        
        if os.path.exists(dst_file):
            print(f"Voice file already exists: {dst_file}")
            continue
        
        print(f"Copying {src_file} to {dst_file}")
        shutil.copy2(src_file, dst_file)
    
    # List the files in the destination directory
    dst_files = [f for f in os.listdir(dst_dir) if f.endswith('.wav')]
    print(f"Destination directory now contains {len(dst_files)} voice files: {', '.join(dst_files)}")
    
    return True

if __name__ == "__main__":
    if setup_voices():
        print("Voice setup completed successfully")
        sys.exit(0)
    else:
        print("Voice setup failed")
        sys.exit(1)

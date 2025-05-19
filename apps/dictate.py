#!/usr/bin/env python3
"""
Simple CLI dictation tool using OpenAI's Whisper.
Records audio from microphone and transcribes it in real-time.

Usage:
    python dictate.py [--model MODEL] [--language LANGUAGE] [--save FILENAME]
    
    - MODEL: whisper model size (tiny, base, small, medium, large, turbo)
    - LANGUAGE: language code (en, es, fr, etc.) or "auto" for auto-detection
    - FILENAME: optional file to save transcription (default: none)
"""

import os
import sys
import time
import wave
import tempfile
import argparse
import signal
from datetime import datetime

try:
    import pyaudio
    import whisper
    import numpy as np
except ImportError:
    print("Required packages not found. Please install with:")
    print("pip install openai-whisper pyaudio numpy")
    sys.exit(1)

# Global flag for handling interruption
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\nStopping dictation...")
    running = False

def list_microphones():
    """List all available microphones"""
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    print("\nAvailable microphones:")
    mic_list = []
    
    for i in range(num_devices):
        device_info = audio.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            name = device_info.get('name')
            print(f"  [{i}] {name}")
            mic_list.append(i)
    
    audio.terminate()
    return mic_list

def check_microphone_volume(device_index=None, duration=3):
    """Test the microphone volume to ensure it's working properly"""
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    print(f"Testing microphone volume for {duration} seconds...")
    print("Please speak normally...")
    
    audio = pyaudio.PyAudio()
    
    # Open the stream
    if device_index is not None:
        try:
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        except Exception as e:
            print(f"Error using selected microphone: {e}")
            print("Falling back to default microphone")
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
    else:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    # Read audio data and check volume
    max_volume = 0
    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        samples = np.frombuffer(data, dtype=np.int16)
        max_sample = np.max(np.abs(samples))
        max_volume = max(max_volume, max_sample)
        
        # Display a simple volume meter
        vol_percent = min(100, int(max_sample / 32768 * 100))
        meter = "█" * int(vol_percent / 5)
        sys.stdout.write(f"\rVolume: {meter.ljust(20)} {vol_percent}%")
        sys.stdout.flush()
        time.sleep(0.1)
    
    # Close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    print("\n")
    
    # Provide feedback on the volume
    if max_volume < 1000:
        print("WARNING: Your microphone volume is very low!")
        print("Tips: Speak louder, move closer to the mic, or increase your mic volume in settings.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    elif max_volume < 5000:
        print("Your microphone volume is a bit low, but should work.")
        print("For better results, consider speaking louder or adjusting your mic settings.")
    else:
        print("Your microphone volume looks good!")
    
    return True

def record_audio(duration=5, rate=16000, device_index=None):
    """Record audio from microphone"""
    # Audio parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    CHUNK = 1024
    
    print(f"Recording for {duration} seconds...")
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Start recording - with specified device if provided
    if device_index is not None:
        try:
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=rate, input=True, input_device_index=device_index,
                            frames_per_buffer=CHUNK)
            print(f"Using microphone: {audio.get_device_info_by_index(device_index)['name']}")
        except Exception as e:
            print(f"Error using selected microphone: {e}")
            print("Falling back to default microphone")
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=rate, input=True,
                            frames_per_buffer=CHUNK)
    else:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=rate, input=True,
                        frames_per_buffer=CHUNK)
    
    frames = []
    for i in range(0, int(rate / CHUNK * duration)):
        if not running:
            break
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    # Stop and close recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save to a temporary WAV file
    temp_file = tempfile.mktemp(suffix=".wav")
    with wave.open(temp_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    return temp_file

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Whisper Dictation Tool")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large", "turbo"],
                        help="Whisper model size (smaller=faster, larger=more accurate)")
    parser.add_argument("--language", default=None, 
                        help="Language code (e.g., en, es, fr) or 'auto' for auto-detection")
    parser.add_argument("--save", default=None, 
                        help="Save transcription to specified file")
    parser.add_argument("--continuous", action="store_true",
                        help="Continuous dictation mode (keeps recording until stopped)")
    parser.add_argument("--duration", type=int, default=10,
                        help="Recording duration in seconds (default: 10)")
    parser.add_argument("--skip-check", action="store_true",
                        help="Skip microphone volume check")
    return parser.parse_args()

def main():
    """Main function to handle dictation"""
    global running
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse arguments
    args = parse_arguments()
    
    # Load model
    print(f"Loading Whisper model '{args.model}'...")
    model = whisper.load_model(args.model)
    print("Model loaded!")
    
    # Prepare language setting
    language = None if args.language == "auto" else args.language
    
    # Open output file if specified
    output_file = None
    if args.save:
        output_file = open(args.save, "w", encoding="utf-8")
    
    # Start dictation
    print("\n=== Whisper Dictation Tool ===")
    print("Speak clearly into your microphone")
    print("Press Ctrl+C to stop")
    print("==============================\n")
    
    try:
        # List available microphones at startup
        device_index = None
        mic_list = list_microphones()
        if len(mic_list) > 1:
            try:
                selection = input("\nSelect microphone number (or press Enter for default): ")
                if selection.strip():
                    device_index = int(selection)
            except ValueError:
                print("Invalid selection, using default microphone")
        
        # Perform volume check unless skipped
        if not args.skip_check:
            check_microphone_volume(device_index)
        
        if args.continuous:
            # Continuous dictation mode
            while running:
                # Record audio
                audio_file = record_audio(duration=args.duration, device_index=device_index)
                
                if not running:
                    break
                
                # Transcribe
                print("Transcribing...")
                result = model.transcribe(
                    audio_file, 
                    language=language,
                    fp16=False
                )
                
                # Output result
                transcription = result["text"].strip()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if transcription:
                    print(f"[{timestamp}] {transcription}")
                    
                    # Save to file if specified
                    if output_file:
                        output_file.write(f"{transcription}\n")
                        output_file.flush()
                
                # Clean up temporary file
                try:
                    os.remove(audio_file)
                except:
                    pass
                
                # Brief pause to allow for interruption
                time.sleep(0.5)
        
        else:
            # Single recording mode
            audio_file = record_audio(duration=args.duration, device_index=device_index)
            
            if running:
                print("Transcribing...")
                result = model.transcribe(
                    audio_file, 
                    language=language,
                    fp16=False
                )
                
                # Output result
                transcription = result["text"].strip()
                
                if transcription:
                    print(f"\nTranscription:\n{transcription}")
                    
                    # Save to file if specified
                    if output_file:
                        output_file.write(f"{transcription}\n")
                
                # Clean up temporary file
                try:
                    os.remove(audio_file)
                except:
                    pass
    
    finally:
        # Close output file if opened
        if output_file:
            output_file.close()
            print(f"Transcription saved to {args.save}")

if __name__ == "__main__":
    main()

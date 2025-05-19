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
    import pyperclip  # For clipboard operations
    import pyautogui  # For simulating paste operation
    import keyboard   # For detecting key presses
except ImportError:
    print("Required packages not found. Please install with:")
    print("pip install openai-whisper pyaudio numpy pyperclip pyautogui keyboard")
    sys.exit(1)

# Global flag for handling interruption
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\nStopping dictation...")
    running = False
    # Force exit after a short delay if not exiting cleanly
    time.sleep(0.5)
    if keyboard and keyboard._listener:
        keyboard._listener.stop()
    time.sleep(0.5)
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Whisper Dictation Tool")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large", "turbo"],
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
    parser.add_argument("--clipboard", action="store_true", default=True,
                        help="Automatically copy transcription to clipboard")
    parser.add_argument("--autopaste", action="store_true",
                        help="Automatically paste transcription where cursor is pointing (implies --clipboard)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay in seconds before pasting (only used with --autopaste, default: 1.0)")
    parser.add_argument("--interactive", action="store_true",
                        help="Run in interactive mode, waiting for commands between dictations")
    parser.add_argument("--spacebar", action="store_true", default=True,
                        help="Use Shift+Spacebar to control recording (press to start/stop)")
    parser.add_argument("--no-spacebar", action="store_true",
                        help="Disable Shift+Spacebar mode")
    
    args = parser.parse_args()
    
    # If --no-spacebar is specified, disable spacebar mode
    if args.no_spacebar:
        args.spacebar = False
    
    return args

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
        data = stream.read(CHUNK, exception_on_overflow=False)
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

def record_until_shift_spacebar(device_index=None, rate=16000, max_duration=60):
    """Record audio from microphone until Shift+Spacebar is pressed or max duration is reached"""
    global running
    # Audio parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    CHUNK = 1024
    
    print("🔴 Recording... (Press SHIFT+SPACEBAR to stop)")
    
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
    start_time = time.time()
    elapsed_time = 0
    last_check = 0
    
    # Record until Shift+Spacebar is pressed or max duration is reached
    while elapsed_time < max_duration and running:
        # Only check keyboard every 0.1 seconds to reduce CPU usage
        current_time = time.time()
        if current_time - last_check >= 0.1:
            if keyboard.is_pressed('shift') and keyboard.is_pressed('space'):
                # Small delay to avoid multiple triggers
                time.sleep(0.3)
                break
                
            # Also check for ESC key
            if keyboard.is_pressed('esc'):
                running = False
                break
                
            last_check = current_time
            
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        
        elapsed_time = time.time() - start_time
        
        # Print a simple time progress indicator
        if int(elapsed_time) % 5 == 0 and int(elapsed_time) != int(elapsed_time - 0.1):  # Every 5 seconds
            sys.stdout.write(f"\rRecording: {int(elapsed_time)}s ")
            sys.stdout.flush()
    
    # Stop and close recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Calculate actual duration
    actual_duration = time.time() - start_time
    print(f"\n✅ Recording stopped after {actual_duration:.1f} seconds")
    
    # Save to a temporary WAV file
    temp_file = tempfile.mktemp(suffix=".wav")
    with wave.open(temp_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    return temp_file

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

def display_interactive_help():
    """Display help for interactive mode"""
    print("\n=== Interactive Mode Commands ===")
    print("  record [duration]  - Start recording (optional duration in seconds)")
    print("  continuous        - Start continuous recording (press Ctrl+C to stop)")
    print("  language [code]    - Set language (e.g., 'en', 'es', 'fr', or 'auto')")
    print("  clipboard on/off   - Toggle copying to clipboard")
    print("  autopaste on/off   - Toggle auto-pasting")
    print("  delay [seconds]    - Set delay before auto-pasting")
    print("  model [name]       - Change model (tiny, base, small, medium, large, turbo)")
    print("  save [filename]    - Set file to save transcriptions (or 'off' to disable)")
    print("  duration [seconds] - Set default recording duration")
    print("  status            - Show current settings")
    print("  help              - Show this help")
    print("  exit/quit         - Exit the program")
    print("================================\n")

def run_spacebar_mode(model, args, device_index=None):
    """Run dictation with Shift+Spacebar control"""
    print("\n=== Whisper Dictation Tool (Shift+Spacebar Mode) ===")
    print("Press SHIFT+SPACEBAR to START recording")
    print("Press SHIFT+SPACEBAR again to STOP recording")
    print("Press ESC or Ctrl+C to exit")
    print("==========================================\n")
    
    # Open output file if specified
    output_file = None
    if args.save:
        output_file = open(args.save, "w", encoding="utf-8")
    
    # Prepare language setting
    language = None if args.language == "auto" else args.language
    
    try:
        # Main dictation loop
        while True:
            # Wait for shift+spacebar to start recording
            print("⏸️  Ready - Press SHIFT+SPACEBAR to start recording...")
            
            # Wait until shift+spacebar is pressed with timeout to allow for interruption
            start_wait = time.time()
            while True:
                # Check for interrupt every iteration with short timeout
                if not running:  # Global flag set by signal handler
                    print("Exiting...")
                    return
                
                if keyboard.is_pressed('shift') and keyboard.is_pressed('space'):
                    # Small delay to avoid multiple triggers
                    time.sleep(0.3)
                    break
                elif keyboard.is_pressed('esc'):
                    print("Exiting...")
                    return
                
                # Check if more than 0.5 seconds has passed
                if time.time() - start_wait > 0.5:
                    # Check if we need to exit
                    if not running:
                        print("Exiting...")
                        return
                    start_wait = time.time()
                
                # Short sleep to prevent high CPU usage
                time.sleep(0.1)
            
            # Check for ESC key
            if keyboard.is_pressed('esc'):
                print("Exiting...")
                break
            
            # Record until shift+spacebar is pressed again
            audio_file = record_until_shift_spacebar(device_index=device_index, max_duration=60)
            
            # Check if we need to exit
            if not running:
                print("Exiting...")
                try:
                    os.remove(audio_file)
                except:
                    pass
                return
            
            print("🔍 Transcribing...")
            result = model.transcribe(
                audio_file, 
                language=language,
                fp16=False
            )
            
            # Output result
            transcription = result["text"].strip()
            if transcription:
                print(f"\n📝 Transcription:\n{transcription}\n")
                
                # Save to file if specified
                if output_file:
                    output_file.write(f"{transcription}\n")
                    output_file.flush()
                
                # Always copy to clipboard for convenience
                pyperclip.copy(transcription)
                print("📋 Copied to clipboard! (Press Ctrl+V to paste)")
                
                # Auto-paste if requested
                if args.autopaste:
                    print(f"🖱️ Auto-pasting in {args.delay} seconds... (Move cursor to desired location)")
                    time.sleep(args.delay)
                    # Detect platform and use appropriate paste command
                    if sys.platform == "darwin":  # macOS
                        pyautogui.hotkey('command', 'v')
                    else:  # Windows/Linux
                        pyautogui.hotkey('ctrl', 'v')
                    print("✅ Pasted!")
            
            # Clean up
            try:
                os.remove(audio_file)
            except:
                pass
            
            # Check if we need to exit
            if not running:
                print("Exiting...")
                return
    
    except KeyboardInterrupt:
        print("\nStopping dictation...")
    
    finally:
        # Close output file if opened
        if output_file:
            output_file.close()
            if args.save:
                print(f"Transcriptions saved to {args.save}")

def run_interactive_mode(model, args):
    """Run the dictation tool in interactive mode"""
    print("\n=== Whisper Dictation Tool (Interactive Mode) ===")
    print("Type 'help' for available commands or 'record' to start dictating")
    print("====================================================\n")
    
    # Initialize settings from args
    settings = {
        "model": args.model,
        "language": args.language,
        "save_file": args.save,
        "clipboard": args.clipboard,
        "autopaste": args.autopaste,
        "delay": args.delay,
        "duration": args.duration,
        "output_file": None
    }
    
    # Open output file if specified
    if settings["save_file"]:
        settings["output_file"] = open(settings["save_file"], "w", encoding="utf-8")
    
    # Store device_index to avoid selecting microphone each time
    device_index = None
    
    # Initial mic selection
    mic_list = list_microphones()
    if len(mic_list) > 1:
        try:
            selection = input("\nSelect microphone number (or press Enter for default): ")
            if selection.strip():
                device_index = int(selection)
        except ValueError:
            print("Invalid selection, using default microphone")
    
    # Check microphone volume unless skipped
    if not args.skip_check:
        check_microphone_volume(device_index)
    
    # Main interactive loop
    try:
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                # Parse command and arguments
                parts = command.split(maxsplit=1)
                cmd = parts[0] if parts else ""
                arg = parts[1] if len(parts) > 1 else ""
                
                # Process commands
                if cmd in ["exit", "quit"]:
                    print("Exiting...")
                    break
                    
                elif cmd == "help":
                    display_interactive_help()
                    
                elif cmd == "status":
                    print("\n=== Current Settings ===")
                    print(f"  Model: {settings['model']}")
                    print(f"  Language: {settings['language'] or 'auto'}")
                    print(f"  Recording duration: {settings['duration']} seconds")
                    print(f"  Save to file: {settings['save_file'] or 'disabled'}")
                    print(f"  Copy to clipboard: {'enabled' if settings['clipboard'] else 'disabled'}")
                    print(f"  Auto-paste: {'enabled' if settings['autopaste'] else 'disabled'}")
                    print(f"  Auto-paste delay: {settings['delay']} seconds")
                    print("======================\n")
                    
                elif cmd == "record":
                    # Parse duration if provided
                    duration = settings["duration"]
                    if arg and arg.isdigit():
                        duration = int(arg)
                    
                    # Record and transcribe
                    print(f"Recording for {duration} seconds...")
                    audio_file = record_audio(duration=duration, device_index=device_index)
                    
                    print("Transcribing...")
                    result = model.transcribe(
                        audio_file, 
                        language=settings["language"],
                        fp16=False
                    )
                    
                    # Output result
                    transcription = result["text"].strip()
                    if transcription:
                        print(f"\nTranscription:\n{transcription}")
                        
                        # Save to file if specified
                        if settings["output_file"]:
                            settings["output_file"].write(f"{transcription}\n")
                            settings["output_file"].flush()
                        
                        # Copy to clipboard if enabled
                        if settings["clipboard"] or settings["autopaste"]:
                            pyperclip.copy(transcription)
                            print("(Copied to clipboard)")
                        
                        # Auto-paste if enabled
                        if settings["autopaste"]:
                            print(f"Auto-pasting in {settings['delay']} seconds... (Move cursor to desired location)")
                            time.sleep(settings["delay"])
                            # Detect platform and use appropriate paste command
                            if sys.platform == "darwin":  # macOS
                                pyautogui.hotkey('command', 'v')
                            else:  # Windows/Linux
                                pyautogui.hotkey('ctrl', 'v')
                            print("(Pasted)")
                    
                    # Clean up
                    try:
                        os.remove(audio_file)
                    except:
                        pass
                
                elif cmd == "continuous":
                    print("Starting continuous recording. Press Ctrl+C to stop...")
                    continuous_running = True
                    
                    try:
                        while continuous_running:
                            # Record
                            audio_file = record_audio(duration=settings["duration"], device_index=device_index)
                            
                            # Transcribe
                            print("Transcribing...")
                            result = model.transcribe(
                                audio_file, 
                                language=settings["language"],
                                fp16=False
                            )
                            
                            # Output
                            transcription = result["text"].strip()
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            
                            if transcription:
                                print(f"[{timestamp}] {transcription}")
                                
                                # Save to file if specified
                                if settings["output_file"]:
                                    settings["output_file"].write(f"{transcription}\n")
                                    settings["output_file"].flush()
                                
                                # Copy to clipboard if enabled
                                if settings["clipboard"] or settings["autopaste"]:
                                    pyperclip.copy(transcription)
                                    print("(Copied to clipboard)")
                                
                                # Auto-paste if enabled
                                if settings["autopaste"]:
                                    print(f"Auto-pasting in {settings['delay']} seconds...")
                                    time.sleep(settings["delay"])
                                    # Detect platform and use appropriate paste command
                                    if sys.platform == "darwin":  # macOS
                                        pyautogui.hotkey('command', 'v')
                                    else:  # Windows/Linux
                                        pyautogui.hotkey('ctrl', 'v')
                                    print("(Pasted)")
                            
                            # Clean up
                            try:
                                os.remove(audio_file)
                            except:
                                pass
                    
                    except KeyboardInterrupt:
                        print("\nContinuous recording stopped")
                        continuous_running = False
                
                elif cmd == "language":
                    if arg in ["auto", ""]:
                        settings["language"] = None
                        print("Language set to auto-detect")
                    else:
                        settings["language"] = arg
                        print(f"Language set to: {arg}")
                
                elif cmd == "clipboard":
                    if arg in ["on", "true", "yes", "1"]:
                        settings["clipboard"] = True
                        print("Clipboard copying enabled")
                    elif arg in ["off", "false", "no", "0"]:
                        settings["clipboard"] = False
                        print("Clipboard copying disabled")
                    else:
                        print(f"Invalid option: {arg}. Use 'on' or 'off'")
                
                elif cmd == "autopaste":
                    if arg in ["on", "true", "yes", "1"]:
                        settings["autopaste"] = True
                        settings["clipboard"] = True  # Autopaste implies clipboard
                        print("Auto-pasting enabled")
                    elif arg in ["off", "false", "no", "0"]:
                        settings["autopaste"] = False
                        print("Auto-pasting disabled")
                    else:
                        print(f"Invalid option: {arg}. Use 'on' or 'off'")
                
                elif cmd == "delay":
                    if arg and arg.replace(".", "", 1).isdigit():
                        settings["delay"] = float(arg)
                        print(f"Auto-paste delay set to {settings['delay']} seconds")
                    else:
                        print(f"Invalid delay: {arg}. Please specify a number of seconds.")
                
                elif cmd == "model":
                    valid_models = ["tiny", "base", "small", "medium", "large", "turbo"]
                    if arg in valid_models:
                        if arg != settings["model"]:
                            print(f"Changing model to {arg}...")
                            settings["model"] = arg
                            model = whisper.load_model(arg)
                            print("Model loaded!")
                        else:
                            print(f"Model is already set to {arg}")
                    else:
                        models_str = ", ".join(valid_models)
                        print(f"Invalid model name: {arg}. Available models: {models_str}")
                
                elif cmd == "save":
                    # Close existing file if open
                    if settings["output_file"]:
                        settings["output_file"].close()
                        settings["output_file"] = None
                    
                    if arg in ["off", "false", "no", "0"]:
                        settings["save_file"] = None
                        print("File saving disabled")
                    elif arg:
                        settings["save_file"] = arg
                        settings["output_file"] = open(arg, "w", encoding="utf-8")
                        print(f"Saving transcriptions to: {arg}")
                    else:
                        print("Please specify a filename or 'off' to disable saving")
                
                elif cmd == "duration":
                    if arg and arg.isdigit():
                        settings["duration"] = int(arg)
                        print(f"Recording duration set to {settings['duration']} seconds")
                    else:
                        print(f"Invalid duration: {arg}. Please specify a number of seconds.")
                        
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        # Close output file if opened
        if settings["output_file"]:
            settings["output_file"].close()
            if settings["save_file"]:
                print(f"Transcriptions saved to {settings['save_file']}")

def main():
    """Main function to handle dictation"""
    global running
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Load model
        print(f"Loading Whisper model '{args.model}'...")
        model = whisper.load_model(args.model)
        print("Model loaded!")
        
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
        
        # Check if running in spacebar mode (default)
        if args.spacebar:
            run_spacebar_mode(model, args, device_index)
            return
        
        # Check if running in interactive mode
        if args.interactive:
            run_interactive_mode(model, args)
            return
        
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
                        
                        # Copy to clipboard if requested - ALWAYS do this in continuous mode for convenience
                        pyperclip.copy(transcription)
                        print("(Copied to clipboard - press Ctrl+V to paste)")
                        
                        # Auto-paste if requested
                        if args.autopaste:
                            print(f"Auto-pasting in {args.delay} seconds... (Move cursor to desired location)")
                            time.sleep(args.delay)
                            pyautogui.hotkey('ctrl', 'v')  # For Windows/Linux
                            # Alternatively for macOS: pyautogui.hotkey('command', 'v')
                            print("(Pasted)")
                    
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
                        
                        # Copy to clipboard if requested
                        if args.clipboard or args.autopaste:
                            pyperclip.copy(transcription)
                            print("(Copied to clipboard)")
                        
                        # Auto-paste if requested
                        if args.autopaste:
                            print(f"Auto-pasting in {args.delay} seconds... (Move cursor to desired location)")
                            time.sleep(args.delay)
                            pyautogui.hotkey('ctrl', 'v')  # For Windows/Linux
                            # Alternatively for macOS: pyautogui.hotkey('command', 'v')
                            print("(Pasted)")
                    
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
                
    except KeyboardInterrupt:
        print("\nStopping dictation...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure keyboard listener is stopped
        if keyboard and hasattr(keyboard, '_listener') and keyboard._listener:
            keyboard._listener.stop()
        
        print("Dictation tool stopped. Press Enter to exit.")

if __name__ == "__main__":
    main()

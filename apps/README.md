# Whisper Dictation Tool

A simple speech-to-text dictation tool using OpenAI's Whisper for accurate transcription.

## 🚀 Quick Start

### On Windows:
Double-click the batch file to start dictation immediately:
```
/apps/dictate-spacebar.bat
```

### On macOS/Linux:
Run the Python script directly:
```
python3 apps/dictate.py
```

Then:
1. Press **SHIFT+SPACEBAR** to start recording
2. Speak clearly into your microphone
3. Press **SHIFT+SPACEBAR** again to stop and transcribe
4. The text is automatically copied to your clipboard
5. Press **Ctrl+V** (Windows/Linux) or **Command+V** (macOS) to paste anywhere
6. Press **ESC** to exit when finished

## 🎤 Shift+Spacebar Dictation Mode

This is the most user-friendly mode for dictation, giving you complete control with Shift+Spacebar key combinations:

```
python dictate.py
```

The script now uses these settings by default:
- Small model (better accuracy)
- Shift+Spacebar control
- Automatic clipboard copy

### How Shift+Spacebar Mode Works:

1. **START** - Press Shift+Spacebar to begin recording
2. **SPEAK** - Dictate your text clearly
3. **STOP** - Press Shift+Spacebar again to finish recording
4. **COPY** - Text is automatically copied to clipboard
5. **PASTE** - Use Ctrl+V (Win/Linux) or Command+V (Mac) to paste anywhere
6. **EXIT** - Press ESC key when done

## 📋 All Command-line Options

| Option | Description |
|--------|-------------|
| `--model MODEL` | Choose model size: tiny, base, small, medium, large, turbo (default: small) |
| `--no-spacebar` | Disable the default Shift+Spacebar mode |
| `--language LANG` | Specify language (e.g., en, es, fr) or "auto" (default) |
| `--clipboard` | Automatically copy transcription to clipboard (enabled by default) |
| `--autopaste` | Automatically paste text where cursor is pointing |
| `--delay SECONDS` | Set delay before auto-pasting (default: 1.0) |
| `--continuous` | Continuous recording mode (Ctrl+C to stop) |
| `--duration SECONDS` | Set recording duration (default: 10) |
| `--save FILE` | Save transcriptions to a file |
| `--interactive` | Run in interactive command mode |
| `--skip-check` | Skip the microphone volume check |

## 💻 Launcher Scripts

### Windows
The apps folder includes these batch files for quick access (Windows only):

| File | Description |
|------|-------------|
| `wdictate.bat` | Simple command to run the dictation tool |
| `whisper-dictate.bat` | Alternative command name to avoid conflicts |
| `dictate-spacebar.bat` | Starts Shift+Spacebar-controlled dictation mode |
| `create-shortcut.bat` | Creates a desktop shortcut for easy access |

### macOS/Linux
For macOS and Linux, create a shell script:

```bash
#!/bin/bash
# Save this as dictate.sh in the apps directory
cd "$(dirname "$0")"
python3 dictate.py "$@"
```

Then make it executable:
```
chmod +x apps/dictate.sh
```

## 📦 Installation

1. Install required packages:
   ```
   # For Windows:
   pip install openai-whisper pyaudio numpy pyperclip pyautogui keyboard

   # For macOS:
   pip3 install openai-whisper pyaudio numpy pyperclip pyautogui keyboard
   ```

2. Install FFmpeg (required by Whisper for audio processing):
   - Windows (using Chocolatey): `choco install ffmpeg`
   - Windows (using Scoop): `scoop install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Ubuntu/Linux: `sudo apt update && sudo apt install ffmpeg`

3. Install PyAudio (which can be tricky on some systems):
   - Windows: If the normal pip install fails, try:
     ```
     pip install pipwin
     pipwin install pyaudio
     ```
   - macOS: You may need to install portaudio first:
     ```
     brew install portaudio
     pip3 install pyaudio
     ```
   - Linux: Install dependencies first:
     ```
     sudo apt install python3-pyaudio portaudio19-dev
     ```

## 🔧 Other Modes

### Interactive Mode
```
python dictate.py --interactive
```

This mode preserves your microphone selection and lets you change settings between dictations using commands:

| Command | Description |
|---------|-------------|
| `record [duration]` | Start recording |
| `language [code]` | Set language |
| `model [name]` | Change model |
| `help` | Show all commands |
| `exit` | Exit program |

### Continuous Mode
```
python dictate.py --continuous --no-spacebar
```
Records continuously in fixed intervals until stopped with Ctrl+C.

## 📝 Tips for Better Dictation

1. **Using Shift+Spacebar** prevents accidental activation when typing in other apps

2. **Choose the right model**:
   - `tiny`: Fastest but least accurate
   - `small`: Good balance of speed/accuracy for most users (default)
   - `medium`: More accurate but slower
   - `large`: Most accurate but slowest

3. **Speak clearly and at a moderate pace**

4. **Position your microphone properly** (6-12 inches from your mouth)

5. **Specify your language** for better accuracy:
   ```
   python dictate.py --language en
   ```

## 🖥️ Platform-Specific Notes

### Windows
- The .bat files provide convenient ways to run the tool
- Run Command Prompt as Administrator if keyboard detection has issues
- Desktop shortcut creation is supported

### macOS
- Use `Command+V` instead of `Ctrl+V` to paste
- You may need to grant permission for keyboard monitoring in System Preferences
- For keyboard issues, try adding Terminal to Accessibility permissions
- The batch files (.bat) won't work - use the Python command directly

### Linux
- Additional packages may be needed for audio: `sudo apt install libasound-dev`
- For keyboard monitoring, X11 may require: `sudo apt install python3-dev python3-xlib`

## ⚠️ Troubleshooting

1. **If you have microphone issues**:
   - Ensure your microphone is set as the default input device
   - Check microphone volume in system settings
   - Try a different microphone if available

2. **If transcription quality is poor**:
   - Use `--model medium` for better accuracy
   - Reduce background noise
   - Position the microphone closer to your mouth

3. **If keyboard module gives errors**:
   - Windows: Run the command prompt as administrator
   - macOS: Add Terminal to Accessibility permissions
   - Linux: Make sure X11 is running and you have appropriate permissions

4. **If the script gets stuck**:
   - Windows: Use the provided `kill-dictation.bat`
   - macOS/Linux: Use `killall python` or `killall python3`

## Notes

- The script creates temporary audio files that are deleted after transcription
- Shift+Spacebar mode gives you precise control over when recording starts and stops
- Using Shift+Spacebar instead of just Spacebar prevents accidental activations
- The text is automatically copied to clipboard for easy pasting
- For macOS, edit the script to use `command+v` instead of `ctrl+v` for pasting

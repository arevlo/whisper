# Whisper Dictation Tool

A simple speech-to-text dictation tool using OpenAI's Whisper for accurate transcription.

## 🚀 Quick Start

Double-click the batch file to start dictation immediately:
```
/apps/dictate-spacebar.bat
```

Then:
1. Press **SHIFT+SPACEBAR** to start recording
2. Speak clearly into your microphone
3. Press **SHIFT+SPACEBAR** again to stop and transcribe
4. The text is automatically copied to your clipboard
5. Press **Ctrl+V** to paste anywhere
6. Press **ESC** to exit when finished

## 🎤 Shift+Spacebar Dictation Mode

This is the most user-friendly mode for dictation, giving you complete control with Shift+Spacebar key combinations:

```
python dictate.py --model small --spacebar
```

### How Shift+Spacebar Mode Works:

1. **START** - Press Shift+Spacebar to begin recording
2. **SPEAK** - Dictate your text clearly
3. **STOP** - Press Shift+Spacebar again to finish recording
4. **COPY** - Text is automatically copied to clipboard
5. **PASTE** - Use Ctrl+V to paste anywhere
6. **EXIT** - Press ESC key when done

## 📋 All Command-line Options

| Option | Description |
|--------|-------------|
| `--model MODEL` | Choose model size: tiny, base, small, medium, large, turbo (default: base) |
| `--spacebar` | **[Recommended]** Use spacebar to start/stop recording |
| `--language LANG` | Specify language (e.g., en, es, fr) or "auto" (default) |
| `--clipboard` | Automatically copy transcription to clipboard |
| `--autopaste` | Automatically paste text where cursor is pointing |
| `--delay SECONDS` | Set delay before auto-pasting (default: 1.0) |
| `--continuous` | Continuous recording mode (Ctrl+C to stop) |
| `--duration SECONDS` | Set recording duration (default: 10) |
| `--save FILE` | Save transcriptions to a file |
| `--interactive` | Run in interactive command mode |
| `--skip-check` | Skip the microphone volume check |

## 💻 Batch Files for Easy Use

The apps folder includes these batch files for quick access:

| File | Description |
|------|-------------|
| `dictate-spacebar.bat` | **[Recommended]** Starts Shift+Spacebar-controlled dictation mode |
| `dictate-clipboard.bat` | Starts continuous recording mode with clipboard |

## 📦 Installation

1. Install required packages:
   ```
   pip install openai-whisper pyaudio numpy pyperclip pyautogui keyboard
   ```

2. Install FFmpeg (required by Whisper for audio processing):
   - Windows (using Chocolatey): `choco install ffmpeg`
   - Windows (using Scoop): `scoop install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`

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
python dictate.py --continuous
```
Records continuously in fixed intervals until stopped with Ctrl+C.

## 📝 Tips for Better Dictation

1. **Using Shift+Spacebar** prevents accidental activation when typing in other apps

2. **Choose the right model**:
   - `tiny`: Fastest but least accurate
   - `small`: Good balance of speed/accuracy for most users
   - `medium`: More accurate but slower
   - `large`: Most accurate but slowest

2. **Speak clearly and at a moderate pace**

3. **Position your microphone properly** (6-12 inches from your mouth)

4. **Specify your language** for better accuracy:
   ```
   python dictate.py --spacebar --language en
   ```

5. **Review your microphone settings** in Windows Sound Control Panel

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
   - Run the command prompt as administrator
   - On macOS/Linux, you may need additional permissions

## Notes

- The script creates temporary audio files that are deleted after transcription
- Shift+Spacebar mode gives you precise control over when recording starts and stops
- Using Shift+Spacebar instead of just Spacebar prevents accidental activations
- The text is automatically copied to clipboard for easy pasting

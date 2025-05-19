# Whisper Dictation Tool

A simple command-line tool for speech recognition and dictation using OpenAI's Whisper.

## Installation

1. Make sure you have the required dependencies:
   ```
   pip install openai-whisper pyaudio numpy
   ```

2. Ensure you have FFmpeg installed (required by Whisper for audio processing).

## Basic Usage

Run the dictation tool with default settings:
```
python dictate.py
```

This will:
- Load the "base" Whisper model
- Record audio for 10 seconds
- Transcribe your speech
- Display the result

## Command Line Options

| Option | Description |
|--------|-------------|
| `--model MODEL` | Choose Whisper model size: tiny, base, small, medium, large, turbo (default: base) |
| `--language LANG` | Specify language code (e.g., en, es, fr) or "auto" for detection (default: auto) |
| `--save FILE` | Save transcription to specified file |
| `--continuous` | Enable continuous dictation mode (keeps recording until Ctrl+C) |
| `--duration SECONDS` | Set recording duration in seconds (default: 10) |
| `--skip-check` | Skip the microphone volume check |

## Examples

1. **Use a better model for more accurate transcription**:
   ```
   python dictate.py --model small
   ```

2. **For continuous dictation** (keeps running until stopped):
   ```
   python dictate.py --continuous
   ```

3. **Specify the language** (for more accurate results):
   ```
   python dictate.py --language en
   ```

4. **Save the transcription to a file**:
   ```
   python dictate.py --save dictation_result.txt
   ```

5. **Full example with all options**:
   ```
   python dictate.py --model small --language en --continuous --duration 5 --save notes.txt
   ```

## Microphone Selection

When running the script, it will:
1. Display a list of available microphones
2. Allow you to select a specific microphone
3. Perform a volume check to ensure your microphone is working properly

## Troubleshooting

1. **If you have microphone issues**:
   - Check your system's sound settings to ensure your microphone is set as the default input device
   - Increase microphone volume in system settings
   - Try a different microphone if available

2. **If transcription quality is poor**:
   - Use a more powerful model (`--model medium` or `--model large`)
   - Speak more clearly and avoid background noise
   - Position the microphone closer to your mouth

3. **If the script takes too long to transcribe**:
   - Use a smaller model (`--model tiny` or `--model base`)
   - Reduce the recording duration (`--duration 3`)

## Notes

- The script creates temporary audio files that are deleted after transcription
- Press Ctrl+C to stop the dictation process at any time

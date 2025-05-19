@echo off
REM Start Whisper in continuous dictation mode with the small model
REM This automatically copies each transcription to clipboard

echo Starting Whisper dictation with continuous clipboard mode...
echo Speak clearly into your microphone.
echo Each transcription will be automatically copied to clipboard.
echo Press Ctrl+C to stop.
echo.

python %~dp0\dictate.py --model small --continuous

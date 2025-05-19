@echo off
REM Start Whisper in Shift+Spacebar-controlled dictation mode with the small model
REM Press Shift+Spacebar to start recording, press Shift+Spacebar again to stop

REM Use a descriptive title to avoid confusion with other dictate commands
title Whisper Dictation Tool

echo Starting Whisper Speech-to-Text Dictation...
echo.
echo QUICK INSTRUCTIONS:
echo   1. Press SHIFT+SPACEBAR to START recording
echo   2. Speak into your microphone
echo   3. Press SHIFT+SPACEBAR again to STOP recording and transcribe
echo   4. Press ESC to exit when done
echo.
echo Each transcription will be automatically copied to clipboard.
echo.

python %~dp0\dictate.py

@echo off
REM Start Whisper in Shift+Spacebar-controlled dictation mode with the small model
REM Press Shift+Spacebar to start recording, press Shift+Spacebar again to stop

echo Starting Whisper dictation with Shift+Spacebar control...
echo.
echo INSTRUCTIONS:
echo   1. Press SHIFT+SPACEBAR to START recording
echo   2. Speak into your microphone
echo   3. Press SHIFT+SPACEBAR again to STOP recording and transcribe
echo   4. Press ESC to exit when done
echo.
echo Each transcription will be automatically copied to clipboard.
echo.

python %~dp0\dictate.py --model small --spacebar --clipboard

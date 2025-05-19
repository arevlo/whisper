@echo off
REM Force-Kill script for Whisper dictation tool
REM Use this if the dictation tool gets stuck and won't exit

echo Force-killing Python processes...
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
echo Done. You can restart the dictation tool now.
pause

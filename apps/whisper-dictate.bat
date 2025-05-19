@echo off
REM This is a simple batch file that runs the whisper dictation tool with default settings
REM Simply run 'whisper-dictate' from the command line

cd /d %~dp0
python dictate.py

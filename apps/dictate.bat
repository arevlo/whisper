@echo off
REM This is a simple batch file that runs the dictation tool with default settings
REM Simply run 'dictate' from the command line

cd /d %~dp0
python dictate.py

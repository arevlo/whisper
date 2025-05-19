#!/bin/bash
# Whisper Dictation Tool launcher for macOS and Linux

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the dictation tool with all passed arguments
python3 dictate.py "$@"

#!/bin/bash
# Whisper Dictation Tool - Linux/WSL version
# This script runs the dictation tool using python3

echo "Whisper Dictation Tool"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the dictation script with all passed arguments
python3 "$SCRIPT_DIR/dictate.py" "$@"

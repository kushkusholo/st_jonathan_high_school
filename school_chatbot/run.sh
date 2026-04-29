#!/bin/bash

# St. Jonathan High School Chatbot Launcher
# This script sets up and runs the chatbot on Mac/Linux

echo ""
echo "========================================"
echo "ST. JONATHAN HIGH SCHOOL CHATBOT"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/"
    echo "Or use: brew install python3 (on Mac)"
    exit 1
fi

echo "[✓] Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[!] Creating virtual environment..."
    python3 -m venv venv
    echo "[✓] Virtual environment created"
fi

# Activate virtual environment
echo "[!] Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "[!] Installing dependencies..."
pip install -r requirements.txt > /dev/null
echo "[✓] Dependencies installed"

# Run the Flask app
echo ""
echo "========================================"
echo "Starting chatbot server..."
echo "========================================"
echo ""
echo "Open your browser and go to:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

python3 app.py

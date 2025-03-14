#!/bin/bash
# Script to run auto_blog on Android using Termux
# Make sure to install required packages with:
# pkg install python git openssl

echo "=========================================="
echo "Auto-Blog System - Android Setup"
echo "=========================================="

# Check if we're running in Termux
if [ -d "/data/data/com.termux" ]; then
  echo "✓ Running in Termux environment"
else
  echo "⚠️ Warning: Not running in Termux. This script is designed for Termux on Android."
  echo "Some commands might not work correctly."
fi

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python installation
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "❌ Python not found. Please install Python:"
  echo "pkg install python"
  exit 1
fi

echo "✓ Using Python: $($PYTHON_CMD --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  $PYTHON_CMD -m venv venv
  if [ $? -ne 0 ]; then
    echo "⚠️ Failed to create venv with $PYTHON_CMD -m venv."
    echo "Trying with pip install virtualenv..."
    pip install virtualenv
    virtualenv venv
    if [ $? -ne 0 ]; then
      echo "❌ Failed to create virtual environment."
      echo "Please install venv: pip install virtualenv"
      exit 1
    fi
  fi
  echo "✓ Virtual environment created."
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
  echo "❌ Failed to activate virtual environment."
  exit 1
fi
echo "✓ Virtual environment activated."

# Install requirements if needed
if [ ! -f "venv/requirements_installed" ]; then
  echo "📦 Installing requirements..."
  pip install -r requirements.txt
  if [ $? -eq 0 ]; then
    touch venv/requirements_installed
    echo "✓ Requirements installed successfully."
  else
    echo "⚠️ Warning: Some requirements failed to install."
    echo "Will attempt to continue anyway."
  fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    echo "⚠️ .env file not found. Creating from example..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your API keys and GitHub credentials."
  else
    echo "❌ No .env or .env.example file found."
    echo "Please create a .env file with your API keys and GitHub credentials."
    exit 1
  fi
fi

# Run the system
echo "=========================================="
echo "Starting Auto-Blog System..."
echo "=========================================="
$PYTHON_CMD run.py

# Deactivate virtual environment
deactivate 
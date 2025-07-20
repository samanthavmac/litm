#!/bin/bash

# Exit on error
set -e

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Run the Flask app
echo "Starting the Flask server..."
export FLASK_APP=app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

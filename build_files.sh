#!/bin/bash
echo "Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages

echo "Collecting static files..."
python3 manage.py collectstatic --noinput
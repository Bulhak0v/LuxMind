#!/bin/bash
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput
#!/bin/bash

# Railway startup script that ensures database is initialized before starting the app
echo "🚀 Starting Manufacturing Workload Management App..."

# Initialize database schema
echo "📝 Initializing database schema..."
python railway_init.py

# Start the application
echo "🌐 Starting Gunicorn server..."
exec gunicorn run:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --preload 
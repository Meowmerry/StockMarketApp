#!/bin/bash

# Stock Market App Startup Script

echo "🚀 Starting Stock Market App..."
echo "📁 Activating virtual environment..."
source venv/bin/activate

echo "🗄️ Initializing database..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"

echo "🌐 Starting Flask application on http://localhost:5001"
echo "📊 Sample login credentials:"
echo "   Username: john_doe, Password: password123"
echo "   Username: demo_user, Password: demo123"
echo ""
echo "🎯 Press Ctrl+C to stop the server"
echo ""

python run.py

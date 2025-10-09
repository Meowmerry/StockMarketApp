#!/usr/bin/env python3
"""
WSGI entry point for production deployment on Render.com
"""

import os
from app import create_app, db

# Create Flask app instance
app = create_app()

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # For production, use environment variables
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

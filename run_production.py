"""
Production Server Launcher for Windows
Uses Waitress instead of Gunicorn (which doesn't support Windows)
"""

from waitress import serve
from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    print("="*70)
    print("S&P 500 PREDICTION DASHBOARD - PRODUCTION SERVER")
    print("="*70)
    print(f"\nServer starting on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    print("="*70 + "\n")

    # Serve with Waitress (production-ready WSGI server for Windows)
    serve(app, host=host, port=port, threads=4)

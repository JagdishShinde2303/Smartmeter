#!/usr/bin/env python3
"""
Flask Application Entry Point
"""
import os
import sys
from app import create_app

if __name__ == '__main__':
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'dev')
    os.environ.setdefault('FLASK_APP', 'run.py')
    
    # Create and run app
    app = create_app()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'dev'
    
    print(f'Starting Smart Energy Meter Backend')
    print(f'Environment: {os.getenv("FLASK_ENV")}')
    print(f'Debug mode: {debug}')
    print(f'Server running on http://0.0.0.0:{port}')
    
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)

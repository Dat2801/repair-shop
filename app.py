"""
Repair Shop Application
Main Entry Point
"""

import os
from app import create_app

# Create Flask app using factory pattern
app = create_app()

if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', True)
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Motor Việt-Nhật Server")
    print(f"{'='*60}")
    print(f"📍 Running on http://{host}:{port}")
    print(f"🐛 Debug Mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )

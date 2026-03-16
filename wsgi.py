"""
WSGI Entry Point for Gunicorn
"""
import os
import sys
from dotenv import load_dotenv

# Ensure repo root is on sys.path so modules like `config` can be imported
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

load_dotenv()

from factory import create_app

app = create_app()

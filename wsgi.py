"""
WSGI Entry Point for Gunicorn
"""
import os
from dotenv import load_dotenv

load_dotenv()

from factory import create_app

app = create_app()

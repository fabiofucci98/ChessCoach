"""Pytest shared fixtures / path setup."""
import os
import sys

# Make the backend package importable when running pytest from any directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

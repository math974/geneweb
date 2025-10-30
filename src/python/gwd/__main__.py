"""Main entry point for gwd module."""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from gwd.cli.main import serve
except ImportError:
    # Fallback if running from gwd directory
    from cli.main import serve

if __name__ == "__main__":
    serve()


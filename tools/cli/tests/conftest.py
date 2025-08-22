"""Pytest configuration for bpsai_pair tests."""
import sys
from pathlib import Path

# Add the package directory to Python path
package_dir = Path(__file__).parent.parent
sys.path.insert(0, str(package_dir))

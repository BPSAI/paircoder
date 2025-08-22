#!/usr/bin/env python3
"""Run tests for bpsai_pair package."""
import subprocess
import sys
from pathlib import Path

def main():
    """Run pytest with proper configuration."""
    test_dir = Path(__file__).parent / "tests"
    package_dir = Path(__file__).parent

    # Run pytest with the package directory in PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = str(package_dir)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", str(test_dir)],
        env=env
    )

    return result.returncode

if __name__ == "__main__":
    import os
    sys.exit(main())

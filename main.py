#!/usr/bin/env python3
"""
Entry point for deploy_tool.
Delegates to deploy_tool.cli.main() for robust CLI execution.
"""

import sys
from pathlib import Path

# Ensure local package is importable when run directly as ./main.py
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from deploy_tool.cli import main

if __name__ == "__main__":
    sys.exit(main())

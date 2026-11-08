#!/usr/bin/env python3
"""Old name of proof.py, kept so existing hooks and CI jobs keep working. Use proof.py."""
import os
import runpy
import sys

sys.argv[0] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proof.py")
runpy.run_path(sys.argv[0], run_name="__main__")

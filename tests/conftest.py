"""
conftest.py

Pytest automatically runs this before any tests. It makes sure the
database exists (with the 'scans' table) before detector.py tries to
query sender history -- otherwise tests fail with "no such table".
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import database

database.init_db()

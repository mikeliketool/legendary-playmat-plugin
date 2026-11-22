"""Make the plugin folder importable. GIMP 3 needs its hyphenated name, so it can't be a Python package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "legendary-playmat"))

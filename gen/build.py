#!/usr/bin/env python3
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tokens import THEMES

OUT = Path(__file__).parent.parent / "assets"
CARDS = ["title", "desktop"]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    only = sys.argv[1:] or CARDS
    for name in only:
        module = importlib.import_module(name)
        for theme in THEMES:
            (OUT / f"{name}-{theme}.svg").write_text(module.svg(theme))
            print(f"assets/{name}-{theme}.svg")

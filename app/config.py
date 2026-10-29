from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARDS_DIR = ROOT / "standards"
PRIVATE_DIR = ROOT / "data" / "private"
OUTPUT_DIR = ROOT / "outputs"
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


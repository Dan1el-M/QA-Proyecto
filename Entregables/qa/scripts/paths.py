"""Keep QA outputs inside Entregables and application sources at the repository root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT.parent if (ROOT.parent / 'config/application.rb').is_file() else ROOT
DOCS = ROOT / 'docs'
DATA = ROOT / 'qa/data'

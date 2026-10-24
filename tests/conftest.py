import sys
from pathlib import Path

# Permite "from app import ..." ao rodar pytest a partir da raiz do repositório.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

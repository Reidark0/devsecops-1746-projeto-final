"""Testes de execução para o script de autoavaliação (selfcheck.py).

Trilha 3: as 7 falhas (F1-F7) foram corrigidas no código, então o selfcheck
deve reportar sucesso (exit code 0) em vez de detectar pendências.
"""

import subprocess
import sys
from pathlib import Path


def test_selfcheck_execution():
    repo_root = Path(__file__).resolve().parent.parent
    script = repo_root / "scripts" / "selfcheck.py"
    assert script.exists(), "O script scripts/selfcheck.py deve existir"

    res_n3 = subprocess.run(
        [sys.executable, str(script), "--nivel", "3"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert res_n3.returncode == 0, "selfcheck --nivel 3 deve passar após a correção de F1 a F7"
    assert "SUCESSO" in res_n3.stdout


if __name__ == "__main__":
    test_selfcheck_execution()
    print("ALL TESTS PASSED")

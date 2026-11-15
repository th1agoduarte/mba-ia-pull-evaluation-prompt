"""
Teste rápido do provider configurado: instancia os LLMs pelo próprio
src/utils.py (o mesmo caminho que evaluate.py e metrics.py usam) e faz uma
chamada curta em cada um. Confirma credenciais, nome de modelo e rota
(direta ou gateway) antes de gastar uma avaliação inteira.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from utils import get_eval_llm, get_llm  # noqa: E402

failed = False
for label, factory in (("LLM_MODEL", get_llm), ("EVAL_MODEL", get_eval_llm)):
    try:
        llm = factory()
        name = getattr(llm, "model_name", None) or getattr(llm, "model", "?")
        answer = llm.invoke("Responda apenas com a palavra: ok").text.strip()
        print(f"✓ {label:<10} {name} -> {answer[:40]!r}")
    except Exception as e:  # noqa: BLE001
        failed = True
        print(f"✗ {label:<10} falhou: {type(e).__name__}: {str(e)[:300]}")

sys.exit(1 if failed else 0)

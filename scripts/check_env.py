"""
Mostra a configuração efetiva (provider, modelos, gateway) e quais variáveis
obrigatórias estão faltando, sem imprimir segredos. Respeita os overrides que o
Makefile aplica via `PROVIDER=...`, porque variáveis de ambiente têm prioridade
sobre o .env no python-dotenv.

Sai com código 1 se faltar alguma variável obrigatória.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

provider = os.getenv("LLM_PROVIDER", "")
base_url = os.getenv("OPENAI_BASE_URL", "")

required = [
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "USERNAME_LANGSMITH_HUB",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "EVAL_MODEL",
]
if provider == "google":
    required.append("GOOGLE_API_KEY")
elif provider == "openai":
    required.append("OPENAI_API_KEY")

print(f"Provider (utils.get_llm): {provider or '-'}")
print(f"Rota:                    {'gateway LiteLLM em ' + base_url if base_url else 'direta no provider'}")
print(f"LLM_MODEL:               {os.getenv('LLM_MODEL') or '-'}")
print(f"EVAL_MODEL:              {os.getenv('EVAL_MODEL') or '-'}")
print(f"LANGSMITH_PROJECT:       {os.getenv('LANGSMITH_PROJECT') or '-'}")
print(f"USERNAME_LANGSMITH_HUB:  {os.getenv('USERNAME_LANGSMITH_HUB') or '-'}")
print()

missing = [v for v in required if not os.getenv(v)]
for v in required:
    print(f"  {'✗' if v in missing else '✓'} {v}")

if missing:
    print(f"\n❌ Faltando: {', '.join(missing)}")
    sys.exit(1)
print("\n✅ Configuração completa")

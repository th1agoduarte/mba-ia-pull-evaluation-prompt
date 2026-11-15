"""
Avalia um prompt arbitrário do Hub (por padrão o v1 original,
leonanluppi/bug_to_user_story_v1) contra o MESMO dataset e as MESMAS métricas
de src/evaluate.py, reaproveitando as funções dele sem alterá-lo.

Serve para medir o ponto de partida e documentar a comparação v1 x v2 no README.

Uso: python scripts/evaluate_baseline.py [owner/prompt]
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)  # evaluate.py usa caminhos relativos

from langsmith import Client  # noqa: E402

from evaluate import create_evaluation_dataset, display_results, run_experiment  # noqa: E402

prompt_name = sys.argv[1] if len(sys.argv) > 1 else "leonanluppi/bug_to_user_story_v1"
dataset_name = f"{os.environ.get('LANGSMITH_PROJECT') or os.getenv('LANGSMITH_PROJECT')}-eval"

client = Client()
create_evaluation_dataset(client, dataset_name, "datasets/bug_to_user_story.jsonl")
scores, url = run_experiment(client, prompt_name, dataset_name)
passed = display_results(prompt_name, scores)
print(f"\nExperimento: {url}")
sys.exit(0 if passed else 1)

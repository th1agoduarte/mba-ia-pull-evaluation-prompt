# Evidências

| Arquivo | Conteúdo |
|---|---|
| `00-baseline-v1.md` | Prompt original v1 avaliado no mesmo dataset/métricas (`make eval-baseline`) |
| `01-iteracao-1.md` / `01-iteracao-1-repeticao.md` | v2 inicial, duas execuções (reprodutibilidade) |
| `02-iteracao-2.md` | **v2 final**: médias, nota por exemplo, saída gerada e justificativa do juiz para os 15 exemplos |
| `logs/` | Saída completa do terminal de cada execução (`iter2_projudge.log` = juiz Pro interrompido por limite de gasto) |
| `screenshots/` | Telas públicas do LangSmith: dataset, experimentos, prompt no Hub e 3 traces |

Os `.md` foram gerados com `make export-experiment ID=<selectedSessions> OUT=... TITLE=...` e as telas com `make screenshot URL=<link público> OUT=...`.

Links públicos: dataset https://smith.langchain.com/public/01c482a3-9481-44a9-ab25-822e592c81af/d · prompt https://smith.langchain.com/hub/evaluation-prompt/bug_to_user_story_v2

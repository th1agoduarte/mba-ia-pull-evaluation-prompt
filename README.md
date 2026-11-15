# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Desafio do módulo **Prompt Engineering** do MBA em Engenharia de Software com IA (Full Cycle).
O enunciado completo está em [DESAFIO.md](DESAFIO.md).

O projeto faz pull do prompt de baixa qualidade `leonanluppi/bug_to_user_story_v1` do LangSmith Prompt Hub, refatora-o em `prompts/bug_to_user_story_v2.yml`, publica a v2 no Hub e a avalia contra um dataset de 15 bugs. A meta é nota ≥ 0.8 em Helpfulness, Correctness, F1-Score, Clarity e Precision.

> 🚧 Em andamento: as seções "Técnicas Aplicadas" e "Resultados Finais" serão preenchidas ao longo das iterações.

## Técnicas Aplicadas (Fase 2)

_A preencher: técnicas escolhidas (Few-shot obrigatório + ao menos uma adicional), justificativa e exemplos de como cada uma aparece no prompt v2._

## Resultados Finais

_A preencher:_

- _Link público do dataset de avaliação com os experimentos (`Client().share_dataset(...)`)_
- _Screenshots das avaliações com todas as notas ≥ 0.8_
- _Tabela de evolução das iterações (v2.0 → v2.n) com as 5 métricas_
- _Comparação v1 × v2: o que mudou e por quê_

## Como Executar

### Pré-requisitos

- Python 3.10+, `make`
- Docker + Docker Compose. Só é necessário para usar Anthropic ou AWS Bedrock (gateway LiteLLM)
- Conta no [LangSmith](https://smith.langchain.com) com API key e **handle público do Hub** criado (veja "Handle do LangSmith Hub" em [DESAFIO.md](DESAFIO.md))
- API key de um provider de LLM. O padrão é Google Gemini (free tier): https://aistudio.google.com/apikey

### Instalação

```bash
make setup      # cria o venv, instala requirements.txt e gera o .env a partir do .env.example
make check-env  # mostra o que falta preencher no .env (sem exibir segredos)
make smoke      # uma chamada curta em cada modelo para validar credenciais
```

Sem `make`: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cp .env.example .env`.

### Execução

| Fase | Comando | Equivalente |
|---|---|---|
| 1. Pull do prompt v1 | `make pull` | `python src/pull_prompts.py` |
| 2. Refatorar | editar `prompts/bug_to_user_story_v2.yml` | — |
| 3. Validar estrutura | `make test` | `pytest tests/test_prompts.py -v` |
| 4. Push da v2 (pública) | `make push` | `python src/push_prompts.py` |
| 5. Avaliar | `make eval` | `python src/evaluate.py` |
| Ciclo de iteração | `make validate` | testes → push → avaliação |

Rode sempre na raiz do repositório. Para iterar, repita as fases 2 a 5 até todas as métricas ficarem ≥ 0.8. `make help` lista todos os alvos.

O roteiro para conferir cada requisito do enunciado está em [VALIDACAO.md](VALIDACAO.md).

### Usando outros LLMs

O `src/utils.py` original (que o enunciado proíbe alterar) aceita só `google` e `openai`. Para usar outros providers sem tocar nele, o projeto inclui um gateway [LiteLLM](https://docs.litellm.ai) em Docker. O gateway expõe Anthropic e AWS Bedrock numa API compatível com a OpenAI, e o projeto chega a ele pelo caminho `openai` que já existe.

```bash
make eval                     # padrão do .env (Gemini direto)
make eval PROVIDER=anthropic  # Claude via gateway (sobe o container automaticamente)
make eval PROVIDER=aws        # Bedrock via gateway
make eval PROVIDER=openai     # OpenAI direta
make gateway-test             # testa o gateway com Gemini, sem custo
make gateway-down
```

Os modelos de cada provider ficam nos presets `<PROVIDER>_LLM_MODEL` / `<PROVIDER>_EVAL_MODEL` do `.env`. O `PROVIDER=` vale só para aquela execução e não altera o `.env`.

> O LangSmith usado é sempre o da nuvem. A versão self-hosted (Docker) exige licença Enterprise, e o entregável precisa de links públicos do smith.langchain.com.

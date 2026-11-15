"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

O `dangerously_pull_public_prompt=True` é obrigatório sempre que o identificador
tem dono explícito ("owner/nome"): o LangSmith bloqueia esse pull por padrão
porque um prompt do Hub é um objeto LangChain serializado, que pode vir de
terceiros. Aqui o prompt é o semente do desafio, então o risco é conhecido.
"""

import sys
import yaml
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from utils import check_env_vars, print_section_header, save_yaml

load_dotenv()


def _str_presenter(dumper, value):
    """Grava textos multilinha como bloco literal (|), legível e fiel ao original."""
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


yaml.add_representer(str, _str_presenter)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# identificador no Hub -> arquivo local
PROMPTS_TO_PULL = {
    "leonanluppi/bug_to_user_story_v1": PROJECT_ROOT / "prompts" / "bug_to_user_story_v1.yml",
}

# Tipo da mensagem do LangChain -> campo no YAML
ROLE_TO_FIELD = {
    "SystemMessagePromptTemplate": "system_prompt",
    "HumanMessagePromptTemplate": "user_prompt",
}


def prompt_to_dict(prompt: ChatPromptTemplate, identifier: str) -> dict:
    """Converte o ChatPromptTemplate do Hub no formato YAML do projeto."""
    repo = identifier.split("/")[-1]
    data = {
        "description": "Prompt para converter relatos de bugs em User Stories",
        "system_prompt": "",
        "user_prompt": "",
        "version": repo.rsplit("_", 1)[-1] if "_v" in repo else "v1",
        "source": identifier,
        "commit_hash": (prompt.metadata or {}).get("lc_hub_commit_hash", ""),
        "pulled_at": date.today().isoformat(),
        "input_variables": list(prompt.input_variables),
        "tags": ["bug-analysis", "user-story", "product-management"],
    }

    for message in prompt.messages:
        field = ROLE_TO_FIELD.get(type(message).__name__)
        if field is None:
            raise ValueError(f"Tipo de mensagem não suportado: {type(message).__name__}")
        data[field] = message.prompt.template

    return {repo: data}


def pull_prompts_from_langsmith() -> bool:
    """Faz pull de todos os prompts de PROMPTS_TO_PULL e salva em YAML."""
    client = Client()
    ok = True

    for identifier, output_path in PROMPTS_TO_PULL.items():
        print(f"⬇️  Pull: {identifier}")
        try:
            prompt = client.pull_prompt(identifier, dangerously_pull_public_prompt=True)
        except Exception as e:
            print(f"   ❌ Falha no pull: {e}")
            ok = False
            continue

        data = prompt_to_dict(prompt, identifier)
        if save_yaml(data, str(output_path)):
            print(f"   ✓ {len(prompt.messages)} mensagens, variáveis {prompt.input_variables}")
            print(f"   ✓ Salvo em {output_path.relative_to(PROJECT_ROOT)}")
        else:
            ok = False

    return ok


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    if not pull_prompts_from_langsmith():
        return 1

    print("\n✅ Pull concluído")
    return 0


if __name__ == "__main__":
    sys.exit(main())

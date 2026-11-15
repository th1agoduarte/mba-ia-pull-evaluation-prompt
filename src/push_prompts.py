"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

O nome publicado é {USERNAME_LANGSMITH_HUB}/<chave do YAML>, que é exatamente o
que src/evaluate.py puxa do Hub para avaliar. A variável do template precisa ser
{bug_report}, a chave de entrada do dataset de avaliação.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from langsmith.utils import LangSmithConflictError

from utils import check_env_vars, load_yaml, print_section_header, validate_prompt_structure

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml"
REQUIRED_VARIABLES = {"bug_report"}


def build_prompt_template(prompt_data: dict) -> ChatPromptTemplate:
    """Monta o ChatPromptTemplate (system + user) a partir do YAML."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])


def build_description(prompt_data: dict) -> str:
    """Descrição exibida no Hub, incluindo as técnicas aplicadas."""
    techniques = ", ".join(prompt_data.get("techniques_applied", []))
    return f"{prompt_data['description'].strip()} Técnicas: {techniques}."


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    identifier = f"{username}/{prompt_name}"
    template = build_prompt_template(prompt_data)

    # Tags do Hub: tags do YAML + versão + técnicas (sem duplicatas, ordem preservada)
    techniques = prompt_data.get("techniques_applied", [])
    tags = list(dict.fromkeys(
        [*prompt_data.get("tags", []), prompt_data.get("version", ""), *techniques]
    ))
    tags = [t for t in tags if t]

    print(f"⬆️  Push: {identifier}")
    print(f"   Versão: {prompt_data.get('version')} | Técnicas: {', '.join(techniques)}")

    try:
        url = Client().push_prompt(
            identifier,
            object=template,
            is_public=True,
            description=build_description(prompt_data),
            readme=build_readme(identifier, prompt_data),
            tags=tags,
        )
    except LangSmithConflictError:
        # O Hub recusa um commit idêntico ao último: o prompt já está atualizado.
        print("   ✓ Nenhuma alteração desde o último push (o Hub já tem esta versão)")
        return True
    except Exception as e:
        print(f"   ❌ Falha no push: {e}")
        if "handle" in str(e).lower() or "403" in str(e) or "404" in str(e):
            print("   Confira se USERNAME_LANGSMITH_HUB é o seu handle público do Hub.")
        return False

    print(f"   ✓ Publicado (público): {url}")
    return True


def build_readme(identifier: str, prompt_data: dict) -> str:
    """README exibido na página do prompt no Hub."""
    techniques = "\n".join(f"- {t}" for t in prompt_data.get("techniques_applied", []))
    return (
        f"# {identifier}\n\n"
        f"{prompt_data['description'].strip()}\n\n"
        f"**Versão:** {prompt_data.get('version')}\n\n"
        f"## Técnicas aplicadas\n\n{techniques}\n\n"
        "## Entrada\n\n- `bug_report`: texto do relato de bug\n"
    )


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    _, errors = validate_prompt_structure(prompt_data)

    if not str(prompt_data.get("user_prompt", "")).strip():
        errors.append("user_prompt está vazio")

    if not errors:
        variables = set(build_prompt_template(prompt_data).input_variables)
        if variables != REQUIRED_VARIABLES:
            errors.append(
                f"Variáveis do template devem ser {sorted(REQUIRED_VARIABLES)}, "
                f"encontradas: {sorted(variables)} (escape chaves literais com {{{{ }}}})"
            )
        if "{bug_report}" in prompt_data["system_prompt"]:
            errors.append("{bug_report} deve aparecer só no user_prompt, não no system_prompt")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(str(PROMPT_FILE))
    if not data:
        return 1

    all_ok = True
    for prompt_name, prompt_data in data.items():
        valid, errors = validate_prompt(prompt_data)
        if not valid:
            print(f"❌ {prompt_name} inválido:")
            for error in errors:
                print(f"   - {error}")
            all_ok = False
            continue

        all_ok = push_prompt_to_langsmith(prompt_name, prompt_data) and all_ok

    if not all_ok:
        return 1

    print("\n✅ Push concluído. Próximo passo: python src/evaluate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

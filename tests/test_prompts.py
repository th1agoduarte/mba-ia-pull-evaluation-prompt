"""
Testes automatizados para validação de prompts.
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    data = load_prompts(PROMPT_FILE)
    assert PROMPT_KEY in data, f"Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE.name}"
    return data[PROMPT_KEY]


@pytest.fixture(scope="module")
def system_prompt(prompt):
    return prompt.get("system_prompt") or ""


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt, system_prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt, "Campo 'system_prompt' ausente"
        assert isinstance(system_prompt, str)
        assert system_prompt.strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        match = re.search(r"Você é (um|uma) ([^.\n]+)", system_prompt)
        assert match, "Nenhuma persona definida ('Você é um/uma ...')"
        persona = match.group(2).lower()
        assert any(role in persona for role in ("product", "analista", "pm", "po")), (
            f"A persona deve ser de produto/negócio, encontrada: '{match.group(2)}'"
        )

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "User Story" in system_prompt
        # Modelo padrão Como / eu quero / para que
        assert re.search(r"Como um .*eu quero .*para que", system_prompt), (
            "O prompt não exige o formato 'Como um ..., eu quero ..., para que ...'"
        )
        # Critérios de aceitação no formato Gherkin
        assert "Critérios de Aceitação" in system_prompt
        for keyword in ("Dado que", "Quando", "Então"):
            assert keyword in system_prompt, f"Formato Dado/Quando/Então incompleto: falta '{keyword}'"

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        examples = re.split(r"^## Exemplo \d+", system_prompt, flags=re.MULTILINE)[1:]
        assert len(examples) >= 2, f"Few-shot exige ao menos 2 exemplos, encontrados: {len(examples)}"
        for i, example in enumerate(examples, 1):
            assert "Relato:" in example, f"Exemplo {i} sem entrada ('Relato:')"
            assert "Resposta:" in example, f"Exemplo {i} sem saída ('Resposta:')"
            answer = example.split("Resposta:", 1)[1]
            assert re.search(r"Como (um|uma|o) .*eu quero .*para que", answer), (
                f"A saída do exemplo {i} não segue o formato de User Story"
            )
            assert "- Dado que" in answer, f"A saída do exemplo {i} não tem critérios de aceitação"

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        text = yaml.safe_dump(prompt, allow_unicode=True)
        assert "[TODO]" not in text
        assert not re.search(r"\bTODO\b", text), "Há marcações TODO no prompt"

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied")
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas, encontradas: {len(techniques)}"
        assert all(isinstance(t, str) and t.strip() for t in techniques)
        assert any("few-shot" in t.lower() for t in techniques), "Few-shot Learning é obrigatório"

    def test_prompt_template_uses_only_bug_report(self, prompt, system_prompt):
        """O template deve ter apenas {bug_report}, e só no user prompt (system x user)."""
        from langchain_core.prompts import ChatPromptTemplate

        template = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("user", prompt["user_prompt"])]
        )
        assert set(template.input_variables) == {"bug_report"}
        assert "{bug_report}" in prompt["user_prompt"]
        assert "{bug_report}" not in system_prompt

    def test_prompt_passes_project_validation(self, prompt):
        """Usa a mesma validação estrutural de src/utils.py."""
        valid, errors = validate_prompt_structure(prompt)
        assert valid, errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

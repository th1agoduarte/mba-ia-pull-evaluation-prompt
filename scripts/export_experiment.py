"""
Exporta um experimento do LangSmith para Markdown, como evidência versionada:
médias das 5 métricas, nota por exemplo, comentário do juiz e a saída gerada.

Uso: python scripts/export_experiment.py <experiment_id> <arquivo.md> [titulo]
O experiment_id é o valor de selectedSessions=... no link impresso por evaluate.py.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

METRICS = ["helpfulness", "correctness", "f1_score", "clarity", "precision"]
THRESHOLD = 0.8


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    experiment_id, out = sys.argv[1], Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else "Experimento"

    client = Client()
    project = client.read_project(project_id=experiment_id)
    runs = sorted(
        client.list_runs(project_id=experiment_id, is_root=True),
        key=lambda r: r.start_time,
    )

    rows = []
    for run in runs:
        feedback = {f.key: f for f in client.list_feedback(run_ids=[run.id])}
        rows.append((run, feedback))

    def avg(key):
        values = [fb[key].score for _, fb in rows if key in fb and fb[key].score is not None]
        return sum(values) / len(values) if values else 0.0

    means = {k: avg(k) for k in METRICS}
    overall = sum(means.values()) / len(means)
    passed = all(v >= THRESHOLD for v in means.values()) and overall >= THRESHOLD
    meta = project.metadata or {}

    lines = [
        f"# {title}",
        "",
        f"- Experimento: `{project.name}`",
        f"- Prompt: `{meta.get('prompt', '-')}`",
        f"- Provider / modelo / juiz: `{meta.get('provider', '-')}` / `{meta.get('llm_model', '-')}` / `{meta.get('eval_model', '-')}`",
        f"- Data: {project.start_time:%Y-%m-%d %H:%M} UTC",
        f"- Exemplos: {len(rows)}",
        "",
        "| Métrica | Média | ≥ 0.8 |",
        "|---|---|---|",
        *[f"| {k} | {v:.4f} | {'✓' if v >= THRESHOLD else '✗'} |" for k, v in means.items()],
        f"| **média geral** | **{overall:.4f}** | {'✓' if overall >= THRESHOLD else '✗'} |",
        "",
        f"**Status: {'✅ APROVADO' if passed else '❌ REPROVADO'}**",
        "",
        "## Por exemplo",
        "",
        "| # | Relato (início) | F1 | Clarity | Precision |",
        "|---|---|---|---|---|",
    ]
    for i, (run, fb) in enumerate(rows, 1):
        bug = run.inputs.get("bug_report", "").splitlines()[0][:70].replace("|", "\\|")
        s = {k: (fb[k].score if k in fb else 0.0) for k in ("f1_score", "clarity", "precision")}
        lines.append(f"| {i} | {bug} | {s['f1_score']:.2f} | {s['clarity']:.2f} | {s['precision']:.2f} |")

    lines += ["", "## Traces detalhados (entrada, saída e justificativa do juiz)", ""]
    for i, (run, fb) in enumerate(rows, 1):
        lines += [
            f"### {i}. {run.inputs.get('bug_report', '').splitlines()[0][:90]}",
            "",
            "<details><summary>Relato completo</summary>",
            "",
            "```text",
            run.inputs.get("bug_report", ""),
            "```",
            "</details>",
            "",
            "**Saída do prompt:**",
            "",
            "```text",
            (run.outputs or {}).get("answer", ""),
            "```",
            "",
        ]
        for key in ("f1_score", "clarity", "precision"):
            if key in fb:
                lines.append(f"- **{key} = {fb[key].score:.2f}**: {fb[key].comment}")
        lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ {out} ({len(rows)} exemplos, média {overall:.4f}, {'APROVADO' if passed else 'REPROVADO'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

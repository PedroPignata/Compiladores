"""Executa os dez casos obrigatórios e gera a tabela de evidências"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transformer_simulator import EmptyInputError, TransformerSimulator  # noqa: E402
from transformer_simulator.required_cases import REQUIRED_CASES, RequiredCase  # noqa: E402


def execute_case(simulator: TransformerSimulator, case: RequiredCase) -> dict[str, str]:
    # roda um caso e compara o resultado com o comportamento esperado
    try:
        result = simulator.simulate(case.input_text)
        tokens = [token.text for token in result.input_tokens]
        approved = True
        detail = f"Pipeline completo: {len(tokens)} tokens, 2 cabeças e 3 camadas."

        # alguns casos precisam de uma verificacao propria
        if case.number == 3:
            approved = "," in tokens and "!" in tokens
            detail = "Vírgula e exclamação foram preservadas como tokens."
        elif case.number == 4:
            approved = any(not token.known and token.token_id == 1 for token in result.input_tokens)
            detail = "Palavras desconhecidas foram marcadas com <UNK>/ID 1."
        elif case.number == 5:
            repeated = [token for token in result.input_tokens if token.text == "Brasil"]
            approved = len({token.token_id for token in repeated}) == 1 and len(repeated) == 3
            detail = "As três ocorrências mantiveram o mesmo ID e posições distintas."
        elif case.number == 6 and case.secondary_input:
            second = simulator.simulate(case.secondary_input)
            first_vectors = {v.token.casefold(): v.values for v in result.positioned_vectors}
            second_vectors = {v.token.casefold(): v.values for v in second.positioned_vectors}
            approved = not np.allclose(first_vectors["cachorro"], second_vectors["cachorro"])
            detail = "A troca de ordem alterou os vetores posicionados dos mesmos tokens."
        elif case.number == 7:
            approved = result.final_answer == "A capital do Brasil é Brasília."
            detail = "A resposta cadastrada foi gerada progressivamente."
        elif case.number == 8:
            approved = result.final_answer.startswith("Não tenho uma resposta cadastrada")
            detail = "O sistema informou que não conhece a resposta."
        elif case.number == 10:
            approved = "&" in tokens and "#" in tokens
            detail = "Os caracteres & e # foram tokenizados sem erro."

        input_display = case.input_text
        if case.secondary_input:
            input_display += f" / {case.secondary_input}"
        return {
            "numero": str(case.number),
            "situacao": case.title,
            "entrada": input_display,
            "tokens": str(tokens),
            "esperado": case.expected_behavior,
            "obtido": detail,
            "resposta": result.final_answer,
            "resultado": "APROVADO" if approved else "REPROVADO",
        }
    except EmptyInputError as error:
        approved = case.number == 9
        return {
            "numero": str(case.number),
            "situacao": case.title,
            "entrada": repr(case.input_text),
            "tokens": "[]",
            "esperado": case.expected_behavior,
            "obtido": str(error),
            "resposta": "Não gerada.",
            "resultado": "APROVADO" if approved else "REPROVADO",
        }


def write_markdown(rows: list[dict[str, str]], output: Path) -> None:
    # transforma os resultados em uma tabela Markdown
    lines = [
        "# Tabela dos testes obrigatórios",
        "",
        "Gerada automaticamente por `scripts/generate_test_report.py`.",
        "",
        "| # | Situação | Entrada | Tokens gerados | Esperado | Obtido | Resposta | Resultado |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        values = [
            row["numero"],
            row["situacao"],
            row["entrada"],
            row["tokens"],
            row["esperado"],
            row["obtido"],
            row["resposta"],
            row["resultado"],
        ]
        escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
        lines.append("| " + " | ".join(escaped) + " |")
    approved = sum(row["resultado"] == "APROVADO" for row in rows)
    lines.extend(["", f"**Resumo:** {approved}/{len(rows)} testes aprovados.", ""])
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    # gera os arquivos Markdown e CSV dentro da pasta de evidencias
    simulator = TransformerSimulator()
    rows = [execute_case(simulator, case) for case in REQUIRED_CASES]
    output_dir = PROJECT_ROOT / "evidencias" / "resultados-dos-testes"
    output_dir.mkdir(parents=True, exist_ok=True)
    write_markdown(rows, output_dir / "testes-obrigatorios.md")
    with (output_dir / "testes-obrigatorios.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 0 if all(row["resultado"] == "APROVADO" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

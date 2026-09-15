import json

import numpy as np

from transformer_simulator import TransformerSimulator


def test_complete_pipeline_for_registered_question():
    # testa todas as etapas juntas usando uma pergunta conhecida
    result = TransformerSimulator().simulate("Qual   é a capital do Brasil?")

    assert result.normalization.normalized == "Qual é a capital do Brasil?"
    assert [token.text for token in result.input_tokens] == [
        "Qual",
        "é",
        "a",
        "capital",
        "do",
        "Brasil",
        "?",
    ]
    assert len(result.attention_heads) == 2
    assert len(result.layers) == 3
    assert result.final_answer == "A capital do Brasil é Brasília."
    assert result.processing_cycles == len(result.generation_steps) + 1
    assert [step.iteration for step in result.generation_steps] == list(
        range(1, len(result.generation_steps) + 1)
    )
    assert all(
        step.selected_token == max(step.candidates, key=lambda item: item.probability).token
        for step in result.generation_steps
    )
    assert all(
        np.isclose(sum(candidate.probability for candidate in step.candidates), 1.0)
        for step in result.generation_steps
    )


def test_result_is_json_serializable():
    # confirma que o resultado pode ser baixado pela interface
    result = TransformerSimulator().simulate("O que é um compilador?")

    serialized = json.dumps(result.to_dict(), ensure_ascii=False)

    assert "compilador traduz código-fonte" in serialized


def test_context_is_reprocessed_and_grows_between_generation_steps():
    # o contexto deve aumentar sempre que um novo token e escolhido
    result = TransformerSimulator().simulate("Quanto é 2 + 2?")
    counts = [step.context_token_count for step in result.generation_steps]

    assert counts == list(range(counts[0], counts[0] + len(counts)))
    assert all(len(step.context_summary) == 4 for step in result.generation_steps)

import numpy as np
import pytest

from transformer_simulator import EmptyInputError, TransformerSimulator
from transformer_simulator.required_cases import REQUIRED_CASES


# usa o mesmo simulador para conferir os casos exigidos na atividade
simulator = TransformerSimulator()


@pytest.mark.parametrize("case", [case for case in REQUIRED_CASES if case.number != 9])
def test_non_empty_required_cases_complete(case):
    result = simulator.simulate(case.input_text)

    assert result.input_tokens
    assert result.final_answer
    assert len(result.attention_heads) >= 2
    assert len(result.layers) >= 3


def test_case_3_keeps_punctuation_as_tokens():
    result = simulator.simulate(REQUIRED_CASES[2].input_text)
    assert [token.text for token in result.input_tokens][-2:] == ["mundo", "!"]
    assert "," in [token.text for token in result.input_tokens]


def test_case_4_marks_unknown_words():
    result = simulator.simulate(REQUIRED_CASES[3].input_text)
    assert any(not token.known and token.token_id == 1 for token in result.input_tokens)


def test_case_5_reuses_ids_but_preserves_positions():
    result = simulator.simulate(REQUIRED_CASES[4].input_text)
    brasil_tokens = [token for token in result.input_tokens if token.text == "Brasil"]
    assert len({token.token_id for token in brasil_tokens}) == 1
    assert len({token.position for token in brasil_tokens}) == 3


def test_case_6_order_changes_positioned_representation():
    # mostra que trocar a ordem muda a representacao dos mesmos tokens
    case = REQUIRED_CASES[5]
    first = simulator.simulate(case.input_text)
    second = simulator.simulate(case.secondary_input)

    first_by_token = {vector.token.casefold(): vector.values for vector in first.positioned_vectors}
    second_by_token = {vector.token.casefold(): vector.values for vector in second.positioned_vectors}
    assert not np.allclose(first_by_token["cachorro"], second_by_token["cachorro"])
    assert not np.allclose(first_by_token["homem"], second_by_token["homem"])


def test_case_7_generates_known_answer():
    result = simulator.simulate(REQUIRED_CASES[6].input_text)
    assert result.final_answer == "A capital do Brasil é Brasília."


def test_case_8_uses_honest_fallback():
    result = simulator.simulate(REQUIRED_CASES[7].input_text)
    assert result.final_answer.startswith("Não tenho uma resposta cadastrada")


def test_case_9_rejects_empty_text():
    with pytest.raises(EmptyInputError):
        simulator.simulate(REQUIRED_CASES[8].input_text)


def test_case_10_preserves_special_characters():
    result = simulator.simulate(REQUIRED_CASES[9].input_text)
    tokens = [token.text for token in result.input_tokens]
    assert "&" in tokens
    assert "#" in tokens

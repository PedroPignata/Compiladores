import pytest

from transformer_simulator.normalization import EmptyInputError, normalize_text
from transformer_simulator.tokenization import detokenize, tokenize


def test_normalization_collapses_spaces_and_preserves_case_and_punctuation():
    result = normalize_text("  Qual   é a capital do Brasil?  ")

    assert result.normalized == "Qual é a capital do Brasil?"


def test_empty_input_is_rejected():
    with pytest.raises(EmptyInputError, match="Digite uma frase"):
        normalize_text(" \n\t ")


def test_tokenizer_separates_unicode_words_and_punctuation():
    assert tokenize("Olá, Brasil!") == ["Olá", ",", "Brasil", "!"]


def test_detokenizer_restores_punctuation_spacing():
    assert detokenize(["A", "capital", "é", "Brasília", "."]) == "A capital é Brasília."

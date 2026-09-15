import numpy as np

from transformer_simulator.attention import calculate_attention, softmax
from transformer_simulator.embeddings import (
    add_position,
    generate_embeddings,
    generate_positional_encodings,
)
from transformer_simulator.layers import run_layers
from transformer_simulator.vocabulary import assign_token_ids


def _positioned(texts):
    # prepara os vetores usados por varios testes deste arquivo
    tokens = assign_token_ids(texts)
    embeddings = generate_embeddings(tokens)
    positions = generate_positional_encodings(tokens)
    return embeddings, positions, add_position(embeddings, positions)


def test_embeddings_are_deterministic_and_four_dimensional():
    # confirma que o mesmo token sempre recebe o mesmo embedding
    tokens = assign_token_ids(["Brasil", "Brasil"])
    first = generate_embeddings(tokens)
    second = generate_embeddings(tokens)

    assert first == second
    assert len(first[0].values) == 4
    assert first[0].values == first[1].values


def test_position_changes_equal_token_embeddings():
    embeddings, _, positioned = _positioned(["Brasil", "Brasil"])

    assert embeddings[0].values == embeddings[1].values
    assert positioned[0].values != positioned[1].values


def test_softmax_is_stable_and_sums_to_one():
    result = softmax(np.asarray([[1000.0, 1001.0, 1002.0]]), axis=1)

    assert np.isfinite(result).all()
    assert np.allclose(result.sum(axis=1), 1.0)


def test_two_attention_heads_have_valid_distributions():
    # cada linha dos pesos precisa formar uma distribuicao que soma um
    _, _, positioned = _positioned(["Qual", "é", "Brasil", "?"])
    heads, combined = calculate_attention(positioned)

    assert len(heads) == 2
    assert np.asarray(combined).shape == (4, 4)
    for head in heads:
        weights = np.asarray(head.weights)
        assert weights.shape == (4, 4)
        assert np.all(weights >= 0)
        assert np.allclose(weights.sum(axis=1), 1.0)


def test_three_layers_are_sequential_and_transform_the_vectors():
    # garante que nenhuma camada pule a saida da camada anterior
    _, _, positioned = _positioned(["Qual", "é", "Brasil", "?"])
    _, combined = calculate_attention(positioned)
    layers = run_layers(combined)

    assert len(layers) == 3
    assert layers[1].input_vectors == layers[0].output_vectors
    assert layers[2].input_vectors == layers[1].output_vectors
    assert all(layer.mean_change > 0 for layer in layers)

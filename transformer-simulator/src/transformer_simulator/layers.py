"""Três camadas sequenciais que transformam a saída da atenção."""

from __future__ import annotations

import math

import numpy as np

from .attention import softmax
from .models import LayerResult


PREPARATION_MATRIX = np.asarray(
    (
        (0.70, 0.10, 0.20, 0.00),
        (0.10, 0.60, 0.00, 0.30),
        (0.20, 0.00, 0.70, 0.10),
        (0.00, 0.30, 0.10, 0.60),
    ),
    dtype=float,
)


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _layer_result(
    name: str,
    description: str,
    before: np.ndarray,
    after: np.ndarray,
) -> LayerResult:
    return LayerResult(
        name=name,
        description=description,
        input_vectors=_matrix_tuple(before),
        output_vectors=_matrix_tuple(after),
        mean_change=float(np.mean(np.abs(after - before))),
    )


def _local_layer(inputs: np.ndarray) -> np.ndarray:
    outputs = np.zeros_like(inputs)
    for index in range(len(inputs)):
        neighbors = [(index, 0.60)]
        if index > 0:
            neighbors.append((index - 1, 0.20))
        if index + 1 < len(inputs):
            neighbors.append((index + 1, 0.20))
        total_weight = sum(weight for _, weight in neighbors)
        for neighbor_index, weight in neighbors:
            outputs[index] += inputs[neighbor_index] * weight / total_weight
    return outputs


def _context_layer(inputs: np.ndarray) -> np.ndarray:
    similarities = (inputs @ inputs.T) / math.sqrt(inputs.shape[1])
    weights = softmax(similarities, axis=1)
    return 0.55 * inputs + 0.45 * (weights @ inputs)


def _preparation_layer(inputs: np.ndarray) -> np.ndarray:
    return np.tanh(inputs @ PREPARATION_MATRIX + 0.10 * inputs)


def run_layers(
    combined_attention: tuple[tuple[float, ...], ...],
) -> tuple[LayerResult, ...]:
    """Executa três transformações; cada uma recebe a saída da anterior."""

    initial = np.asarray(combined_attention, dtype=float)
    local = _local_layer(initial)
    contextual = _context_layer(local)
    prepared = _preparation_layer(contextual)

    return (
        _layer_result(
            "Camada 1 - relações locais",
            "Combina cada token com seus vizinhos imediatos.",
            initial,
            local,
        ),
        _layer_result(
            "Camada 2 - relações contextuais",
            "Usa similaridade para combinar informações mesmo entre tokens distantes.",
            local,
            contextual,
        ),
        _layer_result(
            "Camada 3 - preparação da resposta",
            "Projeta e limita os vetores contextuais antes da previsão.",
            contextual,
            prepared,
        ),
    )

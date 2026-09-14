"""Embeddings didáticos e codificação posicional senoidal."""

from __future__ import annotations

import math

import numpy as np

from .models import TokenInfo, VectorInfo


EMBEDDING_DIMENSION = 4


def generate_embeddings(tokens: tuple[TokenInfo, ...]) -> tuple[VectorInfo, ...]:
    """Gera vetores determinísticos a partir do ID, sem valores aleatórios."""

    vectors: list[VectorInfo] = []
    for token in tokens:
        token_id = token.token_id
        values = (
            math.sin(token_id * 0.13),
            math.cos(token_id * 0.07),
            math.sin(token_id * 0.017 + 0.5),
            math.cos(token_id * 0.031 - 0.25),
        )
        vectors.append(VectorInfo(token.text, token.position, values))
    return tuple(vectors)


def generate_positional_encodings(
    tokens: tuple[TokenInfo, ...],
) -> tuple[VectorInfo, ...]:
    """Aplica a fórmula senoidal usada como inspiração em Transformers."""

    vectors: list[VectorInfo] = []
    for token in tokens:
        values: list[float] = []
        for dimension in range(EMBEDDING_DIMENSION):
            denominator = 10000 ** (2 * (dimension // 2) / EMBEDDING_DIMENSION)
            angle = token.position / denominator
            values.append(math.sin(angle) if dimension % 2 == 0 else math.cos(angle))
        vectors.append(VectorInfo(token.text, token.position, tuple(values)))
    return tuple(vectors)


def add_position(
    embeddings: tuple[VectorInfo, ...],
    positions: tuple[VectorInfo, ...],
) -> tuple[VectorInfo, ...]:
    if len(embeddings) != len(positions):
        raise ValueError("Embeddings e posições devem possuir o mesmo tamanho.")

    combined: list[VectorInfo] = []
    for embedding, position in zip(embeddings, positions, strict=True):
        values = np.asarray(embedding.values) + np.asarray(position.values)
        combined.append(VectorInfo(embedding.token, embedding.position, tuple(values)))
    return tuple(combined)

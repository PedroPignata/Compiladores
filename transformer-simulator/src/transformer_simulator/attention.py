"""Atenção escalada com duas cabeças e matrizes fixas documentadas"""

from __future__ import annotations
import math
import numpy as np
from .models import AttentionHeadResult, VectorInfo

# cada cabeca usa matrizes diferentes para observar relacoes diferentes
HEAD_CONFIGS = (
    {
        "name": "Cabeça 1",
        "focus": "Relações locais/sintáticas (interpretação didática)",
        "WQ": ((0.60, 0.10), (0.20, 0.70), (0.50, -0.30), (0.10, 0.40)),
        "WK": ((0.50, 0.20), (0.10, 0.80), (0.60, -0.20), (0.20, 0.30)),
        "WV": ((0.70, 0.10), (0.10, 0.60), (0.40, 0.20), (0.20, 0.50)),
    },
    {
        "name": "Cabeça 2",
        "focus": "Relações globais/contextuais (interpretação didática)",
        "WQ": ((0.20, 0.70), (0.60, -0.10), (0.10, 0.50), (0.50, 0.20)),
        "WK": ((0.30, 0.60), (0.70, 0.10), (-0.20, 0.40), (0.40, 0.30)),
        "WV": ((0.20, 0.50), (0.60, 0.20), (0.10, 0.70), (0.50, -0.10)),
    },
)


def softmax(values: np.ndarray, axis: int = -1) -> np.ndarray:
    """Softmax numericamente estável"""

    # tirar o maior valor evita numeros grandes demais na exponencial
    shifted = values - np.max(values, axis=axis, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / np.sum(exponentials, axis=axis, keepdims=True)


def _as_matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def calculate_attention(
    positioned_vectors: tuple[VectorInfo, ...],
) -> tuple[tuple[AttentionHeadResult, ...], tuple[tuple[float, ...], ...]]:
    """Calcula Q, K, V e Attention(Q,K,V) para duas cabeças"""

    if not positioned_vectors:
        raise ValueError("A atenção requer pelo menos um token.")

    # transforma os vetores em uma matriz para fazer as contas com NumPy
    inputs = np.asarray([vector.values for vector in positioned_vectors], dtype=float)
    heads: list[AttentionHeadResult] = []
    outputs: list[np.ndarray] = []

    for config in HEAD_CONFIGS:
        # cria as matrizes Q K e V usando as configuracoes da cabeca atual
        wq = np.asarray(config["WQ"], dtype=float)
        wk = np.asarray(config["WK"], dtype=float)
        wv = np.asarray(config["WV"], dtype=float)
        queries = inputs @ wq
        keys = inputs @ wk
        values = inputs @ wv
        # compara cada Query com todas as Keys e aplica a escala da formula
        scores = (queries @ keys.T) / math.sqrt(keys.shape[1])
        # o softmax converte os valores em pesos que somam um
        weights = softmax(scores, axis=1)
        # os pesos dizem quanto de cada Value vai entrar na saida
        output = weights @ values
        outputs.append(output)
        heads.append(
            AttentionHeadResult(
                name=str(config["name"]),
                didactic_focus=str(config["focus"]),
                queries=_as_matrix_tuple(queries),
                keys=_as_matrix_tuple(keys),
                values=_as_matrix_tuple(values),
                scores=_as_matrix_tuple(scores),
                weights=_as_matrix_tuple(weights),
                output=_as_matrix_tuple(output),
                matrices={
                    "WQ": _as_matrix_tuple(wq),
                    "WK": _as_matrix_tuple(wk),
                    "WV": _as_matrix_tuple(wv),
                },
            )
        )

    # junta lado a lado as respostas produzidas pelas duas cabecas
    combined = np.concatenate(outputs, axis=1)
    return tuple(heads), _as_matrix_tuple(combined)


def mean_attention_weights(
    heads: tuple[AttentionHeadResult, ...],
) -> tuple[tuple[float, ...], ...]:
    """Calcula uma visão agregada das cabeças para o resumo final"""

    # faz uma media simples para mostrar um resumo das duas cabecas
    matrices = np.asarray([head.weights for head in heads], dtype=float)
    return _as_matrix_tuple(np.mean(matrices, axis=0))

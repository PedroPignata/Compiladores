"""Orquestra todas as etapas obrigatorias da simulação"""

from __future__ import annotations

import numpy as np

from .attention import calculate_attention
from .embeddings import add_position, generate_embeddings, generate_positional_encodings
from .generation import generate_response
from .layers import run_layers
from .models import SimulationResult, TokenInfo
from .normalization import EmptyInputError, normalize_text
from .tokenization import tokenize
from .vocabulary import assign_token_ids


# lista o que usa operacoes parecidas com as de um Transformer real
REAL_PARTS = (
    "Normalização Unicode e de espaços.",
    "Tokenização por expressão regular.",
    "Conversão dos tokens em IDs de vocabulário.",
    "Codificação posicional senoidal.",
    "Multiplicações matriciais para Query, Key e Value.",
    "Atenção escalada por produto escalar e softmax.",
    "Reprocessamento do contexto a cada token gerado.",
    "Seleção determinística do candidato de maior probabilidade (argmax).",
)

# lista o que foi simplificado ou criado apenas para esta atividade
SIMULATED_PARTS = (
    "Vocabulário pequeno criado para a atividade.",
    "Embeddings didáticos derivados dos IDs, sem treinamento.",
    "Matrizes WQ, WK e WV fixas e não aprendidas.",
    "Interpretação sintática/semântica dos nomes das cabeças.",
    "Três camadas simplificadas, sem rede neural treinada.",
    "Candidatos e probabilidades construídos para demonstração.",
    "Respostas provenientes de uma base de conhecimento cadastrada.",
)

class TransformerSimulator:
    """Fachada principal consumida pela interface e pelos testes"""

    def _encode_token_texts(
        self, token_texts: tuple[str, ...]
    ) -> tuple[
        tuple[TokenInfo, ...],
        tuple,
        tuple,
        tuple,
        tuple,
        tuple,
    ]:
        # este e o caminho principal dos tokens ate o fim das camadas
        tokens = assign_token_ids(list(token_texts))
        embeddings = generate_embeddings(tokens)
        positions = generate_positional_encodings(tokens)
        positioned = add_position(embeddings, positions)
        heads, combined = calculate_attention(positioned)
        layers = run_layers(combined)
        return tokens, embeddings, positions, positioned, heads, layers

    def _context_summary(self, token_texts: tuple[str, ...]) -> tuple[float, ...]:
        # resume a ultima camada em um vetor medio com quatro valores
        *_, layers = self._encode_token_texts(token_texts)
        last_layer = np.asarray(layers[-1].output_vectors, dtype=float)
        return tuple(float(value) for value in np.mean(last_layer, axis=0))

    def simulate(self, text: str) -> SimulationResult:
        # as primeiras etapas limpam o texto e separam os tokens
        normalization = normalize_text(text)
        token_texts = tuple(tokenize(normalization.normalized))
        if not token_texts:
            raise EmptyInputError("A entrada não produziu tokens válidos.")

        # executa embeddings posicao atencao e as tres camadas
        tokens, embeddings, positions, positioned, heads, layers = self._encode_token_texts(
            token_texts
        )
        combined_attention = tuple(
            tuple(value for value in row)
            for row in np.concatenate(
                [np.asarray(head.output, dtype=float) for head in heads], axis=1
            )
        )
        # gera a resposta aos poucos usando o contexto atualizado
        generation_steps, generated, answer, completion_reason = generate_response(
            token_texts,
            normalization.normalized,
            self._context_summary,
        )

        # devolve tudo em um unico objeto que a interface consegue mostrar
        return SimulationResult(
            normalization=normalization,
            input_tokens=tokens,
            embeddings=embeddings,
            positional_encodings=positions,
            positioned_vectors=positioned,
            attention_heads=heads,
            combined_attention=combined_attention,
            layers=layers,
            generation_steps=generation_steps,
            generated_tokens=generated,
            final_answer=answer,
            processing_cycles=1 + len(generation_steps),
            selection_strategy="Argmax: sempre selecionar o token de maior probabilidade.",
            completion_reason=completion_reason,
            real_parts=REAL_PARTS,
            simulated_parts=SIMULATED_PARTS,
        )


__all__ = ["EmptyInputError", "TransformerSimulator"]

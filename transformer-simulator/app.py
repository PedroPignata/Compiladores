"""Interface Streamlit do Simulador Educacional de uma Arquitetura Transformer."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transformer_simulator import EmptyInputError, TransformerSimulator  # noqa: E402
from transformer_simulator.attention import mean_attention_weights  # noqa: E402


st.set_page_config(
    page_title="Transformer por Dentro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_styles() -> None:
    style_path = PROJECT_ROOT / "src" / "transformer_simulator" / "styles.css"
    st.markdown(f"<style>{style_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def rounded(values: tuple[float, ...], digits: int = 4) -> list[float]:
    return [round(float(value), digits) for value in values]


def vector_rows(vectors: tuple) -> list[dict[str, object]]:
    return [
        {
            "Token": vector.token,
            "Posição": vector.position,
            **{f"d{i + 1}": round(float(value), 4) for i, value in enumerate(vector.values)},
        }
        for vector in vectors
    ]


def matrix_rows(tokens: list[str], matrix: tuple[tuple[float, ...], ...]) -> list[dict[str, object]]:
    return [
        {
            "Token": token,
            **{f"d{i + 1}": round(float(value), 4) for i, value in enumerate(row)},
        }
        for token, row in zip(tokens, matrix, strict=True)
    ]


def token_pills(tokens: tuple) -> None:
    pills = "".join(
        (
            f'<span class="token-pill {"" if token.known else "unknown-token"}">'
            f'<span>{html.escape(token.text)}</span><small>#{token.position} · ID {token.token_id}</small>'
            "</span>"
        )
        for token in tokens
    )
    st.markdown(f'<div class="token-row">{pills}</div>', unsafe_allow_html=True)


def attention_heatmap(tokens: list[str], weights: tuple[tuple[float, ...], ...], title: str) -> None:
    figure = go.Figure(
        data=go.Heatmap(
            z=weights,
            x=tokens,
            y=tokens,
            colorscale=[[0, "#eef2ff"], [0.5, "#818cf8"], [1, "#312e81"]],
            zmin=0,
            zmax=max(max(row) for row in weights),
            text=[[f"{value:.3f}" for value in row] for row in weights],
            texttemplate="%{text}",
            hovertemplate="Origem: %{y}<br>Destino: %{x}<br>Peso: %{z:.4f}<extra></extra>",
            colorbar={"title": "Peso"},
        )
    )
    figure.update_layout(
        title=title,
        xaxis_title="Token que recebe atenção (Key)",
        yaxis_title="Token analisado (Query)",
        height=480,
        margin={"l": 40, "r": 20, "t": 70, "b": 40},
    )
    st.plotly_chart(figure, width="stretch")


def probability_chart(step) -> None:
    tokens = [candidate.token for candidate in step.candidates]
    probabilities = [candidate.probability * 100 for candidate in step.candidates]
    colors = ["#4f46e5"] + ["#c7d2fe"] * (len(tokens) - 1)
    figure = go.Figure(go.Bar(x=probabilities, y=tokens, orientation="h", marker_color=colors))
    figure.update_layout(
        xaxis_title="Probabilidade (%)",
        yaxis_title="Possível próximo token",
        height=320,
        margin={"l": 20, "r": 20, "t": 20, "b": 40},
        xaxis={"range": [0, 100]},
    )
    st.plotly_chart(figure, width="stretch")


def stage_heading(number: int, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="stage-heading">
            <span>ETAPA {number}</span>
            <div><h3>{html.escape(title)}</h3><p>{html.escape(subtitle)}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


load_styles()
simulator = TransformerSimulator()

with st.sidebar:
    st.markdown("## 🧠 Transformer por Dentro")
    st.caption("Simulador educacional · Disciplina de Compiladores")
    st.info(
        "Esta é uma simulação educacional simplificada. Os valores não representam "
        "os parâmetros internos de uma LLM comercial."
    )
    st.markdown("### Fluxo")
    st.markdown(
        "Entrada → normalização → tokens → IDs → embeddings → posição → QKV → "
        "atenção → cabeças → camadas → probabilidades → geração → resultado"
    )
    st.markdown("### Experimente")
    st.code("Qual é a capital do Brasil?", language=None)
    st.code("O que é um compilador?", language=None)
    st.code("Quanto é 2 + 2?", language=None)

st.markdown('<p class="eyebrow">SIMULAÇÃO INTERATIVA</p>', unsafe_allow_html=True)
st.title("Veja uma arquitetura Transformer por dentro")
st.write(
    "Digite uma frase ou pergunta e acompanhe como representações numéricas, "
    "atenção e camadas didáticas constroem uma resposta token por token."
)

if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None
if "generation_index" not in st.session_state:
    st.session_state.generation_index = 1

with st.container(border=True):
    user_input = st.text_area(
        "Frase ou pergunta",
        value="Qual é a capital do Brasil?",
        height=100,
        placeholder="Ex.: Qual é a capital do Brasil?",
        key="user_input",
    )
    process_column, reset_column, spacer = st.columns([1, 1, 4])
    with process_column:
        process_clicked = st.button("▶ Processar", type="primary", width="stretch")
    with reset_column:
        reset_clicked = st.button("↻ Reiniciar", width="stretch")

if reset_clicked:
    st.session_state.simulation_result = None
    st.session_state.generation_index = 1
    st.rerun()

if process_clicked:
    try:
        with st.spinner("Executando as etapas do Transformer didático..."):
            st.session_state.simulation_result = simulator.simulate(user_input)
            st.session_state.generation_index = 1
    except EmptyInputError as error:
        st.session_state.simulation_result = None
        st.error(str(error))

result = st.session_state.simulation_result
if result is None:
    st.markdown(
        '<div class="empty-state"><strong>Pronto para começar</strong>'
        '<span>Preencha o campo e clique em Processar.</span></div>',
        unsafe_allow_html=True,
    )
    st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric("Tokens de entrada", len(result.input_tokens))
metric_columns[1].metric("Cabeças de atenção", len(result.attention_heads))
metric_columns[2].metric("Camadas", len(result.layers))
metric_columns[3].metric("Ciclos de processamento", result.processing_cycles)

tabs = st.tabs(
    [
        "1–2 · Entrada",
        "3–4 · Tokens e IDs",
        "5–6 · Vetores",
        "7–8 · QKV e atenção",
        "9–10 · Cabeças e camadas",
        "11–12 · Geração",
        "13 · Resultado",
    ]
)

with tabs[0]:
    stage_heading(1, "Recebimento da frase", "A aplicação preserva a entrada original.")
    st.code(result.normalization.original, language=None)
    stage_heading(2, "Normalização", "Regras conservadoras preparam o texto sem apagar sua intenção.")
    before, after = st.columns(2)
    before.text_area("Entrada original", result.normalization.original, disabled=True)
    after.text_area("Entrada normalizada", result.normalization.normalized, disabled=True)
    st.markdown("**Regras utilizadas**")
    for rule in result.normalization.rules:
        st.write(f"✓ {rule}")
    st.caption("Alterações: " + " ".join(result.normalization.changes))

with tabs[1]:
    stage_heading(3, "Tokenização", "Um token pode ser uma palavra, número, pontuação ou parte textual.")
    token_pills(result.input_tokens)
    st.success(f"A entrada contém {len(result.input_tokens)} tokens.")
    stage_heading(4, "IDs dos tokens", "O modelo opera sobre números, não diretamente sobre palavras.")
    st.dataframe(
        [
            {
                "Posição": token.position,
                "Token": token.text,
                "ID": token.token_id,
                "Conhecido": "Sim" if token.known else "Não — <UNK>",
                "Categoria": token.category,
            }
            for token in result.input_tokens
        ],
        width="stretch",
        hide_index=True,
    )
    if any(not token.known for token in result.input_tokens):
        st.warning("Tokens desconhecidos recebem o ID 1 (<UNK>), sem inventar significado para eles.")

with tabs[2]:
    stage_heading(5, "Embeddings", "Cada ID é convertido em um vetor determinístico de quatro dimensões.")
    st.warning("Embedding didático simulado — estes vetores não foram aprendidos por uma LLM.")
    st.dataframe(vector_rows(result.embeddings), width="stretch", hide_index=True)
    with st.expander("Como os embeddings são calculados?"):
        st.latex(r"E(id)=[\sin(0.13id),\cos(0.07id),\sin(0.017id+0.5),\cos(0.031id-0.25)]")
        st.write("A fórmula é fixa, reproduzível e não usa números aleatórios.")
    stage_heading(6, "Informação de posição", "A ordem entra no vetor antes do cálculo da atenção.")
    position_tab, combined_tab = st.tabs(["Codificação senoidal", "Embedding + posição"])
    with position_tab:
        st.dataframe(vector_rows(result.positional_encodings), width="stretch", hide_index=True)
    with combined_tab:
        st.dataframe(vector_rows(result.positioned_vectors), width="stretch", hide_index=True)
    st.info(
        "Como cada posição recebe um vetor diferente, ‘O cachorro mordeu o homem’ e "
        "‘O homem mordeu o cachorro’ produzem representações posicionadas diferentes."
    )

with tabs[3]:
    selected_head_name = st.selectbox(
        "Cabeça analisada",
        [head.name for head in result.attention_heads],
        key="qkv_head",
    )
    selected_head = next(head for head in result.attention_heads if head.name == selected_head_name)
    tokens = [token.text for token in result.input_tokens]
    stage_heading(7, "Query, Key e Value", "Três projeções diferentes são calculadas para cada token.")
    q_tab, k_tab, v_tab = st.tabs(["Query — o que procura", "Key — o que oferece", "Value — conteúdo"])
    with q_tab:
        st.dataframe(matrix_rows(tokens, selected_head.queries), width="stretch", hide_index=True)
    with k_tab:
        st.dataframe(matrix_rows(tokens, selected_head.keys), width="stretch", hide_index=True)
    with v_tab:
        st.dataframe(matrix_rows(tokens, selected_head.values), width="stretch", hide_index=True)
    with st.expander("Matrizes fixas usadas nesta cabeça"):
        for name, matrix in selected_head.matrices.items():
            st.markdown(f"**{name}**")
            st.dataframe(matrix, width="stretch")
        st.latex(r"Q=XW_Q\qquad K=XW_K\qquad V=XW_V")
    stage_heading(8, "Pesos de atenção", "Softmax transforma relevâncias em distribuições que somam 1.")
    st.latex(r"Attention(Q,K,V)=softmax\left(\frac{QK^T}{\sqrt{d_k}}\right)V")
    attention_heatmap(tokens, selected_head.weights, f"Mapa de atenção — {selected_head.name}")
    sums = [sum(row) for row in selected_head.weights]
    st.caption("Somas das linhas: " + ", ".join(f"{value:.6f}" for value in sums))

with tabs[4]:
    stage_heading(9, "Múltiplas cabeças", "Duas projeções observam relações diferentes e são concatenadas.")
    for head in result.attention_heads:
        with st.container(border=True):
            st.markdown(f"#### {head.name}")
            st.write(head.didactic_focus)
            row = head.weights[0]
            strongest_index = max(range(len(row)), key=row.__getitem__)
            st.caption(
                f"Para ‘{result.input_tokens[0].text}’, maior peso em "
                f"‘{result.input_tokens[strongest_index].text}’: {row[strongest_index]:.3f}."
            )
    st.warning("Os focos das cabeças são rótulos didáticos; em modelos reais eles não são funções fixas.")
    stage_heading(10, "Múltiplas camadas", "Cada camada transforma obrigatoriamente a saída da anterior.")
    for layer in result.layers:
        with st.expander(f"{layer.name} · mudança média {layer.mean_change:.4f}", expanded=True):
            st.write(layer.description)
            layer_before, layer_after = st.columns(2)
            layer_before.dataframe(
                matrix_rows(tokens, layer.input_vectors), width="stretch", hide_index=True
            )
            layer_after.dataframe(
                matrix_rows(tokens, layer.output_vectors), width="stretch", hide_index=True
            )

with tabs[5]:
    stage_heading(11, "Probabilidades", "Quatro candidatos são comparados em cada iteração.")
    stage_heading(12, "Geração progressiva", "O contexto atualizado é reprocessado antes do próximo token.")
    total_steps = len(result.generation_steps)
    control_previous, control_next, control_complete, progress_column = st.columns([1, 1, 1.5, 3])
    with control_previous:
        if st.button("← Anterior", width="stretch"):
            st.session_state.generation_index = max(1, st.session_state.generation_index - 1)
            st.rerun()
    with control_next:
        if st.button("Próximo →", width="stretch"):
            st.session_state.generation_index = min(total_steps, st.session_state.generation_index + 1)
            st.rerun()
    with control_complete:
        if st.button("Mostrar completa", width="stretch"):
            st.session_state.generation_index = total_steps
            st.rerun()

    current_index = min(st.session_state.generation_index, total_steps)
    with progress_column:
        st.progress(current_index / total_steps, text=f"Token {current_index} de {total_steps}")
    step = result.generation_steps[current_index - 1]
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Resposta até agora")
        st.markdown(f'<div class="generated-answer">{html.escape(step.progressive_text)}</div>', unsafe_allow_html=True)
        st.write(f"Token escolhido por argmax: **{step.selected_token}**")
        st.caption(
            f"O contexto com {step.context_token_count} tokens foi reprocessado nesta iteração. "
            f"Resumo contextual: {rounded(step.context_summary)}"
        )
    with right:
        probability_chart(step)
        st.caption(f"Soma das probabilidades: {sum(c.probability for c in step.candidates):.6f}")
    if current_index == total_steps:
        st.success("Condição de término encontrada: a resposta cadastrada foi concluída.")

with tabs[6]:
    stage_heading(13, "Resultado final", "Resumo completo da simulação e das suas limitações.")
    st.markdown(f'<div class="final-answer">{html.escape(result.final_answer)}</div>', unsafe_allow_html=True)
    summary_columns = st.columns(2)
    with summary_columns[0]:
        st.markdown("**Entrada e geração**")
        st.write(f"Pergunta original: `{result.normalization.original}`")
        st.write(f"Tokens de entrada: `{[token.text for token in result.input_tokens]}`")
        st.write(f"Quantidade de tokens: **{len(result.input_tokens)}**")
        st.write(f"Tokens gerados: `{list(result.generated_tokens)}`")
        st.write(f"Ciclos de processamento: **{result.processing_cycles}**")
        st.write(result.completion_reason)
    with summary_columns[1]:
        aggregated = mean_attention_weights(result.attention_heads)
        relations = []
        for origin_index, row in enumerate(aggregated):
            target_index = max(range(len(row)), key=row.__getitem__)
            relations.append(
                f"{result.input_tokens[origin_index].text} → "
                f"{result.input_tokens[target_index].text} ({row[target_index]:.3f})"
            )
        st.markdown("**Principais relações de atenção**")
        for relation in relations:
            st.write(f"• {relation}")
    real_column, simulated_column = st.columns(2)
    with real_column:
        st.markdown("### ✓ Operações reais")
        for item in result.real_parts:
            st.write(f"• {item}")
    with simulated_column:
        st.markdown("### ◇ Partes simuladas")
        for item in result.simulated_parts:
            st.write(f"• {item}")
    st.download_button(
        "Baixar resultado em JSON",
        data=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        file_name="resultado-transformer.json",
        mime="application/json",
    )

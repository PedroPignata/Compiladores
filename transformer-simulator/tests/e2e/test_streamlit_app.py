from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).resolve().parents[2] / "app.py"


def test_streamlit_processes_default_question_without_exception():
    app = AppTest.from_file(str(APP_FILE), default_timeout=15).run()

    app.button[0].click().run()

    assert not app.exception
    assert any(metric.value == "7" for metric in app.metric)
    labels = {tab.label for tab in app.tabs}
    assert {
        "1–2 · Entrada",
        "3–4 · Tokens e IDs",
        "5–6 · Vetores",
        "7–8 · QKV e atenção",
        "9–10 · Cabeças e camadas",
        "11–12 · Geração",
        "13 · Resultado",
    }.issubset(labels)


def test_streamlit_rejects_blank_input():
    app = AppTest.from_file(str(APP_FILE), default_timeout=15).run()

    app.text_area[0].set_value("   ")
    app.button[0].click().run()

    assert not app.exception
    assert app.error[0].value == "Digite uma frase ou pergunta antes de processar."

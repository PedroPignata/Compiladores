# Testes e segunda revisão - 12/11/2026

Linux, Python 3.12.3, pytest 8.4.2, ambiente /tmp/mfn/venv.
Comandos: python -m pip install -r requirements-dev.txt; python -m pytest -q;
python -m compileall -q miniforge tests; git diff --check.
Primeira execução completa: 696 passed em 10,97 s. Sem skips/xfails.

Cobertura: regressões léxicas/sintáticas/semânticas, TAC esperado por comando,
sombreamento e colisão t1, alvos e determinismo, passes isolados, não mutação,
origem e mudou, ponto fixo e idempotência, constantes em laços/junções, divisões
por zero e sinais, inteiros de 100 dígitos sem float, saída e falhas alcançáveis,
inalcançável e ausência de ganho, subprocessos CLI, import sem backend.
A CLI tem 128 combinações testadas além das 32 regressões anteriores.

A segunda revisão compara organização e checklists das páginas 5, 46 e 56 ao
pedido: nomes mineiros preservados, TAC completo, cinco passes e exceção
explícita da VM; nenhuma execução foi usada para validar transformações.
A equivalência geral e desempenho não foram comprovados. As evidências são
estruturais, parametrizadas e de regressão, sem executor disfarçado.
Apresentação revisada por renderização PDF; nenhum teste no PowerPoint.

Segunda execução completa: **696 passed em 10,64 s**, após revisão dos contratos e documentos.

# Verificação da entrega v0.3-semantica

Data real: 06/11/2026. Linux, Python 3.12.3, pytest 8.4.2.
Ambiente isolado em /tmp/mf-audit/venv, dependência instalada de requirements-dev.txt.

## Comandos executados

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m miniforge exemplos/fatorial.mini
python -m miniforge exemplos/semantico.mini --contexto
python -m miniforge exemplos/if_else.mini --tipos
git diff --check
```

## Resultado da segunda execução completa

```text
........................................................................ [ 19%]
........................................................................ [ 38%]
........................................................................ [ 57%]
........................................................................ [ 76%]
........................................................................ [ 95%]
.................                                                        [100%]
377 passed in 9.87s
```

A primeira execução após separar o ZIP revelou erro no teste convertido por
esta integração: tentativa de acessar `.expr` em um nó If. O teste foi
corrigido para inspecionar a condição, seu bloco e a saída final. Não era
um defeito da implementação do colega. A suíte foi então executada por
inteiro novamente, sem skips ou xfails. O primeiro resultado verde foi
377 passed em 8,83 s; a segunda execução verde registrou 9,87 s acima.

## Segunda revisão contra o material

Reavaliados os checklists das páginas 6, 11, 16, 21, 26, 29, 36 e 41:
reservadas e posições, recuperação léxica, FIRST/derivação e banco mínimo,
precedência e associatividade, pilha de símbolos e inicializador, tabela
de tipos, anotação de expressões, cascata e três erros independentes.
Os arquivos do frontend foram comparados ao ZIP e a implementação central
permanece a do grupo. A CLI foi revisada para não importar ou executar backend.

As 32 combinações de flags e os 40 pares operador/tipos estão parametrizados.
Testes de laço infinito e divisão por zero confirmam ausência de execução.
Leitura inexistente/UTF-8 inválido, códigos 0/1/2, stderr, avisos e recusa das
opções futuras estão cobertos. O banco tem 11 + 13 + 18 = 42 arquivos.

## Limites da evidência

Sem execução de programas, geração de código ou benchmark neste corte.
Não houve demonstração presencial à professora nem teste em Windows ou
PowerPoint. O tempo da suíte varia e não mede desempenho do compilador.
Entradas patológicas (profundidade extrema ou limite decimal do Python)
não fazem parte dos testes acadêmicos e permanecem limitações documentadas.

## Apresentação

PPTX com 12 slides, texto e duas tabelas editáveis, notas do apresentador e
roteiro separado. Validação estrutural do pacote e da geometria: nenhuma
ocorrência. Revisão visual das 12 páginas renderizadas do PDF concluída.
O PDF foi exportado pelo LibreOffice 24.2 a partir do PPTX validado, pois o
exportador PDF da biblioteca de autoria encontrou uma dependência de fonte
ausente. Nenhuma instalação ou alteração do runtime foi necessária.
Cores e disposição seguem a referência visual do grupo, com fontes DejaVu
Sans e DejaVu Sans Mono. Não houve teste no aplicativo Microsoft PowerPoint.

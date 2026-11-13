# Validação vigente do MiniForge

Revisão de documentação de 13/11/2026. Código de referência: 7e1408a,
main com execução e sorteio. As alterações desta revisão são documentais;
a implementação e os casos de teste não foram modificados.

## Ambiente e resultados executados

Linux, Python 3.12.3, pytest 8.4.2. Ambiente isolado já instalado:
`/tmp/miniforge-relatorio-venv`. Nos comandos abaixo, python representa o Python
desse ambiente. Usuários devem instalar requirements-dev.txt no próprio ambiente.

| Comando, na pasta MiniForge/ | Resultado |
|---|---|
| `python -m pytest -q` | **817 passed in 15.48s**, sem skips ou xfails |
| Oito comandos da demonstração | Códigos e saídas capturados em demonstracao.md |
| Geração e otimização de todos os exemplos válidos | Contagens recalculadas em otimizacao.md |

A contagem de testes é da versão vigente. Execuções anteriores com 696, 715,
740, 754, 766 e 792 casos são registros históricos, não resultados desta rodada.

## Cobertura e forma de conferir

- Frontend: posições, EOF, recuperação, precedência, comandos, escopos, tipos,
  AST anotada, erros independentes e supressão de cascata.
- TAC: expressões, comandos, rótulos, alvos, nomes internos, sombreamento,
  colisões com temporários, determinismo e origem.
- Passes: transformações isoladas, limites de fluxo, efeitos, divisões por zero,
  negativos e inteiros grandes, não mutação, indicador mudou e ponto fixo.
- CLI: inspeções, geração, execução, combinações válidas/inválidas, retorno,
  leitura de arquivo e bloqueio das fases após erros.
- Calculadora: quatro operações, erros, múltiplas contas e fração truncada para zero.
- Jogo: dicas, contagem, limites, saída, EOF, configuração e sorteio por partida.
- Sorteio: aridade, tipos, ordem, extremos inclusivos, efeitos, chamadas repetidas,
  execução real e preservação com otimização.

Testes que precisam de respostas exatas controlam o gerador, sem criar um
executor substituto. O uso normal continua SystemRandom sem semente fixa.
Há casos com gerador real; não exigem resultados diferentes para passar.

## Reproduzir

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py tests/test_adivinha.py tests/test_sorteio.py
python -m compileall -q miniforge tests
```

As aplicações usam configurações padrão; edições locais de frases ou regras
podem exigir atualização deliberada de expectativas. Não elimine asserções
para esconder falhas. A nova instalação não deve usar o caminho /tmp do revisor;
essa localização só identifica o ambiente em que a validação foi feita.

## Alcance e limitações

Comparações originais/otimizadas reforçam os casos cobertos, mas não provam
equivalência geral. As métricas são estáticas e não medem instruções executadas
ou velocidade. Não houve validação em Windows, PowerPoint ou das apresentações
locais nesta revisão. Resultados dos outros projetos são independentes.

O registro da revisão documental do repositório está em revisao-documental.md.
Execuções anteriores estão identificadas no [índice](README.md) e no
[histórico](historico/README.md), incluindo o marco antigo sem executor.

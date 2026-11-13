# Projeto Final — MiniForge

Pasta de entrega da documentação solicitada: **PDF do projeto, arquitetura e
prints de execução**. O material descreve o MiniForge atual, com compilação,
otimização, execução de TAC e os dois programas em mineirês.

## Arquivo para anexar à atividade

**[MiniForge-Projeto-Final.pdf](MiniForge-Projeto-Final.pdf)** — 18 páginas.

O PDF reúne:

- Identificação do grupo e link do repositório.
- Objetivos, linguagem e vocabulário.
- Lexer, parser, AST, símbolos, semântica, TAC, otimização e execução.
- Arquitetura com diagrama, estrutura de pastas e responsabilidades dos módulos.
- Calculadora e jogo com segredo aleatório.
- Testes, resultados estáticos, limites e instruções para instalar e demonstrar.
- Seis prints de transcrições reais das execuções.

Repositório para informar na atividade:
https://github.com/PedroPignata/Compiladores/tree/main/MiniForge

O PDF está pronto para ser anexado pelo grupo. Nenhum envio ao ambiente da
disciplina foi feito por esta automação.

## Conteúdo da pasta

| Caminho | Conteúdo |
|---|---|
| [MiniForge-Projeto-Final.pdf](MiniForge-Projeto-Final.pdf) | Documento final com arquitetura e prints incorporados |
| [documentacao.md](documentacao.md) | Texto-base editável da documentação e das evidências |
| [arquitetura.md](arquitetura.md) | Arquitetura em Markdown, com acesso ao diagrama |
| [arquitetura.svg](arquitetura.svg) | Diagrama vetorial das fases |
| [prints/](prints/) | Seis capturas PNG em resolução original |
| [registros/](registros/README.md) | Saídas completas e origem dos registros |
| [SHA256SUMS](SHA256SUMS) | Verificação de integridade dos arquivos |

## Evidências incluídas

| Print | O que demonstra |
|---|---|
| [01-calculadora.png](prints/01-calculadora.png) | Soma 18 + 6, resultado 24, retorno ao menu e saída |
| [02-calculadora-fracao.png](prints/02-calculadora-fracao.png) | 2 / 5 recusado pela regra da aplicação, com -O |
| [03-jogo.png](prints/03-jogo.png) | Partida real com segredo aleatório, dicas e acerto |
| [04-tac.png](prints/04-tac.png) | TAC original e otimizado do exemplo de constantes |
| [05-diagnosticos.png](prints/05-diagnosticos.png) | Três erros independentes e posições de origem |
| [06-testes.png](prints/06-testes.png) | Nova execução completa: 817 passed in 12.42s |

As sessões da calculadora e do jogo foram capturadas de processos em
pseudoterminal com entradas ecoadas. As transcrições reais foram renderizadas
em um visualizador local e capturadas no Firefox para legibilidade. O print do
jogo sinaliza um recorte intermediário; o TXT completo acompanha a entrega.
Não são imagens inventadas de resultados nem capturas do desktop do usuário.

## Referência e atualização

Captura em 13/11/2026. Base do código e das capturas:
`71c0eaea7e485f4c0f691b9f851bead7beda30a4`.
O [manifesto](registros/manifesto.json) registra comandos, entradas e retornos.
Nesta partida o segredo foi 15, descoberto por palpites crescentes; esse número
não é fixado no programa e não deve ser esperado em outra execução.

Esta pasta é um retrato da versão e das sessões indicadas. Para uma futura
alteração de código, refaça os registros e o PDF; não substitua métricas
manualmente por números de outra versão. A documentação canônica e vigente
continua em [docs/](../docs/README.md).

A apresentação em slides continua local, fora do Git. Este PDF é a documentação
de entrega solicitada, e não uma apresentação PPTX.

## Executar novamente

Na pasta MiniForge/, com Python 3.10+:

```bash
python3 -m miniforge exemplos/calculadora/interativa.mini --executar
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar -O
python3 -m miniforge exemplos/constantes.mini --tac -O
```

Para testes, instale requirements-dev.txt em um ambiente virtual e use
`python -m pytest -q`. No Windows ou com ambiente ativo, use python no lugar
de python3. Guias completos em [exemplos/README.md](../exemplos/README.md).

No Linux, para conferir os arquivos desta pasta:

```bash
cd projeto-final
sha256sum -c SHA256SUMS
```

O código do compilador não foi alterado para produzir esta pasta. Os binários,
HTMLs temporários e páginas PNG de revisão do PDF não são versionados aqui.

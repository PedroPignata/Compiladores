# Análise integral do enunciado

Fonte analisada: `Desafio_Simulador_Arquitetura_Transformer.pdf`, com 14
páginas. A página 3 está visualmente em branco. O fluxograma obrigatório começa
na página 4 e continua na página 5.

## Objetivo e limite do projeto

O produto deve ser uma aplicação educacional chamada **Simulador de
Processamento de uma LLM**. O usuário informa uma frase ou pergunta e acompanha
como ela percorre uma representação simplificada da arquitetura Transformer até
a formação da resposta.

O trabalho não exige treinar uma LLM. A versão mínima pode usar vocabulário,
embeddings, matrizes, atenção, respostas e probabilidades didáticas, desde que
isso seja informado com clareza. Apenas enviar uma pergunta a uma API e exibir a
resposta não satisfaz o enunciado.

## Fluxo funcional obrigatório

1. Receber a frase original.
2. Normalizar espaços e tratar caixa, pontuação e caracteres especiais segundo
   regras declaradas.
3. Tokenizar, destacar cada token, contar os tokens e explicar que token não é
   necessariamente uma palavra.
4. Associar um ID inteiro a cada token.
5. Gerar embeddings pequenos, entre três e oito dimensões; valores artificiais
   devem ser identificados como **Embedding didático simulado**.
6. Somar ou combinar uma representação de posição e demonstrar que a ordem
   altera o significado.
7. Calcular e mostrar Query, Key e Value a partir do vetor de entrada e das
   matrizes `WQ`, `WK` e `WV`, inclusive exibindo os valores usados.
8. Calcular a atenção por `softmax(QK^T / sqrt(dk))V`, indicar as relações mais
   fortes e garantir que os pesos de cada distribuição somem aproximadamente 1.
9. Executar pelo menos duas cabeças de atenção. Rótulos como "sintática" e
   "semântica" devem ser apresentados como interpretações didáticas, não como
   funções fixas de cabeças reais.
10. Encadear pelo menos três camadas: relações locais, relações contextuais e
    preparação da resposta. Cada camada deve transformar a saída anterior e
    deixar a mudança visível.
11. Mostrar candidatos ao próximo token e suas probabilidades, informando a
    estratégia de seleção. O mínimo aceita `argmax`, isto é, maior
    probabilidade.
12. Gerar a resposta progressivamente. A cada token, atualizar o contexto,
    recalcular probabilidades, selecionar o próximo token e repetir até uma
    condição de término.
13. Exibir um resumo final com pergunta, tokens de entrada, quantidade de
    tokens, relações de atenção, tokens gerados, número de etapas, resposta e a
    distinção entre partes reais e simuladas.

## Interface mínima

A aplicação precisa oferecer campo de entrada, botão **Processar**, botão
**Limpar** ou **Reiniciar**, acompanhamento das etapas e área da resposta final.
Os painéis devem contemplar tokens, IDs, embeddings, QKV, atenção, cabeças,
camadas, probabilidades e geração progressiva sem desorientar o usuário.

## Casos de teste obrigatórios

| # | Situação | Risco principal a validar |
|---:|---|---|
| 1 | Pergunta curta | pipeline mínimo completo |
| 2 | Frase afirmativa | entrada sem intenção interrogativa |
| 3 | Frase com pontuação | pontuação preservada como token |
| 4 | Palavra desconhecida | uso explícito de token desconhecido |
| 5 | Palavras repetidas | IDs iguais e posições diferentes |
| 6 | Mesmas palavras em ordens diferentes | efeito da codificação posicional |
| 7 | Pergunta respondível | geração completa cadastrada |
| 8 | Pergunta não respondível | resposta de fallback honesta |
| 9 | Texto vazio | validação sem iniciar o pipeline |
| 10 | Caracteres especiais | tratamento previsível e sem falha |

Para cada caso será necessário registrar entrada, tokens, comportamento
esperado, comportamento obtido, resposta e situação aprovada ou reprovada.

## Entregáveis

- Código-fonte completo.
- Aplicação publicada, executável ou acompanhada de instruções.
- `README.md` completo.
- Diagrama da arquitetura.
- Relatório de todas as etapas.
- Tabela de testes.
- Capturas de tela.
- Vídeo curto da demonstração.
- Arquivo com os principais prompts usados no desenvolvimento.

O README final também deve explicar instalação, tokenização, embeddings, QKV,
atenção, camadas, seleção do próximo token, partes reais, partes simuladas e
limitações.

## Distribuição da nota

| Critério | Pontos |
|---|---:|
| Entrada, normalização e tokenização | 1,0 |
| IDs e embeddings | 1,0 |
| Query, Key e Value | 1,5 |
| Cálculo e visualização da atenção | 1,5 |
| Múltiplas cabeças e camadas | 1,0 |
| Probabilidades do próximo token | 1,0 |
| Geração progressiva da resposta | 1,0 |
| Interface e experiência educacional | 0,5 |
| Documentação e diagrama | 1,0 |
| Testes e apresentação | 0,5 |
| **Total** | **10,0** |

QKV e atenção concentram 3,0 pontos; por isso terão cálculo verificável, dados
intermediários visíveis e testes numéricos, em vez de animações meramente
decorativas.

## Regras de uso de IA

Os principais prompts devem ser registrados. Todo código gerado precisa ser
revisado e compreendido pela equipe. A solução deve identificar conteúdo
simulado, não atribuir números aleatórios a significados reais, não alegar
acesso aos pesos internos de APIs, não versionar chaves e documentar bibliotecas
e modelos.

## Decisões para a versão mínima

- Implementar o **Nível 1**, com matemática pequena, determinística e
  inspecionável.
- Usar embeddings derivados de uma regra estável e marcados como didáticos.
- Usar matrizes fixas documentadas para QKV e duas cabeças distintas.
- Usar `argmax` como estratégia inicial de seleção.
- Manter um pequeno conjunto de respostas cadastradas e um fallback explícito.
- Não depender de API externa nem sugerir que a simulação revela uma LLM real.

## Critérios de aceite derivados

A primeira versão somente estará pronta quando as 13 etapas forem navegáveis,
as distribuições de atenção e de probabilidade estiverem numericamente válidas,
as três camadas consumirem a saída anterior, a resposta aparecer token a token,
os dez testes estiverem registrados e todos os nove entregáveis existirem.

Os desafios adicionais, como temperatura, Top-K, Top-P, comparação de
tokenizadores, histórico e exportação, ficam fora do escopo inicial e só serão
considerados após os requisitos pontuados.

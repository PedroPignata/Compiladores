# Roteiro de apresentação

## Abertura - 30 segundos

“Nosso projeto é uma simulação educacional de uma arquitetura Transformer. Ele
não treina uma LLM e não acessa pesos de modelos comerciais. O objetivo é tornar
visíveis as principais transformações matemáticas.”

## Arquitetura - 45 segundos

“A interface foi feita em Streamlit. O núcleo Python é separado da interface e
usa NumPy. Cada módulo recebe a saída do anterior: normalização, tokenização,
IDs, embeddings, posição, atenção, camadas e geração. Essa separação permite
testar a matemática sem abrir a interface.”

## Demonstração - 4 minutos

1. Digite `Qual é a capital do Brasil?` e clique em **Processar**.
2. Mostre original e normalizada; explique que caixa e pontuação são preservadas.
3. Mostre os sete tokens e os IDs.
4. Destaque o aviso “Embedding didático simulado”.
5. Compare embedding, posição e vetor somado.
6. Abra Query, Key e Value e mostre as matrizes fixas.
7. Mostre a fórmula e a soma `1,000000` das linhas da atenção.
8. Troque entre as duas cabeças e ressalte que os nomes são didáticos.
9. Mostre que as três camadas recebem a saída anterior.
10. Na geração, avance token a token e mostre candidatos e probabilidades.
11. Abra o resultado final e leia as partes reais e simuladas.

## Testes - 45 segundos

“Foram executados 31 testes automatizados. A tabela exigida contém dez situações:
pergunta curta, afirmação, pontuação, desconhecida, repetição, ordem diferente,
resposta conhecida, resposta desconhecida, vazio e caracteres especiais. Todos
os dez casos foram aprovados.”

## Encerramento - 30 segundos

“A principal limitação é que o vocabulário, os embeddings e as respostas são
didáticos. Mesmo assim, multiplicação matricial, codificação posicional,
softmax, atenção, encadeamento e argmax são operações realmente executadas.”

## Perguntas que podem aparecer

**Por que Python?** Facilita matrizes, testes e interface visual sem esconder a
lógica.

**Isso é uma LLM?** Não. É uma simulação do fluxo arquitetural.

**As probabilidades são reais?** A soma e a seleção são reais; os valores são
didáticos, pois não existe treinamento.

**Por que as cabeças têm nomes?** Apenas para facilitar a explicação. Cabeças
reais não têm necessariamente funções fixas.

**Como a ordem influencia?** A codificação posicional muda o vetor do mesmo
token quando sua posição muda.

# Relatório técnico - Transformer por Dentro

## 1. Introdução

O projeto implementa uma simulação funcional, visual e educacional das etapas
centrais de uma arquitetura Transformer. O objetivo não é treinar uma LLM, mas
permitir que o usuário acompanhe a transformação de uma frase em números, a
contextualização por atenção e a geração de uma resposta progressiva.

A solução foi escrita em Python. O núcleo matemático é independente da
interface Streamlit, o que permite testar cada operação isoladamente.

## 2. Classificação da solução

A implementação corresponde ao **Nível 1 - Simulação didática** do enunciado.
Ela utiliza operações matemáticas verdadeiras sobre um vocabulário, embeddings,
matrizes, probabilidades e respostas didáticas. Não existe acesso a uma LLM
comercial nem a seus pesos internos.

## 3. Etapas implementadas

### 3.1 Recebimento da frase

A interface oferece campo de texto, botão **Processar**, botão **Reiniciar**,
painéis das etapas e área da resposta. A entrada original é mantida no resultado
para comparação e auditoria.

### 3.2 Normalização

O módulo `normalization.py` aplica NFKC, remove espaços duplicados e espaços nas
extremidades. Caixa, pontuação e caracteres especiais são preservados. As regras
e alterações executadas ficam visíveis.

Exemplo:

```text
Original:    "Qual   é a capital do Brasil?"
Normalizada: "Qual é a capital do Brasil?"
```

### 3.3 Tokenização

Uma expressão regular Unicode separa palavras, números e símbolos. A entrada do
exemplo produz:

```text
["Qual", "é", "a", "capital", "do", "Brasil", "?"]
```

Cada token recebe posição e categoria. A interface destaca os tokens e informa
a quantidade. O relatório da aplicação explica que token não é sinônimo de
palavra.

### 3.4 IDs dos tokens

`vocabulary.py` contém um vocabulário pequeno e versionado. A busca não
diferencia maiúsculas de minúsculas. Para o exemplo:

| Token | ID |
|---|---:|
| Qual | 101 |
| é | 87 |
| a | 12 |
| capital | 345 |
| do | 64 |
| Brasil | 728 |
| ? | 9 |

Tokens desconhecidos recebem o ID `1`, correspondente a `<UNK>`.

### 3.5 Embeddings

O embedding possui quatro dimensões e é derivado deterministicamente do ID:

```text
E(id) = [sin(0,13id), cos(0,07id), sin(0,017id+0,5), cos(0,031id-0,25)]
```

Essa regra facilita a inspeção e garante repetibilidade. Os vetores não foram
aprendidos e são sempre identificados como **Embedding didático simulado**.

### 3.6 Informação de posição

O módulo usa codificação senoidal. Para posição `pos`, dimensão `i` e dimensão
total `d=4`, são alternadas funções seno e cosseno com denominador baseado em
`10000^(2 floor(i/2)/d)`. O vetor posicional é somado ao embedding.

Consequentemente, duas ocorrências do mesmo token possuem o mesmo embedding,
mas vetores posicionados diferentes. Isso permite demonstrar o efeito da ordem.

### 3.7 Query, Key e Value

Cada cabeça contém três matrizes fixas `4 × 2`. Com a entrada posicionada `X`:

```text
Q = XWQ
K = XWK
V = XWV
```

As duas colunas de Q e K formam o espaço de consulta e comparação; V contém o
conteúdo que será combinado. Todas as matrizes e saídas ficam disponíveis na
interface.

### 3.8 Pesos de atenção

Os escores são calculados por produto escalar escalado:

```text
scores = QKᵀ / √dk
pesos = softmax(scores)
saída = pesos × V
```

O softmax subtrai o maior escore antes da exponenciação, evitando estouro
numérico. Os testes verificam pesos não negativos e soma `1` em cada linha. A
interface apresenta mapa de calor, valores e soma com seis casas decimais.

### 3.9 Múltiplas cabeças

Foram implementadas duas cabeças com matrizes distintas. A primeira recebe o
rótulo didático de relações locais/sintáticas; a segunda, relações
globais/contextuais. As saídas `n × 2` são concatenadas em uma matriz `n × 4`.

Esses rótulos não afirmam funções fixas de cabeças reais. Em um Transformer
treinado, os padrões surgem do aprendizado e podem não ter interpretação única.

### 3.10 Múltiplas camadas

São executadas três transformações sequenciais:

1. **Relações locais:** média ponderada do token e de seus vizinhos.
2. **Relações contextuais:** similaridade entre todos os tokens seguida de
   softmax e combinação global.
3. **Preparação da resposta:** projeção por uma matriz `4 × 4` e aplicação de
   `tanh`.

Cada `LayerResult` guarda vetores de entrada e saída e a mudança absoluta média.
Os testes confirmam que a entrada de uma camada é exatamente a saída anterior.

### 3.11 Probabilidades

A base didática define uma resposta-alvo. Para cada próximo token, quatro
candidatos recebem probabilidades normalizadas. O token correto começa com
probabilidade `0,82`, e a distribuição é recalculada em cada iteração.

A estratégia declarada é **argmax**, ou seja, escolha do maior valor. Não existe
amostragem aleatória, temperatura, Top-K ou Top-P na versão mínima.

### 3.12 Geração progressiva

Antes de prever cada token, o programa combina os tokens de entrada com os já
gerados e executa novamente IDs, embeddings, posição, atenção e camadas. O passo
registra o número de tokens do contexto, um resumo contextual, candidatos,
probabilidades e texto parcial.

Exemplo:

```text
A
A capital
A capital do
A capital do Brasil
A capital do Brasil é
A capital do Brasil é Brasília
A capital do Brasil é Brasília.
```

A condição de término ocorre quando todos os tokens da resposta cadastrada são
gerados ou quando o limite seguro de 64 novos tokens é atingido.

### 3.13 Resultado final

O último painel reúne pergunta original, tokens, quantidade, principais relações
de atenção, tokens gerados, ciclos, resposta, motivo do término e listas das
partes reais e simuladas. O resultado também pode ser exportado em JSON.

## 4. Respostas e fallback

A base cadastrada cobre capital do Brasil, definição de compilador e soma
`2 + 2`. Perguntas não cadastradas recebem uma resposta honesta de
desconhecimento. Frases afirmativas recebem confirmação genérica.

Esse mecanismo existe para demonstrar a geração; não é um modelo de linguagem.

## 5. Testes

Há 31 testes automatizados divididos em:

- unitários para normalização, tokenização, embeddings, posição, softmax,
  atenção e camadas;
- integração do pipeline e serialização JSON;
- ponta a ponta para os dez cenários obrigatórios.

Na execução registrada, os 31 testes passaram e a tabela obrigatória terminou
com 10/10 casos aprovados.

## 6. Operações reais

- Normalização Unicode e de espaços.
- Tokenização por expressão regular.
- Consulta de IDs.
- Codificação posicional senoidal.
- Multiplicações matriciais.
- Atenção escalada e softmax.
- Encadeamento das camadas.
- Reprocessamento do contexto.
- Seleção por argmax.

## 7. Conteúdo simulado

- Vocabulário reduzido.
- Embeddings derivados por uma fórmula artificial.
- Matrizes não treinadas.
- Rótulos das cabeças.
- Camadas simplificadas.
- Candidatos, probabilidades e respostas cadastradas.

## 8. Limitações e melhorias futuras

A solução não aprende e não generaliza como uma LLM. Entre as extensões
possíveis estão comparação de tokenizadores, temperatura, Top-K/Top-P, histórico,
exportação adicional e integração opcional com um modelo pequeno. Essas
extensões somente devem ser apresentadas após a compreensão da versão atual.

## 9. Conclusão

O simulador atende ao fluxo obrigatório com uma implementação pequena,
reproduzível e explicável. A distinção entre matemática real e parâmetros
simulados impede que a visualização seja interpretada como exposição de dados
internos de uma LLM comercial.

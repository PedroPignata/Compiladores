# Relatório - Analisador Léxico MiniC

## 1. Introdução

A análise léxica é normalmente a primeira etapa de um compilador. Sua função
é percorrer o código-fonte e agrupar caracteres em unidades chamadas tokens.
Cada token possui uma categoria e um lexema, que é o texto original encontrado.
No trecho `int idade = 18;`, por exemplo, `int` é uma palavra reservada,
`idade` é um identificador, `=` é um operador, `18` é um número inteiro e `;`
é um delimitador.

O objetivo deste trabalho foi implementar, em C, um analisador para a linguagem
fictícia MiniC. O programa recebe o nome de um arquivo pela linha de comando,
realiza sua leitura caractere por caractere e informa a linha, a coluna, a
categoria e o lexema de cada token. O analisador também detecta erros léxicos e
continua processando o restante do arquivo.

## 2. Estratégia e algoritmo

O arquivo é aberto com `fopen` e lido com `fgetc` até `EOF`. As variáveis de
linha e coluna começam em 1. Para caracteres comuns, a coluna é incrementada;
ao encontrar `\n`, a linha aumenta e a coluna volta para 1. Antes de iniciar um
token, a posição atual é armazenada como sua posição inicial.

O programa utiliza uma enumeração para as categorias, uma estrutura `Token`
para armazenar tipo, lexema e posição, e uma estrutura `Scanner` para manter o
arquivo, os contadores e a posição corrente. O reconhecimento foi separado em
funções para identificadores, números, literais, delimitadores, operadores e
comentários, deixando o fluxo principal responsável apenas por escolher a regra.

A decisão sobre o token segue esta ordem:

1. Espaços e comentários são consumidos sem gerar tokens;
2. Letras e `_` iniciam identificadores ou palavras reservadas;
3. Algarismos iniciam números inteiros ou reais;
4. Aspas simples iniciam literais de caractere;
5. Delimitadores e operadores são reconhecidos pelas listas da linguagem;
6. Qualquer outro caractere gera erro léxico.

Identificadores são consumidos enquanto houver letras, algarismos ou `_`. Depois
da leitura, o lexema é comparado com as oito palavras reservadas. O limite de 31
caracteres é verificado sem interromper prematuramente o consumo do identificador.
Isso impede que partes restantes sejam interpretadas como um novo token.

Os números são consumidos enquanto houver algarismos ou pontos. Nenhum ponto
indica inteiro; exatamente um ponto, seguido por algarismos, indica real. Um ponto
final ou mais de um ponto produz erro. Literais precisam conter exatamente um
caractere entre duas aspas simples. Literais vazios, longos ou sem fechamento são
consumidos até um ponto seguro de recuperação e geram somente um erro.

Para operadores, foi adotada a regra de maior correspondência: `==`, `!=`, `<=`,
`>=`, `&&` e `||` são verificados antes dos operadores simples. A barra exige uma
decisão adicional: `//` inicia um comentário, enquanto `/` isolado representa
divisão. Quando um caractere é lido antecipadamente e não pertence ao token,
`ungetc` o devolve ao fluxo.

Os vetores possuem limites fixos verificados antes de cada escrita. Cada token
válido incrementa o contador de tokens e cada falha incrementa o contador de
erros. Um erro não encerra a análise, permitindo apresentar outros problemas do
mesmo arquivo. Tokens e erros léxicos usam a mesma saída para preservar a ordem
em que foram encontrados, inclusive quando o resultado é redirecionado.

## 3. Exemplo de entrada e saída

Entrada:

```c
int idade = 18;
float media = 8.5;
```

Saída resumida:

```text
1:1 | PALAVRA_RESERVADA  | int
1:5 | IDENTIFICADOR      | idade
1:11 | OPERADOR           | =
1:13 | NUMERO_INTEIRO     | 18
1:15 | DELIMITADOR        | ;
2:1 | PALAVRA_RESERVADA  | float
2:7 | IDENTIFICADOR      | media
2:13 | OPERADOR           | =
2:15 | NUMERO_REAL        | 8.5
2:18 | DELIMITADOR        | ;

Total de tokens: 10
Total de erros léxicos: 0
```

Nos testes de erro, `12.` e `1.2.3` foram classificados como números malformados,
`''` como literal vazio, `'ab'` como literal com mais de um caractere e `@` como
símbolo inválido. Em todos os casos, os elementos posteriores continuaram sendo
analisados.

## 4. Testes e resultados

Foram executados os 14 grupos obrigatórios: palavras reservadas, identificadores
válidos, identificador acima de 31 caracteres, inteiros, reais, reais
malformados, todos os operadores, todos os delimitadores, comentários, literais
válidos e inválidos, caracteres desconhecidos, arquivo vazio, arquivo somente
com espaços e comentários e tokens sem separação. Também foram testados comentário
terminado diretamente por `EOF`, operadores incompletos e combinação de números
com identificadores.

O exemplo completo do enunciado produziu 26 tokens e nenhum erro. O código foi
compilado com `gcc -Wall -Wextra -pedantic -std=c11` sem erros ou avisos.

## 5. Principais dificuldades

As principais dificuldades foram manter a posição correta durante leituras
antecipadas, diferenciar `/` de `//`, priorizar operadores compostos e recuperar a
análise após entradas malformadas. Outra preocupação foi consumir lexemas longos
sem escrever fora dos limites dos vetores. A solução foi atualizar linha e coluna
somente para caracteres efetivamente consumidos, devolver antecipações com
`ungetc`, separar o comprimento total da quantidade armazenada e isolar cada
regra de reconhecimento em uma função.

## 6. Divisão do trabalho

O trabalho foi desenvolvido individualmente. Todas as etapas de implementação,
teste e documentação foram realizadas pelo autor do repositório.

## 7. Respostas às questões propostas

### 7.1 Por que palavras reservadas e identificadores podem começar sendo reconhecidos pela mesma regra?

Porque ambos seguem inicialmente o mesmo padrão: começam com letra ou `_` e
podem continuar com letras, algarismos ou `_`. Somente depois de formar o lexema
completo é possível compará-lo com a lista de palavras reservadas. Se houver
correspondência exata, ele é palavra reservada; caso contrário, é identificador.

### 7.2 Por que operadores de dois caracteres devem ser verificados antes dos operadores de um caractere?

Para aplicar a maior correspondência possível. Se `>=` não fosse verificado
primeiro, poderia ser dividido incorretamente nos tokens `>` e `=`. A leitura
antecipada garante que o operador composto seja produzido como um único token.

### 7.3 Qual é a diferença entre um erro léxico e um erro sintático?

Erro léxico ocorre quando os caracteres não formam um token válido, como `@` ou
`1.2.3`. Erro sintático ocorre quando os tokens são individualmente válidos, mas
não obedecem à gramática da linguagem, como `int = 10;`.

### 7.4 Por que o analisador deve continuar depois de encontrar um símbolo inválido?

Para localizar o maior número possível de problemas em uma única execução e
evitar que o usuário precise corrigir e executar novamente para descobrir cada
erro. Para isso, o elemento inválido é consumido e a busca pelo próximo token
continua.

### 7.5 Qual é o risco de não verificar o limite do vetor usado para armazenar um lexema?

A escrita pode ultrapassar a memória reservada, corromper dados, provocar falhas
ou criar vulnerabilidades. Em C, esse acesso fora dos limites possui comportamento
indefinido. Por isso, o programa verifica o espaço disponível antes de armazenar
cada caractere.

### 7.6 Em qual etapa seria detectado o problema em `int = 10;`, considerando que todos os caracteres formam tokens válidos?

Na análise sintática. O analisador léxico reconhece corretamente `int`, `=`, `10`
e `;`, mas o analisador sintático percebe que falta um identificador na declaração.

### 7.7 Qual seria a vantagem de armazenar os identificadores encontrados em uma tabela de símbolos?

A tabela de símbolos centraliza informações sobre nomes usados no programa. Em
etapas posteriores, ela permite associar identificadores a tipo, escopo, endereço
ou valor, detectar declarações duplicadas e verificar usos de nomes não declarados.

## 8. Conclusão

O MiniLexer cumpriu o objetivo de separar e classificar os elementos obrigatórios
da linguagem MiniC, mantendo suas posições e recuperando-se de erros. A atividade
demonstrou a importância da leitura antecipada, do controle de estado e do uso
seguro de memória na implementação da primeira etapa de um compilador.

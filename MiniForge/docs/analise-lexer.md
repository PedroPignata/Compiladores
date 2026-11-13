# Reconhecimento léxico no MiniForge

Documento da implementação vigente em miniforge/lexer.py e tokens.py.

## Fluxo de reconhecimento

Lexer.tokens() chama proximo_token() até EOF. Espaços, tabulações e quebras de
linha separam tokens. Comentários // são consumidos até a quebra ou fim do
arquivo. Cada token guarda categoria, lexema, linha e coluna a partir de 1.

Identificadores seguem `[A-Za-z_][A-Za-z0-9_]*`. O lexer consome o nome inteiro
e só depois consulta RESERVADAS. Portanto le_so2 e sorteia_so2 são nomes comuns.
As onze palavras reservadas vigentes estão na [especificação](especificacao.md).
Inteiros usam `[0-9]+`; o sinal negativo é um operador separado.

Operadores de dois caracteres são testados antes dos de um: <= não se divide
em < e =. A vírgula é um delimitador usado nos argumentos de sorteia_so.

## Texto literal

Aspas duplas iniciam TEXTO. O lexer aceita conteúdo Unicode até a próxima
aspa dupla na mesma linha; // dentro das aspas não inicia comentário.
Não há escapes ou interpolação. TEXTO só é aceito pelo parser como argumento
literal de mostra_so, não como expressão ou valor de variável.
Texto sem fechamento antes da quebra ou EOF gera erro léxico com a posição
inicial. Acentos são válidos em mensagens e comentários, mas não em identificadores.

## Recuperação e limites

Caractere desconhecido é descartado e registrado em Lexer.erros; a leitura
continua para listar erros independentes. A CLI imprime os diagnósticos em
stderr e não passa ao parser se a lista de erros não estiver vazia.
O token EOF é emitido mesmo após recuperação.

12ab é NUM seguido de ID, não um erro léxico: a sequência será rejeitada pelo
parser quando inadequada. ! sozinho é inválido; existe apenas o operador !=.
Não há comentário de bloco, número decimal, notação científica ou identificador
Unicode. Esses limites não devem ser confundidos com os recursos de outro
projeto do repositório, como o MiniLexer escrito em C.

Testes: test_lexer.py, test_mineires.py, test_calculadora_interativa.py e
 test_sorteio.py em tests/. A comparação educacional com outros scanners não
substitui os contratos do código atual.

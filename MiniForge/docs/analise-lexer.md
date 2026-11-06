# Análise de um lexer didático (aula 10)

Projeto analisado: **jlox — Crafting Interpreters** (Java),
`munificent/craftinginterpreters`, arquivo
`java/com/craftinginterpreters/lox/Scanner.java`.

1. **Onde está o laço principal do scanner?**
   Em `scanTokens()`: enquanto `!isAtEnd()`, marca `start = current` e chama
   `scanToken()`. Ao sair do laço, acrescenta o token `EOF`.
   `scanToken()` lê um caractere com `advance()` e decide o token com um
   `switch` sobre ele.

2. **Como diferencia reservada de identificador?**
   Lê a palavra inteira em `identifier()` (laço com `isAlphaNumeric`) e só
   depois consulta o mapa estático `keywords`; se não estiver lá, o tipo é
   `IDENTIFIER`. É a mesma estratégia do nosso `RESERVADAS.get(lex, T.ID)`.

3. **Como reconhece operadores de 2 caracteres?**
   Com `match(expected)`: consome o próximo caractere só se ele for o
   esperado. Ex.: `case '<': addToken(match('=') ? LESS_EQUAL : LESS);`.
   Assim o operador mais longo é sempre tentado primeiro.

4. **Ao achar caractere inválido: para ou continua?**
   Continua. O `default` do `switch` chama
   `Lox.error(line, "Unexpected character.")`, que imprime a mensagem e liga
   `hadError`, mas o laço segue. O interpretador só se recusa a executar
   depois que a varredura inteira termina.

5. **Que posição o token guarda (linha? coluna?)**
   Apenas a linha (`Token(type, lexeme, literal, line)`). Não guarda coluna,
   então as mensagens não apontam o caractere exato.

6. **Uma ideia que vamos copiar e por quê.**
   Continuar depois de um erro léxico e reportar todos de uma vez (modo
   pânico): o programador corrige tudo em uma única compilação. No MiniForge,
   `Lexer.erros` acumula as mensagens, o caractere inválido é descartado e a
   CLI imprime todos os erros em stderr e sai com código 1. Diferente do jlox,
   mantemos também a **coluna**, para mensagens no formato
   `linha:coluna: erro léxico: caractere inválido '@', que trem é esse?`.

## Decisões do lexer do MiniForge

- Laço principal em `Lexer.tokens()`; um token por chamada de `proximo_token()`.
- Maior casamento: identificadores e números consomem o lexema mais longo;
  operadores de 2 caracteres (`==`, `!=`, `<=`, `>=`) testados antes dos de 1.
- Reservadas por tabela (`RESERVADAS`) depois de ler a palavra inteira.
- Identificadores e números só com caracteres ASCII (`[A-Za-z_][A-Za-z0-9_]*`
  e `[0-9]+`); letras acentuadas são caracteres inválidos.
- `!` sozinho é caractere inválido (só existe dentro de `!=`).
- `12ab` não é erro léxico: pelo maior casamento vira `NUM '12'` seguido de
  `ID 'ab'`, e o parser rejeita a sequência.
- Não há strings nem comentários de bloco, então não existem erros de
  "não fechado até o fim do arquivo".

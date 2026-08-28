# MiniLexer

Analisador léxico simplificado para a linguagem fictícia MiniC, desenvolvido
em C para a disciplina de Compiladores.

O programa recebe um arquivo-fonte, realiza a leitura caractere por caractere e
exibe os tokens encontrados com linha, coluna, categoria e lexema. Erros léxicos
são informados sem interromper a análise do restante do arquivo.

## Requisitos

- GCC com suporte ao padrão C11;
- Terminal Linux, macOS ou Windows com GCC instalado.

## Compilação

Na raiz do repositório, execute:

```bash
gcc -Wall -Wextra -pedantic -std=c11 minilexer.c -o minilexer
```

No Windows, o executável pode ser gerado como `minilexer.exe`:

```bash
gcc -Wall -Wextra -pedantic -std=c11 minilexer.c -o minilexer.exe
```

## Execução

No Linux ou macOS:

```bash
./minilexer testes/exemplo.mc
```

No Windows:

```powershell
.\minilexer.exe testes\exemplo.mc
```

Se nenhum arquivo for informado, o programa apresenta:

```text
Uso: ./minilexer <arquivo-fonte>
```

Se o arquivo não puder ser aberto, uma mensagem clara é exibida e o programa
termina com código de falha.

## Formato da saída

Cada token é exibido no formato:

```text
LINHA:COLUNA | CATEGORIA | LEXEMA
```

Exemplo:

```text
1:1 | PALAVRA_RESERVADA  | int
1:5 | IDENTIFICADOR      | idade
1:11 | OPERADOR           | =
1:13 | NUMERO_INTEIRO     | 18
1:15 | DELIMITADOR        | ;

Total de tokens: 5
Total de erros léxicos: 0
```

## Elementos reconhecidos

- Palavras reservadas: `int`, `float`, `char`, `if`, `else`, `while`, `return`
  e `print`;
- Identificadores iniciados por letra ou `_`, com no máximo 31 caracteres;
- Números inteiros;
- Números reais com parte inteira e decimal;
- Literais com exatamente um caractere entre aspas simples;
- Operadores `+`, `-`, `*`, `/`, `%`, `=`, `<`, `>`, `!`, `==`, `!=`, `<=`,
  `>=`, `&&` e `||`;
- Delimitadores `(`, `)`, `{`, `}`, `[`, `]`, `;` e `,`;
- Comentários de uma linha iniciados por `//`.

Espaços, tabulações, quebras de linha e comentários são ignorados, mas
continuam sendo considerados no controle de linha e coluna.

## Decisões de implementação

- O arquivo é lido caractere por caractere com `fgetc`;
- `linha` e `coluna` começam em 1 e são atualizadas a cada caractere consumido;
- A posição inicial é salva antes da leitura completa de cada token;
- `ctype.h` é usado para reconhecer letras, algarismos e espaços;
- Palavras reservadas e identificadores são lidos pela mesma regra inicial e
  diferenciados posteriormente por comparação textual;
- Operadores de dois caracteres são verificados antes dos operadores simples;
- `ungetc` devolve ao fluxo um caractere lido antecipadamente que não pertence ao
  token atual;
- Lexemas possuem limites controlados para impedir escrita fora dos vetores;
- Um identificador acima de 31 caracteres é consumido por completo e gera um
  erro léxico;
- Números como `12.` e `1.2.3` geram erro léxico;
- Depois de um erro, o analisador consome a entrada problemática e continua a
  busca pelos próximos tokens.

## Testes realizados

Os arquivos do diretório `testes/` cobrem os 14 grupos obrigatórios:

| Caso | Arquivo principal |
|---|---|
| Palavras reservadas | `palavras_reservadas.mc` |
| Identificadores válidos e acima de 31 caracteres | `identificadores.mc` |
| Inteiros, reais e reais malformados | `numeros.mc` |
| Operadores e delimitadores | `operadores_delimitadores.mc` |
| Comentários e comentário terminado por EOF | `comentarios.mc`, `comentario_eof.mc` |
| Literais válidos e inválidos | `literais.mc` |
| Caracteres inválidos | `caracteres_invalidos.mc` |
| Arquivo vazio | `vazio.mc` |
| Somente espaços e comentários | `somente_espacos_comentarios.mc` |
| Tokens sem espaços | `sem_espacos.mc` |
| Exemplo integrado do enunciado | `exemplo.mc` |

O exemplo integrado produz 26 tokens e nenhum erro léxico. A bateria também
verifica recuperação depois de identificadores longos, números malformados,
literais inválidos e símbolos desconhecidos.

## Estrutura do projeto

```text
.
├── minilexer.c
├── README.md
├── RELATORIO.md
└── testes/
    ├── exemplo.mc
    ├── palavras_reservadas.mc
    ├── identificadores.mc
    ├── numeros.mc
    ├── operadores_delimitadores.mc
    ├── comentarios.mc
    ├── literais.mc
    ├── caracteres_invalidos.mc
    ├── sem_espacos.mc
    └── vazio.mc
```

O diretório possui casos adicionais de fronteira além dos arquivos destacados.

## Limitações

Conforme o escopo da atividade, o programa não implementa:

- Comentários de múltiplas linhas `/* ... */`;
- Strings entre aspas duplas;
- Sequências de escape em literais, como `'\n'`;
- Números em notação científica;
- Análise sintática ou semântica;
- Verificação de tipos, escopos ou declarações;
- Execução do programa MiniC ou geração de código.

Portanto, uma sequência como `int = 10;` possui tokens léxicos válidos, embora
seja sintaticamente incorreta.

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAMANHO_MAX_IDENTIFICADOR 31
#define TAMANHO_MAX_LEXEMA 63

typedef enum {
    TOKEN_PALAVRA_RESERVADA,
    TOKEN_IDENTIFICADOR,
    TOKEN_NUMERO_INTEIRO,
    TOKEN_NUMERO_REAL,
    TOKEN_LITERAL_CARACTERE,
    TOKEN_OPERADOR,
    TOKEN_DELIMITADOR,
    TOKEN_ERRO
} TipoToken;

typedef struct {
    TipoToken tipo;
    char lexema[TAMANHO_MAX_LEXEMA + 1];
    int linha;
    int coluna;
} Token;

typedef struct {
    FILE *arquivo;
    int linha;
    int coluna;
    int totalTokens;
    int totalErros;
} Scanner;

static void avancarPosicao(Scanner *scanner, int caractere)
{
    if (caractere == '\n') {
        scanner->linha++;
        scanner->coluna = 1;
    } else {
        scanner->coluna++;
    }
}

static int devolverCaractere(Scanner *scanner, int caractere)
{
    if (caractere != EOF &&
        ungetc(caractere, scanner->arquivo) == EOF) {
        fprintf(stderr, "Erro ao devolver caractere ao fluxo.\n");
        return 0;
    }

    return 1;
}

static void adicionarAoLexema(char *lexema,
                              size_t *tamanho,
                              int caractere)
{
    if (*tamanho < TAMANHO_MAX_LEXEMA) {
        lexema[*tamanho] = (char)caractere;
        (*tamanho)++;
    }
}

static int ehInicioIdentificador(int caractere)
{
    return isalpha((unsigned char)caractere) || caractere == '_';
}

static int ehParteIdentificador(int caractere)
{
    return isalnum((unsigned char)caractere) || caractere == '_';
}

static int ehPalavraReservada(const char *lexema)
{
    static const char *palavrasReservadas[] = {
        "int",
        "float",
        "char",
        "if",
        "else",
        "while",
        "return",
        "print"
    };
    size_t quantidade =
        sizeof(palavrasReservadas) / sizeof(palavrasReservadas[0]);
    size_t i;

    for (i = 0; i < quantidade; i++) {
        if (strcmp(lexema, palavrasReservadas[i]) == 0) {
            return 1;
        }
    }

    return 0;
}

static int ehDelimitador(int caractere)
{
    return strchr("(){}[];,", caractere) != NULL;
}

static int ehOperadorDeUmCaractere(int caractere)
{
    return strchr("+-*%=<>!", caractere) != NULL;
}

static int podeFormarOperadorComIgual(int caractere)
{
    return strchr("=!<>", caractere) != NULL;
}

static const char *nomeDoToken(TipoToken tipo)
{
    switch (tipo) {
        case TOKEN_PALAVRA_RESERVADA:
            return "PALAVRA_RESERVADA";
        case TOKEN_IDENTIFICADOR:
            return "IDENTIFICADOR";
        case TOKEN_NUMERO_INTEIRO:
            return "NUMERO_INTEIRO";
        case TOKEN_NUMERO_REAL:
            return "NUMERO_REAL";
        case TOKEN_LITERAL_CARACTERE:
            return "LITERAL_CARACTERE";
        case TOKEN_OPERADOR:
            return "OPERADOR";
        case TOKEN_DELIMITADOR:
            return "DELIMITADOR";
        case TOKEN_ERRO:
            return "ERRO_LEXICO";
    }

    return "DESCONHECIDO";
}

static void imprimirToken(const Token *token)
{
    printf("%d:%d | %-18s | %s\n",
           token->linha,
           token->coluna,
           nomeDoToken(token->tipo),
           token->lexema);
}

static void registrarToken(Scanner *scanner,
                           TipoToken tipo,
                           const char *lexema,
                           int linha,
                           int coluna)
{
    Token token;

    token.tipo = tipo;
    token.linha = linha;
    token.coluna = coluna;
    snprintf(token.lexema, sizeof(token.lexema), "%s", lexema);

    imprimirToken(&token);
    scanner->totalTokens++;
}

static void registrarErroLexico(Scanner *scanner,
                                int linha,
                                int coluna,
                                const char *formato,
                                ...)
{
    va_list argumentos;

    printf("ERRO_LEXICO | linha %d, coluna %d | ", linha, coluna);

    va_start(argumentos, formato);
    vprintf(formato, argumentos);
    va_end(argumentos);

    putchar('\n');
    scanner->totalErros++;
}

static int analisarIdentificador(Scanner *scanner, int caractere)
{
    char lexema[TAMANHO_MAX_LEXEMA + 1];
    size_t tamanhoLexema = 0;
    size_t comprimentoTotal = 0;
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    do {
        adicionarAoLexema(lexema, &tamanhoLexema, caractere);
        comprimentoTotal++;
        avancarPosicao(scanner, caractere);
        caractere = fgetc(scanner->arquivo);
    } while (caractere != EOF && ehParteIdentificador(caractere));

    lexema[tamanhoLexema] = '\0';

    if (!devolverCaractere(scanner, caractere)) {
        return 0;
    }

    if (comprimentoTotal > TAMANHO_MAX_IDENTIFICADOR) {
        registrarErroLexico(scanner,
                            linhaInicial,
                            colunaInicial,
                            "identificador excede 31 caracteres");
    } else if (ehPalavraReservada(lexema)) {
        registrarToken(scanner,
                       TOKEN_PALAVRA_RESERVADA,
                       lexema,
                       linhaInicial,
                       colunaInicial);
    } else {
        registrarToken(scanner,
                       TOKEN_IDENTIFICADOR,
                       lexema,
                       linhaInicial,
                       colunaInicial);
    }

    return 1;
}

static int analisarNumero(Scanner *scanner, int caractere)
{
    char lexema[TAMANHO_MAX_LEXEMA + 1];
    size_t tamanhoLexema = 0;
    size_t comprimentoTotal = 0;
    int quantidadePontos = 0;
    int terminaComPonto = 0;
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    do {
        adicionarAoLexema(lexema, &tamanhoLexema, caractere);
        comprimentoTotal++;

        if (caractere == '.') {
            quantidadePontos++;
            terminaComPonto = 1;
        } else {
            terminaComPonto = 0;
        }

        avancarPosicao(scanner, caractere);
        caractere = fgetc(scanner->arquivo);
    } while (caractere != EOF &&
             (isdigit((unsigned char)caractere) || caractere == '.'));

    lexema[tamanhoLexema] = '\0';

    if (!devolverCaractere(scanner, caractere)) {
        return 0;
    }

    if (comprimentoTotal > TAMANHO_MAX_LEXEMA) {
        registrarErroLexico(scanner,
                            linhaInicial,
                            colunaInicial,
                            "número excede o tamanho suportado");
    } else if (quantidadePontos == 0) {
        registrarToken(scanner,
                       TOKEN_NUMERO_INTEIRO,
                       lexema,
                       linhaInicial,
                       colunaInicial);
    } else if (quantidadePontos == 1 && !terminaComPonto) {
        registrarToken(scanner,
                       TOKEN_NUMERO_REAL,
                       lexema,
                       linhaInicial,
                       colunaInicial);
    } else {
        registrarErroLexico(scanner,
                            linhaInicial,
                            colunaInicial,
                            "número malformado: %s",
                            lexema);
    }

    return 1;
}

static void analisarLiteral(Scanner *scanner)
{
    char lexema[TAMANHO_MAX_LEXEMA + 1];
    size_t tamanhoLexema = 0;
    int proximoCaractere;
    int literalValido = 0;
    const char *mensagemErro = NULL;
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    adicionarAoLexema(lexema, &tamanhoLexema, '\'');
    avancarPosicao(scanner, '\'');
    proximoCaractere = fgetc(scanner->arquivo);

    if (proximoCaractere == EOF) {
        mensagemErro = "literal de caractere não fechado";
    } else if (proximoCaractere == '\n') {
        avancarPosicao(scanner, proximoCaractere);
        mensagemErro = "literal de caractere não fechado";
    } else if (proximoCaractere == '\'') {
        adicionarAoLexema(lexema, &tamanhoLexema, proximoCaractere);
        avancarPosicao(scanner, proximoCaractere);
        mensagemErro = "literal de caractere vazio";
    } else {
        adicionarAoLexema(lexema, &tamanhoLexema, proximoCaractere);
        avancarPosicao(scanner, proximoCaractere);
        proximoCaractere = fgetc(scanner->arquivo);

        if (proximoCaractere == '\'') {
            adicionarAoLexema(lexema, &tamanhoLexema, proximoCaractere);
            avancarPosicao(scanner, proximoCaractere);
            literalValido = 1;
        } else {
            while (proximoCaractere != EOF &&
                   proximoCaractere != '\n' &&
                   proximoCaractere != '\'') {
                adicionarAoLexema(lexema,
                                  &tamanhoLexema,
                                  proximoCaractere);
                avancarPosicao(scanner, proximoCaractere);
                proximoCaractere = fgetc(scanner->arquivo);
            }

            if (proximoCaractere == '\'') {
                adicionarAoLexema(lexema,
                                  &tamanhoLexema,
                                  proximoCaractere);
                avancarPosicao(scanner, proximoCaractere);
                mensagemErro = "literal contém mais de um caractere";
            } else {
                if (proximoCaractere == '\n') {
                    avancarPosicao(scanner, proximoCaractere);
                }

                mensagemErro = "literal de caractere não fechado";
            }
        }
    }

    lexema[tamanhoLexema] = '\0';

    if (literalValido) {
        registrarToken(scanner,
                       TOKEN_LITERAL_CARACTERE,
                       lexema,
                       linhaInicial,
                       colunaInicial);
    } else {
        registrarErroLexico(scanner,
                            linhaInicial,
                            colunaInicial,
                            "%s: %s",
                            mensagemErro,
                            lexema);
    }
}

static void analisarDelimitador(Scanner *scanner, int caractere)
{
    char lexema[2] = {(char)caractere, '\0'};
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    registrarToken(scanner,
                   TOKEN_DELIMITADOR,
                   lexema,
                   linhaInicial,
                   colunaInicial);
    avancarPosicao(scanner, caractere);
}

static int analisarBarraOuComentario(Scanner *scanner)
{
    int proximoCaractere;
    int caractere;
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    proximoCaractere = fgetc(scanner->arquivo);

    if (proximoCaractere == '/') {
        avancarPosicao(scanner, '/');
        avancarPosicao(scanner, '/');

        while ((caractere = fgetc(scanner->arquivo)) != EOF) {
            avancarPosicao(scanner, caractere);

            if (caractere == '\n') {
                break;
            }
        }

        return 1;
    }

    if (!devolverCaractere(scanner, proximoCaractere)) {
        return 0;
    }

    registrarToken(scanner,
                   TOKEN_OPERADOR,
                   "/",
                   linhaInicial,
                   colunaInicial);
    avancarPosicao(scanner, '/');

    return 1;
}

static int analisarOperador(Scanner *scanner, int caractere)
{
    char lexema[3] = {(char)caractere, '\0', '\0'};
    int proximoCaractere;
    int linhaInicial = scanner->linha;
    int colunaInicial = scanner->coluna;

    if (caractere == '&' || caractere == '|') {
        proximoCaractere = fgetc(scanner->arquivo);

        if (proximoCaractere == caractere) {
            lexema[1] = (char)proximoCaractere;
            avancarPosicao(scanner, caractere);
            avancarPosicao(scanner, proximoCaractere);
            registrarToken(scanner,
                           TOKEN_OPERADOR,
                           lexema,
                           linhaInicial,
                           colunaInicial);
        } else {
            if (!devolverCaractere(scanner, proximoCaractere)) {
                return 0;
            }

            registrarErroLexico(scanner,
                                linhaInicial,
                                colunaInicial,
                                "operador incompleto: %c",
                                caractere);
            avancarPosicao(scanner, caractere);
        }

        return 1;
    }

    if (podeFormarOperadorComIgual(caractere)) {
        proximoCaractere = fgetc(scanner->arquivo);

        if (proximoCaractere == '=') {
            lexema[1] = '=';
            avancarPosicao(scanner, caractere);
            avancarPosicao(scanner, proximoCaractere);
        } else {
            if (!devolverCaractere(scanner, proximoCaractere)) {
                return 0;
            }

            avancarPosicao(scanner, caractere);
        }
    } else {
        avancarPosicao(scanner, caractere);
    }

    registrarToken(scanner,
                   TOKEN_OPERADOR,
                   lexema,
                   linhaInicial,
                   colunaInicial);

    return 1;
}

static int analisarArquivo(Scanner *scanner)
{
    int caractere;

    while ((caractere = fgetc(scanner->arquivo)) != EOF) {
        if (isspace((unsigned char)caractere)) {
            avancarPosicao(scanner, caractere);
        } else if (ehInicioIdentificador(caractere)) {
            if (!analisarIdentificador(scanner, caractere)) {
                return 0;
            }
        } else if (isdigit((unsigned char)caractere)) {
            if (!analisarNumero(scanner, caractere)) {
                return 0;
            }
        } else if (caractere == '\'') {
            analisarLiteral(scanner);
        } else if (ehDelimitador(caractere)) {
            analisarDelimitador(scanner, caractere);
        } else if (caractere == '/') {
            if (!analisarBarraOuComentario(scanner)) {
                return 0;
            }
        } else if (ehOperadorDeUmCaractere(caractere) ||
                   caractere == '&' || caractere == '|') {
            if (!analisarOperador(scanner, caractere)) {
                return 0;
            }
        } else {
            registrarErroLexico(scanner,
                                scanner->linha,
                                scanner->coluna,
                                "símbolo inválido: %c",
                                caractere);
            avancarPosicao(scanner, caractere);
        }
    }

    return 1;
}

int main(int argc, char *argv[])
{
    Scanner scanner;

    if (argc != 2) {
        fprintf(stderr, "Uso: %s <arquivo-fonte>\n", argv[0]);
        return EXIT_FAILURE;
    }

    scanner.arquivo = fopen(argv[1], "r");

    if (scanner.arquivo == NULL) {
        fprintf(stderr,
                "Erro: não foi possível abrir o arquivo '%s'.\n",
                argv[1]);
        return EXIT_FAILURE;
    }

    scanner.linha = 1;
    scanner.coluna = 1;
    scanner.totalTokens = 0;
    scanner.totalErros = 0;

    if (!analisarArquivo(&scanner)) {
        fclose(scanner.arquivo);
        return EXIT_FAILURE;
    }

    if (ferror(scanner.arquivo)) {
        fprintf(stderr,
                "Erro durante a leitura do arquivo '%s'.\n",
                argv[1]);
        fclose(scanner.arquivo);
        return EXIT_FAILURE;
    }

    if (fclose(scanner.arquivo) != 0) {
        fprintf(stderr,
                "Erro ao fechar o arquivo '%s'.\n",
                argv[1]);
        return EXIT_FAILURE;
    }

    printf("\nTotal de tokens: %d\n", scanner.totalTokens);
    printf("Total de erros léxicos: %d\n", scanner.totalErros);

    return EXIT_SUCCESS;
}

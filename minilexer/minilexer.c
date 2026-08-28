#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAMANHO_MAX_IDENTIFICADOR 31
#define TAMANHO_MAX_LEXEMA 63

static void avancarPosicao(int caractere, int *linha, int *coluna)
{
    if (caractere == '\n') {
        (*linha)++;
        *coluna = 1;
    } else {
        (*coluna)++;
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

static void imprimirToken(int linha,
                          int coluna,
                          const char *categoria,
                          const char *lexema)
{
    printf("%d:%d | %-18s | %s\n",
           linha,
           coluna,
           categoria,
           lexema);
}

int main(int argc, char *argv[])
{
    FILE *arquivo;
    int caractere;
    int linha = 1;
    int coluna = 1;
    int totalTokens = 0;
    int totalErros = 0;

    if (argc != 2) {
        fprintf(stderr, "Uso: %s <arquivo-fonte>\n", argv[0]);
        return EXIT_FAILURE;
    }

    arquivo = fopen(argv[1], "r");

    if (arquivo == NULL) {
        fprintf(stderr,
                "Erro: não foi possível abrir o arquivo '%s'.\n",
                argv[1]);
        return EXIT_FAILURE;
    }

    while ((caractere = fgetc(arquivo)) != EOF) {
        /*
         * Ignora espaços, tabulações, quebras de linha
         * e outros caracteres reconhecidos por isspace.
         */
        if (isspace((unsigned char)caractere)) {
            avancarPosicao(caractere, &linha, &coluna);
            continue;
        }

        /*
         * Identificadores e palavras reservadas.
         */
        if (ehInicioIdentificador(caractere)) {
            char lexema[TAMANHO_MAX_IDENTIFICADOR + 1];
            size_t caracteresArmazenados = 0;
            size_t comprimentoTotal = 0;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            do {
                if (caracteresArmazenados <
                    TAMANHO_MAX_IDENTIFICADOR) {
                    lexema[caracteresArmazenados] =
                        (char)caractere;
                    caracteresArmazenados++;
                }

                comprimentoTotal++;
                avancarPosicao(caractere, &linha, &coluna);
                caractere = fgetc(arquivo);
            } while (caractere != EOF &&
                     ehParteIdentificador(caractere));

            lexema[caracteresArmazenados] = '\0';

            if (caractere != EOF &&
                ungetc(caractere, arquivo) == EOF) {
                fprintf(stderr,
                        "Erro ao devolver caractere ao fluxo.\n");
                fclose(arquivo);
                return EXIT_FAILURE;
            }

            if (comprimentoTotal >
                TAMANHO_MAX_IDENTIFICADOR) {
                fprintf(stderr,
                        "ERRO_LEXICO | linha %d, coluna %d | "
                        "identificador excede 31 caracteres\n",
                        linhaInicial,
                        colunaInicial);
                totalErros++;
            } else if (ehPalavraReservada(lexema)) {
                imprimirToken(linhaInicial,
                              colunaInicial,
                              "PALAVRA_RESERVADA",
                              lexema);
                totalTokens++;
            } else {
                imprimirToken(linhaInicial,
                              colunaInicial,
                              "IDENTIFICADOR",
                              lexema);
                totalTokens++;
            }

            continue;
        }

        /*
         * Números inteiros, reais e malformados.
         */
        if (isdigit((unsigned char)caractere)) {
            char lexema[TAMANHO_MAX_LEXEMA + 1];
            size_t caracteresArmazenados = 0;
            size_t comprimentoTotal = 0;
            int quantidadePontos = 0;
            int terminaComPonto = 0;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            do {
                if (caracteresArmazenados <
                    TAMANHO_MAX_LEXEMA) {
                    lexema[caracteresArmazenados] =
                        (char)caractere;
                    caracteresArmazenados++;
                }

                comprimentoTotal++;

                if (caractere == '.') {
                    quantidadePontos++;
                    terminaComPonto = 1;
                } else {
                    terminaComPonto = 0;
                }

                avancarPosicao(caractere, &linha, &coluna);
                caractere = fgetc(arquivo);
            } while (caractere != EOF &&
                     (isdigit((unsigned char)caractere) ||
                      caractere == '.'));

            lexema[caracteresArmazenados] = '\0';

            if (caractere != EOF &&
                ungetc(caractere, arquivo) == EOF) {
                fprintf(stderr,
                        "Erro ao devolver caractere ao fluxo.\n");
                fclose(arquivo);
                return EXIT_FAILURE;
            }

            if (comprimentoTotal > TAMANHO_MAX_LEXEMA) {
                fprintf(stderr,
                        "ERRO_LEXICO | linha %d, coluna %d | "
                        "número excede o tamanho suportado\n",
                        linhaInicial,
                        colunaInicial);
                totalErros++;
            } else if (quantidadePontos == 0) {
                imprimirToken(linhaInicial,
                              colunaInicial,
                              "NUMERO_INTEIRO",
                              lexema);
                totalTokens++;
            } else if (quantidadePontos == 1 &&
                       !terminaComPonto) {
                imprimirToken(linhaInicial,
                              colunaInicial,
                              "NUMERO_REAL",
                              lexema);
                totalTokens++;
            } else {
                fprintf(stderr,
                        "ERRO_LEXICO | linha %d, coluna %d | "
                        "número malformado: %s\n",
                        linhaInicial,
                        colunaInicial,
                        lexema);
                totalErros++;
            }

            continue;
        }

        /*
         * Literais de caractere.
         */
        if (caractere == '\'') {
            char lexema[TAMANHO_MAX_LEXEMA + 1];
            size_t tamanhoLexema = 0;
            int proximoCaractere;
            int literalValido = 0;
            const char *mensagemErro = NULL;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            /*
             * Consome a aspa de abertura.
             */
            lexema[tamanhoLexema++] = '\'';
            avancarPosicao(caractere, &linha, &coluna);

            proximoCaractere = fgetc(arquivo);

            if (proximoCaractere == EOF) {
                mensagemErro =
                    "literal de caractere não fechado";
            } else if (proximoCaractere == '\n') {
                avancarPosicao(proximoCaractere,
                               &linha,
                               &coluna);

                mensagemErro =
                    "literal de caractere não fechado";
            } else if (proximoCaractere == '\'') {
                /*
                 * Duas aspas consecutivas: literal vazio.
                 */
                lexema[tamanhoLexema++] = '\'';

                avancarPosicao(proximoCaractere,
                               &linha,
                               &coluna);

                mensagemErro =
                    "literal de caractere vazio";
            } else {
                /*
                 * Consome o caractere que deveria estar
                 * dentro do literal.
                 */
                if (tamanhoLexema < TAMANHO_MAX_LEXEMA) {
                    lexema[tamanhoLexema++] =
                        (char)proximoCaractere;
                }

                avancarPosicao(proximoCaractere,
                               &linha,
                               &coluna);

                proximoCaractere = fgetc(arquivo);

                if (proximoCaractere == '\'') {
                    /*
                     * Exatamente um caractere e uma aspa final.
                     */
                    if (tamanhoLexema <
                        TAMANHO_MAX_LEXEMA) {
                        lexema[tamanhoLexema++] = '\'';
                    }

                    avancarPosicao(proximoCaractere,
                                   &linha,
                                   &coluna);

                    literalValido = 1;
                } else {
                    /*
                     * Consome o restante até aspa, nova linha ou EOF.
                     */
                    while (proximoCaractere != EOF &&
                           proximoCaractere != '\n' &&
                           proximoCaractere != '\'') {
                        if (tamanhoLexema <
                            TAMANHO_MAX_LEXEMA) {
                            lexema[tamanhoLexema++] =
                                (char)proximoCaractere;
                        }

                        avancarPosicao(proximoCaractere,
                                       &linha,
                                       &coluna);

                        proximoCaractere = fgetc(arquivo);
                    }

                    if (proximoCaractere == '\'') {
                        if (tamanhoLexema <
                            TAMANHO_MAX_LEXEMA) {
                            lexema[tamanhoLexema++] = '\'';
                        }

                        avancarPosicao(proximoCaractere,
                                       &linha,
                                       &coluna);

                        mensagemErro =
                            "literal contém mais de um caractere";
                    } else {
                        if (proximoCaractere == '\n') {
                            avancarPosicao(proximoCaractere,
                                           &linha,
                                           &coluna);
                        }

                        mensagemErro =
                            "literal de caractere não fechado";
                    }
                }
            }

            lexema[tamanhoLexema] = '\0';

            if (literalValido) {
                imprimirToken(linhaInicial,
                              colunaInicial,
                              "LITERAL_CARACTERE",
                              lexema);
                totalTokens++;
            } else {
                fprintf(stderr,
                        "ERRO_LEXICO | linha %d, coluna %d | "
                        "%s: %s\n",
                        linhaInicial,
                        colunaInicial,
                        mensagemErro,
                        lexema);
                totalErros++;
            }

            continue;
        }

        /*
         * Delimitadores.
         */
        if (ehDelimitador(caractere)) {
            char lexema[2];
            int linhaInicial = linha;
            int colunaInicial = coluna;

            lexema[0] = (char)caractere;
            lexema[1] = '\0';

            imprimirToken(linhaInicial,
                          colunaInicial,
                          "DELIMITADOR",
                          lexema);
            totalTokens++;

            avancarPosicao(caractere, &linha, &coluna);
            continue;
        }

        /*
         * A barra pode ser divisão ou início de comentário.
         */
        if (caractere == '/') {
            int proximoCaractere;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            proximoCaractere = fgetc(arquivo);

            if (proximoCaractere == '/') {
                avancarPosicao('/', &linha, &coluna);
                avancarPosicao('/', &linha, &coluna);

                while ((caractere = fgetc(arquivo)) != EOF) {
                    avancarPosicao(caractere,
                                   &linha,
                                   &coluna);

                    if (caractere == '\n') {
                        break;
                    }
                }

                continue;
            }

            if (proximoCaractere != EOF &&
                ungetc(proximoCaractere, arquivo) == EOF) {
                fprintf(stderr,
                        "Erro ao devolver caractere ao fluxo.\n");
                fclose(arquivo);
                return EXIT_FAILURE;
            }

            imprimirToken(linhaInicial,
                          colunaInicial,
                          "OPERADOR",
                          "/");
            totalTokens++;

            avancarPosicao('/', &linha, &coluna);
            continue;
        }

        /*
         * Operadores simples e operadores seguidos por '='.
         */
        if (ehOperadorDeUmCaractere(caractere)) {
            char lexema[3];
            int proximoCaractere;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            lexema[0] = (char)caractere;
            lexema[1] = '\0';
            lexema[2] = '\0';

            if (podeFormarOperadorComIgual(caractere)) {
                proximoCaractere = fgetc(arquivo);

                if (proximoCaractere == '=') {
                    lexema[1] = '=';

                    avancarPosicao(caractere,
                                   &linha,
                                   &coluna);
                    avancarPosicao(proximoCaractere,
                                   &linha,
                                   &coluna);
                } else {
                    if (proximoCaractere != EOF &&
                        ungetc(proximoCaractere, arquivo) == EOF) {
                        fprintf(stderr,
                                "Erro ao devolver caractere "
                                "ao fluxo.\n");
                        fclose(arquivo);
                        return EXIT_FAILURE;
                    }

                    avancarPosicao(caractere,
                                   &linha,
                                   &coluna);
                }
            } else {
                avancarPosicao(caractere,
                               &linha,
                               &coluna);
            }

            imprimirToken(linhaInicial,
                          colunaInicial,
                          "OPERADOR",
                          lexema);
            totalTokens++;
            continue;
        }

        /*
         * && e ||. Um único & ou | não é válido.
         */
        if (caractere == '&' || caractere == '|') {
            char lexema[3];
            int proximoCaractere;
            int linhaInicial = linha;
            int colunaInicial = coluna;

            proximoCaractere = fgetc(arquivo);

            if (proximoCaractere == caractere) {
                lexema[0] = (char)caractere;
                lexema[1] = (char)proximoCaractere;
                lexema[2] = '\0';

                imprimirToken(linhaInicial,
                              colunaInicial,
                              "OPERADOR",
                              lexema);
                totalTokens++;

                avancarPosicao(caractere,
                               &linha,
                               &coluna);
                avancarPosicao(proximoCaractere,
                               &linha,
                               &coluna);
            } else {
                if (proximoCaractere != EOF &&
                    ungetc(proximoCaractere, arquivo) == EOF) {
                    fprintf(stderr,
                            "Erro ao devolver caractere ao fluxo.\n");
                    fclose(arquivo);
                    return EXIT_FAILURE;
                }

                fprintf(stderr,
                        "ERRO_LEXICO | linha %d, coluna %d | "
                        "operador incompleto: %c\n",
                        linhaInicial,
                        colunaInicial,
                        caractere);
                totalErros++;

                avancarPosicao(caractere,
                               &linha,
                               &coluna);
            }

            continue;
        }

        /*
         * Qualquer caractere restante é inválido.
         */
        fprintf(stderr,
                "ERRO_LEXICO | linha %d, coluna %d | "
                "símbolo inválido: %c\n",
                linha,
                coluna,
                caractere);
        totalErros++;

        avancarPosicao(caractere, &linha, &coluna);
    }

    if (ferror(arquivo)) {
        fprintf(stderr,
                "Erro durante a leitura do arquivo '%s'.\n",
                argv[1]);
        fclose(arquivo);
        return EXIT_FAILURE;
    }

    if (fclose(arquivo) != 0) {
        fprintf(stderr,
                "Erro ao fechar o arquivo '%s'.\n",
                argv[1]);
        return EXIT_FAILURE;
    }

    printf("\nTotal de tokens: %d\n", totalTokens);
    printf("Total de erros léxicos: %d\n", totalErros);

    return EXIT_SUCCESS;
}
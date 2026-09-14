# Registro dos principais prompts

Este arquivo registra solicitações relevantes feitas a ferramentas de IA durante
o desenvolvimento. Novas entradas devem informar data, objetivo, prompt e como
o resultado foi revisado pela equipe.

## 2026-09-11 — Análise e arquitetura inicial

**Objetivo:** analisar integralmente o enunciado, criar a pasta do projeto dentro
do repositório da disciplina, planejar sua arquitetura e publicar essa base.

**Prompt principal:**

> Me ajude a fazer essa atividade de compiladores. Analise o arquivo por inteiro,
> mas antes vamos criar a pasta dessa atividade e sua arquitetura. Tudo será
> feito na pasta de Compiladores do computador, como está na imagem. Ela já está
> conectada ao repositório Git, se não me engano. Publique também no meu
> repositório de Compiladores.

**Arquivos de contexto:**

- `Desafio_Simulador_Arquitetura_Transformer.pdf`
- captura de tela da pasta local `Compiladores`

**Revisão realizada:** a opção inicial por React + TypeScript foi substituída
por Python + Streamlit após discussão com o aluno. Os requisitos e limites
foram mantidos.

## 2026-09-14 — Implementação completa em Python

**Objetivo:** implementar, parte por parte, todos os requisitos do enunciado em
Python e garantir os nove entregáveis.

**Prompt principal:**

> Vamos começar! Quero ir parte por parte fazendo tudo que é pedido no arquivo
> da atividade. Vamos fazer em Python. Lembrando os nove entregáveis e todos os
> tópicos obrigatórios do README.

**Resultado aproveitado:** arquitetura migrada para Python + Streamlit; núcleo
matemático determinístico; interface das 13 etapas; testes; documentação;
tabela, capturas e vídeo de evidência.

**Revisão realizada:** compilação Python, 29 testes automatizados, execução dos
dez casos do enunciado, inspeção no navegador, correção de contraste e
verificação de erros no console.

## Modelo para próximas entradas

```text
## AAAA-MM-DD — Título

Objetivo:
Prompt principal:
Arquivos de contexto:
Resultado aproveitado:
Revisão realizada:
```

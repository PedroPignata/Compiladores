# Simulador Educacional de uma Arquitetura Transformer

Projeto da disciplina de Compiladores para demonstrar visualmente como uma
frase é normalizada, tokenizada, convertida em representações numéricas,
contextualizada por atenção e usada para gerar uma resposta token por token.

> Status: arquitetura inicial e análise do enunciado concluídas. A aplicação
> ainda não foi implementada.

## Estratégia escolhida

A primeira versão será uma simulação didática determinística, executada
inteiramente no navegador. Ela utilizará operações matemáticas reais sobre
vetores pequenos, mas não tentará reproduzir os parâmetros internos de uma LLM
comercial.

- React para compor os painéis e controlar a interação.
- TypeScript para modelar os dados de cada etapa com contratos explícitos.
- Vite para desenvolvimento e geração da versão publicável.
- SVG e CSS para matrizes, mapas de calor e relações de atenção.
- Vitest e Testing Library para testes unitários e de integração.
- Playwright para validar os dez fluxos obrigatórios na interface.

As dependências e os arquivos executáveis serão adicionados na etapa de
implementação. Nenhuma chave de API será necessária na versão mínima.

## Documentação inicial

- [Análise integral do enunciado](./docs/analise-do-enunciado.md)
- [Arquitetura planejada](./docs/arquitetura.md)
- [Registro dos principais prompts](./PROMPTS.md)

## Estrutura do projeto

```text
transformer-simulator/
├── docs/                         # requisitos, arquitetura e relatório
├── evidencias/
│   ├── capturas-de-tela/         # imagens da aplicação final
│   ├── resultados-dos-testes/    # tabela e saídas dos dez testes
│   └── video/                    # demonstração curta
├── src/
│   ├── app/                      # composição e estado global da simulação
│   ├── components/
│   │   ├── input/                # entrada, Processar e Reiniciar
│   │   ├── pipeline/             # navegação pelas etapas
│   │   ├── visualizations/       # tokens, vetores, QKV e atenção
│   │   └── result/               # geração progressiva e resumo final
│   ├── core/
│   │   ├── normalization/        # preparação explícita do texto
│   │   ├── tokenization/         # separação em tokens
│   │   ├── vocabulary/           # IDs estáveis e token desconhecido
│   │   ├── embeddings/           # vetores didáticos determinísticos
│   │   ├── positional-encoding/  # codificação da ordem
│   │   ├── attention/            # Q, K, V, softmax e duas cabeças
│   │   ├── layers/               # três camadas encadeadas
│   │   └── generation/           # probabilidades e próximo token
│   ├── data/                     # vocabulário e respostas cadastradas
│   ├── hooks/                    # integração entre interface e simulador
│   ├── styles/                   # estilos e acessibilidade visual
│   └── types/                    # contratos compartilhados
└── tests/
    ├── unit/                     # matemática e transformações isoladas
    ├── integration/              # pipeline completo
    ├── e2e/                      # dez situações obrigatórias
    └── fixtures/                 # entradas e resultados esperados
```

## Próximas etapas

1. Criar o projeto React/TypeScript e os contratos do domínio.
2. Implementar o núcleo matemático determinístico com testes unitários.
3. Construir os painéis da interface e a geração progressiva.
4. Executar e registrar os dez testes obrigatórios.
5. Finalizar relatório, diagrama, capturas, vídeo e publicação.

## Aviso educacional obrigatório

> Esta é uma simulação educacional simplificada. Os valores não representam os
> parâmetros internos de uma LLM comercial.

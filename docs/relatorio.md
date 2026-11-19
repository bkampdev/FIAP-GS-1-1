# Neighborhood Action Dashboard

## Problema e público

**Global Solution 2026.2 · CitizenTech · Grupo 2**

Graduação ON em Ciência da Computação · FIAP

| Integrante | Registro acadêmico |
| --- | --- |
| Davi Coninck Cassaro | RM572772 |
| Eduardo Backes Klauck | RM575889 |
| Gabriel Gonzales | RM574746 |
| Guilherme Cardoso Bremenkamp | RM574229 |
| Lorenzo Mendes Rocha | RM575361 |

### Jardim Horizonte

No bairro fictício Jardim Horizonte, problemas como uma luminária apagada, uma passagem obstruída ou a deterioração de uma praça podem ser relatados em momentos e lugares diferentes. Quando as informações ficam dispersas, moradores encontram dificuldade para saber se um problema já foi registrado e se alguém iniciou sua análise.

O painel organiza relatos de iluminação, acessibilidade, limpeza e conservação de espaços coletivos. Cada ocorrência tem um código para que a mesma demanda possa ser localizada da abertura ao encerramento. A consulta por categoria e situação permite examinar problemas semelhantes e identificar o que segue pendente.

O público inclui quem mora no bairro, circula por ele ou participa de ações comunitárias. Pessoas idosas, pessoas com deficiência ou mobilidade reduzida e seus cuidadores têm interesse especial em informações claras sobre barreiras em trajetos e espaços de uso coletivo. Uma descrição direta, como "passagem obstruída na praça", facilita a compreensão e a discussão entre diferentes pessoas.

## Requisitos e estruturas de dados

### Escopo e dados

O protótipo usa Python e um menu no terminal. O fluxo reúne listagem, cadastro, busca por código, filtros por categoria e situação, atualização com histórico, fila de abertas, agrupamento por bairro e indicadores.

O código fica em `src/`, a base de inicialização em `data/`, os testes em `tests/` e a documentação em `docs/`. Funções, condicionais e laços estruturam o fluxo.

Os arquivos `data/dados.csv` e `data/historico.csv` guardam a base inicial em UTF-8. Uma ocorrência exige código único, categoria, descrição, bairro, local, dia de abertura e situação. Um evento guarda o código, a situação anterior, a nova situação e o dia da alteração. O cenário inicial foi definido com 12 ocorrências válidas, uma linha inconsistente para exercitar a validação e 10 eventos simulados para reconstruir o histórico.

### Escolhas de representação

| Estrutura | Justificativa |
| --- | --- |
| Lista | Percorre os registros para listar, filtrar e agrupar na ordem de cadastro. |
| Fila | Mantém os códigos de ocorrências abertas por ordem de chegada. |
| Pilha | Empilha alterações e permite consultar os eventos mais recentes primeiro. |
| Dicionário | Associa rótulos aos campos da ocorrência. Um índice por código permite consulta direta. |
| Hierarquia | Agrupa ocorrências em bairro e categoria. |
| Matriz | Cruza as quatro categorias com as três situações em uma lista de listas. |

O índice por código aponta para a mesma ocorrência mantida na lista principal. Assim, uma atualização de situação também aparece na busca e nos filtros. O agrupamento e os indicadores são calculados a partir dos registros da sessão.

## Regras lógicas e fluxo

### Validação e busca

O cadastro exige campos preenchidos, código único, categoria e situação padronizadas e dia de abertura inteiro positivo. `not valor.strip()` identifica um campo de texto vazio após retirar espaços. Um código já presente no índice é rejeitado como duplicado. A base informa a rejeição e aproveita os demais registros. A busca informa quando o código está ausente. O identificador é texto para preservar zeros à esquerda, como em `013`.

O filtro aceita cada critério omitido ou coincidente com o registro. Os resultados satisfazem as duas condições em conjunto. Para iluminação e aberta, por exemplo, uma ocorrência de iluminação em análise fica fora da seleção. O README apresenta a expressão booleana dessa regra.

### Estados e histórico

- **Aberta.** Ocorrência cadastrada e aguardando análise. Novos códigos vão ao fim da fila.
- **Em análise.** A análise simulada começou. O código sai da fila de abertas e a alteração entra no histórico.
- **Concluída.** Encerra o acompanhamento da ocorrência no cenário simulado. O dia desse evento é usado no indicador de tempo.

Só são aceitas as mudanças de aberta para em análise e de em análise para concluída. O dia da mudança precisa ser inteiro positivo e igual ou posterior à abertura e ao último evento da ocorrência. Uma atualização rejeitada preserva a situação, a fila e o histórico. Durante a sessão, a pilha acumula eventos. A consulta os mostra na ordem inversa da aplicação.

## Indicadores do cenário inicial

### Dados de origem e cálculo

O cenário considera as ocorrências válidas de `data/dados.csv` e as alterações simuladas de `data/historico.csv`. Cada ocorrência acrescenta uma unidade à célula correspondente à sua categoria e situação atual. As somas de linhas e colunas dão os totais usados nas proporções.

| Categoria | Aberta | Em análise | Concluída | Total |
| --- | --- | --- | --- | --- |
| Iluminação | 1 | 1 | 1 | 3 |
| Acessibilidade | 1 | 1 | 1 | 3 |
| Limpeza | 1 | 1 | 1 | 3 |
| Conservação de espaços coletivos | 2 | 1 | 0 | 3 |
| Total | 5 | 4 | 3 | 12 |

- **Proporção.** Divida o total da categoria ou situação pelo total de ocorrências válidas e multiplique por 100. Cada categoria representa 25%. Por situação, 41,67% estão abertas, 33,33% em análise e 25,00% concluídas. Com a base vazia, a proporção é zero.
- **Pendências.** Soma de abertas e em análise, ou `5 + 4 = 9`.
- **Tempo médio de conclusão.** Soma das diferenças entre os dias de conclusão e abertura, dividida pela quantidade de conclusões. Os intervalos esperados são 4, 6 e 8 dias, com média de 6 dias. Sem conclusões, a média fica indisponível.

Entre as 12 ocorrências, três estão concluídas. Conservação soma três pendências e nenhuma conclusão. Nesse exercício, o cruzamento permite identificar essa concentração mesmo com as categorias tendo o mesmo volume de registros. A ordem da fila informa o que chegou primeiro. A avaliação da urgência dependeria das condições observadas em cada caso.

## Verificação, limites e impacto

### Verificação dos resultados

Uma execução com uma base fictícia independente e os módulos em desenvolvimento confirmou a fila, o histórico, a matriz e os cálculos. O ensaio também cobriu a rejeição de duplicidade e de salto de situação. Na versão integrada, rode a suíte:

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests
```

Em seguida, reproduza o roteiro no menu iniciado com `python src/sistema.py`.

| Cenário | Resultado esperado no terminal |
| --- | --- |
| Inicialização | Aviso sobre a linha inválida e 12 ocorrências válidas. |
| Cadastro, busca e filtro | `013` localizável por código e no filtro de iluminação aberta. |
| Salto de situação | Aberta para concluída é rejeitada e o estado permanece aberto. |
| Transição válida | `013` sai da fila de abertas e seu evento aparece no topo do histórico. |
| Indicadores após a transição | 13 ocorrências, 5 abertas, 5 em análise, 3 concluídas, 10 pendências e média de 6 dias. |

### Acesso e uso responsável

O menu numerado permite operação pelo teclado. Situações por extenso e mensagens curtas, independentes de cor, ajudam quem tem pouca familiaridade com tecnologia. O uso com leitores de tela e moradores reais ainda precisa ser avaliado. Os exemplos usam locais genéricos e descrições fictícias para proteger a privacidade.

O painel ilustra como consultas e histórico podem apoiar a participação comunitária. As alterações duram uma sessão. O bairro e os dados são simulados, e uma situação concluída representa apenas um registro encerrado no painel. O aprendizado foi combinar estruturas introdutórias para tornar visíveis tanto o andamento de uma ocorrência quanto o conjunto de pendências.

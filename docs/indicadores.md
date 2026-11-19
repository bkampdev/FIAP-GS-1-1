# Indicadores do Jardim Horizonte

## Dados de origem e fórmulas

O painel usa as ocorrências válidas em memória, carregadas de `data/dados.csv` e atualizadas durante a sessão. Cada ocorrência conta uma vez, na célula da sua categoria e da sua situação atual. A matriz usa uma lista de quatro linhas com três valores em cada uma, inclusive quando alguma combinação tem quantidade zero. Registros e eventos rejeitados ficam fora dos cálculos.

| Indicador | Regra de cálculo |
| --- | --- |
| Total por categoria | Soma das três situações na linha da categoria. |
| Total por situação | Soma das quatro categorias na coluna da situação. |
| Proporções | Total da categoria ou da situação dividido pelo número de ocorrências da base. |
| Pendências | Soma das ocorrências abertas e em análise. |
| Tempo médio até conclusão | Soma de `dia` do evento de conclusão menos `dia_abertura` da ocorrência, dividida pelo número de conclusões consideradas. |

O tempo usa os eventos válidos carregados de `data/historico.csv` e os registrados durante a sessão. O código liga cada evento de conclusão ao dia de abertura da ocorrência. O fluxo de situações permite uma conclusão por ocorrência. Entradas em análise e eventos de códigos fora do conjunto consultado ficam fora da média.

Com base vazia, as 12 células, os totais, as proporções e as pendências valem zero. Sem eventos de conclusão para o conjunto, o cálculo retorna `None` e o painel exibe “sem conclusões registradas”. Uma conclusão no mesmo dia da abertura tem duração de zero dias e entra na média. O painel arredonda os percentuais e a média para duas casas decimais. A soma dos percentuais exibidos pode diferir de 100% por arredondamento.

## Conferência manual

Execute `python src/sistema.py` na raiz do repositório integrado, ou use `python3` se esse for o comando disponível. Escolha **8 — Ver indicadores** antes de alterar o cadastro.

| Categoria | Aberta | Em análise | Concluída | Total | Proporção |
| --- | ---: | ---: | ---: | ---: | ---: |
| Iluminação | 1 | 1 | 1 | 3 | 25,00% |
| Acessibilidade | 1 | 1 | 1 | 3 | 25,00% |
| Limpeza | 1 | 1 | 1 | 3 | 25,00% |
| Conservação de espaços coletivos | 2 | 1 | 0 | 3 | 25,00% |
| **Total por situação** | **5** | **4** | **3** | **12** | **100,00%** |
| **Proporção por situação** | **41,67%** | **33,33%** | **25,00%** | | |

A soma das linhas é `3 + 3 + 3 + 3 = 12` e a das colunas é `5 + 4 + 3 = 12`. Cada categoria representa `3 / 12 = 25%` do cadastro. As situações representam `5 / 12`, `4 / 12` e `3 / 12`. As pendências somam `5 + 4 = 9`.

| Código | Dia de abertura | Dia de conclusão | Duração |
| --- | ---: | ---: | ---: |
| 001 | 1 | 5 | 4 dias |
| 004 | 4 | 10 | 6 dias |
| 007 | 7 | 15 | 8 dias |

O tempo médio inicial é `(4 + 6 + 8) / 3 = 6` dias.

1. Pelo menu **2**, cadastre `013` em iluminação no dia 17, com bairro Jardim Horizonte, local Praça das Amoreiras e descrição “Poste com lâmpada apagada”. Consulte novamente o painel. A linha de iluminação passa de `[1, 1, 1]` para `[2, 1, 1]`, com `4 / 13`, exibido como 30,77% do total. As outras categorias têm 23,08% cada. Esses quatro percentuais exibidos somam 100,01% por arredondamento. O cadastro passa a 13 ocorrências (6 abertas, 4 em análise e 3 concluídas), com 10 pendências e média de 6,00 dias.
2. Pelo menu **5**, atualize `013` para em análise no dia 18. A linha de iluminação passa a `[1, 2, 1]` e o painel mostra 5 abertas, 5 em análise e 3 concluídas. O total permanece 13, as pendências somam 10 e a média continua em 6,00 dias.
3. Atualize `013` para concluída no dia 19. A linha de iluminação passa a `[1, 1, 2]`. O total permanece 13, com 5 abertas (38,46%), 4 em análise (30,77%) e 4 concluídas (30,77%). As pendências caem para `5 + 4 = 9` e a média passa a `(4 + 6 + 8 + 2) / 4 = 5` dias.

## Interpretação

Na base simulada, 9 dos 12 registros (75%) ainda demandam acompanhamento. Conservação de espaços coletivos tem três pendências e nenhuma conclusão, o que dá ao grupo um caso para discutir o acompanhamento dessa categoria. O cadastro é fictício e pequeno. A média inicial usa três conclusões, por isso um caso com duração muito diferente pode alterá-la bastante. Decisões sobre demandas de um bairro real exigiriam registros locais e escuta dos moradores.

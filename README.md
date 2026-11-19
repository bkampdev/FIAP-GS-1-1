# Neighborhood Action Dashboard

Global Solution 2026.2 · CitizenTech · Grupo 2 · Ciência da Computação ON, FIAP

## Equipe

| Integrante | RM | GitHub |
| --- | --- | --- |
| Davi Coninck Cassaro | RM572772 | @daviconinck |
| Eduardo Backes Klauck | RM575889 | @BackesEdu |
| Gabriel Gonzales | RM574746 | @ItsTheContext |
| Guilherme Cardoso Bremenkamp | RM574229 | @bkampdev |
| Lorenzo Mendes Rocha | RM575361 | @Rocha0306 |

## Jardim Horizonte

No bairro fictício Jardim Horizonte, relatos sobre iluminação, acessibilidade, limpeza e conservação de espaços coletivos chegam por diferentes canais. Quem usa uma praça ou passa por uma calçada tem dificuldade para saber se o problema já foi registrado e em que etapa está. O painel reúne as ocorrências por código, categoria e situação para facilitar esse acompanhamento.

O público inclui moradores, pessoas que circulam no bairro e grupos que acompanham melhorias comunitárias. Em especial, pessoas idosas, pessoas com deficiência ou mobilidade reduzida e seus cuidadores podem se beneficiar de uma descrição clara de barreiras em espaços de uso coletivo.

## Como executar

Na raiz do repositório, com Python 3 instalado, execute:

```bash
python src/sistema.py
```

Se o executável da instalação se chamar `python3`, use `python3 src/sistema.py`. O projeto usa a biblioteca padrão do Python. Para rodar a suíte a partir da raiz:

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests
```

## Organização

| Caminho | Função |
| --- | --- |
| `src/sistema.py` | Menu no terminal e integração do fluxo. |
| `src/ocorrencias.py` | Cadastro, validação, busca, filtros e agrupamento. |
| `src/acompanhamento.py` | Fila de abertas, transições e histórico. |
| `src/indicadores.py` | Cálculo e apresentação dos indicadores. |
| `data/dados.csv` e `data/historico.csv` | Base fictícia e eventos simulados de inicialização. |
| `tests/` | Testes da aplicação. |
| `docs/` | Relatório em [Markdown](docs/relatorio.md) e [PDF](docs/relatorio.pdf), [roteiro de demonstração](docs/roteiro_video.md), [registro de apoio de IA](docs/uso_ia.md) e [link do vídeo](docs/link_video.txt). |

## Dados, estruturas e regras

Os CSVs usam UTF-8, vírgulas e cabeçalhos. Cada ocorrência exige `codigo`, `categoria`, `descricao`, `bairro`, `local`, `dia_abertura` e `situacao`. O código é único e tratado como texto para preservar zeros à esquerda. O dia de abertura é um inteiro positivo que representa o calendário fictício. Os eventos registram `codigo`, `situacao_anterior`, `nova_situacao` e `dia`. A base de demonstração prevê 12 registros válidos, uma linha rejeitada e 10 eventos válidos aplicados na inicialização.

| Estrutura | Uso e justificativa |
| --- | --- |
| Lista | Mantém a ordem de registro e permite percorrer a base para listar e filtrar. |
| Fila | Mostra os códigos das ocorrências abertas na ordem de cadastro. Novas entradas vão ao fim e um código sai quando sua ocorrência entra em análise. |
| Pilha | Guarda as alterações na ordem em que foram aplicadas. A consulta começa pelo último evento registrado e preserva todos os itens. |
| Dicionário | Representa cada ocorrência pelos nomes dos campos e indexa as ocorrências por código para consulta direta. |
| Hierarquia | Agrupa bairro → categoria → ocorrências para localizar demandas em um território. |
| Matriz | Cruza categorias nas linhas e situações nas colunas, facilitando a leitura dos totais. |

Uma ocorrência **aberta** aguarda análise. **Em análise** indica que a avaliação simulada começou. **Concluída** representa o encerramento no painel. O percurso permitido é `aberta → em análise → concluída`. A atualização exige um código existente e um dia inteiro positivo, igual ou posterior à abertura e ao último evento daquele código. Saltos, repetições e reabertura são rejeitados.

A expressão abaixo descreve a regra do filtro. Quando um critério é omitido, ele aceita qualquer valor. Com os dois critérios preenchidos, ambos devem corresponder.

```python
(categoria is None or ocorrencia["categoria"] == categoria) and (
    situacao is None or ocorrencia["situacao"] == situacao
)
```

Para um campo de texto, `not isinstance(valor, str) or not valor.strip()` identifica um valor que não é texto ou que fica vazio após retirar os espaços nas extremidades. O cadastro rejeita o campo com uma mensagem que o identifica. Depois de validar os campos, a presença do código no índice indica duplicidade.

Na atualização, `if` determina que uma ocorrência aberta pode passar para em análise. `elif` determina que uma ocorrência em análise pode ser concluída. `else` indica que uma ocorrência concluída não tem próxima situação. Quando a solicitação diverge do percurso permitido, a mensagem informa a transição inválida.

Na busca, um código ausente gera uma mensagem de registro não encontrado. Na atualização, a mudança válida altera a ocorrência e acrescenta um evento ao histórico. O terminal mantém as mudanças na memória durante a sessão e reaplica os CSVs originais ao reiniciar.

## Indicadores iniciais esperados

| Categoria | Aberta | Em análise | Concluída | Total | Proporção |
| --- | ---: | ---: | ---: | ---: | ---: |
| Iluminação | 1 | 1 | 1 | 3 | 25% |
| Acessibilidade | 1 | 1 | 1 | 3 | 25% |
| Limpeza | 1 | 1 | 1 | 3 | 25% |
| Conservação de espaços coletivos | 2 | 1 | 0 | 3 | 25% |
| **Total** | **5** | **4** | **3** | **12** | **100%** |
| **Proporção por situação** | **41,67%** | **33,33%** | **25,00%** | | |

- **Totais.** Some as células de cada linha para obter o total por categoria e de cada coluna para obter o total por situação.
- **Proporções.** Divida cada total pelo número de ocorrências válidas e multiplique por 100 para exibir o percentual. Na base inicial, 5 de 12 estão abertas, 4 de 12 em análise e 3 de 12 concluídas. Com a base vazia, as proporções são zero.
- **Pendências.** Some as abertas e as em análise. Na base inicial, `5 + 4 = 9`.
- **Tempo médio de conclusão.** Para cada ocorrência com evento de conclusão, subtraia o dia de abertura do dia desse evento. Some os intervalos e divida pela quantidade de conclusões. Na base inicial, `(4 + 6 + 8) / 3 = 6 dias`. Sem conclusões, a média fica indisponível.

No cenário simulado, conservação concentra três pendências e nenhuma conclusão, embora as categorias tenham o mesmo volume de registros. Esse recorte ajuda a orientar a conversa do grupo sobre o que deve ser examinado primeiro. A fila reflete a ordem de registro. Urgência e gravidade exigiriam informações adicionais.

## Exemplo no terminal

1. Em `2` (cadastro), informe o código `013`, a categoria `iluminação`, a descrição `Poste com lâmpada apagada`, o bairro `Jardim Horizonte`, o local `Praça das Amoreiras` e o dia `17`. A ocorrência começa aberta.
2. Em `3` (busca), informe `013`. O resultado deve identificar a ocorrência e mostrar a situação `aberta`.
3. Em `4` (filtro), selecione `iluminação` e `aberta`. Antes da atualização, o resultado esperado inclui `003` e `013`.
4. Em `5` (atualização), informe `013`, `em análise` e dia `18`. Em `7` (histórico), confira o novo evento. Ao repetir o filtro anterior, só `003` permanece.
5. Em `8` (indicadores), espere 13 ocorrências, 5 abertas, 5 em análise, 3 concluídas, 10 pendências e média de conclusão de 6 dias.

Trechos do terminal após a atualização e a abertura do painel.

```text
013 | dia 18 | aberta -> em análise
Total de ocorrências: 13
Pendências: 10 (abertas + em análise)
Tempo médio até conclusão: 6,00 dias
```

## Acessibilidade, inclusão e privacidade

As opções numeradas permitem navegar pelo teclado. Rótulos em português, situações por extenso e mensagens curtas ajudam pessoas com diferentes níveis de familiaridade com tecnologia e comunicam o resultado sem depender de cor. O vídeo deve acompanhar cada ação com narração e legendas revisadas. A avaliação com moradores reais e o uso com leitores de tela continuam pendentes.

A base e os exemplos descrevem espaços coletivos fictícios. Ao preencher os campos livres, descreva o problema e use um local genérico. Evite nomes, telefones, endereços residenciais e outros dados que permitam identificar alguém.

## Conclusões e limites

A combinação de cadastro, consulta e histórico permite acompanhar a mesma ocorrência da abertura ao encerramento simulado. A lista preserva a ordem de registro, o dicionário facilita a consulta por código e a matriz permite conferir as contagens por dois critérios.

O projeto permitiu praticar a validação antes de alterar os registros e distinguir o número de pendências do tempo médio de conclusão. Cada indicador responde a uma pergunta diferente sobre o andamento das ocorrências.

O painel é um protótipo local com dados simulados e registros temporários. O acompanhamento representa o fluxo interno do painel, sem ligação com atendimento público. A base ilustra possíveis necessidades do bairro e serve para discutir a leitura dos indicadores, que precisariam de dados representativos para orientar decisões sobre uma comunidade real.

## Vídeo e entrega

A publicação do vídeo no YouTube como **Não listado** está pendente. Após a confirmação, a URL completa será registrada nesta seção e em [docs/link_video.txt](docs/link_video.txt). O [roteiro de demonstração](docs/roteiro_video.md) orienta a gravação e o preparo do TXT para o FIAP ON.

Para atualizar o PDF, exporte o [relatório em Markdown](docs/relatorio.md) em A4, iniciando cada seção principal em uma página. Confira se o resultado tem de 4 a 8 páginas e salve em `docs/relatorio.pdf`. A geração do documento pode usar ReportLab com o ambiente de documentação. A execução do painel usa apenas a biblioteca padrão do Python.

## Referências

- [Enunciado da Global Solution no FIAP ON](https://on.fiap.com.br/mod/assign/view.php?id=683165)
- [Modelo de portfólio da coordenação](https://github.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/tree/master)

"""Indicadores do cadastro de ocorrências e do histórico da sessão."""

from ocorrencias import CATEGORIAS, SITUACOES


def calcular_indicadores(ocorrencias, historico):
    """Resume ocorrências e eventos já validados pelo cadastro e acompanhamento."""
    matriz = [[0 for _ in SITUACOES] for _ in CATEGORIAS]
    aberturas = {}

    for ocorrencia in ocorrencias:
        linha = CATEGORIAS.index(ocorrencia["categoria"])
        coluna = SITUACOES.index(ocorrencia["situacao"])
        matriz[linha][coluna] += 1
        aberturas[ocorrencia["codigo"]] = ocorrencia["dia_abertura"]

    totais_categoria = {}
    totais_situacao = {situacao: 0 for situacao in SITUACOES}
    for linha, categoria in enumerate(CATEGORIAS):
        totais_categoria[categoria] = 0
        for coluna, situacao in enumerate(SITUACOES):
            quantidade = matriz[linha][coluna]
            totais_categoria[categoria] += quantidade
            totais_situacao[situacao] += quantidade

    total = len(ocorrencias)
    proporcoes_categoria = {}
    proporcoes_situacao = {}
    for categoria, quantidade in totais_categoria.items():
        proporcoes_categoria[categoria] = quantidade / total if total else 0.0
    for situacao, quantidade in totais_situacao.items():
        proporcoes_situacao[situacao] = quantidade / total if total else 0.0

    dias_ate_conclusao = 0
    numero_conclusoes = 0
    for evento in historico:
        codigo = evento["codigo"]
        if evento["nova_situacao"] == "concluída" and codigo in aberturas:
            dias_ate_conclusao += evento["dia"] - aberturas[codigo]
            numero_conclusoes += 1

    tempo_medio = None
    if numero_conclusoes:
        tempo_medio = dias_ate_conclusao / numero_conclusoes

    return {
        "total": total,
        "matriz": matriz,
        "totais_categoria": totais_categoria,
        "totais_situacao": totais_situacao,
        "proporcoes_categoria": proporcoes_categoria,
        "proporcoes_situacao": proporcoes_situacao,
        "pendencias": totais_situacao["aberta"] + totais_situacao["em análise"],
        "tempo_medio_conclusao": tempo_medio,
    }


def _formatar_percentual(proporcao):
    return f"{proporcao:.2%}".replace(".", ",")


def formatar_indicadores(indicadores):
    """Apresenta o resumo em uma tabela textual com percentuais do cadastro."""
    linha_tabela = "{:<32} | {:>7} | {:>10} | {:>9} | {:>5} | {:>10}"
    cabecalho = linha_tabela.format("Categoria", *SITUACOES, "Total", "% do total")
    total = indicadores["total"]
    linhas = [
        f"Total de ocorrências: {total}",
        cabecalho,
        "-" * len(cabecalho),
    ]
    for linha, categoria in enumerate(CATEGORIAS):
        linhas.append(
            linha_tabela.format(
                categoria,
                *indicadores["matriz"][linha],
                indicadores["totais_categoria"][categoria],
                _formatar_percentual(indicadores["proporcoes_categoria"][categoria]),
            )
        )

    totais = [indicadores["totais_situacao"][situacao] for situacao in SITUACOES]
    percentuais = [
        _formatar_percentual(indicadores["proporcoes_situacao"][situacao])
        for situacao in SITUACOES
    ]
    percentual_total = _formatar_percentual(1.0 if total else 0.0)
    linha_totais = linha_tabela.format("Total por situação", *totais, total, percentual_total)
    linha_percentuais = linha_tabela.format("Percentual por situação", *percentuais, "", "")
    linhas.append(linha_totais)
    linhas.append(linha_percentuais.rstrip(" |"))

    tempo_medio = indicadores["tempo_medio_conclusao"]
    tempo_exibido = "sem conclusões registradas"
    if tempo_medio is not None:
        tempo_exibido = f"{tempo_medio:.2f}".replace(".", ",") + " dias"
    linhas.extend(
        [
            "",
            f"Pendências: {indicadores['pendencias']} (abertas + em análise)",
            f"Tempo médio até conclusão: {tempo_exibido}",
            "",
            "O cadastro parte de data/dados.csv e inclui as alterações da sessão.",
            "Os percentuais dividem cada quantidade pelo total desse cadastro.",
            "O histórico parte de data/historico.csv e inclui os eventos da sessão.",
            "O tempo é a média de dias da abertura ao evento de conclusão.",
        ]
    )
    return "\n".join(linhas)

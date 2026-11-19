"""Acompanha ocorrências abertas, em análise e concluídas.

Uma ocorrência aberta espera triagem na fila. Em análise indica que ela já
foi examinada, e concluída encerra o acompanhamento. O fluxo é aberta →
em análise → concluída, sem saltos, reabertura ou repetição de situação.

A fila permite consultar as demandas por ordem de chegada para orientar a
triagem. Enfileirar exige que a ocorrência esteja aberta (ainda não
examinada) e que seu código esteja fora da fila. A pilha facilita conferir
as últimas mudanças, começando pelo topo e preservando os eventos.
"""

import csv


_SITUACOES = ("aberta", "em análise", "concluída")
_CAMPOS_HISTORICO = ("codigo", "situacao_anterior", "nova_situacao", "dia")
_MENSAGEM_DIA_INVALIDO = "O dia deve ser um número inteiro positivo."


def criar_acompanhamento(cadastro):
    """Inicializa a fila com as ocorrências abertas, em ordem de registro."""
    acompanhamento = {"fila": [], "historico": []}
    for ocorrencia in cadastro["ocorrencias"]:
        enfileirar(acompanhamento, ocorrencia)
    return acompanhamento


def enfileirar(acompanhamento, ocorrencia):
    """Coloca uma ocorrência aberta no fim da fila, uma única vez."""
    codigo = ocorrencia["codigo"]
    fila = acompanhamento["fila"]
    if ocorrencia["situacao"] == "aberta" and codigo not in fila:
        fila.append(codigo)


def _buscar_ocorrencia(cadastro, codigo):
    por_codigo = cadastro["por_codigo"]
    if not isinstance(codigo, str) or codigo not in por_codigo:
        raise ValueError(f"Código desconhecido: {codigo!r}.")
    return por_codigo[codigo]


def atualizar_situacao(cadastro, acompanhamento, codigo, nova_situacao, dia):
    """Valida a mudança antes de atualizar a ocorrência, a fila e a pilha.

    Distingue código desconhecido, situação inválida, situação repetida,
    transição proibida e dia anterior à abertura ou à última mudança.
    Duas mudanças válidas da mesma ocorrência podem ocorrer no mesmo dia.
    """
    ocorrencia = _buscar_ocorrencia(cadastro, codigo)
    situacao_anterior = ocorrencia["situacao"]
    if nova_situacao not in _SITUACOES:
        raise ValueError(f"Situação inválida: {nova_situacao!r}.")
    if nova_situacao == situacao_anterior:
        raise ValueError(f"A ocorrência {codigo} já está na situação {nova_situacao!r}.")

    if situacao_anterior == "aberta":
        proxima_situacao = "em análise"
    elif situacao_anterior == "em análise":
        proxima_situacao = "concluída"
    else:
        proxima_situacao = None
    if nova_situacao != proxima_situacao:
        raise ValueError(
            f"Transição inválida de {situacao_anterior!r} para {nova_situacao!r}."
        )

    if isinstance(dia, bool) or not isinstance(dia, int) or dia < 1:
        raise ValueError(_MENSAGEM_DIA_INVALIDO)

    historico = acompanhamento["historico"]
    dia_minimo = ocorrencia["dia_abertura"]
    for evento in reversed(historico):
        if evento["codigo"] == codigo:
            dia_minimo = max(dia_minimo, evento["dia"])
            break
    if dia < dia_minimo:
        raise ValueError(
            f"Dia {dia} fora de ordem para a ocorrência {codigo}. "
            f"Informe um dia a partir de {dia_minimo}."
        )

    evento = {
        "codigo": codigo,
        "situacao_anterior": situacao_anterior,
        "nova_situacao": nova_situacao,
        "dia": dia,
    }
    ocorrencia["situacao"] = nova_situacao
    fila = acompanhamento["fila"]
    if nova_situacao == "em análise" and codigo in fila:
        fila.remove(codigo)
    historico.append(evento)
    return evento.copy()


def carregar_historico(caminho, cadastro, acompanhamento):
    """Aplica as linhas válidas do CSV e devolve os motivos das rejeições."""
    rejeicoes = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        campos = leitor.fieldnames
        if not campos or sorted(campos) != sorted(_CAMPOS_HISTORICO):
            esperado = ", ".join(_CAMPOS_HISTORICO)
            raise ValueError(f"Cabeçalho inválido no histórico. Esperado {esperado}.")
        for linha in leitor:
            try:
                if None in linha or None in linha.values():
                    raise ValueError("Quantidade de campos inválida.")
                codigo = linha["codigo"]
                ocorrencia = _buscar_ocorrencia(cadastro, codigo)
                if linha["situacao_anterior"] != ocorrencia["situacao"]:
                    raise ValueError(
                        f"Situação anterior divergente para a ocorrência {codigo}. "
                        f"Esperada {ocorrencia['situacao']!r}."
                    )
                try:
                    dia = int(linha["dia"])
                except ValueError:
                    raise ValueError(_MENSAGEM_DIA_INVALIDO) from None
                atualizar_situacao(cadastro, acompanhamento, codigo, linha["nova_situacao"], dia)
            except ValueError as erro:
                rejeicoes.append(f"Linha {leitor.line_num} do histórico: {erro}")
    return rejeicoes


def eventos_recentes(acompanhamento):
    """Consulta uma cópia dos eventos do topo para a base da pilha."""
    return [evento.copy() for evento in reversed(acompanhamento["historico"])]

"""Cadastro e consulta das ocorrências comunitárias."""

import csv


CATEGORIAS = (
    "iluminação",
    "acessibilidade",
    "limpeza",
    "conservação de espaços coletivos",
)
SITUACOES = ("aberta", "em análise", "concluída")
CAMPOS = ("codigo", "categoria", "descricao", "bairro", "local", "dia_abertura", "situacao")


def criar_cadastro():
    return {"ocorrencias": [], "por_codigo": {}}


def cadastrar(cadastro, dados):
    """Valida todos os campos antes de incluir a ocorrência na lista e no índice."""
    if not isinstance(dados, dict):
        raise ValueError("Os dados da ocorrência devem ser um dicionário.")

    ocorrencia = {}
    for campo in CAMPOS:
        valor = dados.get(campo)
        if campo == "dia_abertura":
            if isinstance(valor, str):
                texto = valor.strip()
                try:
                    valor = int(texto) if texto.isdecimal() else None
                except ValueError:
                    valor = None
            if type(valor) is not int or valor < 1:
                raise ValueError("dia_abertura deve ser um número inteiro a partir de 1.")
        else:
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"O campo {campo} é obrigatório e deve conter texto.")
            valor = valor.strip()
            if any(ord(caractere) < 32 or 127 <= ord(caractere) < 160 for caractere in valor):
                raise ValueError(f"O campo {campo} contém um caractere de controle.")
        ocorrencia[campo] = valor

    codigo = ocorrencia["codigo"]
    if codigo in cadastro["por_codigo"]:
        raise ValueError(f"Código duplicado ({codigo}).")
    if ocorrencia["categoria"] not in CATEGORIAS:
        raise ValueError(f"Categoria inválida. Use {', '.join(CATEGORIAS)}.")
    if ocorrencia["situacao"] not in SITUACOES:
        raise ValueError(f"Situação inválida. Use {', '.join(SITUACOES)}.")

    cadastro["ocorrencias"].append(ocorrencia)
    cadastro["por_codigo"][codigo] = ocorrencia
    return ocorrencia


def carregar_ocorrencias(caminho):
    """Carrega uma ocorrência por linha e informa o motivo de cada rejeição."""
    cadastro = criar_cadastro()
    rejeicoes = []
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        try:
            cabecalho = next(csv.reader([arquivo.readline()], strict=True))
        except csv.Error:
            cabecalho = []
        if cabecalho != list(CAMPOS):
            raise ValueError(
                f"Cabeçalho inválido em {caminho}. Esperado {','.join(CAMPOS)}."
            )

        for numero_linha, linha in enumerate(arquivo, start=2):
            try:
                valores = next(csv.reader([linha], strict=True))
            except csv.Error:
                rejeicoes.append(
                    f"Linha {numero_linha}: formato CSV inválido. Confira as aspas e os campos."
                )
                continue
            if len(valores) != len(CAMPOS):
                rejeicoes.append(
                    f"Linha {numero_linha}: esperados {len(CAMPOS)} campos, "
                    f"encontrados {len(valores)}."
                )
                continue
            try:
                cadastrar(cadastro, dict(zip(CAMPOS, valores)))
            except ValueError as erro:
                rejeicoes.append(f"Linha {numero_linha}: {erro}")
    return cadastro, rejeicoes


def buscar_por_codigo(cadastro, codigo):
    """Retorna a ocorrência ou None quando o código não existe."""
    if not isinstance(codigo, str):
        return None
    return cadastro["por_codigo"].get(codigo.strip())


def filtrar(cadastro, categoria=None, situacao=None):
    """Retorna as ocorrências que atendem a todos os filtros informados."""
    if isinstance(categoria, str):
        categoria = categoria.strip()
    if isinstance(situacao, str):
        situacao = situacao.strip()
    if categoria is not None and categoria not in CATEGORIAS:
        raise ValueError(f"Filtro de categoria inválido. Use {', '.join(CATEGORIAS)}.")
    if situacao is not None and situacao not in SITUACOES:
        raise ValueError(f"Filtro de situação inválido. Use {', '.join(SITUACOES)}.")

    resultado = []
    for ocorrencia in cadastro["ocorrencias"]:
        categoria_corresponde = categoria is None or ocorrencia["categoria"] == categoria
        situacao_corresponde = situacao is None or ocorrencia["situacao"] == situacao
        if categoria_corresponde and situacao_corresponde:
            resultado.append(ocorrencia)
    return resultado


def agrupar_por_bairro(cadastro):
    """Monta a hierarquia a partir das ocorrências, na ordem de cadastro."""
    bairros = {}
    for ocorrencia in cadastro["ocorrencias"]:
        bairro = ocorrencia["bairro"]
        categoria = ocorrencia["categoria"]
        if bairro not in bairros:
            bairros[bairro] = {}
        if categoria not in bairros[bairro]:
            bairros[bairro][categoria] = []
        bairros[bairro][categoria].append(ocorrencia)
    return bairros

"""Interface de terminal do Neighborhood Action Dashboard."""

from pathlib import Path

from acompanhamento import (
    atualizar_situacao,
    carregar_historico,
    criar_acompanhamento,
    enfileirar,
    eventos_recentes,
)
from indicadores import calcular_indicadores, formatar_indicadores
from ocorrencias import (
    CATEGORIAS,
    SITUACOES,
    agrupar_por_bairro,
    buscar_por_codigo,
    cadastrar,
    carregar_ocorrencias,
    filtrar,
)


PASTA_DADOS = Path(__file__).resolve().parent.parent / "data"

MENU = """
1. Listar ocorrências
2. Cadastrar ocorrência
3. Buscar por código
4. Filtrar ocorrências
5. Atualizar situação
6. Ver fila
7. Ver histórico
8. Ver indicadores
9. Ver hierarquia
0. Sair"""


def _mostrar_ocorrencias(ocorrencias):
    if not ocorrencias:
        print("Nenhuma ocorrência encontrada.")
        return

    print("Código | Categoria | Bairro | Local | Situação")
    for ocorrencia in ocorrencias:
        print(
            f"{ocorrencia['codigo']} | {ocorrencia['categoria']} | "
            f"{ocorrencia['bairro']} | {ocorrencia['local']} | {ocorrencia['situacao']}"
        )


def _cadastrar_ocorrencia(cadastro, acompanhamento):
    codigo = input("Código: ").strip()
    print("Categorias: " + ", ".join(CATEGORIAS))
    dados = {
        "codigo": codigo,
        "categoria": input("Categoria: ").strip().lower(),
        "descricao": input("Descrição: ").strip(),
        "bairro": input("Bairro: ").strip(),
        "local": input("Local genérico: ").strip(),
        "dia_abertura": input("Dia simulado de abertura: ").strip(),
        "situacao": "aberta",
    }
    ocorrencia = cadastrar(cadastro, dados)
    enfileirar(acompanhamento, ocorrencia)
    print(f"Ocorrência {ocorrencia['codigo']} cadastrada com sucesso.")


def _buscar_ocorrencia(cadastro):
    codigo = input("Código: ").strip()
    ocorrencia = buscar_por_codigo(cadastro, codigo)
    if ocorrencia is None:
        print(f"Ocorrência {codigo} não encontrada.")
        return

    _mostrar_ocorrencias([ocorrencia])
    print(f"Descrição: {ocorrencia['descricao']}")
    print(f"Dia simulado de abertura: {ocorrencia['dia_abertura']}")


def _filtrar_ocorrencias(cadastro):
    print("Deixe um campo em branco para não aplicar o filtro correspondente.")
    print("Categorias: " + ", ".join(CATEGORIAS))
    categoria = input("Categoria: ").strip().lower() or None
    print("Situações: " + ", ".join(SITUACOES))
    situacao = input("Situação: ").strip().lower() or None
    resultado = filtrar(cadastro, categoria=categoria, situacao=situacao)
    print("Ocorrências filtradas")
    _mostrar_ocorrencias(resultado)


def _atualizar_ocorrencia(cadastro, acompanhamento):
    codigo = input("Código: ").strip()
    print("Fluxo: " + " -> ".join(SITUACOES))
    situacao = input("Nova situação: ").strip().lower()
    dia_digitado = input("Dia simulado da alteração: ").strip()
    try:
        dia = int(dia_digitado)
    except ValueError:
        raise ValueError("O dia simulado da alteração deve ser um número inteiro.") from None

    evento = atualizar_situacao(cadastro, acompanhamento, codigo, situacao, dia)
    print(
        f"Ocorrência {evento['codigo']} atualizada com sucesso: "
        f"{evento['situacao_anterior']} -> {evento['nova_situacao']} (dia {evento['dia']})."
    )


def _mostrar_fila(acompanhamento):
    print("Fila de ocorrências abertas")
    fila = acompanhamento["fila"]
    if fila:
        print(" -> ".join(fila))
    else:
        print("Nenhuma ocorrência na fila.")


def _mostrar_historico(acompanhamento):
    print("Histórico de alterações (mais recentes primeiro)")
    eventos = eventos_recentes(acompanhamento)
    if not eventos:
        print("Nenhuma alteração registrada.")
        return

    for evento in eventos:
        print(
            f"{evento['codigo']} | dia {evento['dia']} | "
            f"{evento['situacao_anterior']} -> {evento['nova_situacao']}"
        )


def _mostrar_hierarquia(cadastro):
    print("Hierarquia por bairro e categoria")
    hierarquia = agrupar_por_bairro(cadastro)
    if not hierarquia:
        print("Nenhuma ocorrência encontrada.")
        return

    for bairro, categorias in hierarquia.items():
        print(f"Bairro: {bairro}")
        for categoria, ocorrencias in categorias.items():
            print(f"  Categoria: {categoria}")
            for ocorrencia in ocorrencias:
                print(f"    {ocorrencia['codigo']} | {ocorrencia['local']}")


def _executar_menu(cadastro, acompanhamento):
    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                print("Ocorrências cadastradas")
                _mostrar_ocorrencias(cadastro["ocorrencias"])
            elif opcao == "2":
                _cadastrar_ocorrencia(cadastro, acompanhamento)
            elif opcao == "3":
                _buscar_ocorrencia(cadastro)
            elif opcao == "4":
                _filtrar_ocorrencias(cadastro)
            elif opcao == "5":
                _atualizar_ocorrencia(cadastro, acompanhamento)
            elif opcao == "6":
                _mostrar_fila(acompanhamento)
            elif opcao == "7":
                _mostrar_historico(acompanhamento)
            elif opcao == "8":
                print("Indicadores da sessão")
                indicadores = calcular_indicadores(
                    cadastro["ocorrencias"], acompanhamento["historico"]
                )
                print(formatar_indicadores(indicadores))
            elif opcao == "9":
                _mostrar_hierarquia(cadastro)
            elif opcao == "0":
                return
            else:
                print("Opção inválida. Digite um número de 0 a 9.")
        except ValueError as erro:
            print(f"Entrada inválida: {erro}")


def main():
    """Carrega a base e inicia uma sessão de uso no terminal."""
    print("Neighborhood Action Dashboard")

    arquivo = "dados.csv"
    try:
        cadastro, rejeicoes = carregar_ocorrencias(PASTA_DADOS / arquivo)
        acompanhamento = criar_acompanhamento(cadastro)
        arquivo = "historico.csv"
        rejeicoes_historico = carregar_historico(PASTA_DADOS / arquivo, cadastro, acompanhamento)
    except (OSError, ValueError) as erro:
        print(f"Não foi possível iniciar o sistema: erro ao carregar {arquivo}. {erro}")
        return 1

    print(f"Base carregada: {len(cadastro['ocorrencias'])} ocorrências válidas.")
    for mensagem in rejeicoes:
        print(f"Linha rejeitada em dados.csv: {mensagem}")
    print(f"Histórico carregado: {len(acompanhamento['historico'])} alterações válidas.")
    for mensagem in rejeicoes_historico:
        print(f"Linha rejeitada em historico.csv: {mensagem}")
    print("Alterações valem somente nesta sessão. Use dados fictícios, sem dados pessoais.")

    try:
        _executar_menu(cadastro, acompanhamento)
    except EOFError:
        print("\nEntrada encerrada.")
    except KeyboardInterrupt:
        print("\nSessão interrompida pelo teclado.")

    print("Sessão encerrada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

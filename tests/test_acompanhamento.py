import csv
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from acompanhamento import (
    atualizar_situacao,
    carregar_historico,
    criar_acompanhamento,
    enfileirar,
    eventos_recentes,
)


class AcompanhamentoTest(unittest.TestCase):
    def setUp(self):
        ocorrencias = [
            {"codigo": f"{dia:03}", "situacao": "aberta", "dia_abertura": dia}
            for dia in range(1, 13)
        ]
        self.cadastro = {
            "ocorrencias": ocorrencias,
            "por_codigo": {ocorrencia["codigo"]: ocorrencia for ocorrencia in ocorrencias},
        }
        self.acompanhamento = criar_acompanhamento(self.cadastro)

    def atualizar(self, codigo, situacao, dia):
        return atualizar_situacao(self.cadastro, self.acompanhamento, codigo, situacao, dia)

    def carregar(self, caminho):
        return carregar_historico(caminho, self.cadastro, self.acompanhamento)

    def test_fila_conserva_ordem_e_ignora_ocorrencias_ja_examinadas(self):
        self.atualizar("002", "em análise", 3)
        self.atualizar("004", "em análise", 5)
        self.atualizar("004", "concluída", 10)
        fila = self.acompanhamento["fila"]
        esperado = ["001", "003", "005", "006", "007", "008", "009", "010", "011", "012"]
        self.assertEqual(fila, esperado)
        self.assertEqual(criar_acompanhamento(self.cadastro)["fila"], esperado)

        enfileirar(self.acompanhamento, self.cadastro["por_codigo"]["002"])
        enfileirar(self.acompanhamento, self.cadastro["por_codigo"]["004"])
        nova = {"codigo": "013", "situacao": "aberta", "dia_abertura": 13}
        self.cadastro["ocorrencias"].append(nova)
        self.cadastro["por_codigo"]["013"] = nova
        enfileirar(self.acompanhamento, nova)
        enfileirar(self.acompanhamento, nova)
        self.assertEqual(fila, esperado + ["013"])
        self.atualizar("013", "em análise", 15)
        self.assertEqual(fila, esperado)

    def test_atualizacao_muda_o_objeto_compartilhado_e_registra_evento(self):
        ocorrencia = self.cadastro["ocorrencias"][0]
        evento = self.atualizar("001", "em análise", 1)
        self.assertEqual(
            evento,
            {
                "codigo": "001",
                "situacao_anterior": "aberta",
                "nova_situacao": "em análise",
                "dia": 1,
            },
        )
        self.assertIs(ocorrencia, self.cadastro["por_codigo"]["001"])
        self.assertEqual(ocorrencia["situacao"], "em análise")
        self.assertEqual(self.acompanhamento["historico"], [evento])
        self.assertNotIn("001", self.acompanhamento["fila"])

    def test_atualizacoes_invalidas_preservam_cadastro_fila_e_pilha(self):
        self.atualizar("001", "em análise", 5)
        self.atualizar("002", "em análise", 3)
        self.atualizar("002", "concluída", 4)
        estado = self.cadastro, self.acompanhamento
        antes = deepcopy(estado)
        casos = (
            ("999", "em análise", 8, "Código desconhecido"),
            ("", "em análise", 8, "Código desconhecido"),
            ([], "em análise", 8, "Código desconhecido"),
            ("003", "cancelada", 8, "Situação inválida"),
            ("003", "aberta", 8, "já está na situação"),
            ("003", "concluída", 8, "Transição inválida"),
            ("001", "aberta", 8, "Transição inválida"),
            ("002", "em análise", 8, "Transição inválida"),
            ("003", "em análise", 2, "fora de ordem"),
            ("001", "concluída", 4, "fora de ordem"),
            ("003", "em análise", True, "inteiro positivo"),
            ("003", "em análise", False, "inteiro positivo"),
            ("003", "em análise", 4.5, "inteiro positivo"),
            ("003", "em análise", "4", "inteiro positivo"),
            ("003", "em análise", "amanhã", "inteiro positivo"),
            ("003", "em análise", 0, "inteiro positivo"),
            ("003", "em análise", -1, "inteiro positivo"),
        )
        for codigo, situacao, dia, mensagem in casos:
            with self.subTest(codigo=codigo, situacao=situacao, dia=dia):
                with self.assertRaisesRegex(ValueError, mensagem):
                    self.atualizar(codigo, situacao, dia)
                self.assertEqual(estado, antes)

    def test_historico_segue_ordem_das_mudancas_e_preserva_a_pilha(self):
        primeiro = self.atualizar("001", "em análise", 12)
        segundo = self.atualizar("004", "em análise", 8)
        terceiro = self.atualizar("001", "concluída", 12)
        esperados = [terceiro.copy(), segundo.copy(), primeiro.copy()]

        recentes = eventos_recentes(self.acompanhamento)
        self.assertEqual(recentes, esperados)
        recentes[0]["dia"] = 20
        recentes.pop()
        terceiro["dia"] = 25
        self.assertEqual(eventos_recentes(self.acompanhamento), esperados)
        self.assertEqual(self.acompanhamento["historico"], list(reversed(esperados)))

    def test_csv_rejeita_linhas_invalidas_e_continua_com_as_validas(self):
        dados = (
            "codigo,situacao_anterior,nova_situacao,dia\n"
            "001,em análise,concluída,3\n"
            "999,aberta,em análise,4\n"
            "001,aberta,concluída,4\n"
            "001,aberta,em análise,0\n"
            "001,aberta,em análise,1.5\n"
            "001,aberta,em análise\n"
            "001,aberta,em análise,4,extra\n"
            "001,aberta,em análise,5\n"
            "001,em análise,concluída,4\n"
            "001,em análise,concluída,6\n"
        )
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "historico.csv"
            caminho.write_text(dados, encoding="utf-8")
            rejeicoes = self.carregar(caminho)

        motivos_por_linha = (
            (2, "Situação anterior divergente"),
            (3, "Código desconhecido"),
            (4, "Transição inválida"),
            (5, "inteiro positivo"),
            (6, "inteiro positivo"),
            (7, "Quantidade de campos inválida"),
            (8, "Quantidade de campos inválida"),
            (10, "fora de ordem"),
        )
        self.assertEqual(len(rejeicoes), len(motivos_por_linha))
        for rejeicao, (numero, motivo) in zip(rejeicoes, motivos_por_linha):
            self.assertIn(f"Linha {numero} do histórico", rejeicao)
            self.assertIn(motivo, rejeicao)
        self.assertEqual(self.cadastro["por_codigo"]["001"]["situacao"], "concluída")
        self.assertEqual(self.acompanhamento["fila"][0], "002")
        self.assertEqual([evento["dia"] for evento in self.acompanhamento["historico"]], [5, 6])

    def test_csv_propaga_erros_de_arquivo_e_cabecalho(self):
        estado = self.cadastro, self.acompanhamento
        antes = deepcopy(estado)
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "historico.csv"
            with self.assertRaises(FileNotFoundError):
                self.carregar(caminho)

            caminho.write_text("codigo,situacao,dia\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Cabeçalho inválido"):
                self.carregar(caminho)

            caminho.write_text(
                'codigo,situacao_anterior,nova_situacao,dia\n"001,aberta,em análise,4\n',
                encoding="utf-8",
            )
            with self.assertRaises(csv.Error):
                self.carregar(caminho)
        self.assertEqual(estado, antes)

    def test_csv_de_exemplo_produz_os_estados_e_a_fila_do_contrato(self):
        caminho = Path(__file__).resolve().parents[1] / "data" / "historico.csv"
        self.assertEqual(self.carregar(caminho), [])
        self.assertEqual(self.acompanhamento["fila"], ["003", "006", "009", "011", "012"])
        esperadas = {
            "aberta": ["003", "006", "009", "011", "012"],
            "em análise": ["002", "005", "008", "010"],
            "concluída": ["001", "004", "007"],
        }
        for situacao, codigos in esperadas.items():
            encontrados = [
                ocorrencia["codigo"]
                for ocorrencia in self.cadastro["ocorrencias"]
                if ocorrencia["situacao"] == situacao
            ]
            self.assertEqual(encontrados, codigos)

        pares = [(evento["dia"], evento["codigo"]) for evento in self.acompanhamento["historico"]]
        self.assertEqual(
            pares,
            [
                (2, "001"), (3, "002"), (5, "001"), (5, "004"), (6, "005"),
                (8, "007"), (9, "008"), (10, "004"), (11, "010"), (15, "007"),
            ],
        )


if __name__ == "__main__":
    unittest.main()

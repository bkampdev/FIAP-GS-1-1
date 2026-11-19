import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ocorrencias import (
    CATEGORIAS,
    SITUACOES,
    agrupar_por_bairro,
    buscar_por_codigo,
    cadastrar,
    carregar_ocorrencias,
    criar_cadastro,
    filtrar,
)


class TestOcorrencias(unittest.TestCase):
    def setUp(self):
        self.cadastro = criar_cadastro()
        self.dados = {
            "codigo": "013",
            "categoria": "limpeza",
            "descricao": "Resíduos no caminho",
            "bairro": "Jardim Horizonte",
            "local": "Praça Principal",
            "dia_abertura": "13",
            "situacao": "aberta",
        }

    def test_rejeita_caracteres_de_controle_nos_campos_de_texto(self):
        casos = (("descricao", "Resíduo\nna praça"), ("local", "Praça\x1b[31m"))
        for campo, valor in casos:
            with self.subTest(campo=campo):
                with self.assertRaisesRegex(ValueError, "caractere de controle"):
                    cadastrar(self.cadastro, {**self.dados, campo: valor})
                self.assertEqual(self.cadastro, criar_cadastro())

    def test_csv_preserva_virgulas_em_campos_entre_aspas(self):
        dados = (
            "codigo,categoria,descricao,bairro,local,dia_abertura,situacao\n"
            '013,limpeza,"Folhas, papéis e resíduos",Jardim Horizonte,Praça Central,17,aberta\n'
        )
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.csv"
            caminho.write_text(dados, encoding="utf-8")
            cadastro, rejeicoes = carregar_ocorrencias(caminho)

        self.assertEqual(rejeicoes, [])
        self.assertEqual(buscar_por_codigo(cadastro, "013")["descricao"], "Folhas, papéis e resíduos")

    def test_base_ficticia_com_uma_rejeicao(self):
        caminho = Path(__file__).resolve().parents[1] / "data" / "dados.csv"
        cadastro, rejeicoes = carregar_ocorrencias(caminho)
        ocorrencias = cadastro["ocorrencias"]
        self.assertEqual([item["codigo"] for item in ocorrencias], [f"{dia:03}" for dia in range(1, 13)])
        self.assertEqual([item["dia_abertura"] for item in ocorrencias], list(range(1, 13)))
        self.assertEqual([item["situacao"] for item in ocorrencias], ["aberta"] * 12)
        bairros = agrupar_por_bairro(cadastro)
        self.assertEqual(list(bairros), ["Jardim Horizonte"])
        categorias = bairros["Jardim Horizonte"]
        self.assertEqual(tuple(categorias), CATEGORIAS)
        self.assertEqual([len(grupo) for grupo in categorias.values()], [3, 3, 3, 3])
        self.assertEqual(len(rejeicoes), 1)
        self.assertIn("Linha 14", rejeicoes[0])
        self.assertIn("categoria", rejeicoes[0])
        self.assertIsNone(buscar_por_codigo(cadastro, "099"))

    def test_cadastro_compartilha_a_ocorrencia_com_o_indice_e_a_hierarquia(self):
        ocorrencia = cadastrar(self.cadastro, self.dados)
        self.assertEqual(ocorrencia["dia_abertura"], 13)
        self.assertIs(buscar_por_codigo(self.cadastro, "013"), ocorrencia)
        self.assertIs(self.cadastro["ocorrencias"][0], ocorrencia)
        self.assertIs(agrupar_por_bairro(self.cadastro)["Jardim Horizonte"]["limpeza"][0], ocorrencia)
        ocorrencia["situacao"] = "em análise"
        self.assertEqual(filtrar(self.cadastro, situacao="em análise"), [ocorrencia])
        self.dados["local"] = "Outro local"
        self.assertEqual(ocorrencia["local"], "Praça Principal")

    def test_hierarquia_inclui_novo_bairro(self):
        primeira = cadastrar(self.cadastro, self.dados)
        segunda = cadastrar(
            self.cadastro,
            {**self.dados, "codigo": "014", "bairro": "Vila das Flores", "dia_abertura": 14},
        )
        self.assertEqual(
            agrupar_por_bairro(self.cadastro),
            {"Jardim Horizonte": {"limpeza": [primeira]}, "Vila das Flores": {"limpeza": [segunda]}},
        )

    def test_rejeita_campos_ausentes_ou_invalidos_sem_alterar_o_cadastro(self):
        for campo in self.dados:
            with self.subTest(campo_ausente=campo):
                incompleto = self.dados.copy()
                del incompleto[campo]
                with self.assertRaisesRegex(ValueError, campo):
                    cadastrar(self.cadastro, incompleto)

        invalidos = {
            "categoria": ("infraestrutura", " "),
            "situacao": ("encaminhada", " "),
            "dia_abertura": (0, -1, True, 1.5, "1.5", "1_0", "+2", "amanhã", ""),
            "descricao": (" ", 10),
        }
        for campo, valores in invalidos.items():
            for valor in valores:
                with self.subTest(campo=campo, valor=valor):
                    dados = {**self.dados, campo: valor}
                    with self.assertRaises(ValueError):
                        cadastrar(self.cadastro, dados)
        for dados in (None, []):
            with self.subTest(dados=dados), self.assertRaisesRegex(ValueError, "dicionário"):
                cadastrar(self.cadastro, dados)
        self.assertEqual(self.cadastro, criar_cadastro())

    def test_converte_texto_com_algarismos_decimais(self):
        ocorrencia = cadastrar(self.cadastro, {**self.dados, "dia_abertura": " ٢ "})
        self.assertEqual(ocorrencia["dia_abertura"], 2)

    def test_duplicata_preserva_o_registro_original(self):
        original = cadastrar(self.cadastro, self.dados)
        duplicata = {**self.dados, "codigo": " 013 ", "local": "Parque do Bairro"}
        with self.assertRaisesRegex(ValueError, "duplicado"):
            cadastrar(self.cadastro, duplicata)
        self.assertIs(buscar_por_codigo(self.cadastro, "013"), original)
        self.assertEqual(self.cadastro["ocorrencias"], [original])

    def test_filtros_individuais_combinados_e_sem_resultado(self):
        limpeza = cadastrar(self.cadastro, self.dados)
        encerrada = cadastrar(self.cadastro, {**self.dados, "codigo": "014", "situacao": SITUACOES[2]})
        iluminacao = cadastrar(self.cadastro, {**self.dados, "codigo": "015", "categoria": CATEGORIAS[0]})
        self.assertEqual(filtrar(self.cadastro), [limpeza, encerrada, iluminacao])
        self.assertEqual(filtrar(self.cadastro, categoria="limpeza"), [limpeza, encerrada])
        self.assertEqual(filtrar(self.cadastro, situacao="aberta"), [limpeza, iluminacao])
        self.assertEqual(filtrar(self.cadastro, "limpeza", "concluída"), [encerrada])
        self.assertEqual(filtrar(self.cadastro, " limpeza ", " concluída "), [encerrada])
        self.assertEqual(filtrar(self.cadastro, "iluminação", "concluída"), [])
        self.assertIsNone(buscar_por_codigo(self.cadastro, "000"))
        self.assertIsNone(buscar_por_codigo(self.cadastro, None))
        self.assertIsNone(buscar_por_codigo(self.cadastro, 13))
        for categoria in ("sinalização", "Limpeza", "", 123):
            with self.subTest(categoria=categoria), self.assertRaisesRegex(ValueError, "categoria"):
                filtrar(self.cadastro, categoria=categoria)
        for situacao in ("encaminhada", "em analise", "", 123):
            with self.subTest(situacao=situacao), self.assertRaisesRegex(ValueError, "situação"):
                filtrar(self.cadastro, situacao=situacao)

    def test_carregamento_rejeita_linhas_com_colunas_a_mais_ou_a_menos(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.csv"
            caminho.write_text(
                'codigo,categoria,descricao,bairro,local,dia_abertura,situacao\n'
                '001,limpeza,Campo faltando,Jardim Horizonte,Praça,1\n'
                '002,limpeza,Campo extra,Jardim Horizonte,Praça,2,aberta,extra\n'
                '003,limpeza,"Checar folhas, galhos e resíduos",Jardim Horizonte,Praça,3,aberta\n',
                encoding="utf-8",
            )
            cadastro, rejeicoes = carregar_ocorrencias(caminho)
        self.assertEqual(list(cadastro["por_codigo"]), ["003"])
        self.assertEqual(len(rejeicoes), 2)
        self.assertIn("Linha 2", rejeicoes[0])
        self.assertIn("encontrados 6", rejeicoes[0])
        self.assertIn("Linha 3", rejeicoes[1])
        self.assertIn("encontrados 8", rejeicoes[1])

    def test_aspas_sem_fechamento_nao_descartam_a_linha_valida_seguinte(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.csv"
            caminho.write_text(
                "codigo,categoria,descricao,bairro,local,dia_abertura,situacao\n"
                '001,limpeza,"Aspas sem fechamento\n'
                '002,limpeza,"Folhas, galhos e resíduos",Jardim Horizonte,Praça,2,aberta\n',
                encoding="utf-8",
            )
            cadastro, rejeicoes = carregar_ocorrencias(caminho)
        self.assertEqual(list(cadastro["por_codigo"]), ["002"])
        self.assertEqual(buscar_por_codigo(cadastro, "002")["descricao"], "Folhas, galhos e resíduos")
        self.assertEqual(len(rejeicoes), 1)
        self.assertIn("Linha 2", rejeicoes[0])
        self.assertIn("aspas", rejeicoes[0])

    def test_carregamento_rejeita_cabecalho_incorreto_e_propaga_arquivo_ausente(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.csv"
            with self.assertRaises(FileNotFoundError):
                carregar_ocorrencias(caminho)
            cabecalhos = ("", "codigo,descricao\n", "categoria,codigo,descricao,bairro,local,dia_abertura,situacao\n")
            for cabecalho in cabecalhos:
                with self.subTest(cabecalho=cabecalho):
                    caminho.write_text(cabecalho, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Cabeçalho inválido"):
                        carregar_ocorrencias(caminho)
            caminho.write_bytes(bytes([255]))
            with self.assertRaises(UnicodeDecodeError):
                carregar_ocorrencias(caminho)

    def test_carregamento_com_bom_crlf_duplicata_e_linha_vazia(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.csv"
            caminho.write_text(
                "codigo,categoria,descricao,bairro,local,dia_abertura,situacao\r\n"
                "001,limpeza,Folhas,Jardim Horizonte,Praça,1,aberta\r\n"
                "001,limpeza,Galhos,Jardim Horizonte,Praça,2,aberta\r\n"
                "\r\n"
                "002,limpeza,Resíduos,Jardim Horizonte,Praça,3,aberta\r\n",
                encoding="utf-8-sig",
            )
            cadastro, rejeicoes = carregar_ocorrencias(caminho)
        self.assertEqual(list(cadastro["por_codigo"]), ["001", "002"])
        self.assertEqual(buscar_por_codigo(cadastro, "001")["descricao"], "Folhas")
        self.assertEqual(len(rejeicoes), 2)
        self.assertIn("Linha 3", rejeicoes[0])
        self.assertIn("duplicado", rejeicoes[0])
        self.assertIn("Linha 4", rejeicoes[1])
        self.assertIn("encontrados 0", rejeicoes[1])

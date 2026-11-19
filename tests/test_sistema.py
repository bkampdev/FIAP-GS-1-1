import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS_INTEGRACAO = (
    "src/ocorrencias.py",
    "src/acompanhamento.py",
    "src/indicadores.py",
    "data/dados.csv",
    "data/historico.csv",
)
FILA_INICIAL = "003 -> 006 -> 009 -> 011 -> 012"
NOVO_CADASTRO = (
    "2", "013", "iluminação", "Poste com lâmpada apagada", "Jardim Horizonte",
    "Praça das Amoreiras", "17",
)


class TestSistema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        faltantes = [arquivo for arquivo in ARQUIVOS_INTEGRACAO if not (RAIZ / arquivo).is_file()]
        if faltantes:
            raise unittest.SkipTest("Depende da integração de: " + ", ".join(faltantes))

    def executar(self, *entradas):
        # Também verifica que o sistema localiza os CSVs fora da raiz do projeto.
        with TemporaryDirectory() as pasta:
            resultado = subprocess.run(
                [sys.executable, "-B", str(RAIZ / "src" / "sistema.py")],
                input="\n".join(entradas) + "\n" if entradas else "",
                encoding="utf-8",
                capture_output=True,
                cwd=pasta,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                timeout=10,
            )

        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        self.assertTrue(resultado.stdout.endswith("Sessão encerrada.\n"), resultado.stdout)
        return resultado.stdout

    def indicadores_esperados(self, matriz, pendencias, media):
        from indicadores import formatar_indicadores
        from ocorrencias import CATEGORIAS, SITUACOES

        totais_categoria = dict(zip(CATEGORIAS, map(sum, matriz)))
        totais_situacao = dict(zip(SITUACOES, map(sum, zip(*matriz))))
        total = sum(totais_categoria.values())
        return formatar_indicadores({
            "total": total,
            "matriz": matriz,
            "totais_categoria": totais_categoria,
            "totais_situacao": totais_situacao,
            "proporcoes_categoria": {nome: valor / total for nome, valor in totais_categoria.items()},
            "proporcoes_situacao": {nome: valor / total for nome, valor in totais_situacao.items()},
            "pendencias": pendencias,
            "tempo_medio_conclusao": media,
        })

    def test_carregamento_e_consultas(self):
        saida = self.executar(
            "1", "3", "001", "3", "999", "4", "iluminação", "aberta", "9", "8", "0",
        )

        self.assertIn("Base carregada: 12 ocorrências válidas.", saida)
        self.assertEqual(saida.count("Linha rejeitada em dados.csv:"), 1)
        self.assertIn("Histórico carregado: 10 alterações válidas.", saida)
        self.assertNotIn("Linha rejeitada em historico.csv:", saida)

        listagem = saida.split("Ocorrências cadastradas\n", 1)[1].split("\n1. Listar", 1)[0]
        self.assertEqual(
            [linha.split(" | ")[0] for linha in listagem.splitlines()[1:]],
            [f"{numero:03}" for numero in range(1, 13)],
        )
        consulta = saida.split("Escolha uma opção: Código: ", 1)[1].split("\n1. Listar", 1)[0]
        self.assertRegex(consulta, r"(?m)^001 \| iluminação \| .+ \| concluída$")
        self.assertIn("Descrição: ", consulta)
        self.assertIn("Dia simulado de abertura: 1", consulta)
        self.assertIn("Ocorrência 999 não encontrada.", saida)

        filtro = saida.split("Ocorrências filtradas\n", 1)[1].split("\n1. Listar", 1)[0]
        self.assertEqual(len(filtro.splitlines()), 2)
        self.assertRegex(filtro, r"(?m)^003 \| iluminação \| .+ \| aberta$")

        hierarquia = saida.split("Hierarquia por bairro e categoria\n", 1)[1]
        hierarquia = hierarquia.split("\n1. Listar", 1)[0]
        self.assertIn("Bairro: Jardim Horizonte", hierarquia)
        self.assertIn("  Categoria: iluminação", hierarquia)
        self.assertIn("    003 | ", hierarquia)
        esperado = self.indicadores_esperados([[1, 1, 1], [1, 1, 1], [1, 1, 1], [2, 1, 0]], 9, 6.0)
        self.assertIn("Indicadores da sessão\n" + esperado, saida)

    def test_cadastro_e_mudancas_atualizam_fila_historico_e_indicadores(self):
        saida = self.executar(
            *NOVO_CADASTRO, "6", "8",
            "5", "013", "em análise", "18", "6", "7", "8",
            "5", "013", "concluída", "19", "3", "013", "7", "8", "0",
        )

        self.assertIn("Ocorrência 013 cadastrada com sucesso.", saida)
        self.assertIn(f"Fila de ocorrências abertas\n{FILA_INICIAL} -> 013\n", saida)
        self.assertIn(f"Fila de ocorrências abertas\n{FILA_INICIAL}\n", saida)
        self.assertIn("Ocorrência 013 atualizada com sucesso: aberta -> em análise (dia 18).", saida)
        self.assertIn(
            "Histórico de alterações (mais recentes primeiro)\n013 | dia 18 | aberta -> em análise\n",
            saida,
        )
        self.assertIn(
            "Histórico de alterações (mais recentes primeiro)\n"
            "013 | dia 19 | em análise -> concluída\n013 | dia 18 | aberta -> em análise\n",
            saida,
        )
        self.assertIn("013 | iluminação | Jardim Horizonte | Praça das Amoreiras | concluída", saida)
        secoes = saida.split("Indicadores da sessão\n")[1:]
        esperados = [
            self.indicadores_esperados([[2, 1, 1], [1, 1, 1], [1, 1, 1], [2, 1, 0]], 10, 6.0),
            self.indicadores_esperados([[1, 2, 1], [1, 1, 1], [1, 1, 1], [2, 1, 0]], 10, 6.0),
            self.indicadores_esperados([[1, 1, 2], [1, 1, 1], [1, 1, 1], [2, 1, 0]], 9, 5.0),
        ]
        self.assertEqual(len(secoes), len(esperados))
        for secao, esperado in zip(secoes, esperados):
            self.assertTrue(secao.startswith(esperado + "\n"), secao)

    def test_rejeicoes_preservam_fila_historico_e_indicadores(self):
        consulta_estado = ("6", "7", "8", "0")
        inicial = self.executar(*consulta_estado)
        apos_rejeicoes = self.executar(
            "-1", "",
            "2", "001", *NOVO_CADASTRO[2:],
            "2", "013", "inexistente", *NOVO_CADASTRO[3:],
            *NOVO_CADASTRO[:3], "", *NOVO_CADASTRO[4:],
            *NOVO_CADASTRO[:-1], "0",
            *NOVO_CADASTRO[:-1], "hoje",
            "4", "inexistente", "",
            "5", "999", "em análise", "18",
            "5", "003", "concluída", "18",
            "5", "003", "em análise", "2",
            "5", "003", "em análise", "amanhã",
            "5", "003", "inexistente", "18",
            "5", "002", "em análise", "18",
            "5", "001", "aberta", "18",
            *consulta_estado,
        )

        self.assertEqual(apos_rejeicoes.count("Opção inválida. Digite um número de 0 a 9."), 2)
        self.assertEqual(apos_rejeicoes.count("Entrada inválida:"), 13)
        self.assertNotIn("com sucesso", apos_rejeicoes)
        marcador = "Fila de ocorrências abertas\n"
        self.assertIn(marcador + FILA_INICIAL, inicial)
        self.assertIn(marcador, apos_rejeicoes)
        self.assertEqual(inicial.split(marcador, 1)[1], apos_rejeicoes.split(marcador, 1)[1])

    def test_filtros_opcionais_e_sem_resultados(self):
        saida = self.executar(
            "4", "iluminação", "", "4", "", "aberta", "4", "conservação de espaços coletivos",
            "concluída", "0",
        )
        secoes = saida.split("Ocorrências filtradas\n")[1:]
        categoria, situacao, sem_resultados = [secao.split("\n1. Listar", 1)[0] for secao in secoes]
        self.assertEqual([linha[:3] for linha in categoria.splitlines()[1:]], ["001", "002", "003"])
        self.assertEqual(
            [linha[:3] for linha in situacao.splitlines()[1:]], FILA_INICIAL.split(" -> ")
        )
        self.assertIn("Nenhuma ocorrência encontrada.", sem_resultados)

    def test_eof_no_menu_e_durante_formularios(self):
        for entradas in ((), ("2", "013", "iluminação"), ("5", "003", "em análise")):
            with self.subTest(entradas=entradas):
                saida = self.executar(*entradas)
                self.assertIn("Entrada encerrada.", saida)
                self.assertNotIn("com sucesso", saida)

    def test_csv_ausente_informa_problema_e_impede_inicio(self):
        from sistema import main

        with TemporaryDirectory() as pasta, patch("sistema.PASTA_DADOS", Path(pasta)):
            saida = StringIO()
            with redirect_stdout(saida):
                codigo = main()

        self.assertEqual(codigo, 1)
        self.assertIn("Não foi possível iniciar o sistema: erro ao carregar dados.csv.", saida.getvalue())
        self.assertNotIn("Escolha uma opção", saida.getvalue())


if __name__ == "__main__":
    unittest.main()

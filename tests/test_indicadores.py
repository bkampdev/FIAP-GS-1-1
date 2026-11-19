import unittest

from indicadores import calcular_indicadores
from ocorrencias import CATEGORIAS, SITUACOES


class TestIndicadores(unittest.TestCase):
    def test_base_vazia_conserva_as_categorias_e_situacoes_com_zero(self):
        indicadores = calcular_indicadores([], [])
        self.assertEqual(indicadores["total"], 0)
        self.assertEqual(indicadores["matriz"], [[0, 0, 0] for _ in CATEGORIAS])
        self.assertEqual(indicadores["proporcoes_categoria"], dict.fromkeys(CATEGORIAS, 0.0))
        self.assertEqual(indicadores["proporcoes_situacao"], dict.fromkeys(SITUACOES, 0.0))
        self.assertEqual(indicadores["pendencias"], 0)
        self.assertIsNone(indicadores["tempo_medio_conclusao"])

    def test_media_considera_so_os_eventos_de_conclusao_do_cadastro(self):
        ocorrencias = [
            {"codigo": "001", "situacao": "concluída", "categoria": "iluminação", "dia_abertura": 1},
            {"codigo": "002", "situacao": "em análise", "categoria": "limpeza", "dia_abertura": 2},
        ]
        historico = [
            {"codigo": "001", "nova_situacao": "em análise", "dia": 2},
            {"codigo": "001", "nova_situacao": "concluída", "dia": 5},
            {"codigo": "999", "nova_situacao": "concluída", "dia": 100},
        ]
        indicadores = calcular_indicadores(ocorrencias, historico)
        self.assertEqual(indicadores["matriz"], [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 0, 0]])
        self.assertEqual(indicadores["proporcoes_categoria"]["limpeza"], 0.5)
        self.assertEqual(indicadores["pendencias"], 1)
        self.assertEqual(indicadores["tempo_medio_conclusao"], 4.0)

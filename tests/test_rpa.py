"""Cenarios de teste: SUCESSO, DECISAO e FALHA.
Executar: python -m unittest discover -s tests -v
"""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import requests

from src import coleta, db
from src.regras import classificar
from src.validacao import validar_ponto, validar_previsao


class TestDecisao(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(classificar(2, 1, "medio")[0], "NORMAL")

    def test_atencao_por_acumulado(self):
        self.assertEqual(classificar(16, 5, "medio")[0], "ATENCAO")

    def test_alerta_por_intensidade(self):
        self.assertEqual(classificar(10, 21, "medio")[0], "ALERTA")

    def test_critico(self):
        self.assertEqual(classificar(55, 10, "medio")[0], "CRITICO")

    def test_risco_alto_dispara_mais_cedo(self):
        self.assertEqual(classificar(13, 2, "medio")[0], "NORMAL")
        self.assertEqual(classificar(13, 2, "alto")[0], "ATENCAO")

    def test_sensor_eleva_um_nivel(self):
        self.assertEqual(classificar(16, 5, "medio", nivel_agua_cm=20)[0], "ALERTA")


class TestValidacao(unittest.TestCase):
    def test_ponto_valido(self):
        p = validar_ponto({"id": "X", "bairro": "A", "latitude": "-23.5",
                           "longitude": "-46.6", "risco": "Alto"})
        self.assertEqual(p["risco"], "alto")

    def test_ponto_invalido(self):
        with self.assertRaises(ValueError):
            validar_ponto({"id": "X", "bairro": "A", "latitude": "abc",
                           "longitude": "-46.6", "risco": "alto"})
        with self.assertRaises(ValueError):
            validar_ponto({"id": "X", "bairro": "A", "latitude": "99",
                           "longitude": "-46.6", "risco": "alto"})

    def test_previsao_com_nulos_e_valida(self):
        chuva, _ = validar_previsao({"hourly": {"precipitation": [1.0, None, 2.0]}})
        self.assertEqual(chuva, [1.0, 2.0])

    def test_previsao_invalida(self):
        for ruim in ({}, {"hourly": {"precipitation": [None, None]}},
                     {"hourly": {"precipitation": [-5]}},
                     {"hourly": {"precipitation": [9999]}}):
            with self.assertRaises(ValueError):
                validar_previsao(ruim)


class TestDeduplicacao(unittest.TestCase):
    def setUp(self):
        self.conn = db.conectar(":memory:")
        self.a = {"ponto_id": "P01", "bairro": "X", "nivel": "ALERTA", "acumulado_mm": 30,
                  "max_mm_h": 20, "prob_max": 90, "justificativa": "t", "notificado": 1}

    def test_mesmo_alerta_na_janela_e_duplicado(self):
        self.assertFalse(db.ja_alertado(self.conn, "P01", "ALERTA"))
        db.salvar_alerta(self.conn, self.a)
        self.assertTrue(db.ja_alertado(self.conn, "P01", "ALERTA"))

    def test_nivel_diferente_nao_e_duplicado(self):
        db.salvar_alerta(self.conn, self.a)
        self.assertFalse(db.ja_alertado(self.conn, "P01", "CRITICO"))

    def test_fora_da_janela_nao_e_duplicado(self):
        db.salvar_alerta(self.conn, self.a)
        futuro = datetime.now(timezone.utc) + timedelta(hours=4)
        self.assertFalse(db.ja_alertado(self.conn, "P01", "ALERTA", agora=futuro))


class TestFalhaDeApi(unittest.TestCase):
    @patch("src.coleta.requests.get", side_effect=requests.ConnectionError("fora do ar"))
    def test_retry_e_erro_final(self, mock_get):
        pausas = []
        with self.assertRaises(coleta.ErroColeta):
            coleta.buscar_previsao(-23.5, -46.6, dormir=pausas.append)
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(pausas, [1.0, 2.0])   # backoff exponencial

    @patch("src.coleta.requests.get")
    def test_sucesso_apos_uma_falha(self, mock_get):
        ok = Mock()
        ok.json.return_value = {"hourly": {"precipitation": [1]}}
        ok.raise_for_status.return_value = None
        mock_get.side_effect = [requests.Timeout("lento"), ok]
        r = coleta.buscar_previsao(-23.5, -46.6, dormir=lambda s: None)
        self.assertIn("hourly", r)


if __name__ == "__main__":
    unittest.main()

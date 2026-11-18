"""Dados ficticios para DEMONSTRACAO (video/testes), usados com --simular.

Garante que a banca veja todos os niveis e uma falha tratada, mesmo num
dia sem chuva. Os dados simulados NAO sao reais e o log avisa isso.
"""
from src.coleta import ErroColeta

CHUVA_SIMULADA = {
    "P01": [20.0, 25.0, 15.0],   # 60 mm -> CRITICO
    "P02": [8.0, 12.0, 10.0],    # 30 mm, ponto de risco alto -> ALERTA
    "P03": [4.0, 6.0, 7.0],      # 17 mm -> ATENCAO (+ sensor eleva)
    "P04": [0.0, 0.0, 0.2],      # NORMAL
}


def previsao_simulada(ponto_id: str) -> dict:
    if ponto_id not in CHUVA_SIMULADA:
        raise ErroColeta("falha simulada de API (demonstracao de excecao)")
    return {"hourly": {"precipitation": CHUVA_SIMULADA[ponto_id],
                       "precipitation_probability": [90, 95, 80]}}

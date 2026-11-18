"""Consulta a API Open-Meteo com retry e backoff exponencial."""
import time

import requests

from src import config
from src.logger import get_logger

log = get_logger()


class ErroColeta(Exception):
    """Falha definitiva ao consultar a API depois de todas as tentativas."""


def buscar_previsao(lat: float, lon: float, dormir=time.sleep) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation,precipitation_probability",
        "forecast_hours": config.HORAS_JANELA,
        "timezone": "America/Sao_Paulo",
    }
    ultimo = None
    for tentativa in range(1, config.MAX_TENTATIVAS + 1):
        try:
            r = requests.get(config.API_URL, params=params, timeout=config.TIMEOUT_S)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            ultimo = e
            log.warning("API falhou (tentativa %d/%d): %s",
                        tentativa, config.MAX_TENTATIVAS, type(e).__name__)
            if tentativa < config.MAX_TENTATIVAS:
                dormir(config.BACKOFF_BASE_S * 2 ** (tentativa - 1))
    raise ErroColeta(f"API indisponivel apos {config.MAX_TENTATIVAS} tentativas") from ultimo

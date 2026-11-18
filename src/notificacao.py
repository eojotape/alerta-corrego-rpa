"""Envio de notificacao via Telegram. Sem credenciais, opera em modo simulado."""
import requests

from src import config
from src.logger import get_logger

log = get_logger()
ICONES = {"ATENCAO": "🟡", "ALERTA": "🟠", "CRITICO": "🔴"}


def montar_mensagem(a: dict) -> str:
    return (f"{ICONES.get(a['nivel'], '')} ALERTA CÓRREGO - {a['nivel']}\n"
            f"Local: {a['bairro']}\n"
            f"Chuva prevista (3h): {a['acumulado_mm']:.1f} mm "
            f"(pico {a['max_mm_h']:.1f} mm/h)\n"
            f"Evite o local e acompanhe a Defesa Civil.")


def enviar(a: dict) -> bool:
    """Retorna True se a notificacao foi entregue (ou simulada). Nunca levanta."""
    texto = montar_mensagem(a)
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        log.info("[SIMULADO] notificacao (sem credenciais Telegram): %s / %s",
                 a["bairro"], a["nivel"])
        return True
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": texto},
                          timeout=config.TIMEOUT_S)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        # Nao registrar a URL: ela contem o token.
        log.error("Falha ao enviar Telegram para %s: %s", a["bairro"], type(e).__name__)
        return False

"""Configuracoes centrais do robo. Limiares ajustaveis em um unico lugar."""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
LOGS = BASE / "logs"

PONTOS_CSV = DATA / "pontos_monitorados.csv"
SENSOR_JSON = DATA / "sensor_nivel.json"      # leitura do robo do Maker Lab
DB_PATH = DATA / "alertas.db"
ALERTAS_JSON = DATA / "alertas.json"          # saida consumida pelo MVP
LOG_FILE = LOGS / "rpa.log"


def _carregar_env():
    """Le o arquivo .env (se existir) sem depender de bibliotecas externas."""
    env = BASE / ".env"
    if not env.exists():
        return
    for linha in env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip())


_carregar_env()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Coleta (Open-Meteo, gratuita e sem chave) ---
API_URL = "https://api.open-meteo.com/v1/forecast"
HORAS_JANELA = 3            # previsao das proximas 3 horas
TIMEOUT_S = 15
MAX_TENTATIVAS = 3
BACKOFF_BASE_S = 1.0        # 1s, 2s, 4s...

# --- Regras de negocio (mm de chuva) ---
# Acumulado nas proximas 3h OU intensidade maxima em 1h.
LIMIARES = {
    "CRITICO": {"acumulado": 50.0, "intensidade": 30.0},
    "ALERTA":  {"acumulado": 30.0, "intensidade": 20.0},
    "ATENCAO": {"acumulado": 15.0, "intensidade": 10.0},
}
# Pontos de risco historico alto disparam mais cedo.
FATOR_RISCO = {"alto": 0.8, "medio": 1.0, "baixo": 1.2}
SENSOR_ELEVA_ACIMA_CM = 15.0   # nivel de agua que sobe o alerta um degrau
LIMITE_MM_H_VALIDO = 300.0     # acima disso a leitura e considerada invalida

# --- Deduplicacao ---
JANELA_DEDUP_MIN = 180

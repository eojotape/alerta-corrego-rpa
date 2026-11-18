"""Logs de auditoria: data/hora, nivel e mensagem. Nunca registrar tokens."""
import logging
from logging.handlers import RotatingFileHandler

from src import config


def get_logger(nome="rpa"):
    log = logging.getLogger(nome)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s",
                            "%Y-%m-%d %H:%M:%S")
    config.LOGS.mkdir(exist_ok=True)
    arq = RotatingFileHandler(config.LOG_FILE, maxBytes=500_000,
                              backupCount=3, encoding="utf-8")
    arq.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    log.addHandler(arq)
    log.addHandler(console)
    return log

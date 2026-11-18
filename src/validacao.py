"""Validacao de entradas: CSV de pontos e resposta da API."""
import csv
from pathlib import Path

from src import config

RISCOS = set(config.FATOR_RISCO)


def validar_ponto(linha: dict) -> dict:
    """Valida uma linha do CSV. Levanta ValueError se for invalida."""
    try:
        ponto = {
            "id": (linha.get("id") or "").strip(),
            "bairro": (linha.get("bairro") or "").strip(),
            "latitude": float(linha.get("latitude")),
            "longitude": float(linha.get("longitude")),
            "risco": (linha.get("risco") or "").strip().lower(),
        }
    except (TypeError, ValueError):
        raise ValueError("latitude/longitude ausente ou nao numerica")
    if not ponto["id"] or not ponto["bairro"]:
        raise ValueError("id ou bairro vazio")
    if not -90 <= ponto["latitude"] <= 90 or not -180 <= ponto["longitude"] <= 180:
        raise ValueError("coordenadas fora da faixa")
    if ponto["risco"] not in RISCOS:
        raise ValueError(f"risco invalido: {ponto['risco']!r}")
    return ponto


def carregar_pontos(caminho: Path = None):
    """Retorna (pontos_validos, erros). FileNotFoundError sobe para o orquestrador."""
    caminho = caminho or config.PONTOS_CSV
    validos, erros, vistos = [], [], set()
    with open(caminho, newline="", encoding="utf-8") as f:
        for n, linha in enumerate(csv.DictReader(f), start=2):
            try:
                p = validar_ponto(linha)
                if p["id"] in vistos:
                    raise ValueError(f"id duplicado: {p['id']}")
                vistos.add(p["id"])
                validos.append(p)
            except ValueError as e:
                erros.append(f"linha {n}: {e}")
    return validos, erros


def validar_previsao(dados: dict):
    """Extrai (lista_mm, prob_max) da resposta. Levanta ValueError se invalida."""
    try:
        horario = dados["hourly"]
        chuva = horario["precipitation"]
    except (KeyError, TypeError):
        raise ValueError("resposta sem campo hourly.precipitation")
    if not isinstance(chuva, list):
        raise ValueError("precipitation nao e uma lista")
    valores = [v for v in chuva if v is not None]
    if not valores:
        raise ValueError("todas as leituras de chuva sao nulas")
    for v in valores:
        if not isinstance(v, (int, float)) or v < 0 or v > config.LIMITE_MM_H_VALIDO:
            raise ValueError(f"leitura de chuva invalida: {v!r}")
    probs = [p for p in horario.get("precipitation_probability", []) if p is not None]
    return [float(v) for v in valores], (max(probs) if probs else None)

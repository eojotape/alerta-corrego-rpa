"""Regra de decisao: classifica o risco de enchente de um ponto."""
from src import config

ORDEM = ["NORMAL", "ATENCAO", "ALERTA", "CRITICO"]


def classificar(acumulado_mm, max_mm_h, risco, nivel_agua_cm=None):
    """Retorna (nivel, justificativa).

    Dispara o nivel mais alto cujo limiar (ajustado pelo fator de risco do
    ponto) for atingido por acumulado OU intensidade. Se o sensor de nivel
    de agua indicar elevacao, sobe um degrau.
    """
    fator = config.FATOR_RISCO[risco]
    nivel = "NORMAL"
    for nome in ("CRITICO", "ALERTA", "ATENCAO"):
        lim = config.LIMIARES[nome]
        if acumulado_mm >= lim["acumulado"] * fator or max_mm_h >= lim["intensidade"] * fator:
            nivel = nome
            break
    just = f"acumulado={acumulado_mm:.1f}mm, pico={max_mm_h:.1f}mm/h, risco={risco}"
    if nivel_agua_cm is not None and nivel_agua_cm >= config.SENSOR_ELEVA_ACIMA_CM:
        idx = min(ORDEM.index(nivel) + 1, len(ORDEM) - 1)
        if ORDEM[idx] != nivel:
            nivel = ORDEM[idx]
            just += f", sensor={nivel_agua_cm:.0f}cm (elevou um nivel)"
    return nivel, just

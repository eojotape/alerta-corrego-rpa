"""Orquestrador do robo de alertas de enchente (CitizenTech).

Uso:
    python -m src.main --once              # uma execucao com dados reais
    python -m src.main --once --simular    # demonstracao com chuva ficticia
    python -m src.main --loop --intervalo 60   # roda a cada 60 minutos
"""
import argparse
import json
import sys
import time

from src import config, db, notificacao
from src.coleta import ErroColeta, buscar_previsao
from src.logger import get_logger
from src.regras import classificar
from src.simulacao import previsao_simulada
from src.validacao import carregar_pontos, validar_previsao

log = get_logger()


def ler_sensor() -> dict:
    """Le o nivel de agua do robo do Maker Lab. Tolerante a ausencia/corrupcao."""
    if not config.SENSOR_JSON.exists():
        log.info("Sem arquivo de sensor; seguindo apenas com a previsao.")
        return {}
    try:
        dados = json.loads(config.SENSOR_JSON.read_text(encoding="utf-8"))
        return {l["ponto_id"]: float(l["nivel_cm"]) for l in dados["leituras"]}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        log.error("Arquivo de sensor corrompido; ignorando leituras.")
        return {}


def processar_ponto(ponto, sensor, simular, conn, resumo):
    try:
        bruto = previsao_simulada(ponto["id"]) if simular else \
            buscar_previsao(ponto["latitude"], ponto["longitude"])
        chuva, prob = validar_previsao(bruto)
    except (ErroColeta, ValueError) as e:
        resumo["falhas"] += 1
        log.error("Ponto %s (%s) falhou: %s", ponto["id"], ponto["bairro"], e)
        return

    acumulado, pico = sum(chuva), max(chuva)
    nivel, just = classificar(acumulado, pico, ponto["risco"], sensor.get(ponto["id"]))
    resumo["processados"] += 1
    log.info("Ponto %s %s -> %s (%s)", ponto["id"], ponto["bairro"], nivel, just)

    if nivel == "NORMAL":
        return
    if db.ja_alertado(conn, ponto["id"], nivel):
        resumo["duplicados"] += 1
        log.info("Alerta duplicado ignorado: %s / %s", ponto["bairro"], nivel)
        return

    alerta = {"ponto_id": ponto["id"], "bairro": ponto["bairro"], "nivel": nivel,
              "acumulado_mm": acumulado, "max_mm_h": pico, "prob_max": prob,
              "justificativa": just, "notificado": 0}
    alerta["notificado"] = int(notificacao.enviar(alerta))
    db.salvar_alerta(conn, alerta)
    resumo["alertas"] += 1
    log.info("ALERTA GERADO: %s / %s (notificado=%s)", ponto["bairro"], nivel,
             bool(alerta["notificado"]))


def executar(simular=False) -> dict:
    resumo = {"processados": 0, "alertas": 0, "duplicados": 0, "falhas": 0}
    log.info("=== Inicio da execucao (simulacao=%s) ===", simular)
    if simular:
        log.warning("MODO SIMULACAO: chuva ficticia apenas para demonstracao.")
    try:
        pontos, erros = carregar_pontos()
    except FileNotFoundError:
        log.critical("Arquivo de pontos nao encontrado: %s", config.PONTOS_CSV)
        resumo["erro_fatal"] = True
        return resumo
    for e in erros:
        log.warning("Ponto invalido ignorado (%s)", e)
    if not pontos:
        log.critical("Nenhum ponto valido para monitorar.")
        resumo["erro_fatal"] = True
        return resumo

    sensor = ler_sensor()
    conn = db.conectar()
    try:
        for ponto in pontos:                       # estrutura de repeticao
            processar_ponto(ponto, sensor, simular, conn, resumo)
        # Saida consumida pelo MVP (arquivo estruturado)
        config.ALERTAS_JSON.write_text(
            json.dumps({"gerado_em": db.agora_iso(), "alertas": db.listar_alertas(conn, limite=200)},
                       ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        conn.close()
    log.info("=== Fim: %d processados, %d alertas, %d duplicados, %d falhas ===",
             resumo["processados"], resumo["alertas"], resumo["duplicados"], resumo["falhas"])
    return resumo


def main():
    ap = argparse.ArgumentParser(description="RPA de alertas de enchente")
    ap.add_argument("--once", action="store_true", help="executa uma vez")
    ap.add_argument("--loop", action="store_true", help="executa continuamente")
    ap.add_argument("--intervalo", type=int, default=60, help="minutos entre execucoes")
    ap.add_argument("--simular", action="store_true", help="usa chuva ficticia (demo)")
    args = ap.parse_args()
    if args.loop:
        while True:
            executar(args.simular)
            time.sleep(args.intervalo * 60)
    resumo = executar(args.simular)
    sys.exit(1 if resumo.get("erro_fatal") else 0)


if __name__ == "__main__":
    main()

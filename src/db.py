"""Persistencia em SQLite e deduplicacao de alertas."""
import sqlite3
from datetime import datetime, timedelta, timezone

from src import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ponto_id TEXT NOT NULL,
    bairro TEXT NOT NULL,
    nivel TEXT NOT NULL,
    acumulado_mm REAL,
    max_mm_h REAL,
    prob_max REAL,
    justificativa TEXT,
    notificado INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_alertas_ponto ON alertas(ponto_id, nivel, criado_em);
"""


def agora_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conectar(caminho=None):
    caminho = caminho or config.DB_PATH
    if str(caminho) != ":memory:":
        config.DATA.mkdir(exist_ok=True)
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def ja_alertado(conn, ponto_id, nivel, agora=None, janela_min=None):
    """True se ja existe alerta igual (ponto + nivel) dentro da janela."""
    janela_min = janela_min or config.JANELA_DEDUP_MIN
    agora = agora or datetime.now(timezone.utc)
    limite = (agora - timedelta(minutes=janela_min)).isoformat(timespec="seconds")
    linha = conn.execute(
        "SELECT 1 FROM alertas WHERE ponto_id=? AND nivel=? AND criado_em>=? LIMIT 1",
        (ponto_id, nivel, limite)).fetchone()
    return linha is not None


def salvar_alerta(conn, a: dict) -> int:
    cur = conn.execute(
        """INSERT INTO alertas (ponto_id, bairro, nivel, acumulado_mm, max_mm_h,
           prob_max, justificativa, notificado, criado_em)
           VALUES (:ponto_id, :bairro, :nivel, :acumulado_mm, :max_mm_h,
                   :prob_max, :justificativa, :notificado, :criado_em)""",
        {**a, "criado_em": a.get("criado_em") or agora_iso()})
    conn.commit()
    return cur.lastrowid


def listar_alertas(conn, nivel=None, limite=100):
    sql, args = "SELECT * FROM alertas", []
    if nivel:
        sql += " WHERE nivel=?"
        args.append(nivel.upper())
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(limite)
    return [dict(r) for r in conn.execute(sql, args).fetchall()]

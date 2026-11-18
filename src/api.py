"""API somente leitura para o MVP consumir os alertas.

Uso: python -m src.api   ->   http://localhost:8000/alertas
Usa apenas a biblioteca padrao (sem dependencias para instalar).
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from src import db


class Handler(BaseHTTPRequestHandler):
    def _enviar(self, codigo, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            return self._enviar(200, {"status": "ok"})
        if url.path == "/alertas":
            nivel = parse_qs(url.query).get("nivel", [None])[0]
            conn = db.conectar()
            try:
                return self._enviar(200, {"alertas": db.listar_alertas(conn, nivel)})
            finally:
                conn.close()
        self._enviar(404, {"erro": "rota nao encontrada"})

    def log_message(self, *a):  # silencia o log padrao
        pass


if __name__ == "__main__":
    print("API em http://localhost:8000/alertas  (Ctrl+C para parar)")
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

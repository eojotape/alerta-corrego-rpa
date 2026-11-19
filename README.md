# Alerta Córrego - RPA de Alertas de Enchente (CitizenTech)

Robo (Python) que monitora a previsao de chuva em pontos criticos de Sao Paulo,
classifica o risco de enchente, evita alertas repetidos e notifica a populacao.
Disciplina: Robotic Process Automation - Global Solution 2026.2 (FIAP, 4ES).

## Integrantes
| Nome completo | RM |
|---|---|
| João Pedro de Albuquerque Oliveira | 551579 |
| Pedro Augusto Carneiro Barone Bomfim | 99781 |
| Matheus Augusto Santos Rego | 551466 |

## Problema e beneficio ao cidadao
Hoje alguem precisa consultar a previsao de varios pontos e decidir manualmente
quando avisar. O robo faz isso a cada hora, sem intervencao humana, e entrega os
alertas ao MVP (arquivo JSON, banco SQLite e API /alertas).

## Arquitetura
CSV de pontos -> validacao -> loop por ponto -> API Open-Meteo (retry/backoff)
-> validacao da resposta -> regra de decisao (+ sensor do Maker Lab)
-> deduplicacao -> SQLite + JSON + Telegram -> API /alertas -> MVP.
Diagrama BPMN (`docs/fluxo_enchentes.bpmn`), PDD (`docs/PDD.md`) e relatorio tecnico em PDF (`docs/Relatorio_Tecnico_RPA.pdf`).
Para refazer o PDF apos trocar prints/links: `pip install reportlab pillow` e `python docs/gerar_relatorio.py`.

## Como executar (Python 3.14, Windows/PowerShell)
```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main --once --simular   # demonstracao (chuva ficticia)
python -m src.main --once             # dados reais (Open-Meteo)
python -m src.api                     # http://localhost:8000/alertas
python -m unittest discover -s tests -v
```
Telegram (opcional): copie `.env.example` para `.env` e preencha. Sem isso, o robo
roda em modo simulado de notificacao.

## Regras de negocio
Limiares em `src/config.py` (acumulado 3h OU pico em 1h): Atencao 15 mm / 10 mm/h,
Alerta 30 / 20, Critico 50 / 30. Pontos de risco alto usam 80% dos limiares.
Nivel de agua >= 15 cm (sensor do robo) sobe o alerta um degrau.

## Estrutura
`src/` codigo | `data/` entradas e saidas | `docs/` BPMN e PDD | `assets/` evidencias |
`logs/` amostras de log | `tests/` cenarios de sucesso, decisao e falha

## Seguranca e LGPD
Nenhum dado pessoal e coletado. Credenciais ficam em `.env` (ignorado pelo Git).
Logs nao registram tokens.

## Links
- Video: ([Clique aqui](https://youtu.be/yWX_ZH5nX98))

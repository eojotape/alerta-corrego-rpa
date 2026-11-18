# PDD - Process Definition Document
**Processo:** Monitoramento de chuva e emissão de alertas de enchente
**Projeto:** Alerta Córrego (CitizenTech) - Global Solution 2026.2, FIAP 4ES
**Disciplina:** Robotic Process Automation
**Diagrama:** `docs/fluxo_enchentes.bpmn` (abrir em https://demo.bpmn.io)

## 1. Integrantes
| Nome completo | RM |
|---|---|
| João Pedro de Albuquerque Oliveira | 551579 |
| Pedro Augusto Carneiro Barone Bomfim | 99781 |
| Matheus Augusto Santos Rego | 551466 |

## 2. Contexto e objetivo
**Processo manual (AS-IS):** uma pessoa consulta a previsão de chuva de cada ponto crítico da cidade, interpreta
os números, decide se há risco, confere se já avisou, e comunica a população.
**Processo automatizado (TO-BE):** o robô executa o ciclo completo a cada hora, sem intervenção humana, e entrega
os alertas ao MVP.
**Benefício:** alerta mais rápido, padronizado e auditável; menos ruído por mensagens repetidas.

## 3. Escopo
- **Dentro:** leitura de pontos, consulta de previsão, validação, classificação de risco, deduplicação,
  notificação, persistência, exportação ao MVP e logs.
- **Fora:** envio a assinantes em massa, cadastro de usuários, interface do MVP, previsão própria de chuva.

## 4. Sistemas e atores
| Item | Descrição |
|---|---|
| Robô (Python 3.14) | Executa o processo (`src/main.py`) |
| API Open-Meteo | Fonte externa de previsão de chuva (sem chave) |
| Robô do Maker Lab | Fonte opcional do nível de água (`data/sensor_nivel.json`) |
| Telegram Bot API | Canal de notificação (modo simulado sem credenciais) |
| SQLite / JSON / API /alertas | Saídas consumidas pelo MVP |
| Operador / Defesa Civil | Recebe os alertas e decide a ação em campo |

## 5. Entradas e saídas
| Entradas | Saídas |
|---|---|
| `data/pontos_monitorados.csv` (id, bairro, latitude, longitude, risco) | Alertas em `data/alertas.db` (SQLite) |
| Previsão horária de chuva (Open-Meteo) | `data/alertas.json` |
| `data/sensor_nivel.json` (opcional) | API `GET /alertas` e `GET /health` |
| Parâmetros em `src/config.py` | Notificação Telegram; logs em `logs/rpa.log` |

## 6. Descrição passo a passo
| # | Passo | Regra / detalhe | Exceção |
|---|---|---|---|
| 1 | Gatilho | Execução a cada 60 min (`--loop`) ou manual (`--once`) | - |
| 2 | Ler CSV de pontos | Valida coordenadas, risco, ids únicos | CSV ausente: CRITICAL e encerra (saída 1). Linha inválida: ignora e avisa |
| 3 | Ler sensor | Mapeia ponto -> nível de água (cm) | Ausente ou corrompido: registra e segue sem sensor |
| 4 | **Para cada ponto** | Estrutura de repetição sobre a lista | Falha de um ponto não interrompe o lote |
| 5 | Consultar API | Previsão das próximas 3 h; 3 tentativas, espera 1 s e 2 s | Esgotou: registra falha do ponto |
| 6 | Validar resposta | Rejeita nulos totais, negativos e > 300 mm/h | Inválida: registra falha do ponto |
| 7 | Classificar risco | Ver seção 7 | - |
| 8 | Nível NORMAL? | Sim: encerra o ponto sem alerta | - |
| 9 | Alerta duplicado? | Mesmo ponto + nível nos últimos 180 min | Sim: ignora e registra |
| 10 | Notificar | Telegram (ou modo simulado) | Falha: registra e grava `notificado = 0` |
| 11 | Gravar alerta | Insere no SQLite | - |
| 12 | Exportar | Gera `alertas.json` com os últimos 200 alertas | - |
| 13 | Resumo | Loga processados, alertas, duplicados e falhas | - |

## 7. Regras de negócio
Considera o **acumulado de chuva em 3 h** OU o **pico em 1 h**; vale o maior nível atingido.

| Nível | Acumulado 3 h | Pico 1 h |
|---|---|---|
| Atenção | >= 15 mm | >= 10 mm/h |
| Alerta | >= 30 mm | >= 20 mm/h |
| Crítico | >= 50 mm | >= 30 mm/h |

- **Fator de risco do ponto:** alto = 0,8 / médio = 1,0 / baixo = 1,2 (multiplica os limiares).
- **Sensor:** nível de água >= 15 cm sobe o alerta um degrau.
- **Deduplicação:** janela de 180 minutos; nível maior gera novo alerta.
- Limiares são parâmetros iniciais em `src/config.py`, a calibrar com histórico de alagamentos.

## 8. Logs e auditoria
Formato: `data/hora | nível | mensagem`. Registra início/fim, cada ponto com justificativa numérica, alertas,
duplicados, falhas e erros. Arquivo `logs/rpa.log` com rotação. **Sem dados pessoais e sem tokens.**

## 9. Segurança e LGPD
Nenhum dado pessoal é tratado. Credenciais do Telegram em `.env` (fora do Git). Entradas sempre validadas;
SQL parametrizado.

## 10. Testes
15 testes automatizados (`python -m unittest discover -s tests -v`) cobrindo decisão, validação,
deduplicação e falha de API, mais cenários manuais (CSV ausente, linha inválida, sensor corrompido).

## 11. Premissas e limitações
- A previsão do Open-Meteo é um modelo, não uma medição; o sensor ajuda a confirmar.
- Coordenadas dos pontos são aproximadas.
- Os limiares precisam de calibração com dados históricos reais.
- O envio a assinantes exigiria consentimento e base legal (LGPD).

## 12. Glossário
**RPA:** automação robótica de processos. **Backoff:** espera crescente entre tentativas. **Deduplicação:**
evitar registros ou avisos repetidos. **MVP:** produto mínimo viável.

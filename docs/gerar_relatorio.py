"""Gera o Relatorio Tecnico em PDF (itens 01 a 12 do slide 49, na ordem).

Uso (na raiz do projeto, com o .venv ativo):
    pip install reportlab pillow
    python docs/gerar_relatorio.py

Edite as constantes abaixo (links, nome do produto) e rode de novo sempre que
trocar um print em assets/ -- o PDF e refeito em segundos.
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

# ============ EDITE AQUI ============
PRODUTO = "Alerta Córrego"
GITHUB_URL = ""      # ex.: "https://github.com/usuario/rpa-alerta-enchentes"
VIDEO_URL = ""       # ex.: "https://youtu.be/xxxxxxxx"
INTEGRANTES = [
    ("João Pedro de Albuquerque Oliveira", "551579"),
    ("Pedro Augusto Carneiro Barone Bomfim", "99781"),
    ("Matheus Augusto Santos Rego", "551466"),
]
# =====================================

BASE = Path(__file__).resolve().parent.parent
ASSETS = BASE / "assets"
SAIDA = BASE / "docs" / "Relatorio_Tecnico_RPA.pdf"

AZUL, ROSA, CINZA = colors.HexColor("#1d4ed8"), colors.HexColor("#c2185b"), colors.HexColor("#374151")
ss = getSampleStyleSheet()
T = ParagraphStyle("T", parent=ss["Title"], fontSize=22, leading=26, textColor=ROSA, alignment=0)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=11.5, leading=15, textColor=CINZA)
H = ParagraphStyle("H", parent=ss["Heading1"], fontSize=15, leading=19, textColor=AZUL, spaceBefore=14, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11.5, leading=15, textColor=CINZA, spaceBefore=8, spaceAfter=3)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14.2, spaceAfter=5)
CAP = ParagraphStyle("CAP", parent=B, fontSize=8.5, leading=11, textColor=colors.HexColor("#6b7280"), spaceAfter=9)
CELL = ParagraphStyle("CELL", parent=B, fontSize=9, leading=12, spaceAfter=0)
CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=14, bulletIndent=3, spaceAfter=2)


def ph(txt):
    return f'<font color="#b91c1c"><b>[PREENCHER: {txt}]</b></font>'


def p(t, st=B): return Paragraph(t, st)
def bullets(items): return [Paragraph(i, BUL, bulletText="\u2022") for i in items]


def tabela(cab, linhas, larg):
    dados = [[Paragraph(c, CELLB) for c in cab]] + [[Paragraph(str(c), CELL) for c in l] for l in linhas]
    t = Table(dados, colWidths=[w * cm for w in larg], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def figura(nome, legenda, largura=17.0, alt_max=None):
    arq = ASSETS / nome
    if not arq.exists():
        return [p(ph(f"arquivo assets/{nome} nao encontrado"))]
    iw, ih = ImageReader(str(arq)).getSize()
    w = largura * cm; h = w * ih / iw
    if alt_max and h > alt_max * cm:
        h = alt_max * cm; w = h * iw / ih
    return [KeepTogether([Image(str(arq), w, h), Paragraph(legenda, CAP)])]


def item(n, titulo): return p(f"{n:02d}. {titulo}", H)


def rodape(c, doc):
    w, h = c._pagesize
    c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#6b7280"))
    c.drawString(1.8 * cm, 1.1 * cm, "FIAP - Global Solution 2026.2 - CitizenTech - Robotic Process Automation")
    c.drawRightString(w - 1.8 * cm, 1.1 * cm, f"Página {doc.page}")


S = []
# ---------- capa + item 01 ----------
S += [p("Relatório Técnico", T), p("Robotic Process Automation - Do Processo Manual à Automação Inteligente", SUB),
      p(f"Global Solution 2026.2 - Engenharia de Software, 4º ano (4ES)<br/>Produto: <b>{PRODUTO}</b>", SUB), Spacer(1, 6)]

S += [item(1, "Nome completo e RM de todos os integrantes"),
      tabela(["Nome completo", "RM"], [[n, r] for n, r in INTEGRANTES], [13.4, 3.6])]

# ---------- 02 ----------
S += [item(2, "Identificação da CitizenTech e problema resolvido"),
      p(f"<b>Produto:</b> {PRODUTO}. Solução CitizenTech de monitoramento e alerta de enchentes em áreas urbanas, "
        "na qual o robô descrito neste relatório é o componente de <b>Automação</b>."),
      p("<b>Cidadão e território:</b> moradores, motoristas, comerciantes e agentes de defesa civil de pontos "
        "historicamente sujeitos a alagamento na cidade de São Paulo (Vale do Anhangabaú, Marginal Tietê, "
        "Av. Aricanduva, Marginal Pinheiros e Parque Dom Pedro II)."),
      p("<b>Problema operacional resolvido:</b> para avisar a população, alguém precisaria consultar manualmente a "
        "previsão de chuva de vários pontos, interpretar os valores, decidir se há risco, evitar avisar duas vezes "
        "a mesma coisa e comunicar o resultado. Esse trabalho repetitivo, feito às pressas, atrasa o alerta justamente "
        "quando o tempo de reação importa. O robô executa todo esse ciclo sozinho, a cada hora."),
      p("<b>Evidência do problema:</b> segundo levantamento da Agência Pública com dados da Defesa Civil do Estado de São Paulo, "
        "as chuvas de verão (1º de dezembro a 31 de março) causaram <b>197 mortes</b> em cinco anos (2022 a 2026), por enchentes, "
        "deslizamentos e raios, o que equivale a cerca de <b>uma morte a cada três dias</b>. Só nas oito primeiras semanas da operação "
        "de 2025/2026 foram 12 vítimas, entre elas um casal de idosos arrastado por uma enxurrada para um córrego no Capão Redondo, "
        "Zona Sul da capital. A reportagem também registra que, segundo a Prefeitura de São Paulo, enchentes e alagamentos "
        "<b>aumentaram 47%</b> na capital em 2025 em relação ao ano anterior, que 124 pessoas estavam desalojadas pelas chuvas na "
        "capital em 21/01/2026 e que, em fevereiro de 2025, moradores do Jardim Pantanal ficaram sete dias ilhados. Especialistas "
        "ouvidos apontam que, nas áreas de enxurrada, o tempo entre o aviso e o evento é muito curto e que investir em tecnologia de "
        "monitoramento e alerta é essencial. É esse o espaço do Alerta Córrego."),
      p("<b>Fonte:</b> CUSTÓDIO, Rafael. Chuvas em SP: uma pessoa morre a cada 3 dias, entre dezembro e março, há 5 anos. "
        "Agência Pública, 21 jan. 2026 (dados da Defesa Civil do Estado de SP e da Prefeitura de SP).<br/>"
        '<link href="https://apublica.org/2026/01/chuvas-em-sp-uma-pessoa-morre-a-cada-3-dias-no-verao-ha-5-anos/" color="blue">'
        "https://apublica.org/2026/01/chuvas-em-sp-uma-pessoa-morre-a-cada-3-dias-no-verao-ha-5-anos/</link>. Acesso em: nov. 2026.", CAP),
      p("<b>ODS conectados:</b> <b>ODS 11</b> (Cidades e comunidades sustentáveis), pela meta de reduzir mortes e "
        "perdas econômicas causadas por desastres relacionados à água; e <b>ODS 13</b> (Ação contra a mudança global "
        "do clima), pela meta de reforçar a resiliência e a capacidade de adaptação a riscos climáticos.")]

# ---------- 03 ----------
S += [item(3, "Objetivo da automação e benefício para o cidadão"),
      p("<b>Objetivo:</b> automatizar de ponta a ponta o monitoramento da previsão de chuva, a classificação do risco "
        "de enchente e a emissão de alertas, com o mínimo de intervenção humana, registrando tudo para auditoria e "
        "entregando os resultados de forma estruturada ao MVP."),
      p("<b>Benefícios ao cidadão:</b>")] + bullets([
        "Aviso mais rápido: o ciclo roda a cada hora, sem depender de uma pessoa lembrar de consultar.",
        "Aviso mais confiável: regras explícitas e configuráveis, aplicadas sempre da mesma forma.",
        "Menos ruído: a deduplicação impede mensagens repetidas para o mesmo ponto e nível.",
        "Alerta mais preciso: o nível de água medido pelo robô do Maker Lab pode elevar o alerta antes da chuva prevista se confirmar."]) 

# ---------- 04 ----------
S += [item(4, "Descrição do processo e desenho do fluxo"),
      p("O robô é um processo agendado, em Python, que executa o ciclo abaixo. O desenho completo em BPMN está na "
        "Figura 1 (página seguinte); o arquivo editável (<i>docs/fluxo_enchentes.bpmn</i>) e o PDD "
        "(<i>docs/PDD.md</i>) estão no repositório."),
      tabela(["#", "Etapa", "O que acontece"], [
          ["1", "Gatilho", "Execução agendada (a cada 60 minutos) ou manual: <i>python -m src.main --once</i>."],
          ["2", "Entrada", "Lê o CSV de pontos monitorados e valida cada linha (coordenadas, risco, ids únicos)."],
          ["3", "Sensor", "Lê o nível de água do robô do Maker Lab (opcional; falha não interrompe o fluxo)."],
          ["4", "Loop", "Para cada ponto: consulta a API Open-Meteo, com retry e backoff exponencial."],
          ["5", "Validação", "Descarta nulos, valores negativos ou fora da faixa; ponto inválido não derruba o lote."],
          ["6", "Decisão", "Classifica em Normal, Atenção, Alerta ou Crítico (acumulado 3h ou pico em 1h)."],
          ["7", "Deduplicação", "Ignora alerta igual (ponto + nível) emitido dentro da janela de 180 minutos."],
          ["8", "Saída", "Notifica (Telegram), grava no SQLite e exporta o JSON consumido pelo MVP."],
          ["9", "Auditoria", "Registra data/hora, itens processados, sucessos, falhas e erros em log."]], [0.8, 2.8, 13.4]),
      Spacer(1, 6), p("<b>Cobertura das etapas obrigatórias:</b>", H2),
      tabela(["Etapa", "Onde está no projeto"], [
          ["01 Mapeamento do processo", "BPMN (docs/fluxo_enchentes.bpmn), PDD (docs/PDD.md) e Figura 1"],
          ["02 Desenvolvimento da automação", "Python versionado no GitHub (pasta src/)"],
          ["03 Lógica de negócio e lote", "Condições em src/regras.py e loop por ponto em src/main.py"],
          ["04 Exceções e resiliência", "Item 07 deste relatório (retry, ponto inválido, CSV ausente, sensor corrompido)"],
          ["05 Logs e auditoria", "Item 08 (src/logger.py e pasta logs/)"],
          ["06 Integração com o MVP", "Item 09 (API /alertas, SQLite e alertas.json)"],
          ["07 Testes e validação", "Item 10 (15 testes automatizados e cenários de falha)"],
          ["08 Documentação e publicação", "README.md, docs/ e repositório público"]], [5.4, 11.6]),
      NextPageTemplate("land"), PageBreak()]
S += figura("00_fluxo_bpmn.png", "Figura 1 - Fluxo BPMN do robô: gatilho, leitura de entradas, loop por ponto "
            "(API, validação, decisão, deduplicação, notificação e gravação), tratamento de falhas e saída ao MVP.",
            largura=26.2, alt_max=15.2)
S += [NextPageTemplate("port"), PageBreak()]

# ---------- 05 ----------
S += [item(5, "Tecnologias utilizadas e justificativa"),
      tabela(["Tecnologia", "Uso", "Justificativa"], [
          ["Python 3.14", "Linguagem do robô", "Permite versionar no GitHub, testar e rodar em qualquer máquina; atende ao requisito de Python versionado."],
          ["requests", "Chamadas HTTP (API e Telegram)", "Biblioteca consolidada, com tratamento claro de timeout e erros HTTP."],
          ["API Open-Meteo", "Previsão de chuva por hora e probabilidade", "Gratuita, sem chave de acesso (nada sensível no código) e com dados por coordenada."],
          ["SQLite", "Histórico de alertas e deduplicação", "Banco embarcado, sem servidor, reproduzível por qualquer avaliador."],
          ["JSON", "Saída para o MVP e leitura do sensor", "Formato estruturado e simples de consumir."],
          ["http.server (biblioteca padrão)", "API somente leitura /alertas e /health", "Zero dependências extras e sem risco de incompatibilidade de pacotes."],
          ["Telegram Bot API", "Notificação ao cidadão/operador", "Gratuita; em modo simulado quando não há credenciais."],
          ["logging (RotatingFileHandler)", "Logs de auditoria", "Registro com data/hora e rotação de arquivo."],
          ["unittest", "Testes automatizados", "Biblioteca padrão; cobre sucesso, decisão e falha."],
          ["BPMN 2.0 / PDD", "Documentação do processo", "Notação padrão de mercado; arquivo editável no bpmn.io."]], [3.6, 4.6, 8.8]),
      Spacer(1, 4), p("<b>Por que só Python?</b> O enunciado permite Python e/ou Power Automate. Optamos por Python porque o "
        "fluxo tem laços, regras de negócio e integração por arquivo e API, tudo versionável e testável em código, "
        "sem depender de licenças ou de um servidor de automação.")]

# ---------- 06 ----------
S += [item(6, "Regras de negócio, decisões e processamento"),
      p("A regra de decisão fica em <i>src/regras.py</i> e os limiares em <i>src/config.py</i>, para serem ajustados "
        "sem alterar o código. O robô considera a chuva prevista para as <b>próximas 3 horas</b> e dispara o nível mais "
        "alto cujo limiar for atingido por <b>acúmulo OU intensidade</b>."),
      tabela(["Nível", "Acumulado em 3h", "Pico em 1h"], [
          ["Atenção", "&gt;= 15 mm", "&gt;= 10 mm/h"], ["Alerta", "&gt;= 30 mm", "&gt;= 20 mm/h"],
          ["Crítico", "&gt;= 50 mm", "&gt;= 30 mm/h"], ["Normal", "abaixo de todos os limiares", "-"]], [4.0, 6.5, 6.5]),
      Spacer(1, 5)] + bullets([
        "<b>Fator de risco do ponto:</b> pontos de risco histórico alto usam 80% dos limiares (disparam mais cedo); "
        "médio usa 100%; baixo usa 120%.",
        "<b>Sensor do Maker Lab:</b> nível de água &gt;= 15 cm sobe o alerta em um degrau (Atenção para Alerta, e assim por diante).",
        "<b>Deduplicação:</b> não repete alerta com o mesmo ponto e nível dentro de 180 minutos. Um nível maior é um novo alerta.",
        "<b>Validação de entrada:</b> coordenadas fora da faixa, risco desconhecido, id repetido, chuva nula, negativa ou acima de 300 mm/h são rejeitados.",
        "<b>Processamento em lote:</b> estrutura de repetição percorre todos os pontos; a falha de um não interrompe os demais."]) + [
      p("<b>Justificativa dos limiares:</b> os valores acima são <b>parâmetros iniciais</b>, definidos pela equipe como ponto de "
        "partida, e <b>devem ser calibrados</b> com dados históricos de chuva e de ocorrências de alagamento de cada ponto "
        "(por exemplo, registros do CGE e da Defesa Civil). Por isso ficam centralizados em <i>src/config.py</i>, podendo ser "
        "ajustados sem alterar a lógica do robô.")]

# ---------- 07 ----------
S += [item(7, "Tratamento de exceções e recuperação"),
      p("Nenhuma falha é silenciosa: cada uma é registrada em log com nível adequado e o robô continua sempre que possível."),
      tabela(["Cenário de falha", "Tratamento", "Evidência"], [
          ["API Open-Meteo fora do ar ou lenta", "3 tentativas com espera de 1s e 2s (backoff exponencial); depois marca o ponto como falho e segue o lote.", "Testes (item 10, Figura 12)"],
          ["Resposta inválida (nula, negativa, absurda)", "Validação rejeita o ponto; registra o erro; lote continua.", "Testes (item 10)"],
          ["Arquivo CSV de pontos ausente", "Registra CRITICAL, encerra com código de saída 1, sem travar.", "Figura 2"],
          ["Linha inválida no CSV", "Ignora a linha, registra WARNING com o número da linha e processa o restante.", "Figura 3"],
          ["Arquivo do sensor corrompido ou ausente", "Registra o erro e segue só com a previsão.", "Figura 4"],
          ["Falha no envio da notificação", "Registra o erro (sem expor o token), grava o alerta com notificado = 0.", "Código (src/notificacao.py)"],
          ["Alerta repetido", "Detectado pela deduplicação e ignorado com registro.", "Figura 7"]], [4.6, 8.4, 4.0])]
S += figura("09_falha_csv_ausente.png", "Figura 2 - CSV ausente: erro crítico registrado e código de saída 1.", 15.5, 4)
S += figura("10_falha_ponto_invalido.png", "Figura 3 - Linha inválida no CSV ignorada (aviso na linha 7); os demais pontos seguem.", 16.5, 7)
S += figura("11_falha_sensor_corrompido.png", "Figura 4 - Sensor corrompido: erro registrado e processamento mantido com a previsão.", 16.5, 6)

# ---------- 08 ----------
S += [item(8, "Logs e evidências de auditoria"),
      p("Cada linha do log traz <b>data e hora, nível (INFO, WARNING, ERROR, CRITICAL) e a mensagem</b>. São registrados o "
        "início e o fim da execução, cada ponto processado com sua classificação e justificativa numérica, alertas gerados, "
        "duplicados ignorados e falhas. Os logs são gravados em <i>logs/rpa.log</i> (com rotação) e exibidos no console; "
        "uma amostra está em <i>logs/amostra_execucao.txt</i>. Tokens e dados pessoais nunca são registrados."),
      ]
S += figura("02_execucao_real.png", "Figura 5 - Execução real com a API Open-Meteo: 5 pontos processados, 0 alertas, 0 falhas.", 16.5, 5)
S += figura("03_simulacao_1_alertas.png", "Figura 6 - Execução em modo simulação: 3 alertas gerados (Crítico, Alerta, Alerta elevado pelo sensor) e 1 falha de API tratada. A simulação usa chuva fictícia, apenas para demonstração, e o log avisa isso.", 16.5, 8)
S += figura("04_simulacao_2_duplicados.png", "Figura 7 - Segunda execução: os 3 alertas já emitidos são ignorados como duplicados.", 16.5, 8)

# ---------- 09 ----------
S += [item(9, "Descrição e evidências da integração com o MVP"),
      p("O resultado do robô é disponibilizado aos demais componentes da CitizenTech (MVP) por canais estruturados, sem prints colados:"),
      ] + bullets([
        "<b>API de leitura (src/api.py):</b> <i>GET /alertas</i> (aceita <i>?nivel=CRITICO</i>) e <i>GET /health</i>, em JSON.",
        "<b>Banco SQLite (data/alertas.db):</b> tabela <i>alertas</i> com ponto, nível, chuva, justificativa, status da notificação e data.",
        "<b>Arquivo estruturado (data/alertas.json):</b> exportado ao final de cada execução.",
        "<b>Integração com o Maker Lab (entrada):</b> o robô físico grava o nível de água em <i>data/sensor_nivel.json</i> e o RPA usa essa leitura como segunda fonte para elevar o alerta."])
S += figura("05_api_health.png", "Figura 8 - Endpoint /health respondendo.", 8, 3)
S += figura("06_api_alertas.png", "Figura 9 - Endpoint /alertas retornando os alertas gerados.", 17, 5)
S += figura("07_api_filtro_critico.png", "Figura 10 - Endpoint /alertas?nivel=CRITICO filtrando por nível.", 17, 4)
S += figura("08_alertas_json.png", "Figura 11 - Arquivo alertas.json exportado para o MVP.", 12, 12)

# ---------- 10 ----------
S += [item(10, "Testes realizados (sucesso, decisão e falha)"),
      p("Foram implementados <b>15 testes automatizados</b> (<i>tests/test_rpa.py</i>), todos aprovados, além de cenários "
        "executados manualmente. Comando: <i>python -m unittest discover -s tests -v</i>."),
      tabela(["Tipo", "O que foi testado", "Resultado"], [
          ["Sucesso", "Execução real com a API (Figura 5); execução simulada gerando 3 alertas (Figura 6); resposta com nulos aceita; retry que se recupera após uma falha.", "Aprovado"],
          ["Decisão", "6 testes de classificação: Normal, Atenção por acúmulo, Alerta por intensidade, Crítico, risco alto disparando mais cedo, sensor elevando um nível; 3 testes de deduplicação (mesma janela, nível diferente, fora da janela).", "Aprovado"],
          ["Falha", "API fora do ar com 3 tentativas e backoff de 1s e 2s; ponto inválido; resposta inválida (vazia, nula, negativa, absurda); CSV ausente; linha inválida; sensor corrompido; ponto P05 com falha simulada de API.", "Aprovado"]], [2.2, 12.6, 2.2])]
S += figura("01_testes_unitarios.png", "Figura 12 - Saída dos 15 testes automatizados: 'Ran 15 tests ... OK'.", 16.5, 9)

# ---------- 11 ----------
S += [item(11, "Considerações de segurança e LGPD"),
      ] + bullets([
        "<b>Sem dados pessoais:</b> o robô trabalha com coordenadas de pontos públicos e previsão do tempo. Nenhum dado de cidadão é coletado, armazenado ou registrado em log.",
        "<b>Credenciais fora do código:</b> token e chat do Telegram ficam em arquivo <i>.env</i>, listado no <i>.gitignore</i>; o repositório traz apenas <i>.env.example</i> vazio.",
        "<b>Sem chaves no repositório:</b> a API Open-Meteo não exige chave; logs não registram URLs com token.",
        "<b>Minimização:</b> o banco guarda somente o necessário ao alerta (local, nível, medidas e data).",
        "<b>Entradas não confiáveis:</b> toda entrada (CSV, sensor e resposta de API) é validada antes do uso; consultas SQL usam parâmetros, evitando injeção.",
        "<b>Evolução:</b> se o produto passar a enviar alertas a assinantes, será necessário coletar consentimento, informar a finalidade e proteger os contatos (base legal da LGPD), o que está fora do escopo deste MVP."])

# ---------- 12 ----------
S += [item(12, "Link do repositório GitHub e link do vídeo demonstrativo"),
      p("<b>Repositório GitHub (público):</b> " + (f'<link href="{GITHUB_URL}" color="blue">{GITHUB_URL}</link>' if GITHUB_URL else ph("link do repositorio"))),
      p("<b>Vídeo demonstrativo (até 3 minutos):</b> " + (f'<link href="{VIDEO_URL}" color="blue">{VIDEO_URL}</link>' if VIDEO_URL else ph("link do video no YouTube (nao listado)")))]


def construir():
    pw, ph_ = A4
    doc = BaseDocTemplate(str(SAIDA), pagesize=A4, title="Relatório Técnico - RPA Alertas de Enchente",
                          author="; ".join(n for n, _ in INTEGRANTES))
    m = 1.8 * cm
    doc.addPageTemplates([
        PageTemplate("port", [Frame(m, 1.8 * cm, pw - 2 * m, ph_ - 3.4 * cm, id="p")], onPage=rodape, pagesize=A4),
        PageTemplate("land", [Frame(m, 1.8 * cm, ph_ - 2 * m, pw - 3.4 * cm, id="l")], onPage=rodape, pagesize=landscape(A4))])
    doc.build(S)
    print("PDF gerado em", SAIDA)


if __name__ == "__main__":
    construir()

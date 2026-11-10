"""Gera a apresentação 16:9 e editável do seminário Kibana.

Requisito: Python 3 com python-pptx (py -3 -m pip install python-pptx).
Uso na raiz do projeto: py -3 slides/gerar_slides.py

As capturas em slides/assets/ são as únicas imagens do PPTX. O exemplo de JSON
ilustra o formato do coletor. Os dados das capturas pertencem à sessão registrada.
"""
from datetime import datetime
from math import cos, radians, sin
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA / "seminario_kibana.pptx"
CAPTURAS = PASTA / "assets"
LARGURA, ALTURA = 13.333, 7.5

FUNDO, SUPERFICIE, RELEVO = "0B1020", "131D30", "1B2940"
AZUL, AZUL_CLARO, VERMELHO, ALERTA = "3B82F6", "8AB9FF", "F04A5D", "FF91A0"
TEXTO, SUAVE, LINHA = "F4F7FB", "A9B7CE", "334768"
GRADE, AZUL_ESCURO, VERMELHO_ESCURO = "182540", "152A50", "2A1929"
TITULO, CORPO, CODIGO = "Bahnschrift", "Calibri", "Consolas"

TEMA_CORES = {
    "dk1": FUNDO, "lt1": TEXTO, "dk2": SUPERFICIE, "lt2": SUAVE,
    "accent1": AZUL, "accent2": VERMELHO, "accent3": AZUL_CLARO,
    "accent4": ALERTA, "accent5": "8A92D3", "accent6": LINHA,
    "hlink": AZUL_CLARO, "folHlink": ALERTA,
}


FONTES = {
    1: "https://www.elastic.co/docs/get-started/the-stack",
    2: "https://www.elastic.co/docs/manage-data/data-store/index-basics",
    3: "https://www.elastic.co/docs/explore-analyze/find-and-organize/data-views",
    4: "https://www.elastic.co/docs/explore-analyze/discover",
    5: "https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql",
    6: "https://www.elastic.co/docs/explore-analyze/visualize/lens",
    7: "https://www.elastic.co/docs/explore-analyze/dashboards",
    9: "https://www.elastic.co/docs/reference/logstash/how-logstash-works",
    10: "https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-file",
    11: "https://www.elastic.co/docs/reference/logstash/plugins/plugins-codecs-json_lines",
    12: "https://www.elastic.co/docs/reference/logstash/plugins/plugins-outputs-elasticsearch",
    13: "https://www.elastic.co/docs/reference/logstash/docker-config",
    15: "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent",
    20: "https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-kibana-with-docker",
    22: "https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings",
    26: "https://www.elastic.co/subscriptions",
    27: "https://www.elastic.co/docs/solutions/observability/logs",
    28: "https://www.elastic.co/docs/solutions/security",
}

# ---------- texto e geometria ----------

def rgb(hexadecimal):
    return RGBColor.from_string(hexadecimal)


def R(texto, **estilo):
    """Trecho de texto com estilo próprio."""
    return texto, estilo


def P(*trechos, after=0):
    return [trecho if isinstance(trecho, tuple) else R(trecho) for trecho in trechos], after


def preencher(frame, paragrafos, *, size=20, color=TEXTO, font=CORPO, bold=False,
              align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    frame.clear()
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.vertical_anchor = anchor
    frame.margin_left = frame.margin_top = frame.margin_right = frame.margin_bottom = 0
    for i, (trechos, after) in enumerate(paragrafos):
        paragrafo = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragrafo.alignment = align
        paragrafo.space_after = Pt(after)
        for conteudo, estilo in trechos:
            run = paragrafo.add_run()
            run.text = conteudo
            run.font.name = estilo.get("font", font)
            run.font.size = Pt(estilo.get("size", size))
            run.font.bold = estilo.get("bold", bold)
            run.font.color.rgb = rgb(estilo.get("color", color))
            run.font.language_id = MSO_LANGUAGE_ID.BRAZILIAN_PORTUGUESE


def texto(slide, x, y, w, h, conteudo, *, nome=None, **estilo):
    forma = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    paragrafos = [P(linha) for linha in conteudo.splitlines()] if isinstance(conteudo, str) else conteudo
    preencher(forma.text_frame, paragrafos, **estilo)
    if nome:
        forma.name = nome
    return forma


def titulo(slide, conteudo, *, x=0.76, y=0.68, w=11.81, h=0.82, size=44):
    forma = slide.shapes.title
    forma.left, forma.top = Inches(x), Inches(y)
    forma.width, forma.height = Inches(w), Inches(h)
    preencher(forma.text_frame, [P(linha) for linha in conteudo.splitlines()],
              size=size, font=TITULO, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    return forma


def forma(slide, x, y, w, h, *, fill=None, line=None, peso=1, tipo=MSO_SHAPE.RECTANGLE, nome=None):
    item = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        item.fill.solid()
        item.fill.fore_color.rgb = rgb(fill)
    else:
        item.fill.background()
    if line:
        item.line.color.rgb = rgb(line)
        item.line.width = Pt(peso)
    else:
        item.line.fill.background()
    item.shadow.inherit = False
    if nome:
        item.name = nome
    return item


def ponto(slide, x, y, cor=AZUL, tamanho=0.10):
    return forma(slide, x - tamanho / 2, y - tamanho / 2, tamanho, tamanho,
                 fill=cor, tipo=MSO_SHAPE.OVAL)


def traco(slide, x1, y1, x2, y2, cor=LINHA, *, peso=1, seta=False):
    linha = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    linha.line.color.rgb = rgb(cor)
    linha.line.width = Pt(peso)
    if seta:
        ponta = etree.SubElement(linha.line._get_or_add_ln(), qn("a:tailEnd"))
        ponta.set("type", "triangle")
        ponta.set("w", "med")
        ponta.set("len", "med")
    return linha


def polilinha(slide, pontos, cor, *, peso=1, nome=None):
    pontos = [(Inches(x), Inches(y)) for x, y in pontos]
    desenho = slide.shapes.build_freeform(*pontos[0])
    desenho.add_line_segments(pontos[1:], close=False)
    item = desenho.convert_to_shape()
    item.fill.background()
    item.line.color.rgb = rgb(cor)
    item.line.width = Pt(peso)
    item.shadow.inherit = False
    if nome:
        item.name = nome
    return item


def arco(slide, cx, cy, raio, inicio, fim, cor=LINHA, *, peso=1):
    angulos = (radians(inicio + (fim - inicio) * i / 32) for i in range(33))
    pontos = [(cx + raio * cos(a), cy + raio * sin(a)) for a in angulos]
    return polilinha(slide, pontos, cor, peso=peso, nome="Arco editável")


def fundo(slide, claro=None):
    preenchimento = slide.background.fill
    if claro:
        preenchimento.gradient()
        preenchimento.gradient_stops[0].color.rgb = rgb(FUNDO)
        preenchimento.gradient_stops[1].color.rgb = rgb(claro)
        preenchimento.gradient_angle = 28
    else:
        preenchimento.solid()
        preenchimento.fore_color.rgb = rgb(FUNDO)


def rotulo(slide, x, y, w, conteudo, cor=AZUL_CLARO, *, align=PP_ALIGN.LEFT, size=14):
    return texto(slide, x, y, w, 0.31, conteudo, font=CODIGO, size=size, color=cor, bold=True, align=align)


def pagina(slide, numero):
    traco(slide, 11.71, 7.10, 12.12, 7.10, AZUL, peso=1.5)
    rotulo(slide, 12.21, 6.98, 0.36, f"{numero:02d}", SUAVE, align=PP_ALIGN.RIGHT, size=13)


def abrir_slide(prs, layout, numero, capitulo, nome):
    slide = prs.slides.add_slide(layout)
    fundo(slide)
    rotulo(slide, 0.76, 0.31, 11.81, capitulo)
    titulo(slide, nome)
    pagina(slide, numero)
    return slide


def captura(slide, nome, x, y, w, h, descricao):
    caminho = CAPTURAS / nome
    forma(slide, x - 0.047, y - 0.047, w + 0.094, h + 0.094, fill=SUPERFICIE,
          line=LINHA, nome="Moldura da captura")
    if not caminho.is_file():
        texto(slide, x + 0.28, y + 0.34, w - 0.56, h - 0.68, descricao, size=22, color=SUAVE,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        return False
    figura = slide.shapes.add_picture(str(caminho), Inches(x), Inches(y))
    escala = min(Inches(w) / figura.width, Inches(h) / figura.height)
    figura.width, figura.height = round(figura.width * escala), round(figura.height * escala)
    figura.left = Inches(x) + (Inches(w) - figura.width) // 2
    figura.top = Inches(y) + (Inches(h) - figura.height) // 2
    figura.name = caminho.stem
    figura._element.nvPicPr.cNvPr.set("descr", descricao)
    return True


def notas(slide, ideia, fala, transicao, *, demo=None, imagem=None, refs=()):
    partes = [f"Ideia principal\n{ideia}", f"Sugestão de fala\n{fala}", f"Transição\n{transicao}"]
    if demo:
        partes.append(f"Demonstração\n{demo}")
    if imagem:
        partes.append(f"Imagem\n{imagem}")
    if refs:
        fontes = "\n".join(f"[{numero}] {FONTES[numero]}" for numero in refs)
        partes.append(f"Fontes\n{fontes}")
    slide.notes_slide.notes_text_frame.text = "\n\n".join(partes)


# Traçados simples para os seis pontos do diagrama. Cada ícone é editável.
ICONES = {
    "eventos": (
        ((-.22, -.21), (.22, -.21), (.22, .21), (-.22, .21), (-.22, -.21)),
        ((-.13, -.09), (.12, -.09)), ((-.13, .00), (.12, .00)), ((-.13, .09), (.12, .09)),
    ),
    "terminal": (
        ((-.23, -.20), (.23, -.20), (.23, .20), (-.23, .20), (-.23, -.20)),
        ((-.14, -.09), (-.05, .00), (-.14, .09)), ((.02, .09), (.15, .09)),
    ),
    "jsonl": (
        ((-.18, -.23), (.06, -.23), (.18, -.11), (.18, .23), (-.18, .23), (-.18, -.23)),
        ((.06, -.23), (.06, -.11), (.18, -.11)), ((-.10, .00), (.10, .00)), ((-.10, .10), (.10, .10)),
    ),
    "ingestao": (
        ((-.23, -.19), (.23, -.19), (.07, .02), (.07, .20), (-.07, .20), (-.07, .02), (-.23, -.19)),
    ),
    "indice": (
        ((-.24, -.12), (.00, -.24), (.24, -.12), (.00, .00), (-.24, -.12)),
        ((-.24, .00), (.00, .12), (.24, .00)), ((-.24, .12), (.00, .24), (.24, .12)),
    ),
    "grafico": (
        ((-.24, -.22), (-.24, .21), (.24, .21)),
        ((-.17, .11), (-.07, .00), (.02, .05), (.18, -.15)),
    ),
}


def icone(slide, chave, cx, cy, cor):
    for caminho in ICONES[chave]:
        polilinha(slide, [(cx + dx, cy + dy) for dx, dy in caminho], cor, peso=1.75, nome=f"Ícone {chave}")


# ---------- tema e layouts ----------

def ajustar_tema(prs):
    parte = prs.slide_master.part.part_related_by(RT.THEME)
    raiz = etree.fromstring(parte.blob)
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    raiz.set("name", "Seminario Kibana")
    esquema = raiz.find(".//a:clrScheme", ns)
    esquema.set("name", "Seminario Kibana")
    for nome, valor in TEMA_CORES.items():
        elemento = esquema.find(f"a:{nome}", ns)
        for filho in list(elemento):
            elemento.remove(filho)
        etree.SubElement(elemento, qn("a:srgbClr")).set("val", valor)
    fontes = raiz.find(".//a:fontScheme", ns)
    fontes.set("name", "Seminario Kibana")
    for grupo, nome in (("a:majorFont", TITULO), ("a:minorFont", CORPO)):
        fontes.find(f"{grupo}/a:latin", ns).set("typeface", nome)
    # Sem sombras herdadas do tema (o LibreOffice as aplicaria mesmo com a sombra desligada na forma)
    for estilo in raiz.findall(".//a:effectStyleLst/a:effectStyle", ns):
        for filho in list(estilo):
            estilo.remove(filho)
        etree.SubElement(estilo, qn("a:effectLst"))
    parte._blob = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)


def ajustar_layouts(prs, fator):
    """O modelo padrão é 4:3; estica horizontalmente os placeholders para o formato 16:9."""
    elementos = [prs.slide_master] + list(prs.slide_layouts)
    for item in elementos:
        for shape in item.shapes:
            xfrm = shape._element.find(".//" + qn("a:xfrm"))
            if xfrm is None or xfrm.find(qn("a:off")) is None:
                continue
            off, ext = xfrm.find(qn("a:off")), xfrm.find(qn("a:ext"))
            off.set("x", str(int(int(off.get("x")) * fator)))
            ext.set("cx", str(int(int(ext.get("cx")) * fator)))


# ---------- slides ----------

def slide_capa(prs, layout):
    s = prs.slides.add_slide(layout)
    fundo(s, "121E38")
    for x in (9.45, 10.05, 10.65, 11.25, 11.85, 12.45, 13.05):
        traco(s, x, 0.53, x, 6.90, GRADE, peso=0.65)
    for y in (0.72, 1.62, 2.52, 3.42, 4.32, 5.22, 6.12):
        traco(s, 9.45, y, LARGURA, y, GRADE, peso=0.65)
    for raio in (1.08, 1.85, 2.58, 3.27):
        arco(s, LARGURA, 3.72, raio, 90, 270, LINHA, peso=1.1)
    arco(s, LARGURA, 3.72, 3.27, 152, 216, AZUL, peso=2.2)
    arco(s, LARGURA, 3.72, 2.58, 106, 128, VERMELHO, peso=1.8)
    polilinha(s, [(9.60, 5.75), (10.67, 5.10), (11.57, 5.10), (13.06, 3.95)],
              LINHA, peso=1.2, nome="Trajetória de dados")
    ponto(s, 10.67, 5.10, AZUL_CLARO, 0.13)
    ponto(s, 11.57, 5.10, VERMELHO, 0.14)
    ponto(s, 13.06, 3.95, AZUL, 0.09)

    rotulo(s, 0.79, 0.92, 7.65, "SEMINÁRIO TÉCNICO", AZUL_CLARO, size=15)
    titulo(s, "Kibana", x=0.73, y=1.33, w=8.44, h=1.83, size=104)
    traco(s, 0.80, 3.22, 2.45, 3.22, AZUL, peso=3)
    traco(s, 2.55, 3.22, 2.80, 3.22, VERMELHO, peso=3)
    texto(s, 0.80, 3.59, 8.65, 1.08, "Eventos reais do Windows\ncom Logstash e Elasticsearch",
          size=29, color=SUAVE, nome="Subtítulo")
    texto(s, 0.80, 5.16, 2.46, 0.42, "Luiz Oliveira", size=23, bold=True, nome="Integrante Luiz")
    traco(s, 3.05, 5.20, 3.05, 5.51, LINHA, peso=1.2)
    texto(s, 3.33, 5.16, 3.33, 0.42, "Yahn Freitas", size=23, bold=True, nome="Integrante Yahn")
    texto(s, 0.80, 6.36, 8.55, 0.63, [
        P("Projeto de Desenvolvimento de Dashboard Analítico", after=4),
        P("Avaliação de Produto 2  /  UniSales 2026"),
    ], size=15, color=SUAVE)
    notas(s, "Abrir com uma pergunta de suporte que a turma possa imaginar.",
          "Imaginem que vocês cuidam do suporte de um laboratório. Alguns aplicativos começam a falhar, "
          "mas vocês ainda não sabem quando começou, quantas vezes aconteceu nem quais componentes estão envolvidos. "
          "Como vocês investigariam? Nós somos Luiz e Yahn e vamos mostrar um caminho usando eventos do Windows.",
          "Antes de abrir qualquer dashboard, vamos olhar o que o próprio Windows já registra.")


def slide_problema(prs, layout):
    s = abrir_slide(prs, layout, 2, "CENÁRIO HIPOTÉTICO", "Aplicativos começaram a falhar")
    texto(s, 0.76, 1.55, 11.81, 0.42, "Você assumiu o suporte do laboratório.", size=23, color=SUAVE)
    imagem = captura(s, "visualizador-eventos.png", 0.76, 2.14, 8.02, 4.35,
                     "Visualizador de Eventos do Windows no canal Aplicativo, com a lista de registros.")
    texto(s, 0.76, 6.66, 8.02, 0.33, "Captura do canal Aplicativo no computador da demonstração."
          if imagem else "O canal Aplicativo lista os registros do Windows.", size=16, color=SUAVE)

    rotulo(s, 9.15, 2.19, 3.40, "O QUE INVESTIGAR?", ALERTA)
    traco(s, 9.23, 2.83, 9.23, 5.63, VERMELHO, peso=1.3)
    for i, pergunta in enumerate(("Quando as falhas começaram?", "Com que frequência ocorrem?",
                                  "Quais fontes aparecem?")):
        y = 2.67 + i * 1.18
        ponto(s, 9.23, y + 0.24, VERMELHO, 0.12)
        texto(s, 9.52, y, 3.15, 1.01, pergunta, size=24, font=TITULO, bold=True)
    notas(s, "Uma lista de eventos ajuda a localizar um registro. Comparar horários, frequências e fontes "
             "exige organizar o conjunto.",
          "Por onde vocês começariam? O Visualizador já mostra horário, fonte, nível e ID. Esta captura é real. "
          "A história das falhas no laboratório é só o nosso cenário. Pensem em ler linha por linha para descobrir "
          "se houve um pico de erros. Em 29 de outubro de 2026, uma medição no PC de teste registrou cerca de 440 "
          "eventos em 24 horas no canal Aplicativo.",
          "Para responder às perguntas da turma, vamos transformar a lista em dados que podemos pesquisar.",
          demo="A demonstração começa no mesmo canal Aplicativo do Visualizador de Eventos.",
          imagem="Captura real de Logs do Windows → Aplicativo. O painel de mensagens está oculto." if imagem else None,
          refs=(15,))


def slide_arquitetura(prs, layout):
    s = abrir_slide(prs, layout, 3, "ARQUITETURA", "Dos registros ao painel")
    texto(s, 0.76, 1.55, 11.81, 0.47, "O Windows fornece os eventos. No Docker, a stack os prepara para consulta.",
          size=21, color=SUAVE)
    rotulo(s, 0.76, 2.28, 5.70, "NO WINDOWS", SUAVE)
    rotulo(s, 6.85, 2.28, 5.72, "NOS CONTAINERS DOCKER")
    traco(s, 0.76, 2.69, 6.46, 2.69, LINHA)
    traco(s, 6.85, 2.69, 12.57, 2.69, AZUL, peso=1.6)
    traco(s, 6.64, 2.34, 6.64, 5.58, GRADE, peso=1.5)

    etapas = (
        (1.59, "eventos", "Windows\nEvent Log", "canal Aplicativo", ALERTA),
        (3.57, "terminal", "PowerShell", "Get-WinEvent", AZUL_CLARO),
        (5.53, "jsonl", "JSONL", "eventos.jsonl", AZUL_CLARO),
        (7.65, "ingestao", "Logstash", "prepara", AZUL_CLARO),
        (9.68, "indice", "Elasticsearch", "indexa e pesquisa", AZUL_CLARO),
        (11.72, "grafico", "Kibana", "visualiza", AZUL_CLARO),
    )
    for (origem, *_), (destino, *_) in zip(etapas[:4], etapas[1:5]):
        traco(s, origem + 0.51, 3.45, destino - 0.51, 3.45, AZUL, peso=1.7, seta=True)
    traco(s, 10.21, 3.33, 11.19, 3.33, AZUL, peso=1.65, seta=True)
    traco(s, 11.19, 3.59, 10.21, 3.59, AZUL_CLARO, peso=1.55, seta=True)
    rotulo(s, 10.09, 2.85, 1.22, "RESPOSTAS", SUAVE, align=PP_ALIGN.CENTER, size=12)
    rotulo(s, 10.09, 3.76, 1.22, "CONSULTAS", SUAVE, align=PP_ALIGN.CENTER, size=12)
    for cx, simbolo, nome, detalhe, cor in etapas:
        forma(s, cx - 0.44, 3.01, 0.88, 0.88, fill=SUPERFICIE, line=LINHA, peso=1.25,
              tipo=MSO_SHAPE.OVAL, nome=f"Estação {simbolo}")
        icone(s, simbolo, cx, 3.45, cor)
        texto(s, cx - 0.98, 4.16, 1.96, 0.79, nome, size=20, font=TITULO, bold=True, align=PP_ALIGN.CENTER)
        texto(s, cx - 0.98, 5.00, 1.96, 0.42, detalhe, size=16, color=SUAVE, align=PP_ALIGN.CENTER)

    traco(s, 0.76, 6.08, 12.57, 6.08, LINHA)
    texto(s, 0.76, 6.30, 11.81, 0.43, "Os documentos ficam no Elasticsearch. O Kibana consulta e exibe as respostas.",
          size=21, color=TEXTO)
    notas(s, "Seguir um evento da origem até a visualização e distinguir o Windows dos containers.",
          "No Windows, o PowerShell lê o canal Aplicativo e grava o JSONL. O Logstash lê esse arquivo no Docker, "
          "prepara os dados e envia os eventos ao Elasticsearch. É o Elasticsearch que armazena os documentos. "
          "Quando abrimos um painel, o Kibana pede os dados e exibe a resposta. Os três containers usam a versão 9.5.5.",
          "A primeira passagem acontece no Windows. Vamos ver como o coletor retoma a leitura.",
          demo="Relacionar o arquivo e a contagem da demonstração com as duas partes do diagrama.",
          refs=(1, 13, 15, 20))


def slide_coleta(prs, layout):
    s = abrir_slide(prs, layout, 4, "ORIGEM DOS DADOS", "Coleta dos eventos")
    for raio, cor in ((1.82, GRADE), (1.62, LINHA), (1.43, GRADE)):
        forma(s, 3.02 - raio, 3.72 - raio, 2 * raio, 2 * raio, line=cor, tipo=MSO_SHAPE.OVAL)
    arco(s, 3.02, 3.72, 1.62, 204, 321, AZUL, peso=3)
    arco(s, 3.02, 3.72, 1.62, 26, 64, VERMELHO, peso=2)
    ponto(s, 4.28, 2.70, AZUL_CLARO, 0.10)
    texto(s, 1.36, 2.83, 3.32, 1.31, "15 s", size=78, font=TITULO, bold=True, align=PP_ALIGN.CENTER)
    texto(s, 1.34, 4.30, 3.36, 0.49, "entre verificações", size=20, color=SUAVE, align=PP_ALIGN.CENTER)

    traco(s, 5.74, 2.33, 5.74, 4.99, LINHA, peso=1.5)
    passos = (
        ("Canal Aplicativo", "O PowerShell lê com Get-WinEvent."),
        ("Checkpoint", "O RecordId indica até onde a coleta chegou."),
        ("eventos.jsonl", "Uma linha JSON para cada evento novo."),
    )
    for i, (nome, detalhe) in enumerate(passos):
        y = 2.10 + i * 1.14
        ponto(s, 5.74, y + 0.24, AZUL, 0.15)
        texto(s, 6.06, y, 6.48, 0.48, nome, size=26, font=TITULO, bold=True)
        texto(s, 6.06, y + 0.51, 6.48, 0.37, detalhe, size=19, color=SUAVE)
    traco(s, 0.76, 5.87, 12.57, 5.87, LINHA)
    rotulo(s, 0.76, 6.08, 5.70, "METADADOS SELECIONADOS")
    rotulo(s, 6.58, 6.08, 5.99, "FORA DA EXPORTAÇÃO", ALERTA)
    texto(s, 0.76, 6.45, 5.68, 0.35, "Horário, nível, provedor e IDs.", size=18)
    texto(s, 6.58, 6.45, 5.99, 0.35, "Mensagem, usuário e nome do computador.", size=18)
    notas(s, "O PowerShell coleta periodicamente e exporta apenas metadados selecionados.",
          "A primeira leitura pega até 2.000 eventos dos últimos sete dias. Depois o script confere o canal "
          "Aplicativo a cada 15 segundos. O checkpoint guarda o RecordId até onde lemos. A próxima rodada procura "
          "os eventos posteriores e acrescenta uma linha JSON para cada um. O arquivo inclui um identificador "
          "aleatório da instalação. Mensagem, usuário e nome do computador ficam fora. Horário e provedor podem "
          "revelar contexto, então a pasta runtime/ fica no computador e fora do Git.",
          "O Windows já produziu o arquivo. Agora o Logstash vai acompanhá-lo.",
          demo="Ao mostrar a última linha do JSONL, aponte horário, nível e ID sem abrir mensagens do Windows.",
          refs=(15,))


def slide_logstash(prs, layout):
    s = abrir_slide(prs, layout, 5, "INGESTÃO", "Logstash")
    texto(s, 0.76, 1.55, 11.81, 0.46, "O coletor verifica o Windows em ciclos. O Logstash acompanha o arquivo continuamente.",
          size=20, color=SUAVE)
    forma(s, 0.76, 2.22, 11.81, 3.00, fill=SUPERFICIE, line=LINHA, nome="Faixa contínua de ingestão")
    traco(s, 0.76, 2.22, 12.57, 2.22, AZUL, peso=2.3)
    etapas = (
        (1.03, "Input", "file + codec json", "Lê linhas novas e converte cada JSON em evento."),
        (5.07, "Filter", "mutate", "Remove campos técnicos da ingestão."),
        (9.11, "Output", "elasticsearch", "Grava o evento no índice windows-events."),
    )
    for i, (x, etapa, plugin, tarefa) in enumerate(etapas):
        rotulo(s, x, 2.53, 0.62, f"0{i + 1}", AZUL_CLARO)
        texto(s, x, 2.90, 3.21, 0.64, etapa, size=34, font=TITULO, bold=True)
        texto(s, x, 3.72, 3.25, 0.37, plugin, size=18, font=CODIGO, color=AZUL_CLARO)
        texto(s, x, 4.17, 3.14, 0.80, tarefa, size=19, color=SUAVE)
    traco(s, 4.16, 3.21, 4.86, 3.21, AZUL_CLARO, peso=1.85, seta=True)
    traco(s, 8.20, 3.21, 8.90, 3.21, AZUL_CLARO, peso=1.85, seta=True)

    texto(s, 0.76, 5.65, 5.62, 0.80, [
        P(R("sincedb", font=CODIGO, color=AZUL_CLARO, bold=True), after=5),
        P("Guarda a posição de leitura do arquivo."),
    ], size=18)
    texto(s, 6.69, 5.65, 5.88, 0.80, [
        P(R("document_id", font=CODIGO, color=AZUL_CLARO, bold=True), after=5),
        P("Mantém o mesmo documento em uma releitura."),
    ], size=18)
    traco(s, 6.43, 5.66, 6.43, 6.54, LINHA)
    notas(s, "A coleta periódica e a ingestão contínua são partes diferentes do fluxo.",
          "O Logstash acompanha o arquivo com a entrada file. O sincedb guarda até onde essa entrada leu e "
          "o codec json decodifica a próxima linha. O mutate remove campos técnicos que o próprio Logstash "
          "acrescenta. A saída envia o evento ao Elasticsearch com o ID que veio do coletor. Se uma linha for "
          "relida, o documento de mesmo ID é atualizado. Em termos de memória, a demo usa um heap de 256 MB no Logstash.",
          "O próximo componente recebe esse evento. Vamos ver como ele fica armazenado.",
          demo="Mostre logstash/pipeline/windows-events.conf e percorra input, filter e output na ordem.",
          refs=(9, 10, 11, 12, 13))


def slide_elasticsearch(prs, layout):
    s = abrir_slide(prs, layout, 6, "INDEXAÇÃO", "Elasticsearch")
    texto(s, 0.76, 1.55, 11.81, 0.43, "Indexar organiza os registros para busca e análise.", size=22, color=SUAVE)
    forma(s, 0.76, 2.20, 7.18, 3.87, fill=SUPERFICIE, line=LINHA, nome="Exemplo JSON editável")
    rotulo(s, 1.02, 2.45, 6.55, "JSON DO EVENTO  /  EXEMPLO DE FORMATO", AZUL_CLARO)
    traco(s, 1.02, 2.88, 7.64, 2.88, LINHA)
    linhas = [
        P("{", after=3),
        P(R('  "@timestamp"', color=AZUL_CLARO), ': "2026-10-29T14:05:12.000Z",', after=3),
        P(R('  "event"', color=AZUL_CLARO), ': {"code": "1000"},', after=3),
        P(R('  "log"', color=AZUL_CLARO), ': {"level": ', R('"Error"', color=ALERTA), '},', after=3),
        P(R('  "winlog"', color=AZUL_CLARO), ': {"record_id": 50123}', after=3),
        P("}"),
    ]
    texto(s, 1.02, 3.09, 6.65, 2.22, linhas, size=16.5, font=CODIGO, nome="Trecho ilustrativo do evento")
    texto(s, 1.02, 5.53, 6.66, 0.33, "Campos selecionados da estrutura do projeto.", size=16, color=SUAVE)

    traco(s, 8.52, 2.62, 8.52, 5.62, LINHA, peso=1.4)
    conceitos = (
        ("Índice", "windows-events", CODIGO),
        ("Documento", "Um evento em JSON.", CORPO),
        ("Campos", "date, keyword e long", CODIGO),
    )
    for i, (nome, detalhe, fonte) in enumerate(conceitos):
        y = 2.32 + i * 1.16
        ponto(s, 8.52, y + 0.28, AZUL, 0.13)
        texto(s, 8.87, y, 3.70, 0.53, nome, size=27, font=TITULO, bold=True)
        texto(s, 8.87, y + 0.54, 3.70, 0.41, detalhe, size=18, font=fonte, color=SUAVE)
    texto(s, 0.76, 6.48, 11.81, 0.39, "O ID estável mantém um documento por evento em releituras.", size=19, color=SUAVE)
    notas(s, "Mostrar a relação entre evento, documento, índice e tipo de campo.",
          "O índice windows-events reúne documentos. Cada documento representa um evento em JSON. O exemplo "
          "mostra parte do formato real. O campo @timestamp tem tipo date, o nível e o código são keyword, "
          "e winlog.record_id é long. Esses tipos ajudam a organizar buscas, agrupar os registros e montar uma "
          "linha do tempo. Se o mesmo ID for enviado de novo, o Elasticsearch atualiza o documento.",
          "Com os documentos pesquisáveis, podemos voltar à pergunta da investigação e respondê-la no navegador.",
          demo="Na porta 9200, use a contagem de windows-events para mostrar que o índice recebeu os eventos.",
          refs=(2, 12))


def slide_kibana(prs, layout):
    s = abrir_slide(prs, layout, 7, "EXPLORAÇÃO", "O que é o Kibana")
    texto(s, 0.76, 1.55, 11.81, 0.45, "Uma interface web para explorar os dados do Elasticsearch.", size=22, color=SUAVE)
    forma(s, 0.76, 2.24, 6.88, 3.70, fill=SUPERFICIE, line=LINHA, nome="Pergunta da investigação")
    polilinha(s, [(5.78, 5.95), (7.64, 4.49)], GRADE, peso=1.4)
    polilinha(s, [(6.56, 5.95), (7.64, 5.10)], LINHA, peso=1.05)
    ponto(s, 7.11, 5.53, AZUL, 0.13)
    ponto(s, 7.31, 4.75, VERMELHO, 0.095)
    rotulo(s, 1.03, 2.58, 6.08, "PERGUNTA DE INVESTIGAÇÃO")
    texto(s, 1.03, 3.24, 6.08, 1.47, "Que erros ocorreram\nnesta semana?", size=42, font=TITULO,
          bold=True, nome="Pergunta sobre erros na semana")

    traco(s, 8.19, 2.72, 8.19, 5.40, LINHA, peso=1.4, seta=True)
    for y, etapa, detalhe in (
        (2.42, "Consulta", "O Elasticsearch pesquisa e agrega os dados."),
        (4.08, "Visualização", "O Kibana exibe as respostas em tabelas e gráficos."),
    ):
        ponto(s, 8.19, y + 0.31, AZUL, 0.15)
        texto(s, 8.50, y, 4.07, 0.53, etapa, size=29, font=TITULO, bold=True)
        texto(s, 8.50, y + 0.64, 4.07, 0.77, detalhe, size=20, color=SUAVE)
    rotulo(s, 0.76, 6.43, 5.55, "INTERFACE NO NAVEGADOR  /  PORTA 5601", SUAVE)
    notas(s, "O Elasticsearch executa a consulta. O Kibana permite formulá-la e explorar o resultado.",
          "Voltem à pergunta sobre os erros. Quando escolho um intervalo e filtro pelo nível no Kibana, "
          "o Elasticsearch encontra os documentos e calcula o que o painel precisa. O Kibana apresenta a lista "
          "ou o gráfico no navegador. Os documentos e os objetos salvos do Kibana ficam no Elasticsearch.",
          "Vamos seguir as etapas que vocês vão reconhecer quando abrirmos o Kibana.",
          demo="Use a pergunta da semana para explicar o intervalo Last 7 days no Discover.",
          refs=(1, 4, 6, 7))


def slide_ferramentas(prs, layout):
    s = abrir_slide(prs, layout, 8, "EXPLORAÇÃO", "Ferramentas do Kibana")
    etapas = (
        ("Data View", "Seleciona índice e tempo."),
        ("Discover", "Mostra os documentos."),
        ("KQL", "Filtra os eventos."),
        ("Lens", "Cria gráficos."),
        ("Dashboard", "Reúne as visualizações."),
    )
    traco(s, 0.91, 2.03, 0.91, 5.94, LINHA, peso=1.35)
    for i, (nome, detalhe) in enumerate(etapas):
        y = 1.82 + i * 0.97
        cor = VERMELHO if nome == "KQL" else AZUL
        ponto(s, 0.91, y + 0.24, cor, 0.13)
        texto(s, 1.22, y, 3.02, 0.44, nome, size=23, font=TITULO, bold=True)
        texto(s, 1.22, y + 0.49, 3.02, 0.39, detalhe, size=17, color=SUAVE)

    rotulo(s, 4.59, 1.83, 7.98, "DISCOVER  /  EVENTOS DO WINDOWS")
    imagem = captura(s, "discover.png", 4.59, 2.29, 7.98, 3.57,
                     "Discover com o Data View Eventos do Windows e filtro de nível Error.")
    forma(s, 4.59, 6.19, 7.98, 0.62, fill=RELEVO, line=LINHA, nome="Exemplo KQL")
    texto(s, 4.78, 6.29, 7.58, 0.36, [
        P(R("KQL   ", color=ALERTA, bold=True), R('log.level : "Error"')),
    ], size=18.5, font=CODIGO)
    notas(s, "Preparar a turma para reconhecer as ferramentas durante a demonstração.",
          "Escolho Eventos do Windows no Data View. Ele indica o índice e o campo de tempo. No Discover, "
          "eu vejo os documentos. A KQL restringe a lista aos erros. O Lens usa um campo para montar um gráfico. "
          "No dashboard, a turma consegue comparar os painéis com o mesmo intervalo e os mesmos filtros. "
          "Se quisermos juntar avisos e erros, podemos usar log.level : \"Warning\" or log.level : \"Error\".",
          "Já vimos como explorar os dados. Agora podemos avaliar onde essa abordagem ajuda.",
          demo="No Discover, use log.level : \"Error\". Limpe o filtro e abra a prévia de event.code para ir ao Lens.",
          imagem="Captura real do Discover com a consulta KQL de erros." if imagem else None,
          refs=(3, 4, 5, 6, 7))


def slide_vantagens(prs, layout):
    s = abrir_slide(prs, layout, 9, "AVALIAÇÃO", "Vantagens")
    texto(s, 0.76, 1.81, 11.81, 0.97, "Visualização sem programação", size=49, font=TITULO,
          bold=True, color=AZUL_CLARO)
    texto(s, 0.76, 2.90, 11.81, 0.44, "O Lens permite montar gráficos pela interface.", size=22, color=SUAVE)
    traco(s, 0.76, 3.77, 12.57, 3.77, LINHA, peso=1.45)
    itens = (
        (0.76, "Interatividade", "Pesquisa e filtros por clique em todo o painel."),
        (4.86, "Integração", "Busca no Elasticsearch e ingestão flexível com Logstash."),
        (8.94, "Expansão", "Mais fontes e computadores podem alimentar o índice."),
    )
    for x, nome, detalhe in itens:
        ponto(s, x + 0.15, 3.77, AZUL, 0.16)
        texto(s, x, 4.19, 3.62, 0.56, nome, size=27, font=TITULO, bold=True)
        texto(s, x, 4.87, 3.59, 0.78, detalhe, size=20, color=SUAVE)
    forma(s, 0.76, 6.15, 11.81, 0.57, fill=AZUL_ESCURO, nome="Licença da demonstração")
    texto(s, 0.99, 6.24, 11.30, 0.36, "A demonstração usa os recursos gratuitos da licença Basic.", size=18)
    notas(s, "Explicar o que o Kibana simplifica para quem analisa e onde a solução pode crescer.",
          "Vocês conseguem pesquisar, filtrar e criar gráficos pela interface. A coleta e a ingestão ainda "
          "usam um script e uma configuração. O Elasticsearch executa a busca, e o Logstash pode adaptar as "
          "entradas, os filtros e as saídas para outras fontes. Em outro computador, o mesmo repositório coleta "
          "os eventos daquela máquina. Os recursos que vamos mostrar estão na licença Basic.",
          "Antes de testar ao vivo, vale separar o que cabe nesta demonstração do que exige preparação em produção.",
          demo="No Lens e no dashboard, destaque a criação do gráfico e a filtragem feita pela interface.",
          refs=(1, 6, 7, 9, 26))


def slide_limitacoes(prs, layout):
    s = abrir_slide(prs, layout, 10, "AVALIAÇÃO", "Limitações e aplicações")
    traco(s, 0.76, 2.03, 6.27, 2.03, VERMELHO, peso=2.5)
    traco(s, 6.83, 2.03, 12.57, 2.03, AZUL, peso=2.5)
    traco(s, 6.55, 2.03, 6.55, 5.77, GRADE, peso=1.3)
    colunas = (
        (0.76, "Nesta demonstração", ALERTA, (
            "Memória para três serviços",
            "Coleta a cada 15 segundos",
            "Configuração e manutenção",
            "Escopo local, com um único nó",
        )),
        (6.83, "Onde aplicar", AZUL_CLARO, (
            "Suporte e investigação de falhas",
            "Observabilidade de aplicativos",
            "Análise centralizada de logs",
            "Segurança em soluções apropriadas",
        )),
    )
    for x, nome, cor, itens in colunas:
        texto(s, x, 2.29, 5.43, 0.55, nome, size=27, font=TITULO, color=cor, bold=True)
        for i, item in enumerate(itens):
            y = 3.06 + i * 0.62
            ponto(s, x + 0.07, y + 0.16, cor, 0.085)
            texto(s, x + 0.24, y, 5.21, 0.40, item, size=20)
    forma(s, 0.76, 6.04, 11.81, 0.70, fill=VERMELHO_ESCURO, nome="Segurança em produção")
    traco(s, 0.76, 6.04, 0.76, 6.74, VERMELHO, peso=2.4)
    texto(s, 0.99, 6.18, 11.28, 0.40, [
        P(R("Sem autenticação ou TLS na demo local. ", bold=True, color=ALERTA),
          R("Em produção, configure ambos.")),
    ], size=19)
    notas(s, "Separar as escolhas didáticas da infraestrutura necessária em uso real.",
          "Estamos usando três serviços, então a memória conta. A coleta tem intervalo e a configuração "
          "precisa de manutenção. Aqui tudo roda em um computador e um nó. Tiramos autenticação e TLS para "
          "a demo local. Em produção, a configuração segura é parte do projeto. A mesma ideia pode apoiar "
          "suporte, investigação de falhas, observabilidade, centralização de logs e segurança em uma solução adequada.",
          "Agora vamos acompanhar esse processo funcionando, da lista de eventos até o painel.",
          demo="As portas publicadas pela demonstração aceitam acesso apenas do próprio computador.",
          refs=(1, 22, 27, 28))


def slide_demo(prs, layout):
    s = prs.slides.add_slide(layout)
    fundo(s, "101D36")
    ponto(s, 0.82, 0.63, VERMELHO, 0.11)
    rotulo(s, 1.01, 0.49, 3.05, "AO VIVO  /  5 MIN", ALERTA)
    titulo(s, "Demonstração\nprática", x=0.76, y=1.25, w=3.65, h=1.50, size=38)
    texto(s, 0.76, 3.02, 3.29, 1.52, "Agora vamos acompanhar esse processo funcionando.", size=24, color=SUAVE)
    traco(s, 0.76, 4.75, 2.04, 4.75, AZUL, peso=3)
    traco(s, 2.14, 4.75, 2.40, 4.75, VERMELHO, peso=3)
    imagem = captura(s, "eventos-do-windows.png", 4.50, 1.13, 8.07, 4.27,
                     "Dashboard Eventos do Windows com os quatro painéis originais e o intervalo dos últimos sete dias.")
    texto(s, 4.50, 5.57, 8.07, 0.35, "Eventos do Windows  /  captura do ambiente local"
          if imagem else "Eventos do Windows  /  abra o dashboard local", size=16, color=SUAVE)
    traco(s, 0.86, 6.31, 12.39, 6.31, LINHA, peso=1.45, seta=True)
    for i, etapa in enumerate(("Origem", "Coleta", "Ingestão", "Exploração", "Dashboard")):
        x = 0.86 + i * 2.31
        ponto(s, x, 6.31, VERMELHO if i == 0 else AZUL, 0.13)
        texto(s, x, 6.59, 2.15, 0.37, etapa, size=18, bold=True)
    pagina(s, 11)
    notas(s, "Acompanhar uma única execução, da origem ao dashboard, em cerca de cinco minutos.",
          "Vamos voltar ao canal Aplicativo. Em seguida, mostramos a coleta no PowerShell e uma linha do JSONL. "
          "Apontamos o pipeline do Logstash e a contagem no Elasticsearch. No Kibana, abrimos o Discover, "
          "filtramos os erros com KQL, criamos o gráfico de IDs no Lens e terminamos com um clique no dashboard.",
          "Ao voltar aos slides, retome a pergunta do laboratório e feche com as três ideias da conclusão.",
          demo="Siga o guia rápido do README ou a seção 3 de docs/roteiro_demonstracao.md. Uma pessoa opera, "
               "a outra narra. Os totais variam com os dados e o intervalo.",
          imagem="Captura real do dashboard Eventos do Windows com os quatro painéis originais." if imagem else None)


def slide_conclusao(prs, layout):
    s = prs.slides.add_slide(layout)
    fundo(s, "142340")
    for raio in (1.55, 2.25, 3.01):
        arco(s, 0, ALTURA, raio, 270, 360, LINHA, peso=1.1)
    arco(s, 0, ALTURA, 3.01, 299, 352, AZUL, peso=2.3)
    arco(s, 0, ALTURA, 2.25, 306, 328, VERMELHO, peso=1.8)
    ponto(s, 2.48, 5.79, AZUL_CLARO, 0.13)
    rotulo(s, 0.76, 0.67, 7.50, "CONCLUSÃO", AZUL_CLARO, size=16)
    titulo(s, "Perguntas?", x=0.72, y=2.07, w=7.18, h=1.49, size=86)
    traco(s, 0.78, 3.88, 2.70, 3.88, AZUL, peso=3)
    traco(s, 2.82, 3.88, 3.12, 3.88, VERMELHO, peso=3)

    traco(s, 7.99, 1.57, 7.99, 6.34, LINHA, peso=1.4)
    mensagens = (
        ("Windows", "Produz os eventos reais."),
        ("Logstash e Elasticsearch", "Ingerem e tornam os registros pesquisáveis."),
        ("Kibana", "Permite explorar os dados com filtros e gráficos."),
    )
    for i, (nome, mensagem) in enumerate(mensagens):
        y = 1.77 + i * 1.46
        rotulo(s, 8.26, y + 0.08, 0.43, f"0{i + 1}", AZUL_CLARO)
        texto(s, 8.90, y, 3.67, 0.53, nome, size=22, font=TITULO, bold=True)
        texto(s, 8.90, y + 0.54, 3.67, 0.70, mensagem, size=19, color=SUAVE)
    notas(s, "Responder à pergunta inicial e abrir espaço para a turma e o professor.",
          "Para investigar as falhas do laboratório, começamos com os registros reais do Windows. "
          "O Logstash prepara os eventos, o Elasticsearch permite encontrá-los e o Kibana ajuda a explorar "
          "os resultados. Com isso podemos olhar o horário, a frequência e as fontes. Perguntas?",
          "Deixe este slide visível durante as perguntas. Para fontes e datas de acesso, indique docs/referencias.md.",
          refs=(1, 7, 9))


def main(saida=SAIDA):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(LARGURA), Inches(ALTURA)
    ajustar_layouts(prs, LARGURA / 10)
    ajustar_tema(prs)
    layout = next(l for l in prs.slide_layouts if l.name == "Title Only")
    for criar in (slide_capa, slide_problema, slide_arquitetura, slide_coleta, slide_logstash,
                  slide_elasticsearch, slide_kibana, slide_ferramentas, slide_vantagens, slide_limitacoes,
                  slide_demo, slide_conclusao):
        criar(prs, layout)
    cp = prs.core_properties
    cp.title = "Kibana: eventos reais do Windows com Logstash e Elasticsearch"
    cp.subject = "Seminário técnico - Projeto de Desenvolvimento de Dashboard Analítico"
    cp.keywords = "Kibana; Logstash; Elasticsearch; Dashboard; Logs do Windows"
    cp.author = ""
    cp.last_modified_by = ""
    cp.comments = ""
    cp.category = ""
    cp.language = "pt-BR"
    cp.revision = 1
    agora = datetime.now().replace(microsecond=0)
    cp.created = agora
    cp.modified = agora
    # O modelo padrão traz docProps/app.xml de uma apresentação 4:3 vazia; substitui por valores corretos.
    total = len(prs.slides)
    app_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        f"<PresentationFormat>Widescreen</PresentationFormat><Slides>{total}</Slides><Notes>{total}</Notes>"
        "<HiddenSlides>0</HiddenSlides></Properties>"
    )
    for parte in prs.part.package.iter_parts():
        if str(parte.partname) == "/docProps/app.xml":
            parte._blob = app_xml.encode("utf-8")
    prs.save(saida)
    print(f"Gerado: {saida} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()

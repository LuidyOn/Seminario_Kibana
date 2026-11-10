"""Gera a apresentação editável slides/seminario_kibana.pptx.

Requisito: Python 3 com python-pptx (py -3 -m pip install python-pptx).
Uso, a partir da raiz do repositório:  py -3 slides/gerar_slides.py

Texto, formas e diagramas são editáveis. As capturas em slides/assets/ são opcionais.
Os trechos de JSON são ilustrativos.
"""
from datetime import datetime
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

# Paleta (as cores dos níveis seguem o dashboard: Error em vermelho)
NAVY, TEAL, RED, SLATE = "1B2A41", "0E7C86", "E34948", "4A6178"
TEXT, MUTED, WHITE = "1F2933", "5B6770", "FFFFFF"
LIGHT, BORDER, TEAL_TINT, RED_TINT = "F2F5F7", "D5DDE3", "E3F1F2", "FCEBEA"
CODE_BG, CODE_TXT, CODE_TYPE, ON_DARK = "17202C", "D9E2EC", "7FD1D8", "C9D6DF"
CODE = "Courier New"

TEMA_CORES = {
    "dk1": TEXT, "lt1": WHITE, "dk2": NAVY, "lt2": LIGHT,
    "accent1": TEAL, "accent2": RED, "accent3": "2A78D6", "accent4": "EDA100",
    "accent5": "4A3AA7", "accent6": MUTED, "hlink": TEAL, "folHlink": "4A3AA7",
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


# ---------- utilitários ----------

def rgb(hexa):
    return RGBColor.from_string(hexa)


def R(texto, **estilo):
    """Trecho de texto (run) com estilo opcional."""
    return (texto, estilo)


def P(*trechos, **opcoes):
    """Parágrafo formado por trechos; aceita align, after, before, bullet, size, color, bold."""
    return {"runs": [t if isinstance(t, tuple) else R(t) for t in trechos], **opcoes}


def estilizar(run, size=None, bold=None, italic=None, color=None, font=None, link=None):
    if link:
        run.hyperlink.address = link
    f = run.font
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color:
        f.color.rgb = rgb(color)
    if font:
        f.name = font
    f.language_id = MSO_LANGUAGE_ID.BRAZILIAN_PORTUGUESE


def marcador(paragrafo, cor):
    pPr = paragrafo._p.get_or_add_pPr()
    pPr.set("marL", str(Inches(0.3)))
    pPr.set("indent", str(-Inches(0.25)))
    bu_clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(bu_clr, qn("a:srgbClr")).set("val", cor)
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def preencher(tf, paragrafos, size=16, color=TEXT, bold=False, font=None, align=PP_ALIGN.LEFT,
              after=6, anchor=MSO_ANCHOR.TOP, margens=(0.12, 0.08, 0.12, 0.08)):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (Inches(m) for m in margens)
    for i, par in enumerate(paragrafos):
        if not isinstance(par, dict):
            par = P(par)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = par.get("align", align)
        p.space_after = Pt(par.get("after", after))
        if par.get("before"):
            p.space_before = Pt(par["before"])
        if par.get("bullet"):
            marcador(p, par.get("bullet_color", TEAL))
        for texto, est in par["runs"]:
            run = p.add_run()
            run.text = texto
            estilizar(run, size=est.get("size", par.get("size", size)),
                      bold=est.get("bold", par.get("bold", bold)), italic=est.get("italic"),
                      color=est.get("color", par.get("color", color)),
                      font=est.get("font", par.get("font", font)), link=est.get("link"))


def texto(slide, x, y, w, h, paragrafos, nome=None, **kw):
    if isinstance(paragrafos, str):
        paragrafos = paragrafos.splitlines()
    caixa_txt = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    preencher(caixa_txt.text_frame, paragrafos, margens=(0, 0, 0, 0), **kw)
    if nome:
        caixa_txt.name = nome
    return caixa_txt


def forma(slide, x, y, w, h, fill=LIGHT, line=None, line_w=1.0, raio=0.06, tipo=MSO_SHAPE.ROUNDED_RECTANGLE,
          nome=None, paragrafos=None, **kw):
    s = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    if tipo == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = raio
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(line_w)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if nome:
        s.name = nome
    if paragrafos is not None:
        preencher(s.text_frame, paragrafos, **kw)
    return s


def faixa(slide, x, y, w, h, cor):
    return forma(slide, x, y, w, h, fill=cor, tipo=MSO_SHAPE.RECTANGLE)


def fundo_escuro(slide):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(NAVY)


def seta(slide, x1, y1, x2, y2, cor=MUTED, largura=1.75):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(cor)
    c.line.width = Pt(largura)
    ln = c.line._get_or_add_ln()
    ponta = etree.SubElement(ln, qn("a:tailEnd"))
    for atributo, valor in (("type", "triangle"), ("w", "med"), ("len", "med")):
        ponta.set(atributo, valor)
    return c


def codigo(slide, x, y, w, h, linhas, size=13, nome=None):
    pars = [P(*(l if isinstance(l, list) else [R(l)]), after=0) for l in linhas]
    return forma(slide, x, y, w, h, fill=CODE_BG, raio=0.04, nome=nome, paragrafos=pars, size=size,
                 color=CODE_TXT, font=CODE, after=0, margens=(0.25, 0.18, 0.2, 0.18))


def titulo(slide, texto_titulo, cor=NAVY, size=40):
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.72), Inches(0.44), Inches(11.89), Inches(0.87)
    preencher(t.text_frame, [P(R(texto_titulo, bold=True))], size=size, color=cor,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)
    return t


def notas(slide, fala, refs=()):
    if refs:
        fontes = "\n".join(f"[{numero}] {FONTES[numero]}" for numero in refs)
        fala += f"\n\nFontes:\n{fontes}"
    slide.notes_slide.notes_text_frame.text = fala


def captura(slide, nome, x, y, w, h):
    caminho = CAPTURAS / nome
    if not caminho.is_file():
        return False
    figura = slide.shapes.add_picture(str(caminho), Inches(x), Inches(y))
    fator = min(Inches(w) / figura.width, Inches(h) / figura.height)
    figura.width, figura.height = round(figura.width * fator), round(figura.height * fator)
    figura.left = Inches(x) + (Inches(w) - figura.width) // 2
    figura.top = Inches(y) + (Inches(h) - figura.height) // 2
    figura.name = caminho.stem
    return True


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
    for grupo in ("a:majorFont", "a:minorFont"):
        fontes.find(f"{grupo}/a:latin", ns).set("typeface", "Calibri")
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
    fundo_escuro(s)
    texto(s, 0.76, 0.95, 7.0, 0.34, "SEMINÁRIO TÉCNICO", size=17, bold=True, color=CODE_TYPE)
    t = titulo(s, "Kibana na prática", cor=WHITE, size=60)
    t.left, t.top, t.width, t.height = Inches(0.72), Inches(1.48), Inches(7.65), Inches(1.13)
    texto(s, 0.76, 2.83, 7.5, 1.27, [
        P(R("Eventos reais do Windows", size=30, bold=True), after=5),
        P("com Logstash e Elasticsearch"),
    ], size=24, color=ON_DARK)
    texto(s, 0.76, 5.08, 7.7, 1.72, [
        P(R("Avaliação de Produto 2", color=WHITE, bold=True), after=5),
        P("Projeto de Desenvolvimento de Dashboard Analítico", after=5),
        P("UniSales · 2026", after=5),
        P("Integrantes: nomes a preencher"),
    ], size=17, color=ON_DARK, nome="Identificação acadêmica")

    faixa(s, 8.53, 1.64, 0.04, 4.37, SLATE)
    for i, (etapa, nome) in enumerate((
        ("CANAL DE ORIGEM", "Application"),
        ("ÍNDICE", "windows-events"),
        ("DASHBOARD", "Eventos do Windows"),
    )):
        y = 1.82 + i * 1.42
        texto(s, 8.93, y, 3.66, 0.28, etapa, size=13, bold=True, color=CODE_TYPE)
        texto(s, 8.93, y + 0.34, 3.75, 0.48, nome, size=23, bold=True, color=WHITE)
        if i < 2:
            seta(s, 9.04, y + 0.91, 9.04, y + 1.26, cor=CODE_TYPE, largura=1.5)
    notas(s, "Apresentar o tema e o grupo. Vamos transformar eventos reais do Windows em respostas "
             "visuais com Logstash, Elasticsearch e Kibana.")


def slide_problema(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Análise de eventos do Windows")
    texto(s, 0.72, 1.58, 7.0, 0.42, "Visualizador de Eventos · Canal Aplicativo",
          size=20, bold=True, color=NAVY)
    tem_captura = captura(s, "visualizador-eventos.png", 0.72, 2.12, 7.03, 3.91)
    if not tem_captura:
        faixa(s, 0.72, 2.17, 7.03, 3.37, LIGHT)
        texto(s, 1.04, 2.48, 6.4, 0.45, "Campos de um evento", size=23, bold=True, color=NAVY)
        texto(s, 1.04, 3.12, 6.2, 1.74, [
            P("Nível e horário", after=12),
            P("Provedor de origem", after=12),
            P("ID do evento"),
        ], size=21, color=TEXT)
    texto(s, 0.72, 6.14, 7.03, 0.65, "O Visualizador lista os registros um a um.", size=19, color=MUTED)

    faixa(s, 8.05, 1.60, 0.04, 5.04, BORDER)
    texto(s, 8.39, 1.58, 4.26, 1.00, "≈ 440", size=59, bold=True, color=TEAL)
    texto(s, 8.44, 2.59, 4.17, 0.81, "eventos em 24 h no PC de teste\nCanal Aplicativo, 29/10/2026",
          size=17, color=MUTED)
    perguntas = ("Quantos erros se repetem?", "Quais aplicativos os registram?",
                 "Em que horário os erros se concentram?")
    for i, pergunta in enumerate(perguntas):
        y = 3.61 + i * 0.94
        faixa(s, 8.44, y + 0.06, 0.055, 0.30, RED)
        texto(s, 8.64, y, 4.02, 0.78, pergunta, size=22, bold=True, color=NAVY)
    fala = ("O Windows registra eventos o tempo todo. No computador de testes, foram cerca de 440 em 24 horas "
            "só no canal Aplicativo, em 29/10/2026. No Visualizador de Eventos, a leitura é evento a evento. "
            "Pergunte quantos erros ocorreram, de quais aplicativos, em que horário e se chegou algum evento novo. "
            "Para responder, precisamos coletar, guardar e visualizar os dados.")
    if tem_captura:
        fala += "\n\nImagem: Visualizador de Eventos do Windows, canal Aplicativo."
    notas(s, fala)


def slide_o_que_e(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "O que é o Kibana")
    texto(s, 0.72, 1.45, 11.89, 0.67,
          "A interface web da Elastic Stack consulta e apresenta os dados do Elasticsearch. [1]", size=22)
    faixa(s, 0.72, 2.43, 11.89, 0.035, BORDER)
    forma(s, 0.76, 2.85, 0.66, 0.57, fill=TEAL_TINT, line=TEAL, tipo=MSO_SHAPE.CAN,
          nome="Símbolo de armazenamento")
    forma(s, 8.53, 2.87, 0.69, 0.49, fill=None, line=TEAL, tipo=MSO_SHAPE.RECTANGLE,
          nome="Símbolo de navegador")
    faixa(s, 8.53, 2.99, 0.69, 0.035, TEAL)
    texto(s, 0.72, 3.68, 4.2, 0.54, "Elasticsearch", size=31, bold=True, color=NAVY)
    texto(s, 0.72, 4.36, 4.18, 1.36, [
        P("Armazena documentos JSON.", after=8),
        P("Indexa, pesquisa e agrega.", after=8),
        P(R("API REST · porta 9200", color=MUTED, size=16)),
    ], size=19)
    texto(s, 8.53, 3.68, 4.08, 0.54, "Kibana", size=31, bold=True, color=TEAL)
    texto(s, 8.53, 4.36, 4.08, 1.36, [
        P("Envia consultas ao Elasticsearch.", after=8),
        P("Exibe os resultados.", after=8),
        P(R("Navegador · porta 5601", color=MUTED, size=16)),
    ], size=19)
    for y, legenda, origem, destino, cor in (
        (3.94, "Consultas", 8.13, 5.02, TEAL),
        (4.87, "Resultados", 5.02, 8.13, NAVY),
    ):
        texto(s, 5.02, y - 0.35, 3.11, 0.29, legenda, size=16, color=MUTED, align=PP_ALIGN.CENTER)
        seta(s, origem, y, destino, y, cor=cor, largura=2)
    faixa(s, 0.72, 6.17, 11.89, 0.64, TEAL_TINT)
    texto(s, 0.91, 6.30, 11.48, 0.37,
          "Elasticsearch, Logstash e Kibana usam a versão 9.5.5 na demonstração.", size=17, bold=True, color=NAVY)
    notas(s, "O Elasticsearch armazena e pesquisa. O Kibana consulta o Elasticsearch e mostra o resultado. "
             "A mesma versão nos três componentes facilita a compatibilidade. A demonstração usa 9.5.5.", refs=(1, 20))


def slide_dados(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Documentos e índices")
    texto(s, 0.72, 1.52, 7.01, 0.36, "Uma linha em eventos.jsonl", size=18, bold=True, color=NAVY)
    codigo(s, 0.72, 1.96, 7.02, 0.65,
           ['{"@timestamp":"2026-10-29T14:05:12Z","log":{…}}'], size=15, nome="Trecho ilustrativo do JSONL")
    seta(s, 1.08, 2.72, 1.08, 3.22, cor=TEAL, largura=2)
    texto(s, 1.34, 2.83, 6.2, 0.33, "O Logstash lê a linha com o codec json.", size=16, color=MUTED)
    texto(s, 0.72, 3.42, 7.02, 0.38, "Documento indexado", size=18, bold=True, color=NAVY)
    codigo(s, 0.72, 3.87, 7.02, 1.82, [
        "{",
        '  "@timestamp": "2026-10-29T14:05:12.000Z",',
        '  "log": {"level": "Error"},',
        '  "winlog": {"record_id": 50123}',
        "}",
    ], size=15, nome="Exemplo ilustrativo de documento")
    texto(s, 0.72, 5.83, 7.02, 0.32, "Exemplos ilustrativos do formato.", size=15, color=MUTED)
    faixa(s, 8.04, 1.51, 0.035, 4.56, BORDER)
    texto(s, 8.40, 1.56, 4.21, 0.47, "Índice", size=24, bold=True, color=TEAL)
    texto(s, 8.40, 2.04, 4.21, 0.63, [P(R("windows-events", font=CODE, size=16)), P("Conjunto de documentos")],
          size=17, color=NAVY)
    texto(s, 8.40, 2.91, 4.21, 0.47, "Documento", size=24, bold=True, color=TEAL)
    texto(s, 8.40, 3.39, 4.21, 0.34, "Um evento representado em JSON", size=17)
    texto(s, 8.40, 4.11, 4.21, 0.47, "Campos", size=24, bold=True, color=TEAL)
    for i, (nome, tipo) in enumerate((("@timestamp", "date"), ("log.level", "keyword"), ("winlog.record_id", "long"))):
        y = 4.65 + i * 0.39
        texto(s, 8.40, y, 2.60, 0.35, nome, size=16, font=CODE)
        texto(s, 11.10, y, 1.51, 0.35, tipo, size=16, font=CODE, bold=True, color=TEAL)
    faixa(s, 0.72, 6.38, 11.89, 0.035, BORDER)
    texto(s, 0.72, 6.54, 11.89, 0.35, "Em uma releitura, o mesmo ID atualiza o documento do evento.",
          size=18, bold=True, color=NAVY)
    notas(s, "Cada linha é um objeto JSON. O Logstash lê a linha e envia um documento ao índice windows-events. "
             "O índice reúne documentos. O documento representa um evento. Cada campo tem um tipo definido no "
             "mapeamento. keyword serve para agrupar e filtrar por valor exato, date para a linha do tempo e long "
             "para números inteiros como o RecordId. O exemplo mostra parte do documento. O ID estável mantém um "
             "documento por evento mesmo se o arquivo for relido.", refs=(2, 12))


def slide_ferramentas(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Ferramentas do Kibana")
    ferramentas = (
        ("▤", "Data View", "Indica o índice e o campo de tempo."),
        ("⌕", "Discover", "Explora e filtra os documentos."),
        ("▥", "Lens", "Sugere um gráfico a partir dos campos."),
        ("▦", "Dashboard", "Reúne gráficos com filtros em comum."),
    )
    for i, (icone, nome, funcao) in enumerate(ferramentas):
        y = 1.64 + i * 1.22
        faixa(s, 0.72, y + 1.02, 4.98, 0.025, BORDER)
        texto(s, 0.72, y + 0.05, 0.50, 0.43, icone, font="Segoe UI Symbol", size=23, color=TEAL)
        texto(s, 1.32, y, 4.4, 0.43, nome, size=23, bold=True, color=NAVY)
        texto(s, 1.32, y + 0.48, 4.37, 0.48, funcao, size=17)
    tem_captura = captura(s, "discover.png", 5.99, 1.58, 6.62, 3.52)
    if tem_captura:
        y_kql = 5.60
        texto(s, 5.99, 5.21, 6.62, 0.29, "Discover com o Data View Eventos do Windows", size=14, color=MUTED)
    else:
        y_kql = 2.72
        texto(s, 5.99, 1.72, 6.62, 0.72, "Filtro no Discover", size=30, bold=True, color=TEAL)
    texto(s, 5.99, y_kql + 0.13, 6.62, 0.36, "KQL · Filtro por nível", size=18, bold=True, color=NAVY)
    codigo(s, 5.99, y_kql + 0.58, 6.62, 0.64, ['log.level : "Error"'], size=17, nome="Consulta KQL")
    fala = ("Data View diz ao Kibana qual índice usar e qual é o campo de tempo. Discover explora e filtra "
            "documentos. Lens transforma um campo em gráfico. Dashboard reúne as visualizações e compartilha o tempo "
            "e os filtros. Use KQL para filtrar. Outro exemplo é log.level : \"Warning\" or log.level : \"Error\".")
    if tem_captura:
        fala += "\n\nImagem: Discover no Kibana, com as colunas @timestamp, log.level e event.code."
    notas(s, fala, refs=(3, 4, 5, 6, 7))


def slide_arquitetura(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Arquitetura da demonstração")
    faixa(s, 0.62, 1.66, 6.20, 4.16, LIGHT)
    faixa(s, 6.95, 1.66, 5.77, 4.16, TEAL_TINT)
    texto(s, 0.80, 1.92, 5.65, 0.48, "Windows", size=23, bold=True, color=NAVY)
    texto(s, 7.11, 1.92, 5.42, 0.48, "Docker Compose", size=23, bold=True, color=TEAL)

    componentes = (
        ("Windows\nEvent Log", "Application", 1.73, WHITE, NAVY),
        ("PowerShell", "Get-WinEvent", 1.76, WHITE, NAVY),
        ("JSONL", "eventos.jsonl", 1.66, WHITE, NAVY),
        ("Logstash", "Ingestão", 1.46, SLATE, WHITE),
        ("Elasticsearch", "windows-events", 1.98, NAVY, WHITE),
        ("Kibana", "Painel web", 1.47, TEAL, WHITE),
    )
    x = 0.76
    posicoes = []
    for nome, detalhe, largura, fundo, cor in componentes:
        linhas = [P(R(linha, size=18, bold=True), after=0) for linha in nome.splitlines()]
        linhas.append(P(R(detalhe, size=13), before=5))
        forma(s, x, 2.75, largura, 1.44, fill=fundo, tipo=MSO_SHAPE.RECTANGLE,
              nome=nome.replace("\n", " "), paragrafos=linhas,
              color=cor, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margens=(0.05, 0.04, 0.05, 0.04))
        posicoes.append((x, largura))
        x += largura + 0.36
    for (origem, largura), (destino, _) in zip(posicoes, posicoes[1:]):
        seta(s, origem + largura + 0.05, 3.47, destino - 0.05, 3.47, cor=TEAL, largura=1.7)
    x_es, w_es = posicoes[4]
    x_kibana, w_kibana = posicoes[5]
    seta(s, x_kibana + w_kibana / 2, 4.81, x_es + w_es / 2, 4.81, cor=NAVY, largura=1.65)
    texto(s, 8.76, 5.03, 3.77, 0.43, "Consulta do Kibana ao Elasticsearch", size=15,
          color=NAVY, align=PP_ALIGN.CENTER)
    texto(s, 0.84, 4.89, 5.71, 0.58, "Coleta a cada 15 s e retomada pelo checkpoint.", size=17, color=MUTED)
    texto(s, 0.72, 6.17, 11.89, 0.52,
          "O coletor roda no Windows para ler o canal Aplicativo. O Logstash acompanha o arquivo no Docker.",
          size=18, color=TEXT)
    notas(s, "No Windows, o coletor lê o canal Application com Get-WinEvent a cada 15 segundos e grava eventos.jsonl. "
             "Ele fica fora do Docker porque lê o log do próprio computador. No Docker, o Logstash acompanha "
             "o arquivo e envia ao Elasticsearch. O Kibana consulta o índice e mostra os resultados. "
             "O Elasticsearch expõe a API local na porta 9200 e o Kibana fica no navegador pela porta 5601.",
          refs=(1, 13, 15))


def slide_logstash(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Pipeline do Logstash")
    texto(s, 0.72, 1.48, 11.89, 0.53, "Ingestão contínua com coleta periódica", size=23, bold=True, color=TEAL)
    etapas = (
        ("01", "Entrada", "file + codec json", "Lê as linhas novas do JSONL. O sincedb guarda a posição de leitura."),
        ("02", "Filtro", "mutate", "Remove campos técnicos que o próprio Logstash acrescenta."),
        ("03", "Saída", "elasticsearch", "Grava no índice windows-events com o ID estável de cada evento."),
    )
    for i, (numero, etapa, plugin, descricao) in enumerate(etapas):
        x = 0.72 + i * 4.16
        texto(s, x, 2.32, 0.66, 0.40, numero, size=20, bold=True, color=TEAL)
        texto(s, x, 2.83, 3.52, 0.60, etapa, size=32, bold=True, color=NAVY)
        faixa(s, x, 3.58, 3.57, 0.04, BORDER)
        texto(s, x, 3.80, 3.57, 0.38, plugin, size=17, font=CODE, bold=True, color=TEAL)
        texto(s, x, 4.40, 3.58, 1.12, descricao, size=19)
        if i < len(etapas) - 1:
            seta(s, x + 3.61, 3.10, x + 4.04, 3.10, cor=TEAL, largura=1.7)
    codigo(s, 0.72, 6.10, 11.89, 0.65, ["logstash/pipeline/windows-events.conf"], size=16,
           nome="Arquivo de configuração")
    notas(s, "O Logstash organiza a ingestão em três estágios. A entrada file acompanha o arquivo do coletor "
             "e usa o sincedb para guardar a posição. O codec json transforma cada linha em evento. "
             "O filtro mutate limpa campos técnicos. A saída elasticsearch grava no índice windows-events "
             "com o identificador estável do evento, então releituras atualizam o mesmo documento. "
             "A coleta no Windows ocorre a cada 15 segundos.", refs=(9, 10, 11, 12))


def slide_privacidade(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Dados reais e privacidade")
    colunas = (
        (0.72, "Metadados coletados", TEAL, (
            "Horário em UTC e canal Aplicativo",
            "Provedor de origem e ID do evento",
            "RecordId e nível do evento",
            "Identificador aleatório da instalação",
        )),
        (6.94, "Fora da exportação", RED, (
            "Mensagem completa do evento",
            "Usuário e nome do computador",
            "Processos e dados internos",
            "Canal de Segurança",
        )),
    )
    for x, cabecalho, cor, itens in colunas:
        faixa(s, x, 1.67, 5.67, 0.065, cor)
        texto(s, x, 1.92, 5.67, 0.51, cabecalho, size=25, bold=True, color=NAVY)
        texto(s, x, 2.65, 5.61, 2.77,
              [P(item, bullet=True, bullet_color=cor, after=14) for item in itens], size=20)
    faixa(s, 6.65, 1.94, 0.035, 3.30, BORDER)
    faixa(s, 0.72, 5.55, 11.89, 1.18, LIGHT)
    texto(s, 0.95, 5.75, 11.35, 0.73, [
        P("Amostra inicial dos últimos 7 dias, até 2.000 eventos. Depois, verificação a cada 15 s.", after=7),
        P(R("Horário e provedor podem revelar contexto. ", bold=True), R("A pasta runtime/ fica fora do Git.")),
    ], size=17, color=NAVY)
    notas(s, "Coletamos apenas os metadados selecionados do canal Aplicativo. Mensagem, usuário e nome do computador "
             "ficam de fora, e os eventos não vão para o Git. A primeira leitura cobre até 2.000 eventos "
             "dos últimos sete dias. A partir daí o coletor verifica a cada 15 segundos. "
             "Os totais variam por computador. Metadados também podem revelar contexto. "
             "Pergunta para a demonstração: o que o Windows registrou nesta semana?", refs=(15,))


def slide_transicao(prs, layout):
    s = prs.slides.add_slide(layout)
    fundo_escuro(s)
    titulo(s, "Demonstração prática", cor=WHITE)
    tem_captura = captura(s, "eventos-do-windows.png", 0.72, 1.52, 9.07, 4.95)
    if tem_captura:
        texto(s, 0.72, 6.63, 9.10, 0.31, "Captura do dashboard local. Os valores variam durante a coleta.",
              size=15, color=ON_DARK)
    else:
        texto(s, 0.72, 1.72, 9.07, 0.73, "Eventos do Windows", size=35, bold=True, color=WHITE)
        for i, painel in enumerate(("Total de eventos coletados", "Eventos por nível",
                                   "Eventos por provedor", "Eventos ao longo do tempo")):
            y = 2.66 + i * 0.76
            faixa(s, 0.75, y + 0.13, 0.19, 0.045, CODE_TYPE)
            texto(s, 1.12, y, 8.35, 0.46, painel, size=23, color=ON_DARK)
    faixa(s, 10.05, 1.65, 0.04, 4.85, SLATE)
    texto(s, 10.30, 1.71, 2.30, 0.50, "≈ 5 min", size=28, bold=True, color=CODE_TYPE)
    passos = (
        ("Fonte", "Visualizador de Eventos"),
        ("Ingestão", "JSONL, Logstash e índice"),
        ("Exploração", "Discover e Lens"),
        ("Interação", "Filtros no dashboard"),
    )
    for i, (nome, detalhe) in enumerate(passos):
        y = 2.46 + i * 0.98
        texto(s, 10.30, y, 2.31, 0.36, nome, size=19, bold=True, color=WHITE)
        texto(s, 10.30, y + 0.37, 2.31, 0.45, detalhe, size=15, color=ON_DARK)
    fala = ("Seguir o guia rápido no README e o roteiro detalhado na seção 3 de docs/roteiro_demonstracao.md. "
            "Mostrar o Visualizador de Eventos, religar o coletor e mostrar a linha JSON. Em seguida, explicar "
            "a configuração do Logstash, conferir a contagem no Elasticsearch, filtrar no Discover, criar um "
            "gráfico no Lens pelo campo event.code e aplicar um filtro por clique no dashboard. Relacionar os "
            "passos aos conceitos dos slides 4 a 7.")
    if tem_captura:
        fala += "\n\nImagem: dashboard Eventos do Windows, com os quatro painéis e o intervalo Last 7 days."
    notas(s, fala)


def slide_vantagens(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Vantagens")
    faixa(s, 0.72, 1.73, 4.75, 4.99, TEAL_TINT)
    texto(s, 1.04, 2.16, 4.09, 1.55, "Visualização\nsem programação", size=35, bold=True, color=NAVY)
    texto(s, 1.04, 4.01, 4.10, 2.20, [
        P("O Lens permite criar gráficos pela interface.", after=13),
        P("A coleta e a ingestão usam scripts e configurações."),
    ], size=20)
    itens = (
        ("Integração nativa", "O Elasticsearch executa buscas e agregações."),
        ("Ingestão flexível", "O Logstash combina entradas, filtros e saídas."),
        ("Interatividade", "Tempo e filtros se aplicam ao painel inteiro."),
        ("Recursos gratuitos na demo", "A demonstração funciona com a licença Basic."),
        ("Portabilidade", "Cada computador coleta seus próprios eventos."),
    )
    for i, (nome, descricao) in enumerate(itens):
        y = 1.75 + i * 0.97
        texto(s, 5.90, y, 6.71, 0.38, nome, size=21, bold=True, color=NAVY)
        texto(s, 5.90, y + 0.41, 6.71, 0.37, descricao, size=17)
        if i < len(itens) - 1:
            faixa(s, 5.90, y + 0.83, 6.71, 0.022, BORDER)
    notas(s, "O Kibana permite pesquisar, filtrar e criar gráficos pela interface. A solução completa inclui "
             "um script PowerShell e a configuração do Logstash. O Elasticsearch executa as consultas e "
             "agregações. O Logstash é flexível, os filtros do painel são interativos e os recursos usados "
             "funcionam na licença Basic. O repositório leva o pipeline e o dashboard, e cada computador "
             "coleta os próprios eventos.", refs=(1, 6, 9, 26))


def slide_limitacoes_usos(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Limitações e casos de uso")
    colunas = (
        (0.72, "Limitações da demo", RED, (
            ("Memória", "Três serviços em execução."),
            ("Cadência", "O coletor consulta o Windows a cada 15 s."),
            ("Privacidade", "Só metadados do canal Aplicativo."),
            ("Escopo local", "Um computador e um nó."),
        )),
        (6.91, "Casos de uso", TEAL, (
            ("Suporte e TI", "Investigar falhas recorrentes."),
            ("Observabilidade", "Acompanhar logs em escala."),
            ("Segurança", "Analisar eventos com um SIEM."),
            ("Vários computadores", "Consolidar registros com agentes."),
        )),
    )
    for x, cabecalho, cor, itens in colunas:
        faixa(s, x, 1.64, 5.70, 0.05, cor)
        texto(s, x, 1.91, 5.70, 0.47, cabecalho, size=25, bold=True, color=NAVY)
        for i, (nome, descricao) in enumerate(itens):
            y = 2.62 + i * 0.78
            texto(s, x, y, 5.70, 0.34, nome, size=19, bold=True, color=NAVY)
            texto(s, x, y + 0.35, 5.70, 0.34, descricao, size=17)
    faixa(s, 6.63, 1.89, 0.035, 3.80, BORDER)
    faixa(s, 0.72, 6.06, 11.89, 0.76, RED_TINT)
    texto(s, 0.93, 6.22, 11.44, 0.45, [
        P(R("Segurança desabilitada só na demo local. ", bold=True, color=NAVY),
          R("Em produção, configure autenticação e TLS. [22]")),
    ], size=18)
    notas(s, "A demonstração exige mais memória por usar três serviços. O coletor verifica a cada 15 segundos e "
             "se limita a metadados do canal Aplicativo. A segurança desabilitada é uma simplificação inadequada "
             "para produção. As portas ficam disponíveis somente na máquina local. Em outros projetos, "
             "a stack pode apoiar suporte e TI, observabilidade, segurança e coleta de vários computadores "
             "com agentes.", refs=(1, 22, 27, 28))


def slide_referencias(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Referências")
    grupos = (
        (0.72, "Elastic Stack e Logstash", (
            (1, "The Elastic Stack"),
            (2, "Index fundamentals"),
            (9, "How Logstash Works"),
            (10, "File input plugin"),
            (12, "Elasticsearch output plugin"),
        )),
        (6.91, "Kibana", (
            (3, "Create a data view"),
            (4, "Discover"),
            (5, "KQL"),
            (6, "Lens visualizations"),
            (7, "Dashboards"),
        )),
    )
    for x, titulo_grupo, itens in grupos:
        texto(s, x, 1.70, 5.69, 0.49, titulo_grupo, size=24, bold=True, color=NAVY)
        faixa(s, x, 2.25, 5.68, 0.033, BORDER)
        for i, (numero, fonte) in enumerate(itens):
            texto(s, x, 2.47 + i * 0.50, 5.69, 0.37, [
                P(R(f"[{numero}]".ljust(5), color=MUTED, font=CODE, size=14),
                  R(fonte, color=TEAL, link=FONTES[numero])),
            ], size=19)
    texto(s, 0.72, 5.42, 11.89, 0.42, [
        P(R("Microsoft  ", bold=True, color=NAVY), R("[15]  ", color=MUTED, font=CODE, size=14),
          R("Get-WinEvent", color=TEAL, link=FONTES[15])),
    ], size=20)
    texto(s, 0.72, 6.39, 11.89, 0.37, "Lista completa e datas de acesso em docs/referencias.md.", size=17, color=MUTED)
    notas(s, "Indicar as fontes oficiais da Elastic e da Microsoft. Os links do slide levam às páginas usadas no "
             "seminário. As referências completas, incluindo as datas de acesso, estão em docs/referencias.md.",
          refs=(1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15))


def slide_conclusao(prs, layout):
    s = prs.slides.add_slide(layout)
    fundo_escuro(s)
    titulo(s, "Conclusão", cor=WHITE)
    mensagens = (
        "O Windows fornece os eventos do canal Aplicativo.",
        "O Logstash prepara os registros e o Elasticsearch os indexa.",
        "O Kibana permite investigar os dados com filtros e gráficos.",
    )
    for i, mensagem in enumerate(mensagens):
        y = 1.93 + i * 1.42
        texto(s, 0.72, y, 0.56, 0.42, f"0{i + 1}", size=18, bold=True, color=CODE_TYPE)
        texto(s, 1.47, y - 0.05, 6.49, 1.08, mensagem, size=27, bold=True, color=WHITE)
    faixa(s, 8.46, 1.78, 0.044, 4.56, SLATE)
    texto(s, 8.93, 3.00, 3.76, 0.80, "Perguntas?", size=42, bold=True, color=CODE_TYPE)
    notas(s, "Retomar as três mensagens. O Windows forneceu os eventos. O Logstash preparou os registros e o "
             "Elasticsearch os armazenou. No Kibana, o Data View indicou o índice, o Discover permitiu explorar, "
             "o Lens criou o gráfico e o Dashboard reuniu as visualizações. Foram usados eventos reais coletados "
             "automaticamente, com as mensagens e os identificadores pessoais diretos fora da exportação. "
             "Abrir para perguntas.")


def main(saida=SAIDA):
    prs = Presentation()
    fator = 13.333 / 10
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    ajustar_layouts(prs, fator)
    ajustar_tema(prs)
    layout = next(l for l in prs.slide_layouts if l.name == "Title Only")
    for criar in (slide_capa, slide_problema, slide_o_que_e, slide_dados, slide_ferramentas, slide_arquitetura,
                  slide_logstash, slide_privacidade, slide_transicao, slide_vantagens, slide_limitacoes_usos,
                  slide_referencias, slide_conclusao):
        criar(prs, layout)
    cp = prs.core_properties
    cp.title = "Kibana: explorando eventos reais do Windows com Logstash e Elasticsearch"
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

"""Gera a apresentação editável slides/seminario_kibana.pptx.

Requisito: Python 3 com python-pptx (pip install python-pptx).
Uso, a partir da raiz do repositório:  python slides/gerar_slides.py

Todos os elementos são nativos do PowerPoint (caixas de texto, formas, conectores
e tabela). A única imagem é a captura do dashboard no slide de apoio.
"""
from datetime import datetime
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA / "seminario_kibana.pptx"
CAPTURA = PASTA / "dashboard_kibana.png"
CSV_LINHAS = (PASTA.parent / "data" / "acessos.csv").read_text(encoding="utf-8").splitlines()

# Paleta (o vermelho é o mesmo dos erros 500 no dashboard)
NAVY, TEAL, RED = "1B2A41", "0E7C86", "E34948"
TEXT, MUTED, WHITE = "1F2933", "5B6770", "FFFFFF"
LIGHT, BORDER, TEAL_TINT, RED_TINT = "F2F5F7", "D5DDE3", "E3F1F2", "FCEBEA"
CODE_BG, CODE_TXT, CODE_TYPE, ON_DARK = "17202C", "D9E2EC", "7FD1D8", "C9D6DF"
CODE = "Courier New"

TEMA_CORES = {
    "dk1": TEXT, "lt1": WHITE, "dk2": NAVY, "lt2": LIGHT,
    "accent1": TEAL, "accent2": RED, "accent3": "2A78D6", "accent4": "EDA100",
    "accent5": "4A3AA7", "accent6": MUTED, "hlink": TEAL, "folHlink": "4A3AA7",
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


def estilizar(run, size=None, bold=None, italic=None, color=None, font=None):
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
                      font=est.get("font", par.get("font", font)))


def texto(slide, x, y, w, h, paragrafos, nome=None, **kw):
    caixa_txt = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    preencher(caixa_txt.text_frame, paragrafos, **kw)
    if nome:
        caixa_txt.name = nome
    return caixa_txt


def forma(slide, x, y, w, h, fill=LIGHT, line=None, line_w=1.0, raio=0.06, tipo=MSO_SHAPE.ROUNDED_RECTANGLE,
          dash=None, nome=None, paragrafos=None, **kw):
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
        if dash:
            s.line.dash_style = dash
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if nome:
        s.name = nome
    if paragrafos is not None:
        preencher(s.text_frame, paragrafos, **kw)
    return s


def seta(slide, x1, y1, x2, y2, cor=MUTED, largura=1.75, de=None, para=None, dupla=False, nome=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    if de:
        c.begin_connect(*de)
    if para:
        c.end_connect(*para)
    c.line.color.rgb = rgb(cor)
    c.line.width = Pt(largura)
    ln = c.line._get_or_add_ln()
    for ponta in (["a:headEnd"] if dupla else []) + ["a:tailEnd"]:
        elemento = etree.SubElement(ln, qn(ponta))
        for atributo, valor in (("type", "triangle"), ("w", "med"), ("len", "med")):
            elemento.set(atributo, valor)
    if nome:
        c.name = nome
    return c


def codigo(slide, x, y, w, h, linhas, size=13, nome=None):
    pars = [P(*(l if isinstance(l, list) else [R(l)]), after=0) for l in linhas]
    return forma(slide, x, y, w, h, fill=CODE_BG, raio=0.04, nome=nome, paragrafos=pars, size=size,
                 color=CODE_TXT, font=CODE, after=0, margens=(0.25, 0.18, 0.2, 0.18))


def titulo(slide, texto_titulo, cor=NAVY, size=36):
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.4), Inches(12.13), Inches(0.95)
    preencher(t.text_frame, [P(R(texto_titulo, bold=True))], size=size, color=cor,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)


def notas(slide, texto_notas):
    slide.notes_slide.notes_text_frame.text = texto_notas


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
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY)
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.9), Inches(1.9), Inches(11.5), Inches(1.3)
    preencher(t.text_frame, [P(R("Kibana", bold=True))], size=66, color=WHITE,
              anchor=MSO_ANCHOR.BOTTOM, margens=(0, 0, 0, 0), after=0)
    texto(s, 0.9, 3.3, 11.5, 0.8, [P("Explorando e visualizando logs com Elasticsearch")],
          size=28, color=ON_DARK, margens=(0, 0, 0, 0), nome="Subtítulo")
    texto(s, 0.9, 5.2, 11.5, 1.4, [
        P(R("Seminário técnico · Avaliação de Produto 2", bold=True), color=WHITE),
        P("Projeto de Desenvolvimento de Dashboard Analítico"),
        P("UniSales · 2026"),
    ], size=18, color=ON_DARK, margens=(0, 0, 0, 0), after=4, nome="Identificação acadêmica")
    notas(s, "Apresentar o tema e o grupo. Mensagem: vamos mostrar como transformar logs em respostas "
             "visuais com o Kibana.")


def slide_problema(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "O problema: muitos logs, poucas respostas")
    linhas = ["timestamp,endpoint,method,status_code,…"] + CSV_LINHAS[1:14] + ["…"]
    codigo(s, 0.6, 1.6, 6.5, 4.05, linhas, size=14, nome="Trecho do CSV")
    texto(s, 0.6, 5.75, 6.5, 0.4, [P("Trecho real de data/acessos.csv: 70 linhas só neste exemplo")],
          size=12, color=MUTED, margens=(0, 0, 0, 0))
    perguntas = ["Quantas requisições falharam?", "Em qual endpoint estão os erros?",
                 "A aplicação ficou lenta? Desde quando?", "Houve tentativas de login negadas?"]
    for i, pergunta in enumerate(perguntas):
        y = 1.6 + i * 1.05
        forma(s, 7.45, y, 5.28, 0.9, fill=LIGHT, nome=f"Pergunta {i + 1}",
              paragrafos=[P(R("?  ", bold=True, color=RED, size=22), R(pergunta))],
              size=18, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.2, 0.05), after=0)
    forma(s, 0.6, 6.35, 12.13, 0.7, fill=TEAL_TINT, nome="Necessidade",
          paragrafos=[P(R("É preciso ", color=TEXT), R("guardar", bold=True), R(" os dados de forma pesquisável e "),
                        R("visualizá-los", bold=True), R(" para enxergar padrões."))],
          size=18, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.25, 0.05), after=0)
    notas(s, "Cada requisição vira uma linha de log; em pouco tempo são milhares. Ler linha a linha não responde: "
             "quantos erros, onde, quando, ficou lento? Precisamos guardar de forma pesquisável e visualizar. "
             "Transição: é aqui que entram o Elasticsearch e o Kibana.")


def slide_o_que_e(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "O que é o Kibana")
    texto(s, 0.6, 1.45, 12.13, 0.95, [P(
        R("Interface web da Elastic Stack para "), R("explorar, visualizar e analisar", bold=True),
        R(" os dados armazenados no Elasticsearch. "), R("[1]", color=MUTED, size=14))],
        size=21, color=TEXT, margens=(0, 0, 0, 0))
    forma(s, 0.6, 2.6, 4.9, 3.25, fill=LIGHT, nome="Elasticsearch", paragrafos=[
        P(R("Elasticsearch", bold=True, size=26, color=NAVY), after=12),
        P("Guarda dados como documentos JSON", bullet=True),
        P("Indexa, pesquisa e agrega", bullet=True),
        P("Acesso por API REST · porta 9200", bullet=True),
    ], size=17, margens=(0.3, 0.25, 0.25, 0.2), after=8)
    forma(s, 7.83, 2.6, 4.9, 3.25, fill=LIGHT, nome="Kibana", paragrafos=[
        P(R("Kibana", bold=True, size=26, color=TEAL), after=12),
        P("Interface no navegador · porta 5601", bullet=True),
        P("Discover, Lens e Dashboards", bullet=True),
        P("Não guarda os dados analisados: cada gráfico é uma consulta", bullet=True),
    ], size=17, margens=(0.3, 0.25, 0.25, 0.2), after=8)
    seta(s, 7.7, 3.65, 5.63, 3.65, cor=TEAL, nome="Seta consultas")
    texto(s, 5.55, 3.1, 2.25, 0.45, [P("consultas", align=PP_ALIGN.CENTER)], size=14, color=MUTED,
          margens=(0, 0, 0, 0))
    seta(s, 5.63, 4.85, 7.7, 4.85, cor=NAVY, nome="Seta resultados")
    texto(s, 5.55, 4.95, 2.25, 0.45, [P("resultados", align=PP_ALIGN.CENTER)], size=14, color=MUTED,
          margens=(0, 0, 0, 0))
    forma(s, 0.6, 6.15, 12.13, 0.75, fill=TEAL_TINT, nome="Versões", paragrafos=[P(
        R("Mesma versão em toda a stack [1]: ", bold=True), R("na demonstração, Elasticsearch 9.5.5 e Kibana 9.5.5"))],
        size=17, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.25, 0.05), after=0)
    notas(s, "O Elasticsearch armazena e pesquisa; o Kibana é a interface web que consulta o Elasticsearch e "
             "mostra o resultado. O Kibana não guarda os dados analisados. Os dois precisam estar na mesma versão.")


def slide_dados(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Como os dados ficam no Elasticsearch")
    texto(s, 0.6, 1.45, 6.7, 0.35, [P(R("Uma linha do CSV…", bold=True))], size=15, color=MUTED,
          margens=(0, 0, 0, 0))
    linha_incidente = next(linha for linha in CSV_LINHAS if "T14:11" in linha)
    codigo(s, 0.6, 1.85, 6.7, 0.85, [CSV_LINHAS[0], linha_incidente], size=12.5, nome="Linha do CSV")
    seta(s, 1.4, 2.75, 1.4, 3.3, cor=TEAL, nome="Seta upload")
    texto(s, 1.6, 2.82, 5.6, 0.4, [P("Upload a file (Kibana)")], size=14, color=MUTED, margens=(0, 0, 0, 0))
    texto(s, 0.6, 3.35, 6.7, 0.35, [P(R("…vira um documento JSON no índice acessos", bold=True))], size=15,
          color=MUTED, margens=(0, 0, 0, 0))
    largura = 45
    campos = [
        ('  "@timestamp": "2026-10-01T17:11:00.000Z",', "date"),
        ('  "timestamp": "2026-10-01T14:11:00-03:00",', "date"),
        ('  "endpoint": "/pedidos",', "keyword"),
        ('  "method": "POST",', "keyword"),
        ('  "status_code": 500,', "long"),
        ('  "response_time_ms": 2350', "long"),
    ]
    linhas = ["{"] + [[R(c.ljust(largura)), R(tipo, color=CODE_TYPE, italic=True)] for c, tipo in campos] + ["}"]
    codigo(s, 0.6, 3.75, 6.7, 2.3, linhas, size=13.5, nome="Documento JSON")
    texto(s, 0.6, 6.15, 6.7, 0.4, [P("Em azul-claro: o tipo de cada campo no mapping do índice")], size=12,
          color=MUTED, margens=(0, 0, 0, 0))
    cartoes = [
        ("Índice", "Conjunto de documentos; unidade de armazenamento do Elasticsearch [2]", "acessos · 70 documentos"),
        ("Documento", "Um registro em JSON; aqui, uma requisição", "1 linha do CSV = 1 documento"),
        ("Campo", "Par chave-valor com tipo definido no mapping [2]; o Kibana criou @timestamp",
         "date · keyword · long"),
    ]
    for i, (nome, definicao, exemplo) in enumerate(cartoes):
        forma(s, 7.75, 1.45 + i * 1.85, 4.98, 1.65, fill=LIGHT, nome=nome, paragrafos=[
            P(R(nome, bold=True, size=21, color=NAVY), after=4),
            P(definicao, after=6),
            P(R(exemplo, font=CODE, color=TEAL, size=13)),
        ], size=15, margens=(0.25, 0.15, 0.2, 0.1))
    notas(s, "Uma linha do CSV vira um documento JSON. O índice acessos guarda os 70 documentos; cada chave é "
             "um campo, com tipo definido no mapping. O tipo importa: média só com número, linha do tempo só com "
             "data. O Kibana criou o campo @timestamp, convertido para UTC.")


def slide_ferramentas(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "As ferramentas do Kibana")
    cartoes = [
        ("1", "Data View", "Aponta para o índice e define o campo de tempo [3]", "acessos + @timestamp"),
        ("2", "Discover", "Explora os documentos com busca e filtros [4]", "status_code >= 500"),
        ("3", "Lens", "Cria gráficos arrastando campos e sugere o tipo de gráfico [6]", "endpoints mais acessados"),
        ("4", "Dashboard", "Reúne visualizações; tempo e filtros valem para todas [7]", "Acessos da aplicação"),
    ]
    formas = []
    for i, (num, nome, desc, exemplo) in enumerate(cartoes):
        x = 0.6 + i * 3.13
        formas.append(forma(s, x, 1.6, 2.75, 3.4, fill=LIGHT, nome=nome, paragrafos=[
            P(R(num, bold=True, size=30, color=TEAL), after=2),
            P(R(nome, bold=True, size=23, color=NAVY), after=10),
            P(desc, after=14),
            P(R("Na demo", bold=True, size=12, color=MUTED), after=2),
            P(R(exemplo, font=CODE, size=12.5, color=TEAL)),
        ], size=16, margens=(0.25, 0.2, 0.2, 0.15)))
    for a, b in zip(formas, formas[1:]):
        seta(s, 0, 0, 1, 1, cor=MUTED, largura=1.5, de=(a, 3), para=(b, 1))
    forma(s, 0.6, 5.35, 12.13, 1.05, fill=TEAL_TINT, nome="KQL", paragrafos=[
        P(R("KQL", bold=True, color=TEAL), R(" (Kibana Query Language): linguagem de texto para filtrar dados [5]"),
          after=4),
        P(R("status_code >= 500", font=CODE, size=14), R("      "),
          R('endpoint : "/login" and status_code : 401', font=CODE, size=14)),
    ], size=16, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.08, 0.25, 0.08))
    notas(s, "Data View diz ao Kibana qual índice usar e qual é o campo de tempo. Discover explora e filtra "
             "documentos. Lens transforma um campo em gráfico. Dashboard reúne tudo, com tempo e filtros "
             "compartilhados. KQL é a linguagem simples de filtro que vamos usar.")


def slide_arquitetura(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Arquitetura básica")
    forma(s, 3.25, 1.45, 6.6, 2.7, fill=None, line=MUTED, line_w=1.25, dash=MSO_LINE_DASH_STYLE.DASH,
          raio=0.05, nome="Docker Compose", paragrafos=[P(
              R("Docker Compose · ambiente local · ", color=MUTED), R("docker compose up -d", font=CODE, color=MUTED))],
          size=12, anchor=MSO_ANCHOR.BOTTOM, margens=(0.2, 0.05, 0.2, 0.08), after=0)
    csv = forma(s, 0.6, 1.85, 1.9, 1.6, fill=LIGHT, line=BORDER, nome="Fonte CSV", paragrafos=[
        P(R("Fonte", size=12, color=MUTED), after=2), P(R("acessos.csv", bold=True, color=NAVY)),
        P(R("70 linhas", size=13, color=MUTED))], size=17, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    es = forma(s, 3.4, 1.75, 2.6, 1.8, fill=NAVY, nome="Elasticsearch", paragrafos=[
        P(R("Elasticsearch", bold=True, size=19), after=4), P("índice acessos"), P(R("porta 9200", size=13))],
        size=15, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    kb = forma(s, 7.1, 1.75, 2.6, 1.8, fill=TEAL, nome="Kibana", paragrafos=[
        P(R("Kibana", bold=True, size=19), after=4), P("Data View · Discover"), P("Lens · Dashboard"),
        P(R("porta 5601", size=13))], size=15, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    nav = forma(s, 10.83, 1.85, 1.9, 1.6, fill=LIGHT, line=BORDER, nome="Navegador", paragrafos=[
        P(R("Usuário", size=12, color=MUTED), after=2), P(R("Navegador", bold=True, color=NAVY)),
        P(R("localhost:5601", size=13, color=MUTED))], size=17, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    seta(s, 0, 0, 1, 1, cor=TEAL, de=(csv, 3), para=(es, 1), nome="Seta ingestão")
    texto(s, 2.5, 2.8, 0.72, 0.5, [P("Upload", align=PP_ALIGN.CENTER, after=0),
                                   P("a file", align=PP_ALIGN.CENTER, after=0)], size=11, color=MUTED,
          margens=(0, 0, 0, 0))
    seta(s, 0, 0, 1, 1, cor=MUTED, de=(kb, 1), para=(es, 3), dupla=True, nome="Seta consultas")
    texto(s, 6.0, 2.15, 1.1, 0.5, [P("consultas", align=PP_ALIGN.CENTER)], size=11, color=MUTED,
          margens=(0, 0, 0, 0))
    seta(s, 0, 0, 1, 1, cor=MUTED, de=(nav, 1), para=(kb, 3), dupla=True, nome="Seta HTTP")
    texto(s, 9.9, 2.15, 0.9, 0.5, [P("HTTP", align=PP_ALIGN.CENTER)], size=11, color=MUTED,
          margens=(0, 0, 0, 0))
    etapas = [
        ("1", "Ingestão", "O Kibana lê o CSV, infere os tipos dos campos e envia os documentos [9]"),
        ("2", "Armazenamento e busca", "O Elasticsearch indexa os documentos e responde às consultas"),
        ("3", "Visualização", "O Kibana transforma cliques e filtros em consultas e desenha o resultado"),
    ]
    for i, (num, nome, desc) in enumerate(etapas):
        forma(s, 0.6 + i * 4.11, 4.5, 3.91, 1.5, fill=LIGHT, nome=f"Etapa {num}", paragrafos=[
            P(R(num + "  ", bold=True, size=24, color=TEAL), R(nome, bold=True, size=19, color=NAVY), after=6),
            P(desc)], size=15, margens=(0.25, 0.15, 0.2, 0.1))
    texto(s, 0.6, 6.25, 12.13, 0.45, [P(
        "Em produção, a ingestão costuma usar Elastic Agent, Logstash ou as APIs do Elasticsearch [1].")],
        size=13, color=MUTED, margens=(0, 0, 0, 0))
    notas(s, "CSV, Elasticsearch, Kibana e navegador. Elasticsearch e Kibana rodam em containers com um único "
             "comando. Na demo, a ingestão é o Upload a file do Kibana; em produção, Elastic Agent, Logstash "
             "ou APIs.")


def slide_demonstracao(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Nossa demonstração")
    texto(s, 0.6, 1.35, 12.13, 0.45, [P("Um dia de acessos de uma loja virtual fictícia")], size=18,
          color=MUTED, margens=(0, 0, 0, 0))
    numeros = [("70", "requisições"), ("5", "endpoints"), ("4", "códigos de status HTTP"),
               ("10 h", "de acessos em 01/10/2026")]
    for i, (valor, rotulo) in enumerate(numeros):
        x, y = 0.6 + (i % 2) * 2.62, 2.0 + (i // 2) * 1.75
        forma(s, x, y, 2.42, 1.55, fill=LIGHT, nome=f"Indicador {rotulo}", paragrafos=[
            P(R(valor, bold=True, size=38, color=TEAL), after=0), P(rotulo)],
            size=14, margens=(0.25, 0.15, 0.15, 0.05))
    cabecalho = CSV_LINHAS[0].split(",")
    horarios = ("T08:03", "T08:24", "T09:17", "T14:11", "T17:29")
    amostra = [linha.split(",") for linha in CSV_LINHAS[1:] if any(h in linha for h in horarios)]
    larguras = [2.15, 1.1, 0.8, 1.05, 1.7]
    x_tabela = 12.73 - sum(larguras)
    quadro = s.shapes.add_table(len(amostra) + 1, len(cabecalho), Inches(x_tabela), Inches(2.0),
                                Inches(sum(larguras)), Inches(0.4 * (len(amostra) + 1)))
    quadro.name = "Amostra do CSV"
    tabela = quadro.table
    for j, w in enumerate(larguras):
        tabela.columns[j].width = Inches(w)
    for i, linha in enumerate([cabecalho] + amostra):
        tabela.rows[i].height = Inches(0.4)
        for j, valor in enumerate(linha):
            cel = tabela.cell(i, j)
            cel.fill.solid()
            if i == 0:
                cel.fill.fore_color.rgb = rgb(NAVY)
            else:
                cel.fill.fore_color.rgb = rgb(RED_TINT if linha[3] == "500" else (WHITE if i % 2 else LIGHT))
            numerico = j >= 3 and i > 0
            preencher(cel.text_frame, [P(R(valor, bold=(i == 0)), align=PP_ALIGN.RIGHT if numerico else PP_ALIGN.LEFT)],
                      size=12, color=WHITE if i == 0 else TEXT, anchor=MSO_ANCHOR.MIDDLE,
                      margens=(0.08, 0.03, 0.08, 0.03), after=0)
    texto(s, x_tabela, 4.5, 6.8, 0.4, [P("Amostra de data/acessos.csv (5 de 70 linhas)")], size=12, color=MUTED,
          margens=(0, 0, 0, 0))
    texto(s, x_tabela, 4.95, 6.8, 0.75, [
        P(R("Status: ", bold=True), R("200 sucesso · 401 não autorizado · 404 não encontrado · 500 erro interno"))],
        size=14, color=TEXT, margens=(0, 0, 0, 0))
    forma(s, 0.6, 5.95, 12.13, 0.95, fill=TEAL_TINT, nome="Pergunta-guia", paragrafos=[P(
        R("Pergunta-guia: ", bold=True), R("o que aconteceu com a aplicação nesse dia?"))],
        size=22, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.3, 0.05, 0.3, 0.05), after=0)
    notas(s, "Dataset: 70 requisições fictícias de uma loja virtual em 01/10/2026, das 8h às 18h. Status 200, "
             "401, 404 e 500 e tempo de resposta em ms. Lançar a pergunta-guia sem revelar o incidente.")


def slide_transicao(prs, layout):
    s = prs.slides.add_slide(layout)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY)
    titulo(s, "Demonstração prática", cor=WHITE)
    texto(s, 0.6, 1.4, 12.13, 0.5, [P("Ao vivo no Kibana 9.5.5 · cerca de 5 minutos")], size=20, color=ON_DARK,
          margens=(0, 0, 0, 0))
    passos = [
        ("CSV", "o arquivo de logs"), ("Upload a file", "o CSV vira o índice acessos"),
        ("Discover", "70 documentos"), ("Filtro KQL", "status_code >= 500"),
        ("Lens", "endpoints mais acessados"), ("Dashboard", "visão geral e filtro por clique"),
    ]
    passo = 12.13 / 6
    for i, (nome, desc) in enumerate(passos):
        cx = 0.6 + passo * i + passo / 2
        forma(s, cx - 0.45, 2.9, 0.9, 0.9, fill=TEAL, tipo=MSO_SHAPE.OVAL, nome=f"Passo {i + 1}",
              paragrafos=[P(R(str(i + 1), bold=True), align=PP_ALIGN.CENTER)], size=24, color=WHITE,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)
        if i < len(passos) - 1:
            seta(s, cx + 0.55, 3.35, cx + passo - 0.55, 3.35, cor=ON_DARK, largura=1.25)
        texto(s, cx - passo / 2 + 0.05, 4.05, passo - 0.1, 1.6, [
            P(R(nome, bold=True, size=18, color=WHITE), align=PP_ALIGN.CENTER, after=6),
            P(desc, align=PP_ALIGN.CENTER)], size=14, color=ON_DARK, margens=(0, 0, 0, 0))
    texto(s, 0.6, 6.3, 12.13, 0.5, [P("Roteiro detalhado e plano de contingência: docs/roteiro_demonstracao.md")],
          size=13, color=ON_DARK, margens=(0, 0, 0, 0))
    notas(s, "Seguir docs/roteiro_demonstracao.md, seção 2: CSV, Upload a file, Discover (Search entire time range), "
             "KQL status_code >= 500, Lens pelo campo endpoint (Visualize), salvar no dashboard e clicar na barra "
             "vermelha das 14h. Ao final, ligar cada passo aos conceitos.")


def slide_vantagens(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Vantagens")
    itens = [
        ("Sem código", "Pesquisar, filtrar e criar gráficos pela interface"),
        ("Integração nativa", "Buscas e agregações executadas pelo próprio Elasticsearch"),
        ("Interatividade", "Filtro de tempo global e filtros por clique em todos os painéis"),
        ("Prototipação rápida", "O Lens sugere o gráfico a partir do campo escolhido [6]"),
        ("Essencial gratuito", "Toda a demonstração roda na licença gratuita Basic [17]"),
        ("Portabilidade", "Dashboards exportados e importados em NDJSON [8]"),
    ]
    for i, (lead, desc) in enumerate(itens):
        x, y = 0.6 + (i % 3) * 4.11, 1.6 + (i // 3) * 2.45
        forma(s, x, y, 3.91, 2.2, fill=LIGHT, nome=lead, paragrafos=[
            P(R(str(i + 1), bold=True, size=28, color=TEAL), after=2),
            P(R(lead, bold=True, size=21, color=NAVY), after=6),
            P(desc)], size=16, margens=(0.28, 0.18, 0.25, 0.12))
    notas(s, "Sem código; integração nativa com o Elasticsearch; interatividade; prototipação rápida com o Lens; "
             "o essencial é gratuito; dashboards exportáveis como arquivo, como o deste repositório.")


def slide_limitacoes_usos(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Limitações e exemplos de uso")
    limitacoes = [
        ("Depende do Elasticsearch: ", "os dados precisam ser ingeridos antes"),
        ("Consome recursos: ", "só o Kibana usou cerca de 1,5 GB de RAM nos testes"),
        ("Curva de aprendizado: ", "mapping, linguagens de consulta, muitos menus"),
        ("Segurança exige configuração: ", "desligada aqui só por didática [14]"),
        ("Recursos avançados pagos: ", "ex.: alertas por detecção de anomalias [17]"),
    ]
    usos = [
        ("Logs de aplicações: ", "erros, lentidão e rotas, como na nossa demo [18]"),
        ("Segurança: ", "logins negados (401) e SIEM com Elastic Security [19]"),
        ("Infraestrutura: ", "métricas de servidores e serviços"),
        ("Negócio: ", "pedidos por hora ou por canal, se os dados estiverem no Elasticsearch"),
    ]
    for x, cabecalho, cor, itens, nome in ((0.6, "Limitações", RED, limitacoes, "Limitações"),
                                           (6.78, "Exemplos de uso", TEAL, usos, "Exemplos de uso")):
        pars = [P(R(cabecalho, bold=True, size=24, color=cor), after=12)]
        pars += [P(R(lead, bold=True, color=NAVY), R(resto), bullet=True, bullet_color=cor, after=10)
                 for lead, resto in itens]
        forma(s, x, 1.6, 5.95, 4.9, fill=LIGHT, nome=nome, paragrafos=pars, size=17,
              margens=(0.3, 0.25, 0.3, 0.15))
    notas(s, "Limitações: depende do Elasticsearch, consome memória, tem curva de aprendizado, segurança exige "
             "configuração e há recursos pagos. Usos: logs de aplicações, segurança, infraestrutura e negócio.")


def slide_conclusao(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Conclusão e referências")
    mensagens = [
        "O Kibana é a camada visual do Elasticsearch: do dado bruto ao dashboard, sem programar.",
        "Data View conecta, Discover explora, Lens visualiza e Dashboard reúne.",
        "Na demo, 70 linhas de CSV revelaram um incidente às 14h no endpoint /pedidos.",
    ]
    for i, msg in enumerate(mensagens):
        y = 1.6 + i * 1.42
        forma(s, 0.6, y, 6.2, 1.25, fill=LIGHT, nome=f"Mensagem {i + 1}", paragrafos=[P(msg)],
              size=17, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(1.05, 0.05, 0.25, 0.05), after=0)
        forma(s, 0.85, y + 0.32, 0.6, 0.6, fill=TEAL, tipo=MSO_SHAPE.OVAL, nome=f"Número {i + 1}",
              paragrafos=[P(R(str(i + 1), bold=True), align=PP_ALIGN.CENTER)], size=20, color=WHITE,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)
    texto(s, 0.6, 6.0, 6.2, 0.7, [P(R("Obrigado! Perguntas?", bold=True))], size=26, color=TEAL,
          anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0))
    refs = [
        ("The Elastic Stack", "elastic.co/docs/get-started/the-stack"),
        ("Index fundamentals", "elastic.co/docs/manage-data/data-store/index-basics"),
        ("Create a data view", "elastic.co/docs/explore-analyze/find-and-organize/data-views"),
        ("Discover", "elastic.co/docs/explore-analyze/discover"),
        ("Lens visualizations", "elastic.co/docs/explore-analyze/visualize/lens"),
        ("Dashboards", "elastic.co/docs/explore-analyze/dashboards"),
        ("Upload data files", "elastic.co/docs/manage-data/ingest/upload-data-files"),
        ("Kibana release notes", "elastic.co/docs/release-notes/kibana"),
    ]
    pars = [P(R("Referências principais", bold=True, size=18, color=NAVY), after=8)]
    for titulo_ref, url in refs:
        pars += [P(R("ELASTIC. "), R(titulo_ref, bold=True), R("."), after=0),
                 P(R(url, color=MUTED), after=6)]
    pars.append(P(R("Lista completa (19 fontes, acesso em 7 out. 2026): docs/referencias.md", italic=True,
                    color=MUTED), before=2))
    forma(s, 7.1, 1.6, 5.63, 5.3, fill=LIGHT, nome="Referências", paragrafos=pars, size=11.5,
          margens=(0.25, 0.2, 0.25, 0.1))
    notas(s, "Retomar as três mensagens: o Kibana é a camada visual do Elasticsearch; Data View, Discover, Lens "
             "e Dashboard; na demo, 70 linhas revelaram o incidente das 14h. Referências oficiais da Elastic. "
             "Abrir para perguntas.")


def slide_apoio(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Apoio: resultado esperado da demonstração")
    altura = 5.0
    largura = altura * 2400 / 1350
    imagem = s.shapes.add_picture(str(CAPTURA), Inches((13.333 - largura) / 2), Inches(1.45), height=Inches(altura))
    imagem.name = "Captura do dashboard"
    imagem.line.color.rgb = rgb(BORDER)
    imagem.line.width = Pt(0.75)
    texto(s, 0.6, 6.55, 12.13, 0.4, [P(
        "Dashboard “Acessos da aplicação (logs fictícios)” no Kibana 9.5.5: em vermelho, os erros 500 às 14h",
        align=PP_ALIGN.CENTER)], size=12, color=MUTED, margens=(0, 0, 0, 0))
    notas(s, "Slide de contingência: usar apenas se a demonstração ao vivo e o vídeo falharem.")


def main():
    prs = Presentation()
    fator = 13.333 / 10
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    ajustar_layouts(prs, fator)
    ajustar_tema(prs)
    layout = next(l for l in prs.slide_layouts if l.name == "Title Only")
    for criar in (slide_capa, slide_problema, slide_o_que_e, slide_dados, slide_ferramentas, slide_arquitetura,
                  slide_demonstracao, slide_transicao, slide_vantagens, slide_limitacoes_usos, slide_conclusao,
                  slide_apoio):
        criar(prs, layout)
    cp = prs.core_properties
    cp.title = "Kibana: explorando e visualizando logs com Elasticsearch"
    cp.subject = "Seminário técnico - Projeto de Desenvolvimento de Dashboard Analítico"
    cp.keywords = "Kibana; Elasticsearch; Dashboard; Logs"
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
    prs.save(SAIDA)
    print(f"Gerado: {SAIDA} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()

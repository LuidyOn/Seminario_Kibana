"""Gera a apresentação editável slides/seminario_kibana.pptx.

Requisito: Python 3 com python-pptx (pip install python-pptx).
Uso, a partir da raiz do repositório:  python slides/gerar_slides.py

Todos os elementos são nativos do PowerPoint (caixas de texto, formas e conectores);
não há imagens. Os exemplos de eventos nos slides são ilustrativos: nenhum dado real
do computador é incluído na apresentação.
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


def seta(slide, x1, y1, x2, y2, cor=MUTED, largura=1.75, de=None, para=None, dupla=False, nome=None,
         tipo=MSO_CONNECTOR.STRAIGHT):
    c = slide.shapes.add_connector(tipo, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
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


def cartoes_numerados(s, itens, y, h, tamanho_desc=16):
    """Cartões lado a lado (número, título, descrição, exemplo da demo) ligados por setas."""
    n = len(itens)
    gap = 0.38
    w = (12.13 - gap * (n - 1)) / n
    formas = []
    for i, (num, nome, desc, exemplo) in enumerate(itens):
        x = 0.6 + i * (w + gap)
        pars = [P(R(num, bold=True, size=28, color=TEAL), after=2),
                P(R(nome, bold=True, size=21, color=NAVY), after=8),
                P(desc, after=12)]
        if exemplo:
            pars += [P(R("Na demo", bold=True, size=12, color=MUTED), after=2),
                     P(R(exemplo, font=CODE, size=12, color=TEAL))]
        formas.append(forma(s, x, y, w, h, fill=LIGHT, nome=nome, paragrafos=pars, size=tamanho_desc,
                            margens=(0.25, 0.2, 0.2, 0.15)))
    for a, b in zip(formas, formas[1:]):
        seta(s, 0, 0, 1, 1, cor=MUTED, largura=1.5, de=(a, 3), para=(b, 1))
    return formas


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
    texto(s, 0.9, 3.3, 11.6, 0.8, [P("Explorando eventos reais do Windows com Logstash e Elasticsearch")],
          size=26, color=ON_DARK, margens=(0, 0, 0, 0), nome="Subtítulo")
    texto(s, 0.9, 5.2, 11.5, 1.4, [
        P(R("Seminário técnico · Avaliação de Produto 2", bold=True), color=WHITE),
        P("Projeto de Desenvolvimento de Dashboard Analítico"),
        P("UniSales · 2026"),
    ], size=18, color=ON_DARK, margens=(0, 0, 0, 0), after=4, nome="Identificação acadêmica")
    notas(s, "Apresentar o tema e o grupo. Mensagem: vamos transformar eventos reais do Windows em respostas "
             "visuais com Logstash, Elasticsearch e Kibana.")


def slide_problema(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "O problema: eventos demais para olhar um a um")
    forma(s, 0.6, 1.6, 6.5, 2.45, fill=LIGHT, nome="Visualizador de Eventos", paragrafos=[
        P(R("Visualizador de Eventos do Windows", bold=True, size=21, color=NAVY), after=10),
        P("Cada evento traz nível, data e hora, provedor (fonte) e ID", bullet=True),
        P("Canais separados: Aplicativo, Sistema, Segurança", bullet=True),
        P("A leitura é evento a evento, sem visão de conjunto", bullet=True),
    ], size=17, margens=(0.3, 0.25, 0.25, 0.15), after=8)
    forma(s, 0.6, 4.3, 6.5, 1.59, fill=TEAL_TINT, nome="Escala", paragrafos=[
        P(R("≈ 440 eventos em 24 h", bold=True, size=30, color=TEAL), after=2),
        P("só no canal Aplicativo do computador de testes (medido em 29/10/2026)"),
    ], size=14, color=TEXT, anchor=MSO_ANCHOR.MIDDLE, margens=(0.3, 0.05, 0.25, 0.05))
    perguntas = ["Quantos erros e avisos aconteceram?", "Quais aplicativos mais registram eventos?",
                 "Quando os problemas se concentram?", "Chegou algum evento novo agora?"]
    for i, pergunta in enumerate(perguntas):
        forma(s, 7.45, 1.6 + i * 1.12, 5.28, 0.93, fill=LIGHT, nome=f"Pergunta {i + 1}",
              paragrafos=[P(R("?  ", bold=True, color=RED, size=22), R(pergunta))],
              size=18, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.2, 0.05), after=0)
    forma(s, 0.6, 6.3, 12.13, 0.7, fill=TEAL_TINT, nome="Necessidade",
          paragrafos=[P(R("É preciso ", color=TEXT), R("coletar", bold=True), R(", "), R("guardar", bold=True),
                        R(" de forma pesquisável e "), R("visualizar", bold=True), R(" os eventos."))],
          size=18, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.25, 0.05), after=0)
    notas(s, "O Windows registra eventos o tempo todo; no computador de testes, cerca de 440 por dia só no canal "
             "Aplicativo. No Visualizador de Eventos a leitura é evento a evento: quantos erros, de quais "
             "aplicativos, quando? Transição: precisamos coletar, guardar e visualizar.")


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
        R("Mesma versão em toda a stack [1]: ", bold=True),
        R("na demonstração, Elasticsearch, Logstash e Kibana 9.5.5"))],
        size=17, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.25, 0.05), after=0)
    notas(s, "O Elasticsearch armazena e pesquisa; o Kibana é a interface web que consulta o Elasticsearch e "
             "mostra o resultado. O Kibana não guarda os dados analisados. Toda a stack precisa estar na mesma "
             "versão: 9.5.5 na demonstração.")


def slide_dados(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Como os eventos ficam no Elasticsearch")
    texto(s, 0.6, 1.45, 6.7, 0.35, [P(R("Uma linha do arquivo eventos.jsonl…", bold=True))], size=15,
          color=MUTED, margens=(0, 0, 0, 0))
    codigo(s, 0.6, 1.85, 6.7, 0.62, ['{"@timestamp":"2026-10-29T14:05:12.000Z","log":{…},…}'], size=12.5,
           nome="Linha JSON")
    seta(s, 1.4, 2.52, 1.4, 3.07, cor=TEAL, nome="Seta Logstash")
    texto(s, 1.6, 2.6, 5.6, 0.4, [P("Logstash (codec json)")], size=14, color=MUTED, margens=(0, 0, 0, 0))
    texto(s, 0.6, 3.12, 6.7, 0.35, [P(R("…vira um documento no índice windows-events", bold=True))], size=15,
          color=MUTED, margens=(0, 0, 0, 0))
    largura = 45
    campos = [
        ('  "@timestamp": "2026-10-29T14:05:12.000Z",', "date"),
        ('  "log.level": "Error",', "keyword"),
        ('  "event.provider": "Application Error",', "keyword"),
        ('  "event.code": "1000",', "keyword"),
        ('  "winlog.channel": "Application",', "keyword"),
        ('  "winlog.record_id": 50123', "long"),
    ]
    linhas = ["{"] + [[R(c.ljust(largura)), R(tipo, color=CODE_TYPE, italic=True)] for c, tipo in campos] + ["}"]
    codigo(s, 0.6, 3.5, 6.7, 2.3, linhas, size=13.5, nome="Documento JSON")
    texto(s, 0.6, 5.9, 6.7, 0.75, [P("Exemplo ilustrativo. Em azul-claro: o tipo de cada campo, definido pelo template "
                                     "que o Logstash instala no Elasticsearch.")], size=12, color=MUTED,
          margens=(0, 0, 0, 0))
    cartoes = [
        ("Índice", "Conjunto de documentos; unidade de armazenamento do Elasticsearch [2]", "windows-events"),
        ("Documento", "Um evento do Windows, em JSON", "1 linha do arquivo = 1 documento"),
        ("Campo", "Par chave-valor com tipo definido no mapping [2]", "date · keyword · long"),
    ]
    for i, (nome, definicao, exemplo) in enumerate(cartoes):
        forma(s, 7.75, 1.45 + i * 1.85, 4.98, 1.65, fill=LIGHT, nome=nome, paragrafos=[
            P(R(nome, bold=True, size=21, color=NAVY), after=4),
            P(definicao, after=6),
            P(R(exemplo, font=CODE, color=TEAL, size=13)),
        ], size=15, margens=(0.25, 0.15, 0.2, 0.1))
    notas(s, "Cada linha do arquivo gerado pelo coletor é um objeto JSON; o Logstash a transforma num documento do "
             "índice windows-events. Índice é o conjunto, documento é um evento, campo é cada atributo com seu tipo. "
             "keyword serve para agrupar e filtrar; date, para a linha do tempo. O exemplo é ilustrativo.")


def slide_ferramentas(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "As ferramentas do Kibana")
    cartoes_numerados(s, [
        ("1", "Data View", "Aponta para o índice e define o campo de tempo [3]", "windows-events + @timestamp"),
        ("2", "Discover", "Explora os documentos com busca e filtros [4]", 'log.level : "Error"'),
        ("3", "Lens", "Cria gráficos arrastando campos e sugere o tipo de gráfico [6]", "IDs de evento mais frequentes"),
        ("4", "Dashboard", "Reúne visualizações; tempo e filtros valem para todas [7]", "Eventos do Windows"),
    ], y=1.6, h=3.4)
    forma(s, 0.6, 5.35, 12.13, 1.05, fill=TEAL_TINT, nome="KQL", paragrafos=[
        P(R("KQL", bold=True, color=TEAL), R(" (Kibana Query Language): linguagem de texto para filtrar dados [5]"),
          after=4),
        P(R('log.level : "Error"', font=CODE, size=14), R("      "),
          R('log.level : "Warning" or log.level : "Error"', font=CODE, size=14)),
    ], size=16, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.08, 0.25, 0.08))
    notas(s, "Data View diz ao Kibana qual índice usar e qual é o campo de tempo. Discover explora e filtra "
             "documentos. Lens transforma um campo em gráfico. Dashboard reúne tudo, com tempo e filtros "
             "compartilhados. KQL é a linguagem simples de filtro que vamos usar.")


def slide_logstash(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Logstash: o pipeline de ingestão")
    texto(s, 0.6, 1.45, 12.13, 0.8, [P(
        R("Mecanismo de coleta de dados com pipelines em tempo real "), R("[1]", color=MUTED, size=14),
        R(": cada evento passa por "), R("entrada → filtro → saída", bold=True), R(" "), R("[9]", color=MUTED, size=14))],
        size=20, color=TEXT, margens=(0, 0, 0, 0))
    cartoes_numerados(s, [
        ("1", "Entrada: file", "Lê cada linha nova de eventos.jsonl; o sincedb guarda a posição de leitura [10]",
         "codec => json"),
        ("2", "Filtro: mutate", "Remove campos técnicos acrescentados pelo próprio Logstash",
         "remove_field => [...]"),
        ("3", "Saída: elasticsearch", "Grava no índice; o ID do evento evita documentos duplicados [12]",
         'index => "windows-events"'),
    ], y=2.45, h=3.0)
    forma(s, 0.6, 5.8, 12.13, 0.95, fill=TEAL_TINT, nome="Configuração", paragrafos=[P(
        R("Toda a configuração cabe em um arquivo: ", bold=True),
        R("logstash/pipeline/windows-events.conf", font=CODE, size=15),
        R(" (versionado no repositório)"))],
        size=17, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.25, 0.05, 0.25, 0.05), after=0)
    notas(s, "O Logstash organiza a ingestão em três estágios. Entrada file: acompanha o arquivo do coletor e guarda a "
             "posição no sincedb; o codec json transforma cada linha em evento. Filtro mutate: limpa campos técnicos. "
             "Saída elasticsearch: grava no índice windows-events usando o ID do evento, o que evita duplicatas.")


def slide_arquitetura(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Arquitetura da demonstração")
    forma(s, 0.6, 1.45, 12.13, 1.9, fill=None, line=MUTED, line_w=1.25, dash=MSO_LINE_DASH_STYLE.DASH,
          raio=0.05, nome="Windows", paragrafos=[P(R("Windows (fora do Docker)", color=MUTED))],
          size=12, anchor=MSO_ANCHOR.BOTTOM, margens=(0.2, 0.05, 0.2, 0.06), after=0)
    forma(s, 0.6, 3.75, 12.13, 1.9, fill=None, line=MUTED, line_w=1.25, dash=MSO_LINE_DASH_STYLE.DASH,
          raio=0.05, nome="Docker Compose", paragrafos=[P(
              R("Docker Compose · ambiente local · ", color=MUTED), R("iniciar_demo.ps1", font=CODE, color=MUTED))],
          size=12, anchor=MSO_ANCHOR.BOTTOM, margens=(0.2, 0.05, 0.2, 0.06), after=0)
    caixas = {}
    linha1 = [("Event Log", "Windows Event Log", "canal Application", LIGHT, NAVY),
              ("Coletor", "Coletor PowerShell", "Get-WinEvent a cada 15 s", LIGHT, NAVY),
              ("Arquivo", "eventos.jsonl", "runtime/ (fora do Git)", LIGHT, NAVY)]
    # Faixa de baixo da direita para a esquerda: o arquivo desce direto para o Logstash
    linha2 = [("Kibana", "Kibana", "Dashboard · porta 5601", TEAL, WHITE),
              ("Elasticsearch", "Elasticsearch", "índice windows-events", NAVY, WHITE),
              ("Logstash", "Logstash", "file → elasticsearch", SLATE, WHITE)]
    for y, linha in ((1.62, linha1), (3.92, linha2)):
        for i, (chave, nome, detalhe, fundo, cor) in enumerate(linha):
            caixas[chave] = forma(s, 0.85 + i * 4.11, y, 3.4, 1.12, fill=fundo,
                                  line=BORDER if fundo == LIGHT else None, nome=nome, paragrafos=[
                                      P(R(nome, bold=True, size=19), after=2), P(R(detalhe, size=14))],
                                  size=15, color=cor, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    for a, b in (("Event Log", "Coletor"), ("Coletor", "Arquivo")):
        seta(s, 0, 0, 1, 1, cor=TEAL, de=(caixas[a], 3), para=(caixas[b], 1))
    seta(s, 0, 0, 1, 1, cor=TEAL, de=(caixas["Arquivo"], 2), para=(caixas["Logstash"], 0),
         nome="Seta leitura do arquivo")
    for a, b in (("Logstash", "Elasticsearch"), ("Elasticsearch", "Kibana")):
        seta(s, 0, 0, 1, 1, cor=TEAL, de=(caixas[a], 1), para=(caixas[b], 3))
    notas_arq = [
        ("Incremental", "checkpoint pelo RecordId; novos eventos a cada 15 s"),
        ("Sem duplicatas", "o ID estável do evento vira o ID do documento"),
        ("Privacidade", "só metadados; os eventos não vão para o Git"),
    ]
    for i, (lead, desc) in enumerate(notas_arq):
        forma(s, 0.6 + i * 4.11, 5.9, 3.91, 1.0, fill=LIGHT, nome=f"Nota {lead}", paragrafos=[
            P(R(lead + ": ", bold=True, color=NAVY), R(desc))], size=14, anchor=MSO_ANCHOR.MIDDLE,
              margens=(0.2, 0.05, 0.15, 0.05), after=0)
    notas(s, "No Windows, o coletor lê o canal Application com Get-WinEvent a cada 15 segundos e grava eventos.jsonl. "
             "No Docker, o Logstash lê esse arquivo e envia ao Elasticsearch; o Kibana consulta e mostra. O coletor "
             "fica fora do Docker porque lê o log do próprio computador.")


def slide_demonstracao(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Nossa demonstração: dados reais deste computador")
    colunas = [
        (0.6, "O que coletamos", TEAL, [
            "Horário do evento (UTC)", "Canal Aplicativo (Application)", "Provedor (fonte) e ID do evento",
            "RecordId, o número sequencial do evento", "Nível: Critical, Error, Warning ou Information",
            "Identificador aleatório da instalação"]),
        (6.78, "O que fica de fora", RED, [
            "Mensagem do evento", "Usuário e nome do computador", "Processos e dados internos do evento",
            "Canal de Segurança", "Envio ao Git: a pasta runtime/ é ignorada"]),
    ]
    for x, cabecalho, cor, itens in colunas:
        pars = [P(R(cabecalho, bold=True, size=22, color=cor), after=10)]
        pars += [P(item, bullet=True, bullet_color=cor, after=6) for item in itens]
        forma(s, x, 1.5, 5.95, 3.55, fill=LIGHT, nome=cabecalho, paragrafos=pars, size=17,
              margens=(0.3, 0.22, 0.3, 0.12))
    texto(s, 0.6, 5.25, 12.13, 0.45, [P(
        "Amostra inicial: últimos 7 dias (até 2.000 eventos) · depois, verificação a cada 15 s · "
        "os números variam conforme o computador")], size=14, color=MUTED, margens=(0, 0, 0, 0))
    forma(s, 0.6, 5.85, 12.13, 0.8, fill=TEAL_TINT, nome="Pergunta-guia", paragrafos=[P(
        R("Pergunta-guia: ", bold=True), R("o que o próprio Windows registrou nesta semana?"))],
        size=21, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(0.3, 0.05, 0.3, 0.05), after=0)
    notas(s, "Coletamos apenas metadados do canal Aplicativo; mensagem, usuário e nome do computador ficam de fora, e os "
             "eventos não vão para o Git. Primeira leitura: últimos 7 dias; depois, a cada 15 segundos. Os números "
             "dependem do computador. Lançar a pergunta-guia.")


def slide_transicao(prs, layout):
    s = prs.slides.add_slide(layout)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY)
    titulo(s, "Demonstração prática", cor=WHITE)
    texto(s, 0.6, 1.4, 12.13, 0.5, [P("Ao vivo, com eventos deste computador · cerca de 5 minutos")], size=20,
          color=ON_DARK, margens=(0, 0, 0, 0))
    passos = [
        ("Visualizador de Eventos", "a fonte real"), ("Coletor", "eventos.jsonl"),
        ("Logstash", "lê e envia"), ("Elasticsearch", "guarda e pesquisa"),
        ("Discover", "filtro KQL"), ("Lens", "novo gráfico"), ("Dashboard", "filtro por clique"),
    ]
    passo = 12.13 / len(passos)
    for i, (nome, desc) in enumerate(passos):
        cx = 0.6 + passo * i + passo / 2
        forma(s, cx - 0.4, 2.9, 0.8, 0.8, fill=TEAL, tipo=MSO_SHAPE.OVAL, nome=f"Passo {i + 1}",
              paragrafos=[P(R(str(i + 1), bold=True), align=PP_ALIGN.CENTER)], size=22, color=WHITE,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)
        if i < len(passos) - 1:
            seta(s, cx + 0.48, 3.3, cx + passo - 0.48, 3.3, cor=ON_DARK, largura=1.25)
        texto(s, cx - passo / 2 + 0.04, 3.95, passo - 0.08, 1.6, [
            P(R(nome, bold=True, size=16, color=WHITE), align=PP_ALIGN.CENTER, after=6),
            P(desc, align=PP_ALIGN.CENTER)], size=13, color=ON_DARK, margens=(0, 0, 0, 0))
    texto(s, 0.6, 6.3, 12.13, 0.5, [P("Roteiro detalhado e plano de contingência: docs/roteiro_demonstracao.md")],
          size=13, color=ON_DARK, margens=(0, 0, 0, 0))
    notas(s, "Seguir docs/roteiro_demonstracao.md, seção 3: Visualizador de Eventos, religar o coletor e mostrar os "
             "eventos importados, pipeline do Logstash, contagem no Elasticsearch, Discover com filtro KQL, Lens pelo "
             "campo event.code e dashboard com filtro por clique. Ao final, ligar cada passo aos conceitos.")


def slide_vantagens(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Vantagens")
    itens = [
        ("Sem código", "Pesquisar, filtrar e criar gráficos pela interface"),
        ("Integração nativa", "Buscas e agregações executadas pelo próprio Elasticsearch"),
        ("Ingestão flexível", "O Logstash combina entradas, filtros e saídas por configuração [9]"),
        ("Interatividade", "Filtro de tempo global e filtros por clique em todos os painéis"),
        ("Essencial gratuito", "Toda a demonstração roda na licença gratuita Basic [26]"),
        ("Portabilidade", "Pipeline e dashboard no repositório; cada PC coleta os próprios eventos"),
    ]
    for i, (lead, desc) in enumerate(itens):
        x, y = 0.6 + (i % 3) * 4.11, 1.6 + (i // 3) * 2.45
        forma(s, x, y, 3.91, 2.2, fill=LIGHT, nome=lead, paragrafos=[
            P(R(str(i + 1), bold=True, size=28, color=TEAL), after=2),
            P(R(lead, bold=True, size=21, color=NAVY), after=6),
            P(desc)], size=16, margens=(0.28, 0.18, 0.25, 0.12))
    notas(s, "Sem código; integração nativa com o Elasticsearch; ingestão flexível com o Logstash; interatividade; "
             "o essencial é gratuito; pipeline e dashboard ficam no repositório e cada computador coleta os seus eventos.")


def slide_limitacoes_usos(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Limitações e exemplos de uso")
    limitacoes = [
        ("Mais memória: ", "três serviços (Elasticsearch, Logstash e Kibana)"),
        ("Não é instantâneo: ", "verificação a cada 15 s"),
        ("Escopo restrito: ", "só metadados do canal Aplicativo, por privacidade"),
        ("Segurança exige configuração: ", "desligada aqui só por didática [22]"),
        ("Solução local: ", "um computador, sem alta disponibilidade"),
    ]
    usos = [
        ("Suporte e TI: ", "falhas recorrentes de aplicativos e serviços"),
        ("Logs em escala: ", "solução de observabilidade da Elastic [27]"),
        ("Segurança: ", "SIEM com Elastic Security [28]"),
        ("Vários computadores: ", "agentes enviando ao mesmo Elasticsearch [1]"),
    ]
    for x, cabecalho, cor, itens, nome in ((0.6, "Limitações", RED, limitacoes, "Limitações"),
                                           (6.78, "Exemplos de uso", TEAL, usos, "Exemplos de uso")):
        pars = [P(R(cabecalho, bold=True, size=24, color=cor), after=12)]
        pars += [P(R(lead, bold=True, color=NAVY), R(resto), bullet=True, bullet_color=cor, after=10)
                 for lead, resto in itens]
        forma(s, x, 1.6, 5.95, 4.9, fill=LIGHT, nome=nome, paragrafos=pars, size=17,
              margens=(0.3, 0.25, 0.3, 0.15))
    notas(s, "Limitações: mais memória por serem três serviços, coleta a cada 15 segundos, só metadados do canal "
             "Aplicativo, segurança desligada só por didática e solução local. Usos: suporte e TI, logs em escala, "
             "segurança e vários computadores com agentes.")


def slide_conclusao(prs, layout):
    s = prs.slides.add_slide(layout)
    titulo(s, "Conclusão e referências")
    mensagens = [
        "O Logstash prepara, o Elasticsearch guarda e o Kibana mostra.",
        "Data View conecta, Discover explora, Lens visualiza e Dashboard reúne.",
        "Na demo, eventos reais deste computador chegam ao dashboard automaticamente, sem mensagens nem dados pessoais.",
    ]
    for i, msg in enumerate(mensagens):
        y = 1.6 + i * 1.42
        forma(s, 0.6, y, 5.6, 1.25, fill=LIGHT, nome=f"Mensagem {i + 1}", paragrafos=[P(msg)],
              size=16, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, margens=(1.0, 0.05, 0.2, 0.05), after=0)
        forma(s, 0.82, y + 0.32, 0.6, 0.6, fill=TEAL, tipo=MSO_SHAPE.OVAL, nome=f"Número {i + 1}",
              paragrafos=[P(R(str(i + 1), bold=True), align=PP_ALIGN.CENTER)], size=20, color=WHITE,
              anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0), after=0)
    texto(s, 0.6, 6.0, 5.6, 0.7, [P(R("Obrigado! Perguntas?", bold=True))], size=26, color=TEAL,
          anchor=MSO_ANCHOR.MIDDLE, margens=(0, 0, 0, 0))
    refs = [
        ("ELASTIC", "The Elastic Stack", "elastic.co/docs/get-started/the-stack"),
        ("ELASTIC", "How Logstash Works", "elastic.co/docs/reference/logstash/how-logstash-works"),
        ("ELASTIC", "File input plugin", "elastic.co/docs/reference/logstash/plugins/plugins-inputs-file"),
        ("ELASTIC", "Elasticsearch output plugin",
         "elastic.co/docs/reference/logstash/plugins/plugins-outputs-elasticsearch"),
        ("ELASTIC", "Create a data view", "elastic.co/docs/explore-analyze/find-and-organize/data-views"),
        ("ELASTIC", "Discover", "elastic.co/docs/explore-analyze/discover"),
        ("ELASTIC", "Lens visualizations", "elastic.co/docs/explore-analyze/visualize/lens"),
        ("ELASTIC", "Dashboards", "elastic.co/docs/explore-analyze/dashboards"),
        ("MICROSOFT", "Get-WinEvent",
         "learn.microsoft.com/powershell/module/microsoft.powershell.diagnostics/get-winevent"),
    ]
    pars = [P(R("Referências principais", bold=True, size=18, color=NAVY), after=6)]
    for autor, titulo_ref, url in refs:
        pars += [P(R(autor + ". "), R(titulo_ref, bold=True), R("."), after=0),
                 P(R(url, color=MUTED, size=10.5), after=4)]
    pars.append(P(R("Lista completa (28 fontes, com datas de acesso): docs/referencias.md", italic=True,
                    color=MUTED), before=2))
    forma(s, 6.45, 1.6, 6.28, 5.3, fill=LIGHT, nome="Referências", paragrafos=pars, size=11.5,
          margens=(0.25, 0.18, 0.2, 0.1))
    notas(s, "Retomar as três mensagens: Logstash prepara, Elasticsearch guarda e Kibana mostra; Data View, Discover, "
             "Lens e Dashboard; na demo, dados reais coletados automaticamente, sem mensagens nem dados pessoais. "
             "Referências oficiais da Elastic e da Microsoft. Abrir para perguntas.")


def main():
    prs = Presentation()
    fator = 13.333 / 10
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    ajustar_layouts(prs, fator)
    ajustar_tema(prs)
    layout = next(l for l in prs.slide_layouts if l.name == "Title Only")
    for criar in (slide_capa, slide_problema, slide_o_que_e, slide_dados, slide_ferramentas, slide_logstash,
                  slide_arquitetura, slide_demonstracao, slide_transicao, slide_vantagens, slide_limitacoes_usos,
                  slide_conclusao):
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
    prs.save(SAIDA)
    print(f"Gerado: {SAIDA} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()

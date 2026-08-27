#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de forma e conteudo de arquivos .docx, usando apenas a biblioteca padrao.

Um .docx e um zip contendo XML (word/document.xml, word/styles.xml,
word/footnotes.xml). Este script le esses XML diretamente, resolve a heranca de
estilos (docDefaults -> estilo -> formatacao direta) e produz tres relatorios:

  sumario  -> arvore de titulos com faixas de paragrafos e contagem de palavras
  forma    -> diagnostico de coerencia interna da formatacao
  texto    -> texto corrido com marcadores de paragrafo [P123] e notas de rodape

Uso:
  python analisar_docx.py sumario  "arquivo.docx"
  python analisar_docx.py forma    "arquivo.docx"
  python analisar_docx.py texto    "arquivo.docx" [--de 1] [--ate 400] [--sem-notas]
"""

import argparse
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{%s}" % NS
TWIP_CM = 566.929  # 1 cm = 566.93 twips
TWIP_PT = 20.0     # 1 pt = 20 twips

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------- utilitarios

def val(el, name="val"):
    return el.get(W + name) if el is not None else None


def as_int(v, default=None):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return default


def on(el):
    """Elemento booleano do OOXML: presente = ligado, salvo w:val='0'/'false'."""
    if el is None:
        return None
    v = val(el)
    return v not in ("0", "false", "off")


def cm(twips):
    return twips / TWIP_CM


def merge(*dicts):
    out = {}
    for d in dicts:
        if d:
            out.update({k: v for k, v in d.items() if v is not None})
    return out


# ---------------------------------------------------------------- leitura XML

def read_rpr(rpr):
    d = {}
    if rpr is None:
        return d
    f = rpr.find(W + "rFonts")
    if f is not None:
        v = f.get(W + "ascii") or f.get(W + "hAnsi") or f.get(W + "cs") or f.get(W + "eastAsia")
        if v:
            d["font"] = v
    sz = as_int(val(rpr.find(W + "sz")))
    if sz:
        d["size"] = sz / 2.0
    for tag, key in (("b", "bold"), ("i", "italic"), ("caps", "caps"),
                     ("smallCaps", "smallcaps"), ("u", "underline"),
                     ("strike", "strike")):
        st = on(rpr.find(W + tag))
        if st is not None:
            d[key] = st
    c = rpr.find(W + "color")
    if c is not None and val(c) and val(c) not in ("auto", "000000"):
        d["color"] = val(c)
    h = rpr.find(W + "highlight")
    if h is not None and val(h) not in (None, "none"):
        d["highlight"] = val(h)
    rs = rpr.find(W + "rStyle")
    if rs is not None:
        d["rstyle"] = val(rs)
    return d


def read_ppr(ppr):
    d = {}
    if ppr is None:
        return d
    sp = ppr.find(W + "spacing")
    if sp is not None:
        line = as_int(sp.get(W + "line"))
        if line is not None:
            d["line"] = line
            d["lineRule"] = sp.get(W + "lineRule") or "auto"
        before = as_int(sp.get(W + "before"))
        if before is not None:
            d["before"] = before
        after = as_int(sp.get(W + "after"))
        if after is not None:
            d["after"] = after
    ind = ppr.find(W + "ind")
    if ind is not None:
        for att, key in (("left", "ind_left"), ("start", "ind_left"),
                         ("right", "ind_right"), ("end", "ind_right"),
                         ("firstLine", "ind_first"), ("hanging", "ind_hang")):
            v = as_int(ind.get(W + att))
            if v is not None:
                d[key] = v
    jc = ppr.find(W + "jc")
    if jc is not None:
        d["align"] = val(jc)
    ol = ppr.find(W + "outlineLvl")
    if ol is not None:
        d["outline"] = as_int(val(ol))
    if ppr.find(W + "numPr") is not None:
        d["numbered"] = True
    if ppr.find(W + "pageBreakBefore") is not None:
        d["page_break_before"] = on(ppr.find(W + "pageBreakBefore"))
    ps = ppr.find(W + "pStyle")
    if ps is not None:
        d["style"] = val(ps)
    return d


class Styles:
    """Resolve a cadeia docDefaults -> basedOn -> estilo."""

    def __init__(self, root):
        self.raw = {}
        self.names = {}
        self.based = {}
        self.default_p = {}
        self.default_r = {}
        self.default_style = None
        self._memo = {}
        if root is None:
            return
        dd = root.find(W + "docDefaults")
        if dd is not None:
            rd = dd.find(W + "rPrDefault")
            if rd is not None:
                self.default_r = read_rpr(rd.find(W + "rPr"))
            pd = dd.find(W + "pPrDefault")
            if pd is not None:
                self.default_p = read_ppr(pd.find(W + "pPr"))
        for st in root.findall(W + "style"):
            sid = st.get(W + "styleId")
            if not sid:
                continue
            self.raw[sid] = (read_ppr(st.find(W + "pPr")), read_rpr(st.find(W + "rPr")))
            nm = st.find(W + "name")
            self.names[sid] = val(nm) or sid
            bo = st.find(W + "basedOn")
            if bo is not None:
                self.based[sid] = val(bo)
            if st.get(W + "default") in ("1", "true") and st.get(W + "type") == "paragraph":
                self.default_style = sid

    def resolve(self, sid):
        """(pPr, rPr) acumulados do estilo, seguindo basedOn."""
        if sid is None:
            return {}, {}
        if sid in self._memo:
            return self._memo[sid]
        chain, seen, cur = [], set(), sid
        while cur and cur in self.raw and cur not in seen:
            seen.add(cur)
            chain.append(cur)
            cur = self.based.get(cur)
        ppr, rpr = {}, {}
        for s in reversed(chain):
            p, r = self.raw[s]
            ppr = merge(ppr, p)
            rpr = merge(rpr, r)
        self._memo[sid] = (ppr, rpr)
        return ppr, rpr

    def name(self, sid):
        return self.names.get(sid, sid or "(sem estilo)")


# ------------------------------------------------------------------ paragrafo

HEADING_RE = re.compile(r"^(heading|t[ií]tulo)\s*(\d)", re.I)
MANUAL_NUM_RE = re.compile(r"^\s*(\d+(?:[.\-]\d+)*)[.\-)]?\s+\S")


class Paragraph:
    __slots__ = ("idx", "text", "style", "style_name", "level", "pp", "rp",
                 "runs", "in_table", "notes", "breaks", "page_break")

    def __init__(self):
        self.idx = 0
        self.text = ""
        self.style = None
        self.style_name = ""
        self.level = None
        self.pp = {}
        self.rp = {}
        self.runs = []
        self.in_table = False
        self.notes = []
        self.breaks = 0
        self.page_break = False

    # --- descricoes legiveis -------------------------------------------------

    def line_desc(self):
        p = self.pp
        if "line" not in p:
            return "simples"
        rule = p.get("lineRule", "auto")
        if rule == "auto":
            v = p["line"] / 240.0
            return ("%.2f" % v).rstrip("0").rstrip(".").replace(".", ",")
        return "exato %.0fpt" % (p["line"] / TWIP_PT)

    def indent_desc(self):
        p = self.pp
        parts = []
        le = p.get("ind_left", 0)
        if le:
            parts.append("esq %.2f" % cm(le))
        ri = p.get("ind_right", 0)
        if ri:
            parts.append("dir %.2f" % cm(ri))
        fi = p.get("ind_first", 0)
        ha = p.get("ind_hang", 0)
        if fi:
            parts.append("1a %.2f" % cm(fi))
        if ha:
            parts.append("desloc %.2f" % cm(ha))
        return ("recuo " + " / ".join(parts) + " cm") if parts else "sem recuo"

    def space_desc(self):
        b = self.pp.get("before", 0) / TWIP_PT
        a = self.pp.get("after", 0) / TWIP_PT
        return "antes %.0f / depois %.0f pt" % (b, a)

    def align_desc(self):
        return {"both": "justificado", "left": "esquerda", "right": "direita",
                "center": "centralizado", "start": "esquerda", "end": "direita",
                None: "esquerda (padrao)"}.get(self.pp.get("align"), self.pp.get("align"))

    def font_desc(self):
        f = self.rp.get("font") or "(herdada)"
        s = self.rp.get("size")
        s = ("%.1f" % s).rstrip("0").rstrip(".").replace(".", ",") if s else "?"
        extra = ""
        if self.rp.get("bold"):
            extra += " negrito"
        if self.rp.get("italic"):
            extra += " italico"
        if self.rp.get("caps") or self.rp.get("smallcaps"):
            extra += " versal"
        return "%s %spt%s" % (f, s, extra)

    def signature(self):
        return "%s | entrel %s | %s | %s | %s" % (
            self.font_desc(), self.line_desc(), self.space_desc(),
            self.indent_desc(), self.align_desc())

    def snippet(self, n=90):
        t = re.sub(r"\s+", " ", self.text).strip()
        return t[:n] + ("..." if len(t) > n else "")


def collect_paragraphs(body, styles):
    """Percorre o corpo do documento em ordem, marcando paragrafos de tabela."""
    out = []
    counter = [0]

    def walk(node, in_table):
        for child in node:
            tag = child.tag
            if tag == W + "p":
                counter[0] += 1
                out.append(build_paragraph(child, styles, counter[0], in_table))
            elif tag == W + "tbl":
                walk(child, True)
            elif tag in (W + "sdt", W + "sdtContent", W + "tr", W + "tc",
                         W + "customXml", W + "smartTag"):
                walk(child, in_table)

    walk(body, False)
    return out


def build_paragraph(p, styles, idx, in_table):
    par = Paragraph()
    par.idx = idx
    par.in_table = in_table
    ppr = p.find(W + "pPr")
    direct_p = read_ppr(ppr)
    par.style = direct_p.get("style") or styles.default_style
    par.style_name = styles.name(par.style)
    st_p, st_r = styles.resolve(par.style)
    par.pp = merge(styles.default_p, st_p, direct_p)

    # nivel de titulo: pelo nome do estilo ou pelo outlineLvl
    m = HEADING_RE.match(par.style_name or "")
    if m:
        par.level = int(m.group(2))
    elif par.pp.get("outline") is not None and par.pp["outline"] < 9:
        par.level = par.pp["outline"] + 1

    mark_r = read_rpr(ppr.find(W + "rPr")) if ppr is not None else {}
    texts, run_props = [], []
    for r in p.iter():
        if r.tag == W + "r":
            rpr = r.find(W + "rPr")
            direct_r = read_rpr(rpr)
            eff = merge(styles.default_r, st_r, direct_r)
            if direct_r.get("rstyle"):
                _, cs_r = styles.resolve(direct_r["rstyle"])
                eff = merge(styles.default_r, st_r, cs_r, direct_r)
            chunk = "".join(t.text or "" for t in r.iter(W + "t"))
            for br in r.iter(W + "br"):
                if br.get(W + "type") == "page":
                    par.page_break = True
                else:
                    par.breaks += 1
                    chunk += "\n"
            for _ in r.iter(W + "tab"):
                chunk += "\t"
            if chunk:
                texts.append(chunk)
                run_props.append((len(chunk.strip()), eff))
        elif r.tag == W + "footnoteReference":
            fid = r.get(W + "id")
            if fid:
                par.notes.append(fid)
                texts.append("[nota %s]" % fid)

    par.text = "".join(texts)
    if run_props:
        weight = Counter()
        for n, eff in run_props:
            key = (eff.get("font"), eff.get("size"), bool(eff.get("bold")),
                   bool(eff.get("italic")), bool(eff.get("caps") or eff.get("smallcaps")))
            weight[key] += max(n, 1)
        font, size, b, i, c = weight.most_common(1)[0][0]
        par.rp = {"font": font, "size": size, "bold": b, "italic": i, "caps": c}
        par.runs = run_props
    else:
        par.rp = merge(styles.default_r, st_r, mark_r)
    return par


# ------------------------------------------------------------------ carga

def load(path):
    if not os.path.isfile(path):
        sys.exit("Arquivo nao encontrado: %s" % path)
    z = zipfile.ZipFile(path)
    parts = {}
    for name in ("word/document.xml", "word/styles.xml", "word/footnotes.xml",
                 "word/endnotes.xml"):
        try:
            parts[name] = ET.fromstring(z.read(name))
        except KeyError:
            parts[name] = None
    parts["_names"] = z.namelist()
    z.close()
    return parts


def load_notes(root, styles):
    """Retorna OrderedDict id -> (texto, paragrafos) das notas de rodape."""
    notes = OrderedDict()
    if root is None:
        return notes
    for fn in root.findall(W + "footnote"):
        fid = fn.get(W + "id")
        if fn.get(W + "type") in ("separator", "continuationSeparator", "continuationNotice"):
            continue
        pars = []
        for i, p in enumerate(fn.findall(W + "p"), 1):
            pars.append(build_paragraph(p, styles, i, False))
        txt = " ".join(x.text for x in pars).strip()
        notes[fid] = (txt, pars)
    return notes


def page_setup(body):
    sect = None
    for el in body:
        if el.tag == W + "sectPr":
            sect = el
    if sect is None:
        return None
    mar = sect.find(W + "pgMar")
    sz = sect.find(W + "pgSz")
    out = {}
    if mar is not None:
        for a in ("top", "right", "bottom", "left", "header", "footer", "gutter"):
            v = as_int(mar.get(W + a))
            if v is not None:
                out[a] = cm(v)
    if sz is not None:
        out["w"] = cm(as_int(sz.get(W + "w"), 0))
        out["h"] = cm(as_int(sz.get(W + "h"), 0))
    return out


def words(t):
    return len([w for w in re.split(r"\s+", t) if w.strip(".,;:()[]—-")])


# ------------------------------------------------------------- classificacao

TOC_TAIL_RE = re.compile(r"[\t.…]\s*\d{1,4}\s*$")
CODE_RE = re.compile(r"^\s*(import |from \w+ import|def |class |print\(|#|//|<\?|\{|\}|</?\w+>)")


def is_body(p):
    return (p.level is None and not p.in_table and p.text.strip()
            and len(p.text.strip()) > 60)


def is_toc_entry(p):
    """Linha de sumario automatico ou digitado (titulo + numero de pagina)."""
    name = (p.style_name or "").lower()
    if name.startswith("toc") or "sumario" in name or "sumário" in name:
        return True
    t = p.text.strip()
    # o pontilhado de preenchimento infla o comprimento; some antes de medir
    t = re.sub(r"[.…_]{4,}", " ", t).strip()
    return bool(t and len(t) < 200 and TOC_TAIL_RE.search(t))


def looks_like_code(p):
    t = p.text.strip()
    if not t:
        return False
    if CODE_RE.match(t):
        return True
    simbolos = sum(1 for c in t if c in "{}[]()=;<>_|/\\`")
    return simbolos / len(t) > 0.06


def is_pseudo_heading(p, body_size):
    """Paragrafo curto formatado a mao como titulo, sem estilo de titulo."""
    t = p.text.strip()
    if p.level is not None or not t or len(t) > 130 or p.in_table:
        return False
    if is_toc_entry(p) or looks_like_code(p):
        return False
    if t.endswith((".", ";", ",", ":")) and not MANUAL_NUM_RE.match(t):
        return False
    marked = (p.rp.get("bold") or p.rp.get("caps")
              or (body_size and p.rp.get("size") and p.rp["size"] > body_size))
    return bool(marked) or bool(MANUAL_NUM_RE.match(t) and len(t) < 90)


def is_long_citation(p, body_size, body_start=0):
    """Recuo de citacao longa. So vale depois do inicio do texto: antes disso
    estao folha de rosto e ficha, que tambem usam recuos grandes."""
    if p.level is not None or not p.text.strip() or p.in_table:
        return False
    if p.idx < body_start or looks_like_code(p):
        return False
    left = p.pp.get("ind_left", 0)
    smaller = body_size and p.rp.get("size") and p.rp["size"] < body_size
    return (left >= 1500 and len(p.text.strip()) > 120) or bool(smaller and left > 500)


FIM_TEXTO_RE = re.compile(
    r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA|OBRAS CITADAS|AP[ÊE]NDICES?|ANEXOS?)\b", re.I)
PRE_TEXTUAL_RE = re.compile(
    r"^\s*(SUM[ÁA]RIO|[ÍI]NDICE|LISTA DE|RESUMO|ABSTRACT|RESUMEN|AGRADECIMENTOS?|"
    r"DEDICAT[ÓO]RIA|EP[ÍI]GRAFE|FICHA CATALOGR)", re.I)


def first_heading_idx(pars):
    """Início do texto principal. Prefere o primeiro título numerado, porque
    SUMÁRIO e LISTA DE ... costumam ter estilo de título e vêm antes."""
    heads = [p for p in pars if p.level is not None and p.text.strip()]
    for p in heads:
        if re.match(r"^\s*\d", p.text.strip()):
            return p.idx
    for p in heads:
        if not PRE_TEXTUAL_RE.match(p.text.strip()):
            return p.idx
    return heads[0].idx if heads else 0


def last_body_idx(pars, body_start):
    """Primeiro parágrafo pós-textual (referências, apêndice, anexo). O texto
    principal termina aí: lista de referências não é prosa argumentativa."""
    for p in pars:
        t = p.text.strip()
        if p.idx <= body_start or not t or is_toc_entry(p):
            continue
        if FIM_TEXTO_RE.match(t) and (p.level is not None or len(t) < 60):
            return p.idx
    return len(pars) + 1


LEGENDA_RE = re.compile(r"^\s*(Gr[áa]fico|Tabela|Figura|Quadro|Esquema|Imagem)\s*(\d+)", re.I)
FONTE_RE = re.compile(r"^\s*(Fonte|Nota|Legenda|Obs)\b", re.I)
ITEM_RE = re.compile(r"^\s*([-•–•]|\(?[a-z]\)|\(?[ivx]+\)|\d+[.)])\s+", re.I)
ABREV_RE = re.compile(
    r"\b(art|arts|inc|p|pp|n|no|nº|cf|op|cit|ed|orgs?|coord|séc|sec|vol|fl|fls|"
    r"Dr|Dra|Sr|Sra|Prof|Min|Rel|Ex|Exmo|ss|séss|ap|ac)\.", re.I)
NUM_RE = re.compile(r"\d")
TOKEN_NUM_RE = re.compile(r"^[(\[]?[R$€]?\s?\d[\d.,]*\s?%?[)\]]?[.,;:]?$")
INFERENCIA_RE = re.compile(
    r"\b(portanto|logo|assim sendo|por isso|de modo que|razão pela qual|"
    r"(isso|o que|que) (indica|sugere|revela|significa|explica|demonstra|evidencia|confirma|contraria|implica|permite)|"
    r"conclui-se|depreende-se|infere-se|deduz-se|explica-se|decorre|"
    r"evidencia que|demonstra que|confirma a|contraria a|refuta|corrobora|"
    r"permite (afirmar|concluir|supor|sustentar)|na medida em que|uma vez que|"
    r"porque|dado que|visto que|isto se deve|a explicação|a hipótese|"
    r"contraintuitiv|surpreend|chama a atenção|destaca-se que|o ponto relevante)",
    re.I)
PRESENTACIONAL_RE = re.compile(
    r"\b(representa|corresponde a|totaliz|soma|apresent|foi de|passou de|"
    r"registrou|contabiliz|equivale|perfaz|atingiu|alcançou|verifica-se|observa-se|"
    r"nota-se|percebe-se|conforme o gráfico|conforme a tabela|como se vê)", re.I)


CIT_ANO_RE = re.compile(
    r"\b([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]{2,})\s*(?:et\s+al\.?)?\s*\((\d{4})[a-z]?")
CIT_PAREN_RE = re.compile(
    r"\(\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]{2,})[^)]{0,60}?,\s*(\d{4})[a-z]?")
ASPAS_RE = re.compile(r"[“\"]([^”\"]{4,80})[”\"]")
INSTITUCIONAL = {
    "STF", "STJ", "TSE", "TST", "CNJ", "TCU", "OECD", "OCDE", "BRASIL", "IBGE",
    "IPEA", "ONU", "UNB", "FGV", "CONJUR", "SENADO", "CAMARA", "CÂMARA", "AGU",
    "PGR", "OAB", "ABDF", "CNI", "BANCO", "MINISTERIO", "MINISTÉRIO",
}
NAO_AUTOR = {
    "ANO", "ART", "ARTS", "LEI", "EMENDA", "RESOLUCAO", "RESOLUÇÃO", "TEMA",
    "ADI", "ADC", "ADPF", "MS", "HC", "AGRAVO", "RECURSO", "TABELA", "GRAFICO",
    "GRÁFICO", "FIGURA", "QUADRO", "ESQUEMA", "ANEXO", "APENDICE", "APÊNDICE",
    "EM", "NO", "NA", "DE", "DO", "DA", "PARA", "POR", "COMO", "SEGUNDO",
    "CONFORME", "ENTRE", "ATE", "ATÉ", "DESDE", "AINDA", "APENAS", "ASSIM",
    "ESSE", "ESSA", "ESTE", "ESTA", "AQUELE", "TODOS", "AMBOS", "OUTRO",
    "DURANTE", "APOS", "APÓS", "ANTES", "SOBRE", "COM", "SEM", "SOB", "ANOS",
    "DIAS", "MESES", "PERIODO", "PERÍODO", "CAPITULO", "CAPÍTULO", "SECAO",
    "SEÇÃO", "ITEM", "NOTA", "FONTE", "PAGINA", "PÁGINA", "VOLUME", "EDICAO",
}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.upper())
                   if unicodedata.category(c) != "Mn")


def sentencas(t):
    """Contagem aproximada de frases: neutraliza abreviaturas e numeros."""
    s = ABREV_RE.sub("ABREV", t)
    s = re.sub(r"(?<=\d)[.,](?=\d)", "", s)
    partes = re.split(r"(?<=[.!?])[\s”\")]+(?=[A-ZÀ-ÝÁÉÍÓÚÂÊÔÃÕÇ“(\d])", s.strip())
    return len([p for p in partes if len(p.strip()) > 3]) or 1


def chars_por_linha(ps, size_pt):
    """Caracteres por linha, estimados da mancha real e do corpo da fonte.
    Largura media de caractere em texto corrido = 0,5 em."""
    if not ps or not size_pt:
        return None
    util = ps.get("w", 21.0) - ps.get("left", 3.0) - ps.get("right", 2.0) - ps.get("gutter", 0)
    if util <= 1:
        return None
    return util / (size_pt * 0.01764)


def is_prosa(p, body_size):
    """Paragrafo de prosa argumentativa: exclui item de lista, legenda, chamada
    de enumeracao, pseudo-titulo, codigo, sumario e conteudo de tabela."""
    t = p.text.strip()
    if not is_body(p) or p.in_table:
        return False
    if is_toc_entry(p) or looks_like_code(p) or is_pseudo_heading(p, body_size):
        return False
    if LEGENDA_RE.match(t) or FONTE_RE.match(t) or ITEM_RE.match(t):
        return False
    if t.endswith(":"):
        return False
    return True


def densidade_numerica(t):
    toks = [x for x in re.split(r"\s+", t) if x]
    if not toks:
        return 0.0
    nums = [x for x in toks if TOKEN_NUM_RE.match(x) or x.strip(".,;:") == "%"]
    return len(nums) / len(toks)


def clean_title(t):
    """Normaliza um titulo para comparar sumario com titulos reais."""
    t = TOC_TAIL_RE.sub("", t.strip())
    t = re.sub(r"^\s*\d+(?:[.\-]\d+)*[.\-)]?\s*", "", t)
    t = re.sub(r"[\s.…]+$", "", t)
    return re.sub(r"\s+", " ", t).strip().lower()


# ------------------------------------------------------------------ relatorios

# Papeis que existem, sao contados, e nao se comparam. Cada um varia por
# construcao, e apontar essa variacao produz o falso positivo que enterra o
# achado verdadeiro. Medido numa dissertacao: os tres somam 692 dos 1235 paragrafos
# classificados, e nenhum deles rendeu apontamento que alguem fosse corrigir.
SEM_COMPARACAO = {
    "tabela": "cabecalho, celula de texto e celula de numero sao formas distintas na mesma tabela",
    "pre-textual": "capa, folha de rosto, ficha, dedicatoria e resumo sao paginas unicas",
    "sumario": "a forma vem do nivel do titulo, e quem a gera e o proprio editor",
    "linha curta": "etiqueta de grafico, linha solta e fragmento nao sao prosa e nao tem forma unica",
}


def rotulos_pos_textuais(pars, body_end):
    """Onde comeca cada secao pos-textual, para nomear o papel pelo que ela e.

    Referencia e apendice sao pos-textuais e tem formatacao propria e diferente
    entre si: compara-los um com o outro produziria o falso positivo que esta
    funcao existe para evitar."""
    marcos = []
    for p in pars:
        t = p.text.strip()
        if p.idx < body_end or not t or is_toc_entry(p):
            continue
        if FIM_TEXTO_RE.match(t) and (p.level is not None or len(t) < 60):
            nome = re.sub(r"\s+", " ", t).strip().lower()[:40]
            marcos.append((p.idx, nome))
    return marcos


def papel(p, body_size, body_start, body_end, marcos):
    """Que funcao este paragrafo cumpre. A comparacao de forma so vale dentro
    do mesmo papel: legenda nao se compara com prosa."""
    if not p.text.strip():
        return None
    if p.level is not None:
        return None                      # titulos tem secao propria
    if p.in_table:
        return "tabela"
    if is_toc_entry(p):
        return "sumario"
    if p.idx < body_start:
        return "pre-textual"
    if p.idx >= body_end:
        nome = "referencias"
        for idx, n in marcos:
            if p.idx >= idx:
                nome = n
        return nome
    if LEGENDA_RE.match(p.text):
        return "legenda"
    if FONTE_RE.match(p.text):
        return "fonte de figura"
    # O mesmo piso que is_body aplica, e vem ANTES da citacao longa: sem isso,
    # "Plenario Virtual" em 11pt sob um grafico entrava como citacao recuada.
    # Medido num capitulo em 27/08/2026.
    if len(p.text.strip()) <= 60:
        return "linha curta"
    if is_long_citation(p, body_size, body_start):
        return "citacao longa"
    # Recuo deslocado e a assinatura do item de lista e da definicao, que tem
    # forma propria e nao se compara com prosa corrida. Sem este papel, nove dos
    # dezesseis desvios de corpo do capitulo medido eram itens de uma mesma lista
    # de definicoes, com tres recuos esquerdos diferentes entre si.
    if p.pp.get("ind_hang", 0) > 0:
        return "item de lista"
    return "corpo"


def cmd_sumario(args):
    parts = load(args.arquivo)
    styles = Styles(parts["word/styles.xml"])
    body = parts["word/document.xml"].find(W + "body")
    pars = collect_paragraphs(body, styles)
    notes = load_notes(parts["word/footnotes.xml"], styles)

    heads = [p for p in pars if p.level is not None and p.text.strip()]
    total_words = sum(words(p.text) for p in pars)

    print("# Sumario estrutural\n")
    print("Arquivo: %s" % os.path.basename(args.arquivo))
    print("Paragrafos: %d | Palavras: %d | Notas de rodape: %d | Titulos: %d\n"
          % (len(pars), total_words, len(notes), len(heads)))

    if not heads:
        print("NENHUM titulo com estilo de titulo foi encontrado. O documento")
        print("provavelmente usa titulos formatados a mao (ver comando 'forma').\n")

    print("Nivel | Par. inicial-final | Palavras | Titulo")
    print("----- | ------------------ | -------- | ------")
    bounds = [h.idx for h in heads] + [len(pars) + 1]
    for i, h in enumerate(heads):
        ini, fim = h.idx, bounds[i + 1] - 1
        wcount = sum(words(p.text) for p in pars[ini - 1:fim])
        print("N%d    | %d-%d | %d | %s" % (h.level, ini, fim, wcount, h.snippet(80)))

    print("\nUse: python analisar_docx.py texto \"%s\" --de INI --ate FIM"
          % os.path.basename(args.arquivo))


def cmd_forma(args):
    parts = load(args.arquivo)
    styles = Styles(parts["word/styles.xml"])
    doc = parts["word/document.xml"]
    body = doc.find(W + "body")
    pars = collect_paragraphs(body, styles)
    notes = load_notes(parts["word/footnotes.xml"], styles)
    full_text = "\n".join(p.text for p in pars)

    bodies = [p for p in pars if is_body(p)]
    size_tally = Counter()
    for p in bodies:
        if p.rp.get("size"):
            size_tally[p.rp["size"]] += 1
    body_size = size_tally.most_common(1)[0][0] if size_tally else None
    body_start = first_heading_idx(pars)

    P = print
    P("# Diagnostico de forma (coerencia interna)\n")
    P("Arquivo: %s" % os.path.basename(args.arquivo))
    P("Paragrafos: %d (corpo de texto: %d) | Palavras: %d | Notas: %d"
      % (len(pars), len(bodies), sum(words(p.text) for p in pars), len(notes)))
    imgs = [n for n in parts["_names"] if n.startswith("word/media/")]
    P("Imagens embutidas: %d | Paragrafos em tabela: %d"
      % (len(imgs), len([p for p in pars if p.in_table])))

    # --- 1. pagina
    ps = page_setup(body)
    P("\n## 1. Configuracao de pagina")
    if ps:
        P("Papel: %.1f x %.1f cm" % (ps.get("w", 0), ps.get("h", 0)))
        P("Margens: sup %.2f | inf %.2f | esq %.2f | dir %.2f cm"
          % (ps.get("top", 0), ps.get("bottom", 0), ps.get("left", 0), ps.get("right", 0)))
        if ps.get("gutter"):
            P("Medianiz (gutter): %.2f cm" % ps["gutter"])
    else:
        P("(nao declarada)")

    # --- 2. consistencia formal, por papel
    P("\n## 2. Consistencia formal (mesmo papel, duas formatacoes)")
    body_end = last_body_idx(pars, body_start)
    marcos = rotulos_pos_textuais(pars, body_end)
    grupos = {}
    for p in pars:
        r = papel(p, body_size, body_start, body_end, marcos)
        if r:
            grupos.setdefault(r, []).append(p)

    P("Papeis identificados: " + ", ".join(
        "%s %d" % (r, len(g)) for r, g in
        sorted(grupos.items(), key=lambda kv: -len(kv[1]))) or "(nenhum)")
    P("Compara-se dentro de cada papel, e nunca entre papeis: referencia,")
    P("legenda e fonte de figura tem forma propria, e diferir do corpo e o certo.")

    fora = [(r, len(g)) for r, g in sorted(grupos.items(), key=lambda kv: -len(kv[1]))
            if r in SEM_COMPARACAO and g]
    if fora:
        P("\nNao entram na comparacao, e a razao esta em cada um: " + "; ".join(
            "%s (%d) %s" % (r, n, SEM_COMPARACAO[r]) for r, n in fora))

    achados, uniformes = 0, []
    for r, g in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        if len(g) < 3 or r in SEM_COMPARACAO:
            continue
        sigs = Counter(x.signature() for x in g)
        dom, dom_n = sigs.most_common(1)[0]
        if len(sigs) == 1:
            uniformes.append((r, len(g)))
            continue
        pct = 100.0 * dom_n / len(g)
        if pct < 60:
            achados += 1
            P("\n### %s -- sem forma assentada" % r.upper())
            P("%d paragrafos em %d formatacoes, e a maior tem so %.0f%%."
              % (len(g), len(sigs), pct))
            P("Nao ha versao certa a que alinhar: a escolha e de quem escreve.")
            for sig, n in sigs.most_common(3):
                e = [x for x in g if x.signature() == sig][0]
                P("  [%d] %s" % (n, sig))
                P("     P%d: %s" % (e.idx, e.snippet(70)))
            continue
        achados += 1
        P("\n### %s -- %d de %d fora da forma dominante" % (r.upper(), len(g) - dom_n, len(g)))
        P("Vale: %s" % dom)
        for sig, n in sigs.most_common()[1:args.max_desvios + 1]:
            fora = [x for x in g if x.signature() == sig]
            P("\n  [%d paragrafo(s)] %s" % (n, sig))
            for e in fora[:3]:
                P("     P%d: %s" % (e.idx, e.snippet(70)))
        if len(sigs) - 1 > args.max_desvios:
            P("\n  (+%d variantes nao listadas)" % (len(sigs) - 1 - args.max_desvios))

    if uniformes:
        P("\nUNIFORMES, e isto conta a favor: " + ", ".join(
            "%s (%d)" % (r, n) for r, n in uniformes))
    if not achados:
        P("\nNenhuma divergencia dentro de papel. A formatacao esta consistente.")

    # --- 3. fontes e corpos
    P("\n## 3. Fontes e corpos em uso (todo o documento)")
    fonts = Counter()
    sizes = Counter()
    for p in pars:
        if not p.text.strip():
            continue
        n = max(len(p.text.strip()), 1)
        fonts[p.rp.get("font") or "(herdada)"] += n
        if p.rp.get("size"):
            sizes[p.rp["size"]] += n
    total_chars = sum(fonts.values()) or 1
    for f, n in fonts.most_common(12):
        P("  fonte %-28s %5.1f%% do texto" % (f, 100.0 * n / total_chars))
    P("")
    raros = []
    for s, n in sorted(sizes.items()):
        label = ("%.1f" % s).rstrip("0").rstrip(".")
        pct = 100.0 * n / total_chars
        P("  corpo %-5spt %5.1f%% do texto" % (label, pct))
        if pct < 1.0:
            raros.append(s)
    if len([f for f in fonts if f != "(herdada)"]) > 2:
        P("\n  ALERTA: mais de duas familias tipograficas no documento.")
    for s in raros:
        ex = [p for p in pars if p.rp.get("size") == s and p.text.strip()][:3]
        P("\n  ALERTA: corpo %g pt aparece em menos de 1%% do texto (provavel"
          " descuido, nao escolha):" % s)
        for e in ex:
            P("     P%d: %s" % (e.idx, e.snippet(70)))

    # --- 4. titulos
    P("\n## 4. Estrutura e formatacao dos titulos")
    heads = [p for p in pars if p.level is not None and p.text.strip()]
    if not heads:
        P("Nenhum titulo com estilo de titulo. Ver secao 5 (pseudo-titulos).")
    else:
        P("%d titulos com estilo. Distribuicao: %s" % (
            len(heads), ", ".join("N%d=%d" % (l, c) for l, c in
                                  sorted(Counter(h.level for h in heads).items()))))
        prev = None
        pulos = []
        for h in heads:
            if prev is not None and h.level > prev + 1:
                pulos.append((h.idx, prev, h.level, h.snippet(60)))
            prev = h.level
        if pulos:
            P("\nSALTOS DE NIVEL (titulo que pula um degrau da hierarquia):")
            for idx, a, b, txt in pulos:
                P("  P%d: N%d -> N%d | %s" % (idx, a, b, txt))
        by_level = {}
        for h in heads:
            by_level.setdefault(h.level, Counter())[h.signature()] += 1
        P("\nCoerencia dentro de cada nivel:")
        for lvl in sorted(by_level):
            variants = by_level[lvl].most_common()
            if len(variants) == 1:
                P("  N%d: uniforme -- %s" % (lvl, variants[0][0]))
            else:
                P("  N%d: INCONSISTENTE, %d formatacoes diferentes:" % (lvl, len(variants)))
                for sig, n in variants:
                    ex = [h for h in heads if h.level == lvl and h.signature() == sig][:2]
                    P("     [%dx] %s" % (n, sig))
                    for e in ex:
                        P("        P%d: %s" % (e.idx, e.snippet(60)))
        auto = len([h for h in heads if h.pp.get("numbered")])
        manual = len([h for h in heads if MANUAL_NUM_RE.match(h.text.strip())])
        if auto and manual:
            P("\n  ALERTA: numeracao mista -- %d titulos com numeracao automatica e"
              " %d com numero digitado a mao." % (auto, manual))

    # --- 4b. sumario x titulos reais
    P("\n## 4b. Sumario confrontado com os titulos do texto")
    toc = [p for p in pars if is_toc_entry(p) and p.idx < (body_start or len(pars))
           and len(p.text.strip()) > 8]
    if not toc:
        P("Nenhuma linha de sumario detectada antes do inicio do texto.")
    elif not heads:
        P("%d linhas de sumario, mas nenhum titulo com estilo para comparar." % len(toc))
    else:
        real = {clean_title(h.text): h for h in heads}
        listed = {clean_title(p.text): p for p in toc}
        so_sumario = [t for t in listed if t and t not in real]
        so_texto = [t for t in real if t and t not in listed]
        P("%d linhas no sumario | %d titulos no texto" % (len(toc), len(heads)))
        if not so_sumario and not so_texto:
            P("Batem integralmente.")
        else:
            if so_sumario:
                P("\nNO SUMARIO E NAO NO TEXTO (%d) -- sumario desatualizado ou"
                  " titulo renomeado:" % len(so_sumario))
                for t in so_sumario[:10]:
                    P("  P%d: %s" % (listed[t].idx, listed[t].snippet(75)))
            if so_texto:
                P("\nNO TEXTO E NAO NO SUMARIO (%d):" % len(so_texto))
                for t in so_texto[:10]:
                    P("  P%d: %s" % (real[t].idx, real[t].snippet(75)))

    # --- 5. pseudo-titulos
    P("\n## 5. Pseudo-titulos (formatados a mao, sem estilo de titulo)")
    pseudo = [p for p in pars if is_pseudo_heading(p, body_size)]
    pre = [p for p in pseudo if p.idx < body_start]
    corpo = [p for p in pseudo if p.idx >= body_start]
    if not pseudo:
        P("Nenhum encontrado.")
    else:
        P("%d no total: %d antes do inicio do texto (pre-textuais) e %d no corpo."
          % (len(pseudo), len(pre), len(corpo)))
        P("Consequencia: nao entram no sumario automatico nem no mapa do documento.")
        if corpo:
            P("\nNO CORPO DO TEXTO (os que importam):")
            for p in corpo[:args.max_desvios]:
                P("  P%d [%s] %s" % (p.idx, p.font_desc(), p.snippet(70)))
            if len(corpo) > args.max_desvios:
                P("  (+%d nao listados)" % (len(corpo) - args.max_desvios))
        if pre:
            P("\nPRE-TEXTUAIS (capa, folha de rosto, RESUMO, ABSTRACT etc.):")
            P("  %s" % "; ".join("P%d %s" % (p.idx, p.snippet(40)) for p in pre[:8]))
            if len(pre) > 8:
                P("  (+%d nao listados)" % (len(pre) - 8))

    # --- 6. citacoes longas
    P("\n## 6. Citacoes longas (recuadas)")
    cits = [p for p in pars if is_long_citation(p, body_size, body_start)]
    if not cits:
        P("Nenhum paragrafo recuado como citacao longa foi identificado.")
        if body_size:
            P("(criterio: recuo esquerdo >= 2,6 cm, ou corpo menor que %gpt com recuo)" % body_size)
    else:
        cs = Counter(p.signature() for p in cits)
        P("%d paragrafos, %d formatacoes distintas." % (len(cits), len(cs)))
        for sig, n in cs.most_common():
            ex = [p for p in cits if p.signature() == sig][:2]
            P("  [%dx] %s" % (n, sig))
            for e in ex:
                P("     P%d: %s" % (e.idx, e.snippet(70)))
        if len(cs) > 1:
            P("  ALERTA: citacoes longas com formatacoes divergentes.")

    # --- 7. notas de rodape
    P("\n## 7. Notas de rodape")
    if not notes:
        P("Nenhuma.")
    else:
        nsig = Counter()
        for fid, (txt, npars) in notes.items():
            for np_ in npars:
                if np_.text.strip():
                    nsig[np_.signature()] += 1
        lens = [len(t) for t, _ in notes.values()]
        P("%d notas | extensao media %d caracteres | maior %d"
          % (len(notes), sum(lens) // max(len(lens), 1), max(lens)))
        P("Formatacoes:")
        for sig, n in nsig.most_common(4):
            P("  [%dx] %s" % (n, sig))
        if len(nsig) > 1:
            P("  ALERTA: notas com formatacoes divergentes.")
        subst = [fid for fid, (t, _) in notes.items() if len(t) > 400]
        if subst:
            P("  %d notas com mais de 400 caracteres (notas substantivas, nao so"
              " referencia): ids %s" % (len(subst), ", ".join(subst[:10])))

    # --- 8. sujeira tipografica
    P("\n## 8. Sujeira tipografica")
    P("(linhas de sumario e blocos de codigo dos apendices ficam de fora da contagem)")
    limpos = [p for p in pars if p.text.strip() and not is_toc_entry(p)
              and not looks_like_code(p)]
    checks = [
        ("espaco duplo ou mais", re.compile(r"\S {2,}\S")),
        ("espaco antes de pontuacao", re.compile(r"\s[,.;:!?](\s|$)")),
        ("falta espaco depois de pontuacao", re.compile(r"[,;:][A-Za-zÀ-ÿ]")),
        ("tabulacao no meio do texto", re.compile(r"\t")),
        ("hifen usado como travessao", re.compile(r"\s-{1,2}\s")),
        ("tres pontos em vez de reticencias", re.compile(r"\.\.\.")),
        ("aspas retas", re.compile(r"\"")),
    ]
    achou = False

    def relata(label, hits, nota=""):
        if not hits:
            return False
        P("  %-38s %4d paragrafo(s). Ex.: P%d | %s%s"
          % (label + ":", len(hits), hits[0][0], hits[0][1], nota))
        return True

    for label, rx in checks:
        hits = [(p.idx, p.snippet(70)) for p in limpos if rx.search(p.text)]
        achou |= relata(label, hits)

    desbal = [(p.idx, p.snippet(70)) for p in limpos
              if p.text.count("(") != p.text.count(")")]
    achou |= relata("parenteses desbalanceados", desbal)
    aspas = [(p.idx, p.snippet(70)) for p in limpos
             if p.text.count("“") != p.text.count("”")]
    achou |= relata("aspas curvas desbalanceadas", aspas)
    sem_ponto = [(p.idx, p.snippet(70)) for p in limpos
                 if is_body(p) and p.idx >= body_start and len(p.text.strip()) > 150
                 and not is_pseudo_heading(p, body_size)
                 and not re.match(r"^\s*(Fonte|Nota|Tabela|Gr[áa]fico|Figura|Quadro|Esquema)\b", p.text.strip())
                 and not p.text.strip().endswith((".", "?", "!", ":", "”", "\"", ")", ";"))]
    achou |= relata("paragrafo sem pontuacao final", sem_ponto)

    vazios = [p.idx for p in pars if not p.text.strip()]
    if vazios:
        achou = True
        P("  %-38s %4d (espacamento feito com Enter em vez de espacamento de paragrafo)"
          % ("paragrafos vazios:", len(vazios)))
    for label, sel in (
            ("quebra manual de linha (Shift+Enter):", lambda p: p.breaks),
            ("recuo feito com espaco/tab:", lambda p: p.text.startswith((" ", "\t")) and len(p.text.strip()) > 60),
            ("texto realcado (marca-texto):", lambda p: p.rp.get("highlight")),
            ("texto colorido:", lambda p: p.rp.get("color"))):
        idxs = [p.idx for p in limpos if sel(p)]
        if idxs:
            achou = True
            P("  %-38s %4d paragrafo(s). Ex.: P%s"
              % (label, len(idxs), ", P".join(str(i) for i in idxs[:4])))
    if not achou:
        P("  Nada relevante encontrado.")

    # --- 9. sinais de montagem por colagem
    P("\n## 9. Sinais de colagem / montagem")
    sinais = []
    if len(fonts) > 3:
        sinais.append("%d familias tipograficas distintas" % len(fonts))
    if sigs and len(sigs) > 6:
        sinais.append("%d formatacoes distintas no corpo de texto" % len(sigs))
    if len(sizes) > 4:
        sinais.append("%d corpos de fonte distintos" % len(sizes))
    if pseudo and heads:
        sinais.append("convivencia de titulos com estilo e titulos manuais")
    if sinais:
        for s in sinais:
            P("  - %s" % s)
        P("  Isso costuma indicar trechos colados de fontes diferentes sem"
          " reformatacao. Vale conferir a originalidade dos trechos destoantes.")
    else:
        P("  Nenhum sinal forte.")

    # --- 10. ritmo dos paragrafos
    P("\n## 10. Ritmo dos paragrafos (prosa argumentativa)")
    cpl = chars_por_linha(ps, body_size)
    body_end = last_body_idx(pars, body_start)
    prosa = [p for p in pars if is_prosa(p, body_size) and body_start <= p.idx < body_end]
    if body_end <= len(pars):
        P("Texto principal: P%d a P%d (o pós-textual a partir de P%d fica de fora)."
          % (body_start, body_end - 1, body_end))
    if not prosa:
        P("Nenhum paragrafo de prosa argumentativa isolado.")
    else:
        if cpl:
            piso_ch = 10 * cpl
            P("Mancha de %.1f cm em corpo %g pt: ~%.0f caracteres por linha."
              % (ps["w"] - ps["left"] - ps["right"], body_size, cpl))
            P("Piso de 10 linhas = ~%.0f caracteres = ~%.0f palavras."
              % (piso_ch, piso_ch / 6.2))
        else:
            piso_ch = 780
            P("Geometria da pagina indisponivel; piso de 10 linhas estimado em 780 caracteres.")
        comps = sorted(len(p.text.strip()) for p in prosa)
        med = comps[len(comps) // 2]
        frases = [sentencas(p.text) for p in prosa]
        uma = [p for p, f in zip(prosa, frases) if f == 1]
        duas = [p for p, f in zip(prosa, frases) if f <= 2]
        curtos = [p for p in prosa if len(p.text.strip()) < piso_ch]
        P("\n%d paragrafos de prosa. Mediana %d caracteres (~%.1f linhas, ~%d palavras)."
          % (len(prosa), med, med / cpl if cpl else 0, med / 6.2))
        P("Abaixo do piso de 10 linhas: %d (%.0f%%)."
          % (len(curtos), 100.0 * len(curtos) / len(prosa)))
        P("De frase unica: %d (%.0f%%). De ate duas frases: %d (%.0f%%)."
          % (len(uma), 100.0 * len(uma) / len(prosa),
             len(duas), 100.0 * len(duas) / len(prosa)))
        faixas = Counter()
        for c in comps:
            lin = (c / cpl) if cpl else (c / 78.0)
            faixas["ate 3 linhas" if lin < 3 else
                   "3 a 6 linhas" if lin < 6 else
                   "6 a 10 linhas" if lin < 10 else
                   "10 a 18 linhas" if lin < 18 else "acima de 18 linhas"] += 1
        P("\nDistribuicao:")
        for k in ("ate 3 linhas", "3 a 6 linhas", "6 a 10 linhas",
                  "10 a 18 linhas", "acima de 18 linhas"):
            if faixas.get(k):
                P("  %-20s %4d (%.0f%%)" % (k, faixas[k], 100.0 * faixas[k] / len(prosa)))

        # sequencias em staccato: 3+ paragrafos curtos consecutivos no texto
        curto_set = {p.idx for p in curtos}
        corta = {p.idx for p in pars
                 if p.level is not None or LEGENDA_RE.match(p.text.strip())}
        runs, atual = [], []
        for p in prosa:
            emenda = (not atual or (p.idx - atual[-1].idx <= 3
                      and not any(j in corta for j in range(atual[-1].idx + 1, p.idx))))
            if p.idx in curto_set and emenda:
                atual.append(p)
            else:
                if len(atual) >= 3:
                    runs.append(atual)
                atual = [p] if p.idx in curto_set else []
        if len(atual) >= 3:
            runs.append(atual)
        runs.sort(key=len, reverse=True)
        if not runs:
            P("\nNenhuma sequencia de tres ou mais paragrafos curtos seguidos.")
        else:
            P("\nSEQUENCIAS EM STACCATO (%d trechos de 3+ paragrafos curtos seguidos)."
              % len(runs))
            P("Sao os trechos onde a ligacao entre as frases provavelmente nao foi feita.")
            P("Avalie lendo: o defeito nao e o comprimento, e a relacao deixada implicita.")
            for r in runs[:8]:
                medio = sum(len(x.text.strip()) for x in r) // len(r)
                P("\n  P%d-P%d | %d paragrafos | media %d caracteres (~%.1f linhas)"
                  % (r[0].idx, r[-1].idx, len(r), medio, (medio / cpl) if cpl else 0))
                for x in r[:3]:
                    P("     P%d: %s" % (x.idx, x.snippet(75)))
            if len(runs) > 8:
                P("\n  (+%d sequencias nao listadas)" % (len(runs) - 8))

    # --- 11. graficos e tabelas
    P("\n## 11. Graficos e tabelas: descricao ou analise")
    # legenda antes do inicio do texto e entrada de "Lista de graficos", nao legenda
    legendas = [p for p in pars if LEGENDA_RE.match(p.text.strip())
                and not is_toc_entry(p) and p.idx >= body_start]
    if not legendas:
        P("Nenhuma legenda de grafico, tabela, figura ou quadro identificada.")
    else:
        tipos = Counter()
        for p in legendas:
            m = LEGENDA_RE.match(p.text.strip())
            tipos[m.group(1).capitalize()] += 1
        P("%d legendas: %s" % (len(legendas),
                               ", ".join("%s %d" % (k, v) for k, v in tipos.most_common())))

        # numeracao com falha de sequencia
        por_tipo = {}
        for p in legendas:
            m = LEGENDA_RE.match(p.text.strip())
            por_tipo.setdefault(m.group(1).capitalize(), []).append((int(m.group(2)), p))
        for tipo, lst in sorted(por_tipo.items()):
            nums = [n for n, _ in lst]
            faltando = [n for n in range(1, max(nums) + 1) if n not in nums]
            repetidos = [n for n, c in Counter(nums).items() if c > 1]
            fora = nums != sorted(nums)
            if faltando or repetidos or fora:
                P("\n  %s: numeracao com problema." % tipo)
                if faltando:
                    P("     ausentes: %s" % ", ".join(str(n) for n in faltando))
                if repetidos:
                    P("     repetidos: %s" % ", ".join(str(n) for n in sorted(repetidos)))
                if fora:
                    P("     fora de ordem no documento: %s" % ", ".join(str(n) for n in nums))

        # legenda nunca chamada no corpo do texto
        corpo_txt = " ".join(p.text for p in pars
                             if is_prosa(p, body_size) and p.idx < body_end)
        orfas = []
        for p in legendas:
            m = LEGENDA_RE.match(p.text.strip())
            rot = re.compile(re.escape(m.group(1)) + r"\s*n?[.º°]?\s*" + m.group(2) + r"\b", re.I)
            if not rot.search(corpo_txt):
                orfas.append(p)
        if orfas:
            P("\n  ORFAS (%d): legenda existe e o rotulo nunca aparece no corpo do texto."
              % len(orfas))
            P("  Elemento que o leitor nao sabe quando olhar, e que nada perde se sair.")
            for p in orfas[:10]:
                P("     P%d: %s" % (p.idx, p.snippet(70)))

        # blocos que seguem cada legenda: densidade numerica e marca de inferencia
        idx_map = {p.idx: p for p in pars}
        so_descreve, com_analise, densidades = [], 0, []
        for leg in legendas:
            bloco = []
            j = leg.idx + 1
            while j <= len(pars) and len(bloco) < 6:
                q = idx_map.get(j)
                j += 1
                if q is None:
                    break
                if q.level is not None or LEGENDA_RE.match(q.text.strip()):
                    break
                if is_prosa(q, body_size):
                    bloco.append(q)
            if not bloco:
                continue
            txt = " ".join(b.text for b in bloco)
            dens = densidade_numerica(txt)
            densidades.append(dens)
            tem_inf = bool(INFERENCIA_RE.search(txt))
            if tem_inf:
                com_analise += 1
            elif dens >= 0.06:
                so_descreve.append((leg, bloco, dens))
        if densidades:
            dm = sorted(densidades)[len(densidades) // 2]
            P("\nDensidade numerica mediana dos blocos que seguem uma legenda: %.0f%%"
              " das palavras sao numeros." % (100 * dm))
        P("Blocos com marca de inferencia (portanto, o que indica, explica-se por...): %d de %d."
          % (com_analise, len(densidades)))
        if not so_descreve:
            P("Nenhum bloco puramente descritivo detectado.")
        else:
            P("\nSO DESCRICAO (%d blocos): alta densidade de numeros e nenhuma marca de"
              " inferencia." % len(so_descreve))
            P("Verifique lendo se o trecho apenas narra o que o grafico ja mostra.")
            P("A pergunta a fazer de cada um: o que mudaria no argumento se o grafico saisse?")
            for leg, bloco, dens in sorted(so_descreve, key=lambda x: -x[2])[:8]:
                P("\n  Legenda P%d: %s" % (leg.idx, leg.snippet(65)))
                P("     bloco P%d-P%d | %.0f%% de numeros | %d paragrafos"
                  % (bloco[0].idx, bloco[-1].idx, 100 * dens, len(bloco)))
                P("     P%d: %s" % (bloco[0].idx, bloco[0].snippet(75)))
            if len(so_descreve) > 8:
                P("\n  (+%d blocos nao listados)" % (len(so_descreve) - 8))

    # --- 12. balanco dos capitulos
    P("\n## 12. Balanco dos capitulos (subsidio para fusao e fissao)")
    caps = [h for h in heads if h.level == 1 and body_start <= h.idx < body_end]
    if len(caps) < 2:
        P("Menos de dois capitulos no texto principal; nada a comparar.")
    else:
        limites = [c.idx for c in caps] + [body_end]
        linhas = []
        for i, c in enumerate(caps):
            ini, fim = c.idx, limites[i + 1] - 1
            w = sum(words(p.text) for p in pars[ini - 1:fim])
            subs = Counter(h.level for h in heads if ini < h.idx <= fim and h.level > 1)
            linhas.append((c, ini, fim, w, subs))
        total = sum(l[3] for l in linhas) or 1
        ws = sorted(l[3] for l in linhas)
        mediana = ws[len(ws) // 2]
        P("%d capitulos, %d palavras no texto principal, mediana de %d palavras."
          % (len(caps), total, mediana))
        P("\nCap. | Palavras | %% | Subsecoes | Titulo")
        for c, ini, fim, w, subs in linhas:
            sd = ", ".join("N%d=%d" % (k, v) for k, v in sorted(subs.items())) or "nenhuma"
            P("  P%-5d %6d | %4.1f%% | %-14s | %s" % (ini, w, 100.0 * w / total, sd, c.snippet(55)))
        P("\nSinais (o numero nao decide nada sozinho; decide a unidade de argumento):")
        achou_sinal = False
        for c, ini, fim, w, subs in linhas:
            if w < 0.4 * mediana:
                achou_sinal = True
                P("  P%d MAGRO: %d palavras, %.0f%% da mediana. Candidato a virar secao"
                  " de um capitulo vizinho, se estabelecer parte da mesma asserção."
                  % (ini, w, 100.0 * w / mediana))
            elif w > 2.2 * mediana:
                achou_sinal = True
                P("  P%d INCHADO: %d palavras, %.1fx a mediana. Verifique se sustenta"
                  " uma asserção só ou duas independentes." % (ini, w, w / mediana))
            if w > 0.6 * mediana and not subs:
                achou_sinal = True
                P("  P%d SEM SUBDIVISAO: %d palavras corridas sem subsecao." % (ini, w))
            if subs.get(2, 0) == 1:
                achou_sinal = True
                P("  P%d SUBSECAO UNICA: dividir em uma parte so nao divide nada." % ini)
            if subs.get(2, 0) > 8:
                achou_sinal = True
                P("  P%d FRAGMENTADO: %d subsecoes de primeiro nivel." % (ini, subs[2]))
        if not achou_sinal:
            P("  Nenhum desequilibrio grosseiro entre capitulos.")

        # mesma regra um nivel abaixo: subsecoes dentro de cada capitulo
        n2 = [h for h in heads if h.level == 2 and body_start <= h.idx < body_end]
        if len(n2) >= 3:
            marcos = sorted([h.idx for h in heads
                             if h.level in (1, 2) and body_start <= h.idx < body_end]
                            + [body_end])
            tam = {}
            for h in n2:
                fim = min(x for x in marcos if x > h.idx) - 1
                tam[h.idx] = (sum(words(p.text) for p in pars[h.idx - 1:fim]), fim)
            ws2 = sorted(v[0] for v in tam.values())
            med2 = ws2[len(ws2) // 2]
            P("\nSubsecoes de primeiro nivel (N2): %d, mediana de %d palavras."
              % (len(n2), med2))
            for c, ini, fim, w, subs in linhas:
                filhas = [h for h in n2 if ini < h.idx <= fim]
                if not filhas:
                    continue
                P("\n  Em %s" % c.snippet(58))
                for h in filhas:
                    w2, f2 = tam[h.idx]
                    netas = len([x for x in heads if x.level == 3 and h.idx < x.idx <= f2])
                    marca = ""
                    if w2 < 0.4 * med2:
                        marca = "  <- MAGRA (%.0f%% da mediana)" % (100.0 * w2 / med2)
                    elif w2 > 2.5 * med2:
                        marca = "  <- INCHADA (%.1fx a mediana)" % (w2 / med2)
                    if netas == 1:
                        marca += "  <- uma unica subsubsecao"
                    P("     P%-5d %5d palavras | %s%s" % (h.idx, w2, h.snippet(50), marca))
            P("\n  Subsecao magra ao lado de irmas normais costuma ser assunto que"
              " cabia num paragrafo do texto corrido, nao um item proprio.")

    # --- 13. retorno dos elementos teoricos
    P("\n## 13. Retorno dos elementos teoricos")
    if len(caps) < 2:
        P("Menos de dois capitulos; nada a rastrear.")
    else:
        cap_de = {}
        for i, (c, ini, fim, w, subs) in enumerate(linhas):
            for j in range(ini, fim + 1):
                cap_de[j] = i
        rotulos = ["C%d %s" % (i + 1, l[0].snippet(40)) for i, l in enumerate(linhas)]

        autores, termos = {}, {}
        for p in pars:
            i = cap_de.get(p.idx)
            if i is None or looks_like_code(p) or is_toc_entry(p):
                continue
            for rx in (CIT_ANO_RE, CIT_PAREN_RE):
                for m in rx.finditer(p.text):
                    nome = m.group(1).upper()
                    if nome in NAO_AUTOR or len(nome) < 3:
                        continue
                    autores.setdefault(nome, set()).add(i)
            for m in ASPAS_RE.finditer(p.text):
                t = re.sub(r"\s+", " ", m.group(1)).strip().lower()
                if 5 <= len(t) <= 45 and not t[0].isdigit():
                    termos.setdefault(t, set()).add(i)

        ultimo = len(linhas) - 1
        P("%d autores distintos citados, %d termos entre aspas."
          % (len(autores), len(termos)))

        P("\nAUTORES QUE NAO RETORNAM, por capitulo.")
        P("NAO e defeito por si: em revisao de literatura o normal e que a maioria")
        P("dos autores apareca uma vez e nao volte. Serve so para localizar onde")
        P("esta a massa bibliografica. Os defeitos estao nos dois blocos seguintes.")
        for i, rot in enumerate(rotulos):
            if i == ultimo:
                continue
            presos = sorted(a for a, cs in autores.items() if cs == {i})
            tot = len([a for a, cs in autores.items() if i in cs])
            if not tot:
                continue
            P("  %-45s %3d de %3d autores ficam so aqui (%.0f%%)"
              % (rot, len(presos), tot, 100.0 * len(presos) / tot))

        # --- monocultura e name-dropping, por subsecao
        marcos = sorted(set([h.idx for h in heads
                             if h.level in (1, 2) and body_start <= h.idx < body_end]
                            + [body_end]))
        segs = []
        for k in range(len(marcos) - 1):
            ini, fim = marcos[k], marcos[k + 1] - 1
            tit = next((h for h in heads if h.idx == ini), None)
            proses = [p for p in pars[ini - 1:fim] if is_prosa(p, body_size)]
            inst = []
            for p in proses:
                nomes = set()
                for rx in (CIT_ANO_RE, CIT_PAREN_RE):
                    for m in rx.finditer(p.text):
                        n = m.group(1).upper()
                        if n not in NAO_AUTOR and len(n) >= 3:
                            nomes.add(n)
                for n in nomes:
                    inst.append((p.idx, n))
            if tit is not None and inst:
                segs.append((tit, ini, fim, proses, inst))

        P("\nCONCENTRACAO: um autor sozinho ocupa longo trecho.")
        P("Nao e defeito automatico. Legitimo quando a fonte e institucional, quando")
        P("o autor e o unico que tratou da questao especifica, ou quando o trecho e")
        P("analise minuciosa de um documento unico (manual, acordao, norma), caso em")
        P("que a fonte dominante e o objeto analisado. Vira defeito quando o autor")
        P("unico cobre tema de literatura ampla, fazendo as vezes de uma bibliografia")
        P("que nao foi lida. Decida lendo, nunca pelo percentual.")
        achou_m = False
        for tit, ini, fim, proses, inst in segs:
            cont = Counter(n for _, n in inst)
            top, qt = cont.most_common(1)[0]
            share = 100.0 * qt / len(inst)
            por_par = {}
            for pi, n in inst:
                por_par.setdefault(pi, set()).add(n)
            corrida = maior = 0
            for p in proses:
                s = por_par.get(p.idx)
                if s == {top}:
                    corrida += 1
                    maior = max(maior, corrida)
                elif s:
                    corrida = 0
            if (share >= 50 and qt >= 6) or maior >= 4:
                achou_m = True
                P("  P%-5d %s" % (ini, tit.snippet(52)))
                P("     %s em %d de %d citacoes (%.0f%%); maior sequencia: %d paragrafos"
                  " seguidos citando so ele" % (top.title(), qt, len(inst), share, maior))
                if top in INSTITUCIONAL or (len(top) <= 5 and top.isupper()):
                    P("     (fonte institucional: pode ser citacao de norma ou de dado"
                      " proprio, e nao monocultura de leitura. Confira lendo.)")
        if not achou_m:
            P("  Nenhuma secao dominada por um autor unico.")

        P("\nNAME-DROPPING: muitos autores, cada um citado uma vez so, sem uso.")
        P("Autor mencionado e nunca mobilizado ocupa espaco e nao sustenta nada.")
        achou_n = False
        for tit, ini, fim, proses, inst in segs:
            cont = Counter(n for _, n in inst)
            uma = [n for n, c in cont.items() if c == 1]
            w = sum(words(p.text) for p in proses) or 1
            if len(cont) >= 6 and len(uma) / len(cont) >= 0.8 and len(cont) / w * 1000 >= 8:
                achou_n = True
                P("  P%-5d %s" % (ini, tit.snippet(52)))
                P("     %d autores distintos em %d palavras, %d deles citados uma"
                  " unica vez (%.0f por mil palavras)"
                  % (len(cont), w, len(uma), 1000.0 * len(cont) / w))
                P("     %s" % ", ".join(a.title() for a in sorted(uma)[:12]))
        if not achou_n:
            P("  Nenhuma secao com o padrao.")

        P("\nSEM CONSTRUCAO PREVIA: primeiro aparecem depois da metade do trabalho.")
        P("Elemento que a analise usa sem que o leitor tenha recebido antes.")
        meio = max(1, len(linhas) // 2)
        tardios = sorted((min(cs), a) for a, cs in autores.items()
                         if min(cs) >= meio and len(cs) >= 2)
        if not tardios:
            P("  Nenhum autor mobilizado duas ou mais vezes estreia na segunda metade.")
        else:
            for i in sorted(set(x[0] for x in tardios)):
                nomes = [a.title() for j, a in tardios if j == i]
                P("  estreia em %-40s %s" % (rotulos[i][:40], ", ".join(nomes[:12])))
                if len(nomes) > 12:
                    P("     (+%d)" % (len(nomes) - 12))

        P("\nSO NA CONCLUSAO: aparecem no ultimo capitulo e em nenhum outro.")
        novos_a = sorted(a for a, cs in autores.items() if cs == {ultimo})
        novos_t = sorted(t for t, cs in termos.items() if cs == {ultimo})
        if not novos_a and not novos_t:
            P("  Nada. A conclusao nao introduz autor nem termo novo.")
        else:
            if novos_a:
                P("  autores: %s" % ", ".join(a.title() for a in novos_a[:15]))
            if novos_t:
                P("  termos: %s" % "; ".join('"%s"' % t for t in novos_t[:10]))
            P("  Material novo na conclusao e sinal de argumento que nao foi feito no corpo.")

        P("\nTERMOS ENTRE ASPAS presos a um capitulo (5 ou mais ocorrencias de aspas):")
        presos_t = [(sorted(cs)[0], t) for t, cs in termos.items() if len(cs) == 1]
        por_cap = {}
        for i, t in presos_t:
            por_cap.setdefault(i, []).append(t)
        algum = False
        for i in sorted(por_cap):
            if len(por_cap[i]) < 5 or i == ultimo:
                continue
            algum = True
            P("  %-45s %d termos" % (rotulos[i], len(por_cap[i])))
            P("     %s" % "; ".join('"%s"' % t for t in sorted(por_cap[i])[:8]))
        if not algum:
            P("  Nenhuma concentracao relevante.")

    # --- 14. marcas de escrita que parecem de IA
    P("\n## 14. Marcas de escrita que parecem de IA")
    P("Nao sao prova de nada: sao tracos que hoje fazem um texto humano PARECER")
    P("gerado. Servem para o orientando limpar o texto, tenha usado IA ou nao.")
    prosa14 = [p for p in pars if is_prosa(p, body_size) and body_start <= p.idx < body_end]
    w14 = sum(words(p.text) for p in prosa14) or 1
    if not prosa14:
        P("Sem prosa a medir.")
    else:
        marcas = [
            ("travessao e meio-travessao", re.compile(r"[—–]")),
            ("'nao X, mas Y'", re.compile(
                r"\bn[ãa]o\s+(?:apenas|s[óo]|somente)?[^,.;:]{2,45},?\s+mas\b|"
                r"\bn[ãa]o\s+se\s+trata\s+de[^,.;:]{2,45},?\s+e\s+sim\b", re.I)),
            ("conectivo de arremate", re.compile(
                r"\b(al[ée]m disso|ademais|outrossim|em suma|em [úu]ltima an[áa]lise|"
                r"por fim|dessa forma|dessa maneira|nesse diapas[ãa]o)\b", re.I)),
            ("'vale/cumpre notar, ressaltar, destacar'", re.compile(
                r"\b(vale|cumpre|importa|convém|conv[ée]m)\s+(notar|ressaltar|destacar|"
                r"mencionar|observar|frisar|salientar)\b", re.I)),
            ("'e importante/fundamental ... que'", re.compile(
                r"\b[ée]\s+(importante|fundamental|essencial|preciso|necess[áa]rio|"
                r"crucial)\s+(notar|ressaltar|destacar|observar|mencionar|salientar)\b", re.I)),
            ("elogio abstrato sem medida", re.compile(
                r"\b(robust[oa]s?|significativ[oa]s?|relevant[ees]s?|fundamental|fundamentais|"
                r"cruciais?|essenciais?|primordial|ineg[áa]vel|not[áa]vel|profund[oa]s?)\b", re.I)),
        ]
        P("\nDensidade por mil palavras de prosa (%d palavras):" % w14)
        for nome, rx in marcas:
            hits = [(p.idx, len(rx.findall(p.text))) for p in prosa14 if rx.search(p.text)]
            n = sum(c for _, c in hits)
            if not n:
                continue
            piores = sorted(hits, key=lambda x: -x[1])[:3]
            P("  %-42s %5.1f  (%d ocorrencias em %d paragrafos)"
              % (nome, 1000.0 * n / w14, n, len(hits)))
            P("     concentrados em: %s"
              % ", ".join("P%d (%dx)" % (i, c) for i, c in piores))

        negrito = [p for p in prosa14 if p.rp.get("bold")]
        if negrito:
            P("  %-42s %5.1f  (%d paragrafos de prosa em negrito)"
              % ("negrito no corpo do texto", 1000.0 * len(negrito) / w14, len(negrito)))
            P("     %s" % ", ".join("P%d" % p.idx for p in negrito[:8]))

        comps14 = [len(p.text.strip()) for p in prosa14]
        media = sum(comps14) / len(comps14)
        desvio = (sum((c - media) ** 2 for c in comps14) / len(comps14)) ** 0.5
        cv = desvio / media if media else 0
        P("\nUniformidade de comprimento dos paragrafos: coeficiente de variacao %.2f."
          % cv)
        if cv < 0.45:
            P("  BAIXA VARIACAO: paragrafos de tamanho parecido demais ao longo do")
            P("  texto. E um dos tracos que mais denuncia geracao automatica, e um")
            P("  dos mais faceis de corrigir escrevendo em ritmo variado.")
        else:
            P("  Variacao normal; o ritmo do texto nao chama atencao por esse lado.")

    # --- 15. corpo confrontado com a lista de referencias
    P("\n## 15. Citacoes do corpo x lista de referencias")
    ref_ini = next((p.idx for p in pars if p.idx > body_start and p.text.strip()
                    and re.match(r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA|OBRAS CITADAS)\b",
                                 p.text.strip(), re.I)
                    and (p.level is not None or len(p.text.strip()) < 60)
                    and not is_toc_entry(p)), None)
    if ref_ini is None:
        P("Lista de referencias nao localizada.")
    else:
        ref_fim = next((p.idx for p in pars if p.idx > ref_ini and p.text.strip()
                        and re.match(r"^\s*(AP[ÊE]NDICES?|ANEXOS?)\b", p.text.strip(), re.I)
                        and (p.level is not None or len(p.text.strip()) < 60)),
                       len(pars) + 1)
        entradas = {}
        for p in pars[ref_ini:ref_fim - 1]:
            t = p.text.strip()
            if len(t) < 40 or is_toc_entry(p):
                continue
            ms = re.match(r"^\s*([A-ZÀ-Ý][A-ZÀ-Ý'\- ]{1,40}?)\s*[,.]", t)
            my = re.search(r"\b((?:19|20)\d{2})([a-f])?\b", t)
            if not ms or not my:
                continue
            sob = sem_acento(ms.group(1).strip().split()[-1])
            entradas.setdefault((sob, my.group(1)), []).append((p.idx, t))
        citacoes = {}
        for p in pars:
            if not (body_start <= p.idx < ref_ini) or looks_like_code(p) or is_toc_entry(p):
                continue
            for rx in (CIT_ANO_RE, CIT_PAREN_RE):
                for m in rx.finditer(p.text):
                    nome = m.group(1).upper()
                    if nome in NAO_AUTOR or len(nome) < 3:
                        continue
                    citacoes.setdefault((sem_acento(nome), m.group(2)), []).append(p.idx)
        P("%d entradas na lista (P%d-%d), %d pares autor-ano distintos citados no corpo."
          % (len(entradas), ref_ini, ref_fim - 1, len(citacoes)))

        sem_entrada, ano_diverge = [], []
        sobrenomes = {}
        for (s, a) in entradas:
            sobrenomes.setdefault(s, set()).add(a)
        for (s, a), onde in sorted(citacoes.items()):
            if (s, a) in entradas:
                continue
            if s in sobrenomes:
                ano_diverge.append((s, a, sorted(sobrenomes[s]), onde))
            else:
                sem_entrada.append((s, a, onde))

        P("\nAMBIGUIDADE AUTOR-ANO: mesmo sobrenome e mesmo ano em mais de uma entrada.")
        P("E o modo de falha mais comum de referencia inventada: a citacao autor-data")
        P("do corpo casa com uma entrada que e obra inteiramente diversa. Confira se a")
        P("obra da lista trata mesmo do assunto para o qual foi citada.")
        amb = {k: v for k, v in entradas.items() if len(v) > 1}
        if not amb:
            P("  Nenhum par autor-ano com duas entradas.")
        else:
            for (s, a), lst in sorted(amb.items()):
                cit = citacoes.get((s, a), [])
                P("  %s (%s): %d entradas na lista; citado em %d lugar(es) do corpo%s"
                  % (s.title(), a, len(lst), len(cit),
                     (": P" + ", P".join(str(x) for x in cit[:6])) if cit else ""))
                for idx, t in lst:
                    P("     P%d: %s" % (idx, re.sub(r"\s+", " ", t)[:110]))

        P("\nCITADO NO CORPO E AUSENTE DA LISTA (%d):" % len(sem_entrada))
        for s, a, onde in sem_entrada[:15]:
            P("  %s (%s) em P%s" % (s.title(), a, ", P".join(str(x) for x in onde[:5])))
        if len(sem_entrada) > 15:
            P("  (+%d)" % (len(sem_entrada) - 15))

        P("\nSOBRENOME NA LISTA COM OUTRO ANO (%d): ano do corpo nao confere com o da"
          " entrada, ou sao obras distintas do mesmo autor sem sufixo de letra."
          % len(ano_diverge))
        for s, a, anos, onde in ano_diverge[:15]:
            P("  corpo diz %s (%s); lista tem %s. Em P%s"
              % (s.title(), a, "/".join(anos), ", P".join(str(x) for x in onde[:4])))
        if len(ano_diverge) > 15:
            P("  (+%d)" % (len(ano_diverge) - 15))

        nunca = [k for k in entradas if k not in citacoes]
        P("\nNA LISTA E NUNCA CITADO NO CORPO (%d):" % len(nunca))
        if nunca:
            P("  %s" % "; ".join("%s (%s)" % (s.title(), a) for s, a in sorted(nunca)[:18]))
            if len(nunca) > 18:
                P("  (+%d)" % (len(nunca) - 18))

    P("\n---")
    P("Leia o texto com: python analisar_docx.py texto \"%s\" --de 1 --ate 300"
      % os.path.basename(args.arquivo))


def cmd_texto(args):
    parts = load(args.arquivo)
    styles = Styles(parts["word/styles.xml"])
    body = parts["word/document.xml"].find(W + "body")
    pars = collect_paragraphs(body, styles)
    notes = load_notes(parts["word/footnotes.xml"], styles)

    ini = args.de or 1
    fim = args.ate or len(pars)
    usados = set()

    size_tally = Counter(p.rp["size"] for p in pars if is_body(p) and p.rp.get("size"))
    body_size = size_tally.most_common(1)[0][0] if size_tally else None
    body_start = first_heading_idx(pars)

    print("<!-- %s | paragrafos %d-%d de %d -->\n"
          % (os.path.basename(args.arquivo), ini, fim, len(pars)))
    for p in pars:
        if p.idx < ini or p.idx > fim:
            continue
        t = re.sub(r"[ \t]+", " ", p.text).strip()
        if not t:
            continue
        usados.update(p.notes)
        if p.level is not None:
            print("\n%s [P%d] %s\n" % ("#" * min(p.level + 1, 6), p.idx, t))
        elif is_pseudo_heading(p, body_size):
            print("\n**[P%d] %s**  <!-- pseudo-titulo, sem estilo -->\n" % (p.idx, t))
        elif is_long_citation(p, body_size, body_start):
            print("> [P%d] %s\n" % (p.idx, t))
        else:
            print("[P%d] %s\n" % (p.idx, t))

    if notes and not args.sem_notas:
        print("\n---\n### Notas de rodape citadas neste trecho\n")
        for fid in sorted(usados, key=lambda x: as_int(x, 0)):
            if fid in notes:
                print("[nota %s] %s\n" % (fid, re.sub(r"\s+", " ", notes[fid][0]).strip()))


# ------------------------------------------------------------------ CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("sumario", help="arvore de titulos com faixas de paragrafos")
    s1.add_argument("arquivo")
    s1.set_defaults(func=cmd_sumario)

    s2 = sub.add_parser("forma", help="diagnostico de coerencia formal")
    s2.add_argument("arquivo")
    s2.add_argument("--max-desvios", type=int, default=12)
    s2.set_defaults(func=cmd_forma)

    s3 = sub.add_parser("texto", help="texto corrido com marcadores [Pn]")
    s3.add_argument("arquivo")
    s3.add_argument("--de", type=int, default=None)
    s3.add_argument("--ate", type=int, default=None)
    s3.add_argument("--sem-notas", action="store_true")
    s3.set_defaults(func=cmd_texto)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

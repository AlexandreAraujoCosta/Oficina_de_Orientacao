#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Perfil metrico de um corpus de dissertacoes (.docx e .pdf).

Emite uma linha CSV por trabalho, com indices escala-livre destinados a
comparacao entre trabalhos. Nao julga: mede. Nenhum indice mede qualidade;
todos medem forma, ritmo e higiene. Uma tabela ordenada por qualquer coluna
NAO e um ranking de qualidade.

O ruido por unidade e aceitavel aqui: dilui-se em N, e vies constante nao
atrapalha ordenacao. Para o caso individual, use analisar_docx.py.

Uso:
  python perfil_corpus.py CAMINHO [CAMINHO ...] [--saida perfil.csv] [--recursivo]
  python perfil_corpus.py --resumo perfil.csv

CAMINHO pode ser arquivo .docx/.pdf ou diretorio.
"""

import argparse
import csv
import os
import re
import statistics
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analisar_docx as ad  # noqa: E402

PT_CM = 28.3465
PT_TWIP = 20.0

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ------------------------------------------------------------------ PDF

def _dominante(spans):
    peso = Counter()
    for s in spans:
        n = max(len(s["text"].strip()), 1)
        # corpo medido varia continuamente (11,96 e 12,00 sao a mesma fonte):
        # arredonda a meio ponto, senao a variedade formal fica inflada
        peso[(s["font"], round(s["size"] * 2) / 2, bool(s["flags"] & 2 ** 4))] += n
    return peso.most_common(1)[0][0] if peso else ("", 0.0, False)


def linhas_pdf(doc):
    """Extrai linhas com geometria e tipografia de todas as paginas."""
    out = []
    for np_, page in enumerate(doc, 1):
        alt = page.rect.height
        try:
            d = page.get_text("dict")
        except Exception:
            continue
        for bloco in d.get("blocks", []):
            if bloco.get("type") != 0:
                continue
            for li in bloco.get("lines", []):
                spans = [s for s in li.get("spans", []) if s.get("text", "").strip()]
                if not spans:
                    continue
                texto = "".join(s["text"] for s in spans)
                x0 = min(s["bbox"][0] for s in spans)
                x1 = max(s["bbox"][2] for s in spans)
                y0 = min(s["bbox"][1] for s in spans)
                y1 = max(s["bbox"][3] for s in spans)
                fonte, corpo, negrito = _dominante(spans)
                italico = any(s["flags"] & 2 ** 1 for s in spans)
                out.append({
                    "pag": np_, "texto": texto, "x0": x0, "x1": x1, "y0": y0,
                    "y1": y1, "fonte": fonte, "corpo": corpo, "negrito": negrito,
                    "italico": italico, "rodape": y0 > 0.78 * alt,
                    "bloco": id(bloco),
                })
    return out


NUM_TIT_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+\S")


def paragrafos_pdf(caminho):
    """Reconstroi paragrafos a partir das linhas do PDF, devolvendo objetos
    ad.Paragraph com os mesmos atributos que a via .docx produz."""
    import fitz

    doc = fitz.open(caminho)
    lins = linhas_pdf(doc)
    if not lins:
        n = doc.page_count
        doc.close()
        raise ValueError("PDF sem camada de texto em %d paginas (provavel"
                         " digitalizacao; exigiria OCR)" % n)
    pagina = doc[0].rect
    n_paginas = doc.page_count

    corpos = Counter()
    for l in lins:
        if not l["rodape"]:
            corpos[round(l["corpo"], 1)] += len(l["texto"].strip())
    corpo_base = corpos.most_common(1)[0][0] if corpos else 12.0

    corpo_lins = [l for l in lins if abs(l["corpo"] - corpo_base) < 0.6 and not l["rodape"]]
    margem = statistics.median([l["x0"] for l in corpo_lins]) if corpo_lins else 0.0
    direita = statistics.median([l["x1"] for l in corpo_lins]) if corpo_lins else pagina.width
    alturas = []
    for a, b in zip(lins, lins[1:]):
        if a["pag"] == b["pag"] and 0 < b["y0"] - a["y0"] < 4 * corpo_base:
            alturas.append(b["y0"] - a["y0"])
    salto = statistics.median(alturas) if alturas else corpo_base * 1.2

    ps = {
        "w": pagina.width / PT_CM, "h": pagina.height / PT_CM,
        "left": margem / PT_CM, "right": (pagina.width - direita) / PT_CM,
        "top": min(l["y0"] for l in lins) / PT_CM,
        "bottom": (pagina.height - max(l["y1"] for l in lins)) / PT_CM,
    }

    grupos, atual = [], []
    for i, l in enumerate(lins):
        novo = False
        if not atual:
            novo = False
        else:
            ant = atual[-1]
            recuado = l["x0"] > margem + 0.35 * corpo_base
            curta = ant["x1"] < direita - 2.5 * corpo_base
            gap = (l["pag"] != ant["pag"]) or (l["y0"] - ant["y0"] > 1.55 * salto)
            muda = (abs(l["corpo"] - ant["corpo"]) > 0.6 or l["negrito"] != ant["negrito"]
                    or l["rodape"] != ant["rodape"])
            novo = muda or gap or (recuado and curta) or (curta and recuado)
            if curta and not recuado and not gap and not muda:
                novo = True
        if novo and atual:
            grupos.append(atual)
            atual = []
        atual.append(l)
    if atual:
        grupos.append(atual)

    pars, idx = [], 0
    for g in grupos:
        texto = " ".join(x["texto"] for x in g)
        texto = re.sub(r"(\w)-\s+(\w)", r"\1\2", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        if not texto:
            continue
        idx += 1
        p = ad.Paragraph()
        p.idx = idx
        p.text = texto
        p.in_table = False
        p.style_name = "Nota" if g[0]["rodape"] else "Normal"
        p.style = p.style_name
        peso = Counter()
        for x in g:
            peso[(x["fonte"], round(x["corpo"], 1), x["negrito"], x["italico"])] += len(x["texto"])
        fonte, corpo, negrito, italico = peso.most_common(1)[0][0]
        p.rp = {"font": fonte, "size": corpo, "bold": negrito, "italic": italico,
                "caps": texto.isupper() and len(texto) > 6}
        x0 = min(x["x0"] for x in g)
        prim = g[0]["x0"]
        rest = min([x["x0"] for x in g[1:]], default=prim)
        base = min(x0, rest)
        dentro = []
        for a, b in zip(g, g[1:]):
            if a["pag"] == b["pag"] and 0 < b["y0"] - a["y0"] < 4 * corpo_base:
                dentro.append(b["y0"] - a["y0"])
        ent = statistics.median(dentro) if dentro else salto
        p.pp = {
            "line": max(int(round(240 * ent / max(corpo, 1))), 120),
            "lineRule": "auto",
            "before": 0, "after": 0,
            "ind_left": max(int(round((base - margem) * PT_TWIP)), 0),
            "ind_first": max(int(round((prim - rest) * PT_TWIP)), 0) if prim > rest else 0,
            "align": "both" if len(g) > 1 else "left",
        }
        p.level = None
        p.notes = []
        p.breaks = 0
        p.page_break = False
        p.runs = []
        pars.append(p)
    pars = funde_numero_titulo(pars)
    atribuir_niveis(pars, corpo_base)
    doc.close()
    return pars, ps, n_paginas


SO_NUM_SECAO = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s*$")


def funde_numero_titulo(pars):
    """Funde o paragrafo que so contem o numero da secao com o seguinte.

    Em PDF o numerador e o titulo caem em paragrafos distintos com frequencia
    ('1.1.' num, 'Ancestralidade institucional?' no outro), e sem esta fusao
    nenhuma subsecao e detectada: numero sozinho nao passa em nenhum teste de
    titulo, e o titulo sem numero perde o nivel. Era o problema 1 do plano do
    corpus, e explica n_subsecoes = 0 onde havia dezenas."""
    saida, i = [], 0
    while i < len(pars):
        p = pars[i]
        m = SO_NUM_SECAO.match(p.text or "")
        if m and i + 1 < len(pars):
            prox = pars[i + 1]
            curto = len((prox.text or "").split()) <= 25
            mesma_fonte = abs(prox.rp.get("size", 0) - p.rp.get("size", 0)) < 0.8
            if curto and mesma_fonte:
                prox.text = f"{m.group(1)} {prox.text}".strip()
                saida.append(prox)
                i += 2
                continue
        saida.append(p)
        i += 1
    for n, p in enumerate(saida, start=1):
        p.idx = n
    return saida


def atribuir_niveis(pars, corpo_base):
    """Infere a hierarquia de titulos num PDF, que nao a declara.

    Dissertacao brasileira usa duas convencoes: titulo numerado ('3.2 Nome') e
    titulo nao numerado em versal e negrito, muitas vezes no mesmo corpo do
    texto. A numeracao, quando existe, e mais confiavel e tem prioridade; sem
    ela, ranqueia-se por proeminencia tipografica (corpo, versal, negrito) e o
    nivel sai da posicao no ranking."""
    cand = []
    for p in pars:
        t = p.text.strip()
        # piso de tamanho: a reconstrucao de PDF fragmenta a lista de
        # referencias em pedacos de uma palavra, e 'PEC', '37', 'no' nao sao
        # titulos. Sem esta guarda, um fragmento numerico e tomado por capitulo.
        if not t or len(t) < 8 or len(t.split()) < 2 or len(t) > 150:
            continue
        if eh_sumario(p) or p.style_name == "Nota":
            continue
        caps = t.isupper() and len(t) > 5
        maior = p.rp.get("size", 0) > corpo_base + 0.3
        if not (p.rp.get("bold") or caps or maior):
            continue
        if t.endswith((".", ";", ",")) and not caps and not NUM_TIT_RE.match(t):
            continue
        cand.append((p, caps))
    if not cand:
        return

    numerados = [(p, m) for p, _ in cand for m in [NUM_TIT_RE.match(p.text.strip())] if m]
    if len(numerados) >= 4:
        for p, m in numerados:
            p.level = min(len(m.group(1).split(".")), 6)
        return

    chaves = {}
    for p, caps in cand:
        k = (round(p.rp.get("size", corpo_base) * 2) / 2, bool(p.rp.get("bold")), caps)
        chaves.setdefault(k, []).append(p)
    # proeminencia: corpo maior primeiro, depois versal, depois negrito
    ordem = sorted(chaves, key=lambda k: (-k[0], -int(k[2]), -int(k[1])))
    # descarta chave usada por uma so linha se houver muitas chaves (ruido)
    if len(ordem) > 4:
        ordem = [k for k in ordem if len(chaves[k]) > 1] or ordem
    for nivel, k in enumerate(ordem[:4], 1):
        for p in chaves[k]:
            p.level = nivel


def carregar(caminho):
    """Devolve (paragrafos, geometria, n_paginas, formato)."""
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".pdf":
        pars, ps, n = paragrafos_pdf(caminho)
        return pars, ps, n, "pdf"
    partes = ad.load(caminho)
    estilos = ad.Styles(partes["word/styles.xml"])
    corpo = partes["word/document.xml"].find(ad.W + "body")
    pars = ad.collect_paragraphs(corpo, estilos)
    notas = ad.load_notes(partes["word/footnotes.xml"], estilos)
    for p in pars:
        p.notes = getattr(p, "notes", [])
    ps = ad.page_setup(corpo)
    carregar.notas = notas
    return pars, ps, 0, "docx"


# ------------------------------------------------------------------ indices

ROTULO_RE = re.compile(
    r"(gr[áa]ficos?|tabelas?|figuras?|quadros?|esquemas?)\s*n?[.º°]?\s*"
    r"(\d+(?:\s*(?:,|e|a|até)\s*\d+)*)", re.I)


def rotulos_citados(texto):
    """Rotulos chamados no corpo, cobrindo plural e enumeracao:
    'os graficos 8 e 9', 'tabelas 1 a 3'. Corrige o falso positivo de orfaos."""
    achados = set()
    for m in ROTULO_RE.finditer(texto):
        tipo = ad.sem_acento(m.group(1))[:5].rstrip("S")
        nums = [int(x) for x in re.findall(r"\d+", m.group(2))]
        if len(nums) == 2 and re.search(r"\b(a|at[ée])\b", m.group(2), re.I):
            nums = list(range(min(nums), max(nums) + 1))
        for n in nums:
            achados.add((tipo, n))
    return achados


def eh_sumario(p):
    """Linha de sumario, incluindo os casos que o teste do .docx nao pega: ao
    remover o pontilhado para medir comprimento, apaga-se o proprio ponto que
    antecede o numero de pagina."""
    t = p.text
    return (ad.is_toc_entry(p) or bool(re.search(r"[.…]{4,}", t))
            or bool(re.search(r"\s{3,}\d{1,4}\s*$", t)))


def delimitar(pars):
    """Inicio e fim do texto principal, robustos para PDF.

    Duas armadilhas que a via .docx nao tem: o titulo da capa vira 'titulo' na
    inferencia tipografica, e a linha 'REFERENCIAS .... 105' do sumario parece
    o inicio das referencias. Resolve-se exigindo que o marcador de fim seja a
    ULTIMA ocorrencia e esteja na metade final do documento."""
    n = len(pars)
    heads = [p for p in pars if p.level is not None and p.text.strip()]

    ini = 0
    for p in heads:
        if NUM_TIT_RE.match(p.text.strip()):
            ini = p.idx
            break
    if not ini:
        # comeca depois do ultimo marcador pre-textual (SUMARIO, ABSTRACT...)
        ultimo_pre = 0
        for p in pars:
            if p.idx > 0.35 * n:
                break
            if (p.level is not None and not eh_sumario(p)
                    and ad.PRE_TEXTUAL_RE.match(p.text.strip())
                    and len(p.text.strip()) < 60):
                ultimo_pre = p.idx
        ini = next((p.idx for p in heads if p.idx > ultimo_pre), heads[0].idx if heads else 1)

    fim = n + 1
    for p in pars:
        t = p.text.strip()
        if not t or p.idx < max(ini, 0.5 * n) or eh_sumario(p):
            continue
        if ad.FIM_TEXTO_RE.match(t) and (p.level is not None or len(t) < 60):
            fim = p.idx
            break
    return ini, fim


def normalizar_niveis(pars, ini, fim):
    """Depois de excluir capa e pre-textuais, o menor nivel presente no texto
    principal passa a ser 1, senao 'capitulo' vira uma categoria vazia."""
    niveis = [p.level for p in pars if p.level is not None and ini <= p.idx < fim]
    if not niveis:
        return
    desloc = min(niveis) - 1
    if desloc <= 0:
        return
    for p in pars:
        if p.level is not None:
            p.level = max(p.level - desloc, 1)


def pct(a, b):
    return round(100.0 * a / b, 1) if b else ""


def por_mil(a, w):
    return round(1000.0 * a / w, 2) if w else ""


def indices(caminho, pars, ps, n_paginas, formato):
    d = OrderedDict()
    d["arquivo"] = os.path.basename(caminho)
    d["formato"] = formato
    d["paginas"] = n_paginas or ""

    if not pars:
        return d

    corpos = Counter(p.rp["size"] for p in pars if ad.is_body(p) and p.rp.get("size"))
    corpo_base = corpos.most_common(1)[0][0] if corpos else None
    ini, fim = delimitar(pars)
    normalizar_niveis(pars, ini, fim)
    heads = [p for p in pars if p.level is not None and p.text.strip()]
    w_total = sum(ad.words(p.text) for p in pars)
    principal = [p for p in pars if ini <= p.idx < fim]
    w_princ = sum(ad.words(p.text) for p in principal) or 1

    d["palavras_total"] = w_total
    d["palavras_texto_principal"] = w_princ
    d["pct_pos_textual"] = pct(w_total - w_princ, w_total)

    # --- estrutura
    caps = [h for h in heads if h.level == 1 and ini <= h.idx < fim]
    lim = [c.idx for c in caps] + [fim]
    tam_cap = [sum(ad.words(p.text) for p in pars[lim[i] - 1:lim[i + 1] - 1])
               for i in range(len(caps))]
    d["n_capitulos"] = len(caps)
    d["n_subsecoes"] = len([h for h in heads if h.level == 2 and ini <= h.idx < fim])
    d["profundidade"] = max([h.level for h in heads], default=0)
    d["pct_maior_capitulo"] = pct(max(tam_cap), sum(tam_cap)) if tam_cap else ""
    d["cv_capitulos"] = (round(statistics.pstdev(tam_cap) / statistics.mean(tam_cap), 2)
                         if len(tam_cap) > 1 and statistics.mean(tam_cap) else "")
    marcos = sorted(set([h.idx for h in heads if h.level in (1, 2) and ini <= h.idx < fim] + [fim]))
    tam_sub = [sum(ad.words(p.text) for p in pars[marcos[i] - 1:marcos[i + 1] - 1])
               for i in range(len(marcos) - 1)]
    tam_sub = [t for t in tam_sub if t > 0]
    d["razao_subsecao_max_mediana"] = (round(max(tam_sub) / statistics.median(tam_sub), 1)
                                       if len(tam_sub) > 2 else "")

    # --- ritmo
    prosa = [p for p in pars if ad.is_prosa(p, corpo_base) and ini <= p.idx < fim]
    cpl = ad.chars_por_linha(ps, corpo_base) or 78.0
    if prosa:
        comps = [len(p.text.strip()) for p in prosa]
        frases = [ad.sentencas(p.text) for p in prosa]
        piso = 10 * cpl
        d["mediana_caracteres"] = int(statistics.median(comps))
        d["mediana_linhas"] = round(statistics.median(comps) / cpl, 1)
        d["pct_abaixo_piso"] = pct(len([c for c in comps if c < piso]), len(comps))
        d["pct_frase_unica"] = pct(len([f for f in frases if f == 1]), len(frases))
        d["cv_paragrafo"] = (round(statistics.pstdev(comps) / statistics.mean(comps), 2)
                             if statistics.mean(comps) else "")
        curtos = {p.idx for p, c in zip(prosa, comps) if c < piso}
        corta = {p.idx for p in pars if p.level is not None
                 or ad.LEGENDA_RE.match(p.text.strip())}
        runs, seq = 0, 0
        ant = None
        for p in prosa:
            emenda = ant is None or (p.idx - ant <= 3 and not any(
                j in corta for j in range(ant + 1, p.idx)))
            if p.idx in curtos and emenda:
                seq += 1
            else:
                runs += 1 if seq >= 3 else 0
                seq = 1 if p.idx in curtos else 0
            ant = p.idx
        runs += 1 if seq >= 3 else 0
        d["staccato_por_mil"] = por_mil(runs, w_princ)
    else:
        for k in ("mediana_caracteres", "mediana_linhas", "pct_abaixo_piso",
                  "pct_frase_unica", "cv_paragrafo", "staccato_por_mil"):
            d[k] = ""

    # --- aparato
    notas = getattr(carregar, "notas", {}) if formato == "docx" else {}
    if formato == "pdf":
        nl = [p for p in pars if p.style_name == "Nota" and len(p.text.strip()) > 30]
        n_notas, subst = len(nl), len([p for p in nl if len(p.text) > 400])
    else:
        n_notas = len(notas)
        subst = len([1 for t, _ in notas.values() if len(t) > 400])
    d["notas_por_mil"] = por_mil(n_notas, w_princ)
    d["pct_notas_substantivas"] = pct(subst, n_notas)
    cits = [p for p in pars if ad.is_long_citation(p, corpo_base, ini) and p.idx < fim]
    d["citacoes_longas_por_mil"] = por_mil(len(cits), w_princ)

    # --- bibliografia
    autores_inst, entradas = Counter(), {}
    ref_ini = next((p.idx for p in pars if p.idx > ini and p.text.strip()
                    and re.match(r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA)\b", p.text.strip(), re.I)
                    and (p.level is not None or len(p.text.strip()) < 60)
                    and not ad.is_toc_entry(p)), None)
    if ref_ini:
        ref_fim = next((p.idx for p in pars if p.idx > ref_ini and p.text.strip()
                        and re.match(r"^\s*(AP[ÊE]NDICES?|ANEXOS?)\b", p.text.strip(), re.I)),
                       len(pars) + 1)
        for p in pars[ref_ini:ref_fim - 1]:
            t = p.text.strip()
            if len(t) < 40 or ad.is_toc_entry(p):
                continue
            # indexa TODOS os sobrenomes da entrada, nao so o primeiro: o corpo
            # cita "Barbosa e Esteves (2020)" e a lista traz os dois
            cabeca = t[:260]
            sobrenomes = {ad.sem_acento(x) for x in
                          re.findall(r"([A-ZÀ-Ý][A-ZÀ-Ý'\-]{2,})\s*,", cabeca)}
            my = re.search(r"\b((?:19|20)\d{2})", t)
            if sobrenomes and my:
                for s in sobrenomes:
                    entradas.setdefault((s, my.group(1)), []).append(p.idx)
    citacoes = {}
    for p in pars:
        if not (ini <= p.idx < (ref_ini or fim)) or ad.looks_like_code(p) or ad.is_toc_entry(p):
            continue
        for rx in (ad.CIT_ANO_RE, ad.CIT_PAREN_RE):
            for m in rx.finditer(p.text):
                nome = m.group(1).upper()
                if nome in ad.NAO_AUTOR or len(nome) < 3:
                    continue
                citacoes.setdefault((ad.sem_acento(nome), m.group(2)), []).append(p.idx)
                autores_inst[ad.sem_acento(nome)] += 1
    d["entradas_lista"] = len(entradas)
    d["autores_distintos"] = len(autores_inst)
    d["autores_por_mil"] = por_mil(len(autores_inst), w_princ)
    d["pct_entradas_nao_citadas"] = pct(len([k for k in entradas if k not in citacoes]), len(entradas))
    d["pct_citacoes_sem_entrada"] = pct(len([k for k in citacoes if k not in entradas]), len(citacoes))
    d["pares_ambiguos"] = len([k for k, v in entradas.items() if len(v) > 1])
    conc = []
    for i in range(len(marcos) - 1):
        seg = [p for p in pars[marcos[i] - 1:marcos[i + 1] - 1] if ad.is_prosa(p, corpo_base)]
        c = Counter()
        for p in seg:
            for rx in (ad.CIT_ANO_RE, ad.CIT_PAREN_RE):
                for m in rx.finditer(p.text):
                    n = m.group(1).upper()
                    if n not in ad.NAO_AUTOR and len(n) >= 3:
                        c[ad.sem_acento(n)] += 1
        if sum(c.values()) >= 6:
            conc.append(c.most_common(1)[0][1] / sum(c.values()))
    d["concentracao_max"] = round(100 * max(conc), 1) if conc else ""
    # sistema de citacao: os indices de bibliografia so fazem sentido em
    # autor-data. Trabalho que cita em nota de rodape zera aquelas colunas
    # por genero, nao por defeito.
    inst_mil = 1000.0 * sum(autores_inst.values()) / w_princ
    nota_mil = 1000.0 * n_notas / w_princ
    d["sistema_citacao"] = ("autor-data" if inst_mil >= 2.0
                            else "nota" if nota_mil >= 3.0
                            else "misto/indefinido")

    # --- graficos
    legendas = [p for p in pars if ad.LEGENDA_RE.match(p.text.strip())
                and not ad.is_toc_entry(p) and p.idx >= ini]
    corpo_txt = " ".join(p.text for p in pars if ad.is_prosa(p, corpo_base) and p.idx < fim)
    chamados = rotulos_citados(corpo_txt)
    orfas, com_inf, blocos, dens = 0, 0, 0, []
    mapa = {p.idx: p for p in pars}
    for leg in legendas:
        m = ad.LEGENDA_RE.match(leg.text.strip())
        chave = (ad.sem_acento(m.group(1))[:5].rstrip("S"), int(m.group(2)))
        if chave not in chamados:
            orfas += 1
        bloco, j = [], leg.idx + 1
        while j <= len(pars) and len(bloco) < 6:
            q = mapa.get(j)
            j += 1
            if q is None or q.level is not None or ad.LEGENDA_RE.match(q.text.strip()):
                break
            if ad.is_prosa(q, corpo_base):
                bloco.append(q)
        if bloco:
            blocos += 1
            txt = " ".join(b.text for b in bloco)
            dens.append(ad.densidade_numerica(txt))
            if ad.INFERENCIA_RE.search(txt):
                com_inf += 1
    d["elementos_por_mil"] = por_mil(len(legendas), w_princ)
    d["pct_elementos_orfaos"] = pct(orfas, len(legendas))
    d["pct_blocos_com_inferencia"] = pct(com_inf, blocos)
    d["densidade_numerica_mediana"] = round(100 * statistics.median(dens), 1) if dens else ""

    # --- forma
    bodies = [p for p in pars if ad.is_body(p)]
    sigs = Counter(p.signature() for p in bodies)
    d["pct_formatacao_dominante"] = pct(sigs.most_common(1)[0][1], len(bodies)) if sigs else ""
    d["n_formatacoes_corpo"] = len(sigs)
    por_nivel = {}
    for h in heads:
        por_nivel.setdefault(h.level, set()).add(h.signature())
    d["n_formatacoes_titulo_max"] = max([len(v) for v in por_nivel.values()], default=0)
    d["n_fontes"] = len({p.rp.get("font") for p in pars if p.text.strip() and p.rp.get("font")})
    d["n_corpos"] = len({p.rp.get("size") for p in pars if p.text.strip() and p.rp.get("size")})

    # --- escrita
    marcas = [
        ("travessao", re.compile(r"[—–]")),
        ("nao_x_mas_y", re.compile(
            r"\bn[ãa]o\s+(?:apenas|s[óo]|somente)?[^,.;:]{2,45},?\s+mas\b", re.I)),
        ("arremate", re.compile(
            r"\b(al[ée]m disso|ademais|outrossim|em suma|em [úu]ltima an[áa]lise|"
            r"por fim|dessa forma|dessa maneira)\b", re.I)),
        ("anuncio", re.compile(
            r"\b(vale|cumpre|importa|conv[ée]m)\s+(notar|ressaltar|destacar|"
            r"mencionar|observar|frisar|salientar)\b", re.I)),
        ("elogio_abstrato", re.compile(
            r"\b(robust[oa]s?|significativ[oa]s?|relevant[ees]s?|cruciais?|"
            r"essenciais?|ineg[áa]vel|not[áa]vel)\b", re.I)),
    ]
    txt_prosa = " ".join(p.text for p in prosa)
    for nome, rx in marcas:
        d[nome + "_por_mil"] = por_mil(len(rx.findall(txt_prosa)), w_princ)
    d["negrito_por_mil"] = por_mil(len([p for p in prosa if p.rp.get("bold")]), w_princ)

    # --- estrato: empiricidade
    emp = 0.0
    if dens:
        emp += min(statistics.median(dens) * 100 / 8.0, 1.0)
    emp += min(len(legendas) / max(w_princ / 1000.0, 1) / 1.0, 1.0)
    if any(re.search(r"\b(metodolog|m[ée]todo|procedimentos metodol)", h.text, re.I)
           for h in heads):
        emp += 1.0
    d["idx_empiricidade"] = round(emp / 3.0, 2)
    return d


# ------------------------------------------------------------------ CLI

EXTS = (".docx", ".pdf")


def coletar(caminhos, recursivo):
    arqs = []
    for c in caminhos:
        if os.path.isdir(c):
            if recursivo:
                for raiz, _, nomes in os.walk(c):
                    arqs += [os.path.join(raiz, n) for n in nomes
                             if n.lower().endswith(EXTS) and not n.startswith("~$")]
            else:
                arqs += [os.path.join(c, n) for n in sorted(os.listdir(c))
                         if n.lower().endswith(EXTS) and not n.startswith("~$")]
        elif c.lower().endswith(EXTS):
            arqs.append(c)
    return arqs


def cmd_perfil(args):
    arqs = coletar(args.caminhos, args.recursivo)
    if not arqs:
        sys.exit("Nenhum .docx ou .pdf encontrado.")
    linhas = []
    for i, a in enumerate(arqs, 1):
        print("[%d/%d] %s" % (i, len(arqs), os.path.basename(a)), file=sys.stderr)
        try:
            pars, ps, n, fmt = carregar(a)
            linhas.append(indices(a, pars, ps, n, fmt))
        except Exception as e:
            print("   FALHOU: %s: %s" % (type(e).__name__, e), file=sys.stderr)
            linhas.append(OrderedDict([("arquivo", os.path.basename(a)),
                                       ("formato", "erro"), ("erro", str(e)[:120])]))
    campos = []
    for l in linhas:
        for k in l:
            if k not in campos:
                campos.append(k)
    destino = open(args.saida, "w", newline="", encoding="utf-8-sig") if args.saida else sys.stdout
    w = csv.DictWriter(destino, fieldnames=campos, delimiter=";", extrasaction="ignore")
    w.writeheader()
    for l in linhas:
        w.writerow(l)
    if args.saida:
        destino.close()
        print("\n%d trabalhos gravados em %s" % (len(linhas), args.saida), file=sys.stderr)


def cmd_resumo(args):
    with open(args.csv, newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    if not linhas:
        sys.exit("CSV vazio.")
    estratos = {"todos": linhas}
    if args.estratificar:
        for l in linhas:
            try:
                e = "empirico" if float(l.get("idx_empiricidade") or 0) >= 0.5 else "nao empirico"
            except ValueError:
                e = "indefinido"
            estratos.setdefault("%s / %s / %s" % (l.get("formato", "?"), e,
                                                  l.get("sistema_citacao", "?")), []).append(l)
        estratos.pop("todos", None)
    print("Percentis por indice. Nenhum destes mede qualidade.")
    print("Indices de forma NAO sao comparaveis entre .docx e .pdf: no primeiro")
    print("o valor e declarado, no segundo e medido com ruido. Compare dentro do")
    print("mesmo formato, do mesmo genero e do mesmo sistema de citacao.\n")
    for nome, grupo in estratos.items():
        print("== %s (n=%d) ==" % (nome, len(grupo)))
        print("%-32s %8s %8s %8s %8s %8s" % ("indice", "p10", "p25", "p50", "p75", "p90"))
        for campo in grupo[0]:
            if campo in ("arquivo", "formato", "erro"):
                continue
            vals = []
            for l in grupo:
                try:
                    vals.append(float(str(l.get(campo, "")).replace(",", ".")))
                except (ValueError, TypeError):
                    pass
            if len(vals) < 3:
                continue
            vals.sort()
            q = [vals[min(int(p * len(vals)), len(vals) - 1)] for p in (.1, .25, .5, .75, .9)]
            print("%-32s %8.2f %8.2f %8.2f %8.2f %8.2f" % (campo, *q))
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("caminhos", nargs="*", help="arquivos .docx/.pdf ou diretorios")
    ap.add_argument("--saida", help="grava o CSV neste arquivo")
    ap.add_argument("--recursivo", action="store_true")
    ap.add_argument("--resumo", metavar="CSV", help="imprime percentis de um CSV ja gerado")
    ap.add_argument("--estratificar", action="store_true",
                    help="com --resumo, separa empiricos de nao empiricos")
    args = ap.parse_args()
    if args.resumo:
        args.csv = args.resumo
        cmd_resumo(args)
    elif args.caminhos:
        cmd_perfil(args)
    else:
        ap.error("informe caminhos ou --resumo")


if __name__ == "__main__":
    main()

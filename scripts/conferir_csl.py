#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Confere um estilo CSL contra uma base de teste, e exibe o que ele produz.

A especificacao de referencias do PMPD e o arquivo .csl. Este programa gera o
documento legivel a partir dele: nao descreve a norma em prosa, exibe a saida
que a norma produz, item por item. Quem decide olha o resultado, e nao o XML.

Renderiza com pandoc + citeproc. Nao e o mesmo motor do Zotero (citeproc-js),
e a diferenca aparece em termos de locale; onde isso importa, o relatorio avisa.

  python conferir_csl.py pmpd.csl
  python conferir_csl.py pmpd.csl arcos.csl --comparar
  python conferir_csl.py pmpd.csl --md csl/AMOSTRA-PMPD.md
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(RAIZ, "csl", "fixture.json")
ZOTERO_STYLES = os.path.join(os.path.expanduser("~"), "Zotero", "styles")


# ------------------------------------------------------------------ renderizacao

def achar_estilo(nome):
    """Aceita caminho, nome com .csl, ou nome nu instalado no Zotero."""
    for cand in (nome, nome + ".csl",
                 os.path.join(ZOTERO_STYLES, nome),
                 os.path.join(ZOTERO_STYLES, nome + ".csl")):
        if os.path.isfile(cand):
            return os.path.abspath(cand)
    sys.exit("Estilo nao encontrado: %s (procurei tambem em %s)" % (nome, ZOTERO_STYLES))


TAG_RE = re.compile(r"<[^>]+>")


def destag(h):
    """HTML da entrada -> texto. So o que citeproc emite: span, i, b, a, sup."""
    # Sobrescrito: citeproc devolve "n<sup>o</sup>" onde a base tem "nº".
    # Apagar a marca faria a amostra dizer "no", que nao e o que sai no Word.
    h = re.sub(r"<sup>o</sup>", "º", h)
    h = re.sub(r"<sup>a</sup>", "ª", h)
    h = re.sub(r"<sup>(.*?)</sup>", r"^(\1)", h)
    h = TAG_RE.sub("", h)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        h = h.replace(a, b)
    return " ".join(h.split())


def renderizar(csl, itens):
    """Devolve ({id: citacao}, {id: referencia}) numa rodada so de pandoc.

    A saida e HTML porque citeproc marca cada entrada da bibliografia com
    id="ref-<id>". Casar por titulo nao serve: o titulo de um livro aparece
    dentro da referencia do capitulo que esta nele, e o primeiro conferidor
    escrito aqui pareou os dois trocados. Medido em 27/08/2026.

    Uma rodada so, e nao uma por item, porque desambiguacao (2018a/2018b) e
    repeticao de autoria so existem quando a lista inteira esta presente.
    """
    corpo = "\n\n".join("GG%sGG @%s GG" % (i["id"], i["id"]) for i in itens)
    doc = "---\nnocite: \"@*\"\nlang: pt-BR\n---\n\n%s\n" % corpo

    tmp = tempfile.mkdtemp(prefix="csl-")
    fbib = os.path.join(tmp, "b.json")
    fdoc = os.path.join(tmp, "d.md")
    with open(fbib, "w", encoding="utf-8") as f:
        json.dump(itens, f, ensure_ascii=False)
    with open(fdoc, "w", encoding="utf-8") as f:
        f.write(doc)

    r = subprocess.run(
        ["pandoc", fdoc, "--citeproc", "--bibliography", fbib,
         "--csl", csl, "-t", "html", "--wrap=none"],
        capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit("pandoc falhou em %s:\n%s" % (os.path.basename(csl), r.stderr))

    saida = r.stdout
    refs = {}
    for m in re.finditer(
            r'id="ref-([^"]+)"[^>]*>(.*?)(?=<div id="ref-|</div>\s*</div>\s*$|\Z)',
            saida, re.S):
        refs[m.group(1)] = destag(m.group(2))

    citacoes = {}
    for m in re.finditer(r"GG(\S+?)GG(.*?)GG", destag(saida), re.S):
        citacoes[m.group(1)] = m.group(2).strip()

    faltam = [i["id"] for i in itens if i["id"] not in refs]
    if faltam:
        print("AVISO: %d itens sem entrada na bibliografia: %s"
              % (len(faltam), ", ".join(faltam)), file=sys.stderr)
    return citacoes, refs


# ------------------------------------------------------------------ conferencia

def normalizar(s):
    """Sem acento, sem caixa, so alfanumerico: para procurar campo na saida."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


# Campos que a saida deveria conter, e o que se procura de cada um.
CAMPOS = [
    ("title", lambda v: v),
    ("publisher", lambda v: v),
    ("publisher-place", lambda v: v.split(",")[0]),
    ("genre", lambda v: v.split("(")[0]),
    ("edition", lambda v: v),
    ("page", lambda v: v.split("-")[0]),
    ("volume", lambda v: v),
    ("issue", lambda v: v),
    ("container-title", lambda v: v),
    ("DOI", lambda v: v),
    ("URL", lambda v: v.split("//")[-1].split("/")[0]),
]

COLAGEM_RE = re.compile(r"[a-záéíóúâêôãõçü0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇÜ]")
# Excecoes reais medidas na base: abreviaturas e nomes proprios com maiuscula
# interna. Sem elas o conferidor acusa "S.Paulo" e "GV" como defeito.
COLAGEM_OK = ("S.Paulo", "DOI", "LGPD", "IA", "TCU", "PMPD", "UnB", "GV", "DF")


def conferir(item, ref):
    """Defeitos mecanicos de uma referencia. So o que se prova sem a norma."""
    achados = []
    nref = normalizar(ref)

    for campo, extrair in CAMPOS:
        v = item.get(campo)
        if not v:
            continue
        alvo = normalizar(str(extrair(v)))[:24]
        if alvo and alvo not in nref:
            achados.append("campo ausente: %s = %r" % (campo, str(v)[:48]))

    ano = None
    if item.get("issued", {}).get("date-parts"):
        ano = str(item["issued"]["date-parts"][0][0])
    if ano and ano not in ref:
        achados.append("ano ausente: %s" % ano)

    # Campo colado no vizinho: acha o valor do campo na saida e olha o caractere
    # anterior. E melhor que procurar maiuscula depois de minuscula, porque nao
    # depende da caixa e diz qual campo colou.
    for campo in ("container-title", "publisher", "publisher-place", "genre"):
        v = item.get(campo)
        if not v:
            continue
        alvo = str(v).split(",")[0].split("(")[0].strip()[:20]
        j = ref.find(alvo)
        if j > 0 and (ref[j - 1].isalnum() or ref[j - 1] in ")]"):
            achados.append("campo colado no anterior: %s em ...%s..."
                           % (campo, ref[max(0, j - 20):j + 12]))

    # Rede de seguranca, para colagem entre coisas que nao sao campo nomeado.
    # A excecao respeita limite de palavra: sem isso "DF" apagava o miolo de
    # SUNDFELD e "IA" o de ASSOCIACAO. Medido em 27/08/2026.
    contexto = ref
    for ok in COLAGEM_OK:
        contexto = re.sub(r"\b%s\b" % re.escape(ok), "x" * len(ok), contexto)
    for m in COLAGEM_RE.finditer(contexto):
        j = m.start()
        achados.append("palavras coladas: ...%s..." % contexto[max(0, j - 18):j + 18])

    if ".." in ref.replace("...", ""):
        achados.append("ponto duplicado")
    if re.search(r"[a-z0-9]\.[a-z]", ref.replace("www.", "").replace(".com", "")
                 .replace(".br", "").replace(".gov", "").replace(".org", "")
                 .replace(".htm", "").replace(".jus", "").replace(".asp", "")
                 .replace(".unb", "").replace(".stf", "").replace(".conjur", "")
                 .replace(".tcu", "").replace(".doi", "").replace(".planalto", "")
                 .replace(".portal", "").replace(".exemplo", "")):
        achados.append("falta espaco depois de ponto")
    # Ano com letra colada na frente: "abr. b2018". So conta se os quatro
    # digitos forem um ano plausivel. Sem essa trava o conferidor acusava a
    # pagina "e2145" de artigo eletronico. Medido em 27/08/2026.
    if re.search(r"(?<![\w.])[a-z](1[6-9]\d\d|20\d\d)\b", ref):
        achados.append("sufixo de desambiguacao dentro da data")
    return achados


# ------------------------------------------------------------------ saida

def emitir(csl, itens, citacoes, refs, out):
    nome = os.path.basename(csl)
    w = out.write
    w("# Amostra de referencias: %s\n\n" % nome)
    w("Gerado por `scripts/conferir_csl.py` a partir de `csl/fixture.json`.\n")
    w("Nao editar a mao: a especificacao e o `.csl`, e este arquivo sai dele.\n\n")
    w("Base de teste: %d itens, %d tipos.\n\n"
      % (len(itens), len(set(i["type"] for i in itens))))

    total = 0
    w("## Item por item, na ordem da lista de referencias\n\n")
    w("A ordem importa: o travessao de autoria repetida (`_____`) so faz sentido\n")
    w("em relacao a entrada anterior. Listar na ordem da base, e nao na da lista,\n")
    w("mostrava o travessao apontando para o autor errado.\n\n")
    por_id = {i["id"]: i for i in itens}
    ordem = [por_id[k] for k in refs if k in por_id]
    ordem += [i for i in itens if i["id"] not in refs]
    for i in ordem:
        ref = refs.get(i["id"])
        w("### `%s` — tipo CSL `%s`\n\n" % (i["id"], i["type"]))
        w("- No texto: %s\n" % (citacoes.get(i["id"], "(nao saiu)")))
        w("- Na lista: %s\n" % (ref or "(NAO ENCONTRADA na bibliografia)"))
        if ref:
            probs = conferir(i, ref)
            total += len(probs)
            for p in probs:
                w("- ⚠ %s\n" % p)
        w("\n")

    w("## Contagem\n\n")
    w("%d apontamentos mecanicos em %d itens.\n\n" % (total, len(itens)))
    w("O que este programa NAO confere: se a forma corresponde a NBR 6023:2025\n")
    w("e a NBR 10520:2023. Isso se le na norma, e a norma nao esta aqui.\n")
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("estilos", nargs="+", help="arquivo .csl ou nome instalado no Zotero")
    ap.add_argument("--fixture", default=FIXTURE)
    ap.add_argument("--md", default=None, help="grava a amostra em arquivo")
    ap.add_argument("--comparar", action="store_true",
                    help="so a linha de cada item, lado a lado")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    with open(args.fixture, encoding="utf-8") as f:
        itens = json.load(f)

    estilos = [achar_estilo(e) for e in args.estilos]

    if args.comparar:
        rend = {e: renderizar(e, itens) for e in estilos}
        for i in itens:
            print("\n### %s (%s)" % (i["id"], i["type"]))
            for e in estilos:
                cit, refs = rend[e]
                print("  [%s] %s" % (os.path.basename(e)[:-4],
                                     refs.get(i["id"], "(ausente)")))
        return

    for e in estilos:
        cit, refs = renderizar(e, itens)
        if args.md:
            with open(args.md, "w", encoding="utf-8") as f:
                n = emitir(e, itens, cit, refs, f)
            print("Gravado: %s (%d apontamentos)" % (args.md, n))
        else:
            emitir(e, itens, cit, refs, sys.stdout)


if __name__ == "__main__":
    main()

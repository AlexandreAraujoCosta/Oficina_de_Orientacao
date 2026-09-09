# -*- coding: utf-8 -*-
"""Gera uma copia do .docx com as alteracoes controladas aceitas, sem tocar no original.

POR QUE ISTO EXISTE

A cadeia de extracao se recusa a ler um `.docx` com alteracoes pendentes, e a
recusa esta certa: com elas de pe, o numero de paragrafo que o programa produz nao
bate com o que o autor ve ao abrir. O `normalizar_docx.py` diz por que nao decide
sozinho: **se a marcacao for de quem orienta, aceita-la em silencio apagaria o
trabalho dessa pessoa.**

Este programa nao decide nada: ele executa uma decisao ja tomada, e diz por escrito
o que executou, inclusive quantas marcas eram de cada autor. **A copia e nova**, e o
arquivo do autor fica intacto.

POR QUE NAO SE FAZ COM EXPRESSAO REGULAR

Foi tentado em 08/09/2026 e o arquivo saiu com XML invalido (`mismatched tag`), o
que so apareceu quando a extracao quebrou. Marcacao de revisao aninha, e apagar
`<w:del>...</w:del>` por texto corta no meio de estrutura que continua aberta.

O QUE ELE FAZ, e cada linha e uma regra do formato

    <w:ins>      o texto inserido FICA. Some so a casca.
    <w:del>      o trecho excluido SAI inteiro, com o <w:delText> dentro.
    <w:pPr><w:rPr><w:del/>   marca de paragrafo excluida: o paragrafo se FUNDE
                 com o seguinte, que e o que o Word faz. Sem isso sobra um
                 paragrafo vazio onde havia um item de lista, e o autor ve um
                 marcador orfao.
    <w:moveFrom> sai; <w:moveTo> fica, que e a mesma regra da exclusao e da
                 insercao para texto movido.
    <w:*Change>  a marca de formatacao anterior sai, e o formato atual fica.

Uso:
    python scripts/aceitar_alteracoes.py <trabalho.docx> <saida.docx>
"""
import argparse
import collections
import io
import re
import shutil
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)


def q(nome):
    return "{%s}%s" % (W, nome)


SAEM = {q("del"), q("moveFrom")}
CASCAS = {q("ins"), q("moveTo")}
MUDANCAS = {q("rPrChange"), q("pPrChange"), q("tblPrChange"), q("trPrChange"),
            q("tcPrChange"), q("sectPrChange"), q("numberingChange"),
            q("cellIns"), q("cellDel"), q("cellMerge"), q("customXmlDelRangeStart"),
            q("customXmlDelRangeEnd"), q("customXmlInsRangeStart"),
            q("customXmlInsRangeEnd"), q("moveFromRangeStart"),
            q("moveFromRangeEnd"), q("moveToRangeStart"), q("moveToRangeEnd")}


def autores(raiz):
    de = collections.Counter()
    for el in raiz.iter():
        if el.tag in SAEM or el.tag in CASCAS:
            de[el.get(q("author"), "?")] += 1
    return de


def paragrafo_some(p):
    """A marca de paragrafo foi excluida? Entao ele se funde com o seguinte."""
    ppr = p.find(q("pPr"))
    if ppr is None:
        return False
    rpr = ppr.find(q("rPr"))
    return rpr is not None and rpr.find(q("del")) is not None


def aceitar(raiz):
    """Aplica as regras, de baixo para cima, para nao invalidar a arvore."""
    pais = {c: p for p in raiz.iter() for c in p}
    # 1. o que sai, sai inteiro
    for el in [e for e in raiz.iter() if e.tag in SAEM]:
        pai = pais.get(el)
        if pai is not None:
            pai.remove(el)
    # 2. a casca do que fica some, e os filhos sobem para o lugar dela
    mudou = True
    while mudou:
        mudou = False
        pais = {c: p for p in raiz.iter() for c in p}
        for el in [e for e in raiz.iter() if e.tag in CASCAS]:
            pai = pais.get(el)
            if pai is None:
                continue
            i = list(pai).index(el)
            pai.remove(el)
            for j, filho in enumerate(list(el)):
                pai.insert(i + j, filho)
            mudou = True
            break
    # 3. as marcas de mudanca de formato saem, e o formato atual fica
    pais = {c: p for p in raiz.iter() for c in p}
    for el in [e for e in raiz.iter() if e.tag in MUDANCAS]:
        pai = pais.get(el)
        if pai is not None:
            pai.remove(el)
    return raiz


def marcar_para_fundir(raiz):
    """Anota QUAIS paragrafos se fundem, ANTES de aceitar apagar o sinal.

    A ordem e a armadilha, e o autoteste a pegou em 08/09/2026: `aceitar()` remove
    todo `<w:del>`, inclusive o que fica dentro de `<w:pPr><w:rPr>` marcando que a
    marca de paragrafo foi excluida. Fundir depois disso nao acha mais o sinal.
    """
    return {id(p) for p in raiz.iter(q("p")) if paragrafo_some(p)}


def fundir_paragrafos(corpo, marcados):
    """Paragrafo com a marca excluida junta-se ao seguinte, como o Word faz."""
    fundidos = 0
    filhos = list(corpo)
    i = 0
    while i < len(filhos) - 1:
        p = filhos[i]
        if p.tag == q("p") and id(p) in marcados:
            seg = filhos[i + 1]
            if seg.tag == q("p"):
                for filho in list(p):
                    if filho.tag != q("pPr"):
                        # entra ANTES do conteudo do seguinte, preservando a ordem
                        seg.insert(len(list(seg)) if False else
                                   (1 if seg.find(q("pPr")) is not None else 0), filho)
                corpo.remove(p)
                filhos = list(corpo)
                fundidos += 1
                continue
        i += 1
    return fundidos


def autoteste():
    falhas = []
    xml = ('<w:document xmlns:w="%s"><w:body>'
           '<w:p><w:r><w:t>fica</w:t></w:r>'
           '<w:ins w:author="A"><w:r><w:t> inserido</w:t></w:r></w:ins>'
           '<w:del w:author="B"><w:r><w:delText> excluido</w:delText></w:r></w:del>'
           '</w:p>'
           '<w:p><w:pPr><w:rPr><w:del w:author="A"/></w:rPr></w:pPr>'
           '<w:r><w:t>primeira metade</w:t></w:r></w:p>'
           '<w:p><w:r><w:t>segunda metade</w:t></w:r></w:p>'
           '</w:body></w:document>' % W)
    raiz = ET.fromstring(xml)
    de = autores(raiz)
    if de.get("A") != 2 or de.get("B") != 1:
        falhas.append("nao conta as marcas por autor: %r" % dict(de))
    marcados = marcar_para_fundir(raiz)
    aceitar(raiz)
    corpo = raiz.find(q("body"))
    n = fundir_paragrafos(corpo, marcados)
    txt = ["".join(t.text or "" for t in p.iter(q("t"))) for p in corpo.findall(q("p"))]
    if txt and "inserido" not in txt[0]:
        falhas.append("perde o texto inserido: %r" % txt)
    if txt and "excluido" in txt[0]:
        falhas.append("mantem o texto excluido: %r" % txt)
    # CONTROLE POSITIVO da fusao: os dois paragrafos viram um, na ordem
    if n != 1:
        falhas.append("nao funde o paragrafo cuja marca foi excluida: %d" % n)
    if len(txt) != 2:
        falhas.append("numero de paragrafos errado depois da fusao: %r" % txt)
    elif "primeira metade" not in txt[1] or "segunda metade" not in txt[1]:
        falhas.append("funde na ordem errada: %r" % txt[1])
    # e nada de marca de revisao pode sobrar
    if any(e.tag in SAEM | CASCAS for e in raiz.iter()):
        falhas.append("sobrou marca de revisao depois de aceitar")
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("entrada")
    ap.add_argument("saida")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio programa esta quebrado, e nao gero copia nenhuma:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: mantem o inserido, tira o excluido, funde o paragrafo cuja "
          "marca foi excluida na ordem certa, e nao deixa marca de revisao para tras")

    entrada, saida = Path(a.entrada), Path(a.saida)
    if saida.exists():
        print("\n  %s ja existe, e eu nao sobrescrevo." % saida.name)
        return 2

    zin = zipfile.ZipFile(str(entrada))
    alvos = [n for n in zin.namelist()
             if re.match(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$", n)]
    total, fundidos, de = 0, 0, collections.Counter()
    novos = {}
    for nome in alvos:
        raiz = ET.fromstring(zin.read(nome))
        d = autores(raiz)
        de.update(d)
        total += sum(d.values())
        marcados = marcar_para_fundir(raiz)
        aceitar(raiz)
        corpo = raiz.find(q("body"))
        if corpo is not None:
            fundidos += fundir_paragrafos(corpo, marcados)
        novos[nome] = ET.tostring(raiz, encoding="utf-8", xml_declaration=True)

    zo = zipfile.ZipFile(str(saida), "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        zo.writestr(it, novos.get(it.filename) or zin.read(it.filename))
    zo.close()

    # CONFERENCIA DA PROPRIA SAIDA: o arquivo tem de abrir, e nao pode sobrar marca
    try:
        zc = zipfile.ZipFile(str(saida))
        r = ET.fromstring(zc.read("word/document.xml"))
    except Exception as e:
        print("\n  a copia saiu invalida e eu a apago: %s" % e)
        saida.unlink()
        return 2
    resto = sum(1 for e in r.iter() if e.tag in SAEM | CASCAS)
    if resto:
        print("\n  sobraram %d marca(s) de revisao na copia." % resto)
        return 2

    print("\n  %s  ->  %s" % (entrada.name, saida.name))
    print("  %d marca(s) de revisao aceita(s), %d parágrafo(s) fundido(s)."
          % (total, fundidos))
    print("\n  quem tinha marcação, e isto fica registrado porque a decisão foi de quem pediu:")
    for autor, n in de.most_common():
        print("     %-30s %4d" % (autor[:30], n))
    print("\n  O arquivo original não foi tocado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

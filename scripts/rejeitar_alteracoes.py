# -*- coding: utf-8 -*-
"""Devolve o texto do autor de um .docx que traz alteracoes e comentarios de outra pessoa.

POR QUE ISTO EXISTE

O Warat conversacional le o texto do autor. Quando o arquivo chega com
alteracoes controladas e comentarios do orientador, ler a versao aceita e ler um
trabalho ja em parte corrigido, e os comentarios diriam a leitura o que achar. O
`extrair.py` recusa arquivo com alteracao pendente, com razao: o paragrafo
apagado conta na numeracao.

Este programa recusa todas as alteracoes (o inserido sai, o apagado volta, o
movido volta a origem), tira as mudancas de formatacao e as marcas de comentario,
esvazia o texto dos comentarios e repoe as declaracoes de namespace que o Word
exige. Medido em 18/09/2026: 406 alteracoes e 42 comentarios do orientador,
nenhuma revisao restante, e a extracao conferida contra tres trechos inseridos
(ausentes), tres apagados (presentes) e o texto dos comentarios (ausente).

O QUE ELE NAO DECIDE

De quem sao as alteracoes. Ele recusa todas; se forem do proprio autor, o que ele
devolve e a versao anterior do autor, e quem roda precisa saber disso. A lista de
autores e impressa antes de gravar.

Uso:
    python scripts/rejeitar_alteracoes.py <entrada.docx> <saida.docx>
    python scripts/rejeitar_alteracoes.py --autoteste
"""
import io
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_revisoes import (q, carregar, repor_namespaces, gravar, docx_minimo,  # noqa: E402
                           texto_do_paragrafo, ignoraveis_sem_declaracao)

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SAI_INTEIRO = ("ins", "moveTo", "rPrChange", "pPrChange", "sectPrChange", "tblPrChange",
               "trPrChange", "tcPrChange", "tblGridChange", "numberingChange",
               "moveFromRangeStart", "moveFromRangeEnd", "moveToRangeStart", "moveToRangeEnd",
               "commentRangeStart", "commentRangeEnd")
DESEMBRULHA = ("del", "moveFrom")


def recusar(z):
    """Devolve (trocas {parte: bytes}, contagens, autores)."""
    orig = z.read("word/document.xml")
    root = carregar(z, "word/document.xml")
    autores = Counter(e.get(q("author"), "(sem autor)") for e in root.iter()
                      if e.tag in (q("ins"), q("del"), q("moveTo"), q("moveFrom")))

    def pais():
        return {c: p for p in root.iter() for c in p}

    n = {}
    for tag in SAI_INTEIRO:
        pm = pais()
        els = list(root.iter(q(tag)))
        n[tag] = len(els)
        for e in els:
            if e in pm:
                pm[e].remove(e)
    for tag in DESEMBRULHA:
        while True:
            pm = pais()
            els = [e for e in root.iter(q(tag)) if e in pm]
            if not els:
                break
            e = els[0]
            p = pm[e]
            i = list(p).index(e)
            for c in list(e):
                p.insert(i, c)
                i += 1
            p.remove(e)
            n[tag] = n.get(tag, 0) + 1
    for e in root.iter(q("delText")):
        e.tag = q("t")
    for e in root.iter(q("delInstrText")):
        e.tag = q("instrText")
    pm = pais()
    for e in list(root.iter(q("commentReference"))):
        r = pm.get(e)
        if r is not None and r.tag == q("r") and r in pm:
            pm[r].remove(r)
        elif e in pm:
            pm[e].remove(e)
    restam = sum(1 for e in root.iter() if e.tag in (q("ins"), q("del"), q("moveTo"),
                                                    q("moveFrom"), q("commentReference"),
                                                    q("delText")))
    novo = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    trocas = {"word/document.xml": repor_namespaces(novo, orig)}
    if "word/comments.xml" in z.namelist():
        com = carregar(z, "word/comments.xml")
        n["comentarios"] = len(list(com))
        for c in list(com):
            com.remove(c)
        trocas["word/comments.xml"] = ET.tostring(com, encoding="UTF-8", xml_declaration=True)
    return trocas, n, autores, restam


def autoteste():
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    corpo = ('<w:p><w:r><w:t xml:space="preserve">Texto da autora </w:t></w:r>'
             '<w:ins w:id="1" w:author="Orientador" w:date="2026-09-12T00:00:00Z"><w:r><w:t>INSERIDO</w:t></w:r></w:ins>'
             '<w:del w:id="2" w:author="Orientador" w:date="2026-09-12T00:00:00Z"><w:r><w:delText>apagado</w:delText></w:r></w:del>'
             '<w:commentRangeStart w:id="0"/><w:r><w:t xml:space="preserve"> fim.</w:t></w:r><w:commentRangeEnd w:id="0"/>'
             '<w:r><w:commentReference w:id="0"/></w:r></w:p>'
             '<w:p><w:pPr><w:rPr><w:ins w:id="3" w:author="Orientador" w:date="2026-09-12T00:00:00Z"/></w:rPr></w:pPr>'
             '<w:moveFrom w:id="4" w:author="Orientador" w:date="2026-09-12T00:00:00Z"><w:r><w:t>movido</w:t></w:r></w:moveFrom>'
             '<w:moveTo w:id="5" w:author="Orientador" w:date="2026-09-12T00:00:00Z"><w:r><w:t>DESTINO</w:t></w:r></w:moveTo></w:p>')
    com = ('<?xml version="1.0" encoding="UTF-8"?><w:comments xmlns:w="%s"><w:comment w:id="0" '
           'w:author="Orientador"><w:p><w:r><w:t>COMENTARIO SECRETO</w:t></w:r></w:p></w:comment></w:comments>' % W)
    z = zipfile.ZipFile(docx_minimo(corpo, com))
    trocas, n, autores, restam = recusar(z)
    falhas = []
    doc = ET.fromstring(trocas["word/document.xml"])
    textos = [texto_do_paragrafo(p) for p in doc.iter(q("p"))]
    if textos != ["Texto da autora apagado fim.", "movido"]:
        falhas.append("texto devolvido errado: %r" % textos)
    if restam:
        falhas.append("sobraram %d marcas" % restam)
    if b"COMENTARIO SECRETO" in trocas["word/comments.xml"]:
        falhas.append("o texto do comentario ficou")
    if ignoraveis_sem_declaracao(trocas["word/document.xml"]):
        falhas.append("namespace ignoravel sem declaracao")
    # cinco marcas: a insercao, a exclusao, a marca de paragrafo inserido e as duas
    # pontas do texto movido
    if autores != Counter({"Orientador": 5}):
        falhas.append("autores contados errado: %r" % autores)
    return falhas


def main():
    if sys.argv[1:] == ["--autoteste"] or len(sys.argv) != 3:
        f = autoteste()
        print("autoteste: " + ("passou (inserido sai, apagado e movido voltam, comentario some, "
                               "namespace reposto)" if not f else "FALHOU: " + "; ".join(f)))
        if f or sys.argv[1:] == ["--autoteste"]:
            return 1 if f else 0
        print(__doc__.split("Uso:")[1])
        return 2
    f = autoteste()
    if f:
        print("o proprio programa esta quebrado, e nao gravo nada: " + "; ".join(f))
        return 2
    z = zipfile.ZipFile(sys.argv[1])
    trocas, n, autores, restam = recusar(z)
    print("  alteracoes por autor:")
    for a, k in autores.most_common():
        print("     %-32s %4d" % (a[:32], k))
    print("  tratados: %s" % ", ".join("%s %d" % (k, v) for k, v in n.items() if v))
    if restam:
        print("  sobraram %d marcas de revisao ou comentario; arquivo NAO gravado" % restam)
        return 1
    gravar(z, sys.argv[2], trocas)
    print("  gravado %s" % sys.argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())

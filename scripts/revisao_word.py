# -*- coding: utf-8 -*-
"""Gera a copia com controle de alteracoes pela comparacao do Word.

POR QUE ESTE PROGRAMA EXISTE. A Norma sabe escrever a marcacao de revisao no
XML, e ela sai correta: medido em 30/08/2026 na dissertacao do Akeshi, as 27
marcas de paragrafo excluidas estavam todas em paragrafo vazio. Mesmo assim,
quando o Word aceita essas alteracoes, oito pares de paragrafos de texto se
fundem, entre eles tres legendas que grudam na primeira celula da tabela
seguinte. A causa esta no que o Word faz ao aceitar, e nao no que escrevemos.

A saida daqui nao tem esse risco por construcao: quem escreve a marcacao e o
proprio Word, comparando o arquivo original com a copia ja normalizada. Aceitar
o resultado devolve a copia normalizada porque foi dela que a marcacao nasceu.

O QUE ELE NAO E. Nao substitui o normalizador. A copia limpa continua sendo
feita pelo `normalizar_docx.py --silencio`, em Python puro, sem Word, que e o
que permite rodar no Colab. Este aqui e um passo a mais, opcional, e so para a
copia que vai para quem escreveu.

    python scripts/revisao_word.py trabalho.docx trabalho-limpo.docx

Por padrao ele confere a propria saida: aceita as alteracoes numa copia
descartavel e compara com o arquivo normalizado, paragrafo a paragrafo. Sem essa
conferencia o programa nao teria como afirmar o que a sua razao de existir
afirma.
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

# wdCompareDestinationNew, wdGranularityWordLevel, wdFormatXMLDocument
NOVO_DOC, POR_PALAVRA, FORMATO_DOCX = 2, 1, 16
AUTOR = "Norma"


def word():
    try:
        import win32com.client.dynamic
    except ImportError:
        sys.exit("este programa precisa do pywin32 e do Word: pip install pywin32")
    try:
        w = win32com.client.dynamic.Dispatch("Word.Application")
    except Exception as e:
        sys.exit("nao consegui abrir o Word: %s" % e)
    w.Visible = False
    w.DisplayAlerts = False
    return w


def paragrafos(caminho):
    """Texto de cada paragrafo, na ordem, por varredura com profundidade.

    Regex ingenua de `<w:p>` quebra em caixa de texto, onde ha paragrafo dentro
    de paragrafo, e ja produziu acusacao falsa nesta mesma investigacao."""
    with zipfile.ZipFile(caminho) as z:
        doc = z.read("word/document.xml")
    saida, i, n = [], 0, len(doc)
    abre = re.compile(rb"<w:p(?: [^>]*)?>")
    while True:
        m = abre.search(doc, i)
        if not m:
            break
        prof, j = 1, m.end()
        while prof and j < n:
            a = doc.find(b"<w:p ", j), doc.find(b"<w:p>", j), doc.find(b"</w:p>", j)
            fecha = a[2]
            proximo = min(x for x in (a[0], a[1], n) if x != -1)
            if proximo < fecha:
                prof += 1
                j = proximo + 4
            elif fecha == -1:
                break
            else:
                prof -= 1
                j = fecha + 6
        b = doc[m.start():j]
        t = b"".join(re.findall(rb"<w:t[^>]*>(.*?)</w:t>", b, re.S))
        saida.append(" ".join(re.sub(rb"<[^>]+>", b"", t).decode("utf-8", "replace").split()))
        i = m.end()
    return saida


def comparar(w, original, revisado, destino):
    doc = w.CompareDocuments(
        w.Documents.Open(str(original), ReadOnly=True, AddToRecentFiles=False),
        w.Documents.Open(str(revisado), ReadOnly=True, AddToRecentFiles=False),
        NOVO_DOC, POR_PALAVRA,
        True,   # formatacao
        False,  # caixa
        True,   # espaco em branco
        True,   # tabelas
        True,   # cabecalhos
        True,   # notas
        True,   # caixas de texto
        True,   # campos
        True,   # comentarios
        True,   # movimentos
        AUTOR,
        True)   # ignora avisos
    doc.SaveAs2(str(destino), FileFormat=FORMATO_DOCX)
    n = doc.Revisions.Count
    doc.Close(False)
    for d in list(w.Documents):
        try:
            d.Close(False)
        except Exception:
            pass
    return n


def aceitar(w, origem, destino):
    d = w.Documents.Open(str(origem), ReadOnly=False, AddToRecentFiles=False)
    d.Revisions.AcceptAll()
    d.SaveAs2(str(destino), FileFormat=FORMATO_DOCX)
    d.Close(False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("original", help="o .docx como veio de quem escreveu")
    ap.add_argument("normalizado", help="a cópia limpa, do normalizar_docx.py --silencio")
    ap.add_argument("--saida", help="padrão: <original>-revisao.docx")
    ap.add_argument("--sem-conferir", action="store_true",
                    help="não confere a própria saída (não recomendado)")
    a = ap.parse_args()

    orig = Path(a.original).resolve()
    lim = Path(a.normalizado).resolve()
    for p in (orig, lim):
        if not p.exists():
            sys.exit("nao encontrei %s" % p)
    saida = Path(a.saida).resolve() if a.saida else orig.with_name(orig.stem + "-revisao.docx")

    w = word()
    try:
        n = comparar(w, orig, lim, saida)
        print("%s: %d alterações, escritas pelo Word e assinadas por %s"
              % (saida.name, n, AUTOR))
        if a.sem_conferir:
            return 0

        prova = saida.with_name(saida.stem + "-prova.docx")
        aceitar(w, saida, prova)
    finally:
        w.Quit()

    esperado = [t for t in paragrafos(lim) if t]
    obtido = [t for t in paragrafos(prova) if t]
    print("   conferência: aceitar a revisão devolve %d parágrafos com texto, "
          "contra %d da cópia normalizada" % (len(obtido), len(esperado)))
    if obtido == esperado:
        print("   confere: aceitar esta revisão dá exatamente a cópia normalizada.")
        prova.unlink(missing_ok=True)
        return 0

    import difflib
    d = [l for l in difflib.unified_diff(obtido, esperado, "aceita", "normalizada",
                                         lineterm="", n=0)]
    print("   NAO CONFERE: %d divergências. A prova ficou em %s"
          % (sum(1 for l in d if l.startswith("@@")), prova.name))
    for l in d[:12]:
        print("      %s" % l[:150])
    return 1


if __name__ == "__main__":
    sys.exit(main())

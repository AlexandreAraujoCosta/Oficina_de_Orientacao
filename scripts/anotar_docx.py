# -*- coding: utf-8 -*-
"""Grava uma copia do .docx com os apontamentos como comentarios do Word.

POR QUE ISTO EXISTE

O relatorio e um PDF de cem paginas ao lado do documento, e conferir um item
exige achar o paragrafo. Aqui o apontamento fica no lugar: o autor abre o
trabalho no Word e ve a anotacao na margem, na altura do paragrafo citado.

E o formato tem uma virtude que o PDF nao tem: comentario do Word e conversa.
O orientador le, responde na mesma linha, e a resposta fica no arquivo.

COMO ANCORA

Cada item vira um comentario, ancorado no PRIMEIRO paragrafo que ele cita; os
demais localizadores entram no texto do comentario. Um item que cita nove
paragrafos com nove ancoras seria o mesmo aviso repetido nove vezes na margem.

A TRAVA QUE IMPEDE O PIOR ERRO

Comentario ancorado no paragrafo errado e pior que comentario nenhum, porque
manda o autor olhar onde nao ha nada. A numeracao [P123] vem de
collect_paragraphs, e aqui os paragrafos sao localizados por expressao regular
sobre o XML cru. As duas contagens precisam bater, e o programa se recusa a
gravar quando nao batem.

    python anotar_docx.py <trabalho.docx> <ENTREGA-CORRETOR-*.md> [--saida X.docx]
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar_docx import load, Styles, collect_paragraphs, W  # noqa: E402

AUTOR = "Luis"
INICIAIS = "AL"
DATA = "2026-01-01T12:00:00Z"

RE_PAR_XML = re.compile(rb"<w:p(?:\s[^>]*)?/>|<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
RE_ITEM = re.compile(
    r"^## ([A-Z]{1,2}\d+)\s*$\n+\*\*Aponta:\*\* (.+?)\s*$\n+\*\*Abrir:\*\* (.*?)\s*$",
    re.M | re.S)
RE_LOC = re.compile(r"\[P(\d+)\]")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def spans(doc_bytes):
    """Os paragrafos na ordem em que o documento os traz."""
    return [(m.start(), m.end(), m.group(0).endswith(b"/>"))
            for m in RE_PAR_XML.finditer(doc_bytes)]


def itens(caminho):
    txt = Path(caminho).read_text(encoding="utf-8")
    out = []
    for m in RE_ITEM.finditer(txt):
        cod, aponta, abrir = m.group(1), m.group(2).strip(), m.group(3)
        locs = [int(x) for x in RE_LOC.findall(abrir)]
        if locs:
            out.append((cod, aponta, locs))
    return out


def abertura(pars, n, limite=46):
    """As primeiras palavras do paragrafo, para quem procura no Word com Ctrl+F."""
    if not (1 <= n <= len(pars)):
        return None
    s = " ".join(pars[n - 1].text.split())
    if len(s) < 12:
        return None
    if len(s) <= limite:
        return s
    corte = s.rfind(" ", 0, limite)
    return s[:corte if corte > 20 else limite] + "…"


def mapa_secoes(pars):
    """Para cada paragrafo, a secao em que ele esta.

    Dentro do Word o [P252] nao serve, e a abertura do paragrafo e longa demais
    para caber no meio de uma frase. A secao cabe, e o painel de navegacao a
    encontra."""
    mapa, atual = {}, None
    for p in pars:
        if p.level is not None and p.text.strip():
            s = " ".join(p.text.split())
            m = re.match(r"^(\d+(?:\.\d+)*)", s)
            atual = m.group(1) if m else (s[:24].rsplit(" ", 1)[0] if len(s) > 24 else s)
        mapa[p.idx] = atual
    return mapa


def sem_localizador(texto, mapa):
    """Troca [P123] pela secao, mantendo os colchetes.

    O localizador ocupa lugar de substantivo na frase ("a promessa de [P7]"), e
    por isso a troca precisa ocupar o mesmo lugar. Trocar por "na secao 2.1"
    produz "a promessa de na secao 2.1". Trocar por "[2.1]" preserva a sintaxe,
    porque um colchete substitui outro."""
    def troca(m):
        s = mapa.get(int(m.group(1)))
        return ("[%s]" % s) if s else ""
    t = re.sub(r"\[P(\d+)\]", troca, texto)
    t = re.sub(r"\[P\d+(?:[-–]P?\d+)?\]", "", t)
    # sobra de pontuacao quando um localizador some sem secao conhecida
    t = re.sub(r"\s+([,.;:])", r"", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def comentarios_existentes(z):
    """Os comentarios que o autor ja tem, e o primeiro id livre.

    Os ids precisam ser unicos no arquivo: comecar do zero apagaria a conversa
    que ja esta la."""
    tem = "word/comments.xml" in z.namelist()
    com_xml = z.read("word/comments.xml").decode("utf-8") if tem else None
    usados = [int(x) for x in re.findall(r'w:id="(\d+)"', com_xml or "")]
    return tem, com_xml, usados, (max(usados) + 1 if usados else 0)


def ancorar(doc, sp, por_par, prox):
    """Poe as marcas de comentario nos paragrafos, e devolve (doc novo, novos).

    `por_par` e {numero do paragrafo: [textos]}; `novos` sai como [(id, texto)]
    para quem for escrever o comments.xml."""
    novos, saida, pos = [], [], 0
    for n in sorted(por_par):
        ini, fim, vazio = sp[n - 1]
        if vazio:
            continue
        saida.append(doc[pos:ini])
        bloco = doc[ini:fim]
        # A marca entra depois do <w:pPr>, e nao logo apos a abertura do
        # paragrafo. Ate 27/08/2026 entrava antes, e o Word abria assim mesmo,
        # mas o esquema manda o <w:pPr> ser o primeiro filho de <w:p> e um
        # leitor menos tolerante recusa o arquivo.
        ppr = bloco.find(b"</w:pPr>")
        abre = (ppr + len(b"</w:pPr>")) if ppr >= 0 else bloco.index(b">") + 1
        marca_ini, marca_fim = b"", b""
        for texto in por_par[n]:
            marca_ini += ('<w:commentRangeStart w:id="%d"/>' % prox).encode()
            marca_fim += ('<w:commentRangeEnd w:id="%d"/><w:r><w:commentReference w:id="%d"/></w:r>'
                          % (prox, prox)).encode()
            novos.append((prox, texto))
            prox += 1
        bloco = bloco[:abre] + marca_ini + bloco[abre:-len(b"</w:p>")] + marca_fim + b"</w:p>"
        saida.append(bloco)
        pos = fim
    saida.append(doc[pos:])
    return b"".join(saida), novos


def escrever(z, doc, novos, dest, autor=AUTOR, tem_comentarios=None, com_xml=None):
    """Grava o .docx com o document.xml novo e os comentarios acrescentados.

    Escrever comentario no .docx pede quatro pecas, e faltar uma delas produz
    arquivo que o Word recusa a abrir: o corpo em comments.xml, o tipo em
    [Content_Types].xml, a relacao em document.xml.rels, e a marca no corpo."""
    if tem_comentarios is None:
        tem_comentarios, com_xml, _, _ = comentarios_existentes(z)
    corpo = "".join(
        '<w:comment w:id="%d" w:author="%s" w:initials="%s" w:date="%s">'
        '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:comment>'
        % (cid, esc(autor), INICIAIS, DATA, esc(t)) for cid, t in novos)
    if tem_comentarios:
        com_xml = com_xml.replace("</w:comments>", corpo + "</w:comments>")
    else:
        com_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<w:comments xmlns:w="http://schemas.openxmlformats.org/'
                   'wordprocessingml/2006/main">' + corpo + "</w:comments>")

    ct = z.read("[Content_Types].xml").decode("utf-8")
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    if "comments+xml" not in ct:
        ct = ct.replace("</Types>",
            '<Override PartName="/word/comments.xml" ContentType="application/vnd.'
            'openxmlformats-officedocument.wordprocessingml.comments+xml"/></Types>')
    if "comments.xml" not in rels:
        rels = rels.replace("</Relationships>",
            '<Relationship Id="rIdComentariosLuis" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/comments" Target="comments.xml"/></Relationships>')

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            if it.filename == "word/document.xml":
                zo.writestr(it, doc)
            elif it.filename == "word/comments.xml":
                zo.writestr(it, com_xml)
            elif it.filename == "[Content_Types].xml":
                zo.writestr(it, ct)
            elif it.filename == "word/_rels/document.xml.rels":
                zo.writestr(it, rels)
            else:
                zo.writestr(it, z.read(it.filename))
        if not tem_comentarios:
            zo.writestr("word/comments.xml", com_xml)


def main():
    ap = argparse.ArgumentParser(description="Apontamentos como comentários do Word.")
    ap.add_argument("trabalho")
    ap.add_argument("lista", help="ENTREGA-CORRETOR-*.md")
    ap.add_argument("--saida")
    ap.add_argument("--autor", default=AUTOR)
    a = ap.parse_args()

    if not a.trabalho.lower().endswith(".docx"):
        sys.exit("só funciona com .docx: um PDF não tem onde guardar comentário.")

    # ---- confere a numeracao antes de qualquer coisa
    parts = load(a.trabalho)
    pars = collect_paragraphs(parts["word/document.xml"].find(W + "body"),
                              Styles(parts["word/styles.xml"]))
    z = zipfile.ZipFile(a.trabalho)
    doc = z.read("word/document.xml")
    sp = spans(doc)
    if len(sp) != len(pars):
        sys.exit("as duas contagens de parágrafo não batem (%d por XML, %d pelo extrator).\n"
                 "Ancorar assim poria o comentário no parágrafo errado. Nada foi gravado."
                 % (len(sp), len(pars)))

    secoes = mapa_secoes(pars)
    lista = itens(a.lista)
    if not lista:
        sys.exit("nenhum item com localizador na lista: nada a ancorar.")

    # ---- um comentario por item, no primeiro paragrafo citado
    por_par = {}
    fora = []
    for cod, aponta, locs in lista:
        alvo = next((n for n in locs if 1 <= n <= len(sp)), None)
        if alvo is None:
            fora.append(cod)
            continue
        extra = [x for x in locs if x != alvo]
        texto = "[%s] %s" % (cod, sem_localizador(aponta, secoes))
        # Dentro do Word o [P558] nao aponta para nada: a numeracao e da
        # extracao, e nao do documento. O localizador que funciona ali e o
        # proprio texto, porque o Word tem Ctrl+F. As aberturas abaixo sao
        # copiadas do arquivo por este programa, e nao redigitadas.
        aberturas = [abertura(pars, x) for x in extra]
        aberturas = [x for x in aberturas if x]
        if aberturas:
            texto += "  Também em: " + "; ".join('"%s"' % x for x in aberturas[:4])
            if len(aberturas) > 4:
                texto += "; e em mais %d passagens, listadas no relatório" % (len(aberturas) - 4)
        por_par.setdefault(alvo, []).append(texto)

    # ---- ids livres, para nao colidir com os comentarios do autor
    tem_comentarios, com_xml, usados, prox = comentarios_existentes(z)
    doc, novos = ancorar(doc, sp, por_par, prox)

    dest = Path(a.saida) if a.saida else \
        Path(a.trabalho).with_name(Path(a.trabalho).stem + "-ANOTADO.docx")
    escrever(z, doc, novos, dest, a.autor, tem_comentarios, com_xml)

    print("  %s: %d comentários em %d parágrafos%s"
          % (dest.name, len(novos), len(por_par),
             ", %d do autor preservados" % len(usados) if usados else ""))
    if fora:
        print("  sem âncora (localizador fora do documento): %s" % ", ".join(fora))
    return 0


if __name__ == "__main__":
    sys.exit(main())

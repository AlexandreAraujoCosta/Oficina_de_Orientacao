# -*- coding: utf-8 -*-
"""Grava o .docx de entrega do Warat conversacional: o que o autor aceitou, e o resto na margem.

POR QUE ISTO EXISTE

A conversa termina em duas listas. As propostas de redacao que o autor aceitou
entram como alteracao controlada, para que ele veja o que era e o que passou a
ser, e possa recusar no Word. Os achados verificados que a conversa nao chegou a
discutir entram como comentario na margem do paragrafo: medido em 18/09/2026, a
conversa trouxe tres em cinquenta, e sem esta segunda lista ela entregaria menos
que o relatorio do Luis.

ENTRADA

    <propostas>/P61.substitui.txt     o paragrafo inteiro, como fica
    <propostas>/P132.acrescenta.txt   o texto que entra antes do ponto final
    <comentarios.txt>                 uma linha por comentario: [P530] texto

O texto das propostas e o do modelo, aceito pelo autor; o "Esta" de cada
paragrafo vem da extracao, por copia.

OS CONTROLES, E O ARQUIVO SO E GRAVADO SE TODOS PASSAREM

Aceitando tudo, cada paragrafo fica igual a proposta; recusando tudo, fica igual
ao do autor; nenhum outro paragrafo muda; nenhum prefixo de mc:Ignorable fica sem
declaracao; cada comentario pedido foi ancorado. Paragrafo que nao se acha de modo
unico pelo texto e acusado, e nao adivinhado.

Uso:
    python scripts/aplicar_propostas.py <autor.docx> <extracao.txt> <pasta-propostas> <saida.docx>
                                        [--comentarios comentarios.txt] [--autor Warat]
    python scripts/aplicar_propostas.py --autoteste
"""
import argparse
import copy
import io
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_revisoes import (W, XML_NS, REL, CT, q, carregar, registrar_namespaces,  # noqa: E402
                           repor_namespaces, ignoraveis_sem_declaracao, normal,
                           texto_do_paragrafo, ler_extracao, gravar, docx_minimo)

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DATA = "2026-01-01T00:00:00Z"
TIPO_COM = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
CT_COM = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"


def sem_notas(s):
    """A extracao marca a nota de rodape no texto ([nota 37]); o paragrafo do docx nao.
    Medido em 18/09/2026: sem isto, todo paragrafo com nota ficava sem ancora."""
    return normal(re.sub(r"\s*\[nota \d+\]", "", s or ""))


def ler_propostas(pasta):
    props = {}
    for f in sorted(Path(pasta).glob("P*.txt")):
        m = re.match(r"P(\d+)\.(substitui|acrescenta)\.txt$", f.name)
        if not m:
            raise SystemExit("nome fora do formato: %s (use P61.substitui.txt ou P132.acrescenta.txt)" % f.name)
        props[int(m.group(1))] = (m.group(2), normal(io.open(f, encoding="utf-8").read()))
    return props


def ler_comentarios(caminho):
    """(comentarios, avisos). Linha fora do formato e acusada, e nao engolida: a
    critica fria de 18/09 mandou quatro linhas e viu entrar uma."""
    out, avisos = [], []
    if not caminho:
        return out, avisos
    for k, linha in enumerate(io.open(caminho, encoding="utf-8"), 1):
        if not linha.strip():
            continue
        m = re.match(r"\s*\[P(\d+)([^\]]*)\]\s*(.+)", linha)
        if not m:
            avisos.append("comentarios.txt, linha %d: fora do formato [Pn] texto, não entrou: %s"
                          % (k, linha.strip()[:70]))
            continue
        if re.search(r"\d", m.group(2)) or re.match(r"\s*\[P\d+\]", m.group(3)):
            avisos.append("comentarios.txt, linha %d: mais de um parágrafo; ancorado só no [P%s]"
                          % (k, m.group(1)))
        out.append((int(m.group(1)), m.group(3).strip()))
    return out, avisos


def aplicar(z, par, props, comentarios, autor):
    orig = z.read("word/document.xml")
    root = carregar(z, "word/document.xml")
    paragrafos = list(root.iter(q("p")))
    antes = [texto_do_paragrafo(p) for p in paragrafos]
    falhas, avisos = [], []

    def achar(n):
        if n not in par:
            falhas.append("[P%d] não está na extração" % n)
            return None
        idx = [i for i, t in enumerate(antes) if t and t == sem_notas(par[n])]
        if len(idx) != 1:
            falhas.append("[P%d]: %d parágrafos do docx têm o texto da extração; esperava 1" % (n, len(idx)))
            return None
        return idx[0]

    ident = [900000]

    def novo_id():
        ident[0] += 1
        return str(ident[0])

    def marca(tag):
        e = ET.Element(q(tag))
        e.set(q("id"), novo_id())
        e.set(q("author"), autor)
        e.set(q("date"), DATA)
        return e

    def run_com(rpr, s):
        r = ET.Element(q("r"))
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        t = ET.SubElement(r, q("t"))
        t.text = s
        t.set("{%s}space" % XML_NS, "preserve")
        return r

    alvo, esperado = {}, {}
    for n, (modo, texto) in props.items():
        i = achar(n)
        if i is None:
            continue
        p = paragrafos[i]
        if any(c.tag in (q("hyperlink"), q("ins"), q("del"), q("fldSimple")) for c in p):
            falhas.append("[P%d]: parágrafo com hiperlink, campo ou revisão; este programa não o trata" % n)
            continue
        runs = [c for c in p if c.tag == q("r")]
        if not runs:
            falhas.append("[P%d]: parágrafo sem texto em runs diretos" % n)
            continue
        if modo == "substitui" and any(e.tag in (q("footnoteReference"), q("endnoteReference"))
                                       for e in p.iter()):
            # a referencia da nota esta num run: substituir o paragrafo inteiro a
            # apagaria junto, e a nota sumiria do documento
            falhas.append("[P%d]: o parágrafo tem nota de rodapé, e a substituição integral a "
                          "apagaria; proponha acréscimo, ou deixe a mudança para o autor" % n)
            continue
        alvo[n] = i
        if modo == "substitui":
            formas = {ET.tostring(r.find(q("rPr"))) if r.find(q("rPr")) is not None else b""
                      for r in runs if "".join(t.text or "" for t in r.iter(q("t"))).strip()}
            # o texto novo leva a formatacao do trecho mais longo, e nao a do primeiro:
            # medido em 18/09, "c)" em negrito no inicio deixava o objetivo inteiro em negrito
            maior = max(runs, key=lambda r: len("".join(t.text or "" for t in r.iter(q("t")))))
            if len(formas) > 1:
                avisos.append("[P%d]: o parágrafo tinha formatação variada (itálico, negrito ou "
                              "outra em parte do texto); o texto novo leva a predominante, e o "
                              "que era destacado perde o destaque; confira no Word" % n)
            rpr = maior.find(q("rPr"))
            d = marca("del")
            i0 = list(p).index(runs[0])
            for r in runs:
                p.remove(r)
                for t in r.iter(q("t")):
                    t.tag = q("delText")
                d.append(r)
            p.insert(i0, d)
            ins = marca("ins")
            ins.append(run_com(rpr, texto))
            p.insert(i0 + 1, ins)
            esperado[n] = texto
        else:
            com_texto = [r for r in runs if "".join(t.text or "" for t in r.iter(q("t"))).strip()]
            ult = com_texto[-1]
            ts = [t for t in ult.iter(q("t")) if t.text]
            fim = ts[-1].text.rstrip()
            if not fim or fim[-1] not in ".;":
                falhas.append("[P%d]: o parágrafo não termina em ponto ou ponto e vírgula" % n)
                continue
            pont = fim[-1]
            ts[-1].text = fim[:-1]
            k = list(p).index(ult)
            rpr = ult.find(q("rPr"))
            ins = marca("ins")
            ins.append(run_com(rpr, texto))
            p.insert(k + 1, ins)
            p.insert(k + 2, run_com(rpr, pont))
            esperado[n] = normal(sem_notas(par[n])[:-1] + texto + pont)

    # comentarios: uma ancora por paragrafo pedido
    com_root, novos_com = None, []
    if comentarios:
        if "word/comments.xml" in z.namelist():
            com_root = carregar(z, "word/comments.xml")
        else:
            com_root = ET.Element(q("comments"))
        for n, texto in comentarios:
            i = achar(n)
            if i is None:
                continue
            p = paragrafos[i]
            cid = novo_id()
            filhos = list(p)
            ini = 1 if filhos and filhos[0].tag == q("pPr") else 0
            s = ET.Element(q("commentRangeStart"))
            s.set(q("id"), cid)
            p.insert(ini, s)
            e = ET.Element(q("commentRangeEnd"))
            e.set(q("id"), cid)
            p.append(e)
            r = ET.SubElement(p, q("r"))
            ref = ET.SubElement(r, q("commentReference"))
            ref.set(q("id"), cid)
            c = ET.SubElement(com_root, q("comment"))
            c.set(q("id"), cid)
            c.set(q("author"), autor)
            c.set(q("date"), DATA)
            cp = ET.SubElement(c, q("p"))
            cr = ET.SubElement(cp, q("r"))
            ct = ET.SubElement(cr, q("t"))
            ct.text = texto
            ct.set("{%s}space" % XML_NS, "preserve")
            novos_com.append(n)

    # controles
    for n in alvo:
        p = paragrafos[alvo[n]]
        if texto_do_paragrafo(p, "aceito") != esperado[n]:
            falhas.append("[P%d]: aceito difere da proposta" % n)
        if texto_do_paragrafo(p, "recusado") != sem_notas(par[n]):
            falhas.append("[P%d]: recusado difere do texto do autor" % n)
    mudaram = [i for i in range(len(paragrafos)) if i not in alvo.values()
               and texto_do_paragrafo(paragrafos[i], "aceito") != antes[i]]
    if mudaram:
        falhas.append("%d outros parágrafos mudaram" % len(mudaram))

    doc = repor_namespaces(ET.tostring(root, encoding="UTF-8", xml_declaration=True), orig)
    if ignoraveis_sem_declaracao(doc):
        falhas.append("prefixos de mc:Ignorable sem declaração: %s" % ignoraveis_sem_declaracao(doc))
    trocas = {"word/document.xml": doc}
    if com_root is not None and novos_com:
        trocas["word/comments.xml"] = ET.tostring(com_root, encoding="UTF-8", xml_declaration=True)
        if "word/comments.xml" not in z.namelist():
            ct = z.read("[Content_Types].xml").decode("utf-8")
            ct = ct.replace("</Types>", '<Override PartName="/word/comments.xml" ContentType="%s"/></Types>' % CT_COM)
            trocas["[Content_Types].xml"] = ct.encode("utf-8")
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
            rels = rels.replace("</Relationships>",
                                '<Relationship Id="rIdWaratCom" Type="%s" Target="comments.xml"/></Relationships>' % TIPO_COM)
            trocas["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    return trocas, falhas, sorted(alvo), novos_com, avisos


def autoteste():
    corpo = ('<w:p><w:r><w:t>Old sentence about the hypothesis.</w:t></w:r></w:p>'
             '<w:p><w:r><w:t xml:space="preserve">e) To construct a framework </w:t></w:r>'
             '<w:r><w:rPr><w:i/></w:rPr><w:t>(how).</w:t></w:r></w:p>'
             '<w:p><w:r><w:t>Untouched paragraph.</w:t></w:r></w:p>'
             '<w:p><w:r><w:t>Paragraph for a margin note.</w:t></w:r></w:p>')
    par = {1: "Old sentence about the hypothesis.", 2: "e) To construct a framework (how).",
           3: "Untouched paragraph.", 4: "Paragraph for a margin note."}
    props = {1: ("substitui", "New sentence."), 2: ("acrescenta", "; and to propose standards")}
    z = zipfile.ZipFile(docx_minimo(corpo))
    trocas, falhas, alvo, com, _ = aplicar(z, par, props, [(4, "Achado verificado.")], "Warat")
    f = list(falhas)
    doc = ET.fromstring(trocas["word/document.xml"])
    ps = list(doc.iter(q("p")))
    if texto_do_paragrafo(ps[0], "aceito") != "New sentence.":
        f.append("substituição aceita errada")
    if texto_do_paragrafo(ps[1], "aceito") != "e) To construct a framework (how); and to propose standards.":
        f.append("acréscimo aceito errado: %r" % texto_do_paragrafo(ps[1], "aceito"))
    if texto_do_paragrafo(ps[1], "recusado") != "e) To construct a framework (how).":
        f.append("acréscimo recusado errado")
    if com != [4] or b"Achado verificado." not in trocas.get("word/comments.xml", b""):
        f.append("comentário não gravado")
    if b"comments.xml" not in trocas.get("word/_rels/document.xml.rels", b""):
        f.append("relação da parte de comentários não criada")
    # controle negativo: paragrafo que nao existe tem de ser acusado, e nao adivinhado
    z = zipfile.ZipFile(docx_minimo(corpo))
    _, falhas2, _, _, _ = aplicar(z, {**par, 5: "Nowhere."}, {5: ("substitui", "X.")}, [], "Warat")
    if not any("[P5]" in x for x in falhas2):
        f.append("parágrafo inexistente não foi acusado")
    # nota de rodape: a extracao traz [nota 1], o docx traz a referencia num run
    corpo_nota = ('<w:p><w:r><w:t>Claim with a note.</w:t></w:r>'
                  '<w:r><w:footnoteReference w:id="1"/></w:r></w:p>')
    par_nota = {1: "Claim with a note.[nota 1]"}
    z = zipfile.ZipFile(docx_minimo(corpo_nota))
    _, fal, _, cm, _ = aplicar(z, par_nota, {1: ("substitui", "X.")}, [(1, "nota")], "Warat")
    if not any("nota de rodapé" in x for x in fal):
        f.append("substituição sobre parágrafo com nota não foi recusada")
    if cm != [1]:
        f.append("parágrafo com [nota N] na extração não foi achado para o comentário")
    # substituicao sobre paragrafo com italico em parte: grava, e avisa
    z = zipfile.ZipFile(docx_minimo(corpo))
    _, fal, _, _, av = aplicar(z, par, {2: ("substitui", "Plain text.")}, [], "Warat")
    if fal or not any("formatação variada" in x for x in av):
        f.append("formatação variada não foi avisada: %r %r" % (fal, av))
    # linha de comentario fora do formato e acusada, e nao engolida
    t = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    t.write("[P4] certo\nlinha sem localizador\n[P1, P4] dois lugares\n")
    t.close()
    coms, av = ler_comentarios(t.name)
    Path(t.name).unlink()
    if [n for n, _ in coms] != [4, 1] or len(av) != 2:
        f.append("linhas de comentário: %r %r" % (coms, av))
    return f


def main():
    if sys.argv[1:] == ["--autoteste"]:
        f = autoteste()
        print("autoteste: " + ("passou (substitui, acrescenta, comentário com parte nova, "
                               "parágrafo inexistente acusado)" if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("extracao")
    ap.add_argument("propostas")
    ap.add_argument("saida")
    ap.add_argument("--comentarios")
    ap.add_argument("--autor", default="Warat")
    a = ap.parse_args()
    f = autoteste()
    if f:
        print("o próprio programa está quebrado, e não gravo nada: " + "; ".join(f))
        return 2
    z = zipfile.ZipFile(a.docx)
    coms, avisos_com = ler_comentarios(a.comentarios)
    trocas, falhas, alvo, com, avisos = aplicar(z, ler_extracao(a.extracao), ler_propostas(a.propostas),
                                                coms, a.autor)
    for x in avisos_com + avisos:
        print("AVISO: " + x)
    if falhas:
        print("NÃO GRAVADO:")
        for x in falhas:
            print("  " + x)
        return 1
    gravar(z, a.saida, trocas)
    print("gravado %s: %d alterações (%s), %d comentários; aceito = propostas, recusado = autor, "
          "demais parágrafos intactos" % (a.saida, len(alvo), ", ".join("P%d" % n for n in alvo), len(com)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

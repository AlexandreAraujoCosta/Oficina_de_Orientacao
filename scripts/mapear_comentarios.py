# -*- coding: utf-8 -*-
"""Poe cada comentario de margem no localizador [P###] da extracao.

POR QUE ISTO EXISTE

Para comparar o que quem orienta viu com o que uma ferramenta viu, os dois
precisam falar do mesmo lugar. Os comentarios saem do `.docx` presos a um
trecho; a leitura sai da extracao presa a um numero de paragrafo. Sem a ponte,
o pareamento e feito a olho por um modelo, que e exatamente o passo que esta
oficina tira dos modelos sempre que pode.

A PONTE E O PARAGRAFO, E NAO O TRECHO. O texto ancorado vem partido em pedacos
de execucao do Word, com espacos no meio das palavras ("P lenario V irtual"), e
casa-lo por igualdade falha. O que casa e o paragrafo em que a ancora esta.

DUAS VERSOES DO MESMO TRABALHO. O arquivo comentado costuma ser posterior ao que
foi analisado, com edicoes pelo meio. Este programa mede a deriva entre os dois
e recusa o mapeamento se ela for grande, em vez de devolver localizador errado.

Uso:
    python scripts/mapear_comentarios.py <comentado.docx> <analisado.docx> \
        --extracao extracao/<nome>.txt --saida COMENTARIOS-ORIENTADOR.md
"""
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from anotar_docx import W, Styles, collect_paragraphs, load  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

NS_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def normal(t):
    """Junta o que o Word partiu: espacos a mais e quebras somem."""
    return re.sub(r"\s+", "", t or "").lower()


def comentarios(caminho):
    """[(id, autor, texto)] do word/comments.xml."""
    import xml.etree.ElementTree as ET
    z = zipfile.ZipFile(caminho)
    if "word/comments.xml" not in z.namelist():
        return []
    raiz = ET.fromstring(z.read("word/comments.xml"))
    fora = []
    for c in raiz.iter(NS_W + "comment"):
        txt = " ".join(t.text or "" for t in c.iter(NS_W + "t"))
        fora.append((c.get(NS_W + "id"), c.get(NS_W + "author") or "",
                     " ".join(txt.split())))
    return fora


def ancoras(caminho):
    """{id do comentario: indice do paragrafo em que a marca esta}."""
    z = zipfile.ZipFile(caminho)
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    # os paragrafos, na ordem, e onde cada um comeca e acaba
    vaos = [(m.start(), m.end()) for m in
            re.finditer(r"<w:p(?:\s[^>]*)?/>|<w:p(?:\s[^>]*)?>.*?</w:p>", doc, re.S)]
    fora = {}
    for m in re.finditer(r'<w:comment(?:RangeStart|Reference)[^>]*w:id="(\d+)"', doc):
        pos = m.start()
        for i, (a, b) in enumerate(vaos):
            if a <= pos < b:
                fora.setdefault(m.group(1), i)
                break
    return fora


def texto_dos_paragrafos(caminho):
    partes = load(caminho)
    ps = collect_paragraphs(partes["word/document.xml"].find(W + "body"),
                            Styles(partes["word/styles.xml"]))
    return [" ".join(p.text.split()) for p in ps]


def numeros_da_extracao(caminho):
    """{indice do paragrafo: numero [P###]}, pela ordem em que a extracao os traz."""
    bruto = io.open(caminho, encoding="utf-8", errors="replace").read()
    velho = re.findall(r"^\[[^\]]+\]\s+P(\d+)(?:\s+\[[A-Z_]+\])?\s+\(p\.\d+\)\s*(.*)$",
                       bruto, re.M)
    if velho:
        return [(int(n), " ".join(t.split())) for n, t in velho]
    novo = re.findall(r"^[>#*\t ]*\[P(\d+)\]\s*(.*?)(?=\n[ \t]*\n|\Z)",
                      bruto, re.S | re.M)
    return [(int(n), " ".join(re.sub(r"^[>#*\s]+|[*\s]+$", "", t).split()))
            for n, t in novo]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("comentado")
    ap.add_argument("analisado", nargs="?",
                    help="a versao sobre a qual as leituras rodaram; "
                         "sem ela, o mapeamento e contra o proprio comentado")
    ap.add_argument("--extracao", required=True)
    ap.add_argument("--saida", default="COMENTARIOS-ORIENTADOR.md")
    ap.add_argument("--autor", help="so os comentarios deste autor")
    a = ap.parse_args()

    coment = comentarios(a.comentado)
    if not coment:
        sys.exit("nao ha comentarios em %s" % a.comentado)
    onde = ancoras(a.comentado)
    texto_c = texto_dos_paragrafos(a.comentado)

    # ---- a deriva entre as duas versoes, medida antes de mapear
    if a.analisado:
        texto_a = texto_dos_paragrafos(a.analisado)
        if len(texto_a) != len(texto_c):
            sys.exit("!! as duas versoes tem %d e %d paragrafos: a numeracao "
                     "deslocou e o mapeamento por indice mentiria"
                     % (len(texto_a), len(texto_c)))
        iguais = sum(1 for x, y in zip(texto_a, texto_c) if normal(x) == normal(y))
        pct = 100.0 * iguais / max(1, len(texto_a))
        print("  deriva entre as versoes: %d de %d paragrafos identicos (%.1f%%)"
              % (iguais, len(texto_a), pct))
        if pct < 95:
            sys.exit("!! deriva grande demais; mapeie por conteudo, nao por indice")

    pares = numeros_da_extracao(a.extracao)
    # a extracao so traz paragrafo com texto; casa-se pelo texto normalizado
    por_texto = {}
    for n, t in pares:
        por_texto.setdefault(normal(t), n)

    linhas = ["# Comentários de margem, com o localizador da extração", "",
              "Gerado por `mapear_comentarios.py` de `%s`. O localizador vem do "
              "parágrafo em que a marca do comentário está, casado pelo texto do "
              "parágrafo contra a extração. **Não editar.**"
              % Path(a.comentado).name, ""]
    achados = perdidos = 0
    for cid, autor, txt in coment:
        if a.autor and a.autor.lower() not in autor.lower():
            continue
        i = onde.get(cid)
        alvo = normal(texto_c[i]) if i is not None and i < len(texto_c) else ""
        n = por_texto.get(alvo)
        if n:
            achados += 1
            linhas.append("## C%s — [P%d]" % (cid, n))
        else:
            perdidos += 1
            linhas.append("## C%s — sem localizador" % cid)
        linhas += ["", "**Autor:** %s" % (autor or "(sem nome)"), "",
                   "**Comentário:** %s" % txt, ""]
    Path(a.saida).write_text("\n".join(linhas), encoding="utf-8")
    print("  %s: %d comentários, %d com localizador, %d sem"
          % (a.saida, achados + perdidos, achados, perdidos))

    # ---- CONTROLE POSITIVO: um comentario que sabemos ancorado tem de mapear,
    # e um texto adulterado nao pode achar paragrafo nenhum.
    if achados == 0:
        sys.exit("!! nenhum comentario mapeou: o casamento por texto nao funciona aqui")
    inventado = normal("este paragrafo nao existe em trabalho nenhum " * 3)
    if inventado in por_texto:
        sys.exit("!! o casamento acha paragrafo que nao existe; nao confie nele")
    print("  controle: %d de %d comentários acharam o parágrafo, e um texto "
          "inventado não acha nenhum" % (achados, achados + perdidos))


if __name__ == "__main__":
    main()

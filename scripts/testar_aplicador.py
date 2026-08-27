# -*- coding: utf-8 -*-
"""Testa o aplicador, e antes disso testa o conferidor dele.

POR QUE ISTO EXISTE

Um programa que se declara conferido vale o que valer a conferencia, e
conferencia que nunca reprovou nao foi conferida. Aqui o aplicador e sabotado de
proposito, tres vezes, e o teste so passa se ele se recusar a gravar nas tres.

Depois vem a carga: todas as frases aplicaveis dos dois trabalhos viram reparo de
uma vez, e o `Fica` sai do proprio texto, porque o que se testa e o splice e nao
a prosa. Sao cerca de 670 trocas.

    python testar_aplicador.py [--dir <onde gravar os temporarios>]
"""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reparos as R                                  # noqa: E402
import aplicar_docx as A                             # noqa: E402
from anotar_docx import spans, itens                 # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
# Os casos vem da linha de comando, em pares: o .docx e a lista de itens que o
# `lista_corretor.py` gerou para ele. Assim o teste roda sobre o material de quem
# o executa, e o repositorio nao carrega trabalho de terceiros.
#
#     python testar_aplicador.py trabalho.docx ENTREGA-CORRETOR-trabalho.md
CASOS = list(zip(sys.argv[1::2], sys.argv[2::2]))
if not CASOS:
    sys.exit("uso: testar_aplicador.py <trabalho.docx> <ENTREGA-CORRETOR-*.md> [mais pares]")


# ------------------------------------------------------- o teste do conferidor

def sabotagem(tmp, docx, reparos_md):
    """Estraga o aplicador de tres maneiras e exige recusa nas tres."""
    bom, falhas = A.trocar, []
    saida = tmp / "sabotado.docx"

    def roda(rotulo, deve_gravar):
        if saida.exists():
            saida.unlink()
        buf = io.StringIO()
        sys.argv = ["aplicar_docx.py", str(docx), str(reparos_md),
                    "--saida", str(saida)]
        with contextlib.redirect_stdout(buf):
            codigo = A.main()
        gravou = saida.exists()
        ok = gravou == deve_gravar
        print("    %-22s código=%d gravou=%-5s %s"
              % (rotulo, codigo, gravou, "ok" if ok else "*** NÃO PEGOU ***"))
        if not ok:
            falhas.append(rotulo)

    roda("intacto", True)
    A.trocar = lambda *a: bom(*a).replace(
        b'<w:delText xml:space="preserve">',
        b'<w:delText xml:space="preserve">XX', 1)
    roda("excluído adulterado", False)
    A.trocar = lambda *a: bom(*(a[:6] + (a[6] + " sobra que ninguém pediu",) + a[7:]))
    roda("Fica adulterado", False)
    A.trocar = lambda *a: bom(*a).replace(b"</w:p>", b"", 1)
    roda("parágrafo fundido", False)
    A.trocar = bom
    return not falhas


# ------------------------------------------------------------ o teste de carga

def reparos_de_tudo(docx, lista, destino):
    """Um reparo para cada frase aplicavel dos paragrafos citados.

    O `Fica` sai do proprio texto porque isto e teste de mecanismo. Uma em cada
    sete e retirada pura, para exercitar tambem o caminho sem <w:ins>."""
    doc = zipfile.ZipFile(docx).read("word/document.xml")
    sp = spans(doc)
    citados = sorted({n for _, _, l in itens(lista) for n in l if 1 <= n <= len(sp)})
    L, k = ["# Carga — %s" % Path(docx).name, ""], 0
    for n in citados:
        ini, fim, vazio = sp[n - 1]
        if vazio:
            continue
        texto, mapa, ats = R.fluxo(doc[ini:fim])
        if not texto.strip():
            continue
        for i, (x, y) in enumerate(R.frases(texto), 1):
            x, y = R.limites(texto, x, y)
            if x >= y or not R.cabe_num_segmento(mapa, ats, x, y)[0]:
                continue
            k += 1
            fica = "(nada)" if k % 7 == 0 else ("«%d» " % k) + texto[x:y]
            L += ["## S%d" % k, "", "**Está:** {{P%dF%d}}" % (n, i), "",
                  "**Fica:** " + fica, ""]
    destino.write_text("\n".join(L) + "\n", encoding="utf-8")
    return k


def confere(velho, novo):
    """Bem formado, contagem intacta, volta ao original, resto do zip parado."""
    a, b = zipfile.ZipFile(velho), zipfile.ZipFile(novo)
    for parte in ("word/document.xml", "word/comments.xml"):
        ET.fromstring(b.read(parte))
    dv, dn = a.read("word/document.xml"), b.read("word/document.xml")
    spv, spn = spans(dv), spans(dn)
    if len(spv) != len(spn):
        print("    *** a contagem de parágrafos mudou: %d → %d" % (len(spv), len(spn)))
        return False
    orig = "".join(R.fluxo(dv[i:f])[0] for i, f, _ in spv)
    volta = "".join(R.fluxo(A.visao_recusada(dn[i:f]))[0] for i, f, _ in spn)
    # A marca de comentario entra depois do <w:pPr>, e nao antes dele.
    fora = len(re.findall(rb"<w:p[ >][^>]*><w:commentRange", dn))
    tocadas = {"word/document.xml", "word/comments.xml", "[Content_Types].xml",
               "word/_rels/document.xml.rels"}
    outras = [x for x in a.namelist() if x not in tocadas and a.read(x) != b.read(x)]
    print("    parágrafos %d intactos | volta ao original: %s | pPr fora de "
          "lugar: %d | outras peças do zip tocadas: %s"
          % (len(spv), volta == orig, fora, outras or "nenhuma"))
    return volta == orig and fora == 0 and not outras


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Testa o aplicador e o conferidor dele.")
    ap.add_argument("--dir", help="onde gravar os temporários")
    a = ap.parse_args()
    tmp = Path(a.dir) if a.dir else Path(tempfile.mkdtemp(prefix="aplicador-"))
    tmp.mkdir(parents=True, exist_ok=True)
    os.chdir(RAIZ)

    ok = True
    for docx, lista in CASOS:
        if not Path(docx).exists():
            print("%s: não está aqui, e este caso fica de fora." % docx)
            continue
        print("%s" % docx)
        alvo = tmp / (Path(docx).stem + "-carga.md")
        n = reparos_de_tudo(docx, lista, alvo)
        print("  carga: %d reparos" % n)
        saida = tmp / (Path(docx).stem + "-carga.docx")
        r = subprocess.run([sys.executable, "scripts/aplicar_docx.py", docx,
                            str(alvo), "--saida", str(saida)],
                           capture_output=True, text=True, encoding="utf-8")
        print("   " + (r.stdout or r.stderr).strip().replace("\n", "\n   "))
        ok &= r.returncode == 0 and confere(docx, saida)
        print("  conferidor, sob sabotagem:")
        ok &= sabotagem(tmp, docx, alvo)

    print("\n%s" % ("TUDO PASSOU" if ok else "*** ALGUM TESTE FALHOU ***"))
    print("temporários em %s" % tmp)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

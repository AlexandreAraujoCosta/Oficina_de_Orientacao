# -*- coding: utf-8 -*-
"""Prepara, com um comando, o texto de um autor para o Warat conversacional.

POR QUE ISTO EXISTE

No teste de 18/09/2026 a preparacao levou cinco comandos encadeados a mao, e dois
deles falharam antes de acertar: a recusa das alteracoes quebrou o XML na primeira
versao, e a extracao recusou o arquivo com alteracao pendente. Quem vai rodar o
Warat e a sessao do proprio autor, que nao acompanhou nada disso. Um comando so
tira do modelo a escolha da ordem e dos nomes.

O QUE ELE FAZ, NA ORDEM

1. Olha o .docx: se ha alteracao controlada ou comentario, lista quem assina e
   PARA, a menos que se diga o que fazer com eles (--recusar-alteracoes, quando
   sao de outra pessoa; se sao do autor, ele os resolve no Word antes).
2. Grava em <pasta>/trabalho.docx o texto do autor (recusado, se foi o caso).
3. Extrai (extrair.py) para <pasta>/extracao/trabalho.txt.
4. Monta MAPA.md (mapa_estrutural.py) e MATERIAL.md (montar_material.py).
5. Liga <pasta>/scripts a pasta de scripts da Oficina.

A pasta padrao e trabalhos/<nome>/ dentro da Oficina, que o .gitignore exclui:
nada do trabalho sobe para o repositorio.

Uso:
    python scripts/preparar_trabalho.py <arquivo.docx> [--pasta trabalhos/<nome>] [--recusar-alteracoes]
    python scripts/preparar_trabalho.py --autoteste
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
from preparar_verificacao import ligar_scripts  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def marcas(docx):
    """(alteracoes por autor, numero de comentarios)."""
    z = zipfile.ZipFile(docx)
    d = z.read("word/document.xml")
    autores = Counter(m.decode("utf-8", "replace") for m in
                      re.findall(rb'<w:(?:ins|del|moveFrom|moveTo)\b[^>]*w:author="([^"]*)"', d))
    ncom = 0
    if "word/comments.xml" in z.namelist():
        ncom = len(re.findall(rb"<w:comment\b", z.read("word/comments.xml")))
    return autores, ncom


def rodar(args, cwd, env=None):
    r = subprocess.run([sys.executable] + [str(a) for a in args], cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        raise SystemExit("falhou: %s\n%s%s" % (" ".join(str(a) for a in args),
                                               r.stdout[-1500:], r.stderr[-1500:]))
    return r.stdout


def preparar(docx, pasta, recusar):
    docx, pasta = Path(docx).resolve(), Path(pasta).resolve()
    autores, ncom = marcas(docx)
    if (autores or ncom) and not recusar:
        linhas = ["O arquivo tem %d alterações controladas e %d comentários." % (sum(autores.values()), ncom)]
        linhas += ["   %s: %d" % (a, n) for a, n in autores.most_common()]
        linhas += ["", "Se são de outra pessoa (o orientador, por exemplo), rode de novo com",
                   "--recusar-alteracoes: a leitura vê só o texto do autor.",
                   "Se são do próprio autor, ele as aceita ou recusa no Word e salva antes."]
        raise SystemExit("\n".join(linhas))
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / "trabalho.docx"
    if autores or ncom:
        rodar([AQUI / "rejeitar_alteracoes.py", docx, destino], pasta)
    else:
        shutil.copy2(str(docx), str(destino))
    env = dict(os.environ, OFICINA_EXTRACAO=str(pasta / "extracao"))
    rodar([AQUI / "extrair.py", "trabalho.docx", "--forcar"], pasta, env)
    ext = pasta / "extracao" / "trabalho.txt"
    if not ext.exists():
        raise SystemExit("a extração não gravou %s" % ext)
    rodar([AQUI / "mapa_estrutural.py", ext, "-o", pasta / "MAPA.md"], pasta)
    rodar([AQUI / "montar_material.py", destino, ext, "-o", pasta / "MATERIAL.md", "--mapa", pasta / "MAPA.md"], pasta)
    lig = ligar_scripts(pasta)
    npar = sum(1 for l in ext.read_text(encoding="utf-8").splitlines() if re.match(r"(?:#+\s*)?\[P\d+\]", l))
    return {"pasta": pasta, "paragrafos": npar, "alteracoes": sum(autores.values()), "comentarios": ncom,
            "scripts": lig}


def autoteste():
    from docx_revisoes import docx_minimo
    f = []
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        limpo = d / "limpo.docx"
        limpo.write_bytes(docx_minimo('<w:p><w:r><w:t>Um paragrafo.</w:t></w:r></w:p>').getvalue())
        sujo = d / "sujo.docx"
        sujo.write_bytes(docx_minimo('<w:p><w:r><w:t>Texto </w:t></w:r><w:ins w:id="1" w:author="Outra" '
                                     'w:date="2026-01-01T00:00:00Z"><w:r><w:t>novo</w:t></w:r></w:ins></w:p>').getvalue())
        a, n = marcas(limpo)
        if a or n:
            f.append("acusou marcas num arquivo limpo")
        a, n = marcas(sujo)
        if a != Counter({"Outra": 1}):
            f.append("não achou a alteração de outra pessoa: %r" % a)
        try:
            preparar(sujo, d / "p", recusar=False)
            f.append("seguiu com alteração pendente sem que se dissesse o que fazer")
        except SystemExit as e:
            if "Outra" not in str(e):
                f.append("parou sem dizer quem assina")
    return f


def main():
    if sys.argv[1:] == ["--autoteste"]:
        f = autoteste()
        print("autoteste: " + ("passou (arquivo limpo sem acusação; alteração alheia acusada e para)"
                               if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("--pasta")
    ap.add_argument("--recusar-alteracoes", action="store_true")
    a = ap.parse_args()
    f = autoteste()
    if f:
        print("o próprio programa está quebrado: " + "; ".join(f))
        return 2
    pasta = a.pasta or (RAIZ / "trabalhos" / re.sub(r"[^\w\-]+", "-", Path(a.docx).stem).strip("-"))
    r = preparar(a.docx, pasta, a.recusar_alteracoes)
    print("  pronto em %s" % r["pasta"])
    print("  %d parágrafos numerados; %d alterações e %d comentários recusados; scripts por %s"
          % (r["paragrafos"], r["alteracoes"], r["comentarios"], r["scripts"]))
    print("  Arquivos: trabalho.docx, extracao/trabalho.txt, MAPA.md, MATERIAL.md, scripts/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

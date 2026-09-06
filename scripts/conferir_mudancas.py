# -*- coding: utf-8 -*-
"""Acusa mudanca de prompt que entrou sem ficha, e mede o quanto os prompts cresceram.

POR QUE ISTO EXISTE

Em 05/09/2026 oito alteracoes entraram nos prompts de leitura num dia. O
3-FRENTE-PARA-TRAS dobrou de tamanho e o ALBERTO cresceu 25%, e nenhuma das oito
rodou contra o prompt anterior sobre o mesmo trabalho. Nada no repositorio mostrava
isso: o diff de cada commit e pequeno, e a soma nao aparece em lugar nenhum.

O QUE ELE DECIDE

    ficha ausente    ACUSA. Commit que tocou prompts/ e nao aparece em MUDANCAS.md.
                     O casamento e por data e nome de arquivo, e por isso e frouxo:
                     ele erra para o lado de acusar, que e o lado barato.
    crescimento      INFORMA. Palavras de cada prompt hoje contra a data pedida.

Uso:
    python scripts/conferir_mudancas.py
    python scripts/conferir_mudancas.py --desde 2026-09-01
"""
import argparse
import io
import re
import subprocess
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
FICHA = RAIZ / "prompts" / "MUDANCAS.md"

# O alcance e o que instrui uma leitura, e nao tudo que mora em prompts/. Tipografia
# de pagina e texto de vitrine mudam sem mudar o que a leitura faz, e acusa-los
# encheria a saida de ruido: na primeira execucao, 27 acusacoes, 21 de tipografia.
def instrui_leitura(caminho):
    c = caminho.replace("\\", "/")
    if not c.startswith("prompts/") or not c.endswith(".md"):
        return False
    return ("/leituras/" in c or
            Path(c).name in ("ALBERTO.md", "LUIS.md", "MIRO.md",
                             "ESCOLHER-A-LEITURA.md"))


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=str(RAIZ),
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def commits(desde):
    fora = []
    bruto = git("log", "--since=" + desde, "--format=%h|%ad|%s", "--date=short",
                "--name-only", "--", "prompts/")
    bloco = None
    for ln in bruto.splitlines():
        if "|" in ln and ln.count("|") >= 2:
            bloco = {"h": ln.split("|")[0], "data": ln.split("|")[1],
                     "titulo": ln.split("|", 2)[2], "arqs": []}
            fora.append(bloco)
        elif ln.strip() and bloco is not None:
            if instrui_leitura(ln.strip()):
                bloco["arqs"].append(ln.strip())
    fora = [b for b in fora if b["arqs"]]
    return fora


def fichadas():
    """Os nomes de arquivo citados na tabela de MUDANCAS.md, por data."""
    if not FICHA.exists():
        return set()
    t = io.open(str(FICHA), encoding="utf-8").read()
    pares = set()
    for ln in t.splitlines():
        if not ln.startswith("| "):
            continue
        cols = [c.strip() for c in ln.strip("|").split("|")]
        if len(cols) < 2 or cols[0] in ("Data", "---"):
            continue
        for nome in re.findall(r"[0-9A-ZÁ-Ú][\w-]{3,}", cols[1]):
            pares.add((cols[0], nome.upper()))
    return pares


def autoteste():
    """Prova o casamento com um caso que ele TEM de acusar e um que nao pode."""
    p = fichadas()
    if not p:
        return ["MUDANCAS.md sem nenhuma ficha legivel"]
    falhas = []
    if not any(n.startswith("ALBERTO") for _, n in p):
        falhas.append("nao leu ALBERTO da tabela de fichas")
    falso = casa({"data": "01/01", "arqs": ["prompts/INEXISTENTE.md"]}, p)
    if falso:
        falhas.append("casou arquivo que nao esta em ficha nenhuma")
    if instrui_leitura("prompts/luis.html"):
        falhas.append("alcance inclui pagina html")
    if not instrui_leitura("prompts/leituras/3-FRENTE-PARA-TRAS.md"):
        falhas.append("alcance exclui prompt de leitura")
    return falhas


def casa(c, fichas):
    dia = "/".join(reversed(c["data"].split("-")[1:]))  # 2026-09-05 -> 05/09
    for a in c["arqs"]:
        base = Path(a).stem.upper()
        for d, n in fichas:
            if d == dia and (base.startswith(n) or n.startswith(base)):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde", default="1 day ago")
    a = ap.parse_args()

    falhas = autoteste()
    if falhas:
        print("  o proprio conferidor esta quebrado, e nao reporto nada:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste: le as fichas e nao casa arquivo fora delas")

    fichas = fichadas()
    sem = [c for c in commits(a.desde) if not casa(c, fichas)]
    print("\n  MUDANCAS SEM FICHA desde %s: %d" % (a.desde, len(sem)))
    for c in sem:
        print("     %s %s  %s" % (c["h"], c["data"], c["titulo"][:70]))

    print("\n  CRESCIMENTO desde %s" % a.desde)
    for p in sorted((RAIZ / "prompts").rglob("*.md")):
        rel = p.relative_to(RAIZ).as_posix()
        if not instrui_leitura(rel):
            continue
        antes = git("show", "HEAD@{%s}:%s" % (a.desde, rel))
        if not antes:
            continue
        va, vh = len(antes.split()), len(p.read_text(encoding="utf-8").split())
        if va and abs(vh - va) * 100 // va >= 5:
            print("     %-42s %5d -> %5d  (%+d%%)"
                  % (p.name, va, vh, (vh - va) * 100 // va))

    if sem:
        print("\n  Mudanca sem ficha e mudanca sem caso e sem falseamento ate prova")
        print("  em contrario. Escreva a linha em prompts/MUDANCAS.md.")
    return 1 if sem else 0


if __name__ == "__main__":
    sys.exit(main())

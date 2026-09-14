# -*- coding: utf-8 -*-
"""Poe o ALBERTO.md atual dentro da pagina do Alberto (prompts/analisador.html).

POR QUE ISTO EXISTE

A pagina carrega o prompt inteiro numa constante de JavaScript (`const P_UNICO =
"..."`), e ate 14/09/2026 ela era atualizada a mao ou por programa de ocasiao. Em
14/09 a ressalva do ALBERTO.md mudou e a pagina ficou com a versao velha, sem que
nada acusasse. Este programa faz uma coisa: substitui a constante pelo ALBERTO.md
atual, e diz se havia diferenca. Nao mexe em mais nada da pagina.

Depois dele: `python D:/Claude/Oficinas/publicar.py` monta o conjunto estatico,
e a pagina publicada como Artifact precisa ser republicada a partir do arquivo.

Uso:
    python scripts/atualizar_pagina_alberto.py             grava, se houver diferenca
    python scripts/atualizar_pagina_alberto.py --conferir  so diz se esta em dia
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
PROMPT = RAIZ / "prompts" / "ALBERTO.md"
PAGINA = RAIZ / "prompts" / "analisador.html"

# A constante, com o valor entre aspas duplas e escapes de JSON.
RE_CONST = re.compile(r'(const P_UNICO\s*=\s*)("(?:\\.|[^"\\])*")(\s*;)')


def embutido(html):
    m = RE_CONST.search(html)
    if not m:
        raise SystemExit("nao achei `const P_UNICO = \"...\";` na pagina")
    if len(RE_CONST.findall(html)) != 1:
        raise SystemExit("a constante aparece mais de uma vez; nao sei qual trocar")
    return m, json.loads(m.group(2))


def com_prompt(html, prompt):
    m, _ = embutido(html)
    novo = json.dumps(prompt, ensure_ascii=False)
    return html[:m.start(2)] + novo + html[m.end(2):]


# Controle positivo, plantado: a troca tem de por o texto novo e tirar o velho,
# e o que vai para a constante tem de voltar igual ao passar por JSON.
_H = 'x\nconst P_UNICO = "velho \\"a\\"";\ny'
_N = com_prompt(_H, 'novo "b"\ncom quebra')
assert embutido(_N)[1] == 'novo "b"\ncom quebra' and "velho" not in _N and _N.startswith("x\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--conferir", action="store_true")
    a = ap.parse_args()
    html = io.open(str(PAGINA), encoding="utf-8").read()
    prompt = io.open(str(PROMPT), encoding="utf-8").read()
    _, atual = embutido(html)
    if atual == prompt:
        print("  em dia: a pagina traz o ALBERTO.md atual (%d palavras)" % len(prompt.split()))
        return 0
    i = next((k for k in range(min(len(atual), len(prompt))) if atual[k] != prompt[k]),
             min(len(atual), len(prompt)))
    print("  DIFERE a partir do caractere %d: pagina %d palavras, prompt %d"
          % (i, len(atual.split()), len(prompt.split())))
    if a.conferir:
        return 1
    novo = com_prompt(html, prompt)
    io.open(str(PAGINA), "w", encoding="utf-8").write(novo)
    _, depois = embutido(novo)
    assert depois == prompt
    print("  gravado: %s agora traz o ALBERTO.md atual" % PAGINA.name)
    print("  falta: python D:/Claude/Oficinas/publicar.py, e republicar o Artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())

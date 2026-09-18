# -*- coding: utf-8 -*-
"""Mostra tudo o que uma proposta de redacao muda num paragrafo, anunciado ou nao.

POR QUE ISTO EXISTE

No Warat conversacional o modelo propoe redacao e o autor aceita ou recusa. Medido
em 18/09/2026: em duas propostas seguidas o modelo anunciou que so a ultima frase
mudava e reescreveu tambem as anteriores, e numa terceira trocou um apostrofo que
ninguem viu a olho. A regra de declarar o que muda estava escrita e nao bastou.

O "Esta" vem da extracao, por copia; o "Fica" e a proposta. O programa marca,
palavra a palavra, o que sai [-assim-] e o que entra {+assim+}, e da ALERTA
quando a proposta toca o que nao se reescreve: citacao entre aspas, numero e
referencia autor-ano que estavam no Esta e nao saem identicos no Fica. Alerta
bloqueia a proposta ate o autor decidir sobre ele.

Com --acrescenta, o arquivo traz so o trecho que entra antes do ponto final, e o
programa monta o paragrafo como ficaria antes de comparar; sem isso, o trecho era
comparado com o paragrafo inteiro e dava alertas falsos (critica fria de 18/09).

Uso:
    python scripts/comparar_proposta.py <extracao.txt> <numero-do-paragrafo> <fica.txt> [--acrescenta]
    python scripts/comparar_proposta.py --autoteste
"""
import difflib
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_revisoes import ler_extracao  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ASPAS = re.compile(r"[\"“”«][^\"“”«»]{3,}[\"“”»]")
NUMERO = re.compile(r"\d[\d.,%]*")
REF = re.compile(r"[A-ZÁÉÍÓÚ][A-Za-zÀ-ÿ'’\-]+(?: (?:and|e|&) [A-Z][A-Za-zÀ-ÿ'’\-]+)?,? "
                 r"\(?\d{4}[a-z]?(?:, p\. ?\d+)?\)?")


def normal(s):
    return s.replace("’", "'").replace("“", '"').replace("”", '"')


def diferenca(esta, fica):
    a, b = esta.split(), fica.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(" ".join(a[i1:i2]))
        if op in ("delete", "replace"):
            out.append("[-" + " ".join(a[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            out.append("{+" + " ".join(b[j1:j2]) + "+}")
    return " ".join(out)


def alertas(esta, fica):
    e, f = normal(esta), normal(fica)
    fora = []
    for nome, rx in (("citação entre aspas", ASPAS), ("referência", REF), ("número", NUMERO)):
        for m in rx.finditer(e):
            if m.group(0) not in f:
                fora.append("%s alterada ou retirada: %s" % (nome, m.group(0)))
    return fora


def com_acrescimo(esta, trecho):
    """O paragrafo com o trecho antes do ponto final, como aplicar_propostas o grava."""
    fim = esta.rstrip()
    if not fim or fim[-1] not in ".;":
        raise SystemExit("o parágrafo não termina em ponto ou ponto e vírgula; acréscimo não se aplica")
    return fim[:-1] + trecho.strip() + fim[-1]


def autoteste():
    esta = 'As Silva (2019) wrote, "the court decides by lists", in 1,234 cases.'
    livre = 'As Silva (2019) put it, "the court decides by lists", in 1,234 cases.'
    cit = 'As Silva (2019) wrote, "the court decides", in 1,234 cases.'
    ref = 'As one author wrote, "the court decides by lists", in 1,234 cases.'
    num = 'As Silva (2019) wrote, "the court decides by lists", in 1,243 cases.'
    apos = "the Court’s own rule"
    f = []
    if alertas(esta, livre):
        f.append("acusa troca de palavra fora da citação: %r" % alertas(esta, livre))
    if not any("aspas" in x for x in alertas(esta, cit)):
        f.append("não acusa citação alterada")
    if not any("referência" in x for x in alertas(esta, ref)):
        f.append("não acusa referência retirada")
    if not any("número" in x for x in alertas(esta, num)):
        f.append("não acusa número trocado")
    if "{+put" not in diferenca(esta, livre):
        f.append("não marca a palavra trocada: %s" % diferenca(esta, livre))
    if "[-Court’s-]" not in diferenca(apos, "the Court's own rule"):
        f.append("não mostra a troca de apóstrofo, que em 18/09 passou a olho")
    fica = com_acrescimo(esta, "; and more")
    if alertas(esta, fica) or "{+" not in diferenca(esta, fica):
        f.append("acréscimo: alerta falso ou acréscimo não marcado: %r" % alertas(esta, fica))
    return f


def main():
    f = autoteste()
    if sys.argv[1:] == ["--autoteste"]:
        print("autoteste: " + ("passou (troca livre sem alerta; citação, referência, número e "
                               "apóstrofo acusados)" if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    if f:
        print("o comparador está quebrado: " + "; ".join(f))
        return 2
    args = [a for a in sys.argv[1:] if a != "--acrescenta"]
    if len(args) != 3:
        print(__doc__.split("Uso:")[1])
        return 2
    par = ler_extracao(args[0])
    n = int(args[1].lstrip("Pp[").rstrip("]"))
    if n not in par:
        print("[P%d] não está na extração" % n)
        return 2
    fica = io.open(args[2], encoding="utf-8").read().strip()
    if "--acrescenta" in sys.argv:
        fica = com_acrescimo(par[n], fica)
    print("O QUE MUDA NO [P%d] (sai [-assim-], entra {+assim+}):\n" % n)
    print(diferenca(par[n], fica))
    al = alertas(par[n], fica)
    print("\n" + ("\n".join("ALERTA: " + x for x in al) if al
                  else "Nenhuma citação, referência ou número alterado."))
    return 1 if al else 0


if __name__ == "__main__":
    sys.exit(main())

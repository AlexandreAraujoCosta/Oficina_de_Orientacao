# -*- coding: utf-8 -*-
"""Conta os localizadores [P###] de um trecho de relatorio por faixa de paragrafos.

POR QUE ISTO EXISTE

A proposta de 13/09/2026 (prompts/PROPOSTA-20260913-pontas-contra-o-realizado.md)
manda uma leitura descrever o que a pesquisa realizou a partir dos artefatos, e o
risco medido no papel e a descricao sair como parafrase do capitulo de metodo. O
falsificador e de faixa: se a maioria dos localizadores da descricao cair no
capitulo de metodo, e nao nos apendices e nos resultados, a descricao e parafrase.
Este programa faz essa conta, e nada mais.

O QUE ELE FAZ

Le um arquivo markdown, recorta a secao pedida (do titulo que contem o texto dado
ate o proximo titulo de mesmo nivel ou superior), acha todo [P###] e conta por
faixa. As faixas vem na linha de comando, com nome e limites inclusivos.

Uso:
    python scripts/faixas_localizadores.py RELATORIO.md --secao "O que o trabalho fez" \
        --faixa metodo=63-96 --faixa resultados=99-207 --faixa apendices=265-782
    python scripts/faixas_localizadores.py REGISTRO.md --faixa ...     (o arquivo inteiro)
    python scripts/faixas_localizadores.py --autoteste

Sem --secao, conta o arquivo inteiro. Localizador fora de toda faixa vai em "outras".
Localizador repetido conta uma vez por ocorrencia: e a ancoragem da prosa que se mede.
"""
import argparse
import io
import re
import sys
from collections import Counter

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RE_LOC = re.compile(r"\[P(\d+)\]")
RE_TITULO = re.compile(r"^(#{1,6})\s+(.*)$")


def recortar(texto, trecho):
    """Devolve a secao cujo titulo contem `trecho`, ate o proximo titulo de nivel
    igual ou superior. Compara sem caixa. Devolve None se nao achar."""
    linhas = texto.splitlines()
    inicio = nivel = None
    for i, linha in enumerate(linhas):
        m = RE_TITULO.match(linha)
        if m and trecho.lower() in m.group(2).lower():
            inicio, nivel = i, len(m.group(1))
            break
    if inicio is None:
        return None
    fim = len(linhas)
    for j in range(inicio + 1, len(linhas)):
        m = RE_TITULO.match(linhas[j])
        if m and len(m.group(1)) <= nivel:
            fim = j
            break
    return "\n".join(linhas[inicio:fim])


def contar(texto, faixas):
    """faixas: lista de (nome, a, b). Devolve Counter por nome, mais 'outras' e total."""
    c = Counter()
    total = 0
    for m in RE_LOC.finditer(texto):
        n = int(m.group(1))
        total += 1
        for nome, a, b in faixas:
            if a <= n <= b:
                c[nome] += 1
                break
        else:
            c["outras"] += 1
    return c, total


def ler_faixa(s):
    nome, _, lim = s.partition("=")
    a, _, b = lim.partition("-")
    if not (nome and a and b):
        raise SystemExit("faixa mal escrita: %r (esperado nome=inicio-fim)" % s)
    return nome, int(a), int(b)


def autoteste():
    """Controle positivo: um trecho plantado com contagem conhecida, e um caso
    que tem de reprovar (secao inexistente)."""
    doc = ("# Relatorio\n\nprosa [P5]\n\n## O que o trabalho fez\n\n"
           "a [P70] b [P100] c [P300] d [P301] e [P900]\n\n## Outra\n\n[P71]\n")
    sec = recortar(doc, "o que o trabalho fez")
    assert sec is not None and "[P71]" not in sec and "[P5]" not in sec, sec
    c, total = contar(sec, [("metodo", 63, 96), ("resultados", 99, 207),
                            ("apendices", 265, 782)])
    assert total == 5, total
    assert c["metodo"] == 1 and c["resultados"] == 1 and c["apendices"] == 2 \
        and c["outras"] == 1, dict(c)
    assert recortar(doc, "secao que nao existe") is None
    # sem secao: o arquivo inteiro
    c2, t2 = contar(doc, [("metodo", 63, 96)])
    assert t2 == 7 and c2["metodo"] == 2, (t2, dict(c2))
    print("  autoteste: ok (5 localizadores na secao, 1/1/2/1; 7 no arquivo)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--secao", help="trecho do titulo da secao a recortar")
    ap.add_argument("--faixa", action="append", default=[],
                    help="nome=inicio-fim, inclusivo; repita para cada faixa")
    ap.add_argument("--autoteste", action="store_true")
    a = ap.parse_args()
    if a.autoteste:
        return autoteste()
    if not a.arquivo or not a.faixa:
        ap.error("preciso do arquivo e de ao menos uma --faixa")
    faixas = [ler_faixa(f) for f in a.faixa]
    texto = io.open(a.arquivo, encoding="utf-8").read()
    if a.secao:
        texto = recortar(texto, a.secao)
        if texto is None:
            print("  NAO ACHEI secao cujo titulo contenha %r" % a.secao)
            return 2
    c, total = contar(texto, faixas)
    if total == 0:
        print("  ZERO localizadores no trecho; a conta nao informa nada")
        return 2
    print("  %d localizadores%s" % (total, " na secao %r" % a.secao if a.secao else ""))
    for nome, _, _ in faixas:
        print("  %-12s %4d  (%3.0f%%)" % (nome, c[nome], 100.0 * c[nome] / total))
    print("  %-12s %4d  (%3.0f%%)" % ("outras", c["outras"], 100.0 * c["outras"] / total))
    return 0


if __name__ == "__main__":
    sys.exit(main())

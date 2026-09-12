# -*- coding: utf-8 -*-
"""Conta a fracao de itens de um relatorio que mudam alguma afirmacao do trabalho.

POR QUE ISTO EXISTE

A oficina mede precisao de endereco, cobertura e custo, e o alvo declarado em
10/09/2026 e outro: a relevancia dos itens para quem escreveu o trabalho. Sem um
numero para isso, cada mudanca de prompt e julgada pelo que se mede, e o que se
media fazia o volume subir: em 08/09/2026 um cotejo cego achou 50 itens de
superficie em 91.

O QUE ELE FAZ

Le a classificacao que uma voz produziu com `prompts/CLASSIFICAR-RELEVANCIA.md`
(uma linha por item: codigo | classe | afirmacao | razao), casa os codigos com os
da prosa do relatorio, e imprime a tabela por classe e duas fracoes:

    relevantes   (CONCLUSAO + ALCANCE) / itens que pedem providencia
    superficie   NADA / itens que pedem providencia

Itens que pedem providencia sao os de prefixo S, SC, D e A. F e C nao entram na
conta, e Q entra numa linha propria.

O QUE ELE DECIDE

    codigo so na prosa          ACUSA. O classificador nao leu o item.
    codigo so na classificacao  ACUSA. O classificador inventou um item.
    classe desconhecida         ACUSA.
    codigo repetido             ACUSA.

Nao julga se a classe atribuida esta certa: isso e da voz que classificou, e a
afericao dela esta em AFERICOES.md.

Uso:
    python scripts/relevancia.py <relatorio.md> <classificacao.txt>
    python scripts/relevancia.py --autoteste
"""
import argparse
import io
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from conferir_bloco import da_prosa, executavel  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CLASSES = ("CONCLUSAO", "ALCANCE", "CONFERE", "NADA", "FORCA", "PERGUNTA")
RELEVANTES = ("CONCLUSAO", "ALCANCE")
RE_LINHA = re.compile(r"^\s*([A-Z]{1,2}\d+)\s*\|\s*([A-Z]+)\s*\|(.*?)\|(.*)$")


def ler_classificacao(caminho):
    """Devolve (classes por codigo, queixas)."""
    classes, queixas = {}, []
    for n, linha in enumerate(io.open(caminho, encoding="utf-8",
                                      errors="replace"), 1):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        m = RE_LINHA.match(linha)
        if not m:
            continue                      # cabecalho de alcance, ou prosa
        cod, classe = m.group(1), m.group(2).upper()
        if classe not in CLASSES:
            queixas.append("linha %d: classe desconhecida %r em %s" % (n, classe, cod))
            continue
        if cod in classes:
            queixas.append("linha %d: %s classificado duas vezes" % (n, cod))
            continue
        classes[cod] = classe
    return classes, queixas


def contar(codigos_prosa, classes):
    """A tabela e as duas fracoes. Devolve (Counter, relevantes, superficie, n)."""
    tabela = Counter()
    n = 0
    for cod in codigos_prosa:
        if cod not in classes:
            continue
        classe = classes[cod]
        tabela[classe] += 1
        if executavel(cod):
            n += 1
    rel = sum(tabela[c] for c in RELEVANTES)
    sup = tabela["NADA"]
    return tabela, rel, sup, n


def relatorio(caminho_md, caminho_cls):
    prosa = da_prosa(caminho_md)
    classes, queixas = ler_classificacao(caminho_cls)
    so_prosa = sorted(set(prosa) - set(classes), key=chave)
    so_cls = sorted(set(classes) - set(prosa), key=chave)
    # A execucao e o que separa relevante de forca: um F classificado como
    # CONCLUSAO por engano nao pode inflar a fracao.
    for cod, classe in list(classes.items()):
        if not executavel(cod) and classe in RELEVANTES + ("CONFERE", "NADA"):
            queixas.append("%s nao pede providencia e recebeu %s; nao entra na conta"
                           % (cod, classe))
            classes[cod] = "FORCA" if cod[0] in "FC" else "PERGUNTA"
    tabela, rel, sup, n = contar(prosa, classes)
    return {"tabela": tabela, "relevantes": rel, "superficie": sup, "n": n,
            "so_prosa": so_prosa, "so_cls": so_cls, "queixas": queixas,
            "total_prosa": len(prosa)}


def chave(cod):
    m = re.match(r"([A-Z]+)(\d+)", cod)
    return (m.group(1), int(m.group(2))) if m else (cod, 0)


def imprimir(r):
    print("  itens na prosa: %d; classificados: %d que pedem providencia"
          % (r["total_prosa"], r["n"]))
    for c in CLASSES:
        if r["tabela"][c]:
            print("    %-9s %3d" % (c, r["tabela"][c]))
    if r["n"]:
        print("  relevantes (CONCLUSAO + ALCANCE): %d de %d = %.0f%%"
              % (r["relevantes"], r["n"], 100.0 * r["relevantes"] / r["n"]))
        print("  superficie (NADA):                %d de %d = %.0f%%"
              % (r["superficie"], r["n"], 100.0 * r["superficie"] / r["n"]))
    if r["so_prosa"]:
        print("  ACUSA: %d codigo(s) da prosa sem classificacao: %s"
              % (len(r["so_prosa"]), ", ".join(r["so_prosa"])))
    if r["so_cls"]:
        print("  ACUSA: %d codigo(s) classificados que a prosa nao tem: %s"
              % (len(r["so_cls"]), ", ".join(r["so_cls"])))
    for q in r["queixas"]:
        print("  ACUSA: %s" % q)


# ------------------------------------------------------------------ autoteste
PROSA = (u"### S1. Um titulo\n\n### S2. Outro titulo\n\n### SC1. Uma gralha\n\n"
         u"**F1 - Um ponto forte.**\n\n### Q1. Uma pergunta\n")
CLS_BOA = (u"S1 | CONCLUSAO | a conclusao muda | diz a conta\n"
           u"S2 | CONFERE | - | so o denominador\n"
           u"SC1 | NADA | - | gralha\n"
           u"F1 | FORCA | - | forte\n"
           u"Q1 | PERGUNTA | - | pergunta\n")
CLS_FALTA = CLS_BOA.replace(u"SC1 | NADA | - | gralha\n", u"")
CLS_SOBRA = CLS_BOA + u"S9 | NADA | - | nao existe\n"
CLS_CARIDADE = CLS_BOA.replace(u"F1 | FORCA", u"F1 | CONCLUSAO")


def _escreve(nome, texto):
    p = Path(tempfile.gettempdir()) / nome
    p.write_text(texto, encoding="utf-8")
    return str(p)


def autoteste():
    falhas = []
    md = _escreve("_relev_prosa.md", PROSA)
    r = relatorio(md, _escreve("_relev_boa.txt", CLS_BOA))
    if (r["n"], r["relevantes"], r["superficie"]) != (3, 1, 1):
        falhas.append("conta errada no caso limpo: n=%d rel=%d sup=%d"
                      % (r["n"], r["relevantes"], r["superficie"]))
    if r["so_prosa"] or r["so_cls"] or r["queixas"]:
        falhas.append("acusa no caso limpo")
    # CONTROLE POSITIVO: cada acusacao tem de disparar num caso plantado.
    if relatorio(md, _escreve("_relev_falta.txt", CLS_FALTA))["so_prosa"] != ["SC1"]:
        falhas.append("nao acusa codigo sem classificacao")
    if relatorio(md, _escreve("_relev_sobra.txt", CLS_SOBRA))["so_cls"] != ["S9"]:
        falhas.append("nao acusa codigo inventado")
    rc = relatorio(md, _escreve("_relev_carid.txt", CLS_CARIDADE))
    if rc["relevantes"] != 1 or not rc["queixas"]:
        falhas.append("ponto forte classificado como CONCLUSAO inflou a fracao")
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio", nargs="?")
    ap.add_argument("classificacao", nargs="?")
    ap.add_argument("--autoteste", action="store_true")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio contador esta quebrado, e nao reporto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: 5 casos, todos passaram (conta, falta, sobra, caridade)")
    if a.autoteste or not (a.relatorio and a.classificacao):
        return 0
    imprimir(relatorio(a.relatorio, a.classificacao))
    try:
        from afericao import selo
        selo(__file__)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

Itens que pedem providencia sao os de prefixo S, SC, D, A e P. F, C e as
contribuicoes das leituras (AC, PC, DC) nao entram na conta, e Q entra numa
linha propria.

Onde um prefixo for decisao e nao item, declara-se com `--decisoes D`: o relatorio
do Luis ate 06/09/2026 chamava de D as decisoes que agrupam itens S, e contar as
duas coisas conta o mesmo item duas vezes. A partir de 10/09 D e item da leitura 3.

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
from conferir_bloco import da_prosa  # noqa: E402

# O conjunto e desta medida, e nao o da margem (`conferir_bloco.EXECUTAVEIS`,
# espelho de `lista_corretor.py`), que nao tem P. P e o prefixo da leitura 2
# desde 10/09/2026, e o item pede providencia chegue ele a margem ou nao.
PROVIDENCIA = ("S", "SC", "D", "A", "P")


def prefixo(codigo):
    m = re.match(r"[A-Z]+", codigo)
    return m.group(0) if m else ""


def pede_providencia(codigo):
    return prefixo(codigo) in PROVIDENCIA

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
        if pede_providencia(cod):
            n += 1
    rel = sum(tabela[c] for c in RELEVANTES)
    sup = tabela["NADA"]
    return tabela, rel, sup, n


def relatorio(caminho_md, caminho_cls, decisoes=()):
    prosa = da_prosa(caminho_md)
    classes, queixas = ler_classificacao(caminho_cls)
    # A decisao agrupa itens que ja estao na conta; sai dela, e sai tambem das
    # acusacoes: a pergunta longa de uma decisao passa do limite de titulo de
    # `da_prosa`, e acusar como invencao o que se declarou fora da conta e ruido.
    decis = sorted((c for c in set(classes) | set(prosa) if prefixo(c) in decisoes),
                   key=chave)
    so_prosa = sorted((set(prosa) - set(classes)) - set(decis), key=chave)
    so_cls = sorted((set(classes) - set(prosa)) - set(decis), key=chave)
    for cod in decis:
        classes.pop(cod, None)
    # A providencia e o que separa relevante de forca: um F classificado como
    # CONCLUSAO por engano nao pode inflar a fracao.
    for cod, classe in list(classes.items()):
        if not pede_providencia(cod) and classe in RELEVANTES + ("CONFERE", "NADA"):
            queixas.append("%s nao pede providencia e recebeu %s; nao entra na conta"
                           % (cod, classe))
            classes[cod] = "PERGUNTA" if prefixo(cod) == "Q" else "FORCA"
    tabela, rel, sup, n = contar(prosa, classes)
    return {"tabela": tabela, "relevantes": rel, "superficie": sup, "n": n,
            "so_prosa": so_prosa, "so_cls": so_cls, "queixas": queixas,
            "total_prosa": len(prosa), "decisoes": decis}


def chave(cod):
    m = re.match(r"([A-Z]+)(\d+)", cod)
    return (m.group(1), int(m.group(2))) if m else (cod, 0)


def imprimir(r):
    print("  itens na prosa: %d; classificados: %d que pedem providencia"
          % (r["total_prosa"], r["n"]))
    if r["decisoes"]:
        print("  fora da conta, declaradas decisao: %d (%s)"
              % (len(r["decisoes"]), ", ".join(r["decisoes"])))
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

# O formato de 10/09 (P da leitura 2, contribuicao AC) e o de ate 06/09 (D como
# decisao, item com titulo vazio na linha do codigo), no mesmo arquivo.
PROSA_NOVA = (u"## S1\n\nO titulo veio embaixo.\n\n### P1. Um item da leitura 2\n\n"
              u"**D1. Qual criterio conta?** Resolve S1 e P1.\n\n**AC1.** Uma contribuicao.\n")
CLS_NOVA = (u"S1 | NADA | - | gralha\n"
            u"P1 | ALCANCE | o percentual vale para a amostra | diz o conjunto\n"
            u"D1 | CONCLUSAO | a tese muda | decisao\n"
            u"AC1 | CONCLUSAO | - | contribuicao classificada por engano\n")


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
    mn = _escreve("_relev_nova.md", PROSA_NOVA)
    cn = _escreve("_relev_nova.txt", CLS_NOVA)
    rd = relatorio(mn, cn, decisoes=("D",))
    if (rd["n"], rd["relevantes"], rd["superficie"]) != (2, 1, 1) or rd["decisoes"] != ["D1"]:
        falhas.append("com D declarada decisao: n=%d rel=%d sup=%d decisoes=%r"
                      % (rd["n"], rd["relevantes"], rd["superficie"], rd["decisoes"]))
    if rd["so_prosa"] or rd["so_cls"]:
        falhas.append("item de titulo vazio ou P sem casar: %r %r"
                      % (rd["so_prosa"], rd["so_cls"]))
    if not any("AC1" in q for q in rd["queixas"]):
        falhas.append("contribuicao AC classificada CONCLUSAO nao foi acusada")
    # CONTROLE: sem declarar, D volta a ser item e a conta sobe.
    ri = relatorio(mn, cn)
    if (ri["n"], ri["relevantes"]) != (3, 2):
        falhas.append("sem --decisoes D devia contar D1: n=%d rel=%d"
                      % (ri["n"], ri["relevantes"]))
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio", nargs="?")
    ap.add_argument("classificacao", nargs="?")
    ap.add_argument("--autoteste", action="store_true")
    ap.add_argument("--decisoes", default="",
                    help="prefixos que neste relatorio sao decisao, separados por virgula")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio contador esta quebrado, e nao reporto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: passou (conta, falta, sobra, caridade, decisao declarada, "
          "P e titulo vazio, contribuicao acusada, controle sem declarar)")
    if a.autoteste or not (a.relatorio and a.classificacao):
        return 0
    decisoes = tuple(x.strip().upper() for x in a.decisoes.split(",") if x.strip())
    imprimir(relatorio(a.relatorio, a.classificacao, decisoes))
    try:
        from afericao import selo
        selo(__file__)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

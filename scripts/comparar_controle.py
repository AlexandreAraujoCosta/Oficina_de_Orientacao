# -*- coding: utf-8 -*-
"""Instrumenta a comparação entre o relatório da oficina e o do controle.

POR QUE ISTO EXISTE

O protocolo (`TCC/PROTOCOLO-CONTROLE.md`) exige que três dos seis eixos rodem
cegos: quem julga não pode saber de qual relatório veio a afirmação. Fazer isso à
mão é impossível, porque quem separa já viu. Aqui o sorteio é por programa, com
semente registrada, e a saída sai embaralhada e sem marca de origem.

O QUE ELE FAZ

    eixo 1   mede o endereçamento dos dois: quantas afirmações trazem endereço
             conferível. Programa, e não julgamento.
    eixo 2   sorteia N afirmações endereçadas de cada, embaralha, tira a origem,
             e grava dois arquivos: o cego, que vai ao verificador, e a chave,
             que fica guardada e só se abre depois.
    eixos    4 e 5 usam o mesmo mecanismo sobre itens, e não sobre afirmações.
             `--itens` liga esse modo.

O QUE ELE NÃO FAZ

Não julga. Não decide o que é afirmação forte. Não abre a chave. A separação
entre o que o programa faz e o que a leitura faz é o que dá sentido ao cego.

Uso:
    python comparar_controle.py <oficina.md> <controle.md> --saida DIR
    python comparar_controle.py <oficina.md> <controle.md> --saida DIR --itens
"""
import argparse
import hashlib
import random
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Endereço conferível: o localizador de parágrafo, ou a referência a uma peça
# numerada do trabalho. "no capítulo 4" não conta: não diz onde abrir.
RE_ENDERECO = re.compile(
    r"\[P\d+(?:\s*[-–]\s*P?\d+)?\]"
    r"|\bse(?:ç|c)(?:ão|ao)\s+\d+(?:\.\d+)*"
    r"|\b(?:gr[áa]fico|tabela|quadro|figura|ap[êe]ndice|anexo)\s+\d+"
    r"|\bnota\s+\d+"
    r"|\bp\.\s*\d+", re.I)

# Fim de frase, poupando abreviaturas e o ponto de numeração de seção.
RE_FRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ú*\[])")


def frases(texto):
    """Afirmações candidatas: frases do corpo, sem cabeçalho nem tabela."""
    linhas = []
    for l in texto.split("\n"):
        s = l.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("---"):
            continue
        if s.startswith("<!--"):
            continue
        linhas.append(s)
    bruto = " ".join(linhas)
    saida = []
    for f in RE_FRASE.split(bruto):
        f = " ".join(f.split())
        if len(f) >= 40:
            saida.append(f)
    return saida


RE_ITEM = re.compile(
    r"^(?:#{2,4}\s*|\*\*)([A-Z]{1,2}\d+)[.,:]?\s*(.*?)(?:\*\*)?\s*$", re.M)


def itens(texto):
    """Itens do relatório: código e título. Serve aos eixos 4 e 5."""
    vistos, saida = set(), []
    for m in RE_ITEM.finditer(texto):
        cod, tit = m.group(1), " ".join(m.group(2).split())
        if len(tit) < 20 or cod in vistos:
            continue
        vistos.add(cod)
        saida.append((cod, tit))
    return saida


def autoteste():
    falhas = []
    if not RE_ENDERECO.search("como diz [P1194], a terceira frase"):
        falhas.append("nao acha localizador de paragrafo")
    if not RE_ENDERECO.search("a legenda do Gráfico 54"):
        falhas.append("nao acha figura numerada")
    if not RE_ENDERECO.search("o que a seção 7.4 monta"):
        falhas.append("nao acha secao numerada")
    if RE_ENDERECO.search("no capítulo seguinte o autor retoma"):
        falhas.append("aceita referencia vaga como endereco")
    f = frases("Uma frase inicial que tem tamanho suficiente para entrar. "
               "Outra frase que também tem tamanho suficiente para entrar aqui.")
    if len(f) != 2:
        falhas.append("separador de frases: %d em vez de 2" % len(f))
    return falhas


def main():
    ap = argparse.ArgumentParser(description="Instrumenta a comparação cega.")
    ap.add_argument("oficina")
    ap.add_argument("controle")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--n", type=int, default=30, help="quantas de cada relatório")
    ap.add_argument("--semente", type=int, default=None,
                    help="padrão: derivada do conteúdo dos dois arquivos, de modo "
                         "que a mesma dupla dê sempre o mesmo sorteio e ninguém "
                         "possa repetir até sair a amostra que lhe convém")
    ap.add_argument("--itens", action="store_true",
                    help="sorteia itens em vez de afirmações (eixos 4 e 5)")
    a = ap.parse_args()

    falhas = autoteste()
    if falhas:
        print("  o extrator esta quebrado, e nao gero amostra:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste do extrator: passou")

    to = Path(a.oficina).read_text(encoding="utf-8")
    tc = Path(a.controle).read_text(encoding="utf-8")

    if a.semente is None:
        a.semente = int(hashlib.sha256(
            (to + tc).encode("utf-8")).hexdigest()[:8], 16)

    if a.itens:
        po = [t for _, t in itens(to)]
        pc = [t for _, t in itens(tc)]
        rot = "itens"
    else:
        po, pc = frases(to), frases(tc)
        rot = "afirmações"

    # ---- eixo 1: endereçamento
    def com(lista):
        return [x for x in lista if RE_ENDERECO.search(x)]
    eo, ec = com(po), com(pc)
    print("\n  EIXO 1, endereçamento (%s)" % rot)
    print("    oficina:  %4d, com endereço %4d (%.0f%%)"
          % (len(po), len(eo), 100 * len(eo) / len(po) if po else 0))
    print("    controle: %4d, com endereço %4d (%.0f%%)"
          % (len(pc), len(ec), 100 * len(ec) / len(pc) if pc else 0))

    # ---- amostra cega
    r = random.Random(a.semente)
    amostra = ([("oficina", x) for x in r.sample(eo, min(a.n, len(eo)))]
               + [("controle", x) for x in r.sample(ec, min(a.n, len(ec)))])
    r.shuffle(amostra)

    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    sufixo = "itens" if a.itens else "afirmacoes"

    cego = ["# Amostra cega: %s" % rot, "",
            "Sorteada por `comparar_controle.py`, semente `%d`. **A origem de cada"
            % a.semente,
            "linha não está aqui, e é essa a razão de o arquivo existir.** Cada",
            "entrada tem um número, e a resposta se dá por número.", "",
            "Para cada uma, abra a fonte e responda: **confere**, **não confere**, ou",
            "**não dá para decidir**, e dê o endereço na fonte que sustenta a sua",
            "resposta. Onde a entrada afirmar ausência, procure você mesmo, e prove a",
            "sua busca antes de concordar com a ausência.", "", "---", ""]
    chave = ["# Chave da amostra (não abrir antes de a conferência voltar)", "",
             "semente `%d`" % a.semente, ""]
    for i, (origem, txt) in enumerate(amostra, 1):
        cego += ["**%d.** %s" % (i, txt), ""]
        chave.append("%d. %s" % (i, origem))

    (pasta / ("CEGO-%s.md" % sufixo)).write_text("\n".join(cego) + "\n", encoding="utf-8")
    (pasta / ("CHAVE-%s.md" % sufixo)).write_text("\n".join(chave) + "\n", encoding="utf-8")
    print("\n  amostra cega: %d entradas (%d de cada), semente %d"
          % (len(amostra), min(a.n, len(eo)), a.semente))
    print("    %s" % (pasta / ("CEGO-%s.md" % sufixo)))
    print("    %s  <- não abrir antes" % (pasta / ("CHAVE-%s.md" % sufixo)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

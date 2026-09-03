# -*- coding: utf-8 -*-
"""Grafo de dependencia entre capitulos, por programa.

Capitulo isolado e uma contagem: quantas vezes o resto do trabalho invoca o que
ele produziu. Duas medidas, e as duas com controle.

  REMISSAO EXPLICITA  "como visto no capitulo 1", "conforme a secao 2.3"
  FLUXO DE TERMO      termo que estreia num capitulo e reaparece noutro

O que se procura: capitulo que ninguem consome. Gabarito de 01/09/2026: numa
leitura do trabalho inteiro, o capitulo 2 de uma dissertacao foi apontado como custando
trinta paginas e entregando uma categoria. Se o grafo nao o mostrar fraco, o
grafo nao serve.
"""
import re
import sys
import pathlib
import argparse
import collections
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINHA = re.compile(
    r"^\[[^\]]+\]\s+P(?P<n>\d+)(?:\s+\[(?P<tipo>[A-Z_]+)\])?"
    r"\s+\(p\.(?P<pag>\d+)\)\s*(?P<txt>.*)$", re.M)
SUMARIO = re.compile(r"\.{4,}\s*\d*\s*$")
CAB1 = re.compile(r"^(\d+)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ\s,:;–-]{6,}")
REMISSAO = re.compile(
    r"cap[íi]tulo\s+(\d)|se[çc][ãa]o\s+(\d)(?:\.\d+)*|item\s+(\d)(?:\.\d+)*", re.I)


def tok(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z]{5,}", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("extracao")
    args = ap.parse_args()
    bruto = pathlib.Path(args.extracao).read_text(encoding="utf-8")
    P = {int(m.group("n")): (int(m.group("pag")), m.group("tipo") or "",
                             m.group("txt").strip())
         for m in LINHA.finditer(bruto)}
    N = max(P)

    # ---- fronteiras dos capitulos
    # O cabecalho de nivel 1 nao sobrevive a extracao em varios trabalhos: ele e
    # fundido ao paragrafo seguinte ou perde a numeracao. Os de subsecao (X.Y)
    # sobrevivem, e o capitulo se infere da parte inteira do numero. Exige-se
    # titulo com letras para nao capturar linha de tabela ("3 Pg. 4 - - -").
    SUB = re.compile(r"^(?:\d{1,3}\s+)?(\d)\.(\d+)(?:\.\d+)*\s+"
                     r"(?=[A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç])(.{10,})")
    # o material de abertura termina na ultima linha pontilhada do sumario;
    # ha sumario cuja entrada nao traz pontilhado, e ela passaria o filtro
    pontilhadas = [n for n in P if SUMARIO.search(P[n][2])]
    base = max(pontilhadas) if pontilhadas else 0
    marcos = []
    for n in sorted(P):
        if n <= base:
            continue
        tx = P[n][2]
        if SUMARIO.search(tx):
            continue
        m = SUB.match(tx)
        if m and sum(ch.isalpha() for ch in m.group(3)[:40]) > 20:
            marcos.append((int(m.group(1)), int(m.group(2)), n))
    if not marcos:
        sys.exit("!! nenhum cabecalho de subsecao; grafo nao construido")

    # a primeira subsecao de cada capitulo abre o capitulo
    abre = {}
    for cap, sub, n in marcos:
        if cap not in abre or n < abre[cap]:
            abre[cap] = n
    fim_corpo = min([n for n in sorted(P)
                     if re.match(r"^(REFER[EÊ]NCIAS?|CONCLUS[AÃ]O|CONSIDERA[CÇ][OÕ]ES)",
                                 P[n][2], re.I)
                     and n > max(abre.values())] or [N + 1])
    ordem = sorted(abre)
    caps = {}
    for i, num in enumerate(ordem):
        fim = abre[ordem[i + 1]] if i + 1 < len(ordem) else fim_corpo
        caps[num] = (abre[num], fim)
    print("  capítulos (pela 1a subseção de cada): %s"
          % {k: "P%d-P%d" % v for k, v in caps.items()})
    print("  corpo termina em P%d" % fim_corpo)
    print("  ATENÇÃO: o texto do capítulo anterior à sua 1a subseção fica de fora.")

    def cap_de(n):
        for num, (a, b) in caps.items():
            if a <= n < b:
                return num
        return None

    # ---- CONTROLE POSITIVO do detector de remissao
    ctrl = sum(1 for n in P if REMISSAO.search(P[n][2]))
    print("  controle: %d parágrafos contêm remissão explícita" % ctrl)
    if ctrl == 0:
        sys.exit("!! detector de remissão não acha nada; não reporto")

    # ---- remissoes: quem invoca quem
    inv = collections.Counter()
    for n in P:
        orig = cap_de(n)
        if orig is None:
            continue
        for m in REMISSAO.finditer(P[n][2]):
            alvo = int(next(g for g in m.groups() if g))
            if alvo in caps and alvo != orig:
                inv[(orig, alvo)] += 1

    # ---- fluxo de termo: termo que estreia num capitulo e reaparece noutro
    estreia, uso = {}, collections.Counter()
    freq = collections.Counter()
    for n in sorted(P):
        for w in set(tok(P[n][2])):
            freq[w] += 1
    vocab = {w for w, c in freq.items() if 4 <= c <= 200}
    for n in sorted(P):
        c = cap_de(n)
        if c is None:
            continue
        for w in set(tok(P[n][2])):
            if w not in vocab:
                continue
            if w not in estreia:
                estreia[w] = c
            elif estreia[w] != c:
                uso[(c, estreia[w])] += 1

    print()
    print("  O capitulo posterior tem menos texto adiante para irrigar, entao o")
    print("  fluxo bruto favorece o primeiro. A coluna que decide e a normalizada:")
    print("  fluxo dividido pelo numero de paragrafos que vem depois do capitulo.")
    print()
    print("  %-5s %-8s %-9s %-9s %-12s %-9s %s"
          % ("cap", "parágs", "adiante", "remiss.", "fluxo bruto", "por parág", "invocado por"))
    linhas = []
    for num in sorted(caps):
        a, b = caps[num]
        adiante = max(0, fim_corpo - b)
        recebe_r = sum(v for (o, d), v in inv.items() if d == num)
        recebe_t = sum(v for (o, d), v in uso.items() if d == num)
        norm = recebe_t / adiante if adiante else float("nan")
        quem = sorted({o for (o, d) in list(inv) + list(uso) if d == num})
        linhas.append((num, b - a, adiante, recebe_r, recebe_t, norm))
        print("  %-5d %-8d %-9d %-9d %-12d %-9.2f %s"
              % (num, b - a, adiante, recebe_r, recebe_t, norm,
                 quem if quem else "NINGUÉM"))
    validos = [x for x in linhas if x[2] > 0]
    if len(validos) >= 2:
        pior = min(validos, key=lambda x: x[5])
        melhor = max(validos, key=lambda x: x[5])
        print()
        print("  O capitulo %d e irrigado a %.0f%% da taxa do capitulo %d."
              % (pior[0], 100 * pior[5] / melhor[5], melhor[0]))
        print("  O ultimo capitulo aparece com fluxo zero por construcao: nao ha")
        print("  texto depois dele, e a medida so conta fluxo para a frente.")
    print()
    print("  remissões explícitas, origem -> destino:")
    for (o, d), v in sorted(inv.items(), key=lambda x: -x[1]):
        print("     cap %d -> cap %d : %d" % (o, d, v))


if __name__ == "__main__":
    main()

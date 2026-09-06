# -*- coding: utf-8 -*-
"""Roda todas as buscas de uma leitura numa chamada so, cada uma com o seu controle.

POR QUE ISTO EXISTE

Medido em 06/09/2026. Uma leitura do acervo fez 126 chamadas de ferramenta em
cinquenta minutos, e a correlacao entre numero de chamadas e tempo de relogio, em
dezesseis execucoes do mesmo dia, foi de 0,82. O tamanho do contexto nao explicava
nada: o cache servia 98,4% da entrada e o intervalo mediano entre eventos era de
1,6 segundo. O tempo estava nas idas e voltas, e a maior parte delas era busca em
Python feita uma de cada vez.

A busca de ausencia tem forma fixa: procura-se o termo, e procura-se um termo de
controle que TEM de aparecer, porque zero de busca quebrada tem a mesma cara de
zero de coisa inexistente. Forma fixa cabe em programa, e vinte buscas cabem numa
chamada.

O QUE ELE DECIDE, e o que ele nao decide

    achou / nao achou      informa, com os localizadores.
    CONTROLE FALHOU        ACUSA. O termo de controle nao apareceu, e entao a
                           busca esta quebrada e o resultado do termo principal
                           nao vale nada. E o unico veredito do programa.

Ele nao decide se a ausencia importa. Isso e de quem le.

COMO ESCREVER O LOTE

Um arquivo de texto, uma busca por linha, o termo e o controle separados por `|`:

    aposentadoria | ministro
    pedido de destaque | destaque
    composicao do tribunal | tribunal

O controle e um termo mais largo que o principal, que a mesma busca TEM de achar.
Sem controle a linha roda, e a saida diz que ela rodou sem controle.

Uso:
    python scripts/buscar_lote.py <extracao.txt> <lote.txt>
    python scripts/buscar_lote.py <extracao.txt> --termos "aposentad|ministr" "IRDR|recurso"
    python scripts/buscar_lote.py <extracao.txt> <lote.txt> --contexto 90
"""
import argparse
import io
import re
import sys
import unicodedata
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def sem_acento(t):
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c))


def normal(t):
    """Caixa e acento fora. E o que faz a busca achar o que o grep deste ambiente perde."""
    return sem_acento(t).lower()


def paragrafos(caminho):
    """Le as duas escritas de extracao: `[P12] texto` e `[trab] P12 [TIPO] (p.3) texto`."""
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    fora = {}
    for m in re.finditer(r"^\W{0,4}\[P(\d+)\]\s*(.*)$", t, re.M):
        fora[int(m.group(1))] = m.group(2)
    if not fora:
        for m in re.finditer(r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\])?\s*(?:\(p\.[^)]*\))?\s*(.*)$",
                             t, re.M):
            fora[int(m.group(1))] = m.group(2)
    return fora


def procurar(ps, termo):
    """Devolve os numeros de paragrafo em que o termo ocorre, e o total de ocorrencias."""
    alvo = normal(termo)
    achados, total = [], 0
    for n in sorted(ps):
        c = normal(ps[n]).count(alvo)
        if c:
            achados.append(n)
            total += c
    return achados, total


def ler_lote(caminho):
    linhas = []
    for bruta in io.open(caminho, encoding="utf-8", errors="replace"):
        bruta = bruta.strip()
        if not bruta or bruta.startswith("#"):
            continue
        if "|" in bruta:
            a, b = bruta.split("|", 1)
            linhas.append((a.strip(), b.strip()))
        else:
            linhas.append((bruta, None))
    return linhas


def autoteste():
    """Prova a busca antes de usa-la, com os defeitos deste ambiente na mira."""
    fonte = ("[P1] O ministro pediu aposentadoria em 2021, e a Corte mudou.\n"
             "\n[P2] A INSEGURANCA juridica aparece aqui, e nao a outra palavra.\n"
             "\n[P3] Uma tabela com 22, 12 e 34 casos julgados.\n")
    tmp = Path(__file__).resolve().parent / "_lote_autoteste.txt"
    tmp.write_text(fonte, encoding="utf-8")
    try:
        ps = paragrafos(str(tmp))
        falhas = []
        if len(ps) != 3:
            falhas.append("nao leu os tres paragrafos: %r" % sorted(ps))
        # acento: a busca sem acento acha a palavra acentuada
        if procurar(ps, "aposentadoria")[0] != [1]:
            falhas.append("nao acha palavra acentuada quando o termo vem sem acento")
        # caixa: o termo minusculo acha o texto em maiuscula
        if procurar(ps, "inseguranca")[0] != [2]:
            falhas.append("nao acha texto em caixa alta")
        # dentro de palavra: "seguranca" esta dentro de "INSEGURANCA" e tem de aparecer
        if procurar(ps, "seguranca")[0] != [2]:
            falhas.append("nao acha o termo dentro de outra palavra, "
                          "que e o defeito que ja escondeu ocorrencia real")
        # controle negativo: o que nao existe devolve vazio
        if procurar(ps, "plenario virtual")[0]:
            falhas.append("acha o que nao esta la")
        return falhas
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("extracao")
    ap.add_argument("lote", nargs="?", help="arquivo com uma busca por linha, `termo | controle`")
    ap.add_argument("--termos", nargs="+", help="as buscas na linha de comando, no mesmo formato")
    ap.add_argument("--contexto", type=int, default=0,
                    help="imprime N caracteres em torno da primeira ocorrencia")
    ap.add_argument("--max-loc", type=int, default=12,
                    help="quantos localizadores imprimir por busca (padrao 12)")
    a = ap.parse_args()

    falhas = autoteste()
    if falhas:
        print("  o proprio buscador esta quebrado, e nao reporto nada:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste: acha palavra acentuada e em caixa alta, acha termo dentro de "
          "outra palavra, e nao acha o que nao esta la")

    ps = paragrafos(a.extracao)
    if not ps:
        print("  nao reconheci nenhum paragrafo em %s" % a.extracao)
        return 2
    print("  %s: %d paragrafos, de P%d a P%d\n"
          % (Path(a.extracao).name, len(ps), min(ps), max(ps)))

    if a.lote:
        buscas = ler_lote(a.lote)
    elif a.termos:
        buscas = []
        for t in a.termos:
            if "|" in t:
                x, y = t.split("|", 1)
                buscas.append((x.strip(), y.strip()))
            else:
                buscas.append((t.strip(), None))
    else:
        print("  nada a buscar: passe um arquivo de lote ou --termos")
        return 2

    quebradas = 0
    for termo, controle in buscas:
        achados, total = procurar(ps, termo)
        loc = ", ".join("[P%d]" % n for n in achados[:a.max_loc])
        if len(achados) > a.max_loc:
            loc += " ... (+%d)" % (len(achados) - a.max_loc)
        print("  %-42s %3d ocorrencia(s) em %3d paragrafo(s)"
              % (termo, total, len(achados)))
        if achados:
            print("      %s" % loc)
        if a.contexto and achados:
            t = ps[achados[0]]
            i = normal(t).find(normal(termo))
            print("      ...%s..." % re.sub(
                r"\s+", " ", t[max(0, i - a.contexto):i + a.contexto]))
        if controle:
            ca, ct = procurar(ps, controle)
            if ca:
                print("      controle %r: %d ocorrencia(s) em %d paragrafo(s), a busca funciona"
                      % (controle, ct, len(ca)))
            else:
                quebradas += 1
                print("      *** CONTROLE FALHOU: %r tambem devolve zero." % controle)
                print("          A busca esta quebrada, e o zero acima nao vale nada.")
        else:
            print("      (sem controle: o zero desta linha nao se distingue de busca quebrada)")
        print()

    print("  %d busca(s), %d com controle, %d com o controle falhando"
          % (len(buscas), sum(1 for _, c in buscas if c), quebradas))
    return 1 if quebradas else 0


if __name__ == "__main__":
    sys.exit(main())

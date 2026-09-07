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
    """Le as duas escritas de extracao, e le TAMBEM as notas de rodape.

    A nota de rodape nao tem numero de paragrafo: a extracao a escreve como
    `[nota 12] texto`. Toda busca indexada por `[P###]` a ignorava, e o zero que
    ela devolvia tinha a mesma cara do zero de coisa inexistente. Medido em
    06/09/2026: uma leitura afirmou que dois autores nao eram citados no trabalho,
    com termo de controle passando, e os dois estao na nota 12; a consequencia do
    item foi construida sobre a ausencia falsa.

    As notas entram com chave negativa (-12 para a nota 12), de modo que a saida
    as distingue do paragrafo e nada as confunde com ele.
    """
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    fora = {}
    for m in re.finditer(r"^\W{0,4}\[P(\d+)\]\s*(.*)$", t, re.M):
        fora[int(m.group(1))] = m.group(2)
    if not fora:
        for m in re.finditer(r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\])?\s*(?:\(p\.[^)]*\))?\s*(.*)$",
                             t, re.M):
            fora[int(m.group(1))] = m.group(2)
    # A nota so conta quando ABRE a linha, que e como a extracao grava o bloco de
    # notas ao fim do arquivo. O mesmo `[nota 29]` aparece no meio do paragrafo
    # como chamada, e ali ele nao introduz texto de nota nenhum: introduz a
    # continuacao do proprio paragrafo.
    #
    # Medido em 07/09/2026, e quem achou foi uma leitura, nao um teste meu. A
    # versao anterior casava a chamada inline e indexava o resto do paragrafo
    # como se fosse a nota, de modo que aquele texto era contado DUAS vezes: uma
    # sob [P###] e outra sob a nota. Cinco contagens de controle entraram
    # infladas num relatorio, e uma delas levou a leitura a atribuir a uma nota
    # conteudo que estava no corpo. O defeito infla e nao zera, entao as
    # afirmacoes de ausencia daquele relatorio continuam de pe.
    for m in re.finditer(r"(?m)^\W{0,4}\[nota (\d+)\]\s*(.*)$", t):
        n = -int(m.group(1))
        fora[n] = fora.get(n, "") + " " + m.group(2)
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
             "\n[P3] Uma tabela com 22, 12 e 34 casos julgados.\n"
             "\n[P4] alfa bravo[nota 9] charlie delta.\n"
             "\n[nota 12] Cf. Nino, 2003; Zurn, 2007.\n")
    tmp = Path(__file__).resolve().parent / "_lote_autoteste.txt"
    tmp.write_text(fonte, encoding="utf-8")
    try:
        ps = paragrafos(str(tmp))
        falhas = []
        if sorted(k for k in ps if k > 0) != [1, 2, 3, 4]:
            falhas.append("nao leu os tres paragrafos: %r" % sorted(ps))
        if -12 not in ps:
            falhas.append("nao leu a nota de rodape")
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
        # a nota de rodape tem de ser alcancada, e vir marcada como nota
        if procurar(ps, "zurn")[0] != [-12]:
            falhas.append("nao acha o que so esta na nota de rodape: %r"
                          % (procurar(ps, "zurn")[0],))
        # CONTAGEM EM DOBRO: a chamada `[nota 9]` no meio do paragrafo nao abre
        # nota nenhuma, e o que vem depois dela e o proprio paragrafo. Contar
        # aquilo duas vezes inflou cinco controles num relatorio de 07/09/2026.
        if procurar(ps, "charlie") != ([4], 1):
            falhas.append("conta em dobro o texto que segue a chamada de nota "
                          "no meio do paragrafo: %r" % (procurar(ps, "charlie"),))
        if procurar(ps, "bravo") != ([4], 1):
            falhas.append("perde a palavra colada na chamada de nota: %r"
                          % (procurar(ps, "bravo"),))
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
          "outra palavra, alcanca a nota de rodape, e nao acha o que nao esta la")

    ps = paragrafos(a.extracao)
    if not ps:
        print("  nao reconheci nenhum paragrafo em %s" % a.extracao)
        return 2
    pos = [k for k in ps if k > 0]
    notas = [k for k in ps if k < 0]
    print("  %s: %d paragrafos, de P%d a P%d, mais %d nota(s) de rodape\n"
          % (Path(a.extracao).name, len(pos), min(pos), max(pos), len(notas)))

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
        loc = ", ".join(("[nota %d]" % -n) if n < 0 else ("[P%d]" % n)
                        for n in achados[:a.max_loc])
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

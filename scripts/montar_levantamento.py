# -*- coding: utf-8 -*-
"""Junta as quatro leituras num levantamento so, sem que os codigos colidam.

POR QUE ISTO EXISTE

O passo 5 do Luis confere o levantamento, que e a soma das quatro leituras. As
quatro sao independentes e escolhem os proprios prefixos, de modo que colidem: em
08/09/2026, sobre a dissertacao R, `C1` a `C6` e `H1` a `H3` existiam nos
passos 3 e 4 ao mesmo tempo. Concatenar sem tratar isso **descarta nove itens**,
porque quem le fica com a primeira ocorrencia de cada codigo e nao ve a segunda.

Ate 08/09 essa juncao era feita a mao, e a renumeracao tambem. Feito a mao, o erro
nao aparece: a contagem sai certa e o conteudo some, que e a forma de defeito que
nenhuma conferencia posterior apanha.

O QUE ELE DECIDE

    codigo repetido entre leituras   RENUMERA o da leitura posterior, com letra
                                     livre, e imprime o de-para.
    codigo repetido dentro de uma    ACUSA e para. Duas coisas com o mesmo nome
                                     na mesma leitura e defeito da leitura, e
                                     renumerar esconderia.

Nao le o conteudo dos itens e nao julga nenhum. Junta e desambigua.

Uso:
    python scripts/montar_levantamento.py LEITURA-1.md LEITURA-2.md ... -o LEVANTAMENTO.md
"""
import argparse
import collections
import io
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# As tres escritas de item que o acervo usa, e elas convivem no mesmo arquivo.
# As leituras escrevem o codigo de varios modos, e um programa que leia so um
# deles descarta itens em silencio. Medido em 08/09/2026 sobre as quatro leituras
# do trabalho R: a leitura 1 escreve `| AC01` dentro de tabela, a 2 escreve `## PR-1`
# e a 3 `### C-1`, com hifen. Um padrao sem hifen e sem celula achou 40 codigos
# onde havia 169, e a contagem saiu certa com o conteudo faltando, que e a forma
# de erro que nenhuma conferencia posterior apanha.
# E A REMISSAO EM NEGRITO NAO E DEFINICAO DE ITEM.
#
# Uma leitura escreve, no meio da prosa, `**A1, A2 e A3 terminam em FONTE onde
# precisariam de DADO**`. Isso comeca por `**` seguido de codigo e casava o
# padrao, de modo que o programa acusava A1, A3, A4 e A5 como repetidos dentro
# da mesma leitura e se recusava a montar. Medido em 09/09/2026: os quatro
# estavam definidos uma vez so, numa tabela, e as outras ocorrencias eram
# remissoes. Contagem certa com conteudo errado, outra vez.
#
# O que separa, e vale nas tres escritas: **depois do codigo, a definicao traz um
# SEPARADOR** (ponto, travessao, dois-pontos, ponto medio, celula de tabela, fim
# do negrito ou fim da linha); a remissao emenda uma PALAVRA — `**A3 contem, alem
# disso, ...**`. Exigir o separador resolve os dois casos sem alargar mais nada.
# E a exigencia do separador vale SO na escrita em negrito. Cabecalho e celula de
# tabela podem trazer `## PR-2 dois`, com o titulo emendado por espaco, e ali nao
# ha ambiguidade: prosa nao comeca com `## `. Em `**`, ha, porque frase em negrito
# no meio do texto comeca do mesmo jeito.
RE_ITEM = re.compile(
    r"(?m)^(?:"
    r"(?:\|[ \t]*|#{2,5}[ \t]*\**[ \t]*)([A-Z]{1,2})-?(\d+)\b"
    r"|"
    r"\*\*([A-Z]{1,2})-?(\d+)\b[ \t]*(?=[.:|—–·*]|$)"
    r")")


def cod(m):
    """O codigo canonico, sem o hifen com que algumas leituras o escrevem.

    O padrao tem dois ramos (cabecalho/tabela e negrito), e so um casa por vez:
    os grupos do outro vem `None`.
    """
    letra = m.group(1) or m.group(3)
    numero = m.group(2) or m.group(4)
    return letra + numero

LETRAS = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def codigos(texto):
    """Os codigos que ABREM item, na ordem, sem repetir."""
    fora = []
    for m in RE_ITEM.finditer(texto):
        c = cod(m)
        if c not in fora:
            fora.append(c)
    return fora


def prefixos_livres(usados):
    """Letras de uma e de duas posicoes que ninguem esta usando."""
    for a in LETRAS:
        if a not in usados:
            yield a
    for a in LETRAS:
        for b in LETRAS:
            if a + b not in usados:
                yield a + b


def renomear(texto, de, para):
    """Troca o prefixo em toda ocorrencia do codigo, e so quando ele e codigo.

    A fronteira de palavra dos dois lados evita trocar `C1` dentro de `AC12` e
    dentro de `C10`, que sao codigos diferentes.
    """
    return re.sub(r"\b%s(\d+)\b" % re.escape(de),
                  lambda m: "%s%s" % (para, m.group(1)), texto)


def autoteste():
    """Prova a juncao antes de usa-la. Sem controle, o silencio nao informa."""
    falhas = []
    a = "**C1.** um\n\n**C2.** dois\n\n**H1.** tres\n"
    b = "**C1.** quatro\n\n**D1.** cinco\n"
    ca, cb = codigos(a), codigos(b)
    if ca != ["C1", "C2", "H1"]:
        falhas.append("nao le os codigos da primeira leitura: %r" % ca)
    if cb != ["C1", "D1"]:
        falhas.append("nao le os codigos da segunda: %r" % cb)
    # CONTROLE POSITIVO da colisao: C1 esta nas duas e tem de ser vista
    if not (set(ca) & set(cb)):
        falhas.append("nao ve a colisao que existe entre as duas leituras")
    # A troca e sempre por PREFIXO DE LETRAS, que e o que o chamador extrai com
    # `re.match(r"[A-Z]+", ...)`. Testar com "C1" no lugar de "C" testa o que o
    # programa nunca faz, e foi assim que este autoteste reprovou a si mesmo em
    # 08/09/2026.
    t = renomear("**C1.** x AC12 y C10 z C1 w", "C", "G")
    if "AC12" not in t:
        falhas.append("a troca de prefixo entra em codigo de outra serie: %r" % t)
    if "G10" not in t or "G1 " not in t + " ":
        falhas.append("a troca de prefixo nao alcanca todos os numeros: %r" % t)
    # repetido DENTRO de uma leitura tem de ser visto pelo chamador
    dentro = collections.Counter(cod(m) for m in RE_ITEM.finditer("**C1.** a\n\n**C1.** b\n"))
    if dentro["C1"] != 2:
        falhas.append("nao conta a repeticao dentro da mesma leitura")
    # AS TRES ESCRITAS QUE AS LEITURAS USAM DE FATO, e um padrao que leia so uma
    # delas descarta item em silencio.
    tres = codigos("**C1.** um\n\n## PR-2 dois\n\n| AC01 | numa tabela |\n")
    if tres != ["C1", "PR2", "AC01"]:
        falhas.append("nao le as tres escritas de codigo das leituras: %r" % tres)
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("leituras", nargs="+")
    ap.add_argument("-o", "--saida", required=True)
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio montador esta quebrado, e nao junto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: le as tres escritas de codigo, ve a colisao entre leituras, "
          "conta a repeticao dentro de uma, e a troca de prefixo nao alcanca codigo vizinho")

    textos, nomes = [], []
    for p in a.leituras:
        textos.append(io.open(p, encoding="utf-8", errors="replace").read())
        nomes.append(Path(p).name)

    # repetido DENTRO de uma leitura para tudo: renumerar esconderia defeito dela
    parou = False
    for nome, t in zip(nomes, textos):
        c = collections.Counter(cod(m) for m in RE_ITEM.finditer(t))
        rep = [k for k, v in c.items() if v > 1]
        if rep:
            parou = True
            print("\n  CODIGO REPETIDO DENTRO DE %s: %s" % (nome, ", ".join(sorted(rep))))
    if parou:
        print("\n  Duas coisas com o mesmo nome na mesma leitura e defeito dela.")
        print("  Corrija na origem: renumerar aqui esconderia o defeito.")
        return 2

    vistos, trocas, partes = set(), [], []
    for nome, t in zip(nomes, textos):
        meus = codigos(t)
        pref = collections.defaultdict(list)
        for c in meus:
            pref[re.match(r"[A-Z]+", c).group(0)].append(c)
        for p in sorted(pref):
            if any(c in vistos for c in pref[p]):
                novo = next(x for x in prefixos_livres(
                    {re.match(r"[A-Z]+", v).group(0) for v in vistos} |
                    {re.match(r"[A-Z]+", v).group(0) for v in meus}))
                t = renomear(t, p, novo)
                trocas.append((nome, p, novo, len(pref[p])))
                pref[novo] = [novo + re.sub(r"\D", "", c) for c in pref[p]]
                del pref[p]
        for p in pref:
            vistos.update(pref[p])
        partes.append("\n\n# LEVANTAMENTO — %s\n\n%s" % (nome, t))

    saida = "\n".join(partes)
    io.open(a.saida, "w", encoding="utf-8").write(saida)

    finais = codigos(saida)
    print("\n  %d leitura(s), %d itens, %d codigos distintos" % (len(nomes), len(finais), len(set(finais))))
    if trocas:
        print("\n  RENUMERADOS, para que nada se perca na juncao:")
        for nome, de, para, n in trocas:
            print("     %-46s %s -> %s  (%d itens)" % (nome[:46], de, para, n))
    else:
        print("  nenhuma colisao entre as leituras.")
    if len(finais) != len(set(finais)):
        print("\n  AINDA HA CODIGO REPETIDO na saida, e a juncao nao e confiavel.")
        return 2
    print("\n  %s" % a.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())

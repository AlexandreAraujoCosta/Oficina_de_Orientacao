# -*- coding: utf-8 -*-
"""A pre-analise: mede a forma do trabalho e diz que leitura se paga nele.

POR QUE ISTO EXISTE

Ate 05/09/2026 a escolha entre as leituras era do gosto de quem rodava, e o
custo so aparecia depois. Medido nesse dia, sobre a mesma dissertacao, as vias
custaram de seis a sessenta e cinco reais e de oito minutos a uma hora e meia,
e a diferenca de achado entre elas NAO seguiu a diferenca de preco: o chat em
modelo grande devolveu 24 correcoes em 11 minutos, e o agente no mesmo modelo
devolveu 18 em 53. O que separou 3 de 24 foi o modelo, e nao a via.

Esta pre-analise nao usa modelo nenhum. Ela conta o que a extracao ja tem, e a
recomendacao sai desses numeros, escritos ao lado dela para quem discordar ter
de que discordar.

O QUE ELA NAO SABE

Ela conta figura, tabela, numero e tamanho. Nao le argumento, nao sabe se a
pesquisa e boa, e nao sabe o que o orientador ja viu sozinho. A recomendacao e
sobre onde cada leitura tem material para trabalhar, e nao sobre qualidade.

Uso:
    python scripts/recomendar_via.py extracao/<trabalho>.txt
    python scripts/recomendar_via.py --autoteste
"""
import argparse
import io
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------- os precos
#
# Tabela de 24/06/2026, por milhao de tokens, e a cotacao de 05/09/2026.
# ATUALIZE AS TRES LINHAS QUANDO O PRECO MUDAR: um custo velho apresentado como
# atual e pior que nenhum custo, porque decide compra.
PRECO = {"grande": (5.0, 25.0), "pequeno": (3.0, 15.0)}   # (entrada, saida) USD
DOLAR = 5.12
# Os relatorios devolvem o total de tokens sem separar entrada de saida, e a
# saida custa cinco vezes mais. 8% e o perfil medido das leituras agenticas
# desta bancada. O numero que sai daqui e TETO: a memoria de contexto barateia
# a entrada repetida e isso nao esta descontado.
FATIA_SAIDA = 0.08


def reais(tokens, porte="grande"):
    entrada, saida = PRECO[porte]
    usd = (tokens * (1 - FATIA_SAIDA) * entrada
           + tokens * FATIA_SAIDA * saida) / 1e6
    return usd * DOLAR


# ------------------------------------------------------- as vias, medidas
#
# Cada linha e uma rodada REAL sobre a MESMA dissertacao (35.708 palavras, 63
# figuras), em 05/09/2026, e o que foi medido vai junto, para que ninguem leia
# como promessa o que e uma observacao. Tempo em minutos; `itens` sao as
# correcoes de conteudo, sem as de superficie.
#
# AS VIAS QUE NAO ESTAO AQUI, e a ausencia delas e resultado. As duas
# configuracoes em modelo pequeno foram medidas e saem do cardapio: acharam 3 e
# 7 correcoes contra 18 e 24 das mesmas configuracoes em modelo grande, e
# custaram quase o mesmo. E a via de chat sai por outra razao, que nao e de
# cobertura: sem programa, ela publicou duas afirmacoes de ausencia falsas como
# pontos fortes, negando um vocabulario que ocorre 36 vezes e dando por fechada
# uma contagem que soma 14 numa populacao de 15. Erro de ausencia manda o autor
# nao fazer nada, e e o mais caro que um relatorio pode ter.
VIAS = [
    dict(nome="Passada unica, sem programas", tokens=306287, minutos=13,
         porte="grande", itens=18, docx=True,
         medida="uma leitura, sem programa e sem revisao, 22 paginas de figura"),
    dict(nome="Alberto no agente, completo", tokens=441000, minutos=53,
         porte="grande", itens=18, docx=True,
         medida="a mesma, com programas, figuras e busca externa"),
    dict(nome="Luis completo", tokens=1699617, minutos=99,
         porte="grande", itens=19, docx=True,
         medida="quatro leituras, verificacao e triagem por vozes separadas"),
]


# --------------------------------------------------------- medir o trabalho
RE_VELHO = re.compile(r"^\[[^\]]+\]\s+P(\d+)(?:\s+\[[A-Z_]+\])?"
                      r"\s+\(p\.(\d+)\)\s*(.*)$", re.M)
RE_NOVO = re.compile(r"\[P(\d+)\]\s*(.*?)(?=\n[ \t]*\n|\Z)", re.S)
RE_LEGENDA = re.compile(r"^(?:\d{1,3}\s+)?(Quadro|Tabela|Gr[áa]fico|Figura|Imagem)"
                        r"\s*(\d+)", re.I)
# numero com casa decimal ou percentual: e o que uma leitura de dados confere
RE_NUMERO = re.compile(r"\d+[.,]\d+\s*%|\d+\s*%|\b\d{1,3}(?:\.\d{3})+\b")


def medir(caminho):
    bruto = io.open(caminho, encoding="utf-8", errors="replace").read()
    pares = [(int(n), " ".join(t.split()))
             for n, _p, t in RE_VELHO.findall(bruto)]
    if not pares:
        pares = [(int(n), " ".join(t.split())) for n, t in RE_NOVO.findall(bruto)]
    if not pares:
        sys.exit("nao reconheco a forma desta extracao: %s" % caminho)
    palavras = sum(len(t.split()) for _n, t in pares)
    figuras, tabelas, onde = set(), set(), []
    # SEM LIMITE DE COMPRIMENTO AQUI, e isto e conserto de 05/09/2026: o mapa
    # descarta legenda longa porque quer texto curto, e este programa quer
    # CONTAR peca. Com o limite, uma dissertacao com nove tabelas aparecia com
    # cinco, porque as quatro maiores trazem o conteudo colado na legenda.
    for i, (n, t) in enumerate(pares):
        m = RE_LEGENDA.match(t)
        if m:
            (tabelas if m.group(1).lower().startswith(("tabela", "quadro"))
             else figuras).add(int(m.group(2)))
            onde.append(i)
    # A PECA QUE OCUPA MUITOS PARAGRAFOS e a base reconstituivel, e contar peca
    # nao a enxerga: numa dissertacao de nove tabelas, uma delas ocupa 174
    # paragrafos e carrega o corpus inteiro, caso a caso. E sobre ela que a
    # travessia dos dados trabalha, e por isso ela decide a recomendacao tanto
    # quanto o numero de figuras.
    # So os vaos ENTRE duas legendas. O vao final e o que vem depois da ultima
    # peca, que costuma ser referencia e apendice, e contá-lo faria toda
    # dissertacao com apendice parecer ter uma tabela gigante.
    maior = 0
    for a, b in zip(onde, onde[1:]):
        maior = max(maior, b - a - 1)
    numeros = sum(1 for _n, t in pares if RE_NUMERO.search(t))
    return dict(paragrafos=len(pares), palavras=palavras,
                figuras=len(figuras), tabelas=len(tabelas), com_numero=numeros,
                maior_peca=maior)


# ------------------------------------------------------------ a recomendacao
def recomendar(m):
    """(via recomendada, razao, o que se perde na via mais curta).

    O CRITERIO vem de medicao, e nao de gosto.

    O que a leitura longa tem e as curtas nao tem e a travessia das figuras e
    a aritmetica refeita sobre elas. Numa leitura medida, nove de dezessete
    achados dependiam de ver a imagem. Onde nao ha figura nem numero, essa
    travessia nao tem material, e a leitura longa gasta o dobro para chegar
    perto do mesmo lugar.
    """
    pecas = m["figuras"] + m["tabelas"]
    base = m.get("maior_peca", 0) >= 50
    denso = m["com_numero"] >= 40 and (pecas >= 15 or base)
    medio = pecas >= 6 or m["com_numero"] >= 20
    if denso:
        razao = ("%d figuras e tabelas e %d parágrafos com número ou percentual"
                 % (pecas, m["com_numero"]))
        if base:
            razao += (", e uma peça que ocupa %d parágrafos, o que é corpus "
                      "reproduzido caso a caso" % m["maior_peca"])
        return ("Luis completo",
                razao + ": há material para a travessia dos dados, que é o que "
                "a leitura longa tem e as curtas não têm.",
                "a conferência das figuras contra a prosa, a aritmética refeita "
                "e a busca do que já está publicado")
    if medio:
        return ("Alberto no agente, completo",
                "%d figuras e tabelas e %d parágrafos com número: há o que "
                "conferir, e não o bastante para quatro travessias."
                % (pecas, m["com_numero"]),
                "a verificação por voz que não levantou, e a busca externa")
    return ("Passada unica, sem programas",
            "%d figuras e tabelas e %d parágrafos com número: a travessia dos "
            "dados teria pouco material, e o que decide aqui é a leitura do "
            "argumento." % (pecas, m["com_numero"]),
            "a varredura do aparato bibliográfico, que só o programa faz, e a "
            "busca do que já está publicado")


def escrever(m, alvo=None):
    via, razao, perde = recomendar(m)
    L = ["", "=" * 68,
         "PRE-ANALISE: a forma do trabalho, e que leitura se paga nele",
         "=" * 68, ""]
    L.append("  %d parágrafos, %d palavras, %d figuras, %d tabelas,"
             % (m["paragrafos"], m["palavras"], m["figuras"], m["tabelas"]))
    L.append("  %d parágrafos com número ou percentual." % m["com_numero"])
    L.append("")
    L.append("  RECOMENDADO: %s" % via)
    for linha in _quebrar(razao, 62):
        L.append("    " + linha)
    L.append("")
    L.append("  Escolhendo uma via mais curta, o que fica de fora é")
    for linha in _quebrar(perde + ".", 62):
        L.append("    " + linha)
    L.append("")
    L.append("  O que cada via custou, medido em 05/09/2026:")
    L.append("")
    L.append("    %-38s %5s %9s %8s" % ("", "min", "tokens", "R$"))
    for v in VIAS:
        L.append("    %-38s %5d %9s %8.2f%s"
                 % (v["nome"], v["minutos"],
                    "{:,}".format(v["tokens"]).replace(",", "."),
                    reais(v["tokens"], v["porte"]),
                    "  <--" if v["nome"] == via else ""))
    L.append("")
    L.append("  O preço é teto: a memória de contexto barateia a entrada")
    L.append("  repetida, e isso não está descontado. O tempo é de relógio.")
    L.append("")
    L.append("  A MEDIDA MAIOR DO DIA decide mais que a via. O mesmo")
    L.append("  pedido, na mesma via de chat, devolveu 3 correções em")
    L.append("  modelo pequeno e 24 em modelo grande. No agente, 7 contra 18.")
    L.append("  Escolher o modelo pequeno")
    L.append("  economiza pouco e é onde se perde o achado que ninguém mais viu.")
    L.append("")
    L.append("  Esta pré-análise conta figura, tabela, número e tamanho. Não lê")
    L.append("  argumento e não sabe o que você já viu sozinho: ela diz onde")
    L.append("  cada leitura tem material, e não o que o trabalho vale.")
    L.append("")
    return "\n".join(L)


def _quebrar(texto, largura):
    fora, linha = [], ""
    for p in texto.split():
        if len(linha) + len(p) + 1 > largura:
            fora.append(linha)
            linha = p
        else:
            linha = (linha + " " + p).strip()
    if linha:
        fora.append(linha)
    return fora


CONTROLE_DENSO = "\n\n".join(
    ["[t] P%d (p.%d) Gráfico %d - Uma legenda qualquer" % (i, i, i)
     for i in range(1, 21)]
    + ["[t] P%d (p.%d) A taxa foi de 63,1%% contra 10,5%% no outro grupo, e o "
       "total chegou a 2.928 casos no periodo examinado." % (i, i)
       for i in range(21, 101)])

CONTROLE_MAGRO = "\n\n".join(
    ["[t] P%d (p.%d) Um parágrafo de prosa sobre a doutrina, sem número nenhum, "
     "que existe para o texto ter corpo." % (i, i) for i in range(1, 61)])


def autoteste():
    import tempfile
    d = Path(tempfile.mkdtemp())
    denso = d / "controle_denso.txt"
    denso.write_text(CONTROLE_DENSO, encoding="utf-8")
    m = medir(str(denso))
    if m["figuras"] != 20:
        sys.exit("!! contei %d figuras onde ha 20" % m["figuras"])
    if m["com_numero"] < 80:
        sys.exit("!! contei %d paragrafos com numero onde ha 80" % m["com_numero"])
    if recomendar(m)[0] != "Luis completo":
        sys.exit("!! o trabalho denso nao foi para a leitura longa: %r"
                 % (recomendar(m)[0],))

    magro = d / "controle_magro.txt"
    magro.write_text(CONTROLE_MAGRO, encoding="utf-8")
    m2 = medir(str(magro))
    if m2["figuras"] or m2["tabelas"]:
        sys.exit("!! achei figura onde nao ha: %r" % m2)
    if m2["maior_peca"] != 0:
        sys.exit("!! sem peca nenhuma, a maior peca tem de ser zero: %r" % m2)
    if "Passada unica" not in recomendar(m2)[0]:
        sys.exit("!! o trabalho sem dado nao foi para a via curta: %r"
                 % (recomendar(m2)[0],))

    # a legenda precedida do numero de pagina, que ja escondeu uma tabela real
    uma = d / "controle_pagina.txt"
    uma.write_text("[t] P1 (p.98) 98 Tabela 6 - Indicação das ocorrências",
                   encoding="utf-8")
    if medir(str(uma))["tabelas"] != 1:
        sys.exit("!! a legenda com o numero de pagina colado nao foi contada")

    # A BASE RECONSTITUIVEL: poucas pecas, e uma delas com o corpus dentro.
    # Sem esta regra, uma dissertacao cuja tabela unica ocupa 174 paragrafos
    # ia para a leitura media, e a travessia dos dados e justamente o que ela
    # pedia. Medido em 05/09/2026.
    corpus = d / "controle_corpus.txt"
    corpus.write_text("\n\n".join(
        ["[t] P1 (p.1) Tabela 1 - Uma legenda"]
        + ["[t] P%d (p.%d) 12 34 56 7,8%% 90" % (i, i) for i in range(2, 82)]
        + ["[t] P90 (p.90) Tabela 2 - Outra legenda"]), encoding="utf-8")
    mc = medir(str(corpus))
    if mc["maior_peca"] < 50:
        sys.exit("!! a peca de 80 paragrafos nao foi medida: %r" % mc)
    if recomendar(mc)[0] != "Luis completo":
        sys.exit("!! o corpus reproduzido nao foi para a leitura longa: %r"
                 % (recomendar(mc)[0],))

    # e o preco, que tem de subir com o modelo
    if not reais(1e6, "grande") > reais(1e6, "pequeno") > 0:
        sys.exit("!! a conta de preco esta invertida")
    print("  autoteste da pre-analise: conta as 20 figuras do controle denso e "
          "manda para a leitura longa; nao acha figura no controle magro e "
          "manda para a curta; conta a legenda escondida pelo numero de "
          "pagina; e o preco do modelo grande e maior que o do pequeno.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("extracao", nargs="?")
    ap.add_argument("--autoteste", action="store_true")
    a = ap.parse_args()
    autoteste()
    if a.autoteste:
        return 0
    if not a.extracao:
        sys.exit("falta a extracao. Uso: recomendar_via.py extracao/<nome>.txt")
    print(escrever(medir(a.extracao)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Acha transcricao literal do trabalho dentro do relatorio, com ou sem aspas.

POR QUE ISTO EXISTE, E POR QUE O CONFERIDOR ANTERIOR NAO BASTAVA

`conferir_citacoes.py` confere se o que esta ENTRE ASPAS existe na fonte. Ele
apanha a citacao inventada e nao apanha o oposto, que e o defeito que esta
oficina proibe desde o primeiro dia: **o trecho copiado do trabalho e apresentado
como prosa de quem escreve o relatorio**. Sem aspas, o leitor nao distingue a
palavra da autora da parafrase do leitor, e a promessa de que o relatorio nao
transcreve fica falsa sem que nada acuse.

Medido em 05/09/2026: um relatorio declarava, na segunda pagina, que nenhuma
passagem da dissertacao aparecia transcrita nele. Tinha zero aspas e vinte e duas
sequencias identicas a dissertacao, catorze delas prosa da autora, uma com
dezoito palavras. Quem achou foi um cotejo por voz separada, comparando n-gramas.
Nenhum programa da cadeia olhava para isso.

COMO ELE DECIDE, E O QUE ELE NAO SABE

Compara janelas de N palavras normalizadas (sem acento, sem pontuacao, sem caixa)
do relatorio contra o conjunto das janelas do trabalho. Janela que aparece nos
dois e transcricao literal.

Ele **nao sabe** distinguir prosa da autora de designacao tecnica: "controle
concentrado de constitucionalidade" e do campo e nao e transcricao, e vai casar.
Por isso a saida e uma lista para julgar, e nao um veredicto, e por isso ha uma
lista de expressoes que nao contam. O numero que importa nao e quantas casaram, e
sim quantas sobram depois do julgamento.

Uso:
    python scripts/conferir_transcricao.py RELATORIO.md extracao/trabalho.txt
    python scripts/conferir_transcricao.py RELATORIO.md extracao/trabalho.txt -n 8
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

# A janela de 7 palavras e o limiar em que a coincidencia deixa de ser acaso da
# lingua. Com 5, "de acordo com o que o trabalho" casa em qualquer texto; com 10,
# a transcricao curta escapa. Ajustavel pelo -n.
JANELA = 7

# O que casa por ser do campo, e nao por ter sido copiado. A lista e curta de
# proposito: o julgamento e de quem le, e uma lista grande esconderia achado.
DO_CAMPO = [
    "controle concentrado de constitucionalidade",
    "supremo tribunal federal",
    "recurso extraordinario com agravo",
    "repercussao geral",
]


def normal(t):
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def palavras(t):
    return normal(t).split()


def janelas(ps, n):
    return {" ".join(ps[i:i + n]) for i in range(len(ps) - n + 1)}


def limpar_relatorio(t):
    """Tira do relatorio o que nao e prosa dele: codigo, localizador, tabela."""
    t = re.sub(r"```.*?```", " ", t, flags=re.S)      # bloco de codigo
    t = re.sub(r"`[^`]*`", " ", t)                     # codigo em linha
    t = re.sub(r"\[P\d+\]", " ", t)                    # localizador
    t = re.sub(r"^\s*\|.*$", " ", t, flags=re.M)       # linha de tabela
    t = re.sub(r"^\s*>.*$", " ", t, flags=re.M)        # citacao em bloco
    return t


def achar(relatorio, fonte, n=JANELA):
    rp = palavras(limpar_relatorio(relatorio))
    fj = janelas(palavras(fonte), n)
    fora, i = [], 0
    while i <= len(rp) - n:
        j = " ".join(rp[i:i + n])
        if j in fj:
            # estende enquanto continuar batendo, para dar a sequencia inteira
            fim = i + n
            while fim < len(rp) and " ".join(rp[fim - n + 1:fim + 1]) in fj:
                fim += 1
            fora.append(" ".join(rp[i:fim]))
            i = fim
        else:
            i += 1
    return [s for s in fora
            if not any(c in s for c in DO_CAMPO) and not so_numeros(s)]


def so_numeros(s):
    """Sequencia que e quase toda numero nao e transcricao, e sim dado.

    Uma linha de totais republicada por quem refez a conta ("22, 12, 34, 34...")
    normaliza para uma sequencia de palavras e casa com a fonte, porque os numeros
    sao os mesmos: e disso que a reconciliacao trata. Bloquear ali mandaria a
    leitura esconder a evidencia que ela produziu. O limiar e alto de proposito,
    porque prosa com dois ou tres numeros dentro continua sendo prosa.
    """
    p = s.split()
    return sum(1 for x in p if x.isdigit()) >= max(4, int(0.8 * len(p)))


CONTROLE_FONTE = (
    u"A pesquisa parte de um contexto de tensao institucional entre a expansao "
    u"da autoridade do tribunal e a resistencia dos orgaos de segunda instancia. "
    u"O efeito persuasivo de convencer o auditorio de que nao ha desobediencia "
    u"aparece em quase todas as decisoes analisadas neste trabalho."
)
CONTROLE_BOM = (
    u"O item aponta que a autora descreve um efeito de persuasao sobre quem le, "
    u"e o localizador manda abrir o paragrafo em que isso esta escrito."
)
CONTROLE_RUIM = (
    u"O trabalho sustenta que o efeito persuasivo de convencer o auditorio de "
    u"que nao ha desobediencia se repete."
)


def autoteste():
    achados = achar(CONTROLE_RUIM, CONTROLE_FONTE)
    if not achados:
        sys.exit("!! o conferidor nao acha a transcricao que esta la; nao confie nele")
    if not any("efeito persuasivo de convencer" in a for a in achados):
        sys.exit("!! achou outra coisa: %r" % achados)
    limpo = achar(CONTROLE_BOM, CONTROLE_FONTE)
    if limpo:
        sys.exit("!! acusa transcricao onde ha parafrase: %r" % limpo)
    # e o localizador nao pode virar coincidencia
    if achar(u"Ver [P12] [P13] [P14] [P15] [P16] [P17] [P18]", CONTROLE_FONTE):
        sys.exit("!! conta localizador como texto")
    # linha de totais refeita: e dado, e nao pode ser acusada
    fonte_num = u"os onze totais publicados sao 22 12 34 34 11 19 25 4 17 5 1 no fecho"
    if achar(u"recontei e os totais 22 12 34 34 11 19 25 4 17 5 1 coincidem", fonte_num):
        sys.exit("!! acusa linha de totais republicada como transcricao")
    # e a guarda dos numeros nao pode engolir prosa com numero dentro
    fonte_pr = (u"em 2020 o tribunal decidiu 125 reclamacoes e a metade delas "
                u"repetiu o mesmo argumento de sempre")
    if not achar(u"o tribunal decidiu 125 reclamacoes e a metade delas repetiu o mesmo "
                 u"argumento", fonte_pr):
        sys.exit("!! a guarda dos numeros engoliu prosa que tem numero dentro")
    print("  autoteste: acha a sequencia copiada, nao acusa a parafrase que diz o "
          "mesmo, e ignora os localizadores")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio", nargs="+")
    ap.add_argument("fonte")
    ap.add_argument("-n", "--janela", type=int, default=JANELA)
    a = ap.parse_args()
    autoteste()
    fonte = io.open(a.fonte, encoding="utf-8", errors="replace").read()
    total = 0
    for cam in a.relatorio:
        rel = io.open(cam, encoding="utf-8", errors="replace").read()
        achados = achar(rel, fonte, a.janela)
        total += len(achados)
        print("\n%s: %d sequencia(s) de %d+ palavras identicas ao trabalho"
              % (Path(cam).name, len(achados), a.janela))
        for s in sorted(achados, key=lambda x: -len(x.split())):
            print("   %2d palavras  %s" % (len(s.split()), s[:110]))
    if total:
        print("\nEstas sequencias sao IDENTICAS ao trabalho. Julgue uma a uma: "
              "designacao do campo nao e transcricao, prosa do autor e. O que "
              "sobrar tem de virar localizador, ou entrar entre aspas com a "
              "insercao feita por programa.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

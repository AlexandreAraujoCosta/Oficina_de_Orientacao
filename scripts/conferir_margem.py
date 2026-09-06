# -*- coding: utf-8 -*-
"""Acusa o item que, na margem, aponta uma coisa e nao a nomeia.

POR QUE ISTO EXISTE

O comentario que chega a margem do `.docx` e o titulo do item mais o campo
`O que fazer`. O relatorio fica noutro arquivo, e quem corrige tem so aquilo, ao
lado do paragrafo. Um item que mande *escrever a conta acima*, *percorrer a lista
acima* ou *corrigir como em S7* chega sem o acima e sem o S7.

Medido entre 05 e 06/09/2026, em cinco conferencias de compreensibilidade
seguidas, sobre cinco relatorios diferentes: cerca de trinta e cinco itens
reprovados, e a causa era a mesma em quase todos. Nao e descuido de redacao: o
campo e escrito depois da demonstracao, e quem o escreve ja tem o nome na cabeca.
Por isso vira programa em vez de lembranca.

O QUE ELE DECIDE

    remissao de posicao    ACUSA. "acima" e "abaixo", que nao existem na margem.
                           Na margem nao ha acima.
    remissao a outro item  ACUSA. "como em S7", "o problema de SC44". O outro
                           item esta noutro balao, ou em nenhum.
    contagem sem nome      AVISA. "as cinco obras", "os dois erros", "as duas
                           variaveis". Pode ser que o nome venha logo depois, e
                           por isso avisa em vez de bloquear: quem le decide.

Nao decide se o item esta certo. Decide se ele se executa sozinho.

Uso:
    python scripts/conferir_margem.py <ITENS-....md>
    python scripts/conferir_margem.py <ITENS-....md> --so-erros
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

# Remissao de posicao dentro do relatorio. "Abaixo" entra: a margem tambem nao
# tem abaixo. "A frase acima" e o caso mais frequente.
RE_POSICAO = re.compile(
    r"\b(?:a|o|as|os|da|do|das|dos|na|no|nas|nos)?\s*"
    r"(conta|lista|tabela|frase|passagem|passagens|itens?|paragrafos?|"
    r"parágrafos?|trecho|trechos|quadro|serie|série)\s+"
    r"(acima|abaixo)", re.I)
# `anterior`, `seguinte` e `a seguir` ficaram de fora, e o autoteste diz por que:
# em "trocar 20 por 19 em [P837] e reler a frase seguinte", o seguinte e do
# TRABALHO, no paragrafo que o localizador aponta, e ali a remissao resolve.
# "acima" e "abaixo" so podem ser do relatorio.
RE_POSICAO_SOLTA = re.compile(r"\b(dito acima|visto acima|logo acima|mais acima|"
                              r"como acima|indicad[ao]s? abaixo|listad[ao]s? abaixo|apontad[ao]s? abaixo)\b", re.I)

# Remissao a outro item pelo codigo.
RE_OUTRO_ITEM = re.compile(
    r"\b(?:como em|conforme|igual a|o mesmo de|o problema de|resolvido em|"
    r"junto com|ver|vide)\s+((?:S|SC|D|A|C|F)\d+)\b", re.I)

# Contagem sem nome: "as cinco obras", "os dois erros", "as tres taxas".
NUMERO = (r"dois|duas|tr[êe]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|"
          r"treze|catorze|quinze|vinte|\d{1,3}")
RE_CONTAGEM = re.compile(
    r"\b(?:as|os)\s+(?:" + NUMERO + r")\s+"
    r"([a-zà-ú]{3,20}(?:\s+[a-zà-ú]{3,20})?)", re.I)

# Onde a contagem se salva: se o campo tambem traz nome proprio, termo em
# italico, termo entre aspas ou numero de artigo, o nome provavelmente esta la.
RE_NOME = re.compile(r"\*[^*\n]{2,60}\*|[“\"][^”\"\n]{2,60}[”\"]|"
                     r"\b[A-ZÀ-Ú][a-zà-ú]{2,}\s*(?:\(\d{4}\)|,\s*\d{4})|"
                     r"\bart\.?\s*\d+", re.I)


def campos(caminho):
    """Devolve (codigo, texto que vai a margem) de cada item da lista."""
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    fora = []
    for m in re.finditer(r"^## (\w+)\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S):
        corpo = m.group(2)
        ap = re.search(r"\*\*Aponta:\*\*\s*(.*?)(?=\n\s*\n|\Z)", corpo, re.S)
        mar = re.search(r"\*\*Marca:\*\*\s*(.*?)(?=\n\s*\n|\Z)", corpo, re.S)
        texto = " ".join((ap.group(1) if ap else "").split())
        if mar:
            texto += " " + " ".join(mar.group(1).split())
        fora.append((m.group(1), texto))
    return fora


def julgar(texto):
    """Devolve (erros, avisos) do texto que chega a margem."""
    erros, avisos = [], []
    for m in RE_POSICAO.finditer(texto):
        erros.append("remissão de posição: %r" % m.group(0).strip())
    for m in RE_POSICAO_SOLTA.finditer(texto):
        erros.append("remissão de posição: %r" % m.group(0).strip())
    for m in RE_OUTRO_ITEM.finditer(texto):
        erros.append("remissão a outro item: %r" % m.group(0).strip())
    if not RE_NOME.search(texto):
        for m in RE_CONTAGEM.finditer(texto):
            avisos.append("contagem sem nome: %r" % m.group(0).strip())
    return erros, avisos


def autoteste():
    """Prova o conferidor com o que ele tem de acusar e o que nao pode acusar."""
    falhas = []
    devem = [
        u"escrever em [P439] a conta acima, com os 35,3%",
        u"acrescentar em [P447] um parágrafo que percorra a lista acima",
        u"corrigir a grafia como em SC44, no mesmo parágrafo",
        u"uniformizar as duas passagens indicadas abaixo",
    ]
    for d in devem:
        if not julgar(d)[0]:
            falhas.append("não acusa: %r" % d)
    nao_podem = [
        u"escrever que, retirados os 41 temas de servidor público civil, sobram "
        u"54 negativas em 153 temas, ou 35,3%",
        u"acrescentar as cinco entradas que faltam, que são *Lefebvre*, "
        u"*Mitchell*, *Kitchin*, *Dodge* e *Castells*",
        u"trocar 20 por 19 em [P837] e reler a frase seguinte para confirmar",
    ]
    for n in nao_podem:
        if julgar(n)[0]:
            falhas.append("acusa o que está correto: %r -> %r" % (n[:40], julgar(n)[0]))
    # o aviso da contagem tem de calar quando o nome vem junto
    if julgar(u"acrescentar as cinco entradas: *Lefebvre* e as demais")[1]:
        falhas.append("avisa contagem mesmo com o nome escrito ao lado")
    if not julgar(u"conferir as duas anotações internas e apagá-las")[1]:
        falhas.append("não avisa contagem sem nome nenhum")
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("itens", nargs="+")
    ap.add_argument("--so-erros", action="store_true")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio conferidor esta quebrado, e nao reporto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: acusa a remissão de posição, a remissão a outro item e a "
          "contagem sem nome,\n  e cala quando o nome está escrito ao lado")

    total_e = total_a = 0
    for cam in a.itens:
        its = campos(cam)
        linhas = []
        for cod, texto in its:
            e, av = julgar(texto)
            if e or (av and not a.so_erros):
                linhas.append((cod, e, av))
            total_e += len(e)
            total_a += len(av)
        print("\n  %s: %d itens, %d com apontamento"
              % (Path(cam).name, len(its), len(linhas)))
        for cod, e, av in linhas:
            print("     %-5s %s" % (cod, "; ".join(e + (av if not a.so_erros else []))))
    print("\n  %d remissão(ões) que a margem não resolve, %d aviso(s) de contagem sem nome"
          % (total_e, total_a))
    if total_e:
        print("  Na margem não há acima, não há abaixo e não há o outro item.")
        print("  Escreva no campo o nome da coisa de que ele fala.")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main())

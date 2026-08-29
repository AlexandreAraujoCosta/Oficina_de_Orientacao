# -*- coding: utf-8 -*-
"""Poe os apontamentos dentro do .md, como comentarios de CriticMarkup.

POR QUE ISTO EXISTE

E o equivalente do anotar_docx.py para o caminho em que nao ha .docx. Markdown
nao tem controle de alteracoes, e o CriticMarkup e a convencao feita para suprir:

    {>>comentario<<}          o que este programa escreve
    {++entra++} {--sai--}     insercao e exclusao, para quando houver correcao
    {~~antes~>depois~~}       substituicao

A virtude dela e degradar bem. Editor que reconhece a marca a exibe como
anotacao; editor que nao reconhece mostra o texto entre chaves, que continua
legivel. Nao depende de aplicativo nenhum.

COMO ANCORA

O arquivo de entrada e a extracao numerada, onde cada paragrafo abre com [P123].
Ancorar e achar a linha e escrever ao lado. Aqui, ao contrario do Word, os
localizadores do apontamento funcionam: eles apontam para este mesmo arquivo.

    python anotar_md.py <ENTREGA-PARAGRAFOS-*.md> <ENTREGA-CORRETOR-*.md> [--saida X.md]
"""
import argparse
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



RE_ITEM = re.compile(
    r"^## ([A-Z]{1,2}\d+)\s*$\n+\*\*Aponta:\*\* (.+?)\s*$\n+\*\*Abrir:\*\* (.*?)\s*$",
    re.M | re.S)
RE_LOC = re.compile(r"\[P(\d+)\]")
RE_LINHA = re.compile(r"^\[P(\d+)\]")

CABECALHO = """
> **Este arquivo traz os apontamentos do relatório, em CriticMarkup.**
> Cada um aparece ao fim do parágrafo a que se refere, entre `{>>` e `<<}`.
> Editor que reconhece a marca mostra como anotação; editor que não reconhece
> mostra o texto entre chaves, e ele continua legível.
> O código entre colchetes (`[S21]`) é o do relatório, e os `[P123]` apontam
> para os parágrafos deste mesmo arquivo.
"""


def itens(caminho):
    txt = Path(caminho).read_text(encoding="utf-8")
    out = []
    for m in RE_ITEM.finditer(txt):
        locs = [int(x) for x in RE_LOC.findall(m.group(3))]
        if locs:
            out.append((m.group(1), m.group(2).strip(), locs))
    return out


def main():
    ap = argparse.ArgumentParser(description="Apontamentos no .md, em CriticMarkup.")
    ap.add_argument("trabalho", help="a extração numerada")
    ap.add_argument("lista", help="ENTREGA-CORRETOR-*.md")
    ap.add_argument("--saida")
    a = ap.parse_args()

    linhas = Path(a.trabalho).read_text(encoding="utf-8").splitlines()
    onde = {}
    for i, l in enumerate(linhas):
        m = RE_LINHA.match(l)
        if m:
            onde[int(m.group(1))] = i
    if not onde:
        sys.exit("nenhum parágrafo numerado neste arquivo: ele não é uma extração.")

    lista = itens(a.lista)
    if not lista:
        sys.exit("nenhum item com localizador na lista: nada a ancorar.")

    por_linha, fora = {}, []
    for cod, aponta, locs in lista:
        alvo = next((n for n in locs if n in onde), None)
        if alvo is None:
            fora.append(cod)
            continue
        extra = [x for x in locs if x != alvo]
        texto = "[%s] %s" % (cod, aponta)
        if extra:
            texto += " Também em: " + " ".join("[P%d]" % x for x in extra)
        # a chave dupla dentro do comentario fecharia a marca antes da hora
        texto = texto.replace("<<}", "« }").replace("{>>", "{ »")
        por_linha.setdefault(onde[alvo], []).append(texto)

    for i, marcas in por_linha.items():
        linhas[i] = linhas[i].rstrip() + "".join(" {>>%s<<}" % m for m in marcas)

    # o cabecalho entra depois do bloco de explicacao que a extracao ja traz
    corte = 0
    for i, l in enumerate(linhas[:40]):
        if l.strip() == "---":
            corte = i + 1
            break
    linhas[corte:corte] = CABECALHO.strip().splitlines() + [""]

    dest = Path(a.saida) if a.saida else \
        Path(a.trabalho).with_name(Path(a.trabalho).stem + "-ANOTADO.md")
    dest.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("  %s: %d comentários em %d parágrafos"
          % (dest.name, sum(len(v) for v in por_linha.values()), len(por_linha)))
    if fora:
        print("  sem âncora (localizador fora do arquivo): %s" % ", ".join(fora))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Escreve, em markdown, o texto que cada apontamento tera dentro do Word.

Serve de entrada para o conferidor de compreensibilidade (`prompts/
COMPREENSIBILIDADE.md`), e a razao de existir e que o anexo cru mede outra
coisa: os localizadores `[P123]` nao chegam ao autor, que recebe no lugar deles
o endereco por palavras iniciais, e um item que cita varios pontos chega
repetido em cada um. Conferir o anexo seria conferir um texto que ninguem le.

    python scripts/texto_dos_comentarios.py trabalho.docx ANEXO.md

Nada aqui digita trecho do trabalho: as aberturas sao copiadas do arquivo pelo
proprio programa, como no `anotar_docx.py`.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anotar_docx import (W, Styles, collect_paragraphs, itens, load,  # noqa: E402
                         mapa_secoes, sem_localizador)

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trabalho")
    ap.add_argument("lista", help="o anexo, ou ENTREGA-CORRETOR-*.md")
    ap.add_argument("--saida")
    a = ap.parse_args()

    parts = load(a.trabalho)
    pars = collect_paragraphs(parts["word/document.xml"].find(W + "body"),
                              Styles(parts["word/styles.xml"]))
    secoes = mapa_secoes(pars)
    lista = itens(a.lista)

    linhas = ["# Apontamentos, como chegam a quem escreveu o trabalho", "",
              "Cada bloco abaixo e um comentario na margem do trabalho. Quem le",
              "tem o trabalho aberto e nao acompanhou analise nenhuma.", ""]
    # A regra tem de ser a mesma do anotar_docx.py, senao este arquivo promete
    # marcas que o Word nao vai receber. Sem `Marca`, o item marca UM ponto; com
    # `Marca`, marca ate o teto. Em 02/09/2026 este texto anunciava 61 pontos
    # para um item que ia marcar um so, e a conferencia de compreensibilidade
    # leu a promessa, nao a realidade.
    from anotar_docx import marcas as _marcas
    TETO = 8
    curtas = _marcas(a.lista)
    for cod, aponta, locs in lista:
        limpo = sem_localizador(aponta, secoes, pars)
        linhas += ["## %s" % cod, "", limpo, ""]
        n = min(len(locs), TETO) if curtas.get(cod) else 1
        if n > 1:
            linhas += ["*Este item chega marcado em %d pontos do trabalho%s.*"
                       % (n, ", de %d ao todo" % len(locs)
                          if len(locs) > n else ""), ""]

    dest = Path(a.saida or (Path(a.lista).with_name(
        "COMENTARIOS-" + Path(a.lista).stem + ".md")))
    dest.write_text("\n".join(linhas), encoding="utf-8")
    print("%s: %d apontamentos" % (dest.name, len(lista)))


if __name__ == "__main__":
    main()

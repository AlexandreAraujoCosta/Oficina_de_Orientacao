# -*- coding: utf-8 -*-
"""Extrai do relatorio a lista de itens que o corretor executa.

POR QUE ISTO EXISTE

O corretor recebe o trabalho, o relatorio e o anexo, e precisa percorrer os itens
um a um. Ate 27/08/2026 ele fazia isso lendo a prosa do relatorio inteiro, o que
custa caro e permite pular item. Este programa devolve o indice: codigo, o que o
item aponta, e os paragrafos que ele manda abrir.

E programa, e nao modelo, porque a operacao e mecanica: os itens tem forma
regular no relatorio (`**S29. titulo**` no corpo, `### S13. titulo` no anexo) e
os localizadores estao escritos. Redigitar isso com modelo introduziria erro numa
tarefa que nao tem julgamento nenhum.

O que ele NAO faz: nao resume o item, nao decide prioridade, nao inventa a
correcao. O texto que justifica cada apontamento continua no relatorio, e o
corretor precisa dos dois.

    python lista_corretor.py <relatorio.md> [anexo.md] [--saida X.md]
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



# Duas formas convivem, e ambas aparecem tanto no relatorio quanto no anexo:
# negrito abrindo paragrafo (`**S11. ...**`) e titulo (`### S11. ...`). Ate
# 27/08/2026 o anexo so era lido na forma de titulo, e por isso os itens de
# anexo de dois dos trabalhos medidos, que usam negrito, ficavam de fora sem
# que nada acusasse. As duas passam a valer nos dois arquivos.
RE_NEGRITO = re.compile(r"^\s*(?:\d+[.)]\s*)?\*\*([A-Z]{1,2}\d+)[.,:]?\s*(.*?)\*\*", re.M)
RE_TITULO = re.compile(r"^#{2,4}\s*([A-Z]{1,2}\d+)[.,:]?\s*(.+?)\s*$", re.M)
RE_LOC = re.compile(r"\[P\d+(?:[-–]P?\d+)?\]")

# F e C nao sao correcao: sao ponto forte e contribuicao a reivindicar, e mandar
# o corretor "consertar" um ponto forte e o pior erro que este arquivo poderia
# induzir.
# S, D e SC sao as siglas do Luis. A, V, B, O e Q sao as da Clara, que le
# projeto: articulacao, viabilidade, arguicao, oportunidade e questao em
# aberto. Sem elas, o .docx anotado saia so com as correcoes mecanicas, e a
# analise inteira ficava fora da margem, que e onde quem orienta responde.
EXECUTAVEIS = ("S", "D", "SC", "A", "V", "B", "O", "Q")


def itens(texto, origem, regex):
    achados = []
    marcas = list(regex.finditer(texto))
    for i, m in enumerate(marcas):
        cod, titulo = m.group(1), m.group(2).strip()
        if not cod.rstrip("0123456789") in EXECUTAVEIS:
            continue
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.start():fim]
        locs = []
        for l in RE_LOC.findall(corpo):
            if l not in locs:
                locs.append(l)
        # "- **S9**, pela razao acima" e referencia cruzada numa lista de
        # prioridade, e nao o item. O que separa e o titulo ter substancia.
        if len(titulo) < 25 and len(corpo.strip()) < 200:
            continue
        # A instrucao curta que o item traz quando a correcao e a mesma em cada
        # ocorrencia. Ela decide, no anotar_docx.py, se o item marca todos os
        # pontos que cita ou um so; sem ela, item que cita quinze lugares
        # marcaria os quinze e a margem viraria eco.
        mm = re.search(r"^\*\*Marca:\*\*\s*(.+?)\s*$", corpo, re.M)
        achados.append((cod, titulo, locs, origem, mm.group(1) if mm else None))
    return achados


def main():
    ap = argparse.ArgumentParser(description="Indice de itens para o corretor.")
    ap.add_argument("relatorio")
    ap.add_argument("anexo", nargs="?")
    ap.add_argument("--saida")
    a = ap.parse_args()

    def ler(caminho, origem):
        txt = Path(caminho).read_text(encoding="utf-8")
        achados = itens(txt, origem, RE_NEGRITO) + itens(txt, origem, RE_TITULO)
        # O mesmo codigo pode casar nas duas formas; fica a de titulo, que traz
        # o item inteiro, e nao a linha que so o referencia numa lista.
        melhor = {}
        for cod, tit, locs, org, mrc in achados:
            ant = melhor.get(cod)
            if ant is None or len(tit) > len(ant[1]) or len(locs) > len(ant[2]):
                # A marca vem de onde estiver: se a forma vencedora nao a traz e
                # a outra traz, ela nao pode se perder na escolha.
                melhor[cod] = (cod, tit, locs, org, mrc or (ant[4] if ant else None))
        return list(melhor.values())

    todos = ler(a.relatorio, "relatório")
    if a.anexo and Path(a.anexo).exists():
        vistos = {c for c, *_ in todos}
        todos += [x for x in ler(a.anexo, "anexo") if x[0] not in vistos]

    if not todos:
        sys.exit("nenhum item reconhecido." + '\n\n' + "Cada item precisa abrir com um codigo, numa destas duas formas:" + '\n\n' + "### D1. Nome curto do item" + '\n' + "**D1. Nome curto do item**" + '\n\n' + "O codigo e uma ou duas maiusculas mais numero, e as executaveis sao" + '\n' + "D, S e SC. Item sem localizador [Pxxx] na prosa tambem e descartado.")

    def chave(t):
        cod = t[0]
        return (EXECUTAVEIS.index(cod.rstrip("0123456789")), int(re.sub(r"\D", "", cod)))
    todos.sort(key=chave)

    L = [
        "# Itens para o corretor",
        "",
        "Gerado por `lista_corretor.py` a partir de `%s`. **Não edite:** é índice, e o"
        % Path(a.relatorio).name,
        "que justifica cada item continua no relatório, que precisa ir junto.",
        "",
        "Cada bloco traz o código, o que o item aponta e os parágrafos que ele manda abrir.",
        "`S` é correção, `D` é desenvolvimento e `SC` é sugestão complementar. O campo",
        "*Onde está* diz se o item veio do corpo do relatório ou do anexo.",
        "",
        "---",
        "",
    ]
    for cod, titulo, locs, origem, marca in todos:
        L.append("## %s" % cod)
        L.append("")
        L.append("**Aponta:** %s" % titulo)
        L.append("")
        if marca:
            L.append("**Marca:** %s" % marca)
            L.append("")
        L.append("**Abrir:** %s" % (" ".join(locs) if locs else "(sem localizador no item)"))
        L.append("")
        L.append("**Onde está:** %s" % origem)
        L.append("")

    saida = Path(a.saida) if a.saida else \
        Path(a.relatorio).with_name("CORRETOR-" + Path(a.relatorio).name)
    saida.write_text("\n".join(L) + "\n", encoding="utf-8")
    por = {}
    for cod, *_ in todos:
        por[cod.rstrip("0123456789")] = por.get(cod.rstrip("0123456789"), 0) + 1
    print("  %s: %d itens (%s)" % (saida.name, len(todos),
          ", ".join("%s %d" % (k, v) for k, v in sorted(por.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

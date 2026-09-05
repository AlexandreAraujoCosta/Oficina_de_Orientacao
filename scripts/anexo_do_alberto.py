# -*- coding: utf-8 -*-
"""Deriva, do relatorio do Alberto, a lista de itens que a maquinaria le.

POR QUE ISTO EXISTE

O relatorio do Alberto traz os itens em prosa titulada (`### S6. ...`, com os
campos `- **Aponta**`, `- **O que fazer**`), que e a forma que quem recebe le.
O `anotar_docx.py` e o `texto_dos_comentarios.py` leem outra forma (`## S6`,
`**Aponta:**`, `**Abrir:**`), que e a que ancora o comentario no paragrafo
certo. Ate 05/09/2026 a passagem de uma forma a outra nao existia, e o
`texto_dos_comentarios.py` devolvia zero apontamentos sobre um relatorio de
trinta e nove itens, sem dizer por que.

Ninguem digita o texto do item: este programa o copia do relatorio.

O QUE VAI PARA A MARGEM, E POR QUE NAO E O ITEM INTEIRO

A margem recebe o titulo do item e o campo `O que fazer`, e nao o campo
`Aponta`. O `Aponta` traz a prestacao de contas da busca (quantos paragrafos,
que forma, que recorte), que existe para quem confere o relatorio e nao para
quem corrige o texto. Medido em 05/09/2026, numa leitura fria dos 37
apontamentos de uma dissertacao: doze deles fizeram o leitor ler alguma frase
duas vezes, e em todos era o meio do item. O proprio ALBERTO.md ja diz que o
campo `O que fazer` e "o unico campo que o autor lera ao lado do texto".

Os localizadores de `Abrir` continuam saindo do `Aponta`, porque e la que esta
onde o defeito ocorre, e e por eles que o comentario se ancora.

Uso:
    python scripts/anexo_do_alberto.py RELATORIO-X.md --saida ANEXO-ITENS-X.md
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

# `### S6. titulo` ate o proximo `###` ou `##` de mesmo nivel ou maior.
RE_S = re.compile(
    r"^### (S\d+)\.\s*(.+?)\s*$\n(.*?)(?=^#{2,3} |\Z)", re.M | re.S)
RE_CAMPO = re.compile(
    r"^- \*\*(Tipo|Aponta|O que fazer|O que muda)\*\*\s*(.*?)"
    r"(?=^- \*\*|\Z)", re.M | re.S)
# `**SC1.** texto` ate a linha em branco que precede o proximo SC.
RE_SC = re.compile(
    r"^\*\*(SC\d+)\.\*\*\s*(.*?)(?=^\*\*SC\d+\.\*\*|^#{2,3} |\Z)", re.M | re.S)
RE_LOC = re.compile(r"\[P(\d+)\]")


def um_paragrafo(txt):
    """Junta as quebras de linha do markdown sem colar palavras."""
    return re.sub(r"\s+", " ", txt).strip()


def abrir(texto):
    """Os localizadores na ordem em que aparecem, sem repetir."""
    vistos, fora = set(), []
    for n in RE_LOC.findall(texto):
        if n not in vistos:
            vistos.add(n)
            fora.append("[P%s]" % n)
    return fora


def extrair(txt):
    """[(codigo, aponta, abrir)], na ordem do relatorio."""
    itens = []
    for m in RE_S.finditer(txt):
        cod, titulo, corpo = m.group(1), m.group(2), m.group(3)
        campos = {k: um_paragrafo(v) for k, v in RE_CAMPO.findall(corpo)}
        aponta = campos.get("Aponta", "")
        fazer = campos.get("O que fazer", "")
        if not aponta:
            continue
        cabeca = titulo if titulo.endswith((".", "?", "!")) else titulo + "."
        texto = cabeca if not fazer else cabeca + " " + fazer
        itens.append((cod, um_paragrafo(texto), abrir(aponta) or abrir(texto)))
    for m in RE_SC.finditer(txt):
        cod, corpo = m.group(1), um_paragrafo(m.group(2))
        itens.append((cod, corpo, abrir(corpo)))
    return itens


CABECA = """# Itens do relatório, na forma que a maquinaria lê

Derivado de `%s` por `anexo_do_alberto.py`. Não edite: o que se edita é o
relatório, e este arquivo se gera de novo. O texto de cada item foi copiado do
relatório por programa, e não redigido aqui.

"""


def escrever(origem, itens, saida):
    partes = [CABECA % Path(origem).name]
    for cod, aponta, locs in itens:
        partes.append("## %s\n\n**Aponta:** %s\n\n**Abrir:** %s\n"
                      % (cod, aponta, ", ".join(locs) if locs else ""))
    Path(saida).write_text("\n".join(partes), encoding="utf-8")


CONTROLE = """### S1. Um titulo qualquer

- **Tipo** Uma categoria
- **Aponta** O problema esta em [P10] e tambem em [P20].
- **O que fazer** Consertar [P10].
- **O que muda** Passa a fechar.

### S2. Outro titulo

- **Tipo** Outra categoria
- **Aponta** Nada aqui tem localizador.
- **O que fazer** Nada.

## 8. As correcoes que nao mudam nenhuma afirmacao

**SC1.** [P30] tem uma gralha.

**SC2.** [P40] e [P30] repetem a mesma legenda.
"""


def provar():
    """O extrator tem de achar o que esta la e reprovar o que foi adulterado."""
    itens = extrair(CONTROLE)
    esperado = [
        ("S1", "Um titulo qualquer. Consertar [P10].", ["[P10]", "[P20]"]),
        ("S2", "Outro titulo. Nada.", []),
        ("SC1", "[P30] tem uma gralha.", ["[P30]"]),
        ("SC2", "[P40] e [P30] repetem a mesma legenda.", ["[P40]", "[P30]"]),
    ]
    if itens != esperado:
        sys.exit("o extrator nao le o controle:\n%r" % (itens,))
    # adulterado: sem o campo Aponta, o item tem de sumir
    ruim = extrair(CONTROLE.replace("- **Aponta** O problema", "- **Xponta** O problema"))
    if any(c == "S1" for c, _, _ in ruim):
        sys.exit("o extrator aceita item sem o campo Aponta; nao confie nele")
    # adulterado: cabecalho de nivel errado nao e item
    ruim = extrair(CONTROLE.replace("### S1.", "#### S1."))
    if any(c == "S1" for c, _, _ in ruim):
        sys.exit("o extrator aceita cabecalho de outro nivel; nao confie nele")
    print("controle: o extrator le os quatro itens do controle e reprova as "
          "duas adulteracoes")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio")
    ap.add_argument("--saida")
    a = ap.parse_args()
    provar()
    txt = io.open(a.relatorio, encoding="utf-8").read()
    itens = extrair(txt)
    if not itens:
        sys.exit("nenhum item no relatorio: a forma mudou, e o programa nao serve mais")
    saida = a.saida or str(Path(a.relatorio).with_name(
        "ITENS-" + Path(a.relatorio).name))
    escrever(a.relatorio, itens, saida)
    sem = [c for c, _, l in itens if not l]
    print("%s: %d itens (%d S, %d SC)"
          % (saida, len(itens),
             sum(1 for c, _, _ in itens if not c.startswith("SC")),
             sum(1 for c, _, _ in itens if c.startswith("SC"))))
    if sem:
        print("  sem localizador, e por isso sem ancora no .docx: %s" % ", ".join(sem))


if __name__ == "__main__":
    main()

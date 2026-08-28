# -*- coding: utf-8 -*-
"""Acha o trabalho na pasta e roda a cadeia dos programas sobre ele.

POR QUE ISTO EXISTE

Medido em 28/08/2026, na primeira vez que alguem seguiu o roteiro numa maquina
que nao a de quem o escreveu: os comandos traziam `trabalho.docx` como exemplo,
a pessoa colou como estava, e os quatro programas responderam "nao encontrei".
Trocar o nome a mao pede saber o nome exato, com acento e espaco, e digitar sem
errar. Nada disso e trabalho de quem orienta.

Aqui nao ha nome para digitar. O programa procura o trabalho, diz qual escolheu,
e roda os cinco na ordem.

COMO ESCOLHE, E POR QUE ASSIM

Um so candidato: e ele. Mais de um: o de modificacao mais recente, **com os
outros listados**, para que uma escolha errada apareca em vez de passar batido.
Ficheiro que a propria oficina gerou nao entra (ENTREGA-, ANOTADO-), senao a
segunda rodada analisaria a saida da primeira.

Uso:
    python scripts/analisar.py                 acha e roda tudo
    python scripts/analisar.py --so-achar      so diz qual escolheria
    python scripts/analisar.py <arquivo>       o de sempre, se quiser mandar
"""

import argparse
import subprocess
import sys
from pathlib import Path

# O console do Windows nao aceita acento por padrao, e nome de trabalho com
# acento e a regra em portugues. Sem isto, o programa morre na primeira linha.
for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent
GERADOS = ("entrega-", "anotado-", "relatorio-", "caderno-")


def candidatos(pasta):
    achados = []
    for p in sorted(pasta.iterdir()):
        if not p.is_file() or p.suffix.lower() not in (".docx", ".pdf"):
            continue
        if p.name.startswith("~$") or p.name.lower().startswith(GERADOS):
            continue
        achados.append(p)
    return sorted(achados, key=lambda x: x.stat().st_mtime, reverse=True)


def escolher(pasta):
    achados = candidatos(pasta)
    if not achados:
        sys.exit("nao ha .docx nem .pdf nesta pasta.\n"
                 "Copie o trabalho para ca, ou passe o caminho:\n"
                 "    python scripts/analisar.py caminho/para/o/trabalho.docx")
    escolhido = achados[0]
    if len(achados) > 1:
        print("Ha %d arquivos, e escolhi o modificado mais recentemente:" % len(achados))
        for p in achados:
            marca = "  ->" if p is escolhido else "    "
            print("%s %s" % (marca, p.name))
        print("Se nao for esse, passe o nome: python scripts/analisar.py \"nome.docx\"\n")
    return escolhido


COLHIDO = []


def rodar(programa, *args):
    print("\n" + "=" * 68)
    cabeca = "%s %s" % (programa, " ".join(str(a) for a in args))
    print(cabeca)
    print("=" * 68)
    r = subprocess.run([sys.executable, str(RAIZ / programa)] + [str(a) for a in args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-800:]
    print(saida)
    COLHIDO.append("## " + cabeca + chr(10) + chr(10) + "```" + chr(10) + saida + chr(10) + "```")
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trabalho", nargs="?", help="padrao: o .docx ou .pdf mais recente da pasta")
    ap.add_argument("--so-achar", action="store_true", help="diz qual escolheria e para")
    a = ap.parse_args()

    alvo = Path(a.trabalho) if a.trabalho else escolher(Path.cwd())
    if not alvo.exists():
        sys.exit("nao encontrei %s" % alvo)

    print("Trabalho: %s" % alvo.name)
    if a.so_achar:
        return 0

    docx = alvo.suffix.lower() == ".docx"
    rodar("extrair.py", alvo)
    rodar("analisar_docx.py" if docx else "analisar_pdf.py", "sumario", alvo)
    if docx:
        rodar("analisar_docx.py", "forma", alvo)
        rodar("conferir_consistencia.py", "tudo", alvo)
    rodar("conferir_interno.py", Path("extracao") / (alvo.stem + ".txt"))

    destino = Path("SUSPEITAS-" + alvo.stem + ".md")
    cabecalho = (
        "# Suspeitas levantadas em " + alvo.name + chr(10) + chr(10) +
        "Isto e a saida bruta dos programas, e nao um relatorio. Sao SUSPEITAS:" + chr(10) +
        "nenhum programa distingue mudanca declarada de deslize. Julgue cada uma" + chr(10) +
        "abrindo o paragrafo citado, e nao digite trecho do trabalho." + chr(10) + chr(10) +
        "As legendas e pseudo-titulos marcados dentro de extracao/" + alvo.stem +
        ".txt fazem parte do conjunto e nao estao repetidos aqui." + chr(10) + chr(10))
    destino.write_text(cabecalho + (chr(10) * 2).join(COLHIDO) + chr(10), encoding="utf-8")

    print("\n" + "=" * 68)
    print("Os programas terminaram. Eles levantaram SUSPEITAS, e nao apontamentos:")
    print("nenhum deles distingue mudanca declarada de deslize. O julgamento de")
    print("cada uma e a proxima etapa, e e leitura.")
    print("")
    print("A saida ficou em %s, que e a entrada de quem julga." % destino.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

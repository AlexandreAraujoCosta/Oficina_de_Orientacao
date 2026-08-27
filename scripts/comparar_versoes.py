"""Compara duas extracoes do mesmo trabalho e diz o que mudou.

POR QUE ISTO EXISTE

Numa segunda passada, rodar as seis vozes sobre um texto que mudou 3% redescobre
os mesmos itens e gasta o mesmo. O que informa e outra coisa: **o que mudou, e se
o que o relatorio anterior apontou foi atendido.** Este programa responde a
primeira metade, por comparacao de paragrafos, e prepara a segunda, listando os
localizadores que o relatorio antigo citava e dizendo, de cada um, se o paragrafo
correspondente mudou.

O pareamento e por conteudo, e nao por numero: paragrafo inserido desloca toda a
numeracao seguinte, e comparar P400 com P400 devolveria diferenca em tudo depois
da primeira insercao.

Uso:
    python comparar_versoes.py <antiga.txt> <nova.txt> [--relatorio R.md]
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

RE_PAR = re.compile(r"^[#*>\s]*\[P(\d+)\]\s*(.*)$")
RE_PAR_PDF = re.compile(r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\]\s*)?(?:\(p\.\d+\)\s*)?(.*)$")


def carregar(caminho):
    saida = []
    for linha in Path(caminho).read_text(encoding="utf-8", errors="replace").splitlines():
        if linha.startswith("##EXTRACAO"):
            continue
        m = RE_PAR.match(linha) or RE_PAR_PDF.match(linha)
        if m:
            saida.append((int(m.group(1)), " ".join(m.group(2).split())))
    return saida


def normaliza(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def main():
    ap = argparse.ArgumentParser(description="Compara duas versões da mesma extração.")
    ap.add_argument("antiga")
    ap.add_argument("nova")
    ap.add_argument("--relatorio", help="relatório da versão antiga, para conferir os itens")
    ap.add_argument("--exemplos", type=int, default=8)
    a = ap.parse_args()

    velha, nova = carregar(a.antiga), carregar(a.nova)
    print("antiga: %d parágrafos, %d palavras" % (len(velha), sum(len(t.split()) for _, t in velha)))
    print("nova:   %d parágrafos, %d palavras\n" % (len(nova), sum(len(t.split()) for _, t in nova)))

    tv = [normaliza(t) for _, t in velha]
    tn = [normaliza(t) for _, t in nova]
    sm = difflib.SequenceMatcher(None, tv, tn, autojunk=False)

    iguais = inseridos = removidos = alterados = 0
    mudancas = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            iguais += i2 - i1
        elif tag == "insert":
            inseridos += j2 - j1
            mudancas.append(("inserido", None, [nova[j][0] for j in range(j1, j2)]))
        elif tag == "delete":
            removidos += i2 - i1
            mudancas.append(("removido", [velha[i][0] for i in range(i1, i2)], None))
        else:
            alterados += max(i2 - i1, j2 - j1)
            mudancas.append(("alterado", [velha[i][0] for i in range(i1, i2)],
                             [nova[j][0] for j in range(j1, j2)]))

    print("iguais:    %4d parágrafos" % iguais)
    print("alterados: %4d" % alterados)
    print("inseridos: %4d" % inseridos)
    print("removidos: %4d" % removidos)
    tot = len(velha) or 1
    print("\n%.1f%% dos parágrafos da versão antiga sobrevivem sem alteração\n"
          % (iguais / tot * 100))

    print("As mudanças, em ordem:")
    for tipo, ve, no in mudancas[:a.exemplos * 3]:
        if tipo == "inserido":
            print("  + inseridos P%s-P%s (%d)" % (no[0], no[-1], len(no)))
        elif tipo == "removido":
            print("  - removidos P%s-P%s (%d) da versão antiga" % (ve[0], ve[-1], len(ve)))
        else:
            print("  ~ alterados P%s-P%s -> P%s-P%s" % (ve[0], ve[-1], no[0], no[-1]))

    # ------------------------------------------------ o relatorio anterior
    if a.relatorio:
        texto = Path(a.relatorio).read_text(encoding="utf-8", errors="replace")
        citados = sorted({int(x) for x in re.findall(r"\[P(\d+)", texto)})
        mexidos = set()
        for tipo, ve, no in mudancas:
            if ve:
                mexidos |= set(ve)
        atendidos = [p for p in citados if p in mexidos]
        print("\nO relatório anterior cita %d parágrafos distintos." % len(citados))
        print("  %d deles foram alterados ou removidos (%.0f%%)"
              % (len(atendidos), len(atendidos) / max(1, len(citados)) * 100))
        print("  %d continuam idênticos" % (len(citados) - len(atendidos)))
        print("\n  **Parágrafo idêntico não prova item não atendido**: a correção pode")
        print("  ter sido feita noutro lugar. Mas parágrafo alterado é onde a")
        print("  segunda leitura precisa olhar primeiro.")
        if atendidos:
            print("\n  alterados entre os citados: %s%s"
                  % (", ".join("P%d" % p for p in atendidos[:25]),
                     " ..." if len(atendidos) > 25 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

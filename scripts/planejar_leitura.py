# -*- coding: utf-8 -*-
"""Projeta o tempo de cada braço da leitura e decide o que quebrar.

POR QUE ISTO EXISTE

Os bracos correm ao mesmo tempo, e o tempo de parede e o do mais lento. Quebrar
um braco em partes paralelas so compra tempo enquanto ele for o mais lento;
depois disso paga o prompt duplicado e nao ganha um segundo.

Medido em 09/09/2026, sobre a dissertacao T: 106 figuras
quebradas em quatro deram 10m14s de parede, e a soma dos quatro foi 33m48s.
O modelo abaixo preve 26,7 min para um agente sozinho fazendo as 106, de modo
que a quebra custou cerca de 26%. O prompt de 1.500 tokens reenviado a cada
turno em quatro contextos em vez de um responde por 27% dos 491 mil tokens
gastos, e os dois numeros baterem e indicio de que a quebra custa o prompt
duplicado. **A quebra em quatro foi excessiva:** levou o braco das figuras a
8,4 min quando os bracos de prosa estavam em 14, e os dois ultimos cortes nao
compraram parede nenhuma.

O MODELO, E O QUE ELE VALE

    figuras   segundos = 131 + 13,9 x n        R2 = 0,76, seis pontos
    prosa     ~14,5 min, praticamente fixo     UM ponto medido

O de figuras vem de seis execucoes de um dia so, quase todas do mesmo trabalho,
e abaixo de umas quinze figuras ele nao explica nada: o ponto de 3 figuras
custou mais que o de 13, porque ali so ha custo fixo.

O de prosa **nao e ajuste**: e uma medicao unica (13,7 min sobre 19.166
palavras) sustentada por duas vizinhas de outro tipo de leitura (16,1 e 14,0).
Ele entra como marcador, e o programa o imprime marcado. Nao decida quebrar
prosa com base nele.

AS DUAS REGRAS DE QUEBRA

1. **So o braco do caminho critico se quebra**, e so ate deixar de ser:
   `partes = teto(T_maior / T_segundo_maior)`.
2. **So se quebra material que e lista** (figuras, referencias, itens de
   apendice), onde o tempo escala com a contagem. Prosa nao se quebra: o custo
   e fixo e a relacao entre as partes e o que a prosa tem de proprio.

E quem quebra, consolida: cada parte grava um arquivo, e uma passada final le
so os arquivos, sem abrir imagem, atras do que nenhuma parte podia ver.

Uso:
    python scripts/planejar_leitura.py <trabalho.docx> <extracao.txt>
    python scripts/planejar_leitura.py <trabalho.docx> <extracao.txt> --lotes
"""
import argparse
import io
import math
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --------------------------------------------------------------- os modelos

FIG_FIXO, FIG_POR = 131.0, 13.9        # segundos; R2 = 0,76 em seis pontos
PROSA_MIN = 14.5                       # minutos; UM ponto medido, ver docstring
PROSA_POR_MIL = 0.0                    # nao ha ajuste; fica explicito que e zero


def tempo_figuras(n):
    return (FIG_FIXO + FIG_POR * n) / 60.0


def tempo_prosa(palavras):
    return PROSA_MIN + PROSA_POR_MIL * (palavras / 1000.0)


def partes_para(t_maior, t_segundo):
    """Quantas partes bastam para o braço maior deixar de ser o caminho crítico."""
    if t_segundo <= 0 or t_maior <= t_segundo:
        return 1
    return int(math.ceil(t_maior / t_segundo))


# ------------------------------------------------------------------ leitura

RE_PAR = re.compile(r"\[P(\d+)\]")


def paragrafos(caminho):
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    ps = RE_PAR.split(t)
    return {int(ps[i]): ps[i + 1] for i in range(1, len(ps) - 1, 2)}


def palavras(ps, a, b):
    return sum(len(x.split()) for n, x in ps.items() if a <= n <= b)


def fronteiras_do(caminho):
    import mapa_estrutural as me
    return me.fronteiras(me.ler(caminho))


RE_PARTE = re.compile(r"^\s*\**\s*PARTE\s+([IVX]+|\d+)\b", re.I)
RE_METODO = re.compile(r"^\s*\**\s*(?:[\d.]+\s*)?(Metodologia|Método|Metodo|"
                       r"Procedimentos metodol)", re.I)


def contar_figuras(docx, extracao):
    """Chama o casador e conta as figuras do corpo. Devolve (n, saida)."""
    prog = AQUI / "figuras_do_docx.py"
    if not prog.exists() or not Path(docx).exists():
        return 0, ""
    try:
        r = subprocess.run([sys.executable, str(prog), docx, "--extracao", extracao],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600)
    except Exception:
        return 0, ""
    m = re.search(r"(\d+)\s+figura\(s\)\s+no corpo", r.stdout)
    return (int(m.group(1)) if m else 0), r.stdout


RE_ITEM_INV = re.compile(
    r"^\s*(\d+)\s+\[P(\d+)\]\s+(.*?)\n\s+imagem na posicao \d+.*?: (\S+\.png)", re.M)


# ------------------------------------------------------------------- bracos

def bracos(ps, fr, n_figuras):
    """[(nome, materia, tamanho, unidade, minutos, e_lista)]"""
    N = max(ps) if ps else 0
    ini = fr.get("resumo") or fr.get("abstract") or 1
    intro = fr.get("intro") or ini
    concl = fr.get("conclusao") or N
    refer = fr.get("referencias") or N

    # ONDE A INTRODUCAO ACABA, e nao onde ela comeca. `fr["intro"]` e o
    # paragrafo em que ela abre; o braco A ia de `ini` ate ali, isto e, parava
    # antes da introducao inteira, e o braco D recomecava no mesmo ponto. A
    # introducao entrava nos dois, e nascia um braco fantasma de vinte
    # paragrafos. Medido em 09/09/2026 na dissertacao T.
    partes = sorted(n for n, x in ps.items()
                    if RE_PARTE.match(re.sub(r"<!--.*?-->|[#*]", "", x))
                    and intro < n < concl)
    fim_intro = partes[0] - 1 if partes else intro

    fora = []
    pa = palavras(ps, ini, fim_intro) + palavras(ps, concl, refer - 1)
    fora.append(("A. o que promete e o que afirma",
                 "resumo, abstract, introdução, fecho", pa, "palavras",
                 tempo_prosa(pa), False))

    met = [n for n, x in ps.items() if RE_METODO.match(re.sub(r"<!--.*?-->", "", x))
           and intro <= n < concl]
    pm = 0
    if met:
        for k in met:
            fim = min([n for n in sorted(ps) if n > k + 1
                       and len(ps[n].split()) < 12] + [k + 40])
            pm += palavras(ps, k, fim)
    fora.append(("B. o desenho declarado",
                 "%d seção(ões) de metodologia" % len(met), pm, "palavras",
                 tempo_prosa(pm) if met else 0.0, False))

    pr = palavras(ps, refer, N)
    n_ref = sum(1 for n, x in ps.items() if n > refer
                and re.match(r"^\s*\**[A-ZÀ-Ú]{2,}[A-ZÀ-Ú\s,.]*,", x))
    fora.append(("C. as referências contra o corpo",
                 "%d entrada(s)" % n_ref, n_ref, "entradas",
                 tempo_prosa(pr), True))

    cortes = [fim_intro + 1] + partes + [concl]
    cortes = sorted(set(cortes))
    for k in range(len(cortes) - 1):
        a, b = cortes[k], cortes[k + 1] - 1
        p = palavras(ps, a, b)
        if p < 1500:
            continue
        nome = "D%d. a prosa de substância" % (k + 1) if len(cortes) > 2 else \
               "D. a prosa de substância"
        fora.append((nome, "[P%d]–[P%d]" % (a, b), p, "palavras",
                     tempo_prosa(p), False))

    fora.append(("E. os dados, lidos antes da prosa",
                 "%d figura(s) no corpo" % n_figuras, n_figuras, "figuras",
                 tempo_figuras(n_figuras) if n_figuras else 0.0, True))
    return [b for b in fora if b[4] > 0]


# ---------------------------------------------------------------- autoteste

def autoteste():
    erros = []
    # o modelo das figuras, contra os pontos medidos
    for n, seg in ((25, 383), (27, 523), (27, 568)):
        proj = tempo_figuras(n) * 60
        if abs(proj - seg) > 0.45 * seg:
            erros.append("o modelo erra mais de 45%% em %d figuras: %.0f vs %d"
                         % (n, proj, seg))
    if not (26.0 < tempo_figuras(106) < 27.5):
        erros.append("106 figuras deviam projetar ~26,7 min, deu %.1f"
                     % tempo_figuras(106))
    # a regra de quebra
    if partes_para(26.7, 16.1) != 2:
        erros.append("26,7 contra 16,1 tem de dar 2 partes, deu %d"
                     % partes_para(26.7, 16.1))
    if partes_para(10.0, 16.0) != 1:
        erros.append("braço que já não é o crítico não se quebra")
    if partes_para(50.0, 10.0) != 5:
        erros.append("50 contra 10 tem de dar 5 partes")
    # CONTROLE: quebrar em quatro o que pedia dois nao pode ser o que sai
    if partes_para(26.7, 16.1) == 4:
        erros.append("a regra reproduz a quebra excessiva de 09/09")
    if erros:
        for e in erros:
            print("  AUTOTESTE FALHOU: %s" % e, file=sys.stderr)
        raise SystemExit(2)
    print("  autoteste: o modelo fica a menos de 45% dos três pontos medidos, "
          "projeta 26,7 min para 106 figuras, e a regra de quebra devolve 2 "
          "onde eu quebrei em 4.")


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("extracao")
    ap.add_argument("--lotes", action="store_true",
                    help="grava os arquivos de lote da quebra recomendada")
    a = ap.parse_args()

    autoteste()

    ps = paragrafos(a.extracao)
    if not ps:
        print("  não reconheci parágrafo em %s" % a.extracao, file=sys.stderr)
        return 2
    fr = fronteiras_do(a.extracao)
    n_fig, inventario = contar_figuras(a.docx, a.extracao)

    bs = sorted(bracos(ps, fr, n_fig), key=lambda x: -x[4])
    print("\n  OS BRAÇOS, e eles correm ao mesmo tempo\n")
    print("  %-36s %-30s %8s" % ("braço", "matéria", "min"))
    for nome, mat, tam, uni, mn, lista in bs:
        marca = "" if lista else "  *"
        print("  %-36s %-30s %8.1f%s" % (nome[:36], mat[:30], mn, marca))
    print("\n  * projeção de prosa: UM ponto medido (13,7 min sobre 19.166 "
          "palavras).\n    Não é ajuste, e não decida quebrar prosa por ela.")

    if len(bs) < 2:
        print("\n  um braço só; nada a quebrar.")
        return 0

    maior, segundo = bs[0], bs[1]
    print("\n  CAMINHO CRÍTICO: %s, %.1f min" % (maior[0], maior[4]))
    print("  segundo: %s, %.1f min" % (segundo[0], segundo[4]))

    if not maior[5]:
        print("\n  O braço mais lento é de prosa, e prosa não se quebra: o custo")
        print("  é fixo e a relação entre as partes é o que ela tem de próprio.")
        print("  Tempo de parede projetado: %.1f min." % maior[4])
        return 0

    k = partes_para(maior[4], segundo[4])
    if k <= 1:
        print("\n  Nada a quebrar: o mais lento já está no nível dos outros.")
        print("  Tempo de parede projetado: %.1f min." % maior[4])
        return 0

    print("\n  QUEBRAR EM %d, e não mais: %.1f / %.1f = %.2f."
          % (k, maior[4], segundo[4], maior[4] / segundo[4]))
    print("  Cada parte fica em ~%.1f min, e o caminho crítico passa a ser"
          % (maior[4] / k))
    print("  %s, com %.1f min. Quebrar além disso paga o prompt duplicado"
          % (segundo[0], segundo[4]))
    print("  (~26% medido em 09/09/2026) e não compra parede nenhuma.")
    print("\n  E quem quebra, consolida: cada parte grava um arquivo, e uma")
    print("  passada final lê só os arquivos, sem abrir imagem, atrás do que")
    print("  nenhuma parte podia ver.")

    if a.lotes and n_fig and maior[3] == "figuras":
        itens = RE_ITEM_INV.findall(inventario)
        if not itens:
            print("\n  não consegui reler o inventário para partir em lotes.")
            return 1
        base = Path(a.docx).stem
        por = int(math.ceil(len(itens) / float(k)))
        print("")
        for i in range(k):
            parte = itens[i * por:(i + 1) * por]
            if not parte:
                continue
            nome = "LOTE-FIGURAS-%s-%d.txt" % (base, i + 1)
            with io.open(nome, "w", encoding="utf-8") as fh:
                for n, p, leg, img in parte:
                    fh.write("%s\t[P%s]\t%s\t%s\n" % (n, p, leg.strip(), img))
            print("  %s: %d figuras, de [P%s] a [P%s], ~%.1f min"
                  % (nome, len(parte), parte[0][1], parte[-1][1],
                     tempo_figuras(len(parte))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Confere o que a figura mostra contra o que a prosa diz que ela mostra.

POR QUE ISTO EXISTE

A leitura cega descreve a figura sem saber o que o texto afirma dela. A prosa
afirma sem que ninguem confira contra o desenho. Esta e a unica peca que junta as
duas, e ela e programa, e nao leitura: nao depende de nenhuma voz lembrar de
comparar.

O QUE ELE COMPARA, e o recorte e estreito de proposito

Da prosa, so os numeros que se parecem com afirmacao sobre a figura: percentual
(`63,9%`) e decimal com virgula (`1,84`). Ano, numero de artigo, numero de
processo e numero de pagina ficam de fora, porque enchem o relatorio de acusacao
falsa e nao dizem nada sobre o grafico.

Da figura, os valores que a leitura registrou, separados em impressos e lidos.
**Valor impresso confere por igualdade**; valor lido confere pela margem que a
leitura declarou, ou por 5% quando ela nao declarou nenhuma, porque acusar
divergencia dentro do erro da propria leitura seria acusar a mim mesmo.

O QUE ELE ACUSA

1. Numero que a prosa afirma sobre a figura e que nao esta na figura.
2. Percentual impresso na figura que a prosa nunca menciona (aviso, nao acusacao:
   nem todo valor precisa ser comentado).

CONTROLE POSITIVO

Carrega um caso em que a prosa concorda com a figura (nao pode acusar) e um em
que discorda (tem de acusar), e nao roda se qualquer dos dois falhar.

Uso:
    python scripts/conferir_figura_vs_texto.py <extracao.txt> <FIGURAS.md> [FIGURAS2.md ...]
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

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import base_das_figuras as bf          # noqa: E402

MARGEM_PADRAO = 0.05                   # 5% quando a leitura nao declarou margem

RE_PAR = re.compile(r"\[P(\d+)\]")
RE_ROTULO = re.compile(r"\b(Gr[áa]fico|Figura|Tabela|Quadro)\s+(\d{1,3})\b", re.I)
# so o que parece afirmacao sobre grandeza: percentual, ou decimal com virgula
RE_AFIRMA = re.compile(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*%|(\d{1,4},\d+)")
RE_MARGEM_VAL = re.compile(r"(\d+(?:[.,]\d+)?)")


def paragrafos(caminho):
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    ps = RE_PAR.split(t)
    return {int(ps[i]): ps[i + 1] for i in range(1, len(ps) - 1, 2)}


def num(s):
    s = s.strip().replace(".", "") if "," in s else s.strip()
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def numero_da_figura(titulo):
    m = RE_ROTULO.search(titulo)
    return (m.group(1).lower().replace("á", "a"), int(m.group(2))) if m else None


def valores_por_figura(relatorios):
    """{(rotulo, numero): [(valor, origem, margem_abs)]}"""
    fora = {}
    for r in relatorios:
        txt = io.open(r, encoding="utf-8", errors="replace").read()
        for reg in bf.ler(txt, Path(r).stem):
            chave = numero_da_figura(reg["figura"])
            if not chave or reg["valor"] == "":
                continue
            v = float(reg["valor"])
            marg = None
            if reg["margem"]:
                m = RE_MARGEM_VAL.search(reg["margem"])
                if m:
                    marg = abs(num(m.group(1)) or 0)
            if marg is None and reg["origem"] == "lido":
                marg = abs(v) * MARGEM_PADRAO
            fora.setdefault(chave, []).append((v, reg["origem"], marg or 0.0))
    return fora


def cita(par_txt):
    """Que figuras este paragrafo cita."""
    return {(m.group(1).lower().replace("á", "a"), int(m.group(2)))
            for m in RE_ROTULO.finditer(par_txt)}


def afirmados(par_txt):
    fora = []
    for m in RE_AFIRMA.finditer(par_txt):
        bruto = m.group(1) or m.group(2)
        v = num(bruto)
        if v is not None:
            fora.append((v, m.group(0).strip()))
    return fora


def bate(v, valores):
    for alvo, origem, marg in valores:
        if abs(v - alvo) <= max(marg, 1e-9):
            return (alvo, origem)
    return None


def conferir(ps, figs):
    acusa, silencio = [], []
    citados = {}
    for n in sorted(ps):
        txt = ps[n]
        for chave in cita(txt):
            if chave not in figs:
                continue
            citados.setdefault(chave, set()).add(n)
            for v, bruto in afirmados(txt):
                if not bate(v, figs[chave]):
                    acusa.append((chave, n, bruto, v))
    for chave, valores in sorted(figs.items()):
        impressos = [v for v, o, _ in valores if o == "impresso"]
        if not impressos:
            continue
        prosa = set()
        for n in citados.get(chave, ()):
            prosa.update(v for v, _ in afirmados(ps[n]))
        mudos = [v for v in impressos if not any(abs(v - p) < 1e-9 for p in prosa)]
        if mudos:
            silencio.append((chave, len(mudos), len(impressos),
                             sorted(citados.get(chave, ()))))
    return acusa, silencio, citados


# ---------------------------------------------------------------- autoteste

EXT = """[P10] O Gráfico 1 mostra que 63,9% das inclusões passaram pelo virtual.

[P11] Já o Gráfico 1 indicaria 71,2% no ambiente presencial, o que não está lá.

[P12] O Gráfico 2 chega a 1810 casos em 2021, e este número não é percentual.
"""

REL = """## Gráfico 1 — Inclusões por ambiente

**Endereço.** [P10].

**Valores impressos.**

| Ambiente | Percentual |
|---|---|
| Virtual | 63,9 |
| Presencial | 36,1 |

## Gráfico 2 — Decisões por ano

**Endereço.** [P12].

**Valores lidos.**

| Ano | Leitura | Margem |
|---|---|---|
| 2021 | ~1810 | ±30 |
"""


def autoteste():
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "e.txt").write_text(EXT, encoding="utf-8")
    (d / "f.md").write_text(REL, encoding="utf-8")
    ps = paragrafos(str(d / "e.txt"))
    figs = valores_por_figura([str(d / "f.md")])
    acusa, silencio, _ = conferir(ps, figs)

    erros = []
    if ("grafico", 1) not in figs:
        erros.append("nao leu os valores do Gráfico 1")
    pegou = [(c, n, b) for c, n, b, _ in acusa]
    # tem de acusar 71,2% no P11
    if not any(n == 11 and "71,2" in b for _, n, b in pegou):
        erros.append("nao acusou 71,2%%, que a figura nao tem: %r" % pegou)
    # nao pode acusar 63,9% no P10, que bate com a figura
    if any(n == 10 for _, n, _ in pegou):
        erros.append("acusou 63,9%%, que bate com o valor impresso da figura")
    # 1810 nao e percentual nem decimal com virgula: fica de fora do recorte
    if any(n == 12 for _, n, _ in pegou):
        erros.append("acusou um inteiro sem %% nem virgula, que o recorte exclui")
    # o silencio: 36,1 esta impresso e a prosa nunca o diz
    if not any(c == ("grafico", 1) and q >= 1 for c, q, _, _ in silencio):
        erros.append("nao avisou do valor impresso que a prosa nunca menciona")

    if erros:
        for e in erros:
            print("  AUTOTESTE FALHOU: %s" % e, file=sys.stderr)
        raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("extracao")
    ap.add_argument("figuras", nargs="+")
    ap.add_argument("--silencio", action="store_true",
                    help="lista também os valores impressos que a prosa nunca diz")
    a = ap.parse_args()

    autoteste()
    print("  autoteste: acusa o número que a figura não tem, não acusa o que ela "
          "tem, e não confunde inteiro com percentual.")

    ps = paragrafos(a.extracao)
    figs = valores_por_figura(a.figuras)
    if not figs:
        print("  nenhuma figura com valores nos relatórios dados.", file=sys.stderr)
        return 1
    acusa, silencio, citados = conferir(ps, figs)

    print("\n  %d figura(s) com valores; %d citada(s) na prosa; %d parágrafo(s) "
          "de prosa examinados."
          % (len(figs), len(citados), len({n for v in citados.values() for n in v})))
    print("  Alcance: só percentuais e decimais com vírgula na prosa que cita a "
          "figura pelo rótulo. Prosa que comenta a figura sem nomeá-la fica fora.\n")

    if not acusa:
        print("  Nenhum número afirmado na prosa diverge da figura que ele cita.")
    else:
        print("  %d divergência(s) entre a prosa e a figura que ela cita:\n" % len(acusa))
        for (rot, k), n, bruto, v in acusa:
            vals = sorted({x for x, _, _ in figs[(rot, k)]})
            perto = min(vals, key=lambda x: abs(x - v)) if vals else None
            print("  [P%d]  %s %d  —  a prosa diz %s; o mais próximo na figura é %g"
                  % (n, rot.capitalize(), k, bruto, perto))

    if a.silencio and silencio:
        print("\n  Valores impressos que a prosa nunca menciona (aviso, não acusação):")
        for (rot, k), q, tot, ns in silencio:
            print("  %s %d: %d de %d, citado em %s"
                  % (rot.capitalize(), k, q, tot,
                     ", ".join("P%d" % n for n in ns[:6]) or "lugar nenhum"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

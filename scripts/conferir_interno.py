"""Conferência interna rápida e determinística, para rodar muitas vezes.

POR QUE ISTO EXISTE

A leitura de consistência é a de maior rendimento do instrumento, e boa parte do
que ela faz não precisa de modelo nenhum: conferir se a remissão aponta para algo
que existe, se a numeração de quadros tem buraco, se o percentual sai da divisão
que o próprio texto publica. Medido em 25/08/2026, ela gastou parte do orçamento
confirmando o que fecha — sumário, lista de figuras, datas de normas, um apêndice
linha a linha — e reportou "nenhuma divergência". Isso é trabalho de script.

O QUE ISTO NÃO FAZ, E É PROPOSITAL

Não lê imagem, não julga se uma categoria está bem construída, não avalia
argumento e não afirma nada sobre a origem do texto. Acha o que é mecanicamente
conferível e cala sobre o resto. **Silêncio aqui não é aprovação:** significa que
nada do que esta ferramenta sabe procurar apareceu.

Uso:
    python conferir_interno.py <extracao.txt> [--verboso]
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RE_PAR = re.compile(r"^[#*>\s]*\[P(\d+)\]\s*(.*)$")
RE_PAR_PDF = re.compile(r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\]\s*)?(?:\(p\.(\d+)\)\s*)?(.*)$")

PECAS = ("Quadro", "Gráfico", "Tabela", "Figura")


def carregar(caminho):
    saida = []
    for linha in Path(caminho).read_text(encoding="utf-8", errors="replace").splitlines():
        if linha.startswith("##EXTRACAO"):
            continue
        m = RE_PAR.match(linha)
        if m:
            saida.append((int(m.group(1)), None, m.group(2).strip()))
            continue
        m = RE_PAR_PDF.match(linha)
        if m:
            saida.append((int(m.group(1)),
                          int(m.group(2)) if m.group(2) else None, m.group(3).strip()))
    return saida


# --------------------------------------------------------------- as conferências

def legendas(pars):
    """Onde cada peça é apresentada: 'Quadro 7 – ...' no início do parágrafo."""
    achadas = defaultdict(list)
    for n, _pg, t in pars:
        m = re.match(r"^(%s)\s+(\d+)\s*[–—-]" % "|".join(PECAS), t)
        if m:
            achadas[(m.group(1), int(m.group(2)))].append(n)
    return achadas


def remissoes(pars):
    """Toda menção a peça numerada no corpo."""
    saida = defaultdict(list)
    for n, _pg, t in pars:
        for m in re.finditer(r"\b(%s)s?\s+(\d+)\b" % "|".join(PECAS), t):
            saida[(m.group(1), int(m.group(2)))].append(n)
    return saida


def secoes(pars):
    numeros = set()
    for n, _pg, t in pars:
        m = re.match(r"^(\d+(?:\.\d+)*)\s+[A-ZÀ-Ú]", t)
        if m:
            numeros.add(m.group(1))
    return numeros


def remissoes_secao(pars):
    saida = defaultdict(list)
    for n, _pg, t in pars:
        for m in re.finditer(r"\bse[çc][ãa]o\s+(\d+(?:\.\d+)*)", t, re.I):
            num = m.group(1)
            # "art. 217-A" e afins geram "secao 217": secao nao passa de 99
            # sem subdivisao, e o falso positivo aqui e barato de evitar.
            if "." not in num and int(num) > 99:
                continue
            saida[num].append(n)
    return saida


def percentuais(pars):
    """Recalcula 'N de M' / 'N em M' quando um percentual está na mesma frase."""
    fora = []
    for n, _pg, t in pars:
        for frase in re.split(r"(?<=[.;])\s+", t):
            m = re.search(r"\b([\d.]+)\s+(?:de|em)\s+([\d.]+)\b", frase)
            p = re.search(r"\b(\d{1,3}(?:[.,]\d+)?)\s*%", frase)
            if not (m and p):
                continue
            try:
                a = float(m.group(1).replace(".", ""))
                b = float(m.group(2).replace(".", ""))
                v = float(p.group(1).replace(",", "."))
            except ValueError:
                continue
            if b == 0 or a > b:
                continue
            calc = a / b * 100
            if abs(calc - v) > max(0.6, v * 0.02):
                fora.append((n, m.group(0), p.group(0), round(calc, 1)))
    return fora


def paginas_citadas(pars):
    """Citação a página fora do intervalo que a referência publica."""
    intervalos = {}
    for n, _pg, t in pars:
        m = re.match(r"^([A-ZÀ-Ú][A-ZÀ-Ú\s]+),\s", t)
        if not m:
            continue
        r = re.search(r"\bp\.\s*(\d+)\s*[-–]\s*(\d+)", t)
        if r:
            intervalos[m.group(1).strip()] = (int(r.group(1)), int(r.group(2)), n)
    fora = []
    for n, _pg, t in pars:
        for m in re.finditer(r"\(([A-ZÀ-Ú][A-ZÀ-Ú\s]{2,}),\s*\d{4},\s*p\.\s*(\d+)", t):
            nome, pag = m.group(1).strip(), int(m.group(2))
            if nome in intervalos:
                ini, fim, onde = intervalos[nome]
                if not (ini <= pag <= fim):
                    fora.append((n, nome, pag, ini, fim, onde))
    return fora


def main():
    ap = argparse.ArgumentParser(description="Conferência interna determinística.")
    ap.add_argument("fonte")
    ap.add_argument("--verboso", action="store_true")
    a = ap.parse_args()

    pars = carregar(a.fonte)
    if not pars:
        sys.exit("nenhum parágrafo reconhecido em %s" % a.fonte)
    print("%s: %d parágrafos, %d palavras\n"
          % (Path(a.fonte).name, len(pars), sum(len(t.split()) for _, _, t in pars)))

    achou = False
    legs, rems = legendas(pars), remissoes(pars)


    # 1. remissão a peça que não tem legenda
    # Se as legendas daquele tipo nao foram detectadas (formatacao diferente,
    # legenda dentro da imagem), toda remissao vira "orfa" e o relato e ruido.
    # Medido em 25/08/2026: num trabalho, as 27 pecas sairam como orfas porque
    # nenhuma legenda casou o padrao. Conferidor que grita em tudo nao e lido.
    tipos_vistos = {t for (t, _) in legs}
    tipos_citados = {t for (t, _) in rems}
    sem_legenda = tipos_citados - tipos_vistos
    orfas = {k: v for k, v in rems.items()
             if k not in legs and k[0] not in sem_legenda}
    if orfas:
        achou = True
        print("REMISSÃO A PEÇA SEM LEGENDA (%d)" % len(orfas))
        for (tipo, num), onde in sorted(orfas.items())[:20]:
            print("  %s %d, citado em %s" % (tipo, num, ", ".join("P%d" % x for x in onde[:6])))
        print()

    # 2. legenda repetida ou faltando na série
    for tipo in PECAS:
        nums = sorted(n for (t, n) in legs if t == tipo)
        if not nums:
            continue
        rep = [n for n, c in Counter(
            n for (t, n), v in legs.items() if t == tipo for _ in v).items() if c > 1]
        buracos = [n for n in range(min(nums), max(nums) + 1) if n not in nums]
        if rep or buracos:
            achou = True
            print("SÉRIE DE %s: %d peças, de %d a %d" % (tipo.upper(), len(nums), min(nums), max(nums)))
            if buracos:
                print("  faltam: %s" % ", ".join(str(x) for x in buracos))
            if rep:
                print("  numeradas duas vezes: %s" % ", ".join(str(x) for x in rep))
            print()

    # 3. remissão a seção inexistente
    secs, remsec = secoes(pars), remissoes_secao(pars)
    if secs:
        orf = {k: v for k, v in remsec.items() if k not in secs}
        if orf:
            achou = True
            print("REMISSÃO A SEÇÃO SEM TÍTULO CORRESPONDENTE (%d)" % len(orf))
            for k, onde in sorted(orf.items())[:15]:
                print("  seção %s, citada em %s" % (k, ", ".join("P%d" % x for x in onde[:6])))
            print()

    # 4. percentual que não sai da divisão publicada na mesma frase
    pc = percentuais(pars)
    if pc:
        achou = True
        print("PERCENTUAL QUE NÃO SAI DA DIVISÃO NA MESMA FRASE (%d)" % len(pc))
        for n, div, pct, calc in pc[:15]:
            print("  [P%d] '%s' com '%s'; a divisão dá %.1f%%" % (n, div, pct, calc))
        print()

    # 5. página citada fora do intervalo da referência
    pg = paginas_citadas(pars)
    if pg:
        achou = True
        print("PÁGINA CITADA FORA DO INTERVALO DA REFERÊNCIA (%d)" % len(pg))
        for n, nome, pagina, ini, fim, onde in pg[:15]:
            print("  [P%d] %s p. %d, e a referência em [P%d] publica p. %d-%d"
                  % (n, nome, pagina, onde, ini, fim))
        print()

    if sem_legenda:
        print("FORA DE ALCANCE: nenhuma legenda de %s foi detectada nesta extração,"
              % ", ".join(sorted(sem_legenda)))
        print("  então a conferência de remissão órfã não roda para esses tipos.")
        print("  A legenda pode estar dentro da imagem ou com outra formatação.")
        print()

    if not achou:
        print("Nada do que esta ferramenta sabe procurar apareceu.")
    print("**Silêncio aqui não é aprovação.** Ela não lê imagem, não julga categoria,")
    print("não avalia argumento. O que ela cobre é remissão, numeração, aritmética de")
    print("percentual na mesma frase, e página de citação contra a referência.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

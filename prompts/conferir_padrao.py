# -*- coding: utf-8 -*-
"""Confere se uma pagina segue o padrao visual das paginas da oficina.

POR QUE ISTO EXISTE

Em 04/09/2026 as cinco paginas publicadas usavam dois sistemas visuais: a da
Oficina em Charter sobre papel quente, as tres dos assistentes em Segoe sobre
papel frio, com outra fonte de titulo e outro acento. Havia treze tratamentos de
caixa numa pagina so, titulo de item maior que titulo de secao, e texto corrido
a 2,84 de contraste, abaixo do minimo de 4,5 da WCAG. Nada disso aparece lendo o
arquivo: aparece medindo.

O PADRAO ESTA EM PADRAO-DE-PAGINA.md. Este programa confere o que da para
conferir por leitura do arquivo, e o que exige o navegador fica dito la.

Uso:  python conferir_padrao.py <pagina.html> [outra.html ...]
"""
import io
import re
import sys

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Os valores do sistema. Mudar aqui e mudar em PADRAO-DE-PAGINA.md, nas paginas,
# e rodar este programa em todas elas.
CLARO = {
    "ground": "#FBFAF7", "surface": "#F3F1EC", "sunken": "#EAE7E0",
    "ink": "#191B1F", "ink-soft": "#3D4149", "muted": "#5F636B", "faint": "#6C7079",
    "rule": "#D9D5CC", "rule-firm": "#BFBAAE", "rule-soft": "#E6E2DA",
    "accent": "#33477E", "warn": "#8A5722", "good": "#37613F", "danger": "#A3352B",
}
ESCURO = {
    "ground": "#16171A", "surface": "#1D1F23", "sunken": "#24262B",
    "ink": "#E9E6E0", "ink-soft": "#C4C2BD", "muted": "#94979E", "faint": "#8A8D94",
    "rule": "#34373D", "rule-firm": "#454A52", "rule-soft": "#2A2D32",
    "accent": "#97AAE2", "warn": "#D3A163", "good": "#83B78D", "danger": "#E07A6E",
}
# A regua tipografica: seis degraus, e nada entre eles.
DEGRAUS = (("--t-xs", "12px"), ("--t-sm", "14px"), ("--t-md", "16.5px"),
           ("--t-lg", "19px"), ("--t-h3", "20px"), ("--t-h2", "26px"))

# Texto: tudo isto tem de passar de 4,5 sobre o papel do proprio tema.
TEXTO = ("ink", "ink-soft", "muted", "faint", "accent", "warn", "good", "danger")
PISO = 4.5


def luminancia(hexa):
    h = hexa.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    x, y = luminancia(a), luminancia(b)
    hi, lo = max(x, y), min(x, y)
    return round((hi + 0.05) / (lo + 0.05), 2)


def tokens_do_bloco(css, abre):
    """Le os tokens de um bloco que comeca em `abre`, ate a chave que o fecha."""
    i = css.find(abre)
    if i < 0:
        return None
    j = css.find("}", i)
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9A-Fa-f]{6})", css[i:j]))


def confere(caminho):
    s = io.open(caminho, encoding="utf-8").read()
    css = s[:s.find("</style>")] if "</style>" in s else s
    faltas = []

    def exige(ok, queixa):
        if not ok:
            faltas.append(queixa)

    # 1. charset. Sem ele a pagina servida fora do artifact perde todo acento.
    exige(s.lstrip("﻿").startswith('<meta charset="utf-8">'),
          "a primeira linha nao e <meta charset=\"utf-8\">")

    # 2. os tres estados de tema, e o de sistema protegido contra a escolha clara
    exige("@media (prefers-color-scheme: dark)" in css, "falta o tema do sistema")
    exige(':root:not([data-theme="light"])' in css,
          "o tema do sistema nao esta protegido por :root:not([data-theme=\"light\"])")
    exige(':root[data-theme="dark"]' in css, "falta o bloco data-theme=dark")
    exige(':root[data-theme="light"]' in css, "falta o bloco data-theme=light")

    # 3. os valores do sistema, nos dois temas
    for nome, esperado, abre in (("claro", CLARO, ":root {"),
                                 ("escuro", ESCURO, ':root[data-theme="dark"]')):
        achado = tokens_do_bloco(css, abre)
        if achado is None:
            faltas.append("nao achei o bloco %s" % abre)
            continue
        for k, v in esperado.items():
            if k not in achado:
                faltas.append("tema %s: falta --%s" % (nome, k))
            elif achado[k].upper() != v.upper():
                faltas.append("tema %s: --%s e %s, e o sistema diz %s"
                              % (nome, k, achado[k], v))

    # 4. contraste do texto sobre o proprio papel, nos dois temas
    for nome, t in (("claro", CLARO), ("escuro", ESCURO)):
        for k in TEXTO:
            c = contraste(t[k], t["ground"])
            if c < PISO:
                faltas.append("tema %s: --%s da %.2f sobre o papel, e o piso e %.1f"
                              % (nome, k, c, PISO))

    # 5. corpo, medida e a regua de seis degraus
    exige(re.search(r"body\s*\{[^}]*font-size:\s*var\(--t-md\)", css), "o corpo nao esta no degrau --t-md")
    exige(re.search(r"body\s*\{[^}]*font-family:\s*var\(--sans\)", css),
          "o corpo nao esta na fonte sem serifa do sistema")
    exige("--measure: 66ch" in css, "a medida nao e 66ch")
    exige("escala do sistema" in css, "falta o bloco da escala de titulos")
    for token, valor in DEGRAUS:
        exige(re.search(r"%s:\s*%s\s*;" % (token, re.escape(valor)), css),
              "o degrau %s nao e %s" % (token, valor))
    exige(re.search(r"h1[^{]*\{[^}]*clamp\(34px, 5vw, 48px\)", css), "o h1 foge da escala")
    exige(re.search(r"h2[^{]*\{[^}]*font-size:\s*var\(--t-h2\)", css), "o h2 foge da escala")
    exige(re.search(r"h3[^{]*\{[^}]*font-size:\s*var\(--t-h3\)", css), "o h3 foge da escala")

    # 5b. nenhum tamanho fora da regua, e mono so em texto de maquina
    for tam in re.findall(r"font-size:\s*([^;}]+)", css):
        t = tam.strip()
        if not (t.startswith("var(--t-") or t.startswith("clamp(") or t == "inherit"):
            faltas.append("tamanho fora da regua: %s" % t)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if "var(--mono)" in m.group(2):
            sel = " ".join(m.group(1).split())
            if not re.search(r"code|pre|textarea|\.mono|\.loc|\.cmd|\.pedido-txt|\.prompt", sel):
                faltas.append("mono fora de texto de maquina: %s" % sel[:40])

    # 6. restos do sistema antigo, que passam despercebidos por serem parecidos
    for velho in ("#eef0ef", "#e4e7e5", "#141c24", "#3e6b7a", "#93969D", "Constantia,"):
        if velho.lower() in css.lower():
            faltas.append("resta o valor antigo %s" % velho)

    return faltas


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    # Controle positivo: uma pagina com um token trocado tem de ser reprovada.
    exemplo = io.open(sys.argv[1], encoding="utf-8").read()
    sujo = exemplo.replace("--ink:         #191B1F", "--ink:         #93969D", 1)
    if sujo == exemplo:
        sys.exit("RECUSADO: nao consegui montar o controle positivo nesta pagina.")
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".html")
    os.close(fd)
    io.open(tmp, "w", encoding="utf-8").write(sujo)
    if not confere(tmp):
        os.remove(tmp)
        sys.exit("RECUSADO: o controle positivo passou, e a conferencia nao esta enxergando.")
    os.remove(tmp)
    print("  controle positivo: passou")

    ruim = 0
    for caminho in sys.argv[1:]:
        faltas = confere(caminho)
        print("  %-20s %s" % (caminho, "conforme" if not faltas else "%d fora do padrao" % len(faltas)))
        for f in faltas:
            print("       %s" % f)
        ruim += len(faltas)
    if ruim:
        sys.exit(1)


if __name__ == "__main__":
    main()

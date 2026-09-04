# -*- coding: utf-8 -*-
"""Retira da folha de estilo as regras que nenhum elemento da pagina usa.

POR QUE ISTO EXISTE

As paginas crescem por acrescimo, e o estilo de uma versao anterior fica. Em
04/09/2026 a pagina do Luis carregava 46 classes sem uso, restos de quando ela
era um painel com barra lateral e resultados, e 17 seletores definidos duas ou
tres vezes com valores diferentes. Nada disso muda um pixel: o dano e na proxima
edicao, quando quem for mexer no espacamento de um titulo edita a definicao
errada duas vezes antes de achar a que vale.

O QUE ELE FAZ, E O QUE ELE NAO FAZ

Retira uma regra quando a classe que a nomeia nao aparece em nenhum atributo
class do corpo. Nao mexe em seletor de elemento (h1, p, section), nao mexe em
id, nao junta as definicoes repetidas e nao reordena nada: unir duas definicoes
do mesmo seletor exige decidir qual valor vale, e isso e julgamento, nao
varredura.

A TRAVA

O corpo e comparado antes e depois, byte a byte: se ele mudou, o programa
recusa a gravacao. E cada classe retirada e reprocurada no corpo ja limpo. Sem
isso, a limpeza que quebra a pagina se descobre olhando.

Uso:  python limpar_css.py <pagina.html> [--gravar]
"""
import argparse
import io
import re
import sys

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Uma regra e o seletor mais o bloco. So se olha a regra de classe simples:
# ".foo", ".foo:hover", ".foo .bar", ".foo[aria-pressed]". Regra que mistura
# classe e elemento ("table.dados td") entra pela classe que a inicia.
RE_REGRA = re.compile(r"(?P<sel>[^{}@]+?)\s*\{(?P<corpo>[^{}]*)\}", re.S)


def classes_do_corpo(corpo):
    usadas = set()
    for grupo in re.findall(r'class="([^"]+)"', corpo):
        usadas.update(grupo.split())
    # Classe posta por programa tambem conta.
    for nome in re.findall(r'classList\.(?:add|toggle|remove)\("([^"]+)"', corpo):
        usadas.add(nome)
    for nome in re.findall(r'querySelector(?:All)?\("\.([A-Za-z0-9_-]+)', corpo):
        usadas.add(nome)
    return usadas


def classes_do_seletor(sel):
    """As classes que aparecem no seletor, em qualquer posicao."""
    return set(re.findall(r"\.([A-Za-z][A-Za-z0-9_-]*)", sel))


def limpar(html):
    i = html.index("<style>")
    j = html.index("</style>")
    css, corpo = html[i + len("<style>"):j], html[j:]
    # O prompt embutido nao e corpo da pagina, e traz palavras que enganariam.
    corpo_util = re.sub(r"const P_UNICO = \".*", "", corpo, flags=re.S)
    usadas = classes_do_corpo(corpo_util)

    fora, saida, pos = [], [], 0
    for m in RE_REGRA.finditer(css):
        sel = m.group("sel").strip()
        # Preserva o que nao e regra de classe: @media, :root, elementos, ids.
        if sel.startswith("@") or "{" in sel:
            continue
        # A lista de seletores se avalia parte a parte: ".a, .b" sao duas
        # regras escritas juntas, e uma pode alcancar algo e a outra nao.
        partes = [x.strip() for x in sel.split(",") if x.strip()]
        if not any(classes_do_seletor(x) for x in partes):
            continue
        vivas = []
        for parte in partes:
            cls = classes_do_seletor(parte)
            # Num seletor composto ou descendente, TODAS as classes precisam
            # existir para ele casar: ".metrica .v.alerta" nao alcanca nada se
            # ".metrica" nao esta em lugar nenhum, ainda que ".alerta" esteja.
            if cls and not cls.issubset(usadas):
                continue
            vivas.append(parte)
        if vivas == partes:
            continue
        if vivas:
            troca = ", ".join(vivas) + " {" + m.group("corpo") + "}"
            saida.append((m.start(), m.end(), troca))
            fora.append("(parcial) " + " | ".join(x for x in partes if x not in vivas))
        else:
            saida.append((m.start(), m.end(), ""))
            fora.append(sel)

    novo = css
    for a, b, troca in reversed(saida):
        novo = novo[:a] + troca + novo[b:]
    # Bloco de media que ficou sem nenhuma regra dentro nao faz nada.
    novo = re.sub(r"@media[^{]*\{\s*\}\s*", "", novo)
    novo = re.sub(r"\n{3,}", "\n\n", novo)
    return html[:i + len("<style>")] + novo + corpo, fora, corpo


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pagina")
    p.add_argument("--gravar", action="store_true")
    a = p.parse_args()

    html = io.open(a.pagina, encoding="utf-8").read()
    novo, fora, corpo_antes = limpar(html)

    # Trava 1: o corpo nao pode ter mudado.
    corpo_depois = novo[novo.index("</style>"):]
    if corpo_antes != corpo_depois:
        sys.exit("RECUSADO: o corpo da pagina mudou, e este programa so mexe no estilo.")

    # Trava 2: todo seletor retirado precisa ter ao menos uma classe ausente do
    # corpo, que e o que o impede de alcancar qualquer elemento. Conferir classe
    # a classe seria errado: ".top .privacidade" sai porque .privacidade nao
    # existe, e .top continua em uso noutras regras.
    usadas = classes_do_corpo(re.sub(r"const P_UNICO = \".*", "", corpo_depois, flags=re.S))
    for sel in fora:
        for parte in sel.replace("(parcial) ", "").split("|"):
            cls = classes_do_seletor(parte)
            if cls and cls.issubset(usadas):
                sys.exit("RECUSADO: o seletor %s alcanca elementos e foi retirado."
                         % " ".join(parte.split()))

    # Controle positivo: uma classe inventada tem de ser dada como morta.
    teste = html.replace("</style>", ".zzz-classe-que-nao-existe { color: red; }\n</style>")
    _, fora_teste, _ = limpar(teste)
    if not any("zzz-classe-que-nao-existe" in s for s in fora_teste):
        sys.exit("RECUSADO: o controle positivo falhou, e a varredura nao esta enxergando.")

    css_antes = len(html[html.index("<style>"):html.index("</style>")])
    css_depois = len(novo[novo.index("<style>"):novo.index("</style>")])
    print("  controle positivo: passou")
    print("  regras retiradas: %d" % len(fora))
    for sel in fora:
        print("     %s" % " ".join(sel.split()))
    print("  CSS: %d -> %d bytes (%.0f%% menor)"
          % (css_antes, css_depois, 100 * (1 - css_depois / css_antes)))
    if a.gravar:
        io.open(a.pagina, "w", encoding="utf-8").write(novo)
        print("  gravado em %s" % a.pagina)
    else:
        print("  (nada gravado; use --gravar)")


if __name__ == "__main__":
    main()

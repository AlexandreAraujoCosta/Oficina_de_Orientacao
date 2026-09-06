# -*- coding: utf-8 -*-
"""Tira as figuras do .docx e diz, de cada uma, onde ela esta e o que a legenda diz.

POR QUE ISTO EXISTE

Medido em 06/09/2026. A leitura das figuras era feita pagina a pagina no PDF, uma
chamada por pagina, e a imagem vinha reduzida junto com o resto da folha. Tres
coisas mudam quando as figuras saem do `.docx`:

    resolucao   a imagem vem como o autor a inseriu, com os rotulos de dado
                legiveis um a um. Rotulo truncado ali e defeito do trabalho;
                rotulo ilegivel numa pagina de PDF pode ser so a reducao.
    custo       a restricao de chamada paralela e da leitura de PAGINA DE PDF,
                nao da de arquivo de imagem. Seis imagens pedidas na mesma
                mensagem voltaram as seis, medido no mesmo dia. As figuras de um
                trabalho passam a caber em uma ou duas chamadas.
    endereco    aqui, porque `word/media/` guarda as imagens na ordem de
                insercao e sem legenda nenhuma. Este programa casa cada arquivo
                com o paragrafo em que ele aparece e com a legenda vizinha.

O QUE ELE NAO FAZ

Nao le a figura, e nao diz se ela mostra o que a prosa afirma. Isso e da leitura,
e e por isso que a saida traz o caminho de cada arquivo: para que a leitura peca
todas as imagens numa mensagem so, ja sabendo qual e qual.

Uso:
    python scripts/figuras_do_docx.py <trabalho.docx> [--extracao extracao.txt]
    python scripts/figuras_do_docx.py <trabalho.docx> --saida pasta_das_figuras
"""
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# A legenda de figura, tabela ou grafico, nas formas que o acervo traz. O numero
# pode vir depois de traco, ponto ou espaco, e o tipo pode vir em caixa alta.
# O identificador nem sempre e numero. Numa tese do acervo as figuras sao
# "Figure A", "Figure B" e tres delas "Figure X", o que e defeito do trabalho e
# nao do programa: exigir digito deixava treze figuras sem legenda reconhecida.
RE_LEGENDA = re.compile(
    r"^\s*(Gr[áa]fico|Figura|Tabela|Quadro|Imagem|Chart|Table|Figure)"
    r"\s*(\d{1,3}|[A-Z]|[IVXL]{1,5})\s*[-–—.:]\s*(.*)$"
    r"|^\s*(Gr[áa]fico|Figura|Tabela|Quadro|Imagem|Chart|Table|Figure)"
    r"\s*(\d{1,3})\s*(.*)$", re.I)


def paragrafos_do_docx(caminho):
    """Devolve, na ordem, (texto, lista de arquivos de imagem) de cada paragrafo."""
    with zipfile.ZipFile(caminho) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
    alvo = {}
    for m in re.finditer(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels):
        alvo[m.group(1)] = m.group(2).split("/")[-1]
    fora = []
    for mp in re.finditer(r"<w:p[ >].*?</w:p>|<w:p[^>]*/>", xml, re.S):
        bloco = mp.group(0)
        texto = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", bloco, re.S))
        texto = re.sub(r"<[^>]+>", "", texto)
        imgs = [alvo.get(r) for r in re.findall(r'r:embed="([^"]+)"', bloco)]
        fora.append((texto.strip(), [i for i in imgs if i]))
    return fora


def localizador(texto, extracao):
    """Acha o [P###] do paragrafo, casando o comeco do texto contra a extracao."""
    if not texto or not extracao:
        return None
    chave = re.sub(r"<!--.*?-->", " ", texto).replace("**", " ")
    chave = re.sub(r"^\W+|\W+$", "", re.sub(r"\s+", " ", chave))[:60]
    # Legenda curta ("Grafico 1") e comum, e recusa-la deixava toda figura sem
    # endereco. Ela vale quando casa o PARAGRAFO INTEIRO, e nao um pedaco: assim
    # "Grafico 1" nao casa dentro de "Grafico 1 mostra que", que e prosa.
    inteiro = len(chave) < 12

    def limpar(s):
        # A extracao marca titulo sem estilo com ** e um comentario de HTML:
        #     **[P443] Grafico 1**  <!-- pseudo-titulo, sem estilo -->
        # Sem tirar os dois, "Grafico 1" nunca casa o paragrafo inteiro.
        s = re.sub(r"<!--.*?-->", " ", s)
        s = s.replace("**", " ").replace("`", " ")
        return re.sub(r"^\W+|\W+$", "", re.sub(r"\s+", " ", s))

    def bate(alvo):
        alvo = limpar(alvo)
        return alvo == chave if inteiro else chave in alvo

    for m in re.finditer(r"\[P(\d+)\]([^\n]*)", extracao):
        if bate(re.sub(r"\s+", " ", m.group(2))):
            return int(m.group(1))
    for m in re.finditer(r"^\[[^\]]+\]\s*P(\d+)(?:\s*\[[A-Z]+\])?"
                         r"(?:\s*\(p\.[^)]*\))?\s*([^\n]*)", extracao, re.M):
        if bate(re.sub(r"\s+", " ", m.group(2))):
            return int(m.group(1))
    return None


def autoteste():
    """Prova o leitor de legenda com um caso que tem de casar e um que nao pode."""
    falhas = []
    for bom in ("Gráfico 22 – Decisões por ano", "TABELA 4 - Distribuição",
                "Figura 2: série histórica", "Chart 3 Something"):
        if not RE_LEGENDA.match(bom):
            falhas.append("nao reconhece legenda: %r" % bom)
    for mau in ("O gráfico acima mostra que", "Tabelas de contingência sobre",
                "A figura de duração é apresentada"):
        if RE_LEGENDA.match(mau):
            falhas.append("confunde prosa com legenda: %r" % mau)
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("--extracao", help="para dar o [P###] de cada figura")
    ap.add_argument("--saida", help="pasta onde gravar as imagens "
                                    "(padrão: figuras-<nome do trabalho>)")
    ap.add_argument("--vizinhanca", type=int, default=3,
                    help="quantos parágrafos procurar antes e depois pela legenda")
    a = ap.parse_args()

    falhas = autoteste()
    if falhas:
        print("  o proprio leitor de legenda esta quebrado, e nao reporto nada:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste: reconhece as quatro escritas de legenda e nao confunde "
          "prosa com legenda")

    doc = Path(a.docx)
    saida = Path(a.saida) if a.saida else doc.with_name("figuras-" + doc.stem)
    saida.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(doc)) as z:
        nomes = [n for n in z.namelist() if n.startswith("word/media/")]
        for n in nomes:
            destino = saida / Path(n).name
            destino.write_bytes(z.read(n))
    print("  %d arquivo(s) de imagem em %s\n" % (len(nomes), saida))

    ext = ""
    if a.extracao and Path(a.extracao).exists():
        ext = io.open(a.extracao, encoding="utf-8", errors="replace").read()

    ps = paragrafos_do_docx(str(doc))
    linhas = []
    for i, (texto, imgs) in enumerate(ps):
        for img in imgs:
            legenda, loc = "", None
            for d in list(range(0, a.vizinhanca + 1)) + \
                     [-x for x in range(1, a.vizinhanca + 1)]:
                j = i + d
                if 0 <= j < len(ps):
                    m = RE_LEGENDA.match(ps[j][0])
                    if m:
                        legenda = re.sub(r"\s+", " ", ps[j][0])[:96]
                        loc = localizador(ps[j][0], ext)
                        break
            if loc is None:
                loc = localizador(texto, ext)
            linhas.append((img, loc, legenda))

    print("  %-16s %-9s %s" % ("arquivo", "onde", "legenda vizinha"))
    for img, loc, legenda in linhas:
        print("  %-16s %-9s %s" % (img, ("[P%d]" % loc) if loc else "—",
                                   legenda or "(sem legenda por perto)"))
    sem = [l for l in linhas if not l[2]]
    print("\n  %d figura(s) no corpo; %d sem legenda reconhecida por perto."
          % (len(linhas), len(sem)))
    orfas = len(nomes) - len({l[0] for l in linhas})
    if orfas > 0:
        print("  %d arquivo(s) em word/media/ nao aparecem no corpo: cabeçalho, "
              "logotipo ou imagem removida." % orfas)
    print("\n  Peça as imagens que interessam NUMA MENSAGEM SÓ: a restrição de "
          "chamada\n  paralela é da página de PDF, e não do arquivo de imagem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

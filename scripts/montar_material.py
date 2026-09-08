# -*- coding: utf-8 -*-
"""Monta, uma vez, o material que as leituras hoje buscam cada uma por sua conta.

POR QUE ISTO EXISTE

Medido em 08/09/2026, sobre a dissertacao R. As tres leituras iniciais do
Luis citaram 89, 116 e 61 paragrafos, com **62% a 64% de sobreposicao** entre cada
par e 31 paragrafos citados pelas tres. Nao e desperdicio de leitura: um punhado de
paragrafos carrega o trabalho, e cada voz tem de passar por eles. **O desperdicio e
de montagem**: as tres extrairam as figuras separadamente, abriram a extracao
separadamente e buscaram separadamente.

Este programa faz a montagem uma vez. Cada voz le um arquivo e abre as imagens numa
mensagem so, em vez de ir buscar.

O QUE ELE NAO FAZ, e a distincao importa

Ele **nao recorta** por leitura. Uma conferencia sabe de que paragrafos precisa,
porque sao os que os itens citam; uma leitura nao sabe, e descobrir e o trabalho
dela. Entregar a fatia que eu achar que serve seria decidir por ela o que ela tem
de achar. Entao vai o trabalho inteiro, na ordem, e a voz escolhe.

E ele nao julga nada: junta, numera e diz o que nao conseguiu.

Uso:
    python scripts/montar_material.py <trabalho.docx> <extracao.txt> -o MATERIAL.md
    python scripts/montar_material.py <trabalho.docx> <extracao.txt> -o M.md --mapa MAPA.md
"""
import argparse
import io
import os
import re
import subprocess
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

AQUI = Path(__file__).resolve().parent


def paragrafos(caminho):
    """Le as duas escritas de extracao, e le TAMBEM o bloco de notas do fim."""
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    ps = {}
    for m in re.finditer(r"(?m)^[^\[\n]{0,10}\[P(\d+)\]\s*(.*)$", t):
        ps[int(m.group(1))] = " ".join(m.group(2).split())
    if not ps:
        for m in re.finditer(
                r"(?m)^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\])?\s*(?:\(p\.[^)]*\))?\s*(.*)$", t):
            ps[int(m.group(1))] = " ".join(m.group(2).split())
    notas = {}
    for m in re.finditer(r"(?m)^[^\[\n]{0,10}\[nota (\d+)\]\s*(.*)$", t):
        notas[int(m.group(1))] = " ".join(m.group(2).split())
    return ps, notas


def titulos(ps):
    """Os paragrafos que sao titulo de secao, pela numeracao que o trabalho usa.

    O teto de palavras existe para nao tomar por titulo o paragrafo que comeca por
    numero, e ele era de vinte. **Titulo de secao academica passa disso**: medido em
    08/09/2026, o do capitulo empirico do trabalho R ([P428]) e o da subsecao 3.5
    ([P420]) ficaram de fora do sumario, e uma leitura que se orientasse por ele
    perderia a abertura do nucleo do trabalho. Quem achou foi a leitura que usou o
    material, e nao um teste meu.
    """
    fora = []
    for n in sorted(ps):
        t = ps[n]
        if re.match(r"^\d+(\.\d+)*[.\s–-]", t) and len(t.split()) <= 40:
            fora.append((n, t))
    return fora


def figuras(docx, extracao):
    """Chama o casador de figuras e devolve as linhas dele, ou o motivo de nao ter."""
    prog = AQUI / "figuras_do_docx.py"
    if not prog.exists():
        return None, "figuras_do_docx.py nao esta em %s" % AQUI
    try:
        r = subprocess.run([sys.executable, str(prog), docx, "--extracao", extracao],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300)
    except Exception as e:
        return None, "o casador de figuras falhou: %s" % e
    if r.returncode not in (0, 1):
        return None, "o casador de figuras saiu com codigo %d" % r.returncode
    return r.stdout, None


def autoteste():
    falhas = []
    import tempfile
    ext = ("#### [P1] 1. Introducao\n\n[P2] Texto do primeiro paragrafo.\n\n"
           "[P3] 2.1 Uma subsecao\n\n[P4] Outro paragrafo.\n\n"
           "[P5] 4 A SELECAO DOS RECURSOS REPRESENTATIVOS DA CONTROVERSIA "
           "ANALISE EMPIRICA DAS DECISOES DE AFETACAO PROFERIDAS PELOS "
           "TRIBUNAIS DE ORIGEM ENTRE DOIS MIL E CATORZE E DOIS MIL E VINTE\n\n"
           "[nota 5] Cf. Nino, 2003.\n")
    p = Path(tempfile.gettempdir()) / "_mat_ext.txt"
    p.write_text(ext, encoding="utf-8")
    try:
        ps, nt = paragrafos(str(p))
        if sorted(ps) != [1, 2, 3, 4, 5]:
            falhas.append("nao le os paragrafos, inclusive sob cerquilhas: %r" % sorted(ps))
        if 5 not in nt:
            falhas.append("nao le a nota de rodape")
        ts = [n for n, _ in titulos(ps)]
        # [P5] e um titulo de secao longo, e um teto de vinte palavras o perdia
        if ts != [1, 3, 5]:
            falhas.append("nao reconhece os titulos numerados, "
                          "inclusive o longo: %r" % ts)
        # CONTROLE POSITIVO: paragrafo comum nao pode virar titulo
        if 2 in ts or 4 in ts:
            falhas.append("toma paragrafo de texto por titulo")
    finally:
        try:
            p.unlink()
        except Exception:
            pass
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("extracao")
    ap.add_argument("-o", "--saida", required=True)
    ap.add_argument("--mapa", help="o MAPA.md, se já existir, para entrar no cabeçalho")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio montador esta quebrado, e nao monto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: le paragrafo sob cerquilhas, le nota de rodape, reconhece "
          "titulo numerado e nao toma paragrafo de texto por titulo")

    ps, notas = paragrafos(a.extracao)
    if not ps:
        print("  nao reconheci nenhum paragrafo em %s" % a.extracao)
        return 2
    figs, erro_fig = figuras(a.docx, a.extracao)

    out = []
    out.append("# Material da leitura: tudo num arquivo\n")
    out.append("Trabalho: `%s`" % Path(a.docx).name)
    out.append("Extração: `%s` — %d parágrafos com texto, de [P%d] a [P%d], mais %d nota(s)."
               % (Path(a.extracao).name, len(ps), min(ps), max(ps), len(notas)))
    out.append("\n**Você não precisa ir buscar passagem: ela está aqui.** O trabalho "
               "inteiro está abaixo, na ordem, com o número de parágrafo que é o "
               "endereço que você usa. Nem todo número existe: parágrafo sem texto "
               "não recebe marcador, e afirmar que um localizador está morto sem "
               "conferir aqui é erro.\n")

    ts = titulos(ps)
    if ts:
        out.append("## O sumário, tal como o trabalho o escreve\n")
        for n, t in ts:
            out.append("  [P%d]  %s" % (n, t[:96]))
        out.append("")

    if figs:
        out.append("## As figuras, já extraídas do `.docx`\n")
        out.append("O endereço de uma figura é o parágrafo da legenda, entre colchetes. "
                   "A posição da imagem não é endereço. **Peça as imagens numa mensagem "
                   "só**, e não uma por vez.\n")
        out.append("```")
        # Só a tabela. O autoteste do casador é diagnóstico da ferramenta, e ocupava
        # vinte linhas do cabeçalho sem mudar nada no que a leitura faz. Apontado em
        # 08/09/2026 pela leitura que usou este material.
        util = [l for l in figs.split("\n")
                if not re.match(r"\s*(autoteste|reconhece|conta |endere[cç]a|recusa|"
                                r"junta|alinhamento|casa )", l)]
        out.append("\n".join(util).strip())
        out.append("```\n")
        out.append("As imagens estão em `%s`.\n"
                   % (Path(a.docx).parent / ("figuras-" + Path(a.docx).stem)))
    else:
        out.append("## As figuras\n\n**Não consegui montar a tabela de figuras:** %s\n"
                   % (erro_fig or "motivo não registrado"))

    if a.mapa and Path(a.mapa).exists():
        out.append("## O mapa estrutural\n")
        out.append(io.open(a.mapa, encoding="utf-8", errors="replace").read())
        out.append("")

    out.append("=" * 78)
    out.append("O TRABALHO, NA ORDEM")
    out.append("=" * 78 + "\n")
    for n in sorted(ps):
        out.append("[P%d] %s\n" % (n, ps[n]))
    if notas:
        out.append("-" * 78)
        out.append("AS NOTAS DE RODAPÉ\n")
        for n in sorted(notas):
            out.append("[nota %d] %s\n" % (n, notas[n]))

    texto = "\n".join(out)
    io.open(a.saida, "w", encoding="utf-8").write(texto)
    print("\n  %s  (%d palavras)" % (a.saida, len(texto.split())))
    print("  %d parágrafos, %d nota(s), %d título(s)%s"
          % (len(ps), len(notas), len(ts),
             ", tabela de figuras incluída" if figs else ", SEM tabela de figuras"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Renderiza paginas de um PDF em PNG, para que graficos e tabelas sejam lidos.

POR QUE ISTO EXISTE

`analisar_pdf.py texto` devolve a camada textual, e num trabalho empirico a
camada textual traz a legenda do grafico e nao o grafico. Em `.docx` as imagens
estao embutidas e sao lidas direto do arquivo; em PDF de repositorio, nao. Sem
esta ferramenta o alcance do instrumento depende do formato em que o trabalho
chegou, o que e diferenca de suporte lida como diferenca de trabalho, e
contamina qualquer comparacao entre dissertacoes.

O que se renderiza e a pagina inteira, e nao a imagem extraida. Grafico
vetorial nao e uma imagem embutida: e um conjunto de tracos desenhados na
pagina, e extrair "as imagens" de um PDF assim devolve nada ou devolve pedacos.
Renderizar a pagina resolve os dois casos e ainda preserva legenda, eixo e nota
de rodape no mesmo quadro, que e o que se precisa para conferir rotulo contra
texto.

Uso:
    python renderizar_paginas.py <arquivo.pdf> <paginas> [--saida DIR] [--dpi N]

<paginas> aceita "100", "95-105", "38,66,95-100". Numeracao de pagina do PDF,
que e a mesma que `analisar_pdf.py` imprime como (p.N).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF nao esta instalado. `pip install pymupdf`")


def expandir(spec, maximo):
    """'38,66,95-100' -> [38, 66, 95, ..., 100], sem repetir e dentro do limite."""
    paginas = []
    for parte in re.split(r"[,\s]+", spec.strip()):
        if not parte:
            continue
        m = re.fullmatch(r"(\d+)(?:\s*[-–]\s*(\d+))?", parte)
        if not m:
            sys.exit(f"trecho de pagina invalido: {parte!r}")
        ini = int(m.group(1))
        fim = int(m.group(2)) if m.group(2) else ini
        if fim < ini:
            ini, fim = fim, ini
        paginas.extend(range(ini, fim + 1))
    vistas, saida = set(), []
    for p in paginas:
        if p in vistas:
            continue
        vistas.add(p)
        if 1 <= p <= maximo:
            saida.append(p)
        else:
            print(f"  aviso: pagina {p} fora do documento (1 a {maximo})")
    return saida


def main():
    ap = argparse.ArgumentParser(description="Renderiza paginas de PDF em PNG.")
    ap.add_argument("pdf")
    ap.add_argument("paginas", help='"100", "95-105" ou "38,66,95-100"')
    ap.add_argument("--saida", help="diretorio (padrao: paginas-<nome do pdf>)")
    ap.add_argument("--dpi", type=int, default=160,
                    help="padrao 160; abaixo de 120 rotulo de grafico fica ilegivel")
    a = ap.parse_args()

    caminho = Path(a.pdf)
    if not caminho.exists():
        sys.exit(f"nao encontrei {caminho}")

    doc = fitz.open(caminho)
    alvos = expandir(a.paginas, doc.page_count)
    if not alvos:
        sys.exit("nenhuma pagina valida na selecao")

    destino = Path(a.saida) if a.saida else Path(f"paginas-{caminho.stem}")
    destino.mkdir(parents=True, exist_ok=True)

    escala = a.dpi / 72.0
    matriz = fitz.Matrix(escala, escala)

    for n in alvos:
        pagina = doc[n - 1]  # fitz indexa de zero; (p.N) conta de um
        pix = pagina.get_pixmap(matrix=matriz)
        arquivo = destino / f"p{n:04d}.png"
        pix.save(arquivo)
        print(f"  p.{n} -> {arquivo} ({pix.width}x{pix.height})")

    doc.close()
    print(f"{len(alvos)} paginas em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

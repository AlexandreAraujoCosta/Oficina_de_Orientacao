"""Para cada citacao ausente do PDF de origem, procura nos demais PDFs da pasta.

Se o trecho aparecer em outro trabalho, e contaminacao entre leituras simultaneas.
Se nao aparecer em nenhum, e citacao imprecisa, parafrase entre aspas ou estrago
de extracao, que sao problemas de outra natureza.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from conferir_citacoes import casar, citacoes, normalizar, texto_do_pdf  # noqa: E402


def main():
    pasta_rel, pasta_pdf = Path(sys.argv[1]), Path(sys.argv[2])
    minimo = int(sys.argv[3]) if len(sys.argv) > 3 else 40

    pdfs = sorted(pasta_pdf.rglob("*.pdf"))
    print(f"Indexando {len(pdfs)} PDFs da pasta {pasta_pdf.name}...")
    textos = {p: texto_do_pdf(p) for p in pdfs}

    contaminacao = 0
    for rel in sorted(pasta_rel.glob("p*.md")):
        origem = casar(rel, pdfs)
        if origem is None:
            continue
        corpo = rel.read_text(encoding="utf-8", errors="replace")
        for c in citacoes(corpo, minimo):
            n = normalizar(c)
            if n in textos[origem]:
                continue
            partes = [p.strip() for p in n.replace("…", "...").split("...") if len(p.strip()) >= 20]
            if partes and all(p in textos[origem] for p in partes):
                continue
            alheios = [p.name for p in pdfs if p != origem and (
                n in textos[p] or (partes and all(x in textos[p] for x in partes)))]
            recorte = c[:100].replace("\n", " ")
            if alheios:
                contaminacao += 1
                print(f"  !! {rel.name}: trecho existe em {', '.join(alheios)}")
                print(f"     {recorte}")
            else:
                print(f"  -- {rel.name}: nao existe em nenhum PDF da pasta")
                print(f"     {recorte}")

    print()
    print(f"Trechos localizados em OUTRO trabalho da pasta: {contaminacao}")


if __name__ == "__main__":
    main()

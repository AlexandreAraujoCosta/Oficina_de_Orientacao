# -*- coding: utf-8 -*-
"""Mapeia cada paragrafo do trabalho na pagina em que ele sai impresso.

POR QUE ISTO EXISTE

O localizador `[P123]` e da extracao, e nao existe dentro do Word nem dentro do
PDF: quem recebe o relatorio nao tem como converte-lo em lugar. Quem recebeu a
primeira entrega disse, em 28/08/2026, que preferiu achar os erros de portugues
pelo PDF, "que indica a pagina em que esta o erro". A pagina e o endereco que a
pessoa ja sabe usar.

COMO

O paragrafo e localizado no PDF pelo proprio texto, e nao por contagem: o
programa procura as primeiras palavras do paragrafo, copiadas do arquivo, e
anota a pagina em que elas aparecem. Nada aqui e redigitado por modelo.

A ORDEM IMPORTA, E E A UNICA ARMADILHA

A paginacao vale para a versao que gerou o PDF. Como este programa nao altera o
trabalho, basta que o PDF saia do mesmo `.docx` que esta sendo comentado. Se
alguem aplicar as correcoes antes de paginar, as paginas mudam e o mapa passa a
apontar para o lugar errado sem acusar nada.

    python scripts/paginas.py trabalho.docx
    python scripts/paginas.py trabalho.docx --pdf trabalho.pdf

Sem `--pdf`, o programa pede ao Word instalado que exporte o arquivo. Sem Word e
sem PDF, ele para e diz que parou: mapa pela metade e pior que mapa nenhum.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anotar_docx import W, Styles, collect_paragraphs, load  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def texto_de(p):
    return (p.text if hasattr(p, "text") else str(p)).strip()


def normal(s):
    """Sem acento e sem pontuacao, para comparar o que o PDF quebrou diferente."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def exportar(docx):
    """Pede ao Word que grave o PDF, e devolve o caminho.

    Word e nao LibreOffice porque e o que pagina igual ao que o autor ve: a
    quebra de pagina depende da fonte e do motor de layout, e um PDF paginado
    por outro programa daria pagina que nao confere com a tela de quem escreveu.
    """
    # Dispatch dinamico, e nao o comum: o Dispatch normal gera um cache de
    # tipos em gen_py que corrompe com facilidade, e a partir dai toda chamada
    # falha com um erro sobre um modulo que ninguem escreveu. O dinamico nao usa
    # esse cache. Medido em 28/08/2026, quando a segunda execucao do dia parou
    # de exportar sem que nada tivesse mudado.
    import win32com.client.dynamic
    destino = Path(docx).with_suffix(".pdf").resolve()
    try:
        word = win32com.client.dynamic.Dispatch("Word.Application")
    except Exception:
        # O cache de tipos corrompe sozinho, e a partir dai toda chamada falha
        # com um erro sobre um modulo que ninguem escreveu. Apagar o cache e o
        # conserto, e o programa faz isso uma vez antes de desistir.
        import shutil
        import tempfile
        shutil.rmtree(Path(tempfile.gettempdir()) / "gen_py", ignore_errors=True)
        word = win32com.client.dynamic.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(Path(docx).resolve()), ReadOnly=True)
        doc.SaveAs(str(destino), FileFormat=17)   # 17 = PDF
        doc.Close(False)
    finally:
        word.Quit()
    return destino


def mapear(pdf, pars, minimo=18):
    """{numero do paragrafo: pagina}, e a lista dos que nao foram achados."""
    import fitz
    doc = fitz.open(pdf)
    paginas = [normal(pg.get_text()) for pg in doc]
    doc.close()

    mapa, perdidos, cursor = {}, [], 0
    for i, p in enumerate(pars, 1):
        alvo = normal(texto_de(p))
        if len(alvo) < minimo:
            continue
        palavras = alvo.split()
        # A busca comeca na pagina do paragrafo anterior, porque o texto corre em
        # ordem: procurar sempre do inicio acha a ocorrencia errada quando a
        # mesma frase se repete, o que e comum em legenda de serie de graficos.
        # Em degraus, porque a agulha longa atravessa a quebra de pagina: a
        # legenda do Grafico 58 comeca numa pagina e termina na seguinte, e as
        # doze palavras so ficam inteiras na entrada do indice, la na frente do
        # arquivo. Encurtando, a ocorrencia do corpo aparece.
        onde = []
        for tamanho in (12, 7, 4):
            agulha = " ".join(palavras[:tamanho])
            if len(agulha) < 12:
                break
            onde = [j + 1 for j, pg in enumerate(paginas) if agulha in pg]
            if [x for x in onde if x - 1 >= cursor]:
                break
        # Titulo de secao aparece duas vezes no PDF, no sumario e no corpo, e a
        # primeira ocorrencia e sempre a do sumario. Escolher a primeira punha o
        # capitulo 7 na pagina 10. Vale a primeira a partir de onde o texto ja
        # estava, porque o documento corre em ordem; nao havendo nenhuma
        # adiante, vale a ultima, que nunca e a entrada de sumario.
        adiante = [x for x in onde if x - 1 >= cursor]
        achou = adiante[0] if adiante else (onde[-1] if onde else None)
        if achou is None:
            perdidos.append(i)
        else:
            mapa[i] = achou
            cursor = achou - 1
    return mapa, perdidos


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trabalho", help="o .docx que esta sendo comentado")
    ap.add_argument("--pdf", help="o PDF da MESMA versao; sem isto, o Word exporta")
    ap.add_argument("--saida")
    a = ap.parse_args()

    parts = load(a.trabalho)
    pars = collect_paragraphs(parts["word/document.xml"].find(W + "body"),
                              Styles(parts["word/styles.xml"]))

    pdf = a.pdf
    if not pdf:
        try:
            pdf = exportar(a.trabalho)
        except Exception as e:
            sys.exit("sem PDF e sem Word para gerar um (%s).\n"
                     "Exporte o trabalho em PDF pelo próprio Word, da mesma "
                     "versão que está sendo comentada, e passe --pdf." % e)

    mapa, perdidos = mapear(pdf, pars)
    dest = Path(a.saida or Path(a.trabalho).with_name(
        "paginas-" + Path(a.trabalho).stem + ".json"))
    dest.write_text(json.dumps(mapa, ensure_ascii=False), encoding="utf-8")

    total = len(mapa) + len(perdidos)
    print("%s: %d de %d parágrafos localizados (%.0f%%), %d páginas"
          % (dest.name, len(mapa), total, 100.0 * len(mapa) / max(total, 1),
             max(mapa.values()) if mapa else 0))
    if perdidos:
        # A taxa de perda e informacao sobre esta conversao, e nao ruido: o que
        # nao se acha no PDF costuma ser caixa de texto, cabecalho ou legenda
        # que o Word desenha fora do fluxo.
        print("   não localizados: %s%s"
              % (", ".join("P%d" % x for x in perdidos[:12]),
                 " e mais %d" % (len(perdidos) - 12) if len(perdidos) > 12 else ""))


if __name__ == "__main__":
    main()

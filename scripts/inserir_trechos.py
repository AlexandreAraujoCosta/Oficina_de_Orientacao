"""Insere no relatorio o texto dos paragrafos que ele localiza.

O modelo escreve `[P123]` ou `[P123-P125]` e nunca transcreve. Este script le a
fonte, copia o texto daqueles paragrafos e o insere no relatorio como citacao.
Quem transcreve e o codigo, entao nao existe artigo trocado.

Usa o mesmo `carregar` do analisar_pdf.py, e por isso a numeracao de paragrafo
do relatorio e a mesma que o leitor viu. Se o extrator mudar, os dois mudam
juntos.

Uso:
    python inserir_trechos.py <relatorio.md> <trabalho.pdf> [--saida x.md]
    python inserir_trechos.py --lote <pasta_relatorios> <pasta_pdfs>
"""

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from analisar_pdf import carregar  # noqa: E402
from conferir_citacoes import casar  # noqa: E402

# [P123] ou [P123-P125]; tolera espaco e o hifen longo
REF = re.compile(r"\[P(\d+)(?:\s*[-–]\s*P?(\d+))?\]")

LIMITE_BLOCO = 12  # paragrafos por referencia; acima disso, so o primeiro e o ultimo


def indexar(pdf):
    bs, _corpo, _n = carregar(str(pdf))
    return {b["n"]: b for b in bs}


def trecho(indice, ini, fim):
    """Texto dos paragrafos, ja com o numero e a pagina. Nada e reescrito."""
    faltando = [n for n in range(ini, fim + 1) if n not in indice]
    numeros = [n for n in range(ini, fim + 1) if n in indice]
    if not numeros:
        return None, f"P{ini}" + (f"-P{fim}" if fim != ini else "") + " nao existe na fonte"

    if len(numeros) > LIMITE_BLOCO:
        numeros = [numeros[0], numeros[-1]]
        corte = True
    else:
        corte = False

    linhas = []
    anterior = None
    for n in numeros:
        b = indice[n]
        if anterior is not None and n != anterior + 1:
            linhas.append("> [...]")
        linhas.append(f"> **P{n}** (p.{b['pag']}) {b['texto']}")
        anterior = n
    if corte:
        linhas.insert(1, "> [...]")

    aviso = ""
    if faltando:
        aviso = f"P{faltando[0]} ausente na fonte"
    return "\n".join(linhas), aviso


def dividir_em_blocos(corpo):
    """Os paragrafos do Markdown: o que linha em branco separa.

    Devolve o bloco e, depois dele, a linha em branco que o fechava, para o
    texto sair com o mesmo espacamento que entrou.
    """
    atual = []
    for linha in corpo.splitlines():
        if linha.strip():
            atual.append(linha)
            continue
        if atual:
            yield chr(10).join(atual)
            atual = []
        yield ""
    if atual:
        yield chr(10).join(atual)


def processar(relatorio, pdf, saida=None):
    corpo = Path(relatorio).read_text(encoding="utf-8", errors="replace")
    indice = indexar(pdf)

    inseridos, problemas = 0, []
    saida_linhas = []
    # A citacao entra depois do BLOCO que a referencia, e nao depois da linha.
    # Um relatorio com quebra dura a 80 colunas tem varias linhas por paragrafo,
    # e inserir por linha parte a frase ao meio: o leitor ve "nao admite",
    # depois quatro paragrafos citados, e so entao "resposta negativa". Bloco e
    # o que separa linha em branco, que e o paragrafo do Markdown.
    for bloco_txt in dividir_em_blocos(corpo):
        saida_linhas.extend(bloco_txt.splitlines())
        if not bloco_txt.strip():
            continue
        if bloco_txt.lstrip().startswith(">"):
            continue  # ja e citacao inserida
        refs = list(dict.fromkeys(REF.findall(bloco_txt)))
        if not refs:
            continue
        for ini, fim in refs:
            ini = int(ini)
            fim = int(fim) if fim else ini
            bloco, aviso = trecho(indice, ini, fim)
            if bloco is None:
                problemas.append(aviso)
                saida_linhas.append("")
                saida_linhas.append(f"> **[{aviso}]**")
                continue
            if aviso:
                problemas.append(aviso)
            saida_linhas.append("")
            saida_linhas.append(bloco)
            inseridos += 1
        saida_linhas.append("")

    destino = Path(saida) if saida else Path(relatorio)
    texto = "\n".join(saida_linhas)
    cabecalho = (
        "<!-- Trechos inseridos por scripts/inserir_trechos.py a partir de "
        f"{Path(pdf).name}. O modelo forneceu apenas os localizadores; o texto "
        "citado foi copiado da fonte por codigo. -->\n\n"
    )
    destino.write_text(cabecalho + texto, encoding="utf-8")

    nome = Path(relatorio).name
    print(f"  {nome}: {inseridos} trechos inseridos" +
          (f", {len(problemas)} problemas" if problemas else ""))
    for p in dict.fromkeys(problemas):
        print(f"      {p}")
    return inseridos, len(problemas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("relatorio")
    ap.add_argument("pdf")
    ap.add_argument("--saida")
    ap.add_argument("--lote", action="store_true")
    a = ap.parse_args()

    if not a.lote:
        processar(a.relatorio, a.pdf, a.saida)
        return

    pdfs = sorted(Path(a.pdf).rglob("*.pdf"))
    for rel in sorted(Path(a.relatorio).glob("p*.md")):
        alvo = casar(rel, pdfs)
        if alvo is None:
            print(f"  {rel.name}: sem PDF correspondente")
            continue
        processar(rel, alvo)


if __name__ == "__main__":
    main()

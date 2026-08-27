"""Leitor de PDF para as lentes, com a mesma interface do analisar_docx.py.

    python analisar_pdf.py sumario <arquivo.pdf>
    python analisar_pdf.py texto   <arquivo.pdf> --de N --ate M

Entrega prosa com paragrafos numerados (P1, P2, ...), que e o que as leituras
criticas precisam. Nao mede forma: para isso existe o perfil_corpus.py.

Inclui a fusao de fragmento numerico com a linha seguinte, que e o conserto
previsto na sessao 1 do plano do corpus: sem ela, "1.1." e o titulo viram dois
paragrafos e nenhuma subsecao e detectada.
"""
import argparse
import re
import statistics
import sys
import unicodedata
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF nao esta instalado: pip install pymupdf")

sys.stdout.reconfigure(encoding="utf-8")

NUM_TIT = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s*$")
NUM_COM_TEXTO = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+(\S.*)$")
SO_NUMERO = re.compile(r"^\s*\d{1,4}\s*$")
POS_TEXTUAL = re.compile(
    r"^\s*(refer[êe]ncias|bibliografia|ap[êe]ndices?|anexos?|"
    r"obras\s+citadas|refer[êe]ncias\s+bibliogr[áa]ficas)\b", re.I)
PRE_TEXTUAL = re.compile(
    r"^\s*(sum[áa]rio|resumo|abstract|agradecimentos|dedicat[óo]ria|"
    r"lista\s+de|ep[íi]grafe|ficha\s+catalogr[áa]fica)\b", re.I)


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def blocos(doc):
    """Blocos de texto com pagina, posicao e tamanho de fonte dominante."""
    saida = []
    for n_pag, pag in enumerate(doc, start=1):
        dados = pag.get_text("dict")
        for bl in dados.get("blocks", []):
            if bl.get("type") != 0:
                continue
            linhas, tamanhos, negrito = [], [], 0
            n_spans = 0
            for ln in bl.get("lines", []):
                pedaco = ""
                for sp in ln.get("spans", []):
                    pedaco += sp.get("text", "")
                    tamanhos.append(round(sp.get("size", 0), 1))
                    n_spans += 1
                    if sp.get("flags", 0) & 2 ** 4:
                        negrito += 1
                if pedaco.strip():
                    linhas.append(pedaco.strip())
            texto = " ".join(linhas).strip()
            texto = re.sub(r"\s+", " ", texto)
            if not texto:
                continue
            saida.append({
                "pag": n_pag,
                "y": round(bl["bbox"][1], 1),
                "texto": texto,
                "tam": statistics.median(tamanhos) if tamanhos else 0,
                "pct_negrito": (negrito / n_spans) if n_spans else 0,
            })
    return saida


def funde_numeros(bs):
    """Funde o bloco que so tem o numero da secao com o bloco seguinte."""
    saida, i = [], 0
    while i < len(bs):
        b = bs[i]
        m = NUM_TIT.match(b["texto"])
        adjacente = (i + 1 < len(bs)
                     and bs[i + 1]["pag"] == b["pag"]
                     and abs(bs[i + 1]["y"] - b["y"]) < 40)
        if m and adjacente:
            prox = bs[i + 1]
            b = dict(prox)
            b["texto"] = f"{m.group(1)} {prox['texto']}"
            b["tam"] = max(b["tam"], prox["tam"])
            saida.append(b)
            i += 2
            continue
        if SO_NUMERO.match(b["texto"]):  # numero de pagina solto
            i += 1
            continue
        saida.append(b)
        i += 1
    return saida


FIM_FRASE = re.compile(r"[.!?:;»”\"']\s*$")
# entrada de sumario: pontilhado de conducao, com ou sem o numero da pagina
PONTILHADO = re.compile(r"\.{5,}")


def eh_sumario(t):
    return bool(PONTILHADO.search(t))


def junta_paragrafos(bs, corpo):
    """Funde blocos consecutivos que sao continuacao do mesmo paragrafo.

    O PyMuPDF devolve blocos em nivel de linha em muitos PDFs de dissertacao.
    Sem esta passagem, 'mediana de linhas por paragrafo' e qualquer leitura de
    prosa ficam sem sentido."""
    saida = []
    for b in bs:
        if not saida:
            saida.append(dict(b))
            continue
        ant = saida[-1]
        curto = len(b["texto"].split()) <= 25
        mesma_fonte = abs(b["tam"] - ant["tam"]) < 0.6
        continua = (not FIM_FRASE.search(ant["texto"])) or b["texto"][:1].islower()
        titulo_provavel = (b["tam"] >= corpo + 1.0
                           or NUM_COM_TEXTO.match(b["texto"])
                           or (b["texto"].isupper() and curto))
        if continua and mesma_fonte and not titulo_provavel:
            ant["texto"] = f"{ant['texto']} {b['texto']}".strip()
            continue
        saida.append(dict(b))
    return saida


def eh_titulo(b, corpo):
    """Titulo por numeracao, ou por proeminencia tipografica sobre o corpo."""
    t = b["texto"]
    if len(t) > 220:
        return False
    if NUM_COM_TEXTO.match(t) and len(t.split()) >= 2:
        return True
    if b["tam"] >= corpo + 1.0 and len(t.split()) <= 25:
        return True
    if b["pct_negrito"] > 0.8 and len(t.split()) <= 20 and not t.endswith("."):
        return True
    return t.isupper() and 2 <= len(t.split()) <= 20


def nivel(t):
    m = NUM_COM_TEXTO.match(t)
    if not m:
        return 1
    return m.group(1).count(".") + 1


def carregar(caminho):
    doc = fitz.open(caminho)
    if not any(p.get_text().strip() for p in doc):
        sys.exit("PDF sem camada de texto: nada a ler.")
    bs = funde_numeros(blocos(doc))
    # fonte do corpo = a que cobre mais caracteres. Mediana sobre blocos longos
    # nao serve: com blocos em nivel de linha, quase nenhum e longo.
    peso = {}
    for b in bs:
        peso[b["tam"]] = peso.get(b["tam"], 0) + len(b["texto"])
    corpo = max(peso, key=peso.get) if peso else 11.0
    bs = junta_paragrafos(bs, corpo)
    for i, b in enumerate(bs, start=1):
        b["n"] = i
        b["titulo"] = eh_titulo(b, corpo)
        b["nivel"] = nivel(b["texto"]) if b["titulo"] else 0
    return bs, corpo, len(doc)


def delimitar(bs):
    """Primeiro titulo numerado ate o inicio do pos-textual."""
    # o sumario e uma regiao contigua, e suas entradas se quebram em dois
    # blocos (titulo num, pontilhado no seguinte). Em vez de testar entrada por
    # entrada, acha-se o fim da regiao: o ultimo pontilhado do primeiro terco.
    limite = int(len(bs) * 0.4) or len(bs)
    fim_sumario = 0
    for b in bs[:limite]:
        if eh_sumario(b["texto"]):
            fim_sumario = b["n"]

    inicio = 1
    for b in bs:
        if b["n"] <= fim_sumario:
            continue
        if b["titulo"] and NUM_COM_TEXTO.match(b["texto"]):
            inicio = b["n"]
            break
    # primeiro titulo pos-textual DEPOIS do inicio, e nao o primeiro do arquivo:
    # o sumario tambem lista "Referencias" e listava antes do texto comecar
    fim = bs[-1]["n"]
    for b in bs:
        if b["n"] <= inicio:
            continue
        if b["titulo"] and POS_TEXTUAL.match(sem_acento(b["texto"])):
            fim = b["n"] - 1
            break
    return inicio, fim


def cmd_sumario(bs, corpo, n_pag, caminho):
    ini, fim = delimitar(bs)
    corpo_bs = [b for b in bs if ini <= b["n"] <= fim and not b["titulo"]]
    palavras = sum(len(b["texto"].split()) for b in corpo_bs)
    print(f"ARQUIVO   {caminho}")
    print(f"PAGINAS   {n_pag}")
    print(f"BLOCOS    {len(bs)}  (texto principal: P{ini} a P{fim})")
    print(f"PALAVRAS  {palavras:,} no texto principal")
    print(f"CORPO     fonte dominante {corpo} pt")
    print()
    print("ESTRUTURA")
    for b in bs:
        if not b["titulo"]:
            continue
        marca = "  " * (b["nivel"] - 1)
        faixa = "pre" if b["n"] < ini else ("pos" if b["n"] > fim else "   ")
        print(f"  [{faixa}] P{b['n']:<5} {marca}{b['texto'][:110]}")


def etiqueta(caminho):
    """Etiqueta curta do arquivo, para carimbar cada paragrafo.

    Existe por causa de um caso real: em leva de seis leituras simultaneas, um
    subagente recebeu na saida paragrafos de outro trabalho, lido ao mesmo tempo
    por outro subagente. O script nao tem estado compartilhado, entao a mistura
    ocorre na entrega da saida entre processos concorrentes. Com o carimbo, o
    paragrafo estranho se denuncia; sem ele, a troca e silenciosa e a exigencia
    de citacao literal lhe da aparencia de prova."""
    return Path(caminho).stem[:28]


def cmd_texto(bs, de, ate, caminho):
    et = etiqueta(caminho)
    print(f"### PROCEDENCIA: {et} — confira esta etiqueta em cada paragrafo.")
    print(f"### Paragrafo com etiqueta diferente NAO e deste trabalho: pare e avise.")
    print()
    for b in bs:
        if de <= b["n"] <= ate:
            marca = " [TITULO]" if b["titulo"] else ""
            print(f"[{et}] P{b['n']}{marca} (p.{b['pag']}) {b['texto']}")
            print()
    print(f"### FIM DA EXTRACAO DE {et}")


def main():
    ap = argparse.ArgumentParser(description="Leitor de PDF para leitura critica.")
    ap.add_argument("comando", choices=["sumario", "texto"])
    ap.add_argument("arquivo")
    ap.add_argument("--de", type=int, default=1)
    ap.add_argument("--ate", type=int, default=10 ** 9)
    a = ap.parse_args()

    bs, corpo, n_pag = carregar(a.arquivo)
    if a.comando == "sumario":
        cmd_sumario(bs, corpo, n_pag, a.arquivo)
    else:
        cmd_texto(bs, a.de, a.ate, a.arquivo)


if __name__ == "__main__":
    main()

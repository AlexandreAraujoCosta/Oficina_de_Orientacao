"""Confere se as citacoes literais de um relatorio existem no PDF de origem.

Existe por causa de um caso concreto: numa leva de seis leituras simultaneas, o
relatorio de um trabalho recebeu paragrafos extraidos de outro, lido ao mesmo
tempo por outro subagente. A contaminacao e silenciosa, e a exigencia de citacao
literal do prompt da a ela aparencia de evidencia.

Extrai toda sequencia entre aspas com pelo menos `--minimo` caracteres, procura
cada uma no texto do PDF, e lista as que nao aparecem. Citacao ausente nao prova
contaminacao (pode ser parafrase entre aspas, erro de transcricao ou hifenizacao
desfeita), mas concentra a conferencia manual onde ela vale a pena.

Uso:
    python conferir_citacoes.py <relatorio.md> <trabalho.pdf>
    python conferir_citacoes.py --lote <pasta_relatorios> <pasta_pdfs>
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF nao esta instalado: pip install pymupdf")

# Aspas curvas, retas e angulares. SEM re.S, e de proposito: com ele, um par de
# aspas retas nao relacionadas casa atravessando secoes inteiras do relatorio, e
# o conferidor acusa dezenas de ausencias que sao varredura do proprio padrao.
# Aconteceu em 02/08 e quase virou conclusao sobre os relatorios.
ASPAS = [
    re.compile(r"“([^”\n]{1,400})”"),
    re.compile(r'"([^"\n]{1,400})"'),
    re.compile(r"«([^»\n]{1,400})»"),
]

# Marcas de que o casamento pegou estrutura do relatorio, e nao uma transcricao.
LIXO = re.compile(r"\*\*|^\s*[-*#|]|\n")


def normalizar(s):
    """Minusculas, sem acento, espacos colapsados, sem hifen de fim de linha."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("­", "").replace("-\n", "").replace("- ", "")
    s = re.sub(r"[‘’“”«»\"']", "", s)
    # colchetes e parenteses editoriais: "[foram]", "encontrado[s]", "(...)".
    # Sem isto o conferidor acusa ausencia onde ha apenas marca de edicao.
    s = re.sub(r"[\[\]()]", " ", s)
    s = re.sub(r"\s+", " ", s)
    # Pontuacao de borda: quem cita fecha com ponto onde o original segue com
    # virgula, e isso nao e transcricao infiel. Sem isto o conferidor acusa
    # ausencia em citacao correta, o que aconteceu aqui em 02/08.
    return s.lower().strip().strip(".,;:—- ")


def citacoes(texto, minimo):
    achadas = []
    for padrao in ASPAS:
        for m in padrao.finditer(texto):
            t = m.group(1).strip()
            if len(t) >= minimo and not LIXO.search(t):
                achadas.append(t)
    # remove repetidas preservando a ordem
    vistas, saida = set(), []
    for c in achadas:
        k = normalizar(c)
        if k not in vistas:
            vistas.add(k)
            saida.append(c)
    return saida


def texto_do_docx(caminho):
    """Texto do .docx sem dependencia externa: os `w:t` do documento, das notas
    de rodape e das notas de fim. As notas importam: e nelas que estes trabalhos
    guardam metodo e ressalva."""
    import zipfile

    partes = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]
    pedacos = []
    with zipfile.ZipFile(caminho) as z:
        nomes = set(z.namelist())
        for parte in partes:
            if parte not in nomes:
                continue
            xml = z.read(parte).decode("utf-8", errors="replace")
            # Fim de paragrafo e quebra de linha viram espaco; todo o resto se
            # concatena SEM separador. No OOXML uma palavra dividida em dois
            # `w:r` (por italico, nota de rodape ou marca de revisao) tem dois
            # `w:t`, e juntar com espaco parte a palavra ao meio, fabricando
            # ausencia de citacao. Aconteceu aqui em 02/08.
            xml = re.sub(r"</w:p>|<w:br\s*/>", "<w:t> </w:t>", xml)
            pedacos.extend(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S))
    bruto = "".join(pedacos)
    bruto = bruto.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return normalizar(bruto)


def texto_do_pdf(caminho):
    if str(caminho).lower().endswith((".docx", ".dotx")):
        return texto_do_docx(caminho)
    doc = fitz.open(caminho)
    return normalizar(" ".join(p.get_text() for p in doc))


def conferir(relatorio, pdf, minimo, verboso):
    corpo = Path(relatorio).read_text(encoding="utf-8", errors="replace")
    alvo = texto_do_pdf(pdf)
    cits = citacoes(corpo, minimo)
    ausentes = []
    for c in cits:
        n = normalizar(c)
        if n in alvo:
            continue
        # tolera reticencia de supressao: cada trecho preservado tem de existir
        partes = [p.strip() for p in re.split(r"\.\.\.|…", n) if len(p.strip()) >= 20]
        if partes and all(p in alvo for p in partes):
            continue
        ausentes.append(c)

    nome = Path(relatorio).name
    if not cits:
        print(f"  {nome}: nenhuma citacao com {minimo}+ caracteres. Nada a conferir.")
        return 0, 0
    print(f"  {nome}: {len(cits) - len(ausentes)}/{len(cits)} confirmadas no PDF.")
    for c in ausentes:
        recorte = re.sub(r"\s+", " ", c)[:120]
        print(f"      AUSENTE  {recorte}")
    if verboso and not ausentes:
        print("      todas conferem")
    return len(cits), len(ausentes)


def casar(relatorio, pdfs):
    """Casa o relatorio com o PDF correspondente, por ano e sobrenome no nome do arquivo."""
    m = re.match(r"p\d+-(\d{4})-(.+)\.md$", Path(relatorio).name, re.I)
    if not m:
        return None
    ano, autor = m.group(1), normalizar(m.group(2))
    for p in pdfs:
        n = normalizar(p.stem)
        if n.startswith(ano) and autor in n:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("relatorio", help="arquivo .md, ou pasta com --lote")
    ap.add_argument("pdf", help="arquivo .pdf, ou pasta com --lote")
    ap.add_argument("--lote", action="store_true")
    ap.add_argument("--minimo", type=int, default=40,
                    help="tamanho minimo da citacao conferida")
    ap.add_argument("--verboso", action="store_true")
    a = ap.parse_args()

    if not a.lote:
        conferir(a.relatorio, a.pdf, a.minimo, a.verboso)
        return

    pdfs = sorted(Path(a.pdf).rglob("*.pdf"))
    total_c = total_a = 0
    sem_par = []
    for rel in sorted(Path(a.relatorio).glob("p*.md")):
        alvo = casar(rel, pdfs)
        if alvo is None:
            sem_par.append(rel.name)
            continue
        c, au = conferir(rel, alvo, a.minimo, a.verboso)
        total_c += c
        total_a += au

    print()
    print(f"TOTAL  {total_c - total_a}/{total_c} citacoes confirmadas, {total_a} ausentes.")
    if sem_par:
        print("Sem PDF correspondente: " + ", ".join(sem_par))


if __name__ == "__main__":
    main()

"""Junta relatorio e anexo num documento so, insere os trechos e gera o PDF.

POR QUE UM DOCUMENTO SO

O relatorio e o anexo tem leitores diferentes, e isso justificava dois arquivos.
Na pratica, dois arquivos viram um perdido: quem recebe abre o primeiro, e o
segundo fica no e-mail. Como o anexo tambem e o que se entrega ao corretor
automatico junto do trabalho, ele precisa acompanhar o relatorio sempre.

A separacao que importa nao e de arquivo, e de posicao: o corpo vem primeiro e
cabe numa sessao de leitura; o anexo vem depois, declarado como material de
consulta e de maquina. Quem le para de ler onde o corpo acaba.

Uso:
    python montar_entrega.py <relatorio.md> <anexo.md> <trabalho.pdf|docx> [--saida X.md]
"""

import argparse
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

SEPARADOR = """

<div style="page-break-after: always;"></div>

\\newpage

"""


def paragrafos(trabalho, destino):
    """Grava, ao lado da entrega, o trabalho com os paragrafos numerados.

    E o arquivo que resolve os [P123] do relatorio: quem recebe abre o
    localizador em vez de confiar na transcricao. Vai junto com a entrega
    porque separado ele nao e enviado, e o relatorio sem ele so se confere
    pelos trechos que o proprio relatorio ja transcreveu.

    Nao se chama ANEXO porque ANEXO- ja nomeia o anexo de sugestoes
    complementares, que entra dentro do PDF de entrega. Dois arquivos com o
    mesmo nome e conteudos sem relacao atrapalham na hora de anexar no e-mail.
    """
    sys.path.insert(0, str(RAIZ))
    from conferir_consistencia import carregar  # noqa: E402

    pares = carregar(trabalho)
    saida = destino.with_name(destino.name.replace("ENTREGA-", "ENTREGA-PARAGRAFOS-", 1))
    if saida == destino:
        saida = destino.with_name("ENTREGA-PARAGRAFOS-" + destino.name)

    cab = [
        "# %s, com os parágrafos numerados" % Path(trabalho).name,
        "",
        "Os localizadores `[P123]` do relatório apontam para este arquivo. "
        "São %d parágrafos, do [P%d] ao [P%d]." % (len(pares), pares[0][0], pares[-1][0]),
        "",
        "A numeração pula onde o extrator não rotulou parágrafo vazio, e por isso "
        "a série tem lacunas legítimas. Gerado de `%s` por `montar_entrega.py`: "
        "não edite, porque editar desfaz a correspondência com o relatório."
        % Path(trabalho).name,
        "",
        "---",
        "",
        "",
    ]
    corpo = ["[P%d] %s" % (n, txt) for n, txt in pares]
    saida.write_text("\n".join(cab) + "\n\n".join(corpo) + "\n", encoding="utf-8")
    print("  paragrafos: %s (%d)" % (saida, len(pares)))


def main():
    # O subprocesso devolve U+FFFD quando a saida dele nao e UTF-8 valido, e
    # imprimir isso num console cp1252 derruba o script depois de ele ja ter
    # feito metade do trabalho. Medido em 25/08/2026.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Monta a entrega única: relatório + anexo + PDF.")
    ap.add_argument("relatorio")
    ap.add_argument("anexo")
    ap.add_argument("trabalho")
    ap.add_argument("--saida", help="padrão: ENTREGA-<nome>.md ao lado do relatório")
    ap.add_argument("--sem-pdf", action="store_true")
    ap.add_argument("--sem-paragrafos", action="store_true",
                    help="nao grava o ENTREGA-PARAGRAFOS-<nome>.md ao lado")
    a = ap.parse_args()

    rel = Path(a.relatorio).read_text(encoding="utf-8").rstrip()
    anx = Path(a.anexo).read_text(encoding="utf-8").lstrip()

    # o anexo perde o titulo de nivel 1, que passa a ser secao do documento unico
    if anx.startswith("# "):
        linha, _, resto = anx.partition("\n")
        anx = "# " + linha[2:].strip() + "\n" + resto

    destino = Path(a.saida) if a.saida else \
        Path(a.relatorio).with_name("ENTREGA-" + Path(a.relatorio).name)
    destino.write_text(rel + SEPARADOR + anx + "\n", encoding="utf-8")
    print("  montado: %s" % destino)

    if not a.sem_paragrafos:
        paragrafos(a.trabalho, destino)

    # O indice que o corretor percorre. Vai junto porque separado nao e enviado.
    r = subprocess.run([sys.executable, str(RAIZ / "lista_corretor.py"),
                        a.relatorio, a.anexo,
                        "--saida", str(destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name))],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").rstrip() or (r.stderr or "")[-200:])

    # O .md anotado, em CriticMarkup: serve aos dois caminhos, e e o unico
    # que o caminho do PDF tem, porque la nao ha .docx para comentar.
    r = subprocess.run([sys.executable, str(RAIZ / "anotar_md.py"),
                        str(destino.with_name("ENTREGA-PARAGRAFOS-" + Path(a.relatorio).name)),
                        str(destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name)),
                        "--saida", str(destino.with_name("ENTREGA-ANOTADO-" + Path(a.relatorio).name))],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").rstrip() or (r.stderr or "")[-300:])

    # O .docx anotado: o mesmo relatorio, na margem do documento do autor.
    if a.trabalho.lower().endswith(".docx"):
        r = subprocess.run([sys.executable, str(RAIZ / "anotar_docx.py"), a.trabalho,
                            str(destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name)),
                            "--saida", str(destino.with_name("ENTREGA-ANOTADO-" + Path(a.trabalho).name))],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print((r.stdout or "").rstrip() or (r.stderr or "")[-300:])

    com = destino.with_name(destino.stem + "-COM-TRECHOS.md")
    r = subprocess.run([sys.executable, str(RAIZ / "relatorio_autossuficiente.py"),
                        str(destino), a.trabalho, "--saida", str(com)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        sys.exit((r.stderr or "")[-600:])

    if a.sem_pdf:
        return 0
    r = subprocess.run([sys.executable, str(RAIZ / "gerar_pdf.py"), str(com)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())

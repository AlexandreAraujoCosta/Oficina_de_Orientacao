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
from datetime import date
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
    ap.add_argument("--estudante",
                    help="arquiva tudo em entregas/<estudante>/<AAAA-MM-DD>/; a data "
                         "separa as rodadas do mesmo trabalho, que e o que "
                         "comparar_versoes.py precisa para achar a anterior")
    ap.add_argument("--aceitar-citacoes", action="store_true",
                    help="monta mesmo com citacao que nao confere; carimba o relatorio")
    ap.add_argument("--sem-pdf", action="store_true")
    ap.add_argument("--sem-conferencia", action="store_true",
                    help="monta sem a conferência de compreensibilidade, assumindo a falta")
    ap.add_argument("--pdf", help="o PDF da MESMA versão do trabalho, para o mapa de páginas")
    ap.add_argument("--sem-paginas", action="store_true",
                    help="não gera o mapa de páginas nem abre o Word")
    ap.add_argument("--sem-paragrafos", action="store_true",
                    help="nao grava o ENTREGA-PARAGRAFOS-<nome>.md ao lado")
    a = ap.parse_args()

    # A normalizacao nao se faz aqui, e sim na entrada. Neste ponto o relatorio
    # ja existe e cada localizador dele aponta para um paragrafo deste arquivo:
    # normalizar agora deslocaria a numeracao inteira sem que nada acusasse. O
    # que cabe e dizer que nao foi feita, porque a camada formal do relatorio
    # entao mistura desvio de verdade com ruido de colagem.
    if a.trabalho.lower().endswith(".docx"):
        try:
            import zipfile
            st = zipfile.ZipFile(a.trabalho).read("word/styles.xml")
            if b"Oficina" not in st:
                print("  AVISO: o trabalho nao passou pelo normalizador. O que o relatorio")
                print("         apontar de formatacao mistura desvio e ruido de colagem.")
                print("         Na proxima rodada: normalizar_docx.py ANTES de extrair.")
        except Exception:
            pass

    # A conferencia de compreensibilidade e bloqueante desde 30/08/2026: analise
    # que passa sem leitor frio saiu tres vezes num mesmo dia sem que nada
    # impedisse, e o que ela pega nao aparece de outro modo.
    conf = Path(a.relatorio).with_name("CONFERENCIA-" + Path(a.relatorio).name)
    if not a.sem_conferencia:
        if not conf.exists():
            sys.exit(
                "\n%s nao existe, e sem ele nao se monta a entrega.\n"
                "\nRode texto_dos_comentarios.py, entregue a saida a um leitor que nao\n"
                "escreveu os apontamentos, com prompts/COMPREENSIBILIDADE.md, e grave a\n"
                "tabela que ele devolver naquele arquivo. A tabela volta para voce, que\n"
                "decide item a item: so mantem como esta o que ja responde a objecao.\n"
                "\nPara montar sem isso, e assumindo a falta: --sem-conferencia."
                % conf.name)
        if conf.stat().st_mtime < Path(a.relatorio).stat().st_mtime:
            sys.exit(
                "\n%s e mais antigo que o relatorio: a conferencia rodou sobre uma\n"
                "versao anterior. Rode de novo sobre esta." % conf.name)

    rel = Path(a.relatorio).read_text(encoding="utf-8").rstrip()
    anx = Path(a.anexo).read_text(encoding="utf-8").lstrip()

    # o anexo perde o titulo de nivel 1, que passa a ser secao do documento unico
    if anx.startswith("# "):
        linha, _, resto = anx.partition("\n")
        anx = "# " + linha[2:].strip() + "\n" + resto

    # A entrega se arquiva sozinha: onze arquivos por rodada, e mais de uma
    # rodada por trabalho, nao cabem empilhados no diretorio corrente.
    if a.estudante:
        pasta = Path("entregas") / a.estudante / date.today().isoformat()
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / ("ENTREGA-" + Path(a.relatorio).name)
    elif a.saida:
        destino = Path(a.saida)
    else:
        destino = Path(a.relatorio).with_name("ENTREGA-" + Path(a.relatorio).name)
    # A conferencia de citacoes bloqueia. Ela existe porque um relatorio ja
    # recebeu paragrafos de outro trabalho, e em 28/08/2026 um modelo entregou
    # uma citacao fabricada: abertura verdadeira, continuacao inventada. Etapa
    # cuja execucao depende de quem esta sendo conferido nao e etapa.
    conf = subprocess.run([sys.executable, str(RAIZ / "conferir_citacoes.py"),
                           a.relatorio, a.trabalho],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    ausentes = [x.strip() for x in (conf.stdout or "").splitlines() if "AUSENTE" in x]
    if ausentes and not a.aceitar_citacoes:
        sys.exit(("%d trecho(s) entre aspas nao existem no trabalho." % len(ausentes)) + '\n\n'                 + ('\n').join("  " + x for x in ausentes[:12]) + '\n\n'                 + "A entrega NAO foi montada. Ou o trecho foi digitado errado, ou e" + '\n'                 + "parafrase entre aspas, ou foi inventado. Nenhum dos tres se entrega." + '\n'                 + "Tire as aspas, ou deixe o programa inserir o trecho pelo localizador." + '\n\n'                 + "Se souber que sao falsos positivos, repita com --aceitar-citacoes:" + '\n'                 + "o relatorio sai carimbado dizendo que a conferencia foi dispensada.")
    if ausentes:
        rel = ("> **Conferencia de citacoes dispensada na montagem.** %d trecho(s)" % len(ausentes)
               + " entre aspas deste relatorio nao foram encontrados no trabalho." + '\n'               + "> Quem receber isto precisa conferi-los a mao antes de acreditar." + '\n\n' + rel)
        print("  AVISO: montado com %d citacao(oes) nao conferida(s); o relatorio saiu carimbado." % len(ausentes))
    elif conf.stdout:
        print("  citacoes: " + [x for x in conf.stdout.splitlines() if "confirmadas" in x or "Nada a conferir" in x][-1].strip())

    # O que a normalizacao mudou vai anexo, porque quem recebe o arquivo
    # normalizado precisa saber o que mudou nele, e isso so aparecia no
    # terminal de quem rodou o programa.
    norm = Path(a.trabalho).with_name("ANEXO-NORMALIZACAO-"
                                      + Path(a.trabalho).stem + ".md")
    extra = ""
    if norm.exists():
        extra = SEPARADOR + norm.read_text(encoding="utf-8").lstrip()
        print("  anexo da normalização incluído: %s" % norm.name)

    destino.write_text(rel + SEPARADOR + anx + extra + "\n", encoding="utf-8")
    print("  montado: %s" % destino)

    docx = a.trabalho.lower().endswith(".docx")
    # Num .docx o comentario ja esta na margem do paragrafo certo, e a
    # numeracao so existia para suprir a falta disso.
    if not a.sem_paragrafos and not docx:
        paragrafos(a.trabalho, destino)

    # O indice que o corretor percorre. Vai junto porque separado nao e enviado.
    r = subprocess.run([sys.executable, str(RAIZ / "lista_corretor.py"),
                        a.relatorio, a.anexo,
                        "--saida", str(destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name))],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").rstrip() or (r.stderr or "")[-200:])

    # O .md anotado, em CriticMarkup, e o que o caminho do PDF tem no lugar
    # do .docx comentado. Num .docx seria a mesma coisa dita duas vezes.
    if not docx:
      r = subprocess.run([sys.executable, str(RAIZ / "anotar_md.py"),
                          str(destino.with_name("ENTREGA-PARAGRAFOS-" + Path(a.relatorio).name)),
                          str(destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name)),
                          "--saida", str(destino.with_name("ENTREGA-ANOTADO-" + Path(a.relatorio).name))],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
      print((r.stdout or "").rstrip() or (r.stderr or "")[-300:])

    # O .docx anotado: o mesmo relatorio, na margem do documento do autor.
    if a.trabalho.lower().endswith(".docx"):
        lista = destino.with_name("ENTREGA-CORRETOR-" + Path(a.relatorio).name)

        # ---- o mapa de paginas, que e o endereco que quem recebe sabe usar.
        # Quem recebeu a primeira entrega disse, em 28/08/2026, que preferiu
        # achar os erros pelo PDF, "que indica a pagina em que esta o erro".
        # Depende de haver Word para exportar, ou de um PDF da MESMA versao;
        # faltando os dois, a entrega sai com o endereco por palavras iniciais,
        # que funciona no Ctrl+F, e o programa diz que foi isso que aconteceu.
        mapa = destino.with_name("paginas-" + Path(a.trabalho).stem + ".json")
        arg_pag = []
        if not a.sem_paginas:
            r = subprocess.run([sys.executable, str(RAIZ / "paginas.py"), a.trabalho,
                                "--saida", str(mapa)]
                               + (["--pdf", a.pdf] if a.pdf else []),
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            if mapa.exists():
                arg_pag = ["--paginas", str(mapa)]
                print("  " + (r.stdout or "").strip().splitlines()[0])
            else:
                print("  sem mapa de páginas (%s); o endereço sai pelas palavras "
                      "iniciais do parágrafo"
                      % ((r.stderr or r.stdout or "sem PDF").strip().splitlines()[0][:80]))

        r = subprocess.run([sys.executable, str(RAIZ / "anotar_docx.py"), a.trabalho,
                            str(lista),
                            "--saida", str(destino.with_name("ENTREGA-ANOTADO-" + Path(a.trabalho).name))]
                           + arg_pag,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print((r.stdout or "").rstrip() or (r.stderr or "")[-300:])

        # ---- o texto que cada apontamento tera dentro do Word, para o
        # conferidor de compreensibilidade. Sai sempre, porque conferir depende
        # de existir o arquivo, e depender de alguem lembrar de gerar e o mesmo
        # que nao conferir.
        r = subprocess.run([sys.executable, str(RAIZ / "texto_dos_comentarios.py"),
                            a.trabalho, str(lista),
                            "--saida", str(destino.with_name(
                                "COMENTARIOS-" + Path(a.relatorio).name))],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("  " + ((r.stdout or "").strip() or (r.stderr or "")[-160:].strip()))

        # O indice do corretor e a entrada do anotar_docx.py, e nao entrega:
        # num .docx o apontamento ja vai na margem do paragrafo que ele cita.
        if lista.exists():
            lista.unlink()
        if mapa.exists():
            mapa.unlink()

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
    pdf = com.with_suffix(".pdf")
    if not (docx and pdf.exists()):
        return 0

    # Docx entra, docx sai: fica o trabalho anotado e o PDF do relatorio. O
    # resto e andaime, e so se recolhe depois que o PDF existe, porque sem
    # pandoc ele nao existe e o markdown passa a ser a unica saida.
    guardar = {pdf.name, ("ENTREGA-ANOTADO-" + Path(a.trabalho).name)}
    tmp = destino.parent / "tmp"
    tmp.mkdir(exist_ok=True)
    recolhidos = 0
    for peca in destino.parent.glob("ENTREGA-*"):
        if peca.name in guardar or peca.is_dir():
            continue
        peca.replace(tmp / peca.name)
        recolhidos += 1
    for peca in tmp.iterdir():
        peca.unlink()
    tmp.rmdir()
    print("  %d intermediarios recolhidos e apagados; ficam o .docx anotado e o PDF"
          % recolhidos)
    return 0


if __name__ == "__main__":
    sys.exit(main())

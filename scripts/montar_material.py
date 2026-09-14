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
    quebra = _quebrou(r.stderr)
    if quebra:
        return None, quebra
    if r.returncode not in (0, 1):
        return None, "o casador de figuras saiu com codigo %d" % r.returncode
    return r.stdout, None


def _quebrou(stderr):
    """Excecao nao tratada no casador (ex.: BadZipFile ao apontar um .pdf em vez
    de um .docx real): o stdout ate ali e lixo (autoteste, mensagens parciais), e
    nunca uma tabela de figuras. Achado em 14/09/2026: esse texto estava entrando
    no MATERIAL.md como se fosse extracao real. Devolve o motivo, ou None."""
    if "Traceback (most recent call last):" in (stderr or ""):
        return "o casador de figuras quebrou: %s" % stderr.strip().splitlines()[-1]
    return None


# Controle positivo do detector, plantado: um traceback tem de ser acusado com a
# ultima linha dele, e um aviso comum nao. Sem isso, a guarda acima e so uma
# esperanca, e o modulo se recusa a carregar se ela falhar.
assert _quebrou("autoteste: ok\nTraceback (most recent call last):\n  File x\n"
                "zipfile.BadZipFile: File is not a zip file") \
    == "o casador de figuras quebrou: zipfile.BadZipFile: File is not a zip file"
assert _quebrou("aviso: 3 figuras sem legenda\n") is None and _quebrou("") is None


# QUALQUER titulo de nivel dois fecha a secao anterior, e nao so outro titulo de
# figura. Sem isso, a secao "Quadro 2", que nao tem endereco, engolia a secao
# seguinte inteira e se apropriava do endereco dela: no controle, o Quadro sem
# endereco saiu endereçado em [P999], que era da lista do fim.
RE_SECAO_QUALQUER = re.compile(r"^##\s+(.*?)\s*$", re.M)
RE_EH_FIGURA = re.compile(r"^(Gr[áa]fico|Figura|Tabela|Quadro|Imagem)\b", re.I)
RE_FIG_END = re.compile(r"\*\*Endere[cç]o\.?\*\*\s*[^\n]*?\[?P(\d+)\]?")
RE_CAMPO_LEGENDA = re.compile(r"^\*\*Legenda e fonte declarada\.?\*\*.*?(?=\n\*\*|\Z)",
                              re.M | re.S)


def blocos_pa(caminho):
    """Le o relatorio da leitura de figuras e devolve {P da legenda: texto PA}.

    O PA e prosa escrita por quem leu a imagem, e nao pelo autor do trabalho.
    Por isso ele **nao entra na extracao** e nao ganha numero proprio: ele mora
    num arquivo companheiro e so e fundido aqui, sob pedido, com o numero da
    legenda a que pertence. Assim nenhum dos programas que leem a extracao o ve,
    e nada precisa ser retirado no fim. Retirada que precisa acontecer e
    retirada que um dia nao acontece.

    O campo da legenda sai do bloco: ele repete o que ja esta no paragrafo
    imediatamente acima, no proprio texto do trabalho.
    """
    txt = io.open(caminho, encoding="utf-8", errors="replace").read()
    cortes = [(m.start(), m.end(), m.group(1)) for m in RE_SECAO_QUALQUER.finditer(txt)]
    fora, sem_endereco = {}, []
    for k, (ini, fim_cab, titulo) in enumerate(cortes):
        if not RE_EH_FIGURA.match(titulo):
            continue
        fim = cortes[k + 1][0] if k + 1 < len(cortes) else len(txt)
        corpo = txt[fim_cab:fim].strip()
        m = RE_FIG_END.search(corpo)
        if not m:
            sem_endereco.append(titulo)
            continue
        n = int(m.group(1))
        corpo = RE_CAMPO_LEGENDA.sub("", corpo).strip()
        fora.setdefault(n, []).append((titulo, corpo))
    return fora, sem_endereco


def texto_pa(titulo, corpo, numero):
    return ("[PA%s] LEITURA DA IMAGEM — não é texto do trabalho. Escrita por quem "
            "abriu a figura, antes de ler a prosa que a comenta. Não cite como "
            "sendo do autor.\n\n%s\n\n%s\n" % (numero, titulo, corpo))


def autoteste():
    falhas = []
    for corpo in ("40% dos casos", "40%% literal", "%s e %d", "sem percentual"):
        resultado = texto_pa("Figura 1", corpo, 12)
        if not resultado.startswith("[PA12]") or not resultado.endswith(corpo + "\n"):
            falhas.append("a inserção PA alterou o conteúdo da figura")
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

        # OS BLOCOS PA: le a secao de figura, casa pelo endereco da legenda,
        # tira o campo que repete a legenda, e RECUSA a secao sem endereco.
        rel = Path(tempfile.gettempdir()) / "_mat_figs.md"
        rel.write_text(
            "# cabecalho que nao e figura\n\n"
            "## Gráfico 7 — um título\n\n"
            "**Endereço.** [P812], parágrafo da legenda.\n\n"
            "**Legenda e fonte declarada.** Isto repete o parágrafo do trabalho.\n\n"
            "**O que é.** Série temporal.\n\n"
            "## Quadro 2 — sem endereço nenhum\n\n"
            "**O que é.** Um quadro.\n\n"
            "## Lista 2 — o que ninguém afirmou\n\n"
            "**Endereço.** [P999].\n", encoding="utf-8")
        try:
            pa, sem = blocos_pa(str(rel))
            if list(pa) != [812]:
                falhas.append("os blocos PA saíram em %r, e o controle diz [812]" % list(pa))
            if 812 in pa and "Série temporal" not in pa[812][0][1]:
                falhas.append("o bloco PA perdeu o corpo da seção")
            if 812 in pa and "repete o parágrafo" in pa[812][0][1]:
                falhas.append("o bloco PA manteve o campo da legenda, que duplica o texto")
            if sem != ["Quadro 2 — sem endereço nenhum"]:
                falhas.append("não acusou a figura sem endereço: %r" % sem)
        finally:
            try:
                rel.unlink()
            except Exception:
                pass
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
    ap.add_argument("--com-figuras", dest="com_figuras", action="append", default=[],
                    metavar="FIGURAS.md",
                    help="funde a leitura das imagens no corpo, como blocos [PA###] "
                         "logo depois da legenda. Repetível. DESLIGADO por padrão: "
                         "o PA é prosa de quem leu a imagem, não do autor, e não "
                         "pode entrar sem que se peça.")
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

    pa, pa_sem, pa_orfaos = {}, [], []
    for caminho in a.com_figuras:
        if not Path(caminho).exists():
            print("  !! --com-figuras: %s nao existe" % caminho)
            return 2
        d, sem = blocos_pa(caminho)
        for n, blocos in d.items():
            pa.setdefault(n, []).extend(blocos)
        pa_sem.extend(sem)
    pa_orfaos = sorted(n for n in pa if n not in ps)

    if pa:
        out.append("## A leitura das imagens está fundida no corpo\n")
        out.append("Os blocos marcados `[PA###]` **não são texto do trabalho**: são a "
                   "descrição de quem abriu a figura, antes de ler a prosa que a "
                   "comenta. Cada um vem logo depois do parágrafo da legenda a que "
                   "pertence, e leva o número dela. Não cite um `[PA###]` como sendo "
                   "do autor, e não o conte em nenhuma contagem sobre o trabalho.\n")
        out.append("São %d figuras descritas, em %d arquivo(s) de leitura.\n"
                   % (len(pa), len(a.com_figuras)))

    out.append("=" * 78)
    out.append("O TRABALHO, NA ORDEM")
    out.append("=" * 78 + "\n")
    for n in sorted(ps):
        out.append("[P%d] %s\n" % (n, ps[n]))
        for titulo, corpo in pa.get(n, []):
            out.append(texto_pa(titulo, corpo, n))
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
    if a.com_figuras:
        n_blocos = sum(len(v) for v in pa.values())
        print("  %d bloco(s) [PA###] fundidos em %d parágrafo(s) de legenda."
              % (n_blocos, len(pa)))
        if pa_sem:
            print("  %d seção(ões) de figura SEM endereço, e por isso fora do corpo:"
                  % len(pa_sem))
            for t in pa_sem[:8]:
                print("     %s" % t[:78])
        if pa_orfaos:
            print("  %d endereço(s) de figura que não existem na extração: %s"
                  % (len(pa_orfaos), ", ".join("P%d" % n for n in pa_orfaos[:12])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

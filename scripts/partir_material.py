# -*- coding: utf-8 -*-
"""Reparte o MATERIAL.md em tres arquivos, um por passo da ordem de leitura.

POR QUE ISTO EXISTE

Medido em 14/09/2026, nas duas execucoes do Alberto sobre um TCC: o registro da
execucao 1 diz que o `MATERIAL.md` inteiro (26,5 mil palavras) foi lido **quatro
vezes em sequencia**, uma por passo, e isso e mais da metade dos 321 mil tokens
da execucao. Cada passo precisa de uma parte: o passo 1 le as pontas (resumo,
introducao, conclusao); o passo 2 le os artefatos e o corpo; o passo 3 le o apoio
(referencias e notas). Este programa grava as tres partes, para que cada passo
abra so a sua. E o braco A do item 9 de `prompts/FILA-20260914.md`.

O QUE ELE NAO FAZ

Nao recorta por julgamento: as fronteiras vem do `mapa_estrutural.py`, que ja as
acha para o mapa, e dos titulos numerados. Nao apaga nada: as tres partes juntas
sao o trabalho inteiro, e o programa se recusa a gravar se algum paragrafo ficar
fora ou entrar em duas. O `MATERIAL.md` inteiro continua existindo para quem le
tudo.

AS TRES PARTES

    pontas      do inicio (resumo, abstract) ate o fim da secao que a introducao
                abre, mais a conclusao (do titulo dela ate as referencias ou o
                primeiro apendice)
    apoio       a lista de referencias, e as notas de rodape
    artefatos   tudo o mais: o corpo depois da introducao, os apendices e anexos,
                mais o sumario e a tabela de figuras do cabecalho do MATERIAL.md

Os localizadores [P###] sao os mesmos nos tres arquivos e no inteiro.

Uso:
    python scripts/partir_material.py <extracao.txt> <MATERIAL.md> -o <prefixo>
        grava <prefixo>-pontas.md, <prefixo>-artefatos.md, <prefixo>-apoio.md
    python scripts/partir_material.py --autoteste
"""
import argparse
import importlib.util
import io
import re
import sys
import tempfile
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

AQUI = Path(__file__).resolve().parent


def _modulo(nome):
    s = importlib.util.spec_from_file_location(nome, AQUI / (nome + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


APENDICE = re.compile(r"^[^\w\sÀ-ÿ]{0,20}\s*(AP[EÊ]NDICE|ANEXO|APPENDIX|ANNEX)\b", re.I)
NUMERO = re.compile(r"^[^\w\sÀ-ÿ]{0,20}\s*(\d{1,2}(?:\.\d{1,2}){0,3})[.)]?\s")


def nivel(texto):
    """Profundidade do numero de secao no inicio do titulo: '1.' -> 1, '2.1' -> 2.
    None quando o titulo nao comeca por numero."""
    m = NUMERO.match(texto)
    return m.group(1).count(".") + 1 if m else None


def fronteiras_das_partes(P, titulos_numerados):
    """Devolve (pontas, apoio, artefatos) como conjuntos de numeros de paragrafo.

    P: dict n -> (pagina, tipo, texto), como `mapa_estrutural.ler` devolve.
    titulos_numerados: lista de (n, texto) dos titulos de secao numerados.
    """
    mapa = _modulo("mapa_estrutural")
    fr = mapa.fronteiras(P)
    todos = sorted(P)
    N = todos[-1]
    tit = sorted(n for n, _ in titulos_numerados)
    aps = [n for n in todos if APENDICE.match(P[n][2])]

    # A introducao: do inicio do trabalho ate o titulo que vem depois do ULTIMO
    # titulo de introducao (um trabalho pode ter "1. Introducao" e "2.1 Introducao").
    intros = mapa.acha(P, r"[^\w\sÀ-ÿ]{0,20}\s*(?:\d{1,2}(?:\.\d{1,2}){0,3}[.)]?\s+)?"
                          r"(INTRODU[CÇ][AÃ]O|INTRODUCTION)\b")
    refer = fr["referencias"]
    intros = [n for n in intros if refer is None or n < refer]
    if intros:
        ultimo_intro = intros[-1]
        # A introducao acaba no proximo titulo de nivel igual ou superior ao dela:
        # "1.1 Objetivos" ainda e introducao; "2. Metodo" nao. Sem nivel legivel
        # no titulo da introducao, vale o proximo titulo numerado.
        nivel_intro = nivel(P[ultimo_intro][2])
        depois = [t for t in tit if t > ultimo_intro
                  and (nivel_intro is None or (nivel(P[t][2]) or 1) <= nivel_intro)]
        fim_intro = depois[0] if depois else (fr["conclusao"] or refer or N + 1)
    else:
        fim_intro = fr["intro"] or todos[0]
    inicio_pontas = todos[0]

    # A conclusao: do titulo dela ate as referencias, ou o primeiro apendice
    # depois dela, ou o fim.
    concl = fr["conclusao"]
    if concl is not None:
        limites = [x for x in [refer] + [a for a in aps if a > concl] if x]
        fim_concl = min(limites) if limites else N + 1
        conclusao = set(n for n in todos if concl <= n < fim_concl)
    else:
        conclusao = set()

    # O apoio: da lista de referencias ate o primeiro apendice depois dela.
    if refer is not None:
        depois = [a for a in aps if a > refer]
        fim_ref = depois[0] if depois else N + 1
        apoio = set(n for n in todos if refer <= n < fim_ref)
    else:
        apoio = set()

    pontas = set(n for n in todos if inicio_pontas <= n < fim_intro) | conclusao
    pontas -= apoio
    artefatos = set(todos) - pontas - apoio
    return pontas, apoio, artefatos, dict(fim_intro=fim_intro, conclusao=concl,
                                          referencias=refer, apendices=aps[:1])


def cabecalho_do_material(material):
    """Do MATERIAL.md, o cabecalho ate a linha de separacao do trabalho: o sumario,
    a tabela de figuras e o mapa. Vai inteiro para os artefatos."""
    t = io.open(material, encoding="utf-8", errors="replace").read()
    i = t.find("=" * 78)
    return t[:i].rstrip() if i > 0 else ""


def escrever(prefixo, nome, ns, P, notas, extra, o_que, o_que_nao):
    linhas = ["# Material da leitura, parte `%s`\n" % nome,
              "Esta parte traz **%s**. Não traz %s: isso está nas outras duas partes, "
              "e o trabalho inteiro está em `MATERIAL.md`. Os localizadores `[P###]` "
              "são os mesmos em todas as partes.\n" % (o_que, o_que_nao)]
    if ns:
        linhas.append("Parágrafos desta parte: %d, de [P%d] a [P%d], com saltos onde "
                      "o trecho pertence a outra parte.\n" % (len(ns), min(ns), max(ns)))
    if extra:
        linhas.append(extra + "\n")
    linhas.append("=" * 78)
    linhas.append("O TRABALHO, NESTA PARTE")
    linhas.append("=" * 78 + "\n")
    for n in sorted(ns):
        linhas.append("[P%d] %s\n" % (n, P[n][2]))
    if notas:
        linhas.append("-" * 78)
        linhas.append("AS NOTAS DE RODAPÉ\n")
        for n in sorted(notas):
            linhas.append("[nota %d] %s\n" % (n, notas[n]))
    texto = "\n".join(linhas)
    alvo = Path("%s-%s.md" % (prefixo, nome))
    io.open(alvo, "w", encoding="utf-8").write(texto)
    return alvo, len(texto.split())


def partir(extracao, material, prefixo):
    mapa = _modulo("mapa_estrutural")
    montar = _modulo("montar_material")
    P = mapa.ler(extracao)
    ps, notas = montar.paragrafos(extracao)
    tit = montar.titulos(ps)
    pontas, apoio, artefatos, info = fronteiras_das_partes(P, tit)
    todos = set(P)
    if pontas | apoio | artefatos != todos or (pontas & apoio) or (pontas & artefatos) \
            or (apoio & artefatos):
        raise SystemExit("!! a partição não fecha: %d + %d + %d contra %d parágrafos"
                         % (len(pontas), len(apoio), len(artefatos), len(todos)))
    cab = cabecalho_do_material(material) if material else ""
    saidas = [
        escrever(prefixo, "pontas", pontas, P, {}, "",
                 "o resumo, o abstract, a introdução e a conclusão",
                 "o corpo, os apêndices, as referências nem as notas"),
        escrever(prefixo, "artefatos", artefatos, P, {}, cab,
                 "o corpo depois da introdução, os apêndices e anexos, o sumário e a "
                 "tabela de figuras",
                 "o resumo, a introdução, a conclusão, as referências nem as notas"),
        escrever(prefixo, "apoio", apoio, P, notas, "",
                 "a lista de referências e as notas de rodapé",
                 "o corpo, as pontas nem os apêndices"),
    ]
    return saidas, info, (len(pontas), len(artefatos), len(apoio), len(notas))


def autoteste():
    """Controle positivo: uma extracao sintetica com as cinco pecas, e a particao
    tem de por cada uma no lugar e cobrir tudo uma vez so."""
    ps = [
        "RESUMO", "texto do resumo " * 30, "ABSTRACT", "abstract text " * 30,
        "1. INTRODUÇÃO", "a introdução diz " * 40, "1.1 Objetivos", "objetivos " * 30,
        "2. MÉTODO", "o método foi " * 40, "3. RESULTADOS", "a tabela mostra " * 40,
        "4. CONCLUSÃO", "conclui-se que " * 40, "REFERÊNCIAS", "AUTOR, A. Obra. 2020.",
        "APÊNDICE A — PLANILHA", "REG-001 " * 20,
    ]
    d = Path(tempfile.mkdtemp())
    ext = d / "controle.txt"
    ext.write_text("\n\n".join("[P%d] %s" % (i + 1, t) for i, t in enumerate(ps)),
                   encoding="utf-8")
    mat = d / "MATERIAL.md"
    mat.write_text("# Material\n\n## O sumário\n\n  [P5] 1. INTRODUÇÃO\n\n" + "=" * 78
                   + "\nO TRABALHO\n", encoding="utf-8")
    saidas, info, conta = partir(str(ext), str(mat), str(d / "M"))
    pon = (d / "M-pontas.md").read_text(encoding="utf-8")
    art = (d / "M-artefatos.md").read_text(encoding="utf-8")
    apo = (d / "M-apoio.md").read_text(encoding="utf-8")
    assert "[P1]" in pon and "[P6]" in pon and "[P8]" in pon and "[P13]" in pon, "pontas"
    assert "[P9]" not in pon and "[P15]" not in pon and "[P17]" not in pon, "pontas leva demais"
    assert "[P9]" in art and "[P12]" in art and "[P17]" in art and "[P18]" in art, "artefatos"
    assert "[P13]" not in art and "[P1]" not in art, "artefatos leva ponta"
    assert "[P15]" in apo and "[P16]" in apo and "[P17]" not in apo, "apoio"
    assert "## O sumário" in art and "## O sumário" not in pon, "cabeçalho só nos artefatos"
    assert conta[:3] == (10, 6, 2), conta
    assert nivel("1. INTRODUÇÃO") == 1 and nivel("2.1 Introdução") == 2 \
        and nivel(";;;;;2.5 CONCLUSÕES") == 2 and nivel("RESUMO") is None
    print("  autoteste: 18 parágrafos sintéticos, 10 pontas (a subseção 1.1 fica na "
          "introdução), 6 artefatos, 2 apoio, nenhum fora e nenhum em dois")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("extracao", nargs="?")
    ap.add_argument("material", nargs="?", help="o MATERIAL.md inteiro, para copiar o cabeçalho")
    ap.add_argument("-o", "--prefixo", help="prefixo dos três arquivos de saída")
    ap.add_argument("--autoteste", action="store_true")
    a = ap.parse_args()
    if a.autoteste:
        return autoteste()
    if not (a.extracao and a.prefixo):
        ap.error("preciso da extração e do prefixo de saída")
    autoteste()
    saidas, info, conta = partir(a.extracao, a.material, a.prefixo)
    print("  fronteiras: introdução até [P%s); conclusão em [P%s]; referências em [P%s]; "
          "primeiro apêndice em %s"
          % (info["fim_intro"], info["conclusao"], info["referencias"],
             ("[P%d]" % info["apendices"][0]) if info["apendices"] else "nenhum"))
    for alvo, palavras in saidas:
        print("  %s  (%d palavras)" % (alvo, palavras))
    print("  %d pontas, %d artefatos, %d apoio, %d nota(s); a partição fecha."
          % conta)
    if info["conclusao"] is None:
        print("  !! sem conclusão achada: a parte das pontas só tem a introdução, e a "
              "conclusão, se existir, foi para os artefatos. Confira o mapa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

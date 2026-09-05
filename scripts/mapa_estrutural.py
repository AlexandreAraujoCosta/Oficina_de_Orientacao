# -*- coding: utf-8 -*-
"""Monta o mapa estrutural de um trabalho a partir da extracao numerada.

O mapa e o insumo das leituras: entre 6 e 13 mil palavras, algo entre 12% e 13%
do trabalho, e foi medido que basta. Numa comparacao de 31/08/2026, dos onze
apontamentos que so a travessia sequencial produziu, dez estavam ao alcance do
mapa e um exigia percorrer o texto.

CORRECAO DE 31/08/2026: o mapa nao trazia a lista de referencias, e por isso as
duas leituras ficaram cegas para citacoes que nao fecham com ela, que o pedido
cru achou. Controle do defeito: no mapa antigo de uma dissertacao, `REFER` = 0 e
`Reboul` = 0. As referencias entram agora.

DUAS FORMAS DE EXTRACAO, E A ANTIGA JA NAO EXISTE NO ACERVO

A forma para a qual este programa nasceu era
    [trabalho] P123 [TIPO] (p.45) texto
e nenhuma das doze extracoes da bancada a usa mais: `analisar_docx.py` e
`analisar_pdf.py` escrevem `[P123] texto`, em paragrafo que pode ocupar varias
linhas e que pode vir precedido de marcador de titulo (`## `), de negrito
(`**`) ou de citacao (`> `). Em 05/09/2026 o programa morria com `max() arg is
an empty sequence` sobre qualquer arquivo do acervo, e com ele morria o insumo
das leituras 1, 2 e 3. As duas formas passam a ser lidas.

A pagina nao existe na forma nova. Ela entra pelo `--paginas`, o JSON de
`paginas.py`, e onde nao houver o mapa diz `s.p.` em vez de inventar numero.
"""
import json
import re
import sys
import pathlib
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINHA = re.compile(
    r"^\[(?P<etq>[^\]]+)\]\s+P(?P<n>\d+)(?:\s+\[(?P<tipo>[A-Z_]+)\])?"
    r"\s+\(p\.(?P<pag>\d+)\)\s*(?P<txt>.*)$", re.M)
# A forma nova. O localizador nao e ancorado em inicio de linha, porque a linha
# comeca por `##`, `**` ou `> ` num numero grande de paragrafos: num trabalho
# medido, ancorar perdia 47 de 886.
NOVA = re.compile(r"^(?P<pre>[>#*\t ]*)\[P(?P<n>\d+)\]\s*(?P<txt>.*?)"
                  r"(?=\n[ \t]*\n|\Z)", re.S | re.M)
# o marcador de markdown que a extracao poe em volta do texto do paragrafo
ENFEITE = re.compile(r"^[>#*\s]+|[*\s]+$")

# marcas de item de relatorio anterior, que a extracao as vezes carrega
SUJEIRA = re.compile(r"^(?:[FCSDQ]\d+|SC\d+|\d+)(?:,\s*(?:[FCSDQ]\d+|SC\d+|\d+))*\s{2,}")


def ler(caminho, paginas=None):
    bruto = pathlib.Path(caminho).read_text(encoding="utf-8")
    P = {}
    for m in LINHA.finditer(bruto):
        P[int(m.group("n"))] = (int(m.group("pag")),
                                m.group("tipo") or "",
                                SUJEIRA.sub("", m.group("txt")).strip())
    if P:
        esperado = len(re.findall(r"^\[[^\]]+\]\s+P\d+", bruto, re.M))
        if len(P) != esperado:
            sys.exit("!! extrator quebrado: %d de %d paragrafos" % (len(P), esperado))
        return P

    pags = {}
    if paginas:
        pags = {int(k): v for k, v in
                json.loads(pathlib.Path(paginas).read_text(encoding="utf-8")).items()}
    for m in NOVA.finditer(bruto):
        n = int(m.group("n"))
        txt = ENFEITE.sub("", " ".join(m.group("txt").split()))
        # O nivel do titulo vem do marcador que o extrator escreve antes do
        # localizador. E o unico sinal de hierarquia que sobra: nesta bancada
        # a maioria dos trabalhos nao numera os titulos no corpo, e o programa
        # so os procurava por numero, devolvendo zero titulo de secao.
        grades = m.group("pre").count("#")
        P[n] = (pags.get(n, 0), "T%d" % grades if grades else "",
                SUJEIRA.sub("", txt).strip())
    esperado = len(set(re.findall(r"\[P(\d+)\]", bruto)))
    if len(P) != esperado:
        sys.exit("!! extrator quebrado: %d de %d paragrafos" % (len(P), esperado))
    return P


# linha de sumario: titulo seguido de pontilhado ate o numero da pagina
SUMARIO = re.compile(r"\.{4,}\s*\d*\s*$")


def acha(P, padrao, so_inicio=True, fora_do_sumario=True):
    """Paragrafos cujo texto casa o padrao.

    Linhas de sumario sao descartadas por padrao: elas repetem todos os
    titulos do trabalho e, sem esse filtro, a introducao e localizada na
    pagina do indice. Defeito medido em 31/08/2026."""
    f = re.match if so_inicio else re.search
    return sorted(n for n, (_, _, t) in P.items()
                  if f(padrao, t, flags=re.I)
                  and not (fora_do_sumario and SUMARIO.search(t)))


def fronteiras(P):
    """Descobre as pecas. O sumario repete os titulos, entao a ocorrencia que
    vale e a ultima das primeiras: a do corpo, e nao a da lista."""
    N = max(P)
    def ultima(padrao, minimo=0):
        c = [n for n in acha(P, padrao) if n > minimo]
        return c[-1] if c else None
    # O limite de comprimento nao e enfeite: sem ele, `^RESUMO\b` casa o
    # titulo "Resumo do perfil decisorio do controle concentrado por ambiente",
    # no fim de um trabalho que nao tem resumo nenhum, e o mapa passa a dizer
    # que ha resumo. Medido em 05/09/2026.
    curto = lambda ns: [n for n in ns if len(P[n][2]) <= 40]
    resumo = (curto(acha(P, r"^RESUMO\b")) or [None])[0]
    abstract = (curto(acha(P, r"^ABSTRACT\b")) or [None])[0]
    refer = ultima(r"^REFER[EÊ]NCIAS?\b")
    concl = ultima(r"^(CONCLUS[AÃ]O|CONSIDERA[CÇ][OÕ]ES FINAIS)\b")
    intro = ultima(r"^INTRODU[CÇ][AÃ]O\b")
    if intro is None or (refer and intro > refer):
        # o corpo comeca depois do sumario e das listas, e a ultima linha
        # pontilhada e o fim deles
        pontilhadas = [k for k in P if SUMARIO.search(P[k][2])]
        # o zero fica na lista: sem resumo, sem abstract e sem sumario
        # pontilhado, `if x` esvaziava a lista e o max morria.
        base = max([x for x in (resumo, abstract) if x] + [0]
                   + ([max(pontilhadas)] if pontilhadas else []))
        cand = [k for k in sorted(P) if k > base and not P[k][1]
                and len(P[k][2]) > 220 and not SUMARIO.search(P[k][2])]
        intro = cand[0] if cand else None
    # a conclusao tem de vir antes das referencias
    if concl and refer and concl > refer:
        c = [n for n in acha(P, r"^(CONCLUS[AÃ]O|CONSIDERA[CÇ][OÕ]ES FINAIS)\b") if n < refer]
        concl = c[-1] if c else None
    return dict(resumo=resumo, abstract=abstract, intro=intro,
                conclusao=concl, referencias=refer, fim=N)


def montar(P, fr, nome):
    def bloco(titulo, ns):
        corpo = ["[P%d] (%s) %s" % (n, "p.%d" % P[n][0] if P[n][0] else "s.p.",
                                    P[n][2])
                 for n in ns if n in P and P[n][2]]
        return "## %s\n\n%s" % (titulo, "\n\n".join(corpo)) if corpo else None

    partes, aviso = [], []
    r, a, i, c, rf, N = (fr["resumo"], fr["abstract"], fr["intro"],
                         fr["conclusao"], fr["referencias"], fr["fim"])

    if r:
        fim = a if a and a > r else r + 12
        partes.append(bloco("Resumo, palavras-chave e abstract", range(r, min(fim + 8, N))))
    else:
        aviso.append("resumo nao localizado")

    if i:
        partes.append(bloco("Introdução", range(i, i + 60)))
    else:
        aviso.append("introdução nao localizada")

    lim_a, lim_b = (i or 0), (c or rf or N)
    tit = [n for n in P if lim_a < n < lim_b and len(P[n][2]) < 170
           and (re.match(r"^\d+(\.\d+)*\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", P[n][2])
                or P[n][1].startswith("T"))]
    partes.append(bloco("Títulos de seção", tit))

    leg = [n for n in P if re.match(r"^(Quadro|Tabela|Gráfico|Figura|Imagem)\s*\d+", P[n][2])
           and len(P[n][2]) < 330]
    partes.append(bloco("Legendas de quadros, tabelas, gráficos e figuras", leg))

    ap = [n for n in P if re.match(r"^(AP[EÊ]NDICE|ANEXO)\b", P[n][2], flags=re.I)]
    ap = [n for n in ap if n > (c or 0) or not c]
    partes.append(bloco("Apêndices e anexos", sorted(ap)))

    if c and rf:
        partes.append(bloco("Conclusão", range(c, rf)))
    else:
        aviso.append("conclusão ou referências nao localizadas")

    # A LISTA DE REFERENCIAS, que faltava e cegou duas leituras
    if rf:
        fim_ref = min([n for n in ap if n > rf] or [N + 1])
        partes.append(bloco("Referências", range(rf, fim_ref)))
    else:
        aviso.append("referências nao localizadas")

    txt = "# Mapa estrutural · %s\n\n" % nome
    if aviso:
        txt += "**Peças não localizadas por programa: %s.** Quem ler deve procurá-las na extração.\n\n" % "; ".join(aviso)
    txt += "\n\n".join(p for p in partes if p) + "\n"
    return txt


CONTROLE = u"""##EXTRACAO fonte=controle.docx

## [P1] RESUMO

[P2] Este trabalho examina uma coisa e conclui outra, ao longo de muitas
palavras que existem so para o paragrafo ter corpo bastante para nao ser
confundido com titulo por nenhum dos filtros de comprimento deste programa.

## [P3] ABSTRACT

[P4] This work examines something.

## [P5] INTRODUÇÃO

[P6] A pergunta que este trabalho faz nasce de uma controversia que a
literatura registra ha bastante tempo, e a introducao a enuncia com todas as
letras para que ninguem precise deduzi-la do resto do texto.

### [P7] Metodologia

[P8] Um paragrafo de metodo.

[P9] Gráfico 1 - Um título de legenda qualquer

## [P10] CONCLUSÃO

[P11] O trabalho conclui o que prometeu.

## [P12] REFERÊNCIAS

[P13] AUTOR, Um. Um título. Cidade: Editora, 2020.
"""


def autoteste():
    """O programa acha o que esta la, e perde o que foi adulterado."""
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    alvo = d / "controle_mapa.txt"
    alvo.write_text(CONTROLE, encoding="utf-8")
    P = ler(str(alvo))
    if len(P) != 13:
        sys.exit("!! o leitor pegou %d de 13 paragrafos do controle" % len(P))
    fr = fronteiras(P)
    esperado = dict(resumo=1, abstract=3, intro=5, conclusao=10, referencias=12)
    for k, v in esperado.items():
        if fr[k] != v:
            sys.exit("!! %s deu %r, e o controle diz %r" % (k, fr[k], v))
    txt = montar(P, fr, "controle")
    for s in ("## Resumo", "## Introdução", "## Conclusão", "## Referências",
              "## Títulos de seção", "Metodologia", "Gráfico 1"):
        if s not in txt:
            sys.exit("!! o mapa do controle nao traz %r" % s)

    # adulterado: sem os titulos, as fronteiras tem de se perder
    ruim = ler(str(alvo)) and None
    alvo.write_text(CONTROLE.replace("CONCLUSÃO", "CONVERSA")
                            .replace("REFERÊNCIAS", "REFERIDOS"), encoding="utf-8")
    fr2 = fronteiras(ler(str(alvo)))
    if fr2["conclusao"] is not None or fr2["referencias"] is not None:
        sys.exit("!! o programa acha conclusao e referencias onde nao ha; "
                 "nao confie nele")
    print("  autoteste: as cinco fronteiras do controle sao achadas, o mapa "
          "traz as sete pecas esperadas, e as duas adulteradas se perdem")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("extracao")
    ap.add_argument("-o", "--saida", default="MAPA.md")
    ap.add_argument("-n", "--nome", default="trabalho")
    ap.add_argument("--paginas", help="o JSON de paginas.py, para a forma nova "
                                      "de extracao, que nao traz pagina")
    args = ap.parse_args()

    autoteste()
    P = ler(args.extracao, args.paginas)
    fr = fronteiras(P)
    txt = montar(P, fr, args.nome)
    pathlib.Path(args.saida).write_text(txt, encoding="utf-8")

    # CONTROLE POSITIVO: o mapa tem de conter o que sabemos que ele deve conter
    faltas = [r for r in ("## Resumo", "## Conclusão", "## Referências",
                          "## Títulos de seção") if r not in txt]
    print("  fronteiras: %s" % fr)
    print("  mapa: %d palavras (~%d tokens), %.1f%% dos %d parágrafos"
          % (len(txt.split()), len(txt) // 4,
             100 * len(re.findall(r"\[P\d+\]", txt)) / len(P), len(P)))
    if faltas:
        print("  !! SECOES AUSENTES: %s" % ", ".join(faltas))
    else:
        print("  controle positivo: as quatro seções obrigatórias estão no mapa")


if __name__ == "__main__":
    main()

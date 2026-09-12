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

DUAS FORMAS DE EXTRACAO, UMA POR EXTRATOR

A forma para a qual este programa nasceu era
    [trabalho] P123 [TIPO] (p.45) texto
e ela continua viva: `analisar_pdf.py` a escreve, e cinco das treze extracoes
da bancada estao nela. O que mudou foi o outro extrator. `analisar_docx.py`
escreve `[P123] texto`, em paragrafo que pode ocupar varias linhas e que pode
vir precedido de marcador de titulo (`## `), de negrito (`**`) ou de citacao
(`> `), e as outras oito extracoes estao nessa forma. Em 05/09/2026 o programa
morria com `max() arg is an empty sequence` sobre qualquer trabalho vindo de
`.docx`, e com ele morria o insumo das leituras 1, 2 e 3. As duas formas passam
a ser lidas.

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
    # SEPARAR O RESUMO DO TITULO QUE COMECA COM A MESMA PALAVRA
    #
    # `^RESUMO\b` casa tambem "Resumo do perfil decisorio do controle
    # concentrado por ambiente", que e titulo de secao no fim de um trabalho
    # sem resumo nenhum, e o mapa passava a dizer que ha resumo. Medido em
    # 05/09/2026. O comprimento sozinho nao separa os dois, porque na extracao
    # de PDF o titulo vem grudado no texto que ele encabeca, e o resumo
    # verdadeiro ocupa um paragrafo inteiro. O que separa e a palavra seguinte:
    # "Resumo DO perfil" nomeia o resumo de outra coisa; o resumo do trabalho e
    # seguido do proprio texto, ou de nada.
    DE = re.compile(r"^(RESUMO|ABSTRACT)\s+(?:d[aoe]s?|of|from)\b", re.I)

    def peca(padrao):
        return [n for n in acha(P, padrao) if not DE.match(P[n][2])]

    # O TRABALHO PODE ESTAR EM INGLES, E O MAPA ERA MONOLINGUE. Medido em
    # 05/09/2026: numa tese de doutorado da UnB escrita em ingles, com secoes
    # "1. Introduction", "6. Conclusion" e "REFERENCES", o mapa disse que nao
    # havia conclusao nem referencias, e teria cegado as leituras que partem
    # dessas duas pecas. O numero de secao tambem entra, porque o trabalho
    # numera os titulos no corpo.
    # O NUMERO DE SECAO TEM MAIS DE UM NIVEL, E O TITULO PODE VIR SUJO.
    # Medido em 09/09/2026 sobre sete extracoes: "5.6 Sintese conclusiva" nao
    # casava porque o padrao so admitia um nivel, e o titulo do trabalho K chega
    # como ";;;;;;;;;;;;;;;2.5 CONCLUSOES E RECOMENDACOES", com quinze pontos
    # e virgulas que a celula de tabela deixou colados na frente. Nos dois
    # casos o `^` do padrao batia na sujeira e a secao sumia do mapa.
    NUM = r"[^\w\sÀ-ÿ]{0,20}\s*(?:\d{1,2}(?:\.\d{1,2}){0,3}[.)]?\s+)?"
    resumo = (peca(NUM + r"RESUMO\b") or [None])[0]
    abstract = (peca(NUM + r"ABSTRACT\b") or [None])[0]
    refer = ultima(NUM + r"(REFER[EÊ]NCIAS?|REFERENCES|BIBLIOGRAPHY)\b")

    # O FECHO TEM TRES NOMES, E O MAPA CONHECIA DOIS.
    #
    # Discussao, conclusao e consideracoes finais fazem o mesmo trabalho.
    # Podem aparecer juntas, e o mais comum e haver so uma. "Discussao" nao
    # estava na lista, e na dissertacao T, que fecha com
    # "DISCUSSAO: a necessidade de se diferenciar...", o mapa acusou conclusao
    # ausente num trabalho que conclui. Medido em 09/09/2026.
    #
    # Onde houver mais de um, o bloco comeca no primeiro: quem escreve
    # Discussao e depois Consideracoes finais quer as duas no mapa, e parar na
    # ultima perderia a primeira inteira. Mas "primeiro" so vale perto do fim,
    # porque "Discussao dos resultados" e titulo comum no meio de capitulo
    # empirico, e comecar ali engoliria metade do trabalho.
    FECHO = (NUM + r"(CONCLUS[AÃ]O|CONCLUS[OÕ]ES|CONSIDERA[CÇ][OÕ]ES FINAIS"
             r"|DISCUSS[AÃ]O|CONCLUSIONS?|DISCUSSION|FINAL REMARKS"
             r"|CONCLUDING REMARKS)\b")
    fechos = acha(P, FECHO)

    intro = ultima(NUM + r"(INTRODU[CÇ][AÃ]O|INTRODUCTION)\b")
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
    # O fecho fica entre a introducao e as referencias. Fora dessa faixa e
    # linha de sumario ou secao homonima, e nao abre o bloco.
    dentro = [n for n in fechos
              if (intro is None or n > intro) and (refer is None or n < refer)]
    if dentro:
        fim_corpo = refer or N
        base = intro or 0
        limiar = base + 0.75 * (fim_corpo - base)
        tarde = [n for n in dentro if n >= limiar]
        concl = tarde[0] if tarde else dentro[-1]
    else:
        concl = None
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

    # O `\d{1,3}\s+` do comeco nao e enfeite: na extracao de PDF, o numero da
    # pagina impressa cola no inicio do paragrafo seguinte, e a legenda da
    # Tabela 6 de uma dissertacao comecava por "98 Tabela 6 - ...". Ancorada
    # sem essa folga, ela sumia do mapa, e uma leitura passou a tratar como
    # ausente a legenda que existe. Medido em 05/09/2026.
    leg = [n for n in P
           if re.match(r"^(?:\d{1,3}\s+)?(Quadro|Tabela|Gráfico|Figura|Imagem)\s*\d+",
                       P[n][2])
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


CONTROLE_INGLES = u"""##EXTRACAO fonte=controle_en.docx

## [P1] ABSTRACT

[P2] This dissertation asks whether a concept can be built at all, and the
paragraph is long enough not to be mistaken for a heading by any of the length
filters that this program applies to the pieces it looks for.

## [P3] 1. Introduction

[P4] The question this work asks comes from a controversy that the literature
has registered for a long time, and the introduction states it plainly so that
nobody has to infer it from the rest of the text.

### [P5] 1.1 Method

[P6] A paragraph about method.

## [P7] 6. Conclusion

[P8] The work concludes what it promised.

## [P9] REFERENCES

[P10] AUTHOR, One. A title. City: Press, 2020.
"""

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
    alvo.write_text(CONTROLE.replace("CONCLUSÃO", "CONVERSA")
                            .replace("REFERÊNCIAS", "REFERIDOS"), encoding="utf-8")
    fr2 = fronteiras(ler(str(alvo)))
    if fr2["conclusao"] is not None or fr2["referencias"] is not None:
        sys.exit("!! o programa acha conclusao e referencias onde nao ha; "
                 "nao confie nele")

    # o falso positivo medido: um trabalho SEM resumo, com uma secao chamada
    # "Resumo dos achados". O programa nao pode chama-la de resumo.
    alvo.write_text(CONTROLE.replace("## [P1] RESUMO", "## [P1] Resumo dos achados"),
                    encoding="utf-8")
    fr3 = fronteiras(ler(str(alvo)))
    if fr3["resumo"] is not None:
        sys.exit("!! o programa toma 'Resumo dos achados' por resumo do trabalho; "
                 "nao confie nele")
    # O MESMO CONTROLE EM INGLES: sem ele, o mapa volta a ser monolingue sem
    # que nada acuse, e as leituras que partem do resumo e da conclusao ficam
    # cegas num trabalho inteiro.
    alvo.write_text(CONTROLE_INGLES, encoding="utf-8")
    fr4 = fronteiras(ler(str(alvo)))
    esperado_en = dict(resumo=None, abstract=1, intro=3, conclusao=7, referencias=9)
    for k, v in esperado_en.items():
        if fr4[k] != v:
            sys.exit("!! no controle em ingles, %s deu %r e o esperado e %r"
                     % (k, fr4[k], v))

    # OS TRES NOMES DO FECHO. O trabalho que fecha em "Discussao" concluia
    # sem que o mapa achasse a conclusao; o que fecha nos dois nomes tem de
    # abrir o bloco no primeiro; e "Discussao dos resultados" no meio de um
    # capitulo nao pode abrir bloco nenhum.
    alvo.write_text(CONTROLE.replace("## [P10] CONCLUSÃO",
                                     "## [P10] DISCUSSÃO"), encoding="utf-8")
    if fronteiras(ler(str(alvo)))["conclusao"] != 10:
        sys.exit("!! o trabalho que fecha em 'Discussao' aparece sem conclusao")

    dois = CONTROLE.replace(
        "## [P10] CONCLUSÃO\n\n[P11] O trabalho conclui o que prometeu.",
        "## [P10] DISCUSSÃO\n\n[P11] O trabalho discute o que achou.\n\n"
        "## [P11b] CONSIDERAÇÕES FINAIS\n\n[P11c] E entao encerra.")
    alvo.write_text(dois.replace("[P11b]", "[P14]").replace("[P11c]", "[P15]"),
                    encoding="utf-8")
    if fronteiras(ler(str(alvo)))["conclusao"] != 10:
        sys.exit("!! com Discussao e Consideracoes finais, o bloco tem de "
                 "comecar na Discussao, e a primeira ficaria de fora")

    meio = CONTROLE.replace("### [P7] Metodologia",
                            "### [P7] Discussão dos resultados")
    alvo.write_text(meio, encoding="utf-8")
    if fronteiras(ler(str(alvo)))["conclusao"] != 10:
        sys.exit("!! 'Discussao dos resultados' no meio do corpo abriu o bloco "
                 "de fecho, e o mapa engoliria metade do trabalho")

    print("  autoteste: as cinco fronteiras do controle sao achadas, o mapa "
          "traz as sete pecas esperadas, as duas adulteradas se perdem e o "
          "titulo 'Resumo dos achados' nao passa por resumo; o controle "
          "em ingles acha introduction, conclusion e references; e os tres "
          "nomes do fecho sao achados sem que 'Discussao dos resultados' "
          "no meio do corpo abra bloco")


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

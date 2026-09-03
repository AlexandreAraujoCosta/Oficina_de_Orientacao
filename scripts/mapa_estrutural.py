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

Formato de entrada: a saida de extrair.py, com linhas
    [trabalho] P123 [TIPO] (p.45) texto
em que o campo [TIPO] e opcional.
"""
import re
import sys
import pathlib
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINHA = re.compile(
    r"^\[(?P<etq>[^\]]+)\]\s+P(?P<n>\d+)(?:\s+\[(?P<tipo>[A-Z_]+)\])?"
    r"\s+\(p\.(?P<pag>\d+)\)\s*(?P<txt>.*)$", re.M)

# marcas de item de relatorio anterior, que a extracao as vezes carrega
SUJEIRA = re.compile(r"^(?:[FCSDQ]\d+|SC\d+|\d+)(?:,\s*(?:[FCSDQ]\d+|SC\d+|\d+))*\s{2,}")


def ler(caminho):
    bruto = pathlib.Path(caminho).read_text(encoding="utf-8")
    P = {}
    for m in LINHA.finditer(bruto):
        P[int(m.group("n"))] = (int(m.group("pag")),
                                m.group("tipo") or "",
                                SUJEIRA.sub("", m.group("txt")).strip())
    esperado = len(re.findall(r"^\[[^\]]+\]\s+P\d+", bruto, re.M))
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
    resumo = (acha(P, r"^RESUMO\b") or [None])[0]
    abstract = (acha(P, r"^ABSTRACT\b") or [None])[0]
    refer = ultima(r"^REFER[EÊ]NCIAS?\b")
    concl = ultima(r"^(CONCLUS[AÃ]O|CONSIDERA[CÇ][OÕ]ES FINAIS)\b")
    intro = ultima(r"^INTRODU[CÇ][AÃ]O\b")
    if intro is None or (refer and intro > refer):
        # o corpo comeca depois do sumario e das listas, e a ultima linha
        # pontilhada e o fim deles
        pontilhadas = [k for k in P if SUMARIO.search(P[k][2])]
        base = max([x for x in (resumo, abstract, 0) if x]
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
        corpo = ["[P%d] (p.%d) %s" % (n, P[n][0], P[n][2])
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
    tit = [n for n in P if lim_a < n < lim_b
           and re.match(r"^\d+(\.\d+)*\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", P[n][2]) and len(P[n][2]) < 170]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("extracao")
    ap.add_argument("-o", "--saida", default="MAPA.md")
    ap.add_argument("-n", "--nome", default="trabalho")
    args = ap.parse_args()

    P = ler(args.extracao)
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

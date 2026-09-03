# -*- coding: utf-8 -*-
"""Confronta as chamadas do corpo com a lista de referências, nas duas direções.

POR QUE ISTO EXISTE

A conferência do aparato bibliográfico é a segunda das três coisas em que a
leitura completa se paga contra a rápida, e é a única das três que não é trabalho
de modelo: comparar chamada com entrada é operação determinada, e o modelo que a
faz gasta orçamento para devolver o que um programa devolve em segundos.

A lógica já existia e estava testada, e estava dentro da página do navegador, em
JavaScript, onde o agente não a alcança. Isto é a porta de linha de comando dela,
com dois acréscimos que vieram de defeitos achados em trabalho real em 03/09/2026:
a entrada com os autores invertidos em relação ao corpo, e a chamada cujo ano não
existe em entrada nenhuma daquele sobrenome.

O QUE ELE FAZ, E O QUE ELE NÃO FAZ

Ele **acha candidatos e não julga**. Parte do que ele devolve é artefato legítimo:
citação conjunta indexa um autor só, obra de três autores é chamada por *et al.*,
e um sobrenome comum colide. **A saída é para alguém abrir e decidir**, e o
relatório diz quantos descartou.

Ele **não abre fonte externa**: não diz se a obra existe, se o ano confere com a
edição, nem se ela trata do assunto para o qual foi citada. Isso é leitura.

Uso:
    python conferir_referencias.py extracao/trabalho.txt
    python conferir_referencias.py extracao/trabalho.txt --minimo 3
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


# A extração sai em dois formatos nesta oficina, e um conferidor que só entende
# um devolve zero no outro, com a mesma cara de trabalho sem defeito.
RE_MARCA_A = re.compile(r"\[P(\d+)\]")
RE_MARCA_B = re.compile(r"^\[[^\]]+\]\s*P(\d+)\s", re.M)
RE_PREFIXO_B = re.compile(r"^\s*(?:\[[^\]]*\]\s*)?(?:\(p\.\s*\d+\)\s*)?")

# Em inglês também, porque há tese em inglês neste acervo, e procurar o termo em
# português devolve zero com a mesma cara de trabalho sem lista de referências.
# Medido em 03/09/2026, numa tese de doutorado escrita em inglês.
RE_INI_REF = re.compile(
    r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA|OBRAS CITADAS"
    r"|REFERENCES?|BIBLIOGRAPHY|WORKS CITED)\b", re.I)
RE_FIM_REF = re.compile(
    r"^\s*(AP[ÊE]NDICES?|ANEXOS?|APPENDI(?:X|CES)|ANNEXE?S?)\b", re.I)

# Sobrenome em caixa alta seguido de vírgula é a forma da entrada em ABNT.
RE_SOBRENOME = re.compile(r"([A-ZÀ-Ý][A-ZÀ-Ý'\-]{2,})\s*,")
RE_ANO = re.compile(r"\b((?:19|20)\d{2})")

# As duas formas de chamada: Autor (ano) e (AUTOR, ano).
RE_CIT_ANO = re.compile(
    r"\b([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]{2,})\s*(?:et\s+al\.?)?\s*\((\d{4})[a-z]?")
RE_CIT_PAR = re.compile(
    r"\(\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]{2,})[^)]{0,60}?,\s*(\d{4})[a-z]?")

# Palavras que a expressão de chamada pega e que não são autor. A lista é do
# campo do direito, e cresce com o que aparecer.
NAO_AUTOR = set("""ANO ART ARTS LEI EMENDA RESOLUCAO TEMA ADI ADC ADPF MS HC RCL
TABELA GRAFICO FIGURA QUADRO ESQUEMA ANEXO APENDICE EM NO NA DE DO DA PARA POR
COMO SEGUNDO CONFORME ENTRE ATE DESDE AINDA APENAS ASSIM ESSE ESSA ESTE ESTA
TODOS AMBOS OUTRO DURANTE APOS ANTES SOBRE COM SEM SOB ANOS DIAS MESES PERIODO
CAPITULO SECAO ITEM NOTA FONTE PAGINA VOLUME SUPREMO TRIBUNAL SUPERIOR JUSTICA
CONSTITUICAO SUMULA VINCULANTE BRASIL DISTRITO FEDERAL""".split())


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.upper())
                   if unicodedata.category(c) != "Mn")


def paragrafos(texto):
    """Devolve {numero: texto}, entendendo os dois formatos de extração."""
    achados = {}
    for m in RE_MARCA_B.finditer(texto):
        fim = texto.find("\n[", m.end())
        corpo = texto[m.end():fim if fim > 0 else len(texto)]
        # O formato B ainda traz o papel e a página antes do texto, e sem tirá-los
        # o título da lista nunca casa: o parágrafo começa por
        # "[TITULO] (p.124) REFERÊNCIAS". Foi assim que este conferidor devolveu
        # "não encontrei a lista" no primeiro trabalho real, em 03/09/2026.
        corpo = RE_PREFIXO_B.sub("", corpo, count=1)
        achados[int(m.group(1))] = corpo
    if achados:
        return achados
    ped = RE_MARCA_A.split(texto)
    return {int(ped[i]): ped[i + 1] for i in range(1, len(ped) - 1, 2)}


def e_linha_de_sumario(t):
    """A linha do sumário casa o mesmo título e não é a lista.

    Ela se reconhece pelo pontilhado de condução ou pelo número de página no fim.
    Sem esta guarda, a faixa começa na página 10 e engole o trabalho inteiro.
    """
    return bool(re.search(r"[.…]{4,}", t) or re.search(r"\s\d{1,4}\s*$", t))


def faixa_referencias(pars):
    """(início, fim) da lista de referências, pelos títulos que a abrem e fecham.

    O título nem sempre está sozinho no parágrafo: num trabalho medido em
    03/09/2026 a extração fundiu REFERÊNCIAS com a primeira entrada, e a guarda
    de tamanho, que existia para recusar a linha do sumário, recusava a lista
    inteira junto. Hoje a linha do sumário se recusa pelo que ela é, e o título
    passa mesmo quando vem colado a uma entrada.
    """
    ini = fim = None
    for n in sorted(pars):
        t = pars[n].strip()
        if ini is None and RE_INI_REF.match(t) and not e_linha_de_sumario(t):
            if len(t) < 80 or (RE_SOBRENOME.search(t) and RE_ANO.search(t)):
                ini = n
        elif ini is not None and RE_FIM_REF.match(t) and not e_linha_de_sumario(t) \
                and len(t) < 80:
            fim = n
            break
    return ini, (fim if fim else (max(pars) + 1 if pars else 0))


def entradas(pars, ini, fim, minimo):
    """{(SOBRENOME, ano): [parágrafos]} da lista, e a ordem dos sobrenomes."""
    achadas, ordem = {}, {}
    for n in sorted(pars):
        if not (ini < n < fim):
            continue
        t = pars[n].strip()
        if len(t) < 40:
            continue
        sobres = [sem_acento(x) for x in RE_SOBRENOME.findall(t[:280])]
        ano = RE_ANO.search(t)
        if not sobres or not ano:
            continue
        for s in sobres:
            if len(s) >= minimo:
                achadas.setdefault((s, ano.group(1)), []).append(n)
        if len(sobres) > 1:
            ordem.setdefault(tuple(sobres[:3]), []).append(n)
    return achadas, ordem


def chamadas(pars, ini_corpo, fim_corpo, minimo):
    """{(SOBRENOME, ano): [parágrafos]} do corpo."""
    achadas = {}
    for n in sorted(pars):
        if not (ini_corpo <= n < fim_corpo):
            continue
        for re_ in (RE_CIT_ANO, RE_CIT_PAR):
            for m in re_.finditer(pars[n]):
                s = sem_acento(m.group(1))
                if s in NAO_AUTOR or len(s) < minimo:
                    continue
                achadas.setdefault((s, m.group(2)), []).append(n)
    return achadas


def autoteste():
    """Prova o conferidor com casos que ele TEM de acusar e TEM de deixar passar."""
    falhas = []
    fonte = (
        "[P1] INTRODUÇÃO\n\n"
        "[P2] Como sustenta Reboul (1998), a retórica é isso. E ainda "
        "(PERELMAN, 2005). Também Fantasma (1899) diz algo.\n\n"
        "[P3] REFERÊNCIAS\n\n"
        "[P4] REBOUL, Olivier. Introdução à retórica. São Paulo: Martins Fontes, 1998. "
        "Tradução de alguém, com mais de quarenta caracteres para passar no piso.\n\n"
        "[P5] PERELMAN, Chaim; OLBRECHTS-TYTECA, Lucie. Tratado da argumentação. "
        "São Paulo: Martins Fontes, 2005. Entrada longa o bastante para contar.\n\n"
        "[P6] SOLITARIO, Nunca Citado. Obra que ninguém chama. Brasília: Ed., 2010. "
        "Entrada longa o bastante para passar no piso de quarenta caracteres.\n"
    )
    pars = paragrafos(fonte)
    if len(pars) != 6:
        falhas.append("o extrator de parágrafo devolveu %d, esperava 6" % len(pars))
    ini, fim = faixa_referencias(pars)
    if ini != 3:
        falhas.append("a lista de referências foi localizada em %s, esperava 3" % ini)
    ents, _ = entradas(pars, ini, fim, 3)
    cits = chamadas(pars, 1, ini, 3)
    if ("REBOUL", "1998") not in ents:
        falhas.append("entrada existente não foi vista")
    if ("FANTASMA", "1899") not in cits:
        falhas.append("chamada sem entrada não foi vista")
    if ("FANTASMA", "1899") in ents:
        falhas.append("inventou entrada para chamada inexistente")
    if ("SOLITARIO", "2010") in cits:
        falhas.append("inventou chamada para entrada nunca citada")
    # controle negativo: uma fonte sem lista de referências não pode devolver faixa
    vazio = paragrafos("[P1] Um texto qualquer sem lista nenhuma.\n")
    if faixa_referencias(vazio)[0] is not None:
        falhas.append("achou lista de referências onde não há")
    # o segundo formato de extração tem de ser entendido
    outro = paragrafos("[trabalho] P7 [CORPO] (p.2) Texto no outro formato.\n")
    if 7 not in outro:
        falhas.append("não entende o formato [trabalho] Pnnn")
    elif outro[7].strip() != "Texto no outro formato.":
        falhas.append("não tira o papel e a página do formato [trabalho]: %r" % outro[7])
    # O caso que quebrou de verdade, em 03/09/2026: o título da lista vinha
    # atrás do papel e da página, e o conferidor calava dizendo que não achara.
    real = paragrafos(
        "[trabalho] P9 [TITULO] (p.124) REFERÊNCIAS\n"
        "[trabalho] P10 [CORPO] (p.124) AUTOR, Nome. Uma obra qualquer com mais "
        "de quarenta caracteres para passar no piso, 1998.\n")
    if faixa_referencias(real)[0] != 9:
        falhas.append("não acha a lista de referências no formato [trabalho]")
    # Os dois casos que quebraram no primeiro trabalho real: a linha do sumário
    # casa o mesmo título, e o título vem colado à primeira entrada.
    misto = paragrafos(
        "[trabalho] P1 [TITULO] (p.10) REFERÊNCIAS ................................ 123\n"
        "[trabalho] P2 [CORPO] (p.11) Prosa qualquer do corpo do trabalho.\n"
        "[trabalho] P3 [CORPO] (p.124) REFERÊNCIAS ADEODATO, João. Uma obra com "
        "mais de quarenta caracteres para passar no piso, 1999.\n")
    ingles = paragrafos(
        "[trabalho] P1 [CORPO] (p.1) Some prose in the body of the thesis.\n"
        "[trabalho] P2 [TITULO] (p.90) REFERENCES\n"
        "[trabalho] P3 [CORPO] (p.90) SMITH, John. A work with more than forty "
        "characters so that it clears the floor, 1999.\n")
    if faixa_referencias(ingles)[0] != 2:
        falhas.append("não acha a lista num trabalho em inglês")
    if faixa_referencias(misto)[0] != 3:
        falhas.append("confunde a linha do sumário com a lista, ou recusa o título "
                      "colado à primeira entrada (achou %s)" % (faixa_referencias(misto)[0],))
    return falhas


def main():
    ap = argparse.ArgumentParser(
        description="Confronta chamadas do corpo com a lista de referências.")
    ap.add_argument("extracao")
    ap.add_argument("--minimo", type=int, default=3,
                    help="tamanho mínimo do sobrenome considerado (padrão 3)")
    ap.add_argument("--teto", type=int, default=30,
                    help="quantos itens listar por classe (padrão 30)")
    a = ap.parse_args()

    falhas = autoteste()
    if falhas:
        print("  o próprio conferidor está quebrado, e não reporto nada:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste: passou (acha o que existe, não inventa o que não existe,")
    print("  entende os dois formatos de extração, e não acha lista onde não há)")

    texto = Path(a.extracao).read_text(encoding="utf-8", errors="replace")
    pars = paragrafos(texto)
    if not pars:
        print("\n  não encontrei parágrafo numerado nenhum. A extração está no formato certo?")
        return 2
    ini, fim = faixa_referencias(pars)
    if ini is None:
        print("\n  não encontrei a lista de referências. Nada a conferir.")
        return 1

    ents, ordem = entradas(pars, ini, fim, a.minimo)
    cits = chamadas(pars, min(pars), ini, a.minimo)

    ambiguos = sorted((k, v) for k, v in ents.items() if len(v) > 1)
    sem_entrada = sorted(k for k in cits if k not in ents)
    nunca_citadas = sorted(k for k in ents if k not in cits)
    # chamada cujo ano não existe em entrada nenhuma daquele sobrenome
    anos_por_sobrenome = {}
    for s, ano in ents:
        anos_por_sobrenome.setdefault(s, set()).add(ano)
    ano_errado = sorted((k, sorted(anos_por_sobrenome[k[0]]))
                        for k in sem_entrada if k[0] in anos_por_sobrenome)

    def nome(k):
        return "%s%s %s" % (k[0][0], k[0][1:].lower(), k[1])

    print("\n  %d entradas na lista, %d pares autor-ano chamados no corpo"
          % (len(ents), len(cits)))
    print("  lista de referências: parágrafos %d a %d" % (ini, fim - 1))

    print("\n  PARES AMBÍGUOS (o mesmo autor-ano com mais de uma entrada): %d" % len(ambiguos))
    for k, v in ambiguos[:a.teto]:
        print("     %-28s entradas em %s; citado %d vez(es)"
              % (nome(k), ", ".join("P%d" % x for x in v), len(cits.get(k, []))))

    print("\n  ANO QUE NÃO EXISTE NA LISTA (o sobrenome está lá, o ano não): %d" % len(ano_errado))
    for k, anos in ano_errado[:a.teto]:
        print("     %-28s a lista traz %s; chamado em %s"
              % (nome(k), "/".join(anos), ", ".join("P%d" % x for x in cits[k][:4])))

    print("\n  CHAMADO E AUSENTE DA LISTA: %d" % len(sem_entrada))
    print("     (parte é artefato de citação conjunta, em que só um autor é indexado)")
    for k in sem_entrada[:a.teto]:
        if k in dict(ano_errado):
            continue
        print("     %-28s em %s" % (nome(k), ", ".join("P%d" % x for x in cits[k][:4])))

    print("\n  NA LISTA E NUNCA CITADO: %d" % len(nunca_citadas))
    for k in nunca_citadas[:a.teto]:
        print("     %-28s entrada em %s" % (nome(k), ", ".join("P%d" % x for x in ents[k])))

    print("\n  ORDEM DOS AUTORES, para conferir contra o corpo: %d entradas com dois ou mais"
          % len(ordem))
    for autores, ps in list(ordem.items())[:a.teto]:
        print("     %-46s em %s" % (" ; ".join(a.title() for a in autores),
                                    ", ".join("P%d" % x for x in ps)))

    print("\n  Nada aqui é defeito por si. Abra cada um e decida: citação conjunta,")
    print("  sobrenome comum e obra de três autores produzem candidato legítimo.")
    print("  E o relatório diz quantos você descartou.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

Em 05/09/2026 ele devolveu uma saída inteiramente falsa sobre um trabalho real,
com o autoteste passando: ancorou a lista na linha do sumário que anuncia as
referências, e disse zero chamada no corpo de um trabalho que cita em toda
página. Daí vêm a limpeza da marcação da extração e a confirmação da âncora pela
vizinhança, que estão em faixa_referencias.

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

# A extração escreve o marcador de seção (##, **, >) no começo da linha, e no
# formato A ele cai depois do corte, colado ao fim do parágrafo ANTERIOR. Com
# ele ali, a linha do sumário "REFERÊNCIAS BIBLIOGRÁFICAS 131" deixa de terminar
# em número de página, escapa da guarda que existe para recusá-la, e a lista
# passa a começar no sumário. Medido em 05/09/2026, num trabalho real.
RE_MARCA_VAZADA = re.compile(r"\n[ \t]*(?:#{1,6}|>|\*{1,3})[ \t]*$")
RE_COMENTARIO = re.compile(r"<!--.*?-->", re.S)

# Em inglês também, porque há tese em inglês neste acervo, e procurar o termo em
# português devolve zero com a mesma cara de trabalho sem lista de referências.
# Medido em 03/09/2026, numa tese de doutorado escrita em inglês.
RE_INI_REF = re.compile(
    r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA|OBRAS CITADAS"
    r"|REFERENCES?|BIBLIOGRAPHY|WORKS CITED)\b", re.I)
# O que fecha a lista não é só apêndice e anexo. Em w-v15.txt vem um
# "Glossário" de 52 verbetes entre a última entrada e o "Apêndice A", e ele
# entrava na lista: três verbetes viraram entrada, porque "SISP: Sistema de
# Administração..." e "ETP: Estudo Técnico Preliminar (Lei nº 14...)" têm sigla
# em caixa alta, dois-pontos e ano. Medido em 05/09/2026.
RE_FIM_REF = re.compile(
    r"^\s*(AP[ÊE]NDICES?|ANEXOS?|APPENDI(?:X|CES)|ANNEXE?S?"
    r"|GLOSS[ÁA]RIO|GLOSSARY"
    r"|LISTAS?\s+DE\s+(?:SIGLAS|ABREVIATURAS|S[ÍI]MBOLOS)"
    r"|LIST\s+OF\s+(?:ABBREVIATIONS|ACRONYMS|SYMBOLS)"
    r"|[ÍI]NDICE\s+(?:REMISSIVO|ONOM[ÁA]STICO|DE\s+ASSUNTOS)"
    r"|INDEX)\b", re.I)

# Sobrenome em caixa alta seguido de vírgula é a forma da entrada em ABNT.
RE_SOBRENOME = re.compile(r"([A-ZÀ-Ý][A-ZÀ-Ý'\-]{2,})\s*,")
# Mais estreita que a de cima: aqui o nome do autor tem de ABRIR o parágrafo,
# que é a forma da entrada em ABNT. Separa a entrada da prosa do corpo, que traz
# "(STF, 2022)" no meio da frase e casaria um crivo de posição livre.
# O ponto entra junto com a vírgula porque a autoria institucional é a forma
# dominante de lista inteira neste acervo: "BRASIL. Lei nº...", "ASSOCIAÇÃO
# BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR...". Com só a vírgula, a guarda
# recusava a lista de dois dos onze trabalhos medidos em 05/09/2026.
RE_ENTRADA_ABNT = re.compile(
    r"^[\"\u201c'(\[]?\s*[A-ZÀ-Ý][A-ZÀ-Ý'\-]{2,}"
    r"(?:\s+[A-ZÀ-Ý][A-ZÀ-Ý'\-]*)*\s*[,.]")
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


def limpar(t):
    """Tira do parágrafo o que é marcação da extração, e não texto do trabalho."""
    t = RE_COMENTARIO.sub("", t)
    t = RE_MARCA_VAZADA.sub("", t.rstrip())
    return t.rstrip().rstrip("*").rstrip()


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
        achados[int(m.group(1))] = limpar(corpo)
    if achados:
        return achados
    ped = RE_MARCA_A.split(texto)
    return {int(ped[i]): limpar(ped[i + 1]) for i in range(1, len(ped) - 1, 2)}


def e_linha_de_sumario(t):
    """A linha do sumário casa o mesmo título e não é a lista.

    Ela se reconhece pelo pontilhado de condução ou pelo número de página no fim.
    Sem esta guarda, a faixa começa na página 10 e engole o trabalho inteiro.
    """
    return bool(re.search(r"[.…]{4,}", t) or re.search(r"\s\d{1,4}\s*$", t))


def forma_de_entrada(t):
    """O parágrafo abre por autor em caixa alta, com vírgula ou ponto, e traz ano."""
    t = t.strip()
    return bool(len(t) >= 40 and RE_ENTRADA_ABNT.match(t) and RE_ANO.search(t))


def confirma_vizinhanca(pars, n, janela=10, piso=0.6):
    """Depois de n vem lista, ou vem o resto do sumário e o corpo do trabalho?

    A linha do sumário casa o mesmo título da seção e nem sempre se denuncia
    sozinha: a que não traz pontilhado nem número de página é idêntica ao
    título, e o que as separa é o que vem depois de cada uma.
    """
    seguintes = [pars[m].strip() for m in sorted(pars) if m > n]
    seguintes = [t for t in seguintes if len(t) >= 40][:janela]
    if not seguintes:
        # Sem vizinhança não há o que confirmar, e também não há sumário depois:
        # o título no fim do arquivo, ou colado à única entrada, passa.
        return True
    return sum(1 for t in seguintes if forma_de_entrada(t)) >= piso * len(seguintes)


def faixa_referencias(pars):
    """(início, fim, nota) da lista, pelos títulos que a abrem e fecham.

    O título nem sempre está sozinho no parágrafo: num trabalho medido em
    03/09/2026 a extração fundiu REFERÊNCIAS com a primeira entrada, e a guarda
    de tamanho, que existia para recusar a linha do sumário, recusava a lista
    inteira junto. Hoje a linha do sumário se recusa pelo que ela é, e o título
    passa mesmo quando vem colado a uma entrada.

    A forma do parágrafo, sozinha, não basta. Em 05/09/2026 a extração pôs o
    marcador de seção do parágrafo seguinte no fim da linha do sumário; a lista
    começou na página 131 do sumário, com 699 parágrafos de corpo dentro dela e
    zero chamada achada no corpo, sem aviso nenhum. Cada candidato a título
    agora se confirma pelo que vem depois dele, e a nota diz quando nenhum se
    confirmou, em vez de a faixa errada sair calada.
    """
    candidatos = []
    for n in sorted(pars):
        t = pars[n].strip()
        if RE_INI_REF.match(t) and not e_linha_de_sumario(t):
            if len(t) < 80 or (RE_SOBRENOME.search(t) and RE_ANO.search(t)):
                candidatos.append(n)
    nota = None
    ini = next((n for n in candidatos if confirma_vizinhanca(pars, n)), None)
    if ini is None and candidatos:
        ini = candidatos[0]
        nota = ("nenhum dos %d candidatos a título da lista tem lista depois de si; "
                "ancorei no primeiro (P%d), e a faixa pode estar errada"
                % (len(candidatos), ini))
    # O fechamento tinha a guarda de tamanho que a abertura já perdera em
    # 03/09/2026, e falhava pelo mesmo motivo: em y.txt a extração funde
    # "APÊNDICE – A" com o primeiro parágrafo do apêndice, o parágrafo passa dos
    # 80 caracteres e a lista engolia 509 parágrafos de apêndice. No lugar da
    # guarda de tamanho, recusa-se o parágrafo que tenha forma de entrada, que é
    # o que ela protegia.
    fim = None
    if ini is not None:
        for n in sorted(pars):
            if n <= ini:
                continue
            t = pars[n].strip()
            if RE_FIM_REF.match(t) and not e_linha_de_sumario(t) \
                    and not forma_de_entrada(t):
                fim = n
                break
    return ini, (fim if fim else (max(pars) + 1 if pars else 0)), nota


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
    ini, fim, _ = faixa_referencias(pars)
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
    # O caso que quebrou em 05/09/2026, e que a versão anterior deste programa
    # reprova: a extração encosta o marcador de seção do parágrafo seguinte no
    # fim da linha do sumário, e com ele ali a linha não termina mais em número
    # de página. O conferidor ancorava no sumário, punha 699 parágrafos de corpo
    # dentro da lista e devolvia zero chamada no corpo, sem um aviso.
    vazado = paragrafos(
        "[P155] REFERÊNCIAS BIBLIOGRÁFICAS 131\n\n\n"
        "## [P160] ÍNDICE DE GRÁFICOS\n\n"
        "[P400] Prosa do corpo do trabalho, com tamanho de sobra para o piso.\n\n"
        "## [P1209] REFERÊNCIAS BIBLIOGRÁFICAS\n\n"
        "[P1211] ABBOUD, Georges. Monocráticas do STF são solução e não "
        "problema. Conjur, Brasília, 26 maio 2026.\n\n"
        "[P1213] ADAMY, Pedro. Plenário Virtual em matéria tributária e o "
        "déficit deliberativo. Revista Direito Tributário Atual, n. 46, 2020.\n\n"
        "[P1215] BASTOS, Ana Carolina. STF: sugestões para o aperfeiçoamento "
        "do plenário virtual. Jota, Brasília, 2021.\n")
    if faixa_referencias(vazado)[0] != 1209:
        falhas.append("o marcador de seção colado à linha do sumário põe a lista "
                      "no sumário (achou %s, esperava 1209)"
                      % (faixa_referencias(vazado)[0],))
    # A linha do sumário sem pontilhado e sem número de página é idêntica ao
    # título da seção, e nada na forma dela a denuncia: só o que vem depois.
    sem_pagina = paragrafos(
        "[P1] REFERÊNCIAS BIBLIOGRÁFICAS\n\n"
        "[P2] Prosa do corpo, longa o bastante para passar em qualquer piso de "
        "tamanho que o programa venha a aplicar adiante.\n\n"
        "[P3] Mais prosa do corpo, igualmente longa, e sem forma nenhuma de "
        "entrada bibliográfica, para que a vizinhança fale.\n\n"
        "[P4] Terceira prosa do corpo, do mesmo feitio das duas de cima, e sem "
        "sobrenome em caixa alta abrindo o parágrafo.\n\n"
        "[P5] REFERÊNCIAS BIBLIOGRÁFICAS\n\n"
        "[P6] ABBOUD, Georges. Monocráticas do STF são solução e não problema. "
        "Conjur, Brasília, 26 maio 2026.\n\n"
        "[P7] ADAMY, Pedro. Plenário Virtual em matéria tributária e o déficit "
        "deliberativo. Revista Direito Tributário Atual, n. 46, 2020.\n\n"
        "[P8] BASTOS, Ana Carolina. STF: sugestões para o aperfeiçoamento do "
        "plenário virtual. Jota, Brasília, 2021.\n")
    if faixa_referencias(sem_pagina)[0] != 5:
        falhas.append("ancora no anúncio do sumário que não traz número de página "
                      "(achou %s, esperava 5)" % (faixa_referencias(sem_pagina)[0],))
    # Controle da própria guarda de vizinhança: ela não pode recusar a lista de
    # um trabalho que traga apêndice logo depois das poucas entradas.
    curta = paragrafos(
        "[P1] Prosa do corpo, com tamanho de sobra para passar no piso "
        "de quarenta caracteres que o programa aplica.\n\n"
        "[P2] REFERÊNCIAS\n\n"
        "[P3] REBOUL, Olivier. Introdução à retórica. São Paulo: Martins "
        "Fontes, 1998. Entrada longa o bastante para contar.\n\n"
        "[P4] APÊNDICE A\n")
    if faixa_referencias(curta)[0] != 2:
        falhas.append("a guarda de vizinhança recusa lista curta seguida de "
                      "apêndice (achou %s, esperava 2)" % (faixa_referencias(curta)[0],))
    # O mesmo defeito na outra ponta, achado em 05/09/2026: o título do apêndice
    # vem colado ao primeiro parágrafo dele, e a lista ia até o fim do arquivo.
    apendice = paragrafos(
        "[P1] Prosa do corpo, com tamanho de sobra para passar no piso de "
        "quarenta caracteres que o programa aplica.\n\n"
        "[P2] REFERÊNCIAS\n\n"
        "[P3] REBOUL, Olivier. Introdução à retórica. São Paulo: Martins "
        "Fontes, 1998. Entrada longa o bastante para contar.\n\n"
        "[P4] APÊNDICE – A Este apêndice reúne a decomposição analítica dos "
        "acórdãos, e passa dos oitenta caracteres com folga.\n\n"
        "[P5] SOLITARIO, Nunca Citado. Obra que está no apêndice e não na "
        "lista. Brasília: Ed., 2010. Entrada longa o bastante.\n")
    if faixa_referencias(apendice)[1] != 4:
        falhas.append("o título do apêndice colado ao texto dele não fecha a "
                      "lista (fim %s, esperava 4)" % (faixa_referencias(apendice)[1],))
    # O glossário que se põe entre a lista e o apêndice, achado em w-v15 em
    # 05/09/2026: o verbete tem sigla em caixa alta, dois-pontos e ano, e conta
    # como entrada de quem só souber fechar a lista em apêndice e anexo.
    glossario = paragrafos(
        "[P1] Prosa do corpo, com tamanho de sobra para passar no piso de "
        "quarenta caracteres que o programa aplica.\n\n"
        "[P2] REFERÊNCIAS\n\n"
        "[P3] WILLIAMSON, Oliver E. As instituições econômicas do capitalismo. "
        "São Paulo: Pearson, 2012. Entrada longa o bastante.\n\n"
        "[P4] Glossário\n\n"
        "[P5] ETP: Estudo Técnico Preliminar. Documento de planejamento das "
        "contratações públicas, na Lei nº 14.133, de 2021.\n\n"
        "[P6] Apêndice A\n")
    if faixa_referencias(glossario)[1] != 4:
        falhas.append("o glossário entre a lista e o apêndice não fecha a lista "
                      "(fim %s, esperava 4)" % (faixa_referencias(glossario)[1],))
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
    print("  entende os dois formatos de extração, não acha lista onde não há, e")
    print("  não ancora a lista na linha do sumário que anuncia as referências)")

    texto = Path(a.extracao).read_text(encoding="utf-8", errors="replace")
    pars = paragrafos(texto)
    if not pars:
        print("\n  não encontrei parágrafo numerado nenhum. A extração está no formato certo?")
        return 2
    ini, fim, nota = faixa_referencias(pars)
    if ini is None:
        print("\n  não encontrei a lista de referências. Nada a conferir.")
        return 1
    if nota:
        print("\n  ATENÇÃO, a ancoragem não se confirmou: %s." % nota)
        print("  Confira a faixa abaixo antes de usar qualquer número desta saída.")

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

    # O que se conta são pares autor-ano, e não entradas: a entrada com três
    # autores rende três pares. Dizer "entradas" convidava a cotejar este número
    # com a contagem de parágrafos da lista, que é outra coisa.
    na_faixa = [n for n in pars if ini < n < fim and len(pars[n].strip()) >= 40]
    print("\n  %d pares autor-ano na lista, %d chamados no corpo"
          % (len(ents), len(cits)))
    print("  lista de referências: título em P%d, %d parágrafos com texto de P%d a P%d"
          % (ini, len(na_faixa),
             min(na_faixa) if na_faixa else ini, max(na_faixa) if na_faixa else fim - 1))

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

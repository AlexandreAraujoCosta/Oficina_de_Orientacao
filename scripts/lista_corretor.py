# -*- coding: utf-8 -*-
"""Extrai do relatorio a lista de itens que o corretor executa.

POR QUE ISTO EXISTE

O corretor recebe o trabalho, o relatorio e o anexo, e precisa percorrer os itens
um a um. Ate 27/08/2026 ele fazia isso lendo a prosa do relatorio inteiro, o que
custa caro e permite pular item. Este programa devolve o indice: codigo, o que o
item aponta, e os paragrafos que ele manda abrir.

E programa, e nao modelo, porque a operacao e mecanica: os itens tem forma
regular no relatorio (`**S29. titulo**` no corpo, `### S13. titulo` no anexo) e
os localizadores estao escritos. Redigitar isso com modelo introduziria erro numa
tarefa que nao tem julgamento nenhum.

O que ele NAO faz: nao resume o item, nao decide prioridade, nao inventa a
correcao. O texto que justifica cada apontamento continua no relatorio, e o
corretor precisa dos dois.

    python lista_corretor.py <relatorio.md> [anexo.md] [--saida X.md]
"""
import argparse
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



# Duas formas convivem, e ambas aparecem tanto no relatorio quanto no anexo:
# negrito abrindo paragrafo (`**S11. ...**`) e titulo (`### S11. ...`). Ate
# 27/08/2026 o anexo so era lido na forma de titulo, e por isso os itens de
# anexo de dois dos trabalhos medidos, que usam negrito, ficavam de fora sem
# que nada acusasse. As duas passam a valer nos dois arquivos.
# O codigo em negrito abre a linha OU vem depois de ponto final, dentro do
# paragrafo. A segunda forma nao era lida ate 06/09/2026, e o Alberto a usa nos
# itens de superficie, que ele agrupa varios por paragrafo:
#     **SC5.** [P511] e um marcador de pendencia. **SC6.** [P513], o mesmo.
# Numa entrega de 59 itens, seis ficavam de fora sem que nada acusasse, e a
# contagem nao mostrava porque os que sobravam eram numerados na sequencia.
# O que separa isto de uma referencia cruzada em prosa ("como ja se disse em
# **S9**") e a exigencia de ponto final antes e de conteudo depois.
RE_NEGRITO = re.compile(
    r"(?:^\s*(?:\d+[.)]\s*)?|(?<=[.!?])[ 	]+)"
    r"\*\*([A-Z]{1,2}\d+)[.,:]?\s*(.*?)\*\*", re.M)
# O [ \t]* no lugar de \s* nao e detalhe: \s atravessa a quebra de
# linha, e por isso o titulo ia buscar a primeira linha do paragrafo
# seguinte. Com o Luis isso nunca aparecia, porque ele escreve o nome do
# item na mesma linha do titulo. A Clara escreve o codigo sozinho e o texto
# abaixo, em prosa com quebra dura, e ai o titulo saia cortado na primeira
# quebra: 42 dos 66 comentarios de uma entrega chegaram sem o defeito dito,
# medido pelo conferidor de compreensibilidade em 29/08/2026.
RE_TITULO = re.compile(
    r"^#{2,4}[ \t]*([A-Z]{1,2}\d+)[ \t]*[.,:—–·|-]?[ \t]*(.*?)[ \t]*$", re.M)
# Duas escritas do mesmo campo. O Luis e a Clara escrevem `**Aponta:**` no
# comeco da linha; o Alberto escreve `- **Aponta**`, dentro de item de lista e
# sem dois-pontos. Ate 05/09/2026 so a primeira era lida, e por isso os itens
# de superficie do Alberto chegavam a margem do Word VAZIOS: numa entrega de
# 39 itens, 13 comentarios em branco, sem que nada acusasse.
RE_APONTA = re.compile(
    r"^[-*]?[ \t]*\*\*Aponta:?\*\*[ \t]*(.+?)(?=\n[ \t]*\n|\Z)", re.M | re.S)
# O campo seguinte fecha o anterior, e ele vem em qualquer das duas escritas.
PROXIMO_CAMPO = r"\n[ \t]*[-*]?[ \t]*\*\*[A-Za-zÀ-ú][^*\n]{0,40}:?\*\*"
RE_LOC = re.compile(r"\[P\d+(?:[-–]P?\d+)?\]")

# F e C nao sao correcao: sao ponto forte e contribuicao a reivindicar, e mandar
# o corretor "consertar" um ponto forte e o pior erro que este arquivo poderia
# induzir.
EXECUTAVEIS = ("S", "D", "SC")


def fronteiras(texto):
    """Onde comeca cada item, nas DUAS escritas juntas.

    Ate 06/09/2026 cada escrita era varrida por sua conta, e o corpo de um item
    terminava na proxima marca DA MESMA escrita. Num relatorio em que a secao das
    decisoes usa negrito (`**D6. ...**`) e a das correcoes usa titulo
    (`#### S1 - ...`), o ultimo D em negrito nao encontrava outro negrito adiante
    e ia ate o fim do arquivo: engolia a secao inteira das correcoes. O item D6 de
    uma entrega saiu com a providencia de S1 colada, a linha `Marca` de S3, e um
    campo `Abrir` com 111 localizadores, que eram os de todos os itens somados.
    Quem achou foi a conferencia de compreensibilidade; nenhum programa acusava,
    e o meu controle so olhava para item CURTO DEMAIS.
    """
    pos = set()
    for rx in (RE_NEGRITO, RE_TITULO):
        for m in rx.finditer(texto):
            pos.add(m.start())
    # Titulo de secao tambem fecha item: nenhum item atravessa um cabecalho.
    # Sem isto, o ULTIMO item de uma secao ia ate o proximo item, e engolia a
    # prosa que fecha a secao mais a abertura da seguinte. Medido em 06/09/2026:
    # o item S18 de uma entrega saiu com 57 localizadores, dos quais 27 eram
    # dele e 30 vinham dos cinco mil caracteres de prosa que ele engoliu.
    for m in re.finditer(r"^#{1,6}[ 	]", texto, re.M):
        pos.add(m.start())
    return sorted(pos)


def itens(texto, origem, regex):
    achados = []
    marcas = list(regex.finditer(texto))
    corte = fronteiras(texto)
    for i, m in enumerate(marcas):
        cod, titulo = m.group(1), m.group(2).strip()
        if not cod.rstrip("0123456789") in EXECUTAVEIS:
            continue
        adiante = [c for c in corte if c > m.start()]
        fim = adiante[0] if adiante else len(texto)
        corpo = texto[m.start():fim]
        locs = []
        for l in RE_LOC.findall(corpo):
            if l not in locs:
                locs.append(l)
        # Formato de contrato: o codigo sozinho no titulo, e o texto no bloco
        # **Aponta:**. Sem isto o item entra com titulo vazio e o comentario
        # sai em branco na margem.
        if not titulo:
            ap = RE_APONTA.search(corpo)
            if ap:
                titulo = " ".join(ap.group(1).split())
        # O item de superficie do Alberto nao tem campo nenhum: e o codigo em
        # negrito seguido da prosa, no mesmo paragrafo. Sem isto ele entra com
        # titulo vazio, e o comentario sai em branco na margem.
        if not titulo:
            resto = corpo[m.end() - m.start():].split("\n\n")[0]
            if resto.strip():
                titulo = " ".join(resto.split())

        # "- **S9**, pela razao acima" e referencia cruzada numa lista de
        # prioridade, e nao o item. O que separa e o bloco TER CAMPO de item;
        # o tamanho so decide onde nao ha campo nenhum.
        #
        # Ate 06/09/2026 a regra era so de tamanho (titulo curto e corpo abaixo
        # de 200 caracteres). Ela funcionava por acidente: o corpo do ultimo
        # item de uma escrita ia ate o fim do arquivo, e por isso nunca era
        # curto. Consertada a fronteira, um item legitimo de campo curto passou
        # a ser descartado, e o controle acusou.
        tem_campo = re.search(
            r"^[-*]?[ 	]*\*\*(?:Aponta|O que fazer|Tipo)[.:]?\*\*", corpo, re.M)
        if not tem_campo and not locs and len(titulo) < 25                 and len(corpo.strip()) < 200:
            continue

        # O TITULO DIAGNOSTICA; O COMENTARIO NA MARGEM TEM DE DIZER O QUE FAZER.
        #
        # Na margem do Word chega este titulo, e nada mais: a demonstracao e a
        # providencia ficam no relatorio, que quem corrige nao tem ao lado do
        # paragrafo. Uma conferencia de compreensibilidade em 01/09/2026
        # reprovou quatro de vinte e seis itens exatamente por isso, e a frase
        # que a leitora escrevia comecava por "procurar". Se o item traz
        # `**O que fazer:**`, ele entra aqui, colado ao diagnostico.
        # Para no proximo campo em negrito, e nao so na linha em branco: sem
        # isso `**O que muda:**` entrava junto, e ele e do relatorio, nao da
        # margem. Quem corrige quer a providencia, e a consequencia ja esta
        # dita no documento que acompanha.
        # `O que poderia ser dito depois` e o campo de providencia das sugestoes
        # de desenvolvimento, que nao mandam consertar e sim acrescentar. Ate
        # 06/09/2026 so `O que fazer` era lido, e por isso os tres itens desse
        # genero de um relatorio chegavam a margem so com o diagnostico; a
        # conferencia de compreensibilidade reprovou os tres, pela mesma causa.
        fazer = re.search(
            r"^[-*]?[ 	]*\*\*(?:O que fazer|O que poderia ser dito depois):?\*\*"
            r"\s*(.+?)"
            r"(?=\n\s*\n|" + PROXIMO_CAMPO + r"|\Z)",
            corpo, re.M | re.S)
        if fazer:
            titulo = "%s. O que fazer: %s" % (
                titulo.rstrip("."), " ".join(fazer.group(1).split()))
        # A instrucao curta que o item traz quando a correcao e a mesma em cada
        # ocorrencia. Ela decide, no anotar_docx.py, se o item marca todos os
        # pontos que cita ou um so; sem ela, item que cita quinze lugares
        # marcaria os quinze e a margem viraria eco.
        # Ate 02/09/2026 este padrao terminava em `$` com re.M, e por isso
        # capturava so a PRIMEIRA LINHA FISICA do campo. Num relatorio em que
        # o `Marca` ocupava duas linhas, o texto que ia para a margem do Word
        # acabava em preposicao ("conferir se ha entrada correspondente na"),
        # e uma conferencia de compreensibilidade leu isso como frase cortada
        # do proprio relatorio. Nao era: o relatorio estava inteiro, e quem
        # cortava era este programa. Agora vai ate a linha em branco ou ate o
        # campo seguinte em negrito, como o `O que fazer`.
        mm = re.search(
            r"^[-*]?[ \t]*\*\*Marca:?\*\*\s*(.+?)"
            r"(?=\n\s*\n|" + PROXIMO_CAMPO + r"|\Z)",
            corpo, re.M | re.S)
        achados.append((cod, titulo, locs, origem, mm.group(1) if mm else None))
    return achados


def main():
    ap = argparse.ArgumentParser(description="Indice de itens para o corretor.")
    ap.add_argument("relatorio")
    ap.add_argument("anexo", nargs="?")
    ap.add_argument("--saida")
    a = ap.parse_args()

    def ler(caminho, origem):
        txt = Path(caminho).read_text(encoding="utf-8")
        achados = itens(txt, origem, RE_NEGRITO) + itens(txt, origem, RE_TITULO)
        # O mesmo codigo pode casar nas duas formas; fica a de titulo, que traz
        # o item inteiro, e nao a linha que so o referencia numa lista.
        melhor = {}
        for cod, tit, locs, org, mrc in achados:
            ant = melhor.get(cod)
            if ant is None or len(tit) > len(ant[1]) or len(locs) > len(ant[2]):
                # A marca vem de onde estiver: se a forma vencedora nao a traz e
                # a outra traz, ela nao pode se perder na escolha.
                melhor[cod] = (cod, tit, locs, org, mrc or (ant[4] if ant else None))
        return list(melhor.values())

    todos = ler(a.relatorio, "relatório")
    if a.anexo and Path(a.anexo).exists():
        vistos = {c for c, *_ in todos}
        todos += [x for x in ler(a.anexo, "anexo") if x[0] not in vistos]

    if not todos:
        sys.exit("nenhum item reconhecido." + '\n\n' + "Cada item precisa abrir com um codigo, numa destas duas formas:" + '\n\n' + "### D1. Nome curto do item" + '\n' + "**D1. Nome curto do item**" + '\n\n' + "O codigo e uma ou duas maiusculas mais numero, e as executaveis sao" + '\n' + "D, S e SC. Item sem localizador [Pxxx] na prosa tambem e descartado.")

    def chave(t):
        cod = t[0]
        return (EXECUTAVEIS.index(cod.rstrip("0123456789")), int(re.sub(r"\D", "", cod)))
    todos.sort(key=chave)

    L = [
        "# Itens para o corretor",
        "",
        "Gerado por `lista_corretor.py` a partir de `%s`. **Não edite:** é índice, e o"
        % Path(a.relatorio).name,
        "que justifica cada item continua no relatório, que precisa ir junto.",
        "",
        "Cada bloco traz o código, o que o item aponta e os parágrafos que ele manda abrir.",
        "`S` é correção, `D` é desenvolvimento e `SC` é sugestão complementar. O campo",
        "*Onde está* diz se o item veio do corpo do relatório ou do anexo.",
        "",
        "---",
        "",
    ]
    for cod, titulo, locs, origem, marca in todos:
        L.append("## %s" % cod)
        L.append("")
        L.append("**Aponta:** %s" % titulo)
        L.append("")
        if marca:
            L.append("**Marca:** %s" % marca)
            L.append("")
        L.append("**Abrir:** %s" % (" ".join(locs) if locs else "(sem localizador no item)"))
        L.append("")
        L.append("**Onde está:** %s" % origem)
        L.append("")

    saida = Path(a.saida) if a.saida else \
        Path(a.relatorio).with_name("CORRETOR-" + Path(a.relatorio).name)
    saida.write_text("\n".join(L) + "\n", encoding="utf-8")
    por = {}
    for cod, *_ in todos:
        por[cod.rstrip("0123456789")] = por.get(cod.rstrip("0123456789"), 0) + 1
    print("  %s: %d itens (%s)" % (saida.name, len(todos),
          ", ".join("%s %d" % (k, v) for k, v in sorted(por.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Normaliza o .docx antes da analise, e diz o que mudou.

POR QUE ISTO EXISTE

Trabalho de estudante raramente chega com formatacao feita por estilo. O padrao
observado e outro: o estilo nominal do paragrafo tipico nao e o estilo Normal, e
sim algum estilo importado numa colagem; o estilo muda ao longo do texto, com
varios tipos de paragrafo cumprindo a mesma funcao; e sobre o estilo vem uma
camada de formatacao direta que torna tudo parecido na tela sem tornar nada
igual no arquivo. O espacamento entre blocos e feito com paragrafo vazio, e nao
com espaco antes e depois.

Isso custa em tres lugares. A camada formal da analise acusa como desvio o que e
so ruido de colagem. A numeracao de paragrafo, que e o localizador do relatorio,
muda quando qualquer coisa e apagada. E a paginacao depende de linhas em branco
que nao deveriam existir.

QUANDO RODAR: na entrada, antes de extrair.

Depois de extrair, nao: todo localizador do relatorio se refere a um arquivo
determinado, e normalizar em seguida desloca a numeracao inteira sem que nada
acuse. A ordem e normalizar, extrair, analisar, paginar, comentar.

O QUE ELE FAZ

Apaga paragrafo vazio, convertendo a altura dele em espaco depois do paragrafo
anterior. Junta espaco repetido. Reconhece tres papeis (corpo, referencia e
legenda) e **alinha cada papel a uma forma so**. Poe no estilo de legenda os
paragrafos que descrevem figura. E tira o recuo e o paragrafo sobrando dos
separadores de nota de rodape.

UM ESTILO POR PAPEL, E NAO POR FORMA

Contar as formas encontradas e criar um estilo para cada uma organiza a
aparencia e cimenta a desordem. Legenda que sai em tres formatos nao tem tres
padroes: tem falta de padrao. Dar um estilo a cada variante faz cada uma passar
a ser correta pelo seu proprio estilo, e a camada formal da analise deixa de
enxergar o desvio. Multiplicar estilo e tao ruim quanto nao ter nenhum.

Por isso o papel manda, e a forma dominante daquele papel vira o estilo de todos
os paragrafos dele. Os que estavam diferentes mudam de aparencia, e essa mudanca
e o proprio conserto: ela vem contada no relatorio.

O QUE ELE NAO FAZ

Nao toca na formatacao de corrida de texto, onde moram fonte e corpo de letra:
ali o que se ve muda palavra a palavra, e o ganho nao paga o risco. Nao inventa
forma: cada estilo criado recebe a forma que aqueles paragrafos ja tinham, e por
isso a aparencia nao muda. E nao reescreve estilo existente, porque quem herda
dele sem formatacao direta para se defender mudaria de aparencia junto.

Quando nenhuma forma reune metade do papel, o programa nao alinha e diz por
que: nao ha versao assentada a que alinhar, e escolher uma e decisao de quem
escreveu. Com `--forcar`, vale a mais frequente.

Bloco recuado e linha curta ficam fora dos tres papeis. Recuo proprio e legitimo
na citacao longa, no item de lista e na definicao, e alinha-los ao corpo
destruiria o recuo que o autor quis. Formatacao que aparece uma vez so tambem
fica: raramente e descuido, e costuma ser espaco posto a mao para empurrar um
titulo para a folha seguinte. O relatorio conta quantas sao e quantas tem essa
cara, porque a correcao ali e uma quebra de pagina, e nao um estilo.

    python scripts/normalizar_docx.py trabalho.docx --so-relatorio
    python scripts/normalizar_docx.py trabalho.docx --estilos --legendas --notas
"""
import argparse
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RE_PAR = re.compile(rb"<w:p(?: [^>]*)?/>|<w:p(?: [^>]*)?>.*?</w:p>", re.S)
RE_TBL = re.compile(rb"<w:tbl(?: [^>]*)?>.*?</w:tbl>", re.S)
RE_TEXTO = re.compile(rb"<w:t(?: [^>]*)?>(.*?)</w:t>", re.S)
RE_PPR_BRUTO = re.compile(rb"<w:pPr(?: [^>]*)?>(.*?)</w:pPr>", re.S)
RE_CONTEUDO = re.compile(rb"<w:r[ >]|<w:hyperlink[ >]|<w:p[ >]|<w:sdt[ >]|<w:fldSimple[ >]")


class _PPr:
    """Busca o pPr do proprio paragrafo, e so ele.

    `RE_PPR.search(bloco)` devolvia o primeiro pPr do trecho, que num paragrafo
    com caixa de texto e o pPr do paragrafo de dentro. O programa entao tirava o
    recuo e trocava o estilo do que esta dentro da caixa. Como o esquema manda o
    pPr ser o primeiro filho do paragrafo, basta procurar antes do primeiro
    conteudo."""

    @staticmethod
    def search(bloco):
        # Depois da tag de abertura do proprio paragrafo, senao o padrao de
        # conteudo casa com ela na posicao zero e a janela sai vazia.
        ab = re.match(rb"<w:p(?: [^>]*)?>", bloco)
        ini = ab.end() if ab else 0
        m = RE_CONTEUDO.search(bloco, ini)
        return RE_PPR_BRUTO.search(bloco, ini, m.start() if m else len(bloco))


RE_PPR = _PPr
RE_ESTILO = re.compile(rb'<w:pStyle w:val="([^"]*)"')
RE_LINHA = re.compile(rb'<w:spacing[^>]*w:line="(\d+)"')

# As quatro travas. Paragrafo vazio que traz qualquer uma delas nao e espaco em
# branco: e estrutura, e apaga-lo estraga o documento de outra pessoa em
# silencio, que e o pior defeito que uma ferramenta assim pode ter.
TRAVAS = (
    (rb"<w:sectPr", "quebra de seção"),
    (rb'<w:br[^>]*w:type="(?:page|column)"|<w:pageBreakBefore(?: [^>]*)?/>',
     "quebra de página ou coluna"),
    (rb"<w:drawing|<w:pict|<w:object", "âncora de imagem"),
    (rb"<w:bookmarkStart|<w:bookmarkEnd|<w:commentRangeStart|<w:commentRangeEnd"
     rb"|<w:commentReference|<w:footnoteReference|<w:endnoteReference",
     "âncora de nota, marcador ou comentário"),
    # Campo e alteracao controlada nao aparecem em <w:t>, e por isso o paragrafo
    # que so os contem parecia vazio. Apaga-lo quebraria a remissao cruzada ou
    # jogaria fora o historico de revisao do arquivo de outra pessoa.
    (rb"<w:fldChar|<w:instrText|<w:delText|<w:ins[ >]|<w:del[ >]",
     "campo ou alteração controlada"),
)

# Ordem imposta pelo esquema: w:spacing entra antes de w:ind, w:jc e w:rPr, e
# um arquivo com pPr fora de ordem e recusado por leitor menos tolerante.
AUTOR_REV = "Norma"
DATA_REV = "2026-01-01T12:00:00Z"
_rev = [0]


def _id():
    _rev[0] += 1
    return _rev[0]


def marca_rev(tag):
    """`<w:del ...>` ou `<w:pPrChange ...>` com identificador unico e autor."""
    return b'<w:%s w:id="%d" w:author="%s" w:date="%s"' % (
        tag, _id(), AUTOR_REV.encode(), DATA_REV.encode())


def apagar_com_revisao(bloco):
    """Marca o paragrafo como apagado em vez de retira-lo do arquivo.

    Apagar paragrafo com controle de alteracoes e marcar a MARCA de paragrafo
    como excluida, dentro do rPr do pPr, e nao remover o `<w:p>`. Quem aceitar a
    alteracao junta este paragrafo ao seguinte, que e o efeito de apagar. Os
    paragrafos aqui sao vazios, entao nao ha corrida de texto a envolver em
    `<w:del>`.

    O `<w:del/>` tem de vir antes dos outros filhos do rPr: a ordem e imposta
    pelo esquema, e arquivo fora de ordem e recusado por leitor menos tolerante.
    """
    del_tag = marca_rev(b"del") + b"/>"
    m = RE_PPR.search(bloco)
    if not m:
        ab = re.match(rb"<w:p(?: [^>]*)?>", bloco)
        if not ab:
            return bloco
        return (bloco[:ab.end()] + b"<w:pPr><w:rPr>" + del_tag + b"</w:rPr></w:pPr>"
                + bloco[ab.end():])
    corpo = m.group(1)
    mr = re.search(rb"<w:rPr(?: [^>]*)?>", corpo)
    if mr:
        corpo2 = corpo[:mr.end()] + del_tag + corpo[mr.end():]
    elif re.search(rb"<w:rPr(?: [^>]*)?/>", corpo):
        corpo2 = re.sub(rb"<w:rPr(?: [^>]*)?/>", b"<w:rPr>" + del_tag + b"</w:rPr>",
                        corpo, count=1)
    else:
        # rPr e o penultimo filho de pPr, antes so de sectPr e pPrChange.
        pos = len(corpo)
        for tag in (b"<w:sectPr", b"<w:pPrChange"):
            i = corpo.find(tag)
            if i != -1:
                pos = min(pos, i)
        corpo2 = corpo[:pos] + b"<w:rPr>" + del_tag + b"</w:rPr>" + corpo[pos:]
    return bloco[:m.start(1)] + corpo2 + bloco[m.end(1):]


def com_ppr_change(antigo, novo):
    """Registra, no paragrafo novo, qual era a forma anterior.

    `w:pPrChange` guarda o pPr de antes e e o que faz o Word mostrar a mudanca
    de formatacao como alteracao controlada. Vai no fim do pPr, porque e o
    ultimo filho na sequencia que o esquema define."""
    if antigo == novo:
        return novo
    mv = RE_PPR.search(antigo)
    velho_ppr = b"<w:pPr>" + (mv.group(1) if mv else b"") + b"</w:pPr>"
    mn = RE_PPR.search(novo)
    troca = marca_rev(b"pPrChange") + b">" + velho_ppr + b"</w:pPrChange>"
    if mn:
        return novo[:mn.end(1)] + troca + novo[mn.end(1):]
    ab = re.match(rb"<w:p(?: [^>]*)?>", novo)
    if not ab:
        return novo
    return novo[:ab.end()] + b"<w:pPr>" + troca + b"</w:pPr>" + novo[ab.end():]


TETO = 2400          # o maximo de espaco depois que uma conversao pode gerar

DEPOIS_DE_SPACING = (b"<w:ind", b"<w:contextualSpacing", b"<w:jc",
                     b"<w:outlineLvl", b"<w:rPr", b"<w:sectPr")


RE_ABRE = re.compile(rb"<w:p(?: [^>]*)?>|<w:p(?: [^>]*)?/>|</w:p>")


def paragrafos(doc):
    """Os paragrafos de primeiro nivel, como (inicio, fim).

    Nao serve expressao regular com `.*?</w:p>`: caixa de texto guarda
    paragrafos dentro de um paragrafo, e a busca preguicosa fecha no `</w:p>`
    de dentro. Apagar o que ela devolve deixa um `</w:p>` orfao e o Word recusa
    o arquivo. Aqui a varredura conta profundidade e devolve so o de fora."""
    saida, pilha = [], []
    for m in RE_ABRE.finditer(doc):
        tag = m.group(0)
        if tag.endswith(b"/>"):
            if not pilha:
                saida.append((m.start(), m.end()))
        elif tag.startswith(b"</"):
            if pilha:
                ini = pilha.pop()
                if not pilha:
                    saida.append((ini, m.end()))
        else:
            pilha.append(m.start())
    return saida


RE_SUMARIO = re.compile(r"(Gr[áa]fico|Quadro|Tabela|Figura|Ap[êe]ndice)\s+(\d{1,2})",
                        re.I)
RE_PAGINA = re.compile(r"\s\d{1,3}$")


def fim_do_pretextual(doc, pars, teto=0.45, piso=0.15):
    """O indice do paragrafo em que o corpo comeca.

    A capa, a folha de rosto, a de aprovacao, a dedicatoria, o resumo e o
    sumario sao diagramados a mao, com linha em branco empurrando bloco para
    baixo da pagina. Apagar essas linhas comprime a capa, e foi o que aconteceu
    na primeira execucao. Ali nao ha forma dominante a restaurar, e normalizar
    nao rende nada: o pre-textual fica inteiro como esta.

    O criterio e o mesmo do `conferir_consistencia.py`, para as duas ferramentas
    nao discordarem sobre onde o trabalho comeca: entrada de indice acaba em
    numero de pagina, e legenda de corpo nunca acaba."""
    comtexto = [(i, texto_de(doc[ini:fim]))
                for i, (ini, fim) in enumerate(pars) if not vazio(doc[ini:fim])]
    if not comtexto:
        return 0
    ultimo = 0
    for k, (i, txt) in enumerate(comtexto[:int(len(comtexto) * teto)]):
        if RE_SUMARIO.search(txt or "") and RE_PAGINA.search((txt or "").strip()):
            ultimo = k
    k = ultimo + 1 if ultimo else int(len(comtexto) * piso)
    return comtexto[min(k, len(comtexto) - 1)][0]


RE_ABRE_TBL = re.compile(rb"<w:tbl(?: [^>]*)?>|</w:tbl>")


def dentro_de_tabela(doc):
    """Os intervalos de bytes ocupados por tabela, para nao mexer dentro delas.

    Com profundidade, e nao com `<w:tbl>.*?</w:tbl>`: tabela dentro de celula faz
    a busca preguicosa fechar no `</w:tbl>` de dentro, e o resto da tabela
    externa fica desprotegido. E o mesmo defeito que ja estava tratado para o
    paragrafo, e que eu nao tinha aplicado aqui."""
    saida, pilha = [], []
    for m in RE_ABRE_TBL.finditer(doc):
        if m.group(0).startswith(b"</"):
            if pilha:
                ini = pilha.pop()
                if not pilha:
                    saida.append((ini, m.end()))
        else:
            pilha.append(m.start())
    return saida


def vazio(bloco):
    """Sem texto visivel. Nao basta ser <w:p/>: o comum e ter pPr e nenhum texto."""
    return not b"".join(RE_TEXTO.findall(bloco)).strip()


def travado(bloco):
    for padrao, nome in TRAVAS:
        if re.search(padrao, bloco):
            return nome
    return None


def altura(bloco, padrao=240):
    """A altura do paragrafo vazio em twips, para virar espaco depois.

    Uma linha em branco de corpo mede 240 twips, que sao 12 pontos. Quando o
    proprio paragrafo declara entrelinha automatica, vale o que ele declara."""
    m = RE_LINHA.search(bloco)
    if m and b'w:lineRule="auto"' in bloco:
        return max(int(m.group(1)), 120)
    return padrao


def por_espaco_depois(bloco, twips):
    """Devolve o paragrafo com w:spacing w:after somado, respeitando a ordem."""
    m = RE_PPR.search(bloco)
    if not m:
        marca = re.match(rb"<w:p(?: [^>]*)?>", bloco)
        if not marca:
            return bloco
        return (bloco[:marca.end()]
                + b'<w:pPr><w:spacing w:after="%d"/></w:pPr>' % twips
                + bloco[marca.end():])

    corpo = m.group(1)
    sp = re.search(rb"<w:spacing(?: [^>]*)?/>", corpo)
    if sp:
        velho = sp.group(0)
        a = re.search(rb'w:after="(\d+)"', velho)
        soma = twips + (int(a.group(1)) if a else 0)
        novo = (re.sub(rb'w:after="\d+"', b'w:after="%d"' % soma, velho) if a
                else velho[:-2] + b' w:after="%d"/>' % soma)
        corpo2 = corpo.replace(velho, novo, 1)
    else:
        pos = len(corpo)
        for tag in DEPOIS_DE_SPACING:
            i = corpo.find(tag)
            if i != -1:
                pos = min(pos, i)
        corpo2 = corpo[:pos] + b'<w:spacing w:after="%d"/>' % twips + corpo[pos:]
    return bloco[:m.start(1)] + corpo2 + bloco[m.end(1):]


def junta_espacos(doc, desde=0):
    """Espaco repetido vira um so, dentro do texto e sem tocar em tabulacao.

    So a partir de `desde`, que e onde o corpo comeca. Na capa o alinhamento e
    feito com espaco repetido, e juntar tudo a desmonta, o que contraria a
    propria promessa de nao tocar no pre-textual."""
    n = [0]

    def troca(m):
        if m.start() < desde:
            return m.group(0)
        t = m.group(1)
        novo = re.sub(rb"  +", b" ", t)
        if novo != t:
            n[0] += 1
        return m.group(0).replace(t, novo, 1) if novo != t else m.group(0)

    return RE_TEXTO.sub(troca, doc), n[0]


RE_LEGENDA = re.compile(r"^(Gr[áa]fico|Tabela|Quadro|Figura|Imagem)\s*\d+\s*[-–—.:]")


def texto_de(bloco):
    return " ".join(x.decode("utf-8", "replace")
                    for x in RE_TEXTO.findall(bloco)).strip()


def forma(bloco):
    """A forma do paragrafo: alinhamento, recuo e espacamento.

    So propriedade de paragrafo. Fonte e corpo de letra ficam de fora de
    proposito: eles moram na formatacao de cada corrida de texto, e mexer neles
    e mexer no que a pessoa ve palavra a palavra."""
    pp = RE_PPR.search(bloco)
    corpo = pp.group(1) if pp else b""
    def cap(padrao):
        m = re.search(padrao, corpo)
        return m.group(0) if m else b""
    return (cap(rb"<w:jc(?: [^>]*)?/>"),
            cap(rb"<w:ind(?: [^>]*)?/>"),
            cap(rb"<w:spacing(?: [^>]*)?/>"))


def estilo_de(bloco):
    m = RE_ESTILO.search(bloco)
    return m.group(1) if m else None


def corpo_de_texto(doc, tabelas):
    """Os paragrafos que fazem o papel de corpo, que e onde a forma dominante vale.

    Ficam de fora legenda, sumario, indice de ilustracoes, titulo e tudo o que
    esta dentro de tabela: cada um tem forma propria, e comparar entre papeis
    diferentes acusa como desvio o que e o certo."""
    fora = (b"Legenda", b"Caption", b"Sumrio", b"TOC", b"ndice", b"Ttulo", b"Heading",
            b"Bibliografia", b"Citao", b"Quote", b"Nota", b"Footnote")
    saida = []
    for ini, fim in paragrafos(doc):
        b = doc[ini:fim]
        if vazio(b) or any(x <= ini < y for x, y in tabelas):
            continue
        est = estilo_de(b) or b""
        if any(x in est for x in fora):
            continue
        if RE_LEGENDA.match(texto_de(b)):
            continue
        saida.append((ini, fim))
    return saida


def diagnostico(doc):
    """O retrato dos estilos, que e o que a pessoa precisa ver para decidir."""
    pars = [doc[i:j] for i, j in paragrafos(doc)]
    corpo = [p for p in pars if not vazio(p)]
    estilos = Counter()
    direta = 0
    for p in corpo:
        m = RE_ESTILO.search(p)
        estilos[(m.group(1).decode("utf-8", "replace") if m else "(Normal)")] += 1
        pp = RE_PPR.search(p)
        if pp and re.search(rb"<w:jc|<w:ind|<w:spacing|<w:rFonts|<w:sz", pp.group(1)):
            direta += 1
    return corpo, estilos, direta


RE_REFS = re.compile(r"^\s*(REFER[ÊE]NCIAS?|BIBLIOGRAFIA)", re.I)
RE_POSREFS = re.compile(r"^\s*(AP[ÊE]NDICES?|ANEXOS?)\b", re.I)


def faixa_referencias(doc, pars):
    """Os indices em que a lista de referencias comeca e acaba.

    Serve para dar nome ao padrao, e nao para achar o padrao: as referencias sao
    encontradas por terem forma propria, como qualquer outro padrao. O que a
    faixa faz e permitir chamar o estilo pelo nome certo."""
    # A palavra REFERENCIAS aparece duas vezes: na linha do sumario e no titulo
    # da lista. O que as separa nao e a posicao, e sim o numero de pagina ao fim
    # da entrada de sumario, que e o mesmo discriminador do
    # `conferir_consistencia.py`. Piso por porcentagem nao serve: medido em
    # 28/08/2026, num trabalho com dois apendices longos o titulo estava a 57%
    # do arquivo, e um piso de 60% o descartava.
    ini = None
    for i in range(len(pars) - 1, -1, -1):
        txt = texto_de(doc[pars[i][0]:pars[i][1]])
        if txt and RE_REFS.match(txt) and len(txt) < 60 and not RE_PAGINA.search(txt.strip()):
            ini = i + 1
            break
    if ini is None:
        return None, None
    for i in range(ini, len(pars)):
        txt = texto_de(doc[pars[i][0]:pars[i][1]])
        if txt and RE_POSREFS.match(txt) and len(txt) < 60:
            return ini, i
    return ini, len(pars)


def recuado(dom):
    """A forma tem recuo esquerdo ou deslocamento, que e a assinatura do bloco
    destacado: citacao longa, item de lista, definicao."""
    ind = dom[1]
    return bool(re.search(rb'w:(?:left|start)="([1-9]\d*)"', ind)
                or re.search(rb'w:hanging="([1-9]\d*)"', ind))


PAPEIS = (("Corpo", b"CorpoOficina"),
          ("Referência", b"ReferenciaOficina"),
          ("Legenda", b"LegendaOficina"))


def papeis(doc, pars, tabelas, inicio, faixa_ref):
    """Cada paragrafo no papel que cumpre, e o que sobra a parte.

    **Um estilo por papel, e nao por forma.** Criar um estilo para cada forma
    encontrada organiza a aparencia e cimenta a desordem: tres formas de legenda
    viram tres estilos, cada variante passa a ser correta pelo seu proprio
    estilo, e a camada formal da analise deixa de enxergar o que era desvio.
    Multiplicar estilo e tao ruim quanto nao ter nenhum.

    Tres papeis se reconhecem por regra que se pode enunciar: corpo, referencia
    e legenda. O que nao se reconhece nao recebe estilo nenhum, porque batizar no
    chute afirma um papel que nao se verificou."""
    r0, r1 = faixa_ref
    achados = {nome: [] for nome, _ in PAPEIS}
    outros = []
    for i, (a, b) in enumerate(pars):
        if i < inicio or vazio(doc[a:b]):
            continue
        if any(x <= a < y for x, y in tabelas):
            continue
        est = estilo_de(doc[a:b]) or b""
        if any(x in est for x in (b"Ttulo", b"Heading", b"Sumrio", b"TOC", b"ndice")):
            continue
        txt = texto_de(doc[a:b])
        if RE_LEGENDA.match(txt):
            achados["Legenda"].append(i)
        elif r0 is not None and r0 <= i < r1:
            achados["Referência"].append(i)
        elif recuado(forma(doc[a:b])) or len(txt) <= 60:
            # Bloco recuado e linha curta tem forma propria e legitima: citacao
            # longa, item de lista, definicao. Alinha-los ao corpo destruiria o
            # recuo que o autor quis.
            outros.append(i)
        else:
            achados["Corpo"].append(i)
    return achados, outros


def empurrao(f):
    """A forma parece gambiarra para empurrar conteudo para a pagina seguinte.

    Formatacao que aparece uma vez so raramente e descuido: costuma ser espaco
    enorme posto a mao para jogar um titulo para a folha de baixo. Nomear isso
    como desvio de forma erra o diagnostico, e a correcao certa e uma quebra de
    pagina no paragrafo seguinte."""
    m = re.search(rb'w:(?:before|after)="(\d+)"', f[2] or b"")
    return bool(m and int(m.group(1)) >= 720)


def escolher_forma(doc, pars, indices, piso=0.5):
    """A forma a que o papel inteiro sera alinhado, e a fatia que ela ja tinha.

    Alinhar e o objetivo: a legenda que sai em tres formatos nao tem tres
    padroes, tem falta de padrao, e o conserto e todas ficarem iguais.

    Mas quando nenhuma forma reune metade do papel, nao ha versao assentada a
    que alinhar, e escolher no automatico seria decidir pelo autor um ponto que
    e dele. Nesse caso o programa nao mexe e diz por que."""
    c = Counter(forma(doc[pars[i][0]:pars[i][1]]) for i in indices)
    dom, n = c.most_common(1)[0]
    fatia = n / len(indices)
    return dom, fatia, len(c), fatia >= piso


def alinhar(bloco, dom, marca_id):
    """Poe o estilo do papel e retira a formatacao direta que ele ja carrega.

    Diferente de `limpar_direta`: aqui o paragrafo entra no estilo mesmo que a
    forma dele nao seja a dominante, e e por isso que a aparencia muda. Essa
    mudanca e o proprio conserto, e por isso ela e contada e relatada."""
    mudou = forma(bloco) != dom
    pp = RE_PPR.search(bloco)
    marca = b'<w:pStyle w:val="%s"/>' % marca_id
    if not pp:
        m = re.match(rb"<w:p(?: [^>]*)?>", bloco)
        if not m:
            return bloco, False
        return bloco[:m.end()] + b"<w:pPr>" + marca + b"</w:pPr>" + bloco[m.end():], mudou
    corpo = pp.group(1)
    for tag in (rb"<w:jc(?: [^>]*)?/>", rb"<w:ind(?: [^>]*)?/>",
                rb"<w:spacing(?: [^>]*)?/>"):
        corpo = re.sub(tag, b"", corpo)
    corpo = (re.sub(rb'<w:pStyle w:val="[^"]*"/>', marca, corpo, count=1)
             if RE_ESTILO.search(corpo) else marca + corpo)
    return bloco[:pp.start(1)] + corpo + bloco[pp.end(1):], mudou


def escrever_estilo(estilos_xml, base, dom, novo_id, nome):
    """Cria um estilo com a forma que aqueles paragrafos ja tinham.

    Reescrever um estilo existente seria mais simples e esta errado: quem herda
    dele sem formatacao direta para se defender muda de aparencia junto. Medido
    em 28/08/2026 numa dissertacao de 140 paginas: reescrever o Normal com a
    entrelinha dominante levou o arquivo a 147 paginas. Estilo novo, baseado no
    antigo, move apenas os paragrafos que o recebem."""
    if re.search(rb'w:styleId="%s"' % re.escape(novo_id), estilos_xml):
        return estilos_xml, True
    bloco = (b'<w:style w:type="paragraph" w:customStyle="1" w:styleId="' + novo_id + b'">'
             b'<w:name w:val="' + nome + b'"/>'
             b'<w:basedOn w:val="' + (base or b"Normal") + b'"/>'
             b'<w:qFormat/>'
             b"<w:pPr>" + b"".join(x for x in dom if x) + b"</w:pPr>"
             b"</w:style>")
    if b"</w:styles>" not in estilos_xml:
        return estilos_xml, False
    return estilos_xml.replace(b"</w:styles>", bloco + b"</w:styles>", 1), True


def limpar_separadores(notas_xml):
    """Tira o recuo e o paragrafo sobrando dos separadores de nota de rodape.

    O separador e a linha curta que o Word desenha acima das notas. Ele mora em
    `footnotes.xml`, nas notas de tipo `separator` e `continuationSeparator`, e
    herda o recuo do estilo do corpo: a linha aparece deslocada para dentro,
    porque o recuo de primeira linha da prosa nao tem sentido nenhum ali. Junto
    com ele costuma vir paragrafo vazio a mais, que abre um branco antes das
    notas. Nenhuma das duas coisas e escolha de quem escreveu."""
    ind, extras = 0, 0
    saida, pos = [], 0
    for m in re.finditer(rb'<w:footnote [^>]*w:type="(?:separator|continuationSeparator)"'
                         rb'[^>]*>.*?</w:footnote>', notas_xml, re.S):
        bloco = m.group(0)
        novo, n = re.subn(rb"<w:ind(?: [^>]*)?/>", b"", bloco)
        ind += n
        # O separador precisa de um paragrafo, e so de um: o resto e branco.
        dentro = list(re.finditer(rb"<w:p(?: [^>]*)?>.*?</w:p>|<w:p(?: [^>]*)?/>",
                                  novo, re.S))
        for extra in reversed(dentro[1:]):
            if not b"".join(RE_TEXTO.findall(extra.group(0))).strip() \
                    and b"<w:separator" not in extra.group(0) \
                    and b"<w:continuationSeparator" not in extra.group(0):
                novo = novo[:extra.start()] + novo[extra.end():]
                extras += 1
        saida.append(notas_xml[pos:m.start()]); saida.append(novo); pos = m.end()
    saida.append(notas_xml[pos:])
    return b"".join(saida), ind, extras


def virar_legenda(bloco, estilo):
    """Paragrafo que descreve grafico, tabela ou quadro recebe o estilo de legenda."""
    if estilo_de(bloco) == estilo or not RE_LEGENDA.match(texto_de(bloco)):
        return bloco, False
    marca = b'<w:pStyle w:val="%s"/>' % estilo
    pp = RE_PPR.search(bloco)
    if pp:
        corpo = pp.group(1)
        corpo = (re.sub(rb'<w:pStyle w:val="[^"]*"/>', marca, corpo, count=1)
                 if RE_ESTILO.search(corpo) else marca + corpo)
        return bloco[:pp.start(1)] + corpo + bloco[pp.end(1):], True
    m = re.match(rb"<w:p(?: [^>]*)?>", bloco)
    if not m:
        return bloco, False
    return bloco[:m.end()] + b"<w:pPr>" + marca + b"</w:pPr>" + bloco[m.end():], True


class Registro:
    """Guarda o que foi dito na tela, para gravar como anexo do relatorio.

    Quem recebe o arquivo normalizado precisa saber o que mudou nele, e o que o
    programa dizia so aparecia no terminal de quem o rodou."""

    def __init__(self):
        self.linhas = []

    def __call__(self, texto=''):
        print(texto)
        self.linhas.append(texto)

    def gravar(self, destino, origem):
        corpo = ['# Anexo: o que a normalização mudou no arquivo', '',
                 'Gerado por `normalizar_docx.py` sobre `%s`. Este anexo existe' % origem,
                 'porque quem recebe o arquivo normalizado precisa saber o que',
                 'mudou nele.', '', '```']
        corpo += [l.rstrip() for l in self.linhas]
        corpo += ['```', '']
        destino.write_text(chr(10).join(corpo), encoding='utf-8')


RE_REVISAO = re.compile(rb"<w:(ins|del)\b[^>]*w:author=\"([^\"]*)\"")


def alteracoes_pendentes(doc):
    """Quem assina as alteracoes controladas do arquivo, e quantas de cada um.

    Comentario nao entra: ele nao cria paragrafo e nao move a numeracao."""
    de = Counter()
    for m in RE_REVISAO.finditer(doc):
        de[m.group(2).decode("utf-8", "replace") or "(sem autor)"] += 1
    return de


def porta_das_alteracoes(doc, nome):
    """Para se o arquivo trouxer alteracao controlada por decidir.

    Decidido em 30/08/2026: os programas nao aceitam nem recusam por conta as
    alteracoes de ninguem. Quem decide e quem tem o arquivo."""
    de = alteracoes_pendentes(doc)
    if not de:
        return
    total = sum(de.values())
    plural = "alterações controladas" if total > 1 else "alteração controlada"
    linhas = ["",
              "%s tem %d %s por decidir, e não dá para trabalhar" % (nome, total, plural),
              "assim: enquanto elas existirem, o parágrafo apagado ainda conta, e o",
              "localizador do relatório sai deslocado do arquivo que você abre.",
              "", "Quem assina:"]
    for autor, n in de.most_common():
        linhas.append("   %-28s %4d" % (autor[:28], n))
    linhas += ["",
               "Aceite ou recuse as alterações no Word, salve, e rode de novo.",
               "Nenhum programa daqui decide por você: se a marcação for de quem",
               "orienta, aceitá-la em silêncio apagaria o trabalho dessa pessoa.",
               "Comentário não atrapalha e pode ficar."]
    sys.exit("\n".join(linhas))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trabalho")
    ap.add_argument("--saida")
    ap.add_argument("--estilos", action="store_true",
                    help="unifica a forma do corpo: escreve no estilo e tira a direta")
    ap.add_argument("--silencio", action="store_true",
                    help="grava a cópia já normalizada, sem alterações controladas. "
                         "É o modo que os analisadores usam na primeira fase da leitura, "
                         "porque a numeração de parágrafo precisa ser a final")
    ap.add_argument("--forcar", action="store_true",
                    help="alinha o papel mesmo quando nenhuma forma reúne metade dele")
    ap.add_argument("--notas", action="store_true",
                    help="tira recuo e parágrafo sobrando dos separadores de nota")
    ap.add_argument("--legendas", action="store_true",
                    help="põe no estilo de legenda os parágrafos que descrevem figura")
    ap.add_argument("--so-relatorio", action="store_true",
                    help="diz o que faria, e não grava nada")
    a = ap.parse_args()
    diz = Registro()

    origem = Path(a.trabalho)
    z = zipfile.ZipFile(origem)
    doc = z.read("word/document.xml")
    porta_das_alteracoes(doc, origem.name)

    corpo, estilos, direta = diagnostico(doc)
    diz("%s: %d parágrafos com texto" % (origem.name, len(corpo)))
    diz("   estilos em uso: %d" % len(estilos))
    for nome, n in estilos.most_common(5):
        diz("      %-32s %4d  (%2.0f%%)" % (nome[:32], n, 100.0 * n / max(len(corpo), 1)))
    if estilos:
        maior = estilos.most_common(1)[0]
        if maior[0] != "(Normal)":
            diz("   o parágrafo típico não usa o estilo Normal, e sim %s" % maior[0])
    diz("   com formatação direta sobre o estilo: %d de %d (%.0f%%)"
          % (direta, len(corpo), 100.0 * direta / max(len(corpo), 1)))

    # ---- os vazios, um a um, com as travas
    tabelas = dentro_de_tabela(doc)
    pars = paragrafos(doc)
    inicio = fim_do_pretextual(doc, pars)
    apagar, retidos = [], Counter()
    for i, (ini, fim) in enumerate(pars):
        b = doc[ini:fim]
        if not vazio(b):
            continue
        if i < inicio:
            retidos["pré-textual (capa, folha de rosto, sumário)"] += 1
            continue
        if i == len(pars) - 1:
            retidos["último parágrafo do corpo"] += 1
            continue
        if any(x <= ini < y for x, y in tabelas):
            retidos["dentro de tabela"] += 1
            continue
        nome = travado(b)
        if nome:
            retidos[nome] += 1
            continue
        apagar.append(i)

    vazios = sum(1 for ini, fim in pars if vazio(doc[ini:fim]))
    diz("   o corpo começa no parágrafo %d; antes disso nada é tocado" % (inicio + 1))
    diz("   parágrafos vazios: %d, dos quais %d podem sair" % (vazios, len(apagar)))
    if a.so_relatorio:
        pass
    for nome, n in retidos.most_common():
        diz("      retidos por %s: %d" % (nome, n))

    if a.so_relatorio:
        return

    # ---- reescreve de tras para frente, para os deslocamentos nao invalidarem
    #      as posicoes ainda nao usadas
    fora = set(apagar)
    extra, convertidos, cortados = {}, 0, 0
    for i in apagar:
        anterior = next((j for j in range(i - 1, -1, -1) if j not in fora), None)
        if anterior is None:
            continue
        ini, fim = pars[anterior]
        if vazio(doc[ini:fim]):
            continue
        # Somado, e nao atribuido: tres vazios seguidos depois do mesmo
        # paragrafo valem os tres, e atribuir faria o ultimo apagar os outros.
        extra[anterior] = extra.get(anterior, 0) + altura(doc[pars[i][0]:pars[i][1]])

    # O paragrafo que recebe o espaco e cujo seguinte vai ser apagado no mesmo
    # lote nao leva `pPrChange`. Medido em 30/08/2026: com a marca de exclusao
    # logo abaixo de um `pPrChange`, o Word funde os dois paragrafos ao aceitar,
    # e o que se perde e um paragrafo de texto do autor. O anexo de normalizacao
    # continua registrando a mudanca de espacamento.
    vizinho_apagado = set()
    for i in apagar:
        j = next((k for k in range(i - 1, -1, -1) if k not in fora), None)
        if j is not None:
            vizinho_apagado.add(j)

    ordens = ([(pars[i][0], pars[i][1], None) for i in apagar]
              + [(pars[j][0], pars[j][1], v) for j, v in extra.items()])
    novo = doc
    calados = 0
    for ini, fim, twips in sorted(ordens, key=lambda x: -x[0]):
        antigo = doc[ini:fim]
        if twips is None:
            # Com revisao o paragrafo fica no arquivo, marcado como excluido, e
            # so some quando alguem aceita a alteracao. E por isso que a revisao
            # nao e o padrao: enquanto nao se aceita, a numeracao de paragrafo
            # continua a antiga, e o relatorio ja cita a nova.
            trecho = apagar_com_revisao(antigo) if not a.silencio else b""
        else:
            trecho = por_espaco_depois(antigo, min(twips, TETO))
            indice = next((j for j, (x, y) in enumerate(pars) if x == ini), None)
            if not a.silencio and indice not in vizinho_apagado:
                trecho = com_ppr_change(antigo, trecho)
            elif not a.silencio:
                calados += 1
            convertidos += 1
            if twips > TETO:
                cortados += 1
        novo = novo[:ini] + trecho + novo[fim:]

    pars_dep = paragrafos(novo)
    corta = pars_dep[fim_do_pretextual(novo, pars_dep)][0] if pars_dep else 0
    novo, juntados = junta_espacos(novo, corta)

    # ---- legendas
    virados = 0
    if a.legendas:
        est_leg = next((m.group(1) for m in re.finditer(
            rb'<w:style [^>]*w:styleId="([^"]*)"', z.read("word/styles.xml"))
            if b"Legenda" in m.group(1) or b"Caption" in m.group(1)), None)
        if est_leg:
            saida, pos = [], 0
            for ini, fim in paragrafos(novo):
                b, trocou = virar_legenda(novo[ini:fim], est_leg)
                if trocou:
                    virados += 1
                saida.append(novo[pos:ini]); saida.append(b); pos = fim
            saida.append(novo[pos:])
            novo = b"".join(saida)
        else:
            diz("   sem estilo de legenda no arquivo: nada a converter")

    # ---- um estilo por papel, e os papeis sao tres
    estilos_xml, criados, adiados, resto = None, [], [], (0, 0, 0)
    if a.estilos:
        estilos_xml = z.read("word/styles.xml")
        pars2 = paragrafos(novo)
        tabelas2 = dentro_de_tabela(novo)
        inicio2 = fim_do_pretextual(novo, pars2)
        achados, outros = papeis(novo, pars2, tabelas2, inicio2,
                                 faixa_referencias(novo, pars2))
        # Normal, e nao o estilo mais frequente do arquivo: se o mais frequente
        # for um estilo de titulo, o corpo inteiro passa a herdar negrito, corpo
        # de letra e nivel de topico.
        base = b"Normal"
        onde = {}
        for nome, ident in PAPEIS:
            idx = achados[nome]
            if not idx:
                continue
            dom, fatia, quantas, decide = escolher_forma(novo, pars2, idx)
            if not (decide or a.forcar):
                adiados.append((nome, len(idx), quantas, fatia))
                continue
            estilos_xml, ok = escrever_estilo(
                estilos_xml, base, dom, ident,
                (nome + " (normalizado)").encode("utf-8"))
            criados.append([nome, len(idx), quantas, fatia, ok, 0])
            for i in idx:
                onde[i] = (dom, ident, nome)

        formas_outros = Counter(forma(novo[pars2[i][0]:pars2[i][1]]) for i in outros)
        isoladas = [f for f, n in formas_outros.items() if n <= 2]
        resto = (len(outros), len(isoladas),
                 sum(1 for f in isoladas if empurrao(f)))

        porpapel = {c[0]: c for c in criados}
        saida, pos = [], 0
        for i, (ini, fim) in enumerate(pars2):
            if i not in onde:
                continue
            dom, ident, nome = onde[i]
            b, mudou = alinhar(novo[ini:fim], dom, ident)
            if mudou:
                porpapel[nome][5] += 1
            saida.append(novo[pos:ini]); saida.append(b); pos = fim
        saida.append(novo[pos:])
        novo = b"".join(saida)

    # ---- separadores de nota de rodape
    notas_xml, notas_ind, notas_par = None, 0, 0
    if a.notas and "word/footnotes.xml" in z.namelist():
        notas_xml, notas_ind, notas_par = limpar_separadores(z.read("word/footnotes.xml"))

    destino = Path(a.saida or origem.with_name(origem.stem + "-normalizado.docx"))
    shutil.copy(origem, destino)
    with zipfile.ZipFile(origem) as ze:
        itens = [n for n in ze.namelist()]
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zs:
            for n in itens:
                if n == "word/document.xml":
                    zs.writestr(n, novo)
                elif n == "word/styles.xml" and estilos_xml is not None:
                    zs.writestr(n, estilos_xml)
                elif n == "word/footnotes.xml" and notas_xml is not None:
                    zs.writestr(n, notas_xml)
                else:
                    zs.writestr(n, ze.read(n))

    conf = len(paragrafos(novo))
    diz("\n%s: %d vazios apagados, %d viraram espaço depois, %d espaços repetidos juntados"
          % (destino.name, len(apagar), convertidos, juntados))
    if cortados:
        diz("   em %d parágrafos a altura convertida bateu no teto de %d twips e "
              "foi cortada: ali o espaço devolvido é menor que o apagado"
              % (cortados, TETO))
    diz("   parágrafos: %d antes, %d depois" % (len(pars), conf))
    if not a.silencio and calados:
        diz("   %d mudanças de espaçamento não foram marcadas como alteração, "
            "porque o parágrafo seguinte é apagado e o Word funde os dois ao aceitar"
            % calados)
    if a.estilos:
        for nome, n, quantas, fatia, ok, alin in criados:
            diz("   %-12s %4d parágrafos, em %2d formas; %d alinhados à mais "
                  "frequente (%.0f%%)%s"
                  % (nome, n, quantas, alin, 100 * fatia,
                     "" if ok else "  (não consegui criar o estilo)"))
        for nome, n, quantas, fatia in adiados:
            diz("   %-12s %4d parágrafos, em %2d formas, e a maior reúne %.0f%%: "
                  "não alinhei" % (nome, n, quantas, 100 * fatia))
            diz("      não há forma assentada a que alinhar, e escolher uma é de "
                  "quem escreveu. Com --forcar, vale a mais frequente.")
        diz("   %d parágrafos ficaram fora dos três papéis (recuo próprio ou linha "
              "curta), em %d formas isoladas, das quais %d parecem espaço posto à "
              "mão para empurrar página" % resto)
    if a.notas:
        diz("   separadores de nota: %d recuos retirados, %d parágrafos sobrando apagados"
              % (notas_ind, notas_par))
    if a.legendas:
        diz("   parágrafos convertidos em legenda: %d" % virados)
    anexo = destino.with_name("ANEXO-NORMALIZACAO-" + destino.stem + ".md")
    diz.gravar(anexo, origem.name)
    diz("   o que mudou está em %s, para ir anexo ao relatório." % anexo.name)
    if a.silencio:
        diz("   a numeração mudou, então extraia de novo a partir deste arquivo.")
    else:
        diz("   as mudanças estão como alterações controladas, para aceitar ou recusar.")
        diz("   a numeração de parágrafo só fecha depois de aceitas, então este arquivo")
        diz("   não serve de entrada para a análise: para isso, use --silencio.")


if __name__ == "__main__":
    main()

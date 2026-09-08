# -*- coding: utf-8 -*-
"""Tira as figuras do .docx e diz, de cada uma, onde ela esta e o que a legenda diz.

POR QUE ISTO EXISTE

Medido em 06/09/2026. A leitura das figuras era feita pagina a pagina no PDF, uma
chamada por pagina, e a imagem vinha reduzida junto com o resto da folha. Tres
coisas mudam quando as figuras saem do `.docx`:

    resolucao   a imagem vem como o autor a inseriu, com os rotulos de dado
                legiveis um a um. Rotulo truncado ali e defeito do trabalho;
                rotulo ilegivel numa pagina de PDF pode ser so a reducao.
    custo       a restricao de chamada paralela e da leitura de PAGINA DE PDF,
                nao da de arquivo de imagem. Seis imagens pedidas na mesma
                mensagem voltaram as seis, medido no mesmo dia. As figuras de um
                trabalho passam a caber em uma ou duas chamadas.
    endereco    aqui, porque `word/media/` guarda as imagens na ordem de
                insercao e sem legenda nenhuma. Este programa casa cada arquivo
                com o paragrafo em que ele aparece e com a legenda vizinha.

DE ONDE SAI O ENDERECO

Medido em 07/09/2026 sobre `t-agosto.docx`: as 117 imagens sairam
todas enderecadas em [P161]-[P228], que e o indice de graficos das primeiras
paginas. A causa e que o indice repete a legenda do corpo palavra por palavra, e
o casador buscava o texto da legenda na extracao inteira, ficando com a PRIMEIRA
ocorrencia. Os tres graficos do capitulo 6 estao em [P751], [P763] e [P775]; o
programa dizia [P182], [P183] e [P184].

A contagem de paragrafos aqui repete a regra do extrator, de modo que o n-esimo
paragrafo do corpo e o [Pn] da extracao, e a extracao passou a servir de
CONFERENCIA do alinhamento em vez de fonte do endereco.

Dito com precisao, porque a primeira redacao deste cabecalho dizia que o
endereco sai da posicao e nao do texto: quem localiza a LEGENDA continua sendo
casamento de texto (`RE_LEGENDA`), so que dentro de uma janela de mais ou menos
`--vizinhanca` paragrafos em torno da imagem, e nao no documento inteiro. O que
saiu da busca por texto foi o endereco, que agora e a posicao do paragrafo
encontrado.

UMA FIGURA PODE ESTAR PARTIDA EM VARIOS ARQUIVOS

Alguns graficos deste trabalho estao partidos em arquivos separados: o corpo do
grafico, o rotulo do eixo e a legenda de cores. So um deles mostra o dado. O
alcance disso e menor do que a primeira redacao dizia: dos 97 grupos de imagem,
oitenta e um tem um arquivo so.

A fragmentacao vem de duas formas, e a primeira versao deste conserto so pegava
uma. Dentro de um paragrafo (o Grafico 22, com tres arquivos em [P752]) e
ATRAVESSANDO paragrafos (o Grafico 26, com o corpo em [P835] e a tarja de cores
em [P836]). Sao dez grupos da segunda forma neste trabalho, e neles o programa
elegia a tarja de cores como portadora do dado, com o motivo "arquivo unico".

O programa junta os paragrafos de imagem pura que estejam colados e diz qual
arquivo carrega o dado, pela area em que a imagem e exibida (`wp:extent`) e pelo
reaproveitamento do arquivo em mais de uma figura.

O QUE ELE NAO FAZ

Nao le a figura, e nao diz se ela mostra o que a prosa afirma. Isso e da leitura,
e e por isso que a saida traz o caminho de cada arquivo: para que a leitura peca
todas as imagens numa mensagem so, ja sabendo qual e qual.

Uso:
    python scripts/figuras_do_docx.py <trabalho.docx> [--extracao extracao.txt]
    python scripts/figuras_do_docx.py <trabalho.docx> --saida pasta_das_figuras
    python scripts/figuras_do_docx.py --autoteste
"""
import argparse
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
V = "{urn:schemas-microsoft-com:vml}"

# Os mesmos nos em que o extrator desce sem contar paragrafo
# (scripts/analisar_docx.py, collect_paragraphs).
DESCE = {W + "tbl", W + "sdt", W + "sdtContent", W + "tr", W + "tc",
         W + "customXml", W + "smartTag"}

# Quantas vezes a maior imagem do grupo precisa ser maior que a segunda para que
# se afirme que e ela que carrega o dado. Medido: nos nove grupos com mais de uma
# imagem de `t-agosto.docx`, a razao entre a maior area exibida e a
# segunda vai de 8,4 a 36,4. Por bytes a separacao e bem pior (a menor razao e
# 2,1, e naquele caso o arquivo pequeno era mesmo so a legenda de cores), e por
# isso a area manda e o tamanho em disco entra so como recurso.
#
# CONFERIDO FORA DO TRABALHO EM QUE FOI CALIBRADO, em 08/09/2026, sobre a
# dissertacao de outro autor achada em `Downloads` (44 imagens, 34 grupos, onze
# deles com mais de um arquivo): os onze eleitos abertos um a um sao corpo de
# grafico com dado, e os descartes sao legenda de cores.
#
# E o caso e mais duro que o da calibragem, porque ali a area e os bytes
# concordavam. Neste, em OITO dos onze grupos o arquivo descartado e MAIOR em
# bytes que o eleito, porque a legenda daquele trabalho e um bloco de sete a nove
# linhas de texto: `image19.png` tem 111 KB de legenda contra 45 KB do grafico. O
# desempate por tamanho em disco teria errado os oito, e num deles por sorte
# (47.923 contra 49.037 bytes, razao de 1,02, onde a area da 5,1 para 1).
RAZAO = 3.0

# Abaixo desta proporcao de paragrafos casados, a extracao nao corresponde a
# este .docx e nenhum endereco sai.
ALINHAMENTO_MINIMO = 0.90

# A legenda de figura, tabela ou grafico, nas formas que o acervo traz. O numero
# pode vir depois de traco, ponto ou espaco, e o tipo pode vir em caixa alta.
# O identificador nem sempre e numero. Numa tese do acervo as figuras sao
# "Figure A", "Figure B" e tres delas "Figure X", o que e defeito do trabalho e
# nao do programa: exigir digito deixava treze figuras sem legenda reconhecida.
#
# O `(?i:...)` cobre SO a palavra do tipo, e nao a expressao inteira. Com `re.I`
# global, o `[A-Z]` do identificador casava minuscula e "Figura a - y" era lido
# como legenda. Medido em 07/09/2026 sobre as oito obras distintas do acervo:
# a troca nao muda nada (os mesmos 360 paragrafos casam, e as mesmas figuras
# ficam com legenda), porque as 360 legendas escrevem o tipo com inicial
# maiuscula (Grafico 308, Tabela 17, Quadro 14, Figure 13, Figura 8). Tirar o
# `re.I` inteiro, que foi o que se cogitou, tambem nao mudaria nada ali e
# custaria "TABELA 4" e "GRAFICO 12", que sao grafia corrente.
_TIPO = r"(?i:(Gr[áa]fico|Figura|Tabela|Quadro|Imagem|Chart|Table|Figure))"
# A segunda alternativa aceita numero sem separador, e e ela, e nao o `re.I`, que
# faz "Tabela 1 apresenta os dados" passar por legenda. Fica como esta porque e
# necessaria: dispara 4 vezes em 360, todas na `dissertacao-nova`, onde a legenda
# ao lado da imagem e o texto "Grafico 1" sozinho. Aperta-la para exigir que nada
# sobre depois do numero rejeitaria tambem "Chart 3 Something".
RE_LEGENDA = re.compile(
    r"^\s*" + _TIPO + r"\s*(\d{1,3}|[A-Z]|[IVXL]{1,5})\s*[-–—.:]\s*(.*)$"
    r"|^\s*" + _TIPO + r"\s*(\d{1,3})\s*(.*)$")

# O marcador de paragrafo da extracao so vale no comeco da linha, depois do que
# o extrator poe antes dele (**, #, >). No meio da linha, "[P757]" e referencia
# cruzada escrita pelo leitor, e nao endereco.
RE_MARCADOR = re.compile(r"^[>\s]*[#*`]*\s*\[P(\d+)\][^\n]*", re.M)


# --------------------------------------------------------------- leitura do docx

def paragrafos_do_docx(fonte, desce=None):
    """Devolve, na ordem, (texto, imagens) de cada paragrafo do corpo.

    A posicao na lista e o endereco: o item de indice k e o [P(k+1)] da
    extracao. Para que isso valha, a contagem repete a regra do extrator
    (`collect_paragraphs` em analisar_docx.py): anda a arvore, conta `<w:p>` e
    desce em tabela, sdt, linha, celula e smartTag. Descer errado desloca todo
    endereco, e em silencio: tirar so a tabela do conjunto muda a contagem de
    1.434 para 1.319 neste trabalho e de 1.347 para 801 na `x-v3.docx`.
    O parametro `desce` existe para o autoteste poder provar isso.

    Expressao regular nao serve aqui, e sao DOIS defeitos que se compensam em
    parte, o que faz o erro caber num total de aparencia plausivel:

        `<w:p ...>.*?</w:p>` trata o paragrafo vazio auto-fechado
        `<w:p w14:paraId="..."/>` como abertura, porque o `[ >]` casa o espaco
        antes dos atributos, e engole o paragrafo seguinte inteiro. Sao seis
        desses em `t-agosto.docx`, e custam seis.

        A alternativa `<w:p[^>]*/>` casa `<w:pgSz .../>` e `<w:pgMar .../>`,
        que ficam no `sectPr` final e nao sao paragrafo. Sao dois, e entram.

    A conta e 1.434 - 6 + 2 = 1.430, que era o que a versao anterior devolvia.

    Cada imagem vem como (arquivo, cx, cy), com cx e cy em EMU, que e a area em
    que o Word a exibe. Vale zero quando o desenho nao traz `wp:extent` (VML
    antigo), e nesse caso o desempate cai no tamanho em disco.
    """
    if desce is None:
        desce = DESCE
    fechar = False
    if isinstance(fonte, zipfile.ZipFile):
        z = fonte
    else:
        z = zipfile.ZipFile(fonte)
        fechar = True
    try:
        try:
            xml = z.read("word/document.xml")
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8",
                                                                 "replace")
        except KeyError as erro:
            raise SystemExit("  este .zip nao tem a peca que o .docx deveria "
                             "ter, e nao leio nada dele: %s" % erro)
    finally:
        if fechar:
            z.close()

    alvo = {}
    for m in re.finditer(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels):
        alvo[m.group(1)] = m.group(2).split("/")[-1]

    corpo = ET.fromstring(xml).find(W + "body")
    fora = []
    if corpo is None:
        return fora

    def anda(no):
        for filho in no:
            if filho.tag == W + "p":
                texto = "".join(t.text or "" for t in filho.iter(W + "t"))
                fora.append((texto.strip(), imagens_do_paragrafo(filho, alvo)))
            elif filho.tag in desce:
                anda(filho)

    anda(corpo)
    return fora


def imagens_do_paragrafo(p, alvo):
    """(arquivo, cx, cy) de cada imagem do paragrafo, sem repetir arquivo.

    O mesmo arquivo pode aparecer duas vezes no mesmo paragrafo quando o Word
    grava `mc:AlternateContent` com o desenho moderno numa ramificacao e o VML
    antigo na outra. Sao a mesma figura, e fica a ocorrencia de maior area.
    """
    achados = []
    vistos = set()
    for el in p.iter():
        if el.tag in (WP + "inline", WP + "anchor"):
            ext = el.find(WP + "extent")
            cx = int(ext.get("cx") or 0) if ext is not None else 0
            cy = int(ext.get("cy") or 0) if ext is not None else 0
            for b in el.iter(A + "blip"):
                vistos.add(id(b))
                rid = b.get(R + "embed") or b.get(R + "link")
                if rid and alvo.get(rid):
                    achados.append((alvo[rid], cx, cy))
    for b in p.iter(A + "blip"):
        if id(b) in vistos:
            continue
        rid = b.get(R + "embed") or b.get(R + "link")
        if rid and alvo.get(rid):
            achados.append((alvo[rid], 0, 0))
    for v in p.iter(V + "imagedata"):
        rid = v.get(R + "id")
        if rid and alvo.get(rid):
            achados.append((alvo[rid], 0, 0))

    ordem, melhor = [], {}
    for nome, cx, cy in achados:
        if nome not in melhor:
            ordem.append(nome)
            melhor[nome] = (nome, cx, cy)
        elif cx * cy > melhor[nome][1] * melhor[nome][2]:
            melhor[nome] = (nome, cx, cy)
    return [melhor[nome] for nome in ordem]


# --------------------------------------------------------- conferencia do endereco

def normalizar(s):
    """Deixa so letra e digito, para comparar texto do docx com texto da extracao.

    A extracao mexe no texto de tres jeitos: normaliza espaco (o sumario do Word
    vem com tabulacao), marca pseudo-titulo com ** e um comentario de HTML, e
    poe [nota N] onde havia chamada de nota de rodape. Comparar caractere a
    caractere reprovaria por essas tres e nao por desalinhamento, que e o que se
    quer medir.
    """
    s = re.sub(r"<!--.*?-->", " ", s)
    s = re.sub(r"\[nota\s*\d+\]", " ", s)
    return re.sub(r"[^0-9A-Za-zÀ-ÿ]+", "", s).lower()


def conferir_alinhamento(ps, extracao, largura=40):
    """Confere que o k-esimo paragrafo do docx e o [Pk] da extracao.

    Devolve (casados, divergentes, exemplos, maior_marcador). Sem isto o
    endereco por posicao seria fe: bastaria a extracao ser de outra versao do
    trabalho para todo [P###] sair errado sem sinal nenhum.

    `maior_marcador` existe porque taxa alta nao e cobertura. O proprio
    `analisar_docx.py` sugere, ao fim do relatorio, extrair uma FAIXA
    (`--de 1 --ate 300`), e a extracao dos 300 primeiros paragrafos de
    `t-agosto.docx` casa 208 de 208, imprime 100% e nao confere
    nenhum dos 1.134 paragrafos restantes, que e onde estao todas as figuras.
    """
    casados, divergentes, exemplos = 0, 0, []
    maior = 0
    for m in RE_MARCADOR.finditer(extracao):
        idx = int(m.group(1))
        maior = max(maior, idx)
        if not 1 <= idx <= len(ps):
            divergentes += 1
            if len(exemplos) < 5:
                exemplos.append((idx, "(fora da faixa de parágrafos)", ""))
            continue
        doc = normalizar(ps[idx - 1][0])[:largura]
        ext = normalizar(m.group(0).split("]", 1)[1])[:largura]
        if not doc and not ext:
            continue
        if doc == ext:
            casados += 1
        else:
            divergentes += 1
            if len(exemplos) < 5:
                exemplos.append((idx, doc, ext))
    return casados, divergentes, exemplos, maior


# ------------------------------------------------------------- montagem da figura

def area(img):
    return img[1] * img[2]


def repartir(imgs, uso, tamanhos):
    """Diz qual arquivo do grupo carrega o dado, e por que.

    Dois sinais, e o primeiro nao depende de tamanho: arquivo que aparece em
    mais de uma figura e peca compartilhada (o rotulo do eixo que se repete de
    grafico em grafico), nunca o dado. Sobrando mais de um, decide a area em que
    o Word exibe a imagem, e so quando a maior for RAZAO vezes a segunda. Duas
    figuras lado a lado no mesmo paragrafo tem area parecida e caem na recusa,
    que e o que se quer: melhor dizer que nao sabe.
    """
    if len(imgs) == 1:
        return imgs[0], [], "arquivo único"
    proprios = [i for i in imgs if uso[i[0]] == 1]
    pool = proprios or list(imgs)
    if len(pool) == 1:
        return pool[0], [i for i in imgs if i is not pool[0]], \
            "porque os outros se repetem em outras figuras"
    if all(area(i) for i in pool):
        chave, nome = area, "pela área exibida"
    else:
        chave, nome = (lambda i: tamanhos.get(i[0], 0)), "pelo tamanho em disco"
    ordem = sorted(pool, key=chave, reverse=True)
    if chave(ordem[1]) <= 0 or chave(ordem[0]) < RAZAO * chave(ordem[1]):
        return None, list(imgs), "tamanhos próximos"
    principal = ordem[0]
    return principal, [i for i in imgs if i is not principal], nome


def grupos_de_imagem(ps):
    """Junta em uma figura os paragrafos SEGUIDOS que so tem imagem.

    Medido em 07/09/2026, e e o defeito que a primeira versao deste conserto
    deixou de pe: a fragmentacao nem sempre cabe num paragrafo. No Grafico 26 de
    `t-agosto.docx` o corpo esta em [P835] e a tarja de cores em
    [P836], cada um no seu paragrafo, e o programa dava duas figuras, as duas com
    motivo "arquivo unico", pondo a tarja de cores na lista dos arquivos que
    carregam dado. Mesma coisa no Grafico 27 ([P841] e [P842]).

    A condicao e estreita de proposito: so juntam paragrafos VIZINHOS e SEM
    TEXTO. Um paragrafo vazio no meio separa, e e por isso que as capturas de
    tela do apendice ([P679], [P681], [P686]), que tem um paragrafo vazio entre
    si, continuam figuras distintas. Prosa junto da imagem tambem separa.
    """
    grupos = []
    for k, (texto, imgs) in enumerate(ps):
        if not imgs:
            continue
        # junta ao grupo anterior so se este paragrafo e o anterior forem os
        # dois de imagem pura e estiverem colados.
        if grupos and not texto and grupos[-1][-1] == k - 1 and not ps[k - 1][0]:
            grupos[-1].append(k)
        else:
            grupos.append([k])
    return grupos


def montar_figuras(ps, vizinhanca, tamanhos):
    """Agrupa as imagens e acha a legenda de cada grupo.

    O endereco da figura e o do paragrafo da LEGENDA quando ha uma, porque e por
    ele que a leitura acha a figura no texto extraido; o paragrafo da imagem vai
    junto, e costuma ser o seguinte.

    A legenda e a MAIS PROXIMA, medida em paragrafos, com empate resolvido a
    favor da que vem antes (que e onde a norma poe o titulo de grafico). A ordem
    anterior era `0, +1, +2, +3, -1, -2, -3`, que fazia o paragrafo tres a frente
    ganhar do que estava logo atras: em `x-v3.docx` a imagem de [P528],
    cuja legenda esta em [P527] logo acima, saia como "Grafico 9 ... Plenario
    Presencial" de [P530], que e o grafico seguinte, e os dois graficos saiam com
    o mesmo endereco.
    """
    grupos = grupos_de_imagem(ps)
    uso = Counter(nome for g in grupos for k in g for nome, _, _ in ps[k][1])
    figuras = []
    for g in grupos:
        inicio, fim = g[0], g[-1]
        imgs = [i for k in g for i in ps[k][1]]
        legenda, leg_idx = "", None
        candidatos = [inicio]
        for d in range(1, vizinhanca + 1):
            candidatos += [inicio - d, fim + d]
        for j in candidatos:
            if 0 <= j < len(ps) and RE_LEGENDA.match(ps[j][0]):
                legenda = re.sub(r"\s+", " ", ps[j][0])
                leg_idx = j + 1
                break
        principal, acessorios, motivo = repartir(imgs, uso, tamanhos)
        figuras.append({
            "onde": leg_idx or (inicio + 1),
            "p_imagem": inicio + 1,
            "p_ultimo": fim + 1,
            "p_legenda": leg_idx,
            "legenda": legenda,
            "principal": principal,
            "acessorios": acessorios,
            "motivo": motivo,
            "imgs": imgs,
            "uso": uso,
        })
    return figuras


def kb(n):
    return "%.0f KB" % (n / 1024.0) if n else "?"


# ------------------------------------------------------------------- os controles

_NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
       'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
       'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
       'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


def _tabela(*linhas):
    """Uma <w:tbl> de teste, uma celula por texto de cada linha."""
    fora = ""
    for celulas in linhas:
        fora += "<w:tr>%s</w:tr>" % "".join(
            "<w:tc>%s</w:tc>" % _par(c) for c in celulas)
    return "<w:tbl>%s</w:tbl>" % fora


def _sdt(*paragrafos):
    """Um <w:sdt> de teste, que o extrator atravessa sem contar."""
    return "<w:sdt><w:sdtContent>%s</w:sdtContent></w:sdt>" % "".join(paragrafos)


def _par(texto="", imgs=()):
    """Um <w:p> de teste. imgs = [(rId, cx, cy)]."""
    corpo = ""
    if texto:
        corpo += '<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % texto
    for rid, cx, cy in imgs:
        corpo += ('<w:r><w:drawing><wp:inline><wp:extent cx="%d" cy="%d"/>'
                  '<a:graphic><a:graphicData><pic:pic><pic:blipFill>'
                  '<a:blip r:embed="%s"/></pic:blipFill></pic:pic>'
                  '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
                  % (cx, cy, rid))
    return "<w:p>%s</w:p>" % corpo


def _zip_de_teste(paragrafos, media=()):
    """Monta na memoria o minimo que este programa le de um .docx."""
    doc = ('<?xml version="1.0" encoding="UTF-8"?><w:document %s><w:body>%s'
           '</w:body></w:document>' % (_NS, "".join(paragrafos)))
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships>%s'
            '</Relationships>' % "".join(
                '<Relationship Id="%s" Type="image" Target="media/%s"/>'
                % (rid, nome) for rid, nome, _ in media))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", doc.encode("utf-8"))
        z.writestr("word/_rels/document.xml.rels", rels.encode("utf-8"))
        for _, nome, tam in media:
            z.writestr("word/media/" + nome, b"\0" * tam)
    buf.seek(0)
    return buf


def _endereco_por_texto_antigo(texto, extracao):
    """O casador que este conserto substituiu, guardado so para o controle.

    Ele existe aqui para provar que o caso de teste reproduz mesmo o defeito
    medido em 07/09/2026. Se um dia ele parar de errar naquele caso, o caso
    deixou de exercer o defeito, e o teste que passa nao prova nada.
    """
    if not texto or not extracao:
        return None
    chave = re.sub(r"<!--.*?-->", " ", texto).replace("**", " ")
    chave = re.sub(r"^\W+|\W+$", "", re.sub(r"\s+", " ", chave))[:60]
    inteiro = len(chave) < 12

    def limpar(s):
        s = re.sub(r"<!--.*?-->", " ", s).replace("**", " ").replace("`", " ")
        return re.sub(r"^\W+|\W+$", "", re.sub(r"\s+", " ", s))

    for m in re.finditer(r"\[P(\d+)\]([^\n]*)", extracao):
        alvo = limpar(re.sub(r"\s+", " ", m.group(2)))
        if (alvo == chave) if inteiro else (chave in alvo):
            return int(m.group(1))
    return None


def _contagem_por_regex_antiga(xml):
    """A contagem que este conserto substituiu, guardada so para o controle."""
    return len(re.findall(r"<w:p[ >].*?</w:p>|<w:p[^>]*/>", xml, re.S))


def autoteste():
    """Prova cada regra com um caso que ela tem de reprovar.

    Devolve (falhas, provas). Sem o caso que reprova, o silencio do teste nao
    informa nada: um casador que devolvesse sempre o mesmo numero passaria por
    qualquer teste que so exija "nao explodir".
    """
    falhas, provas = [], []

    # 1. o leitor de legenda. "TABELA 4" e "GRÁFICO 12" estao aqui porque sao o
    #    que se perde ao tirar o `re.I` inteiro, e "Figura a - y" porque e o que
    #    se ganha ao restringi-lo a palavra do tipo.
    for bom in ("Gráfico 22 – Decisões por ano", "TABELA 4 - Distribuição",
                "GRÁFICO 12 – Algo", "Figura 2: série histórica",
                "Figure A. Judgement Sessions Portal", "Chart 3 Something",
                "Gráfico 1"):
        if not RE_LEGENDA.match(bom):
            falhas.append("nao reconhece legenda: %r" % bom)
    for mau in ("O gráfico acima mostra que", "Tabelas de contingência sobre",
                "A figura de duração é apresentada", "Figura a - y"):
        if RE_LEGENDA.match(mau):
            falhas.append("confunde prosa com legenda: %r" % mau)
    # Estes dois continuam passando por legenda, e ficam escritos para que
    # ninguem os descubra de novo como se fossem novidade: sao a segunda
    # alternativa, que aceita numero sem separador, e nao a caixa das letras.
    for conhecido in ("Tabela 1 apresenta os dados", "tabela 3 de resultados"):
        if not RE_LEGENDA.match(conhecido):
            falhas.append("o falso positivo conhecido %r sumiu, e o comentario "
                          "acima da expressao ficou desatualizado" % conhecido)
    velha = re.compile(RE_LEGENDA.pattern.replace("(?i:", "(?:"), re.I)
    if not velha.match("Figura a - y"):
        falhas.append("CONTROLE MORTO: a expressao com re.I global tambem recusa "
                      "'Figura a - y', e o caso nao exerce o defeito")
    elif not falhas:
        provas.append("reconhece sete escritas de legenda, incluídas TABELA e "
                      "GRÁFICO em caixa alta, e recusa quatro prosas, entre elas "
                      "'Figura a - y', que o `re.I` global aceitava")

    # 2. contagem de paragrafo, com o paragrafo vazio auto-fechado que fazia a
    #    expressao regular antiga engolir o seguinte.
    pars = [_par("um"), '<w:p w:rsidR="00AB12CD"/>', _par("tres"), _par("quatro")]
    fonte = _zip_de_teste(pars)
    ps = paragrafos_do_docx(zipfile.ZipFile(fonte))
    if len(ps) != 4:
        falhas.append("contagem de paragrafo: %d em vez de 4" % len(ps))
    elif ps[2][0] != "tres":
        falhas.append("contagem: [P3] deu %r em vez de 'tres'" % ps[2][0])
    fonte.seek(0)
    xml = zipfile.ZipFile(fonte).read("word/document.xml").decode("utf-8")
    antiga = _contagem_por_regex_antiga(xml)
    if antiga == 4:
        falhas.append("CONTROLE MORTO: a regex antiga acerta a contagem neste "
                      "caso, que portanto nao exerce o defeito")
    else:
        provas.append("conta 4 parágrafos onde a expressão regular antiga conta "
                      "%d, por tratar `<w:p .../>` vazio como abertura" % antiga)

    # 2b. a REGRA DE DESCIDA, que e a tese inteira do conserto e que nenhum
    #     controle tocava: os `<w:p>` de dentro de tabela e de sdt contam, e
    #     contam na posicao em que estao. Descer errado desloca todo endereco em
    #     silencio (tirar so a tabela leva 1.434 a 1.319 no trabalho de prova).
    pars = [_par("antes"),
            _tabela(["celula um", "celula dois"], ["celula tres"]),
            _sdt(_par("dentro do sdt")),
            _par("depois")]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(pars)))
    esperado = ["antes", "celula um", "celula dois", "celula tres",
                "dentro do sdt", "depois"]
    if [t for t, _ in ps] != esperado:
        falhas.append("regra de descida: %r em vez de %r"
                      % ([t for t, _ in ps], esperado))
    else:
        magro = DESCE - {W + "tbl"}
        ps_magro = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(pars)),
                                      desce=magro)
        if len(ps_magro) == len(ps):
            falhas.append("CONTROLE MORTO: sem w:tbl no conjunto de descida a "
                          "contagem nao muda, e o caso nao exerce a regra")
        else:
            provas.append("conta os parágrafos de dentro de tabela e de sdt na "
                          "posição em que estão (6 aqui; sem descer em w:tbl "
                          "seriam %d)" % len(ps_magro))

    # 3. o endereco vem da posicao, e nao do texto: o indice de graficos das
    #    primeiras paginas repete a legenda do corpo palavra por palavra.
    legenda = "Gráfico 22 - Decisões por ano"
    pars = [_par("ÍNDICE DE GRÁFICOS"),
            _par(legenda + " 79"),
            _par("Gráfico 23 - Outra coisa 82"),
            '<w:p w:rsidR="00AB12CD"/>',
            _par("prosa qualquer no meio do trabalho"),
            _par(legenda),
            _par("", [("rId1", 5400040, 3603625)]),
            _par("Fonte: elaborado pela autora")]
    media = [("rId1", "image33.png", 51559)]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(pars, media)))
    ext = "\n".join(["[P1] ÍNDICE DE GRÁFICOS",
                     "[P2] %s 79" % legenda,
                     "[P3] Gráfico 23 - Outra coisa 82",
                     "[P5] prosa qualquer no meio do trabalho",
                     "**[P6] %s**  <!-- pseudo-titulo, sem estilo -->" % legenda,
                     "[P8] Fonte: elaborado pela autora"])
    figs = montar_figuras(ps, 3, {"image33.png": 51559})
    if len(figs) != 1:
        falhas.append("endereco: %d figuras em vez de 1" % len(figs))
    elif figs[0]["onde"] != 6:
        falhas.append("endereco: figura em [P%d]; o corpo esta em [P6] e a "
                      "linha do indice em [P2]" % figs[0]["onde"])
    antigo = _endereco_por_texto_antigo(legenda, ext)
    if antigo != 2:
        falhas.append("CONTROLE MORTO: o casador antigo deu [P%s] neste caso, e "
                      "nao o [P2] do indice; o caso nao exerce o defeito"
                      % antigo)
    else:
        provas.append("endereça a figura em [P6], o corpo, onde o casador por "
                      "texto dava [P2], a linha do índice de gráficos")
    casados, divergentes, _, ate = conferir_alinhamento(ps, ext)
    if casados != 6 or divergentes:
        falhas.append("alinhamento: %d casados e %d divergentes, esperava 6 e 0"
                      % (casados, divergentes))
    if ate != 8:
        falhas.append("alinhamento: o maior marcador deu [P%d] e não [P8]" % ate)

    # 4. o alinhamento tem de acusar extracao que nao e deste .docx, e a
    #    assercao e contra o limiar que o programa usa de verdade, e nao contra
    #    "mais divergentes que casados", que quatro sabotagens da guarda passam.
    #    Todo marcador fica DENTRO da faixa de paragrafos de proposito: com um
    #    marcador fora da faixa, o controle reprovava por ele e passava mesmo com
    #    a comparacao de texto desligada, que e falso conforto.
    ext_torta = "\n".join("[P%d] %s" % (i + 2, ps[i][0])
                          for i in range(len(ps) - 1) if ps[i][0])
    casados, divergentes, _, _ = conferir_alinhamento(ps, ext_torta)
    taxa = casados / float(casados + divergentes or 1)
    if taxa >= ALINHAMENTO_MINIMO:
        falhas.append("CONTROLE MORTO: extracao deslocada em um paragrafo "
                      "passou com taxa de %.0f%%, acima do limiar de %.0f%%"
                      % (100 * taxa, 100 * ALINHAMENTO_MINIMO))
    else:
        provas.append("recusa extração deslocada de um parágrafo, sem marcador "
                      "fora da faixa para carregar o veredito: taxa de %.0f%%"
                      % (100 * taxa))

    # 4c. a normalizacao tem de tolerar o que o extrator acrescenta ao texto (a
    #     chamada de nota vira [nota N]) e nada alem disso.
    ext_nota = "\n".join(["[P1] ÍNDICE DE GRÁFICOS",
                          "[P2] %s 79" % legenda,
                          "[P3] Gráfico 23 - Outra coisa 82",
                          "[P5] prosa qualquer[nota 37] no meio do trabalho",
                          "**[P6] %s**" % legenda,
                          "[P8] Fonte: elaborado[nota 38] pela autora"])
    casados, divergentes, _, _ = conferir_alinhamento(ps, ext_nota)
    if divergentes:
        falhas.append("normalizacao: %d divergentes com [nota N] no texto, "
                      "esperava 0" % divergentes)
    else:
        cru = normalizar("prosa qualquer[nota 37] no meio do trabalho")
        if cru == normalizar("prosa qualquer no meio do trabalho"):
            provas.append("casa o texto apesar do [nota N] que o extrator "
                          "insere, e o controle é a comparação crua")
        else:
            falhas.append("CONTROLE MORTO: normalizar nao esta tirando [nota N] "
                          "e mesmo assim os seis marcadores casaram")

    # 4b. taxa alta nao e cobertura: extracao que para antes da figura casa 100%
    #     e nao confere nada onde interessa. O programa tem de saber ate onde a
    #     extracao vai.
    ext_curta = "\n".join(["[P1] ÍNDICE DE GRÁFICOS", "[P2] %s 79" % legenda])
    casados, divergentes, _, ate = conferir_alinhamento(ps, ext_curta)
    taxa = casados / float(casados + divergentes or 1)
    if taxa < ALINHAMENTO_MINIMO:
        falhas.append("CONTROLE MORTO: a extracao parcial ja reprova por taxa, "
                      "e o caso nao exerce a cobertura")
    elif ate >= 6:
        falhas.append("cobertura: a extracao parcial vai ate [P%d], e devia "
                      "parar em [P2]" % ate)
    else:
        provas.append("sabe que uma extração de taxa 100%% pode parar em [P%d] "
                      "e não cobrir a figura de [P6]" % ate)

    # 4d. o marcador so vale no comeco da linha, e a largura da comparacao tem
    #     de ser larga o bastante para separar textos de comeco igual.
    ps_curto = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(
        [_par("Fonte: elaborado pela autora a partir do STF"),
         _par("Fonte: elaborado pela autora a partir do STJ")])))
    ext_ref = ("[P1] Fonte: elaborado pela autora a partir do STF\n"
               "[P2] Fonte: elaborado pela autora a partir do STJ\n"
               "prosa que cita o [P999] no meio da linha, e não é marcador\n")
    casados, divergentes, _, ate = conferir_alinhamento(ps_curto, ext_ref)
    if casados != 2 or divergentes:
        falhas.append("marcador/largura: %d casados e %d divergentes, esperava "
                      "2 e 0" % (casados, divergentes))
    elif ate != 2:
        falhas.append("CONTROLE MORTO: o marcador do meio da linha entrou, e o "
                      "maior virou [P%d]" % ate)
    else:
        trocado = ("[P1] Fonte: elaborado pela autora a partir do STJ\n"
                   "[P2] Fonte: elaborado pela autora a partir do STF\n")
        c2, d2, _, _ = conferir_alinhamento(ps_curto, trocado)
        if d2 != 2:
            falhas.append("CONTROLE MORTO: com os dois 'Fonte:' trocados a "
                          "comparacao ainda aprovou %d; a largura e curta demais"
                          % c2)
        else:
            provas.append("ignora [P###] no meio da linha e separa dois textos "
                          "que só divergem depois do 30º caractere")

    # 4e. o mesmo arquivo duas vezes no mesmo paragrafo (mc:AlternateContent) e
    #     uma imagem so, e fica a ocorrencia de maior area.
    dobrado = [_par("Figura 9 - uma só", [("rId1", 100, 100),
                                          ("rId1", 3000, 3000)])]
    ps_dobro = paragrafos_do_docx(zipfile.ZipFile(
        _zip_de_teste(dobrado, [("rId1", "unica.png", 5000)])))
    achou = ps_dobro[0][1]
    if len(achou) != 1:
        falhas.append("CONTROLE MORTO: o mesmo arquivo duas vezes no paragrafo "
                      "virou %d imagens" % len(achou))
    elif achou[0][1] != 3000:
        falhas.append("deduplicacao: ficou a ocorrencia de area %d, e devia "
                      "ficar a de 3000" % achou[0][1])
    else:
        provas.append("conta uma vez só o arquivo que aparece duas vezes no "
                      "mesmo parágrafo, ficando com a ocorrência maior")

    # 5. agrupamento: tres arquivos no mesmo paragrafo sao uma figura so, e o
    #    dado esta no maior.
    pars = [_par("Gráfico 22 - Decisões por ano"),
            _par("", [("rId1", 885825, 187146),
                      ("rId2", 1638300, 534955),
                      ("rId3", 5400040, 3603625)])]
    media = [("rId1", "eixo.png", 2505), ("rId2", "cores.png", 3877),
             ("rId3", "corpo.png", 51559)]
    tam = {"eixo.png": 2505, "cores.png": 3877, "corpo.png": 51559}
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(pars, media)))
    figs = montar_figuras(ps, 3, tam)
    if len(figs) != 1:
        falhas.append("agrupamento: %d figuras em vez de 1" % len(figs))
    elif not figs[0]["principal"] or figs[0]["principal"][0] != "corpo.png":
        falhas.append("agrupamento: o dado saiu em %r em vez de corpo.png"
                      % (figs[0]["principal"] and figs[0]["principal"][0],))
    elif len(figs[0]["acessorios"]) != 2:
        falhas.append("agrupamento: %d acessorios em vez de 2"
                      % len(figs[0]["acessorios"]))
    else:
        provas.append("junta as três imagens de um mesmo parágrafo numa figura "
                      "e aponta o arquivo que carrega o dado")

    # 5b. a fragmentacao que atravessa paragrafo: o caso do Grafico 26, em que o
    #     corpo esta num paragrafo e a tarja de cores no seguinte. Sao uma figura.
    partido = [_par("Gráfico 26 - Inclusões em pauta por ano"),
               _par("", [("rId3", 5400040, 3603625)]),
               _par("", [("rId2", 1638300, 534955)]),
               _par("Fonte: elaborado pela autora")]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(partido, media)))
    figs = montar_figuras(ps, 3, tam)
    if len(figs) != 1:
        falhas.append("fragmentacao entre paragrafos: %d figuras em vez de 1; "
                      "a tarja de cores volta a ser eleita portadora do dado"
                      % len(figs))
    elif not figs[0]["principal"] or figs[0]["principal"][0] != "corpo.png":
        falhas.append("fragmentacao entre paragrafos: o dado saiu em %r"
                      % (figs[0]["principal"] and figs[0]["principal"][0],))
    else:
        provas.append("junta o corpo do gráfico e a tarja de cores quando estão "
                      "em parágrafos colados, sem texto entre eles")

    # ... e os dois controles: imagens separadas por parágrafo vazio (as capturas
    #     de tela do apêndice) e imagens com prosa junto NAO podem virar grupo.
    soltos = [_par("Figura 1 - a"), _par("", [("rId1", 885825, 187146)]),
              _par(""), _par("", [("rId2", 1638300, 534955)]),
              _par(""), _par("", [("rId3", 5400040, 3603625)])]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(soltos, media)))
    figs = montar_figuras(ps, 3, tam)
    if len(figs) != 3:
        falhas.append("CONTROLE MORTO: tres imagens separadas por paragrafo "
                      "vazio viraram %d figura(s); o agrupamento junta o que "
                      "nao devia" % len(figs))
    else:
        provas.append("não junta imagens separadas por parágrafo vazio, que são "
                      "as capturas de tela em sequência do apêndice")

    com_prosa = [_par("prosa e imagem", [("rId1", 885825, 187146)]),
                 _par("mais prosa", [("rId3", 5400040, 3603625)])]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(com_prosa, media)))
    if len(montar_figuras(ps, 3, tam)) != 2:
        falhas.append("CONTROLE MORTO: paragrafos com prosa junto da imagem "
                      "viraram um grupo so")
    else:
        provas.append("não junta parágrafos que tenham prosa junto da imagem")

    # 5c. a legenda e a MAIS PROXIMA: o caso da x-v3, em que a de tras
    #     estava a um paragrafo e a da frente a dois, e ganhava a da frente.
    duas = [_par("Gráfico 8. Plenário Virtual"),
            _par("", [("rId3", 5400040, 3603625)]),
            _par("Fonte: elaborado pela autora"),
            _par("Gráfico 9. Plenário Presencial"),
            _par("", [("rId2", 1638300, 534955)])]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(duas, media)))
    figs = montar_figuras(ps, 3, tam)
    onde = [(f["p_imagem"], f["onde"]) for f in figs]
    if onde != [(2, 1), (5, 4)]:
        falhas.append("legenda mais proxima: %r, esperava [(2, 1), (5, 4)]"
                      % (onde,))
    else:
        provas.append("dá a cada figura a legenda mais próxima, e não a de três "
                      "parágrafos à frente quando há uma logo atrás")

    # 5d. no empate de distancia ganha a de cima, que e onde a norma poe o
    #     titulo de grafico. Sem isto a escolha ficaria ao acaso da ordem.
    empate = [_par("Gráfico 1 - a de cima"),
              _par("", [("rId3", 5400040, 3603625)]),
              _par("Gráfico 2 - a de baixo")]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(empate, media)))
    figs = montar_figuras(ps, 3, tam)
    if not figs or figs[0]["onde"] != 1:
        falhas.append("empate de distancia: a figura ficou em [P%s], e devia "
                      "ficar na legenda de cima, [P1]"
                      % (figs and figs[0]["onde"]))
    else:
        provas.append("com legenda a um parágrafo acima e outra a um abaixo, "
                      "fica com a de cima")

    # 6. duas figuras de tamanho parecido no mesmo paragrafo: nao se afirma qual
    #    carrega o dado.
    par = [_par("Figura 4 - duas ao lado"),
           _par("", [("rId1", 2600000, 2000000), ("rId2", 2700000, 2000000)])]
    media2 = [("rId1", "esq.png", 40000), ("rId2", "dir.png", 41000)]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(par, media2)))
    figs = montar_figuras(ps, 3, {"esq.png": 40000, "dir.png": 41000})
    if figs and figs[0]["principal"] is not None:
        falhas.append("CONTROLE MORTO: com areas parecidas o programa ainda "
                      "elegeu %r como portador do dado"
                      % (figs[0]["principal"][0],))
    else:
        provas.append("com áreas parecidas, recusa eleger o portador do dado")

    # 7. arquivo reaproveitado em duas figuras e peca compartilhada, mesmo sem
    #    diferenca de tamanho que decida.
    par = [_par("Gráfico 1 - a"),
           _par("", [("rId1", 2000000, 2000000), ("rId3", 2100000, 2000000)]),
           _par("Gráfico 2 - b"),
           _par("", [("rId1", 2000000, 2000000), ("rId2", 2050000, 2000000)])]
    media3 = [("rId1", "eixo.png", 2505), ("rId2", "b.png", 40000),
              ("rId3", "a.png", 41000)]
    tam3 = {"eixo.png": 2505, "b.png": 40000, "a.png": 41000}
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(par, media3)))
    figs = montar_figuras(ps, 3, tam3)
    nomes = [f["principal"][0] if f["principal"] else None for f in figs]
    if nomes != ["a.png", "b.png"]:
        falhas.append("reaproveitamento: o dado saiu em %r, esperava "
                      "['a.png', 'b.png']" % (nomes,))
    else:
        provas.append("trata como peça compartilhada o arquivo que aparece em "
                      "duas figuras, sem depender de tamanho")

    return falhas, provas


# -------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx", nargs="?")
    ap.add_argument("--extracao", help="para conferir o [P###] de cada figura")
    ap.add_argument("--saida", help="pasta onde gravar as imagens "
                                    "(padrão: figuras-<nome do trabalho>)")
    ap.add_argument("--vizinhanca", type=int, default=3,
                    help="quantos parágrafos procurar antes e depois pela legenda")
    ap.add_argument("--autoteste", action="store_true",
                    help="roda só os controles e sai")
    a = ap.parse_args()

    falhas, provas = autoteste()
    if falhas:
        print("  o programa está quebrado, e não reporto nada:")
        for f in falhas:
            print("    %s" % f)
        return 2
    print("  autoteste, %d controles:" % len(provas))
    for p in provas:
        print("    %s" % p)
    if a.autoteste:
        return 0
    if not a.docx:
        ap.error("falta o .docx")
    print("")

    doc = Path(a.docx)
    saida = Path(a.saida) if a.saida else doc.with_name("figuras-" + doc.stem)
    saida.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(doc)) as z:
        nomes = [n for n in z.namelist() if n.startswith("word/media/")]
        tamanhos = {Path(n).name: z.getinfo(n).file_size for n in nomes}
        for n in nomes:
            (saida / Path(n).name).write_bytes(z.read(n))
        ps = paragrafos_do_docx(z)
    print("  %d arquivo(s) de imagem em %s" % (len(nomes), saida))
    print("  %d parágrafos no corpo" % len(ps))

    ext = ""
    if a.extracao:
        if not Path(a.extracao).exists():
            # Antes isto caia na mensagem "sem --extracao", e um erro de
            # digitacao no caminho virava corrida sem conferencia nenhuma, com o
            # programa dizendo que o argumento nao fora dado.
            print("  --extracao aponta para arquivo que não existe: %s"
                  % a.extracao)
            return 2
        ext = io.open(a.extracao, encoding="utf-8", errors="replace").read()

    figuras = montar_figuras(ps, a.vizinhanca, tamanhos)
    ultima = max([f["onde"] for f in figuras] + [0])

    endereca, ate = True, 0
    if ext:
        casados, divergentes, exemplos, ate = conferir_alinhamento(ps, ext)
        total = casados + divergentes
        taxa = casados / float(total) if total else 0.0
        print("  alinhamento com a extração: %d de %d marcadores casam (%.1f%%),"
              " e eles vão até [P%d] de %d parágrafos"
              % (casados, total, 100 * taxa, ate, len(ps)))
        if taxa < ALINHAMENTO_MINIMO:
            endereca = False
            print("  a extração não corresponde a este .docx, e por isso NÃO "
                  "dou endereço nenhum.")
            for idx, d, e in exemplos:
                print("    [P%d] docx=%r extração=%r" % (idx, d[:32], e[:32]))
        elif ate < ultima:
            print("  a extração é PARCIAL e para antes da última figura, em "
                  "[P%d]: taxa alta aí não é\n  cobertura, e as figuras depois "
                  "desse ponto saem sem endereço conferido." % ate)
    else:
        print("  sem --extracao: o [P###] sai da contagem de parágrafos e não "
              "foi conferido contra nada.")
    print("")
    for n, f in enumerate(figuras, 1):
        conferido = endereca and (not ext or f["onde"] <= ate)
        onde = ("[P%d]" % f["onde"]) if endereca else "—"
        if endereca and not conferido:
            onde += "?"
        print("  %-3d %-8s %s" % (n, onde,
                                  f["legenda"][:88] or "(sem legenda por perto)"))
        faixa = ("[P%d]" % f["p_imagem"] if f["p_imagem"] == f["p_ultimo"]
                 else "[P%d]-[P%d]" % (f["p_imagem"], f["p_ultimo"]))
        img_em = ("imagem em %s" % faixa) if endereca else "imagem"
        if f["principal"]:
            nome = f["principal"][0]
            marca = ("" if len(f["imgs"]) == 1
                     else "  (o dado está aqui, %s)" % f["motivo"])
            print("      %s: %s, %s%s"
                  % (img_em, nome, kb(tamanhos.get(nome, 0)), marca))
        else:
            print("      %s: %d arquivos de %s, e não digo qual carrega o dado"
                  % (img_em, len(f["imgs"]), f["motivo"]))
            for nome, _, _ in f["imgs"]:
                print("        %s, %s" % (nome, kb(tamanhos.get(nome, 0))))
        for nome, _, _ in f["acessorios"]:
            repetido = f["uso"][nome]
            extra = (", em %d figuras" % repetido) if repetido > 1 else ""
            print("        peça: %s, %s%s"
                  % (nome, kb(tamanhos.get(nome, 0)), extra))

    usados = {n for f in figuras for n, _, _ in f["imgs"]}
    sem_legenda = [f for f in figuras if not f["legenda"]]
    sem_dado = [f for f in figuras if not f["principal"]]
    print("\n  %d figura(s) no corpo, em %d arquivo(s) de imagem."
          % (len(figuras), len(usados)))
    if sem_legenda:
        print("  %d sem legenda reconhecida por perto." % len(sem_legenda))
    if sem_dado:
        print("  %d com mais de um arquivo e sem dizer qual carrega o dado."
              % len(sem_dado))
    orfas = len(nomes) - len(usados)
    if orfas > 0:
        print("  %d arquivo(s) em word/media/ não aparecem no corpo: cabeçalho, "
              "logotipo, miniatura ou imagem removida." % orfas)

    # Um mesmo arquivo pode carregar o dado de mais de uma figura: no acervo,
    # image48.png aparece sozinho em tres paragrafos. Pedir tres vezes o mesmo
    # arquivo gasta chamada a toa.
    principais, ja = [], set()
    for f in figuras:
        if f["principal"] and f["principal"][0] not in ja:
            ja.add(f["principal"][0])
            principais.append(f["principal"][0])
    if principais:
        print("\n  Os %d arquivos que carregam dado, para pedir NUMA MENSAGEM SÓ "
              "(a restrição\n  de chamada paralela é da página de PDF, e não do "
              "arquivo de imagem):" % len(principais))
        linha = "    "
        for nome in principais:
            if len(linha) + len(nome) > 88:
                print(linha)
                linha = "    "
            linha += nome + " "
        if linha.strip():
            print(linha)
    return 0


if __name__ == "__main__":
    sys.exit(main())

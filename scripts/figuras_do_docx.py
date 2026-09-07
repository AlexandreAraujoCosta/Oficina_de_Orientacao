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

O ENDERECO SAI DA POSICAO, E NAO DO TEXTO DA LEGENDA

Medido em 07/09/2026 sobre `t-agosto.docx`: as 117 imagens sairam
todas enderecadas em [P161]-[P228], que e o indice de graficos das primeiras
paginas. A causa e que o indice repete a legenda do corpo palavra por palavra, e
o casador por texto ficava com a PRIMEIRA ocorrencia. Os tres graficos do
capitulo 6 estao em [P751], [P763] e [P775]; o programa dizia [P182], [P183] e
[P184].

O conserto casa por POSICAO: a contagem de paragrafos aqui repete a regra do
extrator, de modo que o n-esimo paragrafo do corpo e o [Pn] da extracao. A
extracao deixou de ser consultada para achar endereco e passou a servir de
CONFERENCIA do alinhamento, paragrafo a paragrafo.

UMA FIGURA PODE ESTAR PARTIDA EM VARIOS ARQUIVOS

No mesmo trabalho, cada grafico estava partido em tres imagens: o corpo do
grafico, o rotulo do eixo e a legenda de cores, gravados como arquivos
separados. So um deles mostra o dado. O programa agrupa as imagens do mesmo
paragrafo e diz qual carrega o dado, pela area em que a imagem e exibida
(`wp:extent`) e pelo reaproveitamento do arquivo em mais de uma figura.

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
# se afirme que e ela que carrega o dado. Medido no acervo: nos nove paragrafos
# com mais de uma imagem, a razao entre a maior area exibida e a segunda vai de
# 8,4 a 28. Por bytes a separacao e bem pior (a menor razao e 2,1, e naquele
# caso o arquivo pequeno era mesmo so a legenda de cores), e por isso a area
# manda e o tamanho em disco entra so como recurso.
RAZAO = 3.0

# Abaixo desta proporcao de paragrafos casados, a extracao nao corresponde a
# este .docx e nenhum endereco sai.
ALINHAMENTO_MINIMO = 0.90

# A legenda de figura, tabela ou grafico, nas formas que o acervo traz. O numero
# pode vir depois de traco, ponto ou espaco, e o tipo pode vir em caixa alta.
# O identificador nem sempre e numero. Numa tese do acervo as figuras sao
# "Figure A", "Figure B" e tres delas "Figure X", o que e defeito do trabalho e
# nao do programa: exigir digito deixava treze figuras sem legenda reconhecida.
RE_LEGENDA = re.compile(
    r"^\s*(Gr[áa]fico|Figura|Tabela|Quadro|Imagem|Chart|Table|Figure)"
    r"\s*(\d{1,3}|[A-Z]|[IVXL]{1,5})\s*[-–—.:]\s*(.*)$"
    r"|^\s*(Gr[áa]fico|Figura|Tabela|Quadro|Imagem|Chart|Table|Figure)"
    r"\s*(\d{1,3})\s*(.*)$", re.I)

# O marcador de paragrafo da extracao so vale no comeco da linha, depois do que
# o extrator poe antes dele (**, #, >). No meio da linha, "[P757]" e referencia
# cruzada escrita pelo leitor, e nao endereco.
RE_MARCADOR = re.compile(r"^[>\s]*[#*`]*\s*\[P(\d+)\][^\n]*", re.M)


# --------------------------------------------------------------- leitura do docx

def paragrafos_do_docx(fonte):
    """Devolve, na ordem, (texto, imagens) de cada paragrafo do corpo.

    A posicao na lista e o endereco: o item de indice k e o [P(k+1)] da
    extracao. Para que isso valha, a contagem repete a regra do extrator
    (`collect_paragraphs` em analisar_docx.py): anda a arvore, conta `<w:p>` e
    desce em tabela, sdt, linha, celula e smartTag.

    Expressao regular nao serve aqui, e o defeito e do tipo que passa
    despercebido porque some no total. `<w:p ...>.*?</w:p>` trata o paragrafo
    vazio auto-fechado `<w:p w:rsidR="00AB"/>` como abertura, porque o `[ >]`
    casa o espaco antes dos atributos, e engole o paragrafo seguinte inteiro.
    Em `t-agosto.docx` sao seis desses, e a contagem saia 1.430 para
    1.434 paragrafos reais. Quatro de deslocamento erram todo endereco a partir
    do primeiro.

    Cada imagem vem como (arquivo, cx, cy), com cx e cy em EMU, que e a area em
    que o Word a exibe. Vale zero quando o desenho nao traz `wp:extent` (VML
    antigo), e nesse caso o desempate cai no tamanho em disco.
    """
    fechar = False
    if isinstance(fonte, zipfile.ZipFile):
        z = fonte
    else:
        z = zipfile.ZipFile(fonte)
        fechar = True
    try:
        xml = z.read("word/document.xml")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
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
            elif filho.tag in DESCE:
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

    Devolve (casados, divergentes, exemplos). Sem isto o endereco por posicao
    seria fe: bastaria a extracao ser de outra versao do trabalho para todo
    [P###] sair errado sem sinal nenhum.
    """
    casados, divergentes, exemplos = 0, 0, []
    for m in RE_MARCADOR.finditer(extracao):
        idx = int(m.group(1))
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
    return casados, divergentes, exemplos


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
        return imgs[0], [], "único arquivo"
    proprios = [i for i in imgs if uso[i[0]] == 1]
    pool = proprios or list(imgs)
    if len(pool) == 1:
        return pool[0], [i for i in imgs if i is not pool[0]], \
            "os outros se repetem em outras figuras"
    if all(area(i) for i in pool):
        chave, nome = area, "área exibida"
    else:
        chave, nome = (lambda i: tamanhos.get(i[0], 0)), "tamanho em disco"
    ordem = sorted(pool, key=chave, reverse=True)
    if chave(ordem[1]) <= 0 or chave(ordem[0]) < RAZAO * chave(ordem[1]):
        return None, list(imgs), "tamanhos próximos"
    principal = ordem[0]
    return principal, [i for i in imgs if i is not principal], nome


def montar_figuras(ps, vizinhanca, tamanhos):
    """Agrupa as imagens por paragrafo e acha a legenda de cada grupo.

    O endereco da figura e o do paragrafo da LEGENDA quando ha uma, porque e por
    ele que a leitura acha a figura no texto extraido; o paragrafo da imagem vai
    junto, e costuma ser o seguinte.
    """
    com_imagem = [(k, p) for k, p in enumerate(ps) if p[1]]
    uso = Counter(nome for _, p in com_imagem for nome, _, _ in p[1])
    figuras = []
    for k, (texto, imgs) in com_imagem:
        legenda, leg_idx = "", None
        for d in list(range(0, vizinhanca + 1)) + \
                 [-x for x in range(1, vizinhanca + 1)]:
            j = k + d
            if 0 <= j < len(ps) and RE_LEGENDA.match(ps[j][0]):
                legenda = re.sub(r"\s+", " ", ps[j][0])
                leg_idx = j + 1
                break
        principal, acessorios, motivo = repartir(imgs, uso, tamanhos)
        figuras.append({
            "onde": leg_idx or (k + 1),
            "p_imagem": k + 1,
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

    # 1. o leitor de legenda
    for bom in ("Gráfico 22 – Decisões por ano", "TABELA 4 - Distribuição",
                "Figura 2: série histórica", "Chart 3 Something"):
        if not RE_LEGENDA.match(bom):
            falhas.append("nao reconhece legenda: %r" % bom)
    for mau in ("O gráfico acima mostra que", "Tabelas de contingência sobre",
                "A figura de duração é apresentada"):
        if RE_LEGENDA.match(mau):
            falhas.append("confunde prosa com legenda: %r" % mau)
    provas.append("reconhece as quatro escritas de legenda e recusa três prosas "
                  "que começam pela mesma palavra")

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
    casados, divergentes, _ = conferir_alinhamento(ps, ext)
    if casados != 6 or divergentes:
        falhas.append("alinhamento: %d casados e %d divergentes, esperava 6 e 0"
                      % (casados, divergentes))

    # 4. o alinhamento tem de acusar extracao que nao e deste .docx.
    ext_torta = "\n".join("[P%d] %s" % (i + 2, ps[i][0]) for i in range(len(ps))
                          if ps[i][0])
    casados, divergentes, _ = conferir_alinhamento(ps, ext_torta)
    if casados >= divergentes:
        falhas.append("CONTROLE MORTO: extracao deslocada em um paragrafo "
                      "passou com %d casados e %d divergentes"
                      % (casados, divergentes))
    else:
        provas.append("recusa extração deslocada de um parágrafo (%d casados "
                      "contra %d divergentes)" % (casados, divergentes))

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

    # ... e o controle: em paragrafos diferentes nao pode virar grupo.
    soltos = [_par("Figura 1 - a"), _par("", [("rId1", 885825, 187146)]),
              _par("Figura 2 - b"), _par("", [("rId2", 1638300, 534955)]),
              _par("Figura 3 - c"), _par("", [("rId3", 5400040, 3603625)])]
    ps = paragrafos_do_docx(zipfile.ZipFile(_zip_de_teste(soltos, media)))
    figs = montar_figuras(ps, 3, tam)
    if len(figs) != 3:
        falhas.append("CONTROLE MORTO: tres imagens em paragrafos diferentes "
                      "viraram %d figura(s); o agrupamento junta o que nao devia"
                      % len(figs))
    else:
        provas.append("não junta imagens que estão em parágrafos diferentes")

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
    if a.extracao and Path(a.extracao).exists():
        ext = io.open(a.extracao, encoding="utf-8", errors="replace").read()

    endereca = True
    if ext:
        casados, divergentes, exemplos = conferir_alinhamento(ps, ext)
        total = casados + divergentes
        taxa = casados / float(total) if total else 0.0
        print("  alinhamento com a extração: %d de %d parágrafos casam (%.1f%%)"
              % (casados, total, 100 * taxa))
        if taxa < ALINHAMENTO_MINIMO:
            endereca = False
            print("  a extração não corresponde a este .docx, e por isso NÃO "
                  "dou endereço nenhum.")
            for idx, d, e in exemplos:
                print("    [P%d] docx=%r extração=%r" % (idx, d[:32], e[:32]))
    else:
        print("  sem --extracao: o [P###] sai da contagem de parágrafos e não "
              "foi conferido contra nada.")

    figuras = montar_figuras(ps, a.vizinhanca, tamanhos)
    print("")
    for n, f in enumerate(figuras, 1):
        onde = ("[P%d]" % f["onde"]) if endereca else "—"
        print("  %-3d %-8s %s" % (n, onde,
                                  f["legenda"][:88] or "(sem legenda por perto)"))
        img_em = ("imagem em [P%d]" % f["p_imagem"]) if endereca else "imagem"
        if f["principal"]:
            nome = f["principal"][0]
            marca = ("" if len(f["imgs"]) == 1
                     else "  (o dado está aqui, por %s)" % f["motivo"])
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

    principais = [f["principal"][0] for f in figuras if f["principal"]]
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

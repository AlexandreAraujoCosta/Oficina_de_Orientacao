# -*- coding: utf-8 -*-
"""Grava uma copia do .docx com os apontamentos como comentarios do Word.

POR QUE ISTO EXISTE

O relatorio e um PDF de cem paginas ao lado do documento, e conferir um item
exige achar o paragrafo. Aqui o apontamento fica no lugar: o autor abre o
trabalho no Word e ve a anotacao na margem, na altura do paragrafo citado.

E o formato tem uma virtude que o PDF nao tem: comentario do Word e conversa.
O orientador le, responde na mesma linha, e a resposta fica no arquivo.

COMO ANCORA, E A REGRA TEM DUAS METADES

Item que traz o campo `**Marca:**` no anexo marca TODOS os pontos que cita, e
cada marca alem da primeira carrega a instrucao curta daquele campo. E o caso da
correcao ponto a ponto: uma palavra errada em quinze lugares e quinze tarefas, e
cada uma se resolve onde esta.

Item sem esse campo marca UM ponto so, e o texto do comentario diz em que
paginas ele ocorre. E o caso da afirmacao sobre o conjunto: repeti-la em
dezesseis lugares da margem produz eco, e nao endereco.

As duas metades vieram de medicao, e uma corrigiu a outra. Quem recebeu a
primeira entrega, em 28/08/2026, disse que um comentario juntava todos os erros
do capitulo e caia em lugar arbitrario; a resposta foi marcar cada ponto, e numa
entrega de 53 itens isso produziu 307 marcas, das quais 254 eram continuacao.
Uma leitura fria dos mesmos 53 itens, no dia seguinte, reprovou treze deles
porque a frase de reformulacao comecava com "procurar": o texto dizia "as duas
glosas do capitulo 4" sem dizer quais, e a marca e que estava carregando o
endereco. Escrito o endereco no texto, o item de argumento volta a uma marca so,
e a mesma entrega cai para 53.

A TRAVA QUE IMPEDE O PIOR ERRO

Comentario ancorado no paragrafo errado e pior que comentario nenhum, porque
manda o autor olhar onde nao ha nada. A numeracao [P123] vem de
collect_paragraphs, e aqui os paragrafos sao localizados por expressao regular
sobre o XML cru. As duas contagens precisam bater, e o programa se recusa a
gravar quando nao batem.

    python anotar_docx.py <trabalho.docx> <ENTREGA-CORRETOR-*.md> [--saida X.docx]
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar_docx import load, Styles, collect_paragraphs, W  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



AUTOR = "Luis"
INICIAIS = "AL"
DATA = "2026-01-01T12:00:00Z"

RE_PAR_XML = re.compile(rb"<w:p(?:\s[^>]*)?/>|<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
RE_ITEM = re.compile(
    r"^## ([A-Z]{1,2}\d+)\s*$\n+\*\*Aponta:\*\* (.+?)\s*$\n+\*\*Abrir:\*\* (.*?)\s*$",
    re.M | re.S)
RE_LOC = re.compile(r"\[P(\d+)\]")
RE_MARCA = re.compile(
    r"^## ([A-Z]{1,2}\d+)\s*$(?:(?!^## ).)*?^\*\*Marca:\*\* (.+?)\s*$",
    re.M | re.S)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def spans(doc_bytes):
    """Os paragrafos na ordem em que o documento os traz."""
    return [(m.start(), m.end(), m.group(0).endswith(b"/>"))
            for m in RE_PAR_XML.finditer(doc_bytes)]


def itens(caminho):
    txt = Path(caminho).read_text(encoding="utf-8")
    out = []
    for m in RE_ITEM.finditer(txt):
        cod, aponta, abrir = m.group(1), m.group(2).strip(), m.group(3)
        locs = [int(x) for x in RE_LOC.findall(abrir)]
        if locs:
            out.append((cod, aponta, locs))
    return out


def marcas(caminho):
    """A instrucao curta de cada item, para os pontos alem do primeiro.

    Um item que cita quinze ocorrencias da mesma palavra errada precisa marcar as
    quinze, e nao pode levar o apontamento inteiro em todas: quinze comentarios
    com o mesmo paragrafo de texto e leitura de maquina, e quem le o terceiro ja
    nao le. No ponto repetido o que serve e o que fazer ali, numa linha. Isso e
    redacao, e nao se deriva da prosa do apontamento, entao vem escrito no anexo:

        **Marca:** trocar prevalescente por prevalecente

    Sem o campo, o programa cai no comeco do proprio apontamento."""
    txt = Path(caminho).read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in RE_MARCA.finditer(txt)}


def enderecos(locs, pags, secoes, pars, teto=8):
    """Onde o item ocorre, escrito no proprio comentario.

    A pagina quando ela existe, porque e o endereco que quem recebe ja sabe
    usar; a secao ou as palavras iniciais quando nao ha PDF da mesma versao.
    Acima do teto a lista para e diz quantos ficaram de fora, porque enumerar
    trinta paginas numa margem nao ajuda ninguem."""
    if len(locs) < 2:
        return ""
    p = [(pags or {}).get(str(n)) or (pags or {}).get(n) for n in locs]
    if all(p):
        # Em ordem de pagina, e nao na ordem em que o item citou: quem vai
        # corrigir percorre o trabalho do comeco ao fim, e nao na ordem em que
        # a analise achou as coisas.
        vistas = sorted({int(x) for x in p})
        corte = [str(x) for x in vistas[:teto]]
        lista = (", ".join(corte[:-1]) + " e " + corte[-1]) if len(corte) > 1 else corte[0]
        if len(vistas) > teto:
            lista += ", e em mais %d, listadas no relatório" % (len(vistas) - teto)
        # p. no singular e pp. no plural, que e a forma classica da abreviatura.
        uma = len(vistas) == 1
        return "Ocorre %s %s %s." % ("na" if uma else "nas",
                                     "p." if uma else "pp.", lista)
    # Sem mapa de paginas, o endereco que funciona no Word e o que o Ctrl+F acha.
    ab = [x for x in (abertura(pars, n) for n in locs[:4]) if x]
    if ab:
        return ("Ocorre também em %s." % "; ".join('"%s"' % x for x in ab[1:])
                if len(ab) > 1 else "")
    return "Ocorre em %d pontos, listados no relatório." % len(locs)


def resumo_curto(texto, limite=160):
    """O comeco do apontamento, quando o anexo nao trouxe a marca.

    Corta em fim de periodo, e nunca em dois-pontos: frase cortada ali anuncia o
    assunto sem dizer o defeito, que e o pior resultado possivel numa marca."""
    # O endereco `[p. 47]` traz ponto e espaco, e cortar ali parte a marca no
    # meio do localizador. Os colchetes sao mascarados antes de dividir. A
    # mascara nao pode ser espaco de tipo nenhum: `\s` casa tambem com o
    # espaco inseparavel, que foi a primeira tentativa e nao funcionou.
    # chr(31) nao serve: Python conta de chr(28) a chr(31) como espaco, e `\s`
    # casa com eles. A mascara vai na area de uso privado do Unicode.
    MASCARA = chr(0xE000)
    protegido = re.sub(r"\[[^\]]*\]",
                       lambda m: m.group(0).replace(". ", "." + MASCARA),
                       texto.strip())
    partes = [p.replace("." + MASCARA, ". ")
              for p in re.split(r"(?<=[.?!])\s+", protegido)]
    saida = partes[0] if partes else texto
    for p in partes[1:]:
        if len(saida) >= 60 and not saida.rstrip().endswith(":"):
            break
        saida += " " + p
    saida = (saida if len(saida) <= limite
             else saida[:limite].rsplit(" ", 1)[0] + "...")
    # Muito apontamento chega sem ponto final, porque no anexo ele e titulo de
    # item e nao frase. Dentro do comentario ele vira frase, e emenda na linha
    # seguinte se nao for fechado.
    return saida if saida[-1:] in ".?!:;" else saida + "."


def abertura(pars, n, limite=46):
    """As primeiras palavras do paragrafo, para quem procura no Word com Ctrl+F."""
    if not (1 <= n <= len(pars)):
        return None
    s = " ".join(pars[n - 1].text.split())
    if len(s) < 12:
        return None
    if len(s) <= limite:
        return s
    corte = s.rfind(" ", 0, limite)
    return s[:corte if corte > 20 else limite] + "…"


def mapa_secoes(pars):
    """Para cada paragrafo, a secao em que ele esta.

    Dentro do Word o [P252] nao serve, e a abertura do paragrafo e longa demais
    para caber no meio de uma frase. A secao cabe, e o painel de navegacao a
    encontra."""
    mapa, atual = {}, None
    for p in pars:
        if p.level is not None and p.text.strip():
            s = " ".join(p.text.split())
            m = re.match(r"^(\d+(?:\.\d+)*)", s)
            atual = m.group(1) if m else (s[:24].rsplit(" ", 1)[0] if len(s) > 24 else s)
        mapa[p.idx] = atual
    return mapa


def sem_localizador(texto, mapa, pars=None, pags=None):
    """Troca [P123] pelo endereco que funciona dentro do Word.

    O localizador ocupa lugar de substantivo na frase ("a promessa de [P7]"), e
    por isso a troca precisa ocupar o mesmo lugar. Trocar por "na secao 2.1"
    produz "a promessa de na secao 2.1". Trocar por "[2.1]" preserva a sintaxe,
    porque um colchete substitui outro.

    So o nome da secao, porem, nao endereca: ha secao de trinta paginas, e quem
    procura dentro dela esta na mesma situacao de quem nao recebeu localizador
    nenhum. O endereco que funciona ali e o que o Ctrl+F acha, isto e, as
    palavras com que o paragrafo comeca. Elas sao copiadas do arquivo por este
    programa, e nunca redigitadas pelo modelo."""
    def troca(m):
        n = int(m.group(1))
        s = mapa.get(n)
        # A pagina e o endereco que a pessoa ja sabe usar, e foi o que quem
        # recebeu a primeira entrega disse ter preferido. Ela existe quando se
        # paginou o mesmo arquivo que esta sendo comentado, e nao existe quando
        # nao ha PDF; por isso as palavras iniciais continuam de reserva.
        pg = (pags or {}).get(str(n)) or (pags or {}).get(n)
        if pg:
            return "[p. %s]" % pg
        ini = abertura(pars, n) if pars else None
        if ini and s:
            return '["%s", em %s]' % (ini, s)
        if ini:
            return '["%s"]' % ini
        return ("[%s]" % s) if s else ""
    t = re.sub(r"\[P(\d+)\]", troca, texto)
    t = re.sub(r"\[P\d+(?:[-–]P?\d+)?\]", "", t)
    # Espaco solto antes da pontuacao, quando um localizador some sem secao
    # conhecida. O grupo tem de voltar na substituicao: a versao anterior
    # apagava a pontuacao junto, e a frase chegava sem o ponto final.
    t = re.sub(r"\s+([,.;:])", r"\1", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def comentarios_existentes(z):
    """Os comentarios que o autor ja tem, e o primeiro id livre.

    Os ids precisam ser unicos no arquivo: comecar do zero apagaria a conversa
    que ja esta la."""
    tem = "word/comments.xml" in z.namelist()
    com_xml = z.read("word/comments.xml").decode("utf-8") if tem else None
    usados = [int(x) for x in re.findall(r'w:id="(\d+)"', com_xml or "")]
    return tem, com_xml, usados, (max(usados) + 1 if usados else 0)


def ancorar(doc, sp, por_par, prox):
    """Poe as marcas de comentario nos paragrafos, e devolve (doc novo, novos).

    `por_par` e {numero do paragrafo: [textos]}; `novos` sai como [(id, texto)]
    para quem for escrever o comments.xml."""
    novos, saida, pos = [], [], 0
    for n in sorted(por_par):
        ini, fim, vazio = sp[n - 1]
        if vazio:
            continue
        saida.append(doc[pos:ini])
        bloco = doc[ini:fim]
        # A marca entra depois do <w:pPr>, e nao logo apos a abertura do
        # paragrafo. Ate 27/08/2026 entrava antes, e o Word abria assim mesmo,
        # mas o esquema manda o <w:pPr> ser o primeiro filho de <w:p> e um
        # leitor menos tolerante recusa o arquivo.
        ppr = bloco.find(b"</w:pPr>")
        abre = (ppr + len(b"</w:pPr>")) if ppr >= 0 else bloco.index(b">") + 1
        marca_ini, marca_fim = b"", b""
        for texto in por_par[n]:
            marca_ini += ('<w:commentRangeStart w:id="%d"/>' % prox).encode()
            marca_fim += ('<w:commentRangeEnd w:id="%d"/><w:r><w:commentReference w:id="%d"/></w:r>'
                          % (prox, prox)).encode()
            novos.append((prox, texto))
            prox += 1
        bloco = bloco[:abre] + marca_ini + bloco[abre:-len(b"</w:p>")] + marca_fim + b"</w:p>"
        saida.append(bloco)
        pos = fim
    saida.append(doc[pos:])
    return b"".join(saida), novos


def corpo_do_comentario(texto):
    """O texto do apontamento em paragrafos de verdade, com negrito.

    Ate 28/08/2026 o comentario saia num paragrafo unico, e quem o recebeu disse
    que "o texto fica todo junto e sem formatacao, o que dificulta o
    entendimento". O formato do Word sempre permitiu paragrafo e negrito dentro
    do comentario; o programa e que nao usava.

    Convencoes do texto de entrada: linha em branco separa paragrafo, e o que
    esta entre ** vira negrito.
    """
    saida = []
    for bloco in [b for b in texto.split(chr(10)) if b.strip()]:
        corridas = []
        for i, pedaco in enumerate(bloco.split("**")):
            if not pedaco:
                continue
            negrito = "<w:rPr><w:b/></w:rPr>" if i % 2 else ""
            corridas.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
                            % (negrito, esc(pedaco)))
        saida.append("<w:p>" + "".join(corridas) + "</w:p>")
    return "".join(saida) or "<w:p/>"


def escrever(z, doc, novos, dest, autor=AUTOR, tem_comentarios=None, com_xml=None):
    """Grava o .docx com o document.xml novo e os comentarios acrescentados.

    Escrever comentario no .docx pede quatro pecas, e faltar uma delas produz
    arquivo que o Word recusa a abrir: o corpo em comments.xml, o tipo em
    [Content_Types].xml, a relacao em document.xml.rels, e a marca no corpo."""
    if tem_comentarios is None:
        tem_comentarios, com_xml, _, _ = comentarios_existentes(z)
    corpo = "".join(
        '<w:comment w:id="%d" w:author="%s" w:initials="%s" w:date="%s">%s</w:comment>'
        % (cid, esc(autor), INICIAIS, DATA, corpo_do_comentario(t)) for cid, t in novos)
    if tem_comentarios:
        com_xml = com_xml.replace("</w:comments>", corpo + "</w:comments>")
    else:
        com_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<w:comments xmlns:w="http://schemas.openxmlformats.org/'
                   'wordprocessingml/2006/main">' + corpo + "</w:comments>")

    ct = z.read("[Content_Types].xml").decode("utf-8")
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    if "comments+xml" not in ct:
        ct = ct.replace("</Types>",
            '<Override PartName="/word/comments.xml" ContentType="application/vnd.'
            'openxmlformats-officedocument.wordprocessingml.comments+xml"/></Types>')
    if "comments.xml" not in rels:
        rels = rels.replace("</Relationships>",
            '<Relationship Id="rIdComentariosLuis" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/comments" Target="comments.xml"/></Relationships>')

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            if it.filename == "word/document.xml":
                zo.writestr(it, doc)
            elif it.filename == "word/comments.xml":
                zo.writestr(it, com_xml)
            elif it.filename == "[Content_Types].xml":
                zo.writestr(it, ct)
            elif it.filename == "word/_rels/document.xml.rels":
                zo.writestr(it, rels)
            else:
                zo.writestr(it, z.read(it.filename))
        if not tem_comentarios:
            zo.writestr("word/comments.xml", com_xml)


def main():
    ap = argparse.ArgumentParser(description="Apontamentos como comentários do Word.")
    ap.add_argument("trabalho")
    ap.add_argument("lista", help="ENTREGA-CORRETOR-*.md")
    ap.add_argument("--saida")
    ap.add_argument("--autor", default=AUTOR)
    ap.add_argument("--paginas", help="o JSON do paginas.py, da MESMA versão")
    a = ap.parse_args()

    if not a.trabalho.lower().endswith(".docx"):
        sys.exit("só funciona com .docx: um PDF não tem onde guardar comentário.")

    # ---- confere a numeracao antes de qualquer coisa
    parts = load(a.trabalho)
    pars = collect_paragraphs(parts["word/document.xml"].find(W + "body"),
                              Styles(parts["word/styles.xml"]))
    z = zipfile.ZipFile(a.trabalho)
    doc = z.read("word/document.xml")
    sp = spans(doc)
    if len(sp) != len(pars):
        sys.exit("as duas contagens de parágrafo não batem (%d por XML, %d pelo extrator).\n"
                 "Ancorar assim poria o comentário no parágrafo errado. Nada foi gravado."
                 % (len(sp), len(pars)))

    secoes = mapa_secoes(pars)
    lista = itens(a.lista)
    marca = marcas(a.lista)
    pags = json.loads(Path(a.paginas).read_text(encoding="utf-8")) if a.paginas else {}
    if not lista:
        sys.exit("nenhum item com localizador na lista: nada a ancorar.")

    # ---- um comentario por item, no primeiro paragrafo citado
    por_par = {}
    fora = []
    for cod, aponta, locs in lista:
        validos = [n for n in locs if 1 <= n <= len(sp) and not sp[n - 1][2]]
        if not validos:
            fora.append(cod)
            continue
        alvo, demais = validos[0], validos[1:]
        limpo = sem_localizador(aponta, secoes, pars, pags)

        # O item diz onde ele ocorre, no proprio texto. Ate 29/08/2026 essa
        # informacao existia so como marca na margem, e o texto do apontamento
        # falava de "as duas glosas do capitulo 4" sem dizer quais: uma leitura
        # fria dos 53 itens desta entrega reprovou treze deles porque a frase
        # de reformulacao comecava com "procurar".
        onde = enderecos(validos, pags, secoes, pars)
        # O apontamento chega do anexo como titulo de item, e muitas vezes sem
        # ponto final. Dentro do comentario ele vira frase, e emenda no endereco
        # que vem logo abaixo.
        if limpo and limpo[-1] not in ".?!:;":
            limpo += "."

        # Marcar todos os pontos, ou marcar um so, e a decisao esta no campo
        # `Marca:` do anexo. Ele existe quando a correcao e a mesma em cada
        # ocorrencia, e ai cada ponto e uma tarefa. Sem ele o item e uma
        # afirmacao sobre o conjunto, e repeti-la na margem em dezesseis lugares
        # produz eco: medido nesta entrega, 254 das 307 marcas eram continuacao.
        curta = marca.get(cod)
        if curta and demais:
            texto = "**[%s]** %s" % (cod, limpo)
            if onde:
                texto += "%s%s Os pontos estão marcados um a um." % (chr(10), onde)
            por_par.setdefault(alvo, []).append(texto)
            for i, n in enumerate(demais, start=2):
                por_par.setdefault(n, []).append(
                    "**[%s]** %d de %d. %s" % (cod, i, len(validos), curta))
        else:
            texto = "**[%s]** %s" % (cod, limpo)
            if onde and demais:
                texto += "%s%s" % (chr(10), onde)
            por_par.setdefault(alvo, []).append(texto)

    # ---- ids livres, para nao colidir com os comentarios do autor
    tem_comentarios, com_xml, usados, prox = comentarios_existentes(z)
    doc, novos = ancorar(doc, sp, por_par, prox)

    dest = Path(a.saida) if a.saida else \
        Path(a.trabalho).with_name(Path(a.trabalho).stem + "-ANOTADO.docx")
    escrever(z, doc, novos, dest, a.autor, tem_comentarios, com_xml)

    print("  %s: %d comentários em %d parágrafos%s"
          % (dest.name, len(novos), len(por_par),
             ", %d do autor preservados" % len(usados) if usados else ""))
    if fora:
        print("  sem âncora (localizador fora do documento): %s" % ", ".join(fora))
    return 0


if __name__ == "__main__":
    sys.exit(main())

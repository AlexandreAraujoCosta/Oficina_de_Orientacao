# -*- coding: utf-8 -*-
"""Aplica os reparos dentro do .docx do autor, como alteracoes controladas.

POR QUE ISTO EXISTE

O corretor produzia pares Esta/Fica num chat, e o par no chat nao chega a lugar
nenhum: alguem tinha de abrir o arquivo e digitar. Aqui o reparo entra no
documento como marca de revisao do Word, e o autor aceita ou recusa um a um, na
ferramenta que ja usa.

A DIVISAO DE TRABALHO, QUE E O DESENHO INTEIRO

A prosa substituta vem de uma passagem de modelo. A aplicacao e programa. Nao se
pede a modelo que edite o arquivo: ele escreve o `Fica`, e este programa o poe no
lugar. Aplicacao deterministica e o que torna o resultado conferivel.

O `Esta` nao e escrito por ninguem: e um endereco, `{{P464F2}}`, e o texto sai
daqui, copiado do proprio arquivo. Reparo que chegue com texto digitado ali e
recusado com a razao escrita.

ONDE TROCA E ONDE RECUSA

O alvo precisa caber num trecho de formatacao continua. Onde atravessa italico,
nota de rodape, campo ou tabulacao, o programa nao remenda: vira comentario na
margem, com a proposta dentro, e o autor faz a mao. Medido em 27/08/2026 nos
paragrafos citados pelos apontamentos, cabem 91% das frases de uma dissertacao e 79%
das de um capitulo.

A PROVA QUE ELE DA ANTES DE GRAVAR

Duas conferencias, e reprovar em qualquer uma impede a gravacao:

- recusando todas as alteracoes, o texto volta a ser o original, caractere por
  caractere, em todos os paragrafos;
- aceitando todas, o texto e o original com exatamente as trocas pedidas.

Junto vai a trava herdada de `anotar_docx.py`: as duas contagens de paragrafo
precisam bater, porque comentario no paragrafo errado e pior que comentario
nenhum.

O QUE ELE NAO CONFERE

Se o achado foi confirmado. Este programa executa o que o arquivo de reparos
manda, e o portao e humano e fica antes: o relatorio passa por quem responde
pela orientacao, e so entao alguem escreve os reparos. Rodar isto sobre saida
bruta de analisador poe no trabalho do autor correcao derivada de defeito que
talvez nao exista.

    python aplicar_docx.py --frases <trabalho.docx> <ENTREGA-CORRETOR-*.md>
    python aplicar_docx.py <trabalho.docx> <reparos.md> [--lista ENTREGA-CORRETOR-*.md]
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reparos as R                                                # noqa: E402
from analisar_docx import load, Styles, collect_paragraphs, W      # noqa: E402
from anotar_docx import (spans, itens, mapa_secoes, sem_localizador,  # noqa: E402
                         comentarios_existentes, ancorar, escrever)

AUTOR = "Oficina de Orientação (programa)"
DATA = "2026-01-01T12:00:00Z"

RE_INS = re.compile(rb"<w:ins(?:\s[^>]*)?/>|<w:ins(?:\s[^>]*)?>.*?</w:ins>", re.S)
RE_DEL = re.compile(rb"<w:del(?:\s[^>]*)?>(.*?)</w:del>", re.S)


# ------------------------------------------------------- as duas visoes

def visao_recusada(bloco):
    """O paragrafo como ficaria se o autor recusasse tudo.

    E a conferencia que importa: se recusar tudo nao devolve o original, o
    programa estragou texto que ninguem mandou mexer."""
    b = RE_INS.sub(b"", bloco)
    b = RE_DEL.sub(lambda m: m.group(1), b)
    return b.replace(b"<w:delText", b"<w:t").replace(b"</w:delText>", b"</w:t>")


# ------------------------------------------------------- achar e trocar

def alvo(bloco, frase):
    """Onde o reparo morde: (texto, mapa, atomos, inicio, fim) ou (None, razao).

    `frase=None` enderaca o paragrafo inteiro. O fim recua sobre o espaco final,
    porque trocar o espaco junto com a frase junta duas palavras na hora em que
    o autor aceita."""
    texto, mapa, ats = R.fluxo(bloco)
    if not texto.strip():
        return None, "o parágrafo não tem texto"
    if frase is None:
        ini, fim = 0, len(texto)
    else:
        fs = R.frases(texto)
        if not (1 <= frase <= len(fs)):
            return None, ("o parágrafo tem %d frase(s), e o reparo pediu a %d"
                          % (len(fs), frase))
        ini, fim = fs[frase - 1]
    ini, fim = R.limites(texto, ini, fim)
    return (texto, mapa, ats, ini, fim), None


def trocar(bloco, ats, k0, k1, ini, fim, novo, autor, ident, comentario=None):
    """Reescreve os runs que o alvo toca, marcando exclusao e insercao.

    So os runs tocados sao reconstruidos, e o que esta entre eles (marca do
    corretor ortografico, marcador de posicao) passa intacto. O run volta com
    a mesma tag de abertura e o mesmo <w:rPr>, de modo que a formatacao e a
    mesma; cai so o `lastRenderedPageBreak`, que o Word regrava ao paginar.

    `comentario` ancora a razao da troca no proprio trecho trocado, e nao no
    paragrafo. A marca de revisao do Word carrega autor e data, e nao carrega o
    codigo do item nem por que ele mudou; sem isso o autor aceita sem ler, que
    e o modo de falhar que a doutrina do corretor nomeia."""
    marca = 'w:id="%%d" w:author="%s" w:date="%s"' % (R.esc(autor), DATA)
    off = sum(len(a.texto) for a in ats[:k0])
    pedacos = []
    if comentario:
        pedacos.append(('<w:commentRangeStart w:id="%d"/>' % comentario[0]).encode())
    for k in range(k0, k1 + 1):
        a = ats[k]
        abre = bloco[a.ini:bloco.index(b">", a.ini) + 1]
        m = R.RE_RPR.search(bloco[a.ini:a.fim])
        rpr = m.group(0) if m else b""
        la = max(0, ini - off)
        lb = min(len(a.texto), fim - off)
        off += len(a.texto)

        def run(tag, s):
            return (abre + rpr + ('<w:%s xml:space="preserve">%s</w:%s></w:r>'
                                  % (tag, R.esc(s), tag)).encode())
        if la > 0:
            pedacos.append(run("t", a.texto[:la]))
        if lb > la:
            pedacos.append(("<w:del %s>" % (marca % next(ident))).encode()
                           + run("delText", a.texto[la:lb]) + b"</w:del>")
        if k == k1 and novo:
            pedacos.append(("<w:ins %s>" % (marca % next(ident))).encode()
                           + run("t", novo) + b"</w:ins>")
        if k == k1 and comentario:
            pedacos.append(('<w:commentRangeEnd w:id="%d"/><w:r>'
                            '<w:commentReference w:id="%d"/></w:r>'
                            % (comentario[0], comentario[0])).encode())
        if lb < len(a.texto):
            pedacos.append(run("t", a.texto[lb:]))
        if k < k1:
            pedacos.append(bloco[a.fim:ats[k + 1].ini])
    return bloco[:ats[k0].ini] + b"".join(pedacos) + bloco[ats[k1].fim:]


# ------------------------------------------------------- a folha de trabalho

def folha(a, doc, sp, pars):
    lista = itens(a.lista)
    if not lista:
        sys.exit("nenhum item com localizador na lista: não há o que endereçar.")
    secoes = mapa_secoes(pars)

    def resolve(n):
        if not (1 <= n <= len(sp)) or sp[n - 1][2]:
            return None
        texto, mapa, ats = R.fluxo(doc[sp[n - 1][0]:sp[n - 1][1]])
        return texto, lambda x, y: R.cabe_num_segmento(mapa, ats, x, y)[0]

    dest = Path(a.saida) if a.saida else Path(a.lista).with_name(
        "FRASES-" + Path(a.trabalho).stem + ".md")
    total, aptas = R.escrever_folha(
        dest, Path(a.trabalho).name, "aplicar_docx.py",
        "atravessa itálico, nota de rodapé, campo ou tabulação",
        lista, resolve, lambda t: sem_localizador(t, secoes))
    print("  %s: %d frases endereçáveis, %d delas aplicáveis (%.0f%%)"
          % (dest.name, total, aptas, 100.0 * aptas / max(total, 1)))
    return 0


# ------------------------------------------------------------------ aplicar

def paragrafos_do_arquivo(caminho):
    """Texto de cada paragrafo, por varredura com profundidade.

    Regex ingenua de `<w:p>` quebra em caixa de texto, onde ha paragrafo dentro
    de paragrafo, e ja produziu acusacao falsa em 30/08/2026."""
    with zipfile.ZipFile(caminho) as z:
        doc = z.read("word/document.xml")
    saida, i, n = [], 0, len(doc)
    abre = re.compile(rb"<w:p(?: [^>]*)?>")
    while True:
        m = abre.search(doc, i)
        if not m:
            break
        prof, j = 1, m.end()
        while prof and j < n:
            f = doc.find(b"</w:p>", j)
            if f == -1:
                break
            a1, a2 = doc.find(b"<w:p ", j), doc.find(b"<w:p>", j)
            prox = min(x for x in (a1, a2, n) if x != -1)
            if prox < f:
                prof, j = prof + 1, prox + 4
            else:
                prof, j = prof - 1, f + 6
        b = doc[m.start():j]
        txt = b"".join(re.findall(rb"<w:t[^>]*>(.*?)</w:t>", b, re.S))
        saida.append(" ".join(re.sub(rb"<[^>]+>", b"", txt).decode("utf-8", "replace").split()))
        i = m.end()
    return saida


def conferir_no_word(original, corrigido):
    """Recusa tudo no Word e exige o original de volta; aceita tudo e exige o
    mesmo numero de paragrafos.

    E a conferencia que as duas do XML nao alcancam, porque elas testam o nosso
    modelo do aceite e nao o aceite. Sem Word instalado, avisa e segue: o
    programa nao depende dela para gravar, e dizer que nao conferiu vale mais do
    que fingir que conferiu."""
    try:
        import win32com.client.dynamic
    except ImportError:
        print("  a conferencia pelo Word nao rodou: falta o pywin32.")
        return None
    try:
        w = win32com.client.dynamic.Dispatch("Word.Application")
    except Exception as e:
        print("  a conferencia pelo Word nao rodou: %s" % e)
        return None
    w.Visible = False
    w.DisplayAlerts = False
    provas = []
    try:
        for nome, acao in (("recusa", "reject"), ("aceite", "accept")):
            alvo = corrigido.with_name(corrigido.stem + "-prova-" + nome + ".docx")
            d = w.Documents.Open(str(corrigido.resolve()), ReadOnly=False,
                                 AddToRecentFiles=False)
            if acao == "reject":
                d.Revisions.RejectAll()
            else:
                d.Revisions.AcceptAll()
            d.SaveAs2(str(alvo.resolve()), FileFormat=16)
            d.Close(False)
            provas.append((nome, alvo))
    finally:
        w.Quit()

    orig = paragrafos_do_arquivo(original)
    ok = True
    for nome, alvo in provas:
        obtido = paragrafos_do_arquivo(alvo)
        if nome == "recusa":
            bate = obtido == orig
            print("  Word, recusando tudo: %s (%d parágrafos contra %d)"
                  % ("volta ao original" if bate else "NAO VOLTA AO ORIGINAL",
                     len(obtido), len(orig)))
        else:
            bate = len(obtido) == len(orig)
            print("  Word, aceitando tudo: %s (%d parágrafos contra %d)"
                  % ("nenhum parágrafo se fundiu" if bate
                     else "PARAGRAFOS SE FUNDIRAM", len(obtido), len(orig)))
        if bate:
            alvo.unlink(missing_ok=True)
        else:
            ok = False
            print("     a prova ficou em %s" % alvo.name)
    return ok


def main():
    # O console do Windows abre em cp1252, e um til na mensagem derrubava o
    # programa depois de ele ja ter gravado. A guarda existe porque o teste do
    # conferidor chama main() com a saida desviada, e desvio nao reconfigura.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(
        description="Reparos como alterações controladas do Word.")
    ap.add_argument("trabalho")
    ap.add_argument("arquivo", help="os reparos; com --frases, a ENTREGA-CORRETOR-*.md")
    ap.add_argument("--frases", action="store_true",
                    help="não aplica nada: escreve a folha de frases endereçáveis")
    ap.add_argument("--lista", help="ENTREGA-CORRETOR-*.md, para comentar os itens sem reparo")
    ap.add_argument("--saida")
    ap.add_argument("--autor", default=AUTOR)
    ap.add_argument("--sem-word", action="store_true",
                    help="não confere o resultado abrindo no Word (não recomendado)")
    a = ap.parse_args()
    a.lista = a.arquivo if a.frases else a.lista

    if not a.trabalho.lower().endswith(".docx"):
        sys.exit("só funciona com .docx: um PDF não tem onde guardar revisão.")

    # ---- a trava herdada: as duas numeracoes precisam bater
    partes = load(a.trabalho)
    pars = collect_paragraphs(partes["word/document.xml"].find(W + "body"),
                              Styles(partes["word/styles.xml"]))
    z = zipfile.ZipFile(a.trabalho)
    doc = z.read("word/document.xml")
    sp = spans(doc)
    if len(sp) != len(pars):
        sys.exit("as duas contagens de parágrafo não batem (%d por XML, %d pelo "
                 "extrator).\nAplicar assim trocaria texto no parágrafo errado. "
                 "Nada foi gravado." % (len(sp), len(pars)))

    if a.frases:
        return folha(a, doc, sp, pars)

    lista = R.ler_reparos(a.arquivo)
    if not lista:
        sys.exit("nenhum bloco de reparo neste arquivo: ele precisa de **Está:** e **Fica:**.")

    # ---- decide um a um, sem gravar nada ainda
    plano, recusas = {}, []
    for r in lista:
        def recusa(razao):
            recusas.append((r, razao))
        if r.erro:
            recusa(r.erro)
            continue
        if not (1 <= r.par <= len(sp)) or sp[r.par - 1][2]:
            recusa("o parágrafo [P%d] não existe neste documento" % r.par)
            continue
        bloco = doc[sp[r.par - 1][0]:sp[r.par - 1][1]]
        achado, razao = alvo(bloco, r.frase)
        if achado is None:
            recusa(razao)
            continue
        texto, mapa, ats, ini, fim = achado
        if texto[ini:fim] == r.novo:
            recusa("o texto proposto é igual ao que já está lá")
            continue
        if not r.novo:
            # Retirar a frase sem levar junto um dos espacos que a cercavam
            # deixa dois espacos no lugar dela, e o autor so ve isso depois de
            # aceitar. O espaco sai com a frase, e de um lado so.
            antes = fim
            while fim < len(texto) and texto[fim] == " ":
                fim += 1
            if fim == antes:
                while ini > 0 and texto[ini - 1] == " ":
                    ini -= 1
        ok, info = R.cabe_num_segmento(mapa, ats, ini, fim)
        if not ok:
            recusa(info)
            continue
        conflito = next((p for p in plano.get(r.par, [])
                         if not (fim <= p[0] or ini >= p[1])), None)
        if conflito:
            recusa("o trecho se sobrepõe ao do reparo %s, no mesmo parágrafo"
                   % conflito[4].codigo)
            continue
        plano.setdefault(r.par, []).append((ini, fim, info[0], info[-1], r))

    # ---- aplica de tras para diante, para os deslocamentos nao andarem
    #
    # Revisao e comentario tiram o numero do mesmo saco. O esquema os trata como
    # espacos distintos, mas o Word os numera junto, e um arquivo em que a
    # exclusao 1 convive com o comentario 1 e desnecessariamente ambiguo.
    tem, com_xml, usados, prox = comentarios_existentes(z)
    ident = iter(range(prox, 10 ** 6))
    esperado, justificativas = {}, []
    saida, pos = [], 0
    for n in sorted(plano):
        ini_p, fim_p, _ = sp[n - 1]
        bloco = doc[ini_p:fim_p]
        texto = R.fluxo(bloco)[0]
        novo_texto = texto
        for ini, fim, k0, k1, r in sorted(plano[n], key=lambda t: -t[0]):
            ats = R.fluxo(bloco)[2]
            just = (next(ident), "[%s] %s" % (r.codigo, r.muda or
                    "alteração proposta pela correção automática."))
            justificativas.append(just)
            bloco = trocar(bloco, ats, k0, k1, ini, fim, r.novo, a.autor, ident,
                           just)
            novo_texto = novo_texto[:ini] + r.novo + novo_texto[fim:]
        esperado[n] = novo_texto
        saida.append(doc[pos:ini_p])
        saida.append(bloco)
        pos = fim_p
    saida.append(doc[pos:])
    doc_novo = b"".join(saida)

    # ---- conferir antes de gravar, e conferir contra o arquivo, nao contra a
    # intencao: o que se compara e o texto que sai do XML novo
    sp2 = spans(doc_novo)
    problemas = []
    if len(sp2) != len(sp):
        problemas.append("a contagem de parágrafos mudou (%d → %d)"
                         % (len(sp), len(sp2)))
    else:
        for i in range(len(sp)):
            velho = R.fluxo(doc[sp[i][0]:sp[i][1]])[0]
            bloco = doc_novo[sp2[i][0]:sp2[i][1]]
            if R.fluxo(visao_recusada(bloco))[0] != velho:
                problemas.append("recusando tudo, o parágrafo [P%d] não volta ao "
                                 "original" % (i + 1))
            if R.fluxo(bloco)[0] != esperado.get(i + 1, velho):
                problemas.append("aceitando tudo, o parágrafo [P%d] não dá o texto "
                                 "pedido" % (i + 1))
    if problemas:
        print("A conferência reprovou. Nada foi gravado.")
        for p in problemas[:20]:
            print("  - %s" % p)
        if len(problemas) > 20:
            print("  - e mais %d." % (len(problemas) - 20))
        return 1

    # ---- o que nao virou alteracao vira comentario, com a proposta dentro
    por_par, sem_ancora = {}, []
    for r, razao in recusas:
        texto = "[%s] não aplicado: %s." % (r.codigo, razao)
        if r.novo:
            texto += ' Proposta: "%s"' % r.novo
        elif not r.erro:
            texto += " A proposta é retirar o trecho."
        if r.par and 1 <= r.par <= len(sp) and not sp[r.par - 1][2]:
            por_par.setdefault(r.par, []).append(texto)
        else:
            sem_ancora.append(r.codigo)

    if a.lista:
        # Um arquivo so para o autor: os itens que nao geraram reparo continuam
        # visiveis na margem, em vez de ficarem num segundo documento.
        secoes = mapa_secoes(pars)
        feitos = {r.codigo for ns in plano.values() for *_, r in ns}
        feitos |= {r.codigo for r, _ in recusas}
        for cod, aponta, locs in itens(a.lista):
            if cod in feitos:
                continue
            alvo_n = next((n for n in locs if 1 <= n <= len(sp) and not sp[n - 1][2]), None)
            if alvo_n:
                por_par.setdefault(alvo_n, []).append(
                    "[%s] %s" % (cod, sem_localizador(aponta, secoes)))

    doc_novo, novos = ancorar(doc_novo, spans(doc_novo), por_par, next(ident))
    # As justificativas ja tem a ancora dentro do proprio trecho trocado; aqui
    # so entra o corpo delas, junto com o dos comentarios de margem.
    novos = sorted(justificativas + novos)

    dest = Path(a.saida) if a.saida else Path(a.trabalho).with_name(
        "ENTREGA-CORRIGIDO-" + Path(a.trabalho).stem + ".docx")
    escrever(z, doc_novo, novos, dest, a.autor, tem, com_xml)

    trocas = sum(len(v) for v in plano.values())
    print("  %s: %d alteração(ões) controlada(s) em %d parágrafo(s), %d comentário(s)%s"
          % (dest.name, trocas, len(plano), len(novos),
             ", %d do autor preservados" % len(usados) if usados else ""))
    print("  conferido: recusando tudo volta ao original; aceitando tudo dá o texto pedido.")
    if not a.sem_word:
        conferir_no_word(Path(a.trabalho), dest)
    if recusas:
        rec = dest.with_name(dest.stem + "-RECUSAS.md")
        L = ["# Reparos não aplicados — %s" % Path(a.trabalho).name, "",
             "Cada um destes está também como comentário na margem do arquivo "
             "corrigido.", "Aqui ficam juntos, porque quem faz à mão precisa da "
             "lista, e não do arquivo.", ""]
        for r, razao in recusas:
            L.append("## %s (linha %s de %s)" % (r.codigo, r.linha, Path(a.arquivo).name))
            L.append("")
            L.append("**Endereço:** %s" % (("[P%d]" % r.par) + ("F%d" % r.frase if r.frase else "")
                                           if r.par else "(não resolvido)"))
            L.append("")
            L.append("**Por que não entrou:** %s" % razao)
            L.append("")
            if r.novo:
                L.append("**Proposta:** %s" % r.novo)
                L.append("")
        rec.write_text("\n".join(L) + "\n", encoding="utf-8")
        print("  %s: %d reparo(s) para fazer à mão" % (rec.name, len(recusas)))
    if sem_ancora:
        print("  sem âncora, e por isso só no arquivo de recusas: %s"
              % ", ".join(sem_ancora))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Casa o bloco de itens com a prosa do relatorio e acusa a diferenca.

POR QUE ISTO EXISTE

Em 06/09/2026 a lista de itens deixou de ser reconstruida da prosa e passou a ser
lida de `<relatorio>.itens.json`, que a propria leitura grava. A mudanca existe
para acabar com a perda silenciosa de item: sete defeitos do leitor de prosa,
achados num dia, tinham a mesma forma, a contagem certa e o conteudo faltando.

**Na primeira leitura que usou o caminho novo, ele perdeu um item.** O relatorio
trazia SC24 na prosa e o bloco trazia 59 dos 60. Quem achou foi uma revisao
humana, lendo. Sem este programa, o caminho novo nao e mais seguro que o antigo:
e so mais silencioso, porque o leitor de prosa ao menos deixava o rastro do item
malformado.

O QUE ELE DECIDE

    codigo so na prosa   ACUSA. O item existe e nao chega a margem.
    codigo so no bloco   ACUSA. O bloco promete item que a prosa nao demonstra.
    titulo divergente    AVISA. As primeiras palavras nao se parecem, e uma das
                         duas versoes esta velha.

Nao le o conteudo do item e nao julga se ele esta certo. Decide se as duas
escritas do mesmo relatorio falam dos mesmos itens.

Uso:
    python scripts/conferir_bloco.py <relatorio.md>
    python scripts/conferir_bloco.py <relatorio.md> --bloco outro.json
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# As tres escritas de codigo que o acervo usa, e elas convivem no mesmo arquivo:
# titulo (`### S12. ...`), negrito abrindo linha (`**SC7.** ...`) e negrito depois
# de ponto final, que e como um dos assistentes agrupa itens de acabamento.
RE_TITULO = re.compile(r"^#{2,5}[ \t]*\**[ \t]*([A-Z]{1,2}\d+)\b[.,:—–·|\-]?[ \t]*(.*)$", re.M)
# O item pode abrir uma linha de lista (`- **S19.** ...`), que e como a lista de
# pequenas correcoes do Luis sai desde 10/09/2026. Em 13/09 o leitor perdia todos
# os itens dessa lista e o relatorio saia com 25 codigos em 44. O marcador de lista
# (traco, mais, ou numero com ponto) entra como prefixo opcional; o asterisco de
# lista fica de fora, porque colide com o negrito.
RE_NEGRITO = re.compile(
    r"(?:^[ \t]*(?:[-+]|\d+[.)])?[ \t]*|(?<=[.!?])[ \t]+)"
    r"\*\*([A-Z]{1,2}\d+)[.,:]?\*\*[ \t]*([^\n]{0,90})", re.M)

# E a forma em que o codigo e o titulo estao DENTRO do mesmo negrito:
#     **C1 - Os dados contradizem Godoy e Araujo (2022).**
# Sem ela, os itens de contribuicao de tres relatorios do acervo apareciam como
# "so no bloco", que e acusacao falsa: eles estao na prosa, com outra pontuacao.
# O titulo atravessa a quebra de linha em tres relatorios do acervo, porque o
# editor quebra em 88 colunas. Sem admitir UMA quebra, quatro itens de
# contribuicao apareciam como "so no bloco", que e acusacao falsa.
# O titulo dentro do negrito passava de 120 caracteres em quatro contribuicoes
# de um relatorio de 13/09/2026, e as quatro sumiam. O teto sobe a 240 por linha
# e o titulo pode atravessar ate duas quebras, que e o que um titulo de tres
# linhas a 88 colunas pede. O marcador de lista entra como no RE_NEGRITO.
RE_NEGRITO_JUNTO = re.compile(
    r"(?:^[ \t]*(?:[-+]|\d+[.)])?[ \t]*|(?<=[.!?])[ \t]+)"
    r"\*\*([A-Z]{1,2}\d+)[ \t]*[.,:\u2014\u2013\u00b7|\-]+[ \t]*"
    r"([^*\n]{3,240}(?:\n[^*\n]{1,240}){0,2})\*\*", re.M)

# E o parentese que fecha o negrito: `**C1 (pede uma conta).**` e como um
# relatorio de 06/09/2026 abre os quatro itens de uma secao, e os quatro sumiam.
# So nesta forma estrita, no comeco da linha e com nada entre o parentese e o fim
# do negrito: na classe geral de separadores ele lia `**F2 (1.274) contra F6**`
# e `**S5 (quanto a [P439]) CONFERE.**`, que sao remissao e veredito.
RE_NEGRITO_PARENTESE = re.compile(
    r"^[ \t]*\*\*([A-Z]{1,2}\d+)[ \t]+\(([^()\n]{1,80})\)[.:]?\*\*", re.M)


# Os prefixos que viram comentario de margem, e sao os mesmos de lista_corretor.py.
# A distincao importa porque o item de contribuicao, o de forca e a questao em
# aberto nunca vao a margem: quando eles faltam no bloco, o relatorio entregue
# nao perde nada, e dizer "nao chega a margem" seria falso.
# `P` e o prefixo da leitura 2 do Luis desde 10/09/2026, e faltava aqui e em
# lista_corretor.py: item P que chegasse ao relatorio final nao iria a margem.
# Ate 14/09/2026 nenhum relatorio entregue trazia P (a redacao renumera em S), de
# modo que o defeito nunca se materializou; a entrada e preventiva e vale para o
# dia em que a redacao conservar o prefixo, como a ficha de 10/09 manda.
EXECUTAVEIS = ("S", "D", "SC", "A", "P")


def executavel(codigo):
    letras = re.match(r"[A-Z]+", codigo)
    return bool(letras) and letras.group(0) in EXECUTAVEIS


def normal(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def da_prosa(caminho):
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    fora = {}
    for rx in (RE_TITULO, RE_NEGRITO, RE_NEGRITO_JUNTO, RE_NEGRITO_PARENTESE):
        for m in rx.finditer(t):
            cod, tit = m.group(1), " ".join(m.group(2).split())
            # o titulo mais longo ganha: o mesmo codigo pode aparecer numa lista
            # de remissoes, com titulo curto ou vazio, e no item de verdade. Mas o
            # codigo entra mesmo sem titulo: `## S1` sozinho na linha e item, e em
            # 12/09/2026 a comparacao `"" > ""` fazia sumir 23 itens S de um
            # relatorio, que saia com 17 codigos em 48. O preco: codigo que so
            # aparece numa remissao em negrito entra como item, e o conferidor o
            # acusa como falta no bloco, o que se ve.
            if cod not in fora or len(tit) > len(fora[cod]):
                fora[cod] = tit
    return fora


def do_bloco(caminho):
    dados = json.loads(io.open(caminho, encoding="utf-8", errors="replace").read())
    return {str(d.get("codigo", "")).strip(): " ".join(str(d.get("titulo", "")).split())
            for d in dados if isinstance(d, dict)}


def parecidos(a, b, minimo=3):
    """As primeiras palavras coincidem? Compara conjunto, nao ordem."""
    pa, pb = set(normal(a)[:12]), set(normal(b)[:12])
    if not pa or not pb:
        return True
    return len(pa & pb) >= min(minimo, len(pa), len(pb))


def autoteste():
    falhas = []
    prosa = da_prosa.__doc__  # so para nao falhar se alguem apagar a funcao
    if not parecidos("O denominador some no paragrafo seguinte",
                     "O denominador some no paragrafo seguinte"):
        falhas.append("nao reconhece titulo identico")
    if parecidos("O denominador some no paragrafo seguinte",
                 "As figuras nao trazem legenda nenhuma"):
        falhas.append("acha parecido o que e diferente")
    if not parecidos("O denominador declarado some no paragrafo seguinte",
                     "O denominador some no paragrafo seguinte, e nao volta"):
        falhas.append("acusa divergencia onde houve so reescrita da frase")
    # as tres escritas de codigo tem de ser reconhecidas, e a terceira foi a que
    # produziu vinte e seis acusacoes falsas em tres relatorios do acervo
    import tempfile
    longo = ("Um titulo de contribuicao que atravessa tres linhas porque o editor "
             "quebra em oitenta e oito colunas e o texto passa de cento e vinte")
    exemplo = (u"### S1 - Um titulo de correcao\n\n"
               u"**C1 - Os dados contradizem uma fonte no ponto que motivou a parte.**\n\n"
               u"**D4. Uma conta que esta nos numeros de [P440]\n"
               u"e nunca foi feita.**\n\n"
               u"**SC7.** Uma gralha em [P485].\n\n"
               u"## S9\n\nO titulo deste veio na linha de baixo.\n\n"
               u"**C5 (pede uma conta).** A tabela traz os dois fluxos.\n\n"
               u"**F8 (1.274) contra F9 no mesmo ponto.**\n\n"
               u"**S8 (quanto a [P439]) CONFERE.**\n\n"
               # os dois casos de 13/09/2026: item em linha de lista, e titulo longo
               u"- **S19.** Uma gralha em [P12], em lista.\n"
               u"- **S20.** Outra, em [P13].\n\n"
               u"**C9 - " + longo[:88] + "\n" + longo[88:] + " caracteres.**\n")
    p = Path(tempfile.gettempdir()) / "_bloco_autoteste.md"
    p.write_text(exemplo, encoding="utf-8")
    try:
        achados = da_prosa(str(p))
        for c in ("S1", "C1", "D4", "SC7", "S9", "C5", "S19", "S20", "C9"):
            if c not in achados:
                falhas.append("nao reconhece a escrita de %s: %r" % (c, sorted(achados)))
        if "caracteres" not in achados.get("C9", ""):
            falhas.append("perde o titulo longo em negrito: %r" % achados.get("C9"))
        # CONTROLE NEGATIVO: remissao e veredito com parentese nao sao item
        for c in ("F8", "S8"):
            if c in achados:
                falhas.append("toma por item o negrito com parentese de %s" % c)
        if not achados.get("C1", "").startswith("Os dados"):
            falhas.append("nao le o titulo de dentro do negrito: %r" % achados.get("C1"))
        if "nunca foi feita" not in achados.get("D4", ""):
            falhas.append("perde o titulo que atravessa a quebra de linha: %r"
                          % achados.get("D4"))
    finally:
        try:
            p.unlink()
        except Exception:
            pass
    return falhas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio")
    ap.add_argument("--bloco", help="padrão: <relatorio sem extensão>.itens.json")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o proprio conferidor esta quebrado, e nao reporto nada:")
        for x in f:
            print("    %s" % x)
        return 2
    print("  autoteste: reconhece titulo igual, aceita reescrita da frase e nao "
          "confunde titulos diferentes")

    rel = Path(a.relatorio)
    bloco = Path(a.bloco) if a.bloco else Path(str(rel.with_suffix("")) + ".itens.json")
    if not bloco.exists():
        print("\n  %s nao existe. Sem bloco, a lista sai da prosa, e este "
              "conferidor nao tem o que casar." % bloco.name)
        return 2

    p, b = da_prosa(str(rel)), do_bloco(str(bloco))
    faltam = sorted(set(p) - set(b))
    so_prosa = [c for c in faltam if executavel(c)]
    fora_da_margem = [c for c in faltam if not executavel(c)]
    so_bloco = sorted(set(b) - set(p))
    difs = [(c, p[c], b[c]) for c in sorted(set(p) & set(b))
            if p[c] and b[c] and not parecidos(p[c], b[c])]

    print("\n  %s: %d códigos na prosa, %d no bloco" % (rel.name, len(p), len(b)))
    if so_prosa:
        print("\n  SÓ NA PROSA (o item existe e não chega à margem): %d" % len(so_prosa))
        for c in so_prosa:
            print("     %-6s %s" % (c, p[c][:78]))
    if so_bloco:
        print("\n  SÓ NO BLOCO (promete item que a prosa não demonstra): %d" % len(so_bloco))
        for c in so_bloco:
            print("     %-6s %s" % (c, b[c][:78]))
    if fora_da_margem:
        print("\n  FORA DO BLOCO, e não vão à margem (aviso; o prompt pede todos): %d"
              % len(fora_da_margem))
        print("     %s" % ", ".join(fora_da_margem))
    if difs:
        print("\n  TÍTULO DIVERGENTE (aviso; uma das duas versões está velha): %d" % len(difs))
        for c, x, y in difs[:12]:
            print("     %-6s prosa: %s" % (c, x[:66]))
            print("            bloco: %s" % y[:66])

    if not (so_prosa or so_bloco):
        print("\n  os dois falam dos mesmos itens.")
    else:
        print("\n  Corrija no relatório e gere o bloco de novo. Item que existe numa")
        print("  escrita e não na outra chega ou não chega à margem por acidente.")
    return 1 if (so_prosa or so_bloco) else 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Poe cada localizador do relatorio ao lado do paragrafo que ele aponta, numa saida so.

POR QUE ISTO EXISTE

Medido em 07 e 08/09/2026. Conferir os enderecos de um relatorio abrindo um
paragrafo de cada vez custou 18 minutos e 55 chamadas para 126 afirmacoes, e foi
a operacao mais cara do dia: mais cara do que a leitura inteira que produziu o
relatorio, que levou 12 minutos e 7 chamadas.

A mesma forma de desperdicio ja foi corrigida duas vezes nesta oficina, e as duas
por lote: 81 buscas de ausencia couberam em 4 chamadas do `buscar_lote.py`, e 31
leituras de figura couberam numa mensagem. **O endereco era a massa que sobrava**,
e ela e a maior: num relatorio medido, 76% dos localizadores estao nos itens de
correcao, que sao os que nao se pode deixar de conferir.

O QUE ELE FAZ, e o que ele NAO faz

Ele monta o par: o texto do item, e o texto de cada paragrafo que o item cita.
Quem le julga se esta la o que o item diz que esta.

**Ele nao julga nada.** Nao decide se o item esta certo, nao compara sentido, nao
mede parecenca. O unico veredito dele e mecanico:

    LOCALIZADOR MORTO   o [P###] citado nao existe na extracao. E erro certo,
                        porque nenhum julgamento e preciso para constata-lo.

O RISCO, e ele vai declarado porque muda o que a saida vale

Ler o paragrafo colado ao lado nao e a mesma coisa que abrir o trabalho. A saida
traz o paragrafo inteiro, e nao um trecho escolhido, justamente para que a
conferencia nao herde o recorte de quem escreveu o item. Ainda assim, quem confere
por aqui ve o que o localizador aponta e nao ve a vizinhanca: para o item que
depende do que vem antes ou depois, o `--vizinhos` traz os adjacentes.

Uso:
    python scripts/enderecos_em_lote.py <relatorio.md> <extracao.txt>
    python scripts/enderecos_em_lote.py <relatorio.md> <extracao.txt> --vizinhos 1
    python scripts/enderecos_em_lote.py <relatorio.md> <extracao.txt> --so S,SC
"""
import argparse
import io
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# As escritas de item que o acervo usa: titulo, negrito abrindo linha, e codigo e
# titulo dentro do mesmo negrito. As tres convivem no mesmo relatorio.
RE_ITEM = re.compile(
    r"(?m)^(?:#{2,5}[ \t]*\**[ \t]*|\*\*)([A-Z]{1,2}\d+)\b[.,:—–·|\-]?[ \t]*([^\n]{0,110})")

# As tres escritas de localizador. A faixa por extenso ("de [P380] a [P516]") vira
# os dois extremos, e nao os quinhentos do meio: quem confere abre as pontas.
RE_LOC = re.compile(r"\[?\bP(\d+)\]?")
RE_FAIXA = re.compile(r"\bde[ \t]+\[?P(\d+)\]?[ \t]+a[ \t]+\[?P(\d+)\]?")


def paragrafos(caminho):
    """Le as duas escritas de extracao, e le TAMBEM o bloco de notas do fim."""
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    fora = {}
    # `\W{0,4}` não alcança `#### ` (quatro cerquilhas mais o espaço), e os títulos
    # de seção da extração vêm assim. Medido em 08/09/2026: três parágrafos foram
    # dados como localizador morto por isso, que é acusação falsa do próprio
    # conferidor. É o defeito de ambiente que os prompts já registram.
    for m in re.finditer(r"(?m)^[^\[\n]{0,10}\[P(\d+)\]\s*(.*)$", t):
        fora[int(m.group(1))] = " ".join(m.group(2).split())
    if not fora:
        for m in re.finditer(
                r"(?m)^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\])?\s*(?:\(p\.[^)]*\))?\s*(.*)$", t):
            fora[int(m.group(1))] = " ".join(m.group(2).split())
    notas = {}
    for m in re.finditer(r"(?m)^\W{0,4}\[nota (\d+)\]\s*(.*)$", t):
        notas[int(m.group(1))] = " ".join(m.group(2).split())
    return fora, notas


def itens(caminho):
    """Devolve [(codigo, titulo, corpo)], com o corpo indo ate o item seguinte."""
    t = io.open(caminho, encoding="utf-8", errors="replace").read()
    marcas = [(m.start(), m.group(1), " ".join(m.group(2).split()))
              for m in RE_ITEM.finditer(t)]
    # o mesmo codigo pode aparecer numa remissao; fica a primeira ocorrencia de cada
    vistos, limpo = set(), []
    for pos, cod, tit in marcas:
        if cod in vistos:
            continue
        vistos.add(cod)
        limpo.append((pos, cod, tit))
    # A FRONTEIRA E O PROXIMO ITEM **OU O PROXIMO CABECALHO**, o que vier antes.
    # Sem o cabecalho, o ultimo item de uma secao engole a prosa que vem depois
    # dela e os localizadores dessa prosa. Medido em 08/09/2026, no relatorio do
    # Luis sobre o trabalho R: `C17` ficou com 5.415 caracteres e 20 localizadores,
    # tendo absorvido a secao 3.1 inteira. Quem achou foi a conferencia, ao notar
    # que o indice cruzado atribuia a C17 paragrafos que nao sao dele.
    cabecalhos = [m.start() for m in re.finditer(r"(?m)^#{1,5}[ \t]", t)]
    fora = []
    for i, (pos, cod, tit) in enumerate(limpo):
        fim = limpo[i + 1][0] if i + 1 < len(limpo) else len(t)
        seguintes = [c for c in cabecalhos if pos < c < fim]
        if seguintes:
            fim = seguintes[0]
        fora.append((cod, tit, t[pos:fim]))
    return fora


def localizadores(corpo):
    """Os [P###] do corpo, na ordem, sem repetir. A faixa entra pelos dois extremos."""
    fora = []
    for m in RE_FAIXA.finditer(corpo):
        for n in (int(m.group(1)), int(m.group(2))):
            if n not in fora:
                fora.append(n)
    for m in RE_LOC.finditer(corpo):
        n = int(m.group(1))
        if n not in fora:
            fora.append(n)
    return fora


def autoteste():
    """Prova o extrator antes de usa-lo. Sem controle, o silencio dele nao informa."""
    import tempfile
    falhas = []
    rel = ("### S1. Um titulo de correcao\n\nAponta [P751] e o contradiz [P763].\n\n"
           "**C1 — Uma contribuicao.** Está em P775 e na faixa de [P780] a [P790].\n\n"
           "**SC7.** Gralha em [P999].\n")
    ext = ("#### [P751] Sob cabecalho de secao, e ja foi dado como morto por isso.\n\n"
           "[P763] Texto do segundo.\n\n[P775] Texto do terceiro.\n\n"
           "[P780] Comeco da faixa.\n\n[P790] Fim da faixa.\n\n"
           "[nota 12] Cf. Nino, 2003.\n")
    d = Path(tempfile.gettempdir())
    (d / "_end_rel.md").write_text(rel, encoding="utf-8")
    (d / "_end_ext.txt").write_text(ext, encoding="utf-8")
    try:
        ps, nt = paragrafos(str(d / "_end_ext.txt"))
        it = itens(str(d / "_end_rel.md"))
        cods = [c for c, _, _ in it]
        if cods != ["S1", "C1", "SC7"]:
            falhas.append("nao reconhece as tres escritas de item: %r" % cods)
        por = {c: localizadores(b) for c, _, b in it}
        if por.get("S1") != [751, 763]:
            falhas.append("perde localizador entre colchetes: %r" % por.get("S1"))
        # o localizador sem colchete e a faixa por extenso: as duas ja custaram item
        if por.get("C1") != [780, 790, 775]:
            falhas.append("nao le o localizador sem colchete ou a faixa: %r" % por.get("C1"))
        if -12 in ps or 12 not in nt:
            falhas.append("confunde nota de rodape com paragrafo")
        # CONTROLE POSITIVO do unico veredito: o localizador morto tem de ser visto
        # o paragrafo sob cabecalho tem de ser lido: tres localizadores mortos
        # falsos sairam daqui em 08/09/2026
        if 751 not in ps:
            falhas.append("perde o paragrafo cuja linha abre por cerquilhas")
        if 999 in ps:
            falhas.append("a extracao de teste esta errada")
        if por.get("SC7") != [999]:
            falhas.append("nao ve o localizador que nao existe: %r" % por.get("SC7"))
    finally:
        for n in ("_end_rel.md", "_end_ext.txt"):
            try:
                (d / n).unlink()
            except Exception:
                pass
    return falhas


def modo_tudo(a, ps, notas, lista, classes):
    """O trabalho inteiro uma vez, e um índice cruzado no lugar do pareamento.

    Medido em 08/09/2026, sobre o mesmo capítulo e o mesmo relatório: o pareamento
    imprime cada parágrafo uma vez por item que o cita, e 48 itens citaram 177
    localizadores sobre 56 parágrafos. Daí a duplicação, e daí os números:

        pareado, só o parágrafo citado          23.147 palavras
        pareado, com n-1 e n+1                  42.870
        pareado, com n-2 e n+2                  55.265
        o trabalho inteiro mais o relatório     12.217

    **Carregar tudo custa metade do pareamento e um quinto da versão com
    vizinhos**, e traz o que o pareamento não tinha como trazer: a vizinhança de
    cada parágrafo, a distância entre dois deles, o tamanho de uma seção. Duas
    acusações do conferidor lento eram exatamente disso, e o pareamento as perdeu
    porque elas não têm localizador para parear.

    O que o pareamento dava e este modo não dá é o parágrafo debaixo do item.
    Aqui quem confere procura o [P###] no arquivo. Não custa travessia, custa
    atenção, e o índice cruzado existe para reduzir esse custo.
    """
    citados, mortos, carga = {}, [], {}
    for cod, tit, corpo in lista:
        cls = re.match(r"[A-Z]+", cod).group(0)
        if classes and cls not in classes:
            continue
        locs = localizadores(corpo)
        for n in locs:
            if n not in ps:
                mortos.append((cod, n))
            citados.setdefault(n, []).append(cod)
            # O item que fala de dez paragrafos de uma vez (a numeracao das
            # figuras, a palavra repetida) pousa em todos e nao diz de nenhum que
            # ele esta em disputa. Por isso cada item vale 1 dividido pelo numero
            # de paragrafos que cita. Medido em 08/09/2026: sem o peso, a
            # conclusao e um paragrafo de resultados subiam ao 3o e 4o lugares por
            # causa desses itens, e caem para 11o e 12o com ele.
            carga[n] = carga.get(n, 0.0) + 1.0 / max(1, len(locs))

    print("# Conferência de endereços: o trabalho inteiro, uma vez")
    print("\nRelatório: %s" % Path(a.relatorio).name)
    print("Extração:  %s  (%d parágrafos, de P%d a P%d, mais %d nota(s))"
          % (Path(a.extracao).name, len(ps), min(ps), max(ps), len(notas)))
    print("Parágrafos citados por algum item: %d de %d." % (len(citados), len(ps)))
    print("\n**O que decidir, item por item:** está no parágrafo o que o item diz que")
    print("está? Responda CONFERE, CAI (com o que o parágrafo diz de fato) ou ENDEREÇO")
    print("(com o certo, ou a forma fraca se não aparecer). Este programa não julga:")
    print("o único veredito dele é o localizador morto.")
    print("\n**O trabalho inteiro está abaixo, na ordem dele.** Cada parágrafo citado")
    print("traz, ao lado do número, quais itens o citam. Os não citados ficam sem")
    print("marca, e estão aqui para que a vizinhança, a distância entre parágrafos e")
    print("o tamanho das seções se confiram sem abrir mais nada.")
    if mortos:
        print("\n**LOCALIZADORES MORTOS: %d**  %s"
              % (len(mortos), ", ".join("%s→[P%d]" % m for m in mortos)))

    if carga:
        quentes = sorted(carga.items(), key=lambda kv: -kv[1])[:8]
        print("\n" + "-" * 78)
        print("POR ONDE COMEÇAR, e a ordem não é a dos itens")
        print("-" * 78)
        print("\nOs parágrafos de que mais itens dependem. Uma leitura errada aqui não")
        print("custa um item, custa o bloco. A carga pesa cada item por 1 dividido")
        print("pelo número de parágrafos que ele cita, para que o item que fala de")
        print("todas as figuras de uma vez não pareça disputa em cada uma delas.\n")
        for n, q in quentes:
            print("  [P%d]  carga %4.1f   %d item(ns): %s"
                  % (n, q, len(citados[n]), ", ".join(citados[n])))
        # os pares que dividem paragrafo sao onde a colisao entre itens aparece
        largura = {}
        for cod, _, corpo in lista:
            largura[cod] = len(localizadores(corpo))
        pares = {}
        for n, cods in citados.items():
            for i in range(len(cods)):
                for j in range(i + 1, len(cods)):
                    pares.setdefault(tuple(sorted((cods[i], cods[j]))), []).append(n)
        # Dois itens largos coincidem em muitos paragrafos por serem largos, e nao
        # por disputarem a mesma passagem: a numeracao das figuras e a falta de
        # legenda pousam nas mesmas seis, e executar um nao desfaz o outro. Fica o
        # par em que ao menos um lado e estreito.
        juntos = sorted(((p, ns) for p, ns in pares.items()
                         if len(ns) >= 3 and min(largura.get(p[0], 99),
                                                 largura.get(p[1], 99)) <= 5),
                        key=lambda kv: -len(kv[1]))[:8]
        if juntos:
            print("\nItens que dividem três ou mais parágrafos. É onde executar um pode")
            print("desfazer o outro, e a leitura item a item não vê essa colisão.\n")
            for (x, y), ns in juntos:
                print("  %-5s e %-5s  em %d: %s"
                      % (x, y, len(ns), ", ".join("[P%d]" % n for n in sorted(ns)[:8])))

    print("\n" + "=" * 78)
    print("O TRABALHO")
    print("=" * 78 + "\n")
    for n in sorted(ps):
        marca = ("  <- %s" % ", ".join(citados[n])) if n in citados else ""
        print("[P%d]%s %s\n" % (n, marca, ps[n]))
    if notas:
        print("-" * 78)
        for n in sorted(notas):
            print("[nota %d] %s\n" % (n, notas[n]))

    print("=" * 78)
    print("O RELATÓRIO A CONFERIR")
    print("=" * 78 + "\n")
    print(io.open(a.relatorio, encoding="utf-8", errors="replace").read())
    return 1 if mortos else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio")
    ap.add_argument("extracao")
    ap.add_argument("--vizinhos", type=int, default=0,
                    help="imprime N parágrafos antes e depois de cada citado")
    ap.add_argument("--so", help="só estas classes de item, separadas por vírgula (ex.: S,SC)")
    ap.add_argument("--tudo", action="store_true",
                    help="o trabalho inteiro uma vez, com índice cruzado, em vez do pareamento")
    a = ap.parse_args()

    f = autoteste()
    if f:
        print("  o próprio extrator está quebrado, e não imprimo nada:")
        for x in f:
            print("    %s" % x)
        return 2

    ps, notas = paragrafos(a.extracao)
    if not ps:
        print("  não reconheci nenhum parágrafo em %s" % a.extracao)
        return 2
    classes = set(a.so.split(",")) if a.so else None

    lista = itens(a.relatorio)
    mortos, total_loc, impressos = [], 0, 0
    saida = []

    if a.tudo:
        return modo_tudo(a, ps, notas, lista, classes)

    for cod, tit, corpo in lista:
        cls = re.match(r"[A-Z]+", cod).group(0)
        if classes and cls not in classes:
            continue
        locs = localizadores(corpo)
        total_loc += len(locs)
        if not locs:
            continue
        impressos += 1
        saida.append("\n" + "=" * 78)
        saida.append("%s  %s" % (cod, tit))
        saida.append("=" * 78)
        saida.append(" ".join(corpo.split())[:1400])
        saida.append("")
        saida.append("-- o que os endereços apontam --")
        vistos = set()
        for n in locs:
            faixa = range(n - a.vizinhos, n + a.vizinhos + 1) if a.vizinhos else [n]
            for k in faixa:
                if k in vistos:
                    continue
                vistos.add(k)
                if k not in ps:
                    if k == n:
                        mortos.append((cod, k))
                        saida.append("   [P%d]  *** LOCALIZADOR MORTO: não existe na extração." % k)
                    continue
                marca = "   [P%d]" % k if k == n else "    (P%d)" % k
                saida.append("%s  %s" % (marca, ps[k]))
        saida.append("")

    print("# Conferência de endereços em lote")
    print("\nRelatório: %s" % Path(a.relatorio).name)
    print("Extração:  %s  (%d parágrafos, de P%d a P%d, mais %d nota(s))"
          % (Path(a.extracao).name, len(ps), min(ps), max(ps), len(notas)))
    print("Itens com endereço: %d de %d.  Localizadores citados: %d."
          % (impressos, len(lista), total_loc))
    print("\n**O que decidir, item por item:** está no parágrafo o que o item diz que")
    print("está? Responda CONFERE, CAI (com o que o parágrafo diz de fato) ou ENDEREÇO")
    print("(com o certo, ou a forma fraca se não aparecer). Este programa não julga:")
    print("o único veredito dele é o localizador morto.")
    if mortos:
        print("\n**LOCALIZADORES MORTOS: %d**  %s"
              % (len(mortos), ", ".join("%s→[P%d]" % m for m in mortos)))
    print("\n".join(saida))
    return 1 if mortos else 0


if __name__ == "__main__":
    sys.exit(main())

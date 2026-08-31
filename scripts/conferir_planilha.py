# -*- coding: utf-8 -*-
"""Conta os registros de uma planilha reproduzida no trabalho, e nao opina.

POR QUE ESTE PROGRAMA EXISTE

Em 31/08/2026, quatro leituras da mesma dissertacao divergiram sobre um numero
que se conta. O apendice reproduz, linha a linha, a planilha de dados da
pesquisa. O corpo do trabalho diz 136 registros. As duas leituras que percorreram
o documento inteiro acharam 137; as duas que recuperaram trechos por consulta nao
viram nada, e uma delas confirmou 136 dez vezes seguidas, em itens de anexo, como
se estivesse conferindo.

Contar linhas numeradas nao e pergunta que se responda recuperando trecho. E
tambem nao e trabalho de modelo nenhum: e isto aqui, que roda em um segundo.

O custo de nao ter isto ficou medido. Uma das leituras gastou 538 mil tokens e 47
minutos, e dentro desse tempo escreveu um contador proprio que devolveu 101
registros na primeira tentativa, com divergencia em doze unidades da federacao;
so um controle mostrou que o defeito era do contador. Outra tentativa, feita a
mao, devolveu 81 com buracos. **Os dois erros tem a mesma causa:** a extracao de
PDF parte cada linha da planilha em varios paragrafos, e quem varre paragrafo
conta pedaco de linha.

COMO ELE CONTA, E POR QUE ASSIM

Junta a regiao inteira num texto so, desfazendo a quebra por paragrafo, e depois
procura a coluna de numero de ordem: a maior cadeia de inteiros 1, 2, 3, ... em
que cada um aparece depois do anterior e a distancia minima dele. A cadeia mais
longa e a coluna de ordem, porque nenhuma outra coluna de uma planilha cresce de
um em um ao longo de centenas de linhas.

O que ele relata: quantos registros, onde a sequencia salta, e quais registros
sao identicos campo a campo. Duplicata e o achado que explica discrepancia de
total sem que o trabalho tenha errado a conta.

    python scripts/conferir_planilha.py extracao/trabalho.txt
    python scripts/conferir_planilha.py extracao/trabalho.txt --de 1534 --ate 1651

Ele nao decide nada. Se a contagem diverge de um total publicado, quem le e que
diz se o defeito e da planilha, do total, ou deste programa.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# Distancia minima, em caracteres, entre dois numeros de ordem consecutivos.
# Existe porque colunas binarias produzem sequencias de 0 e 1 coladas, e sem ela
# a cadeia salta de um "1" de dado para o "2" da linha seguinte, encurtando a
# contagem. Doze caracteres e menos que a menor linha de dados vista nos testes.
DISTANCIA_MINIMA = 12

# Uma cadeia curta e coincidencia. Abaixo disto o programa nao afirma que achou
# planilha nenhuma.
CADEIA_MINIMA = 20


def paragrafos(texto):
    """Devolve (numero, conteudo) de cada paragrafo da extracao.

    Aceita as duas formas que os extratores produzem: `[P123] texto`, do .docx,
    e `[trabalho] P123 (p.9) texto`, do PDF.
    """
    saida = []
    for linha in texto.split("\n"):
        m = re.match(r"\s*\[[^\]]+\]\s*P(\d+)[^)]*\)?\s*(.*)", linha)
        if m:
            saida.append((int(m.group(1)), m.group(2)))
            continue
        m = re.match(r"\s*\[P(\d+)\]\s*(.*)", linha)
        if m:
            saida.append((int(m.group(1)), m.group(2)))
    return saida


# Quantos numeros de ordem a cadeia pode pular sem se romper. Existe porque
# planilha publicada as vezes salta um numero, e um contador que se rompe no
# salto devolve o tamanho do primeiro pedaco como se fosse o total. Foi o
# primeiro defeito que o controle positivo deste programa pegou, em 31/08/2026:
# contou 16 de 29 porque o bloco de teste omitia o registro 17.
SALTO_MAXIMO = 3


def maior_cadeia(texto):
    """A maior sequencia crescente de inteiros que anda de um em um no texto.

    Devolve [(valor, posicao)]. Programacao dinamica sobre as ocorrencias: a
    melhor cadeia que termina num inteiro de valor v e um a mais que a melhor
    que termina em v-1, ou em v-2, ou em v-3, desde que a posicao avance o
    bastante. Tolerar o salto e o que permite achar a coluna de ordem numa
    planilha que pula um numero, e os pulados saem relatados.
    """
    # O zero fica de fora: coluna de ordem comeca em 1, e um "0" solto antes da
    # primeira linha entrava na cadeia e fazia a contagem sair um a mais.
    ocorrencias = [(int(m.group(1)), m.start())
                   for m in re.finditer(r"(?<!\d)(\d{1,4})(?!\d)", texto)
                   if int(m.group(1)) > 0]

    # Por valor, guarda-se uma LISTA de ocorrencias, e nao so a melhor. Guardar
    # so a melhor quebra de dois modos opostos, e os dois foram medidos em
    # 31/08/2026. Guardando a primeira, o "1" que aparece no resumo ocupa a vaga
    # do valor 1 e o "1" da planilha, 600 mil caracteres adiante, nunca entra:
    # com o teto de distancia em vigor, nenhuma cadeia se forma. Guardando a
    # ultima, uma ocorrencia dentro de um campo de dado rouba a vaga da coluna de
    # ordem e a cadeia se parte. A lista resolve os dois, e o custo e pequeno
    # porque so se olham as ocorrencias dentro da janela de distancia.
    por_valor = {}                 # valor -> [(posicao, comprimento, anterior)]
    melhor_geral = None
    for valor, pos in ocorrencias:
        cand = None
        for recuo in range(1, SALTO_MAXIMO + 1):
            for ant_pos, ant_comp, _ in reversed(por_valor.get(valor - recuo, [])):
                distancia = pos - ant_pos
                if distancia > DISTANCIA_MAXIMA * recuo:
                    break              # a lista esta em ordem: o resto e pior
                if distancia < DISTANCIA_MINIMA:
                    continue
                if not cand or ant_comp + 1 > cand[1]:
                    cand = (pos, ant_comp + 1, (valor - recuo, ant_pos))
        if cand is None:
            cand = (pos, 1, None)
        por_valor.setdefault(valor, []).append(cand)
        if not melhor_geral or cand[1] > melhor_geral[1]:
            melhor_geral = (valor, cand[1], cand[0])
    if not melhor_geral:
        return []

    # refaz a cadeia de tras para a frente
    def acha(valor, pos):
        for p, c, ant in por_valor.get(valor, []):
            if p == pos:
                return c, ant
        return None, None

    cadeia = []
    valor, _, pos = melhor_geral
    while True:
        cadeia.append((valor, pos))
        _, ant = acha(valor, pos)
        if not ant:
            break
        valor, pos = ant
    return list(reversed(cadeia))


def registros(texto, cadeia):
    """O conteudo de cada registro: do seu numero de ordem ate o proximo."""
    saida = []
    for i, (valor, pos) in enumerate(cadeia):
        fim = cadeia[i + 1][1] if i + 1 < len(cadeia) else len(texto)
        campos = texto[pos + len(str(valor)):fim].strip()
        saida.append((valor, " ".join(campos.split())))
    return saida


# Distancia maxima, em caracteres, entre dois numeros de ordem de uma mesma
# planilha. E o discriminador, e ele foi escolhido por medicao em 31/08/2026.
#
# Sem ele, a cadeia mais longa de um trabalho inteiro e a numeracao das notas de
# rodape, que corre de 1 a 269 ao longo do livro e e uma sequencia perfeita. O
# primeiro discriminador tentado foi a uniformidade do comprimento dos
# registros, e ele reprovou uma planilha legitima cuja ultima coluna e texto
# livre: as linhas iam de 19 a 100 caracteres e so 53% ficavam perto da mediana.
#
# O que separa de verdade e a densidade. Medido em quatro casos: planilha de
# apendice da 68 e 75 caracteres por registro; numeracao de nota de rodape da
# 2.431 e 3.640. Nao ha nada entre 100 e 2.400, e o teto fica no meio dessa
# folga larga.
DISTANCIA_MAXIMA = 400


def densidade(cadeia):
    """Caracteres por registro, que e a medida que separa planilha de nota."""
    if len(cadeia) < 2:
        return 0
    return (cadeia[-1][1] - cadeia[0][1]) / (len(cadeia) - 1)


def totais_publicados(pars, quantos):
    """Paragrafos fora da planilha que citam um numero proximo da contagem.

    Serve para o leitor ver, de um lance, contra o que a contagem diverge. Nao
    julga: um numero proximo pode ser de outra coisa.
    """
    alvos = {quantos - 2, quantos - 1, quantos, quantos + 1}
    achados = []
    for n, txt in pars:
        for a in alvos:
            if re.search(r"(?<!\d)%d(?!\d)" % a, txt):
                achados.append((n, a, " ".join(txt.split())[:96]))
                break
    return achados


def controle_positivo():
    """Um bloco que o contador TEM de reprovar, e a conferencia de que reprova.

    Sem isto, o silencio deste programa nao informa nada. O bloco tem 30
    registros, um salto declarado e uma duplicata declarada.
    """
    # O bloco imita uma planilha de verdade, e as duas escolhas abaixo saem de
    # defeitos que este controle ja teve.
    #
    # O identificador tem seis digitos, como os numeros de processo reais. Na
    # primeira versao ele era "A001", "A002", e continha os mesmos numeros da
    # coluna de ordem: a cadeia ancorava dentro do identificador, os campos saiam
    # recortados no lugar errado, e o teste reprovava o contador por um defeito
    # que so existia no teste. Controle mais facil que a realidade nao controla.
    #
    # E a duplicata repete o registro inteiro, campo a campo. Na versao anterior
    # ela repetia so o identificador, e o ano continuava diferente, de modo que
    # nao era duplicata nenhuma e o teste passava por engano.
    def campos_de(i):
        j = 9 if i == 25 else i
        return "%06d REsp UF 20%02d 1 0 1 Nao" % (184000 + j * 37, 10 + j % 9)

    linhas = []
    for i in range(1, 31):
        if i == 17:
            continue                                   # o salto
        linhas.append("%d %s" % (i, campos_de(i)))
    texto = " ".join(linhas)
    cadeia = maior_cadeia(texto)
    regs = registros(texto, cadeia)
    vistos = Counter(c for _, c in regs)
    dup = [c for c, n in vistos.items() if n > 1]
    achou_salto = 17 not in [v for v, _ in cadeia]
    ok = (len(regs) == 29 and achou_salto and len(dup) == 1)
    return ok, len(regs), achou_salto, len(dup)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("extracao", help="o .txt gerado por scripts/extrair.py")
    ap.add_argument("--de", type=int, help="primeiro parágrafo da região")
    ap.add_argument("--ate", type=int, help="último parágrafo da região")
    a = ap.parse_args()

    ok, n, salto, dup = controle_positivo()
    print("CONTROLE POSITIVO: %s" % ("passou" if ok else "FALHOU"))
    print("  bloco de teste com 29 registros, um salto e uma duplicata")
    print("  contou %d, achou o salto: %s, duplicatas: %d" % (n, salto, dup))
    if not ok:
        sys.exit("\n  O contador nao passa no proprio controle. Nada abaixo vale.")
    print()

    caminho = Path(a.extracao)
    if not caminho.exists():
        sys.exit("nao encontrei %s" % caminho)
    pars = paragrafos(caminho.read_text(encoding="utf-8", errors="replace"))
    if not pars:
        sys.exit("nao reconheci paragrafos numerados em %s" % caminho.name)

    dentro = [(n, t) for n, t in pars
              if (a.de is None or n >= a.de) and (a.ate is None or n <= a.ate)]
    texto = " ".join(t for _, t in dentro)
    print("REGIAO: %d paragrafos, de P%d a P%d, %d caracteres"
          % (len(dentro), dentro[0][0], dentro[-1][0], len(texto)))

    cadeia = maior_cadeia(texto)
    if len(cadeia) < CADEIA_MINIMA:
        print("  nenhuma coluna de numero de ordem: a maior sequencia tem %d."
              % len(cadeia))
        print("  Isto nao e achado sobre o trabalho: e este programa dizendo que")
        print("  nao ha planilha numerada nesta regiao.")
        return 0

    regs = registros(texto, cadeia)
    valores = [v for v, _ in cadeia]
    print("  %d registros numerados, de %d a %d" % (len(regs), min(valores), max(valores)))
    print("  %.0f caracteres por registro, o que caracteriza tabela e nao nota"
          % densidade(cadeia))

    faltam = sorted(set(range(min(valores), max(valores) + 1)) - set(valores))
    if faltam:
        print("  saltos na sequencia: %s" % ", ".join(str(x) for x in faltam[:20]))

    vistos = {}
    for v, campos in regs:
        vistos.setdefault(campos, []).append(v)
    duplicatas = {c: vs for c, vs in vistos.items() if len(vs) > 1}
    print()
    if duplicatas:
        print("REGISTROS IDENTICOS CAMPO A CAMPO (%d)" % len(duplicatas))
        for campos, vs in sorted(duplicatas.items(), key=lambda x: x[1][0]):
            print("  registros %s: %s" % (" e ".join(str(v) for v in vs), campos[:88]))
        print()
        print("  Duplicata explica total maior que o de casos distintos, sem que")
        print("  o trabalho tenha errado a conta. Quem le decide qual dos dois")
        print("  numeros a planilha deveria publicar.")
    else:
        print("Nenhum registro identico a outro.")

    print()
    fora = [(n, t) for n, t in pars if not (dentro[0][0] <= n <= dentro[-1][0])]
    proximos = totais_publicados(fora, len(regs))
    if proximos:
        print("PARAGRAFOS FORA DA PLANILHA QUE CITAM UM NUMERO PROXIMO (%d)"
              % len(proximos))
        for n, valor, trecho in proximos[:12]:
            print("  [P%d] %d: %s" % (n, valor, trecho))
        if len(proximos) > 12:
            print("  ... e mais %d" % (len(proximos) - 12))
        print()
        print("  Nao sao achados. Sao os lugares onde conferir se o total publicado")
        print("  e o mesmo que a planilha traz.")

    print()
    print("  Este programa conta e nao julga. Ele nao le a legenda, nao sabe o que")
    print("  cada coluna significa, e nao afirma que um total esta errado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

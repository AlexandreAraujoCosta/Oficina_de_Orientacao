"""Mede as marcas que fazem um texto ser lido como linguagem vazia.

O QUE ISTO NAO E

Nao e deteccao de uso de IA, e o desenho recusa esse uso de proposito: nao ha
como saber, e o custo de errar recai sobre quem escreveu. Nenhum apontamento
gerado daqui pode afirmar, sugerir ou insinuar que um trecho foi gerado.

O QUE ISTO E

Medida de **efeito de recepcao**. Um leitor que topa com arremate vazio, elogio
sem medida ou enfase sem argumento desconta o que vem depois, e o autor paga por
isso mesmo tendo escrito cada palavra. Todas as marcas abaixo sao defeito de
prosa academica por si mesmas, e ja eram antes de existir modelo de linguagem.
Isso e proposital: o apontamento tem de se sustentar sem hipotese nenhuma sobre
como o texto foi produzido.

Ha, porem, uma razao pratica para que a medida seja util agora, e ela e sobre o
processo e nao sobre o texto. Quem pede ajuda a um modelo para escrever, sem
pedir critica dura, recebe texto que concorda com a tese que esta ajudando a
defender: elogia a fonte, afirma relevancia sem medi-la, e enfatiza no lugar de
argumentar. As marcas de elogio e de enfase apanham exatamente isso, e o remedio
e o mesmo em qualquer caso, que e trocar a afirmacao de peso pela medida.

O QUE A DENSIDADE SIGNIFICA

Contagem absoluta nao informa: trabalho grande tem mais de tudo. Tudo sai por mil
palavras, por bloco, com a mediana dos blocos do proprio trabalho como referencia
interna. **O achado nao e "existe", e sim "esta concentrado aqui".** Distribuicao
uniforme e estilo do autor, e nao se aponta estilo.

Uso:
    python prosa_vazia.py <extracao.txt> [--limiar 2.0] [--bloco 120] [--tudo]
"""

import argparse
import re
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

RE_PAR = re.compile(r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\]\s*)?(?:\(p\.(\d+)\)\s*)?(.*)$")
RE_PAR_MD = re.compile(r"^[#*>\s]*\[P(\d+)\]\s*(.*)$")

# A triade saiu da lista em 24/08/2026, no primeiro uso. O padrao devolvia 392
# ocorrencias num trabalho, quase todas enumeracoes legitimas de tres itens que o
# assunto tem. Nao ha regex que separe a triade por reflexo da enumeracao
# verdadeira, porque a diferenca esta em o assunto ter ou nao tres partes, e isso
# nao se le na forma. Fica como conferencia humana.

MARCAS = [
    ("conectivo de arremate",
     r"\b(?:[Aa]lém disso|[Aa]demais|[Vv]ale (?:notar|ressaltar|destacar|lembrar)|"
     r"[Ee]m suma|[Ee]m última análise|[Nn]esse sentido|[Nn]este sentido|"
     r"[Dd]iante disso|[Ii]sso posto|[Cc]om efeito|[Pp]ortanto,)\b",
     "anuncia uma conclusão em vez de tirá-la"),

    ("abertura que anuncia",
     r"\b(?:[Cc]abe (?:destacar|ressaltar|notar|observar|registrar|mencionar)|"
     r"[ÉéEe]\s*(?:importante|preciso|necessário|fundamental)\s+"
     r"(?:destacar|ressaltar|notar|observar|frisar|salientar|mencionar)|"
     r"[Cc]onvém (?:destacar|ressaltar|notar)|[Hh]á que se (?:notar|destacar)|"
     r"[Nn]ão se pode (?:deixar de|olvidar))\b",
     "gasta uma oração dizendo que vai dizer"),

    ("afirmação de peso sem medida",
     r"\b(?:de suma importância|de inegável (?:importância|relevância)|"
     r"(?:extrema|alta|profunda)mente (?:relevante|importante|significativ\w+|complex\w+)|"
     r"[Ii]nquestionavelmente|[Ii]ndubitavelmente|[Ii]negavelmente|"
     r"(?:de|com) (?:grande|enorme|vasta) (?:relevância|importância|envergadura)|"
     r"papel (?:fundamental|central|crucial|primordial)|"
     r"de (?:crucial|vital|capital) importância)\b",
     "afirma peso sem dar a medida que o sustentaria"),

    ("elogio a fonte ou a instituição",
     r"\b(?:[Bb]rilhante|[Nn]otável (?:contribuição|obra|trabalho|esforço)|"
     r"(?:obra|estudo|trabalho|contribuição) seminal|[Cc]onsagrad[oa] (?:autor|jurista|doutrinador)|"
     r"[Rr]enomad[oa]|[Ii]nsigne|[Ee]minente (?:jurista|professor|doutrinador)|"
     r"[Mm]agistral|[Pp]recis[ao] lição|[Ee]scorreit[oa])\b",
     "credita mérito ao autor citado em vez de usar o que ele diz"),

    ("antítese 'não X, mas Y'",
     r"\bnão (?:se trata de|é|era|foi|apenas|somente)\b[^.;:]{5,70}?,\s*(?:mas|e sim|senão)\b",
     "é recurso legítimo; em excesso vira fórmula"),

    ("travessão",
     r"(?<=\s)[—–](?=\s)",
     "em excesso, substitui a pontuação que marcaria a relação entre as orações"),

    ("metadiscurso de seção",
     r"\b(?:[Nn]esta seção|[Nn]o presente (?:tópico|item|capítulo|trabalho)|"
     r"[Cc]omo (?:se verá|visto acima|já mencionado|referido acima|"
     r"anteriormente (?:mencionado|referido|exposto)))\b",
     "descreve o texto em vez de escrevê-lo"),
]


def decalques():
    """Reaproveita a lista de anglicismos de legibilidade.py, se existir."""
    try:
        from legibilidade import CERTEIROS
    except Exception:
        return []
    return [("decalque: " + certo.split(",")[0], rx, quando)
            for rx, certo, quando in CERTEIROS]


def carregar(caminho):
    saida = []
    for linha in Path(caminho).read_text(encoding="utf-8", errors="replace").splitlines():
        if linha.startswith("##EXTRACAO"):
            continue
        m = RE_PAR.match(linha)
        if m:
            saida.append((int(m.group(1)),
                          int(m.group(2)) if m.group(2) else None,
                          m.group(3).strip()))
            continue
        m = RE_PAR_MD.match(linha)
        if m:
            saida.append((int(m.group(1)), None, m.group(2).strip()))
    return saida


def corpo_do_texto(pars, janela=20, minimo=40, fracao=0.6):
    """Descarta capa, folha de rosto, dedicatoria, agradecimentos e sumario.

    Sem isto a medida mente. Medido em 24/08/2026: a capa e a folha de rosto
    davam 17 travessoes por mil palavras, seis vezes a mediana do trabalho,
    porque "BRASILIA - DF" e "Fulana - Orientadora" casam o padrao; e "Por fim,
    agradeco ao Professor" entrava como conectivo de arremate. Nenhuma das duas
    e prosa do autor, e apontar qualquer uma seria ridiculo.
    """
    for i in range(max(0, len(pars) - janela)):
        longos = sum(1 for _, _, tx in pars[i:i + janela] if len(tx.split()) >= minimo)
        if longos >= janela * fracao:
            return pars[i:], pars[i][0]
    return pars, (pars[0][0] if pars else 0)


def medir(paragrafos, marcas):
    achados = {nome: [] for nome, _, _ in marcas}
    palavras = 0
    for numero, _pg, texto in paragrafos:
        palavras += len(texto.split())
        for nome, rx, _ef in marcas:
            for m in re.finditer(rx, texto):
                ini = max(0, m.start() - 35)
                achados[nome].append((numero, texto[ini:m.end() + 35]))
    return palavras, achados


def main():
    ap = argparse.ArgumentParser(
        description="Mede marcas de prosa vazia. Não afirma nada sobre a origem do texto.")
    ap.add_argument("fonte", help="extração canônica .txt ou relatório .md")
    ap.add_argument("--limiar", type=float, default=2.0,
                    help="quantas vezes a mediana dos blocos para virar achado (padrão 2)")
    ap.add_argument("--bloco", type=int, default=120, help="parágrafos por bloco (padrão 120)")
    ap.add_argument("--exemplos", type=int, default=3, help="trechos por marca (padrão 3)")
    ap.add_argument("--faixas",
                    help="restringe a medida a faixas de parágrafos, como "
                         "'P105-P123,P1027-P1045'. É onde a marca custa mais: "
                         "introdução e conclusão são o que se lê com atenção")
    ap.add_argument("--tudo", action="store_true",
                    help="não descarta o pré-textual (capa, folha de rosto, agradecimentos)")
    a = ap.parse_args()

    marcas = MARCAS + decalques()
    pars = carregar(a.fonte)
    if not pars:
        sys.exit("nenhum parágrafo reconhecido em %s" % a.fonte)
    if a.faixas:
        alvo = []
        for f in a.faixas.split(","):
            ini, fim = [int(x.strip().lstrip("Pp")) for x in f.split("-")]
            alvo += [(n, pg, tx) for n, pg, tx in pars if ini <= n <= fim]
        pars = alvo
        print("faixas: %s" % a.faixas)
    elif not a.tudo:
        pars, primeiro = corpo_do_texto(pars)
        print("pré-textual descartado: a medida começa em P%d" % primeiro)

    palavras, achados = medir(pars, marcas)
    mil = palavras / 1000 if palavras else 1
    print("%d parágrafos, %d palavras\n" % (len(pars), palavras))
    print("%-34s %7s %9s   %s" % ("marca", "ocorr.", "por mil", "o que faz ao leitor"))
    print("-" * 108)
    for nome, _rx, efeito in marcas:
        n = len(achados[nome])
        if n:
            print("%-34s %7d %9.2f   %s" % (nome, n, n / mil, efeito))
    vazias = [n for n, _, _ in marcas if not achados[n]]
    if vazias:
        print("\nzero ocorrências: %s" % ", ".join(vazias))

    lista = [pars[i:i + a.bloco] for i in range(0, len(pars), a.bloco)]
    print("\nConcentração por bloco de %d parágrafos." % a.bloco)
    print("A existência de uma marca não é achado; a concentração é.\n")
    houve = False
    for nome, _rx, _ef in marcas:
        dens = []
        for bl in lista:
            pw, ac = medir(bl, marcas)
            dens.append(len(ac[nome]) / (pw / 1000) if pw else 0)
        med = statistics.median(dens)
        picos = [(i, d) for i, d in enumerate(dens) if med > 0 and d >= med * a.limiar]
        if not picos:
            continue
        houve = True
        print("  %s (mediana %.2f por mil)" % (nome, med))
        for i, d in picos:
            ini, fim = lista[i][0][0], lista[i][-1][0]
            pg = [p for _, p, _ in lista[i] if p]
            faixa = " (p. %d-%d)" % (min(pg), max(pg)) if pg else ""
            print("    P%d-P%d%s: %.2f por mil, %.1fx" % (ini, fim, faixa, d, d / med))
        print()
    if not houve:
        print("  nenhuma concentração acima de %.1fx a mediana.\n" % a.limiar)

    print("Exemplos, para conferir se a marca é o que o padrão diz que é:")
    for nome, _rx, _ef in marcas:
        if not achados[nome]:
            continue
        print("\n  %s" % nome)
        for numero, trecho in achados[nome][:a.exemplos]:
            print("    [P%d] ...%s..." % (numero, " ".join(trecho.split())[:105]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

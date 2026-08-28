"""Conferidor de consistencia interna: acha candidatos, nao julga.

Percorre um .docx ou .pdf ja extraido e devolve candidatos a inconsistencia,
para que um leitor (humano ou modelo) julgue apenas os candidatos, e nao o
texto inteiro. A busca e determinada; o julgamento nao e tarefa deste script.

Tres verificacoes:
  numeros   - o mesmo valor aparecendo em contextos que parecem falar da mesma coisa
  listas    - itens numerados (Grafico N, Quadro N, Tabela N) declarados em listas
              e sumario contra os que aparecem no corpo
  termos    - termo declarado com definicao e depois usado longe dela

Uso:
  python scripts/conferir_consistencia.py numeros "arquivo.docx"
  python scripts/conferir_consistencia.py listas  "arquivo.docx"
  python scripts/conferir_consistencia.py termos  "arquivo.docx" --termo triagem
  python scripts/conferir_consistencia.py tudo    "arquivo.docx"
"""

import argparse
import re
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])


# O `#*` original nao alcancava o negrito: o extrator marca pseudo-titulo como
# "**[P21] Banca examinadora**  <!-- pseudo-titulo, sem estilo -->", e com o
# padrao antigo esses paragrafos ficavam INVISIVEIS ao carregador. Eram 11 num
# trabalho, entre eles [P40] RESUMO e [P44] ABSTRACT, que estao entre os mais
# citados pelos relatorios. O efeito era silencioso e do pior tipo: o relatorio
# citava o localizador, o script nao achava o paragrafo, e o leitor recebia o
# apontamento sem o trecho. Medido em 18/08/2026, por um verificador que contou
# 1.279 rotulos onde este partidor via 1.210.
# O `>` esta na classe porque a extracao rende como citacao em bloco o
# paragrafo que o trabalho cita de outro autor, e sem ele esses paragrafos
# ficam invisiveis ao carregador: o relatorio que os aponta recebe "localizador
# nao existe na fonte", que e acusacao falsa contra o proprio relatorio. Medido
# em 23/08: 5 paragrafos num capitulo, 5 noutra dissertacao, 1 numa terceira.
# E o mesmo defeito ja corrigido para `#` e `*`, um caractere adiante.
RE_PAR = re.compile(r"^[#*>\s]*\[P(\d+)\]\s*(.*)$")
RE_SUJEIRA = re.compile(r"\s*<!--.*?-->\s*$|\*\*\s*$")

# O analisar_pdf.py prefixa cada paragrafo com a etiqueta de procedencia, o
# numero sem colchetes e a pagina: "[2015_Autor_10482] P45 [TITULO] (p.12) texto".
# Sem esta segunda forma, `carregar` devolvia zero paragrafos para PDF e o
# chamador via "nenhum paragrafo extraido" como se o arquivo estivesse ruim.
RE_PAR_PDF = re.compile(
    r"^\[[^\]]+\]\s*P(\d+)\s*(?:\[[A-Z]+\]\s*)?(?:\(p\.\d+\)\s*)?(.*)$"
)


def carregar(caminho):
    """Devolve lista de (numero_do_paragrafo, texto).

    Chama analisar_docx.py ou analisar_pdf.py em vez de reextrair, para que a
    numeracao de paragrafo bata exatamente com a dos localizadores usados em
    todo o resto do projeto."""
    import os
    import subprocess

    base = os.path.dirname(os.path.abspath(__file__))

    # Extracao canonica: se existe em extracao/ e a impressao digital do
    # trabalho e a do extrator batem, le de la em vez de reextrair. A conferencia
    # da impressao e o que impede o pior caso, que e texto velho com extrator
    # novo devolvendo localizador errado em silencio.
    try:
        sys.path.insert(0, base)
        from extrair import vigente  # noqa: E402
        cache = vigente(caminho)
    except Exception:
        cache = None
    if cache is not None:
        paragrafos = []
        for linha in cache.read_text(encoding="utf-8", errors="replace").splitlines():
            if linha.startswith("##EXTRACAO"):
                continue
            m = RE_PAR.match(linha) or RE_PAR_PDF.match(linha)
            if m:
                paragrafos.append((int(m.group(1)), m.group(2).strip()))
        if paragrafos:
            return paragrafos

    if caminho.lower().endswith(".docx"):
        script = os.path.join(base, "analisar_docx.py")
        cmd = [sys.executable, script, "texto", caminho]
    elif caminho.lower().endswith(".pdf"):
        script = os.path.join(base, "analisar_pdf.py")
        cmd = [sys.executable, script, "texto", caminho]
    else:
        raise SystemExit("Use .docx ou .pdf")

    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit("falha ao extrair: %s" % (out.stderr or "")[:400])

    paragrafos = []
    for linha in out.stdout.splitlines():
        m = RE_PAR.match(linha) or RE_PAR_PDF.match(linha)
        if m:
            paragrafos.append((int(m.group(1)), m.group(2).strip()))
    if not paragrafos:
        raise SystemExit("nenhum paragrafo extraido; confira o arquivo")
    return paragrafos


# ---------------------------------------------------------------- numeros

RE_NUM = re.compile(
    r"(?<![\w,.])"
    r"(\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?)"
    r"\s*(%)?"
    r"(?![\w])"
)

# valores que aparecem demais para dizer alguma coisa
RUIDO = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0",
         "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
         "2016", "2017", "2018", "2019", "2020", "2021", "2022",
         "2023", "2024", "2025", "2026"}


def normalizar(valor, pct):
    v = valor.replace(".", "").replace(",", ".")
    return ("%s%%" % v) if pct else v


def janela(texto, pos, largura=60):
    ini = max(0, pos - largura)
    fim = min(len(texto), pos + largura)
    return re.sub(r"\s+", " ", texto[ini:fim]).strip()


STOP = set("""a o as os um uma de do da dos das em no na nos nas por para com
que se e ou ao aos à às pelo pela pelos pelas entre sobre sob ante após até
desde durante mediante perante sem trás como quando onde qual quais cujo cuja
é são foi foram ser sendo sido ter tem tinha havia há esse essa esses essas
este esta estes estas aquele aquela isso isto qual mais menos muito pouco
seu sua seus suas nesse nessa neste nesta dele dela deles delas também já
não sim ainda apenas somente inclusive porém mas contudo entretanto
p pp n nº art arts inc parágrafo cf ibid idem apud et al""".split())

# contextos que sao referencia, nao fato do trabalho
RE_REF = re.compile(
    r"(?:p{1,2}\.\s*|n[oº\.]\s*|art\.?\s*|s[úu]mula\s+|"
    r"ER\s+|EC\s+|Lei\s+|ADI\s+|ADC\s+|ADPF\s+|RE\s+|"
    r"Tema\s+|inciso\s+|§\s*)$",
    re.IGNORECASE)

RE_PONTILHADO = re.compile(r"\.{6,}")


def conteudo(texto):
    """Palavras de conteudo do contexto, para medir se dois usos falam do mesmo."""
    palavras = re.findall(r"[a-zà-ÿ]{4,}", texto.lower())
    return {w for w in palavras if w not in STOP}


RE_BIBL = re.compile(r"(https?://|Dispon[íi]vel em|Acesso em|handle/|ISBN|ISSN)", re.I)
RE_TIT_REF = re.compile(r"^\s*REFER[ÊE]NCIAS?", re.I)


def cortar_referencias(paragrafos):
    """Descarta tudo a partir do titulo de referencias. Numero repetido entre
    corpo e bibliografia e o mesmo dado citado duas vezes, e nao divergencia."""
    for i, (_, texto) in enumerate(paragrafos):
        if RE_TIT_REF.match(texto or "") and i > len(paragrafos) * 0.5:
            return paragrafos[:i], paragrafos[i][0]
    return paragrafos, None


def conferir_numeros(paragrafos, min_ocorr=2, max_ocorr=6, min_comum=2):
    """Agrupa valores por ocorrencia e retem so os pares cujos contextos
    partilham vocabulario de conteudo. Dois usos do mesmo numero interessam
    quando falam da mesma coisa; se nao partilham nada, sao fatos distintos
    que por acaso tem o mesmo valor."""
    # O pre-textual sai antes: a entrada do indice de figuras tem o mesmo
    # numero da legenda que ela lista, e o par entre as duas nao e achado.
    inicio = fim_do_pretextual(paragrafos)
    ocorr = defaultdict(list)
    for pnum, texto in paragrafos[inicio:]:
        if not texto or RE_PONTILHADO.search(texto) or RE_BIBL.search(texto):
            continue  # sumario, listas de figuras e entradas bibliograficas
        for m in RE_NUM.finditer(texto):
            bruto, pct = m.group(1), m.group(2)
            if bruto in RUIDO and not pct:
                continue
            antes = texto[max(0, m.start() - 12):m.start()]
            if RE_REF.search(antes):
                continue  # p. 41, art. 41, ADI 49
            ctx = janela(texto, m.start())
            ocorr[normalizar(bruto, pct)].append((pnum, ctx, conteudo(ctx)))

    candidatos = []
    for valor, lista in ocorr.items():
        pars = sorted({p for p, _, _ in lista})
        if not (min_ocorr <= len(pars) <= max_ocorr):
            continue
        # so vale se ao menos dois contextos partilham vocabulario
        melhor, par = 0, None
        for i in range(len(lista)):
            for j in range(i + 1, len(lista)):
                if lista[i][0] == lista[j][0]:
                    continue
                comum = lista[i][2] & lista[j][2]
                if len(comum) > melhor:
                    melhor, par = len(comum), (lista[i], lista[j], comum)
        if melhor >= min_comum:
            candidatos.append((valor, lista, melhor, par))
    candidatos.sort(key=lambda c: -c[2])
    return candidatos


# ---------------------------------------------------------------- listas

RE_ITEM = re.compile(r"\b(Gr[áa]fico|Quadro|Tabela|Figura|Ap[êe]ndice)\s+(\d{1,2})\b",
                     re.IGNORECASE)


RE_PAGINA = re.compile(r"\s\d{1,3}$")


def fim_do_pretextual(paragrafos, teto=0.45, piso=0.15):
    """Onde acaba o sumario e comecam as legendas de verdade.

    A entrada de indice e a legenda tem a mesma forma; o que as separa e o
    numero da pagina ao fim da entrada. Medido em 28/08/2026 numa dissertacao:
    66 entradas de indice acabam em numero e nenhuma das 66 legendas do corpo
    acaba.

    Antes disto o pre-textual era 15% dos paragrafos, por estimativa. No mesmo
    trabalho ele ocupava 25%, e a conferencia acusou 19 graficos e 3 tabelas
    ausentes de uma lista que os continha. Proporcao fixa nao serve: ha trabalho
    com sumario de duas paginas e trabalho com indice de sessenta figuras.
    """
    total = len(paragrafos)
    ultimo = 0
    for i, (_pnum, texto) in enumerate(paragrafos[:int(total * teto)]):
        if RE_ITEM.search(texto or "") and RE_PAGINA.search((texto or "").strip()):
            ultimo = i
    return max(ultimo + 1, int(total * piso)) if ultimo else int(total * piso)


def conferir_listas(paragrafos, corte_lista=0.15):
    """Compara itens numerados citados na parte inicial (sumario e listas)
    com os que aparecem no corpo."""
    limite = fim_do_pretextual(paragrafos)

    def coletar(faixa):
        d = defaultdict(set)
        for pnum, texto in faixa:
            for m in RE_ITEM.finditer(texto or ""):
                d[m.group(1).capitalize()].add(int(m.group(2)))
        return d

    na_lista = coletar(paragrafos[:limite])
    no_corpo = coletar(paragrafos[limite:])

    achados = []
    for tipo in sorted(set(na_lista) | set(no_corpo)):
        a, b = na_lista.get(tipo, set()), no_corpo.get(tipo, set())
        so_lista, so_corpo = sorted(a - b), sorted(b - a)
        if so_lista or so_corpo:
            achados.append((tipo, so_lista, so_corpo, sorted(a), sorted(b)))
    return achados, limite


# ---------------------------------------------------------------- termos

RE_DEF = re.compile(
    r"(entende-se por|define-se|denomina-se|considera-se|"
    r"para os fins desta pesquisa|neste trabalho|aqui,?\s+)",
    re.IGNORECASE)


def conferir_termos(paragrafos, termo):
    """Localiza onde o termo e definido e onde e usado, e mede a distancia.
    Uso longe da definicao e candidato a deriva, nao deriva."""
    t = termo.lower()
    definicoes, usos = [], []
    for pnum, texto in paragrafos:
        low = (texto or "").lower()
        if t not in low:
            continue
        if RE_DEF.search(texto or ""):
            definicoes.append((pnum, janela(texto, low.find(t), 110)))
        else:
            usos.append((pnum, janela(texto, low.find(t), 80)))
    return definicoes, usos


# ---------------------------------------------------------------- saida

def cabecalho(titulo, nota):
    print("\n" + "=" * 72)
    print(titulo)
    print("=" * 72)
    print(nota + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["numeros", "listas", "termos", "tudo"])
    ap.add_argument("arquivo")
    ap.add_argument("--termo", default=None)
    ap.add_argument("--max", type=int, default=40, help="maximo de candidatos")
    args = ap.parse_args()

    paragrafos = carregar(args.arquivo)
    print("Arquivo: %s | %d paragrafos" % (args.arquivo, len(paragrafos)))

    if args.cmd in ("numeros", "tudo"):
        corpo, p_ref = cortar_referencias(paragrafos)
        if p_ref:
            print("Referencias comecam em [P%d]; numeros dali em diante ignorados." % p_ref)
        cands = conferir_numeros(corpo)
        cabecalho(
            "CANDIDATOS: mesmo valor em pontos distantes (%d)" % len(cands),
            "Nao sao achados. Cada linha e um valor que reaparece; quem le decide\n"
            "se os contextos falam da mesma coisa e se concordam.")
        for valor, lista, forca, par in cands[:args.max]:
            print("valor %s  (%d palavras de conteudo em comum)" % (valor, forca))
            if par:
                (pa, ca, _), (pb, cb, _), comum = par
                print("   [P%d] ...%s..." % (pa, ca))
                print("   [P%d] ...%s..." % (pb, cb))
                print("   em comum: %s" % ", ".join(sorted(comum)[:8]))
            outros = sorted({p for p, _, _ in lista} - ({par[0][0], par[1][0]} if par else set()))
            if outros:
                print("   tambem em: %s" % ", ".join("P%d" % p for p in outros))
            print()

    if args.cmd in ("listas", "tudo"):
        achados, limite = conferir_listas(paragrafos)
        cabecalho(
            "CANDIDATOS: listas e sumario contra o corpo (%d tipos)" % len(achados),
            "Parte inicial considerada: P1 a P%d. Divergencia aqui costuma ser\n"
            "peca de enquadramento que nao acompanhou a revisao." % limite)
        for tipo, so_lista, so_corpo, todos_a, todos_b in achados:
            print("%s" % tipo)
            if so_lista:
                print("   declarado na lista e ausente do corpo: %s" % so_lista)
            if so_corpo:
                print("   presente no corpo e ausente da lista: %s" % so_corpo)
            print("   lista=%s" % todos_a)
            print("   corpo=%s\n" % todos_b)

    if args.cmd == "termos":
        if not args.termo:
            raise SystemExit("informe --termo")
        defs, usos = conferir_termos(paragrafos, args.termo)
        cabecalho(
            'CANDIDATOS: usos de "%s" longe da definicao' % args.termo,
            "Definicoes localizadas por marcador explicito. Uso longe da definicao\n"
            "e candidato a deriva, e nao deriva: quem le decide se o referente mudou.")
        print("definicoes encontradas: %d" % len(defs))
        for pnum, ctx in defs:
            print("   [P%d] ...%s..." % (pnum, ctx))
        print("\nusos: %d" % len(usos))
        for pnum, ctx in usos[:args.max]:
            marca = ""
            if defs:
                dist = min(abs(pnum - d) for d, _ in defs)
                if dist > 200:
                    marca = "  <-- %d paragrafos da definicao mais proxima" % dist
            print("   [P%d] ...%s...%s" % (pnum, ctx, marca))

    print("\n" + "-" * 72)
    print("Este script acha candidatos, nao julga. Ele confere o trabalho contra")
    print("ele mesmo, e nao avalia argumento, metodo nem contribuicao.")


if __name__ == "__main__":
    main()

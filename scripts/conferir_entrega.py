# -*- coding: utf-8 -*-
"""Conferências mecânicas que o relatório tem de passar antes de virar entrega.

POR QUE ISTO EXISTE

Em 03/09/2026 a montagem tinha uma trava só, a de compreensibilidade, que é
julgamento humano e custa uma leitura inteira. Os defeitos que mais custaram
naquela rodada não eram de julgamento: eram mecânicos, e nenhum tinha conferidor.

    aspas que não estão na fonte      6 nos três relatórios, uma delas uma
                                      palavra portuguesa numa tese em inglês
    vocabulário de trabalho           45 ocorrências de *controle positivo*,
                                      *na mesma execução*, *fronteira de palavra*
    perífrase                         "o termo que designa os ministros" em vez
                                      da palavra, o que deixa o número para
                                      acreditar e não para conferir

Os três se conferem por programa, e por isso se conferem sempre, e não quando
alguém lembra.

O QUE CADA UM DECIDE

    aspas       BLOQUEIA. Aspas neste projeto significam transcrição da fonte, e
                transcrição só entra por programa. Aspas cujo conteúdo não está
                na fonte é afirmação falsa com aparência de conferível.
    vocabulário BLOQUEIA. É lista fechada, e a saída nomeia cada ocorrência.
    perífrase   AVISA. Tem falso positivo demais para bloquear, mas o aviso é
                onde a redação costuma estar frouxa.

Uso:
    python conferir_entrega.py <relatorio.md> <extracao.txt>
    python conferir_entrega.py <relatorio.md> <extracao.txt> --minimo 6

Sai com código 1 se alguma conferência bloqueante falhar.
"""
import argparse
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# Vocabulário com que a análise é feita, e que não é o de quem recebe o
# relatório. Cada entrada esteve num relatório entregue em 03/09/2026.
VOCABULARIO = [
    "controle positivo", "controles positivos", "controle negativo",
    "controles negativos", "mesma execução", "fronteira de palavra",
    "falso positivo", "falsos positivos", "padrão escapado", "padrão frouxo",
    "cadeia de teste", "artefato da busca", "buscas de ausência",
    "controle de caixa", "faixa acentuada",
    # As palavras de trabalho que o LUIS.md ja mandava nao exportar, e que
    # sairam assim mesmo. Escritas na lista, elas param de depender de lembranca.
    # Medido em 03/09/2026: "fossil" e "voz" num relatorio entregue, e "cotejo"
    # em seis lugares nos tres, sempre designando a maquina e nunca a coisa.
    "fóssil", "fósseis", "fissura", "reenunciação",
    # "acoplamento" solto acusava "redução de acoplamentos" numa tese de
    # arquitetura de TI e assunto do trabalho. Fica a forma da minha análise.
    "fracamente acoplad", "acoplamento ao que mudou",
    "segunda voz", "primeira voz", "por voz que", "uma voz só",
    "o cotejo reabriu", "o cotejo decidiu", "prevalece o cotejo",
    "pelo cotejo", "do cotejo das", "o cotejo recaiu", "passou por cotejo",
]

# "cotejo" e "universo" tem dois sentidos, e o segundo e legitimo: o autor
# cotejando as fontes dele, e o universo estatistico dos dados dele. Por isso
# a lista traz as FORMAS em que a palavra designa a maquina, e nao a palavra
# solta: proibir "cotejo" acusaria tres passagens corretas de uma tese.

# Perífrase: a frase afirma uma contagem sem escrever a palavra contada.
RE_CONTAGEM = re.compile(
    r"(?:o termo|a palavra|a expressão|o vocabulário|o sobrenome|a cadeia)"
    r"\s+(?:que|de|do|da)\b[^.;:]{0,60}?"
    r"(?:tem|dá|ocorre|aparece|soma|devolve)\b", re.I)


def normalizar(s):
    return re.sub(r"\s+", " ", s).strip()


def citacoes(texto, minimo):
    """Trechos entre aspas, curvas e retas.

    As retas se emparelham em ORDEM: um padrão `"([^"]+)"` casa a segunda aspa
    com a terceira e captura o texto ENTRE citações, o que já produziu onze
    acusações falsas numa conferência minha. E o padrão não pode excluir `\\n`:
    citação que atravessa quebra de linha ficaria invisível, e o conferidor
    reportaria um denominador que parece cobertura.
    """
    fora = [m.group(1) for m in
            re.finditer("“([^“”]+)”", texto, re.S)]
    partes = texto.split('"')
    fora += [partes[i] for i in range(1, len(partes), 2)]
    return [c for c in fora if len(normalizar(c)) >= minimo]


def autoteste():
    """Prova os três conferidores antes de usá-los, com caso que têm de acusar."""
    falhas = []
    esperado = ["uma coisa", "outra coisa"]
    obtido = citacoes('diz “uma coisa” e "outra coisa" fim', 6)
    if obtido != esperado:
        falhas.append("extrator de aspas: %r" % (obtido,))
    quebrada = citacoes('a autora escreve: "um trecho\nque atravessa a quebra".', 6)
    if not quebrada or "quebra" not in quebrada[0]:
        falhas.append("extrator perde citacao que atravessa quebra de linha")
    if not RE_CONTAGEM.search("o termo que designa os ministros tem 133 ocorrências"):
        falhas.append("detector de perifrase nao acusa o caso conhecido")
    if RE_CONTAGEM.search("*Justices* aparece em 131 parágrafos"):
        falhas.append("detector de perifrase acusa a forma correta")
    return falhas


def main():
    ap = argparse.ArgumentParser(description="Conferências mecânicas da entrega.")
    ap.add_argument("relatorio")
    ap.add_argument("extracao")
    ap.add_argument("--minimo", type=int, default=6,
                    help="tamanho mínimo do trecho entre aspas a conferir "
                         "(padrão 6; era 40, e as seis aspas falsas de "
                         "03/09/2026 tinham entre 8 e 34 caracteres)")
    a = ap.parse_args()

    falhas_autoteste = autoteste()
    if falhas_autoteste:
        print("  o proprio conferidor esta quebrado, e nao reporto nada:")
        for f in falhas_autoteste:
            print("    %s" % f)
        return 2
    print("  autoteste dos tres conferidores: passou")

    rel = Path(a.relatorio).read_text(encoding="utf-8")
    fonte = normalizar(Path(a.extracao).read_text(encoding="utf-8"))
    bloqueia = False

    # ---- aspas
    cits = citacoes(rel, a.minimo)
    ausentes = [c for c in cits if normalizar(c) not in fonte]
    print("\n  ASPAS: %d conferidas, %d ausentes da fonte" % (len(cits), len(ausentes)))
    for c in ausentes:
        print("     AUSENTE  %s" % normalizar(c)[:100])
    if ausentes:
        bloqueia = True
        print("     Aspas significam transcrição da fonte. Se o trecho é proposta")
        print("     sua, ou proposição que o relatório contrapõe, vai em itálico.")

    # ---- vocabulário
    achados = []
    for termo in VOCABULARIO:
        for m in re.finditer(re.escape(termo), rel, re.I):
            achados.append((rel[:m.start()].count("\n") + 1, m.group()))
    print("\n  VOCABULÁRIO DE TRABALHO: %d ocorrência(s)" % len(achados))
    for ln, t in achados[:20]:
        print("     linha %-5d %s" % (ln, t))
    if len(achados) > 20:
        print("     (e mais %d)" % (len(achados) - 20))
    if achados:
        bloqueia = True

    # ---- perífrase
    per = [(rel[:m.start()].count("\n") + 1, normalizar(m.group()))
           for m in RE_CONTAGEM.finditer(rel)]
    print("\n  PERÍFRASE (aviso, não bloqueia): %d" % len(per))
    for ln, t in per[:12]:
        print("     linha %-5d %s" % (ln, t[:90]))
    if per:
        print("     Escreva a palavra contada, em itálico. Número sem a palavra")
        print("     é para acreditar, não para conferir.")

    print("\n  %s" % ("REPROVADO: corrija antes de montar." if bloqueia
                      else "aprovado nas conferências mecânicas."))
    return 1 if bloqueia else 0


if __name__ == "__main__":
    sys.exit(main())

"""Confere a estrutura de um relatorio produzido pela lente v3.

    python conferir_lente.py <relatorio.md>
    python conferir_lente.py --lote <pasta>

POR QUE ESTE SCRIPT EXISTE

A lente v3 acrescentou uma secao obrigatoria de virtudes (o que a leitura do
material alcanca), porque as versoes anteriores so coletavam desvio em relacao
a regua quantitativa. A objecao que originou isso foi feita pelo especialista do
campo em 01/08/2026, ficou anotada como "correcao pendente", e a versao seguinte
do instrumento foi escrita no dia seguinte sem atende-la. Cento e oito leituras
rodaram com o instrumento nao corrigido.

A licao ja tinha sido paga uma vez, no caso das citacoes: instrucao no prompt nao
corrige defeito estrutural de quem escreve. O que resolveu ali foi tirar a
transcricao da mao do modelo e dar a um script. Aqui vale o mesmo: o cumprimento
da secao de virtudes nao pode depender da boa vontade de um leitor que tem viés
documentado para o contavel.

O QUE ESTE SCRIPT NAO FAZ, E E IMPORTANTE

Ele confere forma, nao conteudo. Um elogio vazio, bem formatado, com localizador
e com a palavra "sem" na frase, passa. O script nao sabe se o apontamento de
virtude diz alguma coisa. Isso e limite conhecido, nao descuido: ele reduz o
espaco onde o viés pode se esconder, nao o elimina.

E, pela regra do projeto sobre conferidores: ele erra. Os padroes de
contrafactual sao heuristica, com falso positivo e falso negativo. A saida marca
"CONFERIR" onde a duvida e do proprio script, e isso nao e acusacao ao relatorio.
Antes de reportar defeito acusado por este script, teste o script.
"""
import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# O separador de faixa aceita hifen, travessao e meio-travessao: travessao em
# faixa numerica e tipografia normal em portugues, e reprovar por isso e rigidez
# do script, nao erro do relatorio. Apontado por um leitor em 11/08.
LOCALIZADOR = re.compile(
    r"\[P\d+(?:[-–—]P\d+)?(?:,\s*P\d+(?:[-–—]P\d+)?)*\]")

# Heuristica de contrafactual: a lente exige dizer o que se perderia sem aquilo.
# Reconhece subjuntivo E indicativo. O indicativo foi acrescentado em 11/08 depois
# de um falso negativo confirmado em teste: um leitor escreveu o contrafactual em
# indicativo ("sem ela, o dado so diz que...") e o script nao reconheceu.
CONTRAFACTUAL = re.compile(
    r"\bsem (?:ele|ela|isso|esse|essa|este|esta|o |a )"
    r"|\bse (?:ele|ela|isso|esse|essa|este|esta|o |a )[^.]{0,80}"
    r"\b(?:fosse|estivesse|retirad|sair|sai\b|tirar)"
    r"|\bdeixaria de\b|\bdeixa de\b|\bnao teria\b|\bnao tem como\b"
    r"|\bteria (?:ficado|sido)\b|\bseria (?:apenas|so|uma|um|outro|outra)\b"
    r"|\bperderia\b|\bficaria\b|\bso diria\b|\bso diz\b|\bdiria (?:apenas|so)\b"
    r"|\bfica (?:apenas|so|sem)\b|\bnao passaria de\b|\bnao passa de\b",
    re.I)

# Aspas que sao mencao, nao transcricao: rotulo de categoria, nome de variavel,
# termo tecnico. Criterio grosseiro mas defensavel: mencao e curta e nao tem
# pontuacao interna de frase. Acrescentado em 11/08 porque o script punia aspas de
# qualquer natureza e forcou um leitor a parafrasear o nome de uma variavel do
# trabalho, perdendo precisao no apontamento.
# A abertura tem de ser mesmo abertura: precedida de espaco, inicio de linha ou
# pontuacao de abertura, e seguida de nao-espaco. Sem isso, com aspas retas o
# script casava o FECHO de uma mencao curta com a ABERTURA da seguinte e capturava
# a prosa do proprio relatorio no meio. Diagnosticado por um leitor em 11/08, que
# discordou do aviso e mostrou o mecanismo em teste isolado.
ASPAS_TRECHO = re.compile(
    r"(?:^|(?<=[\s(\[]))[\"“«](\S[^\"”»]{24,})[\"”»]", re.M)

# Declaracao de ausencia: a lente permite, e desde 11/08 encoraja, dizer que uma
# pergunta nao rendeu neste trabalho. Apontamento assim NAO exige localizador nem
# contrafactual, e exigir seria sabotar a emenda: se declarar ausencia da falha, o
# leitor deixa de declarar, e a pressao de fabricacao volta pela porta dos fundos.
ABSENCIA = re.compile(
    r"\bnao rendeu\b|\bnao encontrei\b|\bnao achei\b|\bnao ha\b|\bnao houve\b"
    r"|\bnada a apontar\b|\bnenhum(?:a)? (?:virtude|apontamento|achado)\b"
    r"|\bausente neste trabalho\b|\bsem achado\b|\bnao se aplica\b",
    re.I)

CABECALHO_REGISTRO = re.compile(r"^#{1,4}\s*.{0,30}registro", re.I | re.M)
CABECALHO_METODO = re.compile(r"^#{1,4}\s*.{0,30}m[eé]todo", re.I | re.M)
CABECALHO_VIRTUDE = re.compile(r"^#{1,4}\s*I\.\s|^#{1,4}\s*O que esta leitura alcanca",
                               re.I | re.M)
CABECALHO_DEFEITO = re.compile(r"^#{1,4}\s*II\.\s|^#{1,4}\s*Os defeitos", re.I | re.M)
CABECALHO_CORTE = re.compile(r"^#{1,4}\s*III\.\s|^#{1,4}\s*Corte declarado", re.I | re.M)
RESSALVA = re.compile(r"Ressalva do instrumento", re.I)
REGISTRO = re.compile(r"registro (quantitativo|interpretativo|hist[oó]rico|misto|em descompasso)",
                      re.I)

# Um apontamento comeca em "**N.", "N.", "**A.", "**Pergunta A." no inicio da
# linha, ou em item de lista. As letras entraram em 11/08, quando a lente trocou
# os itens numerados da secao I por perguntas com letra: sem isso a secao inteira
# virava um apontamento so, e um unico localizador satisfazia tudo. Bug encontrado
# testando o proprio script, que e a regra do projeto.
# Quatro leitores esbarraram na rigidez desta expressao, cada um com um formato de
# rotulo diferente: "A1", "Pergunta B (i).", cabecalho proprio. Quando ela falha, a
# secao inteira vira um apontamento so e as checagens por apontamento perdem o
# sentido. A ultima alternativa, negrito em inicio de linha, cobre os formatos que
# nao dava para antecipar: apontamento comeca em linha propria e quase sempre em
# negrito.
APONTAMENTO = re.compile(
    r"^\s*(?:\*\*)?(?:Pergunta\s+)?(?:\d{1,2}|[A-Z]\d{0,2})(?:[.)]\s|[.)]?\*\*\s)"
    r"|^\s*[-*]\s+\*\*"
    r"|^\s*(?:\*\*)?Campo separado"
    r"|^\s*\*\*\S", re.M | re.I)

# Teto de tamanho para aceitar um apontamento como declaracao de ausencia.
# Existe por causa de um buraco real, aberto em 11/08 pela propria isencao de
# ausencia: com rotulo "A1"/"B2" a separacao falhava, a secao I inteira virava um
# apontamento so, e bastava a expressao "nao rendeu" em qualquer ponto dela para o
# script pular a checagem de localizador do relatorio inteiro. Declaracao de
# ausencia e uma frase ou duas; bloco longo nao e.
MAX_PALAVRAS_AUSENCIA = 90

# Marca do campo que a lente reserva a merito interpretativo sem prova
# procedimental. Exige localizador, nao exige contrafactual.
CAMPO_SEPARADO = re.compile(
    r"campo separado|juizo de quem leu|ju[ií]zo de quem leu"
    r"|sem prova procedimental|sem contrafactual", re.I)

# Orcamento por secao, em palavras (v3.1, 11/08). Cada secao tem o seu e eles nao
# competem: antes havia teto unico e, como a secao de virtudes era protegida do
# corte, ela comia o orcamento da secao de defeitos. Cinco leitores em cinco
# leituras de teste reclamaram do aperto, dois deles declarando nao ter certeza de
# que o corte fora o certo. Orcamento escrito no prompt e instrucao; conferido
# aqui, e restricao.
ORCAMENTO = {
    # 250, e nao 150, porque a declaracao e por trecho: trabalho com onze secoes
    # precisa de mais espaco que um com seis. Medido nos cinco relatorios de
    # teste, onde 150 estourou em tres.
    "registro": 250,
    "metodo": 250,
    "I (virtudes)": 500,
    "II (defeitos)": 900,
    "III (corte)": 150,
}


def sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def fatia(texto, ini_re, fim_res):
    """Trecho entre um cabecalho e o proximo cabecalho conhecido."""
    m = ini_re.search(texto)
    if not m:
        return None
    inicio = m.end()
    fim = len(texto)
    for r in fim_res:
        m2 = r.search(texto, inicio)
        if m2 and m2.start() < fim:
            fim = m2.start()
    return texto[inicio:fim]


def apontamentos(bloco):
    """Divide um bloco em apontamentos, pelo marcador numerado."""
    if not bloco:
        return []
    marcas = [m.start() for m in APONTAMENTO.finditer(bloco)]
    if not marcas:
        corpo = bloco.strip()
        return [corpo] if corpo else []
    marcas.append(len(bloco))
    saida = []
    for i in range(len(marcas) - 1):
        t = bloco[marcas[i]:marcas[i + 1]].strip()
        if t:
            saida.append(t)
    return saida


def conferir(caminho):
    texto = Path(caminho).read_text(encoding="utf-8")
    plano = sem_acento(texto)
    falhas, avisos, notas = [], [], []

    # 1. Declaracao de registro, exigida antes de qualquer avaliacao.
    registros = REGISTRO.findall(plano)
    if not registros:
        falhas.append("nao declara o registro de nenhuma passagem "
                      "(passo obrigatorio da COMUM v3)")
    else:
        notas.append(f"registros declarados: {len(registros)}")

    # 2. A secao de virtudes existe.
    bloco_v = fatia(plano, CABECALHO_VIRTUDE, [CABECALHO_DEFEITO, CABECALHO_CORTE])
    bloco_d = fatia(plano, CABECALHO_DEFEITO, [CABECALHO_CORTE])
    if bloco_v is None:
        falhas.append("secao I (o que esta leitura alcanca) ausente")
        ap_v = []
    else:
        ap_v = apontamentos(bloco_v)
        if not ap_v:
            falhas.append("secao I existe e esta vazia")

    ap_d = apontamentos(bloco_d) if bloco_d else []

    # 3. Razao entre virtude e defeito.
    if ap_d and not ap_v:
        falhas.append(f"{len(ap_d)} apontamento(s) de defeito e nenhum de virtude: "
                      "e exatamente o padrao que a lente v3 existe para corrigir")
    elif ap_v:
        notas.append(f"virtude {len(ap_v)} / defeito {len(ap_d)}")

    # 4. Cada apontamento de virtude precisa de localizador e de contrafactual,
    #    EXCETO os que declaram ausencia, que sao resultado legitimo.
    n_ausencias = 0
    for i, ap in enumerate(ap_v, start=1):
        if ABSENCIA.search(ap):
            if len(ap.split()) <= MAX_PALAVRAS_AUSENCIA:
                n_ausencias += 1
                continue
            # Bloco longo com marca de ausencia dentro: nao e declaracao de
            # ausencia, e provavelmente falha de separacao de apontamentos.
            avisos.append(
                f"virtude {i}: tem marca de ausencia dentro de um bloco de "
                f"{len(ap.split())} palavras. Isso costuma ser falha de separacao "
                "(rotulos que o script nao reconhece). A isencao NAO foi aplicada; "
                "confira se a secao I foi separada em apontamentos (CONFERIR)")
        if not LOCALIZADOR.search(ap):
            falhas.append(f"virtude {i}: sem localizador [P...]")
        # O "campo separado" da lente existe justamente para merito interpretativo
        # SEM prova contrafactual, marcado como juizo de quem leu. Exigir
        # contrafactual dele e incoerencia entre o script e o prompt: apontada por
        # um leitor em 11/08, que discordou do aviso em vez de obedecer.
        if CAMPO_SEPARADO.search(ap):
            continue
        if not CONTRAFACTUAL.search(ap):
            avisos.append(f"virtude {i}: nao achei marca de contrafactual "
                          "(heuristica; CONFERIR a mao)")

    # 4b. Assinatura de grade preenchida. No teste de 11/08, quatro leitores
    #     produziram quatro virtudes cada, em quatro objetos sem nada em comum, e
    #     nenhum declarou ausencia. A uniformidade vinha da grade, nao dos
    #     trabalhos. Isto e heuristica fraca e serve so para provocar releitura.
    n_com_achado = len(ap_v) - n_ausencias
    if n_ausencias:
        notas.append(f"ausencias declaradas: {n_ausencias}")
    elif n_com_achado >= 4:
        avisos.append(f"{n_com_achado} virtudes e nenhuma ausencia declarada: "
                      "confere com a assinatura de grade preenchida vista no teste "
                      "de 11/08. Releia a secao I com desconfianca (CONFERIR)")

    # 4c. Orcamento por secao. Conta so o que se consegue delimitar com seguranca.
    faixas = {
        "registro": fatia(texto, CABECALHO_REGISTRO,
                          [CABECALHO_METODO, CABECALHO_VIRTUDE]),
        "metodo": fatia(texto, CABECALHO_METODO, [CABECALHO_VIRTUDE]),
        "I (virtudes)": fatia(texto, CABECALHO_VIRTUDE,
                              [CABECALHO_DEFEITO, CABECALHO_CORTE]),
        "II (defeitos)": fatia(texto, CABECALHO_DEFEITO, [CABECALHO_CORTE]),
        "III (corte)": fatia(texto, CABECALHO_CORTE, [RESSALVA]),
    }
    medidas, no_teto = [], 0
    for nome, bloco in faixas.items():
        if bloco is None:
            continue
        # tira o bloco de ressalva, que e copiado e fica fora de contagem
        corte_ressalva = RESSALVA.search(bloco)
        if corte_ressalva:
            bloco = bloco[:corte_ressalva.start()]
        n = len(bloco.split())
        lim = ORCAMENTO[nome]
        medidas.append(f"{nome} {n}/{lim}")
        if n > lim:
            avisos.append(f"secao {nome}: {n} palavras, orcamento {lim}. "
                          "Corte dentro da secao e declare na III; nao tome "
                          "emprestado de outra secao")
        elif n >= lim * 0.9:
            no_teto += 1
    if medidas:
        notas.append("palavras por secao: " + ", ".join(medidas))
    if no_teto >= 3:
        avisos.append(f"{no_teto} secoes a 90% ou mais do orcamento: orcamento e "
                      "limite, nao cota a cumprir. Confira se houve enchimento "
                      "para preencher espaco (CONFERIR)")

    # 5. Bloco de ressalva do instrumento.
    if not RESSALVA.search(plano):
        falhas.append("bloco 'Ressalva do instrumento' ausente (secao IV, obrigatoria)")

    # 6. Transcricao: a regra do projeto e localizador, nunca aspas do trabalho.
    # So sinaliza trecho longo entre aspas. Mencao curta (rotulo de categoria,
    # nome de variavel) nao e transcricao e nao deve ser punida.
    trechos = ASPAS_TRECHO.findall(texto)
    if trechos:
        avisos.append(f"{len(trechos)} trecho(s) longo(s) entre aspas: conferir se "
                      "transcrevem o trabalho (a lente proibe; CONFERIR a mao). "
                      f"O primeiro comeca por: {trechos[0][:40]}...")

    return falhas, avisos, notas


def relatar(caminho, falhas, avisos, notas):
    nome = Path(caminho).name
    estado = "FALHA" if falhas else ("AVISO" if avisos else "ok")
    print(f"[{estado}] {nome}")
    for n in notas:
        print(f"        . {n}")
    for f in falhas:
        print(f"   FALHA  {f}")
    for a in avisos:
        print(f"   AVISO  {a}")
    return bool(falhas)


def main():
    ap = argparse.ArgumentParser(
        description="Confere a estrutura de relatorios da lente v3. "
                    "Confere forma, nao qualidade: elogio vazio bem formatado passa.")
    ap.add_argument("alvo")
    ap.add_argument("--lote", action="store_true",
                    help="alvo e uma pasta; confere todos os .md dela")
    a = ap.parse_args()

    alvos = sorted(Path(a.alvo).glob("*.md")) if a.lote else [Path(a.alvo)]
    if not alvos:
        sys.exit("nenhum .md encontrado.")

    reprovados = 0
    for c in alvos:
        if c.name.endswith(".bak"):
            continue
        falhas, avisos, notas = conferir(c)
        if relatar(c, falhas, avisos, notas):
            reprovados += 1
        if len(alvos) > 1:
            print()

    print(f"--- {len(alvos)} relatorio(s), {reprovados} com falha estrutural.")
    print("Este script confere forma. Nao sabe dizer se o apontamento de virtude")
    print("diz alguma coisa, e os avisos sao heuristica: teste o script antes de")
    print("reportar defeito que ele acusou.")
    sys.exit(1 if reprovados else 0)


if __name__ == "__main__":
    main()

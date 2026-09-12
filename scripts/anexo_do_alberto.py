# -*- coding: utf-8 -*-
"""Deriva, do relatorio do Alberto, a lista de itens que a maquinaria le.

POR QUE ISTO EXISTE

O relatorio do Alberto traz os itens em prosa titulada (`### S6. ...`, com os
campos `- **Aponta**`, `- **O que fazer**`), que e a forma que quem recebe le.
O `anotar_docx.py` e o `texto_dos_comentarios.py` leem outra forma (`## S6`,
`**Aponta:**`, `**Abrir:**`), que e a que ancora o comentario no paragrafo
certo. Ate 05/09/2026 a passagem de uma forma a outra nao existia, e o
`texto_dos_comentarios.py` devolvia zero apontamentos sobre um relatorio de
trinta e nove itens, sem dizer por que.

Ninguem digita o texto do item: este programa o copia do relatorio.

O QUE VAI PARA A MARGEM, E POR QUE NAO E O ITEM INTEIRO

A margem recebe o titulo do item e o campo `O que fazer`, e nao o campo
`Aponta`. O `Aponta` traz a prestacao de contas da busca (quantos paragrafos,
que forma, que recorte), que existe para quem confere o relatorio e nao para
quem corrige o texto. Medido em 05/09/2026, numa leitura fria dos 37
apontamentos de uma dissertacao: doze deles fizeram o leitor ler alguma frase
duas vezes, e em todos era o meio do item. O proprio ALBERTO.md ja diz que o
campo `O que fazer` e "o unico campo que o autor lera ao lado do texto".

Os localizadores de `Abrir` continuam saindo do `Aponta`, porque e la que esta
onde o defeito ocorre, e e por eles que o comentario se ancora.

Uso:
    python scripts/anexo_do_alberto.py RELATORIO-X.md --saida ANEXO-ITENS-X.md
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# TRES ESCRITAS DO MESMO ITEM, E O EXTRATOR CONHECIA UMA
#
# O relatorio sai de uma leitura, e cada leitura escreve os campos a sua maneira:
# `- **Aponta**` em item de lista, `**Aponta:**` com dois-pontos, `**Aponta.**`
# com ponto e fora de lista. O separador entre o codigo e o titulo tambem varia
# (ponto, travessao, meio-travessao, ponto medio). Em 05/09/2026 o extrator
# devolveu ZERO correcoes sobre um relatorio de dezessete, calado, porque
# conhecia so uma das escritas. Contagem certa e conteudo vazio e o defeito mais
# caro que este programa pode ter, porque a conferencia seguinte olha o numero.
SEP = r"[ \t]*[.,:—–·|-]?[ \t]*"
RE_S = re.compile(
    r"^#{3,4} (S\d+)" + SEP + r"(.+?)\s*$\n(.*?)(?=^#{2,4} |\Z)", re.M | re.S)
RE_CAMPO = re.compile(
    r"^[-*]?[ \t]*\*\*(Tipo|Aponta|O que fazer|O que muda)[.:]?\*\*[.:]?\s*(.*?)"
    r"(?=^[-*]?[ \t]*\*\*(?:Tipo|Aponta|O que fazer|O que muda|Marca|Abrir|Ordem)"
    r"[.:]?\*\*|\Z)", re.M | re.S)
# `**SC1.** texto` ate o proximo SC ou o proximo cabecalho.
#
# SEM ANCORA DE INICIO DE LINHA, e isso e conserto de 05/09/2026: um relatorio
# escreveu sete itens seguidos na mesma linha (`**SC4.** [P464], o mesmo.
# **SC5.** [P511] e um marcador...`), e o extrator pegou so o primeiro de cada
# linha. Sete de quarenta e oito sumiram sem que nada acusasse.
#
# E O ULTIMO ITEM ENGOLIA O QUE VINHA DEPOIS DELE. O relatorio termina com a
# ressalva de alcance, que nao e cabecalho e por isso nao parava a captura: o
# item de acabamento chegava a leitura fria com a taxa de erro do proprio
# relatorio colada dentro. Medido em 05/09/2026, e foi a leitura fria que
# apanhou. A regra horizontal e a citacao em bloco tambem fecham o item.
RE_SC = re.compile(
    r"\*\*(SC\d+)[.:]?\*\*\s*(.*?)"
    r"(?=\*\*SC\d+[.:]?\*\*|^#{2,4} |^---\s*$|^> |\Z)",
    re.M | re.S)
RE_LOC = re.compile(r"\[P(\d+)\]")


def um_paragrafo(txt):
    """Junta as quebras de linha do markdown sem colar palavras."""
    return re.sub(r"\s+", " ", txt).strip()


def abrir(texto):
    """Os localizadores na ordem em que aparecem, sem repetir."""
    vistos, fora = set(), []
    for n in RE_LOC.findall(texto):
        if n not in vistos:
            vistos.add(n)
            fora.append("[P%s]" % n)
    return fora


def extrair(txt):
    """[(codigo, aponta, abrir)], na ordem do relatorio."""
    itens = []
    for m in RE_S.finditer(txt):
        cod, titulo, corpo = m.group(1), m.group(2), m.group(3)
        campos = {k: um_paragrafo(v) for k, v in RE_CAMPO.findall(corpo)}
        aponta = campos.get("Aponta", "")
        fazer = campos.get("O que fazer", "")
        if not aponta:
            continue
        cabeca = titulo if titulo.endswith((".", "?", "!")) else titulo + "."
        texto = cabeca if not fazer else cabeca + " " + fazer
        itens.append((cod, um_paragrafo(texto), abrir(aponta) or abrir(texto)))
    for m in RE_SC.finditer(txt):
        cod, corpo = m.group(1), um_paragrafo(m.group(2))
        itens.append((cod, corpo, abrir(corpo)))
    return itens


CABECA = """# Itens do relatório, na forma que a maquinaria lê

Derivado de `%s` por `anexo_do_alberto.py`. Não edite: o que se edita é o
relatório, e este arquivo se gera de novo. O texto de cada item foi copiado do
relatório por programa, e não redigido aqui.

"""


def escrever(origem, itens, saida):
    partes = [CABECA % Path(origem).name]
    for cod, aponta, locs in itens:
        partes.append("## %s\n\n**Aponta:** %s\n\n**Abrir:** %s\n"
                      % (cod, aponta, ", ".join(locs) if locs else ""))
    Path(saida).write_text("\n".join(partes), encoding="utf-8")


CONTROLE = """### S1. Um titulo qualquer

- **Tipo** Uma categoria
- **Aponta** O problema esta em [P10] e tambem em [P20].
- **O que fazer** Consertar [P10].
- **O que muda** Passa a fechar.

### S2. Outro titulo

- **Tipo** Outra categoria
- **Aponta** Nada aqui tem localizador.
- **O que fazer** Nada.

## 8. As correcoes que nao mudam nenhuma afirmacao

**SC1.** [P30] tem uma gralha.

**SC2.** [P40] e [P30] repetem a mesma legenda.

**SC3.** [P50] tem um marcador de pendencia. **SC4.** [P60], o mesmo. **SC5.** [P70], o mesmo.
"""

# A segunda escrita, com travessao no titulo e ponto no campo, fora de lista.
CONTROLE_PONTO = """### S1 — Um titulo qualquer

**Tipo:** uma categoria.

**Aponta.** O problema esta em [P10] e tambem em [P20].

**O que fazer.** Consertar [P10].

**O que muda.** Passa a fechar.

---

### S2 · Outro titulo

**Aponta:** Nada aqui tem localizador.

**O que fazer:** Nada.
"""


def provar():
    """O extrator tem de achar o que esta la e reprovar o que foi adulterado."""
    itens = extrair(CONTROLE)
    esperado = [
        ("S1", "Um titulo qualquer. Consertar [P10].", ["[P10]", "[P20]"]),
        ("S2", "Outro titulo. Nada.", []),
        ("SC1", "[P30] tem uma gralha.", ["[P30]"]),
        ("SC2", "[P40] e [P30] repetem a mesma legenda.", ["[P40]", "[P30]"]),
        # OS TRES NA MESMA LINHA, que o extrator perdia por exigir inicio de linha
        ("SC3", "[P50] tem um marcador de pendencia.", ["[P50]"]),
        ("SC4", "[P60], o mesmo.", ["[P60]"]),
        ("SC5", "[P70], o mesmo.", ["[P70]"]),
    ]
    if itens != esperado:
        sys.exit("o extrator nao le o controle:\n%r" % (itens,))
    # A MESMA COISA NA SEGUNDA ESCRITA, e ela tem de dar o mesmo resultado.
    outros = extrair(CONTROLE_PONTO)
    if [(c, t) for c, t, _ in outros] != [
            ("S1", "Um titulo qualquer. Consertar [P10]."),
            ("S2", "Outro titulo. Nada.")]:
        sys.exit("o extrator nao le a escrita com ponto e travessao:\n%r" % (outros,))
    if outros[0][2] != ["[P10]", "[P20]"]:
        sys.exit("os localizadores da segunda escrita nao foram lidos: %r" % (outros[0],))
    # adulterado: sem o campo Aponta, o item tem de sumir
    ruim = extrair(CONTROLE.replace("- **Aponta** O problema", "- **Xponta** O problema"))
    if any(c == "S1" for c, _, _ in ruim):
        sys.exit("o extrator aceita item sem o campo Aponta; nao confie nele")
    # O NIVEL DO CABECALHO. Os itens saem em `###` ou `####`, conforme a leitura
    # os aninhe ou nao sob a subsecao de custo; o `##` e cabecalho de SECAO do
    # relatorio ("## 4. As correcoes") e nao pode virar item.
    if not any(c == "S1" for c, _, _ in extrair(CONTROLE.replace("### S1.", "#### S1."))):
        sys.exit("o extrator perde o item aninhado em quarto nivel")
    ruim = extrair(CONTROLE.replace("### S1.", "## S1."))
    if any(c == "S1" for c, _, _ in ruim):
        sys.exit("o extrator toma cabecalho de secao por item; nao confie nele")
    print("controle: o extrator le os quatro itens do controle nas duas "
          "escritas, perde o item sem campo Aponta, acha o aninhado em "
          "quarto nivel e recusa o cabecalho de secao")


CONTROLE_JSON = [
    {"codigo": "C1", "titulo": "Um titulo qualquer",
     "o_que_fazer": "consertar [P10] e conferir [P20]", "abrir": ["P10", "P20"]},
    {"codigo": "S2", "titulo": "Outro titulo, ja com ponto.",
     "o_que_fazer": "", "abrir": []},
    {"codigo": "Q3", "titulo": "Uma pergunta sem localizador?",
     "o_que_fazer": "responder na defesa", "abrir": []},
]


def do_json(caminho):
    """Le a forma de maquina que as duas leituras ja produzem.

    O relatorio do Luis escreve o item em negrito na linha (`**C1. Titulo.**`),
    e nao em cabecalho (`### C1.`), de modo que o extrator de prosa devolvia
    zero itens sobre um relatorio de cinquenta e cinco. O `.itens.json` que sai
    ao lado do relatorio ja traz codigo, titulo, providencia e localizadores, e
    e a mesma forma nas duas leituras: entrar por ele resolve as duas escritas
    de uma vez, e nada aqui digita texto do relatorio.
    """
    dados = json.loads(io.open(caminho, encoding="utf-8").read())
    itens = []
    for d in dados:
        cod = (d.get("codigo") or "").strip()
        titulo = (d.get("titulo") or "").strip()
        fazer = (d.get("o_que_fazer") or "").strip()
        if not cod or not titulo:
            continue
        cabeca = titulo if titulo.endswith((".", "?", "!")) else titulo + "."
        # O RÓTULO DO CAMPO VOLTA, PORQUE SEM ELE O BALAO SE LE COMO FRASE
        # PARTIDA. Juntando titulo e providencia com um espaco, o autor le
        # "A distribuicao das 36 unidades pelas tres dimensoes: 15, 14 e 7.
        # escrever a distribuicao (...)" — diagnostico e ordem colados, o
        # segundo comecando em minuscula. Uma conferencia de margem de
        # 09/09/2026 reprovou os cinquenta e tres itens por isso, e a causa
        # nao e de redacao: e o par de campos virar uma frase so.
        texto = cabeca if not fazer else cabeca + " **O que fazer:** " + fazer
        # O IMPACTO VAI À MARGEM, E VAI COM A RAZÃO.
        #
        # O grau sozinho é etiqueta e infla; a razão se confere. Quem recebe o
        # comentário decide por onde começar lendo o que deixa de ser perguntado,
        # e não um número de 1 a 4 cujo critério ela não viu.
        grau, razao = d.get("impacto"), (d.get("impacto_razao") or "").strip()
        if grau and razao:
            texto += " **Impacto:** %s — %s" % (grau, razao.rstrip("."))

        # A ANCORA VAI ONDE A CORRECAO VAI, E NAO ONDE A PROVA ESTA.
        #
        # O `anotar_docx.py` ancora o comentario no PRIMEIRO endereco da lista,
        # e a lista vinha em ordem crescente de paragrafo. Como a prova costuma
        # estar antes do ponto a corrigir, o balao caia na prova. Medido em
        # 09/09/2026, na conferencia de margem do relatorio do trabalho K: catorze
        # de cinquenta e cinco itens ancorados fora do alvo, e o extremo mandava
        # exportar a planilha aparecendo trezentos e cinquenta paragrafos antes
        # dela.
        #
        # O `o_que_fazer` nomeia os enderecos do alvo. Eles vao na frente; os
        # demais seguem, na ordem original, porque continuam sendo a prova e o
        # item os cita.
        todos = [str(x).strip("[]") for x in (d.get("abrir") or [])]
        alvos = set(re.findall(r"\[?P?(\d+)\]?", fazer)) if fazer else set()
        na_frente = [x for x in todos if x.lstrip("P") in alvos]
        atras = [x for x in todos if x.lstrip("P") not in alvos]
        locs = ["[%s]" % x for x in (na_frente + atras)]
        itens.append((cod, um_paragrafo(texto), locs))
    return itens


def provar_json():
    import tempfile
    p = Path(tempfile.gettempdir()) / "_ctrl_itens.json"
    p.write_text(json.dumps(CONTROLE_JSON, ensure_ascii=False), encoding="utf-8")
    try:
        itens = do_json(str(p))
        esperado = [
            ("C1", "Um titulo qualquer. **O que fazer:** consertar [P10] e "
                   "conferir [P20]", ["[P10]", "[P20]"]),
            ("S2", "Outro titulo, ja com ponto.", []),
            ("Q3", "Uma pergunta sem localizador? **O que fazer:** responder "
                   "na defesa", []),
        ]
        if itens != esperado:
            sys.exit("o leitor de JSON nao le o controle:\n%r" % (itens,))
        # A REORDENACAO: a prova vem antes na lista, o alvo e citado so na
        # providencia, e mesmo assim o alvo tem de sair na frente.
        prova = [{"codigo": "S9", "titulo": "Um defeito",
                  "o_que_fazer": "reescrever [P211]",
                  "abrir": ["P35", "P106", "P211"]}]
        p.write_text(json.dumps(prova, ensure_ascii=False), encoding="utf-8")
        r = do_json(str(p))
        if r[0][2][0] != "[P211]":
            sys.exit("a ancora nao foi para o alvo da providencia: %r" % (r[0][2],))
        if sorted(r[0][2]) != ["[P106]", "[P211]", "[P35]"]:
            sys.exit("a reordenacao perdeu endereco: %r" % (r[0][2],))

        # O IMPACTO: com razao entra na margem, sem razao NAO entra.
        # Grau sozinho e etiqueta e infla; a razao se confere.
        imp = [{"codigo": "S7", "titulo": "Um defeito",
                "o_que_fazer": "cortar [P10]", "abrir": ["P10"],
                "impacto": 3, "impacto_razao": "a banca deixa de perguntar de onde saiu o numero."},
               {"codigo": "S8", "titulo": "Outro", "o_que_fazer": "cortar [P20]",
                "abrir": ["P20"], "impacto": 2}]
        p.write_text(json.dumps(imp, ensure_ascii=False), encoding="utf-8")
        r = do_json(str(p))
        if "**Impacto:** 3" not in r[0][1]:
            sys.exit("o impacto com razao nao chegou a margem: %r" % (r[0][1],))
        if "Impacto" in r[1][1]:
            sys.exit("o grau sem razao entrou na margem, e ele nao vale sozinho")

        # adulterado: item sem codigo tem de sumir, e nao virar item vazio
        ruim = json.loads(json.dumps(CONTROLE_JSON))
        ruim[0]["codigo"] = ""
        p.write_text(json.dumps(ruim, ensure_ascii=False), encoding="utf-8")
        if any(c == "C1" for c, _, _ in do_json(str(p))):
            sys.exit("o leitor de JSON aceita item sem codigo; nao confie nele")
    finally:
        try:
            p.unlink()
        except Exception:
            pass
    print("controle do JSON: le codigo, titulo, providencia e localizadores, "
          "poe na frente o endereco que a providencia nomeia, nao duplica o "
          "ponto final do titulo e recusa item sem codigo")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio", help="o RELATORIO.md, ou o .itens.json com --json")
    ap.add_argument("--json", action="store_true",
                    help="entra pelo <relatorio>.itens.json em vez da prosa; "
                         "é o caminho para o relatório cujos itens vêm em "
                         "negrito na linha, e não em cabeçalho")
    ap.add_argument("--saida")
    a = ap.parse_args()
    if a.json:
        provar_json()
        itens = do_json(a.relatorio)
        if not itens:
            sys.exit("nenhum item no JSON: confira se ele é a lista de itens")
        saida = a.saida or str(Path(a.relatorio).with_name(
            "ITENS-" + Path(a.relatorio).name.replace(".itens.json", ".md")))
        escrever(a.relatorio, itens, saida)
        sem = [c for c, _, l in itens if not l]
        print("%s: %d itens" % (saida, len(itens)))
        if sem:
            print("  sem localizador, e por isso sem âncora no .docx: %s"
                  % ", ".join(sem))
        return
    provar()
    txt = io.open(a.relatorio, encoding="utf-8").read()
    itens = extrair(txt)
    if not itens:
        sys.exit("nenhum item no relatorio: a forma mudou, e o programa nao serve mais")
    saida = a.saida or str(Path(a.relatorio).with_name(
        "ITENS-" + Path(a.relatorio).name))
    escrever(a.relatorio, itens, saida)
    sem = [c for c, _, l in itens if not l]
    print("%s: %d itens (%d S, %d SC)"
          % (saida, len(itens),
             sum(1 for c, _, _ in itens if not c.startswith("SC")),
             sum(1 for c, _, _ in itens if c.startswith("SC"))))
    if sem:
        print("  sem localizador, e por isso sem ancora no .docx: %s" % ", ".join(sem))


if __name__ == "__main__":
    main()

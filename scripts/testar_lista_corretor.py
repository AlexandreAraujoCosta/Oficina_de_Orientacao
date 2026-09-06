# -*- coding: utf-8 -*-
"""Controle do lista_corretor.py sobre as tres escritas de item que existem.

POR QUE ISTO EXISTE

Em 05/09/2026, uma entrega do Alberto saiu com 13 dos 39 comentarios EM BRANCO
na margem do .docx, e nada acusou: o programa reconhecia o codigo do item e nao
reconhecia os campos, porque o Alberto os escreve em item de lista e sem
dois-pontos (`- **Aponta**`), enquanto o Luis e a Clara os escrevem no comeco
da linha e com dois-pontos (`**Aponta:**`). Contagem certa e conteudo vazio e o
defeito mais caro que este programa pode ter, porque a conferencia seguinte olha
o numero.

Uso:  python scripts/testar_lista_corretor.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lista_corretor import RE_NEGRITO, RE_TITULO, itens  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


ALBERTO = u"""### S1. O capitulo existe apenas como titulo

- **Tipo** Secao por escrever
- **Aponta** O sumario anuncia o capitulo e [P249] descreve o que ele fara.
  A pagina traz o titulo e nada mais.
- **O que fazer** Escrever o capitulo tomando como materia-prima a comparacao
  de [P812] com [P1127].
- **O que muda** Passa a existir a resposta a pergunta de [P242].

### S2. Outro defeito

- **Tipo** Outra categoria
- **Aponta** Esta em [P300].
- **O que fazer** Consertar [P300].
- **O que muda** Fecha.

## 8. As correcoes que nao mudam nenhuma afirmacao

**SC1.** [P495] repete, na legenda do Grafico 16, o mesmo titulo da legenda do
Grafico 5 em [P365], sem dizer que este e dos elogios.

**SC2.** [P949] traz uma virgula sobrando dentro do parentese.
"""

LUIS = u"""## D7

**Aponta:** O resumo anuncia o uso de inteligencia artificial em [P87] e a
justificativa repete a promessa em [P162].

**Abrir:** [P87], [P162]

## S3

**Aponta:** O criterio de selecao nao esta declarado em [P288].

**O que fazer:** Escrever a base, o recorte e a regra de entrada.

**Abrir:** [P288]
"""


# O caso de 06/09/2026: uma secao em negrito seguida de outra em titulo. O ultimo
# item em negrito nao encontra outro negrito adiante, e antes ia ate o fim do
# arquivo, engolindo os itens seguintes e os campos deles.
MISTO = u"""## 3. As decisoes

**D5. Primeira pergunta do trabalho**

Resolve S9. Se for *sim*, entra a razao entre procedentes e ajuizadas de [P872].

**D6. Segunda pergunta do trabalho**

Resolve S1. Se for *nao*, os ordinais saem de [P853] e ficam as contagens.

**Onde os itens se atropelam.** Executar a primeira via de D2 deixa S18 sem objeto.

## 4. As correcoes

#### S1 - O numero da normalizacao esta errado

**Aponta:** A conta de [P853] usa denominador de 68 onde a autora fixou 46.

**O que fazer:** escrever 27,9% em [P853] e em [P889].

**Marca:** fixar o sujeito da afirmacao nas passagens abaixo.

**Abrir:** [P853], [P889]
"""


def ler(txt):
    fora = {}
    for cod, tit, locs, org, mrc in itens(txt, "teste", RE_NEGRITO) + \
            itens(txt, "teste", RE_TITULO):
        if cod not in fora or len(tit) > len(fora[cod][0]):
            fora[cod] = (tit, locs)
    return fora


# Varios itens de superficie no mesmo paragrafo, que e como o Alberto os escreve.
AGRUPADOS = u"""## 8. As correcoes que nao mudam nenhuma afirmacao

**SC5.** [P511] e um marcador de pendencia. **SC6.** [P513], o mesmo. **SC7.**
[P515], o mesmo.

**SC8.** [P594] traz uma anotacao de trabalho em portugues dentro de uma frase
em ingles. Resolver a pendencia e apagar a anotacao. Como ja se disse em **S9**,
a pendencia e a mesma.
"""


def agrupados():
    """Item que abre depois de ponto final, no meio do paragrafo, tem de entrar."""
    m = ler(AGRUPADOS)
    falhas = []
    for c in ("SC5", "SC6", "SC7", "SC8"):
        if c not in m:
            falhas.append("%s ficou de fora" % c)
        elif not m[c][0].strip():
            falhas.append("%s entrou com titulo vazio" % c)
    if "SC6" in m and "[P515]" in m["SC6"][1]:
        falhas.append("SC6 engoliu o localizador de SC7")
    if "S9" in m:
        falhas.append("a referencia cruzada **S9** entrou como item")
    return falhas


def misto():
    """O corpo de um item nao pode atravessar o item seguinte de outra escrita."""
    m = ler(MISTO)
    falhas = []
    if "D6" not in m:
        return ["D6 nao foi reconhecido"]
    tit, locs = m["D6"]
    if "27,9" in tit or "O que fazer" in tit:
        falhas.append("D6 engoliu a providencia de S1: %r" % tit[:90])
    if len(locs) > 4:
        falhas.append("D6 recebeu %d localizadores; sao 2 no item" % len(locs))
    if "S1" not in m:
        falhas.append("S1 se perdeu")
    elif "27,9" not in m["S1"][0]:
        falhas.append("S1 perdeu a propria providencia")
    return falhas


def main():
    a = ler(ALBERTO)
    esperados = ("S1", "S2", "SC1", "SC2")
    faltam = [c for c in esperados if c not in a]
    if faltam:
        sys.exit("o programa nao reconhece %s na escrita do Alberto" % ", ".join(faltam))
    vazios = [c for c in esperados if not a[c][0].strip()]
    if vazios:
        sys.exit("titulo VAZIO em %s: o comentario sairia em branco na margem"
                 % ", ".join(vazios))
    if "O que fazer:" not in a["S1"][0]:
        sys.exit("a providencia do Alberto nao entrou no titulo de S1")
    if "O que muda" in a["S1"][0]:
        sys.exit("o campo `O que muda` vazou para a margem, e ele e do relatorio")
    if "[P249]" not in a["S1"][1] or "[P242]" not in a["S1"][1]:
        sys.exit("os localizadores de S1 nao foram lidos: %r" % (a["S1"][1],))
    if "legenda do Grafico 16" not in a["SC1"][0]:
        sys.exit("o item de superficie do Alberto nao trouxe a prosa: %r" % (a["SC1"][0],))

    b = ler(LUIS)
    for c in ("D7", "S3"):
        if c not in b or not b[c][0].strip():
            sys.exit("a escrita do Luis parou de ser lida em %s" % c)
    if "O que fazer:" not in b["S3"][0]:
        sys.exit("a providencia do Luis nao entrou no titulo de S3")

    # ---- CONTROLE NEGATIVO: adulterado, o programa tem de perder o item
    ruim = ler(ALBERTO.replace("**SC1.**", "SC1."))
    if "SC1" in ruim:
        sys.exit("o programa aceita item sem o codigo em negrito; nao confie nele")
    ruim = ler(ALBERTO.replace("- **Aponta** O sumario", "- **Xponta** O sumario"))
    if "[P249]" in ruim.get("S1", ("", []))[0]:
        sys.exit("o programa acha campo que nao existe; nao confie nele")

    # ---- VARIOS ITENS NO MESMO PARAGRAFO
    g = agrupados()
    if g:
        sys.exit("itens agrupados num paragrafo: " + "; ".join(g))

    # ---- FRONTEIRA ENTRE AS DUAS ESCRITAS
    f = misto()
    if f:
        sys.exit("fronteira entre negrito e titulo: " + "; ".join(f))

    print("controle: as duas escritas de item sao lidas, nenhum titulo sai "
          "vazio, a providencia entra e o `O que muda` fica de fora; e o "
          "programa perde o item quando o codigo ou o campo e adulterado; e o item "
          "em negrito para no item seguinte, ainda que ele venha em titulo")


if __name__ == "__main__":
    main()

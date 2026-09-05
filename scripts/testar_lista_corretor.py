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


def ler(txt):
    fora = {}
    for cod, tit, locs, org, mrc in itens(txt, "teste", RE_NEGRITO) + \
            itens(txt, "teste", RE_TITULO):
        if cod not in fora or len(tit) > len(fora[cod][0]):
            fora[cod] = (tit, locs)
    return fora


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

    print("controle: as duas escritas de item sao lidas, nenhum titulo sai "
          "vazio, a providencia entra e o `O que muda` fica de fora; e o "
          "programa perde o item quando o codigo ou o campo e adulterado")


if __name__ == "__main__":
    main()

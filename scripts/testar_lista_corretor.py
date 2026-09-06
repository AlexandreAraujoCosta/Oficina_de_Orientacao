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
from lista_corretor import (RE_NEGRITO, RE_TITULO, itens, localizadores,  # noqa: E402
                            itens_do_json)

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


# Titulo em negrito que ocupa duas linhas, que e como o Luis escreve os itens
# longos. Sem a quebra simples no padrao, um relatorio de 31 itens devolvia seis.
QUEBRADO = u"""### 4.2 Basta corrigir a frase

**S3. O denominador declarado em [P440] desaparece no paragrafo seguinte e nao
volta ao texto.**

**Aponta:** o valor de 48,0% corre sobre outra base.

**O que fazer:** escrever a base ao lado do percentual.

**Abrir:** [P440], [P498]

**S4. A figura de duracao e apresentada pelo conjunto maior e mede o menor.**

**Aponta:** a legenda diz uma coisa e o eixo diz outra.

**Abrir:** [P452]
"""


# Titulo com italico dentro, e remissoes cruzadas em negrito no corpo do item.
# Os dois derrubaram o programa em 06/09/2026, e por caminhos opostos: o italico
# fechava o titulo antes da hora e o item sumia; a remissao contava como inicio de
# item e fechava o anterior, que perdia o campo Abrir.
ITALICO = u"""### 3.3 As decisoes

**D4. A introducao descreve o desenho executado ou o planejado?** Resolve **S14**,
**S15**, **S16** e **S17**. As quatro reescrevem paragrafos da mesma peca.
**Abrir:** [P126], [P133], [P50], [P405].

### 4.3 Pede rever o que a frase afirma

**S18. *Chamber* traduz Turma no capitulo 1 e gabinete no capitulo 4, e a colisao
cai na frase central de 4.3.1.**

**Aponta:** os dois sentidos convivem sem glossario.

**O que fazer:** fixar um par de termos, mantendo *Panel* para Turma.

**Abrir:** [P82], [P417], [P422]
"""


def bloco_json():
    """O caminho curto: itens lidos como dado, e recusa em vez de adivinhacao."""
    import json
    import tempfile
    from pathlib import Path
    falhas = []

    def escrever(dados):
        p = Path(tempfile.gettempdir()) / "_itens_autoteste.json"
        p.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        return p

    bom = escrever([
        {"codigo": "S1", "titulo": "O denominador some no parágrafo seguinte",
         "o_que_fazer": "escrever a base ao lado do percentual em [P498]",
         "marca": None, "abrir": ["P440", "P498"]},
        {"codigo": "F1", "titulo": "Um ponto forte, que não é executável",
         "o_que_fazer": None, "marca": None, "abrir": ["P100"]},
    ])
    lidos = itens_do_json(bom)
    if len(lidos) != 1:
        falhas.append("devia ler 1 item executavel e leu %d" % len(lidos))
    elif "O que fazer:" not in lidos[0][1]:
        falhas.append("a providencia nao entrou no titulo: %r" % lidos[0][1][:60])
    elif lidos[0][2] != ["[P440]", "[P498]"]:
        falhas.append("localizadores errados: %r" % (lidos[0][2],))

    # os tres casos que ele tem de RECUSAR, e nao adivinhar
    import subprocess
    import sys as _s
    for nome, dados in (
            ("codigo repetido", [{"codigo": "S1", "titulo": "a", "abrir": []},
                                 {"codigo": "S1", "titulo": "b", "abrir": []}]),
            ("titulo vazio", [{"codigo": "S1", "titulo": "", "abrir": []}]),
            ("localizador torto", [{"codigo": "S1", "titulo": "x",
                                    "abrir": ["pagina 4"]}])):
        p = escrever(dados)
        r = subprocess.run(
            [_s.executable, "-c",
             "import sys; sys.path.insert(0, r'%s');"
             "from lista_corretor import itens_do_json; itens_do_json(r'%s')"
             % (str(Path(__file__).resolve().parent), str(p))],
            capture_output=True, text=True)
        if r.returncode == 0:
            falhas.append("aceitou %s em vez de recusar" % nome)
    return falhas


def loc():
    """As tres escritas do localizador, e o que nao pode virar localizador."""
    casos = [
        (u"o trabalho registra, em P439, que 41 temas", ["[P439]"]),
        (u"com o nome de quem o subscreveu [P504, P508, P509]",
         ["[P504]", "[P508]", "[P509]"]),
        (u"abrir [P123] e a faixa [P12-P18]", ["[P123]", "[P12]", "[P18]"]),
        (u"a norma esta na p. 439 da edicao", []),
        (u"o Tema 460 e o RE 1234", []),
        (u"a sigla PGFN2011 nao e localizador", []),
    ]
    return ["%r -> %r, esperado %r" % (c[:44], localizadores(c), e)
            for c, e in casos if localizadores(c) != e]


def italico():
    """Italico no titulo nao pode fazer o item sumir, nem a remissao fechar item."""
    m = ler(ITALICO)
    falhas = []
    if "S18" not in m:
        falhas.append("S18 sumiu: o italico fechou o titulo antes da hora")
    elif "Chamber" not in m["S18"][0]:
        falhas.append("o titulo de S18 saiu sem o termo em italico: %r" % m["S18"][0][:60])
    if "D4" not in m:
        falhas.append("D4 sumiu")
    elif "[P405]" not in m["D4"][1]:
        falhas.append("D4 perdeu o Abrir: as remissoes **S15** fecharam o item")
    for c in ("S14", "S15", "S16", "S17"):
        if c in m:
            falhas.append("a remissao **%s** entrou como item" % c)
    return falhas


def quebrado():
    """Titulo que atravessa a quebra de linha tem de ser lido inteiro."""
    m = ler(QUEBRADO)
    falhas = []
    for c in ("S3", "S4"):
        if c not in m:
            falhas.append("%s ficou de fora" % c)
    if "S3" in m:
        tit = m["S3"][0]
        if "volta ao texto" not in tit:
            falhas.append("o titulo de S3 saiu cortado na quebra: %r" % tit[:70])
        if "O que fazer" not in tit:
            falhas.append("a providencia de S3 nao entrou")
        if "[P452]" in m["S3"][1]:
            falhas.append("S3 engoliu o localizador de S4")
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

    # ---- O BLOCO ESTRUTURADO
    bj = bloco_json()
    if bj:
        sys.exit("leitor do bloco de itens: " + "; ".join(bj))

    # ---- AS TRES ESCRITAS DO LOCALIZADOR
    lo = loc()
    if lo:
        sys.exit("leitor de localizadores: " + "; ".join(lo))

    # ---- ITALICO NO TITULO E REMISSAO CRUZADA EM NEGRITO
    it = italico()
    if it:
        sys.exit("italico e remissao: " + "; ".join(it))

    # ---- TITULO QUE ATRAVESSA A QUEBRA DE LINHA
    q = quebrado()
    if q:
        sys.exit("titulo em duas linhas: " + "; ".join(q))

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

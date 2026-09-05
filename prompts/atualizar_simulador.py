# -*- coding: utf-8 -*-
"""Injeta na pagina do simulador os dois prompts, lidos do BANCA.md.

POR QUE ISTO EXISTE. O texto da sessao vivia em dois lugares: no objeto
`P` da pagina e no `prompts/BANCA.md`, mantidos a mao. Em 05/09/2026 os
dois ainda batiam, conferidos caractere a caractere; o risco e que o
primeiro conserto que passar por um so separe os dois sem aviso, e a
versao errada e sempre a que alguem esta lendo. As outras duas oficinas
ja injetam o prompt do arquivo na pagina, e esta passa a fazer o mesmo.

O ARQUIVO MANDA. O BANCA.md e a fonte; a pagina e derivada.

Uso:  python atualizar_simulador.py
"""
import io
import re
import sys

PASTA = "D:/Claude/Oficina_de_Orientacao/prompts/"
FONTE = PASTA + "BANCA.md"
PAGINA = PASTA + "simulador.html"

CORTE = "\n---\n\n## Argui\u00e7\u00e3o por um examinador s\u00f3\n\n"


def partes(texto):
    """(sessao completa, arguicao por um examinador so), sem os cabecalhos."""
    i = texto.find(CORTE)
    if i < 0:
        sys.exit("nao achei o corte entre os dois prompts no BANCA.md")
    cabeca = texto.find("\n---\n")          # fim do cabecalho do arquivo
    if cabeca < 0 or cabeca > i:
        sys.exit("nao achei o fim do cabecalho do BANCA.md")
    completa = texto[cabeca + len("\n---\n"):i].strip()
    unico = texto[i + len(CORTE):].strip()
    return completa, unico


def injetar(pagina, chave, valor):
    """Troca o template literal de `chave` no objeto P da pagina."""
    marca = chave + ": `"
    i = pagina.find(marca)
    if i < 0:
        sys.exit("nao achei %s no objeto P" % chave)
    a = i + len(marca)
    b = a
    while True:
        b = pagina.find("`", b)
        if b < 0:
            sys.exit("template literal de %s sem fim" % chave)
        if pagina[b - 1] != "\\":
            break
        b += 1
    # crase e cifrao escapam dentro de template literal
    seguro = valor.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return pagina[:a] + seguro + pagina[b:]


def main():
    fonte = io.open(FONTE, encoding="utf-8").read()
    completa, unico = partes(fonte)
    pagina = io.open(PAGINA, encoding="utf-8").read()
    antes = len(pagina)

    pagina = injetar(pagina, "ps", completa)
    pagina = injetar(pagina, "pu", unico)
    io.open(PAGINA, "w", encoding="utf-8").write(pagina)

    print("BANCA.md: %d caracteres | sessao completa %d | examinador so %d"
          % (len(fonte), len(completa), len(unico)))
    print("simulador.html: %d -> %d caracteres" % (antes, len(pagina)))

    # ---- CONTROLE POSITIVO: o que a pagina entrega tem de ser o que o
    # arquivo diz, e o conferidor tem de reprovar uma copia adulterada.
    def extrair(p, chave):
        marca = chave + ": `"
        i = p.find(marca) + len(marca)
        j = i
        while True:
            j = p.find("`", j)
            if p[j - 1] != "\\":
                break
            j += 1
        return p[i:j].replace("\\`", "`").replace("\\${", "${").replace("\\\\", "\\")

    conf = io.open(PAGINA, encoding="utf-8").read()
    for chave, esperado in (("ps", completa), ("pu", unico)):
        if extrair(conf, chave) != esperado:
            sys.exit("o %s da pagina nao reproduz o do arquivo" % chave)
    adulterado = injetar(conf, "ps", completa + " XXX")
    if extrair(adulterado, "ps") == completa:
        sys.exit("o conferidor nao percebe uma adulteracao; nao confie nele")
    print("controle: os dois prompts da pagina reproduzem o arquivo, e o "
          "conferidor reprova uma copia adulterada")


if __name__ == "__main__":
    main()

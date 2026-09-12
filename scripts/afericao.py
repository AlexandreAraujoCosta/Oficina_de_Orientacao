# -*- coding: utf-8 -*-
"""O estado de aferição de cada programa, impresso por ele mesmo ao rodar.

POR QUE ISTO EXISTE

Em 09/09/2026, sete programas foram escritos num dia e quatro produziram numero
errado ou acusacao falsa no primeiro uso real. O que separou o que funcionou do
que falhou nao foi ter controle positivo: os quatro tinham. Foi **a saida ter
sido conferida contra um numero que nao saiu do proprio programa**.

    base_das_figuras.py   extraiu 136 valores lidos; o relatorio declarava 136
    planejar_leitura.py   ajustado em todos os seis pontos, validado em nenhum
    conferir_figura_vs_texto.py   controle sintetico passando; 3 acusacoes
                                  reais, 3 falsas

Este modulo nao afere nada. Ele **imprime o que se sabe da afericao**, ao lado do
resultado, para que ninguem confunda numero calculado com numero conferido. O
registro fica em `AFERICOES.md`, e programa sem linha la diz que nunca foi
aferido.

COMO USAR

No fim do `main()` de qualquer programa:

    from afericao import selo
    selo(__file__)

E onde ele imprimir projecao, contagem transformada ou acusacao:

    print("  26,7 min%s" % afericao.margem(__file__))

O ARQUIVO

`AFERICOES.md` e markdown com uma tabela. Cada linha:

    | programa.py | contra que número externo | quando | resultado |

Editar a mao e o esperado: quem afere escreve o que aferiu. Este modulo so le.
"""
import io
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "AFERICOES.md"

RE_LINHA = re.compile(r"^\|\s*([A-Za-z_0-9]+\.py)\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$", re.M)


def _tabela():
    if not REGISTRO.exists():
        return {}
    fora = {}
    for m in RE_LINHA.finditer(io.open(str(REGISTRO), encoding="utf-8").read()):
        nome = m.group(1)
        fora.setdefault(nome, []).append(
            tuple(x.strip() for x in (m.group(2), m.group(3), m.group(4))))
    return fora


def estado(caminho):
    """(nome, [(contra, quando, resultado)]). Lista vazia = nunca aferido."""
    nome = Path(caminho).name
    return nome, _tabela().get(nome, [])


def margem(caminho):
    """Sufixo curto para colar ao lado de um número. Vazio nunca."""
    nome, linhas = estado(caminho)
    if not linhas:
        return "  [nunca aferido]"
    ruins = [l for l in linhas if re.search(r"falsa|errad|não confere|nao confere",
                                            l[2], re.I)]
    if ruins:
        return "  [aferição: %s]" % ruins[-1][2][:60]
    return "  [aferido: %s]" % linhas[-1][2][:60]


def selo(caminho, silencioso=False):
    """Imprime o estado de aferição do programa. Devolve True se já foi aferido."""
    nome, linhas = estado(caminho)
    if not linhas:
        if not silencioso:
            print("\n  AFERIÇÃO: %s nunca foi conferido contra número externo." % nome)
            print("  O que ele imprime é cálculo, e não medida conferida.")
            print("  Registre em AFERICOES.md quando o conferir.")
        return False
    if not silencioso:
        print("\n  AFERIÇÃO de %s:" % nome)
        for contra, quando, res in linhas:
            print("    %s — %s (%s)" % (res, contra, quando))
    return True


# ---------------------------------------------------------------- contagem

def conserva(antes, depois, nome, permitido=0):
    """Recusa encolhimento não pedido de um conjunto.

    O sincronizador do `.itens.json` levou 55 itens e devolveu 48 porque
    descartava o que nao sabia encontrar. Programa que transforma conjunto
    imprime os dois numeros e para quando a conta nao fecha.
    """
    a, b = len(antes) if hasattr(antes, "__len__") else int(antes), \
           len(depois) if hasattr(depois, "__len__") else int(depois)
    print("  %s: %d entraram, %d saíram" % (nome, a, b))
    if b < a - permitido:
        print("\n  PAREI: %d item(ns) sumiram e nada pediu que sumissem." % (a - b),
              file=sys.stderr)
        print("  Programa que não acha um registro conserva o registro; "
              "descartar é o defeito\n  que este teste existe para pegar.",
              file=sys.stderr)
        raise SystemExit(2)
    return b


def autoteste():
    falhas = []
    # o selo tem de dizer "nunca aferido" para nome que nao esta no registro
    _, l = estado("programa_que_nao_existe_xyz.py")
    if l:
        falhas.append("achou aferição de programa inexistente")
    if "nunca aferido" not in margem("programa_que_nao_existe_xyz.py"):
        falhas.append("não marca como não aferido o que não está no registro")
    # conserva tem de PARAR quando encolhe
    try:
        conserva(range(55), range(48), "teste")
        falhas.append("aceitou 55 entrarem e 48 saírem")
    except SystemExit:
        pass
    # e tem de deixar passar quando nao encolhe
    try:
        conserva(range(10), range(10), "teste")
    except SystemExit:
        falhas.append("parou onde nada sumiu")
    if falhas:
        for f in falhas:
            print("  AUTOTESTE FALHOU: %s" % f, file=sys.stderr)
        raise SystemExit(2)
    print("  autoteste: marca o não aferido, para quando o conjunto encolhe, "
          "e deixa passar quando não encolhe.")


if __name__ == "__main__":
    autoteste()
    selo(__file__)
    print("\n  Registro: %s" % REGISTRO)
    t = _tabela()
    print("  %d programa(s) com linha de aferição." % len(t))
    for nome in sorted(t):
        print("    %-32s %s" % (nome, t[nome][-1][2][:50]))

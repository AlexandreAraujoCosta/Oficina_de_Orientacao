# -*- coding: utf-8 -*-
"""Tira do caminho o CLAUDE.md e a memoria, para medir sem eles. E repoe.

POR QUE ISTO EXISTE

O proprio CLAUDE.md registra o confundidor: os subagentes herdam o arquivo, e uma
sessao nova tambem o carrega, de modo que quando uma leitura cumpre a disciplina
sem que o prompt a peca, isso nao mede o prompt, mede o prompt mais as regras
desta casa. Em 06/09/2026 o arquivo tinha 27.938 bytes e trazia varios casos
concretos deste acervo, entre eles os que sairam das medicoes do proprio dia.

Para medir o que um prompt produz sozinho, os dois precisam sair do caminho. Nao
ha chave de configuracao que os desligue: o que ha e renomear.

O QUE ELE NAO RESOLVE

O prompt do sistema continua, e com ele as instrucoes de como o assistente
trabalha. "Sem contexto nenhum" nao existe; o que este programa da e **sem as
regras que nos dois escrevemos**.

Uso:
    python scripts/sem_regras.py --tirar     antes de abrir a sessao de teste
    python scripts/sem_regras.py --repor     assim que o teste acabar
    python scripts/sem_regras.py --estado    diz onde as coisas estao

Depois de `--tirar`, **abra uma sessao nova**: a sessao ja aberta continua com o
arquivo no contexto dela.
"""
import argparse
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CASA = Path.home() / ".claude"
SUFIXO = ".fora-para-medir"

# So estes dois. Nao mexo em credencial, plugin nem configuracao.
ALVOS = [
    CASA / "CLAUDE.md",
    CASA / "projects" / "D--Claude-TCC" / "memory" / "MEMORY.md",
]


def estado():
    fora = []
    for p in ALVOS:
        guardado = p.with_name(p.name + SUFIXO)
        fora.append((p, p.exists(), guardado.exists()))
    return fora


def imprimir():
    print("  arquivo                                        no lugar   guardado")
    for p, aqui, guard in estado():
        print("  %-46s %-10s %s" % (p.name + "  (" + p.parent.name + ")",
                                    "sim" if aqui else "NAO", "sim" if guard else "nao"))


def tirar():
    st = estado()
    if any(g for _, _, g in st):
        print("  ja ha arquivo guardado: reponha antes de tirar de novo.")
        imprimir()
        return 1
    faltando = [p for p, aqui, _ in st if not aqui]
    if faltando:
        print("  nao achei: %s" % ", ".join(str(p) for p in faltando))
        print("  nao mexo em nada enquanto os dois nao estiverem no lugar.")
        return 2
    for p, _, _ in st:
        p.rename(p.with_name(p.name + SUFIXO))
        print("  guardado: %s" % p.name)
    print("\n  ABRA UMA SESSAO NOVA. A que estiver aberta ja tem o arquivo no")
    print("  contexto dela, e nao adianta ter tirado do disco.")
    print("  Ao terminar:  python scripts/sem_regras.py --repor")
    return 0


def repor():
    st = estado()
    guardados = [(p, p.with_name(p.name + SUFIXO)) for p, _, g in st if g]
    if not guardados:
        print("  nao ha nada guardado.")
        imprimir()
        return 1
    for p, g in guardados:
        if p.exists():
            print("  %s existe e o guardado tambem: nao sobrescrevo, resolva a mao."
                  % p.name)
            return 2
    for p, g in guardados:
        g.rename(p)
        print("  reposto: %s" % p.name)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tirar", action="store_true")
    g.add_argument("--repor", action="store_true")
    g.add_argument("--estado", action="store_true")
    a = ap.parse_args()
    if a.estado:
        imprimir()
        return 0
    return tirar() if a.tirar else repor()


if __name__ == "__main__":
    sys.exit(main())

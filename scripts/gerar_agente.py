# -*- coding: utf-8 -*-
"""Faz do prompt de leitura um tipo de agente, para que o pedido nao entre na leitura.

POR QUE ISTO EXISTE

Medido ao longo de 06/09/2026. Cada vez que uma leitura era disparada, eu escrevia
um pedido, e o pedido variava: umas vezes trazia um bloco de disciplina com
transcricao, busca de controle e alcance declarado; outras vezes repetia as
exigencias que o proprio prompt ja faz; outras nao. Duas consequencias, e as duas
foram medidas.

A primeira: **duas rodadas do mesmo prompt deixavam de ser comparaveis**, porque o
que variava era o meu texto. Uma rodada de medicao teve de ser refeita por isso,
com o braco novo recebendo tres exigencias repetidas que o braco de controle nao
recebeu.

A segunda: **o pedido media a si mesmo**. Quando o bloco de disciplina esta no
pedido, o que a leitura cumpre nao diz nada sobre o prompt publicado, que e o que
roda na maquina de quem nao escreveu o pedido.

Com o prompt virando corpo do agente, o pedido encolhe para o caminho do trabalho
e o caminho da saida, e a leitura passa a ser reproduzivel: mesmo tipo de agente,
mesmo prompt, pedido de duas linhas.

O QUE ELE NAO RESOLVE

O `CLAUDE.md` e a memoria continuam sendo injetados por fora, e o proprio
`CLAUDE.md` registra que os subagentes o herdam. Para rodar sem eles, o caminho
continua sendo `scripts/sem_regras.py`.

Uso:
    python scripts/gerar_agente.py                      gera os tipos conhecidos
    python scripts/gerar_agente.py --tambem D:\\Claude\\TCC
    python scripts/gerar_agente.py --conferir           so diz se estao em dia
"""
import argparse
import io
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent

# nome do tipo -> (prompt de origem, modelo, descricao para quem escolhe)
TIPOS = {
    "alberto": (
        "prompts/ALBERTO.md",
        "opus",
        "A analise geral de um trabalho academico completo: le o trabalho inteiro, "
        "confere os numeros contra as figuras, examina a qualidade das inferencias "
        "e devolve um relatorio com itens enderecados por paragrafo. Use quando o "
        "pedido for uma leitura do Alberto, uma analise geral, ou um parecer sobre "
        "dissertacao, tese ou monografia ja escrita.",
    ),
}

FERRAMENTAS = "Read, Write, Edit, Glob, Grep, Bash, PowerShell, WebSearch, WebFetch"

CABECA = """---
name: %s
description: %s
tools: %s
model: %s
---

<!-- GERADO por scripts/gerar_agente.py a partir de %s.
     NAO EDITE ESTE ARQUIVO: edite o prompt de origem e gere de novo.
     Editar aqui cria duas versoes do mesmo prompt, que divergem em silencio. -->

"""


def gerar(nome, origem, modelo, descricao):
    texto = io.open(str(RAIZ / origem), encoding="utf-8").read()
    return (CABECA % (nome, descricao, FERRAMENTAS, modelo, origem)) + texto


def destinos(extra):
    fora = [RAIZ / ".claude" / "agents"]
    if extra:
        fora.append(Path(extra) / ".claude" / "agents")
    return fora


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tambem", help="outro projeto onde o tipo também deve existir")
    ap.add_argument("--conferir", action="store_true",
                    help="não escreve; diz se o arquivo gerado está em dia")
    a = ap.parse_args()

    problemas = 0
    for nome, (origem, modelo, desc) in TIPOS.items():
        conteudo = gerar(nome, origem, modelo, desc)
        for pasta in destinos(a.tambem):
            alvo = pasta / (nome + ".md")
            if a.conferir:
                atual = alvo.read_text(encoding="utf-8") if alvo.exists() else ""
                if atual != conteudo:
                    problemas += 1
                    print("  DESATUALIZADO: %s" % alvo)
                else:
                    print("  em dia: %s" % alvo)
                continue
            pasta.mkdir(parents=True, exist_ok=True)
            alvo.write_text(conteudo, encoding="utf-8")
            print("  %s  (%d palavras de %s)"
                  % (alvo, len(conteudo.split()), origem))

    if a.conferir:
        if problemas:
            print("\n  Gere de novo: python scripts/gerar_agente.py")
        return 1 if problemas else 0

    print("\n  O pedido de uma leitura passa a ser só o caminho do trabalho e o da")
    print("  saída. Tudo o mais está no corpo do agente, que é o prompt publicado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

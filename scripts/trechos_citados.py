# -*- coding: utf-8 -*-
"""Poe ao lado de uma mensagem ao autor o texto dos paragrafos que ela cita.

POR QUE ISTO EXISTE

O autor tem o .docx, que nao traz numero de paragrafo, e `[P58]` nao lhe diz
nada. Medido na primeira conversa do Warat, em 18/09/2026: na terceira pergunta
quem fazia o papel do autor parou a conversa por isso, e os tres leitores de
compreensibilidade da rodada de 12/09 ja tinham avisado o mesmo sobre os itens.

A mensagem e escrita pelo modelo com localizadores; o texto do paragrafo entra
aqui, copiado da extracao, e nunca digitado. Localizador isolado recebe o
paragrafo inteiro. Intervalo de mais de quatro paragrafos recebe os titulos de
secao que ele contem, porque 56 paragrafos nao sao leitura de conversa.

Duas versoes deste programa erraram antes de acertar, e o autoteste guarda as
duas: a regra de titulo procurava numero no comeco do texto, e na extracao o
titulo vem como cabecalho (`### [P40] 3.1 ...`).

Uso:
    python scripts/trechos_citados.py <extracao.txt> <mensagem.txt>
    python scripts/trechos_citados.py --autoteste
"""
import io
import os
import re
import sys
import tempfile

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# So conta como localizador o que esta entre colchetes. Sem colchete, "P13" e o
# codigo de um item da leitura 2, e nao o paragrafo 13: a critica fria de
# 18/09/2026 achou o programa trocando um pelo outro.
RE_ENTRE = re.compile(r"\[(P\d+(?:\s*(?:,|a|–|-|to|e)\s*P?\d+)*)\]"
                      r"(?:\s*(?:a|–|-|to)\s*\[P(\d+)\])?")


def localizadores(msg):
    """Pares (inicio, fim) na ordem em que aparecem."""
    out = []
    for m in RE_ENTRE.finditer(msg):
        dentro, fim_fora = m.group(1), m.group(2)
        partes = re.split(r"\s*(?:,|\be\b)\s*", dentro)
        for parte in partes:
            nums = [int(x) for x in re.findall(r"\d+", parte)]
            if not nums:
                continue
            out.append((nums[0], nums[-1]) if len(nums) > 1 else (nums[0], nums[0]))
        if fim_fora:
            a = out.pop()[0]
            out.append((a, int(fim_fora)))
    return out


def ler(ext):
    par, titulos = {}, set()
    for linha in io.open(ext, encoding="utf-8"):
        m = re.match(r"(#+\s*)?\[P(\d+)\]\s?(.*)", linha)
        if m:
            par[int(m.group(2))] = m.group(3).strip()
            if m.group(1):
                titulos.add(int(m.group(2)))
    return par, titulos


def trechos(par, titulos, msg):
    vistos, saida = set(), []
    for a, b in localizadores(msg):
        if (a, b) in vistos:
            continue
        vistos.add((a, b))
        if b - a <= 4:
            for p in range(a, b + 1):
                saida.append("[P%d] %s" % (p, par[p]) if p in par
                             else "[P%d] (sem texto na extração)" % p)
        else:
            tit = ["   [P%d] %s" % (p, par[p]) for p in range(a, b + 1) if p in titulos]
            saida.append("[P%d a P%d]: %d parágrafos; títulos de seção no intervalo:"
                         % (a, b, b - a + 1))
            saida.extend(tit or ["   (nenhum título no intervalo)"])
    return saida


def autoteste():
    ext = ("[P1] Primeiro paragrafo do corpo.\n"
           "### [P2] 3.1 Primeira secao\n"
           "[P3] Texto da secao.\n[P4] Mais texto.\n[P5] Ainda.\n[P6] Mais.\n"
           "### [P7] 3.2. Segunda secao\n[P8] Fim.\n")
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(ext)
    f.close()
    par, tit = ler(f.name)
    os.unlink(f.name)
    falhas = []
    s = trechos(par, tit, "veja [P1] e [P9999]")
    if s != ["[P1] Primeiro paragrafo do corpo.", "[P9999] (sem texto na extração)"]:
        falhas.append("isolado ou inexistente errado: %r" % s)
    s = trechos(par, tit, "o capitulo [P2 a P8]")
    if "[P2] 3.1 Primeira secao" not in " ".join(s) or "[P7] 3.2." not in " ".join(s):
        falhas.append("titulo em cabecalho nao reconhecido no intervalo: %r" % s)
    if "[P3]" in " ".join(s):
        falhas.append("intervalo longo trouxe paragrafo de corpo: %r" % s)
    # o modelo escreve [P58, P63]; no teste de 18/09 isso foi trocado a mao por
    # achar que o programa nao lia a virgula, e ele le
    s = trechos(par, tit, "[P3, P4]")
    if s != ["[P3] Texto da secao.", "[P4] Mais texto."]:
        falhas.append("lista com virgula nao lida: %r" % s)
    # codigo de item sem colchete nao e paragrafo
    s = trechos(par, tit, "o item P3 da leitura 2 e o [P1]")
    if s != ["[P1] Primeiro paragrafo do corpo."]:
        falhas.append("leu codigo de item sem colchete como paragrafo: %r" % s)
    s = trechos(par, tit, "de [P2] a [P8]")
    if "[P2 a P8]" not in " ".join(s):
        falhas.append("intervalo entre dois colchetes nao lido: %r" % s)
    return falhas


def main():
    f = autoteste()
    if sys.argv[1:] == ["--autoteste"]:
        print("autoteste: " + ("passou (isolado, inexistente, intervalo com titulo em cabecalho)"
                               if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    if f:
        print("o proprio programa esta quebrado: " + "; ".join(f))
        return 2
    if len(sys.argv) != 3:
        print(__doc__.split("Uso:")[1])
        return 2
    par, tit = ler(sys.argv[1])
    msg = io.open(sys.argv[2], encoding="utf-8").read()
    s = trechos(par, tit, msg)
    print(msg.strip())
    if s:
        print("\n---\nTrechos citados, copiados da extração:\n")
        print("\n\n".join(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())

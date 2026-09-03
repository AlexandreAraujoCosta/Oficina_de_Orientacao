# -*- coding: utf-8 -*-
"""Escreve a tabela gerada nas regras globais e no instrumento, entre marcas."""
import os
import re
import subprocess
import sys
from pathlib import Path

# O filho herda a codificacao do console (cp1252 nesta maquina) e a tabela sai com
# acento; lida como utf-8, a saida quebra e `stdout` volta None. Medido em
# 03/09/2026: o sincronizador estava assim, e a tabela nao era atualizavel.
_env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
_p = subprocess.run([sys.executable, "-X", "utf8", "scripts/legibilidade.py", "--tabela", "x"],
                    capture_output=True, text=True, encoding="utf-8", env=_env)
assert _p.stdout, "legibilidade.py --tabela nao devolveu nada: %s" % (_p.stderr or "")[:300]
tab = _p.stdout.strip()
assert tab.startswith("| Escreve-se"), tab[:80]

INI = "<!-- lista-decalques:inicio — gerada por `python scripts/legibilidade.py --tabela`, não editar à mão -->"
FIM = "<!-- lista-decalques:fim -->"
BLOCO = INI + "\n\n" + tab + "\n\n" + FIM

# 03/09/2026: o LUIS.md foi aposentado e a tabela passou ao passo de redacao
# do pipeline. Alvo antigo: "prompts/LUIS.md".
# O ALBERTO.md fica de fora de proposito: ele cola numa conversa de chat, e ali
# a tabela de 23 linhas e peso morto. A lista curta em prosa que ele traz e a
# forma certa para aquele uso, e se mantem a mao.
ALVOS = ["C:/Users/alexa/.claude/CLAUDE.md",
         "prompts/leituras/6-TRIAGEM-E-REDACAO.md"]
for caminho in ALVOS:
    p = Path(caminho)
    s = p.read_text(encoding="utf-8")
    if INI in s:
        s = re.sub(re.escape(INI) + r".*?" + re.escape(FIM), BLOCO, s, flags=re.S)
    else:
        # substitui a tabela escrita a mao, que comeca no cabecalho de quatro colunas
        m = re.search(r"\| Escreve-se \| Vem de \| Em português \| Legítimo quando \|.*?"
                      r"(?=\n\n)", s, re.S)
        if not m:
            print("tabela não encontrada em", p.name)
            continue
        s = s[:m.start()] + BLOCO + s[m.end():]
    p.write_text(s, encoding="utf-8")
    n = len(re.findall(r"^\| ", tab, re.M)) - 1
    print("%-16s tabela com %d entradas" % (p.name, n))

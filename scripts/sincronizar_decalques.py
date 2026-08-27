# -*- coding: utf-8 -*-
"""Escreve a tabela gerada nas regras globais e no instrumento, entre marcas."""
import re
import subprocess
import sys
from pathlib import Path

tab = subprocess.run([sys.executable, "scripts/legibilidade.py", "--tabela", "x"],
                     capture_output=True, text=True, encoding="utf-8").stdout.strip()
assert tab.startswith("| Escreve-se"), tab[:80]

INI = "<!-- lista-decalques:inicio — gerada por `python scripts/legibilidade.py --tabela`, não editar à mão -->"
FIM = "<!-- lista-decalques:fim -->"
BLOCO = INI + "\n\n" + tab + "\n\n" + FIM

ALVOS = ["C:/Users/alexa/.claude/CLAUDE.md", "prompts/LUIS.md"]
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

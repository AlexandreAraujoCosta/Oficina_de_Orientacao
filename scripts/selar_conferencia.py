# -*- coding: utf-8 -*-
"""Sela a conferência com o hash da versão do relatório que ela leu.

POR QUE ISTO EXISTE

A montagem exigia que o arquivo da conferência fosse mais NOVO que o relatório.
Data de modificação não prova leitura nenhuma: em 03/09/2026 eu passei pela trava
copiando o arquivo da conferência para dentro das pastas dos três trabalhos. A
data ficou nova, e nenhuma leitura nova aconteceu.

O selo não impede a mesma fraude, e não é para isso que serve. Ele transforma um
ACIDENTE em ATO: copiar arquivo, salvar no editor, tocar no arquivo, tudo isso
atualiza a data sem que ninguém queira; nada disso escreve um selo. Quem sela tem
de rodar este programa apontando para as duas coisas, e aí a passagem pela trava
é deliberada e fica registrada no próprio arquivo, com data e hash.

O hash é do relatório INTEIRO. Se uma vírgula mudar depois da conferência, o selo
não confere mais, que é exatamente o que se quer: a conferência certificou aquele
texto, e não o seguinte.

Uso:
    python selar_conferencia.py <conferencia.md> <relatorio.md>
    python selar_conferencia.py <conferencia.md> <relatorio.md> --conferir
"""
import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RE_SELO = re.compile(r"^<!--\s*selo:\s*sha256=([0-9a-f]{64})\s+de=(\S+)\s+em=(\S+)\s*-->\s*$",
                     re.M)


def digestao(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def selo_de(texto):
    m = RE_SELO.search(texto)
    return m.groups() if m else None


def main():
    ap = argparse.ArgumentParser(description="Sela a conferência com o hash do relatório.")
    ap.add_argument("conferencia")
    ap.add_argument("relatorio")
    ap.add_argument("--conferir", action="store_true",
                    help="só confere o selo existente, sem escrever")
    a = ap.parse_args()

    conf, rel = Path(a.conferencia), Path(a.relatorio)
    for p in (conf, rel):
        if not p.exists():
            sys.exit("não encontrei %s" % p)

    atual = digestao(rel)
    texto = conf.read_text(encoding="utf-8")
    achado = selo_de(texto)

    if a.conferir:
        if not achado:
            print("  %s: SEM SELO." % conf.name)
            print("  Sele com: python selar_conferencia.py %s %s" % (conf.name, rel.name))
            return 1
        sha, de, em = achado
        if sha != atual:
            print("  %s: selo NÃO confere." % conf.name)
            print("  A conferência leu outra versão de %s." % rel.name)
            print("  selo:  %s (selado em %s)" % (sha[:16], em))
            print("  atual: %s" % atual[:16])
            return 1
        print("  %s: selo confere (%s, selado em %s)" % (conf.name, sha[:16], em))
        return 0

    agora = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    linha = "<!-- selo: sha256=%s de=%s em=%s -->" % (atual, rel.name, agora)
    if achado:
        texto = RE_SELO.sub(linha, texto, count=1)
        print("  selo atualizado em %s" % conf.name)
    else:
        texto = texto.rstrip() + "\n\n" + linha + "\n"
        print("  selo escrito em %s" % conf.name)
    conf.write_text(texto, encoding="utf-8")
    print("  %s = %s" % (rel.name, atual[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Acusa nome de quem submeteu trabalho em tudo o que vai para o GitHub.

POR QUE ISTO EXISTE

O repositorio traz a maquinaria e nunca o material, e a POLITICA.md diz que as
medicoes identificam o trabalho pelo genero e pelo tamanho, jamais por quem o
escreveu. A regra estava escrita e nada a aplicava: em 18/09/2026 um push levou ao
GitHub cerca de 120 mencoes a oito pessoas, em fichas de mudanca, protocolos de
rodada e comentarios de script ("medido na dissertacao de Fulana"), acumuladas em
75 commits que ninguem conferiu.

A LISTA NAO ESTA AQUI

Os nomes ficam num arquivo fora do repositorio, no computador de quem mantem a
Oficina: `~/.oficina/nomes.txt`, ou o caminho em OFICINA_NOMES. Uma linha por
pessoa, `codigo | forma usada em prosa | variantes separadas por virgula`. Sem o
arquivo o programa para: passar em silencio seria o defeito que ele existe para
impedir. A comparacao ignora caixa e acento ("Iracema" pega "iracema" e "Iracéma").

Uso:
    python scripts/conferir_nomes.py                 os arquivos rastreados, como estao no disco
    python scripts/conferir_nomes.py --preparado     o que esta no indice (para o gancho pre-commit)
    python scripts/conferir_nomes.py --mensagem ARQ  a mensagem de um commit (gancho commit-msg)
    python scripts/conferir_nomes.py --historico     todos os commits e mensagens ja feitos
    python scripts/conferir_nomes.py --autoteste
"""
import io
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LISTA = Path(os.environ.get("OFICINA_NOMES") or (Path.home() / ".oficina" / "nomes.txt"))


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def ler_lista(caminho=LISTA):
    if not Path(caminho).exists():
        raise SystemExit("Sem a lista de nomes em %s: nada foi conferido.\n"
                         "Crie o arquivo (uma linha por pessoa: codigo | nome | variantes) "
                         "ou aponte OFICINA_NOMES para ele." % caminho)
    formas = {}
    for linha in io.open(caminho, encoding="utf-8"):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        partes = [x.strip() for x in linha.split("|")]
        if len(partes) < 2:
            continue
        cod = partes[0]
        for f in [partes[1]] + (partes[2].split(",") if len(partes) > 2 else []):
            f = f.strip()
            if f:
                formas[sem_acento(f)] = cod
    return formas


def padrao(formas):
    alt = sorted((re.escape(f).replace(r"\ ", r"\s*") for f in formas), key=len, reverse=True)
    return re.compile(r"(?<![a-z0-9])(" + "|".join(alt) + r")(?![a-z0-9])")


def achar(texto, rx):
    """[(numero da linha, forma achada)]."""
    out = []
    for n, linha in enumerate(texto.splitlines(), 1):
        for m in rx.finditer(sem_acento(linha)):
            out.append((n, m.group(1)))
    return out


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout


def binario(dados):
    return "\0" in dados[:4000]


def conferir_arquivos(rx, preparado=False):
    achados = []
    if preparado:
        nomes = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").split("\n")
    else:
        nomes = git("ls-files").split("\n")
    for f in filter(None, nomes):
        for n, forma in achar(f, rx):
            achados.append((f, 0, forma))
        if preparado:
            texto = git("show", ":" + f)
        else:
            try:
                texto = io.open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
        if binario(texto):
            continue
        for n, forma in achar(texto, rx):
            achados.append((f, n, forma))
    return achados


def autoteste():
    import tempfile
    t = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    t.write("# comentario\nZ | Iracêma Fictícia | iracema\nQ | Beto | \n")
    t.close()
    formas = ler_lista(t.name)
    os.unlink(t.name)
    rx = padrao(formas)
    f = []
    casos = [("medido na dissertação da Iracema Ficticia", True), ("em `iracema-v3.docx`", True),
             ("o relatório do Beto", True), ("Betoneira e trabalho Z", False),
             ("a dissertação Z, de 140 páginas", False), ("IRACÊMA", True)]
    for texto, esperado in casos:
        if bool(achar(texto, rx)) != esperado:
            f.append("%r: esperava %s" % (texto, "acusar" if esperado else "passar"))
    try:
        ler_lista("/caminho/que/nao/existe.txt")
        f.append("sem lista, seguiu em silêncio")
    except SystemExit:
        pass
    return f


def main():
    a = sys.argv[1:]
    f = autoteste()
    if a == ["--autoteste"]:
        print("autoteste: " + ("passou (acento, nome de arquivo, palavra maior, código e lista ausente)"
                               if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    if f:
        print("o próprio conferidor está quebrado: " + "; ".join(f))
        return 2
    formas = ler_lista()
    rx = padrao(formas)
    if a[:1] == ["--mensagem"]:
        texto = io.open(a[1], encoding="utf-8", errors="replace").read()
        achados = [("mensagem do commit", n, x) for n, x in achar(texto, rx)]
    elif a == ["--historico"]:
        achados = []
        for n, x in achar(git("log", "--all", "--format=%H %s%n%b"), rx):
            achados.append(("mensagens de commit", n, x))
        for n, x in achar(git("log", "--all", "-p", "--format=commit %H"), rx):
            achados.append(("conteúdo de commits antigos", n, x))
    else:
        achados = conferir_arquivos(rx, preparado=(a == ["--preparado"]))
    if not achados:
        print("  nenhum nome da lista (%d formas, %s)" % (len(formas), LISTA))
        return 0
    print("  NOME DE PESSOA em %d lugar(es); troque pelo código da lista:" % len(achados))
    for onde, n, forma in achados[:60]:
        print("     %s%s: %s  ->  %s" % (onde, (":%d" % n) if n else "", forma, formas.get(forma, "?")))
    if len(achados) > 60:
        print("     ... e mais %d" % (len(achados) - 60))
    return 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Resolve as marcas de CriticMarkup de um .md anotado.

POR QUE ISTO EXISTE

Word tem aceitar e recusar; markdown nao tem. As marcas precisam sair antes de o
texto virar entrega, e sair a mao em quarenta e sete marcas deixa `~>` solto no
meio da frase.

DUAS COISAS DIFERENTES, E A DISTINCAO E O PROGRAMA INTEIRO

Comentario e anotacao: some sempre, e nao ha decisao a tomar. Uma versao limpa
nunca o traz.

Mudanca e bifurcacao: `{~~antes~>depois~~}` obriga a escolher um lado, e escolher
por todos de uma vez nao e a decisao de quem escreve, e sim uma previa. Por isso
o modo padrao aqui e --previa, que aceita tudo e serve para gerar PDF de leitura,
e nunca para gravar por cima do arquivo de trabalho.

    python limpar_md.py <arquivo.md> --previa            aceita tudo, tira comentario
    python limpar_md.py <arquivo.md> --aceitar S1,S14    so esses; o resto volta ao original
    python limpar_md.py <arquivo.md> --recusar-tudo      desfaz as mudancas, tira comentario
"""
import argparse
import re
import sys
from pathlib import Path

RE_COMENTARIO = re.compile(r"\{>>(.*?)<<\}", re.S)
RE_SUB = re.compile(r"\{~~(.*?)~>(.*?)~~\}", re.S)
RE_MAIS = re.compile(r"\{\+\+(.*?)\+\+\}", re.S)
RE_MENOS = re.compile(r"\{--(.*?)--\}", re.S)
RE_DESTAQUE = re.compile(r"\{==(.*?)==\}", re.S)
RE_CODIGO = re.compile(r"\[([A-Z]{1,2}\d+)\]")


def main():
    ap = argparse.ArgumentParser(description="Resolve CriticMarkup num .md anotado.")
    ap.add_argument("arquivo")
    ap.add_argument("--saida")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--previa", action="store_true",
                   help="aceita todas as mudanças e tira os comentários (para gerar PDF)")
    g.add_argument("--recusar-tudo", action="store_true",
                   help="desfaz todas as mudanças e tira os comentários")
    g.add_argument("--aceitar", help="códigos a aceitar, separados por vírgula (S1,S14)")
    a = ap.parse_args()

    t = Path(a.arquivo).read_text(encoding="utf-8")
    antes = {"comentário": len(RE_COMENTARIO.findall(t)),
             "substituição": len(RE_SUB.findall(t)),
             "inserção": len(RE_MAIS.findall(t)),
             "exclusão": len(RE_MENOS.findall(t))}
    if not any(antes.values()):
        sys.exit("nenhuma marca de CriticMarkup neste arquivo: nada a resolver.")

    aceitos = set()
    if a.aceitar:
        aceitos = {c.strip().upper() for c in a.aceitar.split(",") if c.strip()}

    def decide(m, vem_do_codigo):
        """Aceita quando o modo manda, ou quando o codigo esta na lista."""
        if a.previa:
            return True
        if a.recusar_tudo:
            return False
        return vem_do_codigo in aceitos

    # O codigo de um item fica no comentario que o acompanha; uma mudanca sem
    # comentario ao lado nao tem codigo, e no modo seletivo ela e recusada, que
    # e o lado seguro.
    def codigo_perto(texto, fim, alcance=400):
        m = RE_CODIGO.search(texto[fim:fim + alcance])
        return m.group(1) if m else None

    def troca_sub(m):
        return m.group(2) if decide(m, codigo_perto(t, m.end())) else m.group(1)

    def troca_mais(m):
        return m.group(1) if decide(m, codigo_perto(t, m.end())) else ""

    def troca_menos(m):
        return "" if decide(m, codigo_perto(t, m.end())) else m.group(1)

    s = RE_SUB.sub(troca_sub, t)
    s = RE_MAIS.sub(troca_mais, s)
    s = RE_MENOS.sub(troca_menos, s)
    s = RE_DESTAQUE.sub(lambda m: m.group(1), s)
    s = RE_COMENTARIO.sub("", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r" +([,.;:])", r"\1", s)
    s = re.sub(r"[ \t]+$", "", s, flags=re.M)

    resta = len(re.findall(r"\{[>~+\-=]", s))
    dest = Path(a.saida) if a.saida else \
        Path(a.arquivo).with_name(Path(a.arquivo).stem + "-LIMPO.md")
    dest.write_text(s, encoding="utf-8")

    modo = "prévia" if a.previa else ("recusa" if a.recusar_tudo else
                                      "seletivo (%d código(s))" % len(aceitos))
    print("  %s: modo %s | %s" % (dest.name, modo,
          ", ".join("%s %d" % (k, v) for k, v in antes.items() if v)))
    if resta:
        print("  ATENÇÃO: %d marca(s) não resolvida(s) sobraram. Confira antes de usar." % resta)
    if a.previa:
        print("  A prévia aceita tudo, e não é a sua decisão: não grave por cima do arquivo de trabalho.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

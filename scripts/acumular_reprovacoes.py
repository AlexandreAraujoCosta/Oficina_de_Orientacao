# -*- coding: utf-8 -*-
"""Acumula, numa serie, os itens que a conferencia de compreensibilidade reprovou.

POR QUE EXISTE. A conferencia de cada entrega diz o que falhou naquela entrega, e
some. O que decide se ela continua valendo a pena nao e a taxa de uma entrega, e
sim se as reprovacoes continuam sendo de especie nova. Reprovacao que se repete
com assinatura mecanica tem de migrar da leitura para um programa; especie que
ninguem antecipou e o que justifica manter um leitor.

A DIVISAO DE TRABALHO. O modelo julga e escreve a tabela; este programa colhe as
linhas reprovadas e as acumula. Acumulacao por modelo apaga o que ja estava la e
nao se confere; acumulacao por programa e conferivel e nao perde.

    python scripts/acumular_reprovacoes.py CONFERENCIA-RELATORIO-FULANO.md --entrega fulano

A serie fica em `relatorios/REPROVACOES-COMPREENSIBILIDADE.md`, fora do
repositorio publico, porque nomeia orientandos.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

SERIE = Path(r"D:\Claude\TCC\relatorios\REPROVACOES-COMPREENSIBILIDADE.md")

CABECALHO = """# Reprovações da conferência de compreensibilidade, em série

Cada linha é um item que um leitor frio não conseguiu executar. A coluna que
decide o futuro da conferência é a **espécie**: enquanto aparecerem espécies
novas, a leitura fria está achando o que ninguém antecipou. Quando três entregas
seguidas reprovarem só por espécies já conhecidas, aquela dimensão migra para
programa e a leitura continua nas outras.

**Aberto em 30/08/2026.** Acumulado por `scripts/acumular_reprovacoes.py`, que
colhe as linhas da tabela e não as reescreve.

| data | entrega | item | espécie | o que faltou |
|---|---|---|---|---|
"""

# As especies conhecidas ate 30/08/2026, e a regra de classificacao.
ESPECIES = [
    ("endereço", r"procurar|onde|endere|varrer|localiz|qual (é |e )?(a |o )?(express|trecho|frase|palavra|autor)"),
    ("termo",    r"termo|categoria|jarg|não sei o que (é|significa)|sem defini"),
    ("forma correta ausente", r"forma correta|como se escreve|o que pôr no lugar|qual (é|e) o certo"),
    ("critério",  r"critério|por que .*(é|e) defeito|não sei se .*(é|e) erro"),
]


def especie(o_que_falta, o_que_eu_faria):
    """Classifica pela razao declarada, e devolve 'outra' quando nao reconhece.

    'outra' e o valor que interessa: e onde aparece a especie nova."""
    texto = ("%s %s" % (o_que_eu_faria, o_que_falta)).lower()
    for nome, padrao in ESPECIES:
        if re.search(padrao, texto):
            return nome
    return "outra"


def reprovados(caminho):
    """As linhas da primeira tabela cuja coluna 'passa' diz não."""
    t = Path(caminho).read_text(encoding="utf-8")
    saida = []
    for linha in t.split("\n"):
        if not linha.startswith("|"):
            continue
        c = [x.strip() for x in linha.strip("|").split("|")]
        if len(c) < 4 or c[0].lower() in ("item", "---"):
            continue
        passa = c[1].replace("*", "").strip().lower()
        if passa in ("não", "nao"):
            saida.append((c[0], c[2], c[3]))
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("conferencia", help="o CONFERENCIA-*.md que o leitor frio gravou")
    ap.add_argument("--entrega", required=True, help="nome curto do trabalho")
    ap.add_argument("--serie", default=str(SERIE))
    a = ap.parse_args()

    linhas = reprovados(a.conferencia)
    serie = Path(a.serie)
    if not serie.exists():
        serie.parent.mkdir(parents=True, exist_ok=True)
        serie.write_text(CABECALHO, encoding="utf-8")

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    t = serie.read_text(encoding="utf-8")
    novas = 0
    for item, faria, falta in linhas:
        marca = "| %s | %s | %s |" % (hoje, a.entrega, item)
        if marca in t:
            continue
        esp = especie(falta, faria)
        t += "| %s | %s | %s | %s | %s |\n" % (
            hoje, a.entrega, item, esp,
            " ".join(falta.split())[:170])
        novas += 1
    serie.write_text(t, encoding="utf-8")

    print("  %s: %d reprovação(ões) na conferência, %d acrescentada(s) à série"
          % (Path(a.conferencia).name, len(linhas), novas))
    if not linhas:
        print("     nenhuma reprovação. Taxa zero não é maturidade por si:")
        print("     é quando a própria conferência passa a precisar de controle.")
        return 0

    conta = {}
    for l in serie.read_text(encoding="utf-8").split("\n"):
        if l.startswith("| ") and l.count("|") >= 5:
            c = [x.strip() for x in l.strip("|").split("|")]
            if c[0] != "data" and not c[0].startswith("---"):
                conta[c[3]] = conta.get(c[3], 0) + 1
    print("  a série, por espécie:")
    for e, n in sorted(conta.items(), key=lambda x: -x[1]):
        print("     %-24s %d" % (e, n))
    if conta.get("outra"):
        print("     'outra' é o que sustenta a conferência: espécie que não se")
        print("     reconheceu, e por isso nenhum programa a pegaria.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

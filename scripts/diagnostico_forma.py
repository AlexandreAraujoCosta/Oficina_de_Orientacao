# -*- coding: utf-8 -*-
"""Diz o que ha de errado com a forma do .docx, e nao mexe em nada.

POR QUE ESTE PROGRAMA EXISTE, E POR QUE ELE NAO ESCREVE

Ate 30/08/2026 este diagnostico vinha junto com a transformacao, no
`normalizar_docx.py`. A transformacao saiu da cadeia naquele dia, e a razao esta
medida: dos 19 apontamentos escritos sobre uma dissertacao real, nenhum veio da
camada formal, e todos teriam sido encontrados no arquivo original. Em troca, a
transformacao produziu cinco defeitos em producao no mesmo dia, entre eles
desmontar a capa de um trabalho que ela nao tinha tocado.

Todo o resto da oficina le e relata. A transformacao era o unico ponto em que um
programa nosso escrevia no arquivo de outra pessoa, e era ali que o risco se
concentrava. O diagnostico continua valendo, e nao corre esse risco: ele conta.

O que ele NAO faz, e nao e omissao: nao converte titulo, nao alinha forma, nao
apaga paragrafo vazio, nao escreve estilo. Cada uma dessas coisas exige uma
decisao que e de quem escreveu o trabalho, e o que este programa entrega e a
informacao para que a decisao seja tomada.

    python scripts/diagnostico_forma.py trabalho.docx

A transformacao esta guardada no ramo `norma-transformadora`, como semente de
outro artefato, com o registro do que funcionou e do que falhou.
"""
import argparse
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalizar_docx as N                                          # noqa: E402


def secao(titulo):
    print()
    print(titulo)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("trabalho", help="o .docx a diagnosticar")
    a = ap.parse_args()

    alvo = Path(a.trabalho)
    if alvo.suffix.lower() != ".docx":
        sys.exit("so funciona com .docx: num PDF a forma ja esta achatada.")
    if not alvo.exists():
        sys.exit("nao encontrei %s" % alvo)

    with zipfile.ZipFile(alvo) as z:
        doc = z.read("word/document.xml")

    pars = N.paragrafos(doc)
    inicio = N.fim_do_pretextual(doc, pars)
    tabelas = N.dentro_de_tabela(doc)
    faixa = N.faixa_referencias(doc, pars)

    corpo, estilos, direta = N.diagnostico(doc)
    print("DIAGNOSTICO DE FORMA: %s" % alvo.name)
    print("  %d paragrafos com texto, %d estilos em uso" % (len(corpo), len(estilos)))
    for nome, n in estilos.most_common(5):
        print("     %-34s %4d  (%2.0f%%)" % (nome[:34], n, 100.0 * n / max(len(corpo), 1)))
    if estilos:
        maior = estilos.most_common(1)[0]
        if maior[0] != "(Normal)":
            print("  o paragrafo tipico nao usa o estilo Normal, e sim %s" % maior[0])
    pct = 100.0 * direta / max(len(corpo), 1)
    print("  com formatacao direta sobre o estilo: %d de %d (%.0f%%)"
          % (direta, len(corpo), pct))
    if pct >= 50:
        print("     acima de metade: o arquivo foi montado por formatacao direta, e")
        print("     nao por estilo. Trocar o estilo nao muda o que se ve.")

    # ---- os papeis, e quantas formas cada um tem
    achados, outros = N.papeis(doc, pars, tabelas, inicio, faixa)
    secao("PADROES DE FORMATACAO, POR PAPEL")
    print("  Cada papel deveria ter uma forma so. Mais de uma e falta de padrao,")
    print("  e a fracao diz quanto do papel ja usa a forma majoritaria.")
    achou_algo = False
    for nome, _ in N.PAPEIS:
        idx = achados.get(nome) or []
        if not idx:
            continue
        achou_algo = True
        dom, fatia, quantas, assentada = N.escolher_forma(doc, pars, idx)
        recado = ("%d ja usam a majoritaria (%.0f%%)"
                  % (round(fatia * len(idx)), 100 * fatia))
        if not assentada:
            recado += "; nenhuma reune metade, e escolher e de quem escreveu"
        print("  %-12s %4d paragrafos em %2d formas; %s" % (nome, len(idx), quantas, recado))
    if not achou_algo:
        print("  nenhum papel reconhecido por regra neste arquivo.")
    if outros:
        print("  %d paragrafos ficaram fora dos papeis (linha curta ou forma isolada)"
              % len(outros))

    # ---- titulos
    parecem, com_estilo = N.titulos_por_marcar(doc, pars, inicio)
    secao("TITULOS")
    print("  %d paragrafos usam estilo de titulo; %d parecem titulo e nao usam"
          % (com_estilo, len(parecem)))
    if parecem and com_estilo <= len(parecem) // 4:
        print("  Marca-los como Titulo 1, 2 e 3 no Word daria sumario automatico,")
        print("  painel de navegacao e numeracao que nao se digita. Padronizar os")
        print("  titulos importa mais do que parece: e deles que saem o sumario, a")
        print("  numeracao e a navegacao do arquivo inteiro.")

    # ---- vazios
    vazios = sum(1 for ini, fim in pars if N.vazio(doc[ini:fim]))
    vazios_corpo = sum(1 for i, (ini, fim) in enumerate(pars)
                       if i >= inicio and N.vazio(doc[ini:fim]))
    secao("PARAGRAFOS VAZIOS")
    print("  %d no arquivo, dos quais %d no corpo" % (vazios, vazios_corpo))
    if vazios_corpo >= 20:
        print("  No corpo, o vazio faz o papel do espaco entre paragrafos, que e")
        print("  propriedade do estilo. No pre-textual ele e diagramacao, e ali esta")
        print("  certo: e o que poe o titulo no meio da folha e a cidade no rodape.")

    # ---- referencias
    secao("LISTA DE REFERENCIAS")
    if faixa[0] is None:
        print("  nao localizada: nao ha titulo REFERENCIAS ou BIBLIOGRAFIA fora do sumario.")
    else:
        print("  %d entradas, do paragrafo %d ao %d"
              % (faixa[1] - faixa[0], faixa[0] + 1, faixa[1]))
        print("  A NBR 6023 pede alinhamento a esquerda, sem recuo, entrelinha")
        print("  simples e uma linha em branco entre entradas.")

    print()
    print("  Este diagnostico nao mexeu em nada. Cada item acima e decisao de quem")
    print("  escreveu o trabalho, e se resolve no Word em minutos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

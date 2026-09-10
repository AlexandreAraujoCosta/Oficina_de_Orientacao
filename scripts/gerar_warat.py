# -*- coding: utf-8 -*-
"""Gera o WARAT: o ALBERTO com uma ordem de leitura trocada, e nada mais.

POR QUE ISTO EXISTE

O `ALBERTO.md` abre a secao de leitura afirmando que **a ordem decide o que voce
vai achar**, e manda inverter: dados antes da prosa que os comenta, julgamento so
no passo 4. A afirmacao esta la desde o comeco e **nunca foi testada**.

O Warat e o braco de controle dessa afirmacao. Ele e o mesmo prompt, palavra por
palavra, com uma unica secao trocada: a da ordem. Se as duas leituras acharem o
mesmo, a afirmacao cai e 738 palavras saem do prompt. Se acharem coisas
diferentes, a inversao se paga e passa a ter numero.

**Gerar por programa, e nao a mao, e o que garante que so a ordem varia.** Uma
copia editada a mao diverge em detalhes que ninguem lembra de conferir, e a
diferenca medida deixa de ser atribuivel.

O QUE ELE TROCA

A secao "A ordem de leitura" inteira, do titulo dela ate o titulo da secao
seguinte. Tudo o mais fica: a disciplina, o exame da inferencia, a regua do
veredito, a estrutura do relatorio, as regras de escrita, os defeitos de ambiente.

Uso:
    python scripts/gerar_warat.py                 grava prompts/WARAT.md
    python scripts/gerar_warat.py --conferir      so diz se esta em dia
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
ORIGEM = RAIZ / "prompts" / "ALBERTO.md"
DESTINO = RAIZ / "prompts" / "WARAT.md"

ABRE = "## A ordem de leitura, e ela decide o que você vai achar"
FECHA = "## O exame da inferência, e é o que um examinador faz"

CABECA = """<!-- GERADO por scripts/gerar_warat.py a partir de prompts/ALBERTO.md.
     NAO EDITE ESTE ARQUIVO. Ele existe para medir uma coisa so, e a medida
     depende de ele ser identico ao ALBERTO em tudo menos na ordem de leitura.
     Para mudar qualquer outra regra, mude no ALBERTO e gere de novo. -->

# Warat: a mesma leitura, na ordem do trabalho

Este prompt é o do Alberto com **uma seção trocada**, a da ordem de leitura. Todo
o resto é idêntico: a disciplina, o exame da inferência, a régua do veredito, a
estrutura do relatório, as regras de escrita.

Ele existe para responder a uma pergunta que a oficina afirma e não mediu: **a
ordem de leitura muda o que se acha?**

"""

ORDEM_NOVA = """## A ordem de leitura: a do próprio trabalho

**Leia o trabalho do começo ao fim, na ordem em que ele foi escrito.** Capa,
resumo, introdução, cada capítulo na sequência, conclusão, referências, apêndices.
É a ordem em que quem examina o trabalho vai lê-lo, e é a ordem em que o autor o
construiu.

Vá anotando enquanto lê, e anote as três coisas ao mesmo tempo, sem separar em
passadas: **o que o trabalho promete**, **o que ele entrega** e **onde uma coisa
não corresponde à outra**. Cada anotação traz o endereço.

Quando chegar a uma tabela, a uma figura ou a um quadro, examine-o ali, no ponto
em que ele aparece, junto com o texto que o comenta. Confira o que a figura mostra
contra o que o parágrafo diz que ela mostra, e siga.

**Julgue à medida que lê.** Onde uma promessa da introdução não aparecer no
capítulo que devia cumpri-la, anote no ponto em que a falta se revela. Onde um
número de um capítulo não fechar com outro de um capítulo anterior, volte àquele e
anote os dois.

Ao terminar a primeira passada, releia as suas anotações e faça três perguntas:

1. **Que promessas ficaram sem entrega**, e onde a falta está.
2. **Que resultados estão nos dados e não foram afirmados em lugar nenhum.** É a
   parte que o autor não produz sozinho, porque ele já sabe o que quis dizer.
3. **A inferência**, que está na seção seguinte e é o passo principal.

**E rótulo ilegível na página reduzida não é achado.** Rótulo truncado na imagem do
`.docx` é defeito do trabalho; rótulo que não se lê numa página de PDF pode ser só a
redução. Antes de escrever que a figura não rotula, abra a imagem dela.

**O endereço de uma figura é o parágrafo da legenda**, e a posição da imagem não é
endereço.
"""


def gerar():
    a = io.open(str(ORIGEM), encoding="utf-8").read()
    i, j = a.find(ABRE), a.find(FECHA)
    if i < 0 or j < 0 or j <= i:
        raise SystemExit("nao achei a secao da ordem no ALBERTO.md; "
                         "o titulo mudou e este programa precisa saber disso")
    return CABECA + a[:i] + ORDEM_NOVA + a[j:], len(a[i:j].split())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--conferir", action="store_true",
                    help="não escreve; diz se o arquivo gerado está em dia")
    a = ap.parse_args()

    novo, tirado = gerar()
    if a.conferir:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual != novo:
            print("  DESATUALIZADO: %s" % DESTINO)
            print("  Gere de novo: python scripts/gerar_warat.py")
            return 1
        print("  em dia: %s" % DESTINO)
        return 0

    DESTINO.write_text(novo, encoding="utf-8")
    print("  %s" % DESTINO)
    print("  %d palavras, contra %d do ALBERTO." % (len(novo.split()),
          len(io.open(str(ORIGEM), encoding="utf-8").read().split())))
    print("  Saíram %d palavras da ordem antiga; entraram %d da nova."
          % (tirado, len(ORDEM_NOVA.split())))
    print("\n  Só a seção da ordem difere. Se as duas leituras acharem o mesmo,")
    print("  a inversão não se paga e essas palavras saem do ALBERTO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

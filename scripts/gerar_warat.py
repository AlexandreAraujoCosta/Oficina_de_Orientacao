# -*- coding: utf-8 -*-
"""Gera os WARAT: o ALBERTO com uma ordem de leitura trocada, e nada mais.

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

DUAS VARIANTES, DESDE 13/09/2026

    trabalho    a ordem do proprio trabalho (capa ate apendices). E a variante
                original, gravada em prompts/WARAT.md.
    realizado   o que foi feito antes do que foi prometido: artefatos, depois
                uma descricao do que a pesquisa realizou, e so entao resumo,
                introducao e conclusao, lidos contra essa descricao. Gravada em
                prompts/WARAT-REALIZADO.md. A proposta e os falsificadores estao
                em prompts/PROPOSTA-20260913-pontas-contra-o-realizado.md.

O QUE ELE TROCA

A secao "A ordem de leitura" inteira, do titulo dela ate o titulo da secao
seguinte. Tudo o mais fica: a disciplina, o exame da inferencia, a regua do
veredito, a estrutura do relatorio, as regras de escrita, os defeitos de ambiente.

A variante `realizado` faz **uma substituicao fora da secao**, declarada abaixo em
SUBSTITUICOES e impressa ao gerar: a frase do ALBERTO que remete ao "passo 2 da
ordem de leitura" como o passo do aparato empirico passa a remeter ao passo 1,
que e onde esse conteudo fica na ordem nova. Sem isso a remissao apontaria para
o passo errado, e isso seria uma segunda variavel escondida.

Uso:
    python scripts/gerar_warat.py                        grava prompts/WARAT.md
    python scripts/gerar_warat.py --variante realizado   grava prompts/WARAT-REALIZADO.md
    python scripts/gerar_warat.py --todas                grava as duas
    python scripts/gerar_warat.py --conferir [--todas]   so diz se esta em dia
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

ABRE = "## A ordem de leitura, e ela decide o que você vai achar"
FECHA = "## O exame da inferência, e é o que um examinador faz"

# ---------------------------------------------------------------- trabalho

CABECA_TRABALHO = """<!-- GERADO por scripts/gerar_warat.py a partir de prompts/ALBERTO.md.
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

ORDEM_TRABALHO = """## A ordem de leitura: a do próprio trabalho

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

# ---------------------------------------------------------------- realizado

CABECA_REALIZADO = """<!-- GERADO por scripts/gerar_warat.py --variante realizado, a partir de
     prompts/ALBERTO.md. NAO EDITE ESTE ARQUIVO. Ele existe para medir uma coisa
     so, e a medida depende de ele ser identico ao ALBERTO em tudo menos na
     ordem de leitura (e numa remissao a ela, que o gerador declara).
     Para mudar qualquer outra regra, mude no ALBERTO e gere de novo. -->

# Warat: a mesma leitura, com o que foi feito antes do que foi prometido

Este prompt é o do Alberto com **uma seção trocada**, a da ordem de leitura. Todo
o resto é idêntico: a disciplina, o exame da inferência, a régua do veredito, a
estrutura do relatório, as regras de escrita.

Ele existe para responder a uma pergunta que a oficina fez em 13/09/2026 e não
mediu: **descrever o que a pesquisa realizou, antes de ler o que ela promete e
conclui, muda o que se acha sobre a introdução e a conclusão?**

"""

ORDEM_REALIZADO = """## A ordem de leitura: o que foi feito antes do que foi prometido

Ler o resumo, a introdução e a conclusão primeiro faz chegar aos dados sabendo o
que eles deviam provar, e então eles são lidos como prova. Aqui a ordem se
inverte: primeiro o que o trabalho entrega, depois uma descrição do que ele fez, e
só então o que ele promete, lido contra essa descrição. Cumpra os seis passos
nesta ordem, e **só comece a julgar no passo 4**.

**1. O que ele entrega, lido de trás para diante.** Abra os apêndices, as tabelas,
as figuras e a seção de resultados **antes** do texto que os comenta, e antes do
resumo, da introdução e da conclusão. Anote o que os dados mostram, com endereço,
sem olhar o que o autor diz que eles mostram. Depois leia o comentário.

De cada figura, antes de saber o que o texto diz que ela mostra: o que ela
mostra, o que ela **permite afirmar** (inclusive a conta que ela permite e o texto
não faz, quando uma afirmação depende dela), o que ela **não** permite (o
denominador, a unidade contada, o critério de inclusão) e o que só o texto poderia
dizer. **E diga, de cada uma, quando ela não permite item nenhum:** figura que
ilustra a interface de um sítio não sustenta afirmação empírica, e preencher todas
é sinal de que se está fabricando.

**O endereço de uma figura é o parágrafo da legenda**, e a posição da imagem não é
endereço.

**E rótulo ilegível na página reduzida não é achado.** Rótulo truncado na imagem do
`.docx` é defeito do trabalho; rótulo que não se lê numa página de PDF pode ser só a
redução. Antes de escrever que a figura não rotula, abra a imagem dela.

**2. O que foi feito.** Antes de abrir o resumo, a introdução e a conclusão,
escreva no registro da leitura uma descrição do que a pesquisa realizou, a partir
do que o passo 1 mostrou, em sete campos, com localizador em cada linha:

- **Material.** O que foi coletado: a unidade, quantas, de onde, de que período,
  com que critério de entrada. Os números saem dos artefatos (tabela, planilha,
  apêndice); onde artefato e prosa divergirem, os dois números, com os dois
  endereços.
- **Tratamento.** Como o material foi classificado ou organizado: cada categoria
  com o nome, a contagem e o lugar em que é definida.
- **Análise.** Que operação foi feita (contagem, comparação, cruzamento, leitura
  interpretativa) e **sobre quantas unidades ela de fato incide**, contadas nos
  resultados, e não anunciadas no método.
- **Resultados.** O que a análise estabelece, uma afirmação por linha, cada uma
  com a tabela, figura ou apêndice de que sai. Entra o que os artefatos
  sustentam, ainda que nenhuma frase do corpo o afirme. **É a lista contra a qual
  o passo 3 lê as duas pontas.**
- **O desenho, dito pelo que ele permite.** Censo ou amostra; documental ou de
  campo; descritivo ou comparativo; um corte no tempo ou série. Cada resposta com
  a consequência que os passos seguintes usam: censo dispensa teste de
  significância; desenho documental não alcança afirmação sobre a prática;
  descrição não sustenta mecanismo. Classificação sem consequência escrita não
  entra.
- **Onde cada coisa está.** Uma linha por capítulo e por apêndice: o que a peça
  faz (coleta, define categorias, apresenta resultado, discute, conclui), o
  intervalo de localizadores, e qual outra peça consome o que ela produz. É daqui
  que se sabe, como fato, se os resultados estão no corpo ou no apêndice, e se os
  capítulos se consomem ou ficam soltos.
- **O método declarado contra o feito.** Só agora leia o capítulo de método, e dê
  a cada procedimento que ele declara um estado: EXECUTADO COMO DECLARADO,
  EXECUTADO DE OUTRO MODO (diga qual), DECLARADO SEM VESTÍGIO, EXECUTADO SEM
  DECLARAÇÃO. Estado, e não item: o item vem no passo 4.

**O capítulo de método se lê por último, e a razão é o risco deste passo.** O que
o trabalho fez não está escrito em lugar nenhum, e o caminho barato é reescrever o
capítulo de método com autoridade de constatação. Descrição cujos localizadores
estão no capítulo de método, e não nos artefatos e nos resultados, é paráfrase:
refaça-a. Nada aqui é julgamento; é descrição, e onde você não souber, escreva o
que faltou para saber.

**3. O que o trabalho promete, lido contra o que foi feito.** Só agora o resumo, a
introdução e a conclusão. Liste o que o trabalho afirma sobre si: a pergunta, os
objetivos, cada ressalva metodológica declarada, o produto que ele anuncia
entregar, e cada asserção forte da conclusão. Cada linha traz o endereço **e diz
se está entre os resultados do passo 2, se está com outro alcance, ou se não
está**. Não julgue ainda: registre.

**4. O cruzamento, e aqui começa o julgamento.** Promessa por promessa, e asserção
por asserção, contra o passo 2: foi entregue? onde? o que foi entregue sustenta o
que foi prometido, ou sustenta menos, ou sustenta outra coisa? Onde o passo 2 não
responder, procure no corpo, com controle, antes de afirmar que não foi executado:
a descrição é a primeira referência, e não a única. Quatro coisas saem daqui e não
saem de lista nenhuma:

- Onde a maioria das promessas de método e de percurso sair sem entrega ou
  entregue de outro modo, o item é um só: **a introdução descreve outro
  trabalho**, com a conta, e a decisão que ele pede tem duas saídas, reescrever a
  introdução a partir do que foi feito ou executar o que ela promete.
- A asserção da conclusão que não está entre os resultados do passo 2 diz, no
  item, as duas coisas: o que a conclusão afirma e o que foi feito.
- O resultado do passo 2 que a conclusão não retoma é item, salvo quando o
  trabalho o exclui expressamente (remete a outro trabalho, declara que não
  desenvolve).
- O limite do desenho vale como ressalva ainda que o autor não a tenha escrito,
  e o item diz que ela vem do desenho, e não de uma frase dele.

**5. O caminho inverso.** Percorra as anotações do passo 1 procurando o que está
nos dados e não foi afirmado em lugar nenhum. É a parte que o autor não produz
sozinho, porque ele já sabe o que quis dizer.

**6. A inferência.** Está na seção seguinte, e é o passo principal.

**No relatório, a descrição do passo 2 entra logo depois das linhas da razão do
veredito e antes das decisões, sob o título "O que o trabalho fez":** no máximo
doze linhas, copiadas dos campos material, análise, resultados e onde cada coisa
está, com os localizadores, seguidas de duas linhas de conta: de quantas
promessas da introdução, quantas descrevem o que foi feito; de quantas asserções
da conclusão, quantas repousam nos resultados. Sem apreciação. A descrição não é
item e não entra na conta de itens.

**No chat, o arquivo inteiro chega de uma vez, e a ordem é a única trava:**
cumpra-a mesmo assim, e diga no registro se leu as pontas antes da hora.
"""

# Remissoes do ALBERTO a passos da ordem, que mudam de numero na variante.
# (texto no ALBERTO, texto na variante). Impressas ao gerar.
SUBSTITUICOES_REALIZADO = (
    ("**O passo 2 da ordem de leitura abre pelo aparato empírico lido de trás para\n"
     "diante**",
     "**O passo 1 da ordem de leitura abre pelo aparato empírico lido de trás para\n"
     "diante**"),
)

VARIANTES = {
    "trabalho": (RAIZ / "prompts" / "WARAT.md", CABECA_TRABALHO, ORDEM_TRABALHO, ()),
    "realizado": (RAIZ / "prompts" / "WARAT-REALIZADO.md", CABECA_REALIZADO,
                  ORDEM_REALIZADO, SUBSTITUICOES_REALIZADO),
}


def gerar(variante):
    destino, cabeca, ordem, substituicoes = VARIANTES[variante]
    a = io.open(str(ORIGEM), encoding="utf-8").read()
    i, j = a.find(ABRE), a.find(FECHA)
    if i < 0 or j < 0 or j <= i:
        raise SystemExit("nao achei a secao da ordem no ALBERTO.md; "
                         "o titulo mudou e este programa precisa saber disso")
    fora = a[:i] + "\0" + a[j:]
    feitas = []
    for velho, novo in substituicoes:
        n = fora.count(velho)
        if n != 1:
            raise SystemExit("a remissao a substituir ocorre %d vezes no ALBERTO, "
                             "e o gerador so sabe lidar com uma: %r" % (n, velho[:60]))
        fora = fora.replace(velho, novo)
        feitas.append((velho, novo))
    texto = cabeca + fora.replace("\0", ordem)
    return destino, texto, len(a[i:j].split()), len(ordem.split()), feitas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variante", choices=sorted(VARIANTES), default="trabalho")
    ap.add_argument("--todas", action="store_true", help="gera (ou confere) as duas")
    ap.add_argument("--conferir", action="store_true",
                    help="não escreve; diz se o arquivo gerado está em dia")
    a = ap.parse_args()

    variantes = sorted(VARIANTES) if a.todas else [a.variante]
    problemas = 0
    for v in variantes:
        destino, novo, tirado, posto, feitas = gerar(v)
        if a.conferir:
            atual = destino.read_text(encoding="utf-8") if destino.exists() else ""
            if atual != novo:
                problemas += 1
                print("  DESATUALIZADO: %s" % destino)
                print("  Gere de novo: python scripts/gerar_warat.py --variante %s" % v)
            else:
                print("  em dia: %s" % destino)
            continue
        destino.write_text(novo, encoding="utf-8")
        print("  %s" % destino)
        print("  %d palavras, contra %d do ALBERTO." % (len(novo.split()),
              len(io.open(str(ORIGEM), encoding="utf-8").read().split())))
        print("  Saíram %d palavras da ordem antiga; entraram %d da nova." % (tirado, posto))
        for velho, nv in feitas:
            print("  Substituição fora da seção: %r -> %r"
                  % (velho.replace("\n", " ")[:70], nv.replace("\n", " ")[:70]))
    if a.conferir:
        return 1 if problemas else 0
    print("\n  Só a seção da ordem difere (mais a remissão declarada, na variante")
    print("  realizado). O que decide é o cotejo cego contra o Alberto no mesmo trabalho.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

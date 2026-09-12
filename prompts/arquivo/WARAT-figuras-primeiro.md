# Warat: a leitura pelas figuras

**Em construção.** Este arquivo tem um passo escrito e mais nada. O que estiver
aqui foi decidido; o que faltar, falta mesmo.

O nome fecha o do teórico cujo primeiro e segundo nomes já batizam as outras duas
leituras desta oficina.

## Passo 1 — todas as figuras, descritas antes de qualquer prosa

**Descreva todas as figuras do trabalho, uma a uma, sem exceção.** Isso inclui a que
não sustenta afirmação nenhuma: o organograma, a captura de tela de um sistema, o
fluxograma de um procedimento, a linha do tempo sem escala. Elas entram com a
descrição e com a frase que diz o que não se pode tirar delas.

**Descrever todas não é extrair afirmação de todas, e a distinção é o que separa
esta leitura de fabricação.** Descrição é dizer o que está impresso: que eixos,
que séries, que rótulos, que valores, que legenda, que fonte declarada. Afirmação
é dizer o que aquilo prova sobre o objeto do trabalho, e a maior parte das figuras
não prova coisa nenhuma. Uma leitura desta oficina foi medida em 06/09/2026
preenchendo item para treze figuras e recusando três: **recusar é resultado**, e
aqui a recusa fica na descrição, escrita, em vez de fazer a figura sumir.

### Como obter as figuras

```
python scripts/figuras_do_docx.py <trabalho.docx> --extracao <extracao.txt>
```

Ele tira as imagens de `word/media/`, casa cada uma com a legenda vizinha e com o
`[P###]` do parágrafo em que ela está, e diz qual arquivo carrega o dado quando a
figura vem partida em vários. **Peça as imagens numa mensagem só**, e não uma por
vez: medido em 06/09/2026, pedir uma por mensagem custou cerca de um quinto do
total da leitura, porque cada mensagem reenvia o contexto inteiro.

**O endereço de uma figura é o parágrafo da legenda**, e a posição da imagem não é
endereço: o parágrafo que carrega a imagem não tem texto, e a extração não lhe dá
marcador. Um relatório saiu com oito itens endereçados em parágrafos que não
existem por causa disso.

Onde o trabalho vier só em PDF, as figuras chegam na leitura das páginas, e ali a
restrição é outra: chamada paralela de leitura de PDF perde a imagem sem avisar.

### O que a descrição de cada figura tem de trazer

    Endereço      o [P###] da legenda, e o número com que o trabalho a chama.
    A legenda     como o trabalho a escreve, e a fonte que ele declara.
    O que é       o gênero: série temporal, distribuição, comparação entre
                  grupos, organograma, captura de tela, esquema.
    Os eixos      o que está em cada um, com a unidade, e onde a escala começa.
                  Escala que não começa em zero muda o que o olho vê.
    As séries     quantas são, o que cada uma nomeia, e como se distinguem
                  (cor, traço, marcador). **Série que a figura não identifica é
                  achado**: quem lê não sabe qual linha é qual.
    Os valores    os que estão impressos, e os que se leem do gráfico com a
                  precisão que ele permite. Diga qual é qual.
    O que falta   denominador, unidade contada, critério de inclusão, período,
                  n de cada grupo. É aqui que quase sempre está o achado.

**Diga sempre com que precisão você leu.** Valor impresso é uma coisa; valor lido
de barra é outra, e tem erro. Onde o gráfico não permitir ler o valor, escreva que
não permite, em vez de estimar sem dizer.

### Antes de ler a prosa que comenta

Esta descrição sai **antes** de você ler o que o trabalho diz sobre cada figura, e
essa ordem é a razão de o passo existir. Lida depois, a figura confirma o texto:
quem já sabe o que ela deve mostrar acha aquilo nela. Medido em 06/09/2026, sobre
treze figuras de uma tese, com a leitura de prosa ao lado como controle: a leitura
cega devolveu cinco achados que a outra não tinha, todos sobre o que a figura
permite e a prosa nunca perguntou.

Depois de descritas todas, e só então, leia o que o trabalho afirma de cada uma.

### O que este passo entrega

Uma descrição por figura, na ordem em que elas aparecem no trabalho, mais duas
listas curtas ao fim:

- **as figuras que não sustentam afirmação empírica**, com a razão de cada uma;
- **o que as figuras permitem afirmar e o trabalho não afirma** — a conta que a
  figura autoriza e não rotula, a soma das barras, a razão entre categorias, o
  complemento de um percentual.

A segunda lista é insumo dos passos seguintes desta leitura, e não item de
relatório: aqui nada ainda foi conferido contra a prosa.

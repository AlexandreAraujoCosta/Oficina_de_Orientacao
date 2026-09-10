# Classificar a relevância dos itens de um relatório

Este pedido vai a uma voz que não escreveu o relatório. Ela recebe o relatório com
o nome da ferramenta apagado, e não recebe o trabalho. A pergunta é uma só, por
item: **se este item for executado, o que muda no trabalho?**

Ele existe porque a oficina mede precisão, cobertura e custo, e não media isto.
Em 08/09/2026 um cotejo cego classificou 91 itens de um relatório e achou 50 de
superfície; a régua daquele dia não ficou escrita, e uma medida que não se repete
não confere nada. Esta régua classifica o efeito que o item declara. Sozinha, não demonstra melhora
de relevância: a compreensão exige leitura independente, e a veracidade e a
utilidade da providência exigem cotejo com o trabalho.

## O que você recebe

Um relatório em markdown, com itens identificados por código no início do título
(`S1`, `SC7`, `D4`, `C2`, `F3`, `Q1`). Você não recebe o trabalho lido, e não
precisa dele: o que se classifica é o que o item **diz** que muda, e não se ele
está certo. Item certo e irrelevante existe, e é o que esta régua procura.

## As quatro classes

Leia o item inteiro (título, o que aponta, o que fazer, o que muda) e escolha uma:

- **CONCLUSAO** — executado o item, alguma conclusão do trabalho passa a dizer
  outra coisa, ou deixa de se sustentar, ou a abordagem muda (variável a
  integrar, comparação a refazer, peça a reduzir ou a tirar do corpo).
- **ALCANCE** — a conclusão fica de pé e passa a valer com outro alcance: outro
  universo, outro número que muda a força da afirmação, uma ressalva que o texto
  não tinha e que restringe o que se afirma.
- **CONFERE** — a afirmação fica igual; o que muda é alguém poder verificá-la:
  denominador ao lado do percentual, base publicada, procedimento escrito,
  referência que faltava na lista.
- **NADA** — nada do que o trabalho afirma muda: gralha, concordância, numeração,
  remissão, grafia, ano divergente de que nenhuma afirmação depende.

Duas classes fora da conta, e o item recebe uma delas quando for o caso:

- **FORCA** — ponto forte ou contribuição (`F`, `C`): não pede providência.
- **PERGUNTA** — questão de arguição (`Q`): pede resposta, e não correção.

## Quatro regras de decisão

**Decida pelo que o item nomeia, e não pelo que ele poderia implicar.** Item que
não nomeia a afirmação do trabalho que muda vai para CONFERE ou NADA, ainda que o
assunto pareça grave. A régua mede o que o relatório entregou ao autor, e não o
que o classificador imagina por trás.

**Afirmação nomeada não basta: confira que a providência a muda.** Item que nomeia
a afirmação e cuja providência a deixa igual (só acrescenta o número, a base, o
procedimento, a referência) é CONFERE, por mais bem escrita que esteja a primeira
linha. A régua mede o que o item faz, e não o que ele diz fazer.

**Na dúvida entre duas classes vizinhas, a de baixo.** CONCLUSAO só quando o item
diz qual conclusão e o que ela passa a dizer. ALCANCE só quando o item diz o que
passa a valer e sobre que conjunto.

A distribuição das classes é livre: todos os itens podem ser relevantes.
Não atribua classes para atingir uma proporção esperada.

## Limite desta classificação

Sem o trabalho, esta classificação mede apenas a relevância apresentada pelo
relatório. Não demonstra veracidade nem utilidade efetiva. A frase de que a régua
é um falsificador de relevância deve ser entendida com esse limite.

Para comparar versões, faça avaliações separadas: compreensão por leitor que não
recebe o trabalho; veracidade por outra voz que consulta a fonte; utilidade das
decisões confirmadas, considerando estágio, prazo e objetivo do estudante.
Registre por item se a ação é compreensível, se a afirmação foi confirmada ou
permanece indeterminada, e qual decisão útil permite. Não some essas medidas em
uma nota. Comentário do orientador sem par pede exame, não reprovação automática.

## A saída

Uma linha por item, nesta forma, e nada mais que isso além de um cabeçalho de uma
linha com o alcance (quantos itens leu, e se algum código não pôde ser lido):

```
S1 | CONCLUSAO | a taxa de 7,6 pontos cai a 2,7 e a afirmação central de [P115] muda | o item diz a conta e o que ela muda
S7 | NADA | - | um número divergente de que nenhuma afirmação depende
F2 | FORCA | - | ponto forte
```

Quatro campos separados por barra vertical: o código, a classe, a afirmação do
trabalho que muda (ou um traço), e a razão em poucas palavras. Todo código do
relatório aparece uma vez. `scripts/relevancia.py` lê este arquivo e acusa código
que falta ou que sobra.

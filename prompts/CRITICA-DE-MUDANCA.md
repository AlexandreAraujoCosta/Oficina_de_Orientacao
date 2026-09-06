# Pedido da crítica fria de uma mudança de prompt

Este arquivo é o pedido que se manda a uma segunda voz, junto com o diff, antes de
a mudança ser commitada. Ela não participou da conversa em que a ideia nasceu, e é
essa a razão de ela servir: quem escreveu a regra lê o que quis dizer.

## O que você recebe

O diff da alteração, o prompt inteiro como ele fica depois dela, e **o caso
concreto que a motivou**, com localizador. Você não recebe a conversa.

## As três perguntas, e responda nesta ordem

**1. A regra nova produziria o caso que a motivou?** Esta é a que pega defeito.
Pegue o caso, percorra a redação nova passo a passo como se fosse a leitura, e diga
onde ele passa e onde ele para. Se ele parar em alguma condição da própria regra,
a regra está errada, por mais bem escrita que esteja. **Não avalie a plausibilidade
da regra: rode o caso.**

**2. O que passava antes e para de passar?** Guarda nova tem falso positivo, e o
preço dele é achado que some sem ninguém notar. Diga que espécie de achado a nova
condição derruba, e dê um exemplo construído por você.

**3. Onde isto contradiz, repete ou supera o que já está no arquivo?** Instrução
nova que supera outra sem apagá-la deixa as duas valendo, e quem lê obedece à
primeira que encontra. Cite as duas passagens, com o número da linha.

## Três coisas a mais, curtas

- **O tamanho.** Diga quantas palavras a alteração acrescenta e a que percentual do
  arquivo isso corresponde. Prompt que cresce sem medida disputa atenção consigo
  mesmo.
- **A espécie da regra.** Ela vem de defeito medido, de raciocínio, ou de pedido?
  Se o diff não disser, diga que não diz.
- **O que ela ensina que o modelo já faz.** Se a instrução descreve algo que uma
  leitura faria sem ser mandada, ela é enfeite e se paga em contexto a cada turno.

## Como responder

Um veredito por pergunta, com a passagem citada. Onde você não conseguir decidir,
escreva que não conseguiu e o que faltou. **Não sugira redação nova**: o pedido é
de crítica, e quem escreve é quem tem o caso na mão.

# Qual leitura pedir, e quanto ela custa

Este arquivo existe para uma conversa: alguém abriu o agente, tem um trabalho na
pasta e não sabe qual das leituras pedir. **Ele traz medida, e não opinião.**

**Ao assistente que estiver lendo isto:** use os números daqui e **não estime
nenhum outro**. Onde faltar dado, diga que falta. Tempo e preço inventados são o
modo mais provável de errar aqui, porque a pergunta é "quanto custa" e a resposta
exata não está à mão. E rode antes a pré-análise, que mede o trabalho concreto:

```
python scripts/analisar.py
```

Ela não usa modelo nenhum. Conta parágrafos, palavras, figuras, tabelas,
parágrafos com número, e a peça que ocupa muitos parágrafos, que é a marca do
corpus reproduzido caso a caso. A recomendação sai desses números, com a razão
escrita ao lado.

---

## O que se mediu, e sobre o quê

Em 05/09/2026, oito leituras da **mesma** dissertação de mestrado em Direito
(35.708 palavras, 63 figuras, base empírica própria), por vozes que não se
leram. Os achados das cinco principais foram pareados um a um, e cada achado da
união foi classificado em três classes:

- **Risco à conclusão.** Se o achado estiver certo, alguma afirmação do trabalho
  deixa de valer, ou passa a valer com outro alcance. Entram as questões de
  banca, porque pergunta que o autor não sabe responder derruba conclusão do
  mesmo jeito.
- **A reivindicar.** O trabalho tem alguma coisa e não a afirma: resultado que
  está nos dados e não foi escrito, contribuição não anunciada, peça que outra
  pesquisa aplicaria.
- **Invisível ao leitor humano.** O achado exigiu uma operação que um leitor
  atento não faz: refazer aritmética sobre dezenas de figuras, contar ocorrências
  no texto inteiro, cruzar a lista de referências nas duas direções, reconstituir
  uma base a partir das barras de um gráfico.

Um achado pode estar em várias classes ou em nenhuma. Gralha, remissão quebrada e
acabamento normalmente não estão em nenhuma: pedem trabalho e não mudam nada.

**Na união havia 46 achados de risco à conclusão e 18 a reivindicar.**

---

## A tabela

| leitura | risco à conclusão | a reivindicar | invisíveis | minutos | R$ |
|---|---|---|---|---|---|
| Expressa | 15 | 6 | 4 | 13 | 10,35 |
| Minuciosa | 30 | 14 | 13 | 99 | 57,00 |

O preço é **teto**: a memória de contexto barateia a entrada repetida, e isso não
está descontado. O tempo é de relógio, medido do pedido à entrega dos arquivos.

**A Expressa rende quase três vezes mais achado de risco por real. A Minuciosa vê
o dobro do que existe.** As duas afirmações são verdadeiras ao mesmo tempo, e é
entre elas que se escolhe.

**E a Minuciosa não é a Expressa com mais itens.** Num pareamento das duas
leituras longas sobre esta dissertação, elas partilharam 25 achados numa união de
82: cada uma vê menos de um terço do que a outra viu. Escolher uma é abrir mão do
que a outra veria, e não comprar mais quantidade da mesma coisa.

---

## O cardápio

### 1. Expressa

Uma leitura, sobre a extração numerada, sem programas de conferência e sem
segunda voz. Devolve o relatório em PDF, o trabalho com os parágrafos numerados e
o `.docx` com os apontamentos na margem.

**Não faz:** a varredura do aparato bibliográfico nas duas direções, a busca do
que já está publicado, e a verificação por voz que não levantou os achados.

### 2. Minuciosa

Quatro leituras independentes, cada uma entrando por uma porta (o que o trabalho
afirma, o que promete, o que os dados mostram, e o que disso já existe publicado),
verificação por uma voz que não levantou nada, triagem e redação por uma voz que
não verificou. Devolve os mesmos arquivos.

**Não faz:** validar o mérito da posição defendida, nem conferir a codificação
contra o documento original. Confere o trabalho contra ele mesmo e contra o que
está publicado.

**A busca externa não se tira dela.** Ela é a quarta leitura, custa 21 dos 99
minutos, e é a única que sai do trabalho. Foi ela que descobriu, nesta
dissertação, que os números de um capítulo inteiro já estavam publicados numa
dissertação de 2022 que o trabalho cita uma vez só, e que os dados prometidos
como públicos não estão em nenhum dos três repositórios declarados. Uma leitura
que confere o trabalho só contra ele mesmo não responde se há contribuição, e é
essa a pergunta que decide se o trabalho vale a publicação.

### 3. Conferência externa, avulsa

O passo que sai do trabalho, rodado sozinho sobre duas ou três proposições que o
autor apresenta como aquisição própria. Responde uma pergunta e só ela: isso já
existe, isso contraria o que existe, ou não encontrei. Serve a quem já tem uma
leitura feita e quer só essa resposta, e serve a um artigo que ninguém analisou.

### 4. Customizada

Compor os passos à mão. Quem pede isto sabe o que quer, e o arquivo
`prompts/leituras/ESTADO.md` traz o desenho de cada passo e o que sustenta cada
escolha.

### 5. Conversar antes de decidir

Peça ao assistente que rode a pré-análise e discuta com você. Ele tem os números
deste arquivo e a forma do seu trabalho, e a escolha fica com você.

---

## O que decide, quando a tabela não decide

**O objetivo da revisão muda qual classe importa.**

Quem **vai entregar** quer os achados de risco à conclusão, porque são os que a
banca usa. Quem **quer saber se publica** quer os a reivindicar, porque são os
que dizem se há contribuição. Quem **vai defender** quer as questões, ainda que
nada mude no texto.

**A forma do trabalho muda quanto cada leitura tem para fazer.** A travessia dos
dados, que é o que a Minuciosa tem e a Expressa não, precisa de dados: num
trabalho sem figura e sem tabela ela não tem material, e a pré-análise recomenda a
Expressa. Num trabalho com base própria, ou com um corpus reproduzido caso a caso,
ela é o que se paga.

**O modelo pesa mais que a leitura.** O modelo da sessão é o modelo das leituras.
Medido no mesmo pedido e na mesma leitura: modelo pequeno devolveu 3 correções e
modelo grande devolveu 24; na outra leitura, 7 contra 18. A economia é de poucos
reais, e o que se perde primeiro é o achado que ninguém mais viu. **Não desça de
modelo para economizar.**

---

## O que saiu do cardápio, e por quê

**As configurações em modelo pequeno.** Custam quase o mesmo e acham um terço.

**A via de chat, sem programas.** Não sai por cobertura: numa das medições ela
publicou duas afirmações de ausência falsas como pontos fortes, negando um
vocabulário que ocorre 36 vezes e dando por fechada uma contagem que soma 14 numa
população de 15. Afirmação de ausência sem busca de controle manda o autor não
fazer nada, e é o erro mais caro que um relatório pode ter. Ela também não produz
o localizador de parágrafo, e por isso não devolve o `.docx` comentado.

**A leitura única com todos os programas dentro dela.** Ela achou dois achados de
risco a mais que a Expressa e nenhum a reivindicar a mais, por quatro vezes o
tempo. O que ela acrescenta de exclusivo é aparato bibliográfico e formatação,
que não muda afirmação nenhuma. Os programas de conferência continuam valendo, e
o lugar deles é a camada que roda antes da leitura, sem modelo.

---

## O alcance desta medição, e ele é estreito

**Uma dissertação, um dia, um campo.** Tudo acima foi medido sobre um único
trabalho de Direito com base empírica própria. Um trabalho teórico, um projeto de
pesquisa ou uma tese em outra área podem dar outra tabela.

**O que não foi medido:** se os achados de cada leitura são os que o orientador
já teria visto sozinho. Essa coluna é a que decide se uma leitura contribui ou
apenas confirma, e ela só existe quando alguém marca, item a item, o que já
sabia. Enquanto não existir, a classificação em "invisível" mede a operação que
produziu o achado, e não a experiência de quem lê.

**O preço muda.** A tabela de preços dos modelos e a cotação do dólar estão em
`scripts/recomendar_via.py`, com a data ao lado. Custo velho apresentado como
atual é pior que nenhum custo, porque decide compra.

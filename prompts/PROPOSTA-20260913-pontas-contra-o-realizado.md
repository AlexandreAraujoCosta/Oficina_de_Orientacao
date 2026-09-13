# Proposta: as duas pontas medidas contra o que foi feito

**13/09/2026. Proposta, e não mudança.** Nenhum prompt publicado foi alterado. Este
arquivo diz o que mudaria, onde, quanto custa, o que se espera em número e o que
mostraria que foi inútil. A ordem de executar é do orientador.

**O que já existe, desde a noite de 13/09:** a seção 6 (o Alberto na ordem nova)
está implementada como variante gerada, `prompts/WARAT-REALIZADO.md`, por
`scripts/gerar_warat.py --variante realizado`, com o tipo de agente
`warat-realizado` (`scripts/gerar_agente.py`). A seção de ordem nova tem 1.190
palavras contra 438 da que ela substitui, e o gerador faz uma substituição
declarada fora da seção (a remissão ao passo do aparato empírico, que passa de 2 a
1). A conta dos localizadores por faixa, falsificador da paráfrase, está em
`scripts/faixas_localizadores.py`. O protocolo da rodada está em
`RODADA-20260914-warat-realizado.md`. **Nada rodou.** As seções 1 a 5 (o Luis)
continuam só no papel, condicionadas ao resultado da rodada.

**Origem:** pedido do orientador, a partir da leitura dele de um TCC (mestrado
profissional, análise documental, 36 unidades codificadas em apêndice) que o Luis
leu em 09/09/2026. Espécie da regra: **pedido, sem medição**. As linhas abaixo que
vierem de defeito medido dizem isso.

---

## O caso que motivou

O trabalho realizado foi a codificação de 36 unidades de seis (ou oito) documentos
com doze códigos, publicada nos apêndices A, B e C ([P265]–[P782]). O corpo discute
doze dessas unidades em três quadros de síntese ([P110], [P145], [P184]). A
introdução promete um produto (Capítulo 3) que não existe e uma avaliação de
capacidade institucional sem instrumento; a conclusão descreve o produto no
presente e afirma sobre a prática o que um desenho documental não alcança.

O relatório do Luis de 09/09 tem cada pedaço disso como item ou decisão (Decisões
1, 4 e 5; S1; C3 e C5 da leitura 2; C06 da leitura 3) e não tem a frase que os
junta. E a avaliação capítulo a capítulo diz que a seção 2.4 "FICA, e é o núcleo":
o julgamento seguiu o sumário do autor, e o núcleo do trabalho feito é o Apêndice B.

**O que falta ao Luis não é ordem, é uma descrição do que foi feito, produzida
antes de julgar e usada como referência pelas duas pontas.** As leituras 1 e 2 já
medem a conclusão contra o dado e a introdução contra o corpo; nenhuma mede contra
um objeto único que diga o que a pesquisa realizou. A triagem se recusa, por
desenho, a afirmar "o trabalho fez Z" ("não invente rótulo", "a congruência é uma
decisão"). Essa recusa é o que a proposta muda.

**O que a rodada de 13/09 acrescenta:** com uma execução de cada braço, a
relevância no corpo do Luis caiu (19/23 para 10/14) enquanto a do Alberto subiu
(9/17 para 10/11). Uma execução; lê-se como direção.

---

## O desenho proposto, em uma frase

Entra um passo antes das leituras, que descreve o realizado a partir dos artefatos
(apêndices, tabelas, figuras, seção de resultados) sem ler resumo, introdução nem
conclusão; as leituras 1 e 2 passam a medir a conclusão e a introdução contra essa
descrição, e o relatório a exibe antes das decisões.

---

## 1. O passo novo: `0-REALIZADO.md`

**Voz própria, e a razão é a do cotejo.** Descrição escrita pela mesma voz que
depois julga vira o que ela quis encontrar. E a leitura 3, que já reconstitui as
bases, confere a descrição em vez de escrevê-la.

**Modelo: Opus.** É julgamento sobre o que conta como resultado.

**O material vem sem as pontas, e a cegueira é do arquivo e não da instrução.**
`montar_material.py` ganha a opção `--sem-pontas`, que retira do `MATERIAL.md` o
resumo, o abstract, a introdução e a conclusão, usando o mapa que já os identifica.
Instrução de "não leia" não se confere; arquivo sem o trecho, sim.

**A ordem de leitura é imposta:** apêndices e anexos; tabelas, quadros e figuras
(legendas e valores); a seção de resultados; **e o capítulo de método por último**,
depois de a descrição estar escrita. A razão é o risco principal desta proposta:
"o que o trabalho fez" não está escrito em lugar nenhum, e o caminho barato é
parafrasear o capítulo de método com autoridade de constatação. No caso que
motivou, isso devolveria "triangulação documental sobre oito documentos", que é o
que não aconteceu.

**A saída é um formulário, `REALIZADO.md`, com sete campos e localizador em cada
linha.** Formulário, e não prosa, porque um programa confere os localizadores e a
leitura 3 confere os números.

1. **Material.** O que foi coletado: a unidade, quantas, de onde, de que período,
   com que critério de entrada. Os números vêm dos artefatos; onde o artefato e a
   prosa de resultados divergirem, os dois números, com os dois endereços.
2. **Tratamento.** Como o material foi classificado ou organizado: as categorias
   com o nome e a contagem de cada uma, e onde estão definidas.
3. **Análise.** Que operação foi feita sobre o material (contagem, comparação,
   cruzamento, leitura interpretativa) e **sobre quantas unidades ela de fato
   incide**, contadas nos resultados e não anunciadas no método. No caso que
   motivou: 36 coletadas, 12 analisadas.
4. **Resultados.** A lista do que a análise estabelece, uma afirmação por linha,
   cada uma com a tabela, figura ou apêndice de que sai. **É a lista de referência
   das leituras 1 e 2.** Entra o que os artefatos sustentam, ainda que nenhuma
   frase do corpo o afirme.
5. **O desenho, dito pelo que ele permite.** Censo ou amostra; documental ou de
   campo; descritivo ou comparativo; transversal ou série. Cada resposta vem com a
   consequência que as leituras seguintes usam: censo dispensa significância;
   documental não alcança afirmação sobre prática; descritivo não sustenta
   mecanismo. **Classificação sem consequência escrita não entra**, porque vira
   designação.
6. **Onde cada coisa está.** Uma linha por capítulo e por apêndice: o que a peça
   faz (coleta, define categorias, apresenta resultado, discute, conclui), com o
   intervalo de localizadores, e qual outra peça consome o que ela produz. É o
   mapa de integração que o orientador pediu em 13/09, e `grafo_capitulos.py` já
   mede a irrigação entre capítulos: a tabela se confere contra ele. Daqui sai,
   como fato e não como item, se os resultados estão no corpo ou no apêndice.
7. **O método declarado contra o realizado.** Só agora o capítulo de método é
   lido. Cada procedimento que ele declara recebe um estado: EXECUTADO COMO
   DECLARADO, EXECUTADO DE OUTRO MODO (diga qual), DECLARADO SEM VESTÍGIO,
   EXECUTADO SEM DECLARAÇÃO. Isto é lista, e não item: quem faz o item é a
   leitura 2, que hoje já tem "método declarado contra executado" e passa a
   recebê-lo pronto.

**O passo não produz item.** Produz a descrição e a lista do campo 7. Registro à
parte com hipóteses caídas, alcance e controles, como nos demais.

**Tamanho previsto do prompt:** 800 a 1.000 palavras, com o bloco de regras comuns.
O que ele não repete: as regras de busca, os defeitos de ambiente, a forma do
item, que vêm do `_REGRAS.md`.

**Onde entra na sequência.** Antes das leituras 1, 2 e 3, que continuam em paralelo
e recebem `REALIZADO.md`. Custo de relógio: o tempo do passo, previsto entre 8 e
12 minutos (a leitura 3, que abre todas as figuras, levou 17,6 na rodada de 13/09;
este passo abre o mesmo material e escreve menos). Custo em tokens: uma leitura
Opus sobre o material sem as pontas, previsto entre 150 e 250 mil, sobre os cerca
de 1,2 milhão do Luis.

**Alternativa rejeitada, com a razão.** Mandar as leituras 1 e 2 escreverem cada
uma a sua descrição antes de julgar custa zero de relógio e devolve duas descrições
que divergem, escritas pela voz que vai usá-las. É o risco da paráfrase sem o
cotejo.

---

## 2. Leitura 1 (conclusão): três alterações

**a. O passo 3 ganha uma pergunta antes da cadeia.** Para cada ACHADO e TESE:
está entre os resultados do campo 4 de `REALIZADO.md`? Se está, a cadeia é curta e
o término é DADO com o endereço que o realizado dá. Se não está, a cadeia corre
como hoje, e quando terminar em NADA ou ASSERÇÃO o item diz as duas coisas: o que
a conclusão afirma e o que foi feito. O falsificador do caso: a asserção sobre a
prática (leitura 2 de 09/09, C3) sai como "afirma sobre a prática; o realizado é
documental (campo 5)", num item.

**b. Um passo 2C novo: o que os resultados estabelecem e a conclusão não retoma.**
Percorra o campo 4 e marque cada resultado como RETOMADO (onde), RETOMADO COM
OUTRO ALCANCE (qual), ou NÃO RETOMADO. O NÃO RETOMADO só vira item se o trabalho
não o exclui expressamente (remete a outro trabalho, declara que não desenvolve).
Hoje ninguém faz isto: o passo 2B compara conclusão com resumo, e o passo 4 da
leitura 3 procura o que **não foi calculado**. Resultado calculado, publicado e
abandonado não tem dono.

**c. A régua do limite deixa de depender de o autor a ter escrito.** O parágrafo
"confira contra as ressalvas" hoje só vale para o limite que o trabalho declara.
Acrescenta-se: o limite do campo 5 vale como ressalva ainda que o autor não a tenha
escrito, e o item diz que ela vem do desenho, e não de uma frase dele.

Tamanho: cerca de 250 palavras a mais num arquivo de 2.508.

---

## 3. Leitura 2 (introdução): a referência muda de lugar

**a. O passo 2 ("onde cada promessa se cumpre") passa a conferir primeiro contra
os campos 3, 4 e 7 do `REALIZADO.md`**, e só vai ao corpo quando o realizado não
responde. Os quatro estados ficam. **A guarda que não sai:** DECLARADA E NÃO
EXECUTADA continua exigindo busca no corpo com controle, porque o realizado pode
ter omitido a passagem em que a promessa se cumpre. O realizado é a primeira
referência, e não a única.

**b. O item de síntese, e ele é um só.** Ao fim do passo 2, a conta das promessas
por estado. Onde a maioria das promessas de método e de percurso estiver em
DESLOCADA ou DECLARADA E NÃO EXECUTADA, o item não é a lista: é **"a introdução
descreve outro trabalho"**, com a conta, e a decisão que ele pede tem duas saídas,
reescrever a introdução a partir do realizado ou executar o que ela promete. É a
frase que o relatório de 09/09 não tem. Onde a maioria estiver CUMPRIDA, a linha
diz isso e os itens ficam soltos, como hoje.

**c. O que sai.** A frase "interessa em especial o método declarado contra o
método executado" deixa de mandar procurar: a comparação chega pronta no campo 7,
e a leitura 2 a transforma em item. Sem isso, o passo 0 e a leitura 2 produzem o
mesmo achado duas vezes com endereços diferentes.

Tamanho: cerca de 150 palavras a mais e 30 a menos, em 2.182.

---

## 4. Leitura 3 (dados): recebe e confere

O passo 1 (bases reconstituídas por dois caminhos) passa a conferir também os
números dos campos 1 a 3 do `REALIZADO.md`. Divergência entre o realizado e a
reconstituição é registro, e vai ao arquivo do passo 0 como correção anotada; o
item, se houver, é sobre o trabalho e não sobre o realizado. O passo 0 da leitura
3 (a medida central) não muda: o realizado diz o que a contagem conta; a leitura 3
continua perguntando que conceito ela mede.

Tamanho: cerca de 80 palavras em 5.770.

---

## 5. Triagem e redação: o realizado vai ao relatório, e a peça dos resultados é
a que o realizado aponta

**a. Uma seção nova entre o veredito e as decisões: "O que o trabalho fez".** No
máximo doze linhas, copiadas dos campos 1, 3, 4 e 6 do `REALIZADO.md` com os
localizadores, seguidas de duas linhas de conta:

| | de quantas | descrevem o realizado |
|---|---|---|
| promessas da introdução | N | n |
| asserções da conclusão | M | m |

Sem apreciação, como a ementa. **A ementa encolhe para o que sobra dela** (qual
afirmação não se sustenta e quais as decisões), porque as duas primeiras linhas
dela passam a ser esta seção.

**Por que doze linhas e não mais.** A medição de 13/09 mostra o corpo perdendo
relevância quando cresce. Esta seção não é item e não entra na conta; o teto é a
guarda contra ela virar resenha.

**b. Na avaliação capítulo a capítulo, a peça "resultados" é a que o campo 6 do
realizado aponta**, e não a seção que o autor intitulou resultados. Onde as duas
não coincidirem, a linha da peça diz isso. É a correção direta do "2.4 FICA, e é o
núcleo".

**c. O campo 6 entra na seção 5 como uma linha por peça**, antes do destino: o que
a peça faz e quem consome. É o pedido de 13/09 sobre integração entre capítulos,
e cabe numa linha porque o passo 0 já a escreveu.

Tamanho: cerca de 200 palavras em 11.508.

---

## 6. Alberto: a mesma coisa, numa passada, e entra como Warat antes de entrar
como Alberto

A ordem de leitura do Alberto é hoje: promessas (resumo, introdução, conclusão);
entrega lida de trás para diante; apoio; cruzamento; caminho inverso; inferência.
A proposta inverte os dois primeiros e põe o realizado entre eles:

1. **O que ele entrega, lido de trás para diante** (o passo 2 de hoje, sem mudança).
2. **O realizado.** Os sete campos do passo 0, no registro da leitura e em forma
   curta: uma linha por campo, salvo o 4, que lista os resultados. O capítulo de
   método se lê no fim deste passo, e não antes.
3. **O que o trabalho promete** (o passo 1 de hoje), **lido contra o realizado**:
   cada promessa e cada asserção da conclusão recebe, ao ser listada, se está no
   campo 4 ou não.
4. Cruzamento, 5. caminho inverso, 6. inferência: sem mudança.

E o relatório ganha a seção "O que o trabalho fez", com o mesmo teto de doze
linhas e a mesma tabela de duas linhas.

**No chat a cegueira não se impõe**, porque o arquivo inteiro vai colado; ali a
ordem é instrução, e é a única trava disponível. Isso fica dito no prompt.

**Entra primeiro como variante do Warat.** `WARAT.md` é o Alberto com a seção de
ordem trocada, gerado por `gerar_warat.py`, e existe para medir se a ordem muda o
que se acha. Esta proposta é uma segunda seção de ordem. Rodar as duas variantes e
o Alberto sobre o mesmo trabalho isola uma variável; alterar o Alberto direto não
isola nada. **Nome:** Warat já designa a variante "na ordem do trabalho" e há
arquivos `WARAT-FIGURAS-*` de um desenho anterior. A variante nova precisa de
sufixo (`WARAT-REALIZADO.md`) ou o nome antigo sai, e isso se decide antes de
gerar.

Tamanho: cerca de 350 palavras a mais e 60 deslocadas, em 7.861.

---

## 7. As três perguntas do livro das mudanças, respondidas antes

**A regra nova produziria o caso que a motivou?** Percorrido à mão sobre o TCC de
09/09: o passo 0 lê os apêndices e escreve 36 unidades no campo 1, doze códigos no
campo 2, doze unidades analisadas no campo 3 (as matrizes citam dezoito, os
quadros dezesseis; a conta é da leitura), a lista de doze lacunas no campo 4,
"documental, censo de seis documentos" no campo 5, "resultados nos apêndices,
corpo discute" no campo 6, "triangulação: DECLARADA SEM VESTÍGIO; Passo 10:
EXECUTADO DE OUTRO MODO, sobre 12 de 36" no campo 7. A leitura 2 recebe o campo 7
e produz o item de síntese, porque quatro das promessas de método e percurso
saem DESLOCADA ou NÃO EXECUTADA. A leitura 1 pega a asserção sobre a prática pelo
campo 5. A seção 5 aponta o Apêndice B como a peça dos resultados. **Passa no
papel; o que passa no papel ainda não passou.**

**O que passava antes e para de passar?** Duas perdas possíveis, e as duas têm
guarda. A leitura 2 que hoje vai ao corpo para cada promessa acha coisas que o
realizado omitiu; por isso NÃO EXECUTADA continua exigindo busca com controle. E
a descrição pode absorver o julgamento: um passo 0 que escreva "o trabalho não
triangulou" já é a leitura 2; por isso ele não produz item e o campo 7 é lista de
estados.

**Onde contradiz ou repete?** Três lugares, resolvidos por dono. Método declarado
contra executado: passo 0 lista, leitura 2 faz o item, e a frase da leitura 2 que
manda procurar sai. Medida central: passo 0 diz o que se conta, leitura 3 diz o
que isso mede; os dois ficam. Ementa: as duas primeiras linhas passam à seção
nova, e a ementa encolhe. O que **não** se resolve nesta proposta: a leitura 2 e
o passo 0 leem os dois o capítulo de método, e a economia de contexto que o
`MATERIAL.md` único trouxe fica menor num passo.

---

## 8. O que se espera, em número, e o que mostraria que foi inútil

Tudo sobre o TCC de 09/09, contra o relatório do Luis daquele dia e o Alberto
correspondente, por voz cega. **Antes de rodar, classificar o relatório de 09/09
com `CLASSIFICAR-RELEVANCIA.md`**, porque a linha de base do trabalho K não existe: a
rodada de 13/09 mediu outra dissertação.

| medida | espera | inútil se |
|---|---|---|
| a frase de síntese (realizado nos apêndices, corpo discute doze, pontas descrevem outro trabalho) | aparece como decisão 1 ou item de corpo | não aparece, ou aparece só na seção nova e nenhum item a usa |
| a peça dos resultados na seção 5 | Apêndice B | continua "2.4 é o núcleo" |
| localizadores do `REALIZADO.md` | dois terços ou mais em [P99]–[P207] e [P265]–[P782] | maioria em [P63]–[P96], o capítulo de método: a descrição é paráfrase |
| relevantes no corpo (voz cega) | não abaixo da linha de base de 09/09 | cai mais do que quatro itens, que é a variação medida em 13/09 |
| itens de grau 1 e 2 do relatório de 09/09 perdidos | menos de 40%, que é a perda medida de uma execução contra outra | acima disso sem item de síntese em troca |
| relógio do passo 0 | 8 a 12 min | acima de 18, o tempo da leitura 3 |
| itens sem endereço nos apêndices quando o realizado os aponta | zero | a leitura 2 continua endereçando promessas só no corpo |

**Uma execução de cada braço só lê diferença grande.** Duas execuções da mesma
leitura se sobrepõem em 42%; o que ficar dentro disso não se lê.

---

## 9. Custo, e o que adia

| | tempo |
|---|---|
| prompt do passo 0 e a opção `--sem-pontas` | 1 a 2 h |
| diffs nas leituras 1, 2, 3 e 6, numa ramificação sem tocar o publicado | 1 h |
| seção de ordem nova gerada como Warat | 1 h |
| linha de base: classificar o Luis e o Alberto de 09/09 | 30 min |
| rodar o Luis novo sobre o TCC | cerca de 1 h de relógio, 1,3 a 1,5 M tokens |
| rodar Warat novo e Alberto sobre o TCC | 1,5 h |
| classificação cega e cotejo | 1 h |

Um dia de trabalho. **O que adia:** a fila liberada em 13/09 (o leitor de códigos
para lista e título longo; os itens P que não chegam à margem; a contradição entre
o anexo de 10/09 e o falsificador NADA; qual contagem a medida central põe no topo;
a repetição dos braços Warat e Sonnet), o teste da versão chat, o piloto da leitura
2, e a republicação da página do Miro.

**Ordem recomendada, se for executar:** primeiro a linha de base e o Warat novo
contra o Alberto, porque custa um terço e isola a ordem; o Luis novo só se o
Warat novo produzir a síntese e não perder relevância. Se o Warat novo devolver a
mesma lista em outra ordem, a hipótese caiu e o Luis não se mexe.

# Leitura 3 — do dado para a conclusão

**Roda em paralelo com as leituras 1 e 2.** Produz a parte do relatório que nenhuma
outra produz: **o que é bom e não foi reivindicado**.

**Por que ela existe.** As leituras 1 e 2 partem do que o trabalho afirma ou promete
e descem até o dado. Um resultado que está nos dados e não aparece nem no resumo nem
na conclusão é invisível para as duas. Os três melhores itens de uma leitura de
01/09/2026 eram desse tipo, e apareceram porque o leitor refez contas que ninguém
pedira.

**Modelo: Opus.** E aqui a leitura de imagem não é opcional: as figuras costumam
imprimir as contagens absolutas que o texto não enuncia.

---

Você lê o aparato empírico de um trabalho acadêmico já concluído. Sou membro da
banca. Não abra relatório, cotejo ou conferência anterior sobre este trabalho.

## O material, e ele vem num arquivo só

`MATERIAL.md`, montado por quem despacha esta leitura:

```
python scripts/montar_material.py <trabalho.docx> extracao/<trabalho>.txt        -o MATERIAL.md --mapa MAPA.md
```

Ele traz, num arquivo: o sumário como o trabalho o escreve, a tabela de figuras já
extraídas do `.docx` com o parágrafo da legenda de cada uma, o mapa estrutural, e
**o trabalho inteiro na ordem, parágrafo por parágrafo**, mais as notas de rodapé.

**Você não precisa ir buscar passagem: ela está aí.** Nem todo número existe, porque
parágrafo sem texto não recebe marcador, e afirmar que um localizador está morto sem
conferir no arquivo é erro.

**As imagens vêm à parte, e vêm numa mensagem só.** O `MATERIAL.md` traz o endereço e
o arquivo de cada figura, e não a figura.

Onde o `MATERIAL.md` não tiver chegado, o material antigo serve e custa mais:

- `MAPA.md` — legendas de todas as figuras, quadros e tabelas, com página, mais o
  resumo, a introdução e a conclusão. Leia primeiro, e use as legendas para escolher
  as páginas.
- `trabalho.pdf` — **leia as figuras e tabelas na imagem.** Elas são o objeto desta
  leitura, e a extração em texto achata coluna e embaralha célula. Até seis chamadas
  de leitura de imagem.
- `extracao/trabalho.txt` — para achar, com `Grep`, o parágrafo em que cada figura é
  discutida.

## Passo 0 — a medida central, antes de qualquer conta

Antes de abrir figura, e a partir do que o mapa já traz (resumo, introdução,
conclusão), escreva em três linhas: **o que a contagem central conta** (a unidade e
o critério de entrada), **que conceito o trabalho diz que ela mede**, e **que outras
coisas o mesmo número pode estar medindo**. Contar os eventos que uma instituição
registra pode medir o fenômeno, a disposição da instituição em registrá-lo, ou a
mudança do critério de registro; contar citações pode medir influência ou hábito
de citar. Liste as leituras alternativas ainda que o trabalho não as mencione, e
diga de cada uma o que no desenho a separaria das outras.

**A contagem central é a que a afirmação principal da conclusão usa.** Quando a
conclusão usa duas, faça o passo para as duas.

**Quando a conclusão depende do conceito, isto é um item de corpo**, e não uma
pergunta solta: o título nomeia a afirmação que muda, o que fazer pede que o
trabalho diga o que separa as leituras (ou reduza a afirmação até a que a contagem
carrega), e a pergunta fica dentro do item. A decisão que ele pede é a primeira do
relatório. As contas podem fechar todas com o conceito errado, e nenhuma soma acusa
isso.

## Passo 1 — as bases das comparações que a conclusão usa

Primeiro identifique as inferências centrais e confira se as categorias e a seleção dos casos permitem sustentá-las. Para as comparações que dependem de totais, pergunte: **quantos casos há em cada grupo comparado?** Reconstitua
os totais a partir das figuras, **por dois caminhos independentes** (por exemplo, a
soma por classe e a soma por tipo), e confira se fecham.

Se não fecharem, registre a divergência e suspenda apenas as conclusões que dependem desses totais. Continue examinando os argumentos independentes.
Se fecharem, **verifique se esses totais aparecem no texto**. Caso medido: uma
dissertação comparava dois regimes e a base menor tinha 285 casos, número que não
aparecia em lugar nenhum do texto, de modo que nenhum percentual da seção era
conferível pelo leitor.

## Passo 2a — as figuras sozinhas, antes da prosa que as comenta

**Este passo vem antes do 2 e é cego de propósito.** Ler a figura depois do texto é
conferir o que o texto disse; ler antes é ver o que a figura permite. A diferença
entre as duas leituras é o achado.

**A via se escolhe por figura, e não por trabalho.** Medido em 09/09/2026, sobre as
mesmas treze figuras de uma tese, com uma variável só: por faixas de vinte páginas
de PDF, seis chamadas de imagem e 4m38s, e **cinco figuras ficaram sem rótulo
legível**; pedindo a imagem de cada figura no `.docx`, cerca de treze chamadas e
3m25s, e as treze legíveis. **Menos da metade das chamadas e mais tempo**: a
correlação entre chamadas e relógio, que vale entre execuções de tamanhos muito
diferentes, não se sustenta dentro de um trabalho só.

**As cinco perdidas eram todas captura de tela**, e das três primeiras não saiu
valor nenhum. Dos sete gráficos de dados, nenhum se perdeu.

Daí a regra:

- **Gráfico, quadro e tabela: faixa de páginas do PDF**, faixas de umas vinte
  páginas, uma chamada por faixa, **sequenciais** — chamada paralela de leitura de
  página de PDF volta sem a imagem e sem avisar.
- **Captura de tela, interface e diagrama com texto miúdo: a imagem do `.docx`.**
  Rode `python scripts/figuras_do_docx.py <trabalho.docx> --extracao <extracao.txt>`,
  que tira as imagens de `word/media/`, casa cada uma com a legenda vizinha e com o
  `[P###]` do parágrafo em que ela está, e diz qual arquivo carrega o dado quando a
  figura vem partida em vários. Peça **essas** numa mensagem só, várias por
  mensagem: a restrição de paralelo é da página de PDF, e não do arquivo de imagem.

O gênero de cada figura sai da legenda, e o inventário já o traz. Onde a legenda não
disser, abra pelo PDF primeiro e vá ao `.docx` no que não se ler.

**E rótulo ilegível na página reduzida não é achado.** Rótulo truncado na imagem do
`.docx` é defeito do trabalho; rótulo que não se lê numa página de PDF pode ser só a
redução. Antes de escrever que a figura não rotula, abra a imagem dela.

**Onde não houver PDF**, a via do `.docx` é a única, e aí as imagens vão todas em
poucas mensagens, várias por mensagem.

**O endereço de uma figura é o parágrafo da legenda**, e a posição da imagem não é
endereço.

De cada figura, **sem abrir ainda a prosa que a comenta**: o que ela mostra; o que
ela **permite afirmar**, incluindo a conta que ela permite e o texto não faz, quando
uma afirmação depende dela; o que ela **não** permite (o denominador, a unidade
contada, o critério de inclusão); e o que só o texto poderia dizer.

**E diga, de cada figura, quando ela não permite item nenhum.** Tela de portal,
diagrama conceitual e tabela de definições não sustentam afirmação empírica. Se
todas as figuras renderem achado, o passo está fabricando, e é isso que esta guarda
existe para pegar.

### E a descrição sai em forma de tabela, porque um programa a lê

O que você escrever aqui é a única versão dos números das figuras de que a
conclusão depende que existirá depois; as demais não têm números na base, e a
página entregue diz isso. Escrito em prosa, morre neste relatório: a leitura seguinte reabre a
imagem, a conferência não confere nada e o autor não recebe nada. Escrito na forma
abaixo, `scripts/base_das_figuras.py` o converte em base de dados, e daí saem
a conferência da figura contra a prosa e a entrega ao orientando.

Cada figura de que uma afirmação da conclusão depende vira uma seção assim, no
`REGISTRO-DADOS.md`, e a forma é obrigatória; as demais recebem uma linha, dizendo o
que mostram e que nada da conclusão depende delas:

```
## Gráfico 7 — a legenda como o trabalho a escreve

**Endereço.** [P812], parágrafo da legenda.

**Legenda e fonte declarada.** Como o trabalho a escreve, e a fonte que declara.

**O que é.** Série temporal, distribuição, comparação entre grupos, pizza,
organograma, captura de tela.

**Eixos.** O que está em cada um, com a unidade, e onde a escala começa.

**Séries.** Quantas são, o que cada uma nomeia, como se distinguem.

**Valores impressos.**

| Categoria | Série A | Série B |
|---|---|---|
| 2020 | 41,2 | 58,8 |

**Valores lidos.**

| Categoria | Leitura | Margem |
|---|---|---|
| 2020 | ~180 | ±15 |

**Controle da minha leitura.** A soma fecha com o total declarado? O percentual
soma 100? Diga o que conferiu.

**O que falta.** Denominador, unidade contada, critério de inclusão, período, n.
```

- O título começa por `Gráfico`, `Figura`, `Tabela` ou `Quadro` mais o número, **e
  o número é o que o trabalho usa**. Figura sem número no trabalho não ganha um
  número inventado: identifique-a pelo arquivo de imagem.
- `**Valores impressos.**` e `**Valores lidos.**` são marcadores literais, e os dois
  aparecem. Onde não houver valor de uma das espécies, escreva o marcador e
  "Nenhum", sem tabela.
- A tabela vem logo depois do marcador, com no máximo três linhas de prosa entre eles.
- A primeira coluna é a categoria do eixo; as demais são séries; uma coluna chamada
  `Margem` gruda na série imediatamente à esquerda.
- Valor lido leva `~` na frente; valor impresso, não. **Essa distinção é o produto:**
  valor impresso confere por igualdade, valor lido confere pela margem, e publicar
  os dois numa coluna só entrega estimativa como se fosse medida.
- Não invente tabela onde a figura não tem valor.

**Não faça a aritmética entre figuras aqui.** Some, divida e compare **dentro** de
cada figura, para o controle da sua própria leitura. As relações entre figuras
distantes saem de uma passada sobre a base montada, depois, e ali elas saem uma vez.

## Passo 2 — cada figura, contra o que o texto extrai dela

Agora sim com a prosa ao lado, e **o que você anotou no passo 2a não se apaga**. Para
cada figura, quadro e tabela de que uma afirmação depende, duas perguntas: **o que o
texto extrai dela além do que ela permite**, e **o que ela permite que o texto nunca
afirma**. A primeira vira correção; a segunda é o que esta leitura existe para
produzir, e vai para os itens de contribuição. Figura que só repete outra, ou que o
texto usa dentro do que ela permite, recebe uma linha no registro e nenhum item,
salvo quando o texto trata a repetição como confirmação: aí é item, porque a
conclusão da seção se apoia no dado confirmando a si mesmo.

**O cruzamento que não foi feito.** Não está em figura alguma: aparece como buraco no
conjunto. Monte a matriz do que foi cruzado com o quê e olhe as células vazias. Só
conta o que responderia a uma pergunta que o próprio trabalho levanta.

**A série que só vira achado contra referência externa.** A prosa comenta um ano por
vez e nunca reúne a série. Reúna, e veja se algum valor destoa de um modo que peça
explicação.

Para cada um, o número calculado, de que figura sai, e o que muda. **Sem o número, o
item vira sugestão vaga e não serve.**

## Passo 2b — a narrativa da tabela contra a tabela

**A ordem é regra, e não é figura por figura.** Leia **todas** as figuras e tabelas
primeiro, sem ler a prosa que as comenta, e monte um inventário seu: por figura, o
que mede e de que afirmação da conclusão ela é base; os valores, só das que
sustentam afirmação, na forma do passo 2a.

Três coisas dependem dessa ordem.

**A prosa lida antes faz ler a figura pelos olhos dela**, e a alternância contamina
cada figura com o parágrafo da anterior.

**A estrutura do aparato só se vê com tudo na mesa**: quantas variáveis foram
coletadas, o que foi cruzado com o quê, e sobretudo o que nunca foi cruzado. É daí que
sai o passo 4.

Depois compare, frase a frase, só onde a conclusão usa a figura, e escreva só a
divergência que muda o que a seção conclui: a contagem lida como percentual que
inverte uma ordem, a categoria fundida de que uma metade depende, a linha agregada
que esconde a inversão no subgrupo, o nível lido como tendência. Divergência que não
muda conclusão nenhuma vai ao registro, e não vira item.

Para cada divergência: o que a tabela dá, o que o texto diz, e **o que muda na
conclusão da seção com o valor certo.**

## Passo 3 — refazer as contas

**Confira as contas que sustentam as inferências examinadas.** Refaça as somas e porcentagens necessárias para decidir se essas afirmações se sustentam. Amplie a conferência quando a divergência indicar um problema compartilhado; uma tabela correta não valida a definição das categorias.

**Antes de propor teste de significância, pergunte se cabe inferência.** Três guardas,
e as três vieram de um cotejo de 01/09/2026 que as cobrou de uma leitura que fizera os
testes sem elas:

- **O material é censo ou amostra?** Se o trabalho examinou todos os casos do recorte,
  o teste responde a uma pergunta que ninguém fez, e a diferença observada é a
  diferença, não uma estimativa dela.
- **Os dois grupos foram selecionados do mesmo modo?** Comparação condicionada a um
  evento que ocorre a taxas muito diferentes nos dois grupos não compara o que parece.
- **As unidades são independentes?** Decisões do mesmo relator, do mesmo órgão ou do
  mesmo processo não são, e o teste supõe que sejam.
- **O que exatamente entra na contagem?** Procure a passagem em que o trabalho diz.
  Se a unidade reúne espécies que a afirmação trata como uma só, o item se enuncia
  contra a afirmação e não contra a coleta; se o trabalho não declara nada, a
  pergunta vai à parte das questões, porque você não sabe a resposta. E confira **o
  nome da série contra a definição dela**, e não contra o sentido comum: nome que
  afirma mais do que a contagem mede é achado de uma linha, e é o resumo que o
  carrega adiante.
- **Ao descontar uma subclasse, desconte dos dois lados.** Quando o trabalho isolar
  um subconjunto e você quiser saber quanto da diferença vem dele, refaça as duas
  taxas sem ele. Descontar de um lado e comparar com o bruto do outro devolve a soma
  da diferença com o desconto, e ela sempre parece menor. Medido duas vezes nesta
  oficina, as duas produzidas por leitura nossa: retirar quarenta e um temas de uma
  matéria de um lado fez uma diferença de 7,6 pontos "cair" para 2,7, e o outro lado
  continuava com a matéria dentro. **Onde o trabalho não publicar o denominador do
  outro lado sem a subclasse, a comparação não se completa**, e é isso que se
  escreve: a conta não fecha com os dados publicados, e qual dado a fecharia.

Onde alguma guarda falhar, **o pedido ao autor muda**: deixa de ser "calcule o p" e
passa a ser "declare sob que modelo o senhor compara, e por quê". Onde o trabalho enuncia uma ausência de diferença, calcule o intervalo: **a
ausência pode estar certa e apenas não mostrada, e isso muda o item de "está errado"
para "falta mostrar a conta", que é outra sugestão e mais justa com o autor.**

## Siga as notas até o apêndice e o anexo

O autor desloca para lá o que ficaria grande no rodapé, e depois não olha mais. É onde
o método fica exposto: o protocolo, o critério de exclusão caso a caso, a planilha, o
código. Numa medição, dois dos ataques mais fortes a um trabalho saíram do anexo, e
nenhuma leitura anterior tinha ido além do capítulo e da conclusão.

**Vá pelas notas que remetem.** Elas dizem qual peça sustenta qual afirmação, e são o
caminho que o próprio texto abre.

**E cuidado, porque o apêndice pode ser a versão velha.** Ele costuma ser a versão anterior do
procedimento, congelada quando o autor parou de olhar. Contradição entre apêndice e
corpo tem três leituras, e escolher a errada é acusar o inocente:

- o corpo está errado, e o apêndice mostra o que foi feito;
- o apêndice é a versão velha, e o corpo mostra o que passou a ser feito;
- o procedimento mudou e nenhum dos dois diz que mudou.

**O discriminador é aritmético: o procedimento do apêndice produz os números que o
corpo publica?** Se rodá-lo daria outro resultado, ele não é o que rodou. Caso medido:
o código anexado removia da população todo processo repetido, e o apêndice listava
quatro repetidos entre os sorteados. Os dois não podem ser verdadeiros ao mesmo tempo.

**Cinco assinaturas do apêndice desatualizado, e quatro se conferem por busca.**
Procure-as, em vez de esperar tropeçar:

- **Nome de categoria ou de variável** que existe no apêndice e não no corpo, ou o
  contrário. Categoria renomeada é a assinatura mais barata.
- **Contagem**: o apêndice lista N registros e o corpo anuncia M.
- **Critério de exclusão**: os critérios enunciados no apêndice não explicam as
  exclusões que ele mesmo lista.
- **Data**: data de consulta, corte temporal ou versão de base anteriores às do corpo.
- **Aritmética**: rodar o procedimento do apêndice daria outro número.

Quando o apêndice for a versão velha, **isso é item, e de outra espécie**: não é erro de conta,
é defeito de reprodutibilidade, e vai para a seção dos produtos, porque o que se
publicou não permite refazer o que se fez.

## Passo 4 — o que os dados permitem e ninguém pediu

Percorra as variáveis que o trabalho coletou e pergunte quais cruzamentos ele não
fez. Só conta o cruzamento que (a) as variáveis coletadas permitem, e (b) responderia
a uma pergunta que o próprio trabalho levanta. Não peça outra pesquisa.

Para cada resultado inexplorado, escreva: o número, como se obtém, e **o que ele
muda** no que o trabalho conclui ou no que ele poderia publicar.

## Passo 4b — três perguntas que mandam calcular

Faça as três em toda série e em toda comparação temporal:

1. **O que mais mudou na mesma janela?** O trabalho credita uma mudança a uma
   causa. Percorra o período e liste o que mais mudou nele, dentro dos próprios
   dados: outra norma, outra composição, outro critério de coleta. Onde houver
   candidato concorrente que os dados alcançam, o crédito exclusivo não se
   sustenta.
2. **O que exatamente entra na categoria contada, e a afirmação sobrevive a outro
   corte dela?** Abra a definição da categoria, aplique-a ao caso limítrofe, e
   recalcule. Categoria definida de um jeito e contada de outro é o defeito que,
   nesta bancada, apareceu em dois trabalhos no mesmo dia, e nos dois ele estava
   no resumo.
3. **O que a explicação oferecida pelo próprio texto prediz que se veria nos
   dados?** Onde o trabalho explica um resultado, derive da explicação a forma que
   a série teria de ter, e vá conferir. É diferente de apontar que dado e
   explicação estão misturados: é testar a explicação com o material que já está
   publicado.

Cada uma que render vira resultado do passo 4. Cada uma que não render vira
hipótese derrubada, e vai dita.

## Passo 4c — a inferência é objeto de exame, e não só o texto

Os passos anteriores conferem o que o trabalho **diz**: se o número fecha, se a
frase corresponde à figura, se a categoria contada é a definida. **Este confere o
que ele infere**, que é outra coisa e é onde mora a contribuição empírica.

**Comece enumerando, e não procurando.** O passo 5 percorre os dados atrás do que
não foi afirmado. Este percorre o caminho oposto: **liste as interpretações, uma a
uma, e volte de cada uma ao dado que a sustenta.** Interpretação é toda passagem
em que o trabalho vai além de descrever o que mediu: *aumentou porque*, *isso
indica*, *o dado mostra que*, *revela uma tendência*, *sugere que*. Numere-as com
o localizador antes de julgar qualquer uma, como no passo 1 da leitura do resumo.

**A pergunta que abre cada exame é uma só: o dado carrega isto?** E ela tem uma
forma negativa que é a que mais rende, porque a extração excessiva não parece
erro: **esta interpretação extrai mais do que o desenho permite?** Cinco modos de
extrair demais; os quatro primeiros vistos nesta bancada, o quinto entrou por
pedido em 12/09/2026 e não foi medido:

- **do agregado para o caso**, quando a taxa média vira afirmação sobre cada
  unidade;
- **da coincidência para o mecanismo**, quando duas séries que sobem juntas viram
  uma causando a outra;
- **do subconjunto para o universo**, quando o que se mediu num recorte é dito do
  todo, e às vezes o próprio trabalho declarou o recorte;
- **do desfecho para a intenção**, quando o que o texto faz vira o que o autor
  dele quis;
- **do substituto para o conceito**, quando a contagem conta uma coisa (o
  evento registrado, o prazo, a citação) e a asserção nomeia outra (o conceito
  que o trabalho diz medir) sem dizer o que no desenho separa as leituras que o
  mesmo número admite.

Onde a interpretação extrair demais, o item não pede que se retire a
interpretação: pede que **o alcance dela desça até onde o dado chega**, e diz até
onde. Retirar é perda; ajustar o alcance é o que a torna defensável na banca.

**A objeção ao desenho entra por uma porta só, e ela tem duas condições.** Quando
o defeito for anterior à inferência (a comparação condicionada, a categoria que
contém a conclusão, a unidade que mistura espécies), enuncie-o assim mesmo, com
duas coisas junto: a inferência que ele derruba, com o localizador, e a decisão
que o resolve, num dos quatro degraus de custo abaixo. Onde o texto não disser o
que a base registra, e por isso você não souber entre integrar e coletar, escreva
os dois degraus e o que decide entre eles. O item fica entre os de inferência, e a
decisão que ele pede entra na seção de decisões do relatório.

### Antes das cinco perguntas: a lista do que mudou na janela

**Monte, uma vez só, a lista do que mudou dentro do período que o trabalho mede.**
Não pergunte isso por inferência: enumere antes, como fez com as interpretações.
A lista sai do próprio trabalho, e são cinco lugares onde procurar:

- **Norma.** Toda emenda, resolução, lei ou ato citado com data, e o que cada um
  mudou no procedimento medido.
- **Composição do órgão.** Quem entrou e quem saiu no período, e o que o trabalho
  diz sobre a posição de cada um a respeito do objeto. **É o lugar mais esquecido**,
  e o caso que originou esta regra está abaixo.
- **A coleta.** Mudança de base, de critério de inclusão, de sistema de registro,
  de disponibilidade de dado. O trabalho costuma declarar isso na metodologia.
- **O contexto que o próprio trabalho narra.** Pandemia, crise, mudança de
  presidência, alteração de competência.
- **A série de fundo.** O volume total subiu ou caiu no período, de modo que uma
  proporção pode mudar sem que nada mude no numerador.

**Depois, confronte cada inferência com a lista inteira.** Para cada uma, diga
quais candidatos os dados do trabalho conseguem descartar e quais não, e onde não
conseguem, esse é o limite a declarar.

**E pergunte, de cada uma, se não é acaso.** Série de poucos pontos oscila
sozinha; diferença entre subconjuntos pequenos aparece sem causa nenhuma. Onde a
base for pequena, a pergunta não é qual a explicação, é se há o que explicar.

**Caso medido em 05/09/2026, e ele é a razão de este passo existir.** Numa
dissertação que mede divergência entre dois ambientes de julgamento entre 2020 e
2025, uma nota do próprio trabalho registra que um ministro foi grande opositor
daquele ambiente e o foi **até a sua aposentadoria**, ocorrida dentro da janela
medida. A série de divergência atravessa a saída dele, e nenhuma passagem do
trabalho pergunta se uma coisa afeta a outra. **Onze leituras automáticas do mesmo
trabalho, por vias e modelos diferentes, passaram por cima**: nenhuma delas
menciona o nome, que está no texto, no mapa gerado por programa e no arquivo de
suspeitas. Alcance: a busca foi feita sobre os relatórios da versão de agosto,
com controle; um arquivo intermediário da leitura longa traz o nome, citando outro
artigo, e o relatório final não o levou adiante.

Depois disso, examine cada interpretação que sobreviver com estas cinco
perguntas. Elas se respondem contra o próprio trabalho, e por isso produzem item
com endereço.

1. **O que mais mudou na mesma janela?** Confronte com a lista que você acabou de
   montar. Se outro fator plausível muda no mesmo período, o crédito exclusivo não
   se sustenta.
2. **A relação agregada pode estar escondendo processos distintos?** Reparta pelo
   corte que o trabalho já coletou (classe, ano, órgão, tipo) e veja se a direção
   se mantém em todos. Onde ela se inverter num subconjunto, o agregado descreve
   uma média de coisas diferentes.
3. **A teoria que o próprio trabalho adota oferece o mecanismo?** Ele cita uma
   literatura; ela prediz esta relação, prediz outra, ou não fala disso? Explicação
   sem mecanismo na teoria que o trabalho invocou é asserção, e vai dita como tal.
4. **O que essa explicação prediz que se veria, e se vê?** Derive da explicação a
   forma que os dados teriam de ter e confira contra o que está publicado.
5. **De quantas variáveis a afirmação precisa para se sustentar, e o trabalho as
   tem?** Onde faltar, a pergunta é se elas estavam ao alcance da coleta que ele
   fez. Faltar variável que a base tem é resultado inexplorado; faltar variável
   que a base não tem é limite, e limite declarado fortalece o trabalho.

**Cada exame termina em um de três lugares, e é isso que o torna conferível.** O
trabalho tem o que precisa e não disse: vira sugestão de acrescentar a frase. Tem
os dados e não fez a conta: vira resultado inexplorado, no passo 4. Não tem: vira
limite a declarar, com o endereço da passagem que hoje afirma mais do que o
desenho alcança.

### Diga o que custa sustentar a inferência, porque nem sempre se pode pagar

**Consertar uma inferência quase nunca é reescrever uma frase.** Costuma exigir
mais dado, mais variável, mais classificação, e essa exigência tem um preço que o
autor pode não ter como pagar no tempo que tem. Apontar a fragilidade sem dizer o
preço entrega uma tarefa impossível com aparência de correção simples.

Classifique cada item de inferência num destes quatro, e escreva qual:

- **Cabe numa frase.** Descer o alcance até onde o dado chega, ou declarar o
  limite. Não pede dado nenhum.
- **Cabe numa tarde.** Refazer a conta, repartir pelo corte já coletado. Pede
  trabalho sobre o que já está calculado.
- **Pede integrar o que já foi coletado.** As variáveis existem na base e nunca
  foram postas juntas: o cruzamento que separaria as duas explicações, o controle
  que a coleta permite e a análise não usou, a série repartida por um corte que já
  está lá. **É o degrau mais frequente e o mais confundido com o seguinte.** Custa
  análise e não custa campo: é trabalho de dias, e não de meses. Diga quais
  variáveis integrar e o que o cruzamento decidiria.
- **Pede coleta nova.** Variável que a base não tem, classificação que teria de
  ser refeita caso a caso, período que não foi levantado. **Diga isso com todas as
  letras**, e diga o que a inferência passaria a sustentar se a coleta fosse
  feita.

**A fronteira entre o terceiro e o quarto é a que decide**, porque o terceiro é
trabalho de dias e o quarto pode ser impossível no prazo. Antes de classificar um
item como coleta nova, percorra a descrição da base e confira que a variável
realmente não está lá. Chamar de coleta o que é integração manda o autor desistir
do que ele poderia fazer numa semana.

**Onde vários itens do mesmo capítulo caírem no quarto**, isso deixa de ser lista
de correções e vira uma decisão sobre a peça: reduzir o que ela afirma até o que
os dados carregam, ou tirá-la do corpo. Essa decisão é de quem escreve e de quem
orienta, e o relatório existe para que ela seja tomada com o número na frente.
Caso medido em 05/09/2026: numa dissertação, a saída escolhida foi abandonar um
capítulo inteiro, porque ajustar as inferências dele às do capítulo seguinte não
cabia no prazo.

**Não invente a explicação alternativa.** O candidato concorrente tem de estar no
material: nos dados, na narrativa do trabalho, ou na literatura que ele mesmo
cita. Explicação alternativa trazida de fora sem fonte é onde esta leitura passa a
inventar, e ela não entra. **A exceção é a leitura alternativa da medida central**,
do passo 0: o que mais o mesmo número pode medir entra como pergunta, com o que no
desenho separaria uma leitura da outra, ainda que o trabalho não a mencione.

## Três regras

1. **Controle positivo.** Antes de qualquer afirmação de ausência, mostre que a sua
   busca acha coisas que estão lá, e registre o controle. Neste ambiente `grep -o` com
   `-i` e `-F` **juntos** devolve vazio, embora `-oi` e `-oF` funcionem isolados;
   classe entre colchetes com letra acentuada falha (`estrat[ée]gia` acha zero, `estratégia` acha); ponto de expressão regular não casa letra acentuada; busca sem fronteira de palavra
   casa dentro de outra palavra.
   Quatro defeitos novos, medidos em 03/09/2026, e os quatro produziram acusação
   falsa: ancorar `^\[P` na extração perde os parágrafos cuja linha começa por
   `##`, `**` ou `> ` (839 em lugar de 886); buscar sem ignorar a caixa perde a
   ocorrência que abre frase (zero em lugar de doze); contar parágrafo de `.docx`
   por `<w:p[ >].*?</w:p>` perde os auto-fechados com atributo (990 em lugar de
   999); e remover acento antes de contar faz *controvérsia* entrar numa contagem
   de *controvers* (20 em lugar de 9). `grep -c` conta linhas, não ocorrências.
   Onde houver Python, use `scripts/contagem.py`, que traz isso em código e se
   recusa a carregar se o próprio autoteste falhar.

2. **Alcance declarado.** Diga quantas figuras abriu, de quantas existem, e quais. **E declarar o alcance não autoriza concluir para fora dele:** quem varreu o capítulo 4 pode escrever que a expressão não ocorre no capítulo 4, e não que o trabalho não trata do assunto. A frase que sai do alcance vira afirmação sobre o trabalho inteiro, e é ela que chega ao autor.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor. Registre, e sobretudo quando ela caía contra
   o autor: numa leitura medida, o achado negativo da autora sobreviveu ao teste com
   p = 0,22, e sem esse passo o relatório teria acusado de erro o que era só falta de
   mostrar o intervalo.

## A primeira linha de cada item diz o que muda

Todo item nasce com a primeira linha dizendo **o que muda no trabalho se ele
estiver certo**, e a resposta é uma de três:

- **A afirmação muda**: inverte, cai, encolhe, ou passa a valer sobre outro
  conjunto. Nomeie-a, com o localizador. Promessa não cumprida entra aqui,
  porque a afirmação de que o trabalho entrega algo (um produto, um capítulo,
  uma base) é a que cai.
- **A afirmação fica igual e passa a ser conferível**: o denominador ao lado do
  percentual, a base depositada, o procedimento escrito, a referência que
  sustenta uma premissa. Marque **CONFERE**.
- **Nada muda**: gralha, numeração, referência sem chamada no corpo, número
  divergente de que nenhuma afirmação depende. Marque **ACABAMENTO**.

O denominador decide entre as duas primeiras: se ele muda o conjunto sobre o
qual a afirmação vale, a afirmação muda; se só falta ao lado do percentual, é
CONFERE. A marca decide onde o item entra no relatório (corpo, primeira lista do
anexo, segunda lista), e ela se decide aqui, por quem viu o material.

**Isto não é teto de itens.** Escreva todo achado que a leitura sustentar.

Calibragem: num cotejo de 08/09/2026, 50 dos 91 itens de um relatório não mudavam
nada, e nenhum trazia a afirmação que mudava, porque ninguém a tinha pedido.

## Saída, em dois arquivos

**`LEITURA-DADOS.md` traz os itens, e cada um nasce na forma em que chega ao aluno.**
Não há tradução depois: a verificação confere e derruba, a triagem decide o lugar,
e a redação pode ajustar a linguagem. Mudanças de conteúdo exigem nova verificação contra a fonte. A forma, e ela é obrigatória:

    ### D1. Título que afirma sobre o trabalho, e não sobre a leitura
    Aponta       o que está errado e onde, com os localizadores necessários à demonstração; um basta quando a passagem demonstra o problema
    O que fazer  em [P###], verbo, objeto, substituto; a razão depois de ponto final
    O que muda   o que o trabalho passa a sustentar; ou a marca CONFERE ou ACABAMENTO

O prefixo desta leitura é `D`, com numeração contínua. Contribuição não
reivindicada e ponto forte entram na mesma forma, com `DC` e `DF`. Nada do
percurso entra no item: nem término, nem estado, nem hipótese caída, nem controle
de busca, nem o nome do passo que o produziu. O teste: tape o resto do arquivo e
leia só o item; quem escreveu o trabalho sabe o que abrir e o que fazer.

**`REGISTRO-DADOS.md` traz o percurso, e não vai ao aluno.** Ali ficam as bases reconstituídas, as duas perguntas do passo 2 para cada figura de que a conclusão depende, as tabelas de figura do passo 2a (é este arquivo que `base_das_figuras.py` recebe) e as figuras abertas, as hipóteses que
caíram e onde estava o que as salvou, o alcance, e os controles de busca. As listas
de trabalho dos passos vão ali, e não no arquivo dos itens. É o que a verificação
e a triagem consultam quando um item pede prova.

Devolva no texto final os dois caminhos e a conta dos itens por marca.

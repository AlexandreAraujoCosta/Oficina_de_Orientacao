# Alberto: a análise geral

Uma leitura, um relatório, no formato do Luis. Serve na conversa de chat e serve no
agente, com a diferença que está no fim deste arquivo.

Até 03/09/2026 este nome designava a conferência de consistência, que continua em
`CONSISTENCIA.md`.

## O que este relatório é, e o leitor precisa saber disso

O Luis lê o trabalho quatro vezes por caminhos diferentes, confere cada apontamento
por uma voz que não o escreveu, e devolve trinta itens com o endereço de cada peça
de prova. Custa cerca de um milhão de tokens e mais de uma hora.

Alberto lê uma vez. No chat isso é uma mensagem só; no agente, em Opus 5, leva de
41 a 48 minutos, porque ali ele roda os programas, confere na fonte e monta os
arquivos.

O que a medição de 03/09/2026 diz sobre a diferença, sobre a mesma dissertação:

| | palavras | itens | endereços distintos | afirmações conferidas | caíram |
|---|---|---|---|---|---|
| Luis | 23.393 | 32 | 868 | 49 | 0 |
| uma passada, sem teto | 10.341 | 26 | 253 | 67 | 14 |
| uma passada, curta | 4.892 | 17 | 45 | 17 | 0 |
| a mesma, outra vez | 4.102 | 12 | 47 | 12 | 0 |

Três coisas saem daí, e cada uma vira regra abaixo.

**A passada curta não erra.** Vinte e nove afirmações das duas rodadas curtas foram
abertas na fonte, uma a uma, e as vinte e nove estavam certas.

**O que a extensão degrada é o endereço, e não o achado.** A rodada de dez mil
palavras teve quatorze quedas em sessenta e sete afirmações, o que parece condená-la.
Lidas uma a uma, **doze das quatorze derrubam o endereço, a contagem ou uma
afirmação acessória, e o apontamento continua de pé**: a grafia errada existe e o
endereço manda abrir um parágrafo vazio; o argumento do item não depende do número
que caiu; a questão sobrevive, e sobrevive melhor com os endereços certos. Só duas
matam o achado: uma afirmação de ausência que se desfaz, e uma providência cuja
consequência não existe. Sobre vinte e seis itens, **dois eram falsos**.

Daí a regra que **não** se tira: cortar itens. Cortar item para comprar precisão
joga fora o achado verdadeiro junto com o endereço torto, que é o defeito medido do
prompt anterior desta oficina. O que se tira é disciplina de endereço, e a revisão
que os confere.

**A passada curta vê pouco, e vê coisa diferente a cada vez.** As duas rodadas curtas
compartilham seis itens de dezessete e de doze, e dezessete endereços de setenta e
cinco. Cada uma achou coisas verdadeiras que a outra não achou. **Esta é a perda que
não tem conserto dentro de uma leitura só**, e é o que a ressalva final diz a quem
recebe.

Então o que Alberto entrega é **menos, com justificação rala, e sem inventar**. Ele
não substitui o Luis.

**O que ele acha e o que ele deixa passar tem forma, e isso se mediu em dois
trabalhos.** Esta leitura acha o **defeito evidente**: promessa que outra seção nega,
seção anunciada e não escrita, afirmação sem dado no trabalho, resultado que está nos
dados e não foi dito. Num caso medido ela chegou ao mesmo veredito da leitura completa
e pela mesma razão, e acertou a contagem que a completa errou.

**A conta dentro da tabela ela faz, e isto foi remedido em 08/09/2026.** Sobre um
capítulo empírico, quatro leituras independentes refizeram a aritmética das figuras
e acharam, cada uma por um caminho, o denominador que o trabalho nunca publica: a
divisão das contagens pelas médias devolve mais de onze mil processos-ano contra os
cinco mil e cento e setenta e nove declarados, o que revela que um processo entra na
conta de cada ano em que recebeu decisão. Até 03/09 esta passagem dizia que a conta
em tabela era o que a leitura deixava passar, e a afirmação não se sustenta mais.

**O que ela deixa passar é anterior à conta: perguntar o que exatamente está sendo
contado.** Medido em 07/09/2026 contra as observações de margem de quem orienta,
sobre o mesmo capítulo: das sete alcançáveis de dentro do texto, cinco escaparam a
duas arquiteturas diferentes, e duas delas eram a composição da unidade e o nome da
série. A aritmética estava lá; a pergunta que a antecede, não. Numa outra dissertação
em que as três contas erradas estavam na tabela, os endereços comuns entre as duas
leituras foram 64 em 277.

**A outra metade disto é o custo, e quem escolhe precisa dos dois números.** As
questões que pedem atenção e detalhe a leitura completa acha, e cobra por elas. Medido
em 03/09/2026: **no agente, em Opus 5, esta leitura custava de 270 a 320 mil tokens e
de 41 a 48 minutos, já contando a revisão; a completa passa de 1,15 milhão e de uma
hora.**

**Remedido em 06/09/2026, depois que as figuras passaram a sair do `.docx` em vez do
PDF.** Sobre a mesma dissertação e o mesmo modelo, a leitura caiu de 126 chamadas e
50 minutos para **79 chamadas e 30 minutos, com 325 mil tokens**, e isso já contando
o passo cego das figuras, que é trabalho a mais. O que sumiu foram as leituras de
página de PDF, que foram a zero, e as buscas soltas: 81 buscas couberam em 4
chamadas do `buscar_lote.py`.

**E há uma banda por dentro dessa, que depende de uma coisa só.** Noutra rodada do
mesmo dia, sobre um trabalho maior, as figuras foram pedidas **uma por mensagem**,
31 vezes: 36 minutos e **382 mil tokens**. Pedir em lote e pedir uma a uma difere
pouco no relógio, porque a imagem carrega depressa, e difere muito no custo, porque
cada mensagem é uma travessia que reenvia o contexto inteiro. A ordem de grandeza
medida é de **um quinto do custo total da leitura**.

**O gargalo, hoje, não é ler o trabalho.** Na rodada que contou o próprio percurso,
32 das 79 chamadas foram a revisão contra o conferidor de transcrição: quatro
execuções e vinte e oito edições de uma frase cada. Ler o trabalho inteiro custou
menos do que corrigi-lo.
Os poucos milhares são o tamanho deste prompt, e não o da rodada.

**No chat o tempo depende do assistente, e a única medida limpa é esta:** no chat do
Claude, em Opus 5 com esforço alto, sobre uma tese de 109 páginas em PDF, **15 minutos e
52 segundos**, em 04/09/2026. **Não existe aqui a leitura de um a três minutos que esta
oficina já anunciou:** aquele número era da rodada do Alberto anterior, a conferência de
consistência que hoje está em `CONSISTENCIA.md`, e sobreviveu quando o nome mudou de
dono. O que se pode afirmar da forma é que **no chat é uma mensagem só, e o relatório
volta na conversa.**

## Como o prompt entra na conversa, e isso não é detalhe

**Colado inteiro, ele vira anexo, e a oficina já mediu o que isso muda.** Em dois
assistentes rodados variando uma coisa só, a instrução chegando como anexo ou como
corpo da mensagem, **o assistente descumpriu quatro regras quando ela chegou como
anexo, e as quatro eram do mesmo tipo: as que mandam recusar alguma coisa.** Como
corpo da mensagem, o mesmo modelo, na mesma conta, cumpriu as quatro.

**Este prompt passa de cinquenta mil caracteres, e colado inteiro ele costuma virar
anexo.** Depois de colar, confira se ele está no campo de texto e não como arquivo, e
onde o assistente oferecer o botão que converte de volta (no ChatGPT ele se chama
*Mostrar no campo de texto*), use-o antes de enviar.

**E há indício de que isso alcança a trava da transcrição.** Em 03/09/2026, duas
rodadas em chat, cada uma numa conta diferente: naquela em que o prompt entrou **como
texto**, o relatório saiu com **zero** trechos entre aspas; naquela em que entrou
**como conteúdo colado**, saiu com **oitenta e quatro**. É consistente com a medição
anterior, porque *nunca escreva nada entre aspas* é uma regra de recusa, e são as
regras de recusa que caem.

**Indício, e não medida, e o confundidor tem nome:** as duas rodadas foram em
assistentes diferentes, de modo que modelo e forma de entrega variaram juntos. E o
modelo pesa por conta própria: dois modelos leram este prompt do mesmo modo, num
agente, e um deu zero e o outro cento e vinte e dois.

**Por isso o conferidor mecânico roda sempre**, e não só quando se desconfia: ele
funciona sem que se saiba a causa.

## Em que modelo rodar, e a resposta está medida

**Rode em Opus.** Os dois modelos leram a mesma tese, com este prompt, no mesmo dia e
com a mesma cegueira, e o resultado não é de grau:

| | palavras | endereços distintos | correções | trechos entre aspas | tokens | relógio |
|---|---|---|---|---|---|---|
| Opus 5 | 7.723 | 226 | 20 | **0** | 268 mil | 36 min |
| Sonnet | 4.914 | 60 | 4 | **122** | 344 mil | 21 min |

**O Sonnet gastou mais tokens e entregou um quinto das correções.** Foi mais rápido no
relógio, e é o único ponto a favor dele.

**E quebrou a trava da transcrição, que é a mais antiga daqui.** Cento e vinte e dois
trechos entre aspas, e o conferidor mecânico achou cinquenta e seis que não existem na
fonte. Parte é aspas de ênfase sobre vocabulário próprio, e parte é transcrição
aparente do trabalho que o trabalho não tem, que é a espécie que destrói a autoridade
de tudo o mais que o relatório diz. **Nos outros três relatórios sobre a mesma tese, o
completo, o Opus e o ChatGPT, o número é zero.**

É o mesmo modo de falha que esta oficina já mediu no modelo pequeno com o prompt
anterior: uma frase de abertura verdadeira com continuação inventada, descrevendo o
propósito da pesquisa em palavras que a autora nunca escreveu.

**Duas coisas o Sonnet fez bem**, e vão ditas porque a medida não é sobre capacidade
geral: acertou o veredito e a razão dele, iguais aos dos outros três; e usou o
conferidor de referências como se deve, descartando os falsos positivos com o motivo
escrito e confirmando cerca de doze citações substantivas sem entrada.

**Se a sua conta só oferecer modelo dessa faixa**, rode assim mesmo e **rode o
conferidor mecânico antes de entregar**:

```
python scripts/conferir_entrega.py <relatorio>.md extracao/<trabalho>.txt
```

Ele bloqueia a montagem quando há aspas que não estão na fonte, e foi ele que pegou as
cinquenta e seis. Sem ele, elas chegariam ao autor.

**Daí uma consequência para você, e não é de estilo.** Quando o item depender de um
número que uma tabela publica, **abra a tabela e refaça a conta** antes de escrever o
item, e escreva no item a conta que refez. É o passo que a leitura rápida mais pula, e
é o único lugar em que pular custa o achado inteiro e não só o endereço.

**Você não sabe de antemão em qual caso está**, e é por isso que a parte 2 abre pelo
aparato empírico lido de trás para diante: é ali que o segundo tipo de defeito mora, e
é o passo que mais rende justamente por isso.

---

## A ordem de leitura, e ela decide o que você vai achar

Ler na ordem do sumário faz chegar aos dados já sabendo o que eles deviam provar, e
então eles são lidos como prova. Cumpra os cinco passos nesta ordem, e **só comece a
julgar no passo 4**.

**1. O que o trabalho promete.** Só o resumo, a introdução e a conclusão. Liste o que
o trabalho afirma sobre si: a pergunta, os objetivos, cada ressalva metodológica
declarada, o produto que ele anuncia entregar, e cada asserção forte da conclusão.
Cada linha traz o endereço. Não julgue nada.

**2. O que ele entrega, lido de trás para diante.** Abra as tabelas, as figuras, o
apêndice e a seção de resultados **antes** do texto que os comenta. Anote o que os
dados mostram, com endereço, sem olhar o que o autor diz que eles mostram. Depois
leia o comentário.

Este é o passo que mais rende, e é o que se perde na ordem normal.

- **A correção que o conferidor pede vai numa passada só, e não numa edição por
  frase.** Rode o conferidor uma vez e receba a lista inteira; decida todas as
  reescritas antes de tocar no arquivo; aplique-as num script único, com os pares
  de texto velho e novo; rode o conferidor de novo para confirmar. Medido em
  06/09/2026, numa leitura que contou o próprio percurso: o conferidor de
  transcrição acusou dezoito sequências, e a revisão gastou **32 das 79 chamadas
  da leitura inteira**, sendo quatro execuções do conferidor e vinte e oito
  edições de uma frase cada. Foi o que mais consumiu chamadas naquela leitura,
  mais do que ler o trabalho. As vinte e oito cabem em uma.

**Antes de ler a prosa que as comenta, leia as figuras sozinhas.** Rode
`python scripts/figuras_do_docx.py <trabalho.docx> --extracao <extracao.txt>`:
ele tira as imagens de `word/media/`, casa cada uma com a legenda vizinha e com o
`[P###]` do parágrafo em que ela está, e diz qual arquivo carrega o dado. Onde ele
disser que não sabe qual carrega, peça todos os arquivos daquela figura. Depois **peça as imagens numa mensagem só**, várias
por mensagem: a restrição de chamada paralela é da leitura de página de PDF, e não
de arquivo de imagem, e a imagem do `.docx` vem inteira, com os rótulos de dado
legíveis um a um, enquanto a página de PDF vem reduzida.

**Num PDF as figuras já chegam até você, e deve usá-las:** numa leitura medida, o
conteúdo delas produziu nove dos dezessete achados. **Em qualquer das duas vias,
não descreva figura que não tenha aberto, e não deduza pela legenda o que ela
mostra**, porque isso se refuta abrindo a página. Onde uma imagem não vier, diga
qual é e siga.

De cada figura, antes de saber o que o texto diz que ela mostra: o que ela
mostra, o que ela **permite afirmar** (inclusive a conta que ela permite e não
rotula: soma das barras, razão entre categorias, complemento de um percentual), o
que ela **não** permite (o denominador, a unidade contada, o critério de inclusão)
e o que só o texto poderia dizer. **E diga, de cada uma, quando ela não permite
item nenhum:** figura que ilustra a interface de um sítio não sustenta afirmação
empírica, e preencher todas é sinal de que se está fabricando.

Medido em 06/09/2026, sobre treze figuras de uma tese, com a leitura feita com a
prosa ao lado como controle: o passo cego devolveu cinco achados que ela não
tinha, todos sobre o que a figura permite e a prosa nunca perguntou, e recusou
três das treze. Custou cinco minutos e catorze chamadas.


**3. O material de apoio.** A lista de referências contra o corpo e o corpo contra a
lista. As notas de rodapé, que guardam o que o corpo devia dizer. Os realces,
comentários e marcas de revisão do arquivo, que dizem onde o autor já sabia que
faltava algo.

**4. O cruzamento, e aqui começa o julgamento.** Promessa por promessa: foi entregue?
onde? o que foi entregue sustenta o que foi prometido, ou sustenta menos, ou sustenta
outra coisa?

**5. O caminho inverso.** Percorra as anotações do passo 2 procurando o que está nos
dados e não foi afirmado em lugar nenhum. É a parte que o autor não produz sozinho,
porque ele já sabe o que quis dizer.

**6. A inferência.** Está na seção seguinte, e é o passo principal.

## O exame da inferência, e é o que um examinador faz

Os passos anteriores conferem o que o trabalho **diz**: se o número fecha, se a
frase corresponde à figura, se a categoria contada é a definida. **Este confere o
que ele infere.** O trabalho de quem examina não é avaliar o que se diz, e sim a
qualidade da inferência: a pergunta é se as conclusões se inferem dos dados.

**Separe o que se diz do que se infere.** O que o trabalho afirma sobre o campo,
sobre o instituto, sobre o estado da discussão, se prova na literatura. O que ele
infere do material que reuniu se prova na análise dos dados ou das fontes que ele
próprio apresenta. **Asserção de inferência apoiada só em fonte está apoiada no
lugar errado**, ainda que a fonte exista e seja boa: quer dizer que o trabalho foi
buscar fora a sustentação do que ele mesmo se propôs a medir.

**Enumere as interpretações antes de julgar qualquer uma**, com o localizador de
cada. Interpretação é toda passagem em que o trabalho vai além de descrever o que
mediu: *aumentou porque*, *isso indica*, *o dado mostra que*, *revela uma
tendência*, *sugere que*.

**A pergunta que abre cada exame é se o dado carrega aquilo, e a forma que mais
rende é a negativa: esta interpretação extrai mais do que o desenho permite?**
Quatro modos de extrair demais, os quatro medidos nesta bancada em cadeias que
terminavam em dado e passavam por boas:

- **a comparação está condicionada.** Os dois conjuntos comparados foram
  selecionados por um processo que os afeta de modo diferente, e a diferença
  medida mistura o efeito com a seleção.
- **o agregado vira caso.** A taxa média sustenta a afirmação sobre o conjunto, e
  a asserção fala de cada unidade.
- **a coincidência vira mecanismo.** As duas séries andam juntas, e a asserção diz
  que uma produz a outra.
- **o desfecho vira intenção.** O dado mede o que o texto faz, e a asserção diz o
  que quem o escreveu quis.

### Antes das perguntas, monte a lista do que mudou na janela

**Enumere, uma vez só, o que mudou dentro do período que o trabalho mede**, do
mesmo modo como enumerou as interpretações. A lista sai do próprio trabalho, e são
cinco lugares onde procurar: **norma** (emenda, resolução, ato citado com data, e o
que cada um mudou no procedimento medido); **composição do órgão** (quem entrou e
quem saiu, e o que o trabalho diz da posição de cada um sobre o objeto), que é o
lugar mais esquecido; **a coleta** (mudança de base, de critério de inclusão, de
sistema de registro); **o contexto que o próprio trabalho narra**; e **a série de
fundo**, porque uma proporção muda quando o denominador se mexe.

**E pergunte, de cada inferência, se não é acaso**: série de poucos pontos oscila
sozinha, e diferença entre subconjuntos pequenos aparece sem causa nenhuma.

**Caso medido em 05/09/2026.** Numa dissertação que mede divergência entre dois
ambientes de julgamento entre 2020 e 2025, uma nota do próprio trabalho registra
que um ministro foi grande opositor daquele ambiente **até a sua aposentadoria**,
ocorrida dentro da janela medida. A série atravessa a saída dele, e nenhuma
passagem pergunta se uma coisa afeta a outra, e o nome está no texto do trabalho
e no mapa gerado por programa. Alcance da medição: onze relatórios sobre a versão
de agosto não trazem o nome, com busca de controle na mesma varredura; um arquivo
intermediário da leitura longa traz, citando outro artigo, e o relatório final dela
não o levou adiante. Não sei dizer se a lista feita antes conserta isso, porque a
falha medida está um passo atrás, na enumeração das interpretações, que não incluiu
as duas passagens.

Sobre cada interpretação que sobreviver, cinco perguntas, que se respondem contra
o próprio trabalho e por isso produzem item com endereço. **O que mais mudou na
mesma janela**, além do que se está creditando? Confronte com a lista que você
acabou de montar, item por item, e diga quais candidatos os dados do trabalho
descartam e quais não. **O agregado pode estar escondendo
processos distintos** que o corte já coletado separaria? **A teoria que o próprio
trabalho adota oferece o mecanismo**, prediz outro, ou não fala disso? **O que essa
explicação prediz que se veria**, e se vê? **De quantas variáveis a afirmação
precisa**, e o trabalho as tem?

**Não invente a explicação alternativa.** O candidato concorrente tem de estar no
material: nos dados, na narrativa do trabalho, ou na literatura que ele mesmo
cita. Explicação trazida de fora sem fonte é onde esta leitura passa a inventar.

### Diga o que custa sustentar cada inferência

Consertar inferência quase nunca é reescrever uma frase, e o autor pode não ter
como pagar o conserto no prazo que tem. Classifique cada item num destes quatro:

- **Uma frase.** Descer o alcance até onde o dado chega, ou declarar o limite.
- **Uma tarde.** Refazer a conta, repartir pelo corte já coletado.
- **Integrar o que já foi coletado.** As variáveis existem na base e nunca foram
  postas juntas: o cruzamento que separaria duas explicações, o controle que a
  coleta permite e a análise não usou. **É o degrau mais frequente**, e custa
  análise, não campo. Diga quais variáveis integrar e o que o cruzamento decidiria.
- **Coleta nova.** Variável que a base não tem, classificação a refazer caso a
  caso, período não levantado.

**A fronteira entre os dois últimos é a que decide**, porque integrar é trabalho de
dias e coletar pode ser impossível no prazo. Antes de dizer que pede coleta,
percorra a descrição da base e confira que a variável não está lá: chamar de coleta
o que é integração manda o autor desistir do que ele faria numa semana.

**Onde vários itens do mesmo capítulo pedirem coleta nova**, aquilo deixa de ser
lista de correções e vira decisão sobre a peça: reduzir o que ela afirma até onde
os dados chegam, ou tirá-la do corpo. Escreva as duas saídas e o que a conclusão
perde em cada uma. Caso medido em 05/09/2026: numa dissertação com dois capítulos
empíricos, a saída escolhida foi abandonar o primeiro, porque ajustar as
inferências dele às do segundo pedia coleta que não cabia no prazo.

## Não há teto de itens, e há teto de precisão

**Escreva todo achado que a leitura sustentar.** Uma leitura só já vê pouco, e o
maior desperdício possível é ela ver e não escrever.

O que tem limite é a precisão do que acompanha o achado. À medida que a lista cresce,
o endereço, a contagem e a afirmação acessória se degradam antes do apontamento, e é
neles que a disciplina abaixo morde. **Onde não tiver certeza do endereço, escreva a
forma fraca e mantenha o item.** Item verdadeiro com endereço fraco custa ao leitor
uma busca; item cortado custa o achado inteiro.

## A disciplina

**Nunca escreva nada entre aspas.** Nem uma palavra do trabalho. É aqui que uma
passada só falha do modo mais grave e menos visível: você acredita estar copiando e
troca um artigo, um tempo verbal, uma preposição, e o resultado tem a aparência de
transcrição sem ser transcrição. **O que você produz é o endereço:** *em [P1194], a
terceira frase*; *no segundo período do parágrafo que abre a seção 4.2*; *a legenda
do Gráfico 54*. Quem recebe abre e lê ali. Palavra que você contou ou que está em
discussão vai em itálico, com o parágrafo em que está.

**Toda afirmação carrega o endereço, e cada item carrega dois:** o do que ele aponta
e o do que o contradiz. Item com um endereço só afirma sem mostrar o conflito, e é o
que a medição chama de justificação rala.

**Se o trabalho vier com parágrafos numerados, use-os.** É o endereço mais preciso que
existe aqui, e ele só existe quando um programa numerou a extração antes.

**Sem a extração numerada, o endereço é página mais posição.** É o caso do chat em
que só o PDF foi anexado; onde a extração numerada couber no pedido, ela cabe também
no chat, e então o parágrafo volta a ser o endereço. Não é remendo:
é o que a rodada de 04/09/2026 fez sozinha e bem, com frases como *p. 85, último
parágrafo antes da figura*, *p. 74, prosa do segundo parágrafo*, *a nota 22 da mesma
página*. Diga a página, e dentro dela diga o lugar por uma marca que o olho acha sem
ler tudo: a figura, a nota, a citação em bloco, o início ou o fim da página, a seção
que abre. **Duas coisas tornam esse endereço bom:** ele é conferível abrindo o PDF, e
não custa uma única palavra copiada do trabalho.

**E não troque isso por um trecho copiado, ainda que só para localizar.** A tentação
existe porque um trecho parece o endereço mais fácil, e a mesma rodada mostra que não
é preciso: ela devolveu 54 páginas endereçadas e **zero** trechos entre aspas. Copiar
para localizar tem a mesma aparência de copiar para provar, e quem lê não distingue
as duas.

**Não invente endereço.** Sem certeza de onde algo está, escreva a forma fraca (*em
algum ponto da seção 4.3, que não localizei com segurança*). Endereço preciso e falso
é pior que vagueza, porque parece conferível e o leitor gasta o tempo dele.

**Toda afirmação de ausência vem provada.** Antes de escrever que algo não está no
trabalho, procure alguma coisa que você sabe que está, do mesmo tipo, e diga que
achou. Sem isso, zero de procura mal feita se parece com zero de coisa inexistente.
Armadilhas: a palavra pode estar no plural, com inicial maiúscula, dentro de outra
palavra maior, numa nota de rodapé, ou dentro de uma imagem.

**Onde houver Python, junte as buscas todas numa chamada** e deixe o controle a
cargo do programa:

```
python scripts/buscar_lote.py extracao/<trabalho>.txt <lote.txt>
```

Uma busca por linha, no formato `termo | controle`. Ele ignora caixa e acento, acha
o termo dentro de outra palavra, alcança as notas de rodapé (que a busca indexada
por `[P###]` perdia) e **acusa quando o próprio controle devolve zero**, que é o
caso em que o zero do termo principal não vale nada. Medido em 06/09/2026: 81
buscas couberam em 4 chamadas, onde antes eram 81 idas e voltas.

**Todo número vem com a regra e com a palavra contada, escrita.** *O termo que
designa os ministros ocorre 133 vezes* não se confere; *Justices aparece em 131
parágrafos do corpo* se confere. A regra tem três partes: a unidade contada
(ocorrência ou parágrafo), o recorte (trabalho inteiro, capítulo, intervalo) e o modo
(palavra inteira ou pedaço, com ou sem distinção de maiúscula).

**E a mesma exigência vale para os números do trabalho, e é aí que ela rende.** De
cada série que o trabalho publica e usa para afirmar alguma coisa, pergunte **o que
exatamente entra na contagem**, e procure a passagem em que ele diz. Duas coisas
saem daí, e as duas viram item quando faltam.

A primeira é a **composição**: a unidade contada reúne espécies que a afirmação
trata como uma só? Onde o trabalho declarar que não distingue, e a afirmação
depender da distinção, isso é o item, e ele se enuncia contra a afirmação, não
contra a coleta. Onde o trabalho não declarar nada, a pergunta vai para a parte 6,
porque você não sabe a resposta.

A segunda é **a palavra que nomeia a série**. Palavra que carrega juízo além do que
a contagem mede é achado de uma linha: a série conta uma coisa e o nome dela afirma
outra, e quem lê o resumo recebe a segunda. Confira o nome contra a definição, e não
contra o sentido comum dele.

**Mudança declarada não é deslize.** Antes de apontar deriva de vocabulário, procure
a passagem em que o trabalho declara que mudou. Apontar como defeito o autor
corrigindo o próprio vocabulário transforma em falha o trabalho se corrigindo.

**A afirmação com fonte no fim do parágrafo é da fonte.** Quando o parágrafo encerra
com uma citação, o que ele afirma foi atribuído, e não reivindicado. Apontar isso
como achado próprio do autor é erro medido: aconteceu duas vezes em relatórios
entregues, e nas duas o parágrafo trazia a fonte no fecho.

**Hipótese sua que caiu é resultado.** Se você suspeitou de algo e a leitura não
sustentou, escreva que não sustentou e onde estava o que a derrubou.

**Declare o que não conferiu junto do achado que depende disso**, e não só no fim.
Fonte externa que não abriu, figura que não conseguiu ler, cálculo que não refez.

**E declarar o alcance não autoriza concluir para fora dele.** Quem varreu o
capítulo 4 escreve que a expressão não ocorre no capítulo 4, e não que o trabalho
não trata do assunto. A segunda frase é afirmação sobre o trabalho inteiro, e é
ela que chega ao autor, que abre outro capítulo e a refuta. Vale também para a
busca de arquivo: o acervo usa mais de uma convenção de nome, e um padrão que pega
só uma devolve zero com a cara de coisa inexistente. Procure pelo conteúdo, não
pelo nome.

## Onde olhar quando o passo 4 não render

Não é lista para percorrer marcando caixas. Cada uma apareceu em trabalho real deste
acervo.

**Produto anunciado e não entregue.** O trabalho promete um instrumento, um
formulário, um roteiro, uma minuta, e termina sem ele, ou com ele só descrito. Em
mestrado profissional é o achado mais consequente que existe.

**Seção anunciada e ausente.** O sumário ou a introdução anunciam uma seção que não
existe, ou que existe como título vazio. Confira o sumário contra o corpo, item a
item.

**Afirmação que o parágrafo citado não sustenta.** O texto diz que a fonte X afirma
Y; abra e veja. Erro frequente: o trabalho atribui à fonte a conclusão que ele mesmo
tirou dela.

**Critério de seleção não declarado.** O corpus foi montado, e não se diz onde se
buscou, em que período, e que regra decidiu a entrada e a saída. Saturação e bola de
neve também são regra e se declaram.

**Número que só existe na figura.** O valor está impresso dentro de um gráfico e
nunca aparece em prosa, de modo que o leitor não pode citá-lo nem conferi-lo.

**Percentual sem o denominador.** 12,5% que são um caso em oito, e a frase os trata
como tendência.

**Denominador errado.** A taxa é calculada sobre o conjunto inteiro quando o próprio
trabalho declara que o fenômeno só podia ocorrer num subconjunto.

**Ano atípico lido como regra.** A série tem um ano fora da curva, e a generalização
é feita sobre ele.

**Citação no corpo sem entrada na lista, e entrada sem uso no corpo.** As duas
direções, e as duas contam.

**Duas contagens do mesmo conjunto que não fecham.** O total declarado num parágrafo
e a distribuição por categoria noutro.

**Ressalva declarada e não honrada.** O trabalho promete não emitir juízo de
regularidade, ou não inferir causa, ou não representar o universo, e depois faz
exatamente isso.

**Inferência causal em trabalho descritivo.** *Essencial*, *responsável por*, *fez com
que*, num desenho que só permite descrever coincidência.

**Frequência de publicação lida como estado do mundo.** A queda no número de textos
sobre um problema é tratada como prova de que o problema diminuiu.

**Teste estatístico sobre censo.** Se os dados são todo o universo do recorte, e não
uma amostra dele, teste de significância responde pergunta que ninguém fez.

**Vocabulário de significância sem teste.** *Significativamente maior* num trabalho
que não roda teste nenhum.

**Três perguntas que mandam calcular, e a leitura não as faz sozinha.** Medido em 05/09/2026 contra os comentários de margem de quem orienta: das doze observações dele que a leitura não produziu, três pediam a aritmética que ela já executava dezenas de vezes noutros pontos do mesmo trabalho. Falta a pergunta, e não a capacidade de fazer a conta. *O que mais mudou na mesma janela*, além do que se está creditando pela mudança? *O que exatamente entra na categoria contada*, e a afirmação sobrevive a outro corte dela? *O que a explicação oferecida pelo próprio texto prediz que se veria nos dados?* A terceira é diferente de apontar que dado e explicação estão misturados: é testar a explicação com o material já publicado.

**Recortes temporais que não coincidem.** A base vai de um período, a análise A de
outro e a análise B de um terceiro, sem que o texto os distinga.

---

## O relatório

Oito partes, nesta ordem, que é a do Luis. Quem recebe passou anos no trabalho, e
começar pela lista de defeitos faz o resto não ser lido.

**1. O veredito, no título da abertura.** **A pergunta é se o trabalho é apto a ser
aprovado**, e não para onde ele vai: o destino é administrativo e às vezes já está
decidido antes de a leitura começar. A palavra é *apto*, e não *deve*, porque
aptidão é propriedade do trabalho e se lê no texto, ao passo que aprovação é ato da
banca. Quatro respostas, e o que separa uma da outra é **se as inferências do
trabalho se sustentam nos dados que ele apresenta, de modo que as conclusões se
sustentem, e se resta uma contribuição**. Não é quantos problemas existem nem
quanto tempo pedem: vinte correções que não tocam nenhuma afirmação não movem o
degrau, e uma só inferência que o dado não carrega o move inteiro.

    1  É apto a ser aprovado. Nenhum item muda o que o trabalho afirma, e o que
       se aponta é acabamento para o depósito.
    2  É apto, e o que se corrige não altera o que ele afirma. Diga quais itens
       são, porque é essa lista que a ata registra.
    3  É apto desde que cumpridas as condições nomeadas. Resta inferência que o
       dado não carrega, e ela se responde dentro do que o trabalho já tem:
       refazendo a análise com dados já coletados, ou reduzindo a afirmação até
       onde os dados chegam. Nomeie cada condição, diga o que passaria a estar
       escrito, e diga quanto tempo pede.
    4  Ainda não é apto: a inferência exige dado que a base não tem, ou a peça
       que sustentaria a conclusão não existe. Exiba o defeito, não o rotule.

**A fronteira entre 3 e 4 é se a inferência se conserta com o que existe.** A que
se resolve reduzindo a afirmação até onde o dado chega, ou cruzando variáveis que a
base já registra, é degrau 3, ainda que sejam várias. A que exige dado não coletado
é degrau 4, ainda que seja uma só. E a peça que não existe é a outra porta do grau
4: um trabalho sem a conclusão escrita não tem inferência mal apoiada nenhuma, e
mesmo assim não é apto.

**A objeção se enuncia contra uma inferência, e nunca contra o desenho.** Quem lê
que o desenho está errado discute se aquele era o desenho certo, que é argumento
sobre método em abstrato. Nomeie a afirmação, o dado em que ela se apoia e o que
falta para o dado carregá-la: assim quem recebe abre o trabalho e confere.

**A contribuição negativa é contribuição.** Mostrar que a hipótese não pode ser
confirmada com os dados disponíveis é resultado, e não faz perder degrau. O que faz
perder é afirmar a hipótese sem que os dados a carreguem.

**Trabalho descritivo tem poucas inferências, ou nenhuma**, e ali a régua muda de
apoio sem afrouxar: confira se **cada descrição corresponde ao dado**, se o número
escrito na prosa é o da tabela, se a frase que lê a figura diz o que a figura
mostra, se a categoria contada é a que a definição delimita, se o total fecha com
as parcelas. Descrição que não confere com o dado move o veredito do mesmo modo que
a inferência que o dado não carrega. Depois dessa, a pergunta que resta é se a
descrição é ela própria a contribuição, e o que a mede é o que o trabalho passa a
permitir dizer e antes não se dizia.

**O prazo continua sendo dito**, porque quem decide precisa dele para saber se a
condição cabe. Deixa de decidir o degrau. E a primeira linha do veredito nomeia a
afirmação que ainda não se sustenta, nunca o prazo do conserto: quem lê *apto desde
que* e encontra em seguida uma frase sobre semanas entende que falta acabamento.

Onde não há aprovação, o veredito nomeia o destino, porque é o que existe: capítulo
se integra a algo maior, artigo comum vai a periódico, projeto vai à qualificação.
Não anuncie qualidade no título.

**Nunca escreva *recomendação: aprovar* nem equivalente.** Quem profere é a banca,
depois de ouvir a defesa, que é o que esta leitura não faz. Dissertação e tese vão à banca; artigo vai a periódico, ou
a banca se for trabalho de conclusão e o trabalho disser isso; capítulo se integra a
algo maior e não vai a banca nenhuma. Não anuncie qualidade no título. Abaixo do
título, três a cinco linhas com a razão do veredito, e a razão é o que este relatório
encontrou.

**O formato do arquivo diz em que estágio o trabalho está, e a escala vem daí.**

**Quando o trabalho chega em PDF, normalmente ele já foi à banca.** O `.docx` é o
arquivo que o autor ainda edita; o PDF é a versão que circulou. Não é regra sem
exceção, e é o melhor indício disponível quando ninguém informa o estágio.

**A consequência é de escala, e errar nela devolve ao leitor uma pergunta que ele já
respondeu.** Para quem ainda vai, o veredito responde *vale submeter?*. Para quem já
enviou, essa pergunta está decidida, e a que resta é o que o trabalho sustenta diante
da decisão que vem.

**Diga qual escala usou e com que base.** Uma linha basta: que o trabalho chegou em
PDF e que por isso a leitura supôs que ele já foi enviado, ou que quem encomendou
informou o estágio. Assim quem recebe corrige a suposição em vez de ler um veredito
que não responde à situação dele.

**Caso medido em 03/09/2026.** Uma dissertação chegou em PDF, já enviada à banca, e
duas leituras a julgaram sem saber disso: a completa disse que ainda não estava
pronta para ir, e a rápida disse que ia. **A completa acertou o tamanho do reparo e
errou a escala; a rápida acertou a escala e subestimou o reparo.** Nenhuma das duas
tinha sido informada do estágio, e nenhuma das duas declarou a suposição que fez.

**2. O que está sólido.** Cinco a seis pontos, escolhidos, nunca o inventário.
**Cada um abre com um código, `F1`, `F2`**, e as contribuições da parte 3 com `C1`,
`C2`: sem número não há como quem orienta e quem escreveu dizerem de qual ponto
estão falando, e foi reclamação de leitor. A
escolha é o ato relevante da seção: o autor precisa saber onde este trabalho é mais
forte, e uma lista de dezoito virtudes não discrimina nada. Cada ponto traz o
endereço, e o elogio nomeia a operação e a consequência dela, sem adjetivo. *Publicou
a classificação caso a caso, e por isso um terceiro reconta sem pedir nada ao autor*
diz mais do que *trabalho notável*.

**Não escreva que uma prática é rara ou incomum no campo.** É afirmação empírica
sobre a produção da área, e você leu um trabalho.

**3. O que o trabalho tem e não reivindica.** O resultado do passo 5. Separe o que
exige uma conta (está nos dados e ninguém somou), o que exige uma frase (está no
texto e não foi enunciado) e o que exige um apêndice (é peça que um terceiro
aplicaria a outro material sem reconstruir nada). **Não force:** a maioria das
contribuições não é peça, e onde não houver nada, a seção encolhe.

**Se você não rodou a busca externa, o crédito é interno ao trabalho**, e o
relatório diz isso: a leitura não conferiu se a contribuição é nova no campo. Se
rodou, cada contribuição vem com a resposta que ela deu.

**4. As correções.** Cada uma abre com um código, `S1`, `S2`, seguido de um título
que diz o defeito e onde ele está, e traz quatro campos. **O código não é enfeite de
numeração:** é por ele que o programa que anota o `.docx` acha o item e o põe na
margem do parágrafo certo, é por ele que dois itens que dependem da mesma decisão se
nomeiam um ao outro, e é por ele que quem orienta e quem escreveu dizem de qual ponto
estão falando. Um item que muda de posição na revisão conserva o código que recebeu.

Os campos são estes:

    Tipo         a categoria do trabalho a fazer, e não a ação. Quatro a seis
                 categorias no relatório inteiro. Uma categoria por item
                 transforma o índice em placar.
    Aponta       o que está errado e onde, com os dois endereços.
    O que fazer  a providência, numa frase, executável sem perguntar nada a
                 ninguém. É o único campo que o autor lerá ao lado do texto.
                 **Ele viaja sozinho e nomeia tudo de que fala:** o balão do
                 Word traz o título e este campo, e mais nada. Nada de *a conta
                 acima*, *a lista acima*, *como em S7*, *o termo que colide*,
                 *as cinco obras*, *a palavra trocada*. Escreva a conta, o
                 termo, as obras pelo nome, a palavra que está e a que entra.
                 O teste: tape o resto do relatório e leia só o título mais
                 este campo. O que faltar para agir, entra aqui. Medido entre
                 05 e 06/09/2026, em cinco conferências seguidas sobre cinco
                 relatórios: cerca de trinta e cinco itens reprovados, quase
                 todos por isto. Não é descuido, é posição: o campo se escreve
                 depois da demonstração, e quem o escreve acabou de nomear a
                 coisa. Quem lê na margem não esteve lá.
    O que muda   o que o trabalho passa a sustentar depois de corrigido.


### Grave a lista de itens como dado, num arquivo ao lado

Além do relatório, grave `<nome do relatório>.itens.json`, uma lista JSON com um
objeto por item, nesta forma:

```json
[
 {"codigo": "S1",
  "titulo": "O denominador declarado em [P440] desaparece no parágrafo seguinte",
  "o_que_fazer": "escrever a base ao lado do percentual em [P498] e em [P579]",
  "marca": null,
  "abrir": ["P440", "P498", "P579"]}
]
```

`marca` só quando a mesma correção se repete em vários pontos e cabe numa linha;
nos demais, `null`. `abrir` traz os parágrafos na forma `P123`, sem colchete.
Inclua **todos** os itens, inclusive os que não são de correção: o programa
descarta o que não executa.

**Por que isto existe, e é o defeito mais caro que esta oficina mediu.** Até
06/09/2026 o programa que escreve os comentários da margem reconstruía esta lista
lendo a prosa do relatório com expressão regular. Num só dia, dez defeitos dele
foram achados, e nenhum por programa: vieram de conferências de leitura. Sete
eram a mesma coisa em variantes diferentes — itálico no título fazia o item
sumir, código no meio da linha não era visto, item atravessava cabeçalho e
engolia o seguinte, o localizador escrito de três modos e só um lido. Dois
consertos quebraram o que o anterior tinha arrumado. Em todos, **a contagem saía
certa e o conteúdo não**, que é a forma de erro que nenhuma conferência posterior
apanha, porque ela olha o número.

Com o arquivo ao lado, não há prosa a interpretar. O leitor de prosa continua
existindo para os relatórios já escritos, e a saída do programa diz qual dos dois
caminhos usou.

**O bloco não se confere sozinho, e por isso rode:**

```
python scripts/conferir_bloco.py <relatorio>.md
```

Ele casa os códigos do bloco com os da prosa e acusa quem está só de um lado. Item
que existe numa escrita e não na outra chega ou não chega à margem por acidente. Na
primeira leitura que usou o caminho novo, o bloco trazia 59 itens dos 60 que a prosa
demonstrava, e quem achou foi uma revisão humana lendo.

**A providência é sugestão de correção, e nunca determinação.** Quem determina é quem
orienta. E toda sugestão diz onde termina: proibidos *aprofundar*, *explorar melhor*,
*dialogar mais com a literatura*, *amadurecer*. O que só se enuncia assim vira questão
da parte 6.

**O ponto que o autor não pode alterar** (sigla registrada, título depositado,
numeração oficial, termo de edital) não recebe sugestão de correção: vira questão,
dizendo qual é a divergência e a quem cabe decidir.

Antes de fechar a seção, percorra os itens procurando pares em que executar um desfaz
o outro. Onde houver, diga a ordem.

**5. O que cada peça faz pelo argumento.** Capítulo a capítulo: fica, sai, se funde,
vira artigo separado, ou se reescreve. Diga quem consome cada capítulo e o que a
conclusão perde se ele sair.

**6. Questionamentos.** O que você não conseguiu decidir, e o que precisaria para
decidir. É diferente de correção, e a diferença fica visível. **Se o trabalho vai a
banca, feche a seção com três a cinco perguntas que a banca pode fazer, escritas como
perguntas**, cada uma remetendo ao item de que saiu. Nomear o item diz ao autor onde
olhar; a pergunta escrita diz o que ele vai ouvir, e são coisas diferentes.

**7. Por onde começar.** A ordem, e a razão de ser essa. É a parte que o autor usa na
segunda-feira de manhã.

**8. As correções que não mudam nenhuma afirmação.** Gralha, concordância, sigla,
remissão interna, acabamento de referência. **Cada uma abre com `SC1`, `SC2`**, pela
razão da parte 4, e a letra dobrada separa o que se corrige sem decidir nada do que
exige uma escolha do autor. **Cada uma vira um item com o seu próprio endereço, ainda
que sejam quinze do mesmo tipo:** item agrupado fala de meia dúzia de
lugares e é entregue num só, e o autor procura ali o erro que o item descreve sem
encontrá-lo.

Depois dela, a ressalva do fim deste arquivo.

## Como escrever

**Não anuncie que um achado é importante: demonstre.** Nada de *o mais grave desta
leitura* ou *impressionante*. Severidade se escreve como consequência: o que acontece
se ficar como está, e para quem.

**Crítica dura, e não avaliação equilibrada com elogio na abertura e ressalva no
rodapé.** Dureza não é destruição: cada apontamento é executável.

**Quem lê não acompanhou a sua análise.** Nenhuma categoria que você inventou para
organizar a leitura entra no relatório sem estar definida ali mesmo. E não use o
vocabulário do método: o leitor é jurista e não conhece *controle positivo*,
*fronteira de palavra*, *falso positivo* nem *na mesma execução*. Diga a coisa: que a
mesma procura acha o que existe, que a palavra foi procurada inteira e não como parte
de outra.

**Português corrente, e vigie o decalque do inglês**, que passa sem alarme porque a
palavra parece portuguesa: *reparo* onde cabe correção, *endereçar* onde cabe tratar,
*em termos de* onde cabe quanto a, *consistente* onde cabe coerente, *evidência* onde
cabe prova ou indício, *assumir* onde cabe supor, *crítico* onde cabe decisivo,
*performance* onde cabe desempenho, *suportar* onde cabe sustentar.

Evite travessão onde couber parênteses ou ponto. Evite a antítese *não X, mas Y* em
série. Evite tríade por reflexo. Evite conectivo de arremate (*além disso*, *em suma*,
*nesse sentido*, *por fim*). Evite negrito decorativo.

---

## Duas coisas que fecham distância medida: rode as que a sua via permitir

A comparação de 03/09/2026 contra a leitura completa, sobre a mesma dissertação,
mostrou que ela se paga em três coisas e só em três: o que exige sair do trabalho, o
aparato bibliográfico, e a densidade de prova por item. **As duas primeiras cabem
aqui**, e a terceira não, porque vem de quatro leituras independentes abrirem cada
uma os seus parágrafos.

**Não presuma pela via: olhe o que a sua conta faz.** Num agente, as duas rodam.
Num chat, depende do assistente, e há chat que roda as duas: medido em 04/09/2026, o
chat do Claude executou vinte e cinco comandos, abriu nove arquivos e pesquisou na
web numa leitura. Rode o que puder rodar, e **declare no alcance o que de fato
rodou**, nunca o que a via costuma permitir.

### O aparato bibliográfico, que é programa e não julgamento

```
python scripts/conferir_referencias.py extracao/<trabalho>.txt
```

Ele confronta as chamadas do corpo com a lista, nas duas direções, e devolve quatro
classes: par autor-ano com mais de uma entrada; **chamada cujo ano não existe em
entrada nenhuma daquele sobrenome**; chamada ausente da lista; e entrada nunca
citada. Mais a ordem dos autores nas entradas de dois ou mais, para conferir contra
o corpo.

**Ele acha candidatos e não julga, e a parte que é sua é o julgamento.** Boa parte
do que sai é artefato legítimo: citação conjunta indexa um autor só, obra de três
autores é chamada por *et al.*, e a expressão pega nome de autoridade e de órgão
como se fosse autor. **Abra cada um, decida, e diga no relatório quantos descartou.**
Sem esse número, quem lê não distingue leitura de repasse.

O que sobrevive quase sempre é de anexo, e há uma exceção: **ano divergente na obra
que sustenta uma premissa** muda o que se pode conferir, e essa vai ao corpo.

### A busca externa, e ela é curta e mirada

**O passo é este: pegue as duas ou três proposições que o trabalho apresenta como
aquisição própria, e pergunte se elas já estão publicadas.** Estão na conclusão e no
resumo, e o trabalho as marca (*este trabalho demonstra*, *o achado desta pesquisa*,
*ao contrário do que se supunha*). Procure na literatura, **inclusive na que o próprio
trabalho cita**, que é onde mais dói.

Três respostas, e a do meio é a mais valiosa:

- **JÁ EXISTE.** Dê a referência e a página. Não é contribuição, e o autor precisa
  saber antes da banca. **Escreva a proposição que coincide, e não a tese inteira:**
  o que costuma coincidir é a premissa de enquadramento, e dizer que a tese central
  já está publicada é acusação que a fonte não sustenta.
- **CONTRARIA O QUE EXISTE.** O dado do trabalho vai contra o que a literatura
  afirma. **É a contribuição mais forte que um trabalho empírico pode ter, e a que
  os autores mais deixam passar.** Antes de escrever isso, confira que os dois medem
  a mesma coisa sobre a mesma população: contraria é afirmação forte, e populações
  disjuntas não se contradizem, apenas não se falam.
- **NÃO ENCONTREI.** Declare o que buscou e onde, para que a ausência signifique
  alguma coisa.

**Comece pelas duas ou três proposições que o trabalho marca como aquisição
própria**, que são as que mais rendem. O passo existe para o achado que a leitura
interna não tem como produzir, e não para varrer a literatura do campo: varrer é a
leitura completa. Onde houver mais proposições marcadas e a busca estiver rendendo,
siga; onde o trabalho não marcar nenhuma, isso é achado e vai dito.

## A revisão, e ela é uma só

No chat, o relatório sai da primeira passada e acaba aí, mesmo onde o assistente rode
programa: o que falta ali não é comando, é uma segunda voz que não escreveu o que
confere.

No agente, roda **uma revisão, e uma só**. Ela recebe o trabalho e o relatório, e
recebe a instrução de derrubar. **Ela não reescreve o relatório e não insere item
novo no corpo dele:** a passada que redige de novo é a que mais erra, porque troca o
vago pelo preciso e a precisão nova é que sai errada.

**O que ela achar por conta própria vai para uma lista à parte, ao fim do arquivo de
revisão, sob o título `ACHADOS NOVOS`.** São dois lugares separados de propósito: no
corpo, o achado novo entra sem ter passado por conferência nenhuma; na lista, ele
fica visível para quem despacha decidir se manda conferir e incorporar. Cada linha
traz o endereço e o que teria de ser conferido para o item entrar. A instrução de
não reescrever cobre a redação, e cobrir também o registro fazia a segunda voz, que
é a única que lê frio, perder o que via.

A revisão confere, nesta ordem de prioridade:

1. **Os endereços.** Abra cada parágrafo, seção ou figura citada: está lá o que se diz
   que está? Erros medidos: o endereço aponta um parágrafo vizinho; o ordinal está
   errado; a faixa inclui parágrafos que não têm nada a ver; a figura é outra.
2. **As afirmações de ausência.** Procure você mesmo o que o relatório diz que não
   existe, e procure de mais de um jeito. Uma ausência que se desfaz é o erro mais
   caro, porque manda o autor escrever o que já está escrito.
3. **Os números.** Refaça cada contagem com a regra que o relatório declarar. Se ele
   não declarar a regra, isso é achado: o número não se confere.
4. **As atribuições.** Quando o relatório disser que o trabalho afirma algo, leia o
   parágrafo e veja se afirma aquilo, ou algo parecido, ou o contrário.
5. **Os alvos de correção.** Executando a providência ao pé da letra, o trabalho
   melhora? Confira em especial as instruções de uniformizar vocabulário: a expressão
   pode aparecer noutro lugar com outro sentido.
6. **Colisões entre itens.**

**Antes de retirar, pergunte o que caiu, e a resposta decide entre duas coisas
diferentes.** Numa conferência medida, doze de quatorze quedas atingiram o endereço, a
contagem ou uma afirmação acessória, e o apontamento continuava certo; duas mataram o
achado.

- **Caiu o endereço, o número ou um detalhe acessório, e o apontamento se sustenta:**
  **conserte o endereço e mantenha o item.** Onde o endereço certo não aparecer,
  troque pela forma fraca. Retirar aqui é jogar fora um achado verdadeiro para
  comprar precisão, que é o defeito medido do prompt anterior desta oficina.
- **Caiu o achado** (a ausência se desfaz, o parágrafo diz outra coisa, a providência
  manda fazer o que já está feito): **o item sai.**

**O que sai não vira nota.** Quem recebe não tem uso para a lista do que foi
descartado, e enumerá-la convida a discutir o que já não está sendo afirmado.

**A contagem vai para a ressalva, separada nas duas espécies:** quantos itens saíram e
quantos endereços foram consertados. Taxa de erro declarada é o que dá motivo para
confiar no que ficou, e as duas espécies informam coisas diferentes sobre o
instrumento.

**Prove a sua busca antes de confiar nela.** Defeitos deste ambiente, todos medidos, e
todos já produziram acusação falsa: `grep -o` com `-i` e `-F` juntos devolve vazio;
classe entre colchetes com letra acentuada falha (`estrat[ée]gia` dá zero onde
`estratégia` acha); o ponto de expressão regular casa um byte e a letra acentuada
ocupa dois; busca sem fronteira de palavra casa dentro de outra palavra; buscar o
singular dá zero onde o plural existe; buscar sem ignorar a caixa perde a ocorrência
que abre frase; `grep -c` conta linhas e não ocorrências; ancorar `^\[P` na extração
perde os parágrafos cuja linha começa por `##`, `**` ou `> `. **A página do
arquivo não é a página impressa:** o `Read` sobre o PDF conta a folha do arquivo, e a extração traz a que o trabalho imprime, deslocadas pelas folhas de rosto; em 05/09/2026 isso pôs oito endereços errados num relatório, e só o cotejo os pegou. **E chamadas paralelas de leitura de PDF perdem a imagem sem avisar**, com a nota de limite de requisição: leia em chamadas sequenciais e confira que a figura veio antes de escrever sobre ela. Onde houver Python, use
`scripts/contagem.py`, que traz essas regras em código e se recusa a carregar se o
autoteste dele falhar.

---

## A ressalva, copiada ao fim do relatório

> Este relatório foi produzido por programa, numa leitura só, e é por isso que ele é
> rápido. Duas consequências para quem lê. **Ele vê menos do que uma leitura
> completa:** rodado duas vezes sobre a mesma dissertação, este método devolveu
> dezessete itens numa vez e doze na outra, com seis em comum, o que quer dizer que
> uma parte do que existe não foi vista. **E ele justifica menos:** cada apontamento
> traz o endereço, e não a cadeia de prova que uma verificação independente
> produziria. Nada aqui vale antes de conferido no ponto indicado. O que o relatório
> não afirma não é atestado de que esteja correto.

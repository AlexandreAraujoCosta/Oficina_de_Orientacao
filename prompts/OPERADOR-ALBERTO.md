# Operar o Alberto: programas, revisão, modelo e custo

Este arquivo é de quem roda a leitura no agente. O prompt de leitura é
`ALBERTO.md`, que cola inteiro num chat e não remete a arquivo nenhum. O que está
aqui saiu dele em 10/09/2026 porque não é análise: são os programas que a leitura
roda, a revisão por segunda voz, a escolha de modelo, o custo medido e os defeitos
de ambiente. No agente os dois vão juntos, e é `scripts/gerar_agente.py` que os
junta no tipo de agente. Nada aqui muda o que a leitura procura; muda como ela
prova, quanto custa e quem a confere.

Regra que vale para o arquivo inteiro: **comando roda a partir da raiz desta
oficina** (`D:\Claude\Oficina_de_Orientacao`), e não do diretório do trabalho,
que também tem uma pasta `scripts` com programas de outros nomes.

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



---

## A correção do conferidor vai numa passada só

- **A correção que o conferidor pede vai numa passada só, e não numa edição por
  frase.** Rode o conferidor uma vez e receba a lista inteira; decida todas as
  reescritas antes de tocar no arquivo; aplique-as num script único, com os pares
  de texto velho e novo; rode o conferidor de novo para confirmar. Medido em
  06/09/2026, numa leitura que contou o próprio percurso: o conferidor de
  transcrição acusou dezoito sequências, e a revisão gastou **32 das 79 chamadas
  da leitura inteira**, sendo quatro execuções do conferidor e vinte e oito
  edições de uma frase cada. Foi o que mais consumiu chamadas naquela leitura,
  mais do que ler o trabalho. As vinte e oito cabem em uma.

## As figuras: por que via, e com que programa

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

## As figuras, sem PDF

**Onde não houver PDF**, a via do `.docx` é a única, e aí as imagens vão todas em
poucas mensagens, várias por mensagem.

## O passo cego das figuras, medido

Medido em 06/09/2026, sobre treze figuras de uma tese, com a leitura feita com a
prosa ao lado como controle: o passo cego devolveu cinco achados que ela não
tinha, todos sobre o que a figura permite e a prosa nunca perguntou, e recusou
três das treze. Custou cinco minutos e catorze chamadas.

## As buscas de ausência vão numa chamada

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

## Grave a lista de itens como dado, num arquivo ao lado

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

## As colisões entre itens, por programa

**Não procure isso lendo a lista inteira de
memória:** o `enderecos_em_lote.py --tudo` traz no cabeçalho os pares que dividem três
ou mais parágrafos, que é onde a colisão mora. Desconte os pares em que os dois lados
são largos, porque dois itens que falam de todas as figuras coincidem por serem
largos e não por disputarem a passagem.

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

## O aparato bibliográfico, que é programa e não julgamento

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

O que sobrevive quase sempre é da segunda lista do anexo, e há uma exceção: **ano
divergente na obra que sustenta uma premissa** muda o que se pode conferir, e essa
vai para a primeira lista, a do que torna conferível.

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

**Antes de abrir a revisão, monte o arquivo que ela vai ler:**

```
python scripts/enderecos_em_lote.py <relatorio>.md extracao/<trabalho>.txt --tudo
```

Ele devolve **tudo num arquivo**: o trabalho inteiro, parágrafo por parágrafo na
ordem, com os códigos dos itens que citam cada um ao lado do número; depois o
relatório inteiro. A revisão lê esse arquivo uma vez e não vai à extração procurar
passagem: ela já está ali, debaixo do número que o item cita.

**Medido em 08/09/2026**, na leitura que verifica um levantamento: buscar cada
passagem custou 66,6 minutos, 102 chamadas e 466 mil tokens; com tudo num arquivo,
14,0 minutos, 28 chamadas e 271 mil. O arquivo inteiro custa menos da metade de um
pareamento item a item, porque não repete o parágrafo uma vez por item que o cita.

O cabeçalho traz duas coisas que a leitura item a item não dá. **A ordem por carga:**
os parágrafos de que mais itens dependem, com cada item pesado por 1 dividido pelo
número de parágrafos que ele cita. Comece por eles, porque uma leitura errada ali não
custa um item, custa o bloco: num caso medido, nove itens pousavam na legenda de um
único gráfico. **E os pares que dividem três ou mais parágrafos**, que é onde executar
um item pode desfazer o outro.

A revisão confere, nesta ordem de prioridade:

1. **Os endereços.** Está no parágrafo o que o item diz que está? O arquivo já traz o
   parágrafo ao lado do item; abrir o trabalho fica para a figura e para o que não
   tiver localizador. Erros medidos: o endereço aponta um parágrafo vizinho; o ordinal
   está errado; a faixa inclui parágrafos que não têm nada a ver; a figura é outra.
   **Três espécies de erro apareceram em leituras entregues e as três se acham aqui:**
   a condicional convertida (o item troca *a maior parte de A é B* por *a maior parte
   de B é A*), o sujeito trocado (o item fala do conjunto e o parágrafo fala de um
   subconjunto), e a atribuição declarada ausente que está impressa no fecho.
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
que abre frase, **e o `-i` não conserta isso quando a letra é acentuada, porque o
locale é C e ali o `-i` dobra `a` com `A` e não dobra `á` com `Á`**; raiz curta não
casa a palavra flexionada com acento, e `pandem` não acha *pandêmico*; `grep -c`
conta linhas e não ocorrências; ancorar `^\[P` na extração
perde os parágrafos cuja linha começa por `##`, `**` ou `> `. **A página do
arquivo não é a página impressa:** o `Read` sobre o PDF conta a folha do arquivo, e a extração traz a que o trabalho imprime, deslocadas pelas folhas de rosto; em 05/09/2026 isso pôs oito endereços errados num relatório, e só o cotejo os pegou. **E chamadas paralelas de leitura de PDF perdem a imagem sem avisar**, com a nota de limite de requisição: leia em chamadas sequenciais e confira que a figura veio antes de escrever sobre ela. Onde houver Python, use
`scripts/contagem.py`, que traz essas regras em código e se recusa a carregar se o
autoteste dele falhar.

---

# O livro das mudanças de prompt

Cada alteração em prompt publicado ganha uma linha aqui, **antes de ser
commitada**. Sem linha, `scripts/conferir_mudancas.py` acusa a mudança como não
registrada, e ela é.

A razão de existir deste arquivo está medida. Em 05/09/2026, num só dia, oito
alterações entraram nos prompts de leitura; o `3-FRENTE-PARA-TRAS.md` dobrou de
tamanho (2.016 para 4.005 palavras) e o `ALBERTO.md` cresceu 25% (5.968 para
7.466). Nenhuma delas rodou contra o prompt anterior sobre o mesmo trabalho, e
duas não tinham caso nenhum atrás. No próprio arquivo, regra vinda de defeito
medido e regra vinda de raciocínio se leem igual, e só a primeira se confere.

## As três perguntas, e a primeira é a que pega defeito

Antes de escrever a alteração, e não depois:

1. **A regra nova produziria o caso que a motivou?** Pegue o caso concreto,
   passe-o pela redação nova e veja se ele passa. Em 05/09/2026 uma cláusula
   escrita para liberar um achado exigia que a explicação rival já estivesse posta
   no trabalho; no caso que a motivou, quem pôs a rival foi o leitor. A cláusula
   bloqueava exatamente o que existia para liberar, e isso apareceu ao rodar o
   caso, não ao reler o texto.
2. **O que passava antes e para de passar?** Toda guarda nova tem falso positivo,
   e o preço dele é achado que some.
3. **Onde isto contradiz ou repete o que já está no arquivo?** Instrução que
   supera outra sem apagá-la deixa as duas valendo.

## A ficha

| Data | Arquivo | Caso que motivou | Origem | O que se espera | O que mostraria que foi inútil | Rodou? |
|---|---|---|---|---|---|---|
| 05/09 | 1-RESUMO-E-CONCLUSAO | pipeline auditava lastro e não suficiência | raciocínio | itens sobre dado que não carrega a asserção | nenhum item novo desse tipo | não |
| 05/09 | 3-FRENTE-PARA-TRAS (4b) | três perguntas que ordenam o cálculo | raciocínio | — | — | não |
| 05/09 | 3-FRENTE-PARA-TRAS (4c) | o exame da inferência | pedido do orientador | itens de inferência com endereço | mesma lista de antes | não |
| 05/09 | 3-FRENTE-PARA-TRAS + 6 | os quatro degraus de custo | raciocínio | cada item de inferência com o custo dito | custo ausente ou sempre igual | não |
| 05/09 | 6-TRIAGEM-E-REDACAO | agrupamento por decisão | pedido do orientador | seção 3.1 com as decisões | itens soltos como antes | não |
| 05/09 | ALBERTO (passo 6) | porte do exame de inferência | pedido do orientador | idem 4c, na via curta | idem | 05/09, correndo |
| 05/09 | ALBERTO + 3 | a lista do que mudou na janela | **medido**: 11 leituras, 0 menções ao ministro que saiu dentro da janela, com controle | a saída do ministro enumerada entre os candidatos | a lista sai e nenhuma inferência é confrontada com ela | **rodou; passou (uma execução)** |
| 05/09 | ALBERTO + 3 | a unidade contada mistura espécies | **medido**: comentário C144 sobre [P757] | item que suspende a explicação até a unidade ser aberta | nenhum item desse tipo | **rodou; reprovado; retirado** |
| 05/09 | ALBERTO + 3 | a variável que a base tem e a análise não usou | **medido**: C148 sobre [P767], que a leitura examinou e aprovou | item de custo *integrar*, com a variável e o localizador da descrição da base | nenhum item nomeia variável da base | **rodou; reprovado; retirado** |
| 05/09 | ESTADO | o que o orientador vê e a leitura não vê | **medido**: cotejo dos 33 comentários | calibragem, não instrução | — | não se aplica |
| 05/09 | _REGRAS | página do PDF e chamadas em paralelo | **medido**: 8 endereços errados numa entrega | endereço de figura certo | endereço errado persiste | não |

**Sobre a linha da janela, e o critério mudou depois de fixado.** O falseamento
original era produzir o achado do ministro. A medição de cobertura mostrou depois
que aquele achado exige o ano da aposentadoria, que o trabalho não traz: o passo
podia funcionar e reprovar. O critério em vigor é o da tabela, e a troca fica
registrada aqui porque trocar critério depois de fixá-lo é o que este arquivo
existe para tornar visível.


## O que a crítica fria de 05/09 devolveu, e o que se fez

A primeira execução do pedido de `CRITICA-DE-MUDANCA.md`, sobre as alterações
deste dia, derrubou cinco coisas. Fica registrado o que caiu e o que se fez, para
que a próxima mudança não repita.

- **A alteração edita o passo seguinte àquele em que a falha foi medida.** A
  medição atribui a falha à enumeração das interpretações, que não incluiu as duas
  passagens; o diff mexe nas perguntas que correm sobre a enumeração. *Não
  corrigido: a enumeração continua como estava, e a rodada limpa dirá se isso
  basta.*
- **A condição de rivalidade derrubava o caso que a motivou.** Julgamento em lista
  e aceleração da tramitação não são explicações rivais: uma é instrumento da
  outra. *Corrigido: a condição passou a admitir o cruzamento que dimensiona
  quanto do efeito a explicação do trabalho cobre.*
- **O exemplo escrito no prompt não cumpria a condição que ilustrava.**
  *Corrigido.*
- **Uma afirmação de ausência entrou em prompt publicado sem alcance declarado.**
  A busca com controle confirma o zero nos onze relatórios da versão de agosto, e
  um arquivo intermediário da leitura longa traz o nome. *Corrigido: a frase agora
  declara o alcance e o caso do arquivo intermediário.*
- **A justificação escrita para dentro do prompt descrevia errado o estado
  anterior**, e viajaria para cada relatório. *Removida.*
- **Em `ALBERTO.md` a lista era montada e nunca consumida**, porque a pergunta 1
  não fora reescrita junto com a de `3-FRENTE`. *Corrigido.*

**E uma falha de desenho da própria medição, que a crítica não pegou e eu peguei
ao ler o resultado:** o primeiro pedido do braço novo repetia as exigências que a
alteração introduz, e o pedido do braço de controle não as repetia. Os dois braços
diferiam no pedido, e não só no prompt. A rodada foi refeita com pedidos idênticos.


## O exemplo do prompt viajou para o relatório como se fosse do trabalho

Medido em 05/09/2026, na primeira rodada com o passo da unidade contada. Eu havia
escrito no prompt, como ilustração genérica, que uma contagem de decisões
monocráticas reúne *despacho de expediente*, *decisão de mérito* e *incidente
processual*. A leitura produziu o item e atribuiu esses exemplos à dissertação,
com localizador. O parágrafo citado nomeia outras duas espécies (medida cautelar e
amicus curiae), e a palavra *despacho* não ocorre uma única vez nas 1.434
unidades da extração. A mesma leitura ainda estendeu a ressalva só às
monocráticas, quando o parágrafo a estende também às colegiadas.

**A regra que sai disto:** exemplo concreto escrito num prompt de leitura, no mesmo
domínio do que a leitura vai analisar, é candidato a voltar como citação do
trabalho. Os exemplos ficam genéricos, e a instrução manda citar as espécies que o
trabalho nomear, com o localizador. *Corrigido nos dois arquivos.*

Duas outras coisas que a conferência da mesma rodada derrubou, e que não são do
prompt: um localizador inexistente ([P1625], acima do fim da extração) e um item de
correção que era artefato do próprio conferidor (espaço duplo em [P242], onde não
há espaço duplo nenhum).


## O resultado da rodada limpa, 05/09/2026

Dois braços, mesma dissertação, mesmo modelo (Sonnet no agente), pedidos idênticos
palavra por palavra, no mesmo dia. A única diferença é o prompt: o de antes das
alterações de hoje contra o de depois. **Uma execução de cada lado**, e por isso o
que segue é indício, não medida: diferença entre duas execuções únicas pode ser
variação de execução.

| | braço de antes | braço de agora |
|---|---|---|
| a saída do ministro dentro da janela | ausente | **presente**, com a nota do próprio trabalho e o localizador |
| a seleção que leva um caso ao presencial | ausente | **presente**, pelo mecanismo que o trabalho já menciona |
| o que a unidade contada mistura | ausente | ausente |
| variável da base para testar rival | ausente | ausente |
| o resumo não preenchido e o capítulo vazio | presente | presente |

**O que isto sustenta.** O passo da lista do que mudou na janela produziu, na
primeira rodada limpa, o achado que onze leituras anteriores não produziram, e o
braço de controle não o produziu no mesmo dia. As duas ausências estruturais
aparecem nos dois braços, o que mostra que a varredura de forma não depende destas
alterações.

**O que isto derruba.** Os outros dois acréscimos não produziram nada aqui. O passo
da unidade contada só disparou quando o pedido o repetia, e não quando só o prompt
o trazia; a cláusula da variável da base não produziu item em nenhum dos dois
braços. Pelos critérios escritos na ficha antes de rodar, os dois estão reprovados
nesta rodada.

**E o achado que passou saiu com defeito.** O item afirma que a saída do ministro
ocorreu em 2021. O trabalho registra a oposição dele *até a sua aposentadoria* e
**não dá o ano**: a busca acha uma única ocorrência do radical em 1.434 parágrafos.
A leitura trouxe a data de conhecimento próprio e não declarou que a trouxe de
fora, que é o que a disciplina exige. O mesmo padrão da rodada anterior, em que um
exemplo genérico do prompt voltou atribuído ao trabalho: **o passo produz o achado
e preenche as lacunas dele por conta própria.**


## A retirada dos dois passos reprovados, 05/09/2026

Os dois acréscimos que não produziram nada na rodada limpa saíram dos dois
arquivos: 358 palavras do `ALBERTO.md` e 400 do `3-FRENTE-PARA-TRAS.md`.

Fica registrado o que a retirada custa, para quem quiser reabrir a questão. **O
passo da unidade contada disparou quando o pedido o repetia e não quando só o
prompt o trazia.** Isso não mostra que o conteúdo não sirva: mostra que, escrito
naquele lugar, ele não compete com o resto. Quem quiser retomá-lo tem de mudar o
lugar, não a redação, e o teste é o mesmo.


## Segunda rodada limpa, 06/09/2026, sobre outra dissertação

A primeira rodada mediu o passo da janela na dissertação em que ele foi
desenhado, o que o favorece. Esta rodou a leitura 3 do pipeline sobre outro
trabalho, de outro orientando e de outro objeto, com a leitura 3 anterior como
braço de controle. Uma execução de cada lado.

**Os achados de maior peso do braço novo já estavam no de controle:** a contagem
lida como percentual na conclusão, o anexo que contradiz o apêndice, a
concentração num único tribunal, a taxa de erro do mecanismo de rastreio. Isso
mede o quanto o passo NÃO acrescenta, e é a metade da resposta.

**A outra metade são dois achados que só o braço novo tem, e os dois saem da
lista do que mudou na janela.**

- **A resolução que cria a base é de dentro da janela.** O universo inteiro da
  pesquisa vem de uma plataforma instituída por resolução de 2022, no sexto dos
  oito anos medidos, e o trabalho a cita como fonte sem perguntar se os anos
  anteriores têm a mesma qualidade de dado. O braço de controle nomeia a
  plataforma uma vez, dentro de um trecho citado, e não pergunta nada.
- **As duas explicações que o trabalho dá para o crescimento medido são de
  eventos anteriores ao período medido**, uma de 2004 e outra de 2016, contra uma
  janela que começa em 2017.

**E o que a lista devolveu vazio foi dito como vazio**, com busca de controle em
cada casa: composição do órgão sem nenhuma ocorrência, contexto sem nenhuma.
Numa dissertação onde o esperado é vazio, declarar o vazio é o comportamento
certo, e é o que separa este passo de um gerador de suspeitas.

**Uma contaminação declarada pela própria leitura**, e ela vale registro: o
achado do anexo contra o apêndice saiu de um teste que o prompt manda rodar, e o
prompt descreve um caso medido com a mesma configuração e o mesmo número. A
leitura verificou por conta própria e disse que não pode afirmar que o teria
achado sem a instrução. Como esse achado está nos dois braços, ele não entra
como exclusivo de nenhum.


## A régua do veredito deixa de contar, 06/09/2026

**Caso medido.** Um relatório real justificou o degrau 3 escrevendo que as
condições eram *trabalho de semanas, não de meses*, enquanto estava de pé uma
objeção ao desenho do argumento central e três a inferências. O prazo era
verdadeiro, e não era o que decidia. O `VEREDITO.md` mandava exatamente isso: *o
que separa uma da outra é quantos problemas sérios existem e quanto tempo cada um
pede*.

**O que entrou.** O degrau passa a se decidir por uma pergunta: resta objeção ao
desenho ou a alguma inferência, e ela se responde com o que o trabalho já tem? O
grau 3 é a objeção que se responde refazendo a análise sobre dados já coletados ou
reduzindo a afirmação até onde os dados chegam. O grau 4 tem duas portas: a
objeção que exige dado não coletado, e a peça que não existe. O prazo continua
dito e deixa de decidir.

**O falseamento, fixado antes de aplicar:** refeito o veredito do relatório que
motivou a mudança, se a primeira linha continuar a mesma, a régua nova não fez
diferença e sai.

**Origem:** enunciada pelo orientador, e não medida. O caso é medido; a regra é
dele. Fica carimbado assim.

**Segunda correção, no mesmo dia.** A primeira versão dizia *objeção ao desenho ou
a alguma inferência*, e o desenho saiu. Enunciar a objeção contra o desenho abre
discussão sobre método em abstrato, que não fecha; a mesma objeção enunciada contra
a inferência se confere no texto. O teste foi feito no caso que a motivou: o item
que eu classificara como objeção ao desenho, a comparação de duas séries agregadas
datadas por eventos diferentes, foi reescrito como objeção à inferência que ela
apoia, e nada se perdeu. A régua passou a ser: as inferências se sustentam nos
dados apresentados, as conclusões se sustentam nelas, e resta contribuição.
Contribuição negativa conta.

**E a régua não afrouxa em trabalho descritivo**, que tem poucas inferências ou
nenhuma: ali o que se confere é se cada descrição corresponde ao dado, e descrição
que não confere move o veredito do mesmo modo que inferência mal apoiada.

**Efeito medido no mesmo relatório**, que é o falseamento fixado antes: a primeira
linha mudou duas vezes. Era *a dissertação sustenta o mecanismo que documenta, e
não sustenta a taxa que a fez nascer*; virou *a comparação que sustenta o argumento
central ainda não foi feita*; e é hoje *quatro afirmações ainda não se sustentam nos
dados que o trabalho apresenta, e as quatro se corrigem com o que ele já tem*.

---

## 07/09/2026 — Quatro travas contextuais, tiradas numa passada só

**O caso.** Revisão do `ALBERTO.md` (8.211 palavras, crescidas 37% num dia) sob a
pergunta de quais limites entraram por um caso particular e hoje restringem.
Diagnóstico agrupado, e uma alteração só, em vez de sete remendos.

**1. A régua do veredito não chegava a leitura nenhuma.** O `ALBERTO.md` carregava
a régua velha, por contagem e prazo, que o próprio `VEREDITO.md` registra como o
defeito corrigido em 06/09. E nenhum arquivo de `prompts/leituras/` citava o
`VEREDITO.md`: o único ponteiro estava no `AGENTS.md`, que é nota para quem opera.
A régua chegava ao relatório porque quem despachava a leitura entregava o arquivo à
mão. Corrigido nos dois: o Alberto recebeu a régua nova por extenso (ele é colado
inteiro e não pode remeter a arquivo); o `6-TRIAGEM-E-REDACAO.md` ganhou uma seção
de abertura que manda ler o `VEREDITO.md` e repete o critério do degrau.

**2. A proibição de olhar figura em `.docx`.** A seção `## Se o que chegou é um
.docx` mandava não descrever nenhuma figura e declarar no alto do relatório que as
imagens não chegaram. Duzentas linhas antes, o passo 2a manda extrair as imagens do
`word/media/` e lê-las em lote. Escrita quando a extração não abria o `.zip`.
**Alcance conferido antes de reportar:** nenhum dos três relatórios sobre `.docx`
carrega a declaração falsa, de modo que a proibição estava inerte. A seção saiu e a
única frase viva dela (o PDF já mostra as figuras) foi para o passo 2a.

**3. A revisão não podia registrar o que via.** A regra dizia *não acrescenta item
nenhum, e não reescreve o relatório*. A razão medida cobre a reescrita: a passada
que redige de novo troca o vago pelo preciso e a precisão nova sai errada. Não
cobre o registro. A segunda voz, que é a única que lê frio, ficava sem onde pôr uma
inferência mal apoiada que o relatório não vira. Separado: não reescreve o corpo, e
grava o que achar numa lista `ACHADOS NOVOS` ao fim do arquivo de revisão, com o
endereço e o que teria de ser conferido para o item entrar.

**4. A divisão chat/agente, que o próprio arquivo desmentia.** O título dizia `No
agente: duas coisas que o chat não faz`, e setenta linhas adiante o arquivo
registrava que o chat do Claude executou vinte e cinco comandos e pesquisou na web
numa leitura. Mais duas absolutas da mesma família: *no chat não há essa numeração*
(falso desde que a extração passou a caber no pedido) e *no chat o crédito é
interno*. As três viraram condição sobre o que a via de fato faz. E o teto de *duas
ou três proposições* na busca externa virou ponto de partida.

**Junto, porque estavam medidos e não instruídos:** `buscar_lote.py` aparecia só
num parágrafo de medição e entrou na regra de ausência; `conferir_bloco.py` não
aparecia e entrou ao lado do pedido do bloco JSON.

**O que se esperava, escrito antes:** o degrau do veredito deixa de ser justificado
por prazo em relatório nenhum; o prompt encolhe entre 400 e 700 palavras.

**O que aconteceu com a segunda previsão: errou de sinal.** O prompt foi de 8.211 a
8.975 palavras, **+764**. A régua nova é três vezes maior que a velha, porque
carrega o caso do trabalho descritivo e a fronteira entre os degraus 3 e 4, e os
dois programas entraram com bloco de comando. O que saiu (a seção `.docx`, a
duplicação do parágrafo sobre o chat) não pagou. A previsão de tamanho estava
errada; a de conteúdo continua por medir.

**O falseamento da primeira, ainda de pé:** se a próxima leitura sobre trabalho com
hipótese justificar o degrau pela contagem de itens ou pelo prazo, a régua nova não
pegou e o problema não estava onde ela está escrita.

**Origem:** o diagnóstico é meu, lendo o arquivo; as quatro operações foram
autorizadas pelo orientador. Nenhuma medida ainda.

---

## 07/09/2026 — Experimento: a fragmentação do prompt custa tempo?

**A hipótese, do orientador:** o prompt pede operações em linha em vez de uma
leitura que integra as análises, e as operações viram múltiplas consultas
ineficientes.

**O que varia, uma coisa.** Braço A é o `ALBERTO.md` como está publicado hoje
(8.975 palavras, cinco programas nomeados, revisão, bloco JSON). Braço B é o mesmo
arquivo com **2.121 palavras removidas por script** (`scratchpad/braco_b.py`), todas
de operação: o bloco JSON e o seu conferidor, o aparato bibliográfico e a busca
externa, a revisão inteira, a correção do conferidor de transcrição, o comando que
extrai as figuras, o buscador em lote e o conferidor de entrega. **A análise é
idêntica nos dois**: ordem de leitura, exame da inferência, disciplina, estrutura do
relatório, régua do veredito e regras de escrita saem intactas.

**O material, o mesmo nos dois:** o capítulo 6 da dissertação T,
`[P721]` a `[P793]`, 4.377 palavras, 53 parágrafos, 13 notas, três gráficos. Vai ser
transformado em artigo independente, e os dois braços são informados disso, porque a
escala do veredito depende do estágio. A extração não carrega os comentários de
margem do orientador (conferido: zero ocorrências).

**Os três gráficos entram como arquivo nos dois braços**, identificados à mão, porque
o `figuras_do_docx.py` casou as 117 imagens com a lista de gráficos do início do
documento e não com a posição no corpo. É defeito do casador e fica registrado; dar
as figuras prontas aos dois evita que ele vire variável.

**O que espero, escrito antes:** B fica entre um terço e metade do relógio e das
chamadas de A. Previsão fraca, porque uma rodada enxuta anterior já deu 9,5 min e 14
chamadas contra 32,3 e 64.

**O que decide, e não é o tempo:** quantos achados de A o B não tem, e de que
espécie. O cotejo vai a uma voz que não escreveu nenhum dos dois, recebendo os dois
sem saber qual é qual.

**A hipótese vence** se B for mais rápido e não perder achado de inferência nenhum.
**A hipótese cai** se B perder inferência, ou se afirmar coisa que A conferiu e
derrubou, que é o modo de falha medido do chat: absolver sem testar.

**Confundidor declarado:** os dois braços herdam o `CLAUDE.md` desta máquina, que
carrega a mesma disciplina. Nenhum dos dois mede o prompt sozinho.

### O resultado, 07/09/2026

| | A (programas e revisão) | B (integrada) |
|---|---|---|
| relógio | 40 min 07 s | 12 min 43 s |
| chamadas | 40 | 7 |
| tokens | 274 mil | 148 mil |
| itens | 42 | 48 |
| das 7 observações do orientador | 2 | 1 |
| afirmações conferidas / caídas | 37 / 0 | 31 / 4 |

**A hipótese cai.** B é 3,2 vezes mais rápido e alcança menos, e o cotejo cego,
que não sabia qual era qual, escolheu A pela taxa de erro. Entre as afirmações
caídas de B há acusação de defeito que o capítulo não tem: em `[P787]` ele diz que
a explicação aparece sem marca de ser alheia, e o parágrafo fecha com a fonte.

**A previsão de tempo errou para o lado de A**: eu escrevera entre um terço e
metade, e as chamadas deram 17,5%.

**O cotejo também errou, e vai registrado.** Ele atribuiu a B duas acusações
falsas; conferindo os dois parágrafos, uma se sustenta e a outra não: o item de B
sobre `[P739]` diz que os quatro parágrafos seguintes apresentam como fato o que
aquele marca como hipótese, e isso está certo. Por isso a tabela traz 4 e não 5.

**O que os 33 minutos compraram foi a conferência, e não o achado.** Os dois
chegaram ao mesmo veredito e ao mesmo achado principal (o denominador que o
Gráfico 25 nunca publica, cuja soma anual excede os 5.179 processos declarados).
A revisão de A retirou um item e consertou dezoito endereços ou providências,
duas das quais mandavam escrever no capítulo afirmação que as figuras dele
desmentem.

**O número que decide não é sobre fragmentação: de sete observações do orientador
alcançáveis de dentro do capítulo, o melhor braço fez duas.** Cinco escaparam aos
dois. Duas delas (que monocráticas são essas, e produtividade contra produção)
são a pergunta da unidade contada, passo que estava no prompt e **saiu em
06/09/2026 por reprovar na rodada limpa**. Não se pode afirmar que ele as teria
pego; pode-se afirmar que saiu e que elas passaram.

**Consequência para a fila, e não é executada aqui:** a distância entre esta
leitura e um examinador não encolhe trocando arquitetura, porque as duas
arquiteturas testadas hoje deram 2 e 1 sobre 7. Encolhe com pergunta escrita.

**Um achado que o experimento não pedia:** o braço A isolou um defeito no
`buscar_lote.py`. A chamada `[nota 29]` no meio do parágrafo fazia o resto do
parágrafo ser indexado duas vezes. Consertado no mesmo dia, com controle positivo
provado contra a versão velha.

**Nota ao commit 0a50b55.** Ele carrega, além do resultado do experimento, a
reescrita do `figuras_do_docx.py` (624 linhas), que entrou por `git add -A` sem
que eu a tivesse lido, e a mensagem do commit não a menciona. Conferida depois:
ela endereça os três gráficos do capítulo 6 em `[P751]`, `[P763]` e `[P775]`,
que é o que a conferência manual deste dia havia apurado, casa 897 de 897
parágrafos com a extração, agrupa as peças de cada figura e nomeia a que carrega
o dado. O autoteste dela traz oito controles, um dos quais recusa extração
deslocada de um parágrafo. **O defeito foi de processo e não de código:
`git add -A` num diretório com trabalho de terceiro em curso.**

---

## 07/09/2026 — `figuras_do_docx.py` passa a endereçar por posição

**Os dois defeitos, medidos sobre `t-agosto.docx`.** O programa
produzia 122 entradas de figura; 93 delas traziam endereço, e as 93 caíam entre
`[P161]` e `[P228]`, que é o índice de gráficos das primeiras páginas. O índice
repete a legenda do corpo palavra por palavra, e o casador ficava com a primeira
ocorrência do texto. Os três gráficos do capítulo 6 estão em `[P751]`, `[P763]` e
`[P775]`; o programa dizia `[P182]`, `[P183]` e `[P184]`. O segundo defeito é que
a legenda casava com mais de um arquivo onde o gráfico está partido em arquivos
separados dentro de `word/media`: o corpo do gráfico, o rótulo do eixo e a
legenda de cores. Só um deles mostra o dado. No Gráfico 22 são `image33.png`
(50 KB) contra `image31.png` (2 KB, que traz só o texto "Ano da decisão") e
`image32.png` (4 KB, que traz só a legenda de cores). **O alcance disso é menor
do que a primeira redação desta ficha dizia:** dos 107 parágrafos com imagem,
noventa e oito têm um arquivo só, seis têm dois e três têm três.

**Três coisas mudaram.** A contagem de parágrafos passou a andar a árvore do XML
com a mesma regra do extrator, em lugar de expressão regular. **São dois defeitos
que se compensam em parte, e a primeira redação desta ficha descrevia só um.**
`<w:p ...>.*?</w:p>` trata o parágrafo vazio auto-fechado
`<w:p w14:paraId="..."/>` como abertura e engole o parágrafo seguinte inteiro:
são seis desses, e custam seis. Na outra ponta, a alternativa `<w:p[^>]*/>` casa
dois elementos que não são parágrafo, `<w:pgSz .../>` e `<w:pgMar .../>`, no
`sectPr` final e fora de qualquer parágrafo. A conta é 1.434 − 6 + 2 = 1.430,
conferida contando os casamentos um a um. O endereço passou a ser a
posição, de modo que o n-ésimo parágrafo do corpo é o `[Pn]` da extração; a
extração deixou de servir para achar endereço e passou a conferir o alinhamento
parágrafo a parágrafo, com recusa a endereçar abaixo de 90% de casamento. E as
imagens de um mesmo parágrafo viraram uma figura só, com o portador do dado
escolhido por dois sinais: arquivo que aparece em mais de uma figura é peça
compartilhada, e entre os restantes decide a área em que o Word exibe a imagem
(`wp:extent`), exigida três vezes maior que a segunda.

**Por que a área e não os bytes.** Nos nove parágrafos com mais de uma imagem, a
razão entre a maior área exibida e a segunda vai de **8,4 a 36,4** (a primeira
redação desta ficha dizia 8,4 a 28, porque só seis dos nove tinham sido
calculados; o teto real é o `[P483]`). Por tamanho em disco a menor razão é 2,1,
e naquele caso o arquivo pequeno era mesmo o acessório: `image10.png` tem 19 KB
sendo apenas a legenda de cores do Gráfico 9, conferido abrindo o arquivo. O
tamanho em disco entra só onde não há `wp:extent`.

**Os oito controles do autoteste, e a contagem certa é de dois ou de cinco.**
Cinco trazem um ramo `CONTROLE MORTO`, que reprova quando o caso de teste deixa
de exercer o defeito: a contagem, o endereço, a extração deslocada, a contraprova
de três imagens em parágrafos diferentes e a recusa de eleger portador com áreas
próximas. Desses cinco, **dois** rodam a implementação antiga dentro do teste e
exigem que ela erre: `_contagem_por_regex_antiga`, que tem de contar 3 onde há 4,
e `_endereco_por_texto_antigo`, que tem de errar para `[P2]`. Os outros três são
as quatro escritas de legenda contra três prosas que começam pela mesma palavra,
o agrupamento das três imagens de um parágrafo e o reconhecimento da peça
compartilhada sem apoio em tamanho. **A primeira redação desta ficha dizia três,
que não é nenhuma das duas leituras**, e ainda arrolava a extração deslocada
entre os controles sem ramo, quando ela tem um.

**O efeito esperado.** O alvo é anterior à mudança e veio do orientador: os três
gráficos do capítulo 6 endereçados em `[P751]`, `[P763]` e `[P775]`, e o
apontamento de qual dos três arquivos de cada um carrega o dado.

**O que se mediu depois de rodar:** 107 figuras em 113 arquivos embutidos,
nenhum endereço entre `[P161]` e `[P228]`, faixa de `[P281]` a `[P1184]`, 897 de
897 parágrafos casando com a extração. Os três gráficos saem em `[P751]`,
`[P763]` e `[P775]`, com `image33.png`, `image35.png` e `image37.png`.

**A comparação de listas, corrigida.** A primeira redação desta ficha dizia que a
lista para pedir em lote caiu de 113 para 104 arquivos, e os dois números são da
versão nova. A versão antiga não tinha lista de lote: imprimia 122 linhas com 116
nomes distintos, três deles (`hdphoto1.wdp` a `hdphoto3.wdp`) apanhados porque
ela varria `r:embed=` no bloco inteiro e pegava o do `a14:imgLayer`. A redução de
trabalho para quem lê é de 122 pedidos, ou 116 arquivos distintos, para 104.

**O que mostraria que a mudança foi inútil**, num `.docx` do acervo que ainda não
passou por aqui, com o limiar dito: abrir todos os arquivos apontados como
portadores do dado e contar quantos são rótulo de eixo ou legenda de cores; acima
de 5%, a régua da área foi calibrada no ruído deste trabalho e `RAZAO` não
generaliza. É o sinal que decide, porque é o único calibrado aqui. Junto, dois
sinais de endereço: figura cujo `[P###]` não bata com a conferência manual da
legenda no texto extraído, em qualquer quantidade, derruba o casamento por
posição, que ou vale para todas ou não vale; e a guarda de alinhamento tem de
recusar endereçar quando se lhe der a extração de outra versão do mesmo trabalho.
**Sai da lista o sinal que a primeira redação punha em primeiro lugar**, endereço
que caia na faixa do índice de listas: a versão nova não consulta o texto da
legenda para endereçar, de modo que ela quase não pode falhar por ali, e
falseador que o desenho torna improvável mede pouco.

**Carimbo.** A ficha está escrita depois de rodar, ao contrário do que este
arquivo exige. O que é anterior à mudança é o alvo dos três gráficos, apurado à
mão pelo orientador e já registrado na seção do experimento acima. O alcance
medido é de um documento.

**Dois prompts publicados corrigidos junto, porque a mudança os tornou falsos.**
`ALBERTO.md` e `3-FRENTE-PARA-TRAS.md` diziam que o programa devolve uma tabela,
e ele devolve uma lista por figura. A frase passou a dizer que o `[P###]` é o do
parágrafo em que a figura está e que o programa nomeia o arquivo que carrega o
dado, com uma instrução nova: onde ele disser que não sabe qual carrega, peça
todos os arquivos daquela figura. `.claude/agents/alberto.md` foi gerado de novo.

**O cotejo, e o que ele derrubou.** A pedido do orientador, as vinte e uma
afirmações desta ficha foram numeradas num arquivo e entregues a uma voz que não
as escreveu, com ordem de conferir cada uma por método próprio e de escrever o
próprio contador em vez de contar a saída do programa. **Quatro caíram**, e as
quatro estão corrigidas acima: a aritmética dos 1.430 (dois defeitos, não um), o
teto da razão de área (36,4 e não 28), a comparação de listas (113 e 104 são
ambos da versão nova) e a contagem dos controles positivos (dois ou cinco, nunca
três). Caiu também a generalização de que cada legenda casava com três arquivos,
que vale para nove dos 107 parágrafos com imagem. **Confirmei as quatro por
medição própria antes de corrigir**, porque relatório de conferidor é hipótese
até ser conferido. As dezessete restantes se sustentaram, incluídas as que
exigiam abrir a imagem.

**A crítica ao falseamento veio do mesmo cotejo**, e é a que mais muda esta
ficha: os três sinais eram decidíveis um a um, e nenhum dizia quantas ocorrências
tornam a mudança inútil, de modo que qualquer falha isolada os satisfazia. O
limiar de 5% escrito acima **entrou por decisão e não por medição**, e fica
carimbado assim; o que é medido é a razão de área nos nove parágrafos, que não é
amostra independente.

**Alcance do cotejo:** um documento, e mutação de uma regra por vez no autoteste
(oito mutações, cada uma acusada pelo controle correspondente). O confundidor
está declarado: a segunda voz herda o `CLAUDE.md` desta máquina, a mesma
disciplina que eu segui, e não é leitura independente dela.

## 07/09/2026 — A segunda voz sobre o código, e o que ela derrubou

A voz que leu o código recebeu ordem de quebrar cada regra de propósito numa
cópia e ver se o controle correspondente acusava. **Ela achou defeito de
comportamento em três lugares, e todos foram consertados.**

**1. O defeito 2 estava consertado pela metade.** O agrupamento era por
parágrafo, e a fragmentação atravessa parágrafos. No Gráfico 26 o corpo está em
`[P835]` e a tarja de cores em `[P836]`, cada um no seu: saíam duas figuras, as
duas com motivo "arquivo único", e a tarja de cores entrava na lista dos
arquivos que carregam dado, que é a chamada que o programa existe para poupar.
São **dez grupos assim** em `t-agosto.docx`, incluídos os três em que
`image48.png` (a tarja compartilhada) era eleita portadora do dado. A condição
nova é estreita: juntam-se parágrafos vizinhos, colados e de imagem pura. Um
parágrafo vazio entre eles separa, e é por isso que as capturas de tela do
apêndice continuam figuras distintas. Efeito medido em dez `.docx`: 107 para 97
figuras nos dois trabalhos do trabalho T, e **nenhuma junção nos outros
oito**. Conferido abrindo os arquivos: `image38.png` é o corpo do Gráfico 26,
com rótulo de dado em cada coluna, e `image39.png` é a tarja "Plenário Virtual /
Plenário Presencial".

**2. A busca da legenda tinha viés para a frente.** A ordem era
`0, +1, +2, +3, -1, -2, -3`, e o parágrafo três à frente ganhava do que estava
logo atrás. Em `x-v3.docx` a imagem de `[P528]`, cuja legenda está em
`[P527]` logo acima, saía como "Gráfico 9. Plenário Presencial" de `[P530]`, e os
dois gráficos saíam com o mesmo endereço. A ordem passou a ser por distância, com
empate a favor da legenda de cima. Efeito medido: **seis endereços corrigidos em
cada um dos quatro arquivos do trabalho X**, dois em `t-agosto.docx` e um
em `t.docx`; conferi os oito primeiros um a um, e os oito passaram a
apontar para a legenda imediatamente acima da imagem.

**3. A guarda de alinhamento passava com extração parcial.** O próprio
`analisar_docx.py` sugere extrair por faixa (`--de 1 --ate 300`), e a extração
dos 300 primeiros parágrafos casa 208 de 208, imprime 100% e não confere nenhum
dos 1.134 parágrafos onde estão todas as figuras. A guarda passou a dizer até
onde os marcadores vão, e a marcar com `?` a figura que fica além disso.

**Dois defeitos de silêncio, corrigidos junto:** `--extracao` com caminho
inexistente caía na mensagem "sem --extracao", de modo que um erro de digitação
convertia corrida conferida em corrida não conferida; e `.docx` sem
`word/document.xml` saía com traceback.

**O achado mais grave não é nenhum dos três: os controles não tocavam a tese.**
`_par()` produzia sempre parágrafo filho direto do `<w:body>`, então nenhum dos
oito controles tinha tabela, `w:sdt` ou aninhamento. **Tirar `w:tbl` do conjunto
de descida leva a contagem de 1.434 para 1.319 neste trabalho e de 1.347 para 801
na `x-v3.docx`, e o autoteste continuava verde.** A regra de descida é a
tese inteira do conserto por posição, e era a única coisa que não se testava.

**A bateria de sabotagem virou o critério, e ela é o que mede um controle.** Doze
sabotagens, uma regra quebrada por vez: as doze são acusadas. Duas delas
mostraram controle fraco que eu tinha escrito como forte: o da extração deslocada
passava com a comparação de texto **desligada**, porque um marcador fora da faixa
carregava sozinho o veredito, e o limiar testado não era o que o programa usa.
Os controles foram de oito para dezessete.

**O que a segunda voz não conseguiu conferir, e importa mais que o resto:** a
calibragem de `RAZAO = 3.0` fora do trabalho em que foi feita. Nos outros oito
`.docx` do acervo há uma imagem por parágrafo, e `repartir` nunca chega ao
limiar. O `ANOTADO-plenario-virtual.docx` não serve, porque é o mesmo trabalho
(os 117 arquivos de `word/media` têm os 117 mesmos MD5). **A conferência de
`RAZAO` continua circular por falta de material, e não por falta de esforço.**

**Fica na fila, medido e não consertado:** `RE_LEGENDA` roda com `re.I`, de modo
que `[A-Z]` casa minúscula e "Tabela 1 apresenta os dados" é lido como legenda
(latente: as 408 legendas atribuídas no acervo são todas legendas de verdade, e a
janela de mais ou menos três parágrafos hoje protege, mas `--vizinhanca` não tem
teto). A leitura das relações por expressão regular exige `Id` antes de `Target` e
devolve lista vazia em silêncio se a ordem inverter. Nenhum dos dois ocorre nos 30
`.docx` do acervo.

**Confundidor declarado:** a voz do código herda o `CLAUDE.md` desta máquina, a
mesma disciplina que eu segui, e não é leitura independente dela.

**Origem:** os dois defeitos iniciais foram relatados pelo orientador, com os
casos; o conserto, os controles e os defeitos desta segunda rodada são meus, e
foram achados por uma segunda voz que o orientador mandou abrir. A nota ao commit
`a05d5bc` registra que a reescrita entrou no `0a50b55` sem ter sido lida.

### O falseamento, rodado em 07/09/2026

**Primeiro achado, e ele é sobre o acervo e não sobre o programa: há 52 arquivos
`.docx` nos dois repositórios e oito obras distintas.** A conta é por impressão
digital das imagens (MD5 de cada arquivo de `word/media`), e ela junta
`plenario-virtual.docx`, `trabalho.docx`, `trabalho-normalizado.docx`,
`ENTREGA-ANOTADO-t-agosto.docx` e mais quatro nomes numa obra só. As
cópias anotadas, normalizadas e entregues multiplicam nomes e não material.

**O sinal do endereço, sobre obra intocada.** `v-tese.docx`, autora
diferente, 13 figuras, 704 parágrafos. Alinhamento de 617 de 617 marcadores,
cobrindo até `[P704]`. **Os 13 endereços conferidos um a um, abrindo os
parágrafos vizinhos de cada figura: 13 certos.** O caso interessante é que essa
tese põe a legenda ACIMA da imagem nas figuras 1 a 6 e ABAIXO nas 7 a 13, e a
regra de distância acertou as duas disposições, que é o que a mudança de hoje
tinha de fazer. Onde o programa diz `Figure X. Source: prepared by the author`, o
parágrafo é mesmo esse: a autora deixou o título por preencher, e o defeito é do
trabalho.

**O sinal que decide, e ele não pôde ser rodado em material independente.** A
régua da área só é exercitada onde há grupo com mais de um arquivo, e nas oito
obras isso ocorre em duas: `t-agosto.docx`, que é onde `RAZAO` foi
calibrada, e `t.docx`, que é a versão anterior do mesmo trabalho, da
mesma autora e com o mesmo hábito de colar gráfico do Excel. Rodei na versão
anterior, que tem 78 imagens, 69 grupos e **dez grupos em que a régua decide**.

**Resultado: dez eleitos abertos, dez são corpo de gráfico com dado.** E a outra
metade do teste, que é a que pegaria o erro grave: **sete descartes distintos
abertos, sete são legenda de cores** (`image2`, `image4`, `image11`, `image19`,
`image30`, `image32`, `image63`). Zero erros em dez, contra um limiar que
reprovava com um. Em três desses grupos quem decidiu foi o reaproveitamento, e
não a área, o que interessa porque é o sinal que não depende de tamanho.

**O que este resultado não autoriza a dizer.** Não é medição independente: mesma
autora, mesma ferramenta de gráfico, e o próprio arquivo de imagem `image11.png`
reaparece em três grupos como no trabalho de agosto. O que ele mostra é que a
régua não se prende ao conjunto exato de figuras em que foi calibrada; o que
falta continua faltando, e é obra de outro autor com figura fragmentada.

**Fica na fila, e é a condição de fechar este falseamento:** achar ou produzir um
`.docx` de outro autor com gráfico partido em arquivos. Enquanto não houver, a
linha honesta na ficha é que `RAZAO` foi calibrada e conferida num só trabalho,
em duas de suas versões.

---

## 07/09/2026 — A busca por nome de arquivo também tem alcance, e o meu era curto

**O caso.** Auditando as entregas, comparei o relatório do Alberto que a autora do trabalho R
recebeu com os arquivos do acervo e afirmei ao orientador que **o relatório
entregue não existia no disco**, sendo uma terceira linhagem de origem
desconhecida. A conclusão saiu de um `ls ALBERTO-*.md`.

Existem duas convenções de nome, e o padrão pegava só uma:

    RELATORIO-ALBERTO-<orientanda>.md   o relatório de producao, o que vai à entrega
    ALBERTO-<ORIENTANDA>-v2.md          as rodadas de medição, feitas depois

O arquivo estava lá o tempo todo, em `RELATORIO-ALBERTO-r.md`, escrito às
20:22, vinte e sete minutos **antes** da primeira rodada de medição. Os itens
diferem porque são leituras diferentes do mesmo trabalho, e não versões do mesmo
texto. Não havia divergência de linhagem nenhuma.

**A regra que eu quebrei é a que esta oficina publica.** *Toda afirmação de
ausência vem provada: procure alguma coisa que você sabe que está, do mesmo tipo,
e diga que achou.* Eu a aplico a busca de texto dentro de um trabalho e não a
apliquei a uma busca por nome de arquivo. **O zero de um padrão de nome estreito
tem exatamente a mesma cara do zero de coisa inexistente**, e produz afirmação
mais grave, porque afirmar que um arquivo entregue não existe põe em dúvida a
entrega inteira.

**O controle que teria bastado**, e custa uma linha: antes de afirmar que um
arquivo não existe, procurar pelo conteúdo e não pelo nome. `grep -rl` numa frase
do próprio documento devolveu os três arquivos em segundos, e foi assim que o erro
caiu.

**É a segunda vez no mesmo dia.** Horas antes eu afirmara que não existia arquivo
com 33 comentários do orientador sobre o trabalho T, tendo varrido só
`D:\Claude\TCC`; o arquivo estava em `Downloads`. Ali eu declarei o alcance e a
afirmação ficou tecnicamente correta, mas a **conclusão** que tirei dela (que a
tarefa nunca teve material) não era coberta pelo alcance declarado. Declarar o
alcance não autoriza concluir para fora dele.

**Se transfere para os prompts?** A regra de ausência com controle já está escrita
no `ALBERTO.md` e no `_REGRAS.md`, e as duas falam de procurar palavra no trabalho.
Nenhuma diz que a mesma exigência vale para procurar arquivo, e as duas leituras
rodam em máquina onde ninguém as corrige. **Fica proposto e não executado**, para
não entrar prompt novo sem caso medido do lado da leitura: os dois casos de hoje
são meus, na condução da sessão, e não de uma leitura.

**Levada aos prompts em 07/09/2026, por decisão do orientador.** A regra maior é a
do alcance, e não a do nome de arquivo: *declarar o alcance não autoriza concluir
para fora dele*. Entrou nos sete lugares em que a leitura pode produzir a frase
larga: os seis passos do Luis (nas cinco escritas diferentes que a regra 2 tem
neles) e a disciplina do `ALBERTO.md`. O passo 6 não carrega o bloco das três
regras, porque não busca, e recebeu outra formulação: é ele que redige, e é na
redação que *não ocorre no capítulo 4* vira *o trabalho não trata do assunto*.
O caso do nome de arquivo entrou só no `_REGRAS.md` e no `ALBERTO.md`, junto dos
defeitos de ambiente, que é onde ele é.

**Objeção minha, registrada e vencida:** os dois casos medidos são meus, na
condução da sessão, e não de uma leitura, de modo que a regra entra sem caso do
lado que o prompt governa. **O falseamento:** se em três leituras seguidas nenhuma
frase de alcance largo aparecer nos relatórios anteriores a esta mudança, ela era
enfeite e sai.

---

## 07/09/2026 — O `re.I` do `RE_LEGENDA`, e a medição contrariou o pedido

**O pedido do orientador foi tirar o `re.I` e medir o efeito.** A medição
contrariou a premissa, e o que entrou foi outra coisa, escolhida por ele depois
de ver o número.

**O `re.I` fazia duas coisas, e só uma é defeito.** Ele deixa a palavra do tipo
ser reconhecida em qualquer caixa (`TABELA 4`, `GRÁFICO 12`) e deixa o `[A-Z]` do
identificador casar minúscula, de modo que `Figura a - y` era lido como legenda.
Tirá-lo inteiro perde a primeira junto com a segunda.

**Efeito medido de tirá-lo: zero.** Nas oito obras distintas do acervo os mesmos
360 parágrafos casam a expressão, as mesmas figuras ficam com legenda e nenhum
endereço muda. A razão está na grafia: **as 360 legendas escrevem o tipo com
inicial maiúscula** (Gráfico 308, Tabela 17, Quadro 14, Figure 13, Figura 8), sem
uma ocorrência em caixa alta ou minúscula. O `re.I` não protegia nada aqui, e
tirá-lo não custaria nada aqui; o custo seria em trabalho futuro que escreva
`TABELA 4`, grafia corrente que falta a estas oito por acaso.

**O falso positivo que motivou o pedido não vem do `re.I`.** `Tabela 1 apresenta
os dados` casa pela segunda alternativa, que aceita número sem separador, e
continua casando com ou sem `re.I`. Essa alternativa dispara **4 vezes em 360**,
todas na `dissertacao-nova`, onde a legenda ao lado da imagem é o texto
`Gráfico 1` sozinho, e por isso ela fica. Apertá-la para exigir que nada sobre
depois do número rejeitaria também `Chart 3 Something`.

**O que entrou:** o `(?i:...)` cobre só a palavra do tipo. `Figura a - y` para de
passar, `TABELA 4` e `GRÁFICO 12` continuam passando. **Conferido nas oito obras:
360 casamentos contra 360, mesmas legendas, zero endereços mudados.** O controle
do autoteste roda a expressão com `re.I` global e exige que ela aceite
`Figura a - y`, senão o caso deixou de exercer o defeito.

**O que continua passando, e fica escrito para não ser redescoberto como
novidade:** `Tabela 1 apresenta os dados` e `tabela 3 de resultados`. O autoteste
agora **exige** que os dois casem, de modo que o dia em que pararem de casar, o
comentário acima da expressão terá ficado desatualizado e o teste avisa.

**Carimbo:** é guarda contra defeito latente, e não correção de defeito
observado. Nenhuma das 408 legendas atribuídas no acervo estava errada por esta
causa. O que a medição mostrou é que o diagnóstico anterior atribuía ao `re.I` um
falso positivo que é da segunda alternativa.

---

## 07/09/2026 — A pergunta da unidade contada volta, e muda de lugar

**Por que volta.** Ela saiu em 05/09 por ter sido reprovada numa rodada limpa, e a
ficha daquela retirada registrou o motivo com precisão: *o passo disparou quando o
pedido o repetia e não quando só o prompt o trazia; isso não mostra que o conteúdo
não sirva, mostra que, escrito naquele lugar, ele não compete com o resto. Quem
quiser retomá-lo tem de mudar o lugar, não a redação.*

**A evidência nova, de 07/09.** No cotejo do capítulo 6 do trabalho T contra as
observações de margem do orientador, duas das cinco que escaparam aos dois braços
são exatamente esta pergunta: que espécie de decisão está contada como monocrática
(`[P773]`), e se a palavra que nomeia a série diz o que a série mede (`[P770]`).
São observações de outro trabalho, feitas por quem orienta, e não por mim.

**O que mudou de lugar, e é a alteração inteira.** Deixou de ser passo à parte e
passou a pender de uma regra que já dispara: *todo número vem com a regra e com a
palavra contada*, que governa os números do relatório e funciona. O acréscimo diz
que a mesma exigência vale para os números do trabalho, e desdobra em duas: a
composição da unidade e o nome da série. No `3-FRENTE-PARA-TRAS.md` entrou como
mais uma guarda na lista que já existe, ao lado de censo, seleção e independência.

**Custo:** 130 palavras no `ALBERTO.md` contra as 358 que a versão de passo tinha,
e 80 no `3-FRENTE`. **Sem exemplo concreto**, porque o exemplo que eu escrevera na
versão anterior voltou atribuído à dissertação, com localizador, e a palavra não
ocorria uma vez em 1.434 parágrafos.

**O falseamento, escrito antes de rodar.** Uma leitura sobre trabalho com série
contada, com o prompt de antes como braço de controle. Se o braço novo não produzir
item nem questão sobre a composição da unidade ou sobre o nome da série, a mudança
de lugar não resolveu e ela sai de novo, desta vez sem retorno.

**Origem: raciocínio meu sobre uma medição do orientador.** A pergunta é dele, e
a decisão de mudar o lugar em vez da redação veio da ficha de 05/09. Não medida.

---

## 08/09/2026 — O falseamento do `RAZAO` fechou, em obra de outro autor

**O que faltava, escrito na ficha de ontem:** um `.docx` de outro autor com
gráfico partido em arquivos. Nas oito obras do acervo só as duas versões da mesma
dissertação exercitavam a régua, e a conferência era circular.

**Onde estava.** `Downloads` tem 285 arquivos `.docx`. A varredura leu só a
estrutura de imagens, sem abrir texto, e achou cinco obras novas com grupo de
mais de um arquivo. A escolhida foi a dissertação em elaboração de outro
orientando (1.759 parágrafos, 44 imagens, 34 grupos, **onze deles decididos pela
régua**). As versões de julho e junho do "Plenário Virtual" ficaram de fora por
serem do mesmo trabalho já usado.

**Resultado: onze eleitos abertos um a um, onze são corpo de gráfico com dado.**
Os descartes conferidos são legenda de cores, incluído `image3.png`, que aparece
em duas figuras e por isso foi tratado como peça compartilhada sem consulta a
tamanho. Zero erros, contra um limiar que reprovava com um.

**O caso é mais duro que o da calibragem, e é isso que dá valor ao resultado.**
No trabalho em que `RAZAO` foi calibrada, a área e os bytes concordavam. Aqui
discordam: **em oito dos onze grupos o arquivo descartado é maior em bytes que o
eleito**, porque a legenda desse trabalho é um bloco de sete a nove linhas de
texto corrido. `image19.png` tem 111 KB de legenda contra 45 KB do gráfico
`image18.png`. O desempate por tamanho em disco teria errado os oito, e num deles
por margem de sorte: 47.923 contra 49.037 bytes, razão de 1,02, onde a área
separa 5,1 para 1.

**O que isto autoriza a dizer, e só isso:** a régua da área não se prende ao
trabalho em que foi calibrada, e a escolha da área em lugar dos bytes, que ontem
se apoiava em nove grupos de uma autora, agora tem contraprova em material que
inverte o sinal do tamanho em disco. **O alcance continua sendo dois autores.**

**Fica disponível para uma segunda rodada**, e não foi feita: outro arquivo de
`Downloads`, com 41 imagens em 15 grupos e 14 decididos pela régua, de terceiro
autor. Se a intenção for fechar o alcance em três autores, é ali.

---

## 08/09/2026 — A pergunta da unidade contada rodou, e o falseamento como estava escrito teria dado vitória

**O desenho.** Dois braços, mesma dissertação, mesmo modelo, pedido idêntico
palavra por palavra, **uma variável só**: o `ALBERTO.md` de antes do `9ecdf76`
contra o de depois, e o `diff` entre os dois é exatamente as 16 linhas da
alteração. Material igual ao do experimento de ontem (capítulo 6, `[P721]` a
`[P793]`, 56 parágrafos marcados, 4.422 palavras), com uma melhora: as três
figuras entraram pelo `figuras_do_docx.py`, com o arquivo do dado já apontado, em
vez de identificadas à mão, que era confundidor declarado na ficha de ontem.
**Uma execução de cada lado**, e portanto o que segue é indício.

**Metade (a), a composição da unidade: os dois braços produziram o item.** O de
controle chegou por `[P736]`, a citação de Reis e Oliveira que o próprio capítulo
traz, e enunciou contra `[P793]`. O braço novo chegou pela moldura do próprio
capítulo (`[P731]`, o art. 97 e a reserva de plenário) contra `[P748]`, e enunciou
contra `[P793]`; ainda registrou a limitação declarada como ponto forte e
produziu uma **segunda** pergunta de composição, sobre outra série (a categoria
Plenário Presencial não separa os julgamentos em lista das demais colegiadas).
**O acréscimo não pode ser creditado por fazer o item aparecer.** No máximo, por
ancorá-lo na moldura do trabalho em vez da literatura, e por produzir o segundo.

**Metade (b), o nome da série: nenhum dos dois produziu.** A oportunidade estava
lá, e isto vem com controle: `produtiv*` ocorre onze vezes no recorte, em
`[P757]`, `[P758]`, `[P759]` e `[P789]`. É exatamente a observação do orientador
que motivou o retorno da pergunta (produtividade contra produção). O acréscimo
falhou aqui.

**O confundidor que impede a leitura causal, e ele não é do prompt:** o braço de
controle **não abriu a segunda voz** e o braço novo abriu. Os dois prompts a
exigem igualmente (treze menções em cada). A revisão do braço novo derrubou três
deslizes do próprio rascunho e levantou um ponto novo. A diferença de quantidade
(17 itens contra 11) não é atribuível ao acréscimo enquanto isso não for repetido.

**E o achado que decide sobre a ficha: o falseamento como estava escrito teria
declarado vitória.** Ele pergunta se o braço novo produz item sobre a composição
**ou** sobre o nome da série; o braço novo produziu sobre a composição, e pela
letra a alteração sobrevive. O que impede essa leitura é o braço de controle, que
a própria ficha mandava rodar e cujo resultado o critério não usava. **Critério
de uma perna só, sobre mudança que existe para produzir diferença.**

**O critério em vigor passa a ser comparativo e por metade**, e fica escrito antes
da próxima rodada: a alteração se sustenta se, em três rodadas, o braço novo
produzir a pergunta do nome da série pelo menos uma vez e o de controle nenhuma;
e a metade da composição sai do critério, porque está medido que aparece sem ela.
Se as três rodadas passarem sem o nome da série, o acréscimo não fez o que se
esperava e sai.

**Defeito de ambiente achado de passagem, e é do prompt publicado.** O
`ALBERTO.md` manda rodar seis programas como `python scripts/<nome>.py` sem dizer
de que diretório. A leitura roda em `D:\Claude\TCC`, onde `scripts\` **existe e
tem 35 programas**, nenhum deles os seis nomeados, que moram só na Oficina. É pior
que arquivo faltando: a pasta existe e traz nomes vizinhos, de modo que uma
leitura pode rodar o programa errado sem desconfiar. Os dois braços caíram nisso e
substituíram por equivalentes manuais, o que afeta os dois igualmente e não
invalida o cotejo. **Não corrigido nesta rodada**, para não mexer em prompt
publicado no meio de uma medição.

---

## 08/09/2026 — A frase que dizia que o Alberto não confere conta em tabela era falsa

**O caso.** Uma voz externa apontou que o `ALBERTO.md` afirmava, sobre si mesmo,
que *o que ela deixa passar é o que depende de conferir número: refazer a conta
dentro de uma tabela de resultado e comparar o que a tabela publica com o que a
prosa afirma dela*. A frase descrevia uma medição de 03/09.

**O que a derruba, e são quatro execuções do mesmo dia.** Sobre o capítulo empírico
da dissertação T, os braços A, B, BUSCA e PRONTO refizeram a
aritmética das figuras e chegaram, cada um por um caminho, ao denominador que o
capítulo nunca publica: as contagens do Gráfico 22 divididas pelas médias do
Gráfico 25 somam mais de onze mil processos-ano contra os 5.179 declarados em
`[P749]`. O braço PRONTO ainda calculou a série proporcional a partir dos números
impressos em `[P757]`, que o capítulo não calcula, e fez dela o achado central.

**O que entra no lugar.** A afirmação corrigida, mais a lacuna onde ela de fato
está: perguntar o que exatamente está sendo contado. Medido em 07/09 contra as
observações de margem do orientador, cinco das sete alcançáveis escaparam a duas
arquiteturas, e duas eram a composição da unidade e o nome da série.

**Não é regra nova, é correção de fato.** Por isso entra sem falseamento próprio:
o que a sustenta são as quatro execuções, e o que a derrubaria é uma leitura que
não faça a conta quando ela decide o item.

**Ressalva sobre a evidência que a voz externa trouxe.** Ela citou um agente de
desk que fez a conta de uma tabela sem instrução no prompt dele. Isso não mede o
modelo sem a regra: os subagentes desta máquina herdam o `CLAUDE.md`, que carrega a
disciplina de contagem. E os números do achado dela não vieram com informação de
terem sido conferidos na fonte.

---

## 08/09/2026 — O passo 5 do Luis passa a receber o trabalho inteiro num arquivo

**A ficha com os falseamentos foi escrita antes dos resultados**, em
`D:/Claude/TCC/experimento/FICHA-PASSO-5-E-6.md`.

**O resultado, uma execução de cada lado, sobre a dissertação R:**

| | tokens | relógio | chamadas |
|---|---|---|---|
| passo 5 antigo (confere o levantamento) | 466.278 | 66,6 min | 102 |
| passo 5 novo | 270.698 | 14,0 min | 28 |
| conferência do relatório já triado, antiga | 262.840 | 16,9 min | 30 |
| a mesma, no modo novo | 249.023 | 15,3 min | 31 |

**O ganho é do levantamento e não de toda conferência**, e isso entrou no prompt
como delimitação: o levantamento espalha itens de quatro leituras por centenas de
parágrafos e o método antigo ia buscar cada um; num relatório triado os itens já
estão organizados e não há o que economizar.

**Falseamento 1, e eu escolhi mal o limiar.** Eu escrevera *se passar de 30
chamadas, não escala*. Deu 31 pela contagem do sistema e 30 pela do agente: caiu em
cima da linha. Limiar de valor exato com duas contagens possíveis não testa nada. O
que sustenta a alteração sem depender dele é a escala: o trabalho cresceu de 56 para
402 parágrafos, sete vezes, e as chamadas foram de 14 para 28, cerca de duas.

**Falseamento 2 continua aberto: não há medida de recall.** O passo 5 antigo
consolidou o levantamento em 44 itens `V` e a conferência nova percorreu 113
códigos. Se os 44 cobriam o mesmo terreno de forma agrupada, os 79% de queda são
reais; se não, estão inflados. **Não sei qual é o caso.**

**Falseamento 3, testado pela metade.** A ordem por carga sobrevive ao desconto dos
itens largos: os quatro parágrafos do topo continuam no topo. Se ela muda alguma
decisão de triagem continua por medir.

**E o método novo devolveu o que o antigo não devolvia:** quatro divergências entre
as quatro leituras, com os dois códigos e o localizador. Sobre `[P460]`-`[P473]`, a
leitura 1 diz que as quatorze categorias estão no corpo e a leitura 4 diz que só
sete estão, e nenhuma das duas confere. Isso não entra na conta de custo, e é o que
quatro leituras dão e uma não dá.

**Divergência registrada.** Eu propus esperar as conferências antes de alterar os
prompts; o orientador mandou fazer, e depois endossou a ordem que eu propusera. A
alteração ficou sem commit até os resultados chegarem, e é este o commit.

**Achado colateral, e ele veio das próprias conferências.** As duas acharam o mesmo
defeito na ferramenta: a fronteira do item era só o item seguinte, e o último item
de cada seção engolia a prosa posterior. Consertado no mesmo dia, com a fronteira
passando a ser o próximo item **ou** o próximo cabeçalho.

---

## 08/09/2026 — A parte 5 pergunta nos dois sentidos, e a metáfora de encanamento sai

**O caso.** O orientador apontou que *consome* é palavra ruim para uma boa
pergunta, e propôs a formulação certa: **que partes se baseiam em partes
anteriores**. Duas coisas saíram daí.

**A palavra já tinha viajado.** *Quem consome esta seção* aparece quatro vezes nos
relatórios de 08/09, copiada da minha redação no prompt. É o tique que a regra
prevê: categoria de trabalho não fica na conversa, vai para o documento entregue a
quem nunca viu a invenção. Trocada aqui e nos dois lugares do
`6-TRIAGEM-E-REDACAO.md` que governam texto entregue. Onde *consumir* é tempo,
token, semana ou linha de lista, fica: ali é a palavra portuguesa.

**E a pergunta estava só num sentido.** *Quem consome cada capítulo* olha para a
frente e acha a peça isolada, que serve à decisão de cortar. *Em que partes
anteriores esta se baseia* olha para trás e acha a afirmação sem apoio, que é o
sentido que a régua nova do veredito tornou decisivo em 06/09. **A parte 5 é
anterior à régua e nunca foi revista depois dela.** Agora pede os dois, com o
endereço de cada elo.

**Junto entrou o que a medição de hoje mostrou ser extraível e o que não é.** Sobre
os 402 parágrafos do trabalho R: verbo de inferência em 62 parágrafos e conector de
consequência em 46, de modo que a lista de candidatas a inferência sai de programa.
Mas só 61 parágrafos trazem remissão explícita, e a maior parte é dêitica (*acima*,
*supra*, *como visto*), que registra a existência do elo e não o destino.

**Daí a regra que entrou:** o elo se declara e não se deduz da vizinhança, e
remissão dêitica sem destino nomeado é achado por si, porque o leitor de um artigo
independente não terá o *acima*.

**O que isso derruba, e é proposta minha de uma hora atrás.** Eu havia proposto um
grafo de dependência computado da coincidência de localizadores entre itens do
relatório. Os números acima mostram que isso seria um grafo do que a leitura
aponta, apresentado como se fosse o do argumento. Grafo tem aparência de coisa
apurada, e esse seria pior do que não ter. **Retirado.**

**Origem:** a formulação é do orientador; a medição de extraibilidade é minha, de
hoje. Sem falseamento próprio: é troca de palavra e acréscimo de um sentido à
pergunta, não regra nova.

---

## 08/09/2026 — A conferência barata vai do Luis para o Alberto

**O caso.** As melhorias da tarde entraram no passo 5 do Luis e não no Alberto, que
é justamente o que deveria ser rápido. O orientador apontou a inconsistência.

**O que muda.** A revisão do Alberto deixa de ir à extração buscar cada passagem e
passa a ler o arquivo do `enderecos_em_lote.py --tudo`: o trabalho inteiro, com os
códigos dos itens ao lado de cada parágrafo, mais o relatório. Ganha a ordem por
carga e a lista de colisões, e a procura de pares que se desfazem deixa de ser feita
de memória.

**Entram na lista do que a revisão procura as três espécies que apareceram em
leituras entregues:** a condicional convertida, o sujeito trocado e a atribuição
declarada ausente que está impressa. As três foram achadas em 07 e 08/09 sobre um
mesmo relatório, e as três se acham no arquivo pareado sem abrir mais nada.

**O que sustenta.** No Luis, a mesma troca levou a verificação de 66,6 min, 102
chamadas e 466 mil tokens para 14,0 min, 28 chamadas e 271 mil.

**O que ainda não se sabe, e por isso a troca vai medida e não decidida.** A revisão
do Alberto faz seis coisas (endereços, ausências, números, atribuições, alvos de
correção, colisões) e a conferência em lote faz a primeira muito bem e as outras em
parte. **Não é substituição, é troca com perda a medir.**

**A medição que decide**, e é o que roda a seguir: a mesma conferência em lote sobre
o `ALBERTO-R-v4.md`, cujo relatório já passou pela revisão cara dentro dos
49,8 minutos da rodada. Se ela acusar o que a revisão cara acusou, a troca se paga;
se acusar menos nas classes que não são endereço, a perda fica dimensionada.

**Falseamento:** se a conferência em lote sobre a v4 não achar nenhum dos 19
endereços ou providências que a revisão cara consertou, ela não substitui aquele
passo e volta a ser primeira passada, com a cara depois.

---

## 08/09/2026 — O resultado do dia, e ele é contra as alterações do dia

### O cotejo cego de três, sobre a dissertação R

Alberto de 06/09, Alberto de 08/09 e Luis, renomeados e sem dizer qual era qual.

| | inferência | descrição | estrutura | superfície | total |
|---|---|---|---|---|---|
| Alberto v2 (06/09) | 11 | 12 | 7 | 29 | 67 |
| Alberto v4 (08/09) | 15 | 14 | 6 | **50** | 91 |
| Luis | 23 | 7 | 15 | 10 | 67 |

**A vantagem numérica da v4 é quase toda de superfície.** Nas duas classes que
decidem, os três estão perto: 23, 29 e 30 itens.

**O cotejo escolheu o Luis**, e não por tamanho: a v4 funda o veredito numa conta
inválida que o Luis faz, vê o mesmo dado de `[P439]` e se recusa a fechar,
escrevendo o que faltaria.

### Os dois defeitos da v4 são meus

**A conta inválida é o erro que esta oficina cometeu em 06/09 e corrigiu**: descontar
quarenta e um temas de uma matéria de um lado só da comparação, fazendo 7,6 pontos
"caírem" para 2,7. Voltou em 08/09, e desta vez abre o relatório, entra no veredito e
volta como primeira pergunta de banca. **Entrou nos dois prompts como armadilha
nomeada**, porque não é descuido: é a conta que o material convida a fazer.

**Os oito itens de figura endereçam `[P444]`, `[P478]`, `[P515]` e `[P522]`**, que não
existem na extração. A causa é o `figuras_do_docx.py`, que imprimia *imagem em
[P444]* para a posição da imagem, e posição de imagem não é endereço, porque o
parágrafo que a carrega não tem texto e a extração não lhe dá marcador. Consertado no
mesmo dia: a posição sai sem colchetes e com a frase que diz que o endereço é o da
legenda. Controle: dos sete localizadores impressos, zero inexistentes, contra quatro
antes.

### A revisão barata sobre a v4

**91 itens, 13,6 minutos, 21 chamadas, 249 mil tokens, zero aberturas fora do
arquivo.** Sobre um relatório que **já tinha passado pela revisão cara** dentro dos
49,8 minutos da rodada, ela achou mais 1 item caído e 5 endereços errados, e oito
achados próprios, entre eles que os cinco n do capítulo 4 somam 160 e não 170.

**O falseamento que eu escrevi não podia disparar**, e é o terceiro do dia com esse
defeito: eu perguntei se a barata acharia os 19 endereços que a cara consertou, e a
cara já os tinha consertado no arquivo que a barata leu. O que se mediu foi outra
coisa, e melhor: **a barata acha o que a cara deixou passar, por um quarto do
tempo.**

**Nove dos 91 itens não puderam ser conferidos**, todos pela mesma causa: dependem de
valor impresso nas figuras, cujos localizadores eram os mortos acima. O defeito da
ferramenta custou 10% da conferência.

---

## 08/09/2026 — `grep -i` não dobra maiúscula acentuada, e a raiz curta não casa a flexão

**O caso, e quem o achou foi uma conferência contra si mesma.** A revisão do
`ALBERTO-R-v5` declarou que três dos seus próprios controles produziram o
achado em vez de o encontrarem, e que nos três o relatório conferido estava certo e
ela errada. As causas são duas, e as duas são deste ambiente:

- **O locale é C**, e ali o `-i` do `grep` dobra `a` com `A` e não dobra `á` com
  `Á`. Então `grep -i "época"` acha no meio da frase e perde no começo dela.
- **Raiz curta não casa a palavra flexionada com acento:** `pandem` não acha
  *pandêmico*, porque o acento entra no meio da raiz.

**Controle, e ele foi rodado antes de publicar a regra.** Num arquivo com duas
ocorrências, uma abrindo frase com maiúscula, `grep -i "época"` devolve 1 e
`grep "época"` devolve 1: o `-i` não muda nada. O `buscar_lote.py` devolve 2,
porque tira o acento antes de comparar.

**A regra entrou nos dois lugares onde os defeitos de ambiente moram**, com a saída
junto: buscar as duas formas, ou usar o `buscar_lote.py`.

**Por que isto importa mais do que parece.** É a família de defeito que produz
afirmação de ausência falsa, que é o erro mais caro desta oficina, porque manda o
autor escrever o que já está escrito. E aqui ele estava dentro do próprio
instrumento de conferência.

---

## 08/09/2026 — O passo 5 novo, medido inteiro, e a lista de colisões que não serve

**O passo 5, sobre a dissertação R, com o mesmo levantamento:**

| | antigo | novo |
|---|---|---|
| relógio | 66,6 min | **19,4 min** |
| chamadas | 102 | **44** |
| tokens | 466 mil | **330 mil** |
| itens conferidos | 44 | **169** |

**Isto fecha o falseamento 2, que ficara aberto de manhã.** Eu não sabia se os 44
itens `V` do método antigo cobriam o mesmo terreno de forma agrupada. Não cobriam:
o novo confere **quatro vezes mais itens em menos de um terço do tempo**, e o
antigo consolidava.

**A primeira tentativa deste mesmo passo conferiu 113 itens e não 169**, porque o
`enderecos_em_lote.py` lia uma só das três escritas de código. O conserto vale 56
itens de cobertura.

**Sete divergências entre as quatro leituras**, contra a uma que se conhecia, cada
uma resolvida com o texto: sobre os 32,6% decide a favor da leitura 3; sobre quantas
categorias residuais `[P473]` nomeia, duas leituras dizem seis e uma diz sete, e são
seis. Isso é o que quatro leituras dão e uma não dá, e agora sai por escrito.

### A lista de colisões que eu construí hoje não serve

Das **quatro colisões reais** que a verificação achou, **nenhuma** está nas oito que
o meu cabeçalho apontou. Das oito apontadas, quatro são o mesmo item visto por duas
leituras e quatro são complementares. **Precisão zero e recall zero.**

A causa é o critério: dividir três ou mais parágrafos mede coincidência de material,
e colisão é coincidência de **providência**. Dois itens que mandam reescrever a
mesma frase colidem ainda que citem parágrafos diferentes; dois que citam a mesma
figura por razões distintas não colidem.

**Fica retirada do cabeçalho na próxima passada**, ou muda de critério para comparar
o campo da providência em vez do conjunto de localizadores. A ordem por carga, que é
a outra metade do cabeçalho, continua: a verificação a usou e disse que vale.

---

## 08/09/2026 — Três defeitos de operação achados pelas próprias leituras

**1. O scratchpad compartilhado sobrescreveu arquivo de trabalho.** O passo 6 do trabalho R reportou que dois arquivos dele foram sobrescritos por conteúdo de outro
trabalho no meio da redação, porque várias rodadas paralelas gravam no mesmo
scratchpad de sessão. Ele detectou, mudou para arquivos dentro da pasta do projeto
e conferiu que nada vazou. **A versão silenciosa desse acidente é um relatório com
parágrafo de outro trabalho dentro.** Daqui em diante cada rodada recebe pasta
própria no pedido.

**2. O programa de endereços toma a sigla do trabalho por código de item.** No
trabalho do trabalho K, `GF1`, `VP2` e `VP3` são siglas de lacuna **do próprio autor**,
e o `enderecos_em_lote.py` as capturou como se fossem itens do levantamento. São os
sete fantasmas da diferença entre os 88 que o programa contou e os 81 que a
verificação conferiu. A causa é o padrão aceitar qualquer `[A-Z]{1,2}\d+` no começo
da linha, e a sigla do trabalho tem essa forma.

**3. Os prompts não fixam convenção de prefixo, e é a causa-raiz do resto.** A
leitura 3 do trabalho K procurou a convenção no `3-FRENTE-PARA-TRAS.md`, no `_REGRAS.md`
e no `LUIS.md`, não achou, **definiu os três prefixos que usou e declarou o
significado no cabeçalho**, que é o comportamento certo diante da lacuna. Mas é por
isso que as quatro leituras escrevem código de quatro modos, e foi disso que saíram
os consertos de hoje no `montar_levantamento.py` e no `enderecos_em_lote.py`.

**Os três ficam registrados e nenhum é consertado agora**, para não trocar
ferramenta no meio de duas rodadas em curso. O terceiro é o que vale mais: fixar a
convenção nos prompts torna desnecessária metade da tolerância que os programas
ganharam hoje.


---

## 10/09/2026 — Seis mudanças para a relevância, e a régua que as confere

**O caso que motivou.** Pedido do orientador: os relatórios devem otimizar a
relevância dos achados para o aluno (o que muda abordagem, conclusão ou
alcance), e não o número deles. Tentativas anteriores com o Opus não tinham
surtido efeito. Diagnóstico de uma crítica fria dos prompts, no mesmo dia: o
critério de relevância existe na triagem e não manda, porque entra no último
passo, depois de leituras instruídas a produzir volume; o aparato de medição
mede precisão, cobertura e custo, e nenhuma ficha deste arquivo tinha fração de
relevância como falsificador.

**A régua, escrita antes de qualquer mudança.** `prompts/CLASSIFICAR-RELEVANCIA.md`
e `scripts/relevancia.py` (autoteste com controle positivo: falta, sobra e
caridade). **Linha de base, medida em 10/09/2026** sobre o relatório Alberto v4 da
dissertação de 08/09, com a origem apagada, por voz que não o escreveu:

| | itens |
|---|---|
| pedem providência | 75 |
| mudam conclusão | 6 |
| mudam alcance | 4 |
| só tornam conferível | 9 |
| não mudam nada | 56 |

**Relevantes: 10 de 75 (13%). Superfície: 56 de 75 (75%).** O cotejo cego de
08/09 dera 50 de superfície em 91 com outra régua; concorda em ordem de
grandeza, e está em `AFERICOES.md`.

**Origem de todas as seis: raciocínio, autorizado pelo orientador.** Nenhuma
rodou ainda. Cada uma tem o falsificador escrito aqui, antes de rodar.

| passo | arquivos | o que se espera | o que mostraria que foi inútil | rodou? |
|---|---|---|---|---|
| 1. porta de entrada: todo item nasce com a afirmação que muda, ou marcado ACABAMENTO | leituras 1, 2 e 3; `6-TRIAGEM` (teste com magnitude; graus 3 e 4 ao anexo); `ALBERTO` | a fração de superfície no corpo cai abaixo de um terço, sem perder item de conclusão | sobre a mesma dissertação, superfície no corpo continua acima de um terço, ou os itens de conclusão caem de 6 | não |
| 2. as decisões abrem o relatório | `6-TRIAGEM` (tabela de seções, seis seções, parágrafo da ordem); `ALBERTO` (nove partes, parte 2) | 3 a 6 decisões, e o pareamento com os comentários do orientador sobe de 2 (capítulo 6 da dissertação de 07/09) | decisões em número maior que seis, ou pareamento continua em 2 | não |
| 3. exceção ao desenho, com inferência e decisão junto | `VEREDITO`, leitura 3 (4c), `ALBERTO` | item de desenho aparece com a inferência nomeada e o degrau de custo | nenhum item de desenho aparece, ou aparece sem inferência nomeada | não |
| 4. o Alberto perde a operação | `ALBERTO` (7.391 palavras, de 10.822); `OPERADOR-ALBERTO.md` novo (4.340); `gerar_agente.py` concatena os dois; `gerar_warat.py` acompanha o corte; `analisador.html` recebe o prompt novo | previsão escrita antes: abaixo de 4.000 palavras. **Não se cumpriu**: ficou em 7.391, porque o que sobrou é análise e os casos de calibragem ficaram por decisão | a rodada perde o achado principal que a versão longa dava (o denominador do Gráfico 25 na dissertação de 07/09) | não |
| 5. Selma: condições e frente a cortar abrem; dimensão 5 e composição da lista vão ao bloco final, sem nota | `prompt_selma.md` (seis blocos); página regenerada; `conferir_molde.py` aceita | a lista de condições não muda de conteúdo entre as duas versões sobre o mesmo projeto | a lista de condições muda, o que indicaria que a forma decidia o mérito | não |
| 6. Miro, projeto colado: as quatro perguntas na ordem do que mudaria mais; a segunda consistência devolve primeiro o que muda mais | `contextos/modulo_2_planejamento.py`; portátil e página regenerados por `atualizar_portatil.py` | a conversa simulada começa pela pergunta que mais mexe nos outros elementos, e pula a que o texto já responde | as quatro saem na ordem fixa, ou abre turno sobre elemento que já se sustentava | não |

**Três coisas que este dia deixa pendentes, e não são executadas aqui.** A
pergunta da unidade contada tem três rodadas prometidas na ficha de 08/09 e
nenhuma rodou; fica suspensa até que a porta de entrada seja medida, porque as
duas mudam o mesmo prompt. O anexo passou a ter duas listas, e
`anexo_do_alberto.py` e `montar_entrega.py` ainda leem uma: quem montar a
próxima entrega confere se os itens de grau 3 chegam à margem. E o falsificador
do plano inteiro, escrito antes do primeiro passo: se depois dos passos 1 e 2 a
fração de superfície cair e o pareamento com o orientador não subir, o
instrumento passou a esconder o irrelevante sem achar o relevante, e a fila
seguinte é o índice do acervo do grupo.

**Sem commit.** Tudo isto está na árvore de trabalho, junto com as alterações de
09/09 que também não tinham commit. A crítica fria de `CRITICA-DE-MUDANCA.md`
rodou sobre o diff isolado das mudanças de hoje, e o que ela devolveu está
registrado abaixo desta ficha.

### O que a crítica fria de 10/09 devolveu, e o que se fez

Rodou sobre o diff isolado das seis mudanças, com os prompts inteiros e o
relatório X classificado como caso concreto. O que ela derrubou, e o destino de
cada coisa:

- **A porta de entrada era binária e mandava ao acabamento o que só torna
  conferível** (o denominador ausente, a base não depositada) **e a promessa não
  cumprida** (o produto anunciado e ausente, que o próprio prompt chama de achado
  mais consequente). *Corrigido:* a porta passou a ter três saídas (a afirmação
  muda; fica igual e passa a ser conferível, marca CONFERE; nada muda, marca
  ACABAMENTO), com a promessa não cumprida nomeada como afirmação que cai e com a
  regra do denominador escrita. No Alberto, a primeira linha é o título do item.
- **O grau 3 ia ao anexo e ao corpo ao mesmo tempo** (ano divergente na obra que
  sustenta premissa). *Corrigido* no Alberto e no operador: vai para a primeira
  lista do anexo.
- **A definição de ANEXO na triagem excluía o que a triagem manda ao anexo.**
  *Corrigido:* o destino descreve as duas listas, e a saída diz em qual.
- **"Nunca contra o desenho" e a porta ficaram lado a lado**, em três arquivos, e
  a triagem manteve o "nunca" sem exceção. *Corrigido* nos quatro lugares, e o
  registro histórico do `VEREDITO.md` diz que a formulação voltou e por que porta.
- **A exceção mandava o item "às decisões", que não recebem item e têm teto de
  seis.** *Corrigido:* o item fica nas correções com o código; a decisão que ele
  pede entra na seção das decisões.
- **A exceção derrubava o item de desenho em que a leitura não sabe se a base
  registra a variável** (S14 do caso). *Corrigido:* onde não souber entre
  integrar e coletar, escreve os dois degraus e o que decide.
- **O código do item que migra ao anexo tinha três regras.** *Corrigido:* na
  primeira lista o item conserva o código `S`; na segunda abre com `SC`.
- **"Cinco seções" a dezesseis linhas de "seis".** *Corrigido.*
- **Miro: a pergunta que o texto já responde contradizia a regra de que seção
  cheia não é elemento resolvido.** *Corrigido:* só não se repete a pergunta cuja
  resposta se sustenta diante dos outros três elementos.
- **Selma: o bloco final dizia "não muda o projeto" e a dimensão 5 diz que as
  marcas o enfraquecem.** *Corrigido:* o bloco diz o que não muda (o que o
  projeto pergunta e como responde) e mantém o custo diante da banca. E o
  tamanho anunciado ("uma ou duas páginas") passou a duas ou três.
- **Legibilidade do Alberto sozinho:** "daí uma consequência" sem antecedente,
  "segundo tipo de defeito" sem tipologia, "não remete a arquivo nenhum" seguido
  de dois arquivos. *Corrigido* nos três pontos.
- **`montar_entrega.py` descrevia o anexo como só acabamento.** *Corrigido* na
  frase impressa; o programa continua lendo uma lista, e separar as duas na
  margem fica pendente.
- **Repetições:** a porta em quatro cópias, o filtro da leitura 2 dito duas
  vezes, a justificação da ordem em dois arquivos. *Corrigido em parte:* o filtro
  da leitura 2 virou um bloco só, a defesa da ordem saiu do Alberto e da triagem
  e a glosa "isto não é teto" ficou numa frase. A porta continua em quatro
  arquivos por decisão: cada prompt de leitura roda sozinho e não pode remeter a
  outro.

**O que a crítica derrubou e fica, com a divergência registrada.** O falsificador
do passo 1 mede o que a regra manda escrever: a leitura passa a nomear a
afirmação, e o classificador decide pelo que o item nomeia. *Feito em parte:* o
classificador ganhou a regra de conferir que a providência muda a afirmação, e não
só a nomeia. O que resolve de vez é a segunda perna, que já estava na ficha: o
pareamento com os comentários do orientador, que não depende da redação do item.
Nenhuma medição de relevância se reporta sem as duas.

**O que a crítica não pôde rodar:** as decisões (o relatório X não tem a seção),
a Selma e o Miro (sem caso concreto no material). Ficam com os falsificadores da
ficha, e sem rodada.

**Tamanho, medido por ela:** o Alberto que o chat recebe caiu de 10.816 para
7.389 palavras; Alberto mais operador somam 11.729, ou 913 a mais que o arquivo
único. A previsão de 4.000 errou por 3.389, e o que ficou é análise por escolha.


---

## 10/09/2026 (tarde) — O item nasce na forma final, e o percurso sai do produto

**O caso.** O orientador apontou que muitos apontamentos, no Alberto e na Selma,
não se entendem: são reflexão da voz de leitura sobre os próprios critérios, e
não comentário operacional ao estudante. Medido no mesmo dia, no levantamento cru
de uma tese (25.793 palavras, antes de qualquer verificação): zero linhas abrem
por verbo de operação, e a voz fala do próprio prompt ("o passo 1 do prompt
manda..."). No relatório entregue da mesma família, depois da revisão cara, 3
itens em 91 têm essa voz. A diferença é a redação, que é a passada medida com
oito e nove afirmações falsas.

**Diagnóstico.** O desenho manda as primeiras vozes escrever em linguagem de
análise (términos, estados, hipóteses caídas) e delega a escrita para o aluno a
uma voz que não viu o material. As regras de honestidade (hipótese caída, alcance,
controle) estão escritas como coisas a dizer, e a voz as diz no produto.

**Origem: raciocínio, autorizado pelo orientador.** Ele recusou o teste prévio
que eu propus (uma leitura 2 em dois braços, 45 minutos) e mandou implementar.
Nenhuma rodada ainda.

| movimento | arquivos | o que se espera | o que mostraria que foi inútil | rodou? |
|---|---|---|---|---|
| o item nasce na forma final (título, aponta, o que fazer, o que muda) na primeira voz; prefixos fixos `A`, `P`, `D`; a redação ordena e nunca reescreve; item com defeito volta à leitura | leituras 1, 2 e 3 (seção de saída); `6-TRIAGEM` (redação) | `COMPREENSIBILIDADE.md` sobre os itens crus passa de dois terços, e a redação deixa de introduzir afirmação falsa | itens crus abaixo de dois terços, ou afirmação falsa nova na redação sem que ela tenha reescrito | não |
| dois arquivos por leitura: `LEITURA-<x>.md` com os itens, `REGISTRO-<x>.md` com o percurso; a tabela de figuras vai ao registro e é ele que `base_das_figuras.py` recebe; o Alberto ganha registro à parte (agente) ou bloco final (chat) | leituras 1, 2 e 3; `5-VERIFICACAO`; `ALBERTO` | nenhum item cita término, estado, hipótese caída ou controle | a voz da leitura reaparece nos itens crus | não |
| Selma: a conta sai da prosa para o bloco de dados, e a fronteira entre 6 e 7 vai a um bloco curto antes dos dados | `prompt_selma.md` | a avaliação analítica sem parágrafo sobre a régua | a régua reaparece na avaliação, ou o lote recusa o bloco novo | não |

**Confundidor declarado:** entra na mesma rodada que a porta de entrada da manhã,
que toca as mesmas seções. Os dois efeitos não se separam nessa rodada.

**Falsificador comum, escrito antes:** rodar `COMPREENSIBILIDADE.md` sobre os
itens crus da leitura, e não só sobre o texto da margem. Linha de base: hoje, zero
linhas do levantamento abrem por verbo de operação.

**Pendências que isto cria:** `montar_levantamento.py` continua lendo os
`LEITURA-*.md` e renumerando colisões, e agora os prefixos são fixos; a
convenção pendente de 08/09 fica resolvida nos prompts e o programa pode
simplificar. A leitura 4 lê contribuição não reivindicada nos mesmos arquivos,
com os prefixos `AC`, `PC`, `DC`. O operador passa a `base_das_figuras.py` o
`REGISTRO-DADOS.md`, e não o `LEITURA-DADOS.md`.


## 10/09/2026: revisão Codex, implementação autorizada

Antes das alterações: corrigir a interpolação de percentuais, completar o contrato da leitura 4 e permitir revisão de linguagem com reconferência das alterações de conteúdo. Priorizar as inferências antes das contas; separar compreensão, veracidade e utilidade. Hipóteses pedagógicas ainda não medidas. Meta técnica: zero falhas nos controles de percentuais e zero divergências dos derivados. Meta experimental: em comparação cega sobre o mesmo trabalho, aumentar a proporção de itens compreendidos sem aumentar afirmações falsas nem perder decisões úteis confirmadas na fonte. Se isso não ocorrer, a alteração não demonstrou benefício. Comentários do orientador são comparação complementar, não catálogo completo de achados. Miro fora do escopo.


---

## 12/09/2026 — A varredura: sai o viés de contar divergências, entra a medida central

**O caso, e ele está no acervo.** Na dissertação sobre desobediência judicial, o
orientador leu o trabalho inteiro e diz que a questão que mais importa é se contar
decisões de procedência em reclamação mede desobediência, ou outra coisa (a
capacidade do sistema de precedentes de interferir; a ampliação das teses pela
própria Corte). O relatório do Luis chegou a essa pergunta (a decisão D5 pergunta
se o crescimento das procedentes mede a desobediência ou a disposição do STF em
acolher) e a enterrou como quinta decisão, atrás de um veredito sobre resumo e
anexo e de cinco pontos fortes que dizem que as somas das tabelas fecham. O do
Alberto abre dizendo que refez as onze colunas célula a célula. A ferramenta viu e
o formato escondeu.

**Diagnóstico.** Os prompts cristalizam a contagem de divergências como o trabalho
principal: recontar bases por dois caminhos, refazer somas e porcentagens, comparar
dígito a dígito, contar percentuais sem denominador, cinco estados por figura, seis
modos de a prosa falhar contra a tabela, a ementa como tabela de términos, e o
ponto forte como conta que fecha. Nada disso pergunta o que a contagem conta.

**Origem: pedido do orientador, sem teste prévio por decisão dele.** Nenhuma rodada.

**O que saiu:**

- Leitura 1: o passo que media o alcance do resumo em três números; a lista de
  alvos como produto (vai ao registro); o superlativo da divergência de alcance.
- Leitura 2: o passo das referências por amostra (é programa e é anexo).
- Leitura 3: os cinco estados por figura (ficam duas perguntas: o que o texto
  extrai além do que a figura permite, e o que ela permite e o texto não afirma);
  os seis modos de a prosa falhar (fica a divergência que muda o que a seção
  conclui); a repetição dígito a dígito; a célula que ninguém comentou; a tabela
  de figura obrigatória para todas (fica para as de que a conclusão depende);
  três parágrafos de medição com chamadas e minutos.
- Alberto: três padrões da lista (número só na figura, citação sem entrada, duas
  contagens que não fecham); o superlativo do passo 2; a narrativa de medição das
  três perguntas.
- Triagem e redação: a ementa como tabela de términos (passa a dizer o que o
  trabalho mede, o que conclui, o que não se sustenta e as decisões); "a linha mais
  informativa"; a conclusão julgada pela tabela de términos.
- Veredito e Alberto: no trabalho descritivo, confere-se a descrição apresentada
  como resultado, e número trocado que não a muda é anexo.
- Metáforas: "fóssil" vira "versão velha" nas três leituras; "irrigando" vira
  "alimentando"; na Selma e no Miro, "consome e entrega" vira "parte de e
  entrega" (no Miro só a palavra, porque ele está fora do foco).

**O que entrou:**

- **A medida central como primeira pergunta**: o que a contagem conta, que
  conceito o trabalho diz que ela mede, que outras coisas o mesmo número pode
  medir. Na leitura 3 é o passo 0; no Alberto abre o exame da inferência; na Selma
  entra na validade do indicador. As leituras alternativas entram como pergunta
  ainda que o trabalho não as mencione, e isso é exceção declarada à regra de não
  inventar explicação.
- **Um quinto modo de a inferência extrair demais**: o conceito diz mais do que a
  contagem conta. Nas leituras 1 e 3 e no Alberto.
- **Ponto forte não é conta que fecha**: na triagem e no Alberto.

| o que se espera | o que mostraria que foi inútil | rodou? |
|---|---|---|
| sobre a dissertação da desobediência, a medida central aparece como primeira decisão, com as leituras alternativas e o que as separaria | a pergunta continua atrás de itens de contagem, ou não aparece | não |
| os pontos fortes deixam de ser somas que fecham | metade ou mais dos pontos fortes continua sendo conta que fecha | não |
| o corpo do relatório perde os itens de divergência que não mudam conclusão | a fração NADA do classificador não cai | não |

**O que não saiu, e por decisão:** o desconto dos dois lados de uma subclasse, a
composição da unidade contada e o nome da série, porque nos casos medidos mudaram a
afirmação central; as três guardas sobre teste de significância; a régua de notas
da Selma, que conta achados e não divergências, e tem razão medida (duas leituras do
mesmo projeto divergiam em dois pontos sem ela).

**Confundidor:** entra na mesma rodada que a porta de entrada e a forma final, que
tocam as mesmas seções.

### O que a crítica fria de 12/09 devolveu, e o que se fez

Rodou sobre os diffs de 10/09 (tarde) e 12/09, com os prompts inteiros e o
relatório do Luis sobre a dissertação da desobediência como caso. Ela cobriu as
duas levas porque a de 10/09 (tarde) caiu por limite de uso.

**O que ela derrubou, e o destino de cada coisa:**

- **A regra passava no caso porque o caso estava transcrito nela.** O exemplo da
  medida central nomeava reclamações procedentes e desobediência, em três prompts
  e na Selma, contra a regra de 05/09 (exemplo do domínio volta como citação).
  *Corrigido:* exemplo genérico (o evento que uma instituição registra pode medir
  o fenômeno, a disposição de registrá-lo, ou a mudança do critério).
- **O item da medida central tinha dois destinos incompatíveis** (pergunta, e ao
  mesmo tempo primeira decisão), e a verificação o derrubaria como não
  conferível. *Corrigido:* é item de corpo com a pergunta dentro; a verificação
  ganhou a trava de que ele não cai por o trabalho não mencionar a alternativa.
- **Nenhuma regra ordenava as decisões**, e foi por isso que a pergunta ficou em
  quinto. *Corrigido:* a ordem é a do que mais muda, e a da medida central vem
  primeiro (triagem, Alberto, veredito).
- **O molde do veredito pedia "o número que sustenta"**, que é a soma refeita.
  *Corrigido.*
- **"A contagem central" era ambígua com duas contagens.** *Corrigido:* é a que a
  afirmação principal usa; com duas, faz-se para as duas.
- **Na leitura 1 o quinto modo não alcançava a passagem**, porque a leitura do
  dado como fenômeno caía em RETOMADA. *Corrigido:* retomada que já lê o dado
  como o conceito é TESE.
- **"Quatro modos" com cinco itens, carimbados como medidos.** *Corrigido* nos
  três arquivos: cinco, e o quinto entrou por pedido, sem medição. A
  justificação repetida seis vezes saiu dos itens de lista.
- **Duas contagens do mesmo conjunto que não fecham** produziu a condição 3 do
  veredito no caso, e tinha saído. *Voltou, condicionada* a uma afirmação usar
  uma das contagens como universo.
- **Figura que repete outra** era o caso medido de REDUNDANTE. *Voltou,
  condicionada* ao texto tratar a repetição como confirmação.
- **O passo das referências da leitura 2 saiu inteiro**, e o pipeline não nomeia
  quem roda o programa. *Voltou reduzido* à referência de que uma premissa
  depende.
- **"A linha mais informativa"** sobrevivia na saída da triagem; **"a contagem por
  estado do passo 2"** sobrevivia no registro da leitura 3 depois de os estados
  saírem; **dois inventários de figura** com alcances diferentes; **o passo 0
  mandava ler o trabalho antes das figuras e o 2b mandava não ler**; **frase
  quebrada** sem ponto em dois arquivos; **o exemplo de mérito** da redação era
  exatamente o que a regra nova desqualifica; **o degrau 4 do veredito** ainda
  admitia "muitos" ou "tempo que não cabe". *Todos corrigidos.*
- **A página das figuras não dizia que a cobertura encolheu.** *Corrigido* no
  aviso e no rodapé de `base_das_figuras.py`.

**O que fica, com a divergência registrada:** a pergunta da unidade contada em
três lugares da leitura 3 (passo 0, guarda do passo 3, pergunta 2 do 4b). São
três operações vizinhas e não uma; fundir pede medir qual delas produz o item, e
isso não foi feito. E a redundância entre leituras, que a varredura reduziu (a
leitura 3 deixa de comparar figura que a conclusão não usa; a leitura 1 continua
comparando resumo contra tabela): a rede ficou com menos fios por decisão do
orientador, e o que mostraria o custo é um achado de resumo contra tabela que a
leitura 1 não pegue.

**Alcance da crítica:** os prompts inteiros e os dois diffs; a dissertação não foi
lida, e onde a resposta dependia dela a crítica disse que não decidiu. As duas
alternativas nomeadas pelo orientador (capacidade do sistema de precedentes de
interferir; ampliação das teses) entram pela regra do passo 0 só por vizinhança:
uma é leitura do conceito, a outra é mecanismo do crescimento. A regra cobre o
conceito; o mecanismo continua coberto pela lista do que mudou na janela.

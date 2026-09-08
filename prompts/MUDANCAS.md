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

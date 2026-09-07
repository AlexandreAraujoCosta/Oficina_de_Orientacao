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

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

## O material

- `MAPA.md` — legendas de todas as figuras, quadros e tabelas, com página, mais o
  resumo, a introdução e a conclusão. Leia primeiro, e use as legendas para escolher
  as páginas.
- `trabalho.pdf` — **leia as figuras e tabelas na imagem.** Elas são o objeto desta
  leitura, e a extração em texto achata coluna e embaralha célula. Até seis chamadas
  de leitura de imagem.
- `extracao/trabalho.txt` — para achar, com `Grep`, o parágrafo em que cada figura é
  discutida.

## Passo 1 — reconstituir as bases, e é o controle de tudo o que vem depois

Antes de qualquer análise: **quantos casos há em cada grupo comparado?** Reconstitua
os totais a partir das figuras, **por dois caminhos independentes** (por exemplo, a
soma por classe e a soma por tipo), e confira se fecham.

Se não fecharem, pare e reporte isso: é o achado, e todo o resto herdaria o defeito.
Se fecharem, **verifique se esses totais aparecem no texto**. Caso medido: uma
dissertação comparava dois regimes e a base menor tinha 285 casos, número que não
aparecia em lugar nenhum do texto, de modo que nenhum percentual da seção era
conferível pelo leitor.

## Passo 2a — as figuras sozinhas, antes da prosa que as comenta

**Este passo vem antes do 2 e é cego de propósito.** Ler a figura depois do texto é
conferir o que o texto disse; ler antes é ver o que a figura permite. A diferença
entre as duas leituras é o achado.

Rode `python scripts/figuras_do_docx.py <trabalho.docx> --extracao <extracao.txt>`,
que tira as imagens de `word/media/`, casa cada uma com a legenda vizinha e com o
`[P###]` do parágrafo em que ela está, e diz qual arquivo carrega o dado. Onde ele
disser que não sabe qual carrega, peça todos os arquivos daquela figura. **Depois peça as imagens numa mensagem só**, várias por
mensagem. Duas coisas justificam isso, e as duas foram medidas em 06/09/2026: a
restrição de chamada paralela é da leitura de *página de PDF* e não de arquivo de
imagem, de modo que seis imagens pedidas juntas voltaram as seis; e a imagem do
`.docx` vem como o autor a inseriu, com os rótulos de dado legíveis um a um,
enquanto a página de PDF vem reduzida. Onde só houver PDF, a leitura é página a
página e sequencial.

De cada figura, **sem abrir ainda a prosa que a comenta**: o que ela mostra; o que
ela **permite afirmar**, incluindo a conta que ela permite e não rotula (soma das
barras, razão entre categorias, complemento de um percentual, normalização de
faixas de largura diferente); o que ela **não** permite (o denominador, a unidade
contada, o critério de inclusão); e o que só o texto poderia dizer.

**E diga, de cada figura, quando ela não permite item nenhum.** Tela de portal,
diagrama conceitual e tabela de definições não sustentam afirmação empírica. Se
todas as figuras renderem achado, o passo está fabricando, e é isso que esta guarda
existe para pegar.

Medido em 06/09/2026, sobre treze figuras de uma tese, tendo como controle a leitura
das mesmas figuras feita com a prosa ao lado: o passo cego devolveu cinco achados
que ela não tinha, entre eles duas faixas de largura diferente tratadas como iguais
no eixo e uma comparação de contagens brutas entre relatores com tempos de exercício
muito diferentes. Recusou três das treze. Custou cinco minutos.

## Passo 2 — cada figura, contra o que o texto extrai dela

Agora sim com a prosa ao lado, e **o que você anotou no passo 2a não se apaga**: a
diferença entre o que a figura permite e o que o texto extrai dela é a matéria deste
passo. Para cada figura, quadro e tabela: o que ela contém, o que o texto tira dela,
e qual destes cinco estados descreve a relação.

- **BEM USADA** — o texto extrai o que ela sustenta.
- **SUBEXPLORADA** — o texto extrai menos do que ela permite: afirma sem o
  denominador, compara sem o intervalo, enuncia ausência sem o teste.
- **INEXPLORADA** — a figura permite uma afirmação que o texto nunca faz. **É o
  achado que esta leitura existe para produzir.**
- **REDUNDANTE** — é transformação aritmética de outra figura. Confira dígito a
  dígito antes de afirmar. Caso medido: um gráfico era, dígito por dígito, a terceira
  série de um gráfico anterior, e as duas seções que os comentavam analisavam a mesma
  variável.
- **CONTRADIZ** — a figura sustenta o contrário do que o texto afirma dela, ou do que
  o trabalho afirma noutro ponto.

**O inventário tem uma coluna que vale mais que as outras:** o que esta figura permite
afirmar que ninguém afirmou. É dela que sai a seção do relatório sobre o que o
trabalho tem e não reivindica, e ela mora em três lugares que só o conjunto revela.

**A célula que ninguém comentou.** A tabela tem mais células do que a prosa usa.
Percorra as que sobraram.

**O cruzamento que não foi feito.** Não está em figura alguma: aparece como buraco no
conjunto. Monte a matriz do que foi cruzado com o quê e olhe as células vazias. Só
conta o que responderia a uma pergunta que o próprio trabalho levanta.

**A série que só vira achado contra referência externa.** A prosa comenta um ano por
vez e nunca reúne a série. Reúna, e veja se algum valor destoa de um modo que peça
explicação.

Para cada um, o número calculado, de que figura sai, e o que muda. **Sem o número, o
item vira sugestão vaga e não serve.**

## Passo 2b — a narrativa da tabela contra a tabela

É onde os defeitos de maior impacto se concentraram nas medições, e onde a tabela
costuma estar certa e a prosa errada.

**A ordem é regra, e não é figura por figura.** Leia **todas** as figuras e tabelas
primeiro, sem ler um parágrafo do trabalho, e monte um inventário seu: por figura, o
que mede, as categorias, as colunas, a base de cada percentual e os valores, com as
suas palavras.

Três coisas dependem dessa ordem.

**A prosa lida antes faz ler a figura pelos olhos dela**, e a alternância contamina
cada figura com o parágrafo da anterior.

**Repetição entre figuras distantes só aparece com as duas à vista.** Uma figura que é,
dígito a dígito, série de outra fica a dezenas de páginas dela, e alternando a
coincidência passa. Compare o inventário consigo mesmo antes de abrir o texto.

**A estrutura do aparato só se vê com tudo na mesa**: quantas variáveis foram
coletadas, o que foi cruzado com o quê, e sobretudo o que nunca foi cruzado. É daí que
sai o passo 4.

Depois compare, frase a frase. Seis modos de falhar, todos medidos:

- **Coluna trocada.** A contagem lida como percentual: onde a tabela dá 19 ocorrências
  e 27,9%, o texto escreve "19% do corpus", e com o valor certo a ordenação que a
  própria frase afirma se inverte.
- **Categorias fundidas.** A tabela separa três e o texto conta duas, e a metade
  redonda que sobe ao resumo depende dessa fusão.
- **Linha agregada no lugar da condicional.** O texto afirma que o padrão vale "em
  ambos os casos", e na linha do subgrupo a ordem das estratégias se inverte.
- **Nível lido como tendência**, ou o contrário: o gráfico mostra a inclinação e o
  texto extrai o patamar.
- **Repetição.** Uma figura é, dígito a dígito, uma série de outra. Confira antes de
  afirmar, e diga em que arenas ou recortes a coincidência vale.
- **O que interessa e não foi lido.** A tabela permite o cruzamento que decidiria a
  questão do capítulo, e o texto não o faz.

Para cada divergência: o que a tabela dá, o que o texto diz, e **o que muda na
conclusão da seção com o valor certo.**

## Passo 3 — refazer as contas

**Não confie no número impresso: recalcule.** Some as colunas e refaça as
porcentagens.

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

**E cuidado, porque o apêndice pode ser fóssil.** Ele costuma ser a versão anterior do
procedimento, congelada quando o autor parou de olhar. Contradição entre apêndice e
corpo tem três leituras, e escolher a errada é acusar o inocente:

- o corpo está errado, e o apêndice mostra o que foi feito;
- o apêndice é fóssil, e o corpo mostra o que passou a ser feito;
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

Quando o apêndice for fóssil, **isso é item, e de outra espécie**: não é erro de conta,
é defeito de reprodutibilidade, e vai para a seção dos produtos, porque o que se
publicou não permite refazer o que se fez.

## Passo 4 — o que os dados permitem e ninguém pediu

Percorra as variáveis que o trabalho coletou e pergunte quais cruzamentos ele não
fez. Só conta o cruzamento que (a) as variáveis coletadas permitem, e (b) responderia
a uma pergunta que o próprio trabalho levanta. Não peça outra pesquisa.

Para cada resultado inexplorado, escreva: o número, como se obtém, e **o que ele
muda** no que o trabalho conclui ou no que ele poderia publicar.

## Passo 4b — três perguntas que mandam calcular

Elas vêm de uma medição de 05/09/2026 contra os comentários de margem de quem
orienta, sobre a mesma dissertação. Das doze observações dele que a leitura não
produziu, **três pediam exatamente a aritmética que ela já executava dezenas de
vezes noutros pontos do mesmo trabalho**. O que faltava era a pergunta, e não a
capacidade de fazer a conta. Faça as três em toda série e em toda comparação
temporal:

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
erro: **esta interpretação extrai mais do que o desenho permite?** Quatro modos de
extrair demais, todos vistos nesta bancada:

- **do agregado para o caso**, quando a taxa média vira afirmação sobre cada
  unidade;
- **da coincidência para o mecanismo**, quando duas séries que sobem juntas viram
  uma causando a outra;
- **do subconjunto para o universo**, quando o que se mediu num recorte é dito do
  todo, e às vezes o próprio trabalho declarou o recorte;
- **do desfecho para a intenção**, quando o que o texto faz vira o que o autor
  dele quis.

Onde a interpretação extrair demais, o item não pede que se retire a
interpretação: pede que **o alcance dela desça até onde o dado chega**, e diz até
onde. Retirar é perda; ajustar o alcance é o que a torna defensável na banca.

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
inventar, e ela não entra.

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

## Saída

Grave em `LEITURA-DADOS.md`. Devolva no texto final: as bases reconstituídas e se
fecham, a contagem por estado do passo 2, e a lista dos resultados inexplorados com o
número de cada um.

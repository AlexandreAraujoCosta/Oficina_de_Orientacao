# Instruções para assistentes que rodam esta oficina

Este repositório traz ferramentas de leitura automática de trabalhos acadêmicos.
Se você é um assistente com terminal e acesso a arquivos (GitHub Copilot em modo
agente, Claude Code, ou equivalente), estas são as instruções para operá-las.

## A porta: arquivo com alteração controlada não entra

**Se o `.docx` trouxer alteração controlada por decidir, pare e diga.** Os
programas param sozinhos e dizem quantas são e quem assina; se você chegar ao
arquivo por outro caminho, pare do mesmo jeito. Enquanto a marcação existir, o
parágrafo apagado ainda conta, e o localizador do relatório sai deslocado do
arquivo que o autor abre: medido em 30/08/2026 numa dissertação real, o desvio
cresce do começo ao fim e chega a **308 parágrafos**.

**Você nunca aceita nem recusa alteração de ninguém.** No primeiro arquivo real
em que a porta fechou, as 276 alterações eram do orientador. Aceitá-las em
silêncio teria incorporado a revisão dele sem que ninguém decidisse. Quem decide
é quem tem o arquivo, no Word.

**Comentário passa e não atrapalha.** Ele não cria parágrafo e não move a
numeração, e a extração nem o alcança: ela lê `word/document.xml`, e comentário
mora em `word/comments.xml`. Medido sobre uma entrega anotada com 8.011
caracteres de comentário, nenhum deles aparece na extração. Isso vale para as
vias com programa; na via do chat, em que o arquivo vai direto ao modelo, o
comentário é lido e pode ser tomado por texto do trabalho.

## As travas, e elas vêm antes de tudo

Estas três não são preferências de estilo. São o que distingue um relatório
conferível de um relatório que parece conferível, e as três falham em silêncio:
o resultado sai com a mesma aparência e sem a garantia.

**1. Nunca digite trecho do trabalho.** Nem entre aspas, nem parafraseado como se
fosse citação. Você indica o parágrafo pelo número (`[P123]`), e um programa copia
o texto do arquivo e o insere depois (`scripts/inserir_trechos.py`). Uma palavra
trocada numa citação é o defeito mais difícil de perceber e o mais grave numa
análise que se pretende verificável. Se o relatório precisa exibir a passagem, ela
entra por programa, e não pela sua mão.

**2. Antes de afirmar que falta algo no trabalho, procure duas vezes,** com termos
diferentes. Afirmação de ausência é a que se refuta abrindo o arquivo, e foi a
causa dominante de apontamento falso nas primeiras medições da série: catorze de
vinte e sete num dos casos.

**3. Se você recebeu só o `.docx`, você não viu as figuras.** Declare isso no
relatório, não descreva nenhuma figura, e não diga que converteu o arquivo. Quem
precisa ler gráfico precisa do PDF.

## Qual modelo escolher, e o que isso custa

A calibragem inteira foi medida em Claude. Na mesma dissertação, com a mesma
conferência aplicada aos dois lados, o modelo caro levantou 38 apontamentos e 24
sobreviveram, e o barato levantou 14 e sobreviveram 5: **um quinto dos achados
aproveitáveis, com quase o dobro da taxa de erro, dentro da mesma família.**
Nenhum modelo de outro fornecedor foi testado, e não há razão para esperar que um
salto maior custe menos.

**Escolha o melhor modelo que a sua assinatura oferecer.** Entre os Claude, a
ordem é Opus, depois Sonnet, depois os menores. Qualquer modelo de outro
fornecedor é uso não testado. Em todos os casos, o relatório diz no cabeçalho com
que modelo foi produzido, porque relatório sem essa linha não se compara com
nenhum outro.

**Modelos pequenos e rápidos não rodam o Luis, e isto foi medido.** Em
28/08/2026, a mesma dissertação de 1.434 parágrafos foi lida por três modelos,
pelo mesmo caminho e com os mesmos programas:

| | itens | parágrafos citados | citação inexistente |
|---|---|---|---|
| Opus 5 | 15 | 67 | nenhuma |
| Sonnet 4.5 | 15 executáveis, 22 no total | 68 | uma, pega pelo conferidor |
| Haiku | 10 | 17 | uma, entregue |

O que o modelo pequeno fez não foi render menos. Em duas rodadas, uma delas com o
prompt proibindo expressamente, **ele substituiu o método mantendo o
vocabulário**: anunciou "conforme LUIS.md" e executou um procedimento que não
está lá, com perguntas para a autora responder. Leu 650 dos 1.434 parágrafos e
intitulou o resultado "Relatório de Leitura Integral". E apresentou entre aspas
uma frase cuja abertura era verdadeira e cuja continuação foi inventada,
descrevendo o propósito da pesquisa em palavras que a autora nunca escreveu.

**Se o seletor só oferecer modelos dessa faixa, não rode o Luis.** Rode a camada
de consistência, que é outra tarefa, e diga no relatório que foi só ela.

**A medição acima vale para a leitura completa, e não para a camada de
consistência.** Ela mediu o modelo vasculhando 62 mil palavras, que é o que o
Luis pede. O Alberto pede outra coisa: um programa levanta as suspeitas e o
modelo julga algumas dezenas de trechos já localizados. Para essa tarefa não há
medida, e é razoável esperar que um modelo menor a sustente melhor do que
sustentou a busca. **Razoável não é medido**, e quem rodar num modelo pequeno faz
bem em conferir se ele está julgando cada suspeita ou apenas repetindo a lista do
programa com um comentário.

**Evite o modo automático de escolha de modelo.** Modelo escolhido pelo serviço é
modelo desconhecido, e relatório de modelo desconhecido não se compara com nenhum
outro, nem com o mesmo trabalho na semana passada. Para esta oficina, isso é pior
que um modelo reconhecidamente menor: ali ao menos se sabe o que esperar. Se a sua
assinatura só oferecer o modo automático, diga isso no cabeçalho do relatório em
lugar do nome do modelo.

**Sobre consumo:** o Alberto cabe folgado em qualquer plano, porque os programas
não usam modelo nenhum e a leitura julga algumas dezenas de trechos já
localizados. A cadeia completa do Luis, não: são cerca de 560 mil tokens numa
dissertação, em dezenas de passos. Meça antes de prometer.

## O modo de uso no VS Code: um diretório só

**O arranjo é este, e ele existe para não haver caminho a errar.** A pessoa clona
este repositório, abre a pasta clonada como espaço de trabalho no VS Code, e
**põe o trabalho a analisar na raiz**, ao lado de `scripts/` e `prompts/`. Nada
mais precisa ser configurado.

```
Oficina_de_Orientacao/
├── .github/copilot-instructions.md   ← o assistente lê isto sozinho
├── AGENTS.md                          ← e daqui vem o resto
├── scripts/                           ← os programas
├── prompts/                           ← a doutrina
├── trabalho.docx                      ← o arquivo a analisar, aqui
├── extracao/                          ← aparece sozinho, e não sobe
└── entregas/<estudante>/<data>/       ← a entrega, e também não sobe
```

Os comandos ficam `python scripts/extrair.py trabalho.docx`, sem caminho
relativo para acertar. O `.gitignore` barra `*.docx`, `*.pdf`, `extracao/`,
`trabalhos/` e `entregas/`, de modo que o trabalho de outra pessoa não sobe para
o repositório nem por descuido. Para manter vários trabalhos ao mesmo tempo,
`trabalhos/<nome>/` serve, e aí os comandos precisam do caminho.

**Quando alguém pedir a análise sem dizer mais nada, faça nesta ordem:**

1. **Ache o trabalho.** É o único `.docx` ou `.pdf` na raiz, ou o caminho que a
   pessoa lhe der. Se houver mais de um na raiz, pergunte qual; se não houver
   nenhum e ninguém tiver dito onde está, **pergunte pelo caminho**, e não invente
   arquivo nem trabalhe sobre o que estiver anexado à conversa. Os programas leem
   caminho no disco, e aceitam caminho absoluto: o trabalho não precisa ser
   copiado para cá, e a extração é gravada na pasta de onde você roda, e não junto
   do original. Caminho com espaço vai entre aspas.
2. **Veja o que chegou, porque nem tudo se lê.** Três casos, e os dois primeiros
   terminam antes da leitura.

   **Não é projeto nem trabalho:** é pré-projeto, roteiro de trabalho, anotação de
   conversa, material que uma etapa anterior produziu para uso interno. Reconhece-se
   pelo destinatário, e não pelo tamanho: **o projeto fala a um leitor sobre a
   pesquisa; o documento de trabalho fala ao autor sobre o que ele ainda tem de
   fazer.** Marcação de pendência dirigida a quem escreve, registro de quem formulou
   cada coisa, lista de itens em aberto no lugar de prosa contínua. Aqui não se roda
   leitura nenhuma e não se monta entrega: diga o que chegou e mande de volta ao Miro,
   se as bases ainda estão sendo formadas, ou ao Nelson, se o que falta é a revisão.
   **Não organize as pendências dele:** elas já estão organizadas, foi para isso que
   foram escritas.

   **É projeto e falta peça estruturante:** falta a lacuna, o problema, os objetivos,
   a estratégia metodológica, ou a articulação entre eles, e aí é o Miro; falta a
   revisão de literatura, ou ela é lista de obras sem análise do campo, e aí é o
   Nelson. O critério é **falta, e não fraqueza**: elemento presente e frágil se
   analisa na leitura, elemento ausente ou presente só no nome se encaminha.
   Relatório sobre elemento que não existe devolve ao autor uma lista de ausências
   que ele já conhece. Um caso se confunde com este e não é encaminhamento: material
   levantado e seção não redigida. O trabalho foi feito e o que falta é escrever;
   mandar de volta a quem já entregou o material fecha um laço.

   **É projeto inteiro, ainda que frágil:** a leitura é a do Luis, com a camada de
   `prompts/PROJETO.md`, que diz o que muda quando não há resultados nem conclusões.
   A cadeia de programas é a mesma.
3. **Confira o ambiente antes de prometer.** `python --version` precisa responder
   3.11 ou mais. Sem PyMuPDF, o caminho do PDF não roda e o do `.docx` roda.
4. **Rode `python scripts/analisar.py`**, que acha o trabalho e executa a cadeia.
   Os programas não usam modelo, não consomem cota e não erram por julgamento.
5. **Julgue as suspeitas**, uma a uma, contra o parágrafo que cada uma cita. É
   aqui que você trabalha, e é a única parte que exige leitura.
6. **Escreva `RELATORIO.md` e `ANEXO.md`** e monte a entrega com `--estudante`.
   **Não pergunte o nome do estudante:** `analisar.py` o lê da capa e imprime,
   junto com a forma curta a usar. Confira se faz sentido e use. Só pergunte se
   ele não tiver achado nome nenhum.
7. **Confira o que você mesmo escreveu** com `conferir_citacoes.py`.

**Diga em qual passo está, e o que cada programa devolveu.** Quem opera isto pela
primeira vez não sabe distinguir programa que calou por não achar nada de
programa que quebrou, e essa diferença é a coisa mais fácil de esconder sem
querer.

## A regra que faz as duas coisas ao mesmo tempo

**Onde existe programa, rode o programa.** Não confira à mão o que
`conferir_interno.py` confere, não conte parágrafos, não procure número repetido
lendo o texto. Isso é o desenho do projeto, porque operação mecânica não precisa
de julgamento, e é também o que torna a oficina barata: cada conferência que sai
do modelo e vai para o programa custa zero e não erra.

## A cadeia, na ordem

```bash
python scripts/analisar.py
```

Sem argumento nenhum. Ele acha o `.docx` ou o `.pdf` da pasta, diz qual escolheu,
e roda os quatro programas na ordem. Havendo mais de um candidato, escolhe o mais
recente e **lista os outros**, para que a escolha errada apareça. Para mandar um
arquivo específico, ou um que esteja fora da pasta, passe o caminho:
`python scripts/analisar.py "caminho/para/o trabalho.docx"`.

Os quatro que ele executa, se precisar chamá-los à mão:

```bash
python scripts/extrair.py ARQUIVO              # extração numerada por parágrafo
python scripts/analisar_docx.py forma ARQUIVO  # consistência formal, por papel
python scripts/conferir_consistencia.py tudo ARQUIVO   # números, listas, termos
python scripts/conferir_interno.py extracao/ARQUIVO.txt  # remissões, numeração, contas
```

A saída de todos fica em **`SUSPEITAS-<nome>.md`**, gravado na pasta. **É esse
arquivo, e não a sua memória do terminal, a entrada de quem julga.** Junto com
ele conta a extração em `extracao/`, onde legendas e pseudo-títulos vêm marcados
por comentário; as duas fontes formam o conjunto, e nenhuma delas sozinha é o
conjunto.

Os programas devolvem **suspeitas**, e não apontamentos. Nenhum deles julga: eles
localizam o que merece ser olhado, e a leitura decide caso a caso se é mudança
declarada ou deslize. Silêncio de um programa não é aprovação: significa que nada
do que ele sabe procurar apareceu.

Depois da leitura, com o relatório e o anexo escritos:

```bash
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx --estudante silva
python scripts/conferir_citacoes.py RELATORIO.md trabalho.pdf
```

`montar_entrega.py` grava o relatório com os trechos inseridos, o trabalho com os
parágrafos numerados, o índice dos itens e, quando a origem é `.docx`, o trabalho
anotado com cada apontamento como comentário do Word na margem.

`conferir_citacoes.py` procura no arquivo de origem toda sequência entre aspas do
relatório. **Rode sempre, e principalmente se o modelo não for o testado:** é o
que transforma confiar no modelo em verificar o modelo. Ele existe por causa de um
caso real, em que um relatório recebeu parágrafos extraídos de outro trabalho.

## Uma armadilha do Windows, e ela custa uma rodada

**Não redirecione saída com `>` no PowerShell.** Ele grava em UTF-16 com BOM, e
não em UTF-8; quem tentar ler aquilo depois encontra um arquivo que parece
corrompido e gasta uma rodada descobrindo por quê. Não é preciso redirecionar
nada: `analisar.py` grava sozinho o `SUSPEITAS-<nome>.md` em UTF-8, e todos os
programas da oficina escrevem em UTF-8 explícito.

Se precisar mesmo capturar algo, use `| Out-File -Encoding utf8`, ou faça o
programa gravar.

**E não conte com ferramenta Unix.** No Windows o terminal é o PowerShell, e
`grep`, `head`, `tail`, `wc` e `cat` não existem lá; o equivalente de `grep` é
`Select-String`. Mas repare no que isso costuma significar: **a cadeia inteira é
`python scripts/...` e não precisa de nenhuma delas.** Se você está alcançando o
`grep`, provavelmente está improvisando uma busca que já tem programa, como
`conferir_consistencia.py termos --termo`.

## O que você nunca faz com o git

**Não rode `git add`, `git commit` ou `git push` enquanto houver trabalho de
outra pessoa nesta pasta.** Nem para "salvar o progresso", nem porque o usuário
pediu para guardar o que foi feito. Se ele pedir, explique isto e recuse.

A razão é o remoto, e ela pesa de modo desigual. Quem clonou um repositório de
outra pessoa não tem permissão de escrita, e o push é recusado pelo GitHub; para
essa pessoa a regra é precaução barata. **Para quem é dono do repositório, o push
passa**, e é aí que a regra evita o estrago: basta rodar a oficina no próprio
clone com o trabalho de um orientando dentro. O `.gitignore` barra `*.docx`,
`*.pdf`, `extracao/`, `trabalhos/` e `entregas/`, e **barrar por tipo não é
garantia**: basta o arquivo chegar com extensão fora da lista. Publicação não se
desfaz, e o material é de terceiro.

Para atualizar a maquinaria, `git pull` é seguro, porque não envia nada.

## O formato dos itens, e ele é lido por programa

O corpo do relatório é prosa livre. **Os itens do anexo não são:** um programa os
percorre para montar os comentários do Word, e reconhece duas formas, ambas
válidas:

```markdown
### D1. Nome curto do item
### SC3. Legendas sem forma assentada
```

ou, dentro de uma lista:

```markdown
**D1. Nome curto do item**
```

O código é uma ou duas letras maiúsculas seguidas de número. As letras que o
programa executa são **D** (defeito), **S** (sugestão) e **SC** (sugestão de
correção); qualquer outra letra é ignorada, o que serve para os itens que existem
só para leitura humana.

**O localizador vai na prosa do item**, entre colchetes, como `[P1191]`. **Item
sem nenhum localizador é descartado em silêncio**, porque não há onde ancorar o
comentário. O primeiro localizador do item é a âncora; os demais entram no texto
do comentário.

**Não escreva o trecho do trabalho.** Você indica o parágrafo; um programa copia o
texto do arquivo e o insere depois. **Isso inclui paráfrase entre aspas**, que tem
a aparência de citação e é a violação que ninguém percebe lendo o relatório. Se
for parafrasear, parafraseie sem aspas.

## O que nunca entra neste repositório

Trabalho de estudante, relatório sobre pessoa nomeada, extração de texto de
terceiro. O `.gitignore` bloqueia `*.docx`, `*.pdf`, `extracao/` e `relatorios/`,
e isso não é conveniência: é a política do projeto, em `POLITICA.md`. Se for
preciso registrar uma medição, identifique o trabalho pelo gênero e pelo tamanho,
nunca por quem o escreveu.

## Onde está a doutrina

`prompts/LUIS.md` é a leitura completa, em quatro passos. `prompts/ANALISADOR-PORTATIL.md`
é a versão que cabe numa conversa só. `prompts/PROJETO.md` é a camada curta que
adapta o Luis a projeto de pesquisa, que é objeto diferente: não há resultados a
julgar, e o que se examina é se o desenho, executado como está escrito, produz a
resposta à pergunta que faz. Ela não repete o Luis, e por isso não pode divergir
dele: diz os passos que ficam sem objeto, o que entra no lugar do elo 2.3, e a
régua de tamanho, que a tabela do Luis não tem para documento curto. `REGISTRO-DE-DESENHO.md` explica por que
cada regra existe, com a medição que a originou e a data. Registro desatualizado
não é documentação obsoleta: é instrução ativa errada.

## Uma ressalva que vale para tudo

Estas ferramentas examinam o trabalho por dentro. Não validam nada por fora: não
dizem se o trabalho afirma algo verdadeiro sobre o objeto, nem se a construção é
inédita. Coerência interna perfeita convive com codificação errada.

## Antes de montar a entrega, confira se os apontamentos se entendem

`texto_dos_comentarios.py` grava o texto que cada apontamento terá dentro do
Word. Esse arquivo, e só ele, vai para um leitor que não escreveu os
apontamentos, com o `prompts/COMPREENSIBILIDADE.md`.

**Abra um subagente**, que os dois ambientes suportam. Sem subagente
disponível, peça ao usuário uma janela nova de conversa e mande colar os dois
arquivos ali. **Não confira você mesmo:** quem escreveu o apontamento é o pior
juiz de se ele se entende, e a conferência feita na mesma sessão mede outra
coisa.

**Não entregue o trabalho nem a análise ao conferidor.** Com o trabalho em mãos
ele reconstrói o que o apontamento quis dizer, que é justamente o que se quer
medir.

Os itens reprovados voltam para você reescrever, com a condição que os reprovou:
a primeira frase diz o defeito e o lugar, sem categoria que você tenha inventado
para organizar a própria leitura.

A conferência devolve ainda uma tabela de língua, que cobre também os itens
aprovados e traz quatro espécies: palavra que parece portuguesa e está no sentido
inglês, frase cujas palavras são todas portuguesas e cuja construção não é, termo
de campo que não é o do autor, e trabalho dito como preço. Essa tabela se corrige
sem o trabalho em mãos, porque o defeito está na frase do apontamento e não no
que ela descreve. Escolha a palavra pela coisa nomeada: em 29/08/2026, dezesseis
ocorrências de *comparador* num mesmo relatório pediram três substitutos
diferentes. **Um item pode passar no teste da ação e estar escrito em inglês
disfarçado**, e foi assim que essas dezesseis chegaram à entrega.

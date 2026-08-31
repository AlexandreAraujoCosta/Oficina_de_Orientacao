# Sessão a abrir: a Oficina de Formatação

Prompt inicial de uma sessão nova, para construir uma oficina que ainda não
existe. Três ferramentas, e elas se sustentam juntas.

---

## Por que uma oficina separada, e não mais uma ferramenta

A oficina de orientação lê e relata. Alberto, Luis e o simulador abrem o
trabalho, apontam e não tocam em nada. Uma ferramenta de forma escreve no arquivo
de quem escreveu o trabalho, e isso não é diferença de assunto: é diferença de
risco.

Em 30/08/2026 essa fronteira foi cruzada por acidente. Um programa que
transformava o arquivo estava no meio da cadeia de análise, rodava em quem não
tinha pedido por ele, e desmontou a capa de uma dissertação que ele não tinha
tocado, porque escrever a forma do corpo no estilo `Normal` alcança tudo o que
herda dele. Separar as oficinas torna essa fronteira estrutural.

**Mesmo repositório.** A maquinaria de OOXML é compartilhada, e duplicá-la
criaria duas versões que divergem. O que muda é o catálogo, a página e a cadeia:
a cadeia da Oficina de Formatação nunca é chamada pela cadeia de análise.

## As três ferramentas, e o risco decresce entre elas

**A Norma escreve no arquivo do autor.** É a de maior risco, e a que já tem
código.

**O analisador de design só olha.** Renderiza as páginas e julga o que se vê.
Risco zero, e é a verificação que faltava à Norma.

**O gerador de PDF por LaTeX escreve um arquivo novo.** Não toca no original, e
por isso escapa da classe inteira de problemas que a Norma enfrentou.

Elas formam uma sequência: a Norma arruma o arquivo que a pessoa continua
editando, o analisador olha o resultado e diz se ficou bom, e o gerador produz o
documento final.

---

## 1. Norma, para normalizar

**O que existe.** `git checkout norma-transformadora` traz
`scripts/normalizar_docx.py`, em Python puro, sem dependência nenhuma, que roda
no Colab. Ele já sabe: varrer parágrafos com profundidade, sem quebrar em caixa
de texto; achar onde termina o pré-textual; achar a faixa das referências,
inclusive com título numerado; reconhecer papéis por regra enunciável; escolher a
forma dominante de cada um e **recusar-se a alinhar** quando nenhuma reúne
metade; apagar parágrafo vazio devolvendo a altura como espaço depois, com quatro
travas; e escrever estilo na ordem que o esquema impõe.

**O que já falhou, com número.** Escrever a forma do corpo no `Normal` levou uma
dissertação de 85 para 92 páginas e desmontou a capa; proteger os herdeiros
exigiu escrever formatação direta em cerca de 360 parágrafos, que é o defeito que
o programa diagnostica. A marcação de revisão escrita à mão, correta no XML,
produziu oito pares de parágrafos fundidos quando o Word aceitou, e a causa não
foi isolada em três hipóteses testadas. A comparação do Word, usada no lugar
dela, reorganiza parágrafos no pré-textual quando o `Normal` muda.

**A decisão que a sessão precisa tomar antes de escrever código**, porque ela dá
programas diferentes:

- **Formatador**: impõe uma norma escolhida, e a forma do arquivo original é
  irrelevante. Não há o que alinhar, há o que aplicar.
- **Organizador**: parte do que o autor fez, acha o padrão dominante e aproxima o
  resto. É o desenho atual, e é o que produziu todos os problemas acima.
- **Mostrador**: não formata nem organiza. Exibe as formas que existem, quantos
  parágrafos usam cada uma, e a escolha de qual vale é de quem tem o arquivo.

A terceira é a que os dados favorecem, porque devolve a decisão a quem tem o
arquivo e deixa o programa fazendo o que ele faz bem, que é contar.

**O que fica de pé em qualquer das três.** Um estilo por papel, e não por forma:
três formas de legenda não são três padrões, são falta de padrão, e criar um
estilo para cada uma cimenta a desordem. O conjunto mínimo: Normal, Rodapé,
Tabela, Legenda, Referência, Parágrafo recuado e a família de Títulos. Onde não
há forma assentada, não se escolhe. E o pré-textual é diagramação feita à mão: o
vazio que ali parece sujeira é o que põe o título no meio da folha.

---

## 2. Analisador de design

**Não existe, e é a peça de que mais se sentiu falta.** Em 30/08 os dois piores
defeitos do dia só apareceram quando as páginas foram renderizadas e olhadas.
Contagem de parágrafo e contagem de estilo não veem o que a página parece: os
relatórios diziam que a capa não fora tocada, e a capa estava desmontada.

**O que ele faria.** Renderiza as páginas do PDF e julga o que se vê. Não abre o
XML, e é essa a diferença: ele avalia o resultado, e não a receita. O que cabe
nele, e cada item se confere olhando:

- comprimento de linha em caracteres, que é o que decide a legibilidade;
- margem e mancha, e se elas cumprem a norma declarada;
- hierarquia visível, isto é, se dá para distinguir um título de nível 2 de um de
  nível 3 sem contar os números;
- linhas órfãs e viúvas, título isolado no pé da página, tabela partida entre
  folhas;
- figura longe da legenda, ou legenda longe da fonte;
- densidade da página, e se ela varia sem razão ao longo do trabalho.

**Ele é a verificação das outras duas.** Rodado antes e depois da Norma, ele diz
o que mudou de fato na página, que é a pergunta que a Norma não sabe responder
sobre si mesma. Rodado sobre a saída do gerador de LaTeX, ele diz se o documento
final está bem posto.

**O que já existe para ele.** `scripts/renderizar_paginas.py` transforma páginas
de PDF em PNG, e o caminho de exportar `.docx` para PDF pelo Word está escrito em
`scripts/paginas.py`. A leitura das imagens é do modelo, e é o único ponto da
oficina inteira em que a avaliação é visual.

---

## 3. Gerador de PDF por LaTeX

**O desenho que escapa do problema.** Ele não modifica o arquivo do autor: lê o
conteúdo e produz um PDF novo. O original fica intacto, e por isso nenhuma das
falhas da Norma pode acontecer aqui. O custo é que o autor deixa de trabalhar no
`.docx` formatado e passa a ter um documento gerado, que ele não edita
diretamente.

**O que já está instalado e conferido**, em 27/08/2026: abntex2, MiKTeX com XeTeX
4.18, pandoc 3.1.2, e Zotero 9.0.6 com Better BibTeX.

**A ordem importa: o estilo CSL vem primeiro.** Ele fixa a forma das referências
que o formatador tem de respeitar, e escrever o formatador antes obrigaria a
refazê-lo depois.

**E há um bloqueio que não é técnico.** A especificação do formato do programa de
pós-graduação não existe por escrito. Sem ela, o gerador ou segue a ABNT estrita,
que o programa pode não exigir, ou segue uma norma inventada por nós, que ninguém
pediu. Escrever essa especificação é decisão de quem coordena o programa, e a
sessão deve começar perguntando se ela existe.

---

## O que a oficina nova herda das antigas, e é obrigatório

**Toda conferência tem controle positivo.** Antes de dizer o que um teste
acusou, dê a ele um caso que ele tem de reprovar e confira que reprova. Num único
dia, quatro conferências escritas às pressas produziram o achado em vez de
encontrá-lo, e três pela mesma causa: varrer parágrafo com expressão que quebra
onde há parágrafo dentro de parágrafo.

**A ferramenta declara o que toca e o que não toca, e prova depois de rodar.**
`scripts/revisao_word.py` é o padrão: ele aceita as próprias alterações numa
cópia descartável, coteja com o esperado, e recusa certificar quando não bate. Foi
essa conferência que impediu a entrega de um arquivo com parágrafos fundidos.

**O alcance vai junto com o resultado**, e a hipótese que caiu no teste é
resultado e vai dita. Não se conserta o que não se diagnosticou: se a causa não
foi isolada, ou se isola, ou se remove a dependência dela, e a ignorância fica
escrita.

---

## O que trazer para a sessão

- O ramo `norma-transformadora`, com o código e os comentários que explicam cada
  regra pela medição que a originou.
- O `REGISTRO-DE-DESENHO.md`, nas seções de 28 e 30 de agosto.
- Um `.docx` real de dissertação, com o pré-textual completo, porque nenhum dos
  problemas conhecidos aparece num arquivo pequeno.
- O Word instalado, para conferir abrindo, e o que for preciso para renderizar
  páginas em imagem.
- A resposta, se houver, sobre a especificação de formato do programa.

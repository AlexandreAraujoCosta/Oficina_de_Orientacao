# Sessão a abrir: o assistente de formatação

Prompt inicial de uma sessão nova. Não é uma ferramenta da oficina: é o começo de
outro artefato, que precisa de várias rodadas e não de uma passagem.

---

## O que se vai construir

Um assistente que **melhora a forma de um trabalho acadêmico em `.docx`**:
organiza os padrões de formatação, padroniza o que está disperso e melhora o
desenho da página. O que a Norma fazia era o primeiro passo disso, e ela está
guardada no ramo `norma-transformadora`, com o código que funciona e o registro
do que falhou.

## O que já está construído, e onde

`git checkout norma-transformadora` traz `scripts/normalizar_docx.py`, que é
Python puro, sem dependência nenhuma, e roda no Colab. O que ele já sabe fazer,
tudo medido em dissertações reais:

- varrer parágrafos com profundidade, sem quebrar em caixa de texto;
- achar onde termina o pré-textual, pela regra do número de página nas entradas
  do sumário;
- achar a faixa da lista de referências, inclusive com título numerado;
- reconhecer três papéis por regra enunciável (corpo, referência, legenda) e
  dois por forma (recuado, tabela);
- escolher a forma dominante de cada papel, e **recusar-se a alinhar** quando
  nenhuma forma reúne metade do papel;
- apagar parágrafo vazio e devolver a altura como espaço depois, com quatro
  travas que impedem apagar o que carrega âncora, quebra, campo ou marcação;
- escrever estilo novo, ou escrever no `Normal`, com a ordem que o esquema impõe;
- reconhecer parágrafo que parece título e não usa estilo de título.

E `scripts/revisao_word.py`, no mesmo ramo, gera a cópia com alteração controlada
pela comparação do Word, de modo que aceitar a revisão devolve a cópia corrigida
por construção, e o programa confere isso sozinho antes de terminar.

## O que já falhou, e é onde a sessão deve começar

Isto não é lista de defeitos a consertar: é o que a experiência de 30/08/2026
mostrou sobre a natureza do problema.

**Escrever a forma do corpo dentro do `Normal` alcança tudo o que herda dele.**
Numa dissertação real, desmontou a capa, que o programa não tinha tocado, e o
arquivo foi de 85 para 92 páginas. Proteger os herdeiros exigiu escrever
formatação direta em cerca de 360 parágrafos, que é exatamente o defeito que o
programa diagnostica.

**A marcação de revisão escrita à mão não sobrevive ao aceite.** Vinte e sete
marcas de parágrafo, todas corretas no XML e todas em parágrafo vazio, produziram
oito pares de parágrafos de texto fundidos quando o Word aceitou. Três hipóteses
caíram no teste e a causa não foi isolada. A saída foi deixar o Word escrever a
marcação, comparando os dois arquivos.

**A comparação do Word também falha, e no pré-textual.** Quando o `Normal` muda,
ela reorganiza parágrafos em regiões que ninguém tocou.

**O pré-textual não é ruído: é diagramação feita à mão.** O vazio que ali parece
sujeira é o que põe o título no meio da folha e a cidade no rodapé. Qualquer
transformação que o alcance está errada, mesmo quando o resultado parece melhor.

## As decisões que já foram tomadas, e por quê

**Um estilo por papel, e não por forma.** Criar um estilo para cada forma
encontrada organiza a aparência e cimenta a desordem: três formas de legenda
viram três estilos, e cada variante passa a ser correta pelo seu próprio estilo.
Multiplicar estilo é tão ruim quanto não ter nenhum.

**O conjunto mínimo de estilos:** Normal para o texto, Rodapé, Tabela, Legenda,
Referência, Parágrafo recuado, e a família de Títulos. A referência tem forma
certa fora do arquivo, que é a NBR 6023, e é o único papel em que o programa
impõe em vez de alinhar.

**Onde não há forma assentada, não se escolhe.** Se nenhuma forma reúne metade do
papel, o programa diz isso e não mexe, porque escolher seria decidir pelo autor um
ponto que é dele.

**Título não se converte por heurística.** Falso positivo entra no sumário
automático. Quando houver sumário manual, ele é a lista de títulos escrita pelo
próprio autor e resolve o problema por consulta; quando não houver, indica-se e
não se converte.

## O que muda de escopo nesta sessão

A oficina de orientação **não depende mais disto**. O diagnóstico de forma virou
um passo da análise, que lê e relata; a transformação saiu da cadeia. Isso
libera o assistente de formatação de duas restrições que o apertavam: ele não
precisa mais rodar em silêncio dentro de outra ferramenta, e não precisa ser
seguro o bastante para rodar em quem não pediu por ele.

Em troca, ele ganha uma exigência: **quem o roda sabe que o arquivo vai mudar, e
tem de poder ver o que mudou antes de aceitar.**

## Por onde começar, e é uma pergunta antes de ser uma tarefa

A pergunta que a sessão precisa responder antes de escrever código é **o que o
usuário quer que o programa decida por ele**. As duas respostas possíveis dão
programas diferentes:

Se ele quer um formatador, o programa impõe uma norma escolhida, a ABNT ou a do
programa de pós-graduação, e a forma do arquivo original é irrelevante. Nesse
caso não há o que "alinhar", há o que aplicar, e o problema deixa de ser de
diagnóstico.

Se ele quer um organizador, o programa parte do que o autor já fez, encontra o
padrão dominante e aproxima o resto dele. É o desenho atual, e é o que produziu
todos os problemas acima, porque respeitar o que existe obriga a distinguir o que
é padrão do que é ruído.

**A terceira via, que talvez seja a certa:** o programa não formata nem organiza,
e sim **mostra**. Exibe as formas que existem, quantos parágrafos usam cada uma, e
oferece ao usuário a escolha de qual vale, aplicando-a depois com o
consentimento dele. Aí a decisão que hoje o programa toma sozinho, e erra, passa
a ser de quem tem o arquivo, e o programa faz o que sabe fazer bem, que é contar.

## O que trazer para a sessão

- O ramo `norma-transformadora`, com o código e os comentários que explicam cada
  regra pela medição que a originou.
- `REGISTRO-DE-DESENHO.md`, nas seções de 28 e 30 de agosto, que contam os
  defeitos com números.
- Um `.docx` real de dissertação, com o pré-textual completo, porque nenhum dos
  problemas acima aparece num arquivo pequeno.
- O Word instalado, para conferir o resultado abrindo e comparando, que é a única
  conferência que pegou os dois piores defeitos de 30/08. Contagem de parágrafo e
  de estilo não veem o que a página parece.

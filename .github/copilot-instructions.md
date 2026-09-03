# Oficina de Orientação

Ferramentas de leitura automática de trabalhos acadêmicos. **Siga `AGENTS.md`, na
raiz do repositório**, que traz o modo de uso, a cadeia de comandos, a escolha de
modelo e a política sobre material de terceiro. Leia também **`TRES-COLUNAS.md`**,
que diz o que a sua ferramenta roda, o que sobra para a pessoa fazer à mão e o
que não se pode afirmar sem conferência. **A divisão não se decide pelo nome do
produto**: decide-se por três capacidades que você descobre em dois minutos, e
que estão descritas lá.

O arranjo é um diretório só: esta pasta, com o trabalho a analisar na raiz. Quando
pedirem a análise sem dizer mais nada, o trabalho é o único `.docx` ou `.pdf` aqui.
Se houver mais de um, pergunte; se não houver nenhum, diga onde pôr.

As três travas, repetidas aqui porque nenhuma delas pode se perder e todas falham
em silêncio:

1. **Nunca digite trecho do trabalho.** Você indica o parágrafo (`[P123]`); um
   programa copia o texto e o insere depois. Citação com uma palavra trocada é o
   defeito mais grave numa análise que se pretende verificável.
2. **Antes de afirmar que falta algo, procure junto uma coisa que você sabe estar
   lá, e relate os dois resultados.** É o controle positivo, e é de graça.
   Procurar duas vezes com termos diferentes não basta: duas buscas quebradas do
   mesmo jeito devolvem zero duas vezes. O que prova que o instrumento funciona
   é ele achar, na mesma execução, o que existe. Defeitos já medidos aqui:
   `grep -c` conta linhas e não ocorrências; `grep -o` com `-i` e `-F` juntos
   devolve vazio; o ponto da expressão regular não casa letra acentuada; busca
   sem fronteira de palavra acha a cadeia dentro de outra palavra; o singular
   devolve zero onde só há plural; `grep` sem `-i` distingue caixa; e procurar o
   **termo** em vez da **coisa** devolve zero num documento que diz o mesmo com
   outras palavras.
3. **Se recebeu só o `.docx`, você não viu as figuras.** Declare, não descreva
   figura nenhuma, e não diga que converteu o arquivo.
4. **A extração em texto não carrega realce, comentário nem nota de rodapé.**
   Antes de acusar qualquer coisa de descuido, abra o `.docx` como zip e leia
   `word/comments.xml`, `word/footnotes.xml` e as marcas de realce em
   `word/document.xml`. Boa parte do que parece descuido está marcada pelo
   autor, ou já é pergunta que ele fez ao orientador. Ignorar isto já produziu,
   nesta oficina, acusação contra parágrafo cuja nota trazia o que se dizia
   faltar.
5. **Nunca rode `git add`, `git commit` ou `git push`** havendo trabalho de
   outra pessoa na pasta. O remoto é público e publicação não se desfaz.
   `git pull` é seguro.

E a regra que orienta o resto: **onde existe programa, rode o programa.** Os
scripts localizam suspeitas em segundos e não erram; o julgamento de cada uma é
que é seu.

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

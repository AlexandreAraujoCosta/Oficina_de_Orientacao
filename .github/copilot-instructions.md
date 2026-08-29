# Oficina de Orientação

Ferramentas de leitura automática de trabalhos acadêmicos. **Siga `AGENTS.md`, na
raiz do repositório**, que traz o modo de uso, a cadeia de comandos, a escolha de
modelo e a política sobre material de terceiro.

O arranjo é um diretório só: esta pasta, com o trabalho a analisar na raiz. Quando
pedirem a análise sem dizer mais nada, o trabalho é o único `.docx` ou `.pdf` aqui.
Se houver mais de um, pergunte; se não houver nenhum, diga onde pôr.

As três travas, repetidas aqui porque nenhuma delas pode se perder e todas falham
em silêncio:

1. **Nunca digite trecho do trabalho.** Você indica o parágrafo (`[P123]`); um
   programa copia o texto e o insere depois. Citação com uma palavra trocada é o
   defeito mais grave numa análise que se pretende verificável.
2. **Antes de afirmar que falta algo, procure duas vezes**, com termos diferentes.
3. **Se recebeu só o `.docx`, você não viu as figuras.** Declare, não descreva
   figura nenhuma, e não diga que converteu o arquivo.
4. **Nunca rode `git add`, `git commit` ou `git push`** havendo trabalho de
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

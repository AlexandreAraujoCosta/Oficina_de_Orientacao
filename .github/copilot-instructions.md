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

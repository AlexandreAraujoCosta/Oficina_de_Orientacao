# Analisador de Consistência

A versão rápida e barata, para rodar em plano gratuito. O ATA completo continua sendo outra coisa.

**O nome é a ressalva.** "Analisador" faria o estudante pensar que a dissertação foi analisada. "Alberto" diz o que foi conferido e, ao dizer, diz o que não foi. Isto não é detalhe de redação: medimos em 14/08 que ressalva global é ignorada e que registro por item não é, e o nome é o registro que ninguém pula.

---

## O que ele faz, e é uma coisa só

**Confere o trabalho contra ele mesmo.** O mesmo número em dois lugares, os itens numerados nas listas contra os do corpo, o termo definido num ponto e usado longe dele, e duas versões do arquivo entre si.

## O que ele não faz, e precisa estar na primeira tela

**Não avalia argumento, método, marco teórico nem contribuição.** Não diz se a tese se sustenta, se o método autoriza as conclusões, nem se o trabalho é original.

**O silêncio dele não é aprovação.** Rodar, receber três achados e corrigi-los não quer dizer que o trabalho esteja bem: quer dizer que a consistência interna foi conferida. **Análise de conteúdo mais intensa só é viável com o sistema completo.**

---

## Por que esta é a camada certa para a versão barata

Quatro critérios, todos medidos em 13 e 14/08:

**Taxa de sustentação alta.** Nas duas leituras completas, as vozes de consistência não perderam nenhuma hipótese no cotejo; as interpretativas perderam de 2 a 3 em 10. Sem orientador filtrando, falso positivo é caro, e esta é a camada que produz menos.

**Custo baixo.** A busca é determinada e cabe em script. As seis vozes do ATA consomem cerca de 1,7 milhão de tokens porque leem o trabalho inteiro seis vezes; o script lê uma vez, sem modelo.

**Achado que humano não produz.** Rastrear um número por todas as aparições em duzentas páginas é tedioso, e por isso não se faz.

**Reparo barato.** É organização, não redimensionamento: nem dado novo nem análise nova. A versão correta em geral já está no texto.

---

## A divisão entre script e modelo

**O script acha candidatos. O modelo julga candidatos.**

É o mesmo princípio da regra do localizador, que tirou a transcrição da mão do modelo: operação determinada vai para mecanismo, julgamento fica com quem julga.

O script entrega dezenas de trechos com localizador. O modelo lê esses trechos, e não as 36 mil palavras. É daí que vem a ordem de grandeza.

## O estado do script (`scripts/conferir_consistencia.py`)

**`listas`** — funciona. Sobre a dissertação de 12/08, achou em segundos que os gráficos 19 e 23 e os quadros 2 e 3 estão no corpo e não nas listas. São três dos dez itens do documento de banca, que custaram duas leituras de agente.

**`numeros`** — funciona depois de duas correções. A primeira versão devolvia 182 candidatos, quase todos ruído, porque ordenava por distância e trazia ao topo os pares sumário-apêndice. **O conserto não foi filtrar mais: foi exigir que os dois contextos partilhem vocabulário de conteúdo.** Dois usos do mesmo número interessam quando falam da mesma coisa. Com o corte da bibliografia, ficou em 15 candidatos, e os do topo são pares reais.

**`termos`** — implementado, ainda não testado.

**A comparação entre versões** entrou em script em 25/08/2026, e é a operação de maior valor medido: o documento de banca saiu quase todo dela. `comparar_versoes.py` pareia os parágrafos por conteúdo e diz, de cada localizador do relatório antigo, se o parágrafo correspondente mudou.

## Um defeito do próprio script, registrado porque é o tema do projeto

O filtro de citação ficou **inerte por um caractere invisível**: um backspace literal entrou no arquivo por escape mal formado num heredoc, e a regex passou a exigir um byte que nunca aparece no texto. Não deu erro, não apareceu em `grep` nem em `sed`, e o efeito foi um filtro que não filtrava nada enquanto parecia estar lá.

Achado só porque os resultados continuavam ruins depois de o código parecer certo. **Quinze ocorrências do mesmo caractere estavam no arquivo.**

---

## O que falta antes de distribuir

1. **A camada de julgamento sobre os candidatos**, que é um prompt curto e não uma cadeia.
2. **Medir a taxa de erro depois do julgamento**, que é o número que nunca foi apurado e sem o qual não se distribui. Tudo que foi medido até agora é taxa de hipótese bruta.
3. **Testar em Sonnet**, que é onde o estudante vai rodar.

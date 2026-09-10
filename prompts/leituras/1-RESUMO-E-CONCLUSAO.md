# Leitura 1 — a partir do resumo e da conclusão

**Roda em paralelo com a leitura 2.** Não depende dela.

**Modelo: Opus.** Medido em 31/08/2026: o mesmo pedido em Sonnet custou 13% menos e
metade do tempo, e devolveu 14 asserções fortes contra 19, duas divergências de
alcance contra sete, e nenhum dos dois achados fora do pareamento. A parte de
classificar é mecânica; a de ver que uma afirmação diverge da tabela de onde saiu não
é, e é ela que rende.

**O corte.** Esta leitura parte do que o trabalho afirma e pergunta de onde vem. A
leitura 2 parte do que ele promete e pergunta onde se cumpre.

---

Você lê um trabalho acadêmico já concluído. Sou membro da banca. Não abra relatório,
cotejo ou conferência anterior sobre ele.

## O material, e ele vem num arquivo só

`MATERIAL.md`, montado por quem despacha esta leitura:

```
python scripts/montar_material.py <trabalho.docx> extracao/<trabalho>.txt        -o MATERIAL.md --mapa MAPA.md
```

Ele traz, num arquivo: o sumário como o trabalho o escreve, a tabela de figuras já
extraídas do `.docx` com o parágrafo da legenda de cada uma, o mapa estrutural, e
**o trabalho inteiro na ordem, parágrafo por parágrafo**, mais as notas de rodapé.

**Você não precisa ir buscar passagem: ela está aí.** Nem todo número existe, porque
parágrafo sem texto não recebe marcador, e afirmar que um localizador está morto sem
conferir no arquivo é erro.

**Medido em 08/09/2026**, sobre a mesma leitura e o mesmo trabalho: buscando passagem
por passagem, 41 chamadas e 16,1 minutos; com tudo num arquivo, 18 chamadas e 13,7
minutos, **e zero buscas de passagem**. É a mesma economia que a verificação já tinha,
e ela é da relação e não da busca: o arquivo não repete o parágrafo uma vez por item
que o cita.

**As imagens vêm à parte, e vêm numa mensagem só.** O `MATERIAL.md` traz o endereço e
o arquivo de cada figura, e não a figura.

Onde o `MATERIAL.md` não tiver chegado, o material antigo serve e custa mais:

- `MAPA.md` — resumo, palavras-chave, abstract, introdução, títulos de seção, legendas
  de quadros, tabelas e gráficos, apêndices, conclusão inteira e lista de referências,
  com localizadores [P###] e página.
- `extracao/trabalho.txt` — o texto completo, numerado. **Não o leia inteiro**; use
  `Grep`.
- `trabalho.pdf` — `Read` com faixa de páginas só para ver tabela ou figura, no máximo
  três vezes.

## Passo 1 — filtrar a conclusão

Uma conclusão não é feita só de conclusões. Percorra-a e classifique cada asserção:

- **RETOMADA** — repete problema, objeto ou método, sem afirmar nada de novo.
- **ACHADO** — afirma o que a pesquisa encontrou no material empírico.
- **TESE** — afirmação interpretativa ou normativa construída sobre os achados.
- **ARGUMENTO** — passo que sustenta um achado ou uma tese e não se sustenta sozinho.
- **DISCUSSÃO** — implicação, impacto possível, agenda.
- **LIMITAÇÃO** — alcance declarado.

Só **ACHADO** e **TESE** contam. Devolva a lista numerada, cada um com localizador e
redigido em uma frase. **É a lista de alvos do passo 3.**

## Passo 2 — contra o resumo

Mesma classificação no resumo. Depois, três perguntas.

**A. O que o resumo afirma e a conclusão não sustenta.** Procure a contrapartida na
conclusão e, não achando, procure no corpo antes de declarar ausência. É promessa que
o trabalho não fecha, e pesa porque o resumo é a peça lida primeiro.

**B. O que a conclusão afirma e o resumo não anuncia.** Contribuição não reivindicada.
Registre, e saiba que esses itens costumam ser inertes para uma banca e úteis para o
autor: marque-os como tal.

**C. Divergência de alcance na mesma afirmação.** Uma generaliza e a outra restringe,
uma quantifica e a outra não, uma dá um número e a tabela dá outro. **É o achado mais
valioso**, e exige conferir contra a tabela de onde o número saiu, e não só contra a
outra peça de texto.

**E o abstract**: não pergunte se ele traduz o resumo, pergunte se o que ele afirma se
sustenta. Caso medido: um resumo dizia que 68 decisões resultaram de sorteio e o
abstract dizia `68 judicial decisions were randomly selected`, o que é falso, e não só
incompleto, porque se sortearam 125 e se excluíram 57 depois.

## Passo 2b — medir o alcance do resumo

Não julgue o resumo aqui: a avaliação por seção o faz. Meça, e entregue três números.

- Quantas asserções fortes da conclusão **não têm contrapartida no resumo**.
- Quais dos quatro elementos o resumo traz: problema ou objetivo; método, com recorte
  e tamanho do material; resultados com os números; conclusão.
- Quantos percentuais o resumo anuncia **sem o denominador**.

## Passo 3 — caminhar de cada asserção forte até o dado

Para cada asserção do passo 1, pergunte o que a sustenta, ache a passagem, e pergunte
de novo, agora dela. Até três saltos, ou até um destes términos:

- **DADO** — tabela, contagem, ou trecho do corpus citado. Término bom.
- **FONTE** — doutrina ou norma citada. Bom para tese, insuficiente para achado.
- **ASSERÇÃO** — outra afirmação do próprio trabalho que também não desce a dado.
  Registre onde a cadeia parou.
- **NADA** — não há passagem que sustente. É o achado mais grave.

Marque à parte a cadeia **estreita**: o suporte existe e é menor que a afirmação
(sustenta um tribunal, um recorte, um subconjunto, e a asserção fala do todo). E a
cadeia que termina em dado que **contradiz** a asserção.

### Antes de percorrer, separe o que se diz do que se infere

**São duas espécies de asserção, e a prova que cada uma pede é outra.** O que o
trabalho **diz** sobre o campo, sobre o instituto, sobre o estado da discussão, se
prova na literatura, e ali o término bom é FONTE. O que ele **infere** do material
que reuniu se prova na análise dos dados ou das fontes que ele próprio apresenta, e
ali FONTE não serve: o término bom é DADO.

Classifique cada asserção nas duas espécies antes de percorrer a cadeia, porque a
classificação muda o que conta como término bom. **Asserção de inferência que
termina em FONTE está apoiada no lugar errado**, ainda que a fonte exista e seja
boa: quer dizer que o trabalho foi buscar fora a sustentação do que ele próprio se
propôs a medir.

### Término bom não é término suficiente

Terminar em dado responde *isto se apoia em alguma coisa?*. Falta a segunda
pergunta, **o que sustenta basta para o que se afirma?**, e é nela que está a
qualidade da inferência, que é o objeto principal de quem examina.

Para toda cadeia que terminar em DADO, pergunte: **o dado carrega a força da
asserção?** Quatro modos de não carregar, e os quatro já apareceram nesta bancada
com o término marcado como bom:

- **a comparação está condicionada.** Os dois conjuntos comparados foram
  selecionados por um processo que os afeta de modo diferente, e a diferença
  medida mistura o efeito com a seleção.
- **o agregado vira caso.** A taxa média sustenta a afirmação sobre o conjunto, e a
  asserção fala de cada unidade.
- **a coincidência vira mecanismo.** As duas séries andam juntas, e a asserção diz
  que uma produz a outra.
- **o desfecho vira intenção.** O dado mede o que o texto faz, e a asserção diz o
  que quem o escreveu quis.

Onde o dado não carregar, o item **não manda retirar a asserção**: manda descer o
alcance dela até onde o dado chega, e diz até onde. Caso medido em 05/09/2026: numa
dissertação, quarenta e uma de quarenta e seis cadeias terminaram em DADO e foram
dadas por boas, e uma delas comparava dois ambientes cuja probabilidade de entrar
na comparação diferia seis vezes.

Caso medido, para calibrar dois términos. Uma conclusão arrolava "segurança jurídica"
entre os valores mobilizados, e a expressão ocorria uma única vez na dissertação
inteira, na própria frase da conclusão: **NADA**. E três teses devolviam como achado a
pressuposição que a autora escrevera na definição da categoria antes de aplicá-la, de
modo que a contagem media o recurso linguístico e não a pressuposição: **ASSERÇÃO**.

**E confira contra as ressalvas.** Se o trabalho declara um limite (não generalizar,
não inferir causa, não buscar intenção, não representar o universo) e a asserção o
atravessa, isso é item de corpo, e a régua é do próprio autor. Dê os dois
localizadores.

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

## Três regras

1. **Controle positivo.** Antes de qualquer afirmação de ausência, mostre que a sua
   busca acha coisas que estão lá, e registre o controle. Neste ambiente `grep -o` com
   `-i` e `-F` **juntos** devolve vazio, embora `-oi` e `-oF` funcionem isolados; ponto
   de expressão regular não casa letra acentuada; busca sem fronteira de palavra casa
   dentro de outra ("segurança" dentro de "insegurança", que já produziu contagem
   errada nesta bancada).
   Quatro defeitos novos, medidos em 03/09/2026, e os quatro produziram acusação
   falsa: ancorar `^\[P` na extração perde os parágrafos cuja linha começa por
   `##`, `**` ou `> ` (839 em lugar de 886); buscar sem ignorar a caixa perde a
   ocorrência que abre frase (zero em lugar de doze); contar parágrafo de `.docx`
   por `<w:p[ >].*?</w:p>` perde os auto-fechados com atributo (990 em lugar de
   999); e remover acento antes de contar faz *controvérsia* entrar numa contagem
   de *controvers* (20 em lugar de 9). `grep -c` conta linhas, não ocorrências.
   Onde houver Python, use `scripts/contagem.py`, que traz isso em código e se
   recusa a carregar se o próprio autoteste falhar.

2. **Alcance declarado.** Diga o que leu e o que não leu. **E declarar o alcance não autoriza concluir para fora dele:** quem varreu o capítulo 4 pode escrever que a expressão não ocorre no capítulo 4, e não que o trabalho não trata do assunto. A frase que sai do alcance vira afirmação sobre o trabalho inteiro, e é ela que chega ao autor.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor. Registre.

## A primeira linha de cada item diz o que muda

Todo item nasce com a primeira linha dizendo **o que muda no trabalho se ele
estiver certo**, e a resposta é uma de três:

- **A afirmação muda**: inverte, cai, encolhe, ou passa a valer sobre outro
  conjunto. Nomeie-a, com o localizador. Promessa não cumprida entra aqui,
  porque a afirmação de que o trabalho entrega algo (um produto, um capítulo,
  uma base) é a que cai.
- **A afirmação fica igual e passa a ser conferível**: o denominador ao lado do
  percentual, a base depositada, o procedimento escrito, a referência que
  sustenta uma premissa. Marque **CONFERE**.
- **Nada muda**: gralha, numeração, referência sem chamada no corpo, número
  divergente de que nenhuma afirmação depende. Marque **ACABAMENTO**.

O denominador decide entre as duas primeiras: se ele muda o conjunto sobre o
qual a afirmação vale, a afirmação muda; se só falta ao lado do percentual, é
CONFERE. A marca decide onde o item entra no relatório (corpo, primeira lista do
anexo, segunda lista), e ela se decide aqui, por quem viu o material.

**Isto não é teto de itens.** Escreva todo achado que a leitura sustentar.

Calibragem: num cotejo de 08/09/2026, 50 dos 91 itens de um relatório não mudavam
nada, e nenhum trazia a afirmação que mudava, porque ninguém a tinha pedido.

## Saída, em dois arquivos

**`LEITURA-RESUMO-CONCLUSAO.md` traz os itens, e cada um nasce na forma em que chega ao aluno.**
Não há tradução depois: a verificação confere e derruba, a triagem decide o lugar,
e a redação pode ajustar a linguagem. Mudanças de conteúdo exigem nova verificação contra a fonte. A forma, e ela é obrigatória:

    ### A1. Título que afirma sobre o trabalho, e não sobre a leitura
    Aponta       o que está errado e onde, com os localizadores necessários à demonstração; um basta quando a passagem demonstra o problema
    O que fazer  em [P###], verbo, objeto, substituto; a razão depois de ponto final
    O que muda   o que o trabalho passa a sustentar; ou a marca CONFERE ou ACABAMENTO

O prefixo desta leitura é `A`, com numeração contínua. Contribuição não
reivindicada e ponto forte entram na mesma forma, com `AC` e `AF`. Nada do
percurso entra no item: nem término, nem estado, nem hipótese caída, nem controle
de busca, nem o nome do passo que o produziu. O teste: tape o resto do arquivo e
leia só o item; quem escreveu o trabalho sabe o que abrir e o que fazer.

**`REGISTRO-RESUMO-CONCLUSAO.md` traz o percurso, e não vai ao aluno.** Ali ficam a lista das asserções fortes e a contagem por término do passo 3, as hipóteses que
caíram e onde estava o que as salvou, o alcance, e os controles de busca. As listas
de trabalho dos passos vão ali, e não no arquivo dos itens. É o que a verificação
e a triagem consultam quando um item pede prova.

Devolva no texto final os dois caminhos e a conta dos itens por marca.

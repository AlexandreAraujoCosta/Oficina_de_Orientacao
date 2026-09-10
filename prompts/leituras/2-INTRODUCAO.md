# Leitura 2 — a partir da introdução

**Roda em paralelo com a leitura 1.** Não depende dela, e é o paralelismo que põe o
relógio em torno de trinta minutos.

**Modelo: Opus.** Julgamento, contexto pequeno, poucas chamadas.

**O corte.** A leitura 1 parte do que o trabalho afirma e pergunta de onde vem. Esta
parte do que o trabalho promete e pergunta onde se cumpre. São classes de defeito
diferentes: lá, afirmação sem lastro; aqui, promessa não cumprida.

---

Você lê um trabalho acadêmico já concluído. Sou membro da banca.

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

- `MAPA.md` — resumo, abstract, **introdução inteira**, títulos de seção, legendas de
  quadros, tabelas e gráficos, apêndices, conclusão e **lista de referências**, com
  localizadores [P###] e página. Leia primeiro e inteiro.
- `extracao/trabalho.txt` — o texto completo, numerado. **Não o leia inteiro.** Use
  `Grep` para ir ao ponto em que uma promessa deveria se cumprir.
- `trabalho.pdf` — use `Read` com faixa de páginas só para ver tabela ou figura, no
  máximo três vezes. Para ler texto do PDF sem gastar chamada de imagem, `pdftotext`.

Não abra relatório, cotejo ou conferência anterior sobre este trabalho.

## Passo 1 — extrair as promessas

A introdução declara: o objeto, o problema, a hipótese, o método, o percurso dos
capítulos, e o que o trabalho pretende contribuir. Liste cada promessa em uma frase,
com o localizador. Inclua o que vem em forma de anúncio ("o capítulo 2 examinará",
"adota-se a metodologia X", "pretende-se demonstrar que").

## Passo 2 — onde cada promessa se cumpre

Para cada uma, ache no trabalho o lugar em que ela se realiza, e diga em qual destes
quatro estados ela está:

- **CUMPRIDA** — existe a passagem, e ela faz o que foi anunciado. Dê o localizador.
- **DESLOCADA** — cumpre-se noutro lugar, ou de outro modo, ou com outro alcance.
  Diga onde e qual a diferença.
- **DECLARADA E NÃO EXECUTADA** — o trabalho anuncia um procedimento e não há passo
  algum que o execute. **Antes de afirmar isso, procure a passagem em que ele
  executa, e registre onde procurou.** É o achado mais grave deste passo.
- **ABANDONADA** — cumpre-se no corpo e desaparece da conclusão, ou o inverso.

Interessa em especial o método declarado contra o método executado, e a hipótese:
**se a hipótese foi desmentida pelos dados, o trabalho diz isso, ou a resgata
redefinindo um conceito?**

## Passo 2b — as ressalvas foram aplicadas?

Todo trabalho declara limites, e é comum que se percam pelo caminho. A ressalva é
promessa de **não** fazer alguma coisa, e vale conferir se foi cumprida com o mesmo
rigor das promessas positivas.

**Mapeie primeiro.** As ressalvas têm marcas de fórmula, e a busca por elas é barata:
*não se pretende*, *não é possível afirmar*, *não permite inferir*, *não se pode
generalizar*, *não serão objeto*, *seria necessário*, *não se trata de*, *com as
devidas cautelas*, *nos limites de*, *escapa ao escopo*. Colha também as da seção de
limitações, quando houver. Liste cada uma com localizador e em uma frase.

**Depois confira cada uma contra a conclusão e contra o resumo**, que é onde elas se
perdem. Três estados:

- **HONRADA** — nenhuma afirmação posterior a atravessa.
- **ATRAVESSADA** — o trabalho afirma exatamente o que disse que não afirmaria. Dê os
  dois localizadores, o da ressalva e o da travessia.
- **ESVAZIADA** — a ressalva sobrevive na letra e não no uso: o texto a repete e
  conclui como se ela não existisse, ou a põe numa nota enquanto a frase do corpo
  segue larga.

Casos medidos. Um trabalho recusava representatividade estatística em quatro
passagens e a conclusão generalizava para a classe inteira de tribunais. Outro
declarava não buscar intenção e usava quatro verbos de propósito na conclusão. Um
terceiro enumerava três situações em que o critério não valeria, respondia que não
seriam o foco, e não fixava etapa alguma para identificá-las.

**A ressalva atravessada é item de corpo**, e dos mais fortes, porque o próprio
trabalho fornece a régua com que se mede. Não é o leitor que impõe o limite: é o autor.

## Passo 3 — o que o trabalho não tomou por objeto

A introdução recorta. Pergunte o que ficou de fora do recorte e estava ao alcance do
material: o objeto vizinho não examinado, o ator cujo discurso não passou pelo mesmo
tratamento, a fonte disponível e não usada. **Não é cobrança de outra pesquisa**: só
conta o que o próprio material já continha e o método já alcançava.

Caso medido, para calibrar: uma dissertação analisava a retórica de tribunais que
descumprem o Supremo, e a única retórica que ela não submetia ao mesmo tratamento era
a do próprio Supremo, cujas decisões estavam no corpus.

## Passo 4 — as referências

O mapa traz a lista. Confira por amostra as citações do corpo contra ela: obra citada
e ausente da lista, ano divergente entre a citação e a entrada, autoria trocada.
**Só interessa a que toca peça de que o argumento depende.**

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

2. **Alcance declarado.** Diga o que leu e o que não leu. **E declarar o alcance não autoriza concluir para fora dele:** quem varreu o capítulo 4 pode escrever que a expressão não ocorre no capítulo 4, e não que o trabalho não trata do assunto. A frase que sai do alcance vira afirmação sobre o trabalho inteiro, e é ela que chega ao autor.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor. Registre.

## O filtro, e vale para tudo acima

**Não segure hipótese por falta de certeza.** A conferência vem depois, é de outra voz
e é barata. Hipótese que cai na conferência é resultado, não erro seu.

### A primeira linha de cada item diz o que muda

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

**`LEITURA-INTRODUCAO.md` traz os itens, e cada um nasce na forma em que chega ao aluno.**
Não há tradução depois: a verificação confere e derruba, a triagem decide o lugar,
e a redação pode ajustar a linguagem. Mudanças de conteúdo exigem nova verificação contra a fonte. A forma, e ela é obrigatória:

    ### P1. Título que afirma sobre o trabalho, e não sobre a leitura
    Aponta       o que está errado e onde, com os localizadores necessários à demonstração; um basta quando a passagem demonstra o problema
    O que fazer  em [P###], verbo, objeto, substituto; a razão depois de ponto final
    O que muda   o que o trabalho passa a sustentar; ou a marca CONFERE ou ACABAMENTO

O prefixo desta leitura é `P`, com numeração contínua. Contribuição não
reivindicada e ponto forte entram na mesma forma, com `PC` e `PF`. Nada do
percurso entra no item: nem término, nem estado, nem hipótese caída, nem controle
de busca, nem o nome do passo que o produziu. O teste: tape o resto do arquivo e
leia só o item; quem escreveu o trabalho sabe o que abrir e o que fazer.

**`REGISTRO-INTRODUCAO.md` traz o percurso, e não vai ao aluno.** Ali ficam a lista das promessas e das ressalvas com o estado de cada uma, as hipóteses que
caíram e onde estava o que as salvou, o alcance, e os controles de busca. As listas
de trabalho dos passos vão ali, e não no arquivo dos itens. É o que a verificação
e a triagem consultam quando um item pede prova.

Devolva no texto final os dois caminhos e a conta dos itens por marca.

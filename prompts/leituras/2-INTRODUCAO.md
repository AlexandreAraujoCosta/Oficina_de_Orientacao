# Leitura 2 — a partir da introdução

**Roda em paralelo com a leitura 1.** Não depende dela, e é o paralelismo que põe o
relógio em torno de trinta minutos.

**Modelo: Opus.** Julgamento, contexto pequeno, poucas chamadas.

**O corte.** A leitura 1 parte do que o trabalho afirma e pergunta de onde vem. Esta
parte do que o trabalho promete e pergunta onde se cumpre. São classes de defeito
diferentes: lá, afirmação sem lastro; aqui, promessa não cumprida.

---

Você lê um trabalho acadêmico já concluído. Sou membro da banca.

## O material

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

2. **Alcance declarado.** Diga o que leu e o que não leu.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor. Registre.

## O filtro, e vale para tudo acima

Só entra a hipótese que, sendo verdadeira, obriga o autor a reescrever alguma coisa
que ele conclui. Erro de português, número que diverge de um dígito e numeração de
quadro não interessam.

**Não segure hipótese por falta de certeza.** A conferência vem depois, é de outra voz
e é barata. Hipótese que cai na conferência é resultado, não erro seu.

## Saída

Grave em `LEITURA-INTRODUCAO.md` e devolva no texto final a lista numerada dos títulos.

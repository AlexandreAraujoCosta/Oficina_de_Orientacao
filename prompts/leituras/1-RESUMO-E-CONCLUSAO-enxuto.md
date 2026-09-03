# Leitura 1 — do resumo e da conclusão até o dado

Opus. Paralela às leituras 2 e 3.

---

Você lê um trabalho acadêmico já concluído. Sou membro da banca. Não abra relatório,
cotejo ou conferência anterior sobre ele.

## Material

- `MAPA.md` — resumo, palavras-chave, abstract, introdução, títulos de seção, legendas
  de figuras e tabelas, apêndices, conclusão e referências, com [P###] e página.
- `extracao/trabalho.txt` — texto completo numerado. Não leia inteiro; use `Grep`.
- `trabalho.pdf` — `Read` com faixa de páginas só para ver tabela ou figura, até três
  vezes.

## Passo 1 — filtrar a conclusão

Classifique cada asserção da conclusão em RETOMADA, ACHADO, TESE, ARGUMENTO,
DISCUSSÃO ou LIMITAÇÃO. Só ACHADO e TESE contam. Devolva a lista numerada, cada um com
localizador e em uma frase. É a lista de alvos do passo 3.

## Passo 2 — contra o resumo

Mesma classificação no resumo. Depois:

**A.** O que o resumo afirma e a conclusão não sustenta. Procure no corpo antes de
declarar ausência.

**B.** O que a conclusão afirma e o resumo não anuncia. Marque estes como úteis ao
autor e inertes para a banca.

**C. Divergência de alcance na mesma afirmação**, e é o achado mais valioso do passo:
uma generaliza e a outra restringe, uma quantifica e a outra não, uma dá um número e a
tabela dá outro. **Confira contra a tabela de onde o número saiu, não contra a outra
peça de texto.**

Sobre o abstract, a pergunta não é se traduz o resumo: é se o que ele afirma se
sustenta. Caso medido: um resumo dizia que 68 decisões resultaram de sorteio e o
abstract dizia `68 judicial decisions were randomly selected`, e sortearam-se 125, das
quais 57 foram excluídas depois.

## Passo 3 — de cada asserção forte até o dado

Pergunte o que sustenta a asserção, ache a passagem, pergunte de novo dela. Até três
saltos ou até o término:

**DADO** (tabela, contagem, trecho do corpus) · **FONTE** (doutrina ou norma; basta
para tese, não para achado) · **ASSERÇÃO** (outra afirmação que também não desce a
dado; diga onde parou) · **NADA**.

Marque à parte a cadeia **estreita** (o suporte sustenta um recorte e a asserção fala
do todo) e a que termina em dado que **contradiz** a asserção. **Relate as linhas
separadas, nunca somadas**: é a soma que diverge entre auditorias.

Dois casos medidos, para calibrar os términos. "Segurança jurídica" arrolada entre os
valores mobilizados, com a expressão ocorrendo uma única vez no trabalho e sendo a
própria frase da conclusão: NADA. Teses que devolvem como achado a pressuposição
escrita na definição da categoria antes de aplicá-la, de modo que a contagem mede o
recurso linguístico e não a pressuposição: ASSERÇÃO.

## Filtro

Só entra o que, sendo verdadeiro, obriga o autor a reescrever algo que ele conclui,
ainda que seja a conclusão de um capítulo. Erro de português e numeração de tabela não
entram. Não segure hipótese por falta de certeza: a conferência vem depois, é de outra
voz, e hipótese que cai lá é resultado.

## Três regras

1. **Controle positivo** antes de qualquer afirmação de ausência, declarado. Neste
   ambiente: `grep -o` com `-i` e `-F` juntos devolve vazio, embora `-oi` e `-oF`
   funcionem; classe entre colchetes com letra acentuada falha (`estrat[ée]gia` acha zero, `estratégia` acha); ponto de expressão regular não casa letra acentuada; busca sem fronteira
   de palavra casa dentro de outra ("segurança" dentro de "insegurança"); e buscar o
   singular acha zero onde o plural existe.
   Quatro defeitos novos, medidos em 03/09/2026, e os quatro produziram acusação
   falsa: ancorar `^\[P` na extração perde os parágrafos cuja linha começa por
   `##`, `**` ou `> ` (839 em lugar de 886); buscar sem ignorar a caixa perde a
   ocorrência que abre frase (zero em lugar de doze); contar parágrafo de `.docx`
   por `<w:p[ >].*?</w:p>` perde os auto-fechados com atributo (990 em lugar de
   999); e remover acento antes de contar faz *controvérsia* entrar numa contagem
   de *controvers* (20 em lugar de 9). `grep -c` conta linhas, não ocorrências.
   Onde houver Python, use `scripts/contagem.py`, que traz isso em código e se
   recusa a carregar se o próprio autoteste falhar.

2. **Alcance declarado**: o que leu e o que não leu.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor.

## Saída

`LEITURA-RESUMO-CONCLUSAO.md`. No texto final: quantas asserções fortes, a contagem
por término com as linhas separadas, e a lista das divergências de alcance e dos
términos NADA e ASSERÇÃO.

# Estado do método de leitura acadêmica

**03/09/2026.** Este arquivo existe para que a próxima sessão comece lendo, e não
reconstruindo a conversa. Traz o desenho congelado, a medição que sustenta cada
escolha, o que foi derrubado, o que não está medido, e onde parou cada trabalho.

---

## 0. O que mudou em 03/09/2026

**São duas ferramentas, e não uma.** O pipeline daqui é a leitura completa. Ao lado dele
existe agora `prompts/ALBERTO.md`, o relatório rápido: uma leitura, o mesmo formato de
oito partes e uma revisão quando roda no agente. O "um a três minutos" que este
arquivo trazia era da ferramenta anterior de mesmo nome, a conferência de
consistência, e não se transfere: medido em 04/09/2026, o Alberto no chat levou
15 minutos e 52 segundos numa tese de 109 páginas. O nome era da
conferência de consistência, que passou a `prompts/CONSISTENCIA.md`.

**O `prompts/LUIS.md` foi aposentado**, e o que ele tinha e o pipeline não tinha veio para
cá: a sugestão de desenvolvimento com a âncora, o reenquadramento, a sugestão que
nunca é determinação, o ponto que o autor não pode alterar, a lista de decalques, o
vocabulário de trabalho que não sai no relatório e a estabilidade dos códigos de item
estão em `6-TRIAGEM-E-REDACAO.md`; a trava dos termos de arte da prática forense está
em `5-VERIFICACAO.md`; o resto da calibragem do campo está em `CALIBRAGEM-DIREITO.md`.
**Ele continua servindo a um caso só**, a leitura de projeto de pesquisa, porque
`prompts/PROJETO.md` é camada fina sobre ele e o pipeline não tem equivalente: as leituras
1 e 3 pedem conclusão e dados, que um projeto não tem. Escrever essa camada sobre o
pipeline está pendente.

**A medição sobre a leitura única, e ela foi lida errado antes de ser lida certa.**
Uma passada só de dez mil palavras teve quatorze quedas em sessenta e sete afirmações,
e a primeira conclusão foi pôr teto de itens no Alberto. Lidas uma a uma, **doze das
quatorze derrubam o endereço, a contagem ou uma afirmação acessória, e o apontamento
continua de pé**; duas matam o achado. Sobre vinte e seis itens, dois eram falsos. O
teto saiu. **O que a extensão degrada é o endereço, e não o achado**, e cortar item
para comprar precisão é o defeito que aposentou o monolítico.

**Duas rodadas curtas do mesmo prompt, sobre a mesma dissertação**, deram dezessete e
doze itens com seis em comum, e dezessete endereços comuns em setenta e cinco. As
vinte e nove afirmações foram abertas na fonte e as vinte e nove estavam certas. A
leitura rápida vê pouco e não inventa; a perda é de cobertura e de justificação.

**Uma manutenção:** `scripts/sincronizar_decalques.py` estava quebrado desde antes
(o filho herdava a codificação do console e a saída acentuada quebrava na leitura como
UTF-8, e `stdout` voltava vazio). Corrigido, e os alvos agora são o `CLAUDE.md` e o
passo 6 daqui.

**O `prompts/leituras/` entrou no git.** Estava fora, e não por estar ignorado: nunca
fora adicionado. Ao adicionar, a seção que dizia onde parou cada trabalho saiu daqui
para o `ANDAMENTO.md`, que fica **fora** do git, porque identifica trabalho por quem o
escreveu e o repositório traz a maquinaria e nunca o material. **Medição que entrar
neste arquivo identifica o trabalho pelo gênero e pelo tamanho.**

---

## 1. O desenho

**Preparo, por programa e sem modelo.**
`scripts/extrair.py` produz a extração numerada. `scripts/mapa_estrutural.py` produz
o mapa (resumo, palavras-chave, abstract, introdução, títulos de seção, legendas de
figuras, apêndices, conclusão **e lista de referências**), com controle positivo que
aborta se o extrator perder parágrafo. `scripts/grafo_capitulos.py` mede irrigação
entre capítulos. `scripts/conferir_planilha.py` conta registros de planilha
reproduzida.

**Quatro leituras, as três primeiras em paralelo.**

| | parte de | acha | modelo |
|---|---|---|---|
| 1 · resumo e conclusão | o que o trabalho afirma | afirmação sem lastro | Opus |
| 2 · introdução | o que ele promete | promessa não cumprida, ressalva atravessada | Opus |
| 3 · figuras | os dados | resultado desperdiçado, narrativa contra tabela | Opus |
| 4 · peso | os candidatos das três | se a contribuição é nova, e para quem | Opus |

A 4 roda depois das outras e **é a única que usa a web**.

**Depois: verificação (Sonnet), triagem e redação (Opus).**

Custo: por volta de 1,2 milhão de tokens e 55 minutos de relógio, com as três
primeiras em paralelo.

---

## 2. O que sustenta cada escolha

**O prompt antigo suprimia achado.** `LUIS.md`, 22.538 palavras, devolveu **dois
itens e nenhum de conteúdo** numa dissertação inteira, depois de derrubar oito
hipóteses. As travas contra falso positivo derrubavam o achado verdadeiro junto.
**Por isso as travas saíram do levantamento e ficam só na verificação.**

**O mapa basta.** Numa comparação, dos onze apontamentos que só a travessia
sequencial produziu, **um** exigia percorrer o texto. O mapa é 12% a 25% do trabalho.

**As referências no mapa não são detalhe.** Sem elas, duas leituras ficaram cegas
para citações que não fecham com a lista. Controle do defeito: no mapa antigo,
`REFER` = 0 e `Reboul` = 0. Corrigido, a leitura 2 achou quatro problemas de citação,
um deles na única fonte da premissa que sustenta um recorte inteiro.

**Ler as figuras se paga.** Quatro dos dezessete itens de uma leitura dependiam da
imagem. E numa leitura de 77 figuras, o maior achado do trabalho foi uma frase de
tópico que diz o contrário do gráfico.

**Ler todas as figuras antes de qualquer prosa.** A repetição entre figuras distantes
só aparece com as duas à vista, e a prosa lida antes faz ler a figura pelos olhos
dela.

**Verificação em Sonnet.** Duas rodadas de Sonnet replicaram entre si (17 e 16
confirmações em 20, derrubando o mesmo item). É o passo com mais chamadas, e é onde a
troca de modelo economiza.

**Levantamento em Opus.** No mesmo pedido, o Sonnet devolveu 14 asserções fortes
contra 19, duas divergências de alcance contra sete, e perdeu os dois achados fora do
pareamento, economizando 13%.

**Uma rodada só perde de 35% a 40%.** Duas rodadas idênticas têm identidade estrita
de 42% a 45%, e a união é de 20 a 23 assuntos, dos quais oito exclusivos.

---

## 3. Derrubado, e não voltar a tentar

**O dossiê de candidatos por item.** Corta as chamadas pela metade (22 contra 45) e
custa 29% mais tokens (243 mil contra 188 mil), porque volta inteiro a cada turno.
Uma versão com oito candidatos, e não vinte, nunca foi medida.

**Os perfis da nuvem como triagem de itens.** Quatro dos cinco itens marcados como
deslocando conclusão não trazem termo nenhum do perfil. O perfil diz qual termo
sustenta conclusão, e não qual item a desloca.

**O agrupamento por sentido como detector.** A partição acerta (separa o uso definido
do uso frouxo), e a medida de separação não discrimina: contra treze outros termos, o
termo defeituoso ficou em décimo de catorze.

**As embeddings para recuperação.** `multilingual-e5-small` deu 32% no top-5 contra
50% do TF-IDF, e a fusão por posto recíproco não recupera. O léxico puro vence, com
teto de 68% no top-20.

**O par defesa e acusação como substituto das duas rodadas.** Não reproduz a
variância que substituiria: erra os três alvos conhecidos. Fica pela ordenação em
quatro células, que é boa.

---

## 4. O que não está medido

**Se o desenho atual bate o pedido cru.** A única medição disso deu **não** (2,5 vezes
os itens por três vezes o custo), e mediu a configuração antiga: levantamento livre,
passos separados, mapa sem referências. O desenho atual é outro. **É a medição que
importa, e a primeira da lista.**

E mais seis, em `memory/medicoes-pendentes.md`.

**Uma medição saiu confundida por erro meu:** a do enxugamento dos prompts. Cortei
texto e cortei os casos de calibragem na mesma rodada, e o que medi foi enxugar mais
tirar o limiar. O resultado (zero términos NADA contra dois) informa a direção, e não
separa as duas causas.

---

## 5. Defeitos deste ambiente, todos medidos

Cada um já produziu, ou quase produziu, acusação falsa.

1. `grep -o` com `-i` **e** `-F` juntos devolve vazio; `-oi` e `-oF` funcionam
   isolados. Sem controle, uma comparação teria reportado 33 ausências falsas.
2. Classe entre colchetes com letra acentuada falha: `estrat[ée]gia` devolve zero
   onde `estratégia` acha.
3. Ponto de expressão regular casa um byte, e letra acentuada ocupa dois: `ap.ndice`
   não acha "apêndice".
4. Busca sem fronteira de palavra casa dentro de outra: "segurança" dentro de
   "insegurança". **Aplicar a fronteira produziu um achado real.**
5. Buscar o singular acha zero onde o plural existe.
6. Extração de `.docx` e de PDF parte um parágrafo em dois, e expressão que varre
   parágrafo quebra onde há parágrafo dentro de parágrafo.

---

## 6. Onde parou cada trabalho

Está em `ANDAMENTO.md`, nesta mesma pasta, **e fora do git**: aquele arquivo
identifica trabalhos por quem os escreveu, e o repositório traz a maquinaria e
nunca o material. Quem retoma a rodada abre os dois.

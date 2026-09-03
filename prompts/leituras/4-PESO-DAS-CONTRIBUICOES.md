# Leitura 4 — o peso das contribuições

**Não é verificação de defeito, e por isso não cabe no passo 5.** Verificar um defeito
é perguntar se o texto diz o que o item afirma. Pesar uma contribuição é perguntar
outra coisa: **isto é novo, e para quem?** A resposta não está no trabalho, e é o
único passo em que a busca na web se paga.

**Roda depois das leituras 1, 2 e 3**, sobre o que elas marcaram como contribuição ou
como resultado inexplorado.

---

Você recebe candidatos a contribuição, levantados por outras vozes sobre um trabalho
acadêmico. Sua tarefa não é confirmar que existem no texto, e sim decidir **quanto
valem**.

## O material

- `LEITURA-RESUMO-CONCLUSAO.md`, `LEITURA-INTRODUCAO.md`, `LEITURA-DADOS.md` — o que
  cada uma marcou como contribuição não reivindicada ou resultado inexplorado.
- `extracao/trabalho.txt` e `trabalho.pdf`, para conferir o que for preciso.
- **A web.** Use busca para responder à pergunta que o trabalho não responde.

## As duas espécies, e elas não se misturam

**Resultado que está nos dados e não está no texto.** Exige que o autor calcule e
escreva. Custa trabalho.

**Contribuição que está no texto e não é anunciada como tal.** Exige uma frase na
conclusão, e às vezes a submissão como produto técnico. Custa uma linha.

Separe as duas na saída: numa lista só, a seção deixa de servir como lista de
providências.

## Passo 1 — isto já existe?

Para cada candidato, procure se a afirmação já está na literatura, **inclusive na que
o próprio trabalho cita**. Caso medido: a afirmação principal de um capítulo empírico já estava
em dois trabalhos que ele próprio referenciava, e o que o tornava publicável eram três
resultados secundários que ele não havia calculado.

Três respostas, e a segunda é a mais valiosa:

- **JÁ EXISTE** — outro trabalho já afirma isso. Dê a referência. Não é contribuição,
  e o autor precisa saber antes da banca.
- **CONTRARIA O QUE EXISTE** — o dado do trabalho vai contra o que a literatura
  afirma, ou contra documento oficial que o próprio trabalho endossa. **É a
  contribuição mais forte que um trabalho empírico pode ter, e a que os autores mais
  deixam passar.**
- **NÃO ENCONTREI** — declare o que buscou e onde, para que a ausência signifique
  alguma coisa.

## Passo 1b — há produto autônomo aqui?

Produto autônomo é o que **outra pessoa reutiliza sem se importar com a tese deste
trabalho**. É esse o teste, e ele separa o produto da ilustração do argumento.

Cinco tipos, e os cinco costumam estar no trabalho sem que ninguém os nomeie.

**Base de dados construída.** O corpus com as variáveis codificadas, registro a
registro. Vale como depósito em repositório e como artigo de dados. Caso medido: um
apêndice reproduzia 136 acórdãos com catorze variáveis e a conclusão não o mencionava
uma vez.

**Esquema categorial original.** A tipologia que o trabalho criou para codificar o
material, com a proposição de cada categoria e a descrição do que ela abrange. Se
outro pesquisador pode aplicá-la a outro recorte, a outro tribunal ou a outro período,
é instrumento e não tabela de resultado. Caso medido: um quadro de catorze categorias
argumentativas era tratado como resultado da pesquisa, quando é a régua com que ela
mediu.

**Modelo ou protocolo de análise.** O procedimento documentado a ponto de ser repetido:
o comando de extração, os critérios de inclusão, os passos de codificação, o que se
faz nos casos duvidosos.

**Diagnóstico de base pública.** É o mais invisível dos cinco. Toda pesquisa empírica
que depende de acervo oficial acumula conhecimento sobre os defeitos daquele acervo:
campo que não confere com o conteúdo, indexação que não permite discriminar o que se
precisa, duplicidade sistemática, filtro que não filtra, série que muda de critério no
meio. **O trabalho registra isso como obstáculo do percurso e nunca como achado**, e é
achado: serve à instituição que mantém a base, à comunidade que vai usá-la depois, e
com frequência é a única contribuição do trabalho que tem destinatário fora da
academia. Casos medidos: um trabalho excluiu mais de cinco mil decisões por não
conseguir discriminá-las pela indexação disponível; outro registrou, no próprio
apêndice, um registro cuja coluna de unidade federativa contradizia o conteúdo da
decisão.

**Proposta normativa ou anteprojeto.** Texto redigido com justificação dispositivo por
dispositivo, que existe fora do argumento que o motivou.

Para cada um que houver, diga: **quem o reutiliza, para quê, e o que falta para ele
sair do trabalho** (depósito, licença, dicionário de variáveis, descrição do
procedimento).

**Se o programa for mestrado profissional, isto deixa de ser oportunidade perdida.** O
produto técnico é exigência formal, e um produto que existe no trabalho sem ser
nomeado como produto é lacuna de cumprimento, não só de reivindicação.

## Passo 2 — o peso

Para cada candidato que sobreviver, responda em uma oração: **quem passa a saber o
quê, depois que isto for reivindicado?** E classifique o destino:

- **CONCLUSÃO** — basta reivindicar no texto que já existe.
- **CÁLCULO** — o resultado existe nos dados e precisa ser produzido.
- **PRODUTO** — base, protocolo, esquema de codificação ou anteprojeto que vale como
  entrega própria, e não como ilustração do argumento.
- **ARTIGO** — sustenta publicação separada. Diga qual é a pergunta do artigo e qual
  o resultado que o sustenta, e **diga se ele basta**: um candidato cuja afirmação principal já
  está na literatura não vira artigo por ser interessante.

## Três regras

1. **Controle positivo.** Busca que não acha nada não prova ausência. Antes de
   escrever "não encontrei", mostre que a mesma busca acha o que você sabe existir.
   Quatro defeitos novos, medidos em 03/09/2026, e os quatro produziram acusação
   falsa: ancorar `^\[P` na extração perde os parágrafos cuja linha começa por
   `##`, `**` ou `> ` (839 em lugar de 886); buscar sem ignorar a caixa perde a
   ocorrência que abre frase (zero em lugar de doze); contar parágrafo de `.docx`
   por `<w:p[ >].*?</w:p>` perde os auto-fechados com atributo (990 em lugar de
   999); e remover acento antes de contar faz *controvérsia* entrar numa contagem
   de *controvers* (20 em lugar de 9). `grep -c` conta linhas, não ocorrências.
   Onde houver Python, use `scripts/contagem.py`, que traz isso em código e se
   recusa a carregar se o próprio autoteste falhar.

2. **Alcance declarado.** Diga o que buscou, onde, e o que ficou fora do seu alcance.
3. **Hipótese sua que caiu é resultado**, e diga **onde estava o que a salvou**: no próprio parágrafo, num apêndice, noutro capítulo, ou só depois de você refazer a conta. Essa localização decide se a queda vira sugestão ao autor. Inclusive quando ela caía a favor do autor.

## Saída

Grave em `PESO-DAS-CONTRIBUICOES.md`, com as duas espécies separadas e, para cada
candidato, a resposta do passo 1 com a referência quando houver.

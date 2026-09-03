# O que roda, o que se faz à mão, o que não se afirma

Esta oficina roda em mais de um assistente, e a divisão do trabalho entre a
máquina e a pessoa muda com o que o assistente tem. **A divisão não se decide
pelo nome do produto**, que muda de mês em mês e de plano para plano: decide-se
por três capacidades, e você descobre quais tem em dois minutos.

**Este documento não ensina a operar agenticamente.** Ensinar isso produziria
cópia mal-adaptada, que é o pior resultado possível: a saída sai com a mesma
forma e sem a camada que a sustenta, e a forma sinaliza rigor que não está lá.

## Descubra o que a sua ferramenta tem, antes de escolher a cadeia

**1. Ela executa comandos no terminal?** Peça que rode `python --version` e mostre
a saída. Se rodar, a coluna 1 inteira é dela. Se não, você roda os programas por
fora e cola as saídas, e a análise continua possível, com mais trabalho seu.

**2. Ela abre uma leitura independente, que não vê esta conversa?** É o que aqui
se chama subagente. Peça-lhe que abra uma e lhe faça uma pergunta que só se
responde lendo um arquivo que você **não** mencionou nesta conversa. Se não
tiver, a segunda voz vira procedimento manual, descrito na coluna 2, **e não
desaparece**.

**3. Quanto ela aguenta antes de perder o começo?** A cadeia completa do Luis
tem cerca de 560 mil tokens em dezenas de passos. Se a sua ferramenta não
sustenta isso, rode o **Alberto**, que confere consistência e localiza
suspeitas, e deixe o Luis, que julga o argumento, para uma ferramenta que
alcance.

**O modelo por trás também importa, e não é detalhe.** Conferir o que já foi
localizado é tarefa que modelo pequeno faz bem; julgar se um argumento se
sustenta, não. Abra o seletor de modelos e veja o que a sua conta oferece hoje:
os planos mudaram em 2026 e continuam mudando, e o que valia para um plano não
vale para outro. **Não presuma pelo nome do plano; olhe o seletor.**

### Uma advertência sobre este documento

O que está aqui vale por capacidade, e não por produto. Quando ele foi escrito,
a única via medida era a de um assistente com terminal, arquivos, subagentes e
orçamento largo. **Se a sua ferramenta tem as três capacidades acima, siga a
cadeia completa**, e a coluna 2 encolhe para quase nada. Se tem só a primeira, a
coluna 2 é sua. A coluna 3 vale sempre, em qualquer ferramenta e em qualquer
plano.

---

## Coluna 1 — O que a ferramenta roda

Tudo o que é programa, se ela tem terminal. A regra da oficina vale igual: **onde existe programa, rode o programa.** Os scripts localizam
suspeitas em segundos e não erram; o julgamento de cada uma é que é seu.

- A extração canônica e o mapa do trabalho.
- A conferência de citações contra a fonte.
- A inserção dos trechos no relatório, por localizador.
- A montagem da entrega, o `.docx` comentado e o PDF.
- As buscas com controle, que são a espinha da coluna 3.

**Uma dependência que costuma faltar:** os programas pedem Python e alguns
pacotes. Se o terminal reclamar de importação, é isso, e resolve-se instalando,
não contornando com o modelo. **Programa que não roda não vira julgamento do
modelo:** ou se instala a dependência, ou se declara que aquela conferência não
foi feita.

---

## Coluna 2 — O que a pessoa faz à mão, quando a ferramenta não tem

**Se a sua ferramenta abre leitura independente e sustenta a cadeia, esta coluna
quase não existe:** o assistente faz tudo isto sozinho, e o que sobra para você
é decidir item a item o que a conferência devolver. O que segue é para quando
falta alguma das capacidades.

### A segunda voz, e é a que mais importa

Toda conferência desta oficina depende de uma voz que **não escreveu** o que
está conferindo. Quem escreveu o apontamento é o pior juiz de se ele se entende,
e a conferência feita na mesma conversa mede outra coisa.

Sem subagente, o substituto existe e é procedimental:

1. Abra **uma conversa nova**, de propósito, na mesma ferramenta ou noutra.
2. Entregue **só o artefato a conferir** e o prompt de conferência.
3. **Não cole o histórico**, não entregue o trabalho analisado, não resuma o que
   já se concluiu. Com o material em mãos, o conferidor reconstrói o que o
   apontamento quis dizer, que é justamente o que se está medindo.
4. A tabela que ele devolver volta para você, que decide item a item. **Só se
   mantém como está o item que já responde à objeção**; achar a objeção indevida
   não basta, porque quem escreveu sempre acha.

Isso vale para as três conferências da oficina: a de compreensibilidade dos
apontamentos, o cotejo que tenta derrubar uma leitura, e a leitura fria de um
documento que cresceu por acréscimo.

**A tentação a resistir é uma só:** continuar na mesma conversa porque ali o
modelo "já tem contexto". É exatamente o contexto que invalida a conferência.

### O que depende de ver, e o modelo não viu

Se você entregou só o `.docx`, o modelo **não viu as figuras**. Ele não pode
descrever, deduzir nem conferir nenhuma. Extraia as imagens e abra uma a uma, ou
declare que a análise não alcançou as figuras. As duas saídas são honestas; a
terceira, que é descrever a figura pela legenda, não é.

### O que a extração de texto não carrega

Realce, comentário e nota de rodapé do Word não aparecem na extração em texto
puro. Isso já produziu, nesta oficina, uma acusação contra um parágrafo cuja
nota de rodapé trazia exatamente o que se dizia faltar, e por duas vezes fez
contar zero marcador de pendência num documento cheio deles. **Antes de acusar
qualquer coisa de descuido, abra o `.docx` como zip e leia `word/comments.xml`,
`word/footnotes.xml` e as marcas de realce em `word/document.xml`.** Boa parte do
que parece descuido está marcada pelo autor, ou já é pergunta que ele fez ao
orientador.

---

## Coluna 3 — O que não se afirma, porque não se conferiu

Esta coluna não depende de ferramenta nenhuma. Ela é a disciplina, e é o que
separa uma leitura de uma impressão.

### Controle positivo em toda busca, e ele é de graça

**Antes de afirmar que algo falta, procure junto uma coisa que você sabe estar
lá, e relate os dois resultados.** Sem isso, o zero de uma busca quebrada tem
exatamente a mesma cara do zero de uma coisa inexistente.

Não basta "procurar duas vezes com termos diferentes": duas buscas quebradas do
mesmo jeito devolvem zero duas vezes. O que prova que o instrumento funciona é
ele achar o que existe, na mesma execução.

Defeitos já medidos nesta oficina, cada um responsável por pelo menos uma
acusação falsa:

- `grep -c` conta **linhas**, não ocorrências.
- `grep -o` com `-i` e `-F` juntos devolve vazio.
- O ponto da expressão regular não casa letra acentuada, porque ela ocupa dois
  bytes.
- Busca sem fronteira de palavra acha a cadeia dentro de outra: "segurança"
  dentro de "insegurança", e um verbo dentro da prosa contado como se fosse
  título de seção.
- Busca no singular devolve zero onde só existe o plural.
- `grep` sem `-i` distingue caixa, e "INTRODU" não acha "Introduction".
- Buscar o **termo** em vez da **coisa**: procurar "segunda voz" devolve zero num
  documento que diz "abra um subagente".

### Alcance declarado junto com o resultado

Diga o que foi medido, sobre que material, e o que ficou de fora. Medição sem
alcance declarado lê-se como cobertura total.

### Hipótese que caiu é resultado, e vai dita

Se você suspeitou de algo e a suspeita não se sustentou, escreva a suspeita e o
que a derrubou. Isso não é confissão de erro: é o que mostra que houve teste.

### Transcrição só por programa

Você indica o parágrafo; o programa copia o texto e o insere. **Nunca digite
trecho do trabalho.** Citação com uma palavra trocada é o defeito mais grave numa
análise que se pretende verificável, e é o mais fácil de cometer.

### O que você não pode dizer

- Que uma referência existe, se não a abriu.
- Que algo não existe no trabalho, se a busca não passou por controle positivo.
- Que uma figura mostra X, se recebeu só o texto.
- Que o autor foi descuidado, se não abriu os comentários e realces dele.
- Que o trabalho está pronto para o passo seguinte, se essa é decisão de quem
  orienta e de quem examina.

---

## O que ainda não foi medido

**Nada disto foi rodado de ponta a ponta fora do assistente em que a oficina foi
construída.** O que está acima decorre das capacidades, e não é relato de
execução. Três números decidem, e nenhum existe:

1. **O que a conta oferece no seletor de modelos**, e por plano, porque o de
   estudante e o pago diferem, e os dois mudaram em 2026.
2. **Se a ferramenta abre leitura independente**, o que decide se a coluna 2 é
   procedimento ou desaparece.
3. **Quanto da cota uma cadeia consome num trabalho inteiro**, que decide entre
   rodar o Alberto e rodar o Luis.

Quem rodar primeiro, anote os três, com o nome e o plano da ferramenta ao lado:
sem isso a medida não se transporta, porque estes produtos mudam de capacidade
sem mudar de nome.

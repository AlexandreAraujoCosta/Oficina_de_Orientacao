# Rodada: o Warat realizado contra o Alberto, sobre o TCC de 09/09

Este arquivo é o pedido que se cola numa sessão do Claude Code aberta em
`D:\Claude\Oficina_de_Orientacao`. A sessão pode ser em Sonnet: ela só opera; as
leituras rodam nos tipos de agente `alberto` e `warat-realizado`, que fixam Opus.
A proposta, os falsificadores e a razão de tudo estão em
`prompts/PROPOSTA-20260913-pontas-contra-o-realizado.md`, e o pedido abaixo não
os repete: lê-se aquele arquivo antes de começar.

---

## O pedido, para colar

Você opera uma rodada de medição da Oficina de Orientação, em
`D:\Claude\Oficina_de_Orientacao`. Leia antes, inteiros:
`prompts/PROPOSTA-20260913-pontas-contra-o-realizado.md` (a hipótese e os
falsificadores, seções 8 e 9), `prompts/MUDANCAS.md` da linha "## 13/09/2026" em
diante (o protocolo da rodada anterior, que este repete) e
`prompts/CLASSIFICAR-RELEVANCIA.md`. Não altere prompt nenhum durante a rodada.

**0. Antes de tudo, o estado do repositório.** Em 13/09 à noite, `prompts/MUDANCAS.md`
e `prompts/leituras/ESTADO.md` apareceram na árvore de trabalho **sem** o registro da
rodada de 13/09 que o commit `fd29229` gravou (algo os reescreveu às 17h19 com a
versão anterior; os programas de 10/09 em `D:\Claude\Oficinas` não rodaram nesse
horário, e a causa não foi achada). Foram restaurados na mesma noite, e a ficha do
Warat realizado já está no fim do `MUDANCAS.md`. Confira que continua assim:

```
grep -n "^## 13/09" prompts/MUDANCAS.md
```

Têm de sair **duas** linhas, a da rodada de 13/09 e a do Warat realizado. Se
faltar alguma, o diff contra o HEAD diz o que sumiu (`git diff --stat`), e
`git restore` sobre os dois arquivos devolve o commit; a ficha do Warat realizado
está também no fim deste arquivo, para reanexar. Registre no relatório da rodada se
isso aconteceu de novo, porque seria a segunda vez.

**1. Gere e confira os prompts e os tipos de agente**, sem editar nada à mão:

```
python scripts/gerar_warat.py --conferir --todas
python scripts/gerar_agente.py --conferir --tambem D:\Claude\TCC
python scripts/faixas_localizadores.py --autoteste
python scripts/relevancia.py --autoteste
```

Todos têm de dizer "em dia" ou "ok". Se algum estiver desatualizado, gere de novo
com o mesmo programa sem `--conferir` e registre no relatório da rodada que isso
aconteceu.

**2. Monte duas pastas isoladas, uma por braço.** Em 08/09 duas rodadas paralelas
gravaram na mesma pasta e uma sobrescreveu a outra. Crie
`D:\Claude\TCC\rodadas\k-20260914\alberto\` e
`D:\Claude\TCC\rodadas\k-20260914\warat-realizado\`, e copie para **cada
uma** só isto, de `D:\Claude\TCC`: `MATERIAL-k.md`, `k-v8-aceito.docx`,
`extracao/k-v8-aceito.txt` (mantendo a subpasta `extracao/`) e `MAPA-k.md`.
**Nada mais**: nenhum relatório, leitura, cotejo, margem ou entrega anterior sobre
este trabalho entra nas pastas, e o pedido a cada agente diz para não abrir nada
fora da pasta dele. Não há PDF nem imagens neste trabalho (o `.docx` tem zero
figuras), e o operador já sabe lidar com isso.

**3. Dispare os dois braços em paralelo, com pedido de duas linhas cada**, porque o
pedido que repete exigências do prompt mede a si mesmo (`scripts/gerar_agente.py`
explica). Um agente do tipo `alberto` e um do tipo `warat-realizado`, cada um com
este pedido, trocando só a pasta e o nome do arquivo:

> Leia o trabalho em `D:\Claude\TCC\rodadas\k-20260914\<braço>\MATERIAL-k.md`
> (extração em `extracao\k-v8-aceito.txt`, arquivo original `k-v8-aceito.docx`,
> na mesma pasta; sem PDF e sem figuras). Grave o relatório em
> `RELATORIO-<braço>-k.md`, o bloco em `RELATORIO-<braço>-k.itens.json` e o
> registro em `REGISTRO-<braço>-k.md`, todos nessa pasta, e não abra nada fora dela.

Anote de cada braço o relógio e, se a saída do agente trouxer, os tokens. Se um
braço cair por limite de sessão, retome-o e escreva que o tempo dele não se mede,
como em 13/09.

**4. A linha de base, que não existe para este trabalho.** A rodada de 13/09 mediu
outra dissertação. Classifique por voz cega (um agente Opus que **não recebe o
trabalho** e recebe o relatório com o nome da ferramenta apagado e um código
sorteado) os três relatórios: `D:\Claude\TCC\RELATORIO-LUIS-k.md` (a linha de
base) e os dois novos. Para apagar o nome, copie cada um como `R-<código>.md` e
troque, por programa, as palavras Alberto, Warat, Luis e "realizado" no título por
"a leitura"; confira com `grep -c` que sumiram. O pedido à voz cega é o
`prompts/CLASSIFICAR-RELEVANCIA.md` inteiro mais uma linha com o caminho do
arquivo. Depois:

```
python scripts/relevancia.py <relatório> <classificação>
```

para cada um. Se `relevancia.py` acusar códigos só na prosa ou só na
classificação, é o leitor de prosa perdendo item (defeito registrado em 13/09, na
fila): conte então pelo bloco `.itens.json`, diga que contou por ele, e não
conserte o leitor no meio da rodada.

**5. O falsificador da paráfrase.** No relatório do Warat realizado e no registro
dele:

```
python scripts/faixas_localizadores.py RELATORIO-warat-realizado-k.md --secao "O que o trabalho fez" --faixa metodo=63-96 --faixa resultados=99-207 --faixa apendices=265-782
python scripts/faixas_localizadores.py REGISTRO-warat-realizado-k.md --faixa metodo=63-96 --faixa resultados=99-207 --faixa apendices=265-782
```

Dois terços ou mais em resultados mais apêndices é o que se espera; maioria em
método é paráfrase, e a rodada registra isso como resultado.

**6. O cotejo cego entre os dois braços.** Um agente Opus que não escreveu nenhum
dos dois recebe os dois relatórios sem nome (os mesmos `R-<código>.md` do passo 4)
e o `MATERIAL-k.md`, e devolve: os achados que só um dos dois tem, com o
código e o localizador; entre esses, quais mudam conclusão, alcance ou abordagem
(a régua de `CLASSIFICAR-RELEVANCIA.md`); e, sobre cada achado exclusivo, se o
material o sustenta, abrindo o parágrafo. Ele não recebe a proposta nem sabe qual
braço é qual. Peça que declare o alcance e os controles de busca.

**7. Preencha a tabela da seção 8 da proposta, uma linha por medida**, com o
número e a palavra "espera" ou "inútil" ao lado, e mais estas quatro, que só se
leem depois de abrir os relatórios:

- a frase de síntese (o realizado nos apêndices, o corpo discute doze unidades, a
  introdução e a conclusão descrevem outro trabalho) aparece no Warat realizado?
  Onde: decisão, item de corpo, só na seção "O que o trabalho fez", ou em lugar
  nenhum? E no Alberto?
- a seção "O que o trabalho fez" existe, tem no máximo doze linhas, e a tabela de
  duas linhas está lá com as duas contas?
- qual peça cada relatório trata como a dos resultados: a seção 2.4 ou o Apêndice B?
- quantos itens de corpo cada um tem, e quantos deles a voz cega classificou como
  CONCLUSAO ou ALCANCE.

**8. Grave o resultado** como ficha nova ao fim de `prompts/MUDANCAS.md`, com o
título "## 14/09/2026 — o Warat realizado contra o Alberto, sobre o TCC de 09/09",
no formato da ficha de 13/09: o que rodou, as medidas em tabela, cada falsificador
com "dispara" ou "não dispara", o que a rodada não mede e o que a contaminou, os
defeitos de instrumento achados. Identifique o trabalho pelo gênero e pelo tamanho
no `MUDANCAS.md` (o repositório não traz nome de estudante); o nome fica só em
`prompts/leituras/ANDAMENTO.md`, que está fora do git, onde você acrescenta uma
seção "Rodada de 14/09" com as pastas e os arquivos. **Não faça commit**: o
orientador decide.

**9. Diga, ao fim, em uma frase cada:** se a hipótese venceu, caiu ou não se lê com
uma execução; e se o Luis deve receber as seções 1 a 5 da proposta, que é a
decisão que a rodada existe para informar.

---

## A ficha a acrescentar ao `MUDANCAS.md` (passo 0), sem alterar

```
## 13/09/2026 (noite) — o Warat realizado: as pontas lidas contra o que foi feito

**Espécie:** pedido do orientador, sem medição. Nenhum prompt publicado muda: entra
um segundo braço de medição, gerado por programa a partir do `ALBERTO.md`.

**O caso que motivou.** Num TCC de mestrado profissional, documental, com 36
unidades codificadas em apêndice, o relatório do Luis de 09/09 tinha cada pedaço da
incongruência entre introdução, método e resultados como item ou decisão, e não a
frase que os junta; e a avaliação capítulo a capítulo chamou de núcleo a seção que o
autor intitulou resultados, quando o que foi feito está no Apêndice B. Diagnóstico:
o que falta não é ordem, é uma descrição do que a pesquisa realizou, produzida antes
de julgar e usada como referência pelas duas pontas. Proposta inteira em
`PROPOSTA-20260913-pontas-contra-o-realizado.md`.

**O que muda.** `scripts/gerar_warat.py` ganha `--variante realizado`, que grava
`prompts/WARAT-REALIZADO.md`: o `ALBERTO.md` com a seção "A ordem de leitura"
trocada (artefatos; depois a descrição do que foi feito, em sete campos, com o
capítulo de método lido por último; depois resumo, introdução e conclusão lidos
contra a descrição; cruzamento; caminho inverso; inferência) e uma seção nova no
relatório, "O que o trabalho fez", com teto de doze linhas. A seção nova tem 1.190
palavras contra 438 da antiga (+752, cerca de 10% do prompt). Uma substituição
declarada fora da seção: a remissão ao "passo 2" do aparato empírico passa a
"passo 1". `scripts/gerar_agente.py` ganha o tipo `warat-realizado` (Opus, mesmo
operador). `scripts/faixas_localizadores.py` conta localizadores por faixa, com
autoteste, para o falsificador da paráfrase. A variante antiga (`WARAT.md`) sai
idêntica ao que era, conferido pelo próprio gerador.

**O que se espera, em número, e o que mostraria que foi inútil:** a tabela da
seção 8 da proposta, sobre o TCC de 09/09, contra o Luis daquele dia e o Alberto
rodado na mesma rodada, por voz cega. Em uma linha: a frase de síntese aparece como
decisão ou item de corpo, a peça dos resultados na seção 5 é o apêndice, dois terços
dos localizadores da descrição estão em resultados e apêndices, e a relevância no
corpo não cai mais do que a variação medida em 13/09 (quatro itens). Inútil se a
lista de itens sair igual à do Alberto em outra ordem, ou se a descrição citar o
capítulo de método em vez dos artefatos.

**As três perguntas.** (1) A regra produziria o caso: percorrido no papel, sim; o
papel não vale. (2) O que deixa de passar: a busca no corpo por promessa, que a
descrição pode omitir; guarda mantida (não executada exige busca com controle). (3)
Onde repete: o Alberto já lia o aparato antes da prosa; o que a variante acrescenta
é a descrição como referência e a leitura das pontas contra ela.

**Rodou?** Não. Protocolo em `RODADA-20260914-warat-realizado.md`.
```

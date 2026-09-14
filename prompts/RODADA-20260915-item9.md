# Rodada: menos leitura por execução, ou mais execuções (item 9 da fila)

Pedido para colar numa sessão do Claude Code aberta em
`D:\Claude\Oficina_de_Orientacao`. A sessão só opera; as leituras rodam nos tipos
de agente `alberto` e `warat-partes`, que fixam Opus. O protocolo repete o de
`RODADA-20260914-warat-realizado.md` (pastas isoladas, pedido de duas linhas, voz
cega, cotejo cego), e o que está lá não se repete aqui.

**A pergunta.** O Alberto lê o material inteiro quatro vezes numa execução, uma
por passo (registro da execução 1 de 14/09), e duas execuções da mesma leitura se
sobrepõem em 57%. Dá para gastar menos por execução sem perder item de corpo, e o
que uma segunda execução acrescenta vale o que custa?

**Três braços e um controle, todos sobre o mesmo TCC de 09/09.**

| braço | o que é | custo previsto |
|---|---|---|
| controle | uma execução do `alberto` sobre o `MATERIAL.md` inteiro, mais a revisão barata (`enderecos_em_lote.py --tudo` lido por uma segunda voz, como o operador descreve) | cerca de 30 min mais 14 |
| A, partes | uma execução do `warat-partes` sobre as três partes, mais a mesma revisão | menos tokens; relógio a medir |
| B, duas execuções | **não roda leitura nova**: as execuções 1 e 2 do Alberto de 14/09 (`rodadas\k-20260914\alberto\` e `execucao2\alberto\`), fundidas por uma revisão barata que lê os dois relatórios e o material e devolve um só | a revisão, cerca de 15 min; as duas execuções já foram pagas |
| C, passos pulados | **medida, não braço**: sobre cada execução (as duas de 14/09, o controle e A), quantas das perguntas que o prompt manda fazer deixaram vestígio no registro ou no relatório | zero |

---

## O pedido, para colar

Você opera uma rodada de medição da Oficina de Orientação, em
`D:\Claude\Oficina_de_Orientacao`. Leia antes, inteiros:
`prompts/RODADA-20260915-item9.md` (este arquivo), o item 9 de
`prompts/FILA-20260914.md`, as duas fichas de 14/09 em `prompts/MUDANCAS.md` e
`prompts/CLASSIFICAR-RELEVANCIA.md`. Não altere prompt nenhum durante a rodada.
Rascunhos com nome próprio (`item9_<braço>_*`), porque o diretório de rascunho é
compartilhado e em 14/09 um programa foi sobrescrito por outra sessão.

**1. Confira os gerados e os programas.**

```
python scripts/gerar_warat.py --conferir --todas
python scripts/gerar_agente.py --conferir --tambem D:\Claude\TCC
python scripts/partir_material.py --autoteste
python scripts/relevancia.py --autoteste
```

**2. Monte as pastas.** `D:\Claude\TCC\rodadas\k-20260915\controle\` e
`\partes\`, cada uma só com `MATERIAL-k.md`, `k-v8-aceito.docx`,
`extracao\k-v8-aceito.txt` e `MAPA-k.md`, copiados de `D:\Claude\TCC`.
Na pasta `partes`, gere as três partes **com o nome que o prompt usa**:

```
python scripts/partir_material.py D:\Claude\TCC\rodadas\k-20260915\partes\extracao\k-v8-aceito.txt D:\Claude\TCC\rodadas\k-20260915\partes\MATERIAL-k.md -o D:\Claude\TCC\rodadas\k-20260915\partes\MATERIAL
```

Ele imprime as fronteiras (esperado neste trabalho: introdução até [P22),
conclusão em [P209], referências em [P219], primeiro apêndice em [P265]) e diz
que a partição fecha. Depois **apague** `MATERIAL-k.md` da pasta `partes`, para
que o braço A não possa reler o inteiro; o controle fica com o inteiro. Nada de
relatório anterior em pasta nenhuma.

**3. Dispare o controle e o braço A em paralelo**, pedido de duas linhas cada:

> Leia o trabalho em `D:\Claude\TCC\rodadas\k-20260915\controle\MATERIAL-k.md`
> (extração em `extracao\k-v8-aceito.txt`, original `k-v8-aceito.docx`, na
> mesma pasta; sem PDF e sem figuras). Grave `RELATORIO-controle-k.md`, o bloco
> `.itens.json` e `REGISTRO-controle-k.md` nessa pasta, e não abra nada fora dela.

> Leia o trabalho em `D:\Claude\TCC\rodadas\k-20260915\partes\`, repartido em
> `MATERIAL-pontas.md`, `MATERIAL-artefatos.md` e `MATERIAL-apoio.md` (extração em
> `extracao\k-v8-aceito.txt`, original `k-v8-aceito.docx`; sem PDF e sem
> figuras). Grave `RELATORIO-partes-k.md`, o bloco `.itens.json` e
> `REGISTRO-partes-k.md` nessa pasta, e não abra nada fora dela.

Anote relógio, tokens e usos de ferramenta de cada um, como em 14/09. **Anote
também, do registro de cada um, quantas vezes cada arquivo de material foi lido
inteiro**: é a medida direta do que o braço A existe para mudar.

**4. A revisão barata, igual para o controle e para A.** Para cada um:

```
python scripts/enderecos_em_lote.py <RELATORIO>.md <extracao> --tudo
```

e uma segunda voz (Opus, que não escreveu o relatório) lê o arquivo que sai e
aplica a lista da seção "A revisão, e ela é uma só" de `OPERADOR-ALBERTO.md`:
derruba, conserta endereço, não insere item, e grava `REVISAO-<braço>.md` com a
conta de itens caídos e endereços consertados. O relatório revisado é o que vai à
classificação.

**5. O braço B, a fusão.** Uma voz Opus recebe os dois relatórios de 14/09
(`rodadas\k-20260914\alberto\RELATORIO-alberto-k.md` e
`execucao2\alberto\RELATORIO-alberto-k.md`), o `MATERIAL-k.md`, e este
pedido: **funda os dois num relatório só, no formato do Alberto**, mantendo todo
item que ao menos um dos dois tem e que o material sustenta (abra o parágrafo de
cada exclusivo antes de mantê-lo), fundindo os pares que dizem a mesma coisa,
conservando os códigos de origem no registro, e derrubando o que o material não
sustenta. Sem item novo. Grave `RELATORIO-fusao-k.md` e `REGISTRO-fusao.md`
em `rodadas\k-20260915\fusao\`, com a conta: itens de cada origem, pares
fundidos, exclusivos mantidos, derrubados. Anote o relógio e os tokens.

**6. Classificação por voz cega** dos três (controle revisado, A revisado, fusão),
como no passo 4 de 14/09: nome apagado, código sorteado, `CLASSIFICAR-RELEVANCIA.md`
inteiro, `relevancia.py` depois. Se o leitor de prosa perder códigos (defeito
conhecido, item 1 da fila), conte pelo bloco e diga.

**7. Cotejo cego, dois pares:** A contra o controle, e a fusão contra o controle.
Mesma voz que em 14/09 (não escreveu nenhum, recebe os relatórios anonimizados e o
material): achados exclusivos de cada lado com código e localizador; quais mudam
conclusão, alcance ou abordagem; e, para esses, se o material os sustenta.

**8. A medida C, passos pulados.** O prompt do Alberto manda, entre outras coisas:
escrever a medida central em três linhas antes de abrir a primeira figura; montar
a lista do que mudou na janela; fazer as três perguntas que mandam calcular; o
passo cego das figuras (não se aplica aqui, sem figuras); a busca de ausência com
controle. Para cada uma das quatro execuções (as duas de 14/09, o controle e A),
diga se o registro ou o relatório traz vestígio de cada uma (busca por termo com
controle positivo, e leitura do trecho), numa tabela execução por pergunta,
CUMPRIDA, PARCIAL ou SEM VESTÍGIO. **Medido em 14/09 antes desta rodada, com
busca só por termo:** nenhuma das duas execuções tem "medida central" no registro;
a execução 2 tem uma ocorrência no relatório; a execução 1, nenhuma. O ângulo que
a execução 2 achou e a 1 não (o que a contagem de trechos mede) é exatamente o que
essa instrução pede. Confira isso lendo, e não só por termo.

**9. A tabela, com o que se espera escrito antes.**

| medida | espera | inútil se |
|---|---|---|
| A: tokens e leituras inteiras do material | um terço a menos de tokens que o controle; nenhuma leitura inteira do material repetida | tokens iguais ou maiores; ou o registro mostrar o inteiro relido por outra via |
| A: itens de corpo CONCLUSAO+ALCANCE (voz cega) | dentro de quatro itens do controle | abaixo disso, e o cotejo achar item de corpo do controle que A não tem e o material sustenta |
| A: afirmações caídas na revisão | igual ou menor que o controle | maior: a economia comprou erro, como em 07/09 |
| B: itens de corpo CONCLUSAO+ALCANCE validados no cotejo | acima do controle por mais de quatro | dentro de quatro: a segunda execução não paga o dobro |
| B: afirmações derrubadas na fusão | zero item falso mantido no cotejo | item falso mantido |
| C: passos com vestígio | a variância entre execuções cair sobre perguntas pedidas e não cumpridas | todos os passos cumpridos nas quatro e a variância continuar: ela é de descoberta, e instrução obrigatória não a resolve |

Uma execução por braço lê diferença grande. A variação medida em 14/09 entre duas
execuções iguais foi de 25% no custo e de quatro itens no corpo; o que ficar
dentro disso não se lê.

**10. Grave** a ficha "## 15/09/2026 — item 9: menos leitura por execução, ou
mais execuções" ao fim de `prompts/MUDANCAS.md`, no formato das de 14/09, e a
seção de andamento em `prompts/leituras/ANDAMENTO.md`. Sem commit. Ao fim, em uma
frase cada: A entra no Alberto (o material repartido vira o padrão do operador)?
B vira o cardápio (duas execuções fundidas como entrega)? E o que C diz sobre
onde está a variância.

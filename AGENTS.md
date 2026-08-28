# Instruções para assistentes que rodam esta oficina

Este repositório traz ferramentas de leitura automática de trabalhos acadêmicos.
Se você é um assistente com terminal e acesso a arquivos (GitHub Copilot em modo
agente, Claude Code, ou equivalente), estas são as instruções para operá-las.

## As travas, e elas vêm antes de tudo

Estas três não são preferências de estilo. São o que distingue um relatório
conferível de um relatório que parece conferível, e as três falham em silêncio:
o resultado sai com a mesma aparência e sem a garantia.

**1. Nunca digite trecho do trabalho.** Nem entre aspas, nem parafraseado como se
fosse citação. Você indica o parágrafo pelo número (`[P123]`), e um programa copia
o texto do arquivo e o insere depois (`scripts/inserir_trechos.py`). Uma palavra
trocada numa citação é o defeito mais difícil de perceber e o mais grave numa
análise que se pretende verificável. Se o relatório precisa exibir a passagem, ela
entra por programa, e não pela sua mão.

**2. Antes de afirmar que falta algo no trabalho, procure duas vezes,** com termos
diferentes. Afirmação de ausência é a que se refuta abrindo o arquivo, e foi a
causa dominante de apontamento falso nas primeiras medições da série: catorze de
vinte e sete num dos casos.

**3. Se você recebeu só o `.docx`, você não viu as figuras.** Declare isso no
relatório, não descreva nenhuma figura, e não diga que converteu o arquivo. Quem
precisa ler gráfico precisa do PDF.

## Qual modelo escolher, e o que isso custa

A calibragem inteira foi medida em Claude. Na mesma dissertação, com a mesma
conferência aplicada aos dois lados, o modelo caro levantou 38 apontamentos e 24
sobreviveram, e o barato levantou 14 e sobreviveram 5: **um quinto dos achados
aproveitáveis, com quase o dobro da taxa de erro, dentro da mesma família.**
Nenhum modelo de outro fornecedor foi testado, e não há razão para esperar que um
salto maior custe menos.

Se o seletor de modelos oferecer Claude Opus, é ele. Sonnet funciona e rende
menos, na proporção acima. Qualquer outro é uso não testado, e o relatório deve
dizer no cabeçalho com que modelo foi produzido.

**Evite o modo automático de escolha de modelo.** Modelo escolhido pelo serviço é
modelo desconhecido, e relatório de modelo desconhecido não se compara com nenhum
outro, nem com o mesmo trabalho na semana passada. Para esta oficina, isso é pior
que um modelo reconhecidamente menor: ali ao menos se sabe o que esperar. Se a sua
assinatura só oferecer o modo automático, diga isso no cabeçalho do relatório em
lugar do nome do modelo.

**Sobre consumo:** o Alberto cabe folgado em qualquer plano, porque os programas
não usam modelo nenhum e a leitura julga algumas dezenas de trechos já
localizados. A cadeia completa do Luis, não: são cerca de 560 mil tokens numa
dissertação, em dezenas de passos. Meça antes de prometer.

## O modo de uso no VS Code: um diretório só

**O arranjo é este, e ele existe para não haver caminho a errar.** A pessoa clona
este repositório, abre a pasta clonada como espaço de trabalho no VS Code, e
**põe o trabalho a analisar na raiz**, ao lado de `scripts/` e `prompts/`. Nada
mais precisa ser configurado.

```
Oficina_de_Orientacao/
├── .github/copilot-instructions.md   ← o assistente lê isto sozinho
├── AGENTS.md                          ← e daqui vem o resto
├── scripts/                           ← os programas
├── prompts/                           ← a doutrina
├── trabalho.docx                      ← o arquivo a analisar, aqui
├── extracao/                          ← aparece sozinho, e não sobe
└── entregas/<estudante>/<data>/       ← a entrega, e também não sobe
```

Os comandos ficam `python scripts/extrair.py trabalho.docx`, sem caminho
relativo para acertar. O `.gitignore` barra `*.docx`, `*.pdf`, `extracao/`,
`trabalhos/` e `entregas/`, de modo que o trabalho de outra pessoa não sobe para
o repositório nem por descuido. Para manter vários trabalhos ao mesmo tempo,
`trabalhos/<nome>/` serve, e aí os comandos precisam do caminho.

**Quando alguém pedir a análise sem dizer mais nada, faça nesta ordem:**

1. **Ache o trabalho.** É o único `.docx` ou `.pdf` na raiz. Se houver mais de um,
   pergunte qual; se não houver nenhum, diga onde pôr, e não invente arquivo.
2. **Confira o ambiente antes de prometer.** `python --version` precisa responder
   3.11 ou mais. Sem PyMuPDF, o caminho do PDF não roda e o do `.docx` roda.
3. **Rode os cinco programas** da seção seguinte, na ordem. Eles não usam modelo,
   não consomem cota e não erram por julgamento.
4. **Julgue as suspeitas**, uma a uma, contra o parágrafo que cada uma cita. É
   aqui que você trabalha, e é a única parte que exige leitura.
5. **Escreva `RELATORIO.md` e `ANEXO.md`** e monte a entrega com `--estudante`.
6. **Confira o que você mesmo escreveu** com `conferir_citacoes.py`.

**Diga em qual passo está, e o que cada programa devolveu.** Quem opera isto pela
primeira vez não sabe distinguir programa que calou por não achar nada de
programa que quebrou, e essa diferença é a coisa mais fácil de esconder sem
querer.

## A regra que faz as duas coisas ao mesmo tempo

**Onde existe programa, rode o programa.** Não confira à mão o que
`conferir_interno.py` confere, não conte parágrafos, não procure número repetido
lendo o texto. Isso é o desenho do projeto, porque operação mecânica não precisa
de julgamento, e é também o que torna a oficina barata: cada conferência que sai
do modelo e vai para o programa custa zero e não erra.

## A cadeia, na ordem

```bash
python scripts/extrair.py trabalho.docx              # extração numerada por parágrafo
python scripts/analisar_docx.py forma trabalho.docx  # consistência formal, por papel
python scripts/conferir_consistencia.py tudo trabalho.docx   # números, listas, termos
python scripts/conferir_interno.py extracao/trabalho.txt     # remissões, numeração, contas
```

Os quatro devolvem **suspeitas**, e não apontamentos. Nenhum deles julga: eles
localizam o que merece ser olhado, e a leitura decide caso a caso se é mudança
declarada ou deslize. Silêncio de um programa não é aprovação: significa que nada
do que ele sabe procurar apareceu.

Depois da leitura, com o relatório e o anexo escritos:

```bash
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx --estudante silva
python scripts/conferir_citacoes.py RELATORIO.md trabalho.pdf
```

`montar_entrega.py` grava o relatório com os trechos inseridos, o trabalho com os
parágrafos numerados, o índice dos itens e, quando a origem é `.docx`, o trabalho
anotado com cada apontamento como comentário do Word na margem.

`conferir_citacoes.py` procura no arquivo de origem toda sequência entre aspas do
relatório. **Rode sempre, e principalmente se o modelo não for o testado:** é o
que transforma confiar no modelo em verificar o modelo. Ele existe por causa de um
caso real, em que um relatório recebeu parágrafos extraídos de outro trabalho.

## O que nunca entra neste repositório

Trabalho de estudante, relatório sobre pessoa nomeada, extração de texto de
terceiro. O `.gitignore` bloqueia `*.docx`, `*.pdf`, `extracao/` e `relatorios/`,
e isso não é conveniência: é a política do projeto, em `POLITICA.md`. Se for
preciso registrar uma medição, identifique o trabalho pelo gênero e pelo tamanho,
nunca por quem o escreveu.

## Onde está a doutrina

`prompts/LUIS.md` é a leitura completa, em quatro passos. `prompts/ANALISADOR-PORTATIL.md`
é a versão que cabe numa conversa só. `REGISTRO-DE-DESENHO.md` explica por que
cada regra existe, com a medição que a originou e a data. Registro desatualizado
não é documentação obsoleta: é instrução ativa errada.

## Uma ressalva que vale para tudo

Estas ferramentas examinam o trabalho por dentro. Não validam nada por fora: não
dizem se o trabalho afirma algo verdadeiro sobre o objeto, nem se a construção é
inédita. Coerência interna perfeita convive com codificação errada.

# Rodar a oficina no VS Code, com o Copilot

Este roteiro serve a duas coisas ao mesmo tempo: usar as ferramentas, e **descobrir
onde alguém de fora trava**. Nada aqui foi testado numa máquina que não a de quem
escreveu o conjunto, e por isso cada passo diz o que observar quando falhar.

Se você está seguindo isto como teste, anote três coisas ao longo do caminho:
**quais modelos o seletor oferece na sua assinatura**, **quanto de cota uma análise
consome**, e **em que passo você precisou de conhecimento que não está escrito
aqui**. A terceira é a mais valiosa, e é a que nenhum de nós consegue ver sozinho.

## O que instalar antes

| | para quê | sem isso |
|---|---|---|
| **Python 3.11 ou mais novo** | tudo | nada roda |
| **git** | clonar o repositório | dá para baixar o zip |
| **VS Code com o GitHub Copilot** | a metade que julga | resta colar os prompts num assistente qualquer |
| **PyMuPDF** (`pip install pymupdf`) | ler PDF | os quatro scripts de PDF param; o caminho do `.docx` funciona |
| **pandoc** e **xelatex** | o relatório em PDF | use `--sem-pdf`; o markdown e o HTML saem do mesmo jeito |

## 1. Clonar e abrir

```bash
git clone https://github.com/AlexandreAraujoCosta/Oficina_de_Orientacao.git
```

Abra **a pasta clonada** como espaço de trabalho no VS Code. Isso importa: o
Copilot lê `.github/copilot-instructions.md` na raiz do espaço de trabalho, e se
você abrir uma pasta acima, ele não acha as instruções e trabalha sem elas.

## 2. Escolher o modelo, e este é o primeiro ponto de medição

No seletor de modelos do Copilot, escolha **Claude Opus** se ele estiver na lista.
Sonnet funciona e rende menos, na proporção que o `AGENTS.md` registra. **Evite o
modo automático:** modelo escolhido pelo serviço é modelo desconhecido, e
relatório de modelo desconhecido não se compara com nenhum outro.

Em 12 de março de 2026 o plano de estudante do GitHub perdeu a seleção de Opus e
Sonnet, restando Haiku, Gemini e GPT. Não confirmei se a mudança atingiu o
benefício docente. **Anote o que aparece na sua lista:** é o que decide se esta
via serve só a quem orienta ou também a quem é orientado.

## 3. Pôr o trabalho no lugar

Copie o `.docx` ou o PDF **para a raiz da pasta clonada**, ao lado de `scripts/`
e `prompts/`. É o arranjo que o `AGENTS.md` define, e ele existe para não haver
caminho relativo a errar. O `.gitignore` barra `*.docx`, `*.pdf`, `extracao/`,
`trabalhos/` e `entregas/`, de modo que nada do trabalho de outra pessoa sobe
para o repositório por descuido.

## 4. Os programas, que rodam sem modelo nenhum

Do terminal, na raiz:

```bash
python scripts/extrair.py trabalho.docx
python scripts/analisar_docx.py sumario trabalho.docx
python scripts/analisar_docx.py forma trabalho.docx
python scripts/conferir_consistencia.py tudo trabalho.docx
python scripts/conferir_interno.py extracao/trabalho.txt
```

Estes cinco não usam inteligência artificial, não consomem cota e não erram por
julgamento. Eles levantam **suspeitas**, e não apontamentos: nenhum deles
distingue mudança declarada de deslize. Silêncio de um programa não é aprovação.

**Se algum quebrar, o problema é ambiente, não trabalho.** Anote a mensagem: é
informação sobre a portabilidade, que é o que este teste procura.

## 5. A leitura, que é onde o Copilot entra

Abra o chat do Copilot **em modo agente** e peça, com estas palavras ou parecidas:

> Leia o `AGENTS.md` na raiz e siga o que ele manda. O trabalho está em
> `trabalhos/silva/trabalho.docx`. Rode a análise de consistência: julgue cada
> suspeita que os programas levantaram, e escreva o relatório.

**Comece pelo Alberto, e não pelo Luis.** A camada de consistência julga algumas
dezenas de trechos já localizados, o que cabe em qualquer contexto. A leitura
completa do Luis é outra ordem de grandeza: o prompt tem 103 KB, cerca de 26 mil
tokens, e o trabalho inteiro entra junto. **Esse é o segundo ponto de medição**, e
é onde eu esperaria a primeira parede: ou o contexto não comporta, ou a cota
acaba. Se acontecer, anote em que passo parou.

Para a leitura completa, quando quiser tentar, o prompt é `prompts/LUIS.md`, e a
versão que cabe numa conversa só é `prompts/ANALISADOR-PORTATIL.md`.

## 6. Montar a entrega

Com o relatório e o anexo escritos, ainda na raiz:

```bash
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx --estudante silva
```

Sai em `entregas/silva/<data>/`. Vindo de `.docx`, a entrega é **o trabalho
anotado e o relatório**: cada apontamento vira comentário do Word na margem do
parágrafo que o exibe, e os comentários que já estavam no arquivo são preservados.
Vindo de PDF, sai o `.md` em CriticMarkup no lugar do `.docx` comentado.

Se faltar pandoc ou xelatex, acrescente `--sem-pdf`.

## 7. Conferir o que o modelo escreveu

```bash
python scripts/conferir_citacoes.py RELATORIO.md trabalho.pdf
```

Procura no arquivo de origem toda sequência entre aspas do relatório. **Rode
sempre, e principalmente se o modelo não for o testado:** é o que transforma
confiar no modelo em verificar o modelo. Ele existe por causa de um caso real, em
que um relatório recebeu parágrafos extraídos de outro trabalho.

## Onde eu apostaria que trava

Escrito antes do teste, para valer como previsão e não como explicação depois.

1. **O seletor não oferece Claude.** Aí a calibragem se perde, e o que sair não se
   compara com nada. É o risco mais provável e o único que não tem contorno.
2. **A leitura completa não cabe.** 26 mil tokens de instrução mais o trabalho
   inteiro, em dezenas de passos. Se travar aqui, o Alberto ainda funciona, e ele
   é a porta de entrada de qualquer modo.
3. **pandoc e xelatex.** São a instalação mais chata da lista, e servem só ao PDF.
   `--sem-pdf` resolve, e ninguém descobre isso sozinho.
4. **O trabalho fora da raiz.** Se o arquivo estiver noutra pasta, o assistente
   não o acha sozinho, porque a regra que ele segue é "o único `.docx` ou `.pdf`
   na raiz". Ele deveria perguntar em vez de inventar, e é isso que o teste
   verifica.

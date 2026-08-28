# Rodar a oficina no VS Code, com o Copilot

Este roteiro serve a duas coisas ao mesmo tempo: usar as ferramentas, e **descobrir
onde alguém de fora trava**. Nada aqui foi testado numa máquina que não a de quem
escreveu o conjunto, e por isso cada passo diz o que observar quando falhar.

Se você está seguindo isto como teste, anote três coisas ao longo do caminho:
**quais modelos o seletor oferece na sua assinatura**, **quanto de cota uma análise
consome**, e **em que passo você precisou de conhecimento que não está escrito
aqui**. A terceira é a mais valiosa, e é a que nenhum de nós consegue ver sozinho.

## O que você instala à mão, e é uma coisa só

**O VS Code, com a extensão GitHub Copilot.** É o único arranque irredutível: o
VS Code porque é onde o Copilot mora, e a extensão porque é o próprio Copilot.
Instala-se pelo painel de extensões, procurando por *GitHub Copilot*, e ela pede
login na conta do GitHub.

Tudo o mais, **inclusive o Python**, sai de um pedido em português ao assistente,
que tem terminal em modo agente. É o passo 2.

## 1. Baixar e abrir

**Baixe o zip**, em `Code` › `Download ZIP` na página do repositório:

https://github.com/AlexandreAraujoCosta/Oficina_de_Orientacao

Descompacte onde quiser e abra **a pasta descompactada** como espaço de trabalho
no VS Code. Isso importa: o Copilot lê `.github/copilot-instructions.md` na raiz
do espaço de trabalho, e se você abrir uma pasta acima, ele não acha as
instruções e trabalha sem elas, sem avisar.

**Por que o zip, e não `git clone`.** Não é para poupar a instalação do git. É que
o clone deixa um remoto configurado, apontando para um endereço público, dentro
da mesma pasta onde você vai pôr a dissertação de outra pessoa. O `.gitignore`
barra os tipos conhecidos, e barrar por tipo não é garantia: basta um arquivo com
extensão fora da lista, ou um clique em *stage all* no painel de controle de
versão. O zip não tem remoto, e o que não tem para onde ir não vai.

**Quem quiser acompanhar o desenvolvimento** clona em vez de baixar, e aí atualiza
com `git pull`, que não envia nada. O `AGENTS.md` proíbe o assistente de rodar
`git add`, `git commit` e `git push` havendo trabalho de terceiro na pasta, mas
essa é uma trava de instrução, e trava de instrução se contorna sozinha quando o
modelo é outro.

## 2. Pedir o que faltar, em uma mensagem

Abra o chat do Copilot **em modo agente**, na pasta que você descompactou, e cole:

> Confira se o Python está instalado e se a versão é 3.11 ou mais nova, rodando
> `python --version`. Se não estiver, ou se for mais antigo, me diga o que você
> pretende instalar e quanto ocupa, **pergunte antes de instalar**, e depois
> confirme que o comando passou a responder.

**Não peça mais nada agora.** As outras duas dependências entram só quando
fizerem falta, cada uma no passo em que faz: o PyMuPDF apenas se o trabalho for
PDF, e o pandoc com o xelatex apenas se você quiser o relatório em PDF. Quem está
só experimentando não precisa de nenhuma das duas, e não faz sentido baixar meio
gigabyte de LaTeX antes de saber se a ferramenta serve.

**Se preferiu clonar em vez de baixar o zip**, o git entra pelo mesmo caminho:
peça a instalação na mesma mensagem, com a mesma exigência de perguntar antes.

## 3. Escolher o modelo, e este é o primeiro ponto de medição

No seletor de modelos do Copilot, escolha **Claude Opus** se ele estiver na lista.
Sonnet funciona e rende menos, na proporção que o `AGENTS.md` registra. **Evite o
modo automático:** modelo escolhido pelo serviço é modelo desconhecido, e
relatório de modelo desconhecido não se compara com nenhum outro.

Em 12 de março de 2026 o plano de estudante do GitHub perdeu a seleção de Opus e
Sonnet, restando Haiku, Gemini e GPT. Não confirmei se a mudança atingiu o
benefício docente. **Anote o que aparece na sua lista:** é o que decide se esta
via serve só a quem orienta ou também a quem é orientado.

## 4. Pôr o trabalho no lugar

Copie o `.docx` ou o PDF **para a raiz da pasta clonada**, ao lado de `scripts/`
e `prompts/`. É o arranjo que o `AGENTS.md` define, e ele existe para não haver
caminho relativo a errar. O `.gitignore` barra `*.docx`, `*.pdf`, `extracao/`,
`trabalhos/` e `entregas/`, de modo que nada do trabalho de outra pessoa sobe
para o repositório por descuido.

## 5. Os programas, que rodam sem modelo nenhum

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

**Se o trabalho for PDF e aparecer `No module named 'fitz'`**, é o PyMuPDF que
falta. Peça ao Copilot: *instale o PyMuPDF com `pip install pymupdf` e rode de
novo*. Com `.docx` isso nunca acontece, porque nenhum dos cinco abre PDF.

**Se algum quebrar por outra razão, o problema é ambiente, não trabalho.** Anote a
mensagem: é informação sobre a portabilidade, que é o que este teste procura.

## 6. A leitura, que é onde o Copilot entra

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

## 7. Montar a entrega

Com o relatório e o anexo escritos, ainda na raiz:

```bash
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx --estudante silva
```

Sai em `entregas/silva/<data>/`. Vindo de `.docx`, a entrega é **o trabalho
anotado e o relatório**: cada apontamento vira comentário do Word na margem do
parágrafo que o exibe, e os comentários que já estavam no arquivo são preservados.
Vindo de PDF, sai o `.md` em CriticMarkup no lugar do `.docx` comentado.

**O PDF é a única coisa que precisa de instalação pesada, e ela é opcional.** Se o
comando reclamar de pandoc ou de xelatex, você tem duas saídas, nesta ordem de
esforço: acrescentar `--sem-pdf`, e o relatório sai em markdown, que abre em
qualquer editor; ou pedir ao Copilot que instale os dois, avisando que são
algumas centenas de megabytes. Só instale se for entregar o PDF a alguém.

## 8. Conferir o que o modelo escreveu

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
3. **O Copilot não saber reagir à falta.** Nada é instalado de antemão, então as
   dependências aparecem como mensagem de erro no meio do caminho: `No module
   named 'fitz'` no passo 5, a reclamação do pandoc no passo 7. A pergunta é se
   ele reconhece o que falta e propõe a instalação, ou se apenas repassa o erro.
   E se instalar meio gigabyte de LaTeX sem perguntar, isso é achado sobre o
   assistente, e não sobre a oficina.
4. **O trabalho fora da raiz.** Se o arquivo estiver noutra pasta, o assistente
   não o acha sozinho, porque a regra que ele segue é "o único `.docx` ou `.pdf`
   na raiz". Ele deveria perguntar em vez de inventar, e é isso que o teste
   verifica.

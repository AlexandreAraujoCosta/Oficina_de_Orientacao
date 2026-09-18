# Como usar o Warat

O Warat é o assistente conversacional da Oficina de Orientação. Ele conversa com
você sobre o seu trabalho acadêmico (tese, dissertação, monografia), uma pergunta
de cada vez: o que o trabalho quer sustentar, de que conjunto ele fala, onde a
introdução e o que foi feito deixaram de coincidir. Enquanto vocês conversam,
outras leituras da Oficina conferem o seu texto contra os dados, e o que elas
acharem entra na conversa depois de verificado.

Quando ele propuser uma nova redação, você aceita, ajusta ou recusa. No fim você
recebe o seu próprio `.docx` com as mudanças que aceitou em controle de alterações
e, na margem, os pontos verificados que não chegaram a ser discutidos.

## O que é preciso ter

- **O Claude Code.** É a aba *Code* do aplicativo Claude, para computador, ou o
  comando `claude` no terminal, numa conta que tenha acesso a ele. **O Warat roda
  só aí.** Ele depende de leituras em paralelo e de programas que o chat comum do
  Claude não tem, e numa conversa comum ele perderia a verificação que dá razão
  de ser a ele.
- **Python 3.11 ou mais novo** instalado no computador.
- **O seu trabalho em `.docx`.** Se o arquivo tiver comentários ou alterações
  controladas do seu orientador, pode deixar: o Warat pergunta de quem são e lê só o
  seu texto.

## Como começar

Abra uma sessão nova do Claude Code, em qualquer pasta, e cole o texto abaixo,
trocando o caminho pelo do seu arquivo:

```
Quero conversar com o Warat, da Oficina de Orientação, sobre o meu trabalho.
Se a Oficina ainda não estiver no meu computador, baixe-a de
https://github.com/AlexandreAraujoCosta/Oficina_de_Orientacao (com git clone ou,
se não houver git, pelo arquivo zip do repositório) para uma pasta ao lado do meu
arquivo; se já estiver, atualize-a. Confira que o Python 3 está instalado. Depois,
a partir da raiz da Oficina, leia e cumpra prompts/WARAT-CONVERSACIONAL.md.
Meu trabalho está em: C:\caminho\para\meu-trabalho.docx
```

O Claude faz o resto. Quando ele pedir permissão para rodar um programa ou abrir um
arquivo, a Oficina está fazendo o que o texto acima pediu.

## O que vai acontecer

1. **Preparação, um ou dois minutos.** O Warat copia e extrai o seu texto numa pasta
   de trabalho, dentro da Oficina (`trabalhos/<nome do arquivo>/`). Se houver
   comentários ou alterações de outra pessoa, ele pergunta de quem são antes de
   seguir.
2. **As primeiras perguntas, em poucos minutos.** Primeiro sobre o contexto: se a
   versão vai à banca ou é de trabalho, que prazo você tem, o que quer que o
   trabalho sustente. Depois, sobre o que o trabalho é.
3. **A conversa.** Responda com as suas palavras. Pode discordar, corrigir o que ele
   entendeu e pedir sugestão de redação. Cada pergunta traz o texto dos parágrafos
   a que se refere, porque o seu arquivo não mostra os números que ele usa.
4. **Os achados das leituras**, depois de uns vinte ou trinta minutos, quando a
   verificação termina. Só entra o que foi conferido contra o texto.
5. **O fechamento, quando você quiser parar.** Ele mostra o que foi discutido, o que
   deu por resolvido (confira), o que ficou em aberto e o que não chegou a ser
   perguntado, e grava `ENTREGA-WARAT.docx` na pasta de trabalho.

## O que convém saber antes

- **Confira cada proposta antes de aceitar.** Cada uma chega com a comparação,
  palavra por palavra, entre o seu texto e o que ficaria. Uma proposta pode mudar
  mais do que anuncia, e é por isso que essa comparação existe.
- **O Warat não substitui quem orienta.** Ele pergunta pela coerência do trabalho e
  confere afirmações contra os dados. A crítica à construção teórica, por exemplo
  se um conceito central está definido ou se uma metáfora se sustenta, ele só
  alcança às vezes, e o juízo sobre ela não é dele.
- **O seu arquivo original não é alterado.** O Warat trabalha numa cópia, e a entrega
  (`ENTREGA-WARAT.docx`) é outra cópia. Se o original tinha comentários ou alterações
  do seu orientador, a entrega não os traz: eles continuam no original, e convém
  guardar os dois.
- **Para onde vai o seu texto.** Ele é lido pelo Claude, na sua conta, como em
  qualquer conversa com o Claude. A pasta de trabalho fica no seu computador e é
  excluída do repositório da Oficina: nada do seu trabalho é publicado ali.
- **As leituras consomem uma parte grande do limite de uso da conta.** Se a sessão
  parar por limite ou se o computador reiniciar, abra a mesma sessão depois e peça
  para continuar de onde parou: o registro da conversa fica em `conversa/CONVERSA.md`,
  na pasta de trabalho, e o Warat retoma a partir dele. Se a sessão tiver se perdido,
  cole de novo o texto do começo: ele encontra a pasta e continua.
- **Quando a entrega trouxer um AVISO sobre formatação**, confira aquele parágrafo no
  Word: uma substituição integral pode ter tirado um itálico ou um negrito que só
  existia em parte do texto.

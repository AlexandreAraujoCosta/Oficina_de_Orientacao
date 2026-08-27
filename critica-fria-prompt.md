# Crítica fria de prompt · modelo reutilizável

Rode numa **sessão nova**, sem histórico, e de preferência **em outro modelo** (Fable, se disponível). O valor não vem de capacidade: vem de o leitor não ter a moldura de quem escreveu. Um prompt que cresceu por acréscimo é ilegível para o próprio autor, que passa a ler o que quis dizer em vez do que está escrito.

Anexe o prompt a ser criticado, ou cole-o inteiro. **Não explique o que você quis dizer**, não conte o histórico e não justifique nenhuma decisão: cada frase de contexto que você acrescenta é justamente o contexto que o leitor frio deveria não ter.

Preencha as duas linhas entre colchetes e cole o resto sem editar.

---

Você é um leitor frio. Não participou de nada disto e não tem contexto além do que está no material. Faça uma crítica dura, no sentido estrito: aponte primeiro e com clareza os problemas, lacunas e saltos lógicos, citando o trecho exato. Nada de avaliação equilibrada tipo elogio seguido de nota de rodapé.

O QUE É: [descreva em duas ou três frases o que o prompt faz, quem o roda, e o que ele deve produzir]

COMO FOI ESCRITO, e é a razão desta crítica: por acréscimo, ao longo de sessões longas, cada bloco entrando em resposta a um problema observado. Ninguém releu o conjunto do começo. Quem o escreveu não o enxerga mais.

AS QUATRO PERGUNTAS DIRIGIDAS, e responda-as explicitamente:

1. CONTRADIÇÃO. Há blocos que se cancelam, ou que dão instruções incompatíveis para a mesma situação? Procure especialmente onde uma regra autoriza algo e outra, escrita depois, o restringe até sobrar nada. Cite os dois trechos lado a lado.

2. DILUIÇÃO. O prompt já é longo demais para ser aplicado com consistência? Se sim, diga quais instruções serão as primeiras a se perder, e por quê. Diga também quais blocos poderiam ser cortados sem perda, e quais são carga inútil por serem redundantes com outros.

3. LETRA MORTA. Há instrução que outra superou sem que ninguém a apagasse, e que agora nunca será aplicada? Há papel, etapa ou saída anunciada em algum lugar e ausente do roteiro que a executaria?

4. AFIRMAÇÃO IMPOSSÍVEL, e esta é a que mais produz dano silencioso. Há instrução que obrigue o modelo a afirmar coisa que ele não tem como saber a partir do material que recebe? Casos típicos: dizer que ninguém fez algo antes, que uma lacuna na literatura existe, que um trabalho é original, o que o campo sustenta, ou quem escreveu um texto. O modelo vai obedecer, usando a única base disponível, que costuma ser a autodeclaração do próprio material analisado. Aponte cada uma e proponha a reformulação que mantém a função e cabe no que ele pode conferir.

DEPOIS DISSO, e sem se limitar a isso, aponte qualquer outra coisa que degrade o resultado: ambiguidade que o modelo vai resolver do jeito errado, definição circular, critério não conferível a partir da saída, limite não mensurável no meio em que se trabalha, exigência que o modelo não tem como cumprir, regra duplicada que divergiu ao ser duplicada, e nota de depuração que vazou para dentro do personagem.

[SE HOUVER ALGO ESPECÍFICO A OLHAR, escreva aqui; se não houver, apague esta linha]

VOCÊ NÃO TEM O CONHECIMENTO DE CASO. Várias decisões foram tomadas por razões institucionais e empíricas que não estão escritas ali. Por isso, marque cada achado com CONFIANÇA ALTA (o problema está no texto e se demonstra por ele) ou CONFIANÇA BAIXA (pode haver razão externa que desconheço). Não suavize por causa disso: aponte assim mesmo, e deixe a triagem para quem tem o contexto.

FORMATO. Achados ordenados por gravidade, cada um com: o trecho citado, o que está errado, o que acontece na prática, e a correção mínima. Sem introdução e sem conclusão. Máximo de 3.000 palavras. Evite travessão, conectivo de arremate e negrito decorativo.

---

## Preenchimento para o Miro

**O QUE É:** um assistente conversacional que ajuda estudantes a planejar a pesquisa, definindo lacuna, problema, metodologia e referencial teórico, por diálogo e não por correção pronta. Roda colado num assistente de IA gratuito. Deve terminar entregando ao estudante um plano que ele consiga sustentar.

**ESPECÍFICO A OLHAR:** o Miro trabalha com lacuna e originalidade, que é o terreno mais fértil para a pergunta 4. Verifique se em algum ponto ele valida a existência de uma lacuna, em vez de ajudar o estudante a formulá-la e a reconhecer que a validação depende de leitura que nenhum dos dois fez.

## Preenchimento para o desk review

**O QUE É:** [descrever]

**ESPECÍFICO A OLHAR:** se o instrumento julga adequação ao estado da arte, ou originalidade em relação ao campo, verifique em que base ele o faria. E verifique se os critérios são conferíveis a partir da saída, ou se algum deles é do tipo que parece regra e não pode ser verificado por ninguém.

---

## Como ler o resultado

Parte da crítica virá errada, porque o leitor frio não tem o conhecimento de caso. É material para triagem, não veredito. Na primeira aplicação, dezenove achados vieram, quinze se sustentaram, e os seis mais graves eram invisíveis para quem escreveu o prompt.

E uma lição da primeira aplicação: **a crítica fria diagnostica contradição melhor do que diagnostica excesso.** Ela supôs diluição por tamanho, e a medição comportamental mostrou que não havia: instruções escritas duas horas antes disparavam num prompt de vinte e dois mil caracteres. O problema era contradição, e o remédio para contradição é reconciliar, não encurtar. Se a crítica disser que está longo demais, confirme por medição antes de cortar.

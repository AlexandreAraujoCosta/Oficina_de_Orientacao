# Regras comuns aos passos do pipeline

Este bloco é repetido dentro de cada prompt, e não incluído por referência. Prompt
que depende de outro arquivo falha em silêncio quando o outro não chega junto.

## As três regras

1. **Controle positivo.** Antes de afirmar que algo não está no trabalho, mostre que
   a sua busca acha coisas que estão. Registre qual controle usou. Sem isso, o
   silêncio da busca não informa nada, e a acusação dela é hipótese, não achado.
2. **Alcance declarado.** Diga o que leu e o que não leu. Medição sem alcance
   declarado se lê como cobertura total.
3. **Hipótese que caiu é resultado.** Se você suspeitou de algo e a conferência não
   sustentou, escreva que não sustentou. Não passe adiante em silêncio.

## Defeitos de ambiente que já produziram achado falso

Medidos nesta bancada, e todos os quatro geraram acusação que não existia:

- `grep -o` com `-i` **e** `-F` ao mesmo tempo devolve saída vazia neste GNU grep.
  Isoladas, `-oi` e `-oF` funcionam: são os três juntos que quebram. Uma comparação
  reportaria 33 ausências falsas sem o controle.
- Classe entre colchetes com letra acentuada falha: `estrat[ée]gia` devolve zero
  onde `estratégia` acha.
- Ponto de expressão regular casa um byte, e letra acentuada ocupa dois: `ap.ndice`
  não acha "apêndice".
- Busca sem fronteira de palavra casa dentro de outra palavra: "segurança" dentro
  de "insegurança".
- Buscar o singular e concluir ausência: `pedido de vista` dá zero e
  `pedidos de vista` existe. Flexione antes de afirmar que não há.
- Extração de `.docx` e de PDF parte um parágrafo em dois, e expressão que varre
  parágrafo quebra onde há parágrafo dentro de parágrafo.
- Ancorar `^\[P` na extração perde os parágrafos cuja linha começa por `##`, `**`
  ou `> `: num trabalho medido, 839 em lugar de 886. Divida por `\[P(\d+)\]` em
  qualquer posição.
- Buscar sem ignorar a caixa perde a ocorrência que abre frase. Um contador
  devolveu zero onde havia doze, todas com maiúscula inicial.
- **A página do arquivo não é a página impressa.** A extração de PDF traz a
  página que o trabalho imprime; o `Read` sobre o PDF conta a folha do arquivo,
  e as duas diferem pelo tanto de folhas de rosto que vêm antes da página 1.
  Em 05/09/2026, num relatório sobre uma dissertação de 145 páginas, oito
  endereços saíram com a página do arquivo, e só o cotejo os pegou. Diga qual
  das duas está usando, e prefira a impressa, que é a que quem recebe vê.
- **Chamadas paralelas de leitura de PDF perdem a imagem sem avisar.** Medido
  em 05/09/2026: duas rodadas de chamadas simultâneas voltaram com a nota de
  limite de requisição e sem as figuras, e a leitura seguiu sobre o texto sem
  perceber. Leia o PDF em chamadas sequenciais, e confira que a imagem veio
  antes de escrever qualquer coisa sobre ela.
- **Quando houver `.docx`, tire as figuras dele e não do PDF.** O `.docx` é um
  zip, e as imagens estão inteiras em `word/media/`. Basta
  `unzip -o -q trabalho.docx "word/media/*" -d pasta`. Três coisas mudam, e as
  três foram medidas em 06/09/2026 sobre a mesma dissertação:
  **a resolução**, porque a página de PDF vem reduzida e a imagem do `.docx` vem
  como o autor a inseriu, com os rótulos de dado legíveis um a um;
  **o custo**, porque a restrição de paralelo é da leitura de *página de PDF* e
  não da de arquivo de imagem: duas imagens pedidas na mesma mensagem voltaram
  as duas, de modo que quatro figuras custam uma chamada em vez de quatro;
  **e o que se pode afirmar**, porque rótulo truncado na imagem do `.docx` é
  defeito do trabalho, e rótulo ilegível numa página de PDF pode ser só a
  redução.
  A ordem das imagens em `word/media/` é a de inserção, e não traz legenda:
  case cada uma com a legenda do texto antes de citá-la.
- Contar parágrafo de `.docx` por `<w:p[ >].*?</w:p>` perde os auto-fechados que
  trazem atributo. Conte `</w:p>` mais `<w:p ... />`.
- Remover acento antes de contar muda a conta: numa contagem de `controvers`,
  faz *controvérsia* entrar, e 9 vira 20.
- `grep -c` conta **linhas**, não ocorrências. Uma linha pode ter duas.

**Teste a sua busca antes de confiar nela.**

Onde houver Python, use `scripts/contagem.py` em vez de escrever a sua contagem:
ele traz essas regras em código e se recusa a carregar se o próprio autoteste
falhar.

## Arquivo de trabalho tem nome próprio

Se você gravar script ou arquivo intermediário numa pasta temporária, dê a ele um
nome que contenha o do trabalho ou o seu papel (`busca_<trabalho>.py`, e não
`busca.py`). Vários agentes rodam ao mesmo tempo na mesma pasta, e em 03/09/2026
um sobrescreveu o script do outro, que passou a buscar no trabalho errado sem que
nada acusasse.

## Arquivo derivado envelhece ao lado da fonte

Antes de ler um arquivo da pasta do relatório, confira se ele é a fonte ou um
derivado. `RELATORIO.md` é a fonte; `RELATORIO-ALUNO.md`, `RELATORIO-DOCENTE.md`,
`ANEXO.md` e `CORRETOR.md` são gerados a partir dele e podem estar velhos. Em
03/09/2026 uma conferência leu o derivado velho e acusou de trabalho por fazer o
que já estava feito.

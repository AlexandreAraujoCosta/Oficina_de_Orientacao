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

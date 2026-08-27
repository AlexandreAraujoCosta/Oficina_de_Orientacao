# Oficina de Orientação

Ferramentas de leitura automática de trabalhos acadêmicos, para quem orienta.
Desenvolvidas por Alexandre Araújo Costa, Faculdade de Direito da UnB, com
assistência do Claude Opus em Claude Code.

O assistente se chama **Luis**, em homenagem a Luis Alberto Warat. Durante quase
uma década ele desconstruía os rascunhos do autor e apontava o rumo de
construções mais robustas, que é o que estas ferramentas tentam fazer.

Este repositório traz **a maquinaria, e nunca o material**. Não há aqui trabalho
de estudante, relatório sobre pessoa nomeada nem extração de texto de terceiro.
As medições registradas nos comentários e no registro de desenho identificam o
trabalho pelo gênero e pelo tamanho, jamais por quem o escreveu. O critério está
em `POLITICA.md`.

## As três ferramentas

**Analisador de consistência.** Confere o trabalho contra ele mesmo, em quatro
níveis: formal, numérica, categorial e textual. Serve em qualquer momento, porque
dobra o trabalho sobre si mesmo e não depende de haver argumento pronto. A metade
mecânica é programa e não custa nada; a metade que julga os candidatos é leitura.

**Luis.** A leitura que julga o argumento, em quatro passos: consistência, a
cadeia do marco e do método, o cotejo adversarial de cada apontamento, e o
relatório. Pede desenvolvimento argumentativo suficiente, com resultados
apresentados e conclusões escritas: rodado antes disso, julga o que ainda não
existe. O prompt está em `prompts/LUIS.md`, e a versão que cabe numa conversa só,
em `prompts/ANALISADOR-PORTATIL.md`.

**Banca simulada.** Uma sessão de arguição com dois examinadores e o orientador
presidindo. Parte do relatório e da apresentação do candidato, e devolve, além da
experiência de ser interpelado, o que a apresentação causou na banca.

## Duas vias de uso

**No chat.** Os prompts de `prompts/` colam em qualquer assistente. Não instala
nada e não custa nada. O que se perde: o cotejo feito por quem não escreveu os
apontamentos, os localizadores `[P123]`, e o arquivo de volta.

**Com os programas.** A cadeia inteira, do texto extraído ao trabalho anotado.

```bash
python scripts/extrair.py trabalho.docx
python scripts/analisar_docx.py forma trabalho.docx
python scripts/conferir_interno.py extracao/trabalho.txt
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx
```

`montar_entrega.py` grava de uma vez: o relatório em PDF, com os parágrafos
citados inseridos abaixo de cada item; o trabalho com os parágrafos numerados; o
índice dos itens para a correção; e, quando a origem é `.docx`, **o trabalho
anotado**, com cada apontamento como comentário do Word na margem do parágrafo
que o exibe.

Depois, `aplicar_docx.py` põe os reparos no arquivo como alterações controladas,
onde o alvo cabe numa formatação contínua, e como comentário onde atravessa.

## O que é preciso ter

Python 3.11 ou mais novo. **PyMuPDF** (`pip install pymupdf`) para os seis
scripts que leem PDF. **pandoc** e **xelatex** para gerar o PDF do relatório. O
resto é biblioteca padrão.

## Alcance

**A arquitetura é geral e a calibragem é do direito.** O que não depende de campo
é a maior parte: consistência numérica e categorial, o fóssil da escrita em
camadas, a ordem do cotejo, a tipologia de vieses de leitura. O que é do direito
está isolado num bloco próprio do prompt, e são os exemplos e as convenções que
ele reconhece. Serve, em princípio, às demais ciências sociais. **Não foi testado
fora do direito**, porque não há corpus de outro campo neste projeto. Ver
`prompts/ALCANCE-outros-campos.md`.

## Por onde entender o desenho

`REGISTRO-DE-DESENHO.md` explica por que a maquinaria é assim. Cada regra vem com
a medição que a originou e a data. Sem ele, o repositório é um punhado de scripts
sem razão declarada.

`POLITICA.md` diz como a análise é usada, por quem, e o que vai para o orientando
e o que vai para quem orienta.

## Uma ressalva que vale para tudo

Estas ferramentas examinam o trabalho por dentro. **Não validam nada por fora:**
não dizem se o trabalho afirma algo verdadeiro sobre o objeto, nem se a
construção é inédita. Coerência interna perfeita convive com codificação errada.

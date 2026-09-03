# Oficina de Orientação

Ferramentas de leitura automática de trabalhos acadêmicos, para quem orienta.
Desenvolvidas por Alexandre Araújo Costa, Faculdade de Direito da UnB, com
assistência do Claude Opus em Claude Code.

Os dois assistentes se chamam **Alberto** e **Luis**, que juntos são o nome de
Luis Alberto Warat. Durante quase uma década ele desconstruía os rascunhos do
autor e apontava o rumo de construções mais robustas, que é o que estas
ferramentas tentam fazer.

Este repositório traz **a maquinaria, e nunca o material**. Não há aqui trabalho
de estudante, relatório sobre pessoa nomeada nem extração de texto de terceiro.
As medições registradas nos comentários e no registro de desenho identificam o
trabalho pelo gênero e pelo tamanho, jamais por quem o escreveu. O critério está
em `POLITICA.md`.

## As ferramentas

**Alberto, o relatório rápido.** Uma leitura, um a três minutos, e um relatório no
mesmo formato do Luis. Cola em qualquer assistente de chat e também roda no agente,
onde ganha uma revisão que derruba o que não se sustenta. O prompt está em
`prompts/ALBERTO.md`.

O que ele entrega, medido em 03/09/2026 sobre a mesma dissertação: **menos, com
justificação rala, e sem inventar**. Vinte e nove afirmações de duas rodadas foram
abertas na fonte e as vinte e nove estavam certas; mas as duas rodadas devolveram
dezessete e doze itens, com seis em comum, contra os trinta e dois do Luis. Cada
apontamento traz o endereço, e não a cadeia de prova que uma verificação independente
produziria.

**O que a extensão degrada é o endereço, e não o achado.** Uma passada única de dez
mil palavras teve quatorze quedas em sessenta e sete afirmações, o que parece
condená-la; lidas uma a uma, doze derrubam o endereço, a contagem ou uma afirmação
acessória, e o apontamento continua de pé. Sobre vinte e seis itens, dois eram falsos.
**Por isso o prompt não corta itens:** cortar para comprar precisão joga fora o achado
verdadeiro junto com o endereço torto, que é o defeito medido do prompt monolítico
anterior. O que ele impõe é disciplina de endereço, e a revisão que os confere.

### Qual das duas rodar, e a resposta não é o tamanho do trabalho

**O rápido acha o defeito evidente, e acha mal o que depende de conferir número.**
Promessa que outra seção nega, seção anunciada e não escrita, afirmação sem dado, o
que está nos dados e não foi dito: disso ele dá conta. O que exige refazer uma conta
dentro de uma tabela de resultado, e comparar o que ela publica com o que o texto
afirma dela, é onde ele passa ao largo.

**O completo acha essas, e as demais que pedem atenção e detalhe, e cobra caro por
isso.** Não é uma versão melhor da mesma coisa por um pouco mais: é quatro vezes o
custo, e a diferença que ela compra é a segunda espécie de defeito, o aparato
bibliográfico e a densidade de prova por item.

#### Tempo e tokens, medidos em 03/09/2026

| | tokens | relógio |
|---|---|---|
| rápido, no chat | uma mensagem: o prompt (cerca de 6 mil) mais o trabalho | 1 a 3 min |
| rápido, no agente | **270 a 320 mil**, incluindo a revisão | **41 a 48 min** |
| completo | **acima de 1,15 milhão** | horas |

**A linha do meio corrige um engano fácil:** os poucos milhares são o tamanho do
prompt, e não o da rodada. No agente o rápido lê o trabalho, abre parágrafos, roda
programas e ainda passa por uma revisão que abre outros oitenta, e isso custa. **O que
o separa do completo não é ser barato em termos absolutos: é ser quatro vezes mais
barato**, e entregar cerca de metade dos itens.

Os números do completo somam as quatro partes medidas hoje (peso das contribuições,
verificação, triagem e redação, cotejo) e **deixam de fora as duas primeiras leituras e
o cotejo delas**, feitos antes e não registrados. O total real é maior.

**No chat a conta é outra e não se mede em tokens:** é uma mensagem numa conta que
você já tem, e o limite que se alcança é o de conversas com arquivo anexado, que numa
conta gratuita chegou depois de três numa mesma manhã.
 **Se o que se quer é saber o que corrigir antes da
banca, o rápido entrega o essencial.** O completo se justifica quando importa saber
se a contribuição é nova, quando o trabalho vai a periódico e o aparato precisa estar
limpo, ou quando os números do trabalho são o que ele afirma.

Isso se mediu rodando os dois sobre os mesmos dois trabalhos, em 03/09/2026.

**Onde o defeito é grande e declarado pelo próprio trabalho, as duas convergem.** Numa
tese com sete seções trazendo apenas um marcador de trabalho por fazer, o rápido e o
completo deram o mesmo veredito pela mesma razão, e **a contagem certa foi a do
rápido**: sete seções, e não oito. Ali o completo custou cinco vezes mais para
acrescentar acabamento.

**Onde o defeito está em contas que exigem refazer uma tabela, o completo abre
vantagem que o rápido não alcança.** Na dissertação em que as três contas erradas
estavam dentro de tabelas de resultado, os endereços comuns entre os dois foram 64 em
277 (Jaccard 0,27), e o completo abriu 199 parágrafos contra 106.

**E há uma classe que o rápido não produz sozinho:** se a contribuição já está
publicada. Ela exige sair do trabalho, e no agente o rápido passou a fazer uma versão
curta disso; no chat, não faz.

| | dissertação com contas em tabela | tese com seções por escrever |
|---|---|---|
| endereços comuns | 64 de 277 (0,27) | 123 de 358 (0,34) |
| itens, rápido contra completo | 32 contra 37 | 50 contra 20 |
| vereditos | divergiram | coincidiram |

**A via do chat entrega o veredito e perde a conferência.** Rodado no ChatGPT sobre a
mesma tese, o rápido acertou o núcleo em nove correções e devolveu **zero
localizadores**, porque no chat não há extração numerada. Serve para decidir o que
fazer, e não serve para o autor corrigir sem procurar cada ponto no arquivo.

**Luis, o relatório completo.** Quatro leituras por caminhos diferentes, verificação,
cotejo adversarial de cada apontamento, e a redação. Custa cerca de um milhão de
tokens e quase uma hora. Pede desenvolvimento argumentativo suficiente, com
resultados apresentados e conclusões escritas: rodado antes disso, julga o que ainda
não existe. Os prompts estão em `prompts/leituras/`, e `ESTADO.md`, ali dentro, traz o
desenho congelado com a medição que sustenta cada escolha.

O prompt monolítico `prompts/LUIS.md` **foi aposentado em 03/09/2026** e não roda mais
sobre trabalho executado: devolvia dois itens e nenhum de conteúdo numa dissertação
inteira, porque as travas contra falso positivo derrubavam o achado verdadeiro junto.
O que ele tinha e o pipeline não tinha foi migrado, e o cabeçalho do arquivo lista o que
foi para onde. Ele segue no lugar por um motivo só: a leitura de projeto de pesquisa
(`prompts/PROJETO.md`) é uma camada fina sobre ele, e o pipeline ainda não tem
equivalente, porque duas de suas leituras pedem conclusão e dados que um projeto não
tem.

**Conferência de consistência.** Dobra o trabalho sobre si mesmo, em quatro níveis:
formal, numérica, categorial e textual. Serve em qualquer momento, porque não depende
de haver argumento pronto. **Confere consistência, e só**, sem julgar o argumento.
Chamava-se Alberto até 03/09/2026, quando o nome passou ao relatório rápido; o prompt
está em `prompts/CONSISTENCIA.md`.

**Banca simulada.** Uma sessão de arguição com dois examinadores e o orientador
presidindo. Parte do relatório e da apresentação do candidato, e devolve, além da
experiência de ser interpelado, o que a apresentação causou na banca.

## Duas vias de uso

**No chat.** Os prompts de `prompts/` colam em qualquer assistente. Não instala
nada e não custa nada. **A ferramenta desenhada para esta via é o Alberto**, porque
o chat precisa de resposta em minutos e ele entrega o relatório inteiro numa
passada. O que se perde aqui: a revisão feita por quem não escreveu os apontamentos,
os localizadores `[P123]`, e o arquivo de volta.

**Com os programas.** A cadeia inteira, do texto extraído ao trabalho anotado. Aqui
cabem os dois: o Luis, com as quatro leituras e o cotejo, e o Alberto, que ganha a
revisão que no chat não existe.

**Antes de mais nada, se o que você tem é um `.docx`, normalize.** Trabalho de
estudante raramente chega formatado por estilo, e o que se vê é sempre o mesmo:
o parágrafo típico não usa o estilo Normal, o estilo muda ao longo do texto, e
sobre ele vem uma camada de formatação direta que deixa tudo parecido na tela
sem deixar nada igual no arquivo. O espaço entre blocos é feito com parágrafo
vazio.

A oficina **não conserta isso**, e a decisão é de 30/08/2026: o programa que
transformava o arquivo saiu da cadeia e está guardado no ramo
`norma-transformadora`, como semente de outro artefato. No lugar dele entrou o
diagnóstico, que lê e relata.

```bash
python scripts/diagnostico_forma.py trabalho.docx
```

O primeiro comando não grava nada e diz o que faria. O segundo apaga parágrafo
vazio, convertendo a altura em espaço depois; junta espaço repetido; **conta
quantos padrões de formatação o corpo tem de fato e cria um estilo para cada um
que recorre**, com a forma que aquele grupo já tinha; põe no estilo de legenda
os parágrafos que descrevem gráfico, tabela ou quadro; e tira o recuo e o
parágrafo sobrando dos separadores de nota de rodapé, que herdam do corpo um
recuo que ali não faz sentido.

**Um estilo por papel, e não por forma.** Contar as formas encontradas e criar
um estilo para cada uma organiza a aparência e cimenta a desordem: legenda que
sai em três formatos não tem três padrões, tem falta de padrão, e dar um estilo
a cada variante faz cada uma passar a ser correta pelo seu próprio estilo, de
modo que a camada formal da análise deixa de ver o desvio. Multiplicar estilo é
tão ruim quanto não ter nenhum. O programa reconhece três papéis, corpo,
referência e legenda, e alinha cada um a uma forma só.

**E não alinha quando não há a que alinhar.** Se nenhuma forma reúne metade do
papel, ele para e diz: escolher uma é decisão de quem escreveu. Medido no
trabalho de 140 páginas: corpo, 333 parágrafos em 19 formas, a maior com 57%,
alinhado; referências, 113 em 4 formas, 88%, alinhado; legendas, 88 em 15 formas
e a maior com 36%, não alinhado.

**O pré-textual não é tocado.** Capa, folha de rosto, folha de aprovação,
dedicatória, resumo e sumário são diagramados à mão, com linha em branco
empurrando bloco para baixo da página, e apagá-las comprime a capa. **Quatro travas impedem que
ele apague parágrafo vazio que seja estrutura:** quebra de seção, quebra de
página ou coluna, âncora de imagem, e âncora de nota, marcador ou comentário.
Parágrafo dentro de tabela não é tocado. O que difere da forma dominante fica, e
é justamente o desvio que a análise deve enxergar depois.

Medido em 28/08/2026, numa dissertação de 1.434 parágrafos e 140 páginas: 18
estilos em uso, 99% dos parágrafos com formatação direta sobre o estilo, 533
parágrafos vazios dos quais 377 saíram e 156 ficaram pelas travas, 66 legendas
convertidas, e o texto saiu idêntico, parágrafo a parágrafo.

```bash
python scripts/extrair.py trabalho.docx
python scripts/analisar_docx.py forma trabalho.docx
python scripts/conferir_interno.py extracao/trabalho.txt
python scripts/montar_entrega.py RELATORIO.md ANEXO.md trabalho.docx
```

**A cadeia é um comando só.** `montar_entrega.py` chama o que precisa: confere as
citações e para se alguma não existir no trabalho; monta o relatório com o anexo;
gera o mapa de páginas, pedindo ao Word que exporte o PDF da mesma versão que
está sendo comentada; e escreve, além da entrega, o `COMENTARIOS-<nome>.md`, que é
o texto exatamente como ele chega a quem recebe, para o conferidor de
compreensibilidade ler. Sem Word e sem `--pdf`, o mapa não sai e o endereço dos
comentários volta a ser as palavras iniciais do parágrafo, que o Ctrl+F encontra;
o programa diz qual dos dois casos ocorreu. `--sem-paginas` dispensa a etapa.

**Ele também avisa quando o trabalho não passou pelo normalizador**, e não
normaliza ali: neste ponto cada localizador do relatório já aponta para um
parágrafo deste arquivo, e normalizar deslocaria a numeração inteira sem que nada
acusasse.

`montar_entrega.py` grava de uma vez: o relatório em PDF, com os parágrafos
citados inseridos abaixo de cada item; o trabalho com os parágrafos numerados; o
índice dos itens para a correção; e, quando a origem é `.docx`, **o trabalho
anotado**, com cada apontamento como comentário do Word na margem do parágrafo
que o exibe.

**Antes de entregar**, `texto_dos_comentarios.py` escreve o texto que cada
apontamento terá dentro do Word, e `prompts/COMPREENSIBILIDADE.md` o lê como se
fosse o autor: sem o trabalho e sem notícia da análise, ele diz de cada item o
que faria ao recebê-lo. Item de que não se consegue extrair uma ação falhou, e o
teste precisa de uma sessão que não tenha escrito os itens, porque quem os
escreveu é o pior juiz de se eles se entendem.

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

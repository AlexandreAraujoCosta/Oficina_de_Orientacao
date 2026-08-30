# Política de uso

Como a análise é usada, por quem, e em que momento. Duas frentes independentes: a individual, sobre um trabalho, e a populacional, sobre um conjunto.

## Princípio de divisão

Uma única análise, dois documentos, dois destinatários. A linha que separa os dois não é de delicadeza, é de natureza do achado:

**O orientando recebe o que é verificável e executável.** Referência ausente da lista, número que não fecha, citação que diverge da fonte, sumário desatualizado, formatação incoerente, trecho que precisa de trabalho conjuntivo. São coisas que se conferem sem discutir e se corrigem sem negociar.

**O orientador recebe o que exige julgamento.** Se o problema de pesquisa se sustenta, se o método aplicado é o método declarado, se a conclusão excede a evidência, se um capítulo deve ser cortado, quanto falta para uma defesa. São decisões de orientação, e uma máquina não as comunica ao orientando.

Rodar duas vezes seria desperdício e produziria divergência entre os documentos. A análise é uma só.

## Análise individual

### Momento 1: caderno do orientando, antes da conversa

Sai junto com a análise e vai direto para o orientando. Finalidade: chegar à reunião com o trabalho limpo, para que a conversa seja sobre o que importa.

Conteúdo:

- Erros verificáveis, em lista numerada, com localização por parágrafo e trecho citado.
- Higiene bibliográfica: citação sem entrada na lista, entrada nunca citada, par autor-ano ambíguo, ano divergente, referência que a conferência na web não localizou ou localizou com divergência.
- Conferência aritmética: o que não fecha, e o que foi conferido e fecha.
- Citação direta que diverge da fonte localizada, com as duas versões transcritas e a diferença marcada.
- Forma: incoerências de formatação, hierarquia de títulos, numeração de elementos gráficos, sumário.
- Descontaminação estilística e as armadilhas de uso de ferramenta, conforme o bloco destacável da definição do agente.
- Trechos que precisam de trabalho conjuntivo, identificados por faixa de parágrafos, com a relação que ficou implícita em cada um. Nunca como métrica e nunca com a instrução de fundir parágrafos.
- As perguntas da banca dos grupos 1 e 2, inevitáveis e evitáveis. É o item de maior valor para o orientando e o que ele não consegue produzir sozinho.

Teto: 600 palavras no bloco de descontaminação, sem teto na lista de erros verificáveis, que é inventário e não texto.

### O que nunca vai para o orientando

Sem exceção, e a razão está escrita ao lado:

- **O veredito e a classificação de estado.** É julgamento de orientação, e quem comunica é o orientador, com as palavras dele. Uma máquina dizendo a um mestrando que o trabalho exige reformulação é ao mesmo tempo cruel e usurpação.
- **Os indícios de uso abusivo de ferramenta.** Reservados, sempre.
- **As perguntas da banca do grupo 3, as fatais.** O orientador decide se, quando e como as apresenta.
- **Avaliação de originalidade, de contribuição e de capacidade do autor.**
- **Qualquer índice numérico do perfil.** Métrica que vira alvo é otimizada, e no caso do ritmo e da análise gráfica o caminho mais barato de otimização é o que estraga o texto.

### Momento 2: relatório do orientador, ao receber o trabalho

O relatório completo, na estrutura e nos tetos da definição do agente.

Uma consequência prática da divisão: os achados mecânicos foram para o caderno do orientando e **não se repetem aqui**. Entram como uma linha de resumo com as contagens, e a lista completa fica em anexo que não precisa ser lido. Isso libera o orçamento de 6.000 palavras para o que exige leitura, que era o objetivo do teto.

O relatório serve como pauta da reunião. A ordem de leitura é veredito, determinações, banca. O resto se consulta.

### Segunda rodada: a versão seguinte

Quando chegar a versão revista, a análise roda tendo em mãos o relatório anterior, e cada determinação é classificada em três estados:

- **Atendida.**
- **Ignorada.**
- **Atendida na aparência**, quando o sintoma foi corrigido e o defeito permaneceu. É a categoria que interessa, e é a razão de numerar os apontamentos de forma contínua e estável.

Só isso já responde à pergunta que importa entre uma versão e outra, que é se o orientando entendeu o problema ou apenas apagou a marca dele.

## Uso populacional

### Instrumento

O script sozinho, sem modelo de linguagem. Um comando `perfil` que varre um diretório e emite uma linha por trabalho, com cerca de 35 colunas, em segundos por arquivo. Duzentas dissertações passando por um agente seria proibitivo e desnecessário: o agente é para o caso individual, o script é para o corpus.

O ruído por unidade é aceitável aqui. Ele se dilui em N, e viés constante não atrapalha ordenação. As exigências trocam de lugar: em vez de precisão por trabalho, cobertura, consistência e custo.

### Estratificação

Comparação entre gêneros produz diferença que é de gênero e não de qualidade. O corpus se estratifica por **índice de empiricidade**, composto de densidade numérica na prosa, elementos gráficos por mil palavras e existência de seção de método, e por ano. Comparações se fazem dentro do estrato.

### Usos legítimos

- **Limiares por percentil**, em vez de cortes arbitrários. Um trabalho no quartil inferior de higiene bibliográfica do próprio programa é afirmação sustentável; um trabalho "abaixo do aceitável" não é.
- **Triagem.** Rodar o corpus, ler os que destoam.
- **Deriva temporal.** Como o perfil do programa muda ano a ano, com atenção às marcas de escrita e à densidade bibliográfica a partir de 2023.
- **Falseamento das próprias regras.** Se as dissertações aprovadas violam sistematicamente uma regra do modelo, a regra é da casa e não da área, e a escolha entre reformar e descrever passa a ser consciente.
- **Séries do mesmo orientando.** Versões sucessivas, gênero constante, variação limpa.

### O que os índices não medem

Qualidade. Todos eles medem forma e higiene, e um trabalho pode ir bem em todos e não ter argumento. Uma tabela ordenada por qualquer coluna vai ser lida como ranking de qualidade por quem a encontrar fora de contexto, e por isso a advertência acompanha o arquivo, não a conversa.

Não há índice composto. Os pesos seriam inventados, e o número resultante pareceria rigoroso sem ser.

### Limites de uso

O corpus é de trabalhos identificados, com autores e orientadores nomeados. Duas fronteiras, e elas são escolha, não impedimento técnico:

- Uso identificado apenas para triagem de trabalhos sob responsabilidade própria.
- Uso agregado e anonimizado para pesquisa sobre o programa, sobre a deriva temporal ou sobre metodologia de avaliação.

**Revisão de 02/08/2026.** A vedação anterior dizia que comparação identificada entre orientadores ou entre linhas de pesquisa é possível de fazer e não deve ser feita com um instrumento que mede higiene e se parece com um que mede mérito. Ela cai. Duas coisas mudaram desde que foi escrita: o corpus é público e identificado no repositório da UnB, e o instrumento deixou de ser só o `perfil`. As leituras de lente examinam desenho de pesquisa, que é matéria de julgamento acadêmico legítimo, e a análise passou a ter uma finalidade que a regra não previa, que é dizer ao próprio orientador o que ele deve melhorar.

A comparação identificada, portanto, pode ser feita. O que fica no lugar da vedação é uma exigência, e ela é mais difícil de cumprir do que a proibição era: **não tomar uma coisa por outra.** Em concreto, e cada item destes já falhou pelo menos uma vez neste projeto:

- **Forma não é mérito.** Os índices do `perfil` medem forma, ritmo e higiene. Nenhuma comparação identificada se apoia neles, e nenhuma tabela ordenável por coluna sai identificada. O que sustenta comparação identificada é a leitura de lente, que argumenta.
- **Defeito do instrumento não é propriedade do trabalho.** Antes de qualquer afirmação identificada, o achado passa pela conferência: citação contra a fonte (`scripts\conferir_citacoes.py`), e checagem de que a faixa de texto lida era a certa. O instrumento já produziu 431 capítulos numa dissertação, delimitação que descartava 88% do texto e paráfrase apresentada como transcrição.
- **Defeito do trabalho não é falha de orientação.** Só o subconjunto que um orientador está posicionado para pegar numa leitura de versão diz algo sobre orientação, e só quando reaparece em anos distantes.
- **Presença não é taxa.** Seis trabalhos por orientador sustentam "esta classe aparece" ou "não aparece". Não sustentam frequência, ordenação nem comparação de intensidade.
- **O corpus não é a produção do orientador.** O repositório traz o que foi depositado, com o orientador de registro. Não distingue coorientação, não mede envolvimento real e não inclui o que ficou fora do repositório.

O que continua vedado, e não por causa da identificação: índice composto, ranking, e qualquer saída que ordene pessoas por uma coluna. A proteção deixou de ser o anonimato e passou a ser o contexto: a comparação identificada anda junto com o argumento que a sustenta e com quem responde por ele.

## Cadência

| Quando | O que roda | Quem lê |
| --- | --- | --- |
| Ao receber uma versão | Análise individual completa | Caderno para o orientando, relatório para o orientador |
| Na versão seguinte | Análise mais confronto com o relatório anterior | Ambos, com o quadro de determinações atendidas |
| Antes da qualificação ou da defesa | Análise completa, com atenção ao bloco da banca | Ambos |
| Semestralmente, ou ao incorporar novos trabalhos | `perfil` sobre o corpus | Orientador |

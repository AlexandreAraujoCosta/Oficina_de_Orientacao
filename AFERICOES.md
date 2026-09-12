# Aferições

Cada programa desta oficina calcula alguma coisa. **Calcular não é conferir.** Um
número só se torna medida quando bate com outro que não saiu do mesmo programa.

Em 09/09/2026 sete programas foram escritos num dia e quatro produziram número
errado ou acusação falsa no primeiro uso real. Os quatro tinham controle positivo.
O que separou o que funcionou do que falhou foi **ter sido conferido contra um
número externo**.

Este arquivo registra o que se sabe. Programa sem linha aqui imprime *nunca
aferido* quando roda, e o que ele mostra é cálculo, não medida.

Quem afere escreve a linha. `scripts/afericao.py` só lê.

| programa | contra que número externo | quando | resultado |
|---|---|---|---|
| base_das_figuras.py | os 136 valores lidos que o próprio relatório de figuras declarava | 09/09/2026 | confere: 136 contra 136 |
| enderecos_em_lote.py | o texto de [P118], [P123], [P128] e [P158] na extração | 09/09/2026 | confere depois do conserto; antes entregava só a primeira linha de cada |
| anexo_do_alberto.py | os 55 itens do `.itens.json` do trabalho K | 09/09/2026 | confere: 55 entraram, 55 saíram |
| conferir_bloco.py | os códigos da prosa contra os do JSON, em dois relatórios | 09/09/2026 | confere: 53 contra 53, e acusou quando divergiam |
| planejar_leitura.py | **nunca aferido contra ponto fora do ajuste** | — | ajustado em todos os seis pontos disponíveis, validado em nenhum; errou +165% na leitura 3 |
| conferir_figura_vs_texto.py | três acusações reais, abertas uma a uma | 09/09/2026 | **3 de 3 falsas**: casa todo número de um parágrafo com a figura que ele cita, e um parágrafo afirma sobre várias coisas |
| conferir_margem.py, classe "contagem sem nome" | cinco acusações reais, abertas | 09/09/2026 | **5 de 5 falsas**: dispara em `as N substantivo` mesmo quando o referente vem nomeado na frase seguinte |
| conferir_margem.py, classes de remissão | os 53 itens do trabalho K e os 59 da tese | 09/09/2026 | zero acusações nos dois, e o autoteste pega os casos plantados; sem acerto real aberto ainda |
| montar_levantamento.py | quatro códigos acusados de repetidos na leitura 1 da tese | 09/09/2026 | **4 de 4 falsos** antes do conserto: contava remissão em prosa como definição de item |
| mapa_estrutural.py | as fronteiras de sete extrações do acervo | 09/09/2026 | seis de sete corretas; a sétima fecha em "5.6 Síntese conclusiva", nome que o programa não conhece |
| gerar_warat.py | o cotejo linha a linha entre `ALBERTO.md` e `WARAT.md` | 09/09/2026 | confere: três blocos de diferença, dois dentro da seção da ordem e um o cabeçalho |
| conferir_transcricao.py | dois relatórios entregues | 09/09/2026 | zero sequências acusadas nos dois; sem acerto real aberto ainda |
| montar_material.py | 41 chamadas e 16,1 min contra 18 e 13,7 na mesma leitura | 08/09/2026 | confere: zero buscas de passagem na execução nova |
| relevancia.py | a classificação de 10/09 do relatório Alberto v4 da dissertação de 08/09 contra o cotejo cego do mesmo dia (50 de superfície em 91) | 10/09/2026 | concorda em ordem de grandeza: 56 NADA em 91, régua mais estrita que a do cotejo; 10 de 75 itens de providência mudam conclusão ou alcance |
| conferir_bloco.py, `da_prosa` depois do conserto | contagem por grep, linha a linha, dos códigos de dois relatórios de 06/09, refeita também por voz fria sem a função | 12/09/2026 | 49 de 49 num; 46 de 48 no outro, e os dois perdidos são decisões com pergunta acima de 120 caracteres; saída idêntica ao commit anterior em 14 relatórios com bloco |
| relevancia.py com `--decisoes` e P | as mesmas duas classificações recontadas por grep sobre o arquivo | 12/09/2026 | confere: 9 ALCANCE e 17 NADA num, 4, 15 e 4 no outro; o resumo que a voz escreveu errava por um, e o arquivo não |
| afericao.py | — | — | nunca aferido; este arquivo é o registro dele |

## O que "sem acerto real aberto ainda" quer dizer

O programa passa no controle que carrega, e o controle é plantado por quem o
escreveu. Ele nunca acusou nada de verdade que alguém tenha ido conferir. **O
silêncio dele não informa**, e a primeira acusação que ele fizer é hipótese.

## O que não está aqui e não pode estar

Mudança de prompt não tem saída para conferir contra número externo. A via de
leitura de figuras entrou em três prompts publicados na manhã de 09/09/2026 e foi
reescrita à tarde, depois de um teste controlado. Para essa classe o único freio é
o falsificador escrito antes — e o que se escreveu naquele dia a própria medição
do dia já dizia ser inutilizável.

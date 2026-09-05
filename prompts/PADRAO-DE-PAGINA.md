# O padrão visual das páginas da oficina

Cinco páginas seguem este padrão desde 04/09/2026: `oficinas.html`, `oficina.html`,
`analisador.html`, `luis.html` e `simulador.html`. Para trazer outra página para
ele, siga o que está aqui e rode `python conferir_padrao.py <pagina.html>`, que
reprova o que estiver fora.

**As irmãs que ainda não entraram:** as páginas da Oficina de Projetos (Miro,
Selma e a página da oficina), que vivem só nos artifacts, e as antigas
`prebanca.html` e `corretor.html`, que estão no repositório.

## Por que ele existe

Em 04/09/2026 as cinco páginas usavam dois sistemas: a da Oficina em Charter
sobre papel quente, com acento azul; as três dos assistentes em Segoe sobre papel
frio, com títulos em Constantia e acento verde-azulado. Quem saía de uma para a
outra mudava de projeto. Junto vieram três defeitos que só a medição mostra:
texto corrido a **2,84** de contraste, quando o mínimo da WCAG é 4,5; título de
item a 29px dentro de seção cujo título tinha 15px; e **treze** tratamentos de
caixa numa página só.

## 1. A folha de tokens

Copie este bloco inteiro para o alto do `<style>`, sem alterar valor nenhum. São
quatro blocos, e os quatro precisam existir: o tema claro em `:root`, o tema do
sistema **protegido** por `:not([data-theme="light"])`, e as duas escolhas
explícitas.

```css
  :root {
    --ground:      #FBFAF7;   --surface:     #F3F1EC;   --sunken:      #EAE7E0;
    --ink:         #191B1F;   --ink-soft:    #3D4149;
    --muted:       #5F636B;   --faint:       #6C7079;
    --rule:        #D9D5CC;   --rule-firm:   #BFBAAE;   --rule-soft:   #E6E2DA;
    --accent:      #33477E;   --accent-soft: #E1E5F1;
    --warn:        #8A5722;   --warn-soft:   #F2E7D8;
    --good:        #37613F;   --good-soft:   #E0EBE1;
    --danger:      #A3352B;   --danger-soft: #F6E6E3;

    --serif: Lora, "Iowan Old Style", Charter, Georgia, "Times New Roman", serif;
    --sans: Mulish, "Segoe UI", Inter, system-ui, -apple-system, sans-serif;
    --mono: "Cascadia Mono", "JetBrains Mono", ui-monospace, Consolas, "SF Mono", monospace;

    --measure: 66ch;

    /* seis degraus, na medida de arcos.org.br/direito-ciencia */
    --t-xs: 14px;    /* rotulo em versalete */
    --t-sm: 16px;    /* texto secundario */
    --t-md: 18px;    /* corpo, em Lora */
    --t-lg: 22px;    /* linha de abertura */
    --t-h3: 19px;
    --t-h2: 24px;
  }
  /* escuro: --ground #16171A, --surface #1D1F23, --sunken #24262B,
     --ink #E9E6E0, --ink-soft #C4C2BD, --muted #94979E, --faint #8A8D94,
     --rule #34373D, --rule-firm #454A52, --rule-soft #2A2D32,
     --accent #97AAE2, --accent-soft #23283A, --warn #D3A163, --warn-soft #33291B,
     --good #83B78D, --good-soft #1E2A20, --danger #E07A6E, --danger-soft #2E1E1C */
```

O arquivo `tokens.py` monta os quatro blocos com estes valores, e foi com ele que
as cinco páginas foram convertidas.

**Piso de contraste: 4,5 sobre o papel do próprio tema**, para toda cor que
carregue texto. É por isso que `--faint` não pode voltar a ser `#93969D` (2,84) e
que `--muted` desceu para `#5F636B`. O conferidor calcula os dezesseis pares.

**Nome próprio de página aponta para o sistema, e não repete valor.** Se a página
já usava outros nomes, mantenha-os como apelido, para o resto do CSS continuar
valendo:

```css
    --paper: var(--ground);  --paper-sunk: var(--sunken);  --ink-faint: var(--muted);
    --correcao: var(--danger);  --medida: var(--accent);  --conforme: var(--good);
```

## 2. A escala

**As duas famílias vêm de <https://arcos.org.br/direito-ciencia/>, e os papéis são
os de lá:** *Lora* no texto corrido, *Mulish* nos títulos, nas aberturas e nos
rótulos. A fonte de máquina fica só para código. As duas se carregam do Google
Fonts, que é o único servidor de fontes que o invólucro do artifact admite, e a
linha vai antes do `<title>`:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mulish:ital,wght@0,400;0,600;0,700;1,400&family=Lora:ital,wght@0,400;0,600;1,400&display=swap">
```

Corpo em `var(--serif)`, **18px**, entrelinha 1.65, que é a medida do modelo.
Este bloco vai no fim do `<style>`, depois de tudo, para vencer as regras antigas
da página:

```css
  /* --- escala do sistema: uma so em todas as paginas da oficina --- */
  h1, .top h1, header h1, .wrap > h1 { font-family: var(--sans); font-weight: 700;
    font-size: clamp(24px, 5vw, 30px); line-height: 1.2; }
  .wrap h2, .shell h2, .via-guia h2, .cuidados h2 { font-family: var(--sans); font-size: var(--t-h2); font-weight: 700; line-height: 1.2; }
  .wrap h3, .shell h3, .via-guia h3, .cuidados h3 { font-family: var(--sans); font-size: var(--t-h3); font-weight: 700; line-height: 1.2;
    letter-spacing: normal; text-transform: none; color: var(--ink); }
  /* a medida vale para todo texto corrido, e nao so para o que esta em secao */
  .wrap p, .wrap li, .wrap dd, .shell p, .shell li, .shell dd { max-width: var(--measure); }
```

30 / 24 / 19 / 18, com 22 na abertura e 16 e 14 no que é secundário. **Nenhum
tamanho fora desses seis degraus**: eram 52 valores distintos de `font-size` nas
cinco páginas, e é isso que fazia a leitura parecer caótica.

**Rótulo não é título**: `.verbete h4`, `.chip`, `.route-sub` e afins ficam em
`--t-xs`, em versalete e na Mulish, e o seletor deles é mais específico, o que já
os preserva.

A medida está no bloco porque declarar `--measure` não basta: antes disso, o Luis
tinha parágrafos de **96 caracteres** por linha, fora de qualquer restrição.

## 3. Quatro tratamentos de caixa, e só quatro

| papel | como se faz | para que serve |
|---|---|---|
| nota | barra esquerda 2px `--rule`, sem fundo | ficha do autor, dedicatória, colofão |
| nota semântica | barra esquerda 3px na cor, fundo `-soft` da mesma cor | `--accent` princípio, `--good` feedback, `--warn` etapa que trava, `--danger` alerta |
| cartão | borda 1px `--rule`, sem fundo | linhas de lista, pares, etapas, verbetes |
| caixa de máquina | fundo `--sunken`, borda 1px `--rule`, raio 3px | comando, prompt, `textarea` |

**Fundo só onde há cor semântica ou máquina.** Foi essa regra que levou a Oficina
de treze tratamentos a quatro: as caixas estruturais perderam o preenchimento e
ficaram com a régua de 1px.

## 4. O cabeçalho, na mesma sequência

1. faixa de topo (`.eyebrow`), em Mulish maiúscula e espaçada, duas linhas:
   `Faculdade de Direito da UnB · PMPD · Oficinas Acadêmicas`, e, nas páginas de
   uma oficina, `Assistentes: <nomes>`. A página atual vem sem link, marcada com
   `class="eb-atual" aria-current="page"`.
2. `h1`, com `1em` de espaço acima e abaixo, medido no próprio corpo do título.
3. o que a página é, em um a três parágrafos.
4. a ficha do autor (`.byline`), sempre com a mesma redação.
5. o bloco de feedback (`.feedback`), com o formulário.

## 5. As três regras que não se veem

- **`<meta charset="utf-8">` na primeira linha.** O invólucro do artifact injeta
  um, e por isso o defeito não aparece lá; servida de qualquer outro lugar, a
  página perde todo acento.
- **Os três estados de tema**, com o do sistema protegido contra a escolha clara.
- **O container centra o texto.** Largura de container muito maior que a medida
  joga o texto para a esquerda e deixa metade da tela vazia. As páginas de
  assistente usam 900px; a de índice, 47rem; a da Oficina tem grade com barra
  lateral.

## 6. Como conferir

```
python conferir_padrao.py oficina.html analisador.html luis.html simulador.html oficinas.html
```

Ele confere o charset, o carregamento das duas fontes, os quatro blocos de tema,
cada valor de token, os dezesseis contrastes, o corpo, a medida, os seis degraus,
os tamanhos fora deles, a fonte de máquina fora de código e os restos do sistema
antigo. Tem
controle positivo: antes de aprovar qualquer página, ele adultera um token e
verifica que a conferência reprova.

**O que ele não confere, e exige o navegador:** quantos tratamentos de caixa a
página tem, a largura real da linha em caracteres, e se algum bloco ficou sem
espaço. Isso se mede rodando um servidor local sobre a pasta e lendo a página
com o `medir.js` desta pasta.

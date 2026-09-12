# -*- coding: utf-8 -*-
"""Tira da leitura de figuras a base de dados que o orientando confere.

POR QUE ISTO EXISTE

A leitura cega das figuras reconstroi, numero a numero, o que cada grafico
mostra. Esses numeros nao sao dado: metade foi **lida do desenho**, contra a
grade, com erro; a outra metade estava **impressa** na figura. Publicados juntos
numa coluna so, viram planilha, e quem le recebe estimativa como medida.

A coluna que diz de onde veio cada valor e o produto. Com ela, o orientando abre
o proprio grafico ao lado e ve onde o rotulo nao bate. Sem ela, a tabela afirma
mais do que a leitura pode.

O QUE ELE FAZ

Le o relatorio do passo 1 e recolhe as tabelas de valores, e **so** elas: a
tabela tem de estar dentro de uma secao de figura e vir depois de um marcador
`**Valores ...**`. A tabela de arquivos que compoem a figura, e as tabelas
derivadas das listas do fim, ficam de fora.

Sai em formato longo, uma linha por celula:

    trabalho, figura, endereco, eixo, categoria, serie, valor, margem, origem, nota

`origem` e `impresso` ou `lido`, e vem do marcador que encabeca a tabela.

CONTROLE POSITIVO

O programa carrega um caso que ele **tem** de recusar (a tabela de arquivos, que
nao esta sob marcador de valores) e um caso que ele tem de aceitar com os numeros
certos. Se qualquer dos dois falhar, ele nao roda.

Uso:
    python scripts/base_das_figuras.py <relatorio.md> [--saida base.csv] [--html pagina.html]
"""
import argparse
import csv
import io
import re
import sys
import unicodedata
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------- utilidades


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def limpo(s):
    """Tira negrito, italico, codigo e espaco dobrado de uma celula."""
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*|\*|_", "", s)
    return re.sub(r"\s+", " ", s).strip()


RE_MARGEM = re.compile(r"^(margem|erro|precis|incerteza|desvio)", re.I)
RE_NUM = re.compile(r"-?\d{1,3}(?:[.  ]\d{3})+(?:[,.]\d+)?|-?\d+(?:[,.]\d+)?")


def numero(cel):
    """Devolve (valor, nota). Valor e None quando a celula nao traz numero."""
    c = limpo(cel)
    if not c or c in ("-", "--", "—", "–"):
        return None, ""
    m = RE_NUM.search(c)
    if not m:
        return None, c
    bruto = m.group(0)
    resto = (c[:m.start()] + c[m.end():]).strip(" ~()").strip()
    t = bruto.replace(" ", "").replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.search(r"\.\d{3}\b", t) and not re.search(r"\.\d{1,2}$", t):
        t = t.replace(".", "")
    try:
        v = float(t)
    except ValueError:
        return None, c
    if "~" in c[:m.start() + 1]:
        resto = ("aproximado " + resto).strip()
    return v, resto


# ------------------------------------------------------------------- leitura

RE_SECAO = re.compile(r"^##\s+(.*?)\s*$", re.M)
RE_VALORES = re.compile(r"^\s*\*\*Valores\b(.*?)\*\*", re.I)
RE_ENDERECO = re.compile(r"\[?P(\d+)\]?")


def origem_do_marcador(txt):
    """Qual das duas palavras vem primeiro no marcador manda.

    O marcador costuma citar as duas: `**Valores impressos.**` e o caso limpo,
    mas `**Valores (todos lidos do desenho; nenhum impresso).**` diz "impresso"
    para negar que haja. Procurar "impress" antes de "lido" classificava essa
    tabela ao contrario, e todos os 136 valores lidos do trabalho T sairiam
    marcados como impressos, que e o erro que a coluna existe para evitar.
    """
    t = sem_acento(txt).lower()
    onde = []
    for palavra, nome in (("impress", "impresso"), ("lido", "lido"),
                          ("leitura", "lido")):
        p = t.find(palavra)
        if p >= 0:
            onde.append((p, nome))
    if not onde:
        return "nao declarada"
    return min(onde)[1]


def tabelas_de(bloco):
    """Devolve [(origem, [linhas])] das tabelas que seguem um marcador de valores."""
    achadas = []
    linhas = bloco.split("\n")
    i = 0
    while i < len(linhas):
        m = RE_VALORES.match(linhas[i])
        if not m:
            i += 1
            continue
        origem = origem_do_marcador(m.group(0))
        j = i + 1
        tab = None
        while j < len(linhas) and j - i < 14:
            if RE_VALORES.match(linhas[j]) or linhas[j].startswith("## "):
                break
            if linhas[j].lstrip().startswith("|"):
                tab = j
                break
            j += 1
        if tab is None:
            i += 1
            continue
        fim = tab
        while fim < len(linhas) and linhas[fim].lstrip().startswith("|"):
            fim += 1
        achadas.append((origem, linhas[tab:fim]))
        i = fim
    return achadas


def celulas(linha):
    partes = linha.strip().strip("|").split("|")
    return [limpo(p) for p in partes]


def eh_separadora(linha):
    return bool(re.match(r"^\s*\|[\s:|-]+\|\s*$", linha))


def ler(texto, trabalho):
    """Devolve a lista de registros em formato longo."""
    fora = []
    cortes = [(m.start(), m.group(1)) for m in RE_SECAO.finditer(texto)]
    for k, (ini, titulo) in enumerate(cortes):
        fim = cortes[k + 1][0] if k + 1 < len(cortes) else len(texto)
        bloco = texto[ini:fim]
        t = sem_acento(titulo).lower()
        if not re.match(r"(grafico|figura|tabela|quadro|imagem)\b", t):
            continue
        end = ""
        mend = re.search(r"\*\*Endere[cç]o\.?\*\*\s*([^\n]*)", bloco)
        if mend:
            me = RE_ENDERECO.search(mend.group(1))
            if me:
                end = "P" + me.group(1)
        for origem, linhas in tabelas_de(bloco):
            corpo = [l for l in linhas if not eh_separadora(l)]
            if len(corpo) < 2:
                continue
            cab = celulas(corpo[0])
            if not cab:
                continue
            eixo = cab[0]
            series, margem_de = [], {}
            for c in range(1, len(cab)):
                if RE_MARGEM.match(cab[c]) and series:
                    margem_de[series[-1]] = c
                else:
                    series.append(c)
            for linha in corpo[1:]:
                cs = celulas(linha)
                if len(cs) < 2:
                    continue
                categoria = cs[0]
                for c in series:
                    if c >= len(cs):
                        continue
                    valor, nota = numero(cs[c])
                    mc = margem_de.get(c)
                    margem = limpo(cs[mc]) if mc is not None and mc < len(cs) else ""
                    if margem in ("-", "--", "—", "–"):
                        margem = ""
                    fora.append(dict(
                        trabalho=trabalho, figura=titulo, endereco=end,
                        eixo=eixo, categoria=categoria, serie=cab[c],
                        valor="" if valor is None else ("%g" % valor),
                        margem=margem, origem=origem, nota=nota))
    return fora


# ---------------------------------------------------------------- autoteste

CASO = """
## Gráfico 22 — Decisões por ano

**Endereço.** `[P751]`, parágrafo da legenda.

**Peças que a compõem.**

| Arquivo | O que é | O que acrescenta |
|---|---|---|
| `gr22.png` | corpo | as duas linhas |

**Valores (todos lidos do desenho; nenhum impresso).**

| Ano | Monocráticas | Colegiadas |
|---|---|---|
| 2008 | 155 | 90 |
| 2020 | 1.690 | 1740 |

## Figura G — `image7.png`

**Endereço.** [P415].

**Valores impressos.** Nenhum.

**Valores lidos.** Contra a grade:

| Dias | Leitura | Margem |
|---|---|---|
| 8 | ~1805 | ±30 |
| 9 | 0 (sem barra visível) | — |

## Lista 2 — o que ninguém afirmou

| Ano | Via cinza | Via azul |
|---|---|---|
| 2020 | 3,1 | 2,0 |
"""


def autoteste():
    r = ler(CASO, "teste")
    erros = []

    if any("Arquivo" in x["eixo"] for x in r):
        erros.append("aceitou a tabela de arquivos, que nao esta sob marcador de valores")
    if any(x["figura"].startswith("Lista") for x in r):
        erros.append("aceitou tabela de secao que nao nomeia figura")

    def um(cat, serie):
        achou = [x for x in r if x["categoria"] == cat and x["serie"] == serie]
        return achou[0] if achou else None

    a = um("2020", "Monocráticas")
    if not a or a["valor"] != "1690":
        erros.append("nao leu 1.690 como 1690: %r" % (a and a["valor"]))
    if a and a["origem"] != "lido":
        erros.append("nao marcou como lido a tabela sob 'Valores (todos lidos...)'")
    if a and a["endereco"] != "P751":
        erros.append("perdeu o endereco da figura: %r" % a["endereco"])

    b = um("8", "Leitura")
    if not b or b["valor"] != "1805" or b["margem"] != "±30":
        erros.append("nao casou valor com a coluna de margem: %r" % (b,))
    if b and "aproximado" not in b["nota"]:
        erros.append("perdeu o til de aproximacao")

    c = um("9", "Leitura")
    if not c or c["valor"] != "0" or "sem barra" not in c["nota"]:
        erros.append("perdeu a nota de 'sem barra visivel': %r" % (c,))
    if c and c["margem"] != "":
        erros.append("tomou o travessao da margem por margem")

    if any(x["serie"] == "Margem" for x in r):
        erros.append("tratou a coluna de margem como serie")

    # o marcador que cita as duas palavras: manda a que vem primeiro
    for marcador, esperado in (
            ("**Valores (todos lidos do desenho; nenhum impresso).**", "lido"),
            ("**Valores impressos.** Nenhum valor lido.", "impresso"),
            ("**Valores lidos.**", "lido"),
            ("**Valores.**", "nao declarada")):
        if origem_do_marcador(marcador) != esperado:
            erros.append("classificou %r como %r, e nao %r"
                         % (marcador, origem_do_marcador(marcador), esperado))

    if erros:
        for e in erros:
            print("  AUTOTESTE FALHOU: %s" % e, file=sys.stderr)
        raise SystemExit(2)
    return len(r)


# --------------------------------------------------------------------- saida

CSS = """
:root{--fundo:#faf9f7;--tinta:#1c1a17;--fraco:#6b6560;--linha:#ddd8d0;
      --impresso:#1f5c3d;--lido:#8a5a1c;--caixa:#fff;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
      --fundo:#171614;--tinta:#eceae6;--fraco:#a09a92;--linha:#332f2a;
      --impresso:#7fc9a2;--lido:#e0a862;--caixa:#1f1e1b;}}
:root[data-theme="dark"]{--fundo:#171614;--tinta:#eceae6;--fraco:#a09a92;
      --linha:#332f2a;--impresso:#7fc9a2;--lido:#e0a862;--caixa:#1f1e1b;}
body{background:var(--fundo);color:var(--tinta);margin:0;
     font:16px/1.6 Charter,"Iowan Old Style",Georgia,serif;}
main{max-width:64rem;margin:0 auto;padding:3rem 1.5rem 6rem;}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 .4rem;text-wrap:balance;}
h2{font-size:1.15rem;margin:2.6rem 0 .3rem;text-wrap:balance;}
p.sub{color:var(--fraco);margin:0 0 2rem;}
.aviso{background:var(--caixa);border:1px solid var(--linha);
       border-left:3px solid var(--lido);padding:1rem 1.2rem;margin:0 0 2.5rem;}
.aviso p{margin:.6rem 0;}
.rolo{overflow-x:auto;border:1px solid var(--linha);background:var(--caixa);}
table{border-collapse:collapse;width:100%;font:13.5px/1.5 ui-monospace,
      "SF Mono",Menlo,Consolas,monospace;font-variant-numeric:tabular-nums;}
th,td{padding:.4rem .7rem;text-align:left;border-bottom:1px solid var(--linha);
      white-space:nowrap;}
th{position:sticky;top:0;background:var(--caixa);font-weight:600;
   border-bottom:2px solid var(--linha);}
td.n{text-align:right;}
.tag{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;
     font-weight:600;}
.impresso{color:var(--impresso);} .lido{color:var(--lido);}
.nota{color:var(--fraco);white-space:normal;font-size:.85em;}
.cont{color:var(--fraco);font-size:.85rem;margin:.3rem 0 0;}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def html(regs, trabalho, fonte):
    imp = sum(1 for r in regs if r["origem"] == "impresso" and r["valor"] != "")
    lid = sum(1 for r in regs if r["origem"] == "lido" and r["valor"] != "")
    figs = []
    for r in regs:
        if r["figura"] not in figs:
            figs.append(r["figura"])
    p = ["<title>Os números das suas figuras</title>",
         "<style>%s</style>" % CSS,
         "<main><h1>Os números das suas figuras</h1>",
         "<p class=sub>%s &middot; %d figuras &middot; %d valores</p>"
         % (esc(trabalho), len(figs), imp + lid),
         "<div class=aviso>"
         "<p><b>Isto não é a sua base de dados.</b> É o que se "
         "consegue ler das figuras de que uma afirmação da conclusão depende, "
         "e só delas; as demais figuras não têm números aqui. "
         "<span class='tag impresso'>impresso</span> marca o valor que está "
         "escrito na figura; <span class='tag lido'>lido</span> marca o valor "
         "medido contra a grade, que traz erro. Aqui há %d impressos e "
         "%d lidos.</p>"
         "<p>Abra a sua planilha ao lado e confira onde os dois não batem. "
         "Onde a diferença estiver na coluna "
         "<span class='tag lido'>lido</span>, pode ser erro desta leitura; onde "
         "estiver na <span class='tag impresso'>impresso</span>, o rótulo da "
         "figura discorda da sua planilha, e um dos dois está errado.</p>"
         "<p>Valor lido de figura sem rótulo tem o erro que a escala permite. "
         "Não use estes números em conta publicada: use-os para achar "
         "onde olhar.</p></div>" % (imp, lid)]
    for f in figs:
        linhas = [r for r in regs if r["figura"] == f]
        end = next((r["endereco"] for r in linhas if r["endereco"]), "")
        p.append("<h2>%s</h2>" % esc(f))
        if end:
            p.append("<p class=cont>Parágrafo da legenda: %s</p>" % esc(end))
        p.append("<div class=rolo><table><thead><tr>")
        p.append("<th>%s</th><th>Série</th><th>Valor</th><th>Margem</th>"
                 "<th>Origem</th><th>Observação</th></tr></thead><tbody>"
                 % esc(linhas[0]["eixo"]))
        for r in linhas:
            p.append("<tr><td>%s</td><td>%s</td><td class=n>%s</td>"
                     "<td class=n>%s</td><td class='tag %s'>%s</td>"
                     "<td class=nota>%s</td></tr>"
                     % (esc(r["categoria"]), esc(r["serie"]), esc(r["valor"]),
                        esc(r["margem"]), r["origem"].split()[0],
                        esc(r["origem"]), esc(r["nota"])))
        p.append("</tbody></table></div>")
    p.append("<p class=cont>Extraído de <code>%s</code> por "
             "<code>scripts/base_das_figuras.py</code>. Nenhum número foi "
             "digitado: todos vieram da leitura das imagens, e a coluna de origem "
             "diz de qual das duas maneiras. Só entram as figuras de que a "
             "conclusão depende.</p>" % esc(fonte))
    p.append("</main>")
    return "\n".join(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("relatorio")
    ap.add_argument("--trabalho", default=None)
    ap.add_argument("--saida", default=None, help="CSV; padrão ao lado do relatório")
    ap.add_argument("--html", default=None)
    a = ap.parse_args()

    n = autoteste()
    print("  autoteste: %d registros; recusa e aceitacao passaram." % n)

    fonte = Path(a.relatorio)
    trabalho = a.trabalho or fonte.stem
    texto = io.open(str(fonte), encoding="utf-8").read()
    regs = ler(texto, trabalho)
    if not regs:
        print("  nenhuma tabela de valores. O relatorio traz marcador '**Valores'?",
              file=sys.stderr)
        return 1

    saida = Path(a.saida) if a.saida else fonte.with_name("BASE-FIGURAS-%s.csv" % trabalho)
    with io.open(str(saida), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(regs[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(regs)

    figs = len({r["figura"] for r in regs})
    imp = sum(1 for r in regs if r["origem"] == "impresso" and r["valor"] != "")
    lid = sum(1 for r in regs if r["origem"] == "lido" and r["valor"] != "")
    vaz = sum(1 for r in regs if r["valor"] == "")
    print("  %s" % saida)
    print("  %d figuras, %d valores: %d impressos, %d lidos, %d sem numero."
          % (figs, len(regs), imp, lid, vaz))

    if a.html:
        Path(a.html).write_text(html(regs, trabalho, fonte.name), encoding="utf-8")
        print("  %s" % a.html)
    return 0


if __name__ == "__main__":
    sys.exit(main())

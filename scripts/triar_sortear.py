"""Triagem e sorteio dos corpora.

Aplica as regras de descarte do PLANO-CORPUS.md sobre o perfil.csv de cada
pasta, junta com metadados.csv pela coluna do arquivo, e sorteia N trabalhos
espalhados pelo periodo. Sorteio deterministico: semente fixa, entao rodar
duas vezes da a mesma lista.

Uso:
    python triar_sortear.py --saida ..\\corpus\\SORTEIO.md
"""

import argparse
import csv
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

PASTAS = [
    ("orientados", "Alexandre Araujo Costa"),
    ("contraste", "Juliano Zaiden Benvindo"),
    ("contraste2", "Henrique Araujo Costa"),
    ("contraste3", "Marcio Iorio Aranha"),
    ("contraste4", "Pablo Holmes Chaves"),
]

SEMENTE = 20260802


def num(valor):
    """Converte campo do CSV em float; devolve None quando vazio ou nao numerico."""
    if valor is None:
        return None
    v = str(valor).strip().replace(",", ".")
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def motivos_descarte(linha, modo="leitura"):
    """Regras de descarte, em dois conjuntos.

    `populacional` sao as cinco regras do PLANO-CORPUS.md, para quando as
    medidas do perfil forem usadas como medida.

    `leitura` guarda so as duas que importam para leitura critica do texto por
    um modelo: existe camada de texto, e o texto tem tamanho de dissertacao.
    As outras tres (pos_textual, n_capitulos, mediana_linhas) medem qualidade
    da reconstrucao de paragrafo em PDF, que nao afeta quem le o texto corrido.
    Enquanto a pendencia de `n_capitulos` nao fechar, aplica-las ao sorteio da
    fase 2 descarta por defeito do instrumento, nao do trabalho.
    """
    motivos = []

    if modo == "leitura":
        # palavras_total nao depende da delimitacao do texto principal, que
        # falha em parte dos PDFs: em 2021_Soares o perfil da 11.221 palavras
        # onde o analisar_pdf.py le 51.186. O teto de 250 mil e limite de
        # leitura, nao juizo sobre o trabalho: acima disso a leitura critica
        # nao cabe numa passada.
        total = num(linha.get("palavras_total"))
        if total is None:
            motivos.append("sem camada de texto ou leitura falhou")
        elif total < 8000:
            motivos.append(f"texto curto ({total:.0f} palavras no total)")
        elif total > 250000:
            motivos.append(f"longo demais para uma leitura ({total:.0f} palavras)")
        return motivos

    palavras = num(linha.get("palavras_texto_principal"))
    if palavras is None:
        motivos.append("sem camada de texto ou leitura falhou")
    else:
        if palavras < 8000:
            motivos.append(f"texto principal curto ({palavras:.0f} palavras)")
        elif palavras > 200000:
            motivos.append(f"texto principal longo ({palavras:.0f} palavras)")

    if True:
        pos = num(linha.get("pct_pos_textual"))
        if pos is not None and pos > 60:
            motivos.append(f"pos-textual em {pos:.1f}%, delimitacao errada")

        caps = num(linha.get("n_capitulos"))
        if caps is not None and (caps == 0 or caps > 20):
            motivos.append(f"n_capitulos = {caps:.0f}")

        med = num(linha.get("mediana_linhas"))
        if med is not None and med < 2:
            motivos.append(f"mediana_linhas = {med:.1f}, paragrafo fragmentado")

    return motivos


def ler_csv(caminho):
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def ano_de(texto):
    m = re.search(r"(19|20)\d{2}", str(texto or ""))
    return int(m.group(0)) if m else None


def chave_handle(valor):
    """Handle normalizado. O coletor renomeia o arquivo para
    `<ano>_<autor>_<colecao>-<numero>.pdf`, entao o nome do bitstream em
    metadados.csv nao serve de chave; o handle serve."""
    m = re.search(r"(\d+)[/-](\d+)", str(valor or ""))
    return f"{m.group(1)}/{m.group(2)}" if m else None


def carregar(pasta, modo="leitura"):
    """Junta perfil e metadados pelo handle."""
    dir_ = RAIZ / "corpus" / pasta
    perfil = ler_csv(dir_ / "perfil.csv")
    meta = {}
    for m in ler_csv(dir_ / "metadados.csv"):
        h = chave_handle(m.get("handle"))
        if h:
            meta[h] = m

    registros = []
    for p in perfil:
        nome = Path(str(p.get("arquivo") or "")).stem
        m = meta.get(chave_handle(nome.split("_")[-1]), {})
        ano = ano_de(m.get("ano")) or ano_de(nome)
        registros.append(
            {
                "arquivo": Path(str(p.get("arquivo") or "")).name,
                "autor": (m.get("autor") or "").strip(),
                "titulo": (m.get("titulo") or "").strip(),
                "tipo": (m.get("tipo") or "").strip(),
                "ano": ano,
                "motivos": motivos_descarte(p, modo),
                "motivos_populacional": motivos_descarte(p, "populacional"),
                "palavras": num(p.get("palavras_total")),
                "sistema_citacao": (p.get("sistema_citacao") or "").strip(),
            }
        )
    return registros


def sortear(elegiveis, n, semente):
    """Um sorteado por estrato, com os estratos definidos por ordem de ano.

    Trabalho sem ano vai para o fim da ordem. Se houver menos elegiveis que n,
    devolve todos.
    """
    if len(elegiveis) <= n:
        return list(elegiveis)

    ordenados = sorted(elegiveis, key=lambda r: (r["ano"] is None, r["ano"] or 0, r["arquivo"]))
    rnd = random.Random(semente)
    escolhidos = []
    total = len(ordenados)
    for i in range(n):
        ini = (i * total) // n
        fim = ((i + 1) * total) // n
        escolhidos.append(rnd.choice(ordenados[ini:fim]))
    return escolhidos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6, help="sorteados por orientador")
    ap.add_argument(
        "--modo",
        choices=["leitura", "populacional"],
        default="leitura",
        help="conjunto de regras de descarte",
    )
    ap.add_argument("--saida", default=str(RAIZ / "corpus" / "SORTEIO.md"))
    args = ap.parse_args()

    linhas = []
    linhas.append("# Triagem e sorteio")
    linhas.append("")
    linhas.append(
        "Gerado por `scripts/triar_sortear.py`. Sorteio deterministico, semente "
        f"`{SEMENTE}`: rodar de novo da a mesma lista."
    )
    linhas.append("")
    linhas.append(f"**Modo de descarte: `{args.modo}`.**")
    linhas.append("")
    if args.modo == "leitura":
        linhas.append(
            "Descarta so por ausencia de camada de texto e por texto principal "
            "fora da faixa de 8.000 a 200.000 palavras. As outras tres regras do "
            "`PLANO-CORPUS.md` (pos-textual, n_capitulos, mediana_linhas) medem "
            "qualidade da reconstrucao de paragrafo em PDF, e a fase 2 nao usa "
            "medida nenhuma: e leitura critica do texto corrido. Aplicadas aqui, "
            "elas descartariam por defeito do instrumento. `n_capitulos` esta "
            "entre as pendencias tecnicas conhecidas, e chega a marcar 431 "
            "capitulos numa dissertacao. A coluna 'Tambem cairia' abaixo registra "
            "quem sairia pelas cinco regras, para quando elas voltarem a valer.\n\n"
            "A contagem usada aqui e `palavras_total`, e nao "
            "`palavras_texto_principal`, porque a delimitacao do texto principal "
            "falha em parte dos PDFs: em `2021_Soares` o perfil da 11.221 "
            "palavras onde o `analisar_pdf.py` le 51.186 no mesmo arquivo. O teto "
            "de 250 mil palavras e limite de leitura, nao juizo sobre o trabalho."
        )
    else:
        linhas.append(
            "As cinco regras do `PLANO-CORPUS.md`, secao 'Triagem antes de medir'. "
            "Advertencia: enquanto a pendencia de `n_capitulos` nao fechar, boa "
            "parte destes descartes e artefato do detector de titulo, nao "
            "propriedade do trabalho."
        )
    linhas.append("")
    linhas.append(
        "Criterio do sorteio: os elegiveis sao ordenados por ano; a serie e "
        f"cortada em {args.n} estratos de tamanho igual; sorteia-se um de cada "
        "estrato. Isso espalha a amostra pelo periodo sem deixar a escolha "
        "dentro do estrato por conta de quem sorteia."
    )
    linhas.append("")

    resumo = []

    for pasta, orientador in PASTAS:
        registros = carregar(pasta, args.modo)
        if not registros:
            linhas.append(f"## `{pasta}` — {orientador}")
            linhas.append("")
            linhas.append("Sem `perfil.csv`. Nada a triar.")
            linhas.append("")
            continue

        descartados = [r for r in registros if r["motivos"]]
        elegiveis = [r for r in registros if not r["motivos"]]
        taxa = 100 * len(descartados) / len(registros)
        escolhidos = sortear(elegiveis, args.n, SEMENTE)

        resumo.append((pasta, orientador, len(registros), len(descartados), taxa, len(escolhidos)))

        linhas.append(f"## `{pasta}` — {orientador}")
        linhas.append("")
        linhas.append(
            f"{len(registros)} trabalhos, {len(descartados)} descartados "
            f"({taxa:.1f}%), {len(elegiveis)} elegiveis, {len(escolhidos)} sorteados."
        )
        linhas.append("")

        if descartados:
            linhas.append("### Descartados")
            linhas.append("")
            linhas.append("| Arquivo | Ano | Motivo |")
            linhas.append("| --- | --- | --- |")
            for r in sorted(descartados, key=lambda x: (x["ano"] or 0, x["arquivo"])):
                linhas.append(
                    f"| `{r['arquivo']}` | {r['ano'] or '?'} | {'; '.join(r['motivos'])} |"
                )
            linhas.append("")

        linhas.append("### Sorteados")
        linhas.append("")
        linhas.append("| Ano | Arquivo | Tipo | Palavras (total) | Citacao | Tambem cairia |")
        linhas.append("| --- | --- | --- | --- | --- | --- |")
        for r in sorted(escolhidos, key=lambda x: (x["ano"] or 0, x["arquivo"])):
            pal = f"{r['palavras']:.0f}" if r["palavras"] is not None else "?"
            extra = [m for m in r["motivos_populacional"] if m not in r["motivos"]]
            linhas.append(
                f"| {r['ano'] or '?'} | `{r['arquivo']}` | {r['tipo'] or '?'} | "
                f"{pal} | {r['sistema_citacao'] or '?'} | {'; '.join(extra) or '—'} |"
            )
        linhas.append("")

        anos = [r["ano"] for r in elegiveis if r["ano"]]
        if anos:
            linhas.append(
                f"Periodo dos elegiveis: {min(anos)} a {max(anos)}. "
                f"Anos sorteados: {', '.join(str(r['ano']) for r in sorted(escolhidos, key=lambda x: x['ano'] or 0) if r['ano'])}."
            )
            linhas.append("")

    linhas.insert(
        6,
        "\n".join(
            ["## Resumo", "", "| Pasta | Orientador | Total | Descartados | Taxa | Sorteados |", "| --- | --- | --- | --- | --- | --- |"]
            + [
                f"| `{p}` | {o} | {t} | {d} | {x:.1f}% | {s} |"
                for p, o, t, d, x, s in resumo
            ]
            + [""]
        ),
    )

    saida = Path(args.saida)
    saida.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Gravado em {saida}")
    for p, o, t, d, x, s in resumo:
        print(f"  {p:12s} {t:3d} trabalhos, {d:2d} descartados ({x:4.1f}%), {s} sorteados")


if __name__ == "__main__":
    main()

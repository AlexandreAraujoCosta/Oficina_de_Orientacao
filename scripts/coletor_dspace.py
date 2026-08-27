"""Coletor do repositorio da UnB (DSpace).

Uso, em duas fases separadas de proposito:

    python coletor_dspace.py sondar  <url_browse>
    python coletor_dspace.py listar  <url_browse> --saida metadados.csv
    python coletor_dspace.py baixar  metadados.csv --pasta <dir>

Sondar imprime o que a pagina devolve, para o formato ser conferido antes de
qualquer coleta. Nao ha pressa: intervalo entre requisicoes e repeticao em caso
de falha, conforme o plano do corpus.
"""
import argparse
import csv
import html
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (pesquisa academica; coleta lenta e com intervalo)"
PAUSA = 2.0


def buscar(url, tentativas=3, binario=False):
    for n in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                dados = r.read()
                return dados if binario else dados.decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError) as e:
            if n == tentativas:
                raise
            espera = PAUSA * 2 ** n
            print(f"  falha ({e}); nova tentativa em {espera:.0f}s", file=sys.stderr)
            time.sleep(espera)


def cmd_sondar(url):
    pagina = buscar(url)
    print(f"BYTES {len(pagina):,}")
    print(f"DSPACE7 (Angular)  {'sim' if 'ds-app' in pagina or '<app-root' in pagina else 'nao'}")
    print(f"JSPUI              {'sim' if '/jspui/' in pagina else 'nao'}")
    print(f"XMLUI              {'sim' if '/xmlui/' in pagina else 'nao'}")
    handles = sorted(set(re.findall(r"/handle/(\d+/\d+)", pagina)))
    print(f"HANDLES na pagina  {len(handles)}")
    for h in handles[:8]:
        print(f"   {h}")
    api = urllib.parse.urljoin(url, "/server/api")
    try:
        print(f"REST /server/api   {'responde' if buscar(api) else 'vazio'}")
    except Exception as e:
        print(f"REST /server/api   nao ({e})")
    print()
    print("--- primeiros 1200 caracteres ---")
    print(pagina[:1200])


def itens_da_listagem(url):
    """Percorre a listagem paginada e devolve (handle, titulo)."""
    vistos, saida, offset = set(), [], 0
    while True:
        sep = "&" if "?" in url else "?"
        pag = f"{url}{sep}rpp=100&offset={offset}"
        print(f"  listagem offset={offset}", file=sys.stderr)
        texto = buscar(pag)
        achados = re.findall(
            r'href="[^"]*?/handle/(\d+/\d+)"[^>]*>(.*?)</a>', texto, re.S)
        novos = 0
        for h, t in achados:
            if h in vistos:
                continue
            vistos.add(h)
            titulo = html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
            if titulo:
                saida.append((h, titulo))
                novos += 1
        if not novos:
            break
        offset += 100
        time.sleep(PAUSA)
    return saida


def cmd_listar(url, saida):
    itens = itens_da_listagem(url)
    print(f"{len(itens)} itens na listagem", file=sys.stderr)
    linhas = []
    for i, (h, titulo) in enumerate(itens, start=1):
        pagina_item = urllib.parse.urljoin(url, f"/handle/{h}")
        print(f"  [{i}/{len(itens)}] {h}", file=sys.stderr)
        try:
            html_item = buscar(pagina_item)
        except Exception as e:
            linhas.append({"handle": h, "titulo": titulo, "erro": str(e)})
            continue
        pdfs = re.findall(r'href="([^"]*?\.pdf[^"]*)"', html_item, re.I)
        pdf = urllib.parse.urljoin(pagina_item, pdfs[0]) if pdfs else ""
        def meta(nome):
            m = re.search(rf'name="{nome}"\s+content="([^"]*)"', html_item)
            return html.unescape(m.group(1)) if m else ""
        linhas.append({
            "handle": h,
            "titulo": titulo or meta("DC.title"),
            "autor": meta("DC.creator") or meta("citation_author"),
            "ano": meta("DCTERMS.issued") or meta("citation_date"),
            "tipo": meta("DC.type"),
            "pdf": pdf,
            "erro": "" if pdf else "sem pdf na pagina",
        })
        time.sleep(PAUSA)
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter=";",
                           fieldnames=["handle", "titulo", "autor", "ano", "tipo", "pdf", "erro"])
        w.writeheader()
        w.writerows(linhas)
    com = sum(1 for l in linhas if l.get("pdf"))
    print(f"gravados {len(linhas)} registros, {com} com PDF, em {saida}")


def cmd_baixar(metadados, pasta):
    destino = pathlib.Path(pasta)
    destino.mkdir(parents=True, exist_ok=True)
    with open(metadados, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    baixados = 0
    for i, l in enumerate(linhas, start=1):
        if not l.get("pdf"):
            continue
        autor = re.sub(r"[^\w]+", "", (l.get("autor") or "anon").split(",")[0])[:28]
        ano = re.sub(r"\D", "", l.get("ano") or "")[:4] or "sd"
        alvo = destino / f"{ano}_{autor}_{l['handle'].replace('/', '-')}.pdf"
        if alvo.exists():
            continue
        print(f"  [{i}/{len(linhas)}] {alvo.name}", file=sys.stderr)
        try:
            alvo.write_bytes(buscar(l["pdf"], binario=True))
            baixados += 1
        except Exception as e:
            print(f"     falhou: {e}", file=sys.stderr)
        time.sleep(PAUSA)
    print(f"{baixados} arquivos novos em {destino}")


CAMPOS = ["handle", "titulo", "autor", "orientador", "coorientador",
          "ano", "tipo", "pdf", "erro"]


def orientadores_da_pagina(html_item):
    """Orientador e coorientador da tabela de registro completo.

    A pagina do item traz `browse?type=advisor&value=<nome>` dentro da celula
    `dc_contributor_advisor`, e o mesmo com `advisorco` para a coorientacao. O
    menu de navegacao tambem tem links `type=advisor`, mas sem `value=`, e por
    isso a exigencia do parametro. Nao se usa `DC.contributor`, que mistura
    orientador e coorientador numa etiqueta so.
    """
    def nomes(tipo):
        achados = re.findall(
            rf'href="[^"]*?browse\?type={tipo}(?:&amp;|&)value=([^"&]+)"', html_item)
        saida, vistos = [], set()
        for a in achados:
            nome = html.unescape(urllib.parse.unquote_plus(a)).strip()
            if nome and nome not in vistos:
                vistos.add(nome)
                saida.append(nome)
        return saida

    # `advisorco` casaria com o padrao de `advisor`; o negative lookahead separa
    return " | ".join(nomes(r"advisor(?!co)")), " | ".join(nomes("advisorco"))


def cmd_orientadores(metadados):
    """Acrescenta orientador e coorientador a um metadados.csv ja existente.

    Retomavel: linha que ja tem orientador preenchido nao e buscada de novo.
    """
    caminho = pathlib.Path(metadados)
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))

    pendentes = [l for l in linhas if not (l.get("orientador") or "").strip()]
    print(f"{len(linhas)} registros, {len(pendentes)} sem orientador", file=sys.stderr)

    for i, l in enumerate(pendentes, start=1):
        h = (l.get("handle") or "").strip()
        if not h:
            continue
        url = f"https://repositorio.unb.br/handle/{h}"
        print(f"  [{i}/{len(pendentes)}] {h}", file=sys.stderr)
        try:
            pagina = buscar(url)
        except Exception as e:
            l["orientador"] = ""
            l["coorientador"] = ""
            l["erro"] = f"{l.get('erro', '')} orientador: {e}".strip()
            continue
        ori, coori = orientadores_da_pagina(pagina)
        l["orientador"] = ori
        l["coorientador"] = coori
        if not ori:
            l["erro"] = f"{l.get('erro', '')} sem orientador na pagina".strip()
        time.sleep(PAUSA)

    with caminho.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter=";", fieldnames=CAMPOS, extrasaction="ignore")
        w.writeheader()
        for l in linhas:
            w.writerow({c: l.get(c, "") for c in CAMPOS})

    com = sum(1 for l in linhas if (l.get("orientador") or "").strip())
    print(f"{com}/{len(linhas)} com orientador em {caminho}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("comando",
                    choices=["sondar", "listar", "baixar", "orientadores"])
    ap.add_argument("alvo")
    ap.add_argument("--saida", default="metadados.csv")
    ap.add_argument("--pasta", default="corpus")
    a = ap.parse_args()
    if a.comando == "sondar":
        cmd_sondar(a.alvo)
    elif a.comando == "listar":
        cmd_listar(a.alvo, a.saida)
    elif a.comando == "orientadores":
        cmd_orientadores(a.alvo)
    else:
        cmd_baixar(a.alvo, a.pasta)


if __name__ == "__main__":
    main()

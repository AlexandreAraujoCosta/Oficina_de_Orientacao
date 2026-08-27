"""Verifica e prepara os patches de harmonizacao emitidos pelo Luis.

Um patch e um reparo cuja versao correta ja existe no proprio trabalho. Levar
essa versao ao ponto fossilizado e copia, nao redacao, e por isso nao e tarefa
de modelo: o analisador entrega o localizador e a operacao, e este script busca
o texto na fonte e monta o resultado. Quem transcreve e o codigo.

Duas operacoes, e nenhuma outra:

    {"destino": "P163", "operacao": "copiar_de", "origem": "P671"}
    {"destino": "P289", "operacao": "substituir", "de": "assincronos",
     "para": "sincronos", "origem": "P267"}

O patch se autoverifica. Em `substituir`, a cadeia `de` tem de ocorrer uma vez
no paragrafo de destino; zero ocorrencias significa que o modelo escreveu
palavra que nao esta la, e o patch e recusado. Recusa nao e falha do script:
e achado sobre aquela leitura, e a taxa de recusa mede fidelidade ao texto sem
cotejo manual.

**Este script nunca escreve na fonte.** A saida e um relatorio com o texto atual
copiado da fonte, o texto proposto, e o estado de cada patch. Quem aplica no
arquivo e o autor, que precisa ler cada substituicao antes de aceita-la.

POR QUE NAO EDITAMOS O .DOCX DIRETAMENTE
----------------------------------------

Quatro razoes, e a ultima e a que decide.

1. Tecnica. O OOXML quebra o texto em runs arbitrarios: a palavra a substituir
   pode estar repartida entre tres elementos <w:t> por causa de revisao
   ortografica, marca de alteracao ou formatacao. Busca e troca no XML falha
   em silencio ou come formatacao. python-docx resolveria parte disso e nao
   esta instalado neste ambiente.

2. Rastro. O arquivo do autor carrega controle de alteracoes, comentarios e a
   ordem de paragrafos de que saem os localizadores. Reescrever o zip por fora
   arrisca perder ou reordenar isso, e entao os localizadores de todos os
   relatorios ja emitidos deixam de bater. Seria quebrar a correspondencia que
   sustenta a regra do localizador.

3. Concorrencia. Se o Word esta com o arquivo aberto, gravar por fora produz
   conflito e uma das versoes morre.

4. Doutrina, e esta e a razao principal. Aceitar sem ler e o modo de falhar.
   Script que grava direto no arquivo torna a aceitacao sem leitura o caminho
   padrao, porque bastaria rodar. Exigir que o autor leve cada substituicao a
   mao e atrito deliberado, e o atrito e a salvaguarda: quem defende o trabalho
   vai ser perguntado sobre a frase, e a frase passa a ser dele.

O custo disso e real e nao se disfarca: aplicar dez alinhamentos a mao e
tedioso, e tedio e exatamente a razao de ninguem atualizar lista de graficos.
Se um dia couber excecao, ela cabe onde nao ha o que julgar (sumario, listas,
paginacao), e nunca onde a substituicao muda o que o trabalho afirma.

Uso:
    python aplicar_patches.py <patches> <trabalho> [--saida rel.md] [--json x.json]

<patches> pode ser um .json com lista de objetos, ou o proprio relatorio .md,
de onde se extraem os objetos escritos dentro de bloco cercado por crase.
"""

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from conferir_consistencia import carregar  # noqa: E402

OPERACOES = ("copiar_de", "substituir")

RE_LOC = re.compile(r"P?(\d+)")
RE_CERCA = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)


# ---------------------------------------------------------------- entrada

def localizador(valor):
    """Aceita 'P289', '[P289]', '289' ou 289. Devolve int, ou None."""
    if valor is None:
        return None
    m = RE_LOC.search(str(valor))
    return int(m.group(1)) if m else None


def ler_patches(caminho):
    """Le a lista de .json, ou a extrai dos blocos cercados de um .md."""
    bruto = Path(caminho).read_text(encoding="utf-8", errors="replace")

    if caminho.lower().endswith(".json"):
        dados = json.loads(bruto)
        return dados if isinstance(dados, list) else [dados]

    patches = []
    for bloco in RE_CERCA.findall(bruto):
        for linha in bloco.splitlines():
            linha = linha.strip().rstrip(",")
            if not linha.startswith("{"):
                continue
            try:
                patches.append(json.loads(linha))
            except json.JSONDecodeError as e:
                patches.append({"_erro_de_leitura": f"{e}", "_linha": linha})
    return patches


# ---------------------------------------------------------------- verificacao

def normalizar_espaco(s):
    return re.sub(r"\s+", " ", s).strip()


def verificar(patch, indice):
    """Devolve (estado, motivo, texto_atual, texto_proposto).

    estado e um de: aplicavel, ja_aplicado, recusado, ambiguo.
    """
    if "_erro_de_leitura" in patch:
        return "recusado", "linha nao e JSON valido: " + patch["_erro_de_leitura"], None, None

    op = patch.get("operacao")
    if op not in OPERACOES:
        return "recusado", f"operacao desconhecida: {op!r}", None, None

    destino = localizador(patch.get("destino"))
    if destino is None:
        return "recusado", "sem destino", None, None
    if destino not in indice:
        return "recusado", f"P{destino} nao existe na fonte", None, None

    atual = indice[destino]

    if op == "copiar_de":
        origem = localizador(patch.get("origem"))
        if origem is None:
            return "recusado", "copiar_de sem origem", atual, None
        if origem not in indice:
            return "recusado", f"origem P{origem} nao existe na fonte", atual, None
        proposto = indice[origem]
        if normalizar_espaco(proposto) == normalizar_espaco(atual):
            return "ja_aplicado", f"P{destino} ja e identico a P{origem}", atual, proposto
        return "aplicavel", "", atual, proposto

    # substituir
    de = patch.get("de")
    para = patch.get("para")
    if de is None or para is None:
        return "recusado", "substituir exige 'de' e 'para'", atual, None
    if de == para:
        return "recusado", "'de' e 'para' sao iguais", atual, None

    n = atual.count(de)
    if n == 1:
        return "aplicavel", "", atual, atual.replace(de, para, 1)
    if n > 1:
        return "ambiguo", f"'{de}' ocorre {n} vezes em P{destino}", atual, None

    # Nao achou. Distingue ausencia real de diferenca de espacamento, porque as
    # duas pedem providencias diferentes.
    if normalizar_espaco(de) in normalizar_espaco(atual):
        return ("recusado",
                f"'{de}' so aparece em P{destino} com espacamento diferente",
                atual, None)

    # O reparo pode ja ter sido feito, mas o script NAO afirma isso: verificar
    # exigiria saber que aquele '{para}' e o resultado deste patch, e nao uma
    # ocorrencia qualquer. Cadeia curta casa em qualquer paragrafo, e quando
    # 'para' e substring de 'de' encontra-lo nao prova nada. Fica como nota.
    nota = ""
    if (len(para) >= 4 and para not in de
            and re.search(r"\b" + re.escape(para) + r"\b", atual)):
        nota = f"; '{para}' ocorre em P{destino}, o reparo pode ja ter sido feito, confira"
    return "recusado", f"'{de}' nao ocorre em P{destino}" + nota, atual, None


# ---------------------------------------------------------------- saida

CABECALHO = """<!-- Gerado por scripts/aplicar_patches.py a partir de {fonte}.
O modelo forneceu apenas localizadores e operacoes; todo texto citado abaixo
foi copiado da fonte por codigo. Nenhum arquivo de origem foi modificado. -->

# Patches de harmonizacao

Fonte: `{fonte}`

Cada bloco traz o texto atual do paragrafo, copiado da fonte, e o texto que
resulta da operacao. **Leia cada substituicao antes de aceita-la:** quem defende
o trabalho vai ser perguntado sobre a frase, e a frase passa a ser sua.
"""

ORDEM = ["aplicavel", "ambiguo", "ja_aplicado", "recusado"]

TITULO = {
    "aplicavel": "Aplicaveis",
    "ambiguo": "Ambiguos, decisao do autor",
    "ja_aplicado": "Ja aplicados, nada a fazer",
    "recusado": "Recusados pelo script",
}


def janela_troca(atual, de, para, largura=90):
    """Contexto ao redor da troca, para o autor achar o ponto sem ler tudo.

    Sem isto, uma palavra trocada dentro de um paragrafo de duzentas e
    invisivel na comparacao entre 'Esta' e 'Fica'.
    """
    pos = atual.find(de)
    if pos < 0:
        return None
    ini = max(0, pos - largura)
    fim = min(len(atual), pos + len(de) + largura)
    esq = ("..." if ini > 0 else "") + normalizar_espaco(atual[ini:pos])
    dir_ = normalizar_espaco(atual[pos + len(de):fim]) + ("..." if fim < len(atual) else "")
    sep = "" if dir_[:1] in ",.;:!?)" else " "
    return f"{esq} ~~{de}~~ **{para}**{sep}{dir_}"


def bloco(patch, estado, motivo, atual, proposto):
    destino = localizador(patch.get("destino"))
    origem = localizador(patch.get("origem"))
    op = patch.get("operacao", "?")

    linhas = [f"### [P{destino}] · {op}" if destino else f"### (sem destino) · {op}"]
    if origem:
        linhas.append(f"Versao vigente em **[P{origem}]**.")
    if motivo:
        linhas.append(f"**Motivo:** {motivo}")
    if estado == "aplicavel" and op == "substituir" and atual is not None:
        jan = janela_troca(atual, patch.get("de", ""), patch.get("para", ""))
        if jan:
            linhas.append("")
            linhas.append(f"**Troca:** {jan}")
    if atual is not None:
        linhas.append("")
        linhas.append("**Esta:**")
        linhas.append("> " + atual.replace("\n", "\n> "))
    if proposto is not None and estado in ("aplicavel",):
        linhas.append("")
        linhas.append("**Fica:**")
        linhas.append("> " + proposto.replace("\n", "\n> "))
    linhas.append("")
    return "\n".join(linhas)


def relatorio(resultados, fonte):
    partes = [CABECALHO.format(fonte=fonte)]

    total = len(resultados)
    contagem = {e: 0 for e in ORDEM}
    for r in resultados:
        contagem[r["estado"]] = contagem.get(r["estado"], 0) + 1

    recusados = contagem["recusado"] + contagem["ambiguo"]
    taxa = (recusados / total * 100) if total else 0.0

    partes.append("## Resumo\n")
    partes.append(f"- Patches recebidos: **{total}**")
    for e in ORDEM:
        partes.append(f"- {TITULO[e]}: **{contagem[e]}**")
    partes.append(
        f"\n**Taxa de recusa: {taxa:.1f}%** "
        f"({recusados} de {total}). A recusa mede fidelidade do modelo ao texto: "
        "patch que nao bate e localizador ou palavra que a leitura errou.\n"
    )

    for e in ORDEM:
        grupo = [r for r in resultados if r["estado"] == e]
        if not grupo:
            continue
        partes.append(f"\n---\n\n## {TITULO[e]} ({len(grupo)})\n")
        for r in grupo:
            partes.append(bloco(r["patch"], r["estado"], r["motivo"],
                                r["atual"], r["proposto"]))

    return "\n".join(partes), contagem, taxa


# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser(
        description="Verifica patches de harmonizacao contra a fonte. "
                    "Nunca escreve no arquivo de origem.")
    ap.add_argument("patches", help=".json com a lista, ou o relatorio .md")
    ap.add_argument("trabalho", help=".docx ou .pdf")
    ap.add_argument("--saida", help="relatorio de saida (padrao: PATCHES-<trabalho>.md)")
    ap.add_argument("--json", dest="json_saida",
                    help="grava tambem o resultado em JSON, para trilha de auditoria")
    a = ap.parse_args()

    patches = ler_patches(a.patches)
    if not patches:
        print("Nenhum patch encontrado em", a.patches)
        return 1

    indice = dict(carregar(a.trabalho))

    resultados = []
    for p in patches:
        estado, motivo, atual, proposto = verificar(p, indice)
        resultados.append({"patch": p, "estado": estado, "motivo": motivo,
                           "atual": atual, "proposto": proposto})

    texto, contagem, taxa = relatorio(resultados, Path(a.trabalho).name)

    destino = Path(a.saida) if a.saida else Path(
        f"PATCHES-{Path(a.trabalho).stem}.md")
    destino.write_text(texto, encoding="utf-8")

    if a.json_saida:
        Path(a.json_saida).write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(patches)} patches lidos de {Path(a.patches).name}")
    for e in ORDEM:
        print(f"  {TITULO[e]}: {contagem[e]}")
    print(f"  taxa de recusa: {taxa:.1f}%")
    print(f"Relatorio em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

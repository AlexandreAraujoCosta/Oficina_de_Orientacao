"""Gera o caderno de conferencia: o trabalho com os paragrafos numerados.

POR QUE ISTO EXISTE

Todo apontamento do Luis traz [P123], e toda determinacao diz que se
confere abrindo o arquivo naquele paragrafo. **Para quem recebe o relatorio, essa
instrucao e inexecutavel:** ninguem escreve uma dissertacao pensando em numero de
paragrafo, e o Word nao mostra essa contagem. O localizador e o sistema de
coordenadas do instrumento, nao o do autor.

O caderno traduz um no outro. E resolve um segundo problema, maior e menos
visivel: **o relatorio foi feito sobre o texto extraido, e nao sobre o arquivo
original.** Se a extracao juntou dois paragrafos, perdeu uma nota de rodape ou
embaralhou uma tabela, a analise herdou o defeito e ninguem tem como saber. Com o
caderno na mao, o autor ve exatamente o objeto que foi lido, e discorda dele se
for o caso.

Duas formas:

    completo    o trabalho inteiro, numerado. E o mapa: serve para achar
                qualquer localizador e para inspecionar a extracao.
    citados     so os paragrafos que o relatorio cita, com vizinhos. E a mesa
                de trabalho: serve para conferir os apontamentos um a um.

Quando se passa um ou mais relatorios, cada paragrafo citado recebe marca e a
lista de itens que o citam, de modo que o autor vê, no proprio texto, quantos
apontamentos tocam aquele ponto.

Uso:
    python caderno_conferencia.py <trabalho> [--relatorio R.md ...]
                                  [--saida CADERNO.md] [--citados] [--vizinhos N]
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from conferir_consistencia import carregar  # noqa: E402

# [P123] ou [P123-P125], com hifen simples ou longo. O colchete e opcional
# porque uma das agregacoes ja entregues escreveu P123 sem ele, 499 vezes: o
# formato do localizador e o que liga relatorio, caderno e script de correção, e
# aceitar as duas formas aqui e mais barato que reescrever relatorio entregue.
# O lookbehind evita casar o P de siglas e de palavras.
RE_REF = re.compile(r"(?<![A-Za-z0-9])\[?P(\d+)(?:\s*[-–]\s*P?(\d+))?\]?")

# Titulo de item do relatorio: "## D12. ...", "### H3 — ...", "### 3.1.1 ...".
# O grupo aceita numeracao hierarquica inteira: sem o (?:\.\d+)* o rotulo de
# "3.1.1" saía como "3", que manda o leitor para a secao e nao para o item.
RE_ITEM = re.compile(r"^#{2,4}\s+((?:[A-Z]{1,3})?\d+(?:\.\d+)*[a-z]?)[\.\)\s—–-]")

# O rotulo em negrito do item, "**S14. ...**", que e o endereco fino. Sem ele o
# caderno so alcanca a secao, e uma secao reune quinze itens: quem abre o
# paragrafo descobre que ha algo sobre ele em 2.2 e ainda tem de achar o qual.
# Com o rotulo, o paragrafo aponta para a sugestao exata que fala dele.
RE_ROTULO = re.compile(r"^\*\*((?:[A-Z]{1,3}\d+[a-z]?|\d+(?:\.\d+){1,3}))\.?\s")


def citacoes(relatorios):
    """Devolve {numero_do_paragrafo: [rotulos dos itens que o citam]}.

    O rotulo e o do item vigente quando a citacao aparece. Citacao antes do
    primeiro titulo fica sob '(abertura)', que costuma ser o resumo do relatorio.
    """
    mapa = defaultdict(list)
    # Com um relatorio so, prefixar o nome dele em toda linha e ruido: o leitor
    # ja sabe de onde vem. Com varios, o prefixo e a unica forma de distinguir.
    varios = len(relatorios) > 1
    for caminho in relatorios:
        nome = Path(caminho).stem
        item = "(abertura)"
        for linha in Path(caminho).read_text(encoding="utf-8", errors="replace").splitlines():
            m = RE_ROTULO.match(linha) or RE_ITEM.match(linha)
            if m:
                item = m.group(1)
            for ini, fim in RE_REF.findall(linha):
                ini = int(ini)
                fim = int(fim) if fim else ini
                if fim < ini:
                    ini, fim = fim, ini
                # faixa larga demais é remissao de bloco, nao citacao de ponto
                if fim - ini > 40:
                    continue
                rotulo = f"{nome}:{item}" if varios else item
                for n in range(ini, fim + 1):
                    if rotulo not in mapa[n]:
                        mapa[n].append(rotulo)
    return mapa


CABECALHO = """<!-- Gerado por scripts/caderno_conferencia.py a partir de {fonte}. -->

# Caderno de conferência · {fonte}

Este é **o texto sobre o qual a análise foi feita**, com os parágrafos numerados.
Os apontamentos do relatório citam esses números, e é aqui que se confere cada um.

**Leia esta ressalva antes de usar.** O que está abaixo é a extração automática do
seu arquivo, e não o arquivo. A extração pode ter juntado dois parágrafos, separado
um, perdido uma nota de rodapé ou desmontado uma tabela. **Se algum trecho aqui não
corresponder ao que você escreveu, o apontamento que o cita herdou esse defeito**, e
a discordância é legítima: avise em vez de corrigir o trabalho.

{resumo}
"""

LEGENDA_MARCA = """
Parágrafos citados pelo relatório aparecem marcados com **▸** e a lista dos itens
que os citam. Quando vários itens tocam o mesmo parágrafo, é sinal de que aquele
ponto concentra o problema, e não de que há vários problemas.
"""


def montar(paragrafos, mapa, somente_citados, vizinhos):
    if somente_citados and mapa:
        manter = set()
        for n in mapa:
            for k in range(n - vizinhos, n + vizinhos + 1):
                manter.add(k)
    else:
        manter = None

    linhas, anterior = [], None
    for numero, texto in paragrafos:
        if manter is not None and numero not in manter:
            continue
        if anterior is not None and numero != anterior + 1:
            linhas.append("")
            linhas.append("*[...]*")
        linhas.append("")
        if numero in mapa:
            itens = ", ".join(mapa[numero])
            linhas.append(f"**▸ P{numero}** · {itens}")
            linhas.append("")
            linhas.append(texto if texto else "*(parágrafo vazio na extração)*")
        else:
            linhas.append(f"**P{numero}** · {texto}" if texto
                          else f"**P{numero}** · *(parágrafo vazio na extração)*")
        anterior = numero
    return "\n".join(linhas)


def main():
    ap = argparse.ArgumentParser(
        description="Gera o caderno de conferência com os parágrafos numerados.")
    ap.add_argument("trabalho", help=".docx ou .pdf")
    ap.add_argument("--relatorio", action="append", default=[],
                    help="relatório .md a cruzar; repetível")
    ap.add_argument("--saida", help="padrão: CADERNO-<trabalho>.md")
    ap.add_argument("--citados", action="store_true",
                    help="só os parágrafos citados e seus vizinhos")
    ap.add_argument("--vizinhos", type=int, default=1,
                    help="parágrafos de contexto de cada lado (padrão 1)")
    a = ap.parse_args()

    paragrafos = carregar(a.trabalho)
    mapa = citacoes(a.relatorio) if a.relatorio else {}

    fonte = Path(a.trabalho).name
    citados = len(mapa)
    if mapa:
        resumo = (f"São **{len(paragrafos)} parágrafos**, dos quais "
                  f"**{citados} são citados** pelo relatório.\n" + LEGENDA_MARCA)
        if a.citados:
            resumo += ("\nEsta é a versão reduzida: só os parágrafos citados e "
                       f"{a.vizinhos} de contexto de cada lado. Para o texto "
                       "inteiro, gere sem `--citados`.\n")
    else:
        resumo = f"São **{len(paragrafos)} parágrafos**.\n"
        if a.citados:
            print("  aviso: --citados sem --relatorio não filtra nada")

    corpo = montar(paragrafos, mapa, a.citados, a.vizinhos)
    texto = CABECALHO.format(fonte=fonte, resumo=resumo) + "\n---\n" + corpo + "\n"

    destino = Path(a.saida) if a.saida else Path(f"CADERNO-{Path(a.trabalho).stem}.md")
    destino.write_text(texto, encoding="utf-8")

    print(f"{len(paragrafos)} parágrafos" +
          (f", {citados} citados por {len(a.relatorio)} relatório(s)" if mapa else ""))
    print(f"Caderno em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

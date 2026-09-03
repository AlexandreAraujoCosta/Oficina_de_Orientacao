# -*- coding: utf-8 -*-
"""De um relatorio, as duas versoes: a do aluno e a do orientador.

POR QUE DUAS

Elas nao diferem em rigor, diferem em par. A do aluno anda junto com o .docx
comentado, em que cada correcao esta na margem do paragrafo, com o que fazer e
os numeros; ali o relatorio so precisa de uma linha por item e de um ponteiro
para a margem. A do orientador nao tem esse par, porque quem orienta le o
relatorio e nao abre o Word do orientando: ali as correcoes vao por extenso, na
ordem em que se le.

Medido em 01/09/2026, num relatorio de 13.664 palavras: as correcoes por extenso
eram 62% do documento e ja estavam todas na margem. A versao do aluno caiu para
5.577 palavras, de 46 paginas para 23.

O QUE ESTE PROGRAMA NAO FAZ, E DE PROPOSITO

Nao escreve, nao classifica e nao troca a pessoa do verbo. Um antecessor deste
programa carregava uma tabela de substituicoes para passar o merito a segunda
pessoa, e uma lista, escrita a mao, dizendo de que tipo era o trabalho de cada
item. As duas coisas sao julgamento e pertencem a quem redige o relatorio, que
tem o trabalho em maos; aqui elas viravam configuracao presa a um orientando so,
e o programa nao servia para o proximo.

O CONTRATO COM O RELATORIO DE ENTRADA

O relatorio ja vem escrito na voz certa (segunda pessoa para o merito e para a
acao, impessoal para o defeito) e ja traz o veredito como titulo da primeira
secao. Deste programa ele precisa apenas de marcas:

    ### S7. Titulo do item                 <- item de correcao, numerado
    **Tipo:** acrescentar o numero que falta   <- como agrupar no indice
    **Marca:** trocar prevalescente por prevalecente   <- texto dos pontos repetidos
    **Ancora:** [P172] [P181]              <- so quando o item nao cita paragrafo

`Tipo` e o unico campo cuja falta muda a saida: sem ele o indice sai numa lista
unica, e o programa avisa. Os demais tem padrao.

    python duas_versoes.py RELATORIO.md --secao-correcoes 3 --anexo-de A
"""
import argparse
import re
import sys
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RE_ITEM = r"(?m)^### %s(\d+)\.\s*(.*)$"
RE_CAMPO = r"(?m)^\*\*%s:\*\*\s*(.+?)\s*$"


def secoes(texto):
    """Parte o relatorio nos titulos de nivel 2, preservando a ordem."""
    partes = re.split(r"(?m)^## ", texto)
    cabeca = partes[0]
    fora = []
    for p in partes[1:]:
        titulo, _, corpo = p.partition("\n")
        fora.append((titulo.strip(), corpo.rstrip()))
    return cabeca.rstrip(), fora


def campo(bloco, nome):
    m = re.search(RE_CAMPO % nome, bloco)
    return m.group(1) if m else None


def localizadores(bloco, so_colchete=True):
    """Onde o item manda olhar.

    So os localizadores entre colchetes, que sao os das transcricoes, isto e,
    os paragrafos em que o defeito esta. As mencoes em prosa ("o P159 ja diz o
    certo") apontam o modelo a copiar, e marcar com uma critica um paragrafo
    que esta certo e pior do que nao marcar: medido em 01/09/2026, incluir a
    prosa deu 109 comentarios em 79 paragrafos, num capitulo de 57 paginas.

    Itens sem transcricao (os do anexo, que falam de figura ou de grafia) nao
    tem colchete nenhum, e ali a mencao em prosa e o proprio lugar a corrigir.
    """
    padrao = r"\[(P\d{1,4})\]" if so_colchete else r"\b(P\d{1,4})\b"
    vistos = []
    for p in re.findall(padrao, bloco):
        if p not in vistos:
            vistos.append(p)
    if not vistos:
        anc = campo(bloco, "Âncora") or campo(bloco, "Ancora")
        if anc:
            vistos = re.findall(r"P\d{1,4}", anc)
    return vistos


def enderecar(secao, letra, so_colchete=True):
    """Escreve, ao fim de cada item, a lista de pontos que ele manda marcar.

    Sem isso o item ancora um comentario so, no primeiro ponto, e os demais
    lugares onde o mesmo defeito ocorre chegam sem marca: medido em
    01/09/2026, 18 comentarios no lugar de 47.

    ESTE PROGRAMA NAO ESCREVE `Marca`, E ISSO E DECISAO, NAO ESQUECIMENTO.

    O `anotar_docx.py` marca todos os pontos do item quando existe o campo
    `Marca`, e um so quando nao existe. O campo serve para a instrucao curta que
    vai nos pontos repetidos, e ela e sempre particular ao item ("trocar
    prevalescente por prevalecente"). Uma versao anterior deste programa gerava
    um `Marca` generico quando o autor nao escrevia nenhum, e o resultado foi
    medido numa conferencia de compreensibilidade em 02/09/2026: o mesmo texto
    chegava em 32 dos 33 itens, falando de "item S1" e do "primeiro ponto
    marcado", que e vocabulario do relatorio e nao do trabalho, e a leitora
    escreveu que depois da primeira aparicao deixou de ler a frase. Um item
    sozinho marcava 61 pontos com esse texto.

    Se a correcao e a mesma em cada ocorrencia, quem redige escreve o `Marca`.
    Se nao escreve, o item marca um ponto e o relatorio lista os demais.

    O separador `---` que fecha a secao e arrastado pelo ultimo item, e o
    endereco acabava depois dele, fora do item e cortado por quem recorta a
    secao. Ele sai daqui e volta no fim.
    """
    marcas = list(re.finditer(RE_ITEM % letra, secao))
    saida, cursor = [], 0
    for i, m in enumerate(marcas):
        saida.append(secao[cursor:m.start()])
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(secao)
        bloco = secao[m.start():fim]
        locs = localizadores(bloco, so_colchete)
        corpo, rabo = bloco.rstrip(), ""
        while corpo.rstrip().endswith("---"):
            corpo = corpo.rstrip()[:-3].rstrip()
            rabo = "\n\n---"
        pedacos = [corpo]
        if locs:
            pedacos.append("*(Ocorrências: %s)*"
                           % " ".join("[%s]" % p for p in locs))
        saida.append("\n\n".join(pedacos) + rabo + "\n")
        cursor = fim
    saida.append(secao[cursor:])
    return "".join(saida)


def indice(secao, letra, nome_docx):
    """Uma linha por item, agrupada pelo tipo de trabalho que ele pede.

    Agrupar por tipo, e nao numerar de um a vinte e seis, porque a contagem
    chega como placar e o tipo chega como plano de trabalho. A classificacao
    vem do campo `Tipo` de cada item, escrito por quem redigiu o relatorio.
    """
    SOBRA = "Correções"
    itens, ordem = {}, []
    marcas = list(re.finditer(RE_ITEM % letra, secao))
    n_tipados = 0
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(secao)
        bloco = secao[m.start():fim]
        t = campo(bloco, "Tipo")
        n_tipados += 1 if t else 0
        tipo = t or SOBRA
        if tipo not in itens:
            itens[tipo] = []
            ordem.append(tipo)
        itens[tipo].append((m.group(1), m.group(2).strip()))
    # O balde dos itens sem Tipo vai por ultimo, sempre. Ordenado por primeira
    # aparicao ele caia no meio e partia os grupos nomeados, o que se viu no
    # primeiro teste real do programa, em 02/09/2026.
    if SOBRA in ordem:
        ordem = [t for t in ordem if t != SOBRA] + [SOBRA]
    total = sum(len(v) for v in itens.values())
    estado = ("nenhum" if n_tipados == 0
              else "todos" if n_tipados == total else "parte")
    L = ["",
         "**Cada uma destas correções está comentada na margem do arquivo "
         "`%s`, no parágrafo a que se refere**, com o que fazer ali e os números "
         "que sustentam o apontamento. Aqui vai uma linha por item, agrupada "
         "pelo tipo de trabalho que pede, para você ver de que natureza é o "
         "serviço antes de abrir o documento." % nome_docx,
         ""]
    for tipo in ordem:
        # O valor de `Tipo` costuma vir com ponto final, porque quem escreve o
        # item escreve uma frase. Como titulo de grupo, o ponto sobra.
        nome = tipo.strip().rstrip(".")
        L += ["### %s" % (nome[0].upper() + nome[1:]), ""]
        for num, titulo in itens[tipo]:
            L.append("- **%s%s.** %s" % (letra, num, titulo))
        L.append("")
    return "\n".join(L), total, estado


def main():
    ap = argparse.ArgumentParser(description="As duas versoes de um relatorio.")
    ap.add_argument("relatorio")
    ap.add_argument("--secao-correcoes", required=True,
                    help="numero da secao que traz as correcoes por extenso, "
                         "como aparece no titulo (ex.: 3)")
    ap.add_argument("--secao-anexo",
                    help="numero da secao das correcoes que nao mudam afirmacao")
    ap.add_argument("--letra", default="S", help="letra dos itens (padrao S)")
    ap.add_argument("--letra-anexo", default="SC")
    ap.add_argument("--docx", default="o .docx anotado que acompanha",
                    help="nome do .docx comentado, citado no indice")
    ap.add_argument("--saida", help="prefixo dos arquivos (padrao: ao lado)")
    a = ap.parse_args()

    fonte = Path(a.relatorio)
    cabeca, lista = secoes(fonte.read_text(encoding="utf-8"))

    def acha(num):
        for i, (tit, corpo) in enumerate(lista):
            if tit.startswith(num + "."):
                return i, tit, corpo
        sys.exit("nao achei a secao %s. Titulos: %s"
                 % (num, ", ".join(t for t, _ in lista)))

    i_cor, t_cor, s_cor = acha(a.secao_correcoes)
    s_cor = enderecar(s_cor, a.letra, so_colchete=True)
    idx, n_itens, tipagem = indice(s_cor, a.letra, a.docx)
    if not n_itens:
        sys.exit("nenhum item `### %s<n>.` na secao %s: nada a separar."
                 % (a.letra, a.secao_correcoes))

    s_anx = None
    if a.secao_anexo:
        i_anx, t_anx, s_anx = acha(a.secao_anexo)
        s_anx = enderecar(s_anx, a.letra_anexo, so_colchete=False)

    def monta(com_correcoes):
        out = [cabeca, ""]
        for i, (tit, corpo) in enumerate(lista):
            if a.secao_anexo and tit.startswith(a.secao_anexo + "."):
                if com_correcoes:
                    out += ["## " + tit, s_anx, "", "---", ""]
                continue
            if i == i_cor:
                if com_correcoes:
                    out += ["## " + tit, s_cor, "", "---", ""]
                else:
                    corte = t_cor.split(".", 1)[1].strip()
                    out += ["## %s. %s" % (a.secao_correcoes, corte), idx,
                            "---", ""]
                continue
            out += ["## " + tit, corpo, "", "---", ""]
        while out and out[-1] in ("", "---"):
            out.pop()
        saida = "\n".join(out) + "\n"

        # SEPARADORES QUE SE ACUMULAM
        #
        # Cada secao fecha com "---", e o corpo de algumas ja traz o seu. O
        # resultado sao dois filetes horizontais seguidos, com um vao grande
        # entre eles, e no PDF de 03/09/2026 isso apareceu cinco vezes num
        # relatorio so. Nao e defeito do LaTeX: sao duas regras no Markdown, e
        # ele desenha as duas. Aqui elas viram uma.
        saida = re.sub(r"(?:^---[ \t]*\n(?:[ \t]*\n)*){2,}", "---\n\n",
                       saida, flags=re.M)
        return saida

    aluno, docente = monta(False), monta(True)

    # ---- conferencias, e nenhuma delas passa vazia
    falhas = []
    definidos = set(re.findall(RE_ITEM % a.letra, docente))
    definidos = {n for n, _ in definidos}
    citados = set(re.findall(r"\b%s(\d{1,2})\b" % a.letra, docente))
    orfaos = sorted(citados - definidos, key=int)
    if orfaos:
        falhas.append("remissoes a itens inexistentes: %s"
                      % ", ".join(a.letra + x for x in orfaos))
    for n in definidos:
        if ("- **%s%s.**" % (a.letra, n)) not in aluno:
            falhas.append("%s%s ficou fora do indice" % (a.letra, n))
    if definidos and ("- **%s%s.**" % (a.letra, sorted(definidos, key=int)[0])
                      not in aluno):
        falhas.append("controle positivo: nem o primeiro item esta no indice")
    if re.search(RE_ITEM % a.letra, aluno):
        falhas.append("a versao do aluno nao deveria trazer item por extenso")
    if falhas:
        sys.exit("NAO GRAVADO:\n  " + "\n  ".join(falhas))

    base = Path(a.saida) if a.saida else fonte.with_suffix("")
    p_al = base.with_name(base.name + "-ALUNO.md")
    p_do = base.with_name(base.name + "-DOCENTE.md")
    p_al.write_text(aluno, encoding="utf-8")
    p_do.write_text(docente, encoding="utf-8")

    print("  %s: %d palavras" % (p_al.name, len(aluno.split())))
    print("  %s: %d palavras" % (p_do.name, len(docente.split())))
    print("  %d itens, todos no indice, nenhuma remissao orfa" % n_itens)
    if tipagem == "nenhum":
        print("  AVISO: nenhum item trouxe `**Tipo:**`, e por isso o indice saiu")
        print("         numa lista unica. Agrupado por tipo de trabalho ele deixa")
        print("         de ser placar; a classificacao e de quem redige o relatorio.")
    elif tipagem == "parte":
        print("  AVISO: parte dos itens trouxe `**Tipo:**` e parte nao. Os sem tipo")
        print("         foram para um grupo `Correcoes` no fim, que e o menos util")
        print("         do indice: vale dar tipo a eles tambem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

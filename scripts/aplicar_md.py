# -*- coding: utf-8 -*-
"""Aplica os reparos no .md, como substituicoes de CriticMarkup.

POR QUE ISTO EXISTE

E o par de `aplicar_docx.py` no caminho em que nao ha `.docx`: o trabalho entrou
em PDF, a correcao passa a ser feita no texto extraido, e markdown nao tem
controle de alteracoes. O CriticMarkup e a convencao feita para suprir, e a
mesma que `anotar_md.py` ja usa para os apontamentos:

    {~~antes~>depois~~}       a troca que este programa escreve
    {>>comentario<<}          o que ele nao conseguiu aplicar

Quem resolve as marcas depois e `limpar_md.py`, que aceita e recusa uma a uma.

O QUE MUDA EM RELACAO AO CAMINHO DO .DOCX

Some a unica razao de recusa que la e a mais comum: no texto extraido nao ha
italico nem nota estruturada, e por isso nao ha trecho que atravesse formatacao.
O que sobra sao as recusas de endereco: paragrafo que nao existe, indice de
frase fora da faixa, e `Esta` com texto digitado.

Entra uma recusa que la nao existe: o CriticMarkup nao tem escape, e um `Fica`
que traga `~~`, `~>` ou `<<}` fecharia a marca antes da hora.

A PROVA QUE ELE DA ANTES DE GRAVAR

Resolvidas as marcas pela recusa, o arquivo volta a ser o original, caractere
por caractere. Reprovar impede a gravacao.

    python aplicar_md.py --frases <ENTREGA-PARAGRAFOS-*.md> <ENTREGA-CORRETOR-*.md>
    python aplicar_md.py <ENTREGA-PARAGRAFOS-*.md> <reparos.md> [--lista ENTREGA-CORRETOR-*.md]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reparos as R                                     # noqa: E402
from anotar_md import itens, RE_LINHA                   # noqa: E402

CABECALHO = """
> **Este arquivo traz as correções propostas, em CriticMarkup.**
> `{~~antes~>depois~~}` é uma troca, e cada uma delas se aceita ou se recusa.
> `{>>comentário<<}` é o que não virou troca, com a proposta dentro, e some
> sempre: não há decisão a tomar num comentário.
> Editor que reconhece as marcas as mostra como revisão; editor que não
> reconhece mostra o texto entre chaves, e ele continua legível.
> Para resolver as marcas: `limpar_md.py --aceitar S1,S14`, ou
> `--recusar-tudo`. A prévia aceita tudo e não é a sua decisão.
"""

RE_SUB = re.compile(r"\{~~(.*?)~>(.*?)~~\}", re.S)
RE_COMENTARIO = re.compile(r"\{>>(.*?)<<\}", re.S)
# Sem escape na convencao, estes tres fecham a marca no meio da frase.
PROIBIDOS = ("~~", "~>", "<<}", "{>>")


def linhas_numeradas(caminho):
    """{numero do paragrafo: indice da linha}, e as linhas."""
    linhas = Path(caminho).read_text(encoding="utf-8").splitlines()
    onde = {}
    for i, l in enumerate(linhas):
        m = RE_LINHA.match(l)
        if m:
            onde[int(m.group(1))] = i
    return linhas, onde


def corpo(linha):
    """A linha sem o rotulo [P123], e onde o corpo comeca."""
    m = RE_LINHA.match(linha)
    ini = m.end() + (1 if linha[m.end():m.end() + 1] == " " else 0)
    return linha[ini:], ini


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Reparos no .md, em CriticMarkup.")
    ap.add_argument("trabalho", help="a extração numerada")
    ap.add_argument("arquivo", help="os reparos; com --frases, a ENTREGA-CORRETOR-*.md")
    ap.add_argument("--frases", action="store_true",
                    help="não aplica nada: escreve a folha de frases endereçáveis")
    ap.add_argument("--lista", help="ENTREGA-CORRETOR-*.md, para comentar os itens sem reparo")
    ap.add_argument("--saida")
    a = ap.parse_args()
    a.lista = a.arquivo if a.frases else a.lista

    linhas, onde = linhas_numeradas(a.trabalho)
    if not onde:
        sys.exit("nenhum parágrafo numerado neste arquivo: ele não é uma extração.")
    original = "\n".join(linhas)

    if a.frases:
        lista = itens(a.lista)
        if not lista:
            sys.exit("nenhum item com localizador na lista: não há o que endereçar.")

        def resolve(n):
            if n not in onde:
                return None
            # No texto extraido nao ha formatacao a atravessar, e por isso toda
            # frase e aplicavel: a folha sai sem nenhum ✗.
            return corpo(linhas[onde[n]])[0], lambda x, y: True

        dest = Path(a.saida) if a.saida else Path(a.lista).with_name(
            "FRASES-" + Path(a.trabalho).stem + ".md")
        total, aptas = R.escrever_folha(
            dest, Path(a.trabalho).name, "aplicar_md.py",
            "não pode virar substituição", lista, resolve, lambda t: t)
        print("  %s: %d frases endereçáveis, %d delas aplicáveis (%.0f%%)"
              % (dest.name, total, aptas, 100.0 * aptas / max(total, 1)))
        return 0

    lista = R.ler_reparos(a.arquivo)
    if not lista:
        sys.exit("nenhum bloco de reparo neste arquivo: ele precisa de **Está:** e **Fica:**.")

    plano, recusas = {}, []
    for r in lista:
        def recusa(razao):
            recusas.append((r, razao))
        if r.erro:
            recusa(r.erro)
            continue
        if r.par not in onde:
            recusa("o parágrafo [P%d] não existe neste arquivo" % r.par)
            continue
        texto = corpo(linhas[onde[r.par]])[0]
        if r.frase is None:
            ini, fim = 0, len(texto)
        else:
            fs = R.frases(texto)
            if not (1 <= r.frase <= len(fs)):
                recusa("o parágrafo tem %d frase(s), e o reparo pediu a %d"
                       % (len(fs), r.frase))
                continue
            ini, fim = fs[r.frase - 1]
        ini, fim = R.limites(texto, ini, fim)
        if ini >= fim:
            recusa("o trecho endereçado está vazio")
            continue
        if texto[ini:fim] == r.novo:
            recusa("o texto proposto é igual ao que já está lá")
            continue
        mau = next((p for p in PROIBIDOS if p in r.novo), None)
        if mau:
            recusa("o texto proposto traz %r, que fecha a marca de CriticMarkup "
                   "antes da hora" % mau)
            continue
        if not r.novo:
            antes = fim
            while fim < len(texto) and texto[fim] == " ":
                fim += 1
            if fim == antes:
                while ini > 0 and texto[ini - 1] == " ":
                    ini -= 1
        conflito = next((p for p in plano.get(r.par, [])
                         if not (fim <= p[0] or ini >= p[1])), None)
        if conflito:
            recusa("o trecho se sobrepõe ao do reparo %s, no mesmo parágrafo"
                   % conflito[2].codigo)
            continue
        plano.setdefault(r.par, []).append((ini, fim, r))

    # ---- escreve de tras para diante, para os deslocamentos nao andarem
    esperado = {}
    for n in plano:
        i = onde[n]
        texto, desloc = corpo(linhas[i])
        novo = texto
        for ini, fim, r in sorted(plano[n], key=lambda t: -t[0]):
            # O codigo vai num comentario colado na troca, e nao por enfeite:
            # `limpar_md.py --aceitar S26` procura o codigo nos 400 caracteres
            # seguintes a marca, e sem ele a aceitacao seletiva nao alcanca
            # troca nenhuma. Junto vai o campo Muda, que e a razao da troca:
            # alteracao sem razao ao lado e alteracao que se aceita sem ler.
            razao = (" " + r.muda) if r.muda else ""
            nota = "{>>[%s]%s<<}" % (r.codigo, razao.replace("<<}", "« }"))
            novo = (novo[:ini] + "{~~%s~>%s~~}" % (texto[ini:fim], r.novo)
                    + nota + novo[fim:])
        esperado[n] = novo
        linhas[i] = linhas[i][:desloc] + novo

    # ---- o que nao virou troca vira comentario, com a proposta dentro
    por_linha, sem_ancora = {}, []
    for r, razao in recusas:
        t = "[%s] não aplicado: %s." % (r.codigo, razao)
        if r.novo:
            t += ' Proposta: "%s"' % r.novo
        elif not r.erro:
            t += " A proposta é retirar o trecho."
        if r.par in onde:
            por_linha.setdefault(onde[r.par], []).append(t)
        else:
            sem_ancora.append(r.codigo)

    if a.lista:
        feitos = {r.codigo for ns in plano.values() for *_, r in ns}
        feitos |= {r.codigo for r, _ in recusas}
        for cod, aponta, locs in itens(a.lista):
            if cod in feitos:
                continue
            alvo = next((n for n in locs if n in onde), None)
            if alvo is not None:
                extra = [x for x in locs if x != alvo]
                t = "[%s] %s" % (cod, aponta)
                if extra:
                    t += " Também em: " + " ".join("[P%d]" % x for x in extra)
                por_linha.setdefault(onde[alvo], []).append(t)

    for i, marcas in por_linha.items():
        limpas = [m.replace("<<}", "« }").replace("{>>", "{ »") for m in marcas]
        linhas[i] = linhas[i].rstrip() + "".join(" {>>%s<<}" % m for m in limpas)

    # ---- conferir antes de gravar: recusando tudo, volta ao original
    saida = "\n".join(linhas)
    volta = RE_COMENTARIO.sub("", RE_SUB.sub(lambda m: m.group(1), saida))
    volta = re.sub(r"[ \t]+$", "", volta, flags=re.M)
    if volta != re.sub(r"[ \t]+$", "", original, flags=re.M):
        print("A conferência reprovou: recusando todas as marcas, o arquivo não "
              "volta ao original. Nada foi gravado.")
        for n in sorted(esperado):
            if RE_SUB.sub(lambda m: m.group(1), esperado[n]) != corpo(
                    Path(a.trabalho).read_text(encoding="utf-8").splitlines()[onde[n]])[0]:
                print("  - o parágrafo [P%d] não volta" % n)
        return 1

    corte = 0
    for i, l in enumerate(linhas[:40]):
        if l.strip() == "---":
            corte = i + 1
            break
    linhas[corte:corte] = CABECALHO.strip().splitlines() + [""]

    dest = Path(a.saida) if a.saida else Path(a.trabalho).with_name(
        Path(a.trabalho).stem + "-CORRIGIDO.md")
    dest.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    trocas = sum(len(v) for v in plano.values())
    print("  %s: %d substituição(ões) em %d parágrafo(s), %d comentário(s)"
          % (dest.name, trocas, len(plano),
             sum(len(v) for v in por_linha.values())))
    print("  conferido: recusando tudo, o arquivo volta ao original.")
    print("  resolva as marcas com limpar_md.py --aceitar S1,S14 (ou --recusar-tudo).")
    if recusas:
        rec = dest.with_name(dest.stem + "-RECUSAS.md")
        L = ["# Reparos não aplicados — %s" % Path(a.trabalho).name, "",
             "Cada um destes está também como comentário no arquivo corrigido.",
             "Aqui ficam juntos, porque quem faz à mão precisa da lista.", ""]
        for r, razao in recusas:
            L += ["## %s (linha %s de %s)" % (r.codigo, r.linha, Path(a.arquivo).name), "",
                  "**Endereço:** %s" % ((("[P%d]" % r.par) +
                                         ("F%d" % r.frase if r.frase else ""))
                                        if r.par else "(não resolvido)"), "",
                  "**Por que não entrou:** %s" % razao, ""]
            if r.novo:
                L += ["**Proposta:** %s" % r.novo, ""]
        rec.write_text("\n".join(L) + "\n", encoding="utf-8")
        print("  %s: %d reparo(s) para fazer à mão" % (rec.name, len(recusas)))
    if sem_ancora:
        print("  sem âncora, e por isso só no arquivo de recusas: %s"
              % ", ".join(sem_ancora))
    return 0


if __name__ == "__main__":
    sys.exit(main())

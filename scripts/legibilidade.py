"""Torna o relatorio legivel por quem nao operou o instrumento.

POR QUE ISTO EXISTE

O relatorio sai escrito no vocabulario de quem o produziu: voz, leitura, cotejo,
localizador, acoplamento, sede, universo, degrau. Sao palavras uteis para operar
o analisador e opacas para o orientando e para o orientador, que recebem o
arquivo sem ter lido nada sobre como ele foi feito. O efeito pratico e que a
pessoa gasta energia decifrando o rotulo antes de chegar ao problema, e parte
dela desiste antes.

POR QUE ISTO E UM SCRIPT, E NAO UMA REESCRITA POR MODELO

Uma passada de modelo sobre o relatorio inteiro e uma passada de parafrase. Cada
item foi calibrado palavra a palavra ("a versao vigente", "nao verificado" em vez
de "nao existe"), e clareza pedida a um modelo suaviza exatamente essas
distincoes. Ninguem conferiria, porque o motivo de existir da camada e que o
leitor nao consegue conferir a versao cifrada.

**Entao a divisao e por risco.** O que este script faz e mecanico e reversivel:
troca de sigla, titulo de secao vindo de tabela fixa, e um punhado de formulas de
frase inteira. Nenhuma dessas operacoes muda o que um item afirma. O que exige
juizo, que e reescrever o titulo de cada item em palavras do proprio trabalho,
fica para um modelo, **que devolve uma tabela `S6<TAB>novo titulo` e nao o texto
reescrito**. O script aplica a tabela. O corpo do item nunca e tocado por modelo.

O relatorio original nao e sobrescrito: a saida vai para outro arquivo, e o diff
entre os dois e a prova de que so mudou o que se anunciou.

Uso:
    python legibilidade.py <relatorio.md> [--titulos t.tsv] [--saida R.md]
                           [--sigla S] [--sem-secoes] [--sem-formulas]
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- secoes
# O mapa e por TITULO, e nao por numero da secao.
#
# A primeira versao casava por numero, supondo que todos os relatorios tivessem a
# mesma estrutura. Nao tem: um traz seis secoes com 2.1 a 2.5, outro traz sete com
# a divisao entre 2 e 3. Aplicada a esse ultimo, a troca por numero renomeou
# "1.2 As virtudes" para "As contas conferem" e "3 Correções que exigem decisao"
# para "Onde o trabalho esta", **anunciando conteudo que nao estava ali, e sem
# erro nenhum**. Medido em 17/08/2026, na segunda execucao deste script.
#
# Casar por titulo nao tem esse modo de falha: titulo desconhecido fica como
# esta e e reportado ao fim, para decisao humana. A troca so ocorre onde alguem
# ja verificou que os dois nomes designam a mesma coisa.
SECOES = {
    "o merito": "O que o trabalho fez e merecia ter sido feito",
    "o que o trabalho faz": "O que o trabalho fez e merecia ter sido feito",
    "o que o trabalho faz que merecia ser feito":
        "O que o trabalho fez e merecia ter sido feito",
    "o ativo": "O que o trabalho construiu de próprio",
    "a aritmetica fecha": "As contas conferem",
    "o aparelho de contagem esta intacto": "As contas conferem",
    "as virtudes, com o localizador e a operacao que as confirmam":
        "As virtudes, e o parágrafo em que cada uma se confere",
    "o que os cotejos confirmaram estar correto, contra a suspeita das leituras":
        "O que foi posto em dúvida e resistiu à conferência",
    "o que os cotejos mostraram estar correto contra a suspeita das leituras":
        "O que foi posto em dúvida e resistiu à conferência",
    "os defeitos, por custo de reparo":
        "Sugestões de correção",
    "os defeitos, e o que custa sana-los":
        "Sugestões de correção",
    "reparos de alinhamento":
        "Correções simples: alinhar o texto ao que ele já diz noutro lugar",
    "reparos que exigem decisao, operacao nova ou redimensionamento":
        "Correções complexas: pedem decisão da autoria, operação nova ou mudança de alcance",
    "cortar": "Basta cortar",
    "reenunciar": "Basta corrigir a frase",
    "reenunciacoes que mudam o que a frase afirma":
        "Correções em que a frase passa a afirmar outra coisa",
    "reenquadrar": "Pede rever o que a frase afirma",
    "reenquadramento": "Pede rever o que a frase afirma",
    "refazer operacao localizada": "Pede refazer uma conta ou uma conferência",
    "operacao localizada a refazer": "Pede refazer uma conta ou uma conferência",
    "refazer desenho": "Pede uma análise que o trabalho ainda não fez",
    "redimensionamento: o que exige decisao da autora sobre o alcance de uma afirmacao":
        "Pede decisão da autora sobre o alcance de uma afirmação",
    "declaracao de limite: o que se resolve escrevendo o que ja se sabe":
        "Basta declarar um limite que o trabalho já conhece",
    "o degrau": "Avaliação geral",
    "onde o trabalho esta, e o que o levaria adiante": "Avaliação geral",
    "o trabalho se defende?": "Avaliação geral",
    "pontos em aberto": "O que o programa não conseguiu decidir, e a quem cabe",
    "pontos em aberto e repasses":
        "O que o programa não conseguiu decidir, e a quem cabe",
    "o que se declara": "O que este relatório não examinou",
    "como este relatorio foi feito, e o que ele nao alcancou":
        "O que este relatório não examinou",
    "reparos de copia": "Pequenas correções, que não pedem decisão nenhuma",
    "reparos que um script pode aplicar":
        "Pequenas correções, que não pedem decisão nenhuma",
    # Titulos ja vigentes: entram como identidade para nao aparecerem na lista
    # de "sem entrada no mapa", que deve conter so o que exige decisao humana.
    "pontos fortes": "Pontos fortes",
    "contribuicoes a reivindicar": "Contribuições a reivindicar",
    "avaliacao geral": "Avaliação geral",
    "sugestoes de correcao": "Sugestões de correção",
    "o que o programa nao conseguiu decidir, e a quem cabe":
        "O que o programa não conseguiu decidir, e a quem cabe",
    "o que este relatorio nao examinou": "O que este relatório não examinou",
    "pequenas correcoes, que nao pedem decisao nenhuma":
        "Pequenas correções, que não pedem decisão nenhuma",
    "basta cortar": "Basta cortar",
    "basta corrigir a frase": "Basta corrigir a frase",
    "pede rever o que a frase afirma": "Pede rever o que a frase afirma",
    "pede refazer uma conta ou uma conferencia": "Pede refazer uma conta ou uma conferência",
    "pede rever o desenho da pesquisa": "Pede uma análise que o trabalho ainda não fez",
    "pede uma analise que o trabalho ainda nao fez":
        "Pede uma análise que o trabalho ainda não fez",
    "discordancias, trocas e datas":
        "Pequenas correções, que não pedem decisão nenhuma",
}

# "universo" saiu do alerta em 18/08/2026: e termo estatistico corrente, que os
# proprios trabalhos usam ("o universo de 1.393 processos, com a semente
# declarada"), e alerta que dispara para uso legitimo treina a ignorar o alerta.
# Titulos ja claros, deixados de proposito: "Organizacao: o que a autora faz
# sozinha numa tarde", "Erros duros, conferiveis abrindo o arquivo", "Numeros que
# nao se refazem", "Discordancias, trocas e datas". Estao em palavras do trabalho,
# que e o criterio, e trocar so para uniformizar pioraria.

ACENTOS = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
                        "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC")


def normalizar(titulo):
    t = titulo.translate(ACENTOS).lower().strip()
    t = re.sub(r"\*+|`", "", t)
    return re.sub(r"\s+", " ", t).rstrip(".")

RE_SECAO = re.compile(r"^(#{1,4})\s+(\d+(?:\.\d+)*)(\.?)\s+(.*)$", re.M)

# A sigla so se detecta no rotulo de item, "**D12. ", e nunca no corpo. Detectar
# pela letra mais frequente do texto inteiro escolhe P, que e o localizador de
# paragrafo, e renomeia os 351 localizadores do relatorio para S123, destruindo
# a ligacao com o trabalho em silencio. Medido em 17/08/2026, na primeira
# execucao deste script.
RE_ROTULO = re.compile(r"^\*\*([A-Z]{1,3})\d+[a-z]?\.\s", re.M)
# Codigos legitimos de item, que nunca devem ser renomeados. Sem esta lista, a
# deteccao "letra mais frequente que nao seja S" escolhia F (seis pontos fortes)
# e convertia os pontos fortes do relatorio em sugestoes de correcao. O passo de
# sigla existe para migrar relatorios antigos, escritos com D de determinacao, e
# nao para mexer em relatorio ja no formato vigente.
PROTEGIDAS = {"P",            # localizador de paragrafo
              "F", "C", "S", "D", "Q"}   # codigos de item em uso

# ---------------------------------------------------------------- abertura
# A abertura antiga trazia um campo de nome a preencher, e o estado real do
# arquivo ao sair da esteira e que ninguem leu. Campo de nome no alto convida a
# preencher com quem nao leu, e a assinatura passa a valer como leitura que nao
# houve. Quem endossar escreve o endosso, como ato, sobre um texto que declara
# nao ter nenhum. Texto de LUIS.md, "A abertura do relatorio".
RE_ABERTURA = re.compile(
    r"^> Relatório do \*\*Luis\*\*, lido e endossado.*$", re.M)

ABERTURA = """> Relatório do **Luis**, gerado automaticamente. **Nenhum humano leu este texto antes de você.**
>
> Os achados foram levantados por leitura automática e depois conferidos contra o próprio trabalho, e o que não se sustentou foi retirado antes desta entrega. Ainda assim, **nada aqui vale antes de ser validado por quem tem competência para isso**, e a exigência é maior nas questões de qualidade: contagem, data divergente e frase que contradiz outra frase se conferem abrindo o arquivo no parágrafo indicado, mas juízo sobre método, argumento e literatura não se confere assim, e é de quem orienta e de quem examina.
>
> As soluções apontadas são **sugestões**. Quem determina é o orientador."""

# ---------------------------------------------------------------- formulas
# So entra aqui frase inteira cuja troca nao pode mudar o que o item afirma.
# Palavra solta ambigua fica de fora de proposito: "voz" vale tanto para as
# leituras automaticas quanto para "em voz do autor", que e uso legitimo e
# frequente nos relatorios, e trocar as duas junto inventaria um erro.
FORMULAS = [
    (re.compile(r"\bVisto por (uma|duas|três|tres|quatro|cinco|seis) leituras?\b"),
     r"Encontrado por \1 leituras automáticas independentes"),
    (re.compile(r"\bem (\w+) localizadores\b"), r"em \1 parágrafos"),
    (re.compile(r"\bnos? localizadores? indicados?\b"), "nos parágrafos indicados"),
    (re.compile(r"\bcotejad([oa]s?)\b"), r"conferid\1"),
    (re.compile(r"\bcotejar\b"), "conferir"),
    (re.compile(r"\bos cotejos\b"), "as conferências"),
    (re.compile(r"\bo cotejo\b"), "a conferência"),
    (re.compile(r"\bmaterial de triagem\b"),
     "material para o orientador triar, e não conclusão"),
]

# ---------------------------------------------------------------- siglas


# ---------------------------------------------------------------- anglicismos

# Decalque: nao e palavra estrangeira no texto, e palavra nossa com sentido que
# ela nao tem. Por isso a lista NAO corrige sozinha, e por isso cada entrada traz
# quando a palavra e legitima: as oito ocorrencias de `rotulo` num relatorio de
# 24/08/2026 pediram cinco substitutos diferentes, e tres palavras examinadas na
# varredura de 18/08 foram mantidas com razao.
# Cada entrada: (padrao, palavra como se escreve, o que fica em portugues,
# quando a palavra e legitima). A palavra vem escrita, e nao deduzida do regex:
# a primeira versao a deduzia e a tabela saia com "brootulosb".
CERTEIROS = [
    (r"\breparos?\b", "reparo", "correção, conserto",
     "significa a objeção: \"fez um reparo à tese\""),
    (r"\br[óo]tulos?\b", "rótulo",
     "designação, qualificação, expressão, nome, descrição",
     "é o que se cola num frasco"),
    # "isto custa uma frase" e decalque de *to cost*. O substantivo
    # ("ordenadas por custo") e legitimo, e por isso o padrao so pega o verbo.
    (r"\bcust(?:a|am|ou|aram|ar|aria)\b", "custar (no sentido de exigir)",
     "exigir, pedir, demandar, ou \"basta uma frase\"",
     "é despesa ou preço, e em \"custou a entender\""),
    (r"\bendere[çc]a\w*\b", "endereçar", "tratar, enfrentar, dirigir-se a",
     "é pôr endereço em correspondência"),
    (r"\bem termos de\b", "em termos de", "quanto a, no que toca a, em matéria de",
     "há termos de verdade: \"nos termos do art. 5º\""),
    (r"\btom(?:a|ou|ar)\s+lugar\b", "tomar lugar", "ocorrer, dar-se, realizar-se",
     "nunca, nesse sentido"),
    (r"\bperformances?\b", "performance", "desempenho", "é a arte performática"),
    (r"\bpr[ée]vio a\b", "prévio a", "antes de, anterior a",
     "\"consentimento prévio\" está correto"),
    (r"\bdelet\w+\b", "deletar", "apagar, excluir, suprimir", "em nada"),
    (r"\bcustomiz\w+\b", "customizar", "adaptar, personalizar, ajustar", "em nada"),
    (r"\bdram[áa]tic[oa]s?\b", "dramático", "acentuado, expressivo, forte",
     "é relativo ao drama"),
    (r"\bsuporta\w*\b", "suportar", "sustentar, apoiar, embasar", "é aguentar carga"),
    # o reflexivo "reporta-se a" e correto e sai do padrao; "reportagem" e
    # "reporter" ja saem pela fronteira de palavra depois da desinencia.
    (r"\breport(?:a|ou|ei|am|aram|ar|ado|ada)\b(?!-se)", "reportar",
     "registrar, relatar, dizer",
     "no reflexivo (\"reporta-se a Kelsen\") e na subordinação"),
]

RUIDOSOS = [
    (r"\bevid[êe]ncias?\b", "evidência", "prova, indício",
     "significa o que salta aos olhos: \"pôr em evidência\""),
    (r"\bconsistentes?\b", "consistente", "coerente, uniforme, constante",
     "significa denso: \"argumentação consistente\""),
    (r"\bassum\w+\b", "assumir", "supor, pressupor",
     "é tomar para si, e \"assumir que\" no sentido de admitir é correto"),
    (r"\brealiz(?:ou|ei|amos|aram)\b", "realizar", "perceber, dar-se conta",
     "é executar: \"realizou a pesquisa\""),
    (r"\bprov[êe]\b|\bprover\b", "prover", "fornecer, oferecer, dar",
     "no sentido jurídico: \"prover o recurso\""),
    (r"\bcr[íi]tic[oa]s?\b", "crítico", "decisivo, essencial, grave",
     "é relativo à crítica, e quase sempre é"),
    (r"\bsens[íi]ve(?:l|is)\b", "sensível", "delicado, controverso",
     "significa perceptível ou considerável"),
    (r"\bsubstantiv[oa]s?\b", "substantivo", "de mérito, de fundo, material",
     "é a classe gramatical"),
    (r"\bsum[áa]rios?\b", "sumário", "resumo, síntese",
     "é o índice, na norma da ABNT, e é o nome que o trabalho analisado pode "
     "dar a uma seção sua, caso em que o relatório só o está citando"),
    (r"\beventualmente\b", "eventualmente", "por fim, afinal, com o tempo",
     "significa ocasionalmente, que é o sentido português"),
]

DECALQUES = CERTEIROS + RUIDOSOS


def tabela_markdown():
    """Emite a lista em markdown, para as tabelas em prosa saírem daqui.

    A lista vivia em tres lugares (este arquivo, o instrumento e as regras
    globais) e divergiu no primeiro dia: `custar` entrou nas tabelas e nao no
    conferidor. Com isto, ha uma fonte so, e as copias se regeneram.
    """
    linhas = ["| Escreve-se | Em português | Legítimo quando |", "|---|---|---|"]
    for grupo, marca in ((CERTEIROS, ""), (RUIDOSOS, " *(alto ruído)*")):
        for _padrao, palavra, certo, quando in grupo:
            linhas.append("| %s%s | %s | %s |" % (palavra, marca, certo, quando))
    return "\n".join(linhas)


def conferir_anglicismos(texto, todos=False):
    """Relata ocorrencias com contexto. Nao troca nada, de proposito."""
    achados = []
    for numero, linha in enumerate(texto.splitlines(), 1):
        # citacao inserida e texto do autor analisado, e nao prosa do relatorio
        if linha.lstrip().startswith(">"):
            continue
        for padrao, _pal, certo, quando in (DECALQUES if todos else CERTEIROS):
            for m in re.finditer(padrao, linha, re.I):
                ini = max(0, m.start() - 45)
                fim = min(len(linha), m.end() + 45)
                achados.append((numero, m.group(0), certo, quando,
                                linha[ini:fim].strip()))
    return achados


def trocar_sigla(texto, de, para):
    """Renomeia D12 para S12 no titulo e em toda remissao.

    Casa o codigo isolado, e nao qualquer D seguido de digito: sem a fronteira,
    uma referencia legislativa ou um nome com D e numero seria capturado.
    """
    padrao = re.compile(rf"(?<![A-Za-z0-9]){de}(\d+[a-z]?)(?![A-Za-z0-9])")
    return padrao.subn(rf"{para}\1", texto)


def carregar_titulos(caminho):
    """Le a tabela `S6<TAB>novo titulo` produzida pela passada de modelo."""
    mapa = {}
    for n, linha in enumerate(Path(caminho).read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = re.split(r"\t|\s{2,}|\s*\|\s*", linha, maxsplit=1)
        if len(partes) != 2:
            print(f"  linha {n} da tabela de títulos não tem duas colunas, ignorada")
            continue
        codigo, titulo = partes[0].strip().strip("*"), partes[1].strip()
        mapa[codigo] = titulo.rstrip(".")
    return mapa


def aplicar_titulos(texto, mapa):
    """Troca so a frase de abertura em negrito, e nunca o corpo do item.

    O padrao exige que o negrito comece a linha e contenha o codigo seguido de
    ponto: e a forma do rotulo. Assim a troca nao alcanca um negrito qualquer no
    meio do paragrafo, onde a prova esta.
    """
    usados = set()

    def troca(m):
        codigo, ponto = m.group(1), m.group(2)
        if codigo not in mapa:
            return m.group(0)
        usados.add(codigo)
        return f"**{codigo}{ponto} {mapa[codigo]}.**"

    # Duas formas de codigo, porque os relatorios usam as duas: rotulo com letra
    # ("S12", "M3") e numeracao hierarquica ("2.1.1"), esta ultima sem ponto final
    # obrigatorio depois do codigo.
    texto = re.sub(r"^\*\*((?:[A-Z]{1,3}\d+[a-z]?|\d+(?:\.\d+){1,3}))(\.?)\s+(.+?)\.?\*\*",
                   troca, texto, flags=re.M)
    return texto, usados


def processar(caminho, titulos, saida, sigla, secoes, formulas, conferir=False):
    origem = Path(caminho)
    texto = origem.read_text(encoding="utf-8", errors="replace")
    conta = Counter()

    if sigla:
        letras = Counter(RE_ROTULO.findall(texto))
        for atual, _ in letras.most_common():
            if atual == sigla or atual in PROTEGIDAS:
                continue
            texto, n = trocar_sigla(texto, atual, sigla)
            conta[f"sigla {atual} para {sigla}"] = n
            break

    nao_mapeados = []
    if secoes:
        def titulo_secao(m):
            nivel, numero, ponto, antigo = m.groups()
            novo = SECOES.get(normalizar(antigo))
            if not novo:
                nao_mapeados.append(f"{numero} {antigo}")
                return m.group(0)
            if novo == antigo:
                return m.group(0)
            conta["títulos de seção"] += 1
            return f"{nivel} {numero}{ponto} {novo}"
        texto = RE_SECAO.sub(titulo_secao, texto)

    texto, n = RE_ABERTURA.subn(lambda _: ABERTURA, texto)
    conta["abertura substituída"] = n

    if formulas:
        for padrao, troca in FORMULAS:
            texto, n = padrao.subn(troca, texto)
            conta["formulas de frase"] += n

    faltando = []
    if titulos:
        mapa = carregar_titulos(titulos)
        texto, usados = aplicar_titulos(texto, mapa)
        conta["títulos de item"] = len(usados)
        faltando = sorted(set(mapa) - usados)

    destino = Path(saida) if saida else origem.with_name(origem.stem + "-LEGIVEL.md")
    if not conferir:
        destino.write_text(texto, encoding="utf-8")

    for chave, n in conta.items():
        if n:
            print(f"  {n} {chave}")
    if faltando:
        print(f"  {len(faltando)} códigos da tabela não existem no relatório: "
              + ", ".join(faltando[:10]))
        print("  Isso é achado sobre a tabela, não falha do script.")
    if nao_mapeados:
        print(f"  {len(nao_mapeados)} títulos de seção sem entrada no mapa, "
              "deixados como estão:")
        for t in nao_mapeados:
            print(f"    {t}")
    restos = sorted({p.lower() for p in re.findall(
        r"\b(?:sede|acoplament\w+|fóssil|fissuras?|degrau|repasses?|"
        r"reenunciaç\w+|reenquadrament\w+|localizador\w*)\b", texto, re.I)})
    if restos:
        print("  ainda no texto, e fora do alcance de troca mecânica: "
              + ", ".join(restos))
    print(f"  Saída em {destino}" if not conferir else "  (conferência: nada gravado)")
    return destino


def main():
    ap = argparse.ArgumentParser(
        description="Troca sigla, títulos de seção e fórmulas fixas do relatório.")
    ap.add_argument("relatorio")
    ap.add_argument("--titulos", help="tabela `S6<TAB>novo título` da passada de modelo")
    ap.add_argument("--saida")
    ap.add_argument("--sigla", default="S", help="letra dos itens (padrão S)")
    ap.add_argument("--sem-secoes", action="store_true")
    ap.add_argument("--conferir", action="store_true",
                    help="não grava nada; só relata o que mudaria")
    ap.add_argument("--sem-formulas", action="store_true")
    ap.add_argument("--anglicismos", action="store_true",
                    help="lista decalques do inglês com contexto; não corrige nada, "
                         "porque a palavra certa varia com a coisa")
    ap.add_argument("--tabela", action="store_true",
                    help="emite a lista em markdown, para colar nas regras")
    ap.add_argument("--todos", action="store_true",
                    help="com --anglicismos, inclui também os de alto ruído "
                         "(sumário, crítico, evidência), que costumam ser legítimos")
    a = ap.parse_args()

    if a.tabela:
        print(tabela_markdown())
        return 0

    if a.anglicismos:
        texto = Path(a.relatorio).read_text(encoding="utf-8", errors="replace")
        achados = conferir_anglicismos(texto, a.todos)
        if not achados:
            print("  nenhum decalque da lista")
            return 0
        nivel = "lista inteira" if a.todos else "só os de baixo ruído; --todos inclui o resto"
        print(f"  {len(achados)} ocorrência(s) ({nivel}). Nada foi alterado.\n")
        for numero, palavra, certo, quando, ctx in achados:
            print(f"  linha {numero}: {palavra}")
            print(f"    em português: {certo}")
            print(f"    {quando}")
            print(f"    ...{ctx}...\n")
        return 0
    processar(a.relatorio, a.titulos, a.saida, a.sigla,
              not a.sem_secoes, not a.sem_formulas, a.conferir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

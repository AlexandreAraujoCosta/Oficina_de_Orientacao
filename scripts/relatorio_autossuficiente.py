"""Insere no relatorio o texto dos paragrafos que ele cita.

POR QUE ISTO EXISTE

O relatorio cita [P123] e nao transcreve, porque transcricao digitada por modelo
sai com uma palavra trocada e ninguem percebe. Isso resolve a fidelidade e cria
outro problema: **o relatorio so e legivel com o trabalho aberto ao lado.** Para
a maquina isso e indiferente; para quem le, e um vaivem constante que faz o
leitor desistir de conferir e passar a acreditar.

Este script fecha a segunda metade da regra do localizador. O modelo forneceu o
numero; aqui o codigo busca o texto na extracao canonica e o insere como citacao.
**Quem transcreve e o programa, entao nao existe artigo trocado**, e o relatorio
passa a ser legivel sozinho.

O que ele NAO faz: nao reescreve o relatorio, nao resume o paragrafo, nao decide
o que e relevante. Insere o paragrafo inteiro, como esta na extracao, e diz de
onde veio.

COMO EVITA INCHAR

Um paragrafo citado quinze vezes no mesmo item entraria quinze vezes. Por isso a
insercao e uma vez por item: da segunda em diante, o localizador fica so como
remissao. Paragrafo muito longo entra ate um limite e o corte e declarado no
proprio bloco, nunca em silencio.

Uso:
    python relatorio_autossuficiente.py <relatorio.md> <trabalho.pdf|.docx>
                                        [--saida R.md] [--limite N] [--todas]
"""

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from conferir_consistencia import carregar  # noqa: E402

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



# [P123] ou P123, faixa com hifen simples ou longo. Colchete opcional porque uma
# das agregacoes ja entregues escreveu sem ele 499 vezes.
RE_REF = re.compile(r"(?<![A-Za-z0-9])\[?P(\d+)(?:\s*[-–]\s*P?(\d+))?\]?")

# Titulo de item: "## D12.", "### H3 —", "### 3.1.1 ".
RE_ITEM = re.compile(r"^#{1,4}\s+((?:[A-Z]{1,3})?\d+(?:\.\d+)*[a-z]?)[\.\)\s—–-]")

# Secoes em que o trecho NAO se insere, so o localizador. Ninguem confere elogio,
# e enfiar o paragrafo inteiro sob cada ponto forte onera a leitura da unica
# secao que o autor le por gosto, pagando por uma verificacao que nao acontece.
RE_TITULO = re.compile(r"^#{1,4}\s+.*$")
SEM_TRECHO = ("pontos fortes",)

# O rotulo em negrito do item, "**S14. ...**". A dedupe usa a secao, e nao ele,
# de proposito: paragrafo citado por dois itens da mesma secao entra uma vez so.
# O rotulo serve ao teto por item, que e outra coisa.
RE_ROTULO_ITEM = re.compile(r"^\*\*([A-Z]{1,3}\d+[a-z]?)\.?\s")

LIMITE_FAIXA = 40      # faixa maior que isso e remissao de bloco, nao citacao
LIMITE_CARACTERES = 1400


def cortar(texto, limite):
    if len(texto) <= limite:
        return texto, False
    corte = texto.rfind(" ", 0, limite)
    return texto[: corte if corte > 0 else limite], True


def bloco(indice, ini, fim, limite):
    """Devolve as linhas de citacao, ou None se nada existir na fonte."""
    numeros = [n for n in range(ini, fim + 1) if n in indice]
    if not numeros:
        return None
    linhas = []
    for n in numeros:
        texto = indice[n].strip()
        if not texto:
            linhas.append(f"> **P{n}** *(parágrafo vazio na extração)*")
            linhas.append(">")
            continue
        texto, cortado = cortar(texto, limite)
        marca = " *[trecho cortado por extensão]*" if cortado else ""
        linhas.append(f"> **P{n}** {texto}{marca}")
        linhas.append(">")
    while linhas and linhas[-1] == ">":
        linhas.pop()
    return linhas


ROTULOS = {
    "F": "**F** é ponto forte: o que o trabalho faz bem, escolhido entre muitos.",
    "S": "**S** é sugestão de correção. Diz o que mudar, onde, e sob que condição "
         "a dificuldade está resolvida.",
    "D": "**D** é sugestão de desenvolvimento: o ponto não está errado, está fino "
         "para o peso que o trabalho lhe dá.",
    "C": "**C** é contribuição a reivindicar: coisa que o trabalho fez e não disse "
         "que fez. Não há o que corrigir; há o que passar a escrever.",
    "Q": "**Q** é questão: ponto que o programa não conseguiu decidir, com a "
         "indicação de quem decide e do que encerra a questão.",
}


def nota_de_tamanho(palavras_texto, palavras_citadas):
    """O paragrafo que desfaz a impressao de que o documento e longo.

    Nao abre com "espessura": e decalque de thickness, e nao se diz de
    documento em portugues. Comeca pelo numero, que e o que desinfla.

    Existe porque o relatorio chega com o dobro ou o triplo das paginas do texto
    que ele de fato pede para ler, e quem abre um arquivo de cinquenta paginas
    decide, antes de ler a primeira linha, que nao vai conseguir. O numero
    honesto e o do texto proprio: as citacoes se consultam, e estao ali para que
    ninguem precise abrir o trabalho ao lado.
    """
    # Sem negrito: desde 31/08/2026 esta nota fecha a ementa, e a ementa sai
    # numa fonte so. Os destaques vinham de quando ela vivia isolada.
    minutos = max(1, round(palavras_texto / 200))
    # Um numero so. Faixa que termina alto ("57 a 80 minutos") desinfla ao
    # contrario: o leitor guarda o teto. Se o numero unico envergonha, o
    # remedio e encurtar o relatorio, e nao alargar a estimativa.
    faixa = "cerca de %d minutos" % minutos
    proporcao = palavras_citadas / max(1, palavras_texto + palavras_citadas)
    return [
        "O texto deste relatório tem cerca de %s palavras, o que dá %s de "
        "leitura. Todo o resto, que é "
        "%d%% do documento, são trechos do próprio trabalho, copiados e inseridos "
        "logo abaixo de cada apontamento. Eles não se leem de ponta a ponta: estão "
        "ali para que não seja preciso abrir o trabalho ao lado para entender o "
        "que se aponta, e para que cada sugestão possa ser pensada dentro deste "
        "documento mesmo, com a frase original à vista. As sugestões complementares "
        "estão no anexo, ao fim deste documento, e não entram nesse tempo: destinam-se ao "
        "corretor automático, e não a esta leitura."
        % ("{:,}".format(palavras_texto).replace(",", "."), faixa, round(proporcao * 100)),
    ]


def guia(indice, rotulos, fonte, contagem, com_trecho):
    """A explicacao de como ler, para quem nunca viu um relatorio destes.

    Reescrita em 18/08/2026 a partir de uma leitura fria, feita por quem recebeu
    so o arquivo. Ela achou, entre outras coisas, que a versao anterior:

    - dizia "Luis" sem nunca explicar o que e, na primeira linha;
    - dava a contagem de paragrafos rotulados como se fosse o maior numero, e o
      leitor que visse [P680] num arquivo de "397 paragrafos" concluia que a
      primeira informacao numerica do documento estava errada;
    - ilustrava o formato com um localizador que nao aparecia em item nenhum;
    - prometia o trecho embaixo de cada item, promessa que deixou de valer na
      secao de pontos fortes, onde os trechos nao entram mais;
    - usava "arquivo" ora para a extracao, ora para o Word do autor, dentro de um
      relatorio cujo assunto e o mesmo nome designando duas coisas.
    """
    numeros = sorted(indice)
    faixa = f"[P{numeros[0]}] a [P{numeros[-1]}]" if numeros else "(vazio)"
    exemplo = f"[P{numeros[len(numeros) // 3]}]" if numeros else "[P1]"
    linhas = [
        "## Como esta leitura foi feita, e como conferi-la",
        "",
        "**Quem escreveu isto.** Sou o Luis, um leitor automático. Leio o trabalho "
        "inteiro e comparo cada afirmação com as demais, procurando onde uma "
        "contradiz a outra ou onde o texto afirma mais do que mediu. Não li as obras "
        "citadas nem conheço o campo como quem o pratica, e por isso o julgamento "
        "sobre o mérito continua sendo de quem orienta e de quem examina. O que eu "
        "faço bem é conferir, e é sob essa medida que este relatório deve ser lido: "
        "onde ele elogia, elogia coisa conferida.",
        "",
        f"**Versão lida:** `{fonte}`. Se você tem mais de uma versão no computador, "
        "é esta a que foi analisada, e apontamento sobre versão diferente não vale.",
        "",
        f"**O que é `{exemplo}`.** É o endereço de um parágrafo no texto que o "
        f"programa leu. A numeração vai de {faixa} e tem intervalos vazios, porque "
        "linhas em branco e quebras de página consomem números sem virar parágrafo. "
        f"São {len(indice)} parágrafos numerados ao todo. **Esse número não existe "
        "no seu Word:** foi criado na leitura, só para que cada apontamento tivesse "
        "um endereço.",
        "",
    ]
    if com_trecho:
        linhas += [
            "**Na maior parte dos itens você não precisa procurar o parágrafo.** O "
            "bloco recuado logo abaixo é o parágrafo inteiro, copiado do seu texto "
            "por programa, e não digitado: nenhuma palavra foi trocada no caminho. "
            "A seção de pontos fortes é a exceção, e ali vai só o número, porque "
            "elogio ninguém confere. Para achar o trecho no seu Word, use a busca "
            "(Ctrl+F) com um pedaço da frase.",
            "",
        ]
    if contagem:
        ordem = ", ".join(f"{n} {c}" for c, n in contagem.items())
        linhas += [
            f"**Quantos são, e em que ordem.** {ordem}. As sugestões de correção "
            "vêm das mais simples às mais complexas, e a avaliação geral, logo "
            "antes delas, diz por quais começar. A última seção reúne os erros "
            "pequenos, que se resolvem numa passada só.",
            "",
        ]
    linhas += [
        "**Duas palavras que se repetem.** *Versão vigente* é a forma que o trabalho "
        "usa na maioria dos lugares, e que serve de modelo para copiar onde ele "
        "divergiu de si mesmo. *Texto lido* é a extração que o programa analisou; "
        "*seu Word* é o arquivo original, e os dois podem divergir.",
        "",
        "**Se o trecho citado não bater com o seu Word**, isso é achado sobre a "
        "leitura e vale avisar. Não invalida o resto, e nem sempre é erro: uma "
        "versão posterior sua pode divergir da que foi lida.",
        "",
        "**Discordar é uso normal.** Cada item traz onde conferir justamente para "
        "que você possa recusá-lo com o texto na mão. O relatório é automático, e "
        "a decisão sobre o que fazer com cada ponto é sua e de quem orienta.",
        "",
    ]
    presentes = [r for r in ("F", "C", "S", "D", "Q") if r in rotulos]
    if presentes:
        linhas += ["**Os códigos dos itens.**", ""]
        linhas += [f"- {ROTULOS[r]}" for r in presentes if r in ROTULOS]
        linhas.append("")
    linhas += ["---", ""]
    return linhas


def processar(relatorio, trabalho, saida, limite, todas, max_por_item=None,
              so_secoes=None):
    """so_secoes restringe a insercao as secoes cujo titulo contenha um dos termos.

    A versao do aluno nao recebe trechos, porque ela anda com o `.docx` comentado e
    o paragrafo esta na margem, no ponto exato. **Os questionamentos sao a excecao,
    e a razao e que ali nao ha margem que os resolva**: questionamento nao vira
    comentario no Word, entao a autora teria de abrir o arquivo de paragrafos para
    cada um. Pedido do usuario em 03/09/2026.
    """
    indice = dict(carregar(trabalho))
    corpo = Path(relatorio).read_text(encoding="utf-8", errors="replace")

    saida_linhas = []
    item = "(abertura)"
    vistos = set()          # (item, numero) ja inseridos
    inseridos, ausentes, remissoes = 0, [], 0
    rotulo, por_item, cortados = None, 0, 0
    sem_trecho = bool(so_secoes)   # com so_secoes, so a secao nomeada insere
    # Numero citado sozinho e que nao existe e defeito do relatorio. Numero que
    # so aparece por expansao de faixa e nao existe e buraco da numeracao: o
    # extrator nao rotula paragrafo vazio, entao a serie tem lacunas legitimas.
    # Acusar as duas coisas junto faz o script culpar o relatorio por [P496-P502]
    # conter um numero vago, e acusacao errada da ferramenta custa mais do que o
    # silencio. Medido em 18/08/2026.
    lacunas = []
    dentro_de_codigo = False

    # O TRECHO ENTRA NO FIM DO PARAGRAFO, E NAO NO FIM DA LINHA.
    #
    # Ate 03/09/2026 o bloco era emitido logo depois da linha que trazia o
    # localizador. O relatorio e quebrado em 80 colunas, entao "a linha" quase
    # nunca e a frase: numa entrega de dissertacao, um item de lista foi cortado
    # em "O teste que separa as duas categorias e se o espaco" e o resto da frase
    # so voltava depois de um bloco de citacao de doze linhas. E o mesmo defeito
    # que apareceu a noite toda noutros lugares: tratar linha fisica como unidade
    # de sentido. Aqui os blocos se acumulam e saem juntos na linha em branco.
    trechos_pendentes = []

    for linha in corpo.splitlines():
        if linha.lstrip().startswith("```"):
            dentro_de_codigo = not dentro_de_codigo
        if trechos_pendentes and not linha.strip():
            saida_linhas.append("")
            saida_linhas.extend(trechos_pendentes)
            trechos_pendentes = []
        saida_linhas.append(linha)

        if dentro_de_codigo:
            continue
        if RE_TITULO.match(linha):
            if so_secoes:
                # SO O TITULO DE SECAO REAVALIA, E NAO O DE ITEM.
                #
                # Um relatorio escreve os itens da secao como `### Q3. ...` e
                # outro como `**Q3. ...**`. Reavaliando em qualquer nivel, o
                # primeiro saia da secao no item seguinte ao titulo dela, e a
                # entrega de uma tese ficou com zero trechos onde a de uma
                # dissertacao teve dezoito. Medido em 03/09/2026.
                nivel = len(linha) - len(linha.lstrip("#"))
                if nivel <= 2:
                    sem_trecho = not any(k in linha.lower() for k in so_secoes)
            else:
                sem_trecho = any(k in linha.lower() for k in SEM_TRECHO)
        m = RE_ITEM.match(linha)
        if m:
            item = m.group(1)
        mr = RE_ROTULO_ITEM.match(linha)
        if mr and mr.group(1) != rotulo:
            rotulo, por_item = mr.group(1), 0
        if sem_trecho or linha.lstrip().startswith(">"):
            continue        # ja e citacao, inserida antes ou escrita a mao

        # Localizador entre crases e exemplo de formato, e nao citacao: a linha
        # "os paragrafos sao citados na forma `[P123]`" fazia o script inserir o
        # paragrafo 123 de verdade, no alto do relatorio, sem nada a ver com ele.
        refs = RE_REF.findall(re.sub(r"`[^`]*`", "", linha))
        if not refs:
            continue

        pendentes = []
        for ini, fim in refs:
            ini = int(ini)
            fim = int(fim) if fim else ini
            if fim < ini:
                ini, fim = fim, ini
            if fim - ini > LIMITE_FAIXA:
                continue
            for n in range(ini, fim + 1):
                chave = (item, n)
                if chave in vistos and not todas:
                    remissoes += 1
                    continue
                vistos.add(chave)
                if max_por_item and rotulo and por_item >= max_por_item:
                    cortados += 1
                    continue
                if n not in indice:
                    destino = ausentes if fim == ini else lacunas
                    if n not in destino:
                        destino.append(n)
                    continue
                pendentes.append(n)
                por_item += 1

        if not pendentes:
            continue

        anterior = None
        # A linha ">" entre dois blocos e o que os torna paragrafos distintos:
        # linhas de citacao consecutivas, sem ela, o markdown junta num
        # paragrafo so por continuacao preguicosa, e trinta e oito paragrafos
        # citados saem como um muro de texto. `bloco` retira o separador final,
        # o que esta certo para ele sozinho e errado para quem o chama em serie,
        # entao a recomposicao e aqui. Defeito entregue em 24/08/2026.
        #
        # Os blocos vao para a fila, e nao para a saida: quem os solta e a linha
        # em branco que fecha o paragrafo. `primeiro` olha a fila, e nao um
        # contador local, porque duas linhas do mesmo paragrafo podem trazer
        # localizadores e os blocos das duas saem juntos.
        primeiro = not trechos_pendentes
        for n in sorted(dict.fromkeys(pendentes)):
            b = bloco(indice, n, n, limite)
            if not b:
                anterior = n
                continue
            if not primeiro:
                trechos_pendentes.append(">")
            if anterior is not None and n != anterior + 1:
                trechos_pendentes.append("> *[...]*")
                trechos_pendentes.append(">")
            trechos_pendentes.extend(b)
            inseridos += 1
            primeiro = False
            anterior = n

    # O ultimo paragrafo do arquivo pode nao terminar em linha em branco, e o
    # bloco dele ficaria na fila sem sair.
    if trechos_pendentes:
        saida_linhas.append("")
        saida_linhas.extend(trechos_pendentes)
        saida_linhas.append("")

    # A guia entra DEPOIS da ementa, e nao antes. O leitor abre o arquivo para
    # saber em que estado esta o trabalho, e nao para aprender a usar o relatorio:
    # instrucao de uso antes do veredicto gasta a atencao mais cara do documento.
    # Depois do primeiro item ja e tarde, porque ali ele ja tropecou no primeiro
    # localizador sem saber o que e.
    rotulos = {m.group(1) for m in re.finditer(r"^\*\*([FCSDQ])\d+[a-z]?\.", corpo, re.M)}
    # Quantos itens de cada tipo, para a guia poder dizer o tamanho do que vem.
    from collections import Counter
    conta_itens = Counter(m.group(1) for m in
                          re.finditer(r"^\*\*([FCSDQ])\d+[a-z]?\.", corpo, re.M))
    NOMES = {"F": "pontos fortes", "S": "sugestões de correção",
             "D": "sugestões de desenvolvimento", "C": "contribuições a reivindicar",
             "Q": "questões"}
    contagem = {NOMES[k]: v for k, v in conta_itens.items() if k in NOMES}
    # A nota fecha a ementa, e o ponto de insercao e o fim dela.
    #
    # A regra anterior procurava o primeiro "---" depois da ementa e inseria logo
    # abaixo. Relatorio que nao usa separador ali caia no ramo de recuo, que
    # devolvia o fim do arquivo, e a nota de tempo de leitura saia na ultima
    # pagina, depois de tudo o que ela deveria ter enquadrado. Foi o que se
    # entregou em 31/08/2026.
    #
    # A regra nova nao depende de separador: acha a proxima secao depois da
    # ementa e insere imediatamente antes dela. Sem ementa, insere antes da
    # primeira secao do documento.
    def e_fronteira(l):
        s = l.strip()
        return s == "---" or (s.startswith("#") and not s.startswith("#####"))

    ementa = next((i for i, l in enumerate(saida_linhas)
                   if l.lstrip("# ").strip().lower().startswith("ementa")), None)
    if ementa is None:
        corte = next((i for i, l in enumerate(saida_linhas)
                      if i and e_fronteira(l)), len(saida_linhas))
    else:
        corte = next((i for i, l in enumerate(saida_linhas)
                      if i > ementa and e_fronteira(l)), len(saida_linhas))
    # `corte` e a linha da proxima secao; a nota entra antes dela.
    corte -= 1
    # Numa entrega unica o anexo vem depois do relatorio no mesmo arquivo, e
    # conta-lo aqui faria a nota prometer o dobro do tempo de leitura. O relogio
    # vale para o corpo, que se le de ponta a ponta; o anexo se consulta.
    # A lista de correcoes que um programa aplica nao se le: e insumo de
    # maquina, como o anexo, e contar o bloco cercado inflaria o relogio.
    def so_prosa(s):
        return re.sub(r"```.*?```", "", s, flags=re.S)
    MARCA_ANEXO = chr(10) + "# Anexo"
    ct = corpo.find(MARCA_ANEXO)
    palavras_texto = len(so_prosa(corpo[:ct] if ct > 0 else corpo).split())
    montado = chr(10).join(saida_linhas)
    cm = montado.find(MARCA_ANEXO)
    palavras_total = len(so_prosa(montado[:cm] if cm > 0 else montado).split())
    nota = nota_de_tamanho(palavras_texto, max(0, palavras_total - palavras_texto))

    # Se o relatorio ja traz a sua propria secao de leitura, escrita a mao, o
    # script nao acrescenta outra: duas secoes com o mesmo titulo, uma logo
    # depois da outra, foi defeito entregue em 24/08/2026.
    ja_tem = any(l.strip().lower().startswith("## como ler") for l in saida_linhas)
    if not ja_tem:
        # O guia desce para o fim, e ate 01/09/2026 abria o documento. Uma
        # leitura fria feita por quem recebe trabalho desses devolveu que a
        # primeira pagina era toda aparato e ressalva: quem escreveu o capitulo
        # lia como o instrumento funciona, o que nao foi conferido e que a
        # decisao continua sendo de outro, antes de chegar a uma linha sobre o
        # proprio trabalho. Ressalva na abertura assusta e e pulada, de modo
        # que nem cumpre a funcao de honestidade que a justificava. Ela se
        # cumpre por existir e ser achada, e nao por vir primeiro.
        saida_linhas += ["", "---", ""] + guia(
            indice, rotulos, Path(trabalho).name, contagem, inseridos > 0) + nota + [""]
    else:
        saida_linhas[corte + 1:corte + 1] = [""] + nota + [""]

    cabecalho = (
        "<!-- Parágrafos inseridos por scripts/relatorio_autossuficiente.py a partir\n"
        f"     de {Path(trabalho).name}. O modelo forneceu apenas os localizadores;\n"
        "     o texto citado foi copiado da extração por código. -->\n\n"
    )
    destino = Path(saida) if saida else Path(relatorio).with_name(
        Path(relatorio).stem + "-COM-TRECHOS.md")
    destino.write_text(cabecalho + "\n".join(saida_linhas) + "\n", encoding="utf-8")

    print(f"  {inseridos} parágrafos inseridos"
          + (f", {remissoes} remissões repetidas não reinseridas" if remissoes else "")
          + (f", {cortados} além do teto de {max_por_item} por item" if cortados else ""))
    if ausentes:
        print(f"  {len(ausentes)} localizadores citados sozinhos não existem na fonte: "
              + ", ".join(f"P{n}" for n in ausentes[:12])
              + (" ..." if len(ausentes) > 12 else ""))
        print("  Isso é achado sobre o relatório: aponta parágrafo que ninguém abriu.")
    if lacunas:
        print(f"  {len(lacunas)} números sem parágrafo dentro de faixas citadas "
              f"({', '.join(f'P{n}' for n in lacunas[:8])}"
              + (" ..." if len(lacunas) > 8 else "") + ")")
        print("  Normal: o extrator não rotula parágrafo vazio, e a série tem lacunas.")
    print(f"  Saída em {destino}")
    return destino


def main():
    ap = argparse.ArgumentParser(
        description="Insere no relatório o texto dos parágrafos que ele cita.")
    ap.add_argument("relatorio")
    ap.add_argument("trabalho", help=".docx ou .pdf")
    ap.add_argument("--saida")
    ap.add_argument("--limite", type=int, default=LIMITE_CARACTERES,
                    help=f"caracteres por parágrafo (padrão {LIMITE_CARACTERES})")
    ap.add_argument("--todas", action="store_true",
                    help="insere em toda citação, mesmo repetida dentro do item")
    ap.add_argument("--max-por-item", type=int, default=None,
                    help="teto de parágrafos inseridos por item; o excedente "
                         "fica só como localizador, e se confere no caderno")
    ap.add_argument("--so-secoes", nargs="+", metavar="TERMO",
                    help="insere so nas secoes cujo titulo contenha um destes "
                         "termos. A entrega do aluno usa --so-secoes questionamento, "
                         "porque questionamento nao vira comentario no Word e ali "
                         "o localizador nao se resolve na margem")
    a = ap.parse_args()
    processar(a.relatorio, a.trabalho, a.saida, a.limite, a.todas, a.max_por_item,
              so_secoes=[s.lower() for s in a.so_secoes] if a.so_secoes else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())

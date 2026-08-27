# -*- coding: utf-8 -*-
"""Nucleo comum dos dois aplicadores: onde o texto pode ser trocado, e o que trocar.

POR QUE ISTO EXISTE SEPARADO

`aplicar_docx.py` e `aplicar_md.py` fazem a mesma decisao e gravam em formatos
diferentes. A decisao e uma so: qual frase o reparo enderecou, se ela cabe num
trecho de formatacao continua, e qual texto entra no lugar. Duplicar isso em
dois arquivos seria duplicar o lugar onde o erro mora.

AS TRES PECAS

1. `frases()` corta o paragrafo em frases e as numera. A numeracao precisa ser
   a mesma que o modelo leu quando escreveu o reparo, e por isso quem a publica
   e quem a consome sao o mesmo codigo.

2. `fluxo()` percorre o XML cru do paragrafo e devolve o texto visivel com o
   mapa de onde cada caractere mora, dizendo onde a formatacao muda e onde ha
   barreira (nota de rodape, campo, tabulacao, imagem). Medido em 27/08/2026:
   80% e 72% dos paragrafos citados tem uma formatacao so, e 93% e 84% das
   frases cabem inteiras dentro de uma. O que atravessa e recusado, e nao
   remendado: recompor a divisao de runs para preservar o italico e onde este
   tipo de programa quebra.

3. `ler_reparos()` le o arquivo de reparos. O `Esta:` so aceita o marcador
   `{{P464F2}}`; texto digitado ali e recusado com a razao escrita. A regra da
   transcricao deixa de ser conselho e passa a ser condicao de execucao.
"""
import re

# ------------------------------------------------------------------- frases

# Abreviaturas que terminam em ponto sem terminar frase. A lista e de prosa
# academica e juridica brasileira, que e o corpus destes trabalhos.
ABREVIATURAS = {
    "art", "arts", "inc", "incs", "al", "cap", "caps", "sec",
    "p", "pp", "pag", "pags", "fl", "fls", "n", "no", "num", "vol", "v",
    "ed", "eds", "org", "orgs", "coord", "coords", "trad", "rev", "atual",
    "cf", "cit", "ibid", "id", "op", "apud", "et", "etc", "ex", "obs",
    "sec", "a.c", "d.c", "dr", "dra", "drs", "prof", "profa", "profs",
    "sr", "sra", "srs", "sras", "jr", "ltda", "s.a", "cia",
    "min", "rel", "des", "ac", "proc", "rec", "sum", "tb", "esp",
    "jan", "fev", "mar", "abr", "jun", "jul", "ago", "set", "out", "nov", "dez",
    "éd", "séc", "súm", "seç", "nº",
}
_FIM = "….?!"
_FECHA = "\"'”’»)]}"
_ABRE = "\"'“‘«([{—–"

_RE_CORTE = re.compile(r"[%s]+[%s]*\s+" % (re.escape(_FIM), re.escape(_FECHA)))


def _abreviatura(texto, pos_do_ponto):
    """A palavra imediatamente antes do ponto e uma abreviatura conhecida?"""
    i = j = pos_do_ponto
    while j > 0 and (texto[j - 1].isalnum() or texto[j - 1] in ".ºª"):
        j -= 1
    tok = texto[j:i].lower().strip(".")
    if not tok:
        return False
    if len(tok) == 1 and tok.isalpha():        # inicial de nome proprio
        return True
    return tok in ABREVIATURAS


def frases(texto):
    """Corta em frases e devolve [(inicio, fim)] em indices de caractere.

    O corte e conservador: na duvida, nao corta. Frase a mais e um localizador
    que o modelo nao vai usar; frase a menos e um localizador que aponta para o
    lugar errado."""
    t = texto
    if not t.strip():
        return []
    cortes, i = [], 0
    for m in _RE_CORTE.finditer(t):
        ponto, depois = m.start(), m.end()
        if depois >= len(t):
            break
        prox = t[depois]
        if not (prox.isupper() or prox.isdigit() or prox in _ABRE):
            continue
        if _abreviatura(t, ponto):
            continue
        cortes.append((i, depois))
        i = depois
    if i < len(t):
        cortes.append((i, len(t)))
    # Residuo de corte errado sai juntando com a frase anterior: juntar e sempre
    # mais seguro que separar, porque quem separa demais desloca a numeracao.
    saida = []
    for ini, fim in cortes:
        if saida and len(t[ini:fim].strip()) < 3:
            saida[-1] = (saida[-1][0], fim)
        else:
            saida.append((ini, fim))
    return saida


# --------------------------------------------------------------- XML do .docx

RE_RUN = re.compile(rb"<w:r(?:\s[^>]*)?/>|<w:r(?:\s[^>]*)?>.*?</w:r>", re.S)
RE_RPR = re.compile(rb"<w:rPr(?:\s[^>]*)?/>|<w:rPr(?:\s[^>]*)?>.*?</w:rPr>", re.S)
RE_T = re.compile(rb"<w:t(?:\s[^>]*)?/>|<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
RE_TAG = re.compile(rb"<(/?)(\w+:[\w\-.]+)")

# Diferencas que o Word cria sozinho e que se fundem sem perda de formatacao:
# estado do corretor ortografico e marca de idioma. Junto vao as propriedades de
# escrita complexa e do Leste Asiatico (`szCs`, `bCs`, `iCs`, `eastAsia`), que
# governam a renderizacao de alfabetos que estes trabalhos nao usam: fundi-las
# nao junta italico com redondo, que e o que precisa continuar separado. Medido
# em 27/08/2026, o ganho e de 6 pontos nos paragrafos do capitulo medido.
# Tudo o mais em <w:rPr> e formatacao de verdade.
RE_RUIDO = re.compile(
    rb"<w:(?:noProof|szCs|bCs|iCs)(?:\s[^>]*)?/>"
    rb"|<w:lang(?:\s[^>]*)?/>|<w:lang(?:\s[^>]*)?>.*?</w:lang>"
    rb'| w:eastAsia="[^"]*"', re.S)

# Dentro de um run, so estes convivem com a troca. `lastRenderedPageBreak` e
# marca transitoria que o Word regrava ao paginar, e por isso pode cair.
FILHOS_OK = {b"w:rPr", b"w:t", b"w:lastRenderedPageBreak"}
# Entre dois runs, so estes podem aparecer sem impedir a troca.
VIZINHOS_OK = {b"w:proofErr", b"w:bookmarkStart", b"w:bookmarkEnd",
               b"w:commentRangeStart", b"w:commentRangeEnd", b"w:pPr", b"w:p"}


def desesc(b):
    s = b.decode("utf-8")
    return (s.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&"))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def norma_rpr(bloco_run):
    """A assinatura de formatacao do run, sem o ruido que o Word inventa."""
    m = RE_RPR.search(bloco_run)
    if not m:
        return b""
    return RE_RUIDO.sub(b"", m.group(0)).replace(b"<w:rPr></w:rPr>", b"")


# A razao da recusa e lida pelo autor, na margem do proprio trabalho, e por isso
# nao pode sair em nome de tag. O que ele precisa saber e o que atravessa o
# trecho, para decidir se faz a mao.
NOMES = {
    "w:footnoteReference": "uma chamada de nota de rodapé",
    "w:endnoteReference": "uma chamada de nota de fim",
    "w:tab": "uma tabulação",
    "w:br": "uma quebra de linha",
    "w:cr": "uma quebra de linha",
    "w:ptab": "uma tabulação",
    "w:fldChar": "um campo automático (sumário, referência cruzada, número de página)",
    "w:instrText": "um campo automático (sumário, referência cruzada, número de página)",
    "w:fldSimple": "um campo automático (sumário, referência cruzada, número de página)",
    "w:hyperlink": "um vínculo",
    "w:drawing": "uma imagem",
    "w:pict": "uma imagem",
    "w:object": "um objeto incorporado",
    "w:sym": "um símbolo de fonte especial",
    "w:noBreakHyphen": "um hífen que não quebra",
    "w:softHyphen": "um hífen condicional",
    "w:delText": "uma exclusão já marcada no arquivo",
    "w:ins": "uma inserção já marcada no arquivo",
    "w:del": "uma exclusão já marcada no arquivo",
    "w:commentReference": "a marca de um comentário",
}


def atravessa(tags):
    """A razao, escrita para quem vai ler na margem."""
    nomes, vistos = [], set()
    for t in sorted(tags):
        n = NOMES.get(t.decode(), "uma estrutura do Word (%s)" % t.decode())
        if n not in vistos:
            vistos.add(n)
            nomes.append(n)
    return "o trecho atravessa " + " e ".join(nomes)


class Atomo(object):
    """Um pedaco do paragrafo, na ordem do documento.

    `texto` e o que o leitor ve. `barreira` diz que aqui a troca nao passa:
    nota de rodape, campo, imagem, quebra, tabulacao, texto ja excluido."""
    __slots__ = ("ini", "fim", "texto", "rpr", "barreira", "t_spans", "razao")

    def __init__(self, ini, fim, texto, rpr, barreira, t_spans=None, razao=None):
        self.ini, self.fim = ini, fim
        self.texto, self.rpr = texto, rpr
        self.barreira, self.razao = barreira, razao
        self.t_spans = t_spans or []


def _filhos(bloco_run):
    """Os nomes das tags dentro do run, fora do <w:rPr>."""
    corpo = RE_RPR.sub(b"", bloco_run, count=1)
    corte = corpo.find(b">")
    if corte >= 0:
        corpo = corpo[corte + 1:]
    return {nome for fecha, nome in RE_TAG.findall(corpo) if not fecha}


def atomos(bloco):
    """Percorre o XML do paragrafo e devolve os atomos, na ordem do documento."""
    out, pos = [], 0
    for m in RE_RUN.finditer(bloco):
        entre = bloco[pos:m.start()]
        sujeira = {t for _, t in RE_TAG.findall(entre)} - VIZINHOS_OK
        if sujeira:
            out.append(Atomo(m.start(), m.start(), "", None, True,
                             razao=atravessa(sujeira)))
        pos = m.end()
        run = m.group(0)
        t_spans, texto = [], []
        for t in RE_T.finditer(run):
            if t.group(1) is None:
                continue
            a = m.start() + t.start(1)
            t_spans.append((a, a + len(t.group(1))))
            texto.append(desesc(t.group(1)))
        estranhos = _filhos(run) - FILHOS_OK
        if estranhos:
            out.append(Atomo(m.start(), m.end(), "".join(texto), None, True,
                             razao=atravessa(estranhos)))
        elif t_spans:
            out.append(Atomo(m.start(), m.end(), "".join(texto),
                             norma_rpr(run), False, t_spans))
    sujeira = {t for _, t in RE_TAG.findall(bloco[pos:])} - VIZINHOS_OK
    if sujeira:
        out.append(Atomo(len(bloco), len(bloco), "", None, True,
                         razao=atravessa(sujeira)))
    return out


def fluxo(bloco):
    """O texto visivel do paragrafo, o mapa dos caracteres, e os atomos.

    `mapa[i] = (indice do atomo, deslocamento dentro dele)`. Barreiras de
    largura zero, como a chamada de nota de rodape, nao entram no texto e por
    isso so aparecem como fronteira entre dois segmentos de formatacao."""
    ats = atomos(bloco)
    partes, mapa = [], []
    for k, a in enumerate(ats):
        for j in range(len(a.texto)):
            mapa.append((k, j))
        partes.append(a.texto)
    return "".join(partes), mapa, ats


def cabe_num_segmento(mapa, ats, ini, fim):
    """O trecho [ini, fim) esta todo numa formatacao continua e sem barreira?

    Devolve (True, [indices dos atomos]) ou (False, razao escrita)."""
    if fim <= ini or fim > len(mapa):
        return False, "trecho vazio ou fora do parágrafo"
    k0, k1 = mapa[ini][0], mapa[fim - 1][0]
    rpr = ats[k0].rpr
    for k in range(k0, k1 + 1):
        a = ats[k]
        if a.barreira:
            return False, a.razao or "barreira no meio do trecho"
        if a.rpr != rpr:
            return False, ("o trecho atravessa uma mudança de formatação "
                       "(itálico, negrito, fonte ou corpo)")
    return True, list(range(k0, k1 + 1))


# ------------------------------------------------------- a folha de trabalho

CABECALHO_FOLHA = """# Frases endereçáveis — %s

Gerado por `%s --frases`. **Não edite:** os endereços daqui são os que o
aplicador resolve na hora de aplicar, e editar desfaz a correspondência.

Cada frase tem um endereço da forma `{{P464F2}}`, e é ele, e não o texto, que
entra no campo *Está* de um reparo. O `Está` é endereço de uma substituição, e
não citação: o programa copia o trecho do próprio arquivo. Frase marcada com
`✗` %s: um reparo endereçado a ela não vira alteração controlada, e sim
comentário na margem, para o autor fazer à mão.

O reparo se escreve assim, um bloco por troca:

    ## S26
    **Tipo:** restringir
    **Está:** {{P464F2}}
    **Fica:** o texto que entra no lugar
    **Muda:** uma frase sobre o que mudou e por quê

Para retirar a frase sem pôr nada no lugar, escreva `**Fica:** (nada)`. Para
trocar o parágrafo inteiro, endereça-se `{{P464}}`, sem o número de frase.

---
"""


def limites(texto, x, y):
    """Apara o espaço das pontas de um trecho, que nunca entra na troca."""
    while y > x and texto[y - 1].isspace():
        y -= 1
    while x < y and texto[x].isspace():
        x += 1
    return x, y


def escrever_folha(dest, trabalho, programa, ressalva, lista, resolve, limpa):
    """Escreve a folha de frases endereçaveis.

    `resolve(n)` devolve (texto, apta) para o paragrafo n, ou None; `apta(x, y)`
    diz se o trecho pode virar alteracao controlada. Os dois aplicadores passam
    coisas diferentes por ai, e o resto do arquivo e o mesmo."""
    L = [CABECALHO_FOLHA % (trabalho, programa, ressalva)]
    vistos, total, aptas = set(), 0, 0
    for cod, aponta, locs in lista:
        L.append("\n## %s\n" % cod)
        L.append("**Aponta:** %s\n" % limpa(aponta))
        for n in locs:
            achado = resolve(n)
            if achado is None:
                continue
            texto, apta = achado
            if not texto.strip():
                continue
            L.append("### [P%d]\n" % n)
            for i, (x, y) in enumerate(frases(texto), 1):
                x, y = limites(texto, x, y)
                if x >= y:
                    continue
                ok = apta(x, y)
                if (n, i) not in vistos:
                    vistos.add((n, i))
                    total += 1
                    aptas += bool(ok)
                L.append("%s`{{P%dF%d}}` %s\n" % ("" if ok else "✗ ", n, i, texto[x:y]))
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    return total, aptas


# ------------------------------------------------------- arquivo de reparos

RE_BLOCO = re.compile(
    r"\*\*Est[áa]:\*\*(?P<esta>.*?)"
    r"(?:\*\*Fica:\*\*(?P<fica>.*?))?"
    r"(?=\*\*Est[áa]:\*\*|\n#{1,6} |\Z)", re.S)
RE_CABECA = re.compile(r"^#{1,6}\s*([A-Z]{1,2}\d+)\b(.*)$", re.M)
RE_MARCADOR = re.compile(r"\{\{\s*P(\d+)(?:\s*F(\d+))?\s*\}\}")
RE_CAMPO = re.compile(r"\*\*(?:Muda|Custo|Tipo|Onde|Aponta|Abrir|Nota):\*\*.*", re.S)
RE_TIPO = re.compile(r"\*\*Tipo:\*\*\s*(.+)")

TIPOS = ("restringir", "retirar", "completar", "definir", "apontar")


class Reparo(object):
    __slots__ = ("codigo", "tipo", "par", "frase", "novo", "muda", "erro", "linha")

    def __init__(self, **kw):
        for s in self.__slots__:
            setattr(self, s, kw.get(s))


def _limpa(s):
    s = re.sub(r"^\s*[-–—]\s*", "", s.strip())
    return re.sub(r"\s*\n\s*", " ", s).strip()


def ler_reparos(caminho):
    """Le o arquivo de reparos. Cada bloco vira um Reparo, com erro se houver.

    O erro nao interrompe a leitura: bloco malformado precisa chegar ao
    relatorio de recusa, e nao derrubar os quarenta que estao certos."""
    txt = open(caminho, encoding="utf-8").read()
    cabecas = [(m.start(), m.group(1)) for m in RE_CABECA.finditer(txt)]
    tipos = [(m.start(), m.group(1).strip().lower()) for m in RE_TIPO.finditer(txt)]

    def antes(pos, lista):
        achado = None
        for p, v in lista:
            if p >= pos:
                break
            achado = v
        return achado

    out = []
    for m in RE_BLOCO.finditer(txt):
        r = Reparo(codigo=antes(m.start(), cabecas) or "(sem código)",
                   tipo=antes(m.start(), tipos),
                   linha=txt.count("\n", 0, m.start()) + 1)
        if r.tipo and r.tipo.split()[0] not in TIPOS:
            r.tipo = None
        esta = RE_CAMPO.sub("", m.group("esta") or "")
        marcas = RE_MARCADOR.findall(esta)
        residuo = _limpa(RE_MARCADOR.sub("", esta).replace("`", ""))
        if len(marcas) != 1:
            r.erro = ("o campo Está precisa de exatamente um marcador "
                      "{{P123F4}}; achei %d" % len(marcas))
            out.append(r)
            continue
        if len(residuo) > 2:
            # A regra da transcricao, executavel: o Esta e endereco, e endereco
            # nao se digita. Texto ali significa que alguem copiou o trecho a
            # mao, e o copiado ja nao e garantidamente o que esta no arquivo.
            r.erro = ("o campo Está veio com texto digitado (%r). Ele é "
                      "endereço, não citação: só o "
                      "marcador entra." % residuo[:60])
            out.append(r)
            continue
        r.par = int(marcas[0][0])
        r.frase = int(marcas[0][1]) if marcas[0][1] else None
        bruto = m.group("fica")
        if bruto is None:
            r.erro = "bloco sem campo Fica"
            out.append(r)
            continue
        mc = RE_CAMPO.search(bruto)
        r.muda = _limpa(re.sub(r"\*\*\w+:\*\*", " ", mc.group(0))) if mc else None
        novo = _limpa(RE_CAMPO.sub("", bruto).replace("`", ""))
        if novo.lower() in ("(nada)", "(vazio)", "(retirar)", "—", "-", ""):
            novo = ""
        r.novo = novo
        out.append(r)
    return out

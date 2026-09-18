# -*- coding: utf-8 -*-
"""O que os programas do Warat conversacional fazem em comum sobre um .docx.

POR QUE ISTO EXISTE

Tres programas mexem no XML do trabalho: um recusa as alteracoes controladas de
outra pessoa, um aplica as propostas que a autora aceitou, e ambos precisam gravar
um arquivo que o Word abra. Medido em 18/09/2026, na tese que motivou o Warat:

- o ElementTree da biblioteca padrao so grava as declaracoes de namespace que usa,
  e o Word lista no elemento raiz, em `mc:Ignorable`, prefixos que nenhum elemento
  usa. Cinco deles (w15, w16, w16cex, w16cid, w16se) sairam sem declaracao, e um
  arquivo assim o Word pode recusar como ilegivel. `repor_namespaces` copia as
  declaracoes do elemento raiz original;
- a primeira recusa de alteracoes foi feita por expressao regular e quebrou o XML
  (`<w:ins .../>` casa como abertura e engole ate o proximo fechamento). Aqui tudo
  e feito sobre a arvore, e nao sobre o texto.

Uso: modulo, importado pelos outros. `python docx_revisoes.py --autoteste`.
"""
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"


def q(t):
    return "{%s}%s" % (W, t)


def registrar_namespaces(raw):
    """Registra os prefixos do XML cru, para que o ElementTree os preserve."""
    for p, u in re.findall(rb'xmlns:([A-Za-z0-9]+)="([^"]+)"', raw):
        try:
            ET.register_namespace(p.decode(), u.decode())
        except ValueError:
            pass


def carregar(z, nome):
    raw = z.read(nome)
    registrar_namespaces(raw)
    return ET.fromstring(raw)


def repor_namespaces(xml_novo, xml_original):
    """Devolve xml_novo com as declaracoes do elemento raiz de xml_original que faltarem."""
    orig = xml_original.decode("utf-8") if isinstance(xml_original, bytes) else xml_original
    novo = xml_novo.decode("utf-8") if isinstance(xml_novo, bytes) else xml_novo
    m_o = re.search(r"<w:document\b[^>]*>", orig)
    m_n = re.search(r"<w:document\b[^>]*>", novo)
    if not (m_o and m_n):
        return novo.encode("utf-8")
    decl = dict(re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', m_o.group(0)))
    tem = set(re.findall(r'xmlns:([A-Za-z0-9]+)=', m_n.group(0)))
    falta = "".join(' xmlns:%s="%s"' % (p, u) for p, u in decl.items() if p not in tem)
    tag = m_n.group(0)
    if not falta:
        return novo.encode("utf-8")
    fim = "/>" if tag.endswith("/>") else ">"
    novo = novo.replace(tag, tag[: -len(fim)] + falta + fim, 1)
    return novo.encode("utf-8")


def ignoraveis_sem_declaracao(xml):
    x = xml.decode("utf-8") if isinstance(xml, bytes) else xml
    m = re.search(r"<w:document\b[^>]*>", x)
    if not m:
        return []
    tag = m.group(0)
    decl = set(re.findall(r'xmlns:([A-Za-z0-9]+)=', tag))
    ign = re.search(r'Ignorable="([^"]*)"', tag)
    return sorted(set(ign.group(1).split()) - decl) if ign else []


def normal(s):
    return " ".join((s or "").replace(" ", " ").split())


def texto_do_paragrafo(p, modo="atual"):
    """Texto de um <w:p>: atual (tudo), aceito (sem o apagado) ou recusado (sem o inserido)."""
    out = []

    def anda(el, em_ins=False, em_del=False):
        for c in el:
            if c.tag in (q("ins"), q("moveTo")):
                anda(c, True, em_del)
            elif c.tag in (q("del"), q("moveFrom")):
                anda(c, em_ins, True)
            elif c.tag in (q("t"), q("delText")):
                if modo == "aceito" and em_del:
                    continue
                if modo == "recusado" and em_ins:
                    continue
                out.append(c.text or "")
            else:
                anda(c, em_ins, em_del)
    anda(p)
    return normal("".join(out))


def ler_extracao(caminho):
    """{numero: texto} da extracao canonica, titulos incluidos (### [Pn])."""
    par = {}
    for linha in io.open(caminho, encoding="utf-8"):
        m = re.match(r"(?:#+\s*)?\[P(\d+)\]\s?(.*)", linha)
        if m:
            par[int(m.group(1))] = m.group(2).strip()
    return par


def gravar(z_origem, destino, trocas):
    """Copia o zip de origem trocando as partes em `trocas` {nome: bytes}; acrescenta as novas."""
    zout = zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED)
    feitos = set()
    for it in z_origem.infolist():
        data = trocas.get(it.filename, z_origem.read(it.filename))
        feitos.add(it.filename)
        zout.writestr(it, data)
    for nome, data in trocas.items():
        if nome not in feitos:
            zout.writestr(nome, data)
    zout.close()


# ---------------------------------------------------------------- para os autotestes

def docx_minimo(corpo_xml, comentarios_xml=None):
    """Um .docx pequeno em memoria, com mc:Ignorable citando um prefixo sem uso."""
    ns = ('xmlns:w="%s" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
          'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
          'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
          'mc:Ignorable="w14 w15"' % W)
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document %s><w:body>%s</w:body></w:document>' % (ns, corpo_xml))
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="%s">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '</Types>' % CT)
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>' % REL)
    drels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="%s"></Relationships>' % REL
    buf = io.BytesIO()
    z = zipfile.ZipFile(buf, "w")
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/_rels/document.xml.rels", drels)
    z.writestr("word/document.xml", doc)
    if comentarios_xml is not None:
        z.writestr("word/comments.xml", comentarios_xml)
    z.close()
    buf.seek(0)
    return buf


def autoteste():
    falhas = []
    buf = docx_minimo('<w:p><w:r><w:t>um</w:t></w:r></w:p>')
    z = zipfile.ZipFile(buf)
    orig = z.read("word/document.xml")
    root = carregar(z, "word/document.xml")
    novo = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    if not ignoraveis_sem_declaracao(novo):
        falhas.append("o controle nao reproduziu a perda de namespace do ElementTree")
    if ignoraveis_sem_declaracao(repor_namespaces(novo, orig)):
        falhas.append("repor_namespaces nao repos as declaracoes")
    p = ET.fromstring('<w:p xmlns:w="%s"><w:r><w:t>a </w:t></w:r><w:ins><w:r><w:t>b </w:t></w:r></w:ins>'
                      '<w:del><w:r><w:delText>c</w:delText></w:r></w:del></w:p>' % W)
    if (texto_do_paragrafo(p, "aceito"), texto_do_paragrafo(p, "recusado")) != ("a b", "a c"):
        falhas.append("texto aceito/recusado errado: %r %r"
                      % (texto_do_paragrafo(p, "aceito"), texto_do_paragrafo(p, "recusado")))
    return falhas


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f = autoteste()
    print("autoteste: " + ("passou (namespace reposto; texto aceito e recusado)" if not f else "; ".join(f)))
    sys.exit(1 if f else 0)

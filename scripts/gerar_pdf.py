"""Converte caderno ou relatorio em PDF (via LaTeX) e em HTML.

POR QUE ISTO EXISTE

O caderno de conferencia e os relatorios saem em Markdown, que e o formato certo
para o que o instrumento faz com eles: texto puro, versionavel, e que um script
altera com seguranca. **Mas quem recebe o trabalho nao usa Markdown.** Entregar
ao orientando um .md e transferir a ele um problema de ferramenta que nao e dele,
e o efeito pratico e que ele nao abre o arquivo.

TRES SAIDAS, E A ESCOLHA IMPORTA

    html        abre em qualquer navegador com dois cliques, sem instalar nada,
                busca com Ctrl+F e imprime em PDF pelo proprio navegador. E a
                saida que nunca falha, e o padrao quando nao ha LaTeX.
    tufte       PDF com margem larga: o paragrafo na coluna principal e os itens
                do relatorio que o citam na margem, ao lado. E o formato natural
                do caderno, porque caderno e texto anotado.
    classico    PDF com margens normais e os itens em nota de rodape. Menos
                elegante e mais robusto: com muitos paragrafos citados seguidos,
                a nota de margem colide e o Tufte perde.

O .md continua sendo o original. Estes sao derivados: corrija o .md e gere de
novo, nunca o contrario.

Requer pandoc e xelatex para os temas de PDF. Sem eles, gera so o HTML e avisa.

Uso:
    python gerar_pdf.py <arquivo.md> [--tema tufte|classico|html] [--saida DIR]
                        [--titulo T] [--manter-tex]
"""

import argparse
import html as _html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



RAIZ = Path(__file__).resolve().parent
TEMPLATES = RAIZ.parent / "templates"

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

# Marcas do caderno: "**▸ P20** · 2.3, 3.4" (citado) e "**P21** · texto" (simples)
RE_CITADO_MD = re.compile(r"^\*\*▸\s*P(\d+)\*\*\s*·\s*(.+?)\s*$", re.M)
RE_SIMPLES_MD = re.compile(r"^\*\*P(\d+)\*\*\s*·\s*", re.M)

RE_CITADO_HTML = re.compile(r"<p>(<strong>▸\s*P\d+</strong>)")
RE_SIMPLES_HTML = re.compile(r"<p>(<strong>P\d+</strong>)")


# ------------------------------------------------------------------ HTML

MOLDURA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: Georgia, 'Times New Roman', serif; font-size: 17px;
         line-height: 1.62; color: #1a1a1a; background: #fbfaf7;
         max-width: 46rem; margin: 0 auto; padding: 3rem 1.25rem 6rem; }}
  h1 {{ font-size: 2rem; line-height: 1.15; margin: 0 0 1rem; color: #003366; }}
  h2 {{ font-size: 1.25rem; margin: 2.2rem 0 .6rem; color: #003366; }}
  h3 {{ font-size: 1.05rem; margin: 1.6rem 0 .4rem; color: #003366; }}
  p {{ margin: 0 0 .9rem; }}
  hr {{ border: 0; border-top: 1px solid #d9d5cc; margin: 2rem 0; }}
  code {{ font-family: Consolas, monospace; font-size: .88em;
          background: #eae7e0; padding: 1px 5px; border-radius: 2px; }}
  pre {{ background: #eae7e0; padding: .8rem 1rem; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ margin: 1rem 0; padding-left: 1rem;
                border-left: 3px solid #d9d5cc; color: #55524d; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .92em;
           display: block; overflow-x: auto; }}
  td, th {{ border: 1px solid #d9d5cc; padding: .35rem .6rem; text-align: left; }}
  p.citado {{ background: #e6ebf7; padding: .5rem .75rem; margin: 1.6rem 0 .35rem;
              border-left: 3px solid #33477e; }}
  p.numero {{ color: #6c7079; }}
  @media print {{ body {{ background: #fff; max-width: none; padding: 0; }} }}
</style></head><body>
{corpo}
</body></html>
"""


def gerar_html(texto, destino, titulo):
    if MarkdownIt is None:
        sys.exit("markdown-it-py nao esta instalado. `pip install markdown-it-py`")
    md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    corpo = md.render(texto)
    corpo = RE_CITADO_HTML.sub(r'<p class="citado">\1', corpo)
    corpo = RE_SIMPLES_HTML.sub(r'<p class="numero">\1', corpo)
    destino.write_text(
        MOLDURA.format(titulo=_html.escape(titulo), corpo=corpo), encoding="utf-8")
    return destino


# ------------------------------------------------------------------ LaTeX

def preparar_para_latex(texto):
    """Troca as marcas do caderno por comandos que o template define.

    Sem isto, o localizador entraria como negrito solto e o tema Tufte nao teria
    o que pôr na margem: a marca precisa virar comando para que cada tema decida
    onde ela aparece.
    """
    def citado(m):
        return f"`\\citado{{P{m.group(1)}}}{{{m.group(2)}}}`{{=latex}}"

    texto = RE_CITADO_MD.sub(citado, texto)
    texto = RE_SIMPLES_MD.sub(
        lambda m: f"`\\numero{{P{m.group(1)}}}`{{=latex}} ", texto)

    # O template ja imprime o titulo; deixar o primeiro "# " no corpo faz o
    # titulo sair duas vezes na primeira pagina.
    texto = re.sub(r"\A(?:<!--.*?-->\s*)?#\s+.+?\n", "", texto, count=1, flags=re.S)

    # O ▸ nao existe na fonte que o xelatex usa e sai como vazio, abrindo buraco
    # no meio da frase que o explica. Trocado por simbolo matematico, que existe
    # em qualquer instalacao.
    texto = texto.replace("▸", r"`$\triangleright$`{=latex}")

    # OS LOCALIZADORES NO MEIO DA PROSA
    #
    # O relatorio cita o paragrafo do trabalho na propria frase, e sao muitos:
    # 148, 179 e 116 nos tres relatorios do aluno de 03/09/2026. Em corpo de
    # texto e entre colchetes, cada um e uma parada do olho, e num paragrafo
    # medido havia seis. Reclamacao do usuario na mesma data.
    #
    # Nao da para move-los para a margem nem para nota: a maioria esta dentro da
    # frase (so um quarto fica sozinho entre parenteses) e vinte e seis ABREM
    # frase, onde o localizador e o sujeito. Mexer na posicao quebraria a sintaxe.
    # O que se faz e tira-los do caminho sem tira-los do lugar: perdem os
    # colchetes, encolhem e esmaecem. Continuam achaveis com Ctrl+F, porque o
    # arquivo de paragrafos numerados traz a mesma cadeia Pxxx.
    #
    # As faixas vem primeiro: se as simples rodassem antes, [P714]-[P719]
    # viraria dois comandos com um traco solto entre eles, e o traco quebraria
    # linha.
    #
    # Duas formas convivem, e a divisao e por relatorio, nao por acaso: os da
    # Duas dissertacoes escrevem [P714]-[P719], com um par de
    # colchetes de cada lado (26 e 29 no relatorio do aluno), e uma tese
    # escreve [P755-P760], tudo dentro de um par so (33). Medido em 03/09/2026.
    # Tratar so uma delas deixaria um relatorio inteiro sem conversao.
    texto = re.sub(
        r"\[P(\d+)\s*[-–—]\s*P?(\d+)\]",
        lambda m: "`\\loc{P%s–P%s}`{=latex}" % (m.group(1), m.group(2)), texto)
    texto = re.sub(
        r"\[P(\d+)\]\s*[-–—]\s*\[?P?(\d+)\]?",
        lambda m: "`\\loc{P%s–P%s}`{=latex}" % (m.group(1), m.group(2)), texto)
    texto = re.sub(
        r"\[P(\d+)\]", lambda m: "`\\loc{P%s}`{=latex}" % m.group(1), texto)

    # O HIFEN QUE SE REPETE NA LINHA SEGUINTE
    #
    # "2020-2025" saia como "2020-" e "-2025". Nao e defeito: e regra
    # tipografica portuguesa, que repete o hifen ao quebrar um composto
    # ("guarda-" / "-chuva"), e o polyglossia a aplica. Esta certa para palavra
    # composta e errada para intervalo de numeros, onde se le como erro de
    # digitacao. O mbox impede a quebra.
    texto = re.sub(
        r"\b(\d{4})\s*-\s*(\d{4})\b",
        lambda m: "`\\mbox{%s–%s}`{=latex}" % (m.group(1), m.group(2)), texto)
    return texto



# O titulo do relatorio e uma linha so no Markdown, e sai em duas no PDF: o que o
# relatorio e, na primeira, e de quem e o trabalho, na segunda. Pedido de
# 31/08/2026. A divisao fica aqui, e nao no relatorio, para que o Markdown e o
# HTML continuem com o titulo inteiro numa linha.
#
# O corte e no ultimo conectivo que introduz o nome, e so quando o que vem
# depois parece nome proprio, isto e, comeca por maiuscula. "Relatorio sobre o
# Capitulo 5 (Parte II), de Fulano" corta em ", de"; "Relatorio sobre a
# dissertacao de Fulano de Tal" corta em " de ". Titulo sem nome nao
# corta, e sai numa linha so.
RE_AUTORIA = re.compile(
    r"^(?P<obra>.+?)[,]?\s+d[eoa]s?\s+(?P<nome>[A-ZÁÉÍÓÚÂÊÔÃÕÇ][^,]*)$")


def _parte(titulo, qual):
    m = RE_AUTORIA.match(titulo.strip())
    if not m:
        return titulo.strip() if qual == "obra" else ""
    return m.group(qual).strip()


def _titulo_curto(titulo):
    return _parte(titulo, "obra")


def _autoria(titulo):
    return _parte(titulo, "nome")

def gerar_pdf(texto, destino, titulo, tema, manter_tex):
    template = TEMPLATES / f"caderno-{tema}.tex"
    if not template.exists():
        sys.exit(f"não achei o template {template}")

    corpo = preparar_para_latex(texto)
    with tempfile.TemporaryDirectory() as tmp:
        entrada = Path(tmp) / "entrada.md"
        entrada.write_text(corpo, encoding="utf-8")
        cmd = [
            "pandoc", str(entrada),
            "--from", "markdown+raw_attribute+pipe_tables",
            "--template", str(template),
            "--pdf-engine", "xelatex",
            "--metadata", f"title={_titulo_curto(titulo)}",
            "--metadata", f"autoria={_autoria(titulo)}",
            "-o", str(destino),
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        if out.returncode != 0:
            erro = (out.stderr or "")[-1500:]
            print("  falha ao compilar o PDF. Fim da mensagem do LaTeX:")
            print("  " + erro.replace("\n", "\n  "))
            if manter_tex:
                guardado = destino.with_suffix(".tex")
                subprocess.run(cmd[:-2] + ["-o", str(guardado)],
                               capture_output=True, text=True)
                print(f"  .tex guardado em {guardado} para inspeção")
            return None
    return destino


# ------------------------------------------------------------------ principal

def main():
    ap = argparse.ArgumentParser(
        description="Gera HTML e PDF a partir de um .md do projeto.")
    ap.add_argument("md")
    ap.add_argument("--tema", choices=["tufte", "classico", "html"], default="classico",
                    help="padrão clássico, que usa a largura da página; tufte só faz sentido com nota de margem, e o relatório não tem; html não exige LaTeX")
    ap.add_argument("--saida", help="diretório de saída (padrão: o do .md)")
    ap.add_argument("--titulo", help="título; padrão é o primeiro # do arquivo")
    ap.add_argument("--manter-tex", action="store_true",
                    help="guarda o .tex quando a compilação falha")
    a = ap.parse_args()

    origem = Path(a.md)
    if not origem.exists():
        sys.exit(f"não encontrei {origem}")
    texto = origem.read_text(encoding="utf-8", errors="replace")

    titulo = a.titulo
    if not titulo:
        m = re.search(r"^#\s+(.+)$", texto, re.M)
        titulo = m.group(1).strip() if m else origem.stem
    titulo = re.sub(r"[*`]", "", titulo)

    pasta = Path(a.saida) if a.saida else origem.parent
    pasta.mkdir(parents=True, exist_ok=True)

    # O HTML sai sempre: e a saida que nunca falha, e serve de rede quando o
    # LaTeX nao compila num computador que nao seja o de quem gerou.
    alvo_html = gerar_html(texto, pasta / (origem.stem + ".html"), titulo)
    print(f"  HTML: {alvo_html}")

    if a.tema == "html":
        return 0

    if not shutil.which("pandoc") or not shutil.which("xelatex"):
        print("  pandoc ou xelatex ausentes: gerei só o HTML.")
        print("  Abra no navegador e use Imprimir para PDF, que dá o mesmo resultado.")
        return 0

    alvo = gerar_pdf(texto, pasta / (origem.stem + ".pdf"), titulo, a.tema, a.manter_tex)
    if alvo:
        print(f"  PDF:  {alvo}  (tema {a.tema})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

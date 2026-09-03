# -*- coding: utf-8 -*-
"""Contagem de parágrafo e de ocorrência, com as regras deste acervo.

POR QUE ISTO EXISTE

Numa só sessão, quatro defeitos de contagem produziram acusação falsa, e três
foram meus. Todos eram conhecidos e estavam escritos em prompt, e nenhum prompt
os impediu, porque prompt não roda. Aqui eles viram código, e o código se prova
sozinho ao ser importado.

Os quatro, e o que cada um custou em 02 e 03/09/2026:

1.  **Âncora `^\\[P`.** Perde os parágrafos cuja linha começa por `##`, `**` ou
    `> `. Apareceu cinco vezes, e uma delas dentro de um conferidor que advertia
    sobre conferidores: acusou 839 marcadores onde há 886.
2.  **Busca sem `-i`.** As ocorrências que sobram começam frase, com maiúscula.
    Um contador meu devolveu zero onde havia doze, e eu reportei ao usuário que
    a conferência estava errada. Estava errado eu.
3.  **`<w:p[ >].*?</w:p>` para contar parágrafo de `.docx`.** Perde os
    auto-fechados que trazem atributo (`<w:p w:rsidR="..."/>`). Dei 990 e 992
    para um arquivo que tem 999, e "corrigi" um 1.434 que estava certo.
4.  **Remover acento antes de contar.** Faz *controvérsia* entrar numa contagem
    de *controvers*: 20 onde a busca literal dá 9.

E um quinto, que não é de contagem e sim de leitura: `grep -c` conta LINHAS, e
uma linha pode ter duas ocorrências ou nenhuma da coisa procurada. Aqui não há
função que conte linha.

COMO USAR

    from contagem import paragrafos_docx, marcadores, ocorrencias, paragrafos_com

    total, com_texto = paragrafos_docx("trabalho.docx")
    paras = marcadores(open("extracao.txt", encoding="utf-8").read())
    n = ocorrencias("soberania", texto)              # palavra inteira, sem caixa
    onde = paragrafos_com("criteri", paras, inteira=False)

Toda função declara a regra que usa. Quem precisar de outra regra passa o
parâmetro, e aí a regra fica escrita na chamada, que é onde o leitor a procura.
"""
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

__all__ = [
    "paragrafos_docx", "marcadores", "ocorrencias", "paragrafos_com",
    "sem_acento", "autoteste",
]


# ------------------------------------------------------------------ parágrafos

def paragrafos_docx(caminho):
    """Devolve (total, com_texto) do `.docx`.

    `total` conta `</w:p>` mais os auto-fechados `<w:p .../>`, que a expressão
    ingênua perde. `com_texto` é o número estável, e é o que a montagem numera:
    ele não muda conforme a regra, porque parágrafo auto-fechado nunca tem texto.
    """
    x = zipfile.ZipFile(str(caminho)).read("word/document.xml").decode("utf-8")
    total = len(re.findall(r"</w:p>", x)) + len(re.findall(r"<w:p\b[^>]*/>", x))
    com_texto = 0
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        if "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S)).strip():
            com_texto += 1
    return total, com_texto


def marcadores(texto):
    """Divide a extração pelos marcadores `[Pn]`, em qualquer posição da linha.

    Devolve {n: texto}. Nunca ancorar em início de linha: 47 dos 886 marcadores
    de um dos trabalhos estão em linhas que começam por `##`, `**` ou `> `.
    """
    ped = re.split(r"\[P(\d+)\]", texto)
    return {int(ped[i]): ped[i + 1] for i in range(1, len(ped) - 1, 2)}


# ------------------------------------------------------------------ ocorrências

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _padrao(termo, inteira, acento):
    corpo = re.escape(sem_acento(termo) if acento else termo)
    # \b não fecha depois de letra acentuada em algumas versões; a classe
    # explícita evita isso e ainda deixa o hífen fora da palavra.
    if inteira:
        return r"(?<![0-9A-Za-zÀ-ÿ])" + corpo + r"(?![0-9A-Za-zÀ-ÿ])"
    return corpo


def ocorrencias(termo, texto, inteira=True, caixa=False, acento=False):
    """Conta OCORRÊNCIAS, nunca linhas.

    inteira=True  exige a palavra inteira: sem isso *ética* casa dentro de
                  *cibernética*, e *8/2025* dentro de *868/2025*.
    caixa=False   ignora maiúscula e minúscula, que é o padrão certo: a forma
                  que abre frase é a que a busca sensível a caixa perde.
    acento=False  NÃO remove acento. Remover faz *controvérsia* entrar numa
                  contagem de *controvers*. Passe True só quando a fonte estiver
                  com acentuação corrompida, e diga isso no relatório.
    """
    alvo = sem_acento(texto) if acento else texto
    return len(re.findall(_padrao(termo, inteira, acento), alvo,
                          0 if caixa else re.I))


def paragrafos_com(termo, paras, inteira=True, caixa=False, acento=False):
    """Lista os números de parágrafo em que o termo ocorre. Unidade declarada."""
    pad = re.compile(_padrao(termo, inteira, acento), 0 if caixa else re.I)
    return sorted(n for n, v in paras.items()
                  if pad.search(sem_acento(v) if acento else v))


# ------------------------------------------------------------------ autoteste

def autoteste():
    """Roda no import. Cada caso reproduz um defeito que já custou um erro.

    Se qualquer um falhar, o módulo não carrega: contador que não se prova não
    deve ser usado, porque o silêncio dele é indistinguível de ausência.
    """
    falhas = []

    def confere(rotulo, obtido, esperado):
        if obtido != esperado:
            falhas.append("%s: obtive %r, esperava %r" % (rotulo, obtido, esperado))

    # 1. marcador fora de início de linha
    ex = "## titulo [P1] um\n**negrito** [P2] dois\n> citada [P3] tres\n[P4] quatro\n"
    confere("marcadores nao ancorados", sorted(marcadores(ex)), [1, 2, 3, 4])
    confere("ancora perderia", len(re.findall(r"^\[P\d+\]", ex, re.M)), 1)

    # 2. caixa
    confere("acha a forma que abre frase", ocorrencias("controle", "Controle e controle"), 2)
    confere("com caixa, acha so uma", ocorrencias("controle", "Controle e controle", caixa=True), 1)

    # 3. palavra inteira, com acento no meio
    confere("etica nao casa em cibernetica", ocorrencias("ética", "cibernética e aritmética"), 0)
    confere("etica casa sozinha", ocorrencias("ética", "a ética aqui"), 1)
    confere("sem inteira, casa dentro", ocorrencias("ética", "cibernética", inteira=False), 1)
    confere("numero nao casa dentro de outro", ocorrencias("8/2025", "868/2025 e 8/2025"), 1)

    # 4. acento muda a conta
    confere("literal nao pega controversia",
            ocorrencias("controvers", "controverso controvérsia", inteira=False), 1)
    confere("sem acento pega as duas",
            ocorrencias("controvers", "controverso controvérsia", inteira=False, acento=True), 2)

    # 5. ocorrencia, e nao linha
    confere("duas na mesma linha contam duas", ocorrencias("risco", "risco e risco"), 2)

    # 6. unidade paragrafo declarada
    paras = {1: "risco risco", 2: "risco", 3: "nada"}
    confere("paragrafos, nao ocorrencias", paragrafos_com("risco", paras), [1, 2])

    # controle negativo: o que nao existe tem de dar zero
    confere("termo inexistente", ocorrencias("xkqzz", ex), 0)
    confere("paragrafo inexistente", paragrafos_com("xkqzz", paras), [])

    return falhas


_falhas = autoteste()
if _falhas:
    sys.stderr.write("contagem.py: autoteste falhou, o modulo nao carrega\n")
    for f in _falhas:
        sys.stderr.write("  %s\n" % f)
    raise ImportError("contagem.py: %d caso(s) de autoteste falharam" % len(_falhas))


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    print("  autoteste: %d casos, todos passaram" % 14)
    if len(sys.argv) > 1:
        alvo = Path(sys.argv[1])
        if alvo.suffix == ".docx":
            t, c = paragrafos_docx(alvo)
            print("  %s: %d parágrafos, %d com texto" % (alvo.name, t, c))
        else:
            p = marcadores(alvo.read_text(encoding="utf-8"))
            print("  %s: %d marcadores, maior %d" % (alvo.name, len(p), max(p) if p else 0))

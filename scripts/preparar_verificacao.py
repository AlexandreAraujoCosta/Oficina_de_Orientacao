# -*- coding: utf-8 -*-
"""Monta a pasta de verificacao de UMA leitura, para que ela nao espere as outras.

POR QUE ISTO EXISTE

No Warat conversacional a conversa com o autor comeca antes de as leituras
terminarem, e os achados delas so entram depois de verificados. Medido em
18/09/2026: a verificacao so foi disparada depois das tres leituras e do
levantamento, a leitura 2 tinha terminado em seis minutos, e a conversa ficou
parada esperando os dados. Verificar leitura por leitura, a medida que cada uma
termina, e o que o desenho pedia.

O `5-VERIFICACAO.md` espera, numa pasta, `LEVANTAMENTO.md`, o registro da leitura
ao lado, o material e `scripts/`. Duas verificacoes na mesma pasta gravariam o
mesmo `VERIFICACAO.md`. Aqui cada leitura ganha a sua pasta:

    <trabalho>/verificacao-<nome>/
        LEVANTAMENTO.md          so os itens desta leitura (montar_levantamento.py)
        LOTE.txt                 o trabalho inteiro com os itens ao lado (enderecos_em_lote.py --tudo)
        REGISTRO-<nome>.md       o percurso da leitura, copiado
        MATERIAL.md, MAPA.md, extracao/, trabalho.docx   copiados
        scripts/                 ligacao para a pasta de scripts

Uso:
    python scripts/preparar_verificacao.py <pasta-do-trabalho> LEITURA-DADOS.md
    python scripts/preparar_verificacao.py --autoteste
"""
import os
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

AQUI = Path(__file__).resolve().parent
COPIAR = ("MATERIAL.md", "MAPA.md", "trabalho.docx", "trabalho.pdf")


def ligar_scripts(destino):
    alvo = destino / "scripts"
    if alvo.exists():
        return "já existia"
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(alvo), str(AQUI)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return "junção"
    else:
        try:
            os.symlink(str(AQUI), str(alvo))
            return "ligação simbólica"
        except OSError:
            pass
    shutil.copytree(str(AQUI), str(alvo), ignore=shutil.ignore_patterns("__pycache__"))
    return "cópia"


def preparar(pasta, leitura):
    pasta = Path(pasta)
    leitura = Path(leitura) if Path(leitura).is_absolute() else pasta / leitura
    if not leitura.exists():
        raise SystemExit("não achei %s" % leitura)
    nome = leitura.stem.replace("LEITURA-", "")
    dest = pasta / ("verificacao-" + nome)
    (dest / "extracao").mkdir(parents=True, exist_ok=True)
    feitos = []
    for f in COPIAR:
        if (pasta / f).exists():
            shutil.copy2(str(pasta / f), str(dest / f))
            feitos.append(f)
    for f in (pasta / "extracao").glob("*.txt"):
        shutil.copy2(str(f), str(dest / "extracao" / f.name))
        feitos.append("extracao/" + f.name)
    reg = pasta / ("REGISTRO-%s.md" % nome)
    if reg.exists():
        shutil.copy2(str(reg), str(dest / reg.name))
        feitos.append(reg.name)
    shutil.copy2(str(leitura), str(dest / leitura.name))
    r = subprocess.run([sys.executable, str(AQUI / "montar_levantamento.py"), leitura.name,
                        "-o", "LEVANTAMENTO.md"], cwd=str(dest), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 or not (dest / "LEVANTAMENTO.md").exists():
        raise SystemExit("montar_levantamento falhou:\n" + (r.stdout or "") + (r.stderr or ""))
    # o 5-VERIFICACAO supoe que quem despacha ja rodou o lote; ninguem o rodava
    # (critica fria de 18/09). Fica gravado em LOTE.txt, e o pedido diz onde.
    ext = dest / "extracao" / "trabalho.txt"
    if ext.exists():
        r = subprocess.run([sys.executable, str(AQUI / "enderecos_em_lote.py"), "LEVANTAMENTO.md",
                            str(Path("extracao") / "trabalho.txt"), "--tudo"], cwd=str(dest),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not r.stdout.strip():
            raise SystemExit("enderecos_em_lote falhou:\n" + (r.stdout or "")[-800:] + (r.stderr or "")[-800:])
        (dest / "LOTE.txt").write_text(r.stdout, encoding="utf-8")
        feitos.append("LOTE.txt")
    ligacao = ligar_scripts(dest)
    return dest, feitos, ligacao


def autoteste():
    f = []
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "extracao").mkdir()
        (d / "extracao" / "trabalho.txt").write_text("[P1] Um.\n", encoding="utf-8")
        (d / "MATERIAL.md").write_text("material", encoding="utf-8")
        (d / "LEITURA-DADOS.md").write_text("### D1. Um item que afirma sobre o trabalho\n\n"
                                            "Aponta [P1].\n", encoding="utf-8")
        (d / "REGISTRO-DADOS.md").write_text("percurso", encoding="utf-8")
        dest, feitos, lig = preparar(d, "LEITURA-DADOS.md")
        lev = (dest / "LEVANTAMENTO.md").read_text(encoding="utf-8")
        if "D1" not in lev:
            f.append("o levantamento não traz o item da leitura")
        for x in ("MATERIAL.md", "REGISTRO-DADOS.md", "extracao/trabalho.txt", "LOTE.txt"):
            if not (dest / x).exists():
                f.append("não copiou %s" % x)
        if not (dest / "scripts" / "montar_levantamento.py").exists():
            f.append("a pasta de scripts não ficou acessível (%s)" % lig)
        if lig in ("junção", "ligação simbólica"):
            try:
                (dest / "scripts").unlink() if os.name != "nt" else os.rmdir(str(dest / "scripts"))
            except OSError:
                pass
    return f


def main():
    if sys.argv[1:] == ["--autoteste"]:
        f = autoteste()
        print("autoteste: " + ("passou (pasta própria, levantamento da leitura, material e scripts)"
                               if not f else "FALHOU: " + "; ".join(f)))
        return 1 if f else 0
    if len(sys.argv) != 3:
        print(__doc__.split("Uso:")[1])
        return 2
    dest, feitos, lig = preparar(sys.argv[1], sys.argv[2])
    print("  %s pronta: %s; scripts por %s" % (dest, ", ".join(feitos), lig))
    print("  Despache a verificação nela, com prompts/leituras/5-VERIFICACAO.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

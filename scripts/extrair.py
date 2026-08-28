"""Extracao canonica: um texto por trabalho, com impressao digital.

POR QUE ISTO EXISTE

Todo localizador [P123] aponta para um paragrafo do **texto extraido**, e nao do
arquivo original. Ate 17/08/2026 esse texto nao existia em lugar nenhum: cada
leitura, cada verificador e cada atacante rodava o extrator de novo para um
arquivo temporario proprio. Foram mais de trinta extracoes do mesmo texto, e
disso vinham tres problemas.

O primeiro e serio: **se o extrator mudar, a numeracao muda, e os localizadores
de todo relatorio ja entregue passam a apontar para o lugar errado, sem que nada
acuse**. O segundo: agentes concorrentes escrevendo em /tmp com nomes parecidos
chegaram a sobrescrever o auxiliar um do outro. O terceiro: custo.

A CACHE E PERIGOSA SE NAO FOR IMPRESSA

Guardar a extracao sem identificar o que a produziu troca um problema por outro
pior: extracao velha lida com extrator novo devolve localizador errado em
silencio, que e exatamente o modo de falha que este projeto passou dias
catalogando. Por isso cada arquivo carrega, no cabecalho, o hash do trabalho e o
hash do extrator, e quem le recusa a cache quando qualquer um dos dois muda.

E A EXTRACAO ANTIGA NAO SE APAGA

Quando a impressao digital muda, a extracao anterior e preservada com o hash no
nome. Relatorio ja entregue promete ao autor que ele confere abrindo o paragrafo
indicado, e essa promessa tem de continuar executavel depois de o extrator mudar.
Apagar a extracao antiga quebraria, retroativamente, a conferibilidade de tudo
que ja saiu.

Uso:
    python extrair.py <trabalho.pdf|.docx> [...]        extrai o que faltar
    python extrair.py --todos <pasta>                   varre a pasta
    python extrair.py --forcar <trabalho>               reextrai mesmo batendo
    python extrair.py --listar                          mostra o que existe
"""

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PROJETO = RAIZ.parent

# A extracao guarda texto do trabalho de outra pessoa, e por isso e gravada
# onde se trabalha, e nao dentro da arvore da maquinaria. OFICINA_EXTRACAO
# fixa outro lugar, para quem preferir um so.
DESTINO = Path(os.environ.get("OFICINA_EXTRACAO") or (Path.cwd() / "extracao"))

MARCA = "##EXTRACAO"


def digitar(caminho, tamanho=16):
    h = hashlib.sha256(Path(caminho).read_bytes()).hexdigest()
    return h[:tamanho]


def extrator_de(trabalho):
    ext = str(trabalho).lower()
    if ext.endswith(".docx"):
        return RAIZ / "analisar_docx.py"
    if ext.endswith(".pdf"):
        return RAIZ / "analisar_pdf.py"
    raise SystemExit(f"nao sei extrair {Path(trabalho).name}: use .docx ou .pdf")


def impressao(trabalho):
    """(hash do trabalho, hash do extrator). Muda qualquer um, a cache morre."""
    return digitar(trabalho), digitar(extrator_de(trabalho))


def caminho_de(trabalho):
    return DESTINO / (Path(trabalho).stem + ".txt")


def ler_cabecalho(arquivo):
    """Devolve (hash_trabalho, hash_extrator) do cabecalho, ou (None, None)."""
    try:
        with open(arquivo, encoding="utf-8", errors="replace") as f:
            for _ in range(6):
                linha = f.readline()
                if not linha.startswith(MARCA):
                    break
                if "trabalho=" in linha and "extrator=" in linha:
                    partes = dict(
                        p.split("=", 1) for p in linha.split()[1:] if "=" in p
                    )
                    return partes.get("trabalho"), partes.get("extrator")
    except OSError:
        pass
    return None, None


def vigente(trabalho):
    """A cache existe e bate? Devolve o caminho, ou None."""
    alvo = caminho_de(trabalho)
    if not alvo.exists():
        return None
    ht, he = impressao(trabalho)
    ct, ce = ler_cabecalho(alvo)
    return alvo if (ct == ht and ce == he) else None


def extrair(trabalho, forcar=False):
    trabalho = Path(trabalho)
    if not trabalho.exists():
        raise SystemExit(f"nao encontrei {trabalho}")

    alvo = caminho_de(trabalho)
    ht, he = impressao(trabalho)

    if not forcar and vigente(trabalho):
        print(f"  {trabalho.name}: ja extraido e batendo")
        return alvo

    if alvo.exists():
        ct, ce = ler_cabecalho(alvo)
        # Nao se apaga extracao antiga: relatorio ja entregue depende dela.
        guardado = alvo.with_suffix(f".{ct or 'sem'}-{ce or 'marca'}.txt")
        if not guardado.exists():
            alvo.replace(guardado)
            print(f"  ATENCAO: a impressao mudou. A anterior foi preservada em")
            print(f"           {guardado.name}")
            print(f"           Os localizadores dos relatorios ja emitidos referem-se")
            print(f"           a ela, e podem nao valer para a nova numeracao.")

    script = extrator_de(trabalho)
    out = subprocess.run(
        [sys.executable, str(script), "texto", str(trabalho)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if out.returncode != 0:
        raise SystemExit(f"falha ao extrair {trabalho.name}: {(out.stderr or '')[:300]}")

    DESTINO.mkdir(parents=True, exist_ok=True)
    cabecalho = (
        f"{MARCA} trabalho={ht} extrator={he}\n"
        f"{MARCA} fonte={trabalho.name}\n"
        f"{MARCA} extrator_arquivo={script.name}\n"
        f"{MARCA} Nao edite. Gerado por scripts/extrair.py; a impressao digital acima\n"
        f"{MARCA} e conferida por quem le, e edicao manual invalida a conferencia.\n"
    )
    alvo.write_text(cabecalho + out.stdout, encoding="utf-8")

    n = sum(1 for l in out.stdout.splitlines() if "] P" in l or l.strip().startswith("[P"))
    print(f"  {trabalho.name}: extraido, ~{n} linhas de paragrafo -> {alvo.name}")
    return alvo


def listar():
    if not DESTINO.exists():
        print("nenhuma extracao ainda")
        return
    for f in sorted(DESTINO.glob("*.txt")):
        ct, ce = ler_cabecalho(f)
        marca = "arquivada" if f.name.count(".") > 1 else "vigente"
        print(f"  {f.name:<52} {marca:<10} trabalho={ct} extrator={ce}")


def main():
    ap = argparse.ArgumentParser(description="Extracao canonica com impressao digital.")
    ap.add_argument("trabalhos", nargs="*")
    ap.add_argument("--todos", help="pasta a varrer por .pdf e .docx")
    ap.add_argument("--forcar", action="store_true", help="reextrai mesmo batendo")
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()

    if a.listar:
        listar()
        return 0

    alvos = [Path(t) for t in a.trabalhos]
    if a.todos:
        p = Path(a.todos)
        alvos += sorted(list(p.glob("*.pdf")) + list(p.glob("*.docx")))
    if not alvos:
        ap.error("informe um trabalho, --todos <pasta> ou --listar")

    for t in alvos:
        extrair(t, a.forcar)
    return 0


if __name__ == "__main__":
    sys.exit(main())

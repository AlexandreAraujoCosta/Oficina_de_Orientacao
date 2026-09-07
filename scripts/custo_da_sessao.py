# -*- coding: utf-8 -*-
"""Quanto uma sessao gastou: relogio, chamadas e tokens, com o preco em reais.

POR QUE ISTO EXISTE

O registro de cada sessao guarda, mensagem a mensagem, o instante e os tokens de
entrada, de saida e de cache. O que falta e a soma. Sem ela, "demorou muito" e
impressao, e a decisao entre modelos e vias fica sem numero.

Medido em 06/09/2026 com este programa: numa sessao de trabalho, o cache serviu
98,4% da entrada, o intervalo mediano entre eventos foi de 1,6 segundo, e as
8.496 chamadas de ferramenta foram TODAS enviadas sozinhas, uma por mensagem.

O QUE ELE NAO SABE

O preco do cache. Token lido do cache custa uma fracao do preco de entrada, e a
fracao muda; aqui ele entra como entrada cheia, de modo que **o valor em reais e
teto, e nao conta**. O que se compara entre duas execucoes continua valendo,
porque as duas sao superestimadas do mesmo jeito.

Uso:
    python scripts/custo_da_sessao.py                    a sessao mais recente
    python scripts/custo_da_sessao.py --ultimas 5        as cinco mais recentes
    python scripts/custo_da_sessao.py <arquivo.jsonl>    uma em particular
    python scripts/custo_da_sessao.py --modelo pequeno   preco do modelo pequeno
"""
import argparse
import io
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ATUALIZE AS TRES LINHAS QUANDO O PRECO MUDAR: custo velho apresentado como
# atual e pior do que custo nenhum.
PRECO = {"grande": (5.0, 25.0), "pequeno": (3.0, 15.0)}   # (entrada, saida) USD/milhao
DOLAR = 5.12
ATUALIZADO_EM = "06/09/2026"

RAIZ = Path.home() / ".claude" / "projects"


def sessoes(n):
    todas = sorted(RAIZ.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return todas[:n]


def ler(caminho):
    inst, ferr = [], Counter()
    ent = saida = cache_lido = cache_novo = 0
    with io.open(str(caminho), encoding="utf-8", errors="replace") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha[0] != "{":
                continue
            try:
                o = json.loads(linha)
            except Exception:
                continue
            t = o.get("timestamp")
            if isinstance(t, str):
                try:
                    inst.append(datetime.fromisoformat(t.replace("Z", "+00:00")))
                except Exception:
                    pass
            msg = o.get("message") or {}
            u = msg.get("usage") or {}
            ent += u.get("input_tokens") or 0
            saida += u.get("output_tokens") or 0
            cache_lido += u.get("cache_read_input_tokens") or 0
            cache_novo += u.get("cache_creation_input_tokens") or 0
            c = msg.get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        ferr[b.get("name", "?")] += 1
    return inst, ferr, ent, saida, cache_lido, cache_novo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--ultimas", type=int, default=1)
    ap.add_argument("--modelo", choices=("grande", "pequeno"), default="grande")
    a = ap.parse_args()

    alvos = [Path(a.arquivo)] if a.arquivo else sessoes(a.ultimas)
    if not alvos:
        print("  não achei registro de sessão em %s" % RAIZ)
        return 2
    p_ent, p_sai = PRECO[a.modelo]

    for cam in alvos:
        inst, ferr, ent, saida, clido, cnovo = ler(cam)
        entrada_total = ent + clido + cnovo
        usd = (entrada_total * p_ent + saida * p_sai) / 1e6
        # Supoe o token lido do cache a um decimo do preco de entrada, que e
        # a ordem usual. E SUPOSICAO DECLARADA, nao tabela conferida, e por
        # isso as duas contas aparecem lado a lado: numa sessao longa a
        # diferenca passa de dez vezes, e so o teto enganaria mais do que
        # informaria.
        usd_est = ((ent + cnovo) * p_ent + clido * p_ent * 0.1
                   + saida * p_sai) / 1e6
        print("\n  %s" % cam.name)
        print("  pasta: %s" % cam.parent.name)
        if inst:
            inst.sort()
            span = (inst[-1] - inst[0]).total_seconds() / 60.0
            gaps = sorted((inst[i + 1] - inst[i]).total_seconds()
                          for i in range(len(inst) - 1))
            gaps = [g for g in gaps if 0 <= g < 3600]
            ativo = sum(gaps) / 60.0
            print("  do primeiro ao último evento: %.0f min (%.1f h)" % (span, span / 60))
            print("  soma dos intervalos abaixo de 1 h: %.0f min" % ativo)
            if gaps:
                print("  intervalo mediano entre eventos: %.1f s" % gaps[len(gaps) // 2])
        tot = sum(ferr.values())
        print("  chamadas de ferramenta: %d" % tot)
        for n, c in ferr.most_common(6):
            print("     %-28s %5d  (%4.1f%%)" % (n, c, 100.0 * c / max(1, tot)))
        print("  tokens: entrada crua %d | cache lido %d | cache gravado %d | saída %d"
              % (ent, clido, cnovo, saida))
        if entrada_total:
            print("  servido por cache: %.1f%%" % (100.0 * clido / entrada_total))
        print("  custo, modelo %s:" % a.modelo)
        print("     teto, cache a preco cheio ........ US$ %9.2f  ~  R$ %10.2f"
              % (usd, usd * DOLAR))
        print("     com o cache a 10%% da entrada ..... US$ %9.2f  ~  R$ %10.2f"
              % (usd_est, usd_est * DOLAR))

    print("")
    print("  Nenhum dos dois e conta de pagar. O teto poe o cache a preco")
    print("  cheio; a outra supoe o cache a um decimo da entrada, que e a ordem")
    print("  usual e e SUPOSICAO declarada. O que se compara entre duas")
    print("  execucoes vale nos dois casos, porque erram do mesmo jeito.")

    print("  Preços de %s: entrada US$ %.0f e saída US$ %.0f por milhão; dólar a %.2f."
          % (ATUALIZADO_EM, p_ent, p_sai, DOLAR))
    return 0


if __name__ == "__main__":
    sys.exit(main())

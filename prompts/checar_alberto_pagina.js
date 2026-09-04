// Confere a pagina do Alberto antes de publicar.
// Roda de dentro de prompts/: node checar_alberto_pagina.js
const fs = require("fs");
const { Script } = require("vm");
const html = fs.readFileSync("analisador.html", "utf8");
const md = fs.readFileSync("ALBERTO.md", "utf8").replace(/\r\n/g, "\n");

const marca = "const P_UNICO = ";
const i = html.indexOf(marca + '"');
if (i < 0) { console.error("P_UNICO nao encontrado"); process.exit(1); }

// Acha o fecho do literal respeitando escape. O texto tem '";' internos, e um
// indexOf ingenuo para no meio, de modo que o JSON.parse falha sem que o
// literal tenha defeito nenhum.
let j = i + marca.length + 1;
for (;;) {
  const k = html.indexOf('"', j);
  if (k < 0) { console.error("literal sem fecho"); process.exit(1); }
  let barras = 0, q = k - 1;
  while (html[q] === "\\") { barras++; q--; }
  if (barras % 2 === 0) { j = k; break; }
  j = k + 1;
}
const cru = html.slice(i + marca.length, j + 1);
let P;
try { P = JSON.parse(cru); }
catch (e) { console.error("LITERAL NAO COMPILA:", e.message); process.exit(1); }
console.log("literal compila |", P.length, "chars | identico ao ALBERTO.md:", P === md);
if (P !== md) {
  for (let n = 0; n < Math.max(P.length, md.length); n++) {
    if (P[n] !== md[n]) {
      console.log("  primeira diferenca em", n);
      console.log("  pagina :", JSON.stringify(P.slice(n - 40, n + 40)));
      console.log("  arquivo:", JSON.stringify(md.slice(n - 40, n + 40)));
      break;
    }
  }
  process.exitCode = 1;
}

const blocos = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
console.log("blocos de script:", blocos.length);
blocos.forEach((b, n) => {
  try { new Script(b); console.log("  bloco " + (n + 1) + " compila (" + b.length + " chars)"); }
  catch (e) { console.error("  bloco " + (n + 1) + " NAO COMPILA: " + e.message); process.exitCode = 1; }
});

// Controle negativo: o conferidor tem de recusar codigo quebrado.
try {
  new Script("function {");
  console.log("CONTROLE FALHOU: codigo quebrado passou");
  process.exitCode = 1;
} catch (e) {
  console.log("controle negativo: codigo quebrado e recusado");
}

const checa = [
  ["title novo", /<title>Alberto — a análise geral<\/title>/, true],
  ["h1 novo", /<h1>Alberto — a análise geral<\/h1>/, true],
  ["textarea do prompt", /id="textoPrompt"/, true],
  ["seletor de vias", /class="via-bt"/, true],
  ["medidor de .docx", /id="entrada"/, true],
  ["guia do agente", /id="guia-agente"/, true],
  ["guia do chat", /id="guia-chat"/, true],
  ["sao duas vias, e nao tres", /id="guia-claude"|id="guia-vscode"/, false],
  ["o guia do agente cobre os dois agentes", /Claude Code/, true],
  ["o guia do agente cobre os dois agentes \(VS Code\)", /VS Code/, true],
  ["cita o LUIS.md aposentado", /LUIS\.md/, false],
  ["aponta para prompts\/leituras", /prompts\/leituras/, true],
  ["titulo velho sumiu", /analisador de consistência/, false],
];
for (const [nome, re, esperado] of checa) {
  const achou = re.test(html);
  const ok = achou === esperado;
  console.log("  " + (ok ? "ok    " : "FALHA ") + nome + (achou ? " (presente)" : " (ausente)"));
  if (!ok) process.exitCode = 1;
}

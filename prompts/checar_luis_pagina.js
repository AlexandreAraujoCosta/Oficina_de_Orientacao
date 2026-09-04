// Confere a pagina do Luis antes de publicar.
//
// POR QUE ISTO EXISTE
//
// A pagina traz o prompt portatil embutido num <pre>, e o repositorio traz o
// mesmo prompt em ANALISADOR-PORTATIL.md. Nada obrigava os dois a coincidirem, e
// em 04/09/2026 eles tinham divergido em mais de mil palavras sem que nada
// acusasse: a pagina publicada servia uma versao antiga, com a escala de veredito
// que fora substituida no dia anterior. O Alberto ja tinha conferidor
// (checar_alberto_pagina.js) e por isso nao sofreu disso.
//
// Uso:  node checar_luis_pagina.js

const fs = require("fs");
const path = require("path");

const AQUI = __dirname;
const html = fs.readFileSync(path.join(AQUI, "luis.html"), "utf8");
const md = fs.readFileSync(path.join(AQUI, "ANALISADOR-PORTATIL.md"), "utf8");

let falhas = 0;
function diz(rot, ok, extra) {
  console.log("  %s  %s%s", ok ? "ok  " : "FALHA", rot, extra ? " | " + extra : "");
  if (!ok) falhas++;
}

// 1. O prompt embutido e identico ao arquivo do repositorio.
const m = html.match(/<pre id="p-luis">([\s\S]*?)<\/pre>/);
diz("o <pre> do prompt existe", !!m);
if (m) {
  const emb = m[1];
  diz("prompt embutido identico ao ANALISADOR-PORTATIL.md",
      emb.trim() === md.trim(),
      emb.trim().split(/\s+/).length + " palavras na pagina, " +
      md.trim().split(/\s+/).length + " no arquivo");
  // Escape: se o .md ganhar < & >, o <pre> quebra a pagina em silencio.
  diz("o .md nao traz caractere que exija escape em HTML",
      !/[<>&]/.test(md));
}

// 2. Os blocos de script compilam.
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((x) => x[1]);
diz("ha dois blocos de script", scripts.length === 2, scripts.length + " encontrados");
scripts.forEach(function (s, i) {
  let ok = true;
  try { new Function(s); } catch (e) { ok = false; }
  diz("bloco " + (i + 1) + " compila", ok);
});

// Controle positivo: o compilador tem de recusar codigo quebrado.
let recusou = false;
try { new Function("function ( {"); } catch (e) { recusou = true; }
diz("controle positivo: codigo quebrado e recusado", recusou);

// 3. O que a pagina precisa dizer, e o que nao pode mais dizer.
const presentes = [
  ["title da pagina", "<title>Luis</title>"],
  ["seletor de vias", 'class="via-bt"'],
  ["guia do chat", 'id="guia-chat"'],
  ["guia do Claude Code", 'id="guia-claude"'],
  ["guia do VS Code", 'id="guia-vscode"'],
  ["aponta o pipeline", "prompts/leituras/"],
  ["remete ao Alberto para o chat", "a ferramenta atual é o"],
  ["escala nova do veredito", "apto a ser aprovado"],
];
const ausentes = [
  ["nao manda rodar o LUIS.md", "Leia prompts/LUIS.md nesta pasta"],
  ["escala velha do veredito sumiu", "pronto para ir à banca"],
];
presentes.forEach(function (par) { diz(par[0] + " (presente)", html.includes(par[1])); });
ausentes.forEach(function (par) { diz(par[0] + " (ausente)", !html.includes(par[1])); });

// Controle positivo da checagem de presenca.
diz("controle positivo: procura por texto inexistente falha",
    !html.includes("zzz-texto-que-nao-existe-zzz"));

console.log(falhas ? "\n  " + falhas + " FALHA(S)" : "\n  pagina do Luis conferida");
process.exit(falhas ? 1 : 0);

// Confere a pagina do Luis antes de publicar.
//
// POR QUE ISTO EXISTE
//
// A pagina do Alberto tinha conferidor desde que foi feita, e a do Luis nao. Em
// 04/09/2026 apareceu o que isso custa: ela servia um prompt embutido mil
// palavras diferente do arquivo do repositorio, com a escala de veredito
// substituida no dia anterior, e descrevia o Alberto pelo que ele era antes do
// redesenho de 03/09. Nada acusava nenhuma das tres coisas.
//
// A via de chat saiu da pagina em 04/09: numa conversa a ferramenta e o Alberto,
// e o prompt que estava aqui destilava o LUIS.md aposentado. O que este programa
// confere agora e que ela nao volte.
//
// Uso:  node checar_luis_pagina.js

const fs = require("fs");
const path = require("path");

const AQUI = __dirname;
const html = fs.readFileSync(path.join(AQUI, "luis.html"), "utf8");

// A prosa se confere sobre o texto sem marcacao: em 04/09/2026 uma checagem
// quebrou porque o nome de um agente virou link no meio da frase, e a frase
// continuava certa para quem le.
const texto = html.replace(/<[^>]+>/g, "");

let falhas = 0;
function diz(rot, ok, extra) {
  console.log("  %s  %s%s", ok ? "ok  " : "FALHA", rot, extra ? " | " + extra : "");
  if (!ok) falhas++;
}

// 1. A via de chat nao pode voltar: numa conversa a ferramenta e o Alberto.
diz("nao ha botao de via de chat", !html.includes('data-via="chat"'));
diz("nao ha guia de chat", !html.includes('id="guia-chat"'));
diz("nao ha prompt portatil embutido", !html.includes('id="p-luis"'));
diz("remete ao Alberto para a conversa",
    texto.includes("a ferramenta é o Alberto"));
diz("diz por que nao ha via de chat, e a razao e a sessao unica",
    texto.includes("sessões separadas"));
diz("nao afirma que conversa nao roda comando",
    !texto.includes("não roda comando nenhum"));

// 2. Os blocos de script compilam.
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((x) => x[1]);
diz("ha um bloco de script", scripts.length === 1, scripts.length + " encontrados");
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
  ["title da pagina", "<title>Luis — a análise minuciosa</title>"],
  ["guia do agente", 'id="guia-agente"'],
  ["o guia cobre o Claude Code", "Claude Code"],
  ["o guia cobre o VS Code", "VS Code"],
  ["aponta o pipeline", "prompts/leituras/"],
];
const ausentes = [
  ["nao manda rodar o LUIS.md", "Leia prompts/LUIS.md nesta pasta"],
  ["nao descreve o Alberto pelo desenho anterior a 03/09", "roda em modelo menor"],
  ["escala velha do veredito sumiu", "pronto para ir à banca"],
  ["nao voltou o prompt embutido", "Luis — versão portátil"],
  ["nao ha seletor, porque ha uma via so", 'class="via-bt"'],
  ["nao voltaram os guias separados por produto", 'id="guia-claude"'],
];
presentes.forEach(function (par) { diz(par[0] + " (presente)", html.includes(par[1])); });
ausentes.forEach(function (par) { diz(par[0] + " (ausente)", !html.includes(par[1])); });

// Controle positivo da checagem de presenca.
diz("controle positivo: procura por texto inexistente falha",
    !html.includes("zzz-texto-que-nao-existe-zzz"));

console.log(falhas ? "\n  " + falhas + " FALHA(S)" : "\n  pagina do Luis conferida");
process.exit(falhas ? 1 : 0);

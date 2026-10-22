#!/usr/bin/env node
/* 離線閱讀器機械檢查：用最小 DOM 樁跑每一個視圖，掃 undefined/NaN/[object Object] 與空視圖。
   用法：node scripts/check_reader.js */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const ROOT = path.resolve(__dirname, "..");
const DATA = fs.readFileSync(path.join(ROOT, "reader/assets/data.js"), "utf8");
const APP = fs.readFileSync(path.join(ROOT, "reader/assets/app.js"), "utf8");
const BAD = /undefined|NaN|\[object Object\]/g;

function mkEl(tag) {
  const e = {
    tagName: tag, className: "", _text: "", _html: "", style: {}, children: [], attrs: {},
    appendChild(c) { this.children.push(c); return c; },
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener() {}, onclick: null,
    querySelector() { return mkEl("div"); }, querySelectorAll() { return []; }, value: "",
  };
  Object.defineProperty(e, "textContent", { get() { return this._text; }, set(v) { this._text = String(v); } });
  Object.defineProperty(e, "innerHTML", { get() { return this._html; }, set(v) { this._html = String(v); } });
  return e;
}
function walk(n, acc) {
  if (!n) return acc;
  acc.push(n);
  (n.children || []).forEach(c => walk(c, acc));
  return acc;
}

const views = ["home", "themes", "read", "items", "concept", "index", "coverage", "prep", "method", "collation", "limits", "mine", "about"];
const store = {};
const listeners = {};
let fails = 0;

const viewNode = mkEl("main");
const doc = {
  createElement: mkEl,
  createTextNode(t) { const n = mkEl("#text"); n._text = String(t); return n; },
  querySelector(s) { return s === "#view" ? viewNode : mkEl("div"); },
  querySelectorAll() { return []; },
  getElementById() { return mkEl("div"); },
  body: mkEl("body"),
};
const win = {
  document: doc, LS: null, addEventListener(k, f) { (listeners[k] = listeners[k] || []).push(f); },
  location: { hash: "#/idea" }, scrollTo() {}, confirm() { return true; },
  localStorage: {
    getItem(k) { return store[k] || null; },
    setItem(k, v) { store[k] = String(v); },
  },
};
store["lingshu.reader.v1"] = JSON.stringify({ agree: 1 });

function Option(text, value) { const o = mkEl("option"); o.textContent = text; o.value = value; return o; }
const ctx = vm.createContext({ window: win, document: doc, localStorage: win.localStorage, location: win.location, confirm: win.confirm, console, Option });
vm.runInContext(DATA, ctx);
vm.runInContext(APP, ctx);

console.log("視圖檢查：");
const routes = views.concat(["read?seq=40", "items?seq=40", "items?theme=entry"]);
for (const v of routes) {
  win.location.hash = "#/" + v;
  viewNode._html = ""; viewNode.children = [];
  (listeners.hashchange || []).forEach(f => f());
  const html = walk(viewNode, []).map(n => (n._html || "") + (n._text || "")).join(" ");
  const nodes = walk(viewNode, []).length;
  const bad = (html.match(BAD) || []).slice(0, 3);
  const empty = nodes <= 2 && !html.trim();
  if (bad.length || empty) { fails++; console.log(`  ✗ ${v}  nodes=${nodes} bad=${JSON.stringify(bad)} empty=${empty}`); }
  else console.log(`  ✓ ${v}  nodes=${nodes} html=${html.length}`);
}
/* 發布資訊單一來源：data/發布資訊.json 與 data.js 的 meta.release 必須一致，
   且「關於」頁要如實顯示授權／聯絡（未定時必須看得到「待定／待補」）。 */
const REL = JSON.parse(fs.readFileSync(path.join(ROOT, "data/發布資訊.json"), "utf8"));
const got = ctx.window.LS.meta.release || {};
const drift = Object.keys(REL).filter(k => k !== "選項" && k !== "待決說明" && k !== "待決"
  && JSON.stringify(REL[k]) !== JSON.stringify(got[k]));
win.location.hash = "#/about";
viewNode._html = ""; viewNode.children = [];
(listeners.hashchange || []).forEach(f => f());
const aboutHtml = walk(viewNode, []).map(n => (n._html || "") + (n._text || "")).join(" ");
const aboutFails = [];
if (drift.length) aboutFails.push("data.js 與 data/發布資訊.json 不同步：" + drift.join("、"));
if (!aboutHtml.includes(REL["站名"])) aboutFails.push("關於頁沒有站名");
if (REL["授權"] === "待定" && !aboutHtml.includes("待定")) aboutFails.push("授權未定卻未顯示「待定」");
if (REL["授權"] !== "待定" && !aboutHtml.includes(REL["授權"])) aboutFails.push("關於頁沒有顯示已定的授權");
if (REL["聯絡"] === "待補" && !aboutHtml.includes("待補")) aboutFails.push("聯絡未填卻未顯示「待補」");
if (REL["Anki實機"] === "未測" && !aboutHtml.includes("Anki 實機")) aboutFails.push("Anki 未測卻未列為待決");
if (aboutFails.length) { fails++; console.log("  ✗ release " + aboutFails.join("；")); }
else console.log(`  ✓ release  站名=${REL["站名"]} 授權=${REL["授權"]} 聯絡=${REL["聯絡"]}`);

process.exit(fails ? 1 : 0);
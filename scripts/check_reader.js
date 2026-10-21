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

const views = ["home", "read", "items", "concept", "index", "prep", "method", "limits", "mine", "about"];
const store = {};
const listeners = {};
let fails = 0;

const viewNode = mkEl("main");
const doc = {
  createElement: mkEl,
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
for (const v of views) {
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
process.exit(fails ? 1 : 0);

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
    /* 嚴格模仿瀏覽器：appendChild 只收節點。樁太寬容會讓 'appendChild("...")' 這種錯漏過 */
    appendChild(c) {
      if (!c || typeof c !== "object") throw new TypeError("appendChild: parameter 1 is not of type 'Node'（收到 " + typeof c + "）");
      this.children.push(c); return c;
    },
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

const views = ["home", "themes", "binghou", "read", "items", "concept", "law", "meridian", "suwen", "prep", "method", "collation", "limits", "mine", "about", "contact"];
let fails = 0;

function Option(text, value) { const o = mkEl("option"); o.textContent = text; o.value = value; return o; }

/* 以 agree 控制是否已過首次確認頁；回傳可逐次操作的環境。 */
function boot(agree) {
  const store = {};
  const listeners = {};
  const viewNode = mkEl("main");
  const cache = { "#view": viewNode };
  const doc = {
    createElement: mkEl,
    createTextNode(t) { const n = mkEl("#text"); n._text = String(t); return n; },
    /* 同一選擇器回同一個節點，寫入才留得住（#stripe 的文字就是靠這個驗） */
    querySelector(s) { if (!cache[s]) cache[s] = s === "#view" ? viewNode : mkEl("div"); return cache[s]; },
    querySelectorAll() { return []; },
    getElementById() { return mkEl("div"); },
    body: mkEl("body"),
  };
  const win = {
    document: doc, LS: null, addEventListener(k, f) { (listeners[k] = listeners[k] || []).push(f); },
    location: { hash: "#/idea" }, scrollTo() {}, confirm() { return true; },
    localStorage: { getItem(k) { return store[k] || null; }, setItem(k, v) { store[k] = String(v); } },
  };
  if (agree) store["lingshu.reader.v1"] = JSON.stringify({ agree: 1 });
  const ctx = vm.createContext({ window: win, document: doc, localStorage: win.localStorage,
    location: win.location, confirm: win.confirm, console, Option });
  vm.runInContext(DATA, ctx);
  vm.runInContext(APP, ctx);
  const html = () => walk(viewNode, []).map(n => (n._html || "") + (n._text || "")).join(" ");
  const go = h => { win.location.hash = "#" + h; viewNode._html = ""; viewNode.children = [];
    (listeners.hashchange || []).forEach(f => f()); return html(); };
  const classes = () => walk(viewNode, []).map(n => n.className).filter(Boolean).join(" ").split(/\s+/).filter(Boolean);
  return { ctx, win, viewNode, listeners, html, go, cache, doc, classes };
}

const env = boot(true);
const ctx = env.ctx, win = env.win, viewNode = env.viewNode, listeners = env.listeners;

console.log("視圖檢查：");
const routes = views.concat(["read?seq=40", "items?seq=40", "items?theme=entry",
  "meridian?tab=bie", "meridian?tab=jin", "meridian?tab=luo", "meridian?tab=shui", "meridian?tab=shu"]);
for (const v of routes) {
  const html = env.go("/" + v);
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
const aboutHtml = env.go("/about");
const aboutFails = [];
if (drift.length) aboutFails.push("data.js 與 data/發布資訊.json 不同步：" + drift.join("、"));
if (!aboutHtml.includes(REL["站名"])) aboutFails.push("關於頁沒有站名");
if (REL["授權"] === "待定" && !aboutHtml.includes("待定")) aboutFails.push("授權未定卻未顯示「待定」");
if (REL["授權"] !== "待定" && !aboutHtml.includes(REL["授權"])) aboutFails.push("關於頁沒有顯示已定的授權");
if (REL["聯絡"] === "待補" && !aboutHtml.includes("待補")) aboutFails.push("聯絡未填卻未顯示「待補」");
if (REL["Anki實機"] === "未測" && !aboutHtml.includes("Anki 實機")) aboutFails.push("Anki 未測卻未列為待決");
if (aboutFails.length) { fails++; console.log("  ✗ release " + aboutFails.join("；")); }
else console.log(`  ✓ release  站名=${REL["站名"]} 授權=${REL["授權"]} 聯絡=${REL["聯絡"]}`);

/* 安全提醒：必須出現在頂欄、首次確認頁、首頁、限制頁、關於頁，且措辭不得弱化。
   頂欄是每頁都看得到的唯一位置，因此單獨比對字串相等。 */
const SAFE = REL["安全提醒"] || "";
const SAFE_SHORT = REL["安全提醒短"] || "";
if (!SAFE.includes("帶教資格")) { fails++; console.log("  ✗ safety 安全提醒本體沒有「帶教資格」"); }
const stripeText = (env.cache["#stripe"] || {}).textContent || "";
if (stripeText !== SAFE_SHORT) { fails++; console.log(`  ✗ safety 頂欄未顯示安全提醒短句（現為「${stripeText}」）`); }
const where = { home: env.go("/home"), limits: env.go("/limits"), about: aboutHtml };
const missing = Object.keys(where).filter(k => !where[k].includes(SAFE));
const gateHtml = boot(false).html();
if (!gateHtml.includes(SAFE)) missing.push("gate");
if (!gateHtml.includes("帶教資格")) missing.push("gate按鈕");
if (missing.length) { fails++; console.log("  ✗ safety 未出現安全提醒：" + missing.join("、")); }
else console.log(`  ✓ safety 頂欄／確認頁／首頁／限制頁／關於頁皆顯示：${SAFE.slice(0, 24)}…`);

/* 已下架：索引與覆蓋表（見 docs/119）。若有人把連結加回來，這裡要紅。 */
const REMOVED = ["index", "coverage"];
const back = REMOVED.filter(r => (ctx.window.__ROUTES || []).indexOf(r) >= 0);
if (back.length) { fails++; console.log("  ✗ removed 已下架視圖又出現：" + back.join("、")); }
else console.log("  ✓ removed  索引／覆蓋表已下架（" + (ctx.window.__ROUTES || []).length + " 個視圖）");

/* 樣式類別：h() 的參數順序是 (tag, html, cls)，寫錯會讓 .card/.hero 靜靜失效，
   畫面「變簡陋」卻不報錯。這裡逐視圖點名必要類別。 */
const NEED = {
  "/home": ["hero", "card", "grid", "alert"],
  "/themes": ["card"],
  "/read": ["list", "tiao"],
  "/read?seq=40": ["orig"],
  "/items?seq=40": ["card"],
  "/suwen": ["card", "quote"],
  "/law": ["card", "quote", "law-item"],
  "/binghou": ["card", "quote", "bh-item"],
  "/meridian": ["card", "mer-card", "mer-row"],
  "/meridian?tab=bie": ["card", "mer-card", "mer-row"],
  "/meridian?tab=jin": ["card", "mer-card", "mer-row"],
  "/meridian?tab=luo": ["card"],
  "/meridian?tab=shui": ["card"],
  "/meridian?tab=shu": ["card", "mer-card"],
  "/limits": ["alert"],
  "/contact": ["card", "want-k", "site", "contact-row"],
};
const clsFails = [];
Object.keys(NEED).forEach(r => {
  env.go(r);
  const got = env.classes();
  const miss = NEED[r].filter(c => got.indexOf(c) < 0);
  if (miss.length) clsFails.push(`${r} 缺 .${miss.join(" .")}`);
});
if (clsFails.length) { fails++; console.log("  ✗ classes " + clsFails.join("；")); }
else console.log("  ✓ classes 10 個視圖的必要樣式類別都在");

/* 聯絡頁：五項求助與相關站點必須由 data/聯絡.json 來，且郵箱狀態要與發布資訊一致
   （未填就必須看得到「待補」，不能靜靜留白）。 */
const CONTACT = JSON.parse(fs.readFileSync(path.join(ROOT, "data/聯絡.json"), "utf8"));
const cHtml = env.go("/contact");
const cFails = [];
if ((CONTACT.want || []).length < 3) cFails.push("求助項目少於 3 項");
(CONTACT.want || []).forEach(x => { if (!cHtml.includes(x.k)) cFails.push("缺求助項：" + x.k.slice(0, 8)); });
(CONTACT.sites || []).forEach(x => { if (!cHtml.includes(x.url)) cFails.push("缺站點：" + x.k); });
if (!cHtml.includes(CONTACT.seal)) cFails.push("頁尾沒有安全提醒短句");
if (CONTACT.contact_ready) {
  if (!cHtml.includes(CONTACT.items[0].mail)) cFails.push("郵箱已填卻沒顯示");
  if (cHtml.includes("待補")) cFails.push("郵箱已填卻仍顯示待補");
} else if (!cHtml.includes("待補")) cFails.push("郵箱未填卻沒顯示待補");
if (cFails.length) { fails++; console.log("  ✗ contact " + cFails.join("；")); }
else console.log(`  ✓ contact  求助 ${CONTACT.want.length} 項／站點 ${CONTACT.sites.length} 個／郵箱 ${CONTACT.contact_ready ? "已填" : "待補"}`);

process.exit(fails ? 1 : 0);
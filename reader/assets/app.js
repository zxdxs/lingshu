/* 靈樞自學材料 · 離線閱讀器（零依賴） */
(function () {
"use strict";
var LS = window.LS || {};
var $ = function (s, r) { return (r || document).querySelector(s); };
var view = $('#view');
var KEY = 'lingshu.reader.v1';
var STATE = load();
/* 預覽掛鉤：供截圖與檢查用，不影響正常瀏覽 */
if (window.__PREVIEW__) { STATE.agree = 1; location.hash = '#/' + window.__PREVIEW__; }
function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
function save() { try { localStorage.setItem(KEY, JSON.stringify(STATE)); } catch (e) {} }
function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function md(s) { return esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>'); }
function h(tag, html, cls) { var e = document.createElement(tag); if (cls) e.className = cls; e.innerHTML = html; return e; }
function byId(id) { return document.getElementById(id); }
function stat(k) { return (LS.meta && LS.meta.stats && LS.meta.stats[k]) || 0; }

var NAV = [['idea','理念'],['read','通讀'],['items','題庫'],['index','索引'],['concept','概念圖'],['limits','限制'],['mine','我的'],['about','關於']];
var VIEWS = {};

/* ---------- 理念／入口 ---------- */
VIEWS.idea = function (box) {
  box.appendChild(h('h1', '靈樞自學材料'));
  box.appendChild(h('p', '《黃帝內經·靈樞》八十一篇，整理成可讀、可練、可查，並且知道自己哪裡不可靠的自學材料。', 'small'));
  var c = h('div', '', 'card');
  c.innerHTML = '<h3>三件事，三個入口</h3>' +
    '<table><tr><th style="width:76px">想做的事</th><th>怎麼做</th></tr>' +
    '<tr><td><b>練</b></td><td><a href="#/items">題庫</a>共 ' + stat('items') + ' 題（填空 ' + stat('fill') + '／選擇 ' + stat('mcq') + '／辨誤 ' + stat('err') + '）；也可匯入 <code>export/靈樞_填空.apkg</code> 到 Anki。</td></tr>' +
    '<tr><td><b>讀</b></td><td><a href="#/read">通讀</a> 81 篇原文（含校記）；概念看 <a href="#/concept">概念圖</a>。</td></tr>' +
    '<tr><td><b>查</b></td><td><a href="#/index">索引</a> ' + stat('index') + ' 條名詞 → 篇；或題庫頁篩選。</td></tr></table>';
  box.appendChild(c);
  var w = h('div', '', 'card');
  w.innerHTML = '<h3>開始之前</h3><p>本材料只做《靈樞》，素問僅作對照。所有臨床主張未經驗證，<b>不可據以施治</b>。' +
    '已知限制 ' + stat('limits') + ' 條、矛盾 ' + stat('contradictions') + ' 條，見 <a href="#/limits">限制</a>。</p>';
  box.appendChild(w);
};

/* ---------- 通讀 ---------- */
VIEWS.read = function (box, q) {
  if (q.seq) return readOne(box, q.seq);
  box.appendChild(h('h1', '通讀'));
  var row = h('div', '', 'row');
  var sel = document.createElement('select');
  sel.appendChild(new Option('全部卷', ''));
  (LS.juan || []).forEach(function (j) { sel.appendChild(new Option(j.label + '（' + j.n + ' 篇）', j.no)); });
  var note = el('span', 'small', '');
  row.appendChild(sel); row.appendChild(note);
  box.appendChild(row);
  var list = h('div', 'list');
  box.appendChild(list);
  function render() {
    list.innerHTML = '';
    var jf = sel.value;
    var done = 0, total = 0;
    (LS.pian || []).forEach(function (p) {
      if (jf !== '' && String(p.juan) !== jf) return;
      total++;
      var read = STATE.read && STATE.read[p.seq];
      if (read) done++;
      var a = document.createElement('a');
      a.href = '#/read?seq=' + p.seq; a.textContent = p.seq + '. ' + p.name;
      var d = h('div', '', '');
      d.style.padding = '6px 0';
      d.innerHTML = '<span class="small">' + (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字</span> '
        + (read ? '<span class="tag">已讀</span>' : '') + ' ';
      d.appendChild(a);
      list.appendChild(d);
    });
    note.textContent = '已讀 ' + done + ' / ' + total;
  }
  sel.onchange = render; render();
};
function readOne(box, seq) {
  var p = (LS.pian || []).filter(function (x) { return String(x.seq) === String(seq); })[0];
  if (!p) { box.appendChild(h('p', '本篇不存在。')); return; }
  box.appendChild(h('h1', p.name));
  box.appendChild(h('p', (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字', 'small'));
  var row = h('div', '', 'row');
  var b = el('button', 'btn', '標為已讀'); b.type = 'button';
  var b2 = el('button', 'btn ghost', '返回'); b2.type = 'button';
  b.onclick = function () { STATE.read = STATE.read || {}; STATE.read[p.seq] = 1; save(); b.textContent = '已讀 ✓'; };
  b2.onclick = function () { location.hash = '#/read'; };
  row.appendChild(b); row.appendChild(b2); box.appendChild(row);
  var t = h('div', 'text');
  p.text.split('\n').forEach(function (line) {
    if (line.trim()) t.appendChild(h('p', esc(line)));
  });
  box.appendChild(t);
  if (p.note) {
    box.appendChild(h('h3', '校記'));
    box.appendChild(h('p', esc(p.note), 'small'));
  }
}

/* ---------- 題庫 ---------- */
VIEWS.items = function (box, q) {
  box.appendChild(h('h1', '題庫'));
  var row = h('div', '', 'row');
  var f1 = document.createElement('select');
  [['', '全部題型'], ['fill_blank', '填空'], ['mcq', '選擇'], ['error_identification', '辨誤']].forEach(function (x) { f1.appendChild(new Option(x[1], x[0])); });
  var f2 = document.createElement('select');
  f2.appendChild(new Option('全部篇', ''));
  (LS.pian || []).forEach(function (p) { f2.appendChild(new Option(p.seq + '. ' + p.name, p.seq)); });
  var f3 = document.createElement('select');
  [['', '全部狀態'], ['case', '案例題'], ['todo', '未作答'], ['wrong', '曾答錯']].forEach(function (x) { f3.appendChild(new Option(x[1], x[0])); });
  var cnt = el('span', 'small', '');
  row.appendChild(f1); row.appendChild(f2); row.appendChild(f3); row.appendChild(cnt);
  box.appendChild(row);
  var list = h('div', '');
  box.appendChild(list);
  var shown = 0;
  function render() {
    list.innerHTML = ''; shown = 0;
    var log = STATE.log || {};
    (LS.items || []).forEach(function (it) {
      if (f1.value && it.type !== f1.value) return;
      if (f2.value && String(it.seq) !== f2.value) return;
      if (f3.value === 'case' && !it.case) return;
      if (f3.value === 'todo' && log[it.id]) return;
      if (f3.value === 'wrong' && log[it.id] !== 'no') return;
      if (shown++ >= 20) return;
      list.appendChild(itemCard(it));
    });
    cnt.textContent = '顯示 ' + Math.min(shown, 21) + (shown > 21 ? '+' : '') + ' 題（可用上方篩選縮小範圍）';
  }
  f1.onchange = f2.onchange = f3.onchange = render; render();
};
function itemCard(it) {
  var c = h('div', '', 'card');
  c.innerHTML = '<div>' + md(it.stem) + '</div>';
  var row = h('div', '', 'row');
  var b = el('button', 'btn ghost', '顯示答案'); b.type = 'button';
  var r1 = el('button', 'btn', '答對'); r1.type = 'button';
  var r2 = el('button', 'btn ghost', '答錯'); r2.type = 'button';
  var a = h('div', 'ans', '');
  a.style.display = 'none';
  a.innerHTML = '<b>' + esc(it.answer) + '</b>' +
    (it.acc && it.acc.length ? ' <span class="small">（亦可：' + esc(it.acc.join('、')) + '）</span>' : '') +
    (it.kind ? ' <span class="tag">' + esc(it.kind) + '</span>' : '') +
    (it.case ? ' <span class="tag">案例題</span>' : '') +
    (it.note ? '<div class="small">' + md(it.note) + '</div>' : '') +
    '<div class="small">《靈樞·' + esc(it.pian) + '》</div>';
  b.onclick = function () { a.style.display = a.style.display === 'none' ? '' : 'none'; };
  function log(k) { STATE.log = STATE.log || {}; STATE.log[it.id] = k; save(); r1.textContent = '答對'; r2.textContent = '答錯'; (k === 'ok' ? r1 : r2).textContent += ' ✓'; }
  r1.onclick = function () { log('ok'); };
  r2.onclick = function () { log('no'); };
  row.appendChild(b); row.appendChild(r1); row.appendChild(r2);
  c.appendChild(row); c.appendChild(a);
  return c;
}

/* ---------- 索引 ---------- */
VIEWS.index = function (box) {
  box.appendChild(h('h1', '索引'));
  var row = h('div', '', 'row');
  var inp = document.createElement('input'); inp.type = 'search'; inp.placeholder = '查名詞、篇名…'; inp.style.minWidth = '240px';
  var cnt = el('span', 'small', '');
  row.appendChild(inp); row.appendChild(cnt); box.appendChild(row);
  var out = h('div', 'list'); box.appendChild(out);
  function render() {
    var q = inp.value.trim();
    out.innerHTML = '';
    var n = 0;
    (LS.index || []).forEach(function (r) {
      var hay = (r.n || '') + ' ' + (r.pian || '') + ' ' + (r.c || '');
      if (q && hay.indexOf(q) < 0) return;
      if (n++ >= 30) return;
      var d = h('div', '', '');
      d.style.padding = '5px 0';
      d.innerHTML = '<span class="small">' + esc(r.c) + '</span> ' + esc(r.n) +
        ' <span class="small">→ ' + esc(r.pian) + (r.pos ? '（' + esc(r.pos) + '）' : '') + '</span>';
      out.appendChild(d);
    });
    cnt.textContent = '顯示 ' + Math.min(n, 31) + (n > 31 ? '+' : '');
  }
  inp.oninput = render; render();
};

/* ---------- 概念圖 ---------- */
var PNG = [['血','多層_血'],['虛實','多層_虛實'],['形','多層_形'],['精','多層_精'],['津液','多層_津液'],['邪','多層_邪'],['營衛','多層_營衛'],['藏府','多層_藏府'],['三焦','多層_三焦'],['清濁','多層_清濁'],['血絡','多層_血絡'],['標本','多層_標本']];
VIEWS.concept = function (box) {
  box.appendChild(h('h1', '概念圖'));
  box.appendChild(h('p', '同一個詞在《靈樞》裡有幾層意思。點開可看大圖；文字說明在各 docs 專篇。', 'small'));
  var g = h('div', 'gal');
  PNG.forEach(function (x) {
    var c = h('div', '', '');
    c.innerHTML = '<a href="../export/' + x[1] + '.png" target="_blank"><img src="../export/' + x[1] + '.png" alt="' + esc(x[0]) + '"></a>' +
      '<div class="small">' + esc(x[0]) + '</div>';
    g.appendChild(c);
  });
  box.appendChild(g);
};

/* ---------- 限制 ---------- */
VIEWS.limits = function (box) {
  box.appendChild(h('h1', '已知限制'));
  box.appendChild(h('p', '先說不能做什麼。完整清單見 data/能力邊界.csv。', 'small'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:56px">#</th><th>問題</th><th style="width:64px">範疇</th><th style="width:44px">級</th></tr>';
  (LS.limits || []).forEach(function (r) {
    t.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.issue) + '</td><td>' + esc(r.cat) + '</td><td>' + esc(r.sev) + '</td></tr>';
  });
  box.appendChild(t);
  box.appendChild(h('h3', '矛盾'));
  var t2 = h('table', '');
  t2.innerHTML = '<tr><th style="width:56px">#</th><th>爭點</th><th style="width:80px">判定</th></tr>';
  (LS.contradictions || []).forEach(function (r) {
    t2.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.point) + '</td><td>' + esc(r.verdict) + '</td></tr>';
  });
  box.appendChild(t2);
};

/* ---------- 我的 ---------- */
VIEWS.mine = function (box) {
  box.appendChild(h('h1', '我的'));
  var read = Object.keys(STATE.read || {}).length;
  var log = STATE.log || {};
  var ok = Object.keys(log).filter(function (k) { return log[k] === 'ok'; }).length;
  var no = Object.keys(log).filter(function (k) { return log[k] === 'no'; }).length;
  box.appendChild(h('p', '已讀 ' + read + ' / ' + (LS.pian || []).length + ' 篇　·　作答 ' + (ok + no) + ' 題（對 ' + ok + '／錯 ' + no + '）'));
  var b = el('button', 'btn ghost', '清除本機進度'); b.type = 'button';
  b.onclick = function () {
    if (!confirm('清除已讀與作答紀錄？')) return;
    STATE.read = {}; STATE.log = {}; save(); route();
  };
  box.appendChild(b);
  box.appendChild(h('p', '進度只存在這個瀏覽器（localStorage），不上傳。', 'small'));
};

/* ---------- 關於 ---------- */
VIEWS.about = function (box) {
  var s = LS.meta.stats;
  box.appendChild(h('h1', '關於'));
  box.appendChild(h('p', LS.meta.bendi, 'small'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:120px">項目</th><th>內容</th></tr>' +
    '<tr><td>規模</td><td>81 篇、經文 ' + s.chars.toLocaleString() + ' 字、題庫 ' + s.items + ' 題</td></tr>' +
    '<tr><td>引文驗證</td><td>題面引文逐字比對；不符 0</td></tr>' +
    '<tr><td>答案類型</td><td>原文 669／推算 24／整理語 15（已標明）</td></tr>' +
    '<tr><td>註家</td><td>《類經》張介賓注為主；19 條配對待專家核</td></tr>' +
    '<tr><td>授權</td><td><b>待定</b>（見 CHANGELOG；目前僅供審閱）</td></tr>' +
    '<tr><td>聯絡</td><td>待補（發布前填入）</td></tr>';
  box.appendChild(t);
  box.appendChild(h('p', LS.meta.warn, 'small'));
};

/* ---------- 路由 ---------- */
function parseHash() {
  var hh = location.hash.replace(/^#\/?/, '');
  var parts = hh.split('?');
  var name = parts[0] || 'idea';
  var q = {};
  (parts[1] || '').split('&').forEach(function (kv) {
    if (!kv) return; var a = kv.split('='); q[decodeURIComponent(a[0])] = decodeURIComponent(a[1] || '');
  });
  return { name: name, q: q };
}
function route() {
  var r = parseHash();
  var v = VIEWS[r.name] || VIEWS.idea;
  view.innerHTML = '';
  v(view, r.q);
  document.querySelectorAll('#nav a').forEach(function (a) {
    a.className = a.getAttribute('data-k') === r.name ? 'on' : '';
  });
  window.scrollTo(0, 0);
}
function bootNav() {
  var nav = byId('nav');
  NAV.forEach(function (x) {
    var a = document.createElement('a');
    a.href = '#/' + x[0]; a.textContent = x[1]; a.setAttribute('data-k', x[0]);
    nav.appendChild(a);
  });
  byId('stripe').textContent = LS.meta.warn;
  byId('footLinks').innerHTML = '<a href="#/limits">限制</a><a href="#/about">關於</a><a href="#/items">題庫</a><a href="#/read">通讀</a>';
}
bootNav();
window.addEventListener('hashchange', route);

/* 首次進入確認 */
if (!STATE.agree) {
  view.innerHTML = '';
  var g = h('div', 'gate');
  g.innerHTML = '<h2>使用前確認</h2><p>本材料是讀書與練習工具，不是診療工具。所有臨床主張未經驗證，<b>不可據以施治</b>。' +
    '<br>原文與題目皆經機器逐字比對；標「待專家核」者，臨床判斷僅供參考。</p>';
  var ok = el('button', 'btn', '我了解，開始'); ok.type = 'button';
  ok.onclick = function () { STATE.agree = 1; save(); route(); };
  g.appendChild(ok); view.appendChild(g);
} else {
  route();
}
})();

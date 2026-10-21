/* 靈樞自學材料 · 離線閱讀器（零依賴） */
(function () {
"use strict";
var LS = window.LS || {};
var KEY = 'lingshu.reader.v1';
var STATE = load();
if (window.__PREVIEW__) { STATE.agree = 1; location.hash = '#/' + window.__PREVIEW__; }
function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
function save() { try { localStorage.setItem(KEY, JSON.stringify(STATE)); } catch (e) {} }
function $(s, r) { return (r || document).querySelector(s); }
function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
function h(tag, html, cls) { var e = document.createElement(tag); if (cls) e.className = cls; e.innerHTML = html; return e; }
function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function md(s) { return esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>'); }
function stat(k) { return (LS.meta && LS.meta.stats && LS.meta.stats[k]) || 0; }
function pct(a, b) { return b ? Math.round(a / b * 100) : 0; }
function bar(a, b) { return '<div class="bar"><i style="width:' + pct(a, b) + '%"></i></div>'; }
function bySeq(seq) { return (LS.pian || []).filter(function (p) { return String(p.seq) === String(seq); })[0]; }
function hash(s) { var x = 0; for (var i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) >>> 0; return x; }

var NAV = [['home','首頁'],['read','通讀'],['items','題庫'],['concept','概念'],['index','索引'],
           ['coverage','覆蓋'],['prep','準備'],['method','方法'],['collation','校勘'],['limits','限制'],
           ['mine','我的'],['about','關於']];
var VIEWS = {};

/* ---------------- 首頁 ---------------- */
VIEWS.home = function (box) {
  var hero = h('div', 'hero', '');
  hero.innerHTML =
    '<div class="kicker">黃帝內經 · 靈樞 · 八十一篇</div>' +
    '<h1>靈樞</h1>' +
    '<p class="lead">把《靈樞》讀成<b>可以驗收的判斷力</b>：81 篇原文、' + stat('items') + ' 道題，' +
    '每一句都能回到底本，每一條限制都寫在站上。</p>' +
    '<div class="row" style="margin-top:14px">' +
      '<a class="btn" href="#/read">入口 01 · 讀原文</a>' +
      '<a class="btn ghost" href="#/items">入口 02 · 練題</a>' +
      '<a class="btn ghost" href="#/concept">入口 03 · 查概念</a>' +
    '</div>' +
    '<div class="stats" style="margin-top:18px">' +
      '<div class="stat"><b>' + stat('pian') + '</b><span>篇</span></div>' +
      '<div class="stat"><b>' + stat('chars').toLocaleString() + '</b><span>經文字</span></div>' +
      '<div class="stat"><b>' + stat('items') + '</b><span>題</span></div>' +
      '<div class="stat"><b>' + stat('quote_seg') + '</b><span>逐字核過的引文段</span></div>' +
    '</div>';
  box.appendChild(hero);

  var g = h('div', 'grid');
  [['目的','讓原文可讀、可練、可查','讀得進去，也練得出來；不以「看懂了」當作學會。'],
   ['價值','把可驗的部分公開','引文逐字比對、答案分型、模組原文、限制與矛盾——全部可查。'],
   ['為什麼現在做','市面上的靈樞多止於導讀','練習紀錄與校勘痕跡很少公開；這份材料把兩者一起留下。']].forEach(function (x) {
    var c = h('div', 'card', '');
    c.innerHTML = '<h3>' + x[0] + '</h3><p class="small muted">' + x[1] + '</p><p>' + x[2] + '</p>';
    g.appendChild(c);
  });
  box.appendChild(g);

  box.appendChild(h('h2', '訓練怎麼進行'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:86px">入口</th><th>要做的事</th><th style="width:150px">產出物（不留下＝沒做）</th></tr>' +
    '<tr><td>讀</td><td>通讀一篇，遇校記停下來看</td><td>標為已讀（本機記錄）</td></tr>' +
    '<tr><td>練</td><td>作答並看解析與出處</td><td>對錯紀錄；' + stat('items') + ' 題可追</td></tr>' +
    '<tr><td>查</td><td>用索引或概念卡回查</td><td>找到篇、句與出處</td></tr>';
  box.appendChild(t);
  box.appendChild(h('p', '表 首頁-1　三個入口與各自的產出物。數字取自 data/題庫_示例.json 與底本。', 'small muted'));

  box.appendChild(h('h3', '驗收四層'));
  var t2 = h('table', '');
  t2.innerHTML = '<tr><th style="width:86px">層</th><th>標準</th><th style="width:130px">本站對應</th></tr>' +
    '<tr><td>應知</td><td>能正確複述原文</td><td>填空題（答案類型：原文）</td></tr>' +
    '<tr><td>應會</td><td>標準情境做得出</td><td>選擇題、辨誤題</td></tr>' +
    '<tr><td>理解</td><td>能解釋、能分層</td><td>概念卡（12 個，逐層原文）</td></tr>' +
    '<tr><td>遷移</td><td>新情境自動運用</td><td>案例題（6 道，待專家核）</td></tr>';
  box.appendChild(t2);

  var no = h('div', 'card', '');
  no.innerHTML = '<h3>本站不做什麼</h3><ul class="small" style="margin:.4em 0 0 1.1em;padding:0">' +
    '<li>不替代臨床判斷：所有臨床主張未經驗證，<b>不可據以施治</b>。</li>' +
    '<li>不把素問納入主體：只在對照時引用。</li>' +
    '<li>不生成原文：L0 一律取自底本，每句可回查。</li>' +
    '<li>不掩蓋不確定：限制 ' + stat('limits') + ' 條、矛盾 ' + stat('contradictions') + ' 條公開列出。</li></ul>' +
    '<p class="small" style="margin-top:10px"><a href="#/limits">看已知限制</a>　·　<a href="#/method">看校勘與矛盾</a>　·　<a href="#/about">看授權與出處</a></p>';
  box.appendChild(no);
};

/* ---------------- 通讀 ---------------- */
VIEWS.read = function (box, q) {
  if (q.seq) return readOne(box, q.seq);
  box.appendChild(h('h1', '通讀'));
  var row = h('div', 'row');
  var sel = document.createElement('select');
  sel.appendChild(new Option('全部卷', ''));
  (LS.juan || []).forEach(function (j) { sel.appendChild(new Option(j.label + '（' + j.n + ' 篇）', j.no)); });
  var inp = document.createElement('input'); inp.type = 'search'; inp.placeholder = '搜篇名…';
  var note = el('span', 'small muted', '');
  row.appendChild(sel); row.appendChild(inp); row.appendChild(note);
  box.appendChild(row);
  var pb = h('div', ''); box.appendChild(pb);
  var list = h('div', 'list'); box.appendChild(list);
  function render() {
    list.innerHTML = '';
    var jf = sel.value, kw = inp.value.trim(), done = 0, total = 0;
    (LS.pian || []).forEach(function (p) {
      if (jf !== '' && String(p.juan) !== jf) return;
      if (kw && p.name.indexOf(kw) < 0) return;
      total++;
      var read = STATE.read && STATE.read[p.seq];
      if (read) done++;
      var d = h('div', 'tiao', '');
      d.innerHTML = '<span class="no">' + p.seq + '</span>' +
        '<a href="#/read?seq=' + p.seq + '">' + esc(p.name) + '</a>' +
        ' <span class="small muted">' + (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字 · ' + (p.items || 0) + ' 題</span>' +
        (read ? ' <span class="pill g">已讀</span>' : '');
      list.appendChild(d);
    });
    var all = Object.keys(STATE.read || {}).length;
    pb.innerHTML = bar(all, (LS.pian || []).length) + '<div class="small muted">全書已讀 ' + all + '/' + (LS.pian || []).length + '　·　本次顯示 ' + total + ' 篇</div>';
  }
  sel.onchange = render; inp.oninput = render; render();
};
function readOne(box, seq) {
  var p = bySeq(seq);
  if (!p) { box.appendChild(h('p', '本篇不存在。')); return; }
  box.appendChild(h('h1', p.name));
  box.appendChild(h('p', (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字 · ' + (p.items || 0) + ' 題', 'small muted'));
  var row = h('div', 'row');
  var b = el('button', 'btn', STATE.read && STATE.read[p.seq] ? '已讀 ✓' : '標為已讀'); b.type = 'button';
  var b2 = el('button', 'btn ghost', '← 回通讀'); b2.type = 'button';
  var b3 = el('a', 'btn ghost', '看本篇題目'); b3.href = '#/items?seq=' + p.seq;
  b.onclick = function () { STATE.read = STATE.read || {}; STATE.read[p.seq] = 1; save(); b.textContent = '已讀 ✓'; };
  b2.onclick = function () { location.hash = '#/read'; };
  row.appendChild(b); row.appendChild(b2); row.appendChild(b3);
  box.appendChild(row);
  var t = h('div', 'orig');
  p.text.split('\n').forEach(function (line, dn) {
    if (!line.trim()) return;
    var para = document.createElement('p');
    var parts = line.split(/(?<=[。！？])/);
    parts.forEach(function (sent, jn) {
      if (!sent) return;
      var sp = document.createElement('span');
      sp.className = 'sent';
      sp.appendChild(document.createTextNode(sent));
      var sid = document.createElement('i');
      sid.className = 'sid';
      sid.textContent = p.seq + '-' + (dn + 1) + '-' + (jn + 1);
      sp.appendChild(sid);
      para.appendChild(sp);
    });
    t.appendChild(para);
  });
  box.appendChild(t);
  var tg = el('button', 'btn ghost', '顯示句號'); tg.type = 'button';
  tg.onclick = function () {
    document.body.classList.toggle('show-sid');
    tg.textContent = document.body.classList.contains('show-sid') ? '隱藏句號' : '顯示句號';
  };
  row.appendChild(tg);
  if (p.note) {
    box.appendChild(h('h3', '校記'));
    box.appendChild(h('p', esc(p.note), 'small'));
  }
  var yin = (LS.yinshi || []).filter(function (y) { return String(y.juan).replace(/^0+/, '') === String(p.juan); })[0];
  if (yin) {
    box.appendChild(h('h3', '音釋'));
    box.appendChild(h('p', esc(yin.text) + '…', 'small'));
  }
}

/* ---------------- 題庫 ---------------- */
VIEWS.items = function (box, q) {
  box.appendChild(h('h1', '題庫'));
  var log = STATE.log || {};
  var attempts = Object.keys(log).length;
  var ok = Object.keys(log).filter(function (k) { return log[k] === 'ok'; }).length;
  box.appendChild(h('div', '', ''));
  var head = h('div', 'card', '');
  head.innerHTML = bar(attempts, stat('items')) +
    '<div class="small muted">已作答 ' + attempts + ' / ' + stat('items') + '　·　答對 ' + ok +
    '（' + pct(ok, attempts) + '%）</div>';
  box.appendChild(head);

  var row = h('div', 'row');
  var f1 = document.createElement('select');
  [['', '全部題型'], ['fill_blank', '填空'], ['mcq', '選擇'], ['error_identification', '辨誤']].forEach(function (x) { f1.appendChild(new Option(x[1], x[0])); });
  var f2 = document.createElement('select');
  f2.appendChild(new Option('全部篇', ''));
  (LS.pian || []).forEach(function (p) { f2.appendChild(new Option(p.seq + '. ' + p.name, p.seq)); });
  if (q.seq) f2.value = q.seq;
  var f3 = document.createElement('select');
  [['', '全部狀態'], ['case', '案例題'], ['todo', '未作答'], ['wrong', '曾答錯']].forEach(function (x) { f3.appendChild(new Option(x[1], x[0])); });
  var cnt = el('span', 'small muted', '');
  row.appendChild(f1); row.appendChild(f2); row.appendChild(f3); row.appendChild(cnt);
  box.appendChild(row);
  var list = h('div', ''); box.appendChild(list);

  function render() {
    list.innerHTML = '';
    var shown = 0;
    (LS.items || []).forEach(function (it) {
      if (f1.value && it.type !== f1.value) return;
      if (f2.value && String(it.seq) !== f2.value) return;
      if (f3.value === 'case' && !it.case) return;
      if (f3.value === 'todo' && log[it.id]) return;
      if (f3.value === 'wrong' && log[it.id] !== 'no') return;
      if (shown >= 20) return;
      shown++;
      list.appendChild(itemCard(it));
    });
    cnt.textContent = '顯示 ' + shown + ' 題' + (shown >= 20 ? '（請用篩選縮小）' : '');
  }
  f1.onchange = f2.onchange = f3.onchange = render; render();
};
function itemCard(it) {
  var c = h('div', 'card', '');
  var head = h('div', '');
  head.innerHTML = '<span class="pill b">' + esc(it.pian) + '</span>' +
    '<span class="pill">' + ({ fill_blank: '填空', mcq: '選擇', error_identification: '辨誤' }[it.type] || it.type) + '</span>' +
    (it.case ? '<span class="pill y">案例題</span>' : '') +
    (it.level ? '<span class="pill">' + esc(it.level) + '</span>' : '');
  c.appendChild(head);
  c.appendChild(h('div', 'q', md(it.stem)));

  if (it.type === 'mcq' || it.case) {
    var opts = [it.answer].concat(it.dis || []);
    var seed = hash(it.id);
    opts.sort(function (a, b) { return (hash(a + seed) % 97) - (hash(b + seed) % 97); });
    var ans = el('div', 'ans', ''); ans.style.display = 'none';
    ans.innerHTML = '<b>正解：' + esc(it.answer) + '</b>' +
      (it.note ? '<div class="small">' + md(it.note) + '</div>' : '');
    opts.forEach(function (o) {
      var b = el('button', 'opt', o); b.type = 'button';
      b.onclick = function () {
        var right = o === it.answer;
        b.className = 'opt ' + (right ? 'right' : 'wrong');
        Array.prototype.forEach.call(c.querySelectorAll('.opt'), function (x) { x.disabled = true; });
        ans.style.display = '';
        log2(it.id, right);
      };
      c.appendChild(b);
    });
    c.appendChild(ans);
  } else {
    var row = h('div', 'row');
    var b = el('button', 'btn ghost', '顯示答案'); b.type = 'button';
    var r1 = el('button', 'btn', '答對'); r1.type = 'button';
    var r2 = el('button', 'btn ghost', '答錯'); r2.type = 'button';
    var a = h('div', 'ans', '');
    a.style.display = 'none';
    a.innerHTML = '<b>' + esc(it.answer) + '</b>' +
      (it.acc && it.acc.length ? ' <span class="small muted">（亦可：' + esc(it.acc.join('、')) + '）</span>' : '') +
      (it.kind ? ' <span class="pill">' + esc(it.kind) + '</span>' : '') +
      (it.note ? '<div class="small">' + md(it.note) + '</div>' : '') +
      '<div class="small">《靈樞·' + esc(it.pian) + '》' + (it.sid ? ' · 句 ' + esc(it.sid) : '') + '</div>';
    b.onclick = function () { a.style.display = a.style.display === 'none' ? '' : 'none'; };
    r1.onclick = function () { log2(it.id, true); r1.textContent = '答對 ✓'; };
    r2.onclick = function () { log2(it.id, false); r2.textContent = '答錯 ✓'; };
    row.appendChild(b); row.appendChild(r1); row.appendChild(r2);
    c.appendChild(row); c.appendChild(a);
  }
  return c;
}
function log2(id, ok) { STATE.log = STATE.log || {}; STATE.log[id] = ok ? 'ok' : 'no'; save(); }

/* ---------------- 概念 ---------------- */
VIEWS.concept = function (box) {
  box.appendChild(h('h1', '概念'));
  box.appendChild(h('p', '同一個詞在《靈樞》裡有幾層意思。每張卡列出各層原文與出處；圖是輔助。', 'small muted'));
  var g = h('div', '');
  (LS.concepts || []).forEach(function (c) {
    var card = document.createElement('details');
    card.className = 'card';
    var rows = (c.layers || []).map(function (L) {
      return '<tr><td style="width:84px">' + esc(L.ctx) + '</td><td>' + esc(L.txt) + '</td><td style="width:88px">' + esc(L.src) + '</td></tr>';
    }).join('');
    card.innerHTML = '<summary><b>' + esc(c.w || c.t) + '</b>　<span class="small muted">' +
      (c.layers || []).length + ' 層</span></summary>' +
      '<p class="small muted">' + esc(c.s) + '</p><p>' + esc(c.note) + '</p>' +
      '<table><tr><th>層</th><th>原文</th><th>出處</th></tr>' + rows + '</table>' +
      '<a class="small" href="../export/' + esc(c.png) + '" target="_blank">看圖 →</a>';
    g.appendChild(card);
  });
  box.appendChild(g);
};

/* ---------------- 索引 ---------------- */
VIEWS.index = function (box) {
  box.appendChild(h('h1', '索引'));
  var cats = {};
  (LS.index || []).forEach(function (r) { cats[r.c] = 1; });
  var row = h('div', 'row');
  var inp = document.createElement('input'); inp.type = 'search'; inp.placeholder = '查名詞、篇名…'; inp.style.minWidth = '240px';
  var sel = document.createElement('select');
  sel.appendChild(new Option('全部類別', ''));
  Object.keys(cats).forEach(function (k) { sel.appendChild(new Option(k, k)); });
  var cnt = el('span', 'small muted', '');
  row.appendChild(inp); row.appendChild(sel); row.appendChild(cnt); box.appendChild(row);
  var out = h('div', ''); box.appendChild(out);
  function render() {
    var q = inp.value.trim(), cf = sel.value;
    out.innerHTML = '';
    var n = 0;
    var tb = h('table', '');
    tb.innerHTML = '<tr><th style="width:70px">類</th><th>名</th><th style="width:120px">篇</th><th style="width:90px">位置</th></tr>';
    (LS.index || []).forEach(function (r) {
      if (cf && r.c !== cf) return;
      var hay = (r.n || '') + ' ' + (r.pian || '');
      if (q && hay.indexOf(q) < 0) return;
      if (n++ >= 80) return;
      tb.innerHTML += '<tr><td>' + esc(r.c) + '</td><td>' + esc(r.n) + '</td><td>' + esc(r.pian) + '</td><td>' + esc(r.pos) + '</td></tr>';
    });
    out.appendChild(tb);
    cnt.textContent = '顯示 ' + Math.min(n, 80) + ' 條';
  }
  inp.oninput = render; sel.onchange = render; render();
};

/* ---------------- 準備 ---------------- */
VIEWS.prep = function (box) {
  box.appendChild(h('h1', '準備'));
  box.appendChild(h('p', '讀之前先補三樣：九鍼、音釋、度量。這三樣不懂，後面會一直卡。', 'small muted'));
  box.appendChild(h('h2', '九鍼'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:56px">序</th><th style="width:76px">鍼</th><th style="width:80px">長</th><th>用途</th></tr>';
  (LS.needles || []).forEach(function (n) {
    t.innerHTML += '<tr><td>' + esc(n.no) + '</td><td>' + esc(n.name) + '</td><td>' + esc(n.len) + '</td><td>' + esc(n.use) + '</td></tr>';
  });
  box.appendChild(t);
  box.appendChild(h('p', '出處：〈九鍼十二原〉與〈九鍼論〉；兩篇毫鍼長度不同，見方法頁。', 'small muted'));

  box.appendChild(h('h2', '音釋'));
  box.appendChild(h('p', '史崧音釋（底本卷末），按卷排列；只節錄前 220 字。', 'small muted'));
  var y = h('div', '');
  (LS.yinshi || []).slice(0, 12).forEach(function (r) {
    y.appendChild(h('div', 'card', '<h3>卷 ' + esc(String(r.juan).replace(/^0+/, '')) + '</h3><p class="small">' + esc(r.text) + '…</p>'));
  });
  box.appendChild(y);
};

/* ---------------- 方法 ---------------- */
VIEWS.method = function (box) {
  box.appendChild(h('h1', '方法與校勘'));
  box.appendChild(h('p', '這一頁回答「這本書可不可信」。完整方法見 docs/01、33、82、88。', 'small muted'));
  var c = h('div', 'card', '');
  c.innerHTML = '<h3>校勘（' + (LS.collation || []).length + ' 點）</h3>' +
    '<p class="small">三源並排（底本／太素／類經）與覆蓋率另成一頁。</p>' +
    '<a class="btn ghost" href="#/collation">看三源並排 →</a>';
  box.appendChild(c);
  box.appendChild(h('h2', '矛盾（' + (LS.contradictions || []).length + '）'));
  var t2 = h('table', '');
  t2.innerHTML = '<tr><th style="width:48px">#</th><th>爭點</th><th style="width:80px">判定</th></tr>';
  (LS.contradictions || []).forEach(function (r) {
    t2.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.point) + '</td><td>' + esc(r.verdict) + '</td></tr>';
  });
  box.appendChild(t2);
};

/* ---------------- 覆蓋 ---------------- */
VIEWS.coverage = function (box) {
  box.appendChild(h('h1', '覆蓋表'));
  box.appendChild(h('p', '81 篇 × 字數 × 題數 × 已讀 × 正確率。聲韻站用 376 章分工表推進度；這裡用同一種表看自己讀到哪。', 'small muted'));
  var log = STATE.log || {}, idx = {};
  (LS.items || []).forEach(function (i) { idx[i.id] = i; });
  var per = {};
  Object.keys(log).forEach(function (id) {
    var it = idx[id]; if (!it) return;
    var k = per[it.seq] = per[it.seq] || [0, 0];
    k[1]++; if (log[id] === 'ok') k[0]++;
  });
  var row = h('div', 'row');
  var sel = document.createElement('select');
  [['', '全部篇'], ['todo', '未讀'], ['thin', '題少（≤6）'], ['wrong', '曾答錯']].forEach(function (x) { sel.appendChild(new Option(x[1], x[0])); });
  var note = el('span', 'small muted', '');
  row.appendChild(sel); row.appendChild(note); box.appendChild(row);
  var out = h('div', ''); box.appendChild(out);
  function render() {
    out.innerHTML = '';
    var t = h('table', '');
    t.innerHTML = '<tr><th style="width:52px">#</th><th>篇</th><th style="width:70px">字數</th>' +
      '<th style="width:52px">題</th><th style="width:52px">已讀</th><th style="width:64px">作答</th><th style="width:64px">正確率</th></tr>';
    var n = 0, items = 0, read = 0;
    (LS.pian || []).forEach(function (p) {
      var rd = STATE.read && STATE.read[p.seq];
      var st = per[p.seq] || [0, 0];
      if (sel.value === 'todo' && rd) return;
      if (sel.value === 'thin' && (p.items || 0) > 6) return;
      if (sel.value === 'wrong' && !(st[1] > st[0])) return;
      n++; items += p.items || 0; if (rd) read++;
      t.innerHTML += '<tr><td>' + p.seq + '</td><td><a href="#/read?seq=' + p.seq + '">' + esc(p.name) + '</a></td>' +
        '<td class="num">' + p.chars + '</td><td class="num">' + (p.items || 0) + '</td>' +
        '<td>' + (rd ? '<span class="pill g">已讀</span>' : '<span class="small muted">—</span>') + '</td>' +
        '<td class="num">' + st[1] + '</td><td class="num">' + (st[1] ? pct(st[0], st[1]) + '%' : '—') + '</td></tr>';
    });
    out.appendChild(t);
    note.textContent = '顯示 ' + n + ' 篇　·　題 ' + items + '　·　已讀 ' + read;
  }
  sel.onchange = render; render();

  var det = document.createElement('details');
  det.className = 'card';
  var t2 = h('table', '');
  t2.innerHTML = '<tr><th style="width:52px">#</th><th>篇</th><th style="width:120px">太素 K4/K12</th><th style="width:120px">類經 K4/K12</th><th style="width:140px">判讀</th></tr>';
  (LS.coverage || []).forEach(function (r) {
    t2.innerHTML += '<tr><td>' + esc(r.seq) + '</td><td class="small">' + esc(r.pian) + '</td>' +
      '<td class="num small">' + (r.t4 == null ? '—' : r.t4 + ' / ' + r.t12) + '</td>' +
      '<td class="num small">' + (r.l4 == null ? '—' : r.l4 + ' / ' + r.l12) + '</td>' +
      '<td class="small">' + esc(r.verdict || '') + '</td></tr>';
  });
  det.innerHTML = '<summary><b>三源覆蓋率</b>　<span class="small muted">81 篇；K4／K12 為 4-gram／12-gram 重合率</span></summary>';
  det.appendChild(t2);
  box.appendChild(det);
};

/* ---------------- 校勘 ---------------- */
VIEWS.collation = function (box) {
  box.appendChild(h('h1', '校勘：三源並排'));
  box.appendChild(h('p', '左為底本（SBCK），中為《太素》，右為《類經》。「—」表示該源無此句或未收此篇。', 'small muted'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:44px">#</th><th style="width:96px">篇</th><th>底本</th><th>太素</th><th>類經</th><th style="width:70px">判定</th></tr>';
  (LS.collation || []).forEach(function (r) {
    t.innerHTML += '<tr><td>' + esc(r.id) + (r.sid ? '<br><span class="muted">' + esc(r.sid) + '</span>' : '') +
      '</td><td class="small">' + esc(r.pian) + '<br><span class="muted">' + esc(r.anchor || '') + '</span></td>' +
      '<td class="small">' + esc(r.base || '') + '</td>' +
      '<td class="small">' + esc(r.taisu || '—') + '</td>' +
      '<td class="small">' + esc(r.leijing || '—') + '</td>' +
      '<td class="small">' + esc((r.verdict || '').slice(0, 14)) + '</td></tr>';
  });
  box.appendChild(t);
};

/* ---------------- 限制 ---------------- */
VIEWS.limits = function (box) {
  box.appendChild(h('h1', '已知限制'));
  box.appendChild(h('p', '先說不能做什麼。完整清單見 data/能力邊界.csv。', 'small muted'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:52px">#</th><th>問題</th><th style="width:70px">範疇</th><th style="width:44px">級</th></tr>';
  (LS.limits || []).forEach(function (r) {
    t.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.issue) + '</td><td class="small">' + esc(r.cat) + '</td><td>' + esc(r.sev) + '</td></tr>';
  });
  box.appendChild(t);
  box.appendChild(h('p', '三項最要緊：臨床主張未驗證、15 條答案為整理語、6 道案例題待專家核。', 'small'));
};

/* ---------------- 我的 ---------------- */
VIEWS.mine = function (box) {
  box.appendChild(h('h1', '我的'));
  var read = Object.keys(STATE.read || {}).length;
  var log = STATE.log || {};
  var byType = { fill_blank: [0, 0], mcq: [0, 0], error_identification: [0, 0] };
  var idx = {};
  (LS.items || []).forEach(function (i) { idx[i.id] = i; });
  Object.keys(log).forEach(function (id) {
    var it = idx[id]; if (!it) return;
    var k = byType[it.type] || (byType[it.type] = [0, 0]);
    k[1]++; if (log[id] === 'ok') k[0]++;
  });
  var c = h('div', 'card', '');
  c.innerHTML = '<h3>通讀</h3>' + bar(read, (LS.pian || []).length) +
    '<div class="small muted">已讀 ' + read + ' / ' + (LS.pian || []).length + ' 篇</div>' +
    '<h3 style="margin-top:18px">題庫</h3>' + bar(Object.keys(log).length, stat('items')) +
    '<div class="small muted">已作答 ' + Object.keys(log).length + ' / ' + stat('items') + '</div>';
  box.appendChild(c);
  var t = h('table', '');
  t.innerHTML = '<tr><th>題型</th><th style="width:90px">作答</th><th style="width:90px">答對</th><th style="width:80px">正確率</th></tr>';
  Object.keys(byType).forEach(function (k) {
    var v = byType[k];
    t.innerHTML += '<tr><td>' + ({ fill_blank: '填空', mcq: '選擇', error_identification: '辨誤' }[k]) + '</td><td class="num">' + v[1] +
      '</td><td class="num">' + v[0] + '</td><td class="num">' + pct(v[0], v[1]) + '%</td></tr>';
  });
  box.appendChild(t);

  /* 四層掌握度（依 bloom 聚合） */
  var BLOOM = [['remember', '應知'], ['understand', '應會'], ['apply', '理解／應用'], ['evaluate', '遷移']];
  var byB = {};
  Object.keys(log).forEach(function (id) {
    var it = idx[id]; if (!it) return;
    var k = it.bloom || 'remember';
    byB[k] = byB[k] || [0, 0];
    byB[k][1]++; if (log[id] === 'ok') byB[k][0]++;
  });
  box.appendChild(h('h3', '四層掌握度'));
  var tb = h('table', '');
  tb.innerHTML = '<tr><th style="width:110px">層</th><th style="width:90px">作答</th><th style="width:90px">答對</th><th style="width:80px">正確率</th></tr>';
  BLOOM.forEach(function (b) {
    var v = byB[b[0]] || [0, 0];
    tb.innerHTML += '<tr><td>' + b[1] + '</td><td class="num">' + v[1] + '</td><td class="num">' + v[0] +
      '</td><td class="num">' + (v[1] ? pct(v[0], v[1]) + '%' : '—') + '</td></tr>';
  });
  box.appendChild(tb);
  box.appendChild(h('p', '對應關係見首頁「驗收四層」；未作答的層顯示 —。', 'small muted'));
  var b = el('button', 'btn ghost', '清除本機進度'); b.type = 'button';
  b.onclick = function () { if (!confirm('清除已讀與作答紀錄？')) return; STATE.read = {}; STATE.log = {}; save(); route(); };
  box.appendChild(b);
  box.appendChild(h('p', '進度只存在這個瀏覽器（localStorage），不上傳。', 'small muted'));
};

/* ---------------- 關於 ---------------- */
VIEWS.about = function (box) {
  box.appendChild(h('h1', '關於'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:110px">項目</th><th>內容</th></tr>' +
    '<tr><td>底本</td><td>' + esc(LS.meta.bendi) + '</td></tr>' +
    '<tr><td>規模</td><td>81 篇、經文 ' + stat('chars').toLocaleString() + ' 字、題庫 ' + stat('items') + ' 題</td></tr>' +
    '<tr><td>引文</td><td>題面逐字比對，不符 0</td></tr>' +
    '<tr><td>答案</td><td>原文 669／推算 24／整理語 15（已標明）</td></tr>' +
    '<tr><td>註家</td><td>《類經》張介賓注為主；19 條配對待專家核</td></tr>' +
    '<tr><td>授權</td><td><b>待定</b>（目前僅供審閱）</td></tr>' +
    '<tr><td>聯絡</td><td>待補（發布前填入）</td></tr>' +
    '<tr><td>引用</td><td>建議格式：《靈樞自學材料》v1.0，篇序＋篇名，例：40〈陰陽清濁〉</td></tr>';
  box.appendChild(t);
  box.appendChild(h('p', LS.meta.warn, 'small'));
};

/* ---------------- 路由 ---------------- */
function parseHash() {
  var hh = location.hash.replace(/^#\/?/, '');
  var parts = hh.split('?');
  var name = parts[0] || 'home';
  var q = {};
  (parts[1] || '').split('&').forEach(function (kv) {
    if (!kv) return; var a = kv.split('='); q[decodeURIComponent(a[0])] = decodeURIComponent(a[1] || '');
  });
  return { name: name, q: q };
}
function updateMastery() {
  var m = $('#mastery'); if (!m) return;
  var read = Object.keys(STATE.read || {}).length;
  var log = Object.keys(STATE.log || {}).length;
  var v = Math.round((pct(read, (LS.pian || []).length) + pct(log, stat('items'))) / 2);
  m.textContent = '掌握度 ' + v + '%';
}
function route() {
  var r = parseHash();
  var v = VIEWS[r.name] || VIEWS.home;
  var view = $('#view');
  view.innerHTML = '';
  v(view, r.q);
  Array.prototype.forEach.call(document.querySelectorAll('#nav a'), function (a) {
    a.className = a.getAttribute('data-k') === r.name ? 'on' : '';
  });
  updateMastery();
  window.scrollTo(0, 0);
}
function boot() {
  var nav = $('#nav');
  NAV.forEach(function (x) {
    var a = document.createElement('a');
    a.href = '#/' + x[0]; a.textContent = x[1]; a.setAttribute('data-k', x[0]);
    nav.appendChild(a);
  });
  $('#stripe').textContent = LS.meta.warn;
  $('#footLinks').innerHTML = '<a href="#/limits">限制</a><a href="#/method">校勘</a><a href="#/items">題庫</a><a href="#/about">關於</a>';
  window.addEventListener('hashchange', route);
  if (!STATE.agree) gate(); else route();
}
function gate() {
  var view = $('#view');
  view.innerHTML = '';
  var g = h('div', 'gate');
  g.innerHTML = '<h2>使用前確認</h2><p>本材料是讀書與練習工具，不是診療工具。所有臨床主張未經驗證，<b>不可據以施治</b>。' +
    '<br>原文與題目皆經機器逐字比對；標「待專家核」者，臨床判斷僅供參考。</p>';
  var ok = el('button', 'btn', '我了解，開始'); ok.type = 'button';
  ok.onclick = function () { STATE.agree = 1; save(); route(); };
  g.appendChild(ok); view.appendChild(g);
}
boot();
})();

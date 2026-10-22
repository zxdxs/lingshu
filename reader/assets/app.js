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
function md(s) {
  return esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>');
}
function stat(k) { return (LS.meta && LS.meta.stats && LS.meta.stats[k]) || 0; }
function pct(a, b) { return b ? Math.round(a / b * 100) : 0; }
function bar(a, b) { return '<div class="bar"><i style="width:' + pct(a, b) + '%"></i></div>'; }
function bySeq(seq) { return (LS.pian || []).filter(function (p) { return String(p.seq) === String(seq); })[0]; }
function hash(s) { var x = 0; for (var i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) >>> 0; return x; }

var NAV = [['home','首頁'],['themes','主題'],['law','通則'],['read','通讀'],['items','題庫'],['concept','概念'],['suwen','異同'],
           ['prep','九鍼'],['method','方法'],['collation','校勘'],['limits','限制'],
           ['mine','我的'],['about','關於']];
var VIEWS = {};

/* ---------------- 首頁 ---------------- */
VIEWS.home = function (box) {
  var hero = h('div', '', 'hero');
  hero.innerHTML =
    '<div class="kicker">中醫典籍導讀 · 黃帝內經</div>' +
    '<h1>靈樞經</h1>' +
    '<p class="lead">把《靈樞》讀成<b>可以驗收的判斷力</b>：81 篇原文、' + stat('items') + ' 道題，' +
    '每一句都能回到底本，每一條限制都寫在站上。</p>' +
    '<div class="row" style="margin-top:14px">' +
      '<a class="btn" href="#/themes">入口 01 · 看主題</a>' +
      '<a class="btn ghost" href="#/read">入口 02 · 讀原文</a>' +
      '<a class="btn ghost" href="#/items">入口 03 · 練題</a>' +
    '</div>' +
    '<div class="stats" style="margin-top:18px">' +
      '<div class="stat"><b>' + stat('pian') + '</b><span>篇</span></div>' +
      '<div class="stat"><b>' + stat('chars').toLocaleString() + '</b><span>經文字</span></div>' +
      '<div class="stat"><b>' + stat('items') + '</b><span>題</span></div>' +
      '<div class="stat"><b>' + stat('quote_seg') + '</b><span>逐字核過的引文段</span></div>' +
    '</div>';
  box.appendChild(hero);

  var safe = h('div', '', 'alert');
  safe.innerHTML = '<b>' + esc(LS.meta.safety) + '</b>' +
    '<span class="small" style="display:block;margin-top:6px">本站的題目、模組與案例只用原文證候作情境，' +
    '不提供劑量、療程或操作步驟；任何臨床處置請由指導醫師決定。</span>';
  box.appendChild(safe);

  box.appendChild(h('h2', '五個主題'));
  box.appendChild(h('p', '主題的劃分與命名為編者所加，非原文原有分類。', 'small muted'));
  var tg = h('div', '', 'grid');
  (LS.themes || []).forEach(function (t) {
    var c = h('div', '', 'card');
    c.innerHTML = '<h3>' + esc(t.題) + '</h3><p class="small"><b>' + esc(t.一句) + '</b></p>' +
      '<a class="small" href="#/themes">讀這個主題 →</a>';
    tg.appendChild(c);
  });
  box.appendChild(tg);

  var g = h('div', '', 'grid');
  [['目的','讓原文可讀、可練、可查','讀得進去，也練得出來；不以「看懂了」當作學會。'],
   ['價值','把可驗的部分公開','引文逐字比對、答案分型、模組原文、限制與矛盾——全部可查。'],
   ['為什麼現在做','市面上的靈樞多止於導讀','練習紀錄與校勘痕跡很少公開；這份材料把兩者一起留下。']].forEach(function (x) {
    var c = h('div', '', 'card');
    c.innerHTML = '<h3>' + x[0] + '</h3><p class="small muted">' + x[1] + '</p><p>' + x[2] + '</p>';
    g.appendChild(c);
  });
  box.appendChild(g);

  var lawCard = h('div', '', 'card');
  lawCard.innerHTML = '<h3>靈樞在講規矩，不只是講故事</h3>' +
    '<p class="small">「虚則實之，滿則泄之」「司外揣內」「粗守形，上守神」「中而不去則精失」——' +
    '這些句子散在八十一篇裡，反覆出現。本站抽成 <b>' + ((LS.law || {})['條數'] || 16) + ' 條通則</b>，' +
    '每條都掛句ID，可回原文對。</p>' +
    '<p class="small"><a href="#/law">看通則 →</a></p>';
  box.appendChild(lawCard);

  var sw = h('div', '', 'card');
  sw.innerHTML = '<h3>靈樞與素問，差在哪</h3>' +
    '<p class="small">兩書同屬《內經》，但不是同一種書：一個把知識建立在「量」上，一個建立在「理」上；' +
    '一個用一日為尺度，一個用一甲子；一個記「這一個人」，一個記「人這一類」。</p>' +
    '<p class="small"><a href="#/suwen">看五條差別與機器量測（規模、用字、重出句、平行篇）→</a></p>';
  box.appendChild(sw);

  box.appendChild(h('h2', '訓練怎麼進行'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:86px">入口</th><th>要做的事</th><th style="width:150px">產出物（不留下＝沒做）</th></tr>' +
    '<tr><td>讀</td><td>通讀一篇，遇校記停下來看</td><td>標為已讀（本機記錄）</td></tr>' +
    '<tr><td>練</td><td>作答並看解析與出處</td><td>對錯紀錄；' + stat('items') + ' 題可追</td></tr>' +
    '<tr><td>查</td><td>用概念卡與題庫篩選回查</td><td>找到篇、句與出處</td></tr>';
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

  var no = h('div', '', 'card');
  no.innerHTML = '<h3>本站不做什麼</h3><ul class="small" style="margin:.4em 0 0 1.1em;padding:0">' +
    '<li>不替代臨床判斷：所有臨床主張未經驗證，<b>不可據以施治</b>。</li>' +
    '<li>不把素問納入主體：只在對照時引用。</li>' +
    '<li>不生成原文：L0 一律取自底本，每句可回查。</li>' +
    '<li>不掩蓋不確定：限制 ' + stat('limits') + ' 條、矛盾 ' + stat('contradictions') + ' 條公開列出。</li></ul>' +
    '<p class="small" style="margin-top:10px"><a href="#/limits">看已知限制</a>　·　<a href="#/method">看校勘與矛盾</a>　·　<a href="#/about">看授權與出處</a></p>';
  box.appendChild(no);
};

/* ---------------- 主題 ---------------- */
VIEWS.themes = function (box) {
  box.appendChild(h('h1', '靈樞在講什麼'));
  var note = h('div', '', 'card');
  note.innerHTML = '<b>先說清楚</b>：以下五個主題的<b>劃分與命名是編者所加</b>，不是《靈樞》原有的分類。原文只提供材料；' +
    '每一條主張下面都附原文與句 ID，讀者可以不同意這個分法，直接讀原文。';
  box.appendChild(note);
  (LS.themes || []).forEach(function (t, i) {
    var c = h('div', '', 'card');
    var qs = (t.句 || []).map(function (q) {
      return '<div class="tiao"><span class="pill b">' + esc(q.id || '') + '</span>' + esc(q.文) +
        ' <span class="small muted">《靈樞·' + esc((LS.pian || []).filter(function (p) { return p.seq === q.篇; })[0]?.name || '') + '》</span></div>';
    }).join('');
    var ps = (t.篇名 || []).map(function (n, j) {
      return '<a class="pill" href="#/read?seq=' + t.篇[j] + '">' + esc(n) + '</a>';
    }).join('');
    var route = '';
    if (t.路線 && t.路線.length) {
      route = '<h3 style="margin:14px 0 4px">病從外入的路線</h3><div class="route">' +
        t.路線.map(function (st) {
          return '<div class="st"><div><b>' + esc(st.站) + '</b></div>' +
            '<div>' + esc(st.證) + '</div>' +
            '<div><a class="pill b" href="#/read?seq=66">' + esc(st.id || '') + '</a></div></div>';
        }).join('') + '</div>' +
        '<p class="small muted">七站都在〈百病始生〉同一段（66-5-1 至 66-5-7），原文用「留而不去」串起來。</p>';
    }
    var cnt = (LS.items || []).filter(function (it) { return (t.篇 || []).indexOf(it.seq) >= 0; }).length;
    c.innerHTML = '<div class="small muted">主題 ' + (i + 1) + '　<span class="pill y">編者歸納</span></div>' +
      '<h3 style="margin:.2em 0">' + esc(t.題) + '</h3>' +
      '<p style="font-size:1.05rem"><b>' + esc(t.一句) + '</b></p>' +
      '<p>' + esc(t.主張) + '</p>' + qs + route +
      '<div class="row" style="margin-top:8px">' + ps + '</div>' +
      '<p class="small"><a href="#/items?theme=' + esc(t.id) + '">這個主題有 ' + cnt + ' 題 →</a>' +
      (t.圖 ? '　<a href="../export/' + esc(t.圖) + '" target="_blank">看圖 →</a>' : '') + '</p>' +
      '<p class="small muted">邊界：' + esc(t.邊界 || '') + '</p>';
    box.appendChild(c);
  });
};

/* ---------------- 通讀 ---------------- */
VIEWS.read = function (box, q) {
  if (q.seq) return readOne(box, q.seq);
  box.appendChild(h('h1', '通讀'));
  var row = h('div', '', 'row');
  var sel = document.createElement('select');
  sel.appendChild(new Option('全部卷', ''));
  (LS.juan || []).forEach(function (j) { sel.appendChild(new Option(j.label + '（' + j.n + ' 篇）', j.no)); });
  var inp = document.createElement('input'); inp.type = 'search'; inp.placeholder = '搜篇名…';
  var note = el('span', 'small muted', '');
  row.appendChild(sel); row.appendChild(inp); row.appendChild(note);
  box.appendChild(row);
  var pb = h('div', ''); box.appendChild(pb);
  var list = h('div', '', 'list'); box.appendChild(list);
  function render() {
    list.innerHTML = '';
    var jf = sel.value, kw = inp.value.trim(), done = 0, total = 0;
    (LS.pian || []).forEach(function (p) {
      if (jf !== '' && String(p.juan) !== jf) return;
      if (kw && p.name.indexOf(kw) < 0) return;
      total++;
      var read = STATE.read && STATE.read[p.seq];
      if (read) done++;
      var d = h('div', '', 'tiao');
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
  var row = h('div', '', 'row');
  var b = el('button', 'btn', STATE.read && STATE.read[p.seq] ? '已讀 ✓' : '標為已讀'); b.type = 'button';
  var b2 = el('button', 'btn ghost', '← 回通讀'); b2.type = 'button';
  var b3 = el('a', 'btn ghost', '看本篇題目'); b3.href = '#/items?seq=' + p.seq;
  b.onclick = function () { STATE.read = STATE.read || {}; STATE.read[p.seq] = 1; save(); b.textContent = '已讀 ✓'; };
  b2.onclick = function () { location.hash = '#/read'; };
  row.appendChild(b); row.appendChild(b2); row.appendChild(b3);
  box.appendChild(row);
  var t = h('div', '', 'orig');
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
  var head = h('div', '', 'card');
  head.innerHTML = bar(attempts, stat('items')) +
    '<div class="small muted">已作答 ' + attempts + ' / ' + stat('items') + '　·　答對 ' + ok +
    '（' + pct(ok, attempts) + '%）</div>';
  box.appendChild(head);

  var row = h('div', '', 'row');
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
  var theme = q.theme ? (LS.themes || []).filter(function (t) { return t.id === q.theme; })[0] : null;
  var tSeqs = theme ? (theme.篇 || []).map(String) : null;
  if (theme) {
    var tp = h('p', '', 'small');
    tp.innerHTML = '主題：<b>' + esc(theme.題) + '</b>　<span class="muted">' + esc(theme.一句) + '</span>　<a href="#/items">清除</a>';
    box.appendChild(tp);
  }
  var list = h('div', ''); box.appendChild(list);

  function render() {
    list.innerHTML = '';
    var shown = 0;
    (LS.items || []).forEach(function (it) {
      if (tSeqs && tSeqs.indexOf(String(it.seq)) < 0) return;
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
  var c = h('div', '', 'card');
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
    var row = h('div', '', 'row');
    var b = el('button', 'btn ghost', '顯示答案'); b.type = 'button';
    var r1 = el('button', 'btn', '答對'); r1.type = 'button';
    var r2 = el('button', 'btn ghost', '答錯'); r2.type = 'button';
    var a = h('div', '', 'ans');
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
  box.appendChild(h('p', '同一個詞在《靈樞》裡有幾層意思。每張卡的<b>分層方式與命名是編者整理</b>；各層原文與出處則逐字取自底本。', 'small muted'));
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


/* ---------------- 異同：靈樞與素問 ---------------- */
VIEWS.suwen = function (box) {
  var S = LS.suwen || {}, N = S.narr || {}, C = S.calc || {};
  box.appendChild(h('h1', '靈樞與素問的異同'));
  box.appendChild(h('p', esc(N['引言'] || ''), 'lead'));

  var warn = h('div', '', 'card');
  warn.innerHTML = '<h3>先說立場</h3><p>本站主體只有《靈樞》八十一篇。素問不進題庫、不進通讀、不佔任何一篇的位置；' +
    '它出現在這一頁，只為了回答一個問題：<b>靈樞在《內經》裡負責什麼</b>。</p>' +
    '<p class="small muted">本頁數字全部由 <code>scripts/compare_suwen.py</code> 從兩份經文算出；' +
    '引文由 <code>scripts/audit_cross_quotes.py</code> 逐字比對所標來源。</p>';
  box.appendChild(warn);


  // ── 五條差別（頁面主體，放在量測之前）──
  var QT = (LS.suwen && LS.suwen.quant) || {};
  var DIFF = (N['差別'] || []);
  function rateTable(key) {
    var rows = (QT['詞頻'] || {})[key] || [];
    if (!rows.length) return '';
    var h = '<table><tr><th style="width:56px">詞</th><th style="width:80px">靈樞</th><th style="width:80px">素問</th><th>倍數</th></tr>';
    rows.forEach(function (x) {
      var a = x['靈樞萬字'], b = x['素問萬字'];
      var m = (b > 0 && a > 0) ? (a >= b ? (a / b) : -(b / a)) : 0;
      var note = !b ? '靈樞獨有' : (!a ? '素問獨有' : (m >= 0 ? '靈樞 ' + m.toFixed(1) + ' 倍' : '素問 ' + (-m).toFixed(1) + ' 倍'));
      h += '<tr><td>' + esc(x['詞']) + '</td><td>' + a + '</td><td>' + b + '</td><td class="small muted">' + note + '</td></tr>';
    });
    return h + '</table>';
  }
  function quantTable(which) {
    var rows = ((QT['量化'] || {})[which] || []).slice(0, 8);
    if (!rows.length) return '';
    var h = '<table><tr><th style="width:120px">篇</th><th style="width:60px">條</th><th>序</th></tr>';
    rows.forEach(function (x) {
      h += '<tr><td><a href="#/read?seq=' + x['序'] + '">' + esc(x['篇']) + '</a></td><td>' + x['條'] + '</td><td class="small muted">' + x['序'] + '</td></tr>';
    });
    return h + '</table>';
  }
  function answererTable() {
    var A = QT['應答者'] || {};
    if (!(A['總次數'] || []).length) return '';
    var h = '<table><tr><th style="width:80px">應答者</th><th style="width:70px">次數</th></tr>';
    (A['總次數'] || []).forEach(function (x) { h += '<tr><td>' + esc(x['名']) + '</td><td>' + x['次數'] + '</td></tr>'; });
    h += '</table>';
    var by = {};
    (A['非岐伯主答篇'] || []).forEach(function (x) { (by[x['主答']] = by[x['主答']] || []).push(x['篇']); });
    Object.keys(by).forEach(function (k) {
      h += '<p class="small"><b>' + esc(k) + '</b>（' + by[k].length + ' 篇）：' + esc(by[k].join('、')) + '</p>';
    });
    return h;
  }

  if (DIFF.length) {
    var c0 = h('div', '', 'card');
    c0.appendChild(el('h2', '', '差別在哪：五條'));
    c0.appendChild(h('p', '以下五條是編者的判斷（『歸』），每條後面接能查的部分（引文逐字驗過、詞頻機器算）；' +
      '量不到的部分會直接寫『量不到』，不拿語氣當證據。', 'small'));
    DIFF.forEach(function (d) {
      var sec = h('div', '', 'card');
      sec.appendChild(h('h3', '', d['n'] + '、' + esc(d['題'])));
      sec.appendChild(h('p', '<b>主張</b>：' + md(d['主張'])));
      (d['證據'] || []).forEach(function (q) {
        sec.appendChild(h('p', '「' + esc(q['引']) + '」', 'quote'));
        sec.appendChild(h('p', '——' + esc(q['來源']), 'small muted'));
      });
      if (d['表'] === '量化') {
        sec.appendChild(h('h4', '量化榜（句內出現數字＋尺寸單位；規則寫在腳本裡）', 'small'));
        sec.appendChild(h('div', 'table-wrap', quantTable('量身體（寸尺丈分度…）')));
        sec.appendChild(h('h4', '量時間（日、刻、息…）', 'small'));
        sec.appendChild(h('div', 'table-wrap', quantTable('量時間（日刻息壯遍宿）')));
      } else if (d['表'] === '時間') {
        sec.appendChild(h('div', 'table-wrap', rateTable('時間（日週期）')));
        sec.appendChild(h('div', 'table-wrap', rateTable('時間（年與甲子）')));
      } else if (d['表'] === '個體') {
        sec.appendChild(h('div', 'table-wrap', rateTable('個體差異')));
      } else if (d['表'] === '界限') {
        sec.appendChild(h('div', 'table-wrap', rateTable('界限與死期')));
      } else if (d['表'] === '師承') {
        sec.appendChild(h('div', 'table-wrap', answererTable()));
        sec.appendChild(h('div', 'table-wrap', rateTable('師承痕跡')));
      }
      if (d['說']) sec.appendChild(h('p', md(d['說']), 'small'));
      if (d['更正']) sec.appendChild(h('p', '<b>出處更正</b>：' + md(d['更正']), 'small'));
      if (d['反證']) {
        var anti = h('div', '', 'alert');
        anti.innerHTML = '<b>反證／量不到的部分</b><br/>' + md(d['反證']);
        sec.appendChild(anti);
      }
      if (d['例外']) sec.appendChild(h('p', '例外：' + md(d['例外']), 'small muted'));
      c0.appendChild(sec);
    });
    box.appendChild(c0);
  }

  // 來歷（史崧序、遺篇）
  if ((N['來歷'] || []).length) {
    var cl0 = h('div', '', 'card');
    cl0.appendChild(el('h2', '', '來歷：兩書的整理不對稱'));
    N['來歷'].forEach(function (x) {
      cl0.appendChild(h('p', '「' + esc(x['引']) + '」', 'quote'));
      cl0.appendChild(h('p', '——' + esc(x['來源']), 'small muted'));
      cl0.appendChild(h('p', esc(x['說']), 'small'));
    });
    box.appendChild(cl0);
  }

  // 名實
  if ((N['名實'] || []).length) {
    var c1 = h('div', '', 'card');
    c1.appendChild(el('h2', '', '名實：兩書是一組'));
    N['名實'].forEach(function (x) {
      c1.appendChild(h('p', '「' + esc(x['引']) + '」', 'quote'));
      c1.appendChild(h('p', '——' + esc(x['來源']), 'small muted'));
      c1.appendChild(h('p', esc(x['說']), 'small'));
    });
    box.appendChild(c1);
  }

  // 規模
  var L = C['統計'] ? C['統計']['靈樞'] : null, Q = C['統計'] ? C['統計']['素問'] : null;
  if (L && Q) {
    var c2 = h('div', '', 'card');
    c2.appendChild(el('h2', '', '規模'));
    c2.innerHTML += '<table><tr><th style="width:96px"></th><th>靈樞</th><th>素問</th></tr>' +
      '<tr><td>卷</td><td>' + L['卷'] + '</td><td>' + Q['卷'] + '</td></tr>' +
      '<tr><td>篇</td><td>' + L['篇'] + '</td><td>' + Q['篇'] + '（今本 81；' + esc(Q['亡篇']) + '亡，另 3 篇篇名行缺）</td></tr>' +
      '<tr><td>經文</td><td>' + L['字'].toLocaleString() + ' 字</td><td>' + Q['字'].toLocaleString() + ' 字</td></tr>' +
      '<tr><td>篇名以「論」結尾</td><td>' + L['篇名以論結尾'] + '／' + L['篇'] + '</td><td>' + Q['篇名以論結尾'] + '／' + Q['篇'] + '</td></tr>' +
      '</table>';
    c2.appendChild(h('p', '素問幾乎每篇都叫「某某論」；靈樞的篇名多為具體名目（九鍼十二原、本輸、骨度、脈度、五十營）——' +
      '篇名本身就是兩種寫法的證據。', 'small'));
    box.appendChild(c2);
  }

  // 用字
  if ((C['用字'] || []).length) {
    var c3 = h('div', '', 'card');
    c3.appendChild(el('h2', '', '用字：每萬字出現次數'));
    var rows = (C['用字'] || []).slice().sort(function (a, b) {
      return Math.abs(b['靈樞萬字'] - b['素問萬字']) - Math.abs(a['靈樞萬字'] - a['素問萬字']);
    });
    var t = '<tr><th style="width:64px">詞</th><th style="width:74px">靈樞</th><th style="width:74px">素問</th><th>差距</th></tr>';
    rows.forEach(function (x) {
      var d = Math.round((x['靈樞萬字'] - x['素問萬字']) * 10) / 10;
      t += '<tr><td>' + esc(x['詞']) + '</td><td>' + x['靈樞萬字'] + '</td><td>' + x['素問萬字'] + '</td>' +
        '<td class="small ' + (Math.abs(d) < 6 ? 'muted' : '') + '">' + (d > 0 ? '靈樞多 ' : (d < 0 ? '素問多 ' : '持平 ')) +
        Math.abs(d) + '</td></tr>';
    });
    c3.innerHTML += '<table>' + t + '</table>';
    c3.appendChild(h('p', '異體已合併計數（鍼／針、剌／刺、脉／脈、隂／陰），否則差異會假性放大。', 'small muted'));
    var notes = N['用字解讀'] || {};
    var keys = Object.keys(notes).filter(function (k) { return notes[k]; });
    if (keys.length) {
      c3.appendChild(el('h3', '', '怎麼讀這張表'));
      var ul = el('ul', 'small', '');
      keys.forEach(function (k) {
        var li = el('li', '', ''); li.innerHTML = '<b>' + esc(k) + '</b>：' + esc(notes[k]);
        ul.appendChild(li);
      });
      c3.appendChild(ul);
    }
    box.appendChild(c3);
  }

  // 重出句
  var sh = C['重出句'] || [];
  var c4 = h('div', '', 'card');
  c4.appendChild(el('h2', '', '重出：兩書都有的句子'));
  c4.appendChild(h('p', '把靈樞 ' + stat('ju') + ' 句逐句拿去素問經文裡找，正規化後完全相同（≥8 字）的有 ' + sh.length + ' 句。' +
    '其餘大量段落是「同一個題目、兩套寫法」，不是逐字重出。', 'small'));
  if (sh.length) {
    var t2 = '<tr><th style="width:104px">靈樞</th><th>文</th><th style="width:132px">素問</th></tr>';
    sh.forEach(function (x) {
      t2 += '<tr><td class="small">' + esc(x['pian']) + '</td><td>' + esc(x['文']) + '</td>' +
        '<td class="small">' + (x['素問篇'] ? '卷' + x['素問卷'] + '〈' + esc(x['素問篇'].replace(/篇$/, '')) + '〉' : '卷' + (x['素問卷'] || '?')) + '</td></tr>';
    });
    c4.innerHTML += '<table>' + t2 + '</table>';
  }
  box.appendChild(c4);

  // 平行篇
  var pp = C['平行篇'] || [];
  if (pp.length) {
    var c5 = h('div', '', 'card');
    c5.appendChild(el('h2', '', '平行篇：同一個題目，兩套寫法'));
    c5.appendChild(h('p', '以四字串覆蓋率配對（雙向），不靠印象。覆蓋率高，表示兩篇在講同一件事、用語接近。', 'small'));
    var t3 = '<tr><th style="width:88px">靈樞</th><th style="width:150px">素問</th><th style="width:70px">覆蓋靈樞</th><th style="width:70px">覆蓋素問</th><th>共用四字串</th></tr>';
    pp.forEach(function (x) {
      t3 += '<tr><td>' + esc(x['靈樞']) + '</td><td class="small">卷' + x['卷'] + '〈' + esc(x['素問'].replace(/篇$/, '')) + '〉</td>' +
        '<td>' + x['覆蓋靈樞'] + '%</td><td>' + x['覆蓋素問'] + '%</td><td class="small">' + x['四字串'] + '</td></tr>';
    });
    c5.innerHTML += '<table>' + t3 + '</table>';
    c5.appendChild(h('p', '靈樞〈病本〉與素問〈標本病傳論〉是同一段文字：靈樞那一篇的四分之三都能在素問裡找到。' +
      '反過來，素問〈血氣形志〉有近三成見於靈樞〈九鍼論〉——誰抄誰，本站不判斷。', 'small'));
    box.appendChild(c5);
  }

  // 怎麼用 / 未做
  var c6 = h('div', '', 'card');
  c6.appendChild(el('h2', '', '本站怎麼用這兩個資料'));
  var ul2 = el('ul', 'small', '');
  (N['怎麼用'] || []).forEach(function (t) { ul2.appendChild(el('li', '', t)); });
  c6.appendChild(ul2);
  box.appendChild(c6);

  var c7 = h('div', '', 'card');
  c7.appendChild(el('h2', '', '〔空〕沒做的事'));
  var ul3 = el('ul', 'small', '');
  (N['未做'] || []).forEach(function (t) { ul3.appendChild(el('li', '', t)); });
  c7.appendChild(ul3);
  box.appendChild(c7);

  box.appendChild(h('p', '引文規矩：「」只給靈樞原文（逐字機器驗證）；『』給素問、類經與我自撰的詞。', 'small muted'));
};


/* ---------------- 通則 ---------------- */
VIEWS.law = function (box, q) {
  var L = LS.law || {};
  box.appendChild(h('h1', '通則：靈樞反覆在講的那些規矩'));
  box.appendChild(h('p', '這一頁不是摘要，是把散在八十一篇裡、反覆出現的判準抽出來。' +
    '每條都掛著句ID，可以回原文對；抽得對不對，你看著原文判斷。', 'lead'));

  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>怎麼讀這一頁</h3><ul class="small">' +
    '<li><b>原則</b>是編者的歸納（歸）；<b>引</b>是原文，句ID 可回查（原）。</li>' +
    '<li><b>推演</b>是這條原則往下走會得到什麼；<b>用</b>是拿它去讀原文時可以問的問題。</li>' +
    '<li><b>界</b>寫的是不能推到哪裡——通則最容易變成過度推論。</li>' +
    '<li>本頁只講「怎麼讀」，不講「怎麼做」。操作、劑量、手法不在這裡，也不該從網頁學。</li></ul>';
  box.appendChild(intro);

  // 學習路徑
  if ((L['路徑'] || []).length) {
    var rt = h('div', '', 'card');
    rt.appendChild(el('h2', '', '從哪讀起：六站'));
    rt.appendChild(h('p', '通則不是用來從第一條背到最後一條的。照這個次序讀，每一站讀完，對應的通則才有依托。', 'small'));
    var tr = '<tr><th style="width:44px">站</th><th>讀這幾篇</th><th>為什麼</th><th style="width:76px">對應通則</th></tr>';
    (L['路徑'] || []).forEach(function (x) {
      var links = (x['篇'] || []).map(function (p) {
        return '<a href="#/read?seq=' + p['序'] + '">' + esc(p['名']) + '</a>';
      }).join('、');
      tr += '<tr><td>' + esc(x['階段']) + '</td><td class="small">' + esc(x['題']) + '<br/>' + links + '</td>' +
        '<td class="small">' + esc(x['為什麼']) + '</td>' +
        '<td class="small">' + (x['通則'] || []).map(function (n) { return '<a href="#/law?n=' + n + '">' + n + '</a>'; }).join(' ') + '</td></tr>';
    });
    var wrap = h('div', '', 'table-wrap');
    wrap.innerHTML = '<table>' + tr + '</table>';
    rt.appendChild(wrap);
    box.appendChild(rt);
  }

  // 目錄
  var toc = h('div', '', 'card');
  toc.appendChild(el('h3', '', (L['條數'] || '') + ' 條，' + (L['組數'] || '') + ' 組'));
  (L['組'] || []).forEach(function (g) {
    var p = h('p', '<b>' + esc(g['組']) + '</b>　', 'small');
    g['條'].forEach(function (x) {
      var a = el('a', '', x['n'] + '. ' + x['名']);
      a.href = '#/law?n=' + x['n'];
      p.appendChild(a);
      p.appendChild(document.createTextNode('　'));
    });
    toc.appendChild(p);
  });
  toc.appendChild(h('p', '判準：一條通則至少要能由兩篇支持；只在一篇出現的寫法，留在那一篇的模組裡，不升為通則。', 'small muted'));
  box.appendChild(toc);

  (L['組'] || []).forEach(function (g) {
    var sec = h('div', '', 'card');
    sec.appendChild(el('h2', '', g['組']));
    (g['條'] || []).forEach(function (x) {
      var art = h('div', '', 'law-item');
      art.setAttribute('id', 'law' + x['n']);
      art.appendChild(el('h3', '', x['n'] + '. ' + x['名']));
      art.appendChild(h('p', '<b>原則</b>（歸）：' + md(x['原則'])));
      (x['引'] || []).forEach(function (q) {
        var qq = h('div', '', 'quote');
        qq.innerHTML = esc(q['文']) +
          '<div class="src">——《靈樞·' + esc(q['篇']) + '》 · 句 ' + esc(q['id']) +
          '　·　' + esc(q['註']) + '</div>';
        art.appendChild(qq);
      });
      art.appendChild(h('p', '<b>推演</b>（歸）：' + md(x['推演']), 'small'));
      art.appendChild(h('p', '<b>用</b>（歸）：' + md(x['用']), 'small'));
      art.appendChild(h('p', '<b>界</b>（空／歸）：' + md(x['界']), 'small muted'));
      var seen = {}, seqs = [];
      (x['引'] || []).forEach(function (q) { if (!seen[q['seq']]) { seen[q['seq']] = 1; seqs.push([q['seq'], q['篇']]); } });
      if (seqs.length) {
        art.appendChild(h('p', '回原文：' + seqs.map(function (p) {
          return '<a href="#/read?seq=' + p[0] + '">〈' + esc(p[1]) + '〉</a>';
        }).join('　'), 'small'));
      }
      sec.appendChild(art);
    });
    box.appendChild(sec);
  });

  var _chuan = '「傳承」一組';
  (L['組'] || []).forEach(function (g) {
    if (g['組'].indexOf('傳承') < 0) return;
    var ns = (g['條'] || []).map(function (x) { return x['n']; });
    if (ns.length) _chuan = '第 ' + ns[0] + '–' + ns[ns.length - 1] + ' 條';
  });
  var tail = h('div', '', 'card');
  tail.innerHTML = '<h3>為什麼要抽成通則</h3>' +
    '<p class="small">單篇讀，容易記住故事；通則讀，才看得出同一個判斷在不同篇裡換了什麼說法。' +
    '本站的「概念」頁處理一個詞的幾層意思，這一頁處理一條規矩的幾種說法——兩者都是為了讓八十一篇彼此對得上。</p>' +
    '<p class="small muted">抽通則的代價是簡化：原文的條件往往比一條原則複雜。所以每條都留「界」，' +
    '把不能推的地方寫出來。</p>' +
    ((LS.defs && LS.defs.pian && LS.defs.pian.length) ?
      '<h3>抽通則時掃過的底：定義句 ' + LS.defs.n + ' 條</h3>' +
      '<p class="small">用三種句式（『…者，…也』『所謂…者』『何謂…』）全書掃過，得 ' + LS.defs.n + ' 條候選。' +
      '密度最高的五篇是 ' + LS.defs.pian.map(function (x) { return '〈' + esc(x[0]) + '〉' + x[1]; }).join('、') +
      '——〈小鍼解〉逐句解釋〈九鍼十二原〉，〈官鍼〉講十二節，〈刺節真邪〉講刺法與邪氣，都是技術篇。' +
      '通則就是從這批候選裡挑出來的，沒挑上的仍在 <code>data/定義句.json</code>。</p>' : '') +
    '<h3 style="margin-top:18px">本站怎麼對待「傳承」</h3>' +
    '<p class="small">靈樞自己立了傳授的規矩（見上列' + _chuan + '）。本站照著做，方式是：</p>' +
    '<ul class="small">' +
    '<li><b>給理解，不給操作</b>：不提供劑量、療程、進針深度或手法步驟——那些需要師授與臨床責任。</li>' +
    '<li><b>每句可回原文</b>：所有引文掛句ID；抽出來的原則標『歸』，不冒充原文。</li>' +
    '<li><b>限制公開</b>：能力邊界 34 條、矛盾 14 條，寫在站上而不是藏起來。</li>' +
    '<li><b>可傳但不可私佔</b>：內容以 CC BY-NC-SA 4.0 釋出——可以教、可以改，但要同樣開放、不得商業使用。</li>' +
    '<li><b>先說誰能用</b>：僅供在有帶教資格的執業中醫師指導下使用。</li></ul>' +
    '<p class="small"><a href="#/themes">回主題</a>　·　<a href="#/suwen">看靈樞與素問的差別</a>　·　' +
    '<a href="#/limits">看本站的能力邊界</a></p>';
  box.appendChild(tail);

  if (q && q.n) {
    var target = document.getElementById('law' + q.n);
    if (target) target.scrollIntoView ? target.scrollIntoView({ block: 'start' }) : null;
  }
};

/* ---------------- 九鍼 ---------------- */
VIEWS.prep = function (box) {
  box.appendChild(h('h1', '九鍼'));
  box.appendChild(h('p', '讀靈樞之前，這一頁要能背：九種鍼、各長多少、各自拿來做什麼。' +
    '靈樞談刺法幾乎都預設你認得這九樣。', 'small'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:44px">序</th><th style="width:68px">鍼</th><th style="width:76px">長</th><th>用途與原文</th></tr>';
  (LS.needles || []).forEach(function (n) {
    t.innerHTML += '<tr><td>' + esc(n.no) + '</td><td>' + esc(n.name) + '</td><td>' + esc(n.len) +
      '</td><td>' + esc(n.use) + '<div class="src">原文：' + esc(n.src) + '</div></td></tr>';
  });
  box.appendChild(t);
  box.appendChild(h('p', '出處：〈九鍼十二原〉與〈九鍼論〉。兩篇毫鍼長度不同（一寸六分／三寸六分），' +
    '是底本自身的差異，不是排印錯。', 'small muted'));
  var c = h('div', '', 'card');
  c.innerHTML = '<h3>為什麼先讀這個</h3><p class="small">靈樞的病位、刺法、禁忌，最後多以「用哪一根鍼」收尾。' +
    '不認得九鍼，讀到「員利者，取之於…」就只剩字面。回原文：' +
    '<a href="#/read?seq=1">〈九鍼十二原〉</a>　<a href="#/read?seq=78">〈九鍼論〉</a>　' +
    '<a href="#/read?seq=7">〈官鍼〉</a></p>';
  box.appendChild(c);
};

/* ---------------- 方法 ---------------- */
VIEWS.method = function (box) {
  box.appendChild(h('h1', '方法與校勘'));
  box.appendChild(h('p', '這一頁回答「這本書可不可信」。完整方法見 docs/01、33、82、88。', 'small muted'));
  var c = h('div', '', 'card');
  c.innerHTML = '<h3>校勘（' + (LS.collation || []).length + ' 點）</h3>' +
    '<p class="small">三源並排（底本／太素／類經）另成一頁；覆蓋率的原始數字在 data/三源覆蓋率.json。</p>' +
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
  var sg = h('div', '', 'alert');
  sg.innerHTML = '<b>' + esc(LS.meta.safety) + '</b>';
  box.appendChild(sg);
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
  var c = h('div', '', 'card');
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
  var R = (LS.meta.release || {});
  box.appendChild(h('h1', '關於'));
  box.appendChild(h('p', (R.站名 || '中醫典籍導讀﹣靈樞經') + (R.英文名 ? '　·　' + R.英文名 : ''), 'small muted'));
  var LABEL = { '聯絡': '聯絡方式', 'Anki實機': 'Anki 實機匯入測試', '授權': '授權' };
  var pend = (R.必要 || []).filter(function (k) {
    return !R[k] || R[k] === '待定' || R[k] === '待補' || R[k] === '未測';
  }).map(function (k) { return LABEL[k] || k; });
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:110px">項目</th><th>內容</th></tr>' +
    '<tr><td>底本</td><td>' + esc(LS.meta.bendi) + '</td></tr>' +
    '<tr><td>規模</td><td>81 篇、經文 ' + stat('chars').toLocaleString() + ' 字、題庫 ' + stat('items') + ' 題</td></tr>' +
    '<tr><td>引文</td><td>題面逐字比對，不符 0</td></tr>' +
    '<tr><td>答案</td><td>原文 ' + (LS.meta.stats.ans_yuanwen || 669) + '／推算 ' +
      (LS.meta.stats.ans_tuisuan || 24) + '／整理語 ' + (LS.meta.stats.ans_zhengli || 15) + '（已標明）</td></tr>' +
    '<tr><td>註家</td><td>《類經》張介賓注為主；19 條配對待專家核</td></tr>' +
    '<tr><td>授權</td><td>' + (R.授權 && R.授權 !== '待定'
      ? esc(R.授權) + '（原文屬公共領域；本計畫之標點、校記、題目、圖表依此釋出，見 <code>LICENSE.txt</code>）'
      : '<b>待定</b>（目前僅供審閱，不得轉載）') + '</td></tr>' +
    '<tr><td>聯絡</td><td>' + (R.聯絡 && R.聯絡 !== '待補'
      ? esc(R.聯絡) : '待補（發布前填入）') + '</td></tr>' +
    '<tr><td>安全</td><td><b>' + esc(LS.meta.safety || '') + '</b></td></tr>' +
    '<tr><td>引用</td><td>' + esc(R.引用格式 || '《中醫典籍導讀﹣靈樞經》v1.0，篇序＋篇名，例：40〈陰陽清濁〉') + '</td></tr>';
  box.appendChild(t);
  if (pend.length) {
    box.appendChild(h('p', '待決：' + pend.join('、') + '（其餘皆已定稿；填入後重建即生效）', 'small'));
  }
  box.appendChild(h('p', LS.meta.safety_note, 'small'));
  box.appendChild(h('p', 'small', '<a href="#/contact">✉️ 看到錯、想指正，或要問授權範圍 →</a>'));
};


/* ---------------- 指正與聯絡 ---------------- */
VIEWS.contact = function (box) {
  var C = LS.contact || {};
  box.appendChild(h('h1', esc(C.title || '指正與聯絡')));
  if (C.lead) { var ld = h('div', '', 'card'); ld.innerHTML = '<p>' + md(C.lead) + '</p>'; box.appendChild(ld); }

  if ((C.want || []).length) {
    var w = h('div', '', 'card');
    w.appendChild(el('h3', '', '最需要人幫忙的五件事'));
    w.appendChild(h('p', '前兩項是站上最大的不確定處，回報一處就少一處。', 'small muted'));
    C.want.forEach(function (x) {
      w.appendChild(el('h4', 'want-k', x.k));
      w.appendChild(h('p', md(x.d), 'small'));
    });
    box.appendChild(w);
  }

  var it = h('div', '', 'card');
  it.appendChild(el('h3', '', '怎麼聯絡'));
  (C.items || []).forEach(function (x) {
    var row = h('div', '', 'contact-row');
    var left = h('div', '', 'contact-txt');
    left.appendChild(el('h4', '', x.k));
    var d = h('p', md(x.d), 'small'); left.appendChild(d);
    if (x.mail) {
      var a = el('a', 'mail', x.mailText || x.mail);
      a.href = 'mailto:' + x.mail; left.appendChild(a);
    } else {
      left.appendChild(h('p', '<b>待補</b>——發布前會填上可公開的郵箱；目前請透過下方相關站點聯絡。', 'small'));
    }
    row.appendChild(left); it.appendChild(row);
  });
  box.appendChild(it);

  var st = h('div', '', 'card');
  st.appendChild(el('h3', '', '相關站點'));
  (C.sites || []).forEach(function (x) {
    var d = h('div', '', 'site');
    var a = el('a', 'site-a', x.k + ' ↗');
    a.href = x.url; a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener noreferrer');
    d.appendChild(a);
    d.appendChild(h('p', md(x.d), 'small'));
    d.appendChild(el('p', 'tiny muted', x.url));
    st.appendChild(d);
  });
  box.appendChild(st);

  var cl = h('div', '', 'card');
  cl.innerHTML = '<p class="small">' + md(C.close || '') + '</p>' +
    '<p class="muted small" style="text-align:right;margin-top:12px">⚠ ' + esc(C.seal || '') + '</p>';
  box.appendChild(cl);
};

/* 供檢查脚本確認有哪些視圖（已下架的路由不該再被連結） */
window.__ROUTES = Object.keys(VIEWS);

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
  $('#footLinks').innerHTML = '<a href="#/contact">✉️ 指正與聯絡</a><a href="#/limits">限制</a><a href="#/method">校勘</a><a href="#/items">題庫</a><a href="#/about">關於</a>';
  window.addEventListener('hashchange', route);
  if (!STATE.agree) gate(); else route();
}
function gate() {
  var view = $('#view');
  view.innerHTML = '';
  var g = h('div', '', 'gate');
  g.innerHTML = '<h2>使用前確認</h2>' +
    '<div class="alert"><b>' + esc(LS.meta.safety) + '</b></div>' +
    '<p>本材料是讀書與練習工具，不是診療工具，也不是教材的替代品。' +
    '書中證候、治法、鍼刺之文，只宜作為隨師學習時的對讀材料；' +
    '自行照書判斷或施治，可能造成傷害。</p>' +
    '<p class="small">原文與題目皆經機器逐字比對；標『待專家核』者，臨床判斷尚待專家審閱。</p>';
  var ok = el('button', 'btn', '我已了解，且在有帶教資格的執業中醫師指導下使用'); ok.type = 'button';
  ok.onclick = function () { STATE.agree = 1; save(); route(); };
  g.appendChild(ok); view.appendChild(g);
}
boot();
})();

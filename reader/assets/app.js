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

function nextLinks(box, links) {
  var d = h('div', '', 'next');
  d.innerHTML = '<span class="next-k">接著看</span>' + (links || []).map(function (x) {
    return '<a href="' + x[1] + '">' + x[0] + '</a>';
  }).join('');
  box.appendChild(d);
}

var NAV = [
  ['home','首頁',1], ['themes','主題'], ['law','通則'],
  ['read','通讀',1], ['meridian','十二經'], ['binghou','病候'], ['variant','變體'], ['jizhu','注家'], ['jiugong','九宫'],
  ['items','題庫',1], ['concept','概念'],
  ['suwen','異同',1], ['prep','九鍼'],
  ['search','搜尋',1], ['method','方法'], ['collation','校勘'], ['limits','限制'],
  ['mine','我的',1], ['about','關於']
];
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

  // 全站地圖：按「先讀什麼、再練什麼、最後查什麼」排，不按頁面建立時間排
  var MAP = [
    ['入門', [['主題', '#/themes', '靈樞在講什麼'], ['通則', '#/law', ((LS.law || {})['條數'] || 44) + ' 條反覆出現的規矩']]],
    ['讀原文', [['通讀', '#/read', '81 篇'], ['十二經', '#/meridian', '六套通道'], ['病候', '#/binghou', '四組模板']]],
    ['練與查', [['題庫', '#/items', '1031 題'], ['概念', '#/concept', '12 張'], ['九鍼', '#/prep', '九種鍼']]],
    ['對照', [['異同', '#/suwen', '靈樞 vs 素問']]],
    ['查核', [['搜尋', '#/search', '全站一次查'], ['方法', '#/method', '可不可信'], ['校勘', '#/collation', '19 點'], ['限制', '#/limits', '34 條']]],
    ['自己', [['我的', '#/mine', '進度'], ['關於', '#/about', '授權與出處'], ['聯絡', '#/contact', '指正']]]
  ];
  box.appendChild(h('h2', '全站地圖'));
  box.appendChild(h('p', '按「先讀什麼、再練什麼、最後查什麼」排。每一頁的底部也有『接著看』，不會走進死路。', 'small muted'));
  var mg = h('div', '', 'grid');
  MAP.forEach(function (g) {
    var c = h('div', '', 'card');
    var hh = '<h3>' + esc(g[0]) + '</h3><ul class="map-list">';
    g[1].forEach(function (x) {
      hh += '<li><a href="' + x[1] + '">' + esc(x[0]) + '</a> <span class="small muted">' + esc(x[2]) + '</span></li>';
    });
    c.innerHTML = hh + '</ul>';
    mg.appendChild(c);
  });
  box.appendChild(mg);

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

  nextLinks(box, [['通則：這幾篇在講什麼規矩', '#/law'], ['十二經：把篇裡的經脉抽出來看', '#/meridian'], ['練這一篇的題', '#/items']]);};
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

  nextLinks(box, [['我的：看成績與正確率', '#/mine'], ['通則：題目背後的原則', '#/law'], ['限制：哪些題還待專家核', '#/limits']]);};
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

  nextLinks(box, [['通則：這些詞在哪些原則裡', '#/law'], ['十二經病候', '#/meridian'], ['練概念類題目', '#/items']]);};


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





/* ---------------- 搜尋 ---------------- */
VIEWS.search = function (box, q) {
  box.appendChild(h('h1', '搜尋'));
  box.appendChild(h('p', '全站一次查：篇、題、通則、十二經、病候、概念、校勘、九鍼、異同、十二原、五輸、經水、營氣、界限、癰疽、限制。' +
    '輸入即篩；按 <kbd>/</kbd> 任何一頁都能跳來這裡。', 'small muted'));

  var S = LS.search || [];
  var row = h('div', '', 'row');
  var inp = document.createElement('input');
  inp.type = 'search'; inp.placeholder = '例：厥、營衛、五十營、死不治…';
  inp.style.minWidth = '280px';
  inp.value = (q && q.q) || '';
  var cnt = el('span', 'small muted', '');
  row.appendChild(inp); row.appendChild(cnt);
  box.appendChild(row);
  var out = h('div', ''); box.appendChild(out);

  var VM = LS.varmap || {};
  function nz(x) { var o = ''; for (var i = 0; i < x.length; i++) o += (VM[x[i]] || x[i]); return o; }
  function render() {
    var kw = inp.value.trim();
    out.innerHTML = '';
    if (!kw) { cnt.textContent = '共 ' + S.length + ' 條索引（已含異體與繁簡對照）；輸入即篩選'; return; }
    var nk = nz(kw);
    var hits = S.filter(function (x) {
      return x.t.indexOf(kw) >= 0 || (x.d || '').indexOf(kw) >= 0 || (x.n && x.n.indexOf(nk) >= 0);
    });
    cnt.textContent = '命中 ' + hits.length + ' 條' + (hits.length >= 60 ? '（顯示前 60）' : '');
    var by = {};
    hits.slice(0, 60).forEach(function (x) { (by[x.k] = by[x.k] || []).push(x); });
    Object.keys(by).forEach(function (k) {
      var c = h('div', '', 'card');
      c.appendChild(el('h3', '', k + '（' + by[k].length + '）'));
      var ul = el('ul', 'map-list', '');
      by[k].forEach(function (x) {
        var li = el('li', '', '');
        li.innerHTML = '<a href="' + x.h + '">' + esc(x.t) + '</a>' +
          (x.d ? ' <span class="small muted">' + esc(x.d) + '</span>' : '');
        ul.appendChild(li);
      });
      c.appendChild(ul);
      out.appendChild(c);
    });
    if (!hits.length) out.appendChild(h('p', '沒有命中。試試單一個字，或換用原文的寫法（例如「脉」不是「脈」）。', 'small'));
  }
  inp.oninput = render;
  render();

  nextLinks(box, [['通則', '#/law'], ['十二經', '#/meridian'], ['題庫', '#/items']]);
};



/* ---------------- 變體：同一原則的多種寫法 ---------------- */
VIEWS.variant = function (box) {
  var D = LS.bianti || {}, groups = D['組'] || [];
  box.appendChild(h('h1', '變體：同一原則的多種寫法'));
  box.appendChild(h('p', '靈樞不是一次寫成的教科書，是不同來源的彙編。同一個原則，常在不同篇換一副說法。' +
    '這一頁把四組並排，看它換了什麼、沒換什麼。', 'lead'));

  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>怎麼看這些組</h3><ul class="small">' +
    '<li>每組不是「矛盾」，而是<b>不同的判準</b>：同一個詞，各篇用不同方式在量。</li>' +
    '<li>差異處是我（編者）的整理，標『歸』；引文照原文，可回查。</li>' +
    '<li>讀法：遇到這些詞，先問「這一段用哪把尺」，再談它的內容。</li></ul>' +
    '<p class="small muted">共 ' + groups.length + ' 組、' + (D['說明'] ? D['說明']['條數'] : '') + ' 句。</p>';
  box.appendChild(intro);

  groups.forEach(function (g) {
    var c = h('div', '', 'card');
    c.appendChild(el('h2', '', g['組']));
    c.appendChild(h('p', '<b>問題</b>：' + esc(g['問題']), 'small'));
    var t = '<tr><th style="width:96px">篇</th><th>原文</th><th style="width:34%">這一句在說什麼</th></tr>';
    (g['條'] || []).forEach(function (x) {
      t += '<tr><td class="small">' + esc(x['篇']) + '<br/><span class="src">' + esc(x['id']) + '</span></td>' +
        '<td class="small">' + esc(x['文']) + '</td><td class="small muted">' + esc(x['註']) + '</td></tr>';
    });
    var w = h('div', '', 'table-wrap'); w.innerHTML = '<table>' + t + '</table>';
    c.appendChild(w);
    c.appendChild(h('p', '<b>差在哪</b>（歸）：' + md(g['差']), 'small'));
    c.appendChild(h('p', '<b>讀時注意</b>（歸）：' + md(g['用']), 'small'));
    box.appendChild(c);
  });

  var tail = h('div', '', 'card');
  tail.innerHTML = '<h3>為什麼單獨立一頁</h3>' +
    '<p class="small">通則那一頁把「共同點」抽出來；這一頁把「不同寫法」並排。' +
    '兩者合看，才不會把靈樞讀成一本前後一致的手冊——它本來就不是。</p>' +
    '<p class="small muted">本頁只做四組；其餘可做而未做的：死期判斷的兩種寫法（日數 vs 死不治）、' +
    '刺法四套清單（工具／病位／五體／目的）、營衛的兩種計數（度與周）。</p>' +
    '<p class="small"><a href="#/law">回通則</a>　·　<a href="#/binghou">看病候</a>　·　' +
    '<a href="#/read">回通讀</a></p>';
  box.appendChild(tail);

  nextLinks(box, [['通則：共同點', '#/law'], ['病候：證候怎麼寫', '#/binghou'], ['方法：收錄狀況', '#/method']]);
};

/* ---------------- 注家：張志聰集註、張介賓類經注（節錄） ---------------- */
VIEWS.jizhu = function (box) {
  var J = LS.jizhu || {}, st = J['統計'] || {}, laws = J['通則'] || [], cases = J['例'] || [];
  box.appendChild(h('h1', '注家怎麼讀這一句'));
  box.appendChild(h('p', '同一句經文，清人張志聰逐篇作注，明人張介賓按類作注。這一頁把兩家的注' +
    '從各自的書裡分離出來、繫到經文句，只取節錄：<b>先看原文，再看注</b>。' +
    '注文是〔注〕層——不是原文，也不是本站的歸納。' +
    '65 條通則中，兩家合計有 <b>54 條</b>至少一家有注可讀。', 'lead'));

  var intro = h('div', '', 'card');
  box.appendChild(h('h2', '一、張志聰《靈樞集註》（清）'));
  intro.innerHTML = '<h3>這批注是怎麼來的</h3><ul class="small">' +
    '<li><b>來源</b>：' + esc(J['來源'] || '') + '</li>' +
    '<li><b>方法</b>：' + esc(J['方法'] || '') + '</li>' +
    '<li><b>結果</b>：81 篇逐篇比對，最低比對率 ' + (st['最低比對率'] || 0) + '%；' +
    '繫上經文句的注 <b>' + (st['有注句數'] || 0) + '</b> 條、注文 ' +
    (st['注文總字'] || 0).toLocaleString() + ' 字；其中 <b>' + (st['通則條有注'] || 0) +
    '</b> 條通則的引文有張注可對。</li>' +
    '<li><b>局限</b>：' + esc(J['局限'] || '') + '</li></ul>';
  box.appendChild(intro);

  box.appendChild(h('h3', '通則引文與張注'));
  box.appendChild(h('p', '只列「有張注可對」的條；其餘通則的引文，張志聰沒有留下可直接繫上的注。', 'small muted'));
  if (!laws.length) box.appendChild(h('p', '目前沒有可對讀的條。', 'small'));
  laws.forEach(function (t) {
    var c = h('div', '', 'card');
    c.appendChild(h('h3', '', t['n'] + '. ' + t['名'] + '　'));
    c.appendChild(h('p', '<span class="pill">' + esc(t['組'] || '') + '</span>', 'small'));
    (t['引'] || []).forEach(function (q) {
      c.appendChild(h('p', '<span class="src">' + esc(q['篇']) + '　' + esc(q['id']) + '</span>', 'small muted'));
      c.appendChild(h('div', '「' + esc(q['文']) + '」', 'quote'));
      c.appendChild(h('div', '<b>張注</b>' + esc(q['注']), 'zj-note'));
    });
    box.appendChild(c);
  });

  box.appendChild(h('h3', '八十一篇各取一條'));
  box.appendChild(h('p', '每篇取字數最多的一條注，看張志聰在這篇最用力講什麼。', 'small muted'));
  var cc = h('div', '', 'card');
  cases.forEach(function (x) {
    var d = h('div', '', 'zj-case');
    d.innerHTML = '<h3><a href="#/read?seq=' + x['序'] + '">〈' + esc(x['篇']) + '〉</a>' +
      '　<span class="src">' + esc(x['id']) + '</span></h3>' +
      '<div class="quote">「' + esc(x['文']) + '」</div>' +
      '<div class="zj-note"><b>張注</b>' + esc(x['注']) + '</div>';
    cc.appendChild(d);
  });
  box.appendChild(cc);

  var tbl = h('div', '', 'card');
  tbl.appendChild(h('h3', '逐篇注文分布'));
  tbl.appendChild(h('p', '「比對率」＝該篇集註文字中能與底本經文逐字對上的比例；比例低，代表該篇注多、或文字差異大。', 'small muted'));
  var t = '<tr><th style="width:56px">序</th><th>篇</th><th style="width:70px">注句</th>' +
    '<th style="width:80px">注字</th><th style="width:70px">比對率</th></tr>';
  (J['篇'] || []).forEach(function (x) {
    if (!x['比對率']) return;
    t += '<tr><td class="num">' + x['序'] + '</td><td><a href="#/read?seq=' + x['序'] + '">' +
      esc(x['篇']) + '</a></td><td class="num">' + Object.keys(x['注'] || {}).length +
      '</td><td class="num">' + (x['注字'] || 0) + '</td><td class="num">' + x['比對率'] + '%</td></tr>';
  });
  var w = h('div', '', 'table-wrap'); w.innerHTML = '<table>' + t + '</table>';
  tbl.appendChild(w);
  box.appendChild(tbl);

  var L = LS.leizhu || {}, lst = L['統計'] || {};
  box.appendChild(h('h2', '二、張介賓《類經》注（明）'));
  var b1 = h('div', '', 'card');
  b1.innerHTML = '<h3>這批注是怎麼來的</h3><ul class="small">' +
    '<li><b>來源</b>：' + esc(L['來源'] || '') + '</li>' +
    '<li><b>方法</b>：' + esc(L['方法'] || '') + '</li>' +
    '<li><b>結果</b>：' + (lst['卷數'] || 0) + ' 卷、注 ' + (lst['注段總數'] || 0).toLocaleString() +
    ' 段；通則引文可對注 <b>' + (lst['段'] || 0) + '</b> 段、<b>' + (lst['條'] || 0) + '</b> 條。</li>' +
    '<li><b>局限</b>：類經為四庫全書錄文，注文照錄無標點；只取引文句末 −8～+12 字內的注，' +
    '寧可少收，也不把隔壁句的注拉過來；注中「…」表示前後兩段注之間有跳接。</li></ul>';
  box.appendChild(b1);
  box.appendChild(h('h3', '通則引文與類經注'));
  box.appendChild(h('p', '與上一節同一批通則，換一家注。卷號是類經卷次——類經按類編排，沒有靈樞篇序。', 'small muted'));
  (L['條'] || []).forEach(function (t) {
    var c = h('div', '', 'card');
    c.appendChild(h('h3', '', t['n'] + '. ' + t['名'] + '　<span class="pill">' + esc(t['組'] || '') + '</span>'));
    (t['引'] || []).forEach(function (q) {
      c.appendChild(h('p', '<span class="src">類經卷 ' + q['卷'] +
        (q['類'] ? '　' + esc(q['類']) : '') + '　' + esc(q['id']) + '</span>', 'small muted'));
      c.appendChild(h('div', '「' + esc(q['文']) + '」', 'quote'));
      c.appendChild(h('div', '<b>類經注</b>' + esc(q['注']), 'zj-note'));
    });
    box.appendChild(c);
  });

  var X = LS.lingshi || {}, xs = X['統計'] || {};
  box.appendChild(h('h2', '三、丹波元簡《靈樞識》（日·江戶）'));
  var c1 = h('div', '', 'card');
  c1.innerHTML = '<h3>這批注是怎麼來的</h3><ul class="small">' +
    '<li><b>來源</b>：' + esc(X['來源'] || '') + '</li>' +
    '<li><b>體例</b>：按經文短句立條；條下先轉引馬蒔（马云）、張介賓（张云）、張志聰（志云）之說，再下己見（簡案）。</li>' +
    '<li><b>結果</b>：' + (xs['條'] || 0) + ' 條中 ' + (xs['繫上'] || 0) + ' 條對回底本句（約 ' +
    Math.round(100 * (xs['繫上'] || 0) / Math.max(1, xs['條'] || 1)) + '%）；通則引文可對注 <b>' +
    (xs['通則引'] || 0) + '</b> 段、<b>' + (xs['通則條'] || 0) + '</b> 條。</li>' +
    '<li><b>局限</b>：條目以短句立目，有些句子不立條；「马云／张云／志云」是<b>轉引</b>，' +
    '不是本站直引原書；未與影印本校。</li></ul>';
  box.appendChild(c1);
  box.appendChild(h('h3', '通則引文與靈樞識'));
  box.appendChild(h('p', '同一批通則的第三家說。注裡引到他人處，前綴已標出是誰的話——那是轉引，不是原書。', 'small muted'));
  (X['通則'] || []).forEach(function (t) {
    var c = h('div', '', 'card');
    c.appendChild(h('h3', '', t['n'] + '. ' + t['名'] + '　<span class="pill">' + esc(t['組'] || '') + '</span>'));
    (t['引'] || []).forEach(function (q) {
      c.appendChild(h('p', '<span class="src">' + esc(q['id']) + '</span>', 'small muted'));
      c.appendChild(h('div', '「' + esc(q['文']) + '」', 'quote'));
      (q['seg'] || [{ '家': '靈樞識', '文': q['注'] }]).forEach(function (sg) {
        c.appendChild(h('div', '<b>' + esc(sg['家']) + '</b>' + esc(sg['文']), 'zj-note'));
      });
    });
    box.appendChild(c);
  });

  var CV = (LS.jizhu || {})['覆蓋'] || {};
  if ((CV['條'] || []).length) {
    var cv = h('div', '', 'card');
    var cs = CV['統計'] || {};
    cv.appendChild(el('h2', '', '三家覆蓋：哪幾條有注可讀'));
    cv.appendChild(h('p', '65 條通則中，三家都有注的 ' + (cs['3'] || 0) + ' 條、兩家 ' +
      (cs['2'] || 0) + ' 條、只有一家 ' + (cs['1'] || 0) + ' 條、三家都沒有 ' + (cs['0'] || 0) + ' 條。' +
      '「有注」＝張志聰〈集註〉、張介賓〈類經注〉、丹波元簡〈靈樞識〉三家之一，能繫到該條引文。', 'small'));
    var ct = '<tr><th style="width:44px">#</th><th>通則</th><th style="width:220px">有注的家</th></tr>';
    CV['條'].forEach(function (x) {
      ct += '<tr><td class="num">' + x['n'] + '</td><td class="small">' + esc(x['名']) + '</td>' +
        '<td class="small">' + x['家'].map(function (f) { return '<span class="pill g">' + esc(f) + '</span>'; }).join(' ') + '</td></tr>';
    });
    var cw = h('div', '', 'table-wrap'); cw.innerHTML = '<table>' + ct + '</table>';
    cv.appendChild(cw);
    box.appendChild(cv);
  }

  var tail = h('div', '', 'alert');
  tail.innerHTML = '<b>怎麼用這一頁</b><span class="small" style="display:block;margin-top:6px">' +
    '注不是標準答案：兩家讀的是同一部經，他們的話可以幫你「看懂原文在說什麼」，' +
    '但不能拿來當原文的證據。要判斷一條通則站不站得住，仍回原文逐字核。</span>';
  box.appendChild(tail);

  nextLinks(box, [['通則：共同點', '#/law'], ['變體：不同寫法', '#/variant'], ['方法：收錄狀況', '#/method']]);
};

/* ---------------- 九宫八風（背景） ---------------- */
VIEWS.jiugong = function (box) {
  var D = LS.jiugong || {};
  box.appendChild(h('h1', '九宫八風：一層背景知識'));
  box.appendChild(h('p', '〈九宫八風〉不是孤立的占書，是秦漢式法與曆法的一頁。' +
    '當時的學者熟悉這一套：太一移日、九宫值日、八風從哪個方向來、傷哪一藏。' +
    '靈樞用它，就像後世醫書用陰陽五行——<b>不是拿它當命題證明，是把它當共同的語言</b>。', 'lead'));

  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>怎麼讀這一頁</h3><ul class="small">' +
    '<li><b>背景知識不等於可驗證的命題</b>：陰陽、五行、九宫都屬這一類。要求它「用靈樞內部證據驗證」是錯的標準——' +
    '背景的定義就是「不自證、只共用」。</li>' +
    '<li>但背景也分兩層：<b>格式</b>（宫名、日數、方位）與<b>推斷</b>（占君相、預測吉凶）。' +
    '前者要知道，後者可以存疑。</li>' +
    '<li>本頁把格式整理出來；占驗部分只照錄，不代為推演。</li></ul>';
  box.appendChild(intro);

  // 九宫
  var c1 = h('div', '', 'card');
  c1.appendChild(el('h2', '', '九宫與太一移日'));
  c1.appendChild(h('p', '太一以冬至起於叶蟄，每宫居若干日，再移下一宫。八宫日數：六宫四十六日、二宫四十五日。' +
    '方位依九宫通例補（標『注』），原文只給宫名與日數。', 'small'));
  var t1 = '<tr><th style="width:44px">#</th><th style="width:80px">宫</th><th style="width:70px">日數</th><th>方位（注）</th></tr>';
  (D['九宫'] || []).forEach(function (g) {
    t1 += '<tr><td>' + g['序'] + '</td><td><b>' + esc(g['宫']) + '</b></td>' +
      '<td class="num">' + g['日數'] + '</td><td class="small muted">' + esc(g['方位']) + '</td></tr>';
  });
  var w1 = h('div', '', 'table-wrap'); w1.innerHTML = '<table>' + t1 + '</table>';
  c1.appendChild(w1);
  if (D['太一']) {
    c1.appendChild(h('p', '原文（句 ' + esc(D['太一']['id']) + '）：' + esc(D['太一']['文'].slice(0, 150)) + '…', 'small muted'));
  }
  box.appendChild(c1);

  // 八風
  var c2 = h('div', '', 'card');
  c2.appendChild(el('h2', '', '八風：方位 → 風名 → 內舍 → 外在 → 氣主'));
  c2.appendChild(h('p', '這張表是全篇最可用的部分：每一風都寫明傷哪一藏、外在哪一部、其氣主何。' +
    '結構與〈五邪〉〈邪氣藏府病形〉同構。', 'small'));
  var t2 = '<tr><th style="width:52px">方位</th><th style="width:86px">風</th><th style="width:64px">內舍</th>' +
    '<th style="width:170px">外在</th><th style="width:72px">氣主</th><th>原文</th></tr>';
  (D['八風'] || []).forEach(function (f) {
    t2 += '<tr><td>' + esc(f['方位']) + '</td><td><b>' + esc(f['風']) + '</b></td>' +
      '<td>' + esc(f['內舍']) + '</td><td class="small">' + esc(f['外在']) + '</td>' +
      '<td>' + esc(f['氣主']) + '</td><td class="small">' + esc(f['文']) +
      ' <span class="src">' + esc(f['id']) + '</span></td></tr>';
  });
  var w2 = h('div', '', 'table-wrap'); w2.innerHTML = '<table>' + t2 + '</table>';
  c2.appendChild(w2);
  box.appendChild(c2);

  // 移日、三虛、避風
  var c3 = h('div', '', 'card');
  c3.appendChild(el('h2', '', '三句關鍵'));
  [['移日', '太一移日'], ['三虛', '三虛相摶'], ['避風', '避虛風']].forEach(function (k) {
    var q = D[k[0]];
    if (!q) return;
    var p = h('p', '', 'quote');
    p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) +
      '　<a href="#/read?seq=77">回原文</a></div>';
    c3.appendChild(p);
    if (k[0] === '三虛') c3.appendChild(h('p', '三虛的定義在〈歲露〉：「乘年之衰，逢月之空，失時之和，因為賊風所傷」。', 'small muted'));
  });
  box.appendChild(c3);

  var tail = h('div', '', 'card');
  tail.innerHTML = '<h3>為什麼不把它踢出去</h3>' +
    '<p class="small">如果因為『無法用靈樞內部證據驗證』就整篇排除，那陰陽、五行、藏象、營衛的循環也都不該收——' +
    '它們同樣是背景，不是推論出來的定理。<b>拒絕背景知識，讀者就讀不懂作者在引什麼。</b></p>' +
    '<p class="small">真正該做的是分層：格式要知道（宫名、日數、八風病位），' +
    '推斷可以存疑（占君相、預測吉凶）。本頁照這個原則處理。</p>' +
    '<p class="small muted">界：這是秦漢式法與曆法的背景，不是現代氣象學或流行病學；' +
    '靈樞用它，不代表它已被驗證，也不代表不能用來理解文本。</p>' +
    '<p class="small"><a href="#/law">看通則（32–34 條即出自本篇）</a>　·　' +
    '<a href="#/read?seq=77">讀〈九宫八風〉全文</a>　·　<a href="#/read?seq=79">讀〈歲露論〉</a></p>';
  box.appendChild(tail);

  nextLinks(box, [['通則：虛風與三虛', '#/law'], ['歲露論：月滿月空', '#/read?seq=79'], ['方法：收錄狀況', '#/method']]);
};

/* ---------------- 字根 ---------------- */
VIEWS.binghou = function (box) {
  var D = LS.binghou || {}, groups = D['組'] || [];
  box.appendChild(h('h1', '病候：四組模板'));
  box.appendChild(h('p', '靈樞的病候篇章共用一個寫法：<b>病名 → 其候 → 治法或死生</b>。' +
    '這一頁把四組並排，不是要你記病名，是要你看見這個寫法本身在示範什麼。', 'lead'));

  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>怎麼看這些條目</h3><ul class="small">' +
    '<li><b>其候</b>是原文對證候的描述，不是定義；同一病名在別篇的寫法可能不同。</li>' +
    '<li><b>治法</b>只照抄原文的取經與手法名稱，本站不提供操作。</li>' +
    '<li>凡標「死不治」「旦發夕死」的，是靈樞把界限寫進病候裡的地方——那比治法更值得注意。</li></ul>' +
    '<p class="small muted">共 ' + groups.length + ' 組、' + (D['說明'] ? D['說明']['條數'] : '') + ' 條；' +
    '取捨只收了厥頭痛、厥心痛、衆痹周痹、五種脹。其餘病候未收，不假裝收齊。</p>';
  box.appendChild(intro);

  groups.forEach(function (g) {
    var c = h('div', '', 'card');
    c.appendChild(el('h2', '', g['組'] + '（〈' + g['篇'] + '〉）'));
    (g['條'] || []).forEach(function (x) {
      var item = h('div', '', 'bh-item');
      item.appendChild(el('h3', '', x['病']));
      (x['證'] || []).forEach(function (q) {
        var p = h('p', '', 'quote');
        p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) + '　' +
          '<a href="#/read?seq=' + esc(q['id'].split('-')[0]) + '">回原文</a></div>';
        item.appendChild(p);
      });
      (x['治'] || []).forEach(function (q) {
        var p = h('p', '', 'small');
        p.innerHTML = '<b>治</b>：' + esc(q['文']) + ' <span class="src">句 ' + esc(q['id']) + '</span>';
        item.appendChild(p);
      });
      if (x['註']) item.appendChild(h('p', '要點：' + esc(x['註']), 'small muted'));
      c.appendChild(item);
    });
    box.appendChild(c);
  });

  var AB = LS.abscess || {};
  if ((AB['癰疽'] || []).length) {
    var ac = h('div', '', 'card');
    ac.appendChild(el('h2', '', '癰疽：部位與死期'));
    ac.appendChild(h('p', '〈癰疽〉十五個病名，九個有明確死期。這裡只列部位、病名、死期——治法與形狀留在原文段裡。', 'small'));
    var at = '<tr><th style="width:36px">#</th><th style="width:96px">名</th><th style="width:120px">部位</th>' +
      '<th style="width:90px">死期</th><th>原文</th></tr>';
    (AB['癰疽'] || []).forEach(function (x) {
      var d = x['死期句'] ? esc(x['死期句']['文'].slice(0, 46)) + '… <span class="src">' + esc(x['死期句']['id']) + '</span>' : '<span class="small muted">原文未給死期</span>';
      at += '<tr><td>' + x['序'] + '</td><td><b>' + esc(x['名']) + '</b></td><td class="small">' + esc(x['部位']) + '</td>' +
        '<td>' + (x['死期'] ? '<b>' + esc(x['死期']) + '</b>' : '—') + '</td><td class="small">' + d + '</td></tr>';
    });
    ac.innerHTML += '<table>' + at + '</table>';
    if (AB['通則']) {
      ac.appendChild(h('p', '通則：' + esc(AB['通則']['文']) + ' <span class="src">句 ' + esc(AB['通則']['id']) + '</span>', 'small'));
    }
    ac.appendChild(h('p', '九個死期裡，最短半日、最長十歲；其餘六個原文沒給。不補。', 'small muted'));
    box.appendChild(ac);
  }

  var tail = h('div', '', 'card');
  tail.innerHTML = '<h3>這個模板告訴你什麼</h3>' +
    '<p class="small">① 病名先於證候，但證候才是判斷依據；② 治法幾乎都落在「取某經某穴」，' +
    '不講劑量與手法；③ 有幾條直接寫死生（真頭痛、真心痛），靈樞不迴避。</p>' +
    '<p class="small">同一組內並排看，會發現厥頭痛六條各配不同經——這是「辨位」的示範；' +
    '厥心痛五條以五藏命名——這是「辨藏」的示範。</p>' +
    '<p class="small"><a href="#/law">回通則</a>　·　<a href="#/meridian">看十二經</a>　·　' +
    '<a href="#/limits">看能力邊界</a></p>';
  box.appendChild(tail);
};

/* ---------------- 十二經（四套通道） ---------------- */
VIEWS.meridian = function (box, q) {
  var tab = (q && q.tab) || 'jing';
  var TABS = [['jing', '十二經脉'], ['bie', '十二經别'], ['jin', '十二經筋'],
              ['luo', '十五絡'], ['shui', '十二經水'], ['shu', '五輸'],
              ['yuan', '十二原'], ['yw', '營衛']];
  box.appendChild(h('h1', '經脉諸層：六套寫法，同一個身體'));
  box.appendChild(h('p', '靈樞講「身體是通道」，用的不是一套圖：經脉是幹道，經别是內部接頭，' +
    '經筋是結聚，絡脉是浮而可見的別出，經水是把十二經比作十二條水道，五輸是每經的井滎腧經合。' +
    '六套模板不同，能回答的問題也不同。', 'lead'));

  var tabRow = h('div', '', 'row');
  TABS.forEach(function (t) {
    var a = el('a', 'btn' + (t[0] === tab ? '' : ' ghost'), t[1]);
    a.href = '#/meridian?tab=' + t[0];
    tabRow.appendChild(a);
  });
  box.appendChild(tabRow);

  if (tab === 'bie') return renderBie(box);
  if (tab === 'shui') return renderShui(box);
  if (tab === 'yuan') return renderYuan(box);
  if (tab === 'yw') return renderYingwei(box);
  if (tab === 'shu') return renderShu(box);
  if (tab === 'jin') return renderJin(box);
  if (tab === 'luo') return renderLuo(box);
  return renderJing(box, q);
};

function renderJing(box, q) {
  var M = LS.mer || {};
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>經脉：一經六句的模板</h3><ul class="small">' +
    '<li>起止 → 是動則病 → 是主所生病 → 虛實 → 治法 → 脉口人迎。</li>' +
    '<li><b>是動則病</b>：經氣異常的第一組反應；<b>是主所生病</b>：這一經所主的病，常涉藏府。</li>' +
    '<li>共 ' + (M['經'] || []).length + ' 經；動候 ' +
    (M['經'] || []).reduce(function (a, x) { return a + (x['動數'] || 0); }, 0) + ' 項、生病 ' +
    (M['經'] || []).reduce(function (a, x) { return a + (x['生數'] || 0); }, 0) + ' 項（以逗號斷句計）。</li>' +
    '<li>本頁不含取穴與操作；要動手，需師授。</li></ul>';
  box.appendChild(intro);

  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:40px">#</th><th>經</th><th style="width:60px">動</th><th style="width:60px">所生</th><th>是動則病（前段）</th></tr>';
  (M['經'] || []).forEach(function (x) {
    var d = (x['是動'] ? x['是動']['文'] : '').split('是動則病')[1] || '';
    t.innerHTML += '<tr><td>' + x['序'] + '</td><td><a href="#/meridian?tab=jing&n=' + x['序'] + '">' + esc(x['經']) + '</a></td>' +
      '<td class="num">' + (x['動數'] || 0) + '</td><td class="num">' + (x['生數'] || 0) + '</td>' +
      '<td class="small">' + esc(d.slice(0, 42)) + (d.length > 42 ? '…' : '') + '</td></tr>';
  });
  box.appendChild(h('p', '表 經脉-1　證候數以逗號斷句計，與後世條文數不同。', 'small muted'));
  box.appendChild(t);

  (M['經'] || []).forEach(function (x) {
    var c = h('div', '', 'card mer-card');
    c.setAttribute('id', 'mer' + x['序']);
    c.appendChild(el('h2', '', x['序'] + '、' + x['經']));
    [['起止', '起止'], ['是動', '是動則病'], ['所生病', '是主所生病'], ['虛實', '氣盛／氣虛'],
     ['治法', '治法'], ['脉口', '脉口與人迎']].forEach(function (pair) {
      var k = pair[0];
      if (!x[k]) return;
      var d = h('div', '', 'mer-row');
      d.innerHTML = '<span class="mer-k">' + pair[1] + '</span>' +
        '<span class="mer-v">' + esc(x[k]['文']) + '</span>' +
        '<span class="src">句 ' + esc(x[k]['id']) + '　<a href="#/read?seq=' + (x[k]['id'].split('-')[0]) + '">回原文</a></span>';
      c.appendChild(d);
    });
    box.appendChild(c);
  });
  if (q && q.n) { var el0 = document.getElementById('mer' + q.n); if (el0 && el0.scrollIntoView) el0.scrollIntoView({ block: 'start' }); }
}

function renderBie(box) {
  var D = LS.jingbie || {}, rows = D['正'] || [];
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>經别：離合出入</h3>' +
    '<p class="small">〈經别〉問的是「離合出入」：十二正經各自別出一支，走到身體深處與表裡經相合。' +
    '十二正配成六組，每組稱「一合」。它不講穴位、講的是內部的接頭。</p>' +
    '<p class="small muted">共 ' + rows.length + ' 正、' + (rows.length / 2) + ' 合。文句照抄原文。</p>';
  box.appendChild(intro);
  var by = {};
  rows.forEach(function (x) { (by[x['合']] = by[x['合']] || []).push(x); });
  Object.keys(by).forEach(function (k) {
    var c = h('div', '', 'card mer-card');
    c.appendChild(el('h2', '', '第 ' + k + ' 合'));
    by[k].forEach(function (x) {
      var d = h('div', '', 'mer-row');
      d.innerHTML = '<span class="mer-k">' + esc(x['經']) + '</span>' +
        '<span class="mer-v">' + esc(x['文'].replace(/^○/, '')) + '</span>' +
        '<span class="src">句 ' + esc(x['id']) + '　<a href="#/read?seq=11">回原文</a></span>';
      c.appendChild(d);
    });
    box.appendChild(c);
  });
  box.appendChild(h('p', '經别的走向是內部接合，不是體表路線；不要與經脉圖混讀。', 'small muted'));
}

function renderJin(box) {
  var D = LS.jingjin || {}, rows = D['筋'] || [];
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>經筋：結聚與轉筋</h3>' +
    '<p class="small">〈經筋〉每條都從四肢寫到頭面，用的是「結于某處」——它講的是筋的結聚點，不是氣血流注。' +
    '病候以「其病…」開頭，治法固定一句：' +
    '『治在燔鍼劫刺，以知爲數，以痛爲輸』，最後給一個季節性的名字（仲春痺、孟春痺…）。</p>' +
    '<p class="small muted">共 ' + rows.length + ' 筋。本頁不提供操作。</p>';
  box.appendChild(intro);
  rows.forEach(function (x) {
    var c = h('div', '', 'card mer-card');
    c.setAttribute('id', 'jin' + x['序']);
    c.appendChild(el('h2', '', x['序'] + '、' + x['經'] + '之筋'));
    [['起止', '起止'], ['病', '其病'], ['治', '治則與命名']].forEach(function (pair) {
      var k = pair[0];
      if (!x[k]) return;
      var d = h('div', '', 'mer-row');
      d.innerHTML = '<span class="mer-k">' + pair[1] + '</span>' +
        '<span class="mer-v">' + esc(x[k]['文'].replace(/^○/, '')) + '</span>' +
        '<span class="src">句 ' + esc(x[k]['id']) + '　<a href="#/read?seq=13">回原文</a></span>';
      c.appendChild(d);
    });
    (x['附'] || []).forEach(function (y) {
      var d = h('div', '', 'mer-row');
      d.innerHTML = '<span class="mer-k">附</span><span class="mer-v">' + esc(y['文'].replace(/^○/, '')) + '</span>' +
        '<span class="src">句 ' + esc(y['id']) + '</span>';
      c.appendChild(d);
    });
    box.appendChild(c);
  });
  box.appendChild(h('p', '經筋的病候多為轉筋、腫痛、拘急——與經脉的「是動／所生病」寫法明顯不同。', 'small muted'));
}

function renderLuo(box) {
  var D = LS.luomai || {}, rows = D['絡'] || [];
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>十五絡：浮而可見的那一層</h3>' +
    '<p class="small">〈經脉〉說『諸脉之浮而常見者，皆絡脉也』。十五別各有一個穴名，' +
    '病候固定寫成「實則…，虛則…，取之所別」。</p>' +
    '<p class="small muted">共 ' + rows.length + ' 別（十二經之別 + 任、督、脾之大絡）。</p>';
  box.appendChild(intro);
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:40px">#</th><th style="width:120px">別</th><th style="width:76px">穴</th><th>起止</th><th style="width:34%">病候（實／虛）</th></tr>';
  rows.forEach(function (x) {
    t.innerHTML += '<tr><td>' + x['序'] + '</td><td class="small">' + esc(x['別']) + '</td>' +
      '<td>' + esc(x['穴']) + '</td>' +
      '<td class="small">' + esc(x['起止'] ? x['起止']['文'].replace(/^○/, '') : '') + '</td>' +
      '<td class="small">' + esc(x['病'] ? x['病']['文'].replace(/^○/, '') : '') + '</td></tr>';
  });
  box.appendChild(t);
  if (D['總結']) {
    var c = h('div', '', 'card');
    c.innerHTML = '<p class="quote">' + esc(D['總結']['文']) + '<div class="src">——〈經脉〉 · 句 ' + esc(D['總結']['id']) + '</div></p>';
    box.appendChild(c);
  }
  box.appendChild(h('p', '刺絡的具體做法（刺結上、寫其邪出其血）需師授，本頁不列。', 'small muted'));
}


function renderShui(box) {
  var D = LS.jingshui || {}, rows = D['水'] || [], dep = D['刺深'] || {};
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>經水：把十二經比作十二條水道</h3>' +
    '<p class="small">〈經水〉的邏輯是「外合於水，內屬於藏府」：十二經各配一條河，' +
    '再從水的大小深淺推到刺的深淺與灸的壯數。</p>' +
    '<p class="small muted">共 ' + rows.length + ' 條對應。這是比附，不是測量；原文自己說「此一隅之陰陽也」。</p>';
  box.appendChild(intro);

  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:40px">#</th><th style="width:120px">經</th><th style="width:90px">水</th><th style="width:110px">內屬</th><th>原文</th></tr>';
  rows.forEach(function (x) {
    t.innerHTML += '<tr><td>' + x['序'] + '</td><td>' + esc(x['經']) + '</td><td><b>' + esc(x['水']) + '</b></td>' +
      '<td class="small">' + esc(x['內屬']) + '</td><td class="small">' + esc(x['文']) +
      ' <a href="#/read?seq=12">回原文</a></td></tr>';
  });
  box.appendChild(t);

  if ((dep['足'] || []).length) {
    var c = h('div', '', 'card');
    c.appendChild(el('h3', '', '刺深與留呼：足六經有數，手經一律從簡'));
    var t2 = '<tr><th style="width:110px">經</th><th style="width:80px">深</th><th style="width:80px">留</th><th>原文</th></tr>';
    dep['足'].forEach(function (x) {
      t2 += '<tr><td>' + esc(x['經']) + '</td><td class="num">' + x['深'] + ' 分</td><td class="num">' + x['留'] + ' 呼</td>' +
        '<td class="small">' + esc(x['文']) + '</td></tr>';
    });
    var tw = h('div', '', 'table-wrap'); tw.innerHTML = '<table>' + t2 + '</table>';
    c.appendChild(tw);
    ['手', '法天之常', '過度之害'].forEach(function (k) {
      if (!dep[k]) return;
      var p = h('p', '', 'small');
      p.innerHTML = (k === '手' ? '<b>手之陰陽</b>：' : k === '法天之常' ? '<b>法天之常</b>：' : '<b>過度之害</b>：') +
        esc(dep[k]['文']) + ' <span class="src">句 ' + esc(dep[k]['id']) + '</span>';
      c.appendChild(p);
    });
    c.appendChild(h('p', '這些數字是本篇的規定，不是現代操作標準；本站不提供操作。', 'small muted'));
    box.appendChild(c);
  }
  box.appendChild(h('p', '<a href="#/read?seq=12">讀〈經水〉全文</a>', 'small'));
}

function renderShu(box) {
  var D = LS.wushu || {}, rows = D['輸'] || [];
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>五輸：井、滎、腧、經、合</h3>' +
    '<p class="small">〈本輸〉一經一句，句內用「；」分五段：井→滎→腧→經→合。' +
    '陽經在腧與經之間多一個「原」。原文只用兩個字交代每穴的位置，其餘靠師授。</p>' +
    '<p class="small muted">共 ' + rows.length + ' 經（五藏五＋六府六）。' +
    '心主（心包）的五輸不在〈本輸〉——這是原文的實況，不是漏抄。</p>';
  box.appendChild(intro);

  var order = ['井', '滎', '腧', '原', '經', '合'];
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:130px">經</th>' + order.map(function (k) { return '<th>' + k + '</th>'; }).join('') + '</tr>';
  rows.forEach(function (x) {
    var cells = order.map(function (k) {
      var v = x['五輸'][k];
      return '<td' + (v ? '' : ' class="muted small"') + '>' + (v ? esc(v['穴']) : '—') + '</td>';
    }).join('');
    t.innerHTML += '<tr><td>' + esc(x['經']) + '</td>' + cells + '</tr>';
  });
  box.appendChild(t);
  box.appendChild(h('p', '表 五輸-1　陰經無「原」穴，以腧為原；陽經另有原穴。', 'small muted'));

  rows.forEach(function (x) {
    var c = h('div', '', 'card mer-card');
    c.appendChild(el('h2', '', x['經']));
    order.forEach(function (k) {
      var v = x['五輸'][k];
      if (!v) return;
      var d = h('div', '', 'mer-row');
      d.innerHTML = '<span class="mer-k">' + k + '</span><span class="mer-v">' + esc(v['文'].replace(/^○/, '')) + '</span>' +
        '<span class="src">句 ' + esc(x['id']) + '</span>';
      c.appendChild(d);
    });
    box.appendChild(c);
  });
  box.appendChild(h('p', '<a href="#/read?seq=2">讀〈本輸〉全文</a>', 'small'));
}


function renderYuan(box) {
  var D = LS.shier_yuan || {}, rows = D['原'] || [];
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>十二原：五藏之氣的十二個出口</h3>' +
    '<p class="small">〈九鍼十二原〉先立原則：『五藏有六府，六府有十二原，十二原出於四闗，四闗主治五藏』' +
    '『五藏有疾，當取之十二原』。然後才列穴。</p>' +
    '<p class="small muted">五藏之原各二（左右），加膏之原、肓之原各一，合 ' +
    (D['說明'] ? D['說明']['合計'] : 12) + ' 原。這是算術，不是修辭——原文自己給的「二」「一」。</p>';
  box.appendChild(intro);

  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:56px">藏</th><th style="width:96px">屬性</th><th style="width:90px">原</th><th style="width:56px">數</th><th>原文</th></tr>';
  rows.forEach(function (x) {
    t.innerHTML += '<tr><td>' + esc(x['藏']) + '</td><td class="small">' + esc(x['屬性']) + '</td>' +
      '<td><b>' + esc(x['原']) + '</b></td><td class="num">' + x['數'] + '</td>' +
      '<td class="small">' + esc(x['文']) + ' <a href="#/read?seq=1">回原文</a></td></tr>';
  });
  box.appendChild(t);

  if ((D['原則'] || []).length) {
    var c = h('div', '', 'card');
    c.appendChild(el('h3', '', '原文的四句理由'));
    (D['原則'] || []).forEach(function (q) {
      var p = h('p', '', 'quote');
      p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) + '</div>';
      c.appendChild(p);
    });
    box.appendChild(c);
  }
  box.appendChild(h('p', '原穴用於五藏之疾的診與治，具體操作需師授；本頁只列關係。', 'small muted'));
}

function renderYingwei(box) {
  var D = LS.yingwei || {};
  var intro = h('div', '', 'card');
  intro.innerHTML = '<h3>營衛：一晝夜的兩張表</h3>' +
    '<p class="small">營在脉中，衛在脉外；衛氣一日一夜五十周於身，晝行陽二十五、夜行陰二十五。' +
    '營氣則按十二經的次序周流。兩張表共用一個前提：<b>五十而復大會</b>。</p>';
  box.appendChild(intro);

  var c1 = h('div', '', 'card');
  c1.appendChild(el('h2', '', '定義'));
  (D['定義'] || []).forEach(function (q) {
    var p = h('p', '', 'quote');
    p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) + '　<a href="#/read?seq=18">回原文</a></div>';
    c1.appendChild(p);
  });
  box.appendChild(c1);

  var c2 = h('div', '', 'card');
  c2.appendChild(el('h2', '', '衛氣：晝二十五、夜二十五'));
  ((D['衛氣'] || {})['總數'] || []).forEach(function (q) {
    var p = h('p', '', 'quote');
    p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) + '　<a href="#/read?seq=76">回原文</a></div>';
    c2.appendChild(p);
  });
  c2.appendChild(el('h3', '', '平旦出於目：一日的路線'));
  ((D['衛氣'] || {})['平旦'] || []).forEach(function (q, i) {
    var p = h('p', '', 'small');
    p.innerHTML = '<b>' + (i + 1) + '</b>　' + esc(q['文'].replace(/^是故/, '')) +
      ' <span class="src">句 ' + esc(q['id']) + '</span>';
    c2.appendChild(p);
  });
  c2.appendChild(el('h3', '', '夜行五藏：腎→心→肺→肝→脾→復注於腎'));
  ((D['衛氣'] || {})['夜行'] || []).forEach(function (q) {
    var p = h('p', '', 'small');
    p.innerHTML = esc(q['文']) + ' <span class="src">句 ' + esc(q['id']) + '</span>';
    c2.appendChild(p);
  });
  box.appendChild(c2);

  var c25 = h('div', '', 'card');
  c25.appendChild(el('h2', '', '候時而刺：時間是操作條件'));
  c25.appendChild(h('p', '〈衛氣行〉最後一段把「什麼時候刺」寫成一套刻度：以平旦為紀、以夜盡為始、一日一夜水下百刻。' +
    '這段話也是通則第 36 條「逢時」的依據。', 'small'));
  ((D['衛氣'] || {})['候時'] || []).forEach(function (q) {
    var p = h('p', '', 'quote');
    p.innerHTML = esc(q['文']) + '<div class="src">句 ' + esc(q['id']) + '　<a href="#/read?seq=76">回原文</a></div>';
    c25.appendChild(p);
  });
  box.appendChild(c25);

  var c3 = h('div', '', 'card');
  c3.appendChild(el('h2', '', '營氣：十二經次序'));
  c3.appendChild(h('p', '〈營氣〉的原文是一段連續敘述；下表是編者依原文提煉的步驟（標『歸』），' +
    '每一列都附出處句，可回原文核。', 'small muted'));
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:40px">步</th><th style="width:130px">經</th><th>原文依據</th></tr>';
  ((D['營氣'] || {})['次序'] || []).forEach(function (x) {
    t.innerHTML += '<tr><td>' + esc(x['步']) + '</td><td>' + esc(x['經']) + '</td>' +
      '<td class="small">' + esc(x['據']) + ' <span class="src">' + esc(x['id']) + '</span></td></tr>';
  });
  box.appendChild(t);
  ((D['營氣'] || {})['原文'] || []).forEach(function (q) {
    var p = h('p', '', 'small muted');
    p.innerHTML = '原文（句 ' + esc(q['id']) + '）：' + esc(q['文'].length > 120 ? q['文'].slice(0, 120) + '…' : q['文']);
    c3.appendChild(p);
  });
  box.appendChild(c3);
  box.appendChild(h('p', '營衛的時刻表是原文的推演，不是現代生理時鐘；本頁不做臨床推論。', 'small muted'));
}

/* ---------------- 通則 ---------------- *//* ---------------- 通則 ---------------- */
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
    rt.appendChild(el('h2', '', '從哪讀起：' + (L['路徑'] || []).length + ' 站'));
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
        var prac = '';
        if (x['相關題'] && x['相關題']['數']) {
          var ov = x['相關題']['重疊'] || 0;
          prac = '　·　相關練習 <a href="#/items?seq=' + x['相關題']['篇'][0] + '">' +
            x['相關題']['數'] + ' 題</a>' +
            (ov ? '（引文重疊 ' + ov + ' 題）' : '（無引文重疊）');
        }
        art.appendChild(h('p', '回原文：' + seqs.map(function (p) {
          return '<a href="#/read?seq=' + p[0] + '">〈' + esc(p[1]) + '〉</a>';
        }).join('　') + prac, 'small'));
        if ((x['類經'] || []).length) {
          var vols = {}, vlist = [];
          (x['類經'] || []).forEach(function (y) { if (!vols[y['卷']]) { vols[y['卷']] = 1; vlist.push(y['卷']); } });
          art.appendChild(h('p', '《類經》亦收此段（卷 ' + vlist.sort(function (a, b) { return a - b; }).join('、') +
            '）；張介賓按類編排，故只給卷號。', 'small muted'));
        }
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
    '<a href="#/meridian">看十二經病候</a>　·　<a href="#/limits">看本站的能力邊界</a></p>';
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

  nextLinks(box, [['十二經：鍼刺的對象', '#/meridian'], ['校勘：毫鍼長度的差異', '#/collation'], ['方法：本站可不可信', '#/method']]);

  var W = LS.wuci || {};
  if ((W['刺'] || []).length) {
    var c2 = h('div', '', 'card');
    c2.appendChild(el('h2', '', '五刺：以應五藏'));
    c2.appendChild(h('p', '〈官鍼〉先說『凡刺有五，以應五藏』，再逐條給名字與取法。' +
      '五刺的對應很乾淨：皮—肺、脉—心、筋—肝、肌—脾、骨—腎。', 'small'));
    var t2 = h('table', '');
    t2.innerHTML = '<tr><th style="width:44px">#</th><th style="width:84px">刺</th><th style="width:52px">應</th><th>原文</th></tr>';
    (W['刺'] || []).forEach(function (x) {
      t2.innerHTML += '<tr><td>' + x['序'] + '</td><td><b>' + esc(x['名']) + '</b></td>' +
        '<td>' + esc(x['應']) + '</td><td class="small">' + esc(x['文'].replace(/^[一二三四五]曰/, '')) +
        ' <span class="src">句 ' + esc(x['id']) + '</span></td></tr>';
    });
    c2.appendChild(t2);
    c2.appendChild(h('p', '五刺是「按病位選刺法」的清單，與九鍼（按工具）不同層次；本頁照原文，不示範操作。', 'small muted'));
    box.appendChild(c2);
  }};

/* ---------------- 方法 ---------------- */
VIEWS.method = function (box) {
  box.appendChild(h('h1', '方法與校勘'));
  box.appendChild(h('p', '這一頁回答「這本書可不可信」。完整方法見 docs/01、33、82、88。', 'small muted'));
  var c = h('div', '', 'card');
  c.innerHTML = '<h3>校勘（' + (LS.collation || []).length + ' 點）</h3>' +
    '<p class="small">三源並排（底本／太素／類經）另成一頁；覆蓋率的原始數字在 data/三源覆蓋率.json。</p>' +
    '<a class="btn ghost" href="#/collation">看三源並排 →</a>';
  box.appendChild(c);
  var CM = LS.covmap || {};
  if (CM['統計']) {
    var cc = h('div', '', 'card');
    cc.appendChild(el('h2', '', '八十一篇的收錄狀況'));
    cc.appendChild(h('p', '這一頁回答「這本書可不可信」；也該回答「這本書做到哪」。' +
      '統計：' + CM['統計']['篇'] + ' 篇中，有解讀層（通則／病候／經脉諸層／概念／模組）的 ' +
      CM['統計']['有解讀層'] + ' 篇，只有題目、還沒有解讀層的 <b>' + CM['統計']['只有題'] + '</b> 篇。', 'small'));
    var only = (CM['只有題的篇'] || []);
    if (only.length) {
      cc.appendChild(h('p', '只有題目的篇（下一批挖掘清單）：', 'small muted'));
      var ul = el('ul', 'map-list', '');
      only.forEach(function (x) {
        var li = el('li', '', '');
        li.innerHTML = '<a href="#/read?seq=' + x['序'] + '">' + esc(x['篇']) + '</a>';
        ul.appendChild(li);
      });
      cc.appendChild(ul);
    }
    cc.appendChild(h('p', '「只有題目」不等於沒價值：題庫已可練；缺的是把該篇的原則抽成通則、或把病候收進病候頁。', 'small muted'));
    var ZJ = LS.zhujia || {};
    if ((ZJ['注家'] || []).length) {
      var zc = h('div', '', 'card');
      zc.appendChild(el('h2', '', '注家見證本：用了誰、還缺誰'));
      zc.appendChild(h('p', '本站的規矩：未入庫者不得引用其文；入庫者須能逐字回查。所以下面把「已入庫」與「未入庫」分開寫。', 'small'));
      var zt = '<tr><th style="width:150px">注家</th><th style="width:50px">時代</th><th style="width:130px">狀態</th>' +
        '<th>用途與缺口</th></tr>';
      (ZJ['注家'] || []).forEach(function (x) {
        var ok = x['狀態'].indexOf('已入庫') === 0;
        zt += '<tr><td><b>' + esc(x['名']) + '</b></td><td class="small">' + esc(x['時代']) + '</td>' +
          '<td class="small">' + (ok ? '<span class="pill g">已入庫</span>' : '<span class="pill y">未入庫</span>') +
          '<br/>' + esc(x['狀態'].replace(/^[^（]*（?|）/g, '')) + '</td>' +
          '<td class="small">' + esc(x['用途']) + '<br/><span class="muted">缺：' + esc(x['缺口']) + '</span>' +
          (x['注意'] ? '<br/><span class="muted">注意：' + esc(x['注意']) + '</span>' : '') + '</td></tr>';
      });
      var zw = h('div', '', 'table-wrap'); zw.innerHTML = '<table>' + zt + '</table>';
      zc.appendChild(zw);
      zc.appendChild(h('p', '清·張志聰《靈樞集註》已去注分經入庫：772 條注繫到經文句，' +
        '20 條通則有注可對。<a href="#/jizhu">看「集註」頁</a>。注文只取節錄，未與影印本逐字校。', 'small muted'));
      box.appendChild(zc);
    }

    var hold = (CM['背景層'] || []);
    if (hold.length) {
      cc.appendChild(h('h3', '背景層：不抽通則，但有專頁', 'small'));
      hold.forEach(function (x) {
        cc.appendChild(h('p', '<a href="#/read?seq=' + x['序'] + '">〈' + esc(x['篇']) + '〉</a>　' +
          esc(x['處理']), 'small'));
        cc.appendChild(h('p', esc(x['理由']), 'small muted'));
      });
    }
    box.appendChild(cc);

    var lines = CM['任務線'] || [];
    if (lines.length) {
      var lc = h('div', '', 'card');
      lc.appendChild(el('h2', '', '七條任務線：一條一條挖'));
      lc.appendChild(h('p', '八十一篇不是同時挖的。分成七條線，逐線處理；每條線的進度由「篇是否已有解讀層」算出，不是手填。', 'small'));
      var lt = '<tr><th style="width:120px">線</th><th style="width:150px">說明</th><th style="width:64px">進度</th><th>篇（✓＝已有解讀層）</th></tr>';
      lines.forEach(function (l) {
        var ps = (l['篇'] || []).map(function (x) {
          return '<a href="#/read?seq=' + x['序'] + '">' + esc(x['篇']) + '</a>' + (x['狀態'] === '有' ? '✓' : '');
        }).join('、');
        lt += '<tr><td><b>' + esc(l['線']) + '</b></td><td class="small">' + esc(l['說明']) + '</td>' +
          '<td class="num">' + l['已'] + '／' + l['共'] + '</td><td class="small">' + ps + '</td></tr>';
      });
      var lw = h('div', '', 'table-wrap'); lw.innerHTML = '<table>' + lt + '</table>';
      lc.appendChild(lw);
      box.appendChild(lc);
    }
  }

  box.appendChild(h('h2', '矛盾（' + (LS.contradictions || []).length + '）'));
  var t2 = h('table', '');
  t2.innerHTML = '<tr><th style="width:48px">#</th><th>爭點</th><th style="width:80px">判定</th></tr>';
  (LS.contradictions || []).forEach(function (r) {
    t2.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.point) + '</td><td>' + esc(r.verdict) + '</td></tr>';
  });
  box.appendChild(t2);

  nextLinks(box, [['校勘：19 條三源並排', '#/collation'], ['限制：34 條能力邊界', '#/limits'], ['異同：與素問的比較', '#/suwen']]);};

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

  var JY = LS.jiayi || {};
  if ((JY['篇'] || []).length) {
    var jc = h('div', '', 'card');
    var js = JY['統計'] || {};
    jc.appendChild(el('h2', '', '甲乙經：靈樞各篇落在哪一卷哪一篇'));
    jc.appendChild(h('p', '《針灸甲乙經》把靈樞、素問按病類重編，是最早的同類編本。' +
      '這裡不談「甲乙經收了哪些篇」，只算一件事：靈樞各篇的正文，在甲乙經的哪一篇裡重合最多。' +
      '重合率＝該篇 4-gram 出現在該甲乙篇的比例；低於 30% 表示甲乙經刪改較多，或本法不適用。', 'small'));
    jc.appendChild(h('p', '81 篇都有落點，其中 <b>' + (js['重合≥30%'] || 0) + '</b> 篇重合 ≥30%；' +
      '通則引文能在甲乙經找到逐字同文的只有 <b>' + (js['通則引有落點'] || 0) + '</b> 段（' +
      (js['通則條有落點'] || 0) + ' 條）——甲乙經多是改寫引用，逐字同文少。', 'small muted'));
    var jt = '<tr><th style="width:44px">序</th><th>靈樞篇</th><th style="width:60px">甲乙卷</th>' +
      '<th>甲乙篇</th><th style="width:64px">重合</th></tr>';
    (JY['篇'] || []).forEach(function (x) {
      var m = x['主'] || {};
      jt += '<tr><td class="num">' + x['序'] + '</td><td class="small">' + esc(x['篇']) + '</td>' +
        '<td class="num">' + (m['卷'] || '—') + '</td><td class="small">' + esc(m['篇'] || '—') + '</td>' +
        '<td class="num">' + (x['重合'] || 0) + '%</td></tr>';
    });
    var jw = h('div', '', 'table-wrap'); jw.innerHTML = '<table>' + jt + '</table>';
    jc.appendChild(jw);
    jc.appendChild(h('p', '注意：這是「文字重合最多的篇」，不等於歷史上甲乙經作者的自注出處；' +
      '甲乙經與靈樞的篇次對應需逐條建立，本頁只做第一步。', 'small muted'));
    box.appendChild(jc);
  }

  nextLinks(box, [['限制：還沒解決的', '#/limits'], ['方法：稽核怎麼做', '#/method'], ['回原文對照', '#/read']]);};

/* ---------------- 限制 ---------------- */
VIEWS.limits = function (box) {
  box.appendChild(h('h1', '已知限制'));
  var sg = h('div', '', 'alert');
  sg.innerHTML = '<b>' + esc(LS.meta.safety) + '</b>';
  box.appendChild(sg);
  box.appendChild(h('p', '先說不能做什麼。完整清單見 data/能力邊界.csv。', 'small muted'));

  var B = LS.bounds || {};
  if ((B['級'] || []).length) {
    var bc = h('div', '', 'card');
    bc.appendChild(el('h2', '', '靈樞自己怎麼分界限'));
    bc.appendChild(h('p', '本站的「能力邊界」是自己的；靈樞也有它的——分別在五種說法上。' +
      '下面只按字面收，不替它引申。', 'small'));
    var bt = '<tr><th style="width:32px">級</th><th style="width:120px">說法</th><th style="width:56px">句數</th>' +
      '<th>說明</th><th style="width:34%">例</th></tr>';
    (B['級'] || []).forEach(function (g) {
      var ex = (g['例'] || []).slice(0, 2).map(function (x) {
        return '<span class="small">' + esc(x['文'].slice(0, 40)) + '… <span class="src">' + esc(x['id']) + '</span></span>';
      }).join('<br/>');
      bt += '<tr><td><b>' + esc(g['級']) + '</b></td><td>' + esc(g['名']) + '</td>' +
        '<td class="num">' + g['數'] + '</td><td class="small">' + esc(g['說明']) + '</td><td>' + ex + '</td></tr>';
    });
    bc.innerHTML += '<table>' + bt + '</table>';
    bc.appendChild(h('p', '合 ' + ((B['說明'] || {})['條數'] || '') + ' 句；一句只歸一級（A→F→B→D→C→E），' +
      '所以數字互斥、可相加。', 'small muted'));
    if (B['時限單位']) {
      var u = B['時限單位'];
      bc.appendChild(h('p', 'F 級的時限單位：日 ' + (u['日'] || 0) + '、年 ' + (u['年'] || 0) +
        '、歲 ' + (u['歲'] || 0) + '、旦夕 ' + (u['旦夕'] || 0) +
        '——幾乎全部以「日」計，年與歲只各一句。靈樞的預後是短尺度的。', 'small'));
    }
    box.appendChild(bc);
  }
  var t = h('table', '');
  t.innerHTML = '<tr><th style="width:52px">#</th><th>問題</th><th style="width:70px">範疇</th><th style="width:44px">級</th></tr>';
  (LS.limits || []).forEach(function (r) {
    t.innerHTML += '<tr><td>' + esc(r.id) + '</td><td>' + esc(r.issue) + '</td><td class="small">' + esc(r.cat) + '</td><td>' + esc(r.sev) + '</td></tr>';
  });
  box.appendChild(t);
  box.appendChild(h('p', '三項最要緊：臨床主張未驗證、15 條答案為整理語、6 道案例題待專家核。', 'small'));

  nextLinks(box, [['方法：校勘與矛盾', '#/method'], ['指正與聯絡', '#/contact'], ['我的：進度與正確率', '#/mine']]);};

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

  nextLinks(box, [['通讀：繼續讀', '#/read'], ['題庫：繼續練', '#/items'], ['限制：知道邊界', '#/limits']]);};

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
  box.appendChild(h('p', 'small', '<a href="#/contact">✉️ 看到錯、想指正，或要問授權範圍 →</a>　·　' +
    '<a href="#/home">全站地圖（首頁）</a>'));
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

  nextLinks(box, [['回限制', '#/limits'], ['看關於', '#/about'], ['回首頁地圖', '#/home']]);};

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
function focusSearch() {
  if (location.hash.indexOf('#/search') !== 0) location.hash = '#/search';
  setTimeout(function () {
    var i = document.querySelector('input[type=search]');
    if (i) i.focus();
  }, 30);
}
document.addEventListener('keydown', function (e) {
  var t = e.target || {};
  if (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT') return;
  if (e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
    e.preventDefault(); focusSearch();
  }
});

function boot() {
  var nav = $('#nav');
  NAV.forEach(function (x) {
    if (x[2]) nav.appendChild(el('span', 'nav-sep', ''));
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

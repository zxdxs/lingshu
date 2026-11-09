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

function fold(title, open) {
  var d = document.createElement('details');
  d.className = 'fold';
  if (open) d.open = true;
  var sm = document.createElement('summary');
  sm.textContent = title;
  d.appendChild(sm);
  return d;
}

function nextLinks(box, links) {
  var d = h('div', '', 'next');
  d.innerHTML = '<span class="next-k">接著看</span>' + (links || []).map(function (x) {
    return '<a href="' + x[1] + '">' + x[0] + '</a>';
  }).join('');
  box.appendChild(d);
}

var NAV = [
  ['home', '首頁'],
  ['grp', '讀', [['read', '通讀 81 篇'], ['recite', '誦讀'], ['jizhu', '注家'], ['meridian', '十二經'],
                  ['binghou', '病候'], ['variant', '變體'], ['jiugong', '九宫八風']]],
  ['grp', '學', [['map', '81 篇地圖'], ['path', '學習路徑'], ['themes', '五個主題'], ['law', '通則 65 條'], ['module', '模組（一篇一卡）']]],
  ['grp', '練', [['items', '題庫'], ['concept', '概念卡'], ['prep', '九鍼']]],
  ['grp', '校', [['collation', '校勘'], ['naming', '名訓層'], ['suwen', '異同'], ['govern', '治理與預算'], ['limits', '限制']]],
  ['grp', '更多', [['search', '搜尋'], ['method', '方法'], ['mine', '我的'], ['about', '關於'], ['contact', '指正與聯絡']]]
];
var VIEWS = {};

/* ---------------- 首頁 ---------------- */
VIEWS.home = function (box) {
  var hero = h('div', '', 'hero');
  hero.innerHTML =
    '<div class="kicker">中醫典籍導讀 · 黃帝內經</div>' +
    '<h1>靈樞經</h1>' +
    '<p class="lead">八十一篇原文、逐句可回查；讀得下去、練得起來、也讀出聲。' +
    '<b>先選一扇門</b>，其餘都在頁尾的地圖裡。</p>' +
    '<div class="row" style="margin-top:14px">' +
      '<a class="btn" href="#/read">讀原文</a>' +
      '<a class="btn ghost" href="#/recite">誦讀</a>' +
      '<a class="btn ghost" href="#/items">練題</a>' +
      '<a class="btn ghost" href="#/path">依路徑</a>' +
    '</div>';
  box.appendChild(hero);

  var safe = h('div', '', 'alert');
  safe.innerHTML = '<b>' + esc(LS.meta.safety) + '</b>' +
    '<span class="small" style="display:block;margin-top:6px">本站的題目、模組與案例只用原文證候作情境，' +
    '不提供劑量、療程或操作步驟；任何臨床處置請由指導醫師決定。</span>';
  box.appendChild(safe);

  var DOORS = [
    ['讀', '一篇一篇讀，每句可回查', [['通讀 81 篇', '#/read'], ['誦讀（出聲）', '#/recite'], ['注家節錄', '#/jizhu']]],
    ['學', '先看骨幹，再看細節', [['81 篇地圖', '#/map'], ['學習路徑', '#/path'], ['通則 65 條', '#/law'], ['五個主題', '#/themes'], ['模組（一篇一卡）', '#/module']]],
    ['練', '作答、對答案、回原文', [['題庫 ' + stat('items') + ' 題', '#/items'], ['概念卡 12 張', '#/concept'], ['九鍼', '#/prep']]],
    ['校', '哪些可信、哪裡還沒解決', [['校勘', '#/collation'], ['名訓層（穴名）', '#/naming'], ['異同（靈樞 vs 素問）', '#/suwen'], ['治理與預算', '#/govern'], ['限制 34 條', '#/limits']]]
  ];
  var dg = h('div', '', 'grid');
  DOORS.forEach(function (d) {
    var c = h('div', '', 'card');
    var hh = '<h3><span class="pill b">' + esc(d[0]) + '</span> ' + esc(d[1]) + '</h3><ul class="map-list">';
    d[2].forEach(function (x) { hh += '<li><a href="' + x[1] + '">' + esc(x[0]) + '</a></li>'; });
    c.innerHTML = hh + '</ul>';
    dg.appendChild(c);
  });
  box.appendChild(dg);

  var stats = h('div', '', 'stats');
  var segn = ((LS.reading || {})['統計'] || {}).段 || 0;
  stats.innerHTML = '<div class="stat"><b>' + stat('pian') + '</b><span>篇</span></div>' +
    '<div class="stat"><b>' + stat('chars').toLocaleString() + '</b><span>經文字</span></div>' +
    '<div class="stat"><b>' + segn + '</b><span>段（含段旨）</span></div>' +
    '<div class="stat"><b>' + stat('items') + '</b><span>題</span></div>' +
    '<div class="stat"><b>' + stat('quote_seg') + '</b><span>逐字核過的引文段</span></div>';
  box.appendChild(stats);

  box.appendChild(h('h2', '全部頁面'));
  box.appendChild(h('p', '依「讀、學、練、校」分組；導覽列也是同一套分組。', 'small muted'));
  var MAP = [
    ['讀', [['通讀 81 篇', '#/read', '原文＋段旨＋注'], ['誦讀', '#/recite', '系統語音、以段為單位'],
            ['注家', '#/jizhu', '張志聰／張介賓／楊上善／丹波元簡'],
            ['十二經', '#/meridian', '六套通道'], ['病候', '#/binghou', '證候怎麼寫'],
            ['變體', '#/variant', '同一原則的多種寫法'], ['九宫八風', '#/jiugong', '背景知識']]],
    ['學', [['81 篇地圖', '#/map', '十一組'], ['學習路徑', '#/path', '三條路線'], ['五個主題', '#/themes', '五個斜切'],
            ['通則', '#/law', ((LS.law || {})['條數'] || 0) + ' 條'], ['模組', '#/module', '81 篇一篇一卡']]],
    ['練', [['題庫', '#/items', stat('items') + ' 題'], ['概念', '#/concept', '12 張'], ['九鍼', '#/prep', '九種鍼']]],
    ['校', [['校勘', '#/collation', '三源並排＋甲乙經'], ['名訓層', '#/naming', '穴名怎麼訓'],
            ['異同', '#/suwen', '靈樞 vs 素問'],
            ['治理', '#/govern', '未決登記簿＋預算'], ['限制', '#/limits', '34 條']]],
    ['更多', [['搜尋', '#/search', '全站一次查'], ['方法', '#/method', '稽核怎麼做'],
             ['我的', '#/mine', '進度'], ['關於', '#/about', '授權與出處'], ['指正與聯絡', '#/contact', '回報一處']]]
  ];
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

  var no = h('div', '', 'card');
  no.innerHTML = '<h3>兩句話说完本站的邊界</h3>' +
    '<p class="small">原文一律取自底本，每句可回查；題目、模組、通則都是編者整理（標〔歸〕），不是原文。' +
    '臨床主張未經驗證，<b>不可據以施治</b>。</p>' +
    '<p class="small"><a href="#/limits">已知限制</a>　·　<a href="#/govern">治理與未決</a>　·　' +
    '<a href="#/about">授權與出處</a>　·　<a href="#/contact">回報</a></p>';
  box.appendChild(no);
};

/* ---------------- 誦讀（以段為單位） ---------------- */
VIEWS.recite = function (box, q) {
  var R = LS.recite || [];
  if (!R.length) { box.appendChild(h('p', '誦讀資料未載入。', 'small')); return; }
  var seq = parseInt((q && q.seq) || STATE.reciteSeq || 1, 10) || 1;
  var P = null;
  R.forEach(function (x) { if (x.seq === seq) P = x; });
  if (!P) { P = R[0]; seq = P.seq; }
  STATE.reciteSeq = seq; save();
  var DZ = ((LS.reading || {}).段旨 || {}).篇 || {};
  var dz = {};
  (DZ[String(seq)] || []).forEach(function (z) { dz[z.d] = z.旨; });
  var SEG = (((LS.reading || {}).閱讀段 || {}).篇 || {})[String(seq)] || null;
  var sid2pd = {};
  if (SEG) SEG.forEach(function (g) { (g.sids || []).forEach(function (sid) { sid2pd[sid] = g.pd; }); });

  box.appendChild(h('h1', '誦讀：一段一段讀出聲'));
  box.appendChild(h('p', '以<b>段落</b>為單位，不再一句一停：一段讀完，留一點白，再進下一段。' +
    '用的是<b>這台機器的系統語音</b>：不預錄音檔、可離線、速度可調；發音與斷句不是定本，遇到多音字請以紙本音釋為準。', 'lead'));

  var paras = [], byD = {};
  (P.sents || []).forEach(function (s) {
    var d = sid2pd[s.id] || s.d || 1;
    if (!byD[d]) { byD[d] = { d: d, sents: [] }; paras.push(byD[d]); }
    byD[d].sents.push(s);
  });
  paras.sort(function (a, b) { return a.d - b.d; });
  // 長段誦讀時按句群分口氣（不改變原文分段）；避免四十、九十句一口氣讀完
  var readParas = [];
  paras.forEach(function (pa) {
    var n = pa.sents.length, size = n > 12 ? Math.ceil(n / Math.ceil(n / 6)) : n;
    if (n <= 8) { pa.part = 1; pa.parts = 1; readParas.push(pa); return; }
    var parts = Math.ceil(n / size);
    for (var k = 0; k < parts; k++) {
      readParas.push({ d: pa.d, sents: pa.sents.slice(k * size, (k + 1) * size),
                       part: k + 1, parts: parts });
    }
  });

  var card = h('div', '', 'card');
  var sel = document.createElement('select');
  sel.className = 'recite-sel';
  R.forEach(function (x) {
    var o = document.createElement('option');
    o.value = x.seq; o.textContent = x.seq + '. ' + x.name;
    if (x.seq === seq) o.selected = true;
    sel.appendChild(o);
  });
  var row1 = h('div', '', 'recite-row');
  row1.appendChild(sel);
  var rate = document.createElement('select');
  [0.7, 0.8, 0.9, 1, 1.1, 1.2].forEach(function (v) {
    var o = document.createElement('option');
    o.value = v; o.textContent = '速度 ' + v + '×';
    if (String(v) === String(STATE.reciteRate || 0.9)) o.selected = true;
    rate.appendChild(o);
  });
  row1.appendChild(rate);
  var loop = document.createElement('label');
  loop.className = 'small';
  var loopCb = document.createElement('input'); loopCb.type = 'checkbox';
  loop.appendChild(loopCb); loop.appendChild(document.createTextNode(' 循環本篇'));
  row1.appendChild(loop);
  var pyLb = document.createElement('label');
  pyLb.className = 'small';
  var pyCb = document.createElement('input'); pyCb.type = 'checkbox';
  pyCb.checked = STATE.recitePy !== false;
  pyLb.appendChild(pyCb); pyLb.appendChild(document.createTextNode(' 拼音'));
  row1.appendChild(pyLb);
  card.appendChild(row1);

  var row2 = h('div', '', 'recite-row');
  var btnPlay = el('button', 'btn', '▶ 播放'); btnPlay.type = 'button';
  var btnPrev = el('button', 'btn ghost', '↑ 上一段'); btnPrev.type = 'button';
  var btnNext = el('button', 'btn ghost', '↓ 下一段'); btnNext.type = 'button';
  var btnAgain = el('button', 'btn ghost', '↻ 重讀本段'); btnAgain.type = 'button';
  [btnPlay, btnPrev, btnNext, btnAgain].forEach(function (b) { row2.appendChild(b); });
  var status = h('span', '', 'small muted');
  row2.appendChild(status);
  card.appendChild(row2);

  var list = h('div', '', 'recite-list' + (pyCb.checked ? '' : ' no-py'));
  var CJK = /[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/;
  function withPinyin(t, py) {
    if (!py) return esc(t);
    var sy = py.split(' ');
    var k = 0, out = '';
    for (var i = 0; i < t.length; i++) {
      var ch = t.charAt(i);
      if (CJK.test(ch) && sy[k]) {
        out += '<ruby>' + esc(ch) + '<rt>' + esc(sy[k]) + '</rt></ruby>';
        k++;
      } else {
        out += esc(ch);
      }
    }
    return out;
  }
  readParas.forEach(function (pa, i) {
    var d = h('div', '', 'recite-para');
    d.setAttribute('data-i', i);
    var head = h('div', '', 'recite-phead');
    head.innerHTML = '<span class="pill b">段 ' + pa.d +
      (pa.parts > 1 ? ' · ' + pa.part + '/' + pa.parts : '') + '</span>' +
      (dz[pa.d] ? '<span class="recite-pzhi">' + esc(dz[pa.d]) + '</span>' : '') +
      '<span class="small muted">' + pa.sents.length + ' 句</span>';
    d.appendChild(head);
    pa.sents.forEach(function (s) {
      var p = h('p', '', 'recite-line');
      p.innerHTML = '<span class="recite-sid">' + esc(s.id) + '</span>' + withPinyin(s.t, s.p);
      d.appendChild(p);
    });
    d.onclick = function (ev) {
      if (ev.target && ev.target.tagName === 'A') return;
      highlight(i);
      if (playing) {
        stop();
        playing = true;
        btnPlay.textContent = '⏸ 暫停';
        speak(i);
      }
    };
    list.appendChild(d);
  });
  card.appendChild(list);
  pyCb.onchange = function () {
    STATE.recitePy = pyCb.checked; save();
    list.className = 'recite-list' + (pyCb.checked ? '' : ' no-py');
  };
  box.appendChild(card);

  var note = h('div', '', 'card');
  note.innerHTML = '<h3>怎麼用</h3><ul class="small">' +
    '<li>按「播放」從目前段落開始；一段讀完會停約 0.35 秒，再進下一段。點任何一段，可從那一段起讀。</li>' +
    '<li>超過八句的長段，誦讀時按句群分「口氣」（如段 1 · 2/5），只為換氣，不改變原文分段。</li>' +
    '<li>上一段／下一段用滑桿或按鈕；「重讀本段」適合反覆跟讀一段。</li>' +
    '<li>段首的短句是<b>編者段旨（歸）</b>，不是原文；用來提示這一段在做什麼，讀完可自己改寫。</li>' +
    '<li>拼音由程式生成（帶聲調），多音字與古讀只校了常見幾條；不是定本，遇疑處請以紙本音釋與字典為準。</li>' +
    '<li>本站不提供人聲錄音；系統語音的發音也不是定本，音釋層（罕字反切）沒有唸進來。</li></ul>';
  box.appendChild(note);

  var synth = window.speechSynthesis;
  var zh = [], cur = 0, playing = false, pend = null;

  function pickVoices() {
    var all = (synth && synth.getVoices) ? synth.getVoices() : [];
    var cand = all.filter(function (v) {
      return /^(zh|cmn)/i.test(v.lang || '') || /chinese|中文|國語|普通话/i.test(v.name || '');
    });
    cand.sort(function (a, b) {
      function w(v) {
        var l = (v.lang || '').toLowerCase();
        if (l.indexOf('tw') >= 0) return 0;
        if (l.indexOf('hk') >= 0) return 1;
        return 2;
      }
      return w(a) - w(b);
    });
    zh = cand;
    if (!synth) setStatus('此瀏覽器不支援語音合成；仍可手動逐段閱讀。');
    else if (!zh.length) setStatus('系統還沒有回報中文語音：可在系統設定安裝（macOS：系統設定 → 輔助使用 → 語音內容），裝好後重開本頁。');
    else setStatus('準備好：' + zh[0].name + '（' + zh[0].lang + '）');
  }
  function setStatus(msg) { status.textContent = msg; }
  function highlight(i) {
    Array.prototype.forEach.call(list.children, function (n, k) {
      n.className = 'recite-para' + (k === i ? ' on' : '');
    });
    var n = list.children[i];
    if (n && n.scrollIntoView) n.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
  function stop() {
    playing = false;
    btnPlay.textContent = '▶ 播放';
    if (pend) { clearTimeout(pend); pend = null; }
    if (synth) synth.cancel();
  }
  function speak(i) {
    if (!synth) { setStatus('此瀏覽器沒有語音合成（speechSynthesis）'); return; }
    if (i < 0) i = 0;
    if (i >= readParas.length) {
      if (loopCb.checked) { i = 0; } else { stop(); setStatus('讀完了（' + readParas.length + ' 口氣）'); return; }
    }
    cur = i;
    highlight(i);
    var text = readParas[i].sents.map(function (s) { return s.t; }).join('');
    var u = new SpeechSynthesisUtterance(text);
    u.lang = 'zh-TW';
    u.rate = parseFloat(rate.value) || 0.9;
    if (zh.length) u.voice = zh[0];
    u.onend = function () {
      if (!playing) return;
      pend = setTimeout(function () { if (playing) speak(cur + 1); }, 350);
    };
    u.onerror = function () { setStatus('語音中斷（可能是系統語音問題）'); };
    synth.cancel();
    synth.speak(u);
    setStatus('第 ' + (i + 1) + ' / ' + readParas.length + ' 口氣（段 ' + readParas[i].d + '，' + readParas[i].sents.length + ' 句）');
  }
  btnPlay.onclick = function () {
    if (!synth) return;
    playing = !playing;
    if (playing) { btnPlay.textContent = '⏸ 暫停'; speak(cur); }
    else { stop(); setStatus('已暫停'); }
  };
  btnPrev.onclick = function () { stop(); cur = Math.max(0, cur - 1); highlight(cur); };
  btnNext.onclick = function () { stop(); cur = Math.min(readParas.length - 1, cur + 1); highlight(cur); };
  btnAgain.onclick = function () { stop(); playing = true; btnPlay.textContent = '⏸ 暫停'; speak(cur); };
  sel.onchange = function () { stop(); location.hash = '#/recite?seq=' + sel.value; };
  rate.onchange = function () { STATE.reciteRate = parseFloat(rate.value); save(); };

  pickVoices();
  if (synth && synth.addEventListener) synth.addEventListener('voiceschanged', pickVoices);
  highlight(0);

  nextLinks(box, [['讀原文（段旨＋注＋音義）', '#/read?seq=' + seq], ['注家怎麼讀', '#/jizhu'], ['學習路徑', '#/path']]);
};

/* ---------------- 主題 ---------------- */
VIEWS.themes = function (box) {
  box.appendChild(h('h1', '靈樞在講什麼'));
  var note = h('div', '', 'card');
  note.innerHTML = '<b>先說清楚</b>：以下五個主題的<b>劃分與命名是編者所加</b>，不是《靈樞》原有的分類；' +
    '它們是<b>斜切</b>五刀，只各取幾篇，不是八十一篇的完整分組。完整分組見 <a href="#/map">81 篇地圖（十一組）</a>。' +
    '原文只提供材料；每一條主張下面都附原文與句 ID，讀者可以不同意這個分法，直接讀原文。';
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

/* ---------------- 81 篇地圖（十一組） ---------------- */
VIEWS.map = function (box) {
  var GD = LS.groups || {};
  var G = (GD.組 || []).slice().sort(function (a, b) { return parseInt(a.id.slice(1), 10) - parseInt(b.id.slice(1), 10); });
  if (!G.length) { box.appendChild(h('p', '分組資料未載入。', 'small')); return; }
  var maxN = Math.max.apply(null, G.map(function (g) { return g.篇.length; }));
  var COL = ['#7a5c3e', '#8a6a3f', '#6d7a4a', '#4f7a6a', '#4a6d84', '#6a5a88', '#8a4f5a', '#9a7040', '#5a7a8a', '#7a6a50', '#6a6a6a'];

  box.appendChild(h('h1', '81 篇地圖：十一組'));
  box.appendChild(h('p', '把八十一篇按「讀它要做什麼」分成十一組。分組取自本專案的學習模組規劃，' +
    '名、主旨與讀法是編者整理（歸），<b>不是《靈樞》原有的分類</b>；原書次序仍可從卷次讀。', 'lead'));

  var stats = h('div', '', 'stats');
  stats.innerHTML = '<div class="stat"><b>' + GD.篇數 + '</b><span>篇</span></div>' +
    '<div class="stat"><b>' + GD.組數 + '</b><span>組</span></div>' +
    '<div class="stat"><b>' + ((LS.law || {})['條數'] || 0) + '</b><span>通則</span></div>' +
    '<div class="stat"><b>' + ((LS.reading || {})['統計'] || {}).段 + '</b><span>段</span></div>';
  box.appendChild(stats);

  var chart = h('div', '', 'card');
  chart.innerHTML = '<h2>十一組的篇數</h2><div class="hbars">' + G.map(function (g, i) {
    return '<a class="hbar" href="#/read?g=' + g.id + '" title="' + esc(g.名) + '">' +
      '<span class="hbar-k"><b>' + g.id + '</b> ' + esc(g.名) + '</span>' +
      '<i style="width:' + Math.round(g.篇.length / maxN * 100) + '%;background:' + COL[i % COL.length] + '"></i>' +
      '<span class="hbar-v">' + g.篇.length + ' 篇 · ' + g.題數 + ' 題</span></a>';
  }).join('') + '</div><p class="small muted">長條＝該組篇數；點一組可只讀那一組。' +
    '分組不平均是故意的：病證各論本來就最多，經絡與刺法是兩條主幹。</p>';
  box.appendChild(chart);

  var grid = h('div', '', 'card');
  var cells = '';
  G.forEach(function (g, i) {
    g.篇.forEach(function (seq) {
      var p = bySeq(seq);
      if (!p) return;
      cells += '<a class="gcell" href="#/read?seq=' + seq + '" title="' + esc(g.id + ' ' + g.名 + ' · ' + p.name) +
        '" style="border-top-color:' + COL[i % COL.length] + '">' + seq + '<span>' + esc(p.name.slice(0, 3)) + '</span></a>';
    });
  });
  grid.innerHTML = '<h2>八十一篇一覽</h2><div class="ggrid">' + cells + '</div>' +
    '<div class="legend">' + G.map(function (g, i) {
      return '<span><i style="background:' + COL[i % COL.length] + '"></i>' + g.id + ' ' + esc(g.名) + '</span>';
    }).join('') + '</div>';
  box.appendChild(grid);

  G.forEach(function (g, i) {
    var c = h('div', '', 'card gcard');
    c.style.borderTop = '4px solid ' + COL[i % COL.length];
    var ps = g.篇.map(function (seq) {
      var p = bySeq(seq);
      return '<a class="pill" href="#/read?seq=' + seq + '">' + seq + '. ' + esc(p.name) + '</a>';
    }).join('');
    var rules = (g.通則 || []).slice(0, 10).map(function (x) {
      return '<a href="#/law?n=' + x.n + '">' + x.n + '. ' + esc(x.名) + '</a>';
    }).join('、');
    c.innerHTML = '<div class="small muted">' + g.id + '　' + g.篇.length + ' 篇 · ' +
      g.字數.toLocaleString() + ' 字 · ' + g.題數 + ' 題</div>' +
      '<h2 style="margin:.2em 0">' + esc(g.名) + '</h2>' +
      '<p><b>' + esc(g.主旨) + '</b></p>' +
      '<p class="small muted">讀法：' + esc(g.讀法) + '</p>' +
      '<div class="row">' + ps + '</div>' +
      (g.概念 && g.概念.length ? '<p class="small">概念：' + g.概念.map(function (x) {
        return '<a class="pill" href="#/concept">' + esc(x) + '</a>';
      }).join('') + '</p>' : '') +
      (rules ? '<p class="small">相關通則：' + rules + ((g.通則 || []).length > 10 ? '…' : '') + '</p>' : '');
    box.appendChild(c);
  });

  var tb = h('div', '', 'card');
  var tr = '<tr><th>組</th><th>篇</th><th>字</th><th>題</th><th>通則數</th><th>通則（前五）</th></tr>';
  G.forEach(function (g) {
    tr += '<tr><td><a href="#/read?g=' + g.id + '">' + g.id + ' ' + esc(g.名) + '</a></td>' +
      '<td class="num">' + g.篇.length + '</td><td class="num">' + g.字數.toLocaleString() + '</td>' +
      '<td class="num">' + g.題數 + '</td><td class="num">' + (g.通則 || []).length + '</td>' +
      '<td class="small">' + (g.通則 || []).slice(0, 5).map(function (x) { return x.n + '. ' + esc(x.名); }).join('、') + '</td></tr>';
  });
  tb.innerHTML = '<h2>組 × 通則</h2><p class="small muted">通則可跨組；這裡算的是「這一組的篇被哪些通則引用」。' +
    '同一條通則可能在多組出現，這正是它成為通則的理由。</p><div class="table-wrap"><table>' + tr + '</table></div>';
  box.appendChild(tb);

  var note = h('div', '', 'card');
  note.innerHTML = '<h3>怎麼用</h3><ul class="small">' +
    '<li>第一次讀：照 M0 → M1 → M2 走，先建立骨架；之後挑一組有興趣的讀。</li>' +
    '<li>要查病：直接跳 M6 病證各論；要查刺法：M4；要查診斷：M5。</li>' +
    '<li>五個「斜切主題」（身體、氣血、病從外入、病的表現、判斷）不是分組，是穿過多組的閱讀軸，見<a href="#/themes">五個主題</a>。</li>' +
    '<li>每篇的段旨、校勘、音義與四家注在<a href="#/read?seq=1">通讀</a>頁；題目可一鍵跳回原文。</li></ul>';
  box.appendChild(note);

  nextLinks(box, [['通讀 81 篇', '#/read'], ['五個主題（斜切）', '#/themes'], ['通則 65 條', '#/law']]);
};

/* ---------------- 通讀（段旨＋校勘＋音義＋四家注） ---------------- */
VIEWS.read = function (box, q) {
  if (q.seq) return readOne(box, parseInt(q.seq, 10), q);
  box.appendChild(h('h1', '通讀 81 篇'));
  box.appendChild(h('p', '按<b>十一個學習模組</b>分組（編者整理，非原書分類）；每篇進去，會看到逐段主旨、' +
    '校勘、音義與四家注。你也可以完全不理分組，用搜尋或卷次找篇。', 'lead'));
  var G = (LS.groups && LS.groups.組) || [];
  G = G.slice().sort(function (a, b) { return parseInt(a.id.slice(1), 10) - parseInt(b.id.slice(1), 10); });

  var row = h('div', '', 'row');
  var gs = document.createElement('select');
  gs.appendChild(new Option('全部分組', ''));
  G.forEach(function (g) { gs.appendChild(new Option(g.id + ' ' + g.名 + '（' + g.篇.length + '）', g.id)); });
  if (q.g) gs.value = q.g;
  var sel = document.createElement('select');
  sel.appendChild(new Option('全部卷', ''));
  (LS.juan || []).forEach(function (j) { sel.appendChild(new Option(j.label + '（' + j.n + ' 篇）', j.no)); });
  var inp = document.createElement('input'); inp.type = 'search'; inp.placeholder = '搜篇名、分組…';
  var note = el('span', 'small muted', '');
  row.appendChild(inp); row.appendChild(gs); row.appendChild(sel); row.appendChild(note);
  box.appendChild(row);

  var pb = h('div', ''); box.appendChild(pb);
  var list = h('div', ''); box.appendChild(list);

  function render() {
    list.innerHTML = '';
    var kw = inp.value.trim(), gf = gs.value, jf = sel.value, total = 0, shown = 0;
    G.forEach(function (g) {
      if (gf && g.id !== gf) return;
      var ps = g.篇.map(bySeq).filter(Boolean).filter(function (p) {
        if (jf !== '' && String(p.juan) !== jf) return false;
        if (kw && !(p.name.indexOf(kw) >= 0 || g.名.indexOf(kw) >= 0 || g.id.indexOf(kw) >= 0)) return false;
        return true;
      });
      total += ps.length;
      if (!ps.length) return;
      shown++;
      var d = document.createElement('details');
      d.className = 'gsec'; d.open = true;
      var sm = document.createElement('summary');
      sm.innerHTML = '<span class="gid">' + esc(g.id) + '</span> <b>' + esc(g.名) + '</b>' +
        ' <span class="small muted">' + ps.length + ' 篇 · ' + g.字數.toLocaleString() + ' 字</span>';
      d.appendChild(sm);
      var desc = el('p', 'small muted', g.主旨);
      d.appendChild(desc);
      var gl = h('div', '', 'glist');
      ps.forEach(function (p) {
        var read = STATE.read && STATE.read[p.seq];
        var it = h('div', '', 'tiao');
        it.innerHTML = '<span class="no">' + p.seq + '</span>' +
          '<a href="#/read?seq=' + p.seq + '">' + esc(p.name) + '</a>' +
          ' <span class="small muted">' + (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字 · ' + (p.items || 0) + ' 題</span>' +
          (read ? ' <span class="pill g">已讀</span>' : '');
        gl.appendChild(it);
      });
      d.appendChild(gl);
      list.appendChild(d);
    });
    var all = Object.keys(STATE.read || {}).length;
    pb.innerHTML = bar(all, (LS.pian || []).length) + '<div class="small muted">全書已讀 ' + all + '/' +
      (LS.pian || []).length + '　·　本次顯示 ' + total + ' 篇、' + shown + ' 組' +
      (total === 0 ? '（試試清除搜尋）' : '') + '</div>';
  }
  inp.oninput = render; gs.onchange = render; sel.onchange = render; render();

  if (q.g) {
    var g0 = G.filter(function (g) { return g.id === q.g; })[0];
    if (g0) {
      var intro = h('div', '', 'card');
      intro.innerHTML = '<span class="gid">' + esc(g0.id) + '</span> <b>' + esc(g0.名) + '</b>' +
        '<p>' + esc(g0.主旨) + '</p><p class="small muted">讀法：' + esc(g0.讀法) + '</p>' +
        '<p class="small"><a href="#/map">看完整地圖</a>　·　<a href="#/law">這一組的通則</a></p>';
      if (box.insertBefore) box.insertBefore(intro, row); else box.appendChild(intro);
    }
  }

  nextLinks(box, [['81 篇地圖：十一組怎麼分', '#/map'], ['通則：這幾篇在講什麼規矩', '#/law'],
    ['注家：四家怎麼讀', '#/jizhu']]);
};

function readOne(box, seq, q) {
  seq = parseInt(seq, 10);
  var p = bySeq(seq);
  if (!p) { box.appendChild(h('p', '本篇不存在。')); return; }
  var RD = LS.reading || {};
  var DZ = ((RD.段旨 || {}).篇 || {})[String(seq)] || [];
  var dz = {};
  DZ.forEach(function (z) { dz[z.d] = z; });
  var SEG = ((RD.閱讀段 || {}).篇 || {})[String(seq)] || null;
  var sid2pd = {};
  if (SEG) SEG.forEach(function (g) { (g.sids || []).forEach(function (sid) { sid2pd[sid] = g.pd; }); });
  var NOTES = (RD.注 || {}).句 || {};
  var YIN = (RD.音義 || {}).句 || {};
  var COLL = RD.校勘 || {};
  var CBYQ = COLL.句 || {}, CBYP = COLL.篇 || {};
  var JZ = COLL.夾註 || {};
  var R = (LS.recite || []).filter(function (x) { return x.seq === seq; })[0];
  var sents = (R && R.sents) || [];
  var paras = [], byD = {};
  sents.forEach(function (s) {
    var d = sid2pd[s.id] || s.d || 1;
    if (!byD[d]) { byD[d] = { d: d, sents: [] }; paras.push(byD[d]); }
    byD[d].sents.push(s);
  });
  paras.sort(function (a, b) { return a.d - b.d; });
  var grp = (LS.groups && LS.groups.組 || []).filter(function (g) { return g.id === p.g; })[0];

  var crumb = h('p', '', 'crumb');
  crumb.innerHTML = '<a href="#/read">通讀</a> / <a href="#/read?g=' + esc(p.g || '') + '">' +
    esc((p.g || '') + ' ' + (p.gname || '')) + '</a> / ' + esc(p.name);
  box.appendChild(crumb);
  box.appendChild(h('h1', p.name));
  box.appendChild(h('p', (p.juan ? '卷' + p.juan + ' · ' : '') + p.chars + ' 字 · ' +
    sents.length + ' 句 · ' + paras.length + ' 段 · ' + (p.items || 0) + ' 題', 'small muted'));

  var row = h('div', '', 'row');
  var b = el('button', 'btn', STATE.read && STATE.read[p.seq] ? '已讀 ✓' : '標為已讀'); b.type = 'button';
  var b2 = el('button', 'btn ghost', '← 回通讀'); b2.type = 'button';
  var b3 = el('a', 'btn ghost', '看本篇題目'); b3.href = '#/items?seq=' + p.seq;
  var b4 = el('a', 'btn ghost', '誦讀本篇'); b4.href = '#/recite?seq=' + p.seq;
  var b5 = el('button', 'btn ghost', '只讀原文'); b5.type = 'button';
  var b6 = el('button', 'btn ghost', '展開全部注'); b6.type = 'button';
  var b7 = el('button', 'btn ghost', '顯示句ID'); b7.type = 'button';
  b.onclick = function () { STATE.read = STATE.read || {}; STATE.read[p.seq] = 1; save(); b.textContent = '已讀 ✓'; };
  b2.onclick = function () { location.hash = '#/read'; };
  row.appendChild(b); row.appendChild(b2); row.appendChild(b3); row.appendChild(b4); row.appendChild(b5); row.appendChild(b6); row.appendChild(b7);
  box.appendChild(row);

  if (q.sid || q.d) {
    var al = h('div', '', 'alert anchor-alert');
    var sid0 = q.sid || '';
    al.innerHTML = '<b>已定位到題目原文</b>　' +
      (sid0 ? '句 ' + esc(sid0) + '　' : '') +
      '<a href="#/read?seq=' + p.seq + '">清除定位，讀全篇</a>';
    box.appendChild(al);
  }

  var grid = h('div', '', 'read-grid');
  var side = h('aside', 'read-side');
  var sc = h('div', '', 'card');
  var navh = '<h3>段目錄</h3><ol class="duan-nav">';
  paras.forEach(function (pa) {
    var z = dz[pa.d];
    navh += '<li><a href="#d' + pa.d + '" data-d="' + pa.d + '"><b>段 ' + pa.d + '</b>' +
      '<span>' + esc((z && z.旨) || '（段旨待補）') + '</span></a></li>';
  });
  navh += '</ol>';
  var myRules = [], seenR = {};
  ((LS.law || {}).組 || []).forEach(function (g) {
    (g.條 || []).forEach(function (x) {
      if (seenR[x.n]) return;
      if ((x.引 || []).some(function (q) { return q.seq === seq; })) {
        seenR[x.n] = 1; myRules.push(x);
      }
    });
  });
  var ruleList = myRules.length ? myRules : (grp && grp.通則 || []);
  if (ruleList.length) {
    navh += '<h3>' + (myRules.length ? '本篇通則' : '本組通則') + '（' + ruleList.length + '）</h3><p class="small">' +
      ruleList.slice(0, 10).map(function (x) {
        return '<a href="#/law?n=' + x.n + '">' + x.n + '. ' + esc(x.名) + '</a>';
      }).join('<br/>') + '</p>';
  }
  var cp = CBYP[String(seq)] || [], jz = JZ[String(seq)] || [];
  if (cp.length || jz.length) {
    navh += '<h3>校勘與夾註</h3><p class="small muted">' +
      (cp.length ? '篇級校勘 ' + cp.length + ' 條　' : '') +
      (jz.length ? '底本夾註 ' + jz.length + ' 條' : '') + '</p>';
  }
  sc.innerHTML = navh;
  side.appendChild(sc);
  grid.appendChild(side);

  var main = h('div', 'read-main'); main.id = 'read-main';
  var intro = h('div', '', 'card read-intro');
  var mod = ((LS.modules || {}).篇 || []).filter(function (x) { return x.篇序 === seq; })[0];
  intro.innerHTML = '<div class="small muted"><span class="gid">' + esc(p.g || '') + '</span> ' +
    esc(p.gname || '') + ' · 段旨、音義、注文皆為輔助，原文為準</div>' +
    (grp ? '<p style="margin:6px 0 2px"><b>這一組在讀什麼：</b>' + esc(grp.主旨) + '</p>' +
      '<p class="small muted" style="margin:0">讀法：' + esc(grp.讀法) + '</p>' : '') +
    (mod && mod.一句 ? '<p style="margin:10px 0 0"><b>篇旨（編者）：</b>' + esc(mod.一句) + '</p>' : '') +
    '<p class="small muted" style="margin:10px 0 0">段旨＝編者歸納（歸）；注文為節錄，張注、馬蒔多為簡體照錄，不與經文混同；' +
    '音義為史崧舊注與本站罕字整理。讀者可以不同意段旨，直接讀原文。</p>' +
    '<p class="small" style="margin:8px 0 0"><span class="pill y">技藝</span> 原文涉及刺法、出血、深度、留呼與禁忌，本站不迴避；' +
    '但只作文本閱讀，實際操作須由合格中醫師指導，切勿照書自行施治。</p>';
  main.appendChild(intro);

  if (cp.length) {
    main.appendChild(collBlock(cp, '篇級校勘'));
  }
  if (jz.length) {
    var jd = document.createElement('details'); jd.className = 'card fold';
    var js = document.createElement('summary');
    js.textContent = '底本夾註 ' + jz.length + ' 條（展開）';
    jd.appendChild(js);
    var jw = h('div', '');
    jz.forEach(function (x) {
      jw.appendChild(h('p', '<b>' + esc(x.type) + '</b>　' + esc(x.text) + '　<span class="small muted">' + esc(x.note) + '</span>', 'small'));
    });
    jd.appendChild(jw); main.appendChild(jd);
  }

  paras.forEach(function (pa) {
    var sec = document.createElement('section');
    sec.className = 'duan'; sec.id = 'd' + pa.d;
    var head = h('div', '', 'duan-head');
    var z = dz[pa.d];
    head.innerHTML = '<span class="duan-no">段 ' + pa.d + '</span>' +
      '<span class="duan-zhi">' + esc((z && z.旨) || '段旨待補') + '</span>' +
      '<span class="duan-meta">' + pa.sents.length + ' 句</span>';
    sec.appendChild(head);
    var body = h('div', '', 'duan-body');
    pa.sents.forEach(function (s) {
      var sp = document.createElement('span');
      sp.className = 'sent'; sp.id = 's-' + s.id;
      sp.appendChild(document.createTextNode(s.t));
      var i = document.createElement('i');
      i.className = 'sid'; i.textContent = s.id;
      sp.appendChild(i);
      body.appendChild(sp);
    });
    sec.appendChild(body);

    var sids = pa.sents.map(function (s) { return s.id; });
    // 音義
    var ys = [], seen = {};
    sids.forEach(function (sid) {
      (YIN[sid] || []).forEach(function (y) {
        var k = y['字'] + '|' + (y['音'] || '');
        if (seen[k]) return; seen[k] = 1; ys.push(y);
      });
    });
    if (ys.length) {
      var yb = h('div', '', 'yin');
      yb.innerHTML = '<b>音義</b>' + ys.map(function (y) {
        return '<span class="yin-item" title="' + esc(y['家'] || '') + '"><b>' + esc(y['字']) + '</b>' +
          (y['音'] ? ' ' + esc(y['音']) : '') +
          (y['義'] ? '　<span class="muted">' + esc(y['義']) + '</span>' : '') + '</span>';
      }).join('');
      sec.appendChild(yb);
    }
    // 句級校勘
    var cs = [];
    sids.forEach(function (sid) { (CBYQ[sid] || []).forEach(function (c) { cs.push(c); }); });
    if (cs.length) sec.appendChild(collBlock(cs, '句級校勘'));

    // 四家注
    var ns = [];
    sids.forEach(function (sid) { (NOTES[sid] || []).forEach(function (n) { ns.push(n); }); });
    if (ns.length) {
      var fam = [];
      ns.forEach(function (n) { if (fam.indexOf(n['家']) < 0) fam.push(n['家']); });
      var nb = h('div', '', 'notes');
      var first = ns[0];
      nb.innerHTML = '<div class="note-brief"><span class="pill b">注</span><b>' + esc(first['家']) + '</b>　' +
        esc(first['文'].slice(0, 90)) + (first['文'].length > 90 ? '…' : '') + '</div>';
      var det = document.createElement('details');
      det.className = 'duan-notes';
      var sm = document.createElement('summary');
      sm.textContent = '展開 ' + ns.length + ' 則（' + fam.join('／') + '）';
      det.appendChild(sm);
      ns.forEach(function (n) {
        var item = h('div', '', 'note-item');
        item.innerHTML = '<div class="note-fam">' + esc(n['家']) + ' <span class="muted">' + esc(n['源'] || '') + '</span></div>' +
          '<div class="note-text">' + esc(n['文']) + '</div>';
        det.appendChild(item);
      });
      nb.appendChild(det);
      sec.appendChild(nb);
    }
    main.appendChild(sec);
  });

  grid.appendChild(main);
  box.appendChild(grid);

  b5.onclick = function () {
    main.classList.toggle('read-plain');
    b5.textContent = main.classList.contains('read-plain') ? '顯示注與音義' : '只讀原文';
  };
  b6.onclick = function () {
    var ds = main.querySelectorAll('details.duan-notes');
    var open = ds.length && ds[0].open;
    Array.prototype.forEach.call(ds, function (d) { d.open = !open; });
    b6.textContent = open ? '展開全部注' : '收起全部注';
  };
  b7.onclick = function () {
    document.body.classList.toggle('show-sid');
    b7.textContent = document.body.classList.contains('show-sid') ? '隱藏句ID' : '顯示句ID';
  };

  // 側欄點擊：只滾動，不改路由
  Array.prototype.forEach.call(side.querySelectorAll('.duan-nav a'), function (a) {
    a.onclick = function (ev) {
      ev.preventDefault();
      var el = document.getElementById('d' + a.getAttribute('data-d'));
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
  });
  if (window.IntersectionObserver) {
    var links = side.querySelectorAll('.duan-nav a');
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        Array.prototype.forEach.call(links, function (a) {
          a.classList.toggle('on', a.getAttribute('data-d') === en.target.id.replace(/^d/, ''));
        });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Array.prototype.forEach.call(main.querySelectorAll('.duan'), function (d) { io.observe(d); });
  }
  if (q.sid || q.d) {
    setTimeout(function () {
      var t = q.sid ? document.getElementById('s-' + q.sid) : null;
      if (!t && q.d) t = document.getElementById('d' + q.d);
      if (t) {
        t.classList.add('target');
        t.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
    }, 80);
  }
}

function collBlock(cs, label) {
  var d = h('div', '', 'collate');
  d.innerHTML = '<b>' + esc(label) + '</b>' + cs.map(function (c) {
    return '<div class="collate-item"><span class="pill y">' + esc(c.id) + '</span> ' +
      '<b>底本</b> ' + esc(c.base) + '　<b>太素</b> ' + esc(c.taisu) +
      '　<b>類經</b> ' + esc(c.leijing) + '　<b>別本</b> ' + esc(c.other) +
      '<div class="small">判定：' + esc(c.verdict) + '（' + esc(c.basis) + '；影響：' + esc(c.impact) + '）</div></div>';
  }).join('');
  return d;
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
  var asid = (LS.meta.stats && LS.meta.stats.anchor_sid) || 0;
  var aoth = (LS.meta.stats && LS.meta.stats.anchor_other) || 0;
  box.appendChild(h('p', '每題作答後都有「回原文」：' + asid + ' 題直接定位到句，' + aoth +
    ' 題依題幹引文、答案或篇首定位（會標明是哪一種）。先讀再答，比刷題有用。', 'small muted'));

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
function anchorHTML(it) {
  if (!it.a) return '';
  var aseq = parseInt(String(it.a).split('-')[0], 10);
  var ap = bySeq(aseq);
  var tag = { '句': '題幹／答案直引', '引文': '題幹引文', '他篇引文': '他篇引文',
    '答案': '答案對應原文', '篇首': '題幹無直引，定位篇首' }[it.ak] || '';
  var cross = (String(aseq) !== String(it.seq)) ? '（他篇）' : '';
  var pd = it.apd || it.ad || 1;
  return '<div class="small" style="margin-top:8px">' +
    '<a class="btn ghost" href="#/read?seq=' + aseq + '&sid=' + encodeURIComponent(it.a) + '&d=' + pd + '">' +
    '回原文 · ' + esc(ap ? ap.name : '') + ' · 段 ' + pd + '（句 ' + esc(it.a) + '）</a> ' +
    '<span class="muted">' + esc(tag + cross) + '</span></div>';
}
function itemCard(it) {
  var c = h('div', '', 'card');
  var head = h('div', '');
  head.innerHTML = '<span class="pill b">' + esc(it.pian) + '</span>' +
    '<span class="pill">' + ({ fill_blank: '填空', mcq: '選擇', error_identification: '辨誤' }[it.type] || it.type) + '</span>' +
    (it.case ? '<span class="pill y">案例題</span>' : '') +
    (it.level ? '<span class="pill">' + esc(it.level) + '</span>' : '');
  c.appendChild(head);
  c.appendChild(h('div', md(it.stem), 'q'));

  if (it.type === 'mcq' || it.case) {
    var opts = [it.answer].concat(it.dis || []);
    var seed = hash(it.id);
    opts.sort(function (a, b) { return (hash(a + seed) % 97) - (hash(b + seed) % 97); });
    var ans = el('div', 'ans', ''); ans.style.display = 'none';
    ans.innerHTML = '<b>正解：' + esc(it.answer) + '</b>' +
      (it.note ? '<div class="small">' + md(it.note) + '</div>' : '') + anchorHTML(it);
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
      '<div class="small">《靈樞·' + esc(it.pian) + '》' + (it.sid ? ' · 句 ' + esc(it.sid) : '') + '</div>' + anchorHTML(it);
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

  var CM = LS.conceptmap;
  if (CM && (CM.節點 || []).length) {
    var mc = h('div', '', 'card');
    var byId = {};
    CM.節點.forEach(function (n) { byId[n.id] = n; });
    var layers = CM.層 || [];
    var bands = layers.map(function (L) {
      var ns = CM.節點.filter(function (n) { return n.層 === L; });
      return '<div class="cm-layer"><div class="cm-lname">' + esc(L) + '</div><div class="cm-nodes">' +
        ns.map(function (n) {
          return '<span class="cm-node" title="' + esc(n.註 || '') + '">' + esc(n.名) + '</span>';
        }).join('') + '</div></div>';
    }).join('');
    var tr = '<tr><th>從</th><th>關係</th><th>到</th><th>證據</th><th>出處</th></tr>';
    (CM.連線 || []).forEach(function (e) {
      var a = byId[e.a] || { 名: e.a }, b = byId[e.b] || { 名: e.b };
      tr += '<tr><td>' + esc(a.名) + '</td><td class="small">' + esc(e['關係']) + '</td><td>' + esc(b.名) +
        '</td><td><span class="pill ' + (e['證據'] === '原文' ? 'g' : '') + '">' + esc(e['證據']) + '</span></td>' +
        '<td class="small">' + esc(e['出'] || '') + '</td></tr>';
    });
    mc.innerHTML = '<h2>概念地圖：' + CM.節點.length + ' 個節點、' + (CM.連線 || []).length + ' 條連線</h2>' +
      '<p class="small muted">' + esc(CM['說明'] || '') + '</p>' +
      '<div class="cm-layers">' + bands + '</div>' +
      '<p class="small muted">節點按層排列；連線是閱讀時可追的方向，不是生理流程圖。證據標「原文」者，出處可回句索引。</p>' +
      '<div class="table-wrap"><table>' + tr + '</table></div>' +
      ((CM.矛盾 || []).length ? '<h3>圖上未解的矛盾</h3><ul class="small">' + CM.矛盾.map(function (x) {
        return '<li><b>' + esc(x['爭點']) + '</b>：' + esc(x['甲']) + '；' + esc(x['乙']) +
          '（' + esc(x['狀態']) + '）</li>';
      }).join('') + '</ul>' : '');
    box.appendChild(mc);
  }

  nextLinks(box, [['81 篇地圖：十一組', '#/map'], ['通則：這些詞在哪些原則裡', '#/law'], ['十二經病候', '#/meridian'], ['練概念類題目', '#/items']]);};


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


  // ── 同文表：兩書哪幾句逐字相同 ──
  var TW = LS.suwentw || {};
  if ((TW['統計'] || {})['篇對']) {
    var tws = TW['統計'] || {};
    var tc = h('div', '', 'card');
    tc.appendChild(el('h2', '', '同文表：兩書哪幾句逐字相同'));
    tc.appendChild(h('p', '不是「靈樞抄素問」，也不是反過來：以 4-gram 重合看，' +
      '兩書絕大多數篇章幾乎不重疊（重合 ≥3% 的篇對只有 ' + tws['篇對'] + ' 組，≥30% 的只有 ' +
      (tws['重合≥30%的篇對'] || 0) + ' 組）。逐字相同的句子全書只有 <b>' + tws['同文句'] + '</b> 句。', 'small'));
    var t1 = '<tr><th style="width:110px">靈樞篇</th><th>素問篇（卷）</th><th style="width:64px">重合</th>' +
      '<th style="width:56px">長段</th><th style="width:56px">同文句</th></tr>';
    (TW['篇對'] || []).forEach(function (x) {
      t1 += '<tr><td class="small">' + esc(x['靈樞']) + '</td>' +
        '<td class="small">' + esc(x['素問']) + '（卷' + x['素問卷'] + '）</td>' +
        '<td class="num">' + x['重合'] + '%</td><td class="num">' + x['段數'] + '</td>' +
        '<td class="num">' + x['同文句'] + '</td></tr>';
    });
    var w1 = h('div', '', 'table-wrap'); w1.innerHTML = '<table>' + t1 + '</table>';
    tc.appendChild(w1);
    if ((TW['篇對'] || []).length && TW['篇對'][0]['例']) {
      tc.appendChild(h('p', '重合最高的一組（' + esc(TW['篇對'][0]['靈樞']) + ' ↔ ' +
        esc(TW['篇對'][0]['素問']) + '，' + TW['篇對'][0]['重合'] + '%）的長同文段：', 'small muted'));
      TW['篇對'][0]['例'].forEach(function (b) {
        tc.appendChild(h('div', esc(b['文']) + '…（' + b['字數'] + ' 字）', 'quote'));
      });
    }
    box.appendChild(tc);

    var fw = fold('逐字同文的 ' + (TW['句'] || []).length + ' 句（展開看）', false);
    var t2 = '<tr><th style="width:160px">靈樞</th><th>文</th><th style="width:150px">素問</th></tr>';
    (TW['句'] || []).forEach(function (x) {
      t2 += '<tr><td class="small">' + esc(x['靈樞篇']) + '<br/><span class="src">' + esc(x['id']) + '</span></td>' +
        '<td class="small">「' + esc(x['文']) + '」</td>' +
        '<td class="small">' + esc(x['素問']) + '<br/><span class="muted">卷' + x['素問卷'] + '</span></td></tr>';
    });
    var w2 = h('div', '', 'table-wrap'); w2.innerHTML = '<table>' + t2 + '</table>';
    fw.appendChild(w2);
    box.appendChild(fw);
  }

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

  var fd1 = fold('八十一篇各取一條（81 條，展開看）', false);
  fd1.appendChild(h('p', '每篇取字數最多的一條注，看張志聰在這篇最用力講什麼。', 'small muted'));
  var cc = h('div', '', 'card');
  cases.forEach(function (x) {
    var d = h('div', '', 'zj-case');
    d.innerHTML = '<h3><a href="#/read?seq=' + x['序'] + '">〈' + esc(x['篇']) + '〉</a>' +
      '　<span class="src">' + esc(x['id']) + '</span></h3>' +
      '<div class="quote">「' + esc(x['文']) + '」</div>' +
      '<div class="zj-note"><b>張注</b>' + esc(x['注']) + '</div>';
    cc.appendChild(d);
  });
  fd1.appendChild(cc);
  box.appendChild(fd1);

  var fd2 = fold('逐篇注文分布（81 列，展開看）', false);
  var tbl = h('div', '');
  tbl.appendChild(h('p', '逐篇的注句數、注字數與比對率。', 'small'));
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
  fd2.appendChild(tbl);
  box.appendChild(fd2);

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
  var fl1 = fold('通則引文與類經注（' + ((L['條'] || []).length) + ' 條，展開看）', false);
  fl1.appendChild(h('p', '與上一節同一批通則，換一家注。卷號是類經卷次——類經按類編排，沒有靈樞篇序。', 'small muted'));
  (L['條'] || []).forEach(function (t) {
    var c = h('div', '', 'card');
    c.appendChild(h('h3', '', t['n'] + '. ' + t['名'] + '　<span class="pill">' + esc(t['組'] || '') + '</span>'));
    (t['引'] || []).forEach(function (q) {
      c.appendChild(h('p', '<span class="src">類經卷 ' + q['卷'] +
        (q['類'] ? '　' + esc(q['類']) : '') + '　' + esc(q['id']) + '</span>', 'small muted'));
      c.appendChild(h('div', '「' + esc(q['文']) + '」', 'quote'));
      c.appendChild(h('div', '<b>類經注</b>' + esc(q['注']), 'zj-note'));
    });
    fl1.appendChild(c);
  });
  box.appendChild(fl1);

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
  var fl2 = fold('通則引文與靈樞識（' + ((X['通則'] || []).length) + ' 條，展開看）', false);
  fl2.appendChild(h('p', '同一批通則的第三家說。注裡引到他人處，前綴已標出是誰的話——那是轉引，不是原書。', 'small muted'));
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
    fl2.appendChild(c);
  });
  box.appendChild(fl2);

  var FD = fold('全書署名分佈（繫上的 ' + (xs['繫上'] || 0) + ' 條，展開看）', false);
  FD.appendChild(h('p', '只算能繫到底本句的 ' + (xs['繫上'] || 0) + ' 條；未繫上的條目（約 ' +
    ((xs['條'] || 0) - (xs['繫上'] || 0)) + ' 條）不列入。同一條可能同時引兩三家。', 'small muted'));
  var ft = '<tr><th style="width:170px">家</th><th style="width:90px">段</th><th>說明</th></tr>';
  var WHY = { '馬蒔（轉引）': '靈樞識引《靈樞注證發微》', '張介賓（轉引）': '靈樞識引《類經》注',
    '張志聰（轉引）': '靈樞識引《靈樞集註》', '丹波元簡': '簡案，己見', '甲乙經': '校勘引甲乙經異文',
    '千金方': '引《千金方》', '外台秘要': '引《外台秘要》', '巢氏病源': '引《諸病源候論》',
    '版本校': '版本異文（张本／志本等）', '未署名': '段首引他書或脫標記' };
  Object.keys(xs['家別'] || {}).sort(function (a, b) { return xs['家別'][b] - xs['家別'][a]; })
    .forEach(function (fam) {
      ft += '<tr><td>' + esc(fam) + '</td><td class="num">' + xs['家別'][fam] + '</td>' +
        '<td class="small muted">' + esc(WHY[fam] || '') + '</td></tr>';
    });
  var fw = h('div', '', 'table-wrap'); fw.innerHTML = '<table>' + ft + '</table>';
  FD.appendChild(fw);
  box.appendChild(FD);

  var MA = X['馬蒔'] || [];
  if (MA.length) {
    var FM = fold('馬蒔轉引輯存（全書 ' + (X['馬蒔總'] || MA.length) + ' 段，此處前 ' + MA.length +
      ' 段，展開看）', false);
    FM.appendChild(h('p', '馬蒔《靈樞注證發微》未入庫，這些話是《靈樞識》轉引的，可能節刪；' +
      '引用時務必寫「轉引」。完整清單見資料檔與 CSV。', 'small'));
    var mt = '<tr><th style="width:110px">篇</th><th style="width:64px">句</th><th>馬蒔說（轉引）</th></tr>';
    MA.forEach(function (x) {
      mt += '<tr><td class="small">' + esc(x['篇']) + '</td><td class="small muted">' +
        esc(x['句'] || '—') + '</td><td class="small">' + esc(x['文']) + '</td></tr>';
    });
    var mw = h('div', '', 'table-wrap'); mw.innerHTML = '<table>' + mt + '</table>';
    FM.appendChild(mw);
    box.appendChild(FM);
  }

  var TS = LS.taisuzhu || {};
  if ((TS['通則'] || []).length) {
    var ts = TS['統計'] || {};
    box.appendChild(h('h2', '四、楊上善《太素》注（隋）'));
    var t1 = h('div', '', 'card');
    t1.innerHTML = '<h3>這批注是怎麼來的</h3><ul class="small">' +
      '<li><b>來源</b>：' + esc(TS['來源'] || '') + '</li>' +
      '<li><b>方法</b>：' + esc(TS['方法'] || '') + '</li>' +
      '<li><b>結果</b>：' + (ts['卷'] || 0) + ' 卷、經文 ' + (ts['經文字'] || 0).toLocaleString() +
      ' 字、注段 ' + (ts['注段'] || 0).toLocaleString() + '、注字 ' + (ts['注字'] || 0).toLocaleString() +
      '；通則引文可對注 <b>' + (ts['通則引'] || 0) + '</b> 段、<b>' + (ts['通則條'] || 0) + '</b> 條。</li>' +
      '<li><b>局限</b>：太素錄文沒有經／注標記，這是<b>機器分離</b>，未與影印本校；' +
      '注可能屬鄰句——每段都標「距」（與引文尾的字數），距越大越不可靠。</li></ul>';
    box.appendChild(t1);
    var ft4 = fold('通則引文與太素注（' + (ts['通則引'] || 0) + ' 段，展開看）', false);
    ft4.appendChild(h('p', '與前三節同一批通則。太素為隋代舊注，年代最早，但分離最不確定。', 'small muted'));
    (TS['通則'] || []).forEach(function (t) {
      var c = h('div', '', 'card');
      c.appendChild(h('h3', '', t['n'] + '. ' + t['名'] + '　<span class="pill">' + esc(t['組'] || '') + '</span>'));
      (t['引'] || []).forEach(function (q) {
        c.appendChild(h('p', '<span class="src">卷 ' + q['卷'] + '　距 ' + (q['距'] > 0 ? '+' : '') + q['距'] + ' 字</span>', 'small muted'));
        c.appendChild(h('div', '「' + esc(q['文']) + '」', 'quote'));
        c.appendChild(h('div', '<b>太素注</b>' + esc(q['注']), 'zj-note'));
      });
      ft4.appendChild(c);
    });
    box.appendChild(ft4);

    var TI = LS.taisuindex || {}, ti = TI['統計'] || {};
    if ((ti['段'] || 0) > 0) {
      var ft5 = fold('逐段索引：' + ti['段'] + ' 段注各繫到哪一句（展開看）', false);
      ft5.appendChild(h('p', '靈樞句 <b>' + (ti['靈樞'] || 0) + '</b> 段、素問（細到篇）<b>' + (ti['素問'] || 0) +
        '</b> 段、未繫 <b>' + (ti['未繫'] || 0) + '</b> 段。繫句以「注緊接句末」為錨：4-gram 取候選，' +
        '主級相似度 ≥0.7、次級（句尾對齊）≥0.60；「比」是相似度，「距」是注與句末的字數。', 'small'));
      var pt = '<tr><th style="width:56px">篇</th><th>篇名</th><th style="width:70px">注段</th></tr>';
      (TI['篇'] || []).forEach(function (x) {
        pt += '<tr><td class="num">' + x['序'] + '</td><td><a href="#/read?seq=' + x['序'] + '">' +
          esc(x['篇']) + '</a></td><td class="num">' + x['段'] + '</td></tr>';
      });
      var pw = h('div', '', 'table-wrap'); pw.innerHTML = '<table>' + pt + '</table>';
      ft5.appendChild(pw);
      ft5.appendChild(h('p', '前 20 段樣本（繫到靈樞句者）：', 'small muted'));
      var st = '<tr><th style="width:64px">句</th><th>注（節錄）</th><th style="width:56px">比</th></tr>';
      (TI['樣本'] || []).forEach(function (r) {
        st += '<tr><td class="small">' + esc(r['句']) + (r['法'] ? '<br/><span class="muted">' + esc(r['法']) + '</span>' : '') +
          '</td><td class="small">' + esc(r['文']) + '</td><td class="num">' + r['比'] + '</td></tr>';
      });
      var sw = h('div', '', 'table-wrap'); sw.innerHTML = '<table>' + st + '</table>';
      ft5.appendChild(sw);
      box.appendChild(ft5);
    }
  }

  var CV = (LS.jizhu || {})['覆蓋'] || {};
  if ((CV['條'] || []).length) {
    var fd3 = fold('三家覆蓋：哪幾條有注可讀（' + ((CV['條'] || []).length) + ' 條，展開看）', false);
    var cv = h('div', '');
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
    fd3.appendChild(cv);
    box.appendChild(fd3);
  }

  var tail = h('div', '', 'alert');
  tail.innerHTML = '<b>怎麼用這一頁</b><span class="small" style="display:block;margin-top:6px">' +
    '注不是標準答案：兩家讀的是同一部經，他們的話可以幫你「看懂原文在說什麼」，' +
    '但不能拿來當原文的證據。要判斷一條通則站不站得住，仍回原文逐字核。</span>';
  box.appendChild(tail);

  nextLinks(box, [['通則：共同點', '#/law'], ['變體：不同寫法', '#/variant'], ['方法：收錄狀況', '#/method']]);
};

/* ---------------- 治理與預算 ---------------- */
VIEWS.govern = function (box) {
  var G = LS.govern || {};
  box.appendChild(h('h1', '治理與預算：誠實標出「不知道」'));
  box.appendChild(h('p', '這一頁回答的不是「有什麼內容」，而是「這些內容有多可信、哪裡還沒解決」。'
    + '分檔、狀態與預算的做法取自數位化整理方法論；不可判定不是失敗，是成果。', 'lead'));

  // 檔位對照
  var g1 = h('div', '', 'card');
  g1.appendChild(el('h2', '', '檔位：每一層話是誰說的'));
  var t1 = '<tr><th style="width:70px">本站</th><th style="width:190px">方法論檔位</th><th>意思</th></tr>';
  (G['檔位對照'] || []).forEach(function (x) {
    t1 += '<tr><td><b>' + esc(x['本站']) + '</b></td><td class="small">' + esc(x['方法論']) + '</td>' +
      '<td class="small muted">' + esc(x['說明']) + '</td></tr>';
  });
  var w1 = h('div', '', 'table-wrap'); w1.innerHTML = '<table>' + t1 + '</table>';
  g1.appendChild(w1);
  if (G['狀態機']) g1.appendChild(h('p', esc(G['狀態機']), 'small muted'));
  box.appendChild(g1);

  // 確定性預算
  var B = G['預算'] || {};
  var g2 = h('div', '', 'card');
  g2.appendChild(el('h2', '', '確定性預算：不是「已發布越多越好」'));
  g2.appendChild(h('p', '方法論要求把 published／suspended／兩存／blocked 一起報，且「長期歸零視為過度收斂警訊」。'
    + '本站只有一位維護者，所以把「還在懸置的」當成正常產出，而不是待清帳。', 'small'));
  var t2 = '<tr><th style="width:210px">指標</th><th style="width:110px">數</th><th>說明</th></tr>';
  var ROWS = [
    ['題數／題有句ID', (B['題數'] || 0) + '／' + (B['題有句ID'] || 0), '每題都能回到句索引；回鏈率 ' + (B['題回鏈率'] || 0) + '%'],
    ['句數', B['句數'] || 0, '底本句索引；句ID 為編者所加'],
    ['通則／有界', (B['通則條數'] || 0) + '／' + (B['通則有界'] || 0), '每條通則都寫了適用邊界（界）'],
    ['未決條目', B['未決條數'] || 0, 'blocked ' + (B['blocked'] || 0) + '、suspended ' + (B['suspended'] || 0)],
    ['裁決：兩存／未定', (B['both_preserved'] || 0) + '／' + (B['undetermined'] || 0), '「兩存」是結果，不是拖著不辦'],
    ['未決占（通則＋未決）', (B['未決占比'] || 0) + '%', '比例高不代表品質差，代表沒把不知道藏起來']
  ];
  ROWS.forEach(function (r) {
    t2 += '<tr><td><b>' + esc(r[0]) + '</b></td><td class="num">' + esc(String(r[1])) + '</td>' +
      '<td class="small muted">' + esc(r[2]) + '</td></tr>';
  });
  var w2 = h('div', '', 'table-wrap'); w2.innerHTML = '<table>' + t2 + '</table>';
  g2.appendChild(w2);
  box.appendChild(g2);

  // 未決登記簿
  var UN = G['未決'] || [];
  var g3 = h('div', '', 'card');
  g3.appendChild(el('h2', '', '未決登記簿（' + UN.length + ' 條）'));
  g3.appendChild(h('p', '每一條都寫了「什麼證據會推翻它」。狀態只有 blocked（取不到）與 suspended（取到但未定）；'
    + '裁決 single／both_preserved／undetermined。', 'small'));
  ['blocked', 'suspended'].forEach(function (st) {
    var rows = UN.filter(function (x) { return x['狀態'] === st; });
    if (!rows.length) return;
    g3.appendChild(el('h3', '', (st === 'blocked' ? '取不到（blocked）' : '取到但未定（suspended）') + '：' + rows.length + ' 條'));
    rows.forEach(function (x) {
      var it = h('div', '', 'law-item');
      it.appendChild(h('h4', '', x['id'] + '　' + esc(x['題']) + '　'
        + '<span class="pill y">' + esc(x['狀態']) + '</span> '
        + '<span class="pill">' + esc(x['裁決']) + '</span> '
        + '<span class="pill">' + esc(x['檔']) + '</span>'));
      it.appendChild(h('p', esc(x['說明']), 'small'));
      it.appendChild(h('p', '<b>證偽條件</b>：' + esc(x['證偽']), 'small'));
      it.appendChild(h('p', '<b>影響</b>：' + esc(x['影響']), 'small muted'));
      g3.appendChild(it);
    });
  });
  box.appendChild(g3);

  // 方法論採納
  var AD = G['採納'] || [];
  var g4 = h('div', '', 'card');
  g4.appendChild(el('h2', '', '方法論：哪幾條採用、哪幾條不'));
  var t4 = '<tr><th style="width:190px">規則</th><th style="width:80px">本站</th><th>做法</th></tr>';
  AD.forEach(function (x) {
    t4 += '<tr><td class="small"><b>' + esc(x['條']) + '</b></td><td class="small">' + esc(x['本站']) + '</td>' +
      '<td class="small muted">' + esc(x['做法']) + '</td></tr>';
  });
  var w4 = h('div', '', 'table-wrap'); w4.innerHTML = '<table>' + t4 + '</table>';
  g4.appendChild(w4);
  g4.appendChild(h('p', '沒做的：五層齊備（本站是原文／注／歸三層加解讀層）、golden set 回歸、'
    + '多人 reviewed_by、JSON Schema 硬檢。理由與替代做法見 docs/184。', 'small muted'));
  box.appendChild(g4);

  nextLinks(box, [['方法：稽核怎麼做', '#/method'], ['限制：還沒解決的', '#/limits'], ['通則', '#/law']]);
};

/* ---------------- 學習路徑 ---------------- */
VIEWS.path = function (box) {
  var P = LS.path || {}, routes = P['路線'] || [];
  box.appendChild(h('h1', '學習路徑：先讀哪一篇'));
  box.appendChild(h('p', '靈樞不是教科書，81 篇也不該從第一頁讀到最後一頁。這一頁給幾條次序建議：' +
    '每一步都指回原文與既有題目，進度由這台機器的閱讀紀錄自動算（換裝置不會帶走）。' +
    '次序與分組是編者所加（歸），不是原書次序。', 'lead'));
  if (!routes.length) { box.appendChild(h('p', '路徑資料未載入。', 'small')); return; }

  var log = STATE.log || {}, read = STATE.read || {};
  function stats(seqs) {
    var total = 0, ans = 0, rd = 0;
    seqs.forEach(function (q) {
      var its = (LS.items || []).filter(function (i) { return String(i.seq) === String(q); });
      total += its.length;
      ans += its.filter(function (i) { return log[i.id] != null; }).length;
      if (read[q]) rd += 1;
    });
    return { total: total, ans: ans, rd: rd, n: seqs.length };
  }

  routes.forEach(function (r) {
    var c = h('div', '', 'card');
    c.appendChild(el('h2', '', r['名']));
    c.appendChild(h('p', '<b>給誰</b>：' + esc(r['給誰'] || '') + '　<b>時間</b>：' + esc(r['時間'] || ''), 'small'));
    var tt = '<tr><th style="width:150px">步</th><th>讀什麼</th><th style="width:150px">進度</th>' +
      '<th style="width:34%">驗收（口頭說得出）</th></tr>';
    (r['步'] || []).forEach(function (st) {
      var seqs = st['篇'] || [];
      var s2 = seqs.length ? stats(seqs) : null;
      var links = seqs.map(function (q) {
        var p = bySeq(q);
        return '<a href="#/read?seq=' + q + '">' + esc(p ? p.name : ('第' + q + '篇')) + '</a>';
      }).join('、');
      if (st['主題']) {
        links = '<a href="#/themes">主題：' + esc(st['主題']) + '</a>';
      }
      var prog = '<span class="muted">—</span>';
      if (s2) {
        var done = s2.rd >= Math.ceil(s2.n * 0.8) && s2.ans >= Math.ceil(s2.total * 0.5);
        prog = '已讀 ' + s2.rd + '/' + s2.n + '<br/>答題 ' + s2.ans + '/' + s2.total +
          (done ? ' <span class="pill g">完成</span>' : '') +
          '<br/><a href="#/items?seq=' + seqs[0] + '">練這幾篇</a>';
      }
      tt += '<tr><td class="small"><b>' + esc(st['名']) + '</b>' +
        (st['線'] ? '<br/><span class="muted">' + esc(st['線']) + '</span>' : '') + '</td>' +
        '<td class="small">' + links + '</td>' +
        '<td class="small">' + prog + '</td>' +
        '<td class="small muted">' + esc(st['驗收'] || '') + '</td></tr>';
    });
    var w = h('div', '', 'table-wrap'); w.innerHTML = '<table>' + tt + '</table>';
    c.appendChild(w);
    var allseq = [];
    (r['步'] || []).forEach(function (st) { allseq = allseq.concat(st['篇'] || []); });
    if (allseq.length) {
      var s3 = stats(allseq);
      var doneN = 0;
      (r['步'] || []).forEach(function (st) {
        var sy = stats(st['篇'] || []);
        if (sy.rd >= Math.ceil(sy.n * 0.8) && sy.ans >= Math.ceil(sy.total * 0.5)) doneN += 1;
      });
      c.appendChild(h('p', '這條線：' + (r['步'] || []).length + ' 步中已完成 <b>' + doneN + '</b> 步；' +
        '全線 ' + s3.total + ' 題、已答 ' + s3.ans + '。', 'small'));
    }
    box.appendChild(c);
  });

  var tail = h('div', '', 'card');
  tail.innerHTML = '<h3>怎麼用</h3><ul class="small">' +
    '<li>不要一天讀完一條線；每天 30–40 分鐘，先讀原文，再答該篇的題。</li>' +
    '<li>「完成」的門檻是：讀過八成篇、答過一半題——不是「看過」就算。</li>' +
    '<li>卡住時回通則頁：那一頁是把散在諸篇的同一條原則收在一起。</li></ul>' +
    '<p class="small"><a href="#/law">通則</a>　·　<a href="#/themes">主題</a>　·　<a href="#/read">通讀</a></p>';
  box.appendChild(tail);
  nextLinks(box, [['主題：五個入口', '#/themes'], ['通則：共同點', '#/law'], ['題庫', '#/items']]);
};

/* ---------------- 模組：一篇一卡 ---------------- */
function renderAny(box, v, depth) {
  depth = depth || 0;
  if (v == null || v === '') return;
  if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
    box.appendChild(h('p', esc(String(v)), 'small'));
    return;
  }
  if (Array.isArray(v)) {
    if (!v.length) return;
    var allObj = v.every(function (x) { return x && typeof x === 'object' && !Array.isArray(x); });
    if (allObj && depth < 3) {
      var keys = [];
      v.slice(0, 80).forEach(function (x) {
        Object.keys(x).forEach(function (k) { if (keys.indexOf(k) < 0) keys.push(k); });
      });
      var t = '<tr>' + keys.map(function (k) { return '<th>' + esc(k) + '</th>'; }).join('') + '</tr>';
      v.slice(0, 80).forEach(function (x) {
        t += '<tr>' + keys.map(function (k) {
          var c = x[k];
          var txt = (c == null) ? '' : (typeof c === 'object' ? JSON.stringify(c) : String(c));
          return '<td class="small">' + esc(txt) + '</td>';
        }).join('') + '</tr>';
      });
      var w = h('div', '', 'table-wrap'); w.innerHTML = '<table>' + t + '</table>';
      box.appendChild(w);
      return;
    }
    var ul = el('ul', 'map-list', '');
    v.slice(0, 60).forEach(function (x) {
      var li = el('li', 'small', '');
      if (x && typeof x === 'object' && !Array.isArray(x)) {
        li.textContent = Object.keys(x).map(function (k) { return k + '：' + x[k]; }).join('；');
      } else {
        li.textContent = String(x);
      }
      ul.appendChild(li);
    });
    box.appendChild(ul);
    return;
  }
  if (typeof v === 'object') {
    Object.keys(v).forEach(function (k) {
      if (depth > 3) return;
      box.appendChild(h('h4', esc(k), 'small'));
      var sub = h('div', '', '');
      renderAny(sub, v[k], depth + 1);
      box.appendChild(sub);
    });
  }
}

VIEWS.module = function (box) {
  var M = LS.modules || {}, list = M['篇'] || [], gen = M['主題型'] || [];
  var bySeq = {};
  (LS.pian || []).forEach(function (p) { bySeq[p.seq] = p; });
  box.appendChild(h('h1', '模組：一篇一卡'));
  box.appendChild(h('p', '八十一篇每篇都有模組。D 型（' + (M['篇數'] || 0) + ' 篇）結構統一：'
    + '一句、分層、原文要點、誤讀、相連通則；主題型（' + (M['主題型數'] || 0) + ' 組）是早先做的，'
    + '結構各異，照原樣呈現。原文一律由句索引按 id 取出，不手打。', 'lead'));

  var seqs = [];
  (LS.pian || []).forEach(function (p) { seqs.push(p.seq); });
  seqs.sort(function (a, b) { return a - b; });

  seqs.forEach(function (seq) {
    var p = bySeq[seq] || { name: '第' + seq + '篇', seq: seq };
    var dm = list.filter(function (x) { return String(x['篇序']) === String(seq); });
    var gm = gen.filter(function (x) { return String(x['序']) === String(seq); });
    if (!dm.length && !gm.length) return;
    var head = seq + '. ' + p.name + (dm.length ? '　' + (dm[0]['一句'] || '').slice(0, 34) + '…' : '');
    var d = fold(head, false);

    dm.forEach(function (m) {
      var body = h('div', '', '');
      body.appendChild(h('p', '<b>一句</b>：' + esc(m['一句']), 'small'));
      var t = '<tr><th style="width:110px">層</th><th>原文</th><th style="width:38%">解（歸）</th></tr>';
      (m['分層'] || []).forEach(function (r) {
        t += '<tr><td class="small"><b>' + esc(r['層']) + '</b><br/><span class="muted">' + esc(r['句']) + '</span></td>' +
          '<td class="small">' + esc(r['原文']) + '</td><td class="small muted">' + esc(r['解']) + '</td></tr>';
      });
      var w = h('div', '', 'table-wrap'); w.innerHTML = '<table>' + t + '</table>';
      body.appendChild(w);
      if (m['誤讀']) body.appendChild(h('p', '<b>誤讀</b>：' + esc(m['誤讀']), 'small'));
      var laws = (m['連通則'] || []);
      if (laws.length) {
        body.appendChild(h('p', '<b>相連通則</b>：' + laws.map(function (x) {
          return '<a href="#/law?n=' + x['n'] + '">' + x['n'] + '. ' + esc(x['名']) + '</a>';
        }).join('、'), 'small'));
      }
      body.appendChild(h('p', '<a href="#/read?seq=' + seq + '">讀這篇原文</a>　·　' +
        '<a href="#/items?seq=' + seq + '">練這篇</a>', 'small'));
      d.appendChild(body);
    });

    gm.forEach(function (g) {
      var gb = h('div', '', '');
      gb.appendChild(h('p', '<span class="pill">主題型</span> ' + esc(g['組']), 'small'));
      renderAny(gb, g['內容'], 0);
      d.appendChild(gb);
    });
    box.appendChild(d);
  });

  nextLinks(box, [['學習路徑', '#/path'], ['通則：共同點', '#/law'], ['通讀 81 篇', '#/read']]);
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
  box.appendChild(h('p', '<a href="#/read?seq=2">讀〈本輸〉全文</a>　·　' +
    '<a href="#/naming">穴名用字與位次爭議：名訓層</a>', 'small'));
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
  box.appendChild(h('p', '原穴用於五藏之疾的診與治，具體操作需師授；本頁只列關係。' +
    '　<a href="#/naming">十二原的兩套 scope（名訓層）</a>', 'small muted'));
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

  // 通則分布圖：先看六十五條落在哪些組，再讀細目
  var gc = (L['組'] || []).map(function (g) { return { 名: g['組'], n: (g['條'] || []).length }; });
  var gmax = Math.max.apply(null, gc.map(function (x) { return x.n; }).concat([1]));
  var chart = h('div', '', 'card');
  chart.innerHTML = '<h2>六十五條的分布</h2><div class="hbars">' + gc.map(function (x) {
    return '<div class="hbar"><span class="hbar-k">' + esc(x['名']) + '</span>' +
      '<i style="width:' + Math.round(x.n / gmax * 100) + '%"></i>' +
      '<span class="hbar-v">' + x.n + ' 條</span></div>';
  }).join('') + '</div><p class="small muted">長條只表示條數，不表示重要性；同一條通則可能跨多篇。' +
    '想看「哪一組的篇被哪些通則引用」，去<a href="#/map">81 篇地圖</a>的組 × 通則表。</p>';
  box.appendChild(chart);

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

  nextLinks(box, [['名訓層：穴名怎麼訓', '#/naming'], ['校勘：19 條三源並排', '#/collation'], ['限制：34 條能力邊界', '#/limits'], ['異同：與素問的比較', '#/suwen']]);};

/* ---------------- 名訓層（穴名辨析） ---------------- */
VIEWS.naming = function (box) {
  var N = LS.naming;
  if (!N) { box.appendChild(h('p', '名訓資料未載入。', 'small')); return; }
  var S = N['統計'] || {};
  function sidLink(sid) {
    var seq = String(sid).split('-')[0];
    return '<a class="small" href="#/read?seq=' + seq + '&sid=' + encodeURIComponent(sid) + '">句 ' + esc(sid) + '</a>';
  }
  function quote(r) {
    return '<div class="nm-q"><span class="nm-qtext">' + esc(r.text) + '</span>' +
      '<span class="nm-qsrc">' + sidLink(r.id) + '　·　' + esc((bySeq(r.seq) || {}).name || '') + '</span></div>';
  }
  function refs(list) { return (list || []).map(quote).join(''); }

  box.appendChild(h('h1', '名訓層：穴名能解釋到什麼程度'));
  box.appendChild(h('p', '這一頁只問三件事：一個穴名能不能解釋；解釋到什麼程度才算合規；古今異名與歸屬爭議怎樣才不污染底本。' +
    '它不問「這個穴治什麼病」。', 'lead'));

  var us = h('div', '', 'card');
  us.appendChild(el('h2', '', '用字先於名訓'));
  us.appendChild(h('p', '名訓的第一步是定形：錄文用哪個字，就先照哪個字。底本本身有幾處用字不一致或疑訛，' +
    '這裡先列出，不替底本改字，也不拿今名回填。', 'small'));
  var ut = '<tr><th style="width:110px">用字</th><th>底本</th><th style="width:280px">本站處置</th></tr>';
  (N['用字'] || []).forEach(function (x) {
    ut += '<tr><td><b>' + esc(x['題']) + '</b></td><td class="small">' + esc(x['底本']) + '</td>' +
      '<td class="small">' + esc(x['處置']) + '</td></tr>';
  });
  var uw = h('div', '', 'table-wrap'); uw.innerHTML = '<table>' + ut + '</table>';
  us.appendChild(uw);
  us.appendChild(h('p', '原則：未回影印本核錄的字，不改、不並、不補；名訓只能在照錄的字上做，不能先換成今字再解釋。', 'small muted'));
  box.appendChild(us);

  var pr = h('div', '', 'card');
  pr.appendChild(el('h2', '', '八條原則'));
  var pg = h('div', '', 'nm-grid');
  (N['原則'] || []).forEach(function (x) {
    var c = h('div', '', 'nm-principle');
    c.innerHTML = '<div class="nm-k">' + esc(x.id) + '</div><h3>' + esc(x['題']) + '</h3><p class="small">' + esc(x['文']) + '</p>';
    pg.appendChild(c);
  });
  pr.appendChild(pg);
  box.appendChild(pr);

  var st = h('div', '', 'card');
  st.appendChild(el('h2', '', '六步法'));
  var sg = h('div', '', 'nm-steps');
  (N['六步'] || []).forEach(function (x) {
    sg.innerHTML += '<div class="nm-step"><span class="nm-stepno">' + esc(x.n) + '</span><div><b>' + esc(x['題']) + '</b>' +
      '<p class="small">' + esc(x['文']) + '</p></div></div>';
  });
  st.appendChild(sg);
  box.appendChild(st);

  var vo = h('div', '', 'card');
  vo.appendChild(el('h2', '', '取象類受控詞表（編者的檢索框架，不是經文分類）'));
  var vt = '<tr><th style="width:86px">類</th><th style="width:150px">取象根據</th><th style="width:120px">代表字</th><th>例穴</th><th>舉證要點</th></tr>';
  (N['詞表'] || []).forEach(function (x) {
    vt += '<tr><td><b>' + esc(x['類']) + '</b></td><td class="small">' + esc(x['取象']) + '</td>' +
      '<td class="small">' + esc(x['代表字']) + '</td><td class="small">' + esc(x['例穴']) + '</td>' +
      '<td class="small">' + esc(x['舉證']) + '</td></tr>';
  });
  var vw = h('div', '', 'table-wrap'); vw.innerHTML = '<table>' + vt + '</table>';
  vo.appendChild(vw);
  vo.appendChild(h('p', '同一字可以跨類，但一條依據只能記一類；「病機功效」最危險，因為它把後世用穴偷換成古人命名，凡入此類一律 C 檔並標 later_view。', 'small muted'));
  box.appendChild(vo);

  var gr = h('div', '', 'card');
  gr.appendChild(el('h2', '', '證據分檔與措辭紅線'));
  var gt = '<tr><th style="width:120px">檔位</th><th>證據要求</th><th>可用措辭</th><th>禁用措辭</th><th style="width:56px">本站標</th></tr>';
  (N['檔位'] || []).forEach(function (x) {
    gt += '<tr><td><b>' + esc(x['檔']) + '</b></td><td class="small">' + esc(x['要求']) + '</td>' +
      '<td class="small">' + esc(x['可用']) + '</td><td class="small">' + esc(x['禁用']) + '</td>' +
      '<td class="num">' + esc(x['本站標']) + '</td></tr>';
  });
  var gw = h('div', '', 'table-wrap'); gw.innerHTML = '<table>' + gt + '</table>';
  gr.appendChild(gw);
  gr.appendChild(h('p', '檔位取證據鏈的最短板，不取最亮點；C 檔不得使用定論句式。本站把 A／B／C 對到〔原〕／〔注〕／〔歸〕，但兩套標記不是自動等價，仍以證據為準。', 'small'));
  box.appendChild(gr);

  var df = h('div', '', 'card');
  df.appendChild(el('h2', '', '三類差異：異名、異體、標目歸經'));
  df.appendChild(h('p', '穴名不同進 v 表；用字異體也進 v 表；經脈標目不同進 l 表。兩表不得互填。', 'small'));
  var xt = '<tr><th style="width:64px">編號</th><th>底本錄文</th><th>今名</th><th>類型</th><th>處置</th><th style="width:64px">句</th></tr>';
  (N['異名'] || []).forEach(function (x) {
    xt += '<tr><td><b>' + esc(x.id) + '</b></td><td>' + esc(x['底本']) + '</td><td>' + esc(x['今名']) + '</td>' +
      '<td class="small">' + esc(x['類型']) + '</td><td class="small">' + esc(x['處置']) + '</td>' +
      '<td>' + sidLink(x.sid) + '</td></tr>';
  });
  var xw = h('div', '', 'table-wrap'); xw.innerHTML = '<table>' + xt + '</table>';
  df.appendChild(xw);
  var lt = '<tr><th style="width:64px">編號</th><th>本輸標目</th><th>今制歸經</th><th>說明</th><th style="width:64px">句</th></tr>';
  (N['標目'] || []).forEach(function (x) {
    lt += '<tr><td><b>' + esc(x.id) + '</b></td><td>' + esc(x['本輸標目']) + '</td><td>' + esc(x['今制']) + '</td>' +
      '<td class="small">' + esc(x['說明']) + '</td><td>' + sidLink(x.sid) + '</td></tr>';
  });
  var lw = h('div', '', 'table-wrap'); lw.innerHTML = '<table>' + lt + '</table>';
  df.appendChild(lw);
  if (N['十二原'] && N['十二原'].d001) {
    var dd = N['十二原'];
    [dd.d001, dd.d002].forEach(function (d) {
      df.appendChild(h('p', '<b>' + esc(d['題']) + '</b>：甲 ' + esc(d['甲']) + '；乙 ' + esc(d['乙']) +
        '；判定 <span class="pill y">' + esc(d['狀態']) + '</span>。' + esc(d['理由']), 'small'));
    });
  }
  box.appendChild(df);

  var ex = h('div', '');
  ex.appendChild(h('h2', '七個實例：每例都給錄文、拆字、兩證、檔位與證偽'));
  (N['實例'] || []).forEach(function (e, i) {
    var c = h('div', '', 'card nm-ex');
    var et = '<tr><th style="width:44px">字</th><th style="width:90px">類</th><th>字書層</th><th>醫理層</th><th style="width:86px">檔位</th></tr>';
    (e.elements || []).forEach(function (x) {
      et += '<tr><td><b>' + esc(x.char) + '</b></td><td class="small">' + esc(x.cls) + '</td>' +
        '<td class="small">' + esc(x.lexis) + '</td><td class="small">' + esc(x.medical) + '</td>' +
        '<td class="small">' + esc(x.grade) + '</td></tr>';
    });
    c.innerHTML = '<div class="nm-exhead"><span class="nm-exno">例 ' + (i + 1) + '</span><b>' + esc(e.name) + '</b>' +
      '<span class="pill">' + esc(e.tag) + '</span><span class="pill ' + (e.status.indexOf('blocked') >= 0 ? 'y' : 'g') + '">' + esc(e.status) + '</span></div>' +
      '<div class="nm-refs">' + refs(e.refs) + '</div>' +
      (e.elements && e.elements.length ? '<div class="table-wrap"><table>' + et + '</table></div>' : '<p class="small muted">elements 留空：無可證依據。</p>') +
      '<p><b>判</b>：' + esc(e.conclusion) + '</p>' +
      '<p class="small"><b>證偽</b>：' + esc(e.falsifier) + '</p>' +
      '<p class="small"><b>關聯</b>：' + esc((e.links || []).join('；')) + '</p>' +
      '<p class="small"><b>本例誤判</b>：' + esc(e.mistake) + '</p>' +
      '<p class="small muted"><b>說明</b>：' + esc(e.review) + '</p>';
    ex.appendChild(c);
  });
  box.appendChild(ex);

  var ws = h('div', '', 'card');
  ws.appendChild(el('h2', '', '五輸：先訓類名，再約束穴名'));
  ws.appendChild(h('p', '本輸十一經，每經一句；陰經無原，陽經多一原。表內用底本字，今名另欄，不用今名回填。', 'small'));
  var wt = '<tr><th style="width:76px">本輸標目</th><th style="width:120px">今制</th><th>井</th><th>滎</th><th>腧</th><th>原</th><th>經</th><th>合</th><th>差異</th><th style="width:56px">句</th></tr>';
  (N['五腧'] || []).forEach(function (x) {
    wt += '<tr><td><b>' + esc(x.base) + '</b></td><td class="small">' + esc(x.modern) + '</td>' +
      [x.jing, x.ying, x.shu, x.yuan, x.jing2, x.he].map(function (y) { return '<td class="small">' + esc(y || '—') + '</td>'; }).join('') +
      '<td class="small">' + esc(x.diff) + '</td><td>' + sidLink(x.sid) + '</td></tr>';
  });
  var ww = h('div', '', 'table-wrap'); ww.innerHTML = '<table>' + wt + '</table>';
  ws.appendChild(ww);
  ws.appendChild(h('p', '類名的經文依據在 1-8-3（底本作「所以為合」；通行本多作「所入為合」，未回影印本核錄，不逕改）；' +
    '五藏井木、六府井金是本輸的標注事實，但不能延伸為子母補瀉取穴。', 'small muted'));
  box.appendChild(ws);

  var yz = h('div', '', 'card');
  yz.appendChild(el('h2', '', '十二原的兩套 scope'));
  var A = N['十二原'].A, B = N['十二原'].B;
  var at = '<tr><th>藏</th><th>原</th><th>數</th><th>句</th></tr>';
  (A['條'] || []).forEach(function (x) { at += '<tr><td>' + esc(x['藏']) + '</td><td><b>' + esc(x['原']) + '</b></td><td class="num">' + x['數'] + '</td><td>' + sidLink(x.sid) + '</td></tr>'; });
  yz.innerHTML = '<p class="small"><b>' + esc(A['名']) + '</b>：' + esc(A['說明']) + '</p>' +
    '<div class="table-wrap"><table>' + at + '</table></div>' +
    '<p class="small" style="margin-top:10px"><b>' + esc(B['名']) + '</b>：' + esc(B['說明']) + '</p>' +
    '<p class="small">' + (B['條'] || []).map(esc).join('、') + '。</p>' +
    '<p class="small muted">' + esc(B['注']) + '</p>' +
    '<p class="small">出題或檢索時必須先標 scope；不標 scope 的「十二原」答案不唯一。</p>';
  box.appendChild(yz);

  var pf = h('div', '', 'card');
  pf.appendChild(el('h2', '', '常見誤判與攔截'));
  var pt = '<tr><th style="width:220px">誤判形態</th><th>後果</th><th style="width:240px">攔截</th></tr>';
  (N['誤判'] || []).forEach(function (x) {
    pt += '<tr><td>' + esc(x[0]) + '</td><td class="small">' + esc(x[1]) + '</td><td class="small">' + esc(x[2]) + '</td></tr>';
  });
  var pw = h('div', '', 'table-wrap'); pw.innerHTML = '<table>' + pt + '</table>';
  pf.appendChild(pw);
  box.appendChild(pf);

  var mc = h('div', '', 'card');
  mc.appendChild(el('h2', '', '機器參與的硬邊界（本站寫作規約）'));
  var ml = '<ol class="small nm-machine">';
  (N['機器'] || []).forEach(function (x) { ml += '<li><b>' + esc(x[0]) + '</b>：' + esc(x[1]) + '</li>'; });
  ml += '</ol>';
  mc.innerHTML += ml;
  mc.appendChild(h('p', '這些是本站採用的寫作約束；CI 與回歸用例尚未建立，不把它們說成已驗證的指標。', 'small muted'));
  box.appendChild(mc);

  var fd = h('div', '', 'card');
  fd.appendChild(el('h2', '', '欄位契約速查'));
  var ft = '<tr><th style="width:150px">欄位</th><th>含義</th><th>約束</th></tr>';
  (N['欄位'] || []).forEach(function (x) { ft += '<tr><td><code>' + esc(x[0]) + '</code></td><td class="small">' + esc(x[1]) + '</td><td class="small">' + esc(x[2]) + '</td></tr>'; });
  var fw = h('div', '', 'table-wrap'); fw.innerHTML = '<table>' + ft + '</table>';
  fd.appendChild(fw);
  fd.appendChild(h('p', '字段之外兩條紀律：檔位取最短板；寫不出證據的地方，留白是成果，填充是事故。', 'small'));
  box.appendChild(fd);

  var td = h('div', '', 'card');
  td.innerHTML = '<h2>驗收與待辦</h2><p>' + esc(N['驗收']) + '</p><ol class="small">' +
    (N['待辦'] || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ol>';
  box.appendChild(td);

  var stat = h('div', '', 'card');
  stat.innerHTML = '<div class="stats" style="margin:0"><div class="stat"><b>' + (S['原則'] || 0) + '</b><span>原則</span></div>' +
    '<div class="stat"><b>' + (S['詞表'] || 0) + '</b><span>取象類</span></div>' +
    '<div class="stat"><b>' + (S['實例'] || 0) + '</b><span>實例</span></div>' +
    '<div class="stat"><b>' + (S['五腧'] || 0) + '</b><span>五輸經</span></div>' +
    '<div class="stat"><b>' + (S['用字'] || 0) + '</b><span>用字備註</span></div></div>';
  box.appendChild(stat);

  nextLinks(box, [['通讀：回到原文與段旨', '#/read?seq=2'], ['五輸表：本輸十一經', '#/meridian?tab=shu'],
    ['校勘：三源並排', '#/collation'], ['注家：四家怎麼讀', '#/jizhu']]);
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

  var JT = LS.jiayitiao || {};
  if ((JT['條'] || []).length) {
    var jt = JT['統計'] || {};
    var fc = fold('甲乙經逐條對應（引用句 ' + (jt['有對應'] || 0) + '／' + (jt['引用句'] || 0) +
      ' 有對應，展開看）', false);
    fc.appendChild(h('p', '把本站引用到的每一句（通則、變體、病候、癰疽、界限、十二經病候）拿去甲乙經找最相近的一條。' +
      '相似度 ≥0.85 才收；差異只列不判——甲乙經改寫多，用字與文句都可能不同。' +
      '全書可比 ' + (jt['同文'] || 0) + ' 句同文、' + (jt['近似'] || 0) + ' 句近似（合計 ' + (jt['總對上'] || 0) + '）。', 'small'));
    var tt = '<tr><th style="width:52px">句</th><th>靈樞（底本）</th><th>甲乙經</th><th style="width:34%">差異（未判定）</th></tr>';
    (JT['條'] || []).forEach(function (r) {
      var d = (r['異'] || []).map(function (x) {
        return (x['甲'] ? '甲「' + esc(x['甲']) + '」' : '（甲無）') +
               (x['乙'] ? '／乙「' + esc(x['乙']) + '」' : '（乙無）');
      }).join('；') || '<span class="muted">同文</span>';
      tt += '<tr><td class="small">' + esc(r['id']) + '<br/><span class="muted">卷 ' + r['卷'] + '</span></td>' +
        '<td class="small">' + esc(r['甲']) + '</td><td class="small">' + esc(r['乙']) + '</td>' +
        '<td class="small muted">' + d + '</td></tr>';
    });
    var tw = h('div', '', 'table-wrap'); tw.innerHTML = '<table>' + tt + '</table>';
    fc.appendChild(tw);
    fc.appendChild(h('p', '「字形／通假」類差異（府腑、太、著着等）已另外計數，不在上表逐條列；' +
      '其餘差異包含改寫、脫衍與訛字，本站不判是非。', 'small muted'));
    box.appendChild(fc);
  }

  var TP = LS.taisupa || {}, tp = TP['統計'] || {};
  if ((tp['段'] || 0) > 0) {
    var fp = fold('太素平按：蕭延平的校記（' + tp['段'] + ' 條，展開看）', false);
    fp.appendChild(h('p', '太素的「平按」不是楊上善注，是民國蕭延平校刻《太素》時寫的校記：' +
      '記版本異文、闕文、補入與他書對應。這一層過去被丟棄，現在單獨收起來。' +
      '統計為字串出現次數（「提甲乙」＝文中出現「甲乙」二字，含「甲乙經」）。', 'small'));
    var pt = '<tr><th style="width:150px">項</th><th style="width:90px">次</th><th>說明</th></tr>';
    var WHY2 = { '段': '校記條數', '字': '校記字數', '見素問': '明言「此條見素問…」',
      '見靈樞': '明言「此條見靈樞…」', '見甲乙': '明言「此條見甲乙…」',
      '提靈樞': '文中出現「靈樞」', '提素問': '文中出現「素問」', '提甲乙': '文中出現「甲乙」',
      '提袁刻': '引袁刻（袁氏刻本）', '提原抄': '引原抄（影寫本）', '提別本': '引別本' };
    Object.keys(WHY2).forEach(function (k) {
      if (tp[k] == null) return;
      pt += '<tr><td>' + esc(k) + '</td><td class="num">' + tp[k] + '</td>' +
        '<td class="small muted">' + esc(WHY2[k]) + '</td></tr>';
    });
    var pw2 = h('div', '', 'table-wrap'); pw2.innerHTML = '<table>' + pt + '</table>';
    fp.appendChild(pw2);
    fp.appendChild(h('p', '前 10 條樣本：', 'small muted'));
    var ps = '<tr><th style="width:56px">卷</th><th>校記（節錄）</th></tr>';
    (TP['條'] || []).forEach(function (x) {
      ps += '<tr><td class="num">' + x['卷'] + '</td><td class="small">' + esc(x['文']) + '</td></tr>';
    });
    var pw3 = h('div', '', 'table-wrap'); pw3.innerHTML = '<table>' + ps + '</table>';
    fp.appendChild(pw3);
    box.appendChild(fp);
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
    } else if (x.url) {
      var b = el('a', 'mail', x.url.replace(/^https?:\/\//, ''));
      b.href = x.url; b.setAttribute('target', '_blank'); b.setAttribute('rel', 'noopener noreferrer');
      left.appendChild(b);
    } else if (x.qr) {
      left.appendChild(h('p', '<b>' + esc(x.wechat || '') + '</b>　掃碼加好友（同上兩個站的維護者）', 'small'));
      var q = el('img', 'qr');
      q.src = x.qr; q.alt = '微信二維碼：' + (x.wechat || '');
      q.setAttribute('width', '180');
      left.appendChild(q);
    } else {
      left.appendChild(h('p', '<b>待補</b>——發布前會填上可公開的郵箱；目前請透過下方相關站點聯絡。', 'small'));
    }
    row.appendChild(left); it.appendChild(row);
  });
  box.appendChild(it);

  var FB = C.feedback || {};
  if (FB.issueUrl || FB.mail) {
    var fb = h('div', '', 'card');
    fb.appendChild(el('h3', '', '回報一處，就少一處'));
    fb.appendChild(h('p', '兩種走法，挑順手的：<b>GitHub Issue</b> 公開可追蹤（單點勘誤最快）；'
      + '<b>email</b> 適合附圖、長文、整份校表。', 'small'));
    var fs = '<tr><th style="width:96px">走法</th><th>怎麼做</th></tr>';
    if (FB.issueUrl) {
      fs += '<tr><td><b>Issue</b></td><td class="small"><a href="' + esc(FB.issueUrl) +
        '" target="_blank" rel="noopener noreferrer">開一個勘誤 Issue</a>——有表單，照欄位填即可。</td></tr>';
    }
    if (FB.mail) {
      var subj = encodeURIComponent(FB.mailSubject || '靈樞站勘誤');
      var body = encodeURIComponent(FB.mailBody || '');
      fs += '<tr><td><b>Email</b></td><td class="small"><a href="mailto:' + esc(FB.mail) +
        '?subject=' + subj + '&body=' + body + '">寫信給 ' + esc(FB.mail) + '</a>（主旨與內文已幫你開好格式）。</td></tr>';
    }
    var fw = h('div', '', 'table-wrap'); fw.innerHTML = '<table>' + fs + '</table>';
    fb.appendChild(fw);
    if ((FB.checklist || []).length) {
      var ul = el('ul', 'map-list', '');
      fb.appendChild(h('p', '回報時請附這五樣（少一樣我就得再問一次）：', 'small muted'));
      FB.checklist.forEach(function (x) { ul.appendChild(el('li', 'small', x)); });
      fb.appendChild(ul);
    }
    fb.appendChild(h('p', '回報會反映到站上；原文異文一律兩處並存，不擅自改定。',
      'small muted'));
    box.appendChild(fb);
  }

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
  if (window.speechSynthesis) { try { window.speechSynthesis.cancel(); } catch (e) {} }
  var r = parseHash();
  var v = VIEWS[r.name] || VIEWS.home;
  var view = $('#view');
  view.innerHTML = '';
  v(view, r.q);
  Array.prototype.forEach.call(document.querySelectorAll('#nav a'), function (a) {
    a.className = a.getAttribute('data-k') === r.name ? 'on' : '';
  });
  Array.prototype.forEach.call(document.querySelectorAll('#nav details.navgrp'), function (d) {
    d.open = false;
    var on = d.querySelectorAll('a.on').length > 0;
    d.querySelector('summary').className = on ? 'on' : '';
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
    if (x[0] === 'grp') {
      var d = document.createElement('details'); d.className = 'navgrp';
      var sm = document.createElement('summary'); sm.textContent = x[1];
      sm.setAttribute('data-grp', x[1]);
      d.appendChild(sm);
      var menu = el('div', 'navmenu', '');
      x[2].forEach(function (it) {
        var a = document.createElement('a');
        a.href = '#/' + it[0]; a.textContent = it[1]; a.setAttribute('data-k', it[0]);
        menu.appendChild(a);
      });
      d.appendChild(menu); nav.appendChild(d);
      return;
    }
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

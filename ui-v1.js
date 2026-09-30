// ui-v1.js — pomoćnici uz ui-v1.css. Bez zavisnosti; učitava se sa <script src="ui-v1.js" defer>.
// ui.toast(), ui.confirm(), ui.busy(), ui.fmt.*, ui.tabs()
(function () {
  const ui = {};

  let box;
  function toasts() {
    if (!box) { box = document.createElement('div'); box.className = 'toasts'; box.setAttribute('aria-live', 'polite'); document.body.append(box); }
    return box;
  }

  // ui.toast('Saved') · ui.toast('Deleted', { undo: () => restore() }) · ui.toast('Failed', { type: 'err' })
  ui.toast = function (text, opts = {}) {
    const t = document.createElement('div');
    t.className = 'toast' + (opts.type === 'err' ? ' err' : '');
    t.textContent = text;
    if (opts.undo) {
      const b = document.createElement('button');
      b.textContent = opts.undoLabel || 'Undo';
      b.onclick = () => { opts.undo(); t.remove(); };
      t.append(b);
    }
    toasts().append(t);
    setTimeout(() => t.remove(), opts.ms || (opts.undo ? 6000 : 3500));
  };

  // await ui.confirm({ title, text, ok: 'Delete', danger: true }) → true/false
  ui.confirm = function ({ title = 'Are you sure?', text = '', ok = 'Confirm', cancel = 'Cancel', danger = false } = {}) {
    return new Promise(resolve => {
      const d = document.createElement('dialog');
      d.className = 'ui-dialog';
      d.innerHTML = `<div class="dialog-head"></div><div class="dialog-body"></div>
        <div class="dialog-foot"><button class="btn" value="0"></button><button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" value="1"></button></div>`;
      d.querySelector('.dialog-head').textContent = title;
      d.querySelector('.dialog-body').textContent = text;
      const [c, o] = d.querySelectorAll('.dialog-foot button');
      c.textContent = cancel; o.textContent = ok;
      d.querySelectorAll('.dialog-foot button').forEach(b => b.onclick = () => d.close(b.value));
      d.addEventListener('close', () => { resolve(d.returnValue === '1'); d.remove(); });
      document.body.append(d); d.showModal(); o.focus();
    });
  };

  // await ui.busy(button, async () => save()) — dugme pokazuje rad i ne može se kliknuti dvaput
  ui.busy = async function (btn, fn) {
    btn.setAttribute('aria-busy', 'true'); btn.disabled = true;
    try { return await fn(); }
    finally { btn.removeAttribute('aria-busy'); btn.disabled = false; }
  };

  // Brojevi i datumi uvijek kroz Intl; jezik se bira jednom po aplikaciji (document.documentElement.lang)
  const L = () => document.documentElement.lang || 'en';
  ui.fmt = {
    num: (n, d = 0) => new Intl.NumberFormat(L(), { minimumFractionDigits: d, maximumFractionDigits: d }).format(n),
    money: (n, cur = 'EUR') => new Intl.NumberFormat(L(), { style: 'currency', currency: cur }).format(n),
    date: v => new Intl.DateTimeFormat(L(), { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(v)),
    ago: v => {
      const s = (new Date(v) - Date.now()) / 1000, r = new Intl.RelativeTimeFormat(L(), { numeric: 'auto' });
      for (const [u, k] of [['year', 31536000], ['month', 2592000], ['day', 86400], ['hour', 3600], ['minute', 60]])
        if (Math.abs(s) >= k) return r.format(Math.round(s / k), u);
      return r.format(Math.round(s), 'second');
    },
  };

  // <div class="tabs" data-tabs><button aria-controls="a">…</button></div> + paneli sa id-em
  ui.tabs = function (root) {
    const btns = [...root.querySelectorAll('button[aria-controls]')];
    const show = b => btns.forEach(x => {
      const on = x === b; x.setAttribute('aria-selected', on);
      document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
    });
    btns.forEach(b => b.onclick = () => show(b));
    show(btns.find(b => b.getAttribute('aria-selected') === 'true') || btns[0]);
  };

  // Samo svijetla tema (30.09.2026). Brise se izbor koji je pregledac zapamtio ranije.
  try { localStorage.removeItem('ui-theme'); } catch {}
  delete document.documentElement.dataset.theme;

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tabs]').forEach(ui.tabs);
    document.addEventListener('click', e => {
      const tr = e.target.closest('tr[data-href]');
      if (tr && !e.target.closest('a,button,input,select')) location.href = tr.dataset.href;
    });
  });

  window.ui = ui;
})();

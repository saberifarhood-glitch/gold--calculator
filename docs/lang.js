// Language switcher — PT ↔ FA
const STORAGE_KEY = 'bfy_lang';

function setLang(lang) {
  localStorage.setItem(STORAGE_KEY, lang);
  applyLang(lang);
}

function applyLang(lang) {
  const isFa = lang === 'fa';

  // Direction & font
  document.body.classList.toggle('fa', isFa);
  document.documentElement.lang = lang;

  // Toggle active buttons
  document.getElementById('btn-pt').classList.toggle('active', !isFa);
  document.getElementById('btn-fa').classList.toggle('active', isFa);

  // Update all elements with data-pt / data-fa
  document.querySelectorAll('[data-pt]').forEach(el => {
    const text = el.getAttribute(isFa ? 'data-fa' : 'data-pt');
    if (text) el.innerHTML = text;
  });
}

// On load: use saved preference or default PT
(function () {
  const saved = localStorage.getItem(STORAGE_KEY) || 'pt';
  applyLang(saved);
})();

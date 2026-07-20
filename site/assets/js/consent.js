/* Kredato — cookie-уведомление (implied consent, 152-ФЗ информирование) */
(function () {
  "use strict";
  var KEY = "kredato_cookie_ok";
  try { if (localStorage.getItem(KEY) === "1") return; } catch (e) {}

  function build() {
    var bar = document.createElement("div");
    bar.id = "cookie-bar";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Уведомление об использовании cookie");
    bar.innerHTML =
      '<p>Мы используем cookie и системы аналитики (Яндекс.Метрика, Google Analytics), ' +
      'чтобы улучшать сайт. Оставаясь здесь, вы соглашаетесь с обработкой данных ' +
      'согласно <a href="/privacy.html">Политике ПДн</a> (152-ФЗ).</p>' +
      '<button type="button" id="cookie-ok">Понятно</button>';
    document.body.appendChild(bar);
    document.getElementById("cookie-ok").addEventListener("click", function () {
      try { localStorage.setItem(KEY, "1"); } catch (e) {}
      bar.remove();
    });
  }

  var css =
    "#cookie-bar{position:fixed;left:0;right:0;bottom:0;z-index:9999;" +
    "display:flex;gap:16px;align-items:center;justify-content:center;flex-wrap:wrap;" +
    "padding:14px 20px;background:#1a1a2e;color:#eee;font-size:14px;line-height:1.5;" +
    "box-shadow:0 -2px 12px rgba(0,0,0,.25)}" +
    "#cookie-bar p{margin:0;max-width:820px}" +
    "#cookie-bar a{color:#7db1ff;text-decoration:underline}" +
    "#cookie-ok{flex:none;padding:9px 22px;border:0;border-radius:6px;cursor:pointer;" +
    "background:#4a7dff;color:#fff;font-size:14px;font-weight:600}" +
    "#cookie-ok:hover{background:#3866e0}" +
    "@media(max-width:600px){#cookie-bar{font-size:13px;padding:12px 14px}}";
  var st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  if (document.body) build();
  else document.addEventListener("DOMContentLoaded", build);
})();

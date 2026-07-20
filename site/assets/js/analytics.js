/* Kredato — счётчики аналитики (KISS, defer-loaded, без блокировки рендера) */
(function () {
  "use strict";

  var GA4 = "G-J8KKCQS6YS";   // Google Analytics 4 (Measurement ID)
  var YM  = 110885200;        // Яндекс.Метрика (номер счётчика)

  /* --- Google Analytics 4 --- */
  (function () {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag("js", new Date());
    gtag("config", GA4);
  })();

  /* --- Яндекс.Метрика (инициализируется, когда задан номер) --- */
  if (YM) {
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      k = e.createElement(t); a = e.getElementsByTagName(t)[0];
      k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
    ym(YM, "init", { clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: true });
  }
})();

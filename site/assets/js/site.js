/* Kredato — минимальный vanilla JS (без библиотек). Поверх style.css. */
(function () {
  "use strict";

  /* В6: sticky-cta — показать .show после скролла 60% страницы,
     закрытие навсегда через localStorage (уважение пользователя = анти-спам). */
  var cta = document.getElementById("stickyCta");
  if (cta) {
    var dismissed = false;
    try { dismissed = localStorage.getItem("k_ctu") === "1"; } catch (e) {}
    if (!dismissed) {
      var onScroll = function () {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        if (h > 0 && window.scrollY > 0.6 * h) {
          cta.classList.add("show");
        } else {
          cta.classList.remove("show");
        }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
    var closeBtn = cta.querySelector(".close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        cta.classList.remove("show");
        try { localStorage.setItem("k_ctu", "1"); } catch (e) {}
      });
    }
  }

  /* В9: бургер — переключение класса open на nav (mobile). */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector("header.site nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    /* закрываем меню при клике по ссылке (мобайл) */
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* В4: tabs rates-ticker — переключение .hidden панелей + live load from rates.json. */
  var ticker = document.querySelector('.rates-ticker');
  if (ticker) {
    var buttons = ticker.querySelectorAll('.tabs button');
    var panels = ticker.querySelectorAll('.panel');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var period = btn.getAttribute('data-period');
        buttons.forEach(function (b) {
          b.setAttribute('aria-selected', b === btn ? 'true' : 'false');
        });
        panels.forEach(function (p) {
          p.classList.toggle('hidden', p.getAttribute('data-panel') !== period);
        });
      });
    });

    var accentEl = ticker.querySelector('.val');
    var captionEl = ticker.querySelector('.caption');
    var introEl = ticker.querySelector('h3');
    var currentPeriod = '6m';
    function applyPeriod(period, data) {
      var p = data.periods && data.periods[period];
      if (!p) return;
      if (introEl && data.updated_at) {
        var d = new Date(data.updated_at);
        var dateStr = isNaN(d) ? '' : d.toLocaleDateString('ru-RU');
        introEl.textContent = 'Ставки на ' + (dateStr || 'сегодня') + ' (по открытым данным)';
      }
      var map = { 'Вклады': 'deposits', 'Ипотека': 'mortgage', 'Кредиты': 'loans' };
      rows.forEach(function (panel) {
        var label = panel.querySelector('.row span');
        var val = panel.querySelector('.row .val');
        var key = label ? map[label.textContent.trim()] : '';
        if (!key) return;
        if (val && p[key]) {
          val.textContent = p[key];
        }
      });
      if (captionEl && data.caption) {
        captionEl.textContent = data.caption;
      }
    }
    try {
      fetch('assets/data/rates.json?' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (data) {
        applyPeriod(currentPeriod, data);
        buttons.forEach(function (btn) {
          btn.addEventListener('click', function () {
            var period = btn.getAttribute('data-period');
            currentPeriod = period;
            applyPeriod(period, data);
          });
        });
      }).catch(function () {});
    } catch (e) {}
  }
})();

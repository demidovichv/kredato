/* Kredato — динамические виджеты (В): подбор ПОД юзера из контента сайта.
   Берём реальные slug-ы существующих страниц — НЕ выдуманные тарифы. */
(function () {
  "use strict";

  /* F9 — офферы под гео: выбор региона -> реальные страницы сайта */
  function geoWidget(block) {
    var sel = block.querySelector('[data-geo="region"]');
    var out = block.querySelector(".geo-out");
    if (!sel || !out) return;
    /* реальные рубрики/страницы сайта (slug -> название) */
    var MAP = {
      "msk":  [["/fin/", "Финансы (вклады, карты, ипотека)"], ["/strah/", "Страхование (ОСАГО, КАСКО)"]],
      "spb":  [["/fin/", "Финансы (вклады, карты, ипотека)"], ["/strah/", "Страхование (ОСАГО, КАСКО)"]],
      "reg":  [["/fin/", "Финансы (вклады, карты, ипотека)"], ["/strah/", "Страхование (ОСАГО, КАСКО)"]],
      "sng":  [["/fin/sng/", "Финансы в СНГ (займы онлайн, Казахстан)"], ["/of/", "Витрина МФО (СНГ-доступные)"]],
      "kz":   [["/fin/sng/zaymy-kazahstan-online/", "Займы онлайн в Казахстане"], ["/of/", "Витрина МФО"]],
      "by":   [["/of/", "Витрина МФО (доступно из РБ)"], ["/earning/", "Заработок онлайн"]]
    };
    function render() {
      var key = sel.value;
      var list = MAP[key] || [];
      if (!list.length) { out.innerHTML = "Выберите регион"; return; }
      var html = "<ul class='geo-list'>";
      list.forEach(function (it) {
        html += "<li><a href='" + it[0] + "'>" + it[1] + "</a></li>";
      });
      html += "</ul><p class='calc-sub'>Показаны разделы сайта, доступные для выбранного региона. Конкретные офферы — на страницах витрины.</p>";
      out.innerHTML = html;
    }
    sel.addEventListener("change", render);
    render();
  }

  /* E7 — подборка ИИ-инструментов: чекбоксы нужд -> фильтр статей заработка */
  function aiWidget(block) {
    var boxes = block.querySelectorAll('[data-ai]');
    var out = block.querySelector(".ai-out");
    if (!boxes.length || !out) return;
    /* реальные статьи раздела earning (slug -> что решает) */
    var TOOLS = {
      "text":   [["/earning/kursy-neyrosetey-marketing/", "Курсы по нейросетям в маркетинге"], ["/learn/golos-zarabotok-gayd/", "Голос: заработок голосовыми ИИ"]],
      "design": [["/earning/ii-dlya-malogo-biznesa/", "ИИ для малого бизнеса"], ["/earning/kursy-neyrosetey-marketing/", "Нейросети в маркетинге"]],
      "code":   [["/jobs/gde-nayti-zakazy-kwork-fl/", "Фриланс-биржи (Kwork, FL)"], ["/learn/cheklist-frilansera-novichka/", "Чек-лист фрилансера"]],
      "video":  [["/earning/podrabotka-vecherom-2026/", "Подработка вечером"], ["/earning/frilans-mamam-v-dekrete/", "Фриланс для мам в декрете"]]
    };
    function render() {
      var keys = Array.prototype.slice.call(boxes).filter(function (b) { return b.checked; })
        .map(function (b) { return b.getAttribute("data-ai"); });
      var seen = {}, html = "<ul class='geo-list'>";
      var any = false;
      keys.forEach(function (k) {
        (TOOLS[k] || []).forEach(function (it) {
          if (!seen[it[0]]) { seen[it[0]] = 1; html += "<li><a href='" + it[0] + "'>" + it[1] + "</a></li>"; any = true; }
        });
      });
      html += "</ul>";
      out.innerHTML = any ? html : "<p class='calc-sub'>Отметьте, что нужно — подберём материалы сайта.</p>";
    }
    boxes.forEach(function (b) { b.addEventListener("change", render); });
    render();
  }

  document.querySelectorAll("[data-widget=geo]").forEach(geoWidget);
  document.querySelectorAll("[data-widget=ai]").forEach(aiWidget);
})();

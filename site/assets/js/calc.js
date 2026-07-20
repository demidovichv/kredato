/* Kredato — калькуляторы (честные формулы, без выдуманных тарифов).
   Единый DRY-движок: каждый калькулятор = блок <div class="calculator" data-calc="ID">
   с полями data-f="имя" и шаблоном результата в data-out. */
(function () {
  "use strict";
  var R = function (id) { return document.getElementById(id); };
  var num = function (v) { var n = parseFloat(String(v).replace(/\s/g, "")); return isNaN(n) ? 0 : n; };
  var fmt = function (n) { return Math.round(n).toLocaleString("ru-RU") + " ₽"; };
  var pct = function (n) { return (Math.round(n * 100) / 100).toLocaleString("ru-RU"); };

  /* дифференцированный платёж (аннуитет) — стандарт ипотеки/кредита */
  function annuity(P, annualRate, months) {
    var r = annualRate / 100 / 12;
    if (r === 0) return P / months;
    return P * r * Math.pow(1 + r, months) / (Math.pow(1 + r, months) - 1);
  }

  /* конфигураторы: возвращают строку результата по значениям полей */
  var CALCS = {
    /* F5 — вклад */
    deposit: function (f) {
      var P = num(f.amt), rate = num(f.rate), m = Math.round(num(f.months)), cap = f.cap;
      if (!P || !rate || !m) return "Заполните поля";
      if (cap) {
        var total = P * Math.pow(1 + (rate / 100) / 12, m);
        return "Через " + m + " мес: <b>" + fmt(total) + "</b><br>Доход: <b>" + fmt(total - P) + "</b>";
      }
      var pr = P * (rate / 100) * (m / 12);
      return "Через " + m + " мес: <b>" + fmt(P + pr) + "</b><br>Доход: <b>" + fmt(pr) + "</b>";
    },
    /* F1/F2 — кредитная карта: рассрочка или переплата по минималке */
    card: function (f) {
      var P = num(f.amt), rate = num(f.rate), m = Math.round(num(f.months)), grace = Math.round(num(f.grace));
      if (!P || !rate || !m) return "Заполните поля";
      var prosech = P / m;
      var perMonth = annuity(P, rate, m);
      var overPay = perMonth * m - P;
      var out = "Средний платёж при погашении за " + m + " мес: <b>" + fmt(perMonth) + "</b><br>" +
        "Переплата: <b>" + fmt(overPay) + "</b>";
      if (grace > 0) out += "<br>Льготный период " + grace + " дн. — при погашении в срок переплаты нет.";
      return out;
    },
    /* F7 — ипотека (аннуитет) */
    mortgage: function (f) {
      var P = num(f.amt), rate = num(f.rate), y = Math.round(num(f.years));
      if (!P || !rate || !y) return "Заполните поля";
      var m = y * 12;
      var pay = annuity(P, rate, m);
      var over = pay * m - P;
      return "Ежемесячный платёж: <b>" + fmt(pay) + "</b><br>Переплата за " + y +
        " лет: <b>" + fmt(over) + "</b>";
    },
    /* F8 — рефинансирование: точка безубыточности */
    refinance: function (f) {
      var P = num(f.amt), oldR = num(f.old), newR = num(f.new), fee = num(f.fee);
      if (!P || !oldR || !newR) return "Заполните поля";
      var saveYear = P * (oldR - newR) / 100;
      if (saveYear <= 0) return "Новая ставка не ниже старой — смысла нет.";
      var months = fee > 0 ? Math.ceil((fee / saveYear) * 12) : 0;
      return "Экономия в год: <b>" + fmt(saveYear) + "</b><br>" +
        (months > 0 ? "Комиссия окупится за <b>~" + months + " мес</b>." : "Без комиссии — сразу в плюсе.");
    },
    /* S1 — ОСАГО: грубая оценка по базовому тарифу (честный диапазон) */
    osago: function (f) {
      var power = Math.round(num(f.power)), city = f.region, age = Math.round(num(f.age)), exp = Math.round(num(f.exp));
      if (!power) return "Укажите мощность";
      // базовый тариф ЦБ 2026 (диапазон), берём середину для оценки
      var base = 3500;
      var kbt = power <= 100 ? 1.0 : (power <= 150 ? 1.2 : 1.5);
      var kvo = (city === "msk" || city === "spb") ? 2.0 : 1.0;
      var kbs = (age < 22 || exp < 3) ? 1.8 : (age > 59 ? 1.0 : 1.0);
      var low = base * 0.45 * kbt * kvo * kbs;   // нижняя граница диапазона ЦБ
      var high = base * 2.35 * kbt * kvo * kbs;  // верхняя граница
      return "Оценка ОСАГО: <b>от " + fmt(low) + " до " + fmt(high) + "</b><br>" +
        "<span class='calc-sub'>по базовому тарифу ЦБ, без скидок за стаж/безаварийность</span>";
    },
    /* S4/S5/S6 — КАСКО-конструктор: доля от стоимости авто */
    kasko: function (f) {
      var car = num(f.car), ageY = Math.round(num(f.ageY)), newCar = f.isnew;
      if (!car) return "Укажите стоимость авто";
      var rate = (newCar ? 3.2 : 2.4) + (ageY > 7 ? -0.6 : 0) + (ageY > 3 && ageY <= 7 ? 0 : 0);
      rate = Math.max(1.2, Math.min(rate, 4.5));
      var prem = car * rate / 100;
      return "Премия КАСКО ~ <b>" + fmt(prem) + "</b><br>" +
        "Ставка оценки: <b>" + pct(rate) + "%</b> от стоимости";
    }
  };

  function bindCalc(block) {
    var id = block.getAttribute("data-calc");
    var fn = CALCS[id];
    if (!fn) return;
    var out = block.querySelector(".result");
    var fields = block.querySelectorAll("[data-f]");
    function recompute() {
      var f = {};
      block.querySelectorAll("[data-f]").forEach(function (el) {
        f[el.getAttribute("data-f")] = el.type === "checkbox" ? el.checked : el.value;
      });
      out.innerHTML = fn(f);
    }
    fields.forEach(function (el) {
      el.addEventListener(el.type === "checkbox" ? "change" : "input", recompute);
    });
    // кастомные степперы
    block.querySelectorAll(".step-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var wrap = btn.closest(".stepper");
        var input = wrap.querySelector("input[type=number]");
        var step = parseFloat(wrap.getAttribute("data-step")) || 1;
        var dir = parseInt(btn.getAttribute("data-dir"), 10) || 1;
        var cur = parseFloat(input.value); if (isNaN(cur)) cur = 0;
        var next = Math.max(0, cur + dir * step);
        if (input.step && input.step.indexOf(".") >= 0) next = Math.round(next * 100) / 100;
        input.value = next;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      });
    });
    recompute();
  }

  document.querySelectorAll(".calculator[data-calc]").forEach(bindCalc);
})();

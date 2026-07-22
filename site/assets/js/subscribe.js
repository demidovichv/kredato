/* kredato.com — единый сборщик подписок через Cloudflare Pages Function /api/subscribe.
 *
 * Resend — основной/резерв канал. UniSender остаётся в резерве, если нет ключа.
 */

(function () {
  // Основной эндпоинт. Если Functions отключены — graceful fallback на subscribe.html.
  var API_SUBSCRIBE = '/api/subscribe';

  function resolveSource() {
    var path = window.location.pathname || '';
    if (/\/earning\//.test(path)) return 'earning';
    if (/\/fin\//.test(path)) return 'fin';
    if (/\/strah\//.test(path)) return 'strah';
    if (/\/jobs\//.test(path)) return 'jobs';
    if (/\/learn\//.test(path)) return 'learn';
    if (/\/of\//.test(path)) return 'of';
    return 'kredato';
  }

  function resolveMagnet() {
    var el = document.querySelector('[data-magnet]');
    return el ? String(el.getAttribute('data-magnet') || '').trim() : '';
  }

  function slots() {
    return document.querySelectorAll('[data-uni-form]');
  }

  function bindForm(form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = (form.querySelector('input[name="email"]') || {}).value || '';
      var consent = (form.querySelector('input[name="consent"]') || {}).checked;

      if (!email || !email.includes('@')) {
        var bad = form.querySelector('.form-success');
        if (bad) { bad.textContent = 'Укажите корректный email и согласие на рассылку.'; bad.style.display = 'block'; }
        return;
      }

      var source = (form.querySelector('input[name="vertical"]:checked') || {}).value || resolveSource();
      var magnet = resolveMagnet();
      var successEl = form.querySelector('.form-success');
      var btn = form.querySelector('button[type="submit"]');

      if (!consent) {
        if (successEl) { successEl.textContent = 'Нужно согласие на рассылку.'; successEl.style.display = 'block'; }
        return;
      }

      if (btn) { btn.disabled = true; btn.textContent = 'Отправка…'; }
      if (successEl) { successEl.style.display = 'none'; }

      fetch(API_SUBSCRIBE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, magnet }),
      })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var msg = 'Проверь почту — там письмо с подтверждением подписки.';
        if (data.status === 'queued_without_resend') msg = 'Подписка в очереди. Подтверждение придёт после настройки почты.';
        if (data.status === 'doi_sent') msg = 'Проверь почту — там письмо с подтверждением подписки.';
        if (data.status === 'worker_error') msg = 'Серверная ошибка: ' + (data.detail || 'попробуйте через минуту');
        if (data.status === 'resend_error') msg = 'Ошибка отправки на почту. Если повторится — напишите нам.';
        if (data.status === 'error') msg = 'Ошибка: ' + (data.detail || 'проверьте форму');
        if (successEl) { successEl.textContent = '✅ ' + msg; successEl.style.display = 'block'; }
      })
      .catch(function () {
        if (successEl) { successEl.textContent = 'Ошибка соединения. Попробуйте ещё раз.'; successEl.style.display = 'block'; }
      })
      .finally(function () {
        if (btn) { btn.disabled = false; btn.textContent = 'Подписаться'; }
      });
    });
  }

  // Fallback: если на странице есть форма с action="../../subscribe.html" или "#"
  // переключаем на fetch-submit выше. Оставляем совместимость.
  slots().forEach(function (s) {
    if (!s.hasAttribute('data-subscribe-bound')) {
      s.setAttribute('data-subscribe-bound', '1');
      bindForm(s);
    }
  });
})();

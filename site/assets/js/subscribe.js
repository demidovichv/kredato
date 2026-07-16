/* kredato.com — подключение формы подписки (UniSender, Фри).
 *
 * ВСТАВЬ СВОЙ ID ФОРМЫ из кабинета UniSender (Рассылки → Формы →
 * скрипт для сайта). Один ID → подхватывается на всех 26 страницах.
 * Пока ID пустой — форма показывает плейсхолдер и НЕ шлёт (безопасно).
 */
(function () {
  // >>> ВПИШИ СЮДА ID ФОРМЫ UNISENDER ПОСЛЕ РЕГИСТРАЦИИ <<<
  var UNI_FORM_ID = ''; // напр. 'abc123def'

  function slots() {
    return document.querySelectorAll('[data-uni-form]');
  }

  if (!UNI_FORM_ID) {
    // Домен/кабинет ещё не готовы: оставляем плейсхолдер, не шлём.
    slots().forEach(function (s) {
      s.classList.add('uni-slot--pending');
    });
    return;
  }

  // Подгружаем виджет UniSender один раз.
  if (!window.__uniLoaded) {
    window.__uniLoaded = true;
    var sc = document.createElement('script');
    sc.async = true;
    sc.src = 'https://us1.unisender.com/v5/uni_public_form.js';
    document.head.appendChild(sc);
  }

  // Помечаем слоты готовыми к инициализации виджетом.
  slots().forEach(function (s) {
    s.setAttribute('data-uni-id', UNI_FORM_ID);
    s.classList.add('uni-slot--ready');
  });
})();

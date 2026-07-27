/**
 * kredato.com — Cloudflare Pages Function
 * GET /api/confirm → подтверждение email из DOI + welcome email с PDF.
 */
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const email = String(url.searchParams.get('email') || '').trim();
  const magnet = String(url.searchParams.get('magnet') || '').trim();

  try {
    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ status: 'error', detail: 'email_required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const apiKeyKredato = env.RESEND_API_KEY_KREDATO || '';
    const apiKeyMyfinq = env.RESEND_API_KEY || '';
    const fromKredato = env.RESEND_FROM_KREDATO || 'Kredato <noreply@kredato.com>';
    const fromMyfinq = env.RESEND_FROM_MYFINQ || 'Kredato <noreply@myfinq.xyz>';

    let apiKey = '';
    let from = '';
    let domainLabel = 'kredato.com';

    if (apiKeyKredato) {
      apiKey = apiKeyKredato;
      from = fromKredato;
      domainLabel = 'kredato.com';
    } else if (apiKeyMyfinq) {
      apiKey = apiKeyMyfinq;
      from = fromMyfinq;
      domainLabel = 'myfinq.xyz';
    }

    if (!apiKey) {
      // No mail config — just render confirmation page inline
      return renderConfirmed(email, magnet, domainLabel, false);
    }

    // Best-effort: mark as confirmed in Resend audience
    const audienceId = env.RESEND_AUDIENCE_ID || '';
    if (audienceId) {
      await fetch(`https://api.resend.com/audiences/${audienceId}/contacts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          first_name: '',
          last_name: '',
          custom_properties: { confirmed_at: new Date().toISOString(), magnet, domain: domainLabel },
        }),
      }).catch(() => {});
    }

    // Welcome email + PDF
    const brand = domainLabel === 'myfinq.xyz' ? 'myfinq.xyz' : 'kredato.com';
    const pdfUrl = magnet
      ? `${new URL(request.url).origin}/assets/pdf/${encodeURIComponent(magnet)}.pdf`
      : '';
    const subject = 'Добро пожаловать в Kredato — вот ваш PDF';
    const welcomeHtml = `<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1f2937">
  <div style="background:#0f172a;color:#e2e8f0;padding:20px;border-radius:12px;margin-bottom:20px">
    <h1 style="margin:0;font-size:22px">Готово — подписка подтверждена</h1>
  </div>
  <p>Спасибо! Ваш email подтверждён. Теперь можно пользоваться рассылкой Kredato.</p>
  ${pdfUrl ? `<p><strong>Ваш PDF-магнит:</strong><br><a href="${pdfUrl}" style="color:#2563eb;text-decoration:none">Скачать файл</a></p>` : ''}
  <p style="font-size:13px;color:#6b7280">Если кнопка не открывается — скопируйте ссылку в браузер.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="font-size:12px;color:#9ca3af">${brand} · Отписаться в один клик — в каждом письме.</p>
</body>
</html>`;

    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: [email],
        subject,
        html: welcomeHtml,
      }),
    }).catch(() => {});

    return renderConfirmed(email, magnet, domainLabel, true);
  } catch (err) {
    return new Response(JSON.stringify({ status: 'worker_error', detail: String(err) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

function renderConfirmed(email, magnet, domainLabel, mailSent) {
  const origin = 'https://kredato.com';
  const pdfUrl = magnet ? `${origin}/assets/pdf/${encodeURIComponent(magnet)}.pdf` : '';
  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Подписка подтверждена — Kredato</title>
<link rel="stylesheet" href="/assets/css/style.css?v=3">
<meta name="robots" content="noindex, nofollow">
<script src="/assets/js/analytics.js" defer></script>
<script src="/assets/js/consent.js" defer></script>
<style>
.state{display:none}
.state.is-active{display:block}
.card{max-width:560px;margin:0 auto;padding:24px}
.lead{color:#374151}
.muted{color:#6b7280;font-size:14px}
</style>
</head>
<body>
<header class="site">
  <div class="wrap">
    <div class="logo">Kred<span>ato</span></div>
    <nav><a href="/">На главную</a></nav>
  </div>
</header>

<section class="hero compact">
  <div class="wrap">
    <div id="s-confirm" class="state is-active">
      <span class="tag green">Double opt-in</span>
      <h1>Почти готово!</h1>
      <p class="lead">Мы отправили письмо с подтверждением на указанный email. Перейдите по ссылке в письме, чтобы активировать подписку.</p>
      <p class="muted">Не пришло письмо? Проверьте папку «Спам» или напишите нам ответом.</p>
    </div>

    <div id="s-done" class="state">
      <span class="tag green">Готово</span>
      <h1>Подписка подтверждена</h1>
      <p class="lead">Спасибо! Ваш email подтверждён. Теперь можно пользоваться рассылкой Kredato.</p>
      <div id="pdf-block" style="display:none">
        <p><strong>Ваш PDF-магнит:</strong><br>
          <a id="pdf-link" href="/assets/pdf/" style="color:#2563eb;text-decoration:none">Скачать файл</a>
        </p>
        <p class="muted">Если кнопка не открывается — скопируйте ссылку в браузер.</p>
      </div>
      <div class="hero-actions">
        <a href="/" class="btn alt">На главную</a>
      </div>
    </div>
  </div>
</section>

<footer class="site">
  <div class="wrap">
    <div class="notice advertiser">
      <p>Мы зарабатываем, когда вы оформляете продукт по нашей ссылке — комиссию платит нам провайдер, вам условия не ухудшаются. А факты в разборе берём из открытых данных банков и ЦБ, а не от рекламодателей.</p>
    </div>
    <div class="disclaimer">
      <p>© 2026 Kredato. Материалы носят информационный характер и <strong>не являются финансовой рекомендацией</strong>.</p>
      <p><a href="/">На главную</a> · <a href="/privacy.html">Политика ПДн</a></p>
    </div>
  </div>
</footer>

<script>
(function(){
  try {
    var params = new URLSearchParams(window.location.search);
    var email = params.get('confirmed');
    var magnet = params.get('magnet');
    var confirmed = Boolean(email);
    var confirmEl = document.getElementById('s-confirm');
    var doneEl = document.getElementById('s-done');
    var pdfBlock = document.getElementById('pdf-block');
    var linkEl = document.getElementById('pdf-link');
    if (confirmEl) confirmEl.classList.toggle('is-active', !confirmed);
    if (doneEl) doneEl.classList.toggle('is-active', confirmed);
    if (pdfBlock && linkEl && magnet) {
      pdfBlock.style.display = '';
      linkEl.href = '/assets/pdf/' + encodeURIComponent(magnet) + '.pdf';
      linkEl.textContent = magnet;
    } else if (pdfBlock) {
      pdfBlock.style.display = 'none';
    }
  } catch (e) {}
})();
</script>
</body>
</html>`;

  return new Response(html, {
    status: 200,
    headers: { 'Content-Type': 'text/html; charset=utf-8' },
  });
}

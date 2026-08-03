/**
 * kredato.com — Cloudflare Pages Function
 * GET /api/confirm → подтверждение email из DOI + welcome email с PDF.
 */
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const email = String(url.searchParams.get('email') || '').trim();
  const magnet = String(url.searchParams.get('magnet') || '').trim() || 'magnet-3-deposits-rates';

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

    let mailSent = false;
    if (apiKey) {
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

      const brand = domainLabel === 'myfinq.xyz' ? 'myfinq.xyz' : 'kredato.com';
      const pdfName = magnet ? `${magnet}.pdf` : '';
      const origin = new URL(request.url).origin;
      const pdfUrl = pdfName ? `${origin}/assets/pdf/${encodeURIComponent(pdfName)}` : '';

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

      const payload: Record<string, unknown> = {
        from,
        to: [email],
        subject,
        html: welcomeHtml,
      };

      if (pdfName) {
        let pdfBuffer: Buffer | ArrayBuffer | null = null;
        let pdfFilename = pdfName;
        try {
          const pdfRes = await fetch(`${origin}/assets/pdf/${encodeURIComponent(pdfName)}`);
          if (pdfRes.ok) {
            pdfBuffer = await pdfRes.arrayBuffer();
          }
        } catch {
          pdfBuffer = null;
        }
        if (pdfBuffer) {
          payload.attachments = [
            {
              filename: pdfFilename,
              content: Buffer.from(pdfBuffer).toString('base64'),
            },
          ];
        }
      }

      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }).catch(() => {});
      mailSent = true;
    }

    return renderConfirmed(email, magnet, domainLabel, mailSent);
  } catch (err) {
    return new Response(JSON.stringify({ status: 'worker_error', detail: String(err) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

function renderConfirmed(email, magnet, domainLabel, mailSent) {
  const pdfHref = magnet
    ? `/assets/pdf/${encodeURIComponent(magnet)}.pdf`
    : '/assets/pdf/';
  const confirmed = Boolean(email && String(email).includes('@'));
  const state = confirmed ? 's-done' : 's-confirm';
  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${
  confirmed
    ? 'Подписка подтверждена — Kredato'
    : 'Подписка почти готова — Kredato'
}</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,sans-serif;background:#ffffff;color:#111827;line-height:1.5}
.site{max-width:1100px;margin:0 auto;padding:16px}
.logo{font-size:20px;color:#0f172a}
.logo span{color:#2563eb}
.hero{padding:24px 0}
.hero-compact .wrap{max-width:560px;margin:0 auto}
.tag{display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid #0f172a;color:#0f172a;font-size:12px;margin-bottom:10px}
.tag.green{background:#0f172a;color:#fff;border-color:#0f172a}
.state{display:none}
.state.is-active{display:block}
.lead{color:#374151;font-size:16px}
.muted{color:#6b7280;font-size:14px}
.btn{display:inline-block;padding:12px 24px;border-radius:8px;background:#16a34a;color:#fff;text-decoration:none;font-weight:600;margin-top:12px}
.btn.alt{background:#e5e7eb;color:#0f172a}
.footer{max-width:1100px;margin:0 auto;padding:24px 16px;color:#6b7280;font-size:13px}
</style>
<script src="/assets/js/analytics.js" defer></script>
<script src="/assets/js/consent.js" defer></script>
</head>
<body>
<header class="site">
  <div class="wrap">
    <div class="logo">Kred<span>ato</span></div>
    <nav><a href="/">На главную</a></nav>
  </div>
</header>

<section class="hero hero-compact">
  <div class="wrap">
    <div id="s-confirm" class="state${
      confirmed ? '' : ' is-active'
    }">
      <span class="tag green">Double opt-in</span>
      <h1>Почти готово!</h1>
      <p class="lead">Мы отправили письмо с подтверждением на указанный email. Перейдите по ссылке в письме, чтобы активировать подписку.</p>
      <p class="muted">Не пришло письмо? Проверьте папку «Спам» или напишите нам ответом.</p>
    </div>

    <div id="s-done" class="state${
      confirmed ? ' is-active' : ''
    }">
      <span class="tag green">Готово</span>
      <h1>Подписка подтверждена</h1>
      <p class="lead">Спасибо! Ваш email подтверждён. Теперь можно пользоваться рассылкой Kredato.</p>
      <div id="pdf-block" style="${
        confirmed && magnet ? '' : 'display:none'
      }">
        <p><strong>Ваш PDF-магнит:</strong><br>
          <a id="pdf-link" href="${pdfHref}" style="color:#2563eb;text-decoration:none">Скачать файл</a>
        </p>
        <p class="muted">Если кнопка не открывается — скопируйте ссылку в браузер.</p>
      </div>
      <div class="hero-actions">
        <a href="/" class="btn alt">На главную</a>
      </div>
    </div>
  </div>
</section>

<div class="footer">
  <p>© 2026 Kredato. Материалы носят информационный характер и <strong>не являются финансовой рекомендацией</strong>.</p>
  <p><a href="/">На главную</a> · <a href="/privacy.html">Политика ПДн</a></p>
</div>

<script>
(function(){
  try {
    var params = new URLSearchParams(window.location.search);
    var email = params.get('email') || '';
    var magnet = params.get('magnet') || '';
    confirmed = Boolean(email && email.includes('@'));
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
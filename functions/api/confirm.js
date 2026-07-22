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
      const confirmedUrl = new URL(request.url);
      confirmedUrl.pathname = '/subscribe.html';
      confirmedUrl.search = `confirmed=${encodeURIComponent(email)}`;
      return Response.redirect(confirmedUrl.toString(), 302);
    }

    // Best-effort: помечаем подтверждённым (если настроен audience)
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
    const pdfUrl = magnet ? `https://kredato.com/assets/pdf/${magnet}.pdf` : 'https://kredato.com/assets/pdf/';
    const brand = domainLabel === 'myfinq.xyz' ? 'myfinq.xyz' : 'kredato.com';
    const subject = `Добро пожаловать в Kredato — вот ваш PDF`;
    const welcomeHtml = `<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1f2937">
  <div style="background:#0f172a;color:#e2e8f0;padding:20px;border-radius:12px;margin-bottom:20px">
    <h1 style="margin:0;font-size:22px">Готово — подписка подтверждена</h1>
  </div>
  <p>Спасибо! Ваш email подтверждён. Теперь можно пользоваться рассылкой Kredato.</p>
  <p><strong>Ваш PDF-магнит:</strong><br>
    <a href="${pdfUrl}" style="color:#2563eb;text-decoration:none">${magnet || 'Скачать файл'}</a>
  </p>
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
        subject: 'Добро пожаловать в Kredato — вот ваш PDF',
        html: welcomeHtml,
      }),
    }).catch(() => {});

    const confirmedUrl = new URL(request.url);
    confirmedUrl.pathname = '/subscribe.html';
    confirmedUrl.search = `confirmed=${encodeURIComponent(email)}`;
    return Response.redirect(confirmedUrl.toString(), 302);
  } catch (err) {
    return new Response(JSON.stringify({ status: 'worker_error', detail: String(err) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

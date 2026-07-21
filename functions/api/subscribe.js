/**
 * kredato.com — Cloudflare Pages Function
 * POST /api/subscribe → принимает email, отправляет DOI через Resend.
 */
export async function onRequestPost(context) {
  const { request, env } = context;
  
  // CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: corsHeaders(),
    });
  }

  try {
    const body = await request.json().catch(() => ({}));
    const email = String(body.email || '').trim();
    const source = String(body.source || '').trim() || 'unknown';
    const magnet = String(body.magnet || '').trim() || '';

    if (!email || !email.includes('@')) {
      return json(400, { error: 'email_required' });
    }

    // Базовые проверки
    if (email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return json(400, { error: 'email_invalid' });
    }

    // Если ключа нет — graceful fallback
    const apiKey = env.RESEND_API_KEY || '';
    if (!apiKey) {
      return json(200, { 
        status: 'queued', 
        message: 'email_queued_without_resend',
        source,
        magnet,
      });
    }

    const audienceId = env.RESEND_AUDIENCE_ID || '';
    const from = env.RESEND_FROM || 'Kredato <noreply@kredato.com>';

    // 1) Добавляем в лист (если настроен audience)
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
          custom_properties: { source, magnet },
        }),
      }).catch(() => {});
    }

    // 2) Отправляем DOI
    const resendRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: [email],
        subject: 'Подтвердите подписку — Kredato',
        html: doiTemplate(email, magnet),
      }),
    });

    if (!resendRes.ok) {
      const errText = await resendRes.text().catch(() => '');
      return json(500, { 
        status: 'resend_error', 
        detail: errText.slice(0, 200) 
      });
    }

    return json(200, { 
      status: 'doi_sent', 
      source,
      magnet,
    });

  } catch (e) {
    return json(500, { 
      status: 'error', 
      detail: 'internal_error' 
    });
  }
}

/** GET /api/subscribe — health check + CORS allowlist */
export async function onRequestGet(context) {
  return new Response(JSON.stringify({ ok: true, service: 'kredato-subscribe' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}


/* --- helpers --- */

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function doiTemplate(email, magnet) {
  const confirmUrl = `https://kredato.com/api/confirm?email=${encodeURIComponent(email)}&magnet=${encodeURIComponent(magnet)}`;
  const pdfUrl = magnet ? `https://kredato.com/assets/pdf/${magnet}.pdf` : 'https://kredato.com/assets/pdf/';
  return `<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1f2937">
  <div style="background:#0f172a;color:#e2e8f0;padding:20px;border-radius:12px;margin-bottom:20px">
    <h1 style="margin:0;font-size:22px">Kredato — подтверждение подписки</h1>
  </div>
  <p>Вы оформили подписку на <strong>kredato.com</strong>. Подтвердите email, чтобы активировать её по 152-ФЗ.</p>
  <p>
    <a href="${confirmUrl}" style="display:inline-block;background:#16a34a;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600">
      Подтвердить подписку
    </a>
  </p>
  <p style="font-size:13px;color:#6b7280">Ссылка работает 48 часов. Если вы не оставляли заявку — проигнорируйте это письмо.</p>
  ${magnet ? `<p style="font-size:13px;color:#6b7280">После подтверждения мы пришлём PDF: <a href="${pdfUrl}">${magnet}</a></p>` : ''}
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="font-size:12px;color:#9ca3af">kredato.com · Рассылки по 152-ФЗ с двойным подтверждением. Отписаться в один клик — в каждом письме.</p>
</body>
</html>`;
}

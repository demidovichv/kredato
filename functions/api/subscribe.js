/**
 * kredato.com — Cloudflare Pages Function
 * POST /api/subscribe → принимает email, отправляет DOI через Resend.
 *
 * Поддерживает два аккаунта Resend одновременно:
 *  - RESEND_API_KEY_KREDATO + RESEND_FROM_KREDATO  → kredato.com
 *  - RESEND_API_KEY         + RESEND_FROM_MYFINQ   → myfinq.xyz
 *
 * Приоритет: kredato.com → myfinq.xyz → graceful fallback без отправки.
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

    // Два канала Resend: kredato.com → myfinq.xyz → offline
    const apiKeyKredato = env.RESEND_API_KEY_KREDATO || '';
    const apiKeyMyfinq = env.RESEND_API_KEY || '';
    const fromKredato = env.RESEND_FROM_KREDATO || 'Kredato <noreply@kredato.com>';
    const fromMyfinq = env.RESEND_FROM_MYFINQ || 'Kredato <noreply@myfinq.xyz>';
    const audienceId = env.RESEND_AUDIENCE_ID || '';

    let apiKey = '';
    let from = '';
    let domainLabel = '';

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
      return json(200, {
        status: 'queued',
        message: 'email_queued_without_resend',
        source,
        magnet,
      });
    }

    // 1) Добавляем в лист (если настроен audience)
    if (audienceId) {
      await fetch(
        `https://api.resend.com/audiences/${audienceId}/contacts`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            first_name: '',
            last_name: '',
            custom_properties: { source, magnet, domain: domainLabel },
          }),
        }
      ).catch(() => {});
    }

    // 2) Отправляем DOI
    const subject =
      domainLabel === 'kredato.com'
        ? 'Подтвердите подписку — Kredato'
        : `Подтвердите подписку — Kredato / ${domainLabel}`;

    const resendRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: [email],
        subject,
        html: doiTemplate(email, magnet, domainLabel),
      }),
    });

    if (!resendRes.ok) {
      const errText = await resendRes.text().catch(() => '');
      // fallback: если kredato.com упал, пробуем myfinq.xyz
      if (apiKeyKredato && apiKeyMyfinq) {
        const fallback = await sendVia(
          apiKeyMyfinq,
          fromMyfinq,
          email,
          subject,
          doiTemplate(email, magnet, 'myfinq.xyz')
        );
        if (fallback) {
          return json(200, {
            status: 'doi_sent',
            via: 'myfinq.xyz',
            source,
            magnet,
          });
        }
      }
      return json(500, {
        status: 'resend_error',
        detail: errText.slice(0, 200),
      });
    }

    return json(200, {
      status: 'doi_sent',
      via: domainLabel,
      source,
      magnet,
    });

  } catch (e) {
    return json(500, {
      status: 'error',
      detail: 'internal_error',
    });
  }
}

/** GET /api/subscribe — health check + CORS allowlist */
export async function onRequestGet(context) {
  return new Response(
    JSON.stringify({ ok: true, service: 'kredato-subscribe' }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders(),
      },
    }
  );
}

/* --- helpers --- */

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(),
    },
  });
}

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

async function sendVia(apiKey, from, email, subject, html) {
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ from, to: [email], subject, html }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

function doiTemplate(email, magnet, domainLabel) {
  const confirmUrl = `https://kredato.com/api/confirm?email=${encodeURIComponent(email)}&magnet=${encodeURIComponent(magnet)}`;
  const pdfUrl = magnet
    ? `https://kredato.com/assets/pdf/${magnet}.pdf`
    : 'https://kredato.com/assets/pdf/';
  const brand = domainLabel === 'myfinq.xyz' ? 'myfinq.xyz' : 'kredato.com';
  return `<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1f2937">
  <div style="background:#0f172a;color:#e2e8f0;padding:20px;border-radius:12px;margin-bottom:20px">
    <h1 style="margin:0;font-size:22px">Kredato — подтверждение подписки</h1>
  </div>
  <p>Вы оформили подписку на <strong>${brand}</strong>. Подтвердите email, чтобы активировать её по 152-ФЗ.</p>
  <p>
    <a href="${confirmUrl}" style="display:inline-block;background:#16a34a;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600">
      Подтвердить подписку
    </a>
  </p>
  <p style="font-size:13px;color:#6b7280">Ссылка работает 48 часов. Если вы не оставляли заявку — проигнорируйте это письмо.</p>
  ${magnet ? `<p style="font-size:13px;color:#6b7280">После подтверждения мы пришлём PDF: <a href="${pdfUrl}">${magnet}</a></p>` : ''}
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="font-size:12px;color:#9ca3af">${brand} · Рассылки по 152-ФЗ с двойным подтверждением. Отписаться в один клик — в каждом письме.</p>
</body>
</html>`;
}

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);

  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/assets/')) {
    return new Response(null, { status: 200 });
  }

  return new Response('Not Found', {
    status: 404,
    headers: { 'Content-Type': 'text/plain' }
  });
}

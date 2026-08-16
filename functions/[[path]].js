export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);

  // Пропускаем API и статику
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/assets/')) {
    return NextResponse.next();
  }

  return new Response('Not Found', { status: 404 });
}

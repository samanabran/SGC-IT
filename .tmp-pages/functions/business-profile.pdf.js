export async function onRequestGet(context) {
  const fetchUrl = 'https://raw.githubusercontent.com/samanabran/SGC-IT/main/SGC%20TECH%20AI%20BUSINESS%20PROFILE.pdf';
  const upstreamResponse = await fetch(fetchUrl, {
    method: context.request.method,
    headers: context.request.headers,
    cf: { cacheTtl: 86400, cacheEverything: true }
  });

  const headers = new Headers(upstreamResponse.headers);
  headers.set('Content-Type', 'application/pdf');
  headers.set('Content-Disposition', 'inline; filename="SGC TECH AI BUSINESS PROFILE.pdf"');

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers
  });
}

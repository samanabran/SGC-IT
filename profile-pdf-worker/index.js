export default {
  async fetch(request, env, ctx) {
    const url = 'https://raw.githubusercontent.com/renbran/SGC-IT/main/SGC%20TECH%20AI%20BUSINESS%20PROFILE.pdf';
    const upstreamResponse = await fetch(url, {
      method: request.method,
      headers: request.headers,
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
};

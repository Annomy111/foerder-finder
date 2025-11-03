export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Forward to OCI backend via HTTPS (nginx reverse proxy)
    const backendUrl = `https://130.61.76.199${url.pathname}${url.search}`;

    // Handle preflight immediately
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
          'Access-Control-Allow-Headers': 'Authorization, Content-Type, Accept'
        }
      });
    }

    try {
      // Copy request but change URL and add Host header
      const modifiedHeaders = new Headers(request.headers);
      modifiedHeaders.set('Host', '130.61.76.199');

      const modifiedRequest = new Request(backendUrl, {
        method: request.method,
        headers: modifiedHeaders,
        body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      });

      // Fetch from backend (allow self-signed cert)
      const response = await fetch(modifiedRequest);

      // Add CORS headers
      const modifiedResponse = new Response(response.body, response);
      modifiedResponse.headers.set('Access-Control-Allow-Origin', '*');
      modifiedResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
      modifiedResponse.headers.set('Access-Control-Allow-Headers', 'Authorization, Content-Type, Accept');

      return modifiedResponse;
    } catch (error) {
      return new Response(JSON.stringify({ error: 'Backend connection failed', details: error.message }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  },
};

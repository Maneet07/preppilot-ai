export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Skip api routes - let the backend handle them
    // In production, these would be proxied or handled by the FastAPI setup
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/v1/')) {
      // Return placeholder - in real deployment, proxy to backend
      return new Response(JSON.stringify({ error: 'backend_not_configured' }), {
        headers: { 'Content-Type': 'application/json' },
        status: 503
      });
    }
    
    // Serve SPA - return index.html for all other routes
    if (url.pathname === '/' || url.pathname === '/index.html') {
      return fetch('dist/index.html');
    }
    
    // Try to serve static assets
    const assetPath = `dist/${url.pathname === '/' ? 'index.html' : url.pathname}`;
    const cacheKey = assetPath;
    
    try {
      const assetResponse = await env.ASSETS.fetch(request);
      if (assetResponse.status !== 404) {
        return assetResponse;
      }
    } catch (e) {
      // Asset not found
    }
    
    // Fallback to index.html for SPA routing
    return fetch('dist/index.html');
  }
};
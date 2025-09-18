/* Root-scoped SW controlling entire origin */
const VERSION = '2025-09-18-root-1';
const CACHE_NAME = `quantlens-root-${VERSION}`;
const FALLBACK_HTML = '/site/index.html';

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      try { await cache.add(new Request(FALLBACK_HTML, { cache: 'reload' })); } catch {}
    })()
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter(k => k.startsWith('quantlens-root-') && k !== CACHE_NAME).map(k => caches.delete(k)));
      await self.clients.claim();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const accept = req.headers.get('accept') || '';
  const isHTML = req.mode === 'navigate' || accept.includes('text/html');
  if (isHTML) {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req, { cache: 'no-store' });
        const cache = await caches.open(CACHE_NAME);
        // Keep a fresh fallback copy of site index
        cache.put(FALLBACK_HTML, fresh.clone());
        return fresh;
      } catch (err) {
        const cache = await caches.open(CACHE_NAME);
        const offline = await cache.match(FALLBACK_HTML);
        if (offline) return offline;
        return new Response('<!doctype html><title>Offline</title><h1>Offline</h1>', { headers: { 'Content-Type': 'text/html' } });
      }
    })());
    return;
  }
  // Non-HTML: try network with no-store, else cache
  event.respondWith((async () => {
    try { return await fetch(req, { cache: 'no-store' }); }
    catch {
      const cache = await caches.open(CACHE_NAME);
      const hit = await cache.match(req, { ignoreSearch: true });
      if (hit) return hit;
      throw new Error('Network and cache miss');
    }
  })());
});

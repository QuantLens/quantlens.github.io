/* QuantLens Service Worker: network-first for HTML to avoid stale caches */
const VERSION = '2025-09-18-1';
const CACHE_NAME = `quantlens-shell-${VERSION}`;
const SHELL_URL = 'index.html'; // relative to scope

self.addEventListener('install', (event) => {
  // Precache a minimal shell for offline fallback
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        await cache.add(new Request(SHELL_URL, { cache: 'reload' }));
      } catch (err) {
        // Ignore if offline during first install
      }
    })()
  );
  // Activate this SW immediately
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Clean up old caches and take control of open pages
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => k.startsWith('quantlens-shell-') && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

// Helper: network-first for navigations with offline fallback to cached shell
async function handleNavigation(event) {
  try {
    const resp = await fetch(event.request, { cache: 'no-store' });
    // Optionally refresh shell cache with fresh copy of index
    const cache = await caches.open(CACHE_NAME);
    cache.put(SHELL_URL, resp.clone());
    return resp;
  } catch (err) {
    const cache = await caches.open(CACHE_NAME);
    const offline = await cache.match(SHELL_URL);
    if (offline) return offline;
    // As a last resort, return a basic response
    return new Response('<!doctype html><title>Offline</title><h1>Offline</h1>', { headers: { 'Content-Type': 'text/html' } });
  }
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const accept = req.headers.get('accept') || '';
  const isHTML = req.mode === 'navigate' || accept.includes('text/html');
  if (isHTML) {
    event.respondWith(handleNavigation(event));
    return;
  }
  // For other assets, prefer network with no-store; fall back to cache if present
  event.respondWith(
    (async () => {
      try {
        return await fetch(req, { cache: 'no-store' });
      } catch (err) {
        const cache = await caches.open(CACHE_NAME);
        const hit = await cache.match(req, { ignoreSearch: true });
        if (hit) return hit;
        throw err;
      }
    })()
  );
});

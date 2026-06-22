// FIFA World Cup 2026 Tracker — Service Worker
const CACHE_NAME = 'wc2026-v3';
const NETWORK_FIRST = ['scores.json', 'index.html', '/worldcup2026-tracker/', '/worldcup2026-tracker/index.html'];

// Assets to pre-cache on install (fonts, icons — rarely change)
const PRECACHE_ASSETS = [
  'icon-192.png',
  'icon-512.png',
  'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600;700&display=swap'
];

// Install — pre-cache static assets only (NOT index.html)
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_ASSETS).catch(function() {
        // Silently fail on individual asset errors
      });
    })
  );
  self.skipWaiting();
});

// Activate — clean up old caches
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) { return key !== CACHE_NAME; })
            .map(function(key) { return caches.delete(key); })
      );
    })
  );
  self.clients.claim();
});

// Fetch strategy:
// - index.html + scores.json → network-first (always fresh)
// - everything else → cache-first (fonts, icons etc.)
self.addEventListener('fetch', function(e) {
  var url = e.request.url;

  // Network-first for index.html and scores.json
  var isNetworkFirst = NETWORK_FIRST.some(function(p) { return url.includes(p); });
  if (isNetworkFirst) {
    e.respondWith(
      fetch(e.request).then(function(response) {
        // Cache a copy for offline fallback
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(e.request, clone);
          });
        }
        return response;
      }).catch(function() {
        // Offline fallback — serve cached version
        return caches.match(e.request);
      })
    );
    return;
  }

  // Cache-first for everything else (fonts, icons)
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      if (cached) return cached;
      return fetch(e.request).then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(e.request, clone);
          });
        }
        return response;
      });
    })
  );
});

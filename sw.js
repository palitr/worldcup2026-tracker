// FIFA World Cup 2026 Tracker — Service Worker
const CACHE_NAME = 'wc2026-v2';
const SCORES_URL = 'scores.json';

// Assets to pre-cache on install
const PRECACHE_ASSETS = [
  '/worldcup2026-tracker/',
  '/worldcup2026-tracker/index.html',
  'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600;700&display=swap'
];

// Install — pre-cache core assets
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_ASSETS).catch(function() {
        // Silently fail on individual asset errors (e.g. fonts offline)
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

// Fetch — network-first for scores.json, cache-first for everything else
self.addEventListener('fetch', function(e) {
  var url = e.request.url;

  // Always network-first for scores.json (live data must be fresh)
  if (url.includes(SCORES_URL)) {
    e.respondWith(
      fetch(e.request).catch(function() {
        return caches.match(e.request);
      })
    );
    return;
  }

  // Cache-first for all other assets
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      if (cached) return cached;
      return fetch(e.request).then(function(response) {
        // Cache valid responses
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(e.request, clone);
          });
        }
        return response;
      }).catch(function() {
        // Offline fallback for navigation requests
        if (e.request.mode === 'navigate') {
          return caches.match('/worldcup2026-tracker/index.html');
        }
      });
    })
  );
});

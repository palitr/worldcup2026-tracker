// FIFA World Cup 2026 Tracker — Service Worker
const CACHE_NAME = 'wc2026-v4';
const NETWORK_FIRST = ['index.html', '/worldcup2026-tracker/', '/worldcup2026-tracker/index.html'];
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
      return cache.addAll(PRECACHE_ASSETS).catch(function() {});
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

// Fetch strategy
self.addEventListener('fetch', function(e) {
  var url = e.request.url;
  var isNetworkFirst = NETWORK_FIRST.some(function(p) { return url.includes(p); });
  if (isNetworkFirst) {
    e.respondWith(
      fetch(e.request).then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) { cache.put(e.request, clone); });
        }
        return response;
      }).catch(function() { return caches.match(e.request); })
    );
    return;
  }
  if (url.includes('scores.json')) {
    e.respondWith(
      caches.open(CACHE_NAME).then(function(cache) {
        return cache.match(e.request).then(function(cached) {
          var fetchPromise = fetch(e.request).then(function(response) {
            if (response && response.status === 200) cache.put(e.request, response.clone());
            return response;
          });
          return cached || fetchPromise;
        });
      })
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      if (cached) return cached;
      return fetch(e.request).then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) { cache.put(e.request, clone); });
        }
        return response;
      });
    })
  );
});

// ── Notification click — open / focus the tracker ─────────────────────────
self.addEventListener('notificationclick', function(e) {
  e.notification.close();
  var target = e.notification.data && e.notification.data.url
    ? e.notification.data.url
    : '/worldcup2026-tracker/';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(list) {
      // If tracker already open, focus it
      for (var i = 0; i < list.length; i++) {
        var c = list[i];
        if (c.url.includes('worldcup2026-tracker') && 'focus' in c) {
          return c.focus();
        }
      }
      // Otherwise open a new tab
      if (clients.openWindow) return clients.openWindow(target);
    })
  );
});

// ── Push handler stub (for future server-push support) ────────────────────
self.addEventListener('push', function(e) {
  if (!e.data) return;
  var data = e.data.json();
  e.waitUntil(
    self.registration.showNotification(data.title || 'WC2026 Tracker', {
      body: data.body || '',
      icon: '/worldcup2026-tracker/icon-192.png',
      badge: '/worldcup2026-tracker/icon-192.png',
      data: data
    })
  );
});

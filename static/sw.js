self.addEventListener('install', e => {
  e.waitUntil(caches.open('wa-links-v1')
    .then(cache => cache.addAll([
      '/',
      '/static/css/style.css',
      '/static/manifest.json'
    ]))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request)
      .then(r => r || fetch(e.request))
  );
});

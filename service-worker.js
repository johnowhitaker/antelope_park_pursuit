const cacheName = 'pwa-cache-v3';
const urlsToCache = [
    './',
    'index.html',
    'styles.css',
    'app.js',
    'manifest.json',
    'favicon.ico',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(cacheName).then(cache => {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);
    // Only handle GET
    if (req.method !== 'GET') return;

    // Network-first for data to avoid stale tasks
    if (url.pathname.includes('/data/')) {
        event.respondWith(
            fetch(req).then(res => {
                if (res.ok) {
                    const clone = res.clone();
                    caches.open(cacheName).then(c => c.put(req, clone));
                }
                return res;
            }).catch(() => caches.match(req))
        );
        return;
    }

    // Cache-first for app shell and images
    event.respondWith(
        caches.match(req).then(cached => {
            if (cached) return cached;
            return fetch(req).then(res => {
                if ((url.pathname.includes('/images/')) && res.ok) {
                    const clone = res.clone();
                    caches.open(cacheName).then(c => c.put(req, clone));
                }
                return res;
            });
        })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== cacheName).map(k => caches.delete(k))
        ))
    );
});

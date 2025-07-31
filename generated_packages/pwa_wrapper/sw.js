const CACHE_NAME = "app-v1";
self.addEventListener("install", e => {
    e.waitUntil(caches.open(CACHE_NAME));
});
self.addEventListener("fetch", e => {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
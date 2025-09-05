self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open("hospital-app-cache").then(function(cache) {
      return cache.addAll([
        "./",
        "./static/manifest.json",
        "./assets/Logo_final_800px.png"
      ]);
    })
  );
});

self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});

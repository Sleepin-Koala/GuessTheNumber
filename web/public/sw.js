// Service worker: app shell en cache, assets cache-first, API toujours reseau.
// Les valeurs ci-dessous sont remplacees au build par vite.config.js (plugin swPrecache)
const VERSION = "__BUILD_ID__";
const BUILD_ASSETS = ["__ASSET_LIST__"].filter((u) => u !== "__ASSET_LIST__");
const SHELL_CACHE = `shell-${VERSION}`;
const ASSET_CACHE = `assets-${VERSION}`;
const SHELL_URLS = ["/", "/offline.html", "/manifest.webmanifest", "/favicon.svg", "/icons/icon-192.png", "/icons/icon-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((c) => c.addAll([...SHELL_URLS, ...BUILD_ASSETS])));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => ![SHELL_CACHE, ASSET_CACHE].includes(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// le client decide quand activer une nouvelle version
self.addEventListener("message", (event) => {
  if (event.data === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // API (autre origine) -> reseau

  // navigation: reseau d'abord, puis shell en cache (SPA), puis page hors ligne
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(SHELL_CACHE).then((c) => c.put("/", copy));
          return res;
        })
        .catch(async () => (await caches.match("/")) || (await caches.match("/offline.html")))
    );
    return;
  }

  // fichiers statiques: cache d'abord
  event.respondWith(
    // ignoreVary: les modules JS sont demandes en mode CORS (en-tete Origin), pas le precache
    caches.match(req, { ignoreVary: true }).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(ASSET_CACHE).then((c) => c.put(req, copy));
        }
        return res;
      });
    })
  );
});

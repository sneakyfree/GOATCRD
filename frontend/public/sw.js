// GOATCRD Service Worker v1
// Caching strategies for offline support

const CACHE_NAME = 'goatcrd-v1';
const STATIC_CACHE = 'goatcrd-static-v1';
const API_CACHE = 'goatcrd-api-v1';

// Assets to cache immediately on install
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/manifest.json',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== STATIC_CACHE && name !== API_CACHE)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip non-http(s) requests
    if (!url.protocol.startsWith('http')) return;

    // API requests - network first, then cache
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirst(request, API_CACHE));
        return;
    }

    // Static assets - cache first
    if (isStaticAsset(url.pathname)) {
        event.respondWith(cacheFirst(request, STATIC_CACHE));
        return;
    }

    // HTML pages - network first with offline fallback
    if (request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(networkFirstWithFallback(request));
        return;
    }

    // Default - network first
    event.respondWith(networkFirst(request, CACHE_NAME));
});

// Cache-first strategy
async function cacheFirst(request, cacheName) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('[SW] Fetch failed:', error);
        throw error;
    }
}

// Network-first strategy
async function networkFirst(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        const cached = await caches.match(request);
        if (cached) {
            console.log('[SW] Serving from cache:', request.url);
            return cached;
        }
        throw error;
    }
}

// Network-first with offline fallback for HTML
async function networkFirstWithFallback(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        // Try cache
        const cached = await caches.match(request);
        if (cached) return cached;

        // Fallback to index.html for SPA routing
        const fallback = await caches.match('/index.html');
        if (fallback) return fallback;

        // Return offline page
        return new Response(
            `<!DOCTYPE html>
            <html>
            <head>
                <title>Offline - GOATCRD</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { 
                        font-family: system-ui, sans-serif;
                        display: flex; align-items: center; justify-content: center;
                        min-height: 100vh; margin: 0;
                        background: #0f172a; color: white; text-align: center;
                    }
                    .container { max-width: 400px; padding: 2rem; }
                    h1 { font-size: 3rem; margin-bottom: 1rem; }
                    p { color: rgba(255,255,255,0.7); }
                    button { 
                        margin-top: 2rem; padding: 1rem 2rem;
                        background: #3b82f6; color: white;
                        border: none; border-radius: 8px;
                        font-size: 1rem; cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📡</h1>
                    <h2>You're Offline</h2>
                    <p>Please check your internet connection and try again.</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            </body>
            </html>`,
            { headers: { 'Content-Type': 'text/html' } }
        );
    }
}

// Check if request is for a static asset
function isStaticAsset(pathname) {
    const extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.ico'];
    return extensions.some((ext) => pathname.endsWith(ext));
}

// Push notifications
self.addEventListener('push', (event) => {
    const data = event.data?.json() || {};
    const title = data.title || 'GOATCRD';
    const options = {
        body: data.body || 'You have a new notification',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        data: data.url || '/',
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const url = event.notification.data || '/';

    event.waitUntil(
        self.clients.matchAll({ type: 'window' }).then((clients) => {
            for (const client of clients) {
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }
            return self.clients.openWindow(url);
        })
    );
});

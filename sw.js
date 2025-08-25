// Service Worker para MetaX PWA const CACHE\_NAME = 'metax-v1.0.0'; const urlsToCache = \[ '/', '/index.html', '/manifest.json', '/favicon.ico', // CSS e JS principais '<https://cdn.tailwindcss.com>', '<https://unpkg.com/lucide@latest/dist/umd/lucide.js>' ];

// Instalar o Service Worker self.addEventListener('install', (event) => { console.log('MetaX: Service Worker instalando...'); event.waitUntil( caches.open(CACHE\_NAME) .then((cache) => { console.log('MetaX: Cache aberto'); return cache.addAll(urlsToCache); }) .then(() => { console.log('MetaX: Recursos em cache'); return self.skipWaiting(); }) ); });

// Ativar o Service Worker self.addEventListener('activate', (event) => { console.log('MetaX: Service Worker ativo'); event.waitUntil( caches.keys().then((cacheNames) => { return Promise.all( cacheNames.map((cacheName) => { if (cacheName !== CACHE\_NAME) { console.log('MetaX: Removendo cache antigo:', cacheName); return caches.delete(cacheName); } }) ); }).then(() => { return self.clients.claim(); }) ); });

// Interceptar requisições self.addEventListener('fetch', (event) => { event.respondWith( caches.match(event.request) .then((response) => { // Retorna do cache se disponível if (response) { return response; }

```
    // Senão, busca na rede
    return fetch(event.request).then((response) => {
      // Verifica se é uma resposta válida
      if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
      }
      
      // Clona a resposta para armazenar no cache
      const responseToCache = response.clone();
      
      caches.open(CACHE_NAME)
        .then((cache) => {
          cache.put(event.request, responseToCache);
        });
        
      return response;
    }).catch(() => {
      // Se offline, retorna página offline personalizada
      if (event.request.destination === 'document') {
        return caches.match('/');
      }
    });
  })
```

); });

// Push notifications (futuro) self.addEventListener('push', (event) => { console.log('MetaX: Push notification recebida');

const options = { body: event.data ? event.data.text() : 'Nova notificação MetaX', icon: '/icon-192.png', badge: '/icon-192.png', vibrate: \[200, 100, 200], data: { dateOfArrival: Date.now(), primaryKey: '1' }, actions: \[ { action: 'explore', title: 'Abrir MetaX', icon: '/icon-192.png' }, { action: 'close', title: 'Fechar' } ] };

event.waitUntil( self.registration.showNotification('MetaX Sistema', options) ); });

// Click em notificação self.addEventListener('notificationclick', (event) => { console.log('MetaX: Notificação clicada'); event.notification.close();

if (event.action === 'explore') { event.waitUntil(clients.openWindow('/')); } });

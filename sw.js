/* Public assets only: authenticated APIs and account pages never enter caches. */
const CACHE='electrol-india-com-v1';
self.addEventListener('install',e=>e.waitUntil(self.skipWaiting()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith('electrol-india-com-')&&k!==CACHE)await caches.delete(k);await self.clients.claim()})()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||!/^\/(css|js|assets|data)\//.test(u.pathname)||e.request.headers.has('authorization'))return;e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(()=>caches.match(e.request)))});
self.addEventListener('push',e=>{e.waitUntil((async()=>{let d;try{d=e.data.json()}catch{return}await self.registration.showNotification(d.title||'Electrol India update',{body:d.body||'',tag:d.id||'electrol-update',icon:'/assets/favicon.svg',data:{url:typeof d.url==='string'&&d.url.startsWith('/')&&!d.url.startsWith('//')?d.url:'/account/notifications/'}})})())});
self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(clients.openWindow(new URL(e.notification.data?.url||'/account/notifications/',location.origin).href))});

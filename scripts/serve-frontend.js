const http = require('http');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const buildDir = path.join(root, 'frontend', 'build');
const port = Number(process.env.FRONTEND_PORT || 3000);
const backendHost = process.env.BACKEND_HOST || '127.0.0.1';
const backendPort = Number(process.env.BACKEND_PORT || 8000);

const apiPrefixes = [
  '/api/v1',
  '/api/v2',
  '/health',
  '/attacks',
  '/normal-flows',
  '/simulate',
  '/simulate-attack/',
  '/decisions',
  '/reason-codes',
  '/metrics',
  '/connectors',
];

const contentTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.txt': 'text/plain; charset=utf-8',
};

function isApiRequest(urlPath) {
  return apiPrefixes.some(prefix => urlPath === prefix || urlPath.startsWith(prefix));
}

function proxyToBackend(req, res) {
  const options = {
    hostname: backendHost,
    port: backendPort,
    path: req.url,
    method: req.method,
    headers: req.headers,
  };

  const proxyReq = http.request(options, proxyRes => {
    res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', err => {
    res.writeHead(502, { 'content-type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ detail: `Backend unavailable: ${err.message}` }));
  });

  req.pipe(proxyReq);
}

function serveStatic(req, res) {
  const parsedUrl = new URL(req.url, `http://localhost:${port}`);
  const safePath = decodeURIComponent(parsedUrl.pathname).replace(/^\/+/, '');
  let filePath = path.join(buildDir, safePath);

  if (!filePath.startsWith(buildDir)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(buildDir, 'index.html');
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'content-type': contentTypes[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

if (!fs.existsSync(path.join(buildDir, 'index.html'))) {
  console.error('frontend/build/index.html not found. Run npm.cmd run build first.');
  process.exit(1);
}

const indexHtml = fs.readFileSync(path.join(buildDir, 'index.html'), 'utf8');
if (indexHtml.includes('BridgeGuard MVP') || indexHtml.includes('/static/app.js')) {
  console.error('Detected legacy v1 static bundle in frontend/build. Run npm.cmd run build from frontend before serving.');
  process.exit(1);
}

http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://localhost:${port}`);
  if (isApiRequest(parsedUrl.pathname)) {
    proxyToBackend(req, res);
    return;
  }
  serveStatic(req, res);
}).listen(port, () => {
  console.log(`BridgeGuard frontend available at http://localhost:${port}`);
  console.log(`Proxying API requests to http://${backendHost}:${backendPort}`);
});

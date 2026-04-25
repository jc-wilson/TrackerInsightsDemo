import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const root = normalize(join(import.meta.dirname, ".."));
const port = Number.parseInt(process.env.PORT || "4173", 10);

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};

function resolvePath(url) {
  const pathname = new URL(url, `http://localhost:${port}`).pathname;
  const relativePath = pathname === "/" ? "frontend/index.html" : pathname.slice(1);
  const resolved = normalize(join(root, relativePath));

  if (!resolved.startsWith(root)) {
    return null;
  }

  return resolved;
}

const server = createServer(async (request, response) => {
  const filePath = resolvePath(request.url);

  if (!filePath) {
    response.writeHead(403);
    response.end("Forbidden");
    return;
  }

  try {
    const body = await readFile(filePath);
    response.writeHead(200, {
      "Content-Type": contentTypes[extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    response.end(body);
  } catch {
    response.writeHead(404);
    response.end("Not found");
  }
});

server.listen(port, () => {
  console.log(`Tracker Insights frontend running at http://localhost:${port}`);
});

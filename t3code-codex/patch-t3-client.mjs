import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const clientDir = process.env.T3_CLIENT_DIR ?? "/usr/local/lib/node_modules/t3/dist/client";
const indexHtmlPath = join(clientDir, "index.html");
const assetsDir = join(clientDir, "assets");

function replaceRequired(source, target, replacement, label) {
  if (!source.includes(target)) {
    throw new Error(`T3 client patch target not found: ${label}`);
  }
  return source.split(target).join(replacement);
}

if (!existsSync(indexHtmlPath)) {
  throw new Error(`T3 client index.html not found at ${indexHtmlPath}`);
}

let indexHtml = readFileSync(indexHtmlPath, "utf8");
indexHtml = replaceRequired(indexHtml, 'href="/favicon.ico"', 'href="./favicon.ico"', "favicon");
indexHtml = replaceRequired(
  indexHtml,
  'href="/apple-touch-icon.png"',
  'href="./apple-touch-icon.png"',
  "apple touch icon",
);
indexHtml = replaceRequired(indexHtml, 'src="/assets/', 'src="./assets/', "script assets");
indexHtml = replaceRequired(indexHtml, 'href="/assets/', 'href="./assets/', "style assets");
writeFileSync(indexHtmlPath, indexHtml);

const indexJsPath = readdirSync(assetsDir)
  .filter((entry) => /^index-.*\.js$/.test(entry))
  .map((entry) => join(assetsDir, entry))[0];

if (!indexJsPath) {
  throw new Error(`T3 client index bundle not found in ${assetsDir}`);
}

let indexJs = readFileSync(indexJsPath, "utf8");
indexJs = replaceRequired(
  indexJs,
  "new Worker(`/assets/",
  "new Worker(`./assets/",
  "worker asset path",
);
indexJs = replaceRequired(
  indexJs,
  "let r=new URL(Pge(n.target.httpBaseUrl));return r.pathname=e,t&&(r.search=new URLSearchParams(t).toString()),r.toString()",
  "let r=n.source===`window-origin`?new URL(e.replace(/^\\/+/,``),new URL(`./`,window.location.href)):new URL(Pge(n.target.httpBaseUrl));return n.source===`window-origin`||(r.pathname=e),t&&(r.search=new URLSearchParams(t).toString()),r.toString()",
  "http API base path",
);
indexJs = replaceRequired(
  indexJs,
  "return t.pathname=`/ws`,t.toString()",
  "return t.pathname=new URL(`./ws`,window.location.href).pathname,t.toString()",
  "websocket path",
);
indexJs = replaceRequired(
  indexJs,
  "return ti({routeTree:Lzt,history:e,context:",
  "return ti({routeTree:Lzt,basepath:new URL(`./`,location.href).pathname.replace(/\\/$/,``)||`/`,history:e,context:",
  "router basepath",
);
writeFileSync(indexJsPath, indexJs);

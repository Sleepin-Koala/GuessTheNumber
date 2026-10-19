import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

// Injecte dans dist/sw.js la liste des fichiers du build (pour le mode hors ligne)
// et un identifiant de version (pour renouveler le cache a chaque build).
function swPrecache() {
  let outDir = 'dist'
  return {
    name: 'sw-precache',
    apply: 'build',
    configResolved(config) { outDir = config.build.outDir },
    writeBundle(_options, bundle) {
      // les gros chunks charges a la demande (three.js) ne sont pas precaches
      const onDemand = (f) => bundle[f].type === 'chunk' && !bundle[f].isEntry && bundle[f].code.length > 400_000
      const bigAudio = (f) => /\.(mp3|wav)$/.test(f) && (bundle[f].source?.length ?? 0) > 100_000   // musique / gros sons: telecharges au premier usage
      const assets = Object.keys(bundle).filter((f) => !f.endsWith('.map') && !onDemand(f) && !bigAudio(f)).map((f) => '/' + f)
      const file = join(outDir, 'sw.js')
      const source = readFileSync(file, 'utf8')
        .replace('"__ASSET_LIST__"]', JSON.stringify(assets).slice(1))
        .replace('__BUILD_ID__', Date.now().toString(36))
      writeFileSync(file, source)
    },
  }
}

// Politique de securite du contenu (production uniquement: le serveur de dev a besoin de scripts inline).
// connect-src n'autorise que l'API configuree (HTTP + WebSocket). frame-ancestors / X-Frame-Options sont a poser
// dans les en-tetes du serveur qui heberge ces fichiers (une balise <meta> ne les prend pas en compte).
function csp(apiOrigin) {
  const ws = apiOrigin.replace(/^http/, 'ws')
  const policy = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "media-src 'self' data: blob:",
    "font-src 'self' data:",
    `connect-src 'self' ${apiOrigin} ${ws}`,
    "worker-src 'self'",
    "manifest-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; ')
  return {
    name: 'csp',
    apply: 'build',
    transformIndexHtml: (html) => html.replace('<head>', `<head>\n    <meta http-equiv="Content-Security-Policy" content="${policy}" />\n    <meta name="referrer" content="no-referrer" />`),
  }
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const api = loadEnv(mode, process.cwd(), '').VITE_API_URL || 'http://127.0.0.1:8000'
  return { plugins: [react() , tailwindcss(), swPrecache(), csp(api)] }
})

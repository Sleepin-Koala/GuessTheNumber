import { defineConfig } from 'vite'
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
      const assets = Object.keys(bundle).filter((f) => !f.endsWith('.map')).map((f) => '/' + f)
      const file = join(outDir, 'sw.js')
      const source = readFileSync(file, 'utf8')
        .replace('"__ASSET_LIST__"]', JSON.stringify(assets).slice(1))
        .replace('__BUILD_ID__', Date.now().toString(36))
      writeFileSync(file, source)
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react() , tailwindcss(), swPrecache()],
})

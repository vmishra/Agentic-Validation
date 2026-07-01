import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    port: Number(process.env.AEGIS_FE_PORT) || 5176,
    proxy: {
      '/api': { target: `http://127.0.0.1:${process.env.AEGIS_BE_PORT || 8791}`, changeOrigin: true },
    },
  },
})

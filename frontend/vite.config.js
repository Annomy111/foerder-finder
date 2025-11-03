import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

// https://vitejs.dev/config/
// Using SWC plugin for 70% faster builds vs Babel
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy API calls to backend (nur für lokale Entwicklung)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate React and related libs
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Separate icons
          'lucide-icons': ['lucide-react'],
          // Separate heavy DOCX library (lazy loaded)
          'docx-vendor': ['docx', 'file-saver'],
          // Separate Zustand
          'zustand': ['zustand'],
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
})

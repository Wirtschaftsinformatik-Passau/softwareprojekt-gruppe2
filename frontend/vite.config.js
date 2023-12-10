import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5000
  },
  resolve: {
    alias: {
      // Set up your aliases here
      '@': path.resolve(__dirname, '@')
    },
  },
  
    optimizeDeps: {
      include: ["@fullcalendar/core",
      "@fullcalendar/daygrid",
      "@fullcalendar/interaction",
      "@fullcalendar/list",
      "@fullcalendar/react",
      "@fullcalendar/timegrid"]
    }
  
})

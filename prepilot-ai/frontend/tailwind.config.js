/** @type {import('tailwindcss').config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#f8f9fa',
          secondary: '#ffffff',
          muted: '#f1f3f5',
        },
        fg: {
          primary: '#1e293b',
          secondary: '#64748b',
          muted: '#94a3b8',
        },
        accent: {
          primary: '#4f46e5',
          muted: '#a5f3fc',
        },
        border: '#e2e8f0',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
    },
  },
  plugins: [],
}
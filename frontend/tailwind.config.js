/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FFD700',
        secondary: '#FFA500',
        accent: '#FF6B6B',
        'accent-dark': '#E63946',
        bg: '#F8F9FA',
        'card-bg': '#FFFFFF',
        'text-primary': '#2D3748',
        'text-secondary': '#718096'
      },
      fontFamily: {
        game: ['Segoe UI', 'Microsoft YaHei', 'sans-serif'],
        pixel: ['Courier New', 'monospace']
      },
      boxShadow: {
        'magic': '0 10px 40px rgba(255, 215, 0, 0.3), 0 4px 12px rgba(0, 0, 0, 0.1)',
        'card': '0 4px 20px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.5)'
      }
    }
  },
  plugins: []
}

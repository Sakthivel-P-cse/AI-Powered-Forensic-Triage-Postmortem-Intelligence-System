/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forensic: {
          bg: '#0D1117',
          surface: '#11161D',
          panel: '#161B22',
          border: '#1F2A37',
          line: '#243042',
          muted: '#7A8899',
          text: '#D6E1EE',
          accent: '#00C8FF',
          accentDim: '#0A8AB0',
          warn: '#FFB454',
          danger: '#FF5C7A',
          critical: '#FF2E5B',
          ok: '#5CFFB1',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace', 'monospace'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(0,200,255,0.25), 0 0 24px rgba(0,200,255,0.10)',
      },
    },
  },
  plugins: [],
};

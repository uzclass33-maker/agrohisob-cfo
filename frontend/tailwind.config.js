/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand green — deep, calm "field pine" tones
        agro: {
          50: '#f1f7f3',
          100: '#e0eee5',
          200: '#c3dccd',
          300: '#99c3ab',
          400: '#6ca586',
          500: '#4c8a6a',
          600: '#397054',
          700: '#2f5a45',
          800: '#274939',
          900: '#213c30',
          950: '#10211a',
        },
        // Secondary navy — trust, ledger, precision
        navy: {
          50: '#f4f6fa',
          100: '#e8ecf4',
          200: '#cfd9e8',
          300: '#a9bad4',
          400: '#7d94ba',
          500: '#5d76a2',
          600: '#4a5f87',
          700: '#3d4d6e',
          800: '#25304d',
          900: '#1a2340',
          950: '#101527',
        },
        // Warm agricultural accent — harvest gold, used sparingly
        harvest: {
          50: '#fbf7ec',
          100: '#f6edd3',
          200: '#ecd9a2',
          300: '#dfc06b',
          400: '#d3a747',
          500: '#c08f33',
          600: '#a37228',
          700: '#835823',
          800: '#6c4823',
          900: '#5c3c21',
          950: '#341f0f',
        },
        // Neutral page canvas — very light green-tinted paper white
        canvas: '#f6f8f5',
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
      },
      boxShadow: {
        card: '0 1px 2px rgba(16, 33, 26, 0.04), 0 1px 3px rgba(16, 33, 26, 0.06)',
        lift: '0 12px 32px -14px rgba(16, 33, 26, 0.18), 0 2px 8px rgba(16, 33, 26, 0.06)',
      },
      keyframes: {
        rise: {
          from: { opacity: '0', transform: 'translateY(14px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        growBar: {
          from: { transform: 'scaleX(0)' },
          to: { transform: 'scaleX(1)' },
        },
        softPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.55' },
        },
      },
      animation: {
        rise: 'rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) both',
        fadeIn: 'fadeIn 0.6s ease-out both',
        growBar: 'growBar 0.9s cubic-bezier(0.22, 1, 0.36, 1) both',
        softPulse: 'softPulse 2.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

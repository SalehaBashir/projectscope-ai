/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2a835f',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#12544f',
        },
        deep: '#092328',
        accent: {
          DEFAULT: '#8bbb92',
          foreground: '#0d1f1c',
        },
        background: '#f7faf8',
        surface: '#ffffff',
        foreground: '#0d1f1c',
        muted: {
          DEFAULT: '#eef3f0',
          foreground: '#5b6e68',
        },
        border: '#e1e8e4',
        success: '#1a7f42',
        warning: '#b26a00',
        danger: '#c84141',
      },
      fontFamily: {
        sans: ['var(--font-inter)', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '14px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(9, 35, 40, 0.06)',
        md: '0 4px 16px rgba(9, 35, 40, 0.08)',
        lg: '0 8px 30px rgba(9, 35, 40, 0.12)',
      },
    },
  },
  plugins: [],
}

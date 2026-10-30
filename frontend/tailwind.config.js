/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#050811",
          card: "#0d1322",
          border: "#1e293b",
          cyan: "#00f3ff",
          emerald: "#10b981",
          crimson: "#ef4444",
          amber: "#f59e0b",
          purple: "#a855f7"
        }
      },
      animation: {
        'pulse-fast': 'pulse 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { filter: 'drop-shadow(0 0 4px rgba(0, 243, 255, 0.6))' },
          '100%': { filter: 'drop-shadow(0 0 16px rgba(0, 243, 255, 0.9))' },
        }
      }
    },
  },
  plugins: [],
};


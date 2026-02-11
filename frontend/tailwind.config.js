/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        golf: {
          green: '#10b981',
          fairway: '#22c55e',
          rough: '#84cc16',
          hazard: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}

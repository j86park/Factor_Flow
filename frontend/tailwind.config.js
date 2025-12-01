/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          'dark-bg': '#0a0e14',
          'card-bg': '#131b26',
        }
      },
    },
    plugins: [],
  }
  
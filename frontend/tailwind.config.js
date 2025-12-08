/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        belBlue: "#1a4ca3",
        belBlueLight: "#3b82f6",
      },
    },
  },
  plugins: [],
};

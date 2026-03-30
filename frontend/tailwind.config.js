/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand:      { DEFAULT: "#1d4ed8", dark: "#1e3a8a", light: "#3b82f6" },
        ink:        { DEFAULT: "#111827", soft: "#4b5563" },
        panel:      { DEFAULT: "#ffffff", muted: "#f8fafc" },
        line:       "#d6dde7",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 32px rgba(15,23,42,.08)",
        lift: "0 8px 18px rgba(15,23,42,.12)",
      },
      borderRadius: {
        card: "14px",
      },
    },
  },
  plugins: [],
};

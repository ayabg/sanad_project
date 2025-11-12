/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'sanad-blue': '#87CEEB', // Sky Blue (Calm)
        'sanad-green': '#98FB98', // Pale Green (Therapeutic Accent)
        'sanad-bg': '#F8F8F8',   // Soft Off-White (Background)
        'sanad-crisis': '#FFC107', // Soft Orange (Alert)
      },
    },
  },
  plugins: [],
}

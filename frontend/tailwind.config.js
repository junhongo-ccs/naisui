/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // 背景色。"base" にすると fontSize.base と衝突し、text-base が文字色 #FAFAFA も付けてしまう。
        surface: "#FAFAFA",
        brand: {
          50: "#effcfa",
          100: "#d6f5f0",
          200: "#aeeae1",
          300: "#7adbcd",
          400: "#45c2b1",
          500: "#26a794",
          600: "#1c8778",
          700: "#1a6c62",
          800: "#19564f",
          900: "#194843",
        },
      },
      fontSize: {
        base: ["15px", "1.6"],
      },
    },
  },
  plugins: [],
}


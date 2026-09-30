/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // 背景色。"base" にすると fontSize.base と衝突し、text-base が文字色 #FAFAFA も付けてしまう。
        surface: "#FAFAFA",
        // 避難所の記号（#16a34a = 600）とヘッダー（700）にそろえた緑（Tailwindのgreenと同じ値）。
        // 白い文字を載せるのは700以上にする（600だとコントラスト比が約3.3:1でAAに届かない）。
        brand: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
        },
      },
      fontSize: {
        base: ["15px", "1.6"],
      },
      // 回答を待つ間の3つの丸（ChatPanel.jsx の TypingIndicator）。少し浮きながら濃くなる動きを、丸ごとにずらして波にする。
      keyframes: {
        typing: {
          "0%, 60%, 100%": { transform: "translateY(0)", opacity: "0.35" },
          "30%": { transform: "translateY(-4px)", opacity: "1" },
        },
      },
      animation: {
        typing: "typing 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
}


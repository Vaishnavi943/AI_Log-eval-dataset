export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14171c",
        paper: "#f7f7f5",
        accent: "#3b6e5e",
        warn: "#b5502e",
        line: "#dcded9",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
}

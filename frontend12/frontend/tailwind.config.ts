import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0d10",
        surface: "#14171c",
        surface2: "#1b1f26",
        border: "#262b33",
        accent: "#c1654a",
        accent2: "#e08a6d",
        text: "#e8e6e3",
        muted: "#9aa1ac",
        success: "#4caf7d",
        danger: "#e2574c",
        warning: "#d9a441",
      },
      borderRadius: {
        xl: "14px",
      },
    },
  },
  plugins: [],
};
export default config;

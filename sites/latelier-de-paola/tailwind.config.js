/** @type {import('tailwindcss').Config} */
// Mapping des tokens Steep (DESIGN.md du brief) — les valeurs vivent dans src/index.css (:root + .dark).
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        "background-alt": "hsl(var(--background-alt))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        subtle: "hsl(var(--subtle))",
        border: "hsl(var(--border))",
      },
      fontFamily: {
        heading: "var(--font-heading)",
        body: "var(--font-body)",
      },
      // Demi-graisses Söhne/Inter du DESIGN.md (430/450/480) — jamais de bold display.
      fontWeight: {
        "body-regular": "430",
        "body-medium": "450",
        "body-strong": "480",
      },
      fontSize: {
        // Display serif Steep : 44/64/90px, graisse 400, interligne 1.3.
        "display-md": ["44px", { lineHeight: "1.3", fontWeight: "400" }],
        "display-lg": ["64px", { lineHeight: "1.3", fontWeight: "400" }],
        "display-xl": ["90px", { lineHeight: "1.3", letterSpacing: "-0.025em", fontWeight: "400" }],
      },
      borderRadius: {
        image: "var(--radius-image)",
        input: "var(--radius-input)",
        elevated: "var(--radius-elevated)",
        card: "var(--radius-card)",
      },
      maxWidth: {
        canvas: "1200px",
      },
      spacing: {
        section: "80px",
      },
    },
  },
  plugins: [],
};

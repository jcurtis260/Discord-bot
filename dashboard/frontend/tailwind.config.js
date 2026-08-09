/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        discord: {
          blurple: '#5865F2',
          green: '#57F287',
          yellow: '#FEE75C',
          fuchsia: '#EB459E',
          red: '#ED4245',
          white: '#FFFFFF',
          black: '#000000',
          dark: {
            100: '#4E5058',
            200: '#3F4147',
            300: '#35373C',
            400: '#2B2D31',
            500: '#232428',
            600: '#1E1F22',
          },
        },
      },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        display: ["Manrope", "Inter", "ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      colors: {
        brand: {
          navy: '#0F3D64',
          green: '#1E9E6A',
          sky: '#0E86D4',
          sand: '#F5EFE6',
          blush: '#F2D4C7',
        },
        primary: {
          50: '#eef4fb',
          100: '#d6e3f5',
          200: '#adc8ec',
          300: '#84ade1',
          400: '#3f7dcd',
          500: '#215fa7',
          600: '#164a84',
          700: '#123c6b',
          800: '#0f3258',
          900: '#0b2340',
        },
        emerald: {
          50: '#e6f7f0',
          100: '#c0ecd9',
          200: '#8edebb',
          300: '#59ce9b',
          400: '#34be81',
          500: '#1ea96d',
          600: '#188b5a',
          700: '#136d48',
          800: '#0d4d34',
          900: '#083424',
        },
      },
      boxShadow: {
        soft: '0 20px 40px -24px rgba(15,61,100,0.35)',
        elevated: '0 30px 60px -30px rgba(15,61,100,0.45)',
        glow: '0 0 0 1px rgba(14,134,212,0.15), 0 20px 45px -25px rgba(30,158,106,0.35)',
      },
      borderRadius: {
        xl2: '1.25rem',
        xl3: '1.75rem',
      },
      transitionTimingFunction: {
        'gentle': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out both',
        float: 'float 4s ease-in-out infinite',
      },
      backgroundImage: {
        'mesh-gradient': 'radial-gradient(circle at 10% 10%, rgba(14,134,212,0.16), transparent 55%), radial-gradient(circle at 80% 0%, rgba(30,158,106,0.25), transparent 45%), radial-gradient(circle at 50% 90%, rgba(242,212,199,0.35), transparent 50%)',
        'grid-overlay': 'linear-gradient(90deg, rgba(15,61,100,0.08) 1px, transparent 1px), linear-gradient(0deg, rgba(15,61,100,0.08) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
}

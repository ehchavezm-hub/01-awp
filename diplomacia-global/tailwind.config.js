/** Configuración de Tailwind CSS (colores institucionales y fuente legible). */
module.exports = {
  content: ['./public/**/*.html', './public/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        marino: { DEFAULT: '#0b2545', claro: '#13315c', suave: '#e8eef7' },
        marfil: '#fdfbf5',
        tinta: '#1a1a1a',
        oro: '#8a5a00'
      },
      fontFamily: {
        sans: ['"Atkinson Hyperlegible"', 'Verdana', '"Segoe UI"', 'Arial', 'sans-serif']
      }
    }
  }
};

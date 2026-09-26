/**
 * Configuración de Tailwind CSS.
 * Colores tomados de la plantilla "dip_ppt" (paleta editorial tipo Financial Times).
 */
module.exports = {
  content: ['./public/**/*.html', './public/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        papel: { DEFAULT: '#FFF1E5', suave: '#F2E9DC', palido: '#E2D7CA' }, // FT Pink / Pink Light / Pink Pale
        clarete: '#990F3D',  // FT Claret: identidad, titulares
        pizarra: '#33302E',  // Slate Black: texto principal
        oxford: '#0F5499',   // Oxford Blue: enlaces y botón principal
        azafran: '#F2AF26',  // Saffron: destacados
        gris: '#66605A',     // Gray Dark FT: texto secundario
        verde: '#007A3D',    // FT Green (tono oscuro para cumplir contraste)
        purpura: '#593380'   // Purple Opinion: análisis
      },
      fontFamily: {
        sans: ['"Atkinson Hyperlegible"', 'Verdana', '"Segoe UI"', 'Arial', 'sans-serif'],
        titular: ['Georgia', '"Times New Roman"', 'serif']
      }
    }
  }
};

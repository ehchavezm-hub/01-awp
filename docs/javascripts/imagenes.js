// Las imágenes de los documentos apuntan a NotebookLM (lh3.googleusercontent.com)
// y pueden no cargar si el lector no tiene acceso. En ese caso se ocultan
// para no mostrar iconos de imagen rota.
(function () {
  function ocultar(img) {
    img.style.display = "none";
  }

  // Imágenes que fallan después de cargar este script.
  document.addEventListener(
    "error",
    function (evento) {
      if (evento.target && evento.target.tagName === "IMG") {
        ocultar(evento.target);
      }
    },
    true
  );

  // Imágenes que ya habían fallado antes de que este script se ejecutara.
  function revisar() {
    document.querySelectorAll(".md-typeset img").forEach(function (img) {
      if (img.complete && img.naturalWidth === 0) {
        ocultar(img);
      }
    });
  }
  revisar();
  window.addEventListener("load", revisar);
})();

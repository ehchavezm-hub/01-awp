from doc2md.verificar import comparar, palabras, texto_de_markdown


def test_identico_es_aprobado():
    r = comparar("p1", "Advanced Work Packaging (AWP)", "# Advanced Work Packaging (AWP)")
    assert r.total_referencia == 4
    assert not r.faltantes and not r.sobrantes
    assert r.aprobado(0.995)


def test_detecta_palabra_inventada_y_faltante():
    r = comparar("p1", "El plan de trabajo diario", "El plan de trabajo semanal")
    assert r.faltantes == {"diario": 1}
    assert r.sobrantes == {"semanal": 1}
    assert not r.aprobado(0.5)


def test_mayusculas_cuentan():
    r = comparar("p1", "CWP", "cwp")
    assert not r.aprobado(0.5)


def test_ignora_sintaxis_markdown():
    md = "| CWA | Construction Work Area |\n|---|---|\n![fig](img/a.png) [ver](http://x.org/y)\n<!-- página 1 -->"
    assert palabras(texto_de_markdown(md)) == ["CWA", "Construction", "Work", "Area", "ver"]


def test_ligaduras_y_guion_blando():
    r = comparar("p1", "ﬁeld inter­face", "field interface")
    assert r.aprobado(1.0)


def test_une_palabras_cortadas_por_guion():
    r = comparar("p1", "la infor-\nmación del proyecto", "la información del proyecto")
    assert r.aprobado(1.0)
    assert r.unidas_por_guion == [("infor", "mación")]


def test_encabezado_excluido_no_cuenta_como_faltante():
    ref = "Document ID: CII-2021\nTexto del cuerpo"
    r = comparar("p1", ref, "Texto del cuerpo", excluido="Document ID: CII-2021")
    assert r.aprobado(1.0)
    assert sum(r.excluidas.values()) == 4


def test_orden_distinto_no_falla_pero_se_informa():
    r = comparar("p1", "uno dos tres cuatro", "cuatro tres dos uno")
    assert r.aprobado(1.0)
    assert r.similitud_orden < 1.0


def test_pagina_ocr_nunca_se_aprueba_sola():
    r = comparar("p1", "", "texto reconocido")
    r.ocr = True
    assert not r.aprobado(0.0)


def test_texto_opcional_no_es_sobrante():
    r = comparar("c1", "Texto", "Texto\n\nFigura 1\n\n![Image](a.png)", opcional="Figura 1")
    assert r.aprobado(1.0)

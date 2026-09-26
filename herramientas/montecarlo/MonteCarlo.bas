Attribute VB_Name = "MonteCarlo"
Option Explicit

' ======================================================================
'  ANALISIS CUANTITATIVO DE RIESGOS - SIMULACION MONTECARLO (version 3)
'  Obras de construccion. Dimensiones de impacto configurables
'  (tblDimensiones): COSTO, PLAZO, ING_DISENO, ING_CAMPO y las que agregue
'  el usuario.
'
'  Macros publicas:
'    EjecutarSimulacion  - valida, simula y genera las hojas de salida
'    ValidarDatos        - valida tblRiesgos y marca las celdas con error
'    LimpiarResultados   - limpia las hojas de salida (no las elimina)
'    AgregarDimension    - agrega una dimension de impacto
'    ValidarParametros() - funcion Boolean usada por las anteriores
'
'  Hojas por CodeName: hjInicio, hjGuia, hjParametros, hjResultados,
'  hjCurvaS, hjTornado, hjRangos, hjMatriz, hjComparacion, hjSimulacion,
'  hjTeoria.
'
'  Codigo fuente 100% ASCII. Los textos con tildes se generan con
'  U("...\u00F3...") que convierte las secuencias \uXXXX con ChrW().
' ======================================================================

' ---------------- Limites ----------------
Private Const MAX_RIESGOS As Long = 200
Private Const MAX_DIMENSIONES As Long = 6
Private Const MIN_ITER As Long = 1000
Private Const MAX_ITER As Long = 100000
Private Const MAX_FILAS_SIM As Long = 5000
Private Const N_CLASES As Long = 20
Private Const COL_AUX_GRAFICOS As Long = 60   ' columna BH: datos auxiliares de las lineas de referencia
Private Const MAX_ERRORES_MSG As Long = 30
Private Const LIMITE_VALORES As Double = 20000000#
Private Const DOS_PI As Double = 6.28318530717959
Private Const PI_ As Double = 3.14159265358979
Private Const GAMMA_EULER As Double = 0.577215664901533

' ---------------- Generador MRG32k3a (L'Ecuyer) ----------------
Private Const MRG_M1 As Double = 4294967087#
Private Const MRG_M2 As Double = 4294944443#
Private Const MRG_A12 As Double = 1403580#
Private Const MRG_A13N As Double = 810728#
Private Const MRG_A21 As Double = 527612#
Private Const MRG_A23N As Double = 1370589#
Private Const MRG_NORMA As Double = 2.32830654929573E-10

' ---------------- Colores: paleta Bloomberg (Long = R + 256*G + 65536*B) ----------------
Private Const COLOR_TITULO_FONDO As Long = 0            ' #000000 banda de titulo de hoja
Private Const COLOR_TITULO_TEXTO As Long = 2662655      ' #FFA028 texto de la banda de titulo
Private Const COLOR_ENCABEZADO As Long = 0              ' #000000 fondo de encabezado de tabla
Private Const COLOR_ENCABEZADO_TEXTO As Long = 2662655  ' #FFA028 texto de encabezado de tabla
Private Const COLOR_BLANCO As Long = 16777215           ' #FFFFFF fondo de filas
Private Const COLOR_TEXTO As Long = 0                   ' #000000 texto de celdas
Private Const COLOR_SUBTITULO As Long = 3355443         ' #333333 subtitulos y notas
Private Const COLOR_FILA_ALTERNA As Long = 15464447     ' #FFF7EB fila alterna (tinte ambar)
Private Const COLOR_ENTRADA As Long = 14086399          ' #FFF0D6 celda de entrada (tinte ambar)
Private Const COLOR_SALIDA As Long = 15592941           ' #EDEDED celda de salida (tinte gris)
Private Const COLOR_P10 As Long = 12842570              ' #4AF6C3 resaltado P10
Private Const COLOR_P50 As Long = 2142463               ' #FFB020 resaltado P50
Private Const COLOR_P80 As Long = 2662655               ' #FFA028 resaltado P80 / nivel elegido
Private Const COLOR_P90 As Long = 2001915               ' #FB8B1E resaltado P90
Private Const COLOR_ERROR As Long = 4015103             ' #FF433D error de validacion
Private Const COLOR_ADVERTENCIA As Long = 2142463       ' #FFB020 advertencia de validacion
Private Const COLOR_OPORTUNIDAD As Long = 378880        ' #00C805 marca de oportunidad
Private Const COLOR_BORDE As Long = 3355443             ' #333333 bordes finos
Private Const COLOR_REF_P50 As Long = 3355443           ' #333333 linea de referencia P50
Private Const COLOR_REF_NIVEL As Long = 4015103         ' #FF433D linea de referencia del nivel
Private Const COLOR_TORNADO_BAJO As Long = 378880       ' #00C805 tornado 10% inferior
Private Const COLOR_TORNADO_ALTO As Long = 4015103      ' #FF433D tornado 10% superior
Private Const COLOR_MATRIZ_BAJO As Long = 378880        ' #00C805 matriz: puntaje bajo
Private Const COLOR_MATRIZ_MEDIO As Long = 2142463      ' #FFB020 matriz: puntaje medio
Private Const COLOR_MATRIZ_ALTO As Long = 4015103       ' #FF433D matriz: puntaje alto
Private Const COLOR_DESPUES As Long = 3355443           ' #333333 serie "despues" en COMPARACION
Private Const COLOR_SERIE_DEFECTO As Long = 26367       ' #FF6600 serie si la dimension no trae color

' ---------------- Codigos de distribucion ----------------
Private Const D_DESCONOCIDA As Long = -1
Private Const D_NINGUNA As Long = 0
Private Const D_CONSTANTE As Long = 1
Private Const D_UNIFORME As Long = 2
Private Const D_TRIANGULAR As Long = 3
Private Const D_TRIGEN As Long = 4
Private Const D_PERT As Long = 5
Private Const D_PERT_MOD As Long = 6
Private Const D_BETA As Long = 7
Private Const D_NORMAL As Long = 8
Private Const D_NORMAL_TRUNC As Long = 9
Private Const D_LOGNORMAL As Long = 10
Private Const D_GAMMA As Long = 11
Private Const D_EXPONENCIAL As Long = 12
Private Const D_WEIBULL As Long = 13
Private Const D_GUMBEL As Long = 14
Private Const D_LOGISTICA As Long = 15
Private Const D_PARETO As Long = 16
Private Const D_POISSON As Long = 17
Private Const D_BINOMIAL As Long = 18
Private Const D_DISC_UNIFORME As Long = 19
Private Const D_DISCRETA As Long = 20
Private Const N_DISTRIBUCIONES As Long = 20

' ---------------- Tipos ----------------
Private Type TRiesgo
    Id As String
    Nombre As String
    Tipo As String
    Signo As Double
    Estado As String
    Fila As Long
    Prob As Double
    ProbRes As Double
    FactorRes As Double
    CostoResp As Double
    TieneRespuesta As Boolean
    Grupo As String
    Rho As Double
End Type

Private Type TDimension
    Clave As String
    Nombre As String
    Unidad As String
    ValorBase As Double
    TieneBase As Boolean
    Formato As String
    ReservaGestion As Boolean
    ColorSerie As Long
End Type

Private Type TSens
    Idx As Long
    MediaR As Double
    Rho As Double
    Contrib As Double
    BajoMedia As Double
    AltoMedia As Double
    Swing As Double
End Type

' ---------------- Estado para mensajes de error ----------------
Private gEtapa As String
Private gRiesgoActual As Long
Private gDimActual As Long
Private gPasoGrafico As String
Private gNFallosGraf As Long
Private gPrimerFalloGraf As String
Private gSinGraficos As Boolean   ' solo para pruebas automaticas (False en uso normal)

' ---------------- Modelo leido ----------------
Private gNR As Long
Private gND As Long
Private gN As Long
Private gR() As TRiesgo
Private gD() As TDimension
Private gDist() As Long           ' (riesgo, dimension)
Private gPar() As Double          ' (riesgo, dimension, 1..4)
Private gDiscV() As Variant       ' (riesgo, dimension): valores de DISCRETA
Private gDiscF() As Variant       ' (riesgo, dimension): probabilidad acumulada de DISCRETA
Private gNivel As Double
Private gResGestPct As Double
Private gSemilla As Double
Private gSemillaFija As Boolean
Private gHayDespues As Boolean
Private gCostoRespTotal As Double
Private gDimCosto As Long
Private gNPend As Long
Private gNEstim As Long
Private gNEjemploAct As Long
Private gAdvert As String
Private gNAdv As Long

' ---------------- Resultados ----------------
Private gM() As Double            ' (iteracion, riesgo, dimension) antes de respuestas
Private gMD() As Double           ' (iteracion, riesgo, dimension) despues de respuestas
Private gTot() As Double          ' (iteracion, dimension)
Private gTotD() As Double         ' (iteracion, dimension)
Private gOcc() As Long            ' (riesgo) numero de ocurrencias
Private gOrdM() As Double         ' (iteracion, dimension): totales ordenados antes
Private gOrdDM() As Double        ' (iteracion, dimension): totales ordenados despues
Private gNG As Long
Private gGrupoNom() As String
Private gGrupoObj() As Double
Private gGrupoLog() As Double
Private gGrupoN() As Long
Private gCuerpoEsc As Range       ' tblEscalas (cuerpo) usado en la matriz
Private gEncEsc As Range          ' tblEscalas (encabezado)

' ---------------- Estado del generador ----------------
Private gS10 As Double
Private gS11 As Double
Private gS12 As Double
Private gS20 As Double
Private gS21 As Double
Private gS22 As Double


' ======================================================================
'  MACROS PUBLICAS
' ======================================================================

Public Sub EjecutarSimulacion()
    Dim t0 As Double, calcPrev As Long, msg As String, d As Long
    Dim s() As Double, valores As Double

    On Error GoTo EH
    gEtapa = "validando datos"
    gRiesgoActual = 0
    gDimActual = 0
    calcPrev = xlCalculationAutomatic

    If Not ValidarParametros(False) Then Exit Sub

    valores = CDbl(gN) * gNR * gND
    If gHayDespues Then valores = valores * 2
    If valores > LIMITE_VALORES Then
        If MsgBox(U("La simulaci\u00F3n guardar\u00E1 ") & Format$(valores, "#,##0") & _
                  U(" valores en memoria y puede ser lenta o agotar la memoria de Excel de 32 bits.") & vbLf & _
                  U("Sugerencia: reduzca el n\u00FAmero de iteraciones.") & vbLf & vbLf & U("\u00BFDesea continuar?"), _
                  vbQuestion + vbYesNo, Titulo()) = vbNo Then Exit Sub
    End If

    t0 = Timer
    calcPrev = Application.Calculation
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual

    gNFallosGraf = 0
    gPrimerFalloGraf = ""
    gEtapa = "simulando iteraciones"
    NucleoSimulacion

    gEtapa = "escribiendo la hoja RESULTADOS"
    Application.StatusBar = "Escribiendo resultados..."
    EscribirResultados
    gEtapa = "escribiendo la hoja CURVA_S"
    EscribirCurvaS
    gEtapa = "calculando la sensibilidad (TORNADO)"
    Application.StatusBar = "Calculando sensibilidad..."
    EscribirTornado
    gEtapa = "escribiendo la hoja RANGOS"
    EscribirRangos
    gEtapa = "escribiendo la hoja MATRIZ_PI"
    EscribirMatriz
    gEtapa = "escribiendo la hoja COMPARACION"
    EscribirComparacion
    gEtapa = "escribiendo la hoja SIMULACION"
    EscribirSimulacion

    Restaurar calcPrev
    hjResultados.Activate
    hjResultados.Range("A1").Select

    msg = U("Simulaci\u00F3n completada.") & vbLf & vbLf & _
          ChrW$(8226) & " Iteraciones: " & Format$(gN, "#,##0") & vbLf & _
          ChrW$(8226) & " Riesgos activos: " & gNR & "   (estimados por validar: " & gNEstim & _
          "; pendientes de cuantificar: " & gNPend & ")" & vbLf & _
          ChrW$(8226) & " Semilla: " & TextoSemilla() & vbLf & _
          ChrW$(8226) & " Tiempo: " & Format$(Timer - t0, "0.0") & " s" & vbLf
    If gNFallosGraf > 0 Then msg = msg & ChrW$(8226) & U(" Gr\u00E1ficos no creados: ") & gNFallosGraf & _
        " (" & gPrimerFalloGraf & U("). El aviso queda en cada hoja; los resultados num\u00E9ricos son v\u00E1lidos.") & vbLf
    If gNAdv > 0 Then msg = msg & ChrW$(8226) & " Advertencias: " & gNAdv & U(" (vea la hoja RESULTADOS)") & vbLf
    msg = msg & vbLf & "Nivel de confianza: " & Format$(gNivel, "0%") & vbLf
    For d = 1 To gND
        Ordenados d, False, s
        msg = msg & gD(d).Nombre & " (" & gD(d).Unidad & "):  P50 = " & Format$(Percentil(s, gN, 50), gD(d).Formato) & _
              "   P" & Format$(gNivel * 100, "0") & " = " & Format$(Percentil(s, gN, gNivel * 100), gD(d).Formato) & vbLf
    Next d
    MsgBox msg, vbInformation, Titulo()
    Exit Sub

EH:
    msg = "Error " & Err.Number & ": " & Err.Description & vbLf & vbLf & "Etapa: " & gEtapa
    If gRiesgoActual > 0 And gRiesgoActual <= gNR Then
        msg = msg & vbLf & "Riesgo: " & gR(gRiesgoActual).Id & " - " & Left$(gR(gRiesgoActual).Nombre, 80) & _
              " (fila " & gR(gRiesgoActual).Fila & " de la hoja PARAMETROS)"
    End If
    If gDimActual > 0 And gDimActual <= gND Then msg = msg & vbLf & U("Dimensi\u00F3n: ") & gD(gDimActual).Nombre
    Restaurar calcPrev
    MsgBox msg, vbCritical, Titulo()
End Sub

' Boton "VALIDAR DATOS"
Public Sub ValidarDatos()
    On Error GoTo EH
    ValidarParametros True
    Exit Sub
EH:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, Titulo()
End Sub

' Lee y valida la configuracion, las dimensiones, las escalas y los riesgos.
' Deja el modelo en memoria. Marca las celdas con error y muestra los mensajes.
Public Function ValidarParametros(Optional ByVal mostrarOk As Boolean = False) As Boolean
    Dim errs As String, nErr As Long, msg As String
    Dim loR As ListObject, loD As ListObject, loE As ListObject

    Set loR = Tabla(hjParametros, "tblRiesgos")
    Set loD = Tabla(hjParametros, "tblDimensiones")
    Set loE = Tabla(hjParametros, "tblEscalas")
    If LeerModeloDe(loR.DataBodyRange, loR.HeaderRowRange, loD.DataBodyRange, loD.HeaderRowRange, _
                    loE.DataBodyRange, loE.HeaderRowRange, True, errs, nErr) Then
        ValidarParametros = True
        If mostrarOk Then
            msg = U("Validaci\u00F3n correcta: ") & gNR & U(" riesgo(s) activo(s) y ") & gND & _
                  U(" dimensi\u00F3n(es) listos para simular.")
            If gNAdv > 0 Then msg = msg & vbLf & vbLf & "Advertencias (no impiden simular):" & vbLf & gAdvert
            MsgBox msg, vbInformation, Titulo()
        End If
    Else
        msg = "Se encontraron " & nErr & U(" error(es). Las celdas con problema quedaron marcadas en rojo:") & _
              vbLf & vbLf & errs
        If gNAdv > 0 Then msg = msg & vbLf & "Advertencias:" & vbLf & gAdvert
        MsgBox msg, vbExclamation, Titulo()
    End If
End Function

' Boton "LIMPIAR RESULTADOS"
Public Sub LimpiarResultados()
    Dim hojas As Variant, nombres As Variant, ws As Worksheet, k As Long
    Dim loR As ListObject
    On Error GoTo EH
    If MsgBox(U("Se limpiar\u00E1 el contenido de las hojas de resultados (RESULTADOS, CURVA_S, TORNADO, RANGOS, ") & _
              U("MATRIZ_PI, COMPARACION y SIMULACION) y los colores de validaci\u00F3n.") & vbLf & vbLf & _
              U("\u00BFDesea continuar?"), vbQuestion + vbYesNo, Titulo()) = vbNo Then Exit Sub
    Application.ScreenUpdating = False
    hojas = Array(hjResultados, hjCurvaS, hjTornado, hjRangos, hjMatriz, hjComparacion, hjSimulacion)
    nombres = Array("RESULTADOS", "CURVA S", "TORNADO", "RANGOS", U("MATRIZ PROBABILIDAD-IMPACTO"), _
                    U("COMPARACI\u00D3N ANTES / DESPU\u00C9S"), U("SIMULACI\u00D3N"))
    For k = 0 To 6
        Set ws = hojas(k)
        PrepararHoja ws
        PonerTitulo ws, nombres(k) & U(" \u2014 Presione \u25B6 CORRER SIMULACI\u00D3N en la hoja PARAMETROS"), "", 12
    Next k
    Set loR = Tabla(hjParametros, "tblRiesgos")
    RestablecerColoresEntrada loR.DataBodyRange, loR.HeaderRowRange
    Application.ScreenUpdating = True
    MsgBox U("Resultados limpiados. Listo para una nueva simulaci\u00F3n."), vbInformation, Titulo()
    Exit Sub
EH:
    Application.ScreenUpdating = True
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, Titulo()
End Sub

' Boton "AGREGAR DIMENSION": agrega una fila en tblDimensiones, las columnas
' DIST_<CLAVE>, <CLAVE>_P1..P4 y AYUDA_<CLAVE> en tblRiesgos y la columna
' IMP_<CLAVE> en tblEscalas. No requiere modificar el codigo.
Public Sub AgregarDimension()
    Dim loD As ListObject, loR As ListObject, loE As ListObject
    Dim clave As String, nombre As String, unidad As String, formato As String
    Dim col As ListColumn, k As Long, cD As Long, colores As Variant, filaLibre As Long
    Dim encD As Variant, nombresCol As Variant, posDesp As Long

    On Error GoTo EH
    Set loD = Tabla(hjParametros, "tblDimensiones")
    Set loR = Tabla(hjParametros, "tblRiesgos")
    Set loE = Tabla(hjParametros, "tblEscalas")
    clave = UCase$(Trim$(InputBox(U("Clave de la nueva dimensi\u00F3n (MAY\u00DASCULAS, sin espacios ni tildes; ") & _
                                  U("ej. CALIDAD, SSOMA, ING_DISENO2):"), Titulo())))
    If Len(clave) = 0 Then Exit Sub
    If Not ClaveValida(clave) Then
        MsgBox U("La clave solo puede tener letras A-Z, d\u00EDgitos y guion bajo, empezar con letra y tener ") & _
               U("como m\u00E1ximo 15 caracteres."), vbExclamation, Titulo()
        Exit Sub
    End If
    encD = loD.HeaderRowRange.Value
    cD = ColEnc(encD, "CLAVE")
    If loD.DataBodyRange Is Nothing Then Exit Sub
    If True Then
        For k = 1 To loD.ListRows.Count
            If UCase$(Txt(loD.DataBodyRange.Cells(k, cD).Value)) = clave Then
                MsgBox U("Ya existe una dimensi\u00F3n con la clave ") & clave & ".", vbExclamation, Titulo()
                Exit Sub
            End If
        Next k
    End If
    nombre = Trim$(InputBox(U("Nombre de la dimensi\u00F3n (ej. Calidad - no conformidades):"), Titulo(), clave))
    If Len(nombre) = 0 Then nombre = clave
    unidad = Trim$(InputBox(U("Unidad de medida (ej. HH, NCR, d\u00EDas, S/):"), Titulo(), "HH"))
    formato = Trim$(InputBox(U("Formato num\u00E9rico (c\u00F3digo ingl\u00E9s de Excel, ej. #,##0 o #,##0.0):"), Titulo(), "#,##0"))
    If Len(formato) = 0 Then formato = "#,##0"

    ' Fila libre (CLAVE vacia) en tblDimensiones: la tabla trae filas reservadas
    filaLibre = 0
    For k = 1 To loD.ListRows.Count
        If Len(Txt(loD.DataBodyRange.Cells(k, cD).Value)) = 0 Then
            filaLibre = k
            Exit For
        End If
    Next k
    If filaLibre = 0 Then
        MsgBox U("No quedan filas libres en tblDimensiones (m\u00E1ximo ") & MAX_DIMENSIONES & U(" dimensiones)."), vbExclamation, Titulo()
        Exit Sub
    End If

    Application.ScreenUpdating = False
    colores = Array("#FF6600", "#0068FF", "#CC7A00", "#2A2A2A", "#FF6600", "#0068FF")
    With loD.DataBodyRange
        .Cells(filaLibre, ColEnc(encD, "CLAVE")).Value = clave
        .Cells(filaLibre, ColEnc(encD, "NOMBRE")).Value = nombre
        .Cells(filaLibre, ColEnc(encD, "UNIDAD")).Value = unidad
        .Cells(filaLibre, ColEnc(encD, "FORMATO")).Value = formato
        .Cells(filaLibre, ColEnc(encD, "ACTIVA")).Value = "SI"
        .Cells(filaLibre, ColEnc(encD, "RESERVA_GESTION")).Value = "NO"
        .Cells(filaLibre, ColEnc(encD, "COLOR")).Value = colores(filaLibre - 1)
    End With

    ' Columnas nuevas en tblRiesgos, antes de NOTAS
    posDesp = ColEnc(loR.HeaderRowRange.Value, "NOTAS")
    If posDesp = 0 Then posDesp = loR.ListColumns.Count + 1
    nombresCol = Array("DIST_" & clave, clave & "_P1", clave & "_P2", clave & "_P3", clave & "_P4", "AYUDA_" & clave)
    For k = 0 To 5
        Set col = loR.ListColumns.Add(posDesp + k)
        col.Name = nombresCol(k)
        If Not col.DataBodyRange Is Nothing Then
            If k = 5 Then
                col.DataBodyRange.Formula = "=IFERROR(INDEX(tblDistribuciones[AYUDA],MATCH([@[DIST_" & clave & _
                                            "]],tblDistribuciones[DISTRIBUCION],0)),"""")"
                col.DataBodyRange.Interior.Color = COLOR_SALIDA
            Else
                col.DataBodyRange.Interior.Color = COLOR_ENTRADA
                If k = 0 Then
                    col.DataBodyRange.Validation.Delete
                    col.DataBodyRange.Validation.Add Type:=3, AlertStyle:=1, Operator:=1, Formula1:="=ListaDistribuciones"
                    col.DataBodyRange.Validation.InputTitle = U("Distribuci\u00F3n")
                    col.DataBodyRange.Validation.InputMessage = U("Elija la distribuci\u00F3n (vac\u00EDo = no afecta). Vea la hoja GUIA.")
                End If
            End If
        End If
    Next k
    ' Umbral de impacto en tblEscalas
    Set col = loE.ListColumns.Add
    col.Name = "IMP_" & clave
    If Not col.DataBodyRange Is Nothing Then
        col.DataBodyRange.Interior.Color = COLOR_ENTRADA
        For k = 1 To col.DataBodyRange.Rows.Count - 1
            col.DataBodyRange.Cells(k, 1).Value = 3 ^ (k - 1)
        Next k
    End If
    Application.ScreenUpdating = True
    MsgBox U("Dimensi\u00F3n ") & clave & U(" agregada.") & vbLf & vbLf & _
           U("Complete DIST_") & clave & U(" y sus par\u00E1metros en tblRiesgos y ajuste los umbrales IMP_") & clave & _
           U(" en tblEscalas (se cargaron 1, 3, 9, 27 como referencia)."), vbInformation, Titulo()
    Exit Sub
EH:
    Application.ScreenUpdating = True
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, Titulo()
End Sub


' ======================================================================
'  LECTURA Y VALIDACION
' ======================================================================

Private Function Tabla(ByVal ws As Worksheet, ByVal nombre As String) As ListObject
    On Error Resume Next
    Set Tabla = ws.ListObjects(nombre)
    On Error GoTo 0
    If Tabla Is Nothing Then
        Err.Raise 513, "MonteCarlo", "No se encuentra la tabla '" & nombre & "' en la hoja " & ws.Name & "."
    End If
End Function

' Indice de columna por el texto del encabezado (0 si no existe).
Private Function ColEnc(ByVal enc As Variant, ByVal nombre As String) As Long
    Dim k As Long
    nombre = UCase$(Trim$(nombre))
    For k = LBound(enc, 2) To UBound(enc, 2)
        If UCase$(Trim$(Txt(enc(LBound(enc, 1), k)))) = nombre Then
            ColEnc = k - LBound(enc, 2) + 1
            Exit Function
        End If
    Next k
End Function

Private Function ClaveValida(ByVal clave As String) As Boolean
    Dim k As Long, ch As String
    If Len(clave) = 0 Or Len(clave) > 15 Then Exit Function
    For k = 1 To Len(clave)
        ch = Mid$(clave, k, 1)
        If k = 1 Then
            If ch < "A" Or ch > "Z" Then Exit Function
        ElseIf Not ((ch >= "A" And ch <= "Z") Or (ch >= "0" And ch <= "9") Or ch = "_") Then
            Exit Function
        End If
    Next k
    ClaveValida = True
End Function

' Restablece el color de entrada del cuerpo de tblRiesgos (columnas AYUDA_* en gris).
Private Sub RestablecerColoresEntrada(ByVal cuerpo As Range, ByVal enc As Range)
    Dim k As Long, v As Variant
    If cuerpo Is Nothing Then Exit Sub
    cuerpo.Interior.Color = COLOR_ENTRADA
    v = enc.Value
    For k = 1 To enc.Columns.Count
        If Left$(UCase$(Txt(v(1, k))), 6) = "AYUDA_" Then cuerpo.Columns(k).Interior.Color = COLOR_SALIDA
    Next k
End Sub

' Lee todo el modelo desde rangos (cuerpo y encabezado de cada tabla).
Private Function LeerModeloDe(ByVal cuerpoR As Range, ByVal encR As Range, ByVal cuerpoD As Range, _
                              ByVal encD As Range, ByVal cuerpoE As Range, ByVal encE As Range, _
                              ByVal marcar As Boolean, ByRef errs As String, ByRef nErr As Long) As Boolean
    Dim v As Variant, datosD As Variant, eD As Variant, datosR As Variant, eR As Variant
    Dim i As Long, d As Long, k As Long, antes As Long, fila As Long
    Dim cClave As Long, cNombre As Long, cUnidad As Long, cBase As Long, cFormato As Long
    Dim cActiva As Long, cResGest As Long, cColor As Long
    Dim colDist() As Long, colP() As Long
    Dim cId As Long, cNom As Long, cTipo As Long, cEstado As Long, cActivo As Long, cProb As Long
    Dim cGrupo As Long, cRho As Long, cProbRes As Long, cFactor As Long, cCosto As Long
    Dim nombre As String, activo As String, estado As String, pref As String, tipo As String
    Dim cod As Long, algunaDist As Boolean, p(1 To 4) As Double, crudo(1 To 4) As Variant
    Dim clave As String

    errs = ""
    nErr = 0
    gAdvert = ""
    gNAdv = 0
    gNR = 0
    gND = 0
    gNPend = 0
    gNEstim = 0
    gNEjemploAct = 0
    gHayDespues = False
    gCostoRespTotal = 0
    gDimCosto = 0

    If marcar Then
        RestablecerColoresEntrada cuerpoR, encR
        On Error Resume Next
        hjParametros.Range("CostoBase").Interior.Color = COLOR_ENTRADA
        hjParametros.Range("PlazoBase").Interior.Color = COLOR_ENTRADA
        hjParametros.Range("Iteraciones").Interior.Color = COLOR_ENTRADA
        hjParametros.Range("Semilla").Interior.Color = COLOR_ENTRADA
        hjParametros.Range("NivelConfianza").Interior.Color = COLOR_ENTRADA
        hjParametros.Range("ReservaGestionPct").Interior.Color = COLOR_ENTRADA
        On Error GoTo 0
    End If

    ' --- Configuracion ---
    v = hjParametros.Range("Iteraciones").Value
    If Not EsNum(v) Then
        AgregarError errs, nErr, U("N\u00FAmero de iteraciones: debe ser un entero entre 1,000 y 100,000.")
        MarcarCelda hjParametros.Range("Iteraciones"), marcar, COLOR_ERROR
    ElseIf CDbl(v) < MIN_ITER Or CDbl(v) > MAX_ITER Or CDbl(v) <> Int(CDbl(v)) Then
        AgregarError errs, nErr, U("N\u00FAmero de iteraciones: debe ser un entero entre 1,000 y 100,000.")
        MarcarCelda hjParametros.Range("Iteraciones"), marcar, COLOR_ERROR
    Else
        gN = CLng(v)
    End If
    v = hjParametros.Range("Semilla").Value
    gSemillaFija = False
    If Len(Txt(v)) > 0 Then
        If EsNum(v) Then
            gSemillaFija = True
            gSemilla = Abs(Int(CDbl(v)))
        Else
            AgregarError errs, nErr, U("Semilla aleatoria: d\u00E9jela vac\u00EDa o ingrese un n\u00FAmero entero.")
            MarcarCelda hjParametros.Range("Semilla"), marcar, COLOR_ERROR
        End If
    End If
    v = hjParametros.Range("NivelConfianza").Value
    If Not EsNum(v) Then
        AgregarError errs, nErr, "Nivel de confianza: ingrese un valor entre 0.50 y 0.95 (50% a 95%)."
        MarcarCelda hjParametros.Range("NivelConfianza"), marcar, COLOR_ERROR
    ElseIf CDbl(v) < 0.5 Or CDbl(v) > 0.95 Then
        AgregarError errs, nErr, "Nivel de confianza: ingrese un valor entre 0.50 y 0.95 (50% a 95%)."
        MarcarCelda hjParametros.Range("NivelConfianza"), marcar, COLOR_ERROR
    Else
        gNivel = CDbl(v)
    End If
    v = hjParametros.Range("ReservaGestionPct").Value
    gResGestPct = 0
    If Len(Txt(v)) > 0 Then
        If Not EsNum(v) Then
            AgregarError errs, nErr, U("Reserva de gesti\u00F3n (%): ingrese un porcentaje entre 0% y 100%.")
            MarcarCelda hjParametros.Range("ReservaGestionPct"), marcar, COLOR_ERROR
        ElseIf CDbl(v) < 0 Or CDbl(v) > 1 Then
            AgregarError errs, nErr, U("Reserva de gesti\u00F3n (%): ingrese un porcentaje entre 0% y 100%.")
            MarcarCelda hjParametros.Range("ReservaGestionPct"), marcar, COLOR_ERROR
        Else
            gResGestPct = CDbl(v)
        End If
    End If
    ValidarBaseOpcional "CostoBase", "Costo base", marcar, errs, nErr
    ValidarBaseOpcional "PlazoBase", "Plazo base", marcar, errs, nErr

    ' --- Dimensiones ---
    If cuerpoD Is Nothing Then
        AgregarError errs, nErr, U("La tabla tblDimensiones no tiene filas: agregue al menos una dimensi\u00F3n.")
        LeerModeloDe = False
        Exit Function
    End If
    eD = encD.Value
    datosD = cuerpoD.Value
    cClave = ColEnc(eD, "CLAVE")
    cNombre = ColEnc(eD, "NOMBRE")
    cUnidad = ColEnc(eD, "UNIDAD")
    cBase = ColEnc(eD, "BASE")
    cFormato = ColEnc(eD, "FORMATO")
    cActiva = ColEnc(eD, "ACTIVA")
    cResGest = ColEnc(eD, "RESERVA_GESTION")
    cColor = ColEnc(eD, "COLOR")
    If cClave = 0 Or cNombre = 0 Or cUnidad = 0 Or cActiva = 0 Then
        AgregarError errs, nErr, U("tblDimensiones debe tener las columnas CLAVE, NOMBRE, UNIDAD y ACTIVA.")
        LeerModeloDe = False
        Exit Function
    End If
    ReDim gD(1 To MAX_DIMENSIONES)
    ReDim colDist(1 To MAX_DIMENSIONES)
    ReDim colP(1 To MAX_DIMENSIONES, 1 To 4)
    eR = encR.Value
    For i = 1 To UBound(datosD, 1)
        clave = UCase$(Txt(datosD(i, cClave)))
        If Len(clave) > 0 And UCase$(Txt(datosD(i, cActiva))) <> "NO" Then
            If Not ClaveValida(clave) Then
                AgregarError errs, nErr, U("tblDimensiones, fila ") & i & ": la clave '" & clave & U("' no es v\u00E1lida.")
                MarcarCelda cuerpoD.Cells(i, cClave), marcar, COLOR_ERROR
            ElseIf gND >= MAX_DIMENSIONES Then
                AgregarError errs, nErr, U("Se admite un m\u00E1ximo de ") & MAX_DIMENSIONES & U(" dimensiones activas.")
            Else
                For k = 1 To gND
                    If gD(k).Clave = clave Then
                        AgregarError errs, nErr, U("tblDimensiones: la clave ") & clave & U(" est\u00E1 repetida.")
                        MarcarCelda cuerpoD.Cells(i, cClave), marcar, COLOR_ERROR
                        GoTo SiguienteDim
                    End If
                Next k
                gND = gND + 1
                With gD(gND)
                    .Clave = clave
                    .Nombre = Txt(datosD(i, cNombre))
                    If Len(.Nombre) = 0 Then .Nombre = clave
                    .Unidad = Txt(datosD(i, cUnidad))
                    .TieneBase = False
                    .ValorBase = 0
                    If cBase > 0 Then
                        If EsNum(datosD(i, cBase)) Then
                            .ValorBase = CDbl(datosD(i, cBase))
                            .TieneBase = (.ValorBase > 0)
                        End If
                    End If
                    .Formato = "#,##0"
                    If cFormato > 0 Then
                        If Len(Txt(datosD(i, cFormato))) > 0 Then .Formato = Txt(datosD(i, cFormato))
                    End If
                    .ReservaGestion = False
                    If cResGest > 0 Then .ReservaGestion = (UCase$(Txt(datosD(i, cResGest))) = "SI")
                    .ColorSerie = COLOR_SERIE_DEFECTO
                    If cColor > 0 Then .ColorSerie = ColorHex(Txt(datosD(i, cColor)), COLOR_SERIE_DEFECTO)
                End With
                If clave = "COSTO" Then gDimCosto = gND
                colDist(gND) = ColEnc(eR, "DIST_" & clave)
                For k = 1 To 4
                    colP(gND, k) = ColEnc(eR, clave & "_P" & k)
                Next k
                If colDist(gND) = 0 Or colP(gND, 1) = 0 Or colP(gND, 2) = 0 Or colP(gND, 3) = 0 Or colP(gND, 4) = 0 Then
                    AgregarError errs, nErr, U("tblRiesgos no tiene las columnas de la dimensi\u00F3n ") & clave & _
                        " (DIST_" & clave & ", " & clave & "_P1 ... " & clave & U("_P4). Use el bot\u00F3n AGREGAR DIMENSI\u00D3N.")
                    If gDimCosto = gND Then gDimCosto = 0
                    gND = gND - 1
                End If
            End If
        End If
SiguienteDim:
    Next i
    If gND = 0 Then
        AgregarError errs, nErr, U("No hay dimensiones activas v\u00E1lidas en tblDimensiones.")
        LeerModeloDe = False
        Exit Function
    End If

    ' --- Riesgos ---
    cId = ColEnc(eR, "ID")
    cNom = ColEnc(eR, "NOMBRE DEL RIESGO")
    cTipo = ColEnc(eR, "TIPO")
    cEstado = ColEnc(eR, "ESTADO")
    cActivo = ColEnc(eR, "ACTIVO")
    cProb = ColEnc(eR, "PROBABILIDAD")
    cGrupo = ColEnc(eR, "GRUPO_CORRELACION")
    cRho = ColEnc(eR, "RHO_GRUPO")
    cProbRes = ColEnc(eR, "PROB_RESIDUAL")
    cFactor = ColEnc(eR, "FACTOR_IMPACTO_RESIDUAL")
    cCosto = ColEnc(eR, "COSTO_RESPUESTA")
    If cNom = 0 Or cActivo = 0 Or cProb = 0 Then
        AgregarError errs, nErr, U("tblRiesgos debe tener las columnas NOMBRE DEL RIESGO, ACTIVO y PROBABILIDAD.")
        LeerModeloDe = False
        Exit Function
    End If
    If cuerpoR Is Nothing Then
        AgregarError errs, nErr, "La tabla tblRiesgos no tiene filas."
        LeerModeloDe = False
        Exit Function
    End If

    ReDim gR(1 To MAX_RIESGOS)
    ReDim gDist(1 To MAX_RIESGOS, 1 To gND)
    ReDim gPar(1 To MAX_RIESGOS, 1 To gND, 1 To 4)
    ReDim gDiscV(1 To MAX_RIESGOS, 1 To gND)
    ReDim gDiscF(1 To MAX_RIESGOS, 1 To gND)
    datosR = cuerpoR.Value

    For i = 1 To UBound(datosR, 1)
        fila = cuerpoR.Row + i - 1
        nombre = Txt(datosR(i, cNom))
        estado = ""
        If cEstado > 0 Then estado = UCase$(Txt(datosR(i, cEstado)))
        activo = UCase$(Txt(datosR(i, cActivo)))
        If InStr(1, estado, "PENDIENTE") > 0 Then gNPend = gNPend + 1
        If Len(nombre) = 0 And Len(Txt(datosR(i, cProb))) = 0 Then GoTo SiguienteRiesgo
        If activo = "NO" Then GoTo SiguienteRiesgo

        antes = nErr
        pref = "Fila " & fila
        If cId > 0 Then
            If Len(Txt(datosR(i, cId))) > 0 Then pref = pref & " (" & Txt(datosR(i, cId)) & ")"
        End If
        pref = pref & ": "
        If Len(nombre) = 0 Then
            AgregarError errs, nErr, pref & "falta el nombre del riesgo."
            MarcarCelda cuerpoR.Cells(i, cNom), marcar, COLOR_ERROR
        End If
        If Len(activo) > 0 And activo <> "SI" And activo <> "S" & ChrW$(205) Then
            AgregarError errs, nErr, pref & "ACTIVO debe ser SI o NO."
            MarcarCelda cuerpoR.Cells(i, cActivo), marcar, COLOR_ERROR
        End If
        tipo = "AMENAZA"
        If cTipo > 0 Then
            If Len(Txt(datosR(i, cTipo))) > 0 Then tipo = UCase$(Txt(datosR(i, cTipo)))
            If tipo <> "AMENAZA" And tipo <> "OPORTUNIDAD" Then
                AgregarError errs, nErr, pref & "TIPO debe ser AMENAZA u OPORTUNIDAD."
                MarcarCelda cuerpoR.Cells(i, cTipo), marcar, COLOR_ERROR
            End If
        End If

        If gNR >= MAX_RIESGOS Then
            AgregarError errs, nErr, pref & U("se admite un m\u00E1ximo de ") & MAX_RIESGOS & " riesgos activos."
            GoTo SiguienteRiesgo
        End If
        k = gNR + 1
        With gR(k)
            .Id = ""
            If cId > 0 Then .Id = Txt(datosR(i, cId))
            If Len(.Id) = 0 Then .Id = "F" & fila
            .Nombre = nombre
            .Tipo = tipo
            If tipo = "OPORTUNIDAD" Then .Signo = -1# Else .Signo = 1#
            .Estado = estado
            .Fila = fila
            .Prob = 1#
            .ProbRes = -1#
            .FactorRes = 1#
            .CostoResp = 0#
            .TieneRespuesta = False
            .Grupo = ""
            .Rho = 0#
        End With

        ' Probabilidad
        v = datosR(i, cProb)
        If Len(Txt(v)) = 0 Then
            gR(k).Prob = 1#
        ElseIf Not EsNum(v) Then
            AgregarError errs, nErr, pref & U("PROBABILIDAD debe ser un n\u00FAmero entre 0 y 1.")
            MarcarCelda cuerpoR.Cells(i, cProb), marcar, COLOR_ERROR
        ElseIf CDbl(v) < 0 Or CDbl(v) > 1 Then
            AgregarError errs, nErr, pref & "PROBABILIDAD debe estar entre 0 y 1 (ej. 0.35 = 35%)."
            MarcarCelda cuerpoR.Cells(i, cProb), marcar, COLOR_ERROR
        Else
            gR(k).Prob = CDbl(v)
            If gR(k).Prob > 0.5 Then
                AgregarAdvertencia pref & "probabilidad " & Format$(gR(k).Prob, "0%") & _
                    U(" > 50%: considere incluirlo en la l\u00EDnea base y modelar como oportunidad que no ocurra (Vose).")
                MarcarCelda cuerpoR.Cells(i, cProb), marcar, COLOR_ADVERTENCIA
            End If
        End If

        ' Distribuciones por dimension
        algunaDist = False
        For d = 1 To gND
            gDist(k, d) = D_NINGUNA
            cod = DistCodigo(Txt(datosR(i, colDist(d))))
            If cod = D_DESCONOCIDA Then
                AgregarError errs, nErr, pref & "DIST_" & gD(d).Clave & " '" & Txt(datosR(i, colDist(d))) & U("' no reconocida.")
                MarcarCelda cuerpoR.Cells(i, colDist(d)), marcar, COLOR_ERROR
            ElseIf cod > 0 Then
                algunaDist = True
                crudo(1) = datosR(i, colP(d, 1))
                crudo(2) = datosR(i, colP(d, 2))
                crudo(3) = datosR(i, colP(d, 3))
                crudo(4) = datosR(i, colP(d, 4))
                If ValidarDistribucion(cod, crudo, pref & gD(d).Clave & " - " & DistNombre(cod) & ": ", _
                                       errs, nErr, p, k, d, cuerpoR, i, colP, d, marcar) Then
                    gDist(k, d) = cod
                    gPar(k, d, 1) = p(1)
                    gPar(k, d, 2) = p(2)
                    gPar(k, d, 3) = p(3)
                    gPar(k, d, 4) = p(4)
                End If
            End If
        Next d
        If Not algunaDist Then
            AgregarError errs, nErr, pref & U("indique al menos una distribuci\u00F3n de impacto (DIST_<DIMENSI\u00D3N>).")
            For d = 1 To gND
                MarcarCelda cuerpoR.Cells(i, colDist(d)), marcar, COLOR_ERROR
            Next d
        End If

        ' Correlacion
        If cGrupo > 0 Then gR(k).Grupo = UCase$(Txt(datosR(i, cGrupo)))
        If Len(gR(k).Grupo) > 0 Then
            v = Empty
            If cRho > 0 Then v = datosR(i, cRho)
            If Not EsNum(v) Then
                AgregarError errs, nErr, pref & U("RHO_GRUPO debe ser un n\u00FAmero entre 0 y 0.95 cuando hay GRUPO_CORRELACION.")
                If cRho > 0 Then MarcarCelda cuerpoR.Cells(i, cRho), marcar, COLOR_ERROR
            ElseIf CDbl(v) < 0 Or CDbl(v) > 0.95 Then
                AgregarError errs, nErr, pref & "RHO_GRUPO debe estar entre 0 y 0.95."
                MarcarCelda cuerpoR.Cells(i, cRho), marcar, COLOR_ERROR
            Else
                gR(k).Rho = CDbl(v)
            End If
        End If

        ' Respuesta (escenario despues)
        If cProbRes > 0 Then
            v = datosR(i, cProbRes)
            If Len(Txt(v)) > 0 Then
                If Not EsNum(v) Then
                    AgregarError errs, nErr, pref & "PROB_RESIDUAL debe estar entre 0 y 1."
                    MarcarCelda cuerpoR.Cells(i, cProbRes), marcar, COLOR_ERROR
                ElseIf CDbl(v) < 0 Or CDbl(v) > 1 Then
                    AgregarError errs, nErr, pref & "PROB_RESIDUAL debe estar entre 0 y 1."
                    MarcarCelda cuerpoR.Cells(i, cProbRes), marcar, COLOR_ERROR
                Else
                    gR(k).ProbRes = CDbl(v)
                    gR(k).TieneRespuesta = True
                End If
            End If
        End If
        If cFactor > 0 Then
            v = datosR(i, cFactor)
            If Len(Txt(v)) > 0 Then
                If Not EsNum(v) Then
                    AgregarError errs, nErr, pref & "FACTOR_IMPACTO_RESIDUAL debe estar entre 0 y 1."
                    MarcarCelda cuerpoR.Cells(i, cFactor), marcar, COLOR_ERROR
                ElseIf CDbl(v) < 0 Or CDbl(v) > 1 Then
                    AgregarError errs, nErr, pref & "FACTOR_IMPACTO_RESIDUAL debe estar entre 0 y 1."
                    MarcarCelda cuerpoR.Cells(i, cFactor), marcar, COLOR_ERROR
                Else
                    gR(k).FactorRes = CDbl(v)
                    gR(k).TieneRespuesta = True
                End If
            End If
        End If
        If cCosto > 0 Then
            v = datosR(i, cCosto)
            If Len(Txt(v)) > 0 Then
                If Not EsNum(v) Then
                    AgregarError errs, nErr, pref & U("COSTO_RESPUESTA debe ser un n\u00FAmero mayor o igual a 0.")
                    MarcarCelda cuerpoR.Cells(i, cCosto), marcar, COLOR_ERROR
                ElseIf CDbl(v) < 0 Then
                    AgregarError errs, nErr, pref & U("COSTO_RESPUESTA debe ser un n\u00FAmero mayor o igual a 0.")
                    MarcarCelda cuerpoR.Cells(i, cCosto), marcar, COLOR_ERROR
                Else
                    gR(k).CostoResp = CDbl(v)
                    If gR(k).CostoResp > 0 Then gR(k).TieneRespuesta = True
                End If
            End If
        End If

        If nErr = antes Then
            gNR = k
            If gR(k).ProbRes < 0 Then gR(k).ProbRes = gR(k).Prob
            If gR(k).TieneRespuesta Then gHayDespues = True
            gCostoRespTotal = gCostoRespTotal + gR(k).CostoResp
            If InStr(1, estado, "ESTIMADO") > 0 Then gNEstim = gNEstim + 1
            If InStr(1, estado, "EJEMPLO") > 0 Then gNEjemploAct = gNEjemploAct + 1
        End If
SiguienteRiesgo:
    Next i

    If gNR = 0 And nErr = 0 Then
        AgregarError errs, nErr, U("No hay riesgos activos: marque ACTIVO = SI en al menos un riesgo cuantificado.")
    End If
    If gCostoRespTotal > 0 And gDimCosto = 0 Then
        AgregarAdvertencia U("Hay COSTO_RESPUESTA pero no existe la dimensi\u00F3n COSTO activa: el costo de respuesta no se sumar\u00E1.")
    End If
    If gNEstim > 0 Then AgregarAdvertencia gNEstim & U(" riesgo(s) activo(s) con ESTADO = ESTIMADO - VALIDAR: ") & _
        U("son estimaciones preliminares; val\u00EDdelas con el due\u00F1o de cada riesgo.")
    If gNPend > 0 Then AgregarAdvertencia gNPend & U(" riesgo(s) PENDIENTES DE CUANTIFICAR (no se simulan).")
    If gNEjemploAct > 0 Then AgregarAdvertencia gNEjemploAct & U(" riesgo(s) EJEMPLO est\u00E1n activos: desact\u00EDvelos al cargar datos reales.")
    If gNR > 0 Then ValidarGrupos
    Set gCuerpoEsc = cuerpoE
    Set gEncEsc = encE
    If Not cuerpoE Is Nothing Then ValidarEscalas cuerpoE, encE, marcar, errs, nErr

    LeerModeloDe = (nErr = 0)
End Function

Private Sub ValidarBaseOpcional(ByVal nombreRango As String, ByVal etiqueta As String, ByVal marcar As Boolean, _
                                ByRef errs As String, ByRef nErr As Long)
    Dim v As Variant
    v = hjParametros.Range(nombreRango).Value
    If Len(Txt(v)) = 0 Then Exit Sub
    If Not EsNum(v) Then
        AgregarError errs, nErr, etiqueta & U(": d\u00E9jelo vac\u00EDo o ingrese un n\u00FAmero mayor o igual a 0.")
        MarcarCelda hjParametros.Range(nombreRango), marcar, COLOR_ERROR
    ElseIf CDbl(v) < 0 Then
        AgregarError errs, nErr, etiqueta & U(": d\u00E9jelo vac\u00EDo o ingrese un n\u00FAmero mayor o igual a 0.")
        MarcarCelda hjParametros.Range(nombreRango), marcar, COLOR_ERROR
    End If
End Sub

' Todos los riesgos de un grupo deben tener el mismo RHO_GRUPO (se usa el del primero).
Private Sub ValidarGrupos()
    Dim r As Long, q As Long
    For r = 1 To gNR
        If Len(gR(r).Grupo) > 0 Then
            For q = 1 To r - 1
                If gR(q).Grupo = gR(r).Grupo Then
                    If Abs(gR(q).Rho - gR(r).Rho) > 0.000001 Then
                        AgregarAdvertencia "Grupo " & gR(r).Grupo & ": RHO_GRUPO distinto en " & gR(r).Id & _
                            " (se usa " & Format$(gR(q).Rho, "0.00") & ", el del primer riesgo del grupo)."
                    End If
                    Exit For
                End If
            Next q
        End If
    Next r
End Sub

Private Sub ValidarEscalas(ByVal cuerpoE As Range, ByVal encE As Range, ByVal marcar As Boolean, _
                           ByRef errs As String, ByRef nErr As Long)
    Dim e As Variant, datos As Variant, c As Long, d As Long, i As Long, previo As Double
    e = encE.Value
    datos = cuerpoE.Value
    c = ColEnc(e, "PROB_MAX")
    If c = 0 Then
        AgregarAdvertencia U("tblEscalas no tiene la columna PROB_MAX: no se generar\u00E1 la matriz probabilidad-impacto.")
        Exit Sub
    End If
    previo = -1
    For i = 1 To UBound(datos, 1)
        If EsNum(datos(i, c)) Then
            If CDbl(datos(i, c)) <= previo Then
                AgregarError errs, nErr, U("tblEscalas: PROB_MAX debe ser creciente (nivel ") & i & ")."
                MarcarCelda cuerpoE.Cells(i, c), marcar, COLOR_ERROR
            End If
            previo = CDbl(datos(i, c))
        End If
    Next i
    For d = 1 To gND
        c = ColEnc(e, "IMP_" & gD(d).Clave)
        If c = 0 Then
            AgregarAdvertencia "tblEscalas no tiene la columna IMP_" & gD(d).Clave & U(": esa dimensi\u00F3n no se clasifica en la matriz.")
        Else
            previo = -1
            For i = 1 To UBound(datos, 1)
                If EsNum(datos(i, c)) Then
                    If CDbl(datos(i, c)) <= previo Then
                        AgregarError errs, nErr, "tblEscalas: IMP_" & gD(d).Clave & " debe ser creciente (nivel " & i & ")."
                        MarcarCelda cuerpoE.Cells(i, c), marcar, COLOR_ERROR
                    End If
                    previo = CDbl(datos(i, c))
                End If
            Next i
        End If
    Next d
End Sub

' Valida los parametros de una distribucion; devuelve en p() los parametros internos.
Private Function ValidarDistribucion(ByVal cod As Long, crudo() As Variant, ByVal pref As String, _
                                     ByRef errs As String, ByRef nErr As Long, p() As Double, _
                                     ByVal r As Long, ByVal d As Long, ByVal cuerpo As Range, ByVal fila As Long, _
                                     colP() As Long, ByVal dCol As Long, ByVal marcar As Boolean) As Boolean
    Dim np As Long, k As Long, antes As Long, a As Double, b As Double
    Dim vals() As Double, probs() As Double, acum() As Double, nv As Long, suma As Double

    antes = nErr
    np = DistNParams(cod)
    For k = 1 To 4
        p(k) = 0
    Next k

    If cod = D_DISCRETA Then
        If Not LeerLista(Txt(crudo(1)), vals, nv) Then
            AgregarError errs, nErr, pref & U("P1 debe ser la lista de valores separados por ; (ej. 0;50000;120000).")
            MarcarCelda cuerpo.Cells(fila, colP(dCol, 1)), marcar, COLOR_ERROR
        ElseIf Not LeerLista(Txt(crudo(2)), probs, k) Then
            AgregarError errs, nErr, pref & U("P2 debe ser la lista de probabilidades separadas por ; (ej. 0.5;0.3;0.2).")
            MarcarCelda cuerpo.Cells(fila, colP(dCol, 2)), marcar, COLOR_ERROR
        ElseIf k <> nv Then
            AgregarError errs, nErr, pref & "P1 y P2 deben tener la misma cantidad de elementos."
            MarcarCelda cuerpo.Cells(fila, colP(dCol, 1)), marcar, COLOR_ERROR
            MarcarCelda cuerpo.Cells(fila, colP(dCol, 2)), marcar, COLOR_ERROR
        Else
            suma = 0
            For k = 1 To nv
                If probs(k) < 0 Then suma = -1000
                suma = suma + probs(k)
            Next k
            If Abs(suma - 1) > 0.001 Then
                AgregarError errs, nErr, pref & U("las probabilidades de P2 deben ser \u2265 0 y sumar 1 (suman ") & Format$(suma, "0.000") & ")."
                MarcarCelda cuerpo.Cells(fila, colP(dCol, 2)), marcar, COLOR_ERROR
            Else
                ReDim acum(1 To nv)
                a = 0
                For k = 1 To nv
                    a = a + probs(k) / suma
                    acum(k) = a
                Next k
                acum(nv) = 1#
                gDiscV(r, d) = vals
                gDiscF(r, d) = acum
            End If
        End If
        ValidarDistribucion = (nErr = antes)
        Exit Function
    End If

    For k = 1 To np
        If EsNum(crudo(k)) Then
            p(k) = CDbl(crudo(k))
        ElseIf cod = D_TRIGEN And k = 4 And Len(Txt(crudo(k))) = 0 Then
            p(4) = 10
        ElseIf cod = D_PERT_MOD And k = 4 And Len(Txt(crudo(k))) = 0 Then
            p(4) = 4
        Else
            AgregarError errs, nErr, pref & U("falta el par\u00E1metro P") & k & " (" & DistParametro(cod, k) & U(") o no es num\u00E9rico.")
            MarcarCelda cuerpo.Cells(fila, colP(dCol, k)), marcar, COLOR_ERROR
        End If
    Next k
    If nErr > antes Then
        ValidarDistribucion = False
        Exit Function
    End If

    Select Case cod
        Case D_UNIFORME, D_DISC_UNIFORME
            If p(1) > p(2) Then AgregarError errs, nErr, pref & U("debe cumplirse M\u00EDnimo (P1) \u2264 M\u00E1ximo (P2).")
            If cod = D_DISC_UNIFORME And (p(1) <> Int(p(1)) Or p(2) <> Int(p(2))) Then
                AgregarError errs, nErr, pref & "P1 y P2 deben ser enteros."
            End If
        Case D_TRIANGULAR, D_PERT, D_PERT_MOD
            If Not (p(1) <= p(2) And p(2) <= p(3)) Then
                AgregarError errs, nErr, pref & U("debe cumplirse M\u00EDnimo (P1) \u2264 Moda (P2) \u2264 M\u00E1ximo (P3).")
            End If
            If cod = D_PERT_MOD And p(4) <= 0 Then AgregarError errs, nErr, pref & "gamma (P4) debe ser mayor que 0."
        Case D_TRIGEN
            If Not (p(1) <= p(2) And p(2) <= p(3)) Then
                AgregarError errs, nErr, pref & U("debe cumplirse Valor bajo (P1) \u2264 Moda (P2) \u2264 Valor alto (P3).")
            ElseIf p(4) <= 0 Or p(4) >= 50 Then
                AgregarError errs, nErr, pref & "el percentil bajo (P4) debe estar entre 0 y 50 (ej. 10)."
            Else
                ResolverTrigen p(1), p(2), p(3), p(4) / 100#, a, b
                p(1) = a
                p(3) = b
            End If
        Case D_BETA
            If p(1) <= 0 Or p(2) <= 0 Then AgregarError errs, nErr, pref & "alfa (P1) y beta (P2) deben ser mayores que 0."
            If p(3) > p(4) Then AgregarError errs, nErr, pref & U("debe cumplirse M\u00EDnimo (P3) \u2264 M\u00E1ximo (P4).")
        Case D_NORMAL
            If p(2) <= 0 Then AgregarError errs, nErr, pref & U("la desviaci\u00F3n est\u00E1ndar (P2) debe ser mayor que 0.")
        Case D_NORMAL_TRUNC
            If p(2) <= 0 Then
                AgregarError errs, nErr, pref & U("la desviaci\u00F3n est\u00E1ndar (P2) debe ser mayor que 0.")
            ElseIf p(3) >= p(4) Then
                AgregarError errs, nErr, pref & U("debe cumplirse M\u00EDnimo (P3) < M\u00E1ximo (P4).")
            ElseIf Phi((p(4) - p(1)) / p(2)) - Phi((p(3) - p(1)) / p(2)) < 0.001 Then
                AgregarError errs, nErr, pref & U("el intervalo [P3, P4] est\u00E1 demasiado lejos de la media (probabilidad < 0.1%).")
            End If
        Case D_LOGNORMAL
            If p(1) <= 0 Then AgregarError errs, nErr, pref & "la media (P1) debe ser mayor que 0."
            If p(2) <= 0 Then AgregarError errs, nErr, pref & U("la desviaci\u00F3n est\u00E1ndar (P2) debe ser mayor que 0.")
        Case D_GAMMA, D_WEIBULL
            If p(1) <= 0 Or p(2) <= 0 Then AgregarError errs, nErr, pref & "forma (P1) y escala (P2) deben ser mayores que 0."
        Case D_EXPONENCIAL
            If p(1) <= 0 Then AgregarError errs, nErr, pref & "la media (P1) debe ser mayor que 0."
        Case D_GUMBEL, D_LOGISTICA
            If p(2) <= 0 Then AgregarError errs, nErr, pref & "la escala (P2) debe ser mayor que 0."
        Case D_PARETO
            If p(1) <= 1 Then AgregarError errs, nErr, pref & "la forma (P1) debe ser mayor que 1 para que la media exista."
            If p(2) <= 0 Then AgregarError errs, nErr, pref & U("el m\u00EDnimo (P2) debe ser mayor que 0.")
        Case D_POISSON
            If p(1) < 0 Or p(1) > 1000000 Then AgregarError errs, nErr, pref & "la media (P1) debe estar entre 0 y 1,000,000."
        Case D_BINOMIAL
            If p(1) < 1 Or p(1) <> Int(p(1)) Or p(1) > 1000000 Then
                AgregarError errs, nErr, pref & "n (P1) debe ser un entero entre 1 y 1,000,000."
            End If
            If p(2) < 0 Or p(2) > 1 Then AgregarError errs, nErr, pref & "p (P2) debe estar entre 0 y 1."
    End Select
    If nErr > antes Then
        For k = 1 To np
            MarcarCelda cuerpo.Cells(fila, colP(dCol, k)), marcar, COLOR_ERROR
        Next k
    End If
    ValidarDistribucion = (nErr = antes)
End Function

' Lista de numeros separados por ";" (acepta punto o coma decimal).
Private Function LeerLista(ByVal s As String, vals() As Double, ByRef n As Long) As Boolean
    Dim partes As Variant, k As Long, t As String
    n = 0
    s = Trim$(s)
    If Len(s) = 0 Then Exit Function
    partes = Split(s, ";")
    ReDim vals(1 To UBound(partes) - LBound(partes) + 1)
    For k = LBound(partes) To UBound(partes)
        t = Replace(Trim$(partes(k)), ",", ".")
        If Len(t) = 0 Then Exit Function
        If Not EsNumeroTexto(t) Then Exit Function
        n = n + 1
        vals(n) = Val(t)
    Next k
    LeerLista = (n > 0)
End Function

Private Function EsNumeroTexto(ByVal t As String) As Boolean
    Dim k As Long, ch As String, puntos As Long, digitos As Long
    For k = 1 To Len(t)
        ch = Mid$(t, k, 1)
        If ch >= "0" And ch <= "9" Then
            digitos = digitos + 1
        ElseIf ch = "." Then
            puntos = puntos + 1
        ElseIf ch = "-" And k = 1 Then
            ' signo inicial permitido
        Else
            Exit Function
        End If
    Next k
    EsNumeroTexto = (digitos > 0 And puntos <= 1)
End Function

' TRIGEN: triangular (a, m, b) tal que P(X < bajo) = q y P(X > alto) = q (Vose).
Private Sub ResolverTrigen(ByVal bajo As Double, ByVal m As Double, ByVal alto As Double, ByVal q As Double, _
                           ByRef a As Double, ByRef b As Double)
    Dim it As Long, lo As Double, hi As Double, medio As Double, k As Long, ancho As Double
    If alto <= bajo Then
        a = bajo
        b = alto
        Exit Sub
    End If
    a = bajo
    b = alto
    ancho = alto - bajo
    For it = 1 To 60
        ' a: raiz de (bajo - a)^2 - q (b - a)(m - a) = 0 con a <= bajo
        hi = bajo
        lo = bajo - ancho
        Do While (bajo - lo) ^ 2 - q * (b - lo) * (m - lo) < 0
            lo = lo - ancho
        Loop
        For k = 1 To 80
            medio = (lo + hi) / 2
            If (bajo - medio) ^ 2 - q * (b - medio) * (m - medio) > 0 Then lo = medio Else hi = medio
        Next k
        a = (lo + hi) / 2
        ' b: raiz de (b - alto)^2 - q (b - a)(b - m) = 0 con b >= alto
        lo = alto
        hi = alto + ancho
        Do While (hi - alto) ^ 2 - q * (hi - a) * (hi - m) < 0
            hi = hi + ancho
        Loop
        For k = 1 To 80
            medio = (lo + hi) / 2
            If (medio - alto) ^ 2 - q * (medio - a) * (medio - m) > 0 Then hi = medio Else lo = medio
        Next k
        b = (lo + hi) / 2
    Next it
End Sub

Private Sub AgregarError(ByRef errs As String, ByRef nErr As Long, ByVal msg As String)
    nErr = nErr + 1
    If nErr <= MAX_ERRORES_MSG Then
        errs = errs & "- " & msg & vbLf
    ElseIf nErr = MAX_ERRORES_MSG + 1 Then
        errs = errs & U("- ... (hay m\u00E1s errores; corrija los anteriores y valide de nuevo)") & vbLf
    End If
End Sub

Private Sub AgregarAdvertencia(ByVal msg As String)
    gNAdv = gNAdv + 1
    If gNAdv <= MAX_ERRORES_MSG Then
        gAdvert = gAdvert & "- " & msg & vbLf
    ElseIf gNAdv = MAX_ERRORES_MSG + 1 Then
        gAdvert = gAdvert & U("- ... (hay m\u00E1s advertencias)") & vbLf
    End If
End Sub

Private Sub MarcarCelda(ByVal rng As Range, ByVal marcar As Boolean, ByVal color As Long)
    If marcar Then rng.Interior.Color = color
End Sub


' ======================================================================
'  CATALOGO DE DISTRIBUCIONES
' ======================================================================

Private Function DistCodigo(ByVal s As String) As Long
    Dim k As Long
    s = UCase$(Trim$(s))
    If Len(s) = 0 Or s = "-" Or s = "(VACIO)" Or s = U("(VAC\u00CDO)") Or s = "NINGUNA" Or s = ChrW$(8212) Or s = ChrW$(8211) Then
        DistCodigo = D_NINGUNA
        Exit Function
    End If
    For k = 1 To N_DISTRIBUCIONES
        If DistNombre(k) = s Then
            DistCodigo = k
            Exit Function
        End If
    Next k
    DistCodigo = D_DESCONOCIDA
End Function

Private Function DistNombre(ByVal cod As Long) As String
    Select Case cod
        Case D_CONSTANTE: DistNombre = "CONSTANTE"
        Case D_UNIFORME: DistNombre = "UNIFORME"
        Case D_TRIANGULAR: DistNombre = "TRIANGULAR"
        Case D_TRIGEN: DistNombre = "TRIGEN"
        Case D_PERT: DistNombre = "PERT"
        Case D_PERT_MOD: DistNombre = "PERT_MODIFICADA"
        Case D_BETA: DistNombre = "BETA_GENERAL"
        Case D_NORMAL: DistNombre = "NORMAL"
        Case D_NORMAL_TRUNC: DistNombre = "NORMAL_TRUNCADA"
        Case D_LOGNORMAL: DistNombre = "LOGNORMAL"
        Case D_GAMMA: DistNombre = "GAMMA"
        Case D_EXPONENCIAL: DistNombre = "EXPONENCIAL"
        Case D_WEIBULL: DistNombre = "WEIBULL"
        Case D_GUMBEL: DistNombre = "GUMBEL"
        Case D_LOGISTICA: DistNombre = "LOGISTICA"
        Case D_PARETO: DistNombre = "PARETO"
        Case D_POISSON: DistNombre = "POISSON"
        Case D_BINOMIAL: DistNombre = "BINOMIAL"
        Case D_DISC_UNIFORME: DistNombre = "DISCRETA_UNIFORME"
        Case D_DISCRETA: DistNombre = "DISCRETA"
        Case Else: DistNombre = "-"
    End Select
End Function

Private Function DistNParams(ByVal cod As Long) As Long
    Select Case cod
        Case D_CONSTANTE, D_EXPONENCIAL, D_POISSON: DistNParams = 1
        Case D_UNIFORME, D_NORMAL, D_LOGNORMAL, D_GAMMA, D_WEIBULL, D_GUMBEL, D_LOGISTICA, D_PARETO, _
             D_BINOMIAL, D_DISC_UNIFORME, D_DISCRETA: DistNParams = 2
        Case D_TRIANGULAR, D_PERT: DistNParams = 3
        Case D_TRIGEN, D_PERT_MOD, D_BETA, D_NORMAL_TRUNC: DistNParams = 4
        Case Else: DistNParams = 0
    End Select
End Function

Private Function DistParametro(ByVal cod As Long, ByVal k As Long) As String
    Dim t As Variant
    Select Case cod
        Case D_CONSTANTE: t = Array("valor", "", "", "")
        Case D_UNIFORME, D_DISC_UNIFORME: t = Array(U("m\u00EDnimo"), U("m\u00E1ximo"), "", "")
        Case D_TRIANGULAR, D_PERT: t = Array(U("m\u00EDnimo"), "moda", U("m\u00E1ximo"), "")
        Case D_PERT_MOD: t = Array(U("m\u00EDnimo"), "moda", U("m\u00E1ximo"), "gamma")
        Case D_TRIGEN: t = Array("valor bajo", "moda", "valor alto", "% bajo")
        Case D_BETA: t = Array("alfa", "beta", U("m\u00EDnimo"), U("m\u00E1ximo"))
        Case D_NORMAL, D_LOGNORMAL: t = Array("media", U("desv. est\u00E1ndar"), "", "")
        Case D_NORMAL_TRUNC: t = Array("media", U("desv. est\u00E1ndar"), U("m\u00EDnimo"), U("m\u00E1ximo"))
        Case D_GAMMA, D_WEIBULL: t = Array("forma", "escala", "", "")
        Case D_EXPONENCIAL, D_POISSON: t = Array("media", "", "", "")
        Case D_GUMBEL: t = Array(U("ubicaci\u00F3n"), "escala", "", "")
        Case D_LOGISTICA: t = Array("media", "escala", "", "")
        Case D_PARETO: t = Array("forma", U("m\u00EDnimo"), "", "")
        Case D_BINOMIAL: t = Array("n", "p", "", "")
        Case D_DISCRETA: t = Array("valores", "probabilidades", "", "")
        Case Else: t = Array("", "", "", "")
    End Select
    DistParametro = t(k - 1)
End Function

' Media teorica de la distribucion (sin signo ni probabilidad de ocurrencia).
Private Function DistMediaTeorica(ByVal cod As Long, ByVal p1 As Double, ByVal p2 As Double, ByVal p3 As Double, _
                                  ByVal p4 As Double, ByVal r As Long, ByVal d As Long) As Double
    Dim al As Double, be As Double, za As Double, zb As Double, v As Variant, f As Variant, k As Long, prev As Double
    Select Case cod
        Case D_CONSTANTE: DistMediaTeorica = p1
        Case D_UNIFORME, D_DISC_UNIFORME: DistMediaTeorica = (p1 + p2) / 2
        Case D_TRIANGULAR, D_TRIGEN: DistMediaTeorica = (p1 + p2 + p3) / 3
        Case D_PERT, D_PERT_MOD
            If p3 <= p1 Then
                DistMediaTeorica = p1
            Else
                If cod = D_PERT Then p4 = 4
                al = 1 + p4 * (p2 - p1) / (p3 - p1)
                be = 1 + p4 * (p3 - p2) / (p3 - p1)
                DistMediaTeorica = p1 + (p3 - p1) * al / (al + be)
            End If
        Case D_BETA: DistMediaTeorica = p3 + (p4 - p3) * p1 / (p1 + p2)
        Case D_NORMAL, D_LOGNORMAL, D_LOGISTICA, D_POISSON, D_EXPONENCIAL: DistMediaTeorica = p1
        Case D_NORMAL_TRUNC
            za = (p3 - p1) / p2
            zb = (p4 - p1) / p2
            DistMediaTeorica = p1 + p2 * (DensNormal(za) - DensNormal(zb)) / (Phi(zb) - Phi(za))
        Case D_GAMMA: DistMediaTeorica = p1 * p2
        Case D_WEIBULL: DistMediaTeorica = p2 * Exp(LnGamma(1 + 1 / p1))
        Case D_GUMBEL: DistMediaTeorica = p1 + GAMMA_EULER * p2
        Case D_PARETO: DistMediaTeorica = p1 * p2 / (p1 - 1)
        Case D_BINOMIAL: DistMediaTeorica = p1 * p2
        Case D_DISCRETA
            v = gDiscV(r, d)
            f = gDiscF(r, d)
            prev = 0
            For k = LBound(v) To UBound(v)
                DistMediaTeorica = DistMediaTeorica + v(k) * (f(k) - prev)
                prev = f(k)
            Next k
    End Select
End Function


' ======================================================================
'  GENERADOR DE NUMEROS ALEATORIOS MRG32k3a Y VARIABLES ALEATORIAS
' ======================================================================

Private Function FMod(ByVal a As Double, ByVal m As Double) As Double
    FMod = a - m * Int(a / m)
    If FMod < 0 Then FMod = FMod + m
    If FMod >= m Then FMod = FMod - m
End Function

' Estado inicial a partir de una semilla entera (reproducible).
Private Sub SembrarGenerador(ByVal semilla As Double)
    Dim x As Double, v(1 To 6) As Double, k As Long
    x = FMod(Abs(Int(semilla)), 4294967296#)
    For k = 1 To 6
        x = FMod(69069# * x + 1#, 4294967296#)
        v(k) = x
    Next k
    gS10 = FMod(v(1), MRG_M1)
    gS11 = FMod(v(2), MRG_M1)
    gS12 = FMod(v(3), MRG_M1)
    gS20 = FMod(v(4), MRG_M2)
    gS21 = FMod(v(5), MRG_M2)
    gS22 = FMod(v(6), MRG_M2)
    If gS10 = 0 And gS11 = 0 And gS12 = 0 Then gS10 = 12345#
    If gS20 = 0 And gS21 = 0 And gS22 = 0 Then gS20 = 12345#
End Sub

Private Sub FijarEstadoGenerador(ByVal a0 As Double, ByVal a1 As Double, ByVal a2 As Double, _
                                 ByVal b0 As Double, ByVal b1 As Double, ByVal b2 As Double)
    gS10 = a0: gS11 = a1: gS12 = a2
    gS20 = b0: gS21 = b1: gS22 = b2
End Sub

' Uniforme en (0,1): nunca devuelve 0 ni 1.
Private Function Aleatorio() As Double
    Dim p1 As Double, p2 As Double
    p1 = MRG_A12 * gS11 - MRG_A13N * gS10
    p1 = p1 - MRG_M1 * Int(p1 / MRG_M1)
    If p1 < 0 Then p1 = p1 + MRG_M1
    If p1 >= MRG_M1 Then p1 = p1 - MRG_M1
    gS10 = gS11: gS11 = gS12: gS12 = p1
    p2 = MRG_A21 * gS22 - MRG_A23N * gS20
    p2 = p2 - MRG_M2 * Int(p2 / MRG_M2)
    If p2 < 0 Then p2 = p2 + MRG_M2
    If p2 >= MRG_M2 Then p2 = p2 - MRG_M2
    gS20 = gS21: gS21 = gS22: gS22 = p2
    If p1 > p2 Then
        Aleatorio = (p1 - p2) * MRG_NORMA
    Else
        Aleatorio = (p1 - p2 + MRG_M1) * MRG_NORMA
    End If
End Function

Private Function Muestra(ByVal cod As Long, ByVal p1 As Double, ByVal p2 As Double, ByVal p3 As Double, _
                         ByVal p4 As Double, ByVal r As Long, ByVal d As Long) As Double
    Dim u As Double
    Select Case cod
        Case D_CONSTANTE: Muestra = p1
        Case D_UNIFORME: Muestra = p1 + Aleatorio() * (p2 - p1)
        Case D_TRIANGULAR, D_TRIGEN: Muestra = GenTriangular(p1, p2, p3)
        Case D_PERT: Muestra = GenPert(p1, p2, p3, 4#)
        Case D_PERT_MOD: Muestra = GenPert(p1, p2, p3, p4)
        Case D_BETA: Muestra = GenBeta(p1, p2, p3, p4)
        Case D_NORMAL: Muestra = p1 + p2 * GenNormal01()
        Case D_NORMAL_TRUNC: Muestra = GenNormalTruncada(p1, p2, p3, p4)
        Case D_LOGNORMAL: Muestra = GenLogNormal(p1, p2)
        Case D_GAMMA: Muestra = p2 * GenGamma(p1)
        Case D_EXPONENCIAL: Muestra = -p1 * Log(Aleatorio())
        Case D_WEIBULL: Muestra = p2 * (-Log(Aleatorio())) ^ (1# / p1)
        Case D_GUMBEL: Muestra = p1 - p2 * Log(-Log(Aleatorio()))
        Case D_LOGISTICA
            u = Aleatorio()
            Muestra = p1 + p2 * Log(u / (1# - u))
        Case D_PARETO: Muestra = p2 / Aleatorio() ^ (1# / p1)
        Case D_POISSON: Muestra = GenPoisson(p1)
        Case D_BINOMIAL: Muestra = GenBinomial(p1, p2)
        Case D_DISC_UNIFORME
            Muestra = p1 + Int(Aleatorio() * (p2 - p1 + 1#))
            If Muestra > p2 Then Muestra = p2
        Case D_DISCRETA: Muestra = GenDiscreta(r, d)
        Case Else: Muestra = 0
    End Select
End Function

Private Function GenTriangular(ByVal a As Double, ByVal m As Double, ByVal b As Double) As Double
    Dim u As Double
    If b <= a Then
        GenTriangular = a
        Exit Function
    End If
    u = Aleatorio()
    If u < (m - a) / (b - a) Then
        GenTriangular = a + Sqr(u * (b - a) * (m - a))
    Else
        GenTriangular = b - Sqr((1# - u) * (b - a) * (b - m))
    End If
End Function

' Beta-PERT con parametro lambda (4 = PERT clasica).
Private Function GenPert(ByVal a As Double, ByVal m As Double, ByVal b As Double, ByVal lambda As Double) As Double
    Dim al As Double, be As Double
    If b <= a Then
        GenPert = a
        Exit Function
    End If
    al = 1# + lambda * (m - a) / (b - a)
    be = 1# + lambda * (b - m) / (b - a)
    GenPert = GenBeta(al, be, a, b)
End Function

Private Function GenBeta(ByVal alfa As Double, ByVal beta As Double, ByVal mn As Double, ByVal mx As Double) As Double
    Dim x As Double, y As Double
    If mx <= mn Then
        GenBeta = mn
        Exit Function
    End If
    x = GenGamma(alfa)
    y = GenGamma(beta)
    GenBeta = mn + (mx - mn) * x / (x + y)
End Function

' Gamma(k, 1): metodo de Marsaglia-Tsang.
Private Function GenGamma(ByVal k As Double) As Double
    Dim d As Double, c As Double, x As Double, v As Double, u As Double
    If k < 1# Then
        GenGamma = GenGamma(k + 1#) * Aleatorio() ^ (1# / k)
        Exit Function
    End If
    d = k - 1# / 3#
    c = 1# / Sqr(9# * d)
    Do
        Do
            x = GenNormal01()
            v = 1# + c * x
        Loop While v <= 0
        v = v * v * v
        u = Aleatorio()
        If u < 1# - 0.0331 * x * x * x * x Then Exit Do
        If Log(u) < 0.5 * x * x + d * (1# - v + Log(v)) Then Exit Do
    Loop
    GenGamma = d * v
End Function

' Normal estandar por Box-Muller.
Private Function GenNormal01() As Double
    GenNormal01 = Sqr(-2# * Log(Aleatorio())) * Cos(DOS_PI * Aleatorio())
End Function

Private Function GenNormalTruncada(ByVal mu As Double, ByVal sd As Double, ByVal mn As Double, ByVal mx As Double) As Double
    Dim fa As Double, fb As Double, u As Double, x As Double
    fa = Phi((mn - mu) / sd)
    fb = Phi((mx - mu) / sd)
    u = fa + Aleatorio() * (fb - fa)
    If u <= 0 Then u = 1E-300
    If u >= 1 Then u = 1# - 1E-16
    x = mu + sd * PhiInv(u)
    If x < mn Then x = mn
    If x > mx Then x = mx
    GenNormalTruncada = x
End Function

' LogNormal parametrizada con la media y la desviacion de la variable.
Private Function GenLogNormal(ByVal m As Double, ByVal sd As Double) As Double
    Dim s2 As Double
    s2 = Log(1# + (sd / m) ^ 2)
    GenLogNormal = Exp(Log(m) - s2 / 2# + Sqr(s2) * GenNormal01())
End Function

' Poisson: Knuth si lambda < 30; si no, PTRS (Hormann, rechazo transformado).
Private Function GenPoisson(ByVal lam As Double) As Double
    Dim L As Double, k As Double, p As Double
    Dim slam As Double, loglam As Double, b As Double, a As Double, invalfa As Double, vr As Double
    Dim u As Double, v As Double, us As Double
    If lam <= 0 Then
        GenPoisson = 0
        Exit Function
    End If
    If lam < 30 Then
        L = Exp(-lam)
        k = 0
        p = 1#
        Do
            k = k + 1
            p = p * Aleatorio()
        Loop While p > L
        GenPoisson = k - 1
        Exit Function
    End If
    slam = Sqr(lam)
    loglam = Log(lam)
    b = 0.931 + 2.53 * slam
    a = -0.059 + 0.02483 * b
    invalfa = 1.1239 + 1.1328 / (b - 3.4)
    vr = 0.9277 - 3.6224 / (b - 2)
    Do
        u = Aleatorio() - 0.5
        v = Aleatorio()
        us = 0.5 - Abs(u)
        k = Int((2 * a / us + b) * u + lam + 0.43)
        If us >= 0.07 And v <= vr Then
            GenPoisson = k
            Exit Function
        End If
        If k >= 0 And Not (us < 0.013 And v > us) Then
            If Log(v) + Log(invalfa) - Log(a / (us * us) + b) <= -lam + k * loglam - LnGamma(k + 1) Then
                GenPoisson = k
                Exit Function
            End If
        End If
    Loop
End Function

' Binomial: suma de Bernoulli si n <= 50; si no, inversion con recurrencia
' (o aproximacion normal si la probabilidad de 0 no es representable).
Private Function GenBinomial(ByVal n As Double, ByVal p As Double) As Double
    Dim k As Double, u As Double, pmf As Double, cdf As Double, q As Double
    If p <= 0 Then
        GenBinomial = 0
        Exit Function
    End If
    If p >= 1 Then
        GenBinomial = n
        Exit Function
    End If
    If n <= 50 Then
        For k = 1 To n
            If Aleatorio() < p Then GenBinomial = GenBinomial + 1
        Next k
        Exit Function
    End If
    q = 1# - p
    If n * Log(q) > -700 Then
        u = Aleatorio()
        pmf = Exp(n * Log(q))
        cdf = pmf
        k = 0
        Do While u > cdf And k < n
            pmf = pmf * (n - k) / (k + 1) * p / q
            k = k + 1
            cdf = cdf + pmf
        Loop
        GenBinomial = k
    Else
        k = Int(n * p + Sqr(n * p * q) * GenNormal01() + 0.5)
        If k < 0 Then k = 0
        If k > n Then k = n
        GenBinomial = k
    End If
End Function

Private Function GenDiscreta(ByVal r As Long, ByVal d As Long) As Double
    Dim u As Double, k As Long, f As Variant, v As Variant
    f = gDiscF(r, d)
    v = gDiscV(r, d)
    u = Aleatorio()
    For k = LBound(f) To UBound(f)
        If u <= f(k) Then
            GenDiscreta = v(k)
            Exit Function
        End If
    Next k
    GenDiscreta = v(UBound(v))
End Function

' Distribucion normal estandar acumulada (erfc de Numerical Recipes, error < 1.2e-7).
Private Function Phi(ByVal x As Double) As Double
    Dim z As Double, t As Double, r As Double
    z = Abs(x) / 1.4142135623731
    t = 1# / (1# + 0.5 * z)
    r = t * Exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + _
        t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + _
        t * (-0.82215223 + t * 0.17087277)))))))))
    If x >= 0 Then Phi = 1# - 0.5 * r Else Phi = 0.5 * r
End Function

Private Function DensNormal(ByVal x As Double) As Double
    DensNormal = Exp(-0.5 * x * x) / 2.506628274631
End Function

' Inversa de la normal estandar (algoritmo de Acklam, error relativo < 1.2e-9).
Private Function PhiInv(ByVal p As Double) As Double
    Dim q As Double, r As Double
    Const A1 As Double = -39.6968302866538, A2 As Double = 220.946098424521, A3 As Double = -275.928510446969
    Const A4 As Double = 138.357751867269, A5 As Double = -30.6647980661472, A6 As Double = 2.50662827745924
    Const B1 As Double = -54.4760987982241, B2 As Double = 161.585836858041, B3 As Double = -155.698979859887
    Const B4 As Double = 66.8013118877197, B5 As Double = -13.2806815528857
    Const C1 As Double = -7.78489400243029E-03, C2 As Double = -0.322396458041136, C3 As Double = -2.40075827716184
    Const C4 As Double = -2.54973253934373, C5 As Double = 4.37466414146497, C6 As Double = 2.93816398269878
    Const D1 As Double = 7.78469570904146E-03, D2 As Double = 0.32246712907004, D3 As Double = 2.445134137143
    Const D4 As Double = 3.75440866190742
    Const P_BAJO As Double = 0.02425
    If p < P_BAJO Then
        q = Sqr(-2# * Log(p))
        PhiInv = (((((C1 * q + C2) * q + C3) * q + C4) * q + C5) * q + C6) / ((((D1 * q + D2) * q + D3) * q + D4) * q + 1#)
    ElseIf p <= 1# - P_BAJO Then
        q = p - 0.5
        r = q * q
        PhiInv = (((((A1 * r + A2) * r + A3) * r + A4) * r + A5) * r + A6) * q / _
                 (((((B1 * r + B2) * r + B3) * r + B4) * r + B5) * r + 1#)
    Else
        q = Sqr(-2# * Log(1# - p))
        PhiInv = -(((((C1 * q + C2) * q + C3) * q + C4) * q + C5) * q + C6) / ((((D1 * q + D2) * q + D3) * q + D4) * q + 1#)
    End If
End Function

' Logaritmo de la funcion Gamma (Numerical Recipes, x > 0).
Private Function LnGamma(ByVal x As Double) As Double
    Dim y As Double, tmp As Double, ser As Double
    y = x
    tmp = x + 5.5
    tmp = tmp - (x + 0.5) * Log(tmp)
    ser = 1.00000000019001
    y = y + 1: ser = ser + 76.1800917294715 / y
    y = y + 1: ser = ser - 86.5053203294168 / y
    y = y + 1: ser = ser + 24.0140982408309 / y
    y = y + 1: ser = ser - 1.23173957245016 / y
    y = y + 1: ser = ser + 1.20865097386618E-03 / y
    y = y + 1: ser = ser - 5.395239384953E-06 / y
    LnGamma = -tmp + Log(2.506628274631 * ser / x)
End Function


' ======================================================================
'  NUCLEO DE LA SIMULACION
' ======================================================================

Private Sub NucleoSimulacion()
    Dim r As Long, i As Long, d As Long, ua As Double, x As Double
    Dim nIt As Long, nRi As Long, nDi As Long
    Dim ocA As Boolean, ocD As Boolean, s() As Double

    gEtapa = "iniciando el generador de numeros aleatorios"
    If gSemillaFija Then
        SembrarGenerador gSemilla
    Else
        SembrarGenerador Int(Timer * 1000#) + 7919# * Second(Now) + 104729# * Minute(Now)
    End If

    gEtapa = "reservando memoria para la simulacion"
    nIt = gN
    nRi = gNR
    nDi = gND
    ReDim gM(1 To nIt, 1 To nRi, 1 To nDi)
    If gHayDespues Then
        ReDim gMD(1 To nIt, 1 To nRi, 1 To nDi)
    End If
    ReDim gOcc(1 To nRi)
    gEtapa = "simulando iteraciones"

    For r = 1 To gNR
        gRiesgoActual = r
        For i = 1 To gN
            ua = Aleatorio()
            ocA = (ua < gR(r).Prob)
            ocD = False
            If gHayDespues Then ocD = (ua < gR(r).ProbRes)
            If ocA Or ocD Then
                If ocA Then gOcc(r) = gOcc(r) + 1
                For d = 1 To gND
                    If gDist(r, d) > 0 Then
                        gDimActual = d
                        x = gR(r).Signo * Muestra(gDist(r, d), gPar(r, d, 1), gPar(r, d, 2), gPar(r, d, 3), gPar(r, d, 4), r, d)
                        If ocA Then gM(i, r, d) = x
                        If ocD Then gMD(i, r, d) = x * gR(r).FactorRes
                    End If
                Next d
            End If
        Next i
        gDimActual = 0
        Application.StatusBar = U("Simulando riesgo ") & r & " de " & gNR & " (" & Format$(r / gNR, "0%") & ")..."
        DoEvents
    Next r
    gRiesgoActual = 0

    gEtapa = U("aplicando la correlaci\u00F3n entre riesgos")
    Application.StatusBar = U("Aplicando correlaci\u00F3n entre riesgos...")
    AplicarCorrelacion

    gEtapa = "calculando totales"
    ReDim gTot(1 To nIt, 1 To nDi)
    If gHayDespues Then
        ReDim gTotD(1 To nIt, 1 To nDi)
    End If
    For d = 1 To gND
        For i = 1 To gN
            For r = 1 To gNR
                gTot(i, d) = gTot(i, d) + gM(i, r, d)
            Next r
        Next i
        If gHayDespues Then
            For i = 1 To gN
                For r = 1 To gNR
                    gTotD(i, d) = gTotD(i, d) + gMD(i, r, d)
                Next r
                If d = gDimCosto Then gTotD(i, d) = gTotD(i, d) + gCostoRespTotal
            Next i
        End If
    Next d

    ' Totales ordenados (matrices 2D: se evita guardar arreglos dentro de Variant)
    ReDim gOrdM(1 To nIt, 1 To nDi)
    If gHayDespues Then
        ReDim gOrdDM(1 To nIt, 1 To nDi)
    End If
    For d = 1 To gND
        ColumnaTotal gTot, d, gN, s
        QuickSort s, 1, gN
        For i = 1 To gN
            gOrdM(i, d) = s(i)
        Next i
        If gHayDespues Then
            ColumnaTotal gTotD, d, gN, s
            QuickSort s, 1, gN
            For i = 1 To gN
                gOrdDM(i, d) = s(i)
            Next i
        End If
    Next d
End Sub

' Iman-Conover con un factor comun por grupo. La correlacion de rango objetivo
' rho se convierte a correlacion normal r = 2 sin(pi rho / 6).
Private Sub AplicarCorrelacion()
    Dim r As Long, q As Long, g As Long, i As Long, d As Long, kd As Long
    Dim rn As Double, w() As Double, sc() As Double, clave() As Double
    Dim ixK() As Long, ixS() As Long, perm() As Long, tmp() As Double
    Dim yaVisto As Boolean, miembros() As Long, nm As Long, rkM() As Double, suma As Double, npar As Long
    Dim ra() As Double, rb() As Double, ix() As Long

    gNG = 0
    ReDim gGrupoNom(1 To gNR + 1)
    ReDim gGrupoObj(1 To gNR + 1)
    ReDim gGrupoLog(1 To gNR + 1)
    ReDim gGrupoN(1 To gNR + 1)
    ReDim w(1 To gN)
    ReDim sc(1 To gN)
    ReDim perm(1 To gN)
    ReDim tmp(1 To gN)
    ReDim miembros(1 To gNR)

    For r = 1 To gNR
        If Len(gR(r).Grupo) > 0 Then
            yaVisto = False
            For q = 1 To gNG
                If gGrupoNom(q) = gR(r).Grupo Then yaVisto = True
            Next q
            If Not yaVisto Then
                gNG = gNG + 1
                gGrupoNom(gNG) = gR(r).Grupo
                gGrupoObj(gNG) = gR(r).Rho
                nm = 0
                For q = r To gNR
                    If gR(q).Grupo = gR(r).Grupo Then
                        nm = nm + 1
                        miembros(nm) = q
                    End If
                Next q
                gGrupoN(gNG) = nm
                rn = 2# * Sin(PI_ * gR(r).Rho / 6#)
                For i = 1 To gN
                    w(i) = GenNormal01()
                Next i
                For q = 1 To nm
                    gRiesgoActual = miembros(q)
                    kd = PrimeraDimension(miembros(q))
                    If kd > 0 And nm > 1 And rn > 0 Then
                        For i = 1 To gN
                            sc(i) = Sqr(rn) * w(i) + Sqr(1# - rn) * GenNormal01()
                        Next i
                        ReDim clave(1 To gN)
                        For i = 1 To gN
                            clave(i) = gM(i, miembros(q), kd)
                        Next i
                        OrdenIndices clave, gN, ixK
                        OrdenIndices sc, gN, ixS
                        For i = 1 To gN
                            perm(ixS(i)) = ixK(i)
                        Next i
                        For d = 1 To gND
                            If gDist(miembros(q), d) > 0 Then
                                For i = 1 To gN
                                    tmp(i) = gM(perm(i), miembros(q), d)
                                Next i
                                For i = 1 To gN
                                    gM(i, miembros(q), d) = tmp(i)
                                Next i
                                If gHayDespues Then
                                    For i = 1 To gN
                                        tmp(i) = gMD(perm(i), miembros(q), d)
                                    Next i
                                    For i = 1 To gN
                                        gMD(i, miembros(q), d) = tmp(i)
                                    Next i
                                End If
                            End If
                        Next d
                    End If
                Next q
                ' Correlacion de rango lograda: promedio de pares (rangos en una matriz)
                suma = 0
                npar = 0
                If nm > 1 Then
                    ReDim rkM(1 To gN, 1 To nm)
                    For q = 1 To nm
                        kd = PrimeraDimension(miembros(q))
                        ReDim clave(1 To gN)
                        If kd > 0 Then
                            For i = 1 To gN
                                clave(i) = gM(i, miembros(q), kd)
                            Next i
                        End If
                        RangosPromedio clave, gN, ra, ix
                        For i = 1 To gN
                            rkM(i, q) = ra(i)
                        Next i
                    Next q
                    ReDim ra(1 To gN)
                    ReDim rb(1 To gN)
                    For q = 1 To nm - 1
                        For g = q + 1 To nm
                            For i = 1 To gN
                                ra(i) = rkM(i, q)
                                rb(i) = rkM(i, g)
                            Next i
                            suma = suma + Pearson(ra, rb, gN)
                            npar = npar + 1
                        Next g
                    Next q
                End If
                If npar > 0 Then gGrupoLog(gNG) = suma / npar Else gGrupoLog(gNG) = 0
            End If
        End If
    Next r
    gRiesgoActual = 0
End Sub

Private Function PrimeraDimension(ByVal r As Long) As Long
    Dim d As Long
    For d = 1 To gND
        If gDist(r, d) > 0 Then
            PrimeraDimension = d
            Exit Function
        End If
    Next d
End Function

' Valor monetario esperado del riesgo r en la dimension d = p x media teorica x signo.
Private Function VME(ByVal r As Long, ByVal d As Long) As Double
    If gDist(r, d) <= 0 Then Exit Function
    VME = gR(r).Prob * gR(r).Signo * _
          DistMediaTeorica(gDist(r, d), gPar(r, d, 1), gPar(r, d, 2), gPar(r, d, 3), gPar(r, d, 4), r, d)
End Function

Private Function ImpactoMedioCondicional(ByVal r As Long, ByVal d As Long) As Double
    If gDist(r, d) <= 0 Then Exit Function
    ImpactoMedioCondicional = DistMediaTeorica(gDist(r, d), gPar(r, d, 1), gPar(r, d, 2), gPar(r, d, 3), gPar(r, d, 4), r, d)
End Function


' ======================================================================
'  ESTADISTICA
' ======================================================================

Private Sub ColumnaRiesgo(ByVal r As Long, ByVal d As Long, ByVal N As Long, dst() As Double)
    Dim i As Long
    ReDim dst(1 To N)
    For i = 1 To N
        dst(i) = gM(i, r, d)
    Next i
End Sub

' Totales ordenados de la dimension d (despues = True: escenario despues de respuestas).
Private Sub Ordenados(ByVal d As Long, ByVal despues As Boolean, dst() As Double)
    If despues Then
        ColumnaTotal gOrdDM, d, gN, dst
    Else
        ColumnaTotal gOrdM, d, gN, dst
    End If
End Sub

Private Sub ColumnaTotal(m() As Double, ByVal d As Long, ByVal N As Long, dst() As Double)
    Dim i As Long
    ReDim dst(1 To N)
    For i = 1 To N
        dst(i) = m(i, d)
    Next i
End Sub

Private Sub QuickSort(a() As Double, ByVal lo As Long, ByVal hi As Long)
    Dim i As Long, j As Long, pv As Double, tmp As Double
    Do While lo < hi
        i = lo
        j = hi
        pv = a((lo + hi) \ 2)
        Do While i <= j
            Do While a(i) < pv
                i = i + 1
            Loop
            Do While a(j) > pv
                j = j - 1
            Loop
            If i <= j Then
                tmp = a(i): a(i) = a(j): a(j) = tmp
                i = i + 1
                j = j - 1
            End If
        Loop
        If j - lo < hi - i Then
            If lo < j Then QuickSort a, lo, j
            lo = i
        Else
            If i < hi Then QuickSort a, i, hi
            hi = j
        End If
    Loop
End Sub

Private Sub QuickSortIdx(a() As Double, ix() As Long, ByVal lo As Long, ByVal hi As Long)
    Dim i As Long, j As Long, pv As Double, tmp As Double, ti As Long
    Do While lo < hi
        i = lo
        j = hi
        pv = a((lo + hi) \ 2)
        Do While i <= j
            Do While a(i) < pv
                i = i + 1
            Loop
            Do While a(j) > pv
                j = j - 1
            Loop
            If i <= j Then
                tmp = a(i): a(i) = a(j): a(j) = tmp
                ti = ix(i): ix(i) = ix(j): ix(j) = ti
                i = i + 1
                j = j - 1
            End If
        Loop
        If j - lo < hi - i Then
            If lo < j Then QuickSortIdx a, ix, lo, j
            lo = i
        Else
            If i < hi Then QuickSortIdx a, ix, i, hi
            hi = j
        End If
    Loop
End Sub

' ix(k) = indice del k-esimo menor valor de x.
Private Sub OrdenIndices(x() As Double, ByVal N As Long, ix() As Long)
    Dim k() As Double, i As Long
    ReDim k(1 To N)
    ReDim ix(1 To N)
    For i = 1 To N
        k(i) = x(i)
        ix(i) = i
    Next i
    QuickSortIdx k, ix, 1, N
End Sub

Private Function Percentil(s() As Double, ByVal N As Long, ByVal p As Double) As Double
    Dim h As Double, k As Long
    If N <= 1 Then
        Percentil = s(1)
        Exit Function
    End If
    h = (N - 1) * p / 100 + 1
    k = Int(h)
    If k >= N Then
        Percentil = s(N)
    ElseIf k < 1 Then
        Percentil = s(1)
    Else
        Percentil = s(k) + (h - k) * (s(k + 1) - s(k))
    End If
End Function

Private Function EstMedia(a() As Double, ByVal N As Long) As Double
    Dim i As Long, s As Double
    For i = 1 To N
        s = s + a(i)
    Next i
    EstMedia = s / N
End Function

Private Function EstDesv(a() As Double, ByVal N As Long, ByVal m As Double) As Double
    Dim i As Long, s As Double
    If N < 2 Then Exit Function
    For i = 1 To N
        s = s + (a(i) - m) * (a(i) - m)
    Next i
    EstDesv = Sqr(s / (N - 1))
End Function

Private Function FraccionCero(a() As Double, ByVal N As Long) As Double
    Dim i As Long, k As Long
    For i = 1 To N
        If a(i) = 0 Then k = k + 1
    Next i
    FraccionCero = k / N
End Function

Private Sub RangosPromedio(x() As Double, ByVal N As Long, rk() As Double, ix() As Long)
    Dim k() As Double, i As Long, j As Long, m As Long, prom As Double
    ReDim k(1 To N)
    ReDim ix(1 To N)
    ReDim rk(1 To N)
    For i = 1 To N
        k(i) = x(i)
        ix(i) = i
    Next i
    QuickSortIdx k, ix, 1, N
    i = 1
    Do While i <= N
        j = i
        Do While j < N
            If k(j + 1) <> k(i) Then Exit Do
            j = j + 1
        Loop
        prom = (i + j) / 2
        For m = i To j
            rk(ix(m)) = prom
        Next m
        i = j + 1
    Loop
End Sub

Private Function Pearson(a() As Double, b() As Double, ByVal N As Long) As Double
    Dim i As Long, ma As Double, mb As Double
    Dim sab As Double, saa As Double, sbb As Double, da As Double, db As Double
    ma = EstMedia(a, N)
    mb = EstMedia(b, N)
    For i = 1 To N
        da = a(i) - ma
        db = b(i) - mb
        sab = sab + da * db
        saa = saa + da * da
        sbb = sbb + db * db
    Next i
    If saa <= 0 Or sbb <= 0 Then
        Pearson = 0
    Else
        Pearson = sab / Sqr(saa * sbb)
    End If
End Function

' Sensibilidad de cada riesgo en la dimension d. Resultado ordenado por |swing|.
Private Sub CalcularSensibilidad(ByVal d As Long, sens() As TSens, ByRef nS As Long)
    Dim tot() As Double, rkTot() As Double, ixTot() As Long, x() As Double, rk() As Double, ix() As Long
    Dim i As Long, r As Long, j As Long, a As Long, b As Long, nDec As Long
    Dim sumR2 As Double, sb As Double, sa As Double, mTot As Double
    Dim ord() As Long, clave() As Double, tmpI As Long, tmpK As Double, copia() As TSens

    nS = 0
    ReDim sens(1 To gNR)
    ColumnaTotal gTot, d, gN, tot
    RangosPromedio tot, gN, rkTot, ixTot
    mTot = EstMedia(tot, gN)
    nDec = gN \ 10
    If nDec < 1 Then nDec = 1
    For r = 1 To gNR
        If gDist(r, d) > 0 Then
            gRiesgoActual = r
            ColumnaRiesgo r, d, gN, x
            nS = nS + 1
            sens(nS).Idx = r
            sens(nS).MediaR = EstMedia(x, gN)
            RangosPromedio x, gN, rk, ix
            If x(ix(1)) < x(ix(gN)) Then
                sens(nS).Rho = Pearson(rk, rkTot, gN)
                sb = 0
                sa = 0
                For i = 1 To nDec
                    sb = sb + tot(ix(i))
                    sa = sa + tot(ix(gN - nDec + i))
                Next i
                sens(nS).BajoMedia = sb / nDec
                sens(nS).AltoMedia = sa / nDec
                sens(nS).Swing = sens(nS).AltoMedia - sens(nS).BajoMedia
            Else
                sens(nS).Rho = 0
                sens(nS).BajoMedia = mTot
                sens(nS).AltoMedia = mTot
                sens(nS).Swing = 0
            End If
            sumR2 = sumR2 + sens(nS).Rho * sens(nS).Rho
        End If
    Next r
    gRiesgoActual = 0
    If nS = 0 Then Exit Sub
    For j = 1 To nS
        If sumR2 > 0 Then sens(j).Contrib = sens(j).Rho * sens(j).Rho / sumR2
    Next j
    ' Orden por |swing| descendente sobre un vector de indices (sin copiar tipos completos)
    ReDim ord(1 To nS)
    ReDim clave(1 To nS)
    For j = 1 To nS
        ord(j) = j
        clave(j) = Abs(sens(j).Swing)
    Next j
    For a = 2 To nS
        tmpI = ord(a)
        tmpK = clave(a)
        b = a - 1
        Do While b >= 1
            If clave(b) >= tmpK Then Exit Do
            ord(b + 1) = ord(b)
            clave(b + 1) = clave(b)
            b = b - 1
        Loop
        ord(b + 1) = tmpI
        clave(b + 1) = tmpK
    Next a
    ReDim copia(1 To nS)
    For j = 1 To nS
        CopiarSens sens(ord(j)), copia(j)
    Next j
    For j = 1 To nS
        CopiarSens copia(j), sens(j)
    Next j
End Sub

Private Sub CopiarSens(src As TSens, dst As TSens)
    dst.Idx = src.Idx
    dst.MediaR = src.MediaR
    dst.Rho = src.Rho
    dst.Contrib = src.Contrib
    dst.BajoMedia = src.BajoMedia
    dst.AltoMedia = src.AltoMedia
    dst.Swing = src.Swing
End Sub


' ======================================================================
'  HOJAS DE SALIDA
' ======================================================================

Private Sub EscribirResultados()
    Dim ws As Worksheet, fila As Long, d As Long, k As Long, a() As Variant, s() As Double
    Dim pcts As Variant, p As Double, m As Double, sd As Double, pn As Double, rg As Double
    Dim vmeTot As Double, r As Long, se As Double, lo As Long, hi As Long, semi As Double
    Dim nCols As Long, nSug As Double, lineas As Variant

    Set ws = hjResultados
    PrepararHoja ws
    PonerTitulo ws, U("RESULTADOS \u2014 AN\u00C1LISIS CUANTITATIVO DE RIESGOS (MONTECARLO)"), _
        "Fecha: " & Format$(Now, "dd/mm/yyyy hh:mm") & "   |   Iteraciones: " & Format$(gN, "#,##0") & _
        "   |   Semilla: " & TextoSemilla() & "   |   Riesgos activos: " & gNR & _
        "   |   Estimados por validar: " & gNEstim & "   |   Pendientes: " & gNPend & _
        "   |   Nivel de confianza: " & Format$(gNivel, "0%"), 11

    ' --- Resumen ---
    fila = 5
    Seccion ws.Cells(fila, 2), U("1. RESUMEN POR DIMENSI\u00D3N")
    ws.Cells(fila + 1, 2).Resize(1, 10).Value = Array(U("DIMENSI\u00D3N"), "UNIDAD", U("BASE (l\u00EDnea base)"), _
        "MEDIA DEL IMPACTO", "P50 DEL IMPACTO", "P" & Format$(gNivel * 100, "0") & " DEL IMPACTO", _
        "RESERVA PARA CONTINGENCIAS", U("RESERVA DE GESTI\u00D3N"), "PRESUPUESTO RECOMENDADO", "% SOBRE LA BASE")
    Encabezado ws.Cells(fila + 1, 2).Resize(1, 10)
    ReDim a(1 To gND, 1 To 10)
    For d = 1 To gND
        Ordenados d, False, s
        m = EstMedia(s, gN)
        pn = Percentil(s, gN, gNivel * 100)
        rg = ReservaGestion(d)
        a(d, 1) = gD(d).Nombre
        a(d, 2) = gD(d).Unidad
        If gD(d).TieneBase Then a(d, 3) = gD(d).ValorBase Else a(d, 3) = "-"
        a(d, 4) = m
        a(d, 5) = Percentil(s, gN, 50)
        a(d, 6) = pn
        a(d, 7) = pn
        a(d, 8) = rg
        a(d, 9) = gD(d).ValorBase + pn + rg
        If gD(d).TieneBase Then a(d, 10) = (pn + rg) / gD(d).ValorBase Else a(d, 10) = "-"
    Next d
    ws.Cells(fila + 2, 2).Resize(gND, 10).Value = a
    Cuerpo ws.Cells(fila + 2, 2).Resize(gND, 10)
    For d = 1 To gND
        ws.Cells(fila + 1 + d, 4).Resize(1, 7).NumberFormat = gD(d).Formato
    Next d
    ws.Cells(fila + 2, 11).Resize(gND, 1).NumberFormat = "0.0%"
    Resaltar ws.Cells(fila + 2, 8).Resize(gND, 1), COLOR_P80
    fila = fila + 3 + gND
    NotaPie ws.Cells(fila, 2), U("Reserva para contingencias = P") & Format$(gNivel * 100, "0") & _
        U(" del impacto simulado (riesgos conocidos, PMI). Reserva de gesti\u00F3n = % de la base para trabajo no previsto; ") & _
        U("no se simula. Presupuesto recomendado = base + contingencia + gesti\u00F3n.")
    fila = fila + 2

    ' --- Bloques por dimension ---
    pcts = Array(0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100)
    For d = 1 To gND
        gDimActual = d
        Ordenados d, False, s
        m = EstMedia(s, gN)
        sd = EstDesv(s, gN, m)
        pn = Percentil(s, gN, gNivel * 100)
        Seccion ws.Cells(fila, 2), (d + 1) & ". " & UCase$(gD(d).Nombre) & " (" & gD(d).Unidad & ")"
        fila = fila + 1
        ' Percentiles
        If gD(d).TieneBase Then nCols = 3 Else nCols = 2
        ReDim a(1 To 1, 1 To nCols)
        a(1, 1) = "PERCENTIL"
        a(1, 2) = "IMPACTO (" & gD(d).Unidad & ")"
        If nCols = 3 Then a(1, 3) = "TOTAL = BASE + IMPACTO"
        ws.Cells(fila, 2).Resize(1, nCols).Value = a
        Encabezado ws.Cells(fila, 2).Resize(1, nCols)
        ReDim a(1 To 13, 1 To nCols)
        For k = 0 To 12
            p = pcts(k)
            a(k + 1, 1) = EtiquetaP(p)
            a(k + 1, 2) = Percentil(s, gN, p)
            If nCols = 3 Then a(k + 1, 3) = gD(d).ValorBase + a(k + 1, 2)
        Next k
        ws.Cells(fila + 1, 2).Resize(13, nCols).Value = a
        Cuerpo ws.Cells(fila + 1, 2).Resize(13, nCols)
        ws.Cells(fila + 1, 3).Resize(13, nCols - 1).NumberFormat = gD(d).Formato
        For k = 0 To 12
            Select Case pcts(k)
                Case 10: Resaltar ws.Cells(fila + 1 + k, 2).Resize(1, nCols), COLOR_P10
                Case 50: Resaltar ws.Cells(fila + 1 + k, 2).Resize(1, nCols), COLOR_P50
                Case 80: Resaltar ws.Cells(fila + 1 + k, 2).Resize(1, nCols), COLOR_P80
                Case 90: Resaltar ws.Cells(fila + 1 + k, 2).Resize(1, nCols), COLOR_P90
            End Select
        Next k

        ' Estadisticas, VME, reservas y precision (a la derecha)
        vmeTot = 0
        For r = 1 To gNR
            vmeTot = vmeTot + VME(r, d)
        Next r
        rg = ReservaGestion(d)
        se = sd / Sqr(gN)
        lo = Int(gN * gNivel - 1.96 * Sqr(gN * gNivel * (1 - gNivel)))
        hi = -Int(-(gN * gNivel + 1.96 * Sqr(gN * gNivel * (1 - gNivel))))
        If lo < 1 Then lo = 1
        If hi > gN Then hi = gN
        If pn <> 0 Then semi = (s(hi) - s(lo)) / 2 / Abs(pn) Else semi = 0
        If semi > 0 Then nSug = gN * (semi / 0.01) ^ 2 Else nSug = gN
        ReDim a(1 To 22, 1 To 2)
        a(1, 1) = U("ESTAD\u00CDSTICAS"): a(1, 2) = ""
        a(2, 1) = "Media (valor esperado)": a(2, 2) = m
        a(3, 1) = U("Desviaci\u00F3n est\u00E1ndar"): a(3, 2) = sd
        a(4, 1) = U("Coeficiente de variaci\u00F3n"): a(4, 2) = CoefVar(sd, m)
        a(5, 1) = U("M\u00EDnimo / M\u00E1ximo"): a(5, 2) = Format$(s(1), gD(d).Formato) & " / " & Format$(s(gN), gD(d).Formato)
        a(6, 1) = "Probabilidad de impacto = 0": a(6, 2) = FraccionCero(s, gN)
        a(7, 1) = U("VME total (\u03A3 p \u00D7 impacto medio)"): a(7, 2) = vmeTot
        a(8, 1) = U("Diferencia VME vs. media simulada"): a(8, 2) = DifRel(vmeTot, m)
        a(9, 1) = "RESERVAS (nivel " & Format$(gNivel, "0%") & ")": a(9, 2) = ""
        a(10, 1) = "a) Reserva para contingencias (P" & Format$(gNivel * 100, "0") & ")": a(10, 2) = pn
        a(11, 1) = "b) Presupuesto al valor esperado (base + media)": a(11, 2) = gD(d).ValorBase + m
        a(12, 1) = "b) Contingencia sobre el valor esperado (P" & Format$(gNivel * 100, "0") & U(" \u2212 media)"): a(12, 2) = pn - m
        a(13, 1) = U("c) Reserva de gesti\u00F3n (") & Format$(gResGestPct, "0.0%") & U(" \u00D7 base)"): a(13, 2) = rg
        a(14, 1) = "d) Presupuesto recomendado (base + a + c)": a(14, 2) = gD(d).ValorBase + pn + rg
        a(15, 1) = U("PRECISI\u00D3N DE LA SIMULACI\u00D3N"): a(15, 2) = ""
        a(16, 1) = U("Error est\u00E1ndar de la media"): a(16, 2) = se
        a(17, 1) = "IC 95% de la media": a(17, 2) = Format$(m - 1.96 * se, gD(d).Formato) & " a " & Format$(m + 1.96 * se, gD(d).Formato)
        a(18, 1) = "IC 95% del P" & Format$(gNivel * 100, "0"): a(18, 2) = Format$(s(lo), gD(d).Formato) & " a " & Format$(s(hi), gD(d).Formato)
        a(19, 1) = "Semiancho relativo del IC del P" & Format$(gNivel * 100, "0"): a(19, 2) = semi
        a(20, 1) = U("Iteraciones sugeridas para \u00B11%"): a(20, 2) = -Int(-nSug)
        a(21, 1) = U("Estado de la precisi\u00F3n")
        If semi <= 0.01 Then a(21, 2) = U("Suficiente (IC dentro de \u00B11%)") Else a(21, 2) = U("Aumente las iteraciones (IC mayor a \u00B11%)")
        a(22, 1) = U("Base de la dimensi\u00F3n")
        If gD(d).TieneBase Then a(22, 2) = gD(d).ValorBase Else a(22, 2) = U("sin base (solo impacto)")
        ws.Cells(fila, 7).Resize(22, 2).Value = a
        Cuerpo ws.Cells(fila, 7).Resize(22, 2)
        Encabezado ws.Cells(fila, 7).Resize(1, 2)
        Encabezado ws.Cells(fila + 8, 7).Resize(1, 2)
        Encabezado ws.Cells(fila + 14, 7).Resize(1, 2)
        ws.Cells(fila, 8).Resize(22, 1).NumberFormat = gD(d).Formato
        ws.Cells(fila + 3, 8).NumberFormat = "0.0%"
        ws.Cells(fila + 5, 8).NumberFormat = "0.0%"
        ws.Cells(fila + 7, 8).NumberFormat = "0.00%"
        ws.Cells(fila + 18, 8).NumberFormat = "0.00%"
        ws.Cells(fila + 19, 8).NumberFormat = "#,##0"
        ws.Cells(fila, 8).Resize(22, 1).HorizontalAlignment = xlRight
        Resaltar ws.Cells(fila + 9, 7).Resize(1, 2), COLOR_P80
        Resaltar ws.Cells(fila + 13, 7).Resize(1, 2), COLOR_P80
        If semi > 0.01 Then Resaltar ws.Cells(fila + 20, 7).Resize(1, 2), COLOR_ADVERTENCIA
        fila = fila + 24
    Next d
    gDimActual = 0

    ' --- Correlacion ---
    Seccion ws.Cells(fila, 2), (gND + 2) & U(". CORRELACI\u00D3N ENTRE RIESGOS (Iman\u2013Conover, un factor por grupo)")
    fila = fila + 1
    If gNG = 0 Then
        ws.Cells(fila, 2).Value = U("No hay grupos de correlaci\u00F3n: los riesgos se simulan de forma independiente.")
        fila = fila + 2
    Else
        ws.Cells(fila, 2).Resize(1, 5).Value = Array("GRUPO", U("N.\u00B0 DE RIESGOS"), "RHO OBJETIVO (rango)", _
            "RHO LOGRADA (promedio de pares)", "NOTA")
        Encabezado ws.Cells(fila, 2).Resize(1, 5)
        ReDim a(1 To gNG, 1 To 5)
        For k = 1 To gNG
            a(k, 1) = gGrupoNom(k)
            a(k, 2) = gGrupoN(k)
            a(k, 3) = gGrupoObj(k)
            a(k, 4) = gGrupoLog(k)
            If gGrupoN(k) < 2 Then
                a(k, 5) = U("Grupo de un solo riesgo: no hay con qui\u00E9n correlacionar.")
            Else
                a(k, 5) = U("Con probabilidad < 1 muchos valores son 0 (empates); la correlaci\u00F3n lograda resulta menor que la objetivo.")
            End If
        Next k
        ws.Cells(fila + 1, 2).Resize(gNG, 5).Value = a
        Cuerpo ws.Cells(fila + 1, 2).Resize(gNG, 5)
        ws.Cells(fila + 1, 4).Resize(gNG, 2).NumberFormat = "0.00"
        fila = fila + gNG + 2
    End If

    ' --- Advertencias ---
    Seccion ws.Cells(fila, 2), (gND + 3) & U(". ADVERTENCIAS DE LA VALIDACI\u00D3N")
    fila = fila + 1
    If gNAdv = 0 Then
        ws.Cells(fila, 2).Value = "Sin advertencias."
    Else
        lineas = Split(gAdvert, vbLf)
        For k = LBound(lineas) To UBound(lineas)
            If Len(lineas(k)) > 0 Then
                ws.Cells(fila, 2).Value = lineas(k)
                ws.Cells(fila, 2).Interior.Color = COLOR_ADVERTENCIA
                fila = fila + 1
            End If
        Next k
    End If

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 26
    ws.Columns("C:F").ColumnWidth = 18
    ws.Columns("G").ColumnWidth = 44
    ws.Columns("H:K").ColumnWidth = 22
End Sub

Private Function ReservaGestion(ByVal d As Long) As Double
    If gD(d).ReservaGestion And gD(d).TieneBase Then ReservaGestion = gResGestPct * gD(d).ValorBase
End Function

Private Sub EscribirCurvaS()
    Dim ws As Worksheet, fila As Long, d As Long, k As Long, a() As Variant, s() As Double
    Dim frec() As Long, mn As Double, ancho As Double, i As Long, c As Long, hay As Boolean

    Set ws = hjCurvaS
    PrepararHoja ws
    PonerTitulo ws, U("CURVA S \u2014 PROBABILIDAD ACUMULADA E HISTOGRAMAS"), _
        U("Probabilidad de que el impacto total sea menor o igual al valor indicado. Una secci\u00F3n por dimensi\u00F3n."), 16
    fila = 5
    For d = 1 To gND
        gDimActual = d
        Ordenados d, False, s
        hay = (s(gN) > s(1))
        Seccion ws.Cells(fila, 2), UCase$(gD(d).Nombre) & " (" & gD(d).Unidad & ")"
        ws.Cells(fila + 1, 2).Resize(1, 2).Value = Array("PROBABILIDAD ACUMULADA", "IMPACTO (" & gD(d).Unidad & ")")
        Encabezado ws.Cells(fila + 1, 2).Resize(1, 2)
        ReDim a(1 To 21, 1 To 2)
        For k = 0 To 20
            a(k + 1, 1) = k * 5 / 100
            a(k + 1, 2) = Percentil(s, gN, k * 5)
        Next k
        ws.Cells(fila + 2, 2).Resize(21, 2).Value = a
        Cuerpo ws.Cells(fila + 2, 2).Resize(21, 2)
        ws.Cells(fila + 2, 2).Resize(21, 1).NumberFormat = "0%"
        ws.Cells(fila + 2, 2).Resize(21, 1).HorizontalAlignment = xlCenter
        ws.Cells(fila + 2, 3).Resize(21, 1).NumberFormat = gD(d).Formato
        Resaltar ws.Cells(fila + 12, 2).Resize(1, 2), COLOR_P50
        Resaltar ws.Cells(fila + 18, 2).Resize(1, 2), COLOR_P80
        Resaltar ws.Cells(fila + 20, 2).Resize(1, 2), COLOR_P90

        ' Histograma
        ws.Cells(fila + 1, 5).Resize(1, 6).Value = Array("CLASE", "DESDE", "HASTA", "MARCA DE CLASE", "FRECUENCIA", "FRECUENCIA (%)")
        Encabezado ws.Cells(fila + 1, 5).Resize(1, 6)
        ReDim frec(1 To N_CLASES)
        mn = s(1)
        ancho = (s(gN) - s(1)) / N_CLASES
        For i = 1 To gN
            If ancho > 0 Then c = Int((s(i) - mn) / ancho) + 1 Else c = 1
            If c > N_CLASES Then c = N_CLASES
            If c < 1 Then c = 1
            frec(c) = frec(c) + 1
        Next i
        ReDim a(1 To N_CLASES, 1 To 6)
        For k = 1 To N_CLASES
            a(k, 1) = k
            a(k, 2) = mn + (k - 1) * ancho
            a(k, 3) = mn + k * ancho
            a(k, 4) = mn + (k - 0.5) * ancho
            a(k, 5) = frec(k)
            a(k, 6) = frec(k) / gN
        Next k
        ws.Cells(fila + 2, 5).Resize(N_CLASES, 6).Value = a
        Cuerpo ws.Cells(fila + 2, 5).Resize(N_CLASES, 6)
        ws.Cells(fila + 2, 5).Resize(N_CLASES, 1).HorizontalAlignment = xlCenter
        ws.Cells(fila + 2, 6).Resize(N_CLASES, 3).NumberFormat = gD(d).Formato
        ws.Cells(fila + 2, 9).Resize(N_CLASES, 1).NumberFormat = "#,##0"
        ws.Cells(fila + 2, 10).Resize(N_CLASES, 1).NumberFormat = "0.0%"

        If hay Then
            GraficoCurvaS ws, Array(ws.Cells(fila + 2, 3).Resize(21, 1)), Array(ws.Cells(fila + 2, 2).Resize(21, 1)), _
                Array(gD(d).Nombre), Array(gD(d).ColorSerie), U("Curva S \u2014 ") & gD(d).Nombre & " (" & gD(d).Unidad & ")", _
                gD(d).Nombre & " (" & gD(d).Unidad & ")", ws.Cells(fila, 12), _
                Percentil(s, gN, 50), Percentil(s, gN, gNivel * 100), gD(d).Formato, s(1), 480, 290
            GraficoHistograma ws, ws.Cells(fila + 2, 8).Resize(N_CLASES, 1), ws.Cells(fila + 2, 9).Resize(N_CLASES, 1), _
                U("Histograma \u2014 ") & gD(d).Nombre & " (" & gD(d).Unidad & ")", gD(d).ColorSerie, ws.Cells(fila, 21), gD(d).Formato
        Else
            ws.Cells(fila + 24, 2).Value = U("Sin variabilidad en esta dimensi\u00F3n: no se generan gr\u00E1ficos.")
        End If
        fila = fila + 26
    Next d
    gDimActual = 0
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B:C").ColumnWidth = 16
    ws.Columns("D").ColumnWidth = 3
    ws.Columns("E:J").ColumnWidth = 13
    ws.Columns("K").ColumnWidth = 3
End Sub

Private Sub EscribirTornado()
    Dim ws As Worksheet, fila As Long, d As Long
    Set ws = hjTornado
    PrepararHoja ws
    PonerTitulo ws, U("TORNADO \u2014 SENSIBILIDAD DEL TOTAL A CADA RIESGO"), _
        U("Orden: mayor swing primero. Spearman = correlaci\u00F3n de rangos riesgo vs. total. Swing = media del total con el ") & _
        U("riesgo en su 10% superior \u2212 media con el riesgo en su 10% inferior. Verde = 10% inferior, rojo = 10% superior."), 14
    fila = 5
    For d = 1 To gND
        gDimActual = d
        fila = BloqueTornado(ws, fila, d) + 2
    Next d
    gDimActual = 0
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 4
    ws.Columns("C").ColumnWidth = 7
    ws.Columns("D").ColumnWidth = 46
    ws.Columns("E").ColumnWidth = 13
    ws.Columns("F:M").ColumnWidth = 14
    ws.Columns("N").ColumnWidth = 3
End Sub

Private Function BloqueTornado(ByVal ws As Worksheet, ByVal fila As Long, ByVal d As Long) As Long
    Dim sens() As TSens, nS As Long, a() As Variant, k As Long, nChart As Long, mTot As Double
    Dim co As ChartObject, ultima As Long, tot() As Double

    Seccion ws.Cells(fila, 2), "TORNADO DE " & UCase$(gD(d).Nombre) & " (" & gD(d).Unidad & ")"
    CalcularSensibilidad d, sens, nS
    If nS = 0 Then
        ws.Cells(fila + 1, 2).Value = U("No hay riesgos activos con impacto en esta dimensi\u00F3n.")
        BloqueTornado = fila + 1
        Exit Function
    End If
    ColumnaTotal gTot, d, gN, tot
    mTot = EstMedia(tot, gN)
    ws.Cells(fila + 1, 2).Resize(1, 12).Value = Array("#", "ID", "RIESGO", "TIPO", "IMPACTO MEDIO" & vbLf & "del riesgo", _
        "SPEARMAN" & vbLf & "(rho)", U("CONTRIBUCI\u00D3N" & vbLf & "A LA VARIANZA"), "TOTAL MEDIO" & vbLf & "riesgo 10% inf.", _
        "TOTAL MEDIO" & vbLf & "riesgo 10% sup.", "SWING", U("\u0394 vs. media" & vbLf & "(10% inferior)"), U("\u0394 vs. media" & vbLf & "(10% superior)"))
    Encabezado ws.Cells(fila + 1, 2).Resize(1, 12)
    ReDim a(1 To nS, 1 To 12)
    nChart = 0
    For k = 1 To nS
        a(k, 1) = k
        a(k, 2) = gR(sens(k).Idx).Id
        a(k, 3) = gR(sens(k).Idx).Nombre
        a(k, 4) = gR(sens(k).Idx).Tipo
        a(k, 5) = sens(k).MediaR
        a(k, 6) = sens(k).Rho
        a(k, 7) = sens(k).Contrib
        a(k, 8) = sens(k).BajoMedia
        a(k, 9) = sens(k).AltoMedia
        a(k, 10) = sens(k).Swing
        a(k, 11) = sens(k).BajoMedia - mTot
        a(k, 12) = sens(k).AltoMedia - mTot
        If Abs(sens(k).Swing) > 0 Then nChart = k
    Next k
    ws.Cells(fila + 2, 2).Resize(nS, 12).Value = a
    Cuerpo ws.Cells(fila + 2, 2).Resize(nS, 12)
    ws.Cells(fila + 2, 4).Resize(nS, 1).WrapText = False
    ws.Cells(fila + 2, 2).Resize(nS, 2).HorizontalAlignment = xlCenter
    ws.Cells(fila + 2, 6).Resize(nS, 1).NumberFormat = gD(d).Formato
    ws.Cells(fila + 2, 7).Resize(nS, 1).NumberFormat = "0.00"
    ws.Cells(fila + 2, 8).Resize(nS, 1).NumberFormat = "0.0%"
    ws.Cells(fila + 2, 9).Resize(nS, 5).NumberFormat = gD(d).Formato
    For k = 1 To nS
        If gR(sens(k).Idx).Tipo = "OPORTUNIDAD" Then ws.Cells(fila + 1 + k, 5).Interior.Color = COLOR_OPORTUNIDAD
    Next k
    ultima = fila + 1 + nS
    If nChart > 0 And Not gSinGraficos Then
        Set co = GraficoTornado(ws, ws.Cells(fila + 2, 3).Resize(nChart, 1), ws.Cells(fila + 2, 12).Resize(nChart, 1), _
                                ws.Cells(fila + 2, 13).Resize(nChart, 1), U("Tornado \u2014 ") & gD(d).Nombre & " (" & gD(d).Unidad & ")", _
                                ws.Cells(fila, 15), nChart, gD(d).Formato)
        If Not co Is Nothing Then
            Do While ws.Cells(ultima, 1).Top < co.Top + co.Height
                ultima = ultima + 1
            Loop
        End If
    End If
    BloqueTornado = ultima
End Function

Private Sub EscribirRangos()
    Dim ws As Worksheet, a() As Variant, fmt() As String, nFil As Long, r As Long, d As Long, k As Long
    Dim x() As Double, s() As Double, vmeTot As Double

    Set ws = hjRangos
    PrepararHoja ws
    PonerTitulo ws, U("TABLA DE RANGOS POR RIESGO Y DIMENSI\u00D3N"), _
        U("Estad\u00EDsticos sobre las ") & Format$(gN, "#,##0") & U(" iteraciones (incluye los escenarios en que el riesgo no ocurre, con impacto 0). ") & _
        U("VME = probabilidad \u00D7 impacto medio te\u00F3rico (negativo en oportunidades)."), 16
    ws.Range("B4").Resize(1, 16).Value = Array("ID", "RIESGO", "TIPO", U("DIMENSI\u00D3N"), "UNIDAD", "PROBABILIDAD" & vbLf & "(dato)", _
        "FRECUENCIA" & vbLf & "OBSERVADA", U("M\u00CDNIMO"), "P10", "P25", "P50", "P75", "P90", U("M\u00C1XIMO"), "PROMEDIO", "VME")
    Encabezado ws.Range("B4").Resize(1, 16)
    ws.Rows(4).RowHeight = 32

    nFil = gND
    For r = 1 To gNR
        For d = 1 To gND
            If gDist(r, d) > 0 Then nFil = nFil + 1
        Next d
    Next r
    ReDim a(1 To nFil, 1 To 16)
    ReDim fmt(1 To nFil)
    k = 0
    For r = 1 To gNR
        gRiesgoActual = r
        For d = 1 To gND
            If gDist(r, d) > 0 Then
                k = k + 1
                ColumnaRiesgo r, d, gN, x
                QuickSort x, 1, gN
                a(k, 1) = gR(r).Id
                a(k, 2) = gR(r).Nombre
                a(k, 3) = gR(r).Tipo
                a(k, 4) = gD(d).Nombre
                a(k, 5) = gD(d).Unidad
                a(k, 6) = gR(r).Prob
                a(k, 7) = gOcc(r) / gN
                LlenarEstadisticos a, k, x
                a(k, 16) = VME(r, d)
                fmt(k) = gD(d).Formato
            End If
        Next d
    Next r
    gRiesgoActual = 0
    For d = 1 To gND
        k = k + 1
        Ordenados d, False, s
        vmeTot = 0
        For r = 1 To gNR
            vmeTot = vmeTot + VME(r, d)
        Next r
        a(k, 1) = "TOTAL"
        a(k, 2) = "TOTAL " & UCase$(gD(d).Nombre)
        a(k, 3) = "-"
        a(k, 4) = gD(d).Nombre
        a(k, 5) = gD(d).Unidad
        a(k, 6) = "-"
        a(k, 7) = 1 - FraccionCero(s, gN)
        LlenarEstadisticos a, k, s
        a(k, 16) = vmeTot
        fmt(k) = gD(d).Formato
    Next d
    ws.Range("B5").Resize(nFil, 16).Value = a
    Cuerpo ws.Range("B5").Resize(nFil, 16)
    ws.Range("C5").Resize(nFil, 1).WrapText = False
    ws.Range("B5").Resize(nFil, 1).HorizontalAlignment = xlCenter
    ws.Range("G5").Resize(nFil, 2).NumberFormat = "0.0%"
    ws.Range("G5").Resize(nFil, 2).HorizontalAlignment = xlCenter
    For k = 1 To nFil
        ws.Range("I5").Offset(k - 1, 0).Resize(1, 9).NumberFormat = fmt(k)
        If a(k, 3) = "OPORTUNIDAD" Then ws.Range("D5").Offset(k - 1, 0).Interior.Color = COLOR_OPORTUNIDAD
    Next k
    Resaltar ws.Range("B5").Offset(nFil - gND, 0).Resize(gND, 16), COLOR_P50
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 8
    ws.Columns("C").ColumnWidth = 50
    ws.Columns("D:H").ColumnWidth = 13
    ws.Columns("I:Q").ColumnWidth = 13
End Sub

Private Sub LlenarEstadisticos(a() As Variant, ByVal k As Long, s() As Double)
    a(k, 8) = s(1)
    a(k, 9) = Percentil(s, gN, 10)
    a(k, 10) = Percentil(s, gN, 25)
    a(k, 11) = Percentil(s, gN, 50)
    a(k, 12) = Percentil(s, gN, 75)
    a(k, 13) = Percentil(s, gN, 90)
    a(k, 14) = s(gN)
    a(k, 15) = EstMedia(s, gN)
End Sub

Private Sub EscribirMatriz()
    Dim ws As Worksheet, e As Variant, datos As Variant
    Dim nNiv As Long, cProb As Long, cDesc As Long, cImp() As Long, d As Long, r As Long, k As Long
    Dim nivP() As Long, nivI() As Long, nivG() As Long, nivD() As Long, fila As Long, a() As Variant, desc() As String
    Dim impMed As Double

    Set ws = hjMatriz
    PrepararHoja ws
    PonerTitulo ws, U("MATRIZ PROBABILIDAD\u2013IMPACTO (5\u00D75)"), _
        U("Nivel de probabilidad seg\u00FAn PROB_MAX y nivel de impacto seg\u00FAn IMP_<DIMENSI\u00D3N> de tblEscalas (impacto medio si ocurre). ") & _
        U("La matriz general usa el mayor nivel de impacto entre las dimensiones. Puntaje = nivel P \u00D7 nivel I: ") & _
        U("verde \u2264 4, \u00E1mbar 5\u201312, rojo \u2265 15. (O) = oportunidad."), 14

    If gCuerpoEsc Is Nothing Or gEncEsc Is Nothing Then
        ws.Range("B5").Value = U("tblEscalas no tiene filas: no se puede generar la matriz.")
        Exit Sub
    End If
    e = gEncEsc.Value
    datos = gCuerpoEsc.Value
    nNiv = UBound(datos, 1)
    If nNiv > 5 Then nNiv = 5
    cProb = ColEnc(e, "PROB_MAX")
    cDesc = ColEnc(e, "DESCRIPCION")
    If cProb = 0 Then
        ws.Range("B5").Value = "tblEscalas no tiene la columna PROB_MAX."
        Exit Sub
    End If
    ReDim desc(1 To 5)
    For k = 1 To 5
        desc(k) = CStr(k)
        If cDesc > 0 And k <= nNiv Then desc(k) = k & " " & Txt(datos(k, cDesc))
    Next k
    ReDim cImp(1 To gND)
    For d = 1 To gND
        cImp(d) = ColEnc(e, "IMP_" & gD(d).Clave)
    Next d

    ReDim nivP(1 To gNR)
    ReDim nivI(1 To gNR, 1 To gND)
    ReDim nivG(1 To gNR)
    For r = 1 To gNR
        nivP(r) = NivelEscala(gR(r).Prob, datos, cProb, nNiv)
        For d = 1 To gND
            If gDist(r, d) > 0 And cImp(d) > 0 Then
                impMed = Abs(ImpactoMedioCondicional(r, d))
                nivI(r, d) = NivelEscala(impMed, datos, cImp(d), nNiv)
                If nivI(r, d) > nivG(r) Then nivG(r) = nivI(r, d)
            End If
        Next d
    Next r

    ' Tabla de clasificacion
    fila = 5
    Seccion ws.Cells(fila, 2), U("CLASIFICACI\u00D3N DE LOS RIESGOS")
    fila = fila + 1
    ReDim a(1 To 1, 1 To 5 + 2 * gND)
    a(1, 1) = "ID": a(1, 2) = "RIESGO": a(1, 3) = "PROBABILIDAD": a(1, 4) = "NIVEL P"
    For d = 1 To gND
        a(1, 4 + 2 * d - 1) = "IMPACTO MEDIO " & UCase$(gD(d).Clave)
        a(1, 4 + 2 * d) = "NIVEL I " & UCase$(gD(d).Clave)
    Next d
    a(1, 5 + 2 * gND) = "NIVEL GENERAL / PUNTAJE"
    ws.Cells(fila, 2).Resize(1, 5 + 2 * gND).Value = a
    Encabezado ws.Cells(fila, 2).Resize(1, 5 + 2 * gND)
    ReDim a(1 To gNR, 1 To 5 + 2 * gND)
    For r = 1 To gNR
        a(r, 1) = gR(r).Id
        a(r, 2) = gR(r).Nombre
        a(r, 3) = gR(r).Prob
        a(r, 4) = nivP(r)
        For d = 1 To gND
            If gDist(r, d) > 0 Then
                a(r, 4 + 2 * d - 1) = gR(r).Signo * ImpactoMedioCondicional(r, d)
                If nivI(r, d) > 0 Then a(r, 4 + 2 * d) = nivI(r, d) Else a(r, 4 + 2 * d) = "-"
            Else
                a(r, 4 + 2 * d - 1) = "-"
                a(r, 4 + 2 * d) = "-"
            End If
        Next d
        a(r, 5 + 2 * gND) = nivG(r) & " / " & nivP(r) * nivG(r)
    Next r
    ws.Cells(fila + 1, 2).Resize(gNR, 5 + 2 * gND).Value = a
    Cuerpo ws.Cells(fila + 1, 2).Resize(gNR, 5 + 2 * gND)
    ws.Cells(fila + 1, 3).Resize(gNR, 1).WrapText = False
    ws.Cells(fila + 1, 4).Resize(gNR, 1).NumberFormat = "0%"
    For d = 1 To gND
        ws.Cells(fila + 1, 5 + 2 * d - 1).Resize(gNR, 1).NumberFormat = gD(d).Formato
    Next d
    For r = 1 To gNR
        ws.Cells(fila + r, 6 + 2 * gND).Interior.Color = ColorPuntaje(nivP(r) * nivG(r))
    Next r
    fila = fila + gNR + 3

    ' Matriz general y por dimension
    fila = BloqueMatriz(ws, fila, U("MATRIZ GENERAL (mayor nivel de impacto)"), nivP, nivG, desc)
    ReDim nivD(1 To gNR)
    For d = 1 To gND
        If cImp(d) > 0 Then
            For r = 1 To gNR
                nivD(r) = nivI(r, d)
            Next r
            fila = BloqueMatriz(ws, fila, U("MATRIZ DE ") & UCase$(gD(d).Nombre), nivP, nivD, desc)
        End If
    Next d
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 22
    ws.Columns("C").ColumnWidth = 40
    ws.Columns("D:G").ColumnWidth = 22
    ws.Range("H1").Resize(1, 2 * gND).EntireColumn.ColumnWidth = 14
End Sub

Private Function BloqueMatriz(ByVal ws As Worksheet, ByVal fila As Long, ByVal titulo As String, nivP() As Long, _
                              nivI() As Long, desc() As String) As Long
    Dim cp As Long, ci As Long, r As Long, texto As String, n As Long, celda As Range
    Seccion ws.Cells(fila, 2), titulo
    ws.Cells(fila + 1, 2).Value = U("PROBABILIDAD \ IMPACTO")
    For ci = 1 To 5
        ws.Cells(fila + 1, 2 + ci).Value = desc(ci)
    Next ci
    Encabezado ws.Cells(fila + 1, 2).Resize(1, 6)
    For cp = 5 To 1 Step -1
        Set celda = ws.Cells(fila + 2 + (5 - cp), 2)
        celda.Value = desc(cp)
        Encabezado celda
        For ci = 1 To 5
            texto = ""
            n = 0
            For r = 1 To gNR
                If nivP(r) = cp And nivI(r) = ci Then
                    n = n + 1
                    texto = texto & gR(r).Id
                    If gR(r).Tipo = "OPORTUNIDAD" Then texto = texto & "(O)"
                    texto = texto & ", "
                End If
            Next r
            Set celda = ws.Cells(fila + 2 + (5 - cp), 2 + ci)
            If n > 0 Then
                celda.Value = n & ": " & Left$(texto, Len(texto) - 2)
            Else
                celda.Value = "-"
            End If
            celda.Interior.Color = ColorPuntaje(cp * ci)
            celda.Font.Color = COLOR_TEXTO
            celda.WrapText = True
            celda.VerticalAlignment = xlTop
            celda.Borders.LineStyle = xlContinuous
            celda.Borders.Color = COLOR_BORDE
        Next ci
        ws.Rows(fila + 2 + (5 - cp)).RowHeight = 45
    Next cp
    BloqueMatriz = fila + 9
End Function

Private Function NivelEscala(ByVal v As Double, datos As Variant, ByVal c As Long, ByVal nNiv As Long) As Long
    Dim k As Long
    For k = 1 To nNiv
        If Not EsNum(datos(k, c)) Then
            NivelEscala = k
            Exit Function
        ElseIf v <= CDbl(datos(k, c)) Then
            NivelEscala = k
            Exit Function
        End If
    Next k
    NivelEscala = nNiv
End Function

Private Function ColorPuntaje(ByVal puntaje As Long) As Long
    If puntaje <= 4 Then
        ColorPuntaje = COLOR_MATRIZ_BAJO
    ElseIf puntaje <= 12 Then
        ColorPuntaje = COLOR_MATRIZ_MEDIO
    Else
        ColorPuntaje = COLOR_MATRIZ_ALTO
    End If
End Function

Private Sub EscribirComparacion()
    Dim ws As Worksheet, fila As Long, d As Long, k As Long, a() As Variant, s() As Double, sd() As Double
    Dim pcts As Variant, etiquetas As Variant, va As Double, vd As Double, r As Long, n As Long
    Dim rngX As Range, rngXD As Range, rngY As Range, xMin As Double

    Set ws = hjComparacion
    PrepararHoja ws
    PonerTitulo ws, U("COMPARACI\u00D3N ANTES / DESPU\u00C9S DE LAS RESPUESTAS"), _
        U("Ambos escenarios usan los mismos n\u00FAmeros aleatorios. Despu\u00E9s = PROB_RESIDUAL y FACTOR_IMPACTO_RESIDUAL; ") & _
        U("en COSTO se suma COSTO_RESPUESTA. Beneficio neto = reserva antes \u2212 reserva despu\u00E9s (ya incluye el costo de las respuestas)."), 12
    If Not gHayDespues Then
        ws.Range("B5").Value = U("No hay respuestas registradas: complete PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL o COSTO_RESPUESTA ") & _
                               U("en tblRiesgos para comparar el antes y el despu\u00E9s.")
        Exit Sub
    End If
    n = 0
    For r = 1 To gNR
        If gR(r).TieneRespuesta Then n = n + 1
    Next r
    ws.Range("B4").Value = U("Riesgos con respuesta registrada: ") & n & U("   |   Costo total de las respuestas: S/ ") & Format$(gCostoRespTotal, "#,##0")
    fila = 6
    pcts = Array(10, 50, 80, 90, gNivel * 100)
    etiquetas = Array("P10", "P50", "P80", "P90", "P" & Format$(gNivel * 100, "0") & " (nivel elegido)")
    For d = 1 To gND
        gDimActual = d
        Ordenados d, False, s
        Ordenados d, True, sd
        Seccion ws.Cells(fila, 2), UCase$(gD(d).Nombre) & " (" & gD(d).Unidad & ")"
        ws.Cells(fila + 1, 2).Resize(1, 4).Value = Array(U("M\u00C9TRICA"), "ANTES", U("DESPU\u00C9S"), U("DIFERENCIA (antes \u2212 despu\u00E9s)"))
        Encabezado ws.Cells(fila + 1, 2).Resize(1, 4)
        ReDim a(1 To 9, 1 To 4)
        For k = 0 To 4
            va = Percentil(s, gN, pcts(k))
            vd = Percentil(sd, gN, pcts(k))
            a(k + 1, 1) = etiquetas(k)
            a(k + 1, 2) = va
            a(k + 1, 3) = vd
            a(k + 1, 4) = va - vd
        Next k
        a(6, 1) = "Media"
        a(6, 2) = EstMedia(s, gN)
        a(6, 3) = EstMedia(sd, gN)
        a(6, 4) = a(6, 2) - a(6, 3)
        va = Percentil(s, gN, gNivel * 100)
        vd = Percentil(sd, gN, gNivel * 100)
        If d = gDimCosto Then
            a(7, 1) = U("Costo de las respuestas (incluido en DESPU\u00C9S)"): a(7, 2) = "-": a(7, 3) = gCostoRespTotal: a(7, 4) = "-"
            a(8, 1) = U("Reducci\u00F3n bruta de la reserva (sin costo de respuestas)"): a(8, 2) = "-": a(8, 3) = "-"
            a(8, 4) = va - (vd - gCostoRespTotal)
        Else
            a(7, 1) = "-": a(7, 2) = "-": a(7, 3) = "-": a(7, 4) = "-"
            a(8, 1) = "-": a(8, 2) = "-": a(8, 3) = "-": a(8, 4) = "-"
        End If
        a(9, 1) = "BENEFICIO NETO (reserva P" & Format$(gNivel * 100, "0") & U(" antes \u2212 despu\u00E9s)")
        a(9, 2) = va
        a(9, 3) = vd
        a(9, 4) = va - vd
        ws.Cells(fila + 2, 2).Resize(9, 4).Value = a
        Cuerpo ws.Cells(fila + 2, 2).Resize(9, 4)
        ws.Cells(fila + 2, 3).Resize(9, 3).NumberFormat = gD(d).Formato
        ws.Cells(fila + 2, 3).Resize(9, 3).HorizontalAlignment = xlRight
        Resaltar ws.Cells(fila + 10, 2).Resize(1, 4), COLOR_P80

        ' Tabla para la curva S superpuesta
        ws.Cells(fila + 1, 7).Resize(1, 3).Value = Array("PROBABILIDAD", "ANTES", U("DESPU\u00C9S"))
        Encabezado ws.Cells(fila + 1, 7).Resize(1, 3)
        ReDim a(1 To 21, 1 To 3)
        For k = 0 To 20
            a(k + 1, 1) = k * 5 / 100
            a(k + 1, 2) = Percentil(s, gN, k * 5)
            a(k + 1, 3) = Percentil(sd, gN, k * 5)
        Next k
        ws.Cells(fila + 2, 7).Resize(21, 3).Value = a
        Cuerpo ws.Cells(fila + 2, 7).Resize(21, 3)
        ws.Cells(fila + 2, 7).Resize(21, 1).NumberFormat = "0%"
        ws.Cells(fila + 2, 8).Resize(21, 2).NumberFormat = gD(d).Formato
        If s(gN) > s(1) Or sd(gN) > sd(1) Then
            Set rngY = ws.Cells(fila + 2, 7).Resize(21, 1)
            Set rngX = ws.Cells(fila + 2, 8).Resize(21, 1)
            Set rngXD = ws.Cells(fila + 2, 9).Resize(21, 1)
            If s(1) < sd(1) Then xMin = s(1) Else xMin = sd(1)
            GraficoCurvaS ws, Array(rngX, rngXD), Array(rngY, rngY), Array("Antes", U("Despu\u00E9s")), _
                Array(gD(d).ColorSerie, COLOR_DESPUES), U("Antes vs. despu\u00E9s \u2014 ") & gD(d).Nombre & " (" & gD(d).Unidad & ")", _
                gD(d).Nombre & " (" & gD(d).Unidad & ")", ws.Cells(fila, 11), Percentil(s, gN, 50), _
                Percentil(s, gN, gNivel * 100), gD(d).Formato, xMin, 480, 290
        End If
        fila = fila + 25
    Next d
    gDimActual = 0
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 52
    ws.Columns("C:E").ColumnWidth = 18
    ws.Columns("F").ColumnWidth = 3
    ws.Columns("G:I").ColumnWidth = 15
    ws.Columns("J").ColumnWidth = 3
End Sub

Private Sub EscribirSimulacion()
    Dim ws As Worksheet, h() As Variant, a() As Variant, fmt() As String
    Dim nShow As Long, nCol As Long, col As Long, i As Long, r As Long, d As Long

    Set ws = hjSimulacion
    PrepararHoja ws
    nShow = gN
    If nShow > MAX_FILAS_SIM Then nShow = MAX_FILAS_SIM
    PonerTitulo ws, U("SIMULACI\u00D3N \u2014 PRIMERAS ") & Format$(nShow, "#,##0") & " ITERACIONES", _
        U("Totales por dimensi\u00F3n y el impacto de cada riesgo en cada iteraci\u00F3n (escenario antes de las respuestas)."), 12
    nCol = 1 + gND
    For r = 1 To gNR
        For d = 1 To gND
            If gDist(r, d) > 0 Then nCol = nCol + 1
        Next d
    Next r
    ReDim h(1 To 1, 1 To nCol)
    ReDim fmt(1 To nCol)
    ReDim a(1 To nShow, 1 To nCol)
    h(1, 1) = "ITER"
    fmt(1) = "0"
    For i = 1 To nShow
        a(i, 1) = i
    Next i
    For d = 1 To gND
        h(1, 1 + d) = "TOTAL " & UCase$(gD(d).Clave) & " (" & gD(d).Unidad & ")"
        fmt(1 + d) = gD(d).Formato
        For i = 1 To nShow
            a(i, 1 + d) = gTot(i, d)
        Next i
    Next d
    col = 1 + gND
    For r = 1 To gNR
        For d = 1 To gND
            If gDist(r, d) > 0 Then
                col = col + 1
                h(1, col) = gR(r).Id & " " & gD(d).Clave
                fmt(col) = gD(d).Formato
                For i = 1 To nShow
                    a(i, col) = gM(i, r, d)
                Next i
            End If
        Next d
    Next r
    ws.Range("B4").Resize(1, nCol).Value = h
    Encabezado ws.Range("B4").Resize(1, nCol)
    ws.Rows(4).RowHeight = 32
    ws.Range("B5").Resize(nShow, nCol).Value = a
    With ws.Range("B5").Resize(nShow, nCol)
        .Borders.LineStyle = xlContinuous
        .Borders.Color = COLOR_BORDE
    End With
    For col = 1 To nCol
        ws.Range("B5").Offset(0, col - 1).Resize(nShow, 1).NumberFormat = fmt(col)
    Next col
    ws.Range("B5").Resize(nShow, 1).HorizontalAlignment = xlCenter
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 8
    ws.Range("C1").Resize(1, nCol - 1).EntireColumn.ColumnWidth = 14
End Sub


' ======================================================================
'  GRAFICOS
' ======================================================================

' Curva S (una o varias series) con lineas de referencia P50 y nivel elegido.
Private Sub GraficoCurvaS(ByVal ws As Worksheet, rangosX As Variant, rangosY As Variant, nombres As Variant, _
                          colores As Variant, ByVal titulo As String, ByVal ejeX As String, ByVal pos As Range, _
                          ByVal v50 As Double, ByVal vNivel As Double, ByVal fmt As String, ByVal vMin As Double, _
                          ByVal ancho As Double, ByVal alto As Double)
    Dim co As ChartObject, ch As Chart, s As Series, k As Long, nSeries As Long
    Dim rX As Range, rY As Range, aux As Range
    If gSinGraficos Then Exit Sub
    On Error GoTo EH
    gPasoGrafico = "crear el objeto"
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, ancho, alto)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    For k = LBound(rangosX) To UBound(rangosX)
        gPasoGrafico = "agregar la serie " & (k - LBound(rangosX) + 1)
        Set rX = rangosX(k)
        Set rY = rangosY(k)
        Set s = ch.SeriesCollection.NewSeries
        s.XValues = RefRango(rX)
        s.Values = RefRango(rY)
        s.Name = CStr(nombres(k))
    Next k
    nSeries = ch.SeriesCollection.Count
    gPasoGrafico = "tipo de grafico"
    ch.ChartType = xlXYScatterSmoothNoMarkers
    gPasoGrafico = "color de las series"
    For k = 1 To nSeries
        ch.SeriesCollection(k).Format.Line.ForeColor.RGB = CLng(colores(k - 1 + LBound(colores)))
        ch.SeriesCollection(k).Format.Line.Weight = 2.25
    Next k
    ' Datos de las lineas de referencia en celdas auxiliares (a la derecha de la hoja)
    Set aux = ws.Cells(pos.Row, COL_AUX_GRAFICOS)
    LineaReferencia ch, aux, v50, 0.5, "P50", fmt, vMin, COLOR_REF_P50
    LineaReferencia ch, aux.Offset(0, 2), vNivel, gNivel, "P" & Format$(gNivel * 100, "0"), fmt, vMin, COLOR_REF_NIVEL
    gPasoGrafico = "titulo y leyenda"
    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.ChartTitle.Font.Bold = True
    If nSeries > 1 Then
        ch.HasLegend = True
        ch.Legend.Position = xlLegendPositionBottom
        ' Quitar de la leyenda las dos lineas de referencia
        On Error Resume Next
        ch.Legend.LegendEntries(ch.Legend.LegendEntries.Count).Delete
        ch.Legend.LegendEntries(ch.Legend.LegendEntries.Count).Delete
        On Error GoTo EH
    Else
        ch.HasLegend = False
    End If
    gPasoGrafico = "ejes"
    With ch.Axes(xlValue)
        .MinimumScale = 0
        .MaximumScale = 1
        .MajorUnit = 0.1
        .TickLabels.NumberFormat = "0%"
        .HasTitle = True
        .AxisTitle.Text = "Probabilidad acumulada"
    End With
    With ch.Axes(xlCategory)
        .HasTitle = True
        .AxisTitle.Text = ejeX
        .TickLabels.NumberFormat = fmt
    End With
    Exit Sub
EH:
    FalloGrafico co, pos, titulo, Err.Number, Err.Description
End Sub

Private Sub LineaReferencia(ByVal ch As Chart, ByVal aux As Range, ByVal x As Double, ByVal y As Double, _
                            ByVal etiqueta As String, ByVal fmt As String, ByVal xMin As Double, ByVal color As Long)
    Dim s As Series, a(1 To 4, 1 To 2) As Variant
    gPasoGrafico = "linea de referencia " & etiqueta
    a(1, 1) = etiqueta & " (x)"
    a(1, 2) = etiqueta & " (y)"
    a(2, 1) = xMin: a(2, 2) = y
    a(3, 1) = x:    a(3, 2) = y
    a(4, 1) = x:    a(4, 2) = 0
    aux.Resize(4, 2).Value = a
    aux.Resize(4, 2).Font.Color = COLOR_SUBTITULO
    aux.Resize(4, 2).Font.Size = 8
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = RefRango(aux.Offset(1, 0).Resize(3, 1))
    s.Values = RefRango(aux.Offset(1, 1).Resize(3, 1))
    s.Name = etiqueta
    s.ChartType = xlXYScatterLinesNoMarkers
    s.Format.Line.ForeColor.RGB = color
    s.Format.Line.Weight = 1.25
    s.Format.Line.DashStyle = 4   ' msoLineDash
    s.Points(2).HasDataLabel = True
    s.Points(2).DataLabel.Text = etiqueta & ": " & Format$(x, fmt)
    s.Points(2).DataLabel.Position = xlLabelPositionRight
    s.Points(2).DataLabel.Font.Size = 9
    s.Points(2).DataLabel.Font.Bold = True
End Sub

Private Sub GraficoHistograma(ByVal ws As Worksheet, ByVal rCat As Range, ByVal rVal As Range, ByVal titulo As String, _
                              ByVal color As Long, ByVal pos As Range, ByVal fmt As String)
    Dim co As ChartObject, ch As Chart, s As Series
    If gSinGraficos Then Exit Sub
    On Error GoTo EH
    gPasoGrafico = "crear el objeto"
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, 480, 290)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    gPasoGrafico = "agregar la serie"
    Set s = ch.SeriesCollection.NewSeries
    s.Values = RefRango(rVal)
    s.XValues = RefRango(rCat)
    s.Name = "Frecuencia"
    gPasoGrafico = "tipo y formato"
    ch.ChartType = xlColumnClustered
    ch.SeriesCollection(1).Format.Fill.ForeColor.RGB = color
    ch.ChartGroups(1).GapWidth = 10
    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.ChartTitle.Font.Bold = True
    ch.HasLegend = False
    gPasoGrafico = "ejes"
    ch.Axes(xlCategory).TickLabels.NumberFormat = fmt
    ch.Axes(xlValue).HasTitle = True
    ch.Axes(xlValue).AxisTitle.Text = "Frecuencia (iteraciones)"
    Exit Sub
EH:
    FalloGrafico co, pos, titulo, Err.Number, Err.Description
End Sub

Private Function GraficoTornado(ByVal ws As Worksheet, ByVal rCat As Range, ByVal rInf As Range, ByVal rSup As Range, _
                                ByVal titulo As String, ByVal pos As Range, ByVal nBarras As Long, _
                                ByVal fmt As String) As ChartObject
    Dim co As ChartObject, ch As Chart, s As Series
    On Error GoTo EH
    gPasoGrafico = "crear el objeto"
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, 560, 110 + 24 * nBarras)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    gPasoGrafico = "agregar las series"
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = RefRango(rCat)
    s.Values = RefRango(rInf)
    s.Name = "Riesgo en su 10% inferior"
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = RefRango(rCat)
    s.Values = RefRango(rSup)
    s.Name = "Riesgo en su 10% superior"
    gPasoGrafico = "tipo y formato"
    ch.ChartType = xlBarClustered
    ch.SeriesCollection(1).Format.Fill.ForeColor.RGB = COLOR_TORNADO_BAJO
    ch.SeriesCollection(2).Format.Fill.ForeColor.RGB = COLOR_TORNADO_ALTO
    ch.ChartGroups(1).Overlap = 100
    ch.ChartGroups(1).GapWidth = 40
    gPasoGrafico = "ejes"
    With ch.Axes(xlCategory)
        .ReversePlotOrder = True
        .TickLabelPosition = xlTickLabelPositionLow
        .Crosses = xlMaximum
    End With
    With ch.Axes(xlValue)
        .TickLabels.NumberFormat = fmt
        .HasTitle = True
        .AxisTitle.Text = U("Variaci\u00F3n del total respecto de su media")
    End With
    gPasoGrafico = "titulo y leyenda"
    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.ChartTitle.Font.Bold = True
    ch.HasLegend = True
    ch.Legend.Position = xlLegendPositionBottom
    Set GraficoTornado = co
    Exit Function
EH:
    FalloGrafico co, pos, titulo, Err.Number, Err.Description
    Set GraficoTornado = Nothing
End Function

' Referencia de rango en texto (='Hoja'!$A$1:$A$9): es la forma mas estable de enlazar una serie.
Private Function RefRango(ByVal r As Range) As String
    RefRango = "='" & Replace(r.Worksheet.Name, "'", "''") & "'!" & r.Address
End Function

' Si un grafico falla, se borra lo creado, se deja un aviso en la hoja y la simulacion continua.
Private Sub FalloGrafico(ByVal co As ChartObject, ByVal pos As Range, ByVal titulo As String, _
                         ByVal nErr As Long, ByVal desc As String)
    On Error Resume Next
    If Not co Is Nothing Then co.Delete
    pos.Value = U("No se pudo crear el gr\u00E1fico \u00AB") & titulo & U("\u00BB. Error ") & nErr & ": " & desc & _
                " (paso: " & gPasoGrafico & U("). Los datos de las tablas son v\u00E1lidos.")
    pos.Font.Bold = True
    pos.Font.Color = COLOR_TEXTO
    pos.Interior.Color = COLOR_ADVERTENCIA
    gNFallosGraf = gNFallosGraf + 1
    If Len(gPrimerFalloGraf) = 0 Then gPrimerFalloGraf = "Error " & nErr & ": " & desc & " (paso: " & gPasoGrafico & ")"
End Sub


' ======================================================================
'  UTILIDADES
' ======================================================================

' Convierte las secuencias \uXXXX en caracteres Unicode (permite codigo fuente ASCII).
Private Function U(ByVal s As String) As String
    Dim p As Long, res As String
    p = InStr(1, s, "\u", vbBinaryCompare)
    Do While p > 0
        res = res & Left$(s, p - 1) & ChrW$(CLng("&H" & Mid$(s, p + 2, 4)))
        s = Mid$(s, p + 6)
        p = InStr(1, s, "\u", vbBinaryCompare)
    Loop
    U = res & s
End Function

Private Function Titulo() As String
    Titulo = U("An\u00E1lisis de riesgos \u2014 Simulaci\u00F3n Montecarlo")
End Function

Private Function TextoSemilla() As String
    If gSemillaFija Then TextoSemilla = Format$(gSemilla, "0") Else TextoSemilla = "aleatoria"
End Function

Private Function Txt(ByVal v As Variant) As String
    If IsError(v) Then Exit Function
    If IsEmpty(v) Or IsNull(v) Then Exit Function
    Txt = Trim$(CStr(v))
End Function

Private Function EsNum(ByVal v As Variant) As Boolean
    If IsError(v) Then Exit Function
    If IsEmpty(v) Or IsNull(v) Then Exit Function
    If VarType(v) = vbBoolean Then Exit Function
    If VarType(v) = vbString Then
        If Len(Trim$(v)) = 0 Then Exit Function
    End If
    EsNum = IsNumeric(v)
End Function

Private Function ColorHex(ByVal s As String, ByVal defecto As Long) As Long
    s = Replace(Trim$(s), "#", "")
    If Len(s) <> 6 Then
        ColorHex = defecto
        Exit Function
    End If
    On Error GoTo Malo
    ColorHex = CLng("&H" & Mid$(s, 1, 2)) + 256& * CLng("&H" & Mid$(s, 3, 2)) + 65536 * CLng("&H" & Mid$(s, 5, 2))
    Exit Function
Malo:
    ColorHex = defecto
End Function

Private Function CoefVar(ByVal d As Double, ByVal m As Double) As Variant
    If m = 0 Then CoefVar = "-" Else CoefVar = d / Abs(m)
End Function

Private Function DifRel(ByVal a As Double, ByVal b As Double) As Variant
    If b = 0 Then DifRel = "-" Else DifRel = (a - b) / Abs(b)
End Function

Private Function EtiquetaP(ByVal p As Double) As String
    Select Case p
        Case 0: EtiquetaP = U("P0 (m\u00EDnimo)")
        Case 10: EtiquetaP = "P10 (optimista)"
        Case 50: EtiquetaP = "P50 (mediana)"
        Case 90: EtiquetaP = "P90 (conservador)"
        Case 100: EtiquetaP = U("P100 (m\u00E1ximo)")
        Case Else: EtiquetaP = "P" & Format$(p, "0")
    End Select
End Function

Private Sub Restaurar(ByVal calcPrev As Long)
    On Error Resume Next
    Application.StatusBar = False
    Application.Calculation = calcPrev
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

Private Sub PrepararHoja(ByVal ws As Worksheet)
    Do While ws.ChartObjects.Count > 0
        ws.ChartObjects(1).Delete
    Loop
    ws.Cells.Clear
    ws.Cells.Font.Name = "Calibri"
    ws.Cells.Font.Size = 10
    ws.Cells.RowHeight = 15
End Sub

' Banda de titulo negra con texto ambar en la fila 2 y subtitulo en la fila 3.
Private Sub PonerTitulo(ByVal ws As Worksheet, ByVal texto As String, ByVal subt As String, ByVal nCols As Long)
    ws.Range("B2").Resize(1, nCols).Interior.Color = COLOR_TITULO_FONDO
    With ws.Range("B2")
        .Value = texto
        .Font.Bold = True
        .Font.Size = 14
        .Font.Color = COLOR_TITULO_TEXTO
    End With
    ws.Rows(2).RowHeight = 26
    If Len(subt) > 0 Then
        With ws.Range("B3")
            .Value = subt
            .Font.Italic = True
            .Font.Color = COLOR_SUBTITULO
        End With
    End If
End Sub

Private Sub Seccion(ByVal c As Range, ByVal texto As String)
    c.Value = texto
    c.Font.Bold = True
    c.Font.Size = 11
    c.Font.Color = COLOR_TEXTO
End Sub

Private Sub NotaPie(ByVal c As Range, ByVal texto As String)
    c.Value = texto
    c.Font.Italic = True
    c.Font.Color = COLOR_SUBTITULO
End Sub

Private Sub Encabezado(ByVal rng As Range)
    With rng
        .Interior.Color = COLOR_ENCABEZADO
        .Font.Color = COLOR_ENCABEZADO_TEXTO
        .Font.Bold = True
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .WrapText = True
        .Borders.LineStyle = xlContinuous
        .Borders.Color = COLOR_BORDE
    End With
    If rng.Rows(1).RowHeight < 30 Then rng.Rows(1).RowHeight = 30
End Sub

Private Sub Cuerpo(ByVal rng As Range)
    Dim k As Long
    With rng
        .Interior.Color = COLOR_BLANCO
        .Font.Color = COLOR_TEXTO
        .Borders.LineStyle = xlContinuous
        .Borders.Color = COLOR_BORDE
        .VerticalAlignment = xlCenter
    End With
    For k = 2 To rng.Rows.Count Step 2
        rng.Rows(k).Interior.Color = COLOR_FILA_ALTERNA
    Next k
End Sub

Private Sub Resaltar(ByVal rng As Range, ByVal color As Long)
    rng.Interior.Color = color
    rng.Font.Color = COLOR_TEXTO
    rng.Font.Bold = True
End Sub

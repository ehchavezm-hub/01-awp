Attribute VB_Name = "MonteCarlo"
Option Explicit

' ======================================================================
'  SIMULACION MONTECARLO - ANALISIS CUANTITATIVO DE RIESGOS
'  Obras de construccion: impacto en COSTO (S/) y en PLAZO (dias)
'
'  Macros asignadas a los botones de la hoja PARAMETROS:
'    RunMonteCarlo  - valida, simula y genera todas las hojas de salida
'    ValidarDatos   - valida tblRiesgos y marca en rojo las celdas con error
'    ClearResults   - limpia las hojas de salida (no las elimina)
'
'  Hojas referenciadas por CodeName: shInicio, shParam, shRes, shCurva,
'  shTornado, shRangos, shSim.
'
'  El codigo fuente es 100% ASCII a proposito (el proyecto VBA usa la
'  pagina de codigos 1252). Los textos con tildes se generan con
'  U("...\u00F3...") que convierte las secuencias \uXXXX con ChrW().
' ======================================================================

' ---------------- Constantes ----------------
Private Const MAX_RIESGOS As Long = 50
Private Const MIN_ITER As Long = 1000
Private Const MAX_ITER As Long = 100000
Private Const MAX_FILAS_SIM As Long = 5000
Private Const N_CLASES As Long = 20
Private Const MAX_ERRORES_MSG As Long = 25
Private Const DOS_PI As Double = 6.28318530717959

' Posicion de las columnas dentro de tblRiesgos
Private Const COL_ID As Long = 1
Private Const COL_NOMBRE As Long = 2
Private Const COL_ACTIVO As Long = 3
Private Const COL_PROB As Long = 4
Private Const COL_DISTC As Long = 5
Private Const COL_C1 As Long = 6
Private Const COL_DISTT As Long = 9
Private Const COL_T1 As Long = 10
Private Const N_COLS_TABLA As Long = 13

' Codigos de distribucion
Private Const D_DESCONOCIDA As Long = -1
Private Const D_NINGUNA As Long = 0
Private Const D_TRIANGULAR As Long = 1
Private Const D_PERT As Long = 2
Private Const D_NORMAL As Long = 3
Private Const D_UNIFORME As Long = 4
Private Const D_LOGNORMAL As Long = 5
Private Const D_EXPONENCIAL As Long = 6
Private Const D_WEIBULL As Long = 7

' ---------------- Tipos ----------------
Private Type TRiesgo
    Id As String
    Nombre As String
    Fila As Long            ' fila de la hoja PARAMETROS
    Prob As Double          ' probabilidad de ocurrencia (0-1)
    DistC As Long           ' distribucion del impacto en costo (0 = no afecta)
    C1 As Double
    C2 As Double
    C3 As Double
    DistT As Long           ' distribucion del impacto en plazo (0 = no afecta)
    T1 As Double
    T2 As Double
    T3 As Double
End Type

Private Type TSens          ' sensibilidad de un riesgo (tornado)
    Idx As Long             ' indice del riesgo
    Media As Double         ' impacto medio del riesgo
    Rho As Double           ' correlacion de Spearman riesgo vs total
    Contrib As Double       ' rho^2 / suma(rho^2)
    BajoMedia As Double     ' media del total cuando el riesgo esta en su 10% inferior
    AltoMedia As Double     ' media del total cuando el riesgo esta en su 10% superior
    Swing As Double         ' AltoMedia - BajoMedia
End Type

' ---------------- Estado para mensajes de error ----------------
Private gEtapa As String
Private gRiesgo As Long
Private gSinGraficos As Boolean   ' solo para pruebas automaticas (siempre False en uso normal)


' ======================================================================
'  MACROS PUBLICAS
' ======================================================================

Public Sub RunMonteCarlo()
    Dim r() As TRiesgo, nR As Long, errs As String
    Dim N As Long, vSem As Variant, semTxt As String
    Dim baseC As Double, baseT As Double
    Dim c() As Double, t() As Double, totC() As Double, totT() As Double, occ() As Long
    Dim sC() As Double, sT() As Double
    Dim t0 As Double, calcPrev As Long, dummy As Single, msg As String
    Dim hayC As Boolean, hayT As Boolean

    On Error GoTo EH
    gEtapa = "validando datos"
    gRiesgo = 0
    calcPrev = xlCalculationAutomatic

    If Not ValidarParametros(False) Then Exit Sub
    ParseRiesgos r, nR, errs, False

    N = CLng(shParam.Range("Iteraciones").Value)
    baseC = NumOr(shParam.Range("CostoBase").Value, 0)
    baseT = NumOr(shParam.Range("PlazoBase").Value, 0)
    vSem = shParam.Range("Semilla").Value

    t0 = Timer
    calcPrev = Application.Calculation
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual
    Application.StatusBar = U("Iniciando simulaci\u00F3n Montecarlo...")

    If EsNum(vSem) Then
        dummy = Rnd(-1)
        Randomize CDbl(vSem)
        semTxt = CStr(vSem)
    Else
        Randomize
        semTxt = "aleatoria"
    End If

    gEtapa = "simulando iteraciones"
    Simular r, nR, N, c, t, totC, totT, occ

    gEtapa = "ordenando resultados"
    Application.StatusBar = "Calculando percentiles..."
    CopiaOrdenada totC, N, sC
    CopiaOrdenada totT, N, sT
    hayC = (sC(N) > sC(1))
    hayT = (sT(N) > sT(1))

    gEtapa = "escribiendo la hoja RESULTADOS"
    Application.StatusBar = "Escribiendo resultados..."
    EscribirResultados sC, sT, N, nR, semTxt, baseC, baseT

    gEtapa = "escribiendo la hoja CURVA_S"
    EscribirCurvaS sC, sT, N, hayC, hayT

    gEtapa = "calculando la sensibilidad (TORNADO)"
    Application.StatusBar = "Calculando sensibilidad (tornado)..."
    EscribirTornado c, t, totC, totT, N, r, nR

    gEtapa = "escribiendo la hoja RANGOS"
    EscribirRangos c, t, sC, sT, N, r, nR, occ

    gEtapa = "escribiendo la hoja SIMULACION"
    EscribirSimulacion c, t, totC, totT, N, r, nR

    Restaurar calcPrev
    shRes.Activate
    shRes.Range("A1").Select

    msg = U("Simulaci\u00F3n completada.") & vbLf & vbLf & _
          ChrW$(8226) & " Iteraciones: " & Format$(N, "#,##0") & vbLf & _
          ChrW$(8226) & " Riesgos activos: " & nR & vbLf & _
          ChrW$(8226) & " Semilla: " & semTxt & vbLf & _
          ChrW$(8226) & " Tiempo: " & Format$(Timer - t0, "0.0") & " s" & vbLf & vbLf & _
          "COSTO   P50: S/ " & Format$(Percentil(sC, N, 50), "#,##0") & _
          "    P80: S/ " & Format$(Percentil(sC, N, 80), "#,##0") & vbLf & _
          "PLAZO   P50: " & Format$(Percentil(sT, N, 50), "#,##0.0") & U(" d\u00EDas") & _
          "    P80: " & Format$(Percentil(sT, N, 80), "#,##0.0") & U(" d\u00EDas")
    MsgBox msg, vbInformation, Titulo()
    Exit Sub

EH:
    msg = "Error " & Err.Number & ": " & Err.Description & vbLf & vbLf & "Etapa: " & gEtapa
    If gRiesgo > 0 Then
        msg = msg & vbLf & "Riesgo: " & r(gRiesgo).Nombre & " (fila " & r(gRiesgo).Fila & " de la hoja PARAMETROS)"
    End If
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

' Devuelve True si la configuracion y todas las filas activas de tblRiesgos son validas.
' Las celdas con error quedan marcadas en rojo y se listan en un mensaje.
Public Function ValidarParametros(Optional ByVal mostrarOk As Boolean = False) As Boolean
    Dim r() As TRiesgo, nR As Long, errs As String
    If ParseRiesgos(r, nR, errs, True) Then
        ValidarParametros = True
        If mostrarOk Then
            MsgBox U("Validaci\u00F3n correcta: ") & nR & U(" riesgo(s) activo(s) listos para simular."), _
                   vbInformation, Titulo()
        End If
    Else
        MsgBox "Se encontraron errores (las celdas con problema quedaron marcadas en rojo):" & _
               vbLf & vbLf & errs, vbExclamation, Titulo()
    End If
End Function

' Boton "LIMPIAR RESULTADOS": limpia el contenido y los graficos de las hojas de salida.
Public Sub ClearResults()
    Dim hojas As Variant, nombres As Variant, ws As Worksheet, k As Long
    On Error GoTo EH
    If MsgBox(U("Se limpiar\u00E1 el contenido de las hojas RESULTADOS, CURVA_S, TORNADO, RANGOS y SIMULACION.") & _
              vbLf & vbLf & U("\u00BFDesea continuar?"), vbQuestion + vbYesNo, Titulo()) = vbNo Then Exit Sub
    Application.ScreenUpdating = False
    hojas = Array(shRes, shCurva, shTornado, shRangos, shSim)
    nombres = Array("RESULTADOS", "CURVA S", "TORNADO", "RANGOS", U("SIMULACI\u00D3N"))
    For k = 0 To 4
        Set ws = hojas(k)
        PrepararHoja ws
        With ws.Range("B2")
            .Value = nombres(k) & U(" \u2014 Presione \u25B6 CORRER SIMULACI\u00D3N en la hoja PARAMETROS")
            .Font.Bold = True
            .Font.Size = 13
            .Font.Color = RGB(15, 110, 86)
        End With
    Next k
    Application.ScreenUpdating = True
    MsgBox "Resultados limpiados. Listo para una nueva simulaci" & ChrW$(243) & "n.", vbInformation, Titulo()
    Exit Sub
EH:
    Application.ScreenUpdating = True
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, Titulo()
End Sub


' ======================================================================
'  LECTURA Y VALIDACION DE PARAMETROS
' ======================================================================

Private Function TablaRiesgos() As ListObject
    On Error Resume Next
    Set TablaRiesgos = shParam.ListObjects("tblRiesgos")
    On Error GoTo 0
    If TablaRiesgos Is Nothing Then
        Err.Raise vbObjectError + 513, "MonteCarlo", _
                  "No se encuentra la tabla 'tblRiesgos' en la hoja PARAMETROS."
    End If
End Function

' Lee la configuracion y tblRiesgos. Devuelve True si no hay errores.
' r(1..nR) recibe los riesgos activos y validos.
Private Function ParseRiesgos(ByRef r() As TRiesgo, ByRef nR As Long, ByRef errs As String, _
                              ByVal marcar As Boolean) As Boolean
    ParseRiesgos = ParseRiesgosDe(TablaRiesgos().DataBodyRange, r, nR, errs, marcar)
End Function

' body = cuerpo de datos de tblRiesgos (Nothing si la tabla no tiene filas).
Private Function ParseRiesgosDe(ByVal body As Range, ByRef r() As TRiesgo, ByRef nR As Long, _
                                ByRef errs As String, ByVal marcar As Boolean) As Boolean
    Dim datos As Variant, v As Variant
    Dim i As Long, nErr As Long, antes As Long, fila As Long
    Dim nombre As String, activo As String, pref As String
    Dim dc As Long, dt As Long, prob As Double
    Dim p1 As Double, p2 As Double, p3 As Double
    Dim q1 As Double, q2 As Double, q3 As Double

    ReDim r(1 To MAX_RIESGOS)
    nR = 0
    errs = ""
    nErr = 0

    If marcar Then
        If Not body Is Nothing Then body.Interior.Color = RGB(255, 242, 204)
        shParam.Range("CostoBase").Interior.Color = RGB(255, 242, 204)
        shParam.Range("PlazoBase").Interior.Color = RGB(255, 242, 204)
        shParam.Range("Iteraciones").Interior.Color = RGB(255, 242, 204)
        shParam.Range("Semilla").Interior.Color = RGB(255, 242, 204)
    End If

    ' --- Configuracion ---
    v = shParam.Range("Iteraciones").Value
    If Not IteracionesValidas(v) Then
        AddErr errs, nErr, U("N\u00FAmero de iteraciones: debe ser un entero entre 1,000 y 100,000.")
        MarcarError shParam.Range("Iteraciones"), marcar
    End If
    v = shParam.Range("Semilla").Value
    If Len(Txt(v)) > 0 And Not EsNum(v) Then
        AddErr errs, nErr, U("Semilla aleatoria: d\u00E9jela vac\u00EDa o ingrese un n\u00FAmero.")
        MarcarError shParam.Range("Semilla"), marcar
    End If
    v = shParam.Range("CostoBase").Value
    If Len(Txt(v)) > 0 And Not EsNum(v) Then
        AddErr errs, nErr, U("Costo base: d\u00E9jelo vac\u00EDo o ingrese un n\u00FAmero.")
        MarcarError shParam.Range("CostoBase"), marcar
    End If
    v = shParam.Range("PlazoBase").Value
    If Len(Txt(v)) > 0 And Not EsNum(v) Then
        AddErr errs, nErr, U("Plazo base: d\u00E9jelo vac\u00EDo o ingrese un n\u00FAmero.")
        MarcarError shParam.Range("PlazoBase"), marcar
    End If

    If body Is Nothing Then
        AddErr errs, nErr, "La tabla tblRiesgos no tiene filas de datos."
        ParseRiesgosDe = False
        Exit Function
    End If

    datos = body.Value
    For i = 1 To UBound(datos, 1)
        fila = body.Row + i - 1
        If FilaVacia(datos, i) Then GoTo Siguiente

        nombre = Txt(datos(i, COL_NOMBRE))
        activo = UCase$(Txt(datos(i, COL_ACTIVO)))
        If activo = "NO" Then GoTo Siguiente

        antes = nErr
        If Len(nombre) > 0 Then
            pref = "Fila " & fila & " (" & nombre & "): "
        Else
            pref = "Fila " & fila & ": "
        End If
        p1 = 0: p2 = 0: p3 = 0: q1 = 0: q2 = 0: q3 = 0
        prob = 1

        If Len(nombre) = 0 Then
            AddErr errs, nErr, pref & "falta el nombre del riesgo."
            MarcarError body.Cells(i, COL_NOMBRE), marcar
        End If
        If Len(activo) > 0 And activo <> "SI" And activo <> "S" & ChrW$(205) Then
            AddErr errs, nErr, pref & "ACTIVO debe ser SI o NO."
            MarcarError body.Cells(i, COL_ACTIVO), marcar
        End If

        v = datos(i, COL_PROB)
        If Len(Txt(v)) = 0 Then
            prob = 1
        ElseIf Not EsNum(v) Then
            AddErr errs, nErr, pref & U("PROBABILIDAD debe ser un n\u00FAmero entre 0 y 1.")
            MarcarError body.Cells(i, COL_PROB), marcar
        ElseIf CDbl(v) < 0 Or CDbl(v) > 1 Then
            AddErr errs, nErr, pref & "PROBABILIDAD debe estar entre 0 y 1 (ej. 0.35 = 35%)."
            MarcarError body.Cells(i, COL_PROB), marcar
        Else
            prob = CDbl(v)
        End If

        dc = DistCodigo(Txt(datos(i, COL_DISTC)))
        dt = DistCodigo(Txt(datos(i, COL_DISTT)))
        If dc = D_DESCONOCIDA Then
            AddErr errs, nErr, pref & "DIST_COSTO '" & Txt(datos(i, COL_DISTC)) & U("' no reconocida.")
            MarcarError body.Cells(i, COL_DISTC), marcar
        End If
        If dt = D_DESCONOCIDA Then
            AddErr errs, nErr, pref & "DIST_PLAZO '" & Txt(datos(i, COL_DISTT)) & U("' no reconocida.")
            MarcarError body.Cells(i, COL_DISTT), marcar
        End If
        If dc = D_NINGUNA And dt = D_NINGUNA Then
            AddErr errs, nErr, pref & U("indique al menos una distribuci\u00F3n (DIST_COSTO o DIST_PLAZO).")
            MarcarError body.Cells(i, COL_DISTC), marcar
            MarcarError body.Cells(i, COL_DISTT), marcar
        End If
        If dc > 0 Then ValidarDist dc, datos, i, COL_C1, "costo", pref, body, marcar, errs, nErr, p1, p2, p3
        If dt > 0 Then ValidarDist dt, datos, i, COL_T1, "plazo", pref, body, marcar, errs, nErr, q1, q2, q3

        If nErr = antes Then
            If nR >= MAX_RIESGOS Then
                AddErr errs, nErr, pref & U("se admite un m\u00E1ximo de ") & MAX_RIESGOS & " riesgos activos."
            Else
                nR = nR + 1
                With r(nR)
                    .Id = Txt(datos(i, COL_ID))
                    If Len(.Id) = 0 Then .Id = CStr(i)
                    .Nombre = nombre
                    .Fila = fila
                    .Prob = prob
                    .DistC = dc: .C1 = p1: .C2 = p2: .C3 = p3
                    .DistT = dt: .T1 = q1: .T2 = q2: .T3 = q3
                End With
            End If
        End If
Siguiente:
    Next i

    If nR = 0 And nErr = 0 Then
        AddErr errs, nErr, "No hay riesgos activos en tblRiesgos (ACTIVO = SI y con nombre)."
    End If
    ParseRiesgosDe = (nErr = 0)
End Function

' Valida los parametros de una distribucion. Devuelve los parametros en p1..p3.
Private Function ValidarDist(ByVal d As Long, datos As Variant, ByVal i As Long, ByVal col0 As Long, _
                             ByVal dimTxt As String, ByVal pref As String, ByVal body As Range, _
                             ByVal marcar As Boolean, ByRef errs As String, ByRef nErr As Long, _
                             ByRef p1 As Double, ByRef p2 As Double, ByRef p3 As Double) As Boolean
    Dim np As Long, k As Long, antes As Long
    Dim p(1 To 3) As Double
    Dim txtD As String

    antes = nErr
    np = DistNParams(d)
    txtD = pref & DistNombre(d) & " de " & dimTxt & ": "
    For k = 1 To np
        If EsNum(datos(i, col0 + k - 1)) Then
            p(k) = CDbl(datos(i, col0 + k - 1))
        Else
            AddErr errs, nErr, txtD & U("falta el par\u00E1metro P") & k & U(" o no es num\u00E9rico.")
            MarcarError body.Cells(i, col0 + k - 1), marcar
        End If
    Next k

    If nErr = antes Then
        Select Case d
            Case D_TRIANGULAR, D_PERT
                If Not (p(1) <= p(2) And p(2) <= p(3)) Then
                    AddErr errs, nErr, txtD & U("debe cumplirse M\u00EDn (P1) <= Moda (P2) <= M\u00E1x (P3).")
                    MarcarError body.Cells(i, col0).Resize(1, 3), marcar
                End If
            Case D_UNIFORME
                If p(1) > p(2) Then
                    AddErr errs, nErr, txtD & U("debe cumplirse M\u00EDn (P1) <= M\u00E1x (P2).")
                    MarcarError body.Cells(i, col0).Resize(1, 2), marcar
                End If
            Case D_NORMAL
                If p(2) <= 0 Then
                    AddErr errs, nErr, txtD & U("la desviaci\u00F3n est\u00E1ndar (P2) debe ser mayor que 0.")
                    MarcarError body.Cells(i, col0 + 1), marcar
                End If
            Case D_LOGNORMAL
                If p(1) <= 0 Then
                    AddErr errs, nErr, txtD & "la media (P1) debe ser mayor que 0."
                    MarcarError body.Cells(i, col0), marcar
                End If
                If p(2) <= 0 Then
                    AddErr errs, nErr, txtD & U("la desviaci\u00F3n est\u00E1ndar (P2) debe ser mayor que 0.")
                    MarcarError body.Cells(i, col0 + 1), marcar
                End If
            Case D_EXPONENCIAL
                If p(1) <= 0 Then
                    AddErr errs, nErr, txtD & "la media (P1) debe ser mayor que 0."
                    MarcarError body.Cells(i, col0), marcar
                End If
            Case D_WEIBULL
                If p(1) <= 0 Then
                    AddErr errs, nErr, txtD & "la forma (P1) debe ser mayor que 0."
                    MarcarError body.Cells(i, col0), marcar
                End If
                If p(2) <= 0 Then
                    AddErr errs, nErr, txtD & "la escala (P2) debe ser mayor que 0."
                    MarcarError body.Cells(i, col0 + 1), marcar
                End If
        End Select
    End If

    p1 = p(1): p2 = p(2): p3 = p(3)
    ValidarDist = (nErr = antes)
End Function

Private Function IteracionesValidas(ByVal v As Variant) As Boolean
    If Not EsNum(v) Then Exit Function
    If CDbl(v) < MIN_ITER Or CDbl(v) > MAX_ITER Then Exit Function
    If CDbl(v) <> Int(CDbl(v)) Then Exit Function
    IteracionesValidas = True
End Function

' Fila vacia: sin nombre, sin probabilidad, sin distribuciones y sin parametros.
Private Function FilaVacia(datos As Variant, ByVal i As Long) As Boolean
    Dim k As Long
    For k = COL_NOMBRE To N_COLS_TABLA - 1
        If k <> COL_ACTIVO Then
            If Len(Txt(datos(i, k))) > 0 Then Exit Function
        End If
    Next k
    FilaVacia = True
End Function

Private Sub AddErr(ByRef errs As String, ByRef nErr As Long, ByVal msg As String)
    nErr = nErr + 1
    If nErr <= MAX_ERRORES_MSG Then
        errs = errs & "- " & msg & vbLf
    ElseIf nErr = MAX_ERRORES_MSG + 1 Then
        errs = errs & U("- ... (hay m\u00E1s errores; corrija los anteriores y valide de nuevo)") & vbLf
    End If
End Sub

Private Sub MarcarError(ByVal rng As Range, ByVal marcar As Boolean)
    If marcar Then rng.Interior.Color = RGB(255, 199, 206)
End Sub

Private Function DistCodigo(ByVal s As String) As Long
    s = UCase$(Trim$(s))
    If Len(s) = 0 Or s = "-" Or s = "NINGUNA" Or s = "N/A" Or s = ChrW$(8212) Or s = ChrW$(8211) Then
        DistCodigo = D_NINGUNA
        Exit Function
    End If
    Select Case s
        Case "TRIANGULAR": DistCodigo = D_TRIANGULAR
        Case "PERT": DistCodigo = D_PERT
        Case "NORMAL": DistCodigo = D_NORMAL
        Case "UNIFORME": DistCodigo = D_UNIFORME
        Case "LOGNORMAL": DistCodigo = D_LOGNORMAL
        Case "EXPONENCIAL": DistCodigo = D_EXPONENCIAL
        Case "WEIBULL": DistCodigo = D_WEIBULL
        Case Else: DistCodigo = D_DESCONOCIDA
    End Select
End Function

Private Function DistNombre(ByVal d As Long) As String
    Select Case d
        Case D_TRIANGULAR: DistNombre = "TRIANGULAR"
        Case D_PERT: DistNombre = "PERT"
        Case D_NORMAL: DistNombre = "NORMAL"
        Case D_UNIFORME: DistNombre = "UNIFORME"
        Case D_LOGNORMAL: DistNombre = "LOGNORMAL"
        Case D_EXPONENCIAL: DistNombre = "EXPONENCIAL"
        Case D_WEIBULL: DistNombre = "WEIBULL"
        Case Else: DistNombre = "-"
    End Select
End Function

Private Function DistNParams(ByVal d As Long) As Long
    Select Case d
        Case D_TRIANGULAR, D_PERT: DistNParams = 3
        Case D_NORMAL, D_UNIFORME, D_LOGNORMAL, D_WEIBULL: DistNParams = 2
        Case D_EXPONENCIAL: DistNParams = 1
        Case Else: DistNParams = 0
    End Select
End Function


' ======================================================================
'  MOTOR DE SIMULACION
' ======================================================================

' Simula N iteraciones. c(i,j) y t(i,j) = impacto del riesgo j en la iteracion i.
' Si el riesgo ocurre, costo y plazo se muestrean en la misma iteracion.
Private Sub Simular(r() As TRiesgo, ByVal nR As Long, ByVal N As Long, _
                    c() As Double, t() As Double, totC() As Double, totT() As Double, occ() As Long)
    Dim i As Long, j As Long, paso As Long
    Dim sc As Double, st As Double, x As Double, ocurre As Boolean

    ReDim c(1 To N, 1 To nR)
    ReDim t(1 To N, 1 To nR)
    ReDim totC(1 To N)
    ReDim totT(1 To N)
    ReDim occ(1 To nR)
    paso = N \ 20
    If paso < 1 Then paso = 1

    For i = 1 To N
        sc = 0
        st = 0
        For j = 1 To nR
            gRiesgo = j
            If r(j).Prob >= 1 Then
                ocurre = True
            Else
                ocurre = (Rnd() < r(j).Prob)
            End If
            If ocurre Then
                occ(j) = occ(j) + 1
                If r(j).DistC > 0 Then
                    x = Muestra(r(j).DistC, r(j).C1, r(j).C2, r(j).C3)
                    c(i, j) = x
                    sc = sc + x
                End If
                If r(j).DistT > 0 Then
                    x = Muestra(r(j).DistT, r(j).T1, r(j).T2, r(j).T3)
                    t(i, j) = x
                    st = st + x
                End If
            End If
        Next j
        totC(i) = sc
        totT(i) = st
        If i Mod paso = 0 Then
            Application.StatusBar = U("Simulando... ") & Format$(i / N, "0%") & " completado"
            DoEvents
        End If
    Next i
    gRiesgo = 0
End Sub

Private Function Muestra(ByVal d As Long, ByVal p1 As Double, ByVal p2 As Double, ByVal p3 As Double) As Double
    Select Case d
        Case D_TRIANGULAR: Muestra = RandTriangular(p1, p2, p3)
        Case D_PERT: Muestra = RandPERT(p1, p2, p3)
        Case D_NORMAL: Muestra = RandNormal(p1, p2)
        Case D_UNIFORME: Muestra = p1 + Rnd() * (p2 - p1)
        Case D_LOGNORMAL: Muestra = RandLogNormal(p1, p2)
        Case D_EXPONENCIAL: Muestra = RandExponencial(p1)
        Case D_WEIBULL: Muestra = RandWeibull(p1, p2)
        Case Else: Muestra = 0
    End Select
End Function

' Uniforme en (0,1): nunca devuelve 0 (evita Log(0)).
Private Function U01() As Double
    Dim u As Double
    Do
        u = Rnd()
    Loop While u <= 0
    U01 = u
End Function

Private Function RandTriangular(ByVal a As Double, ByVal m As Double, ByVal b As Double) As Double
    Dim u As Double
    If b <= a Then
        RandTriangular = a
        Exit Function
    End If
    u = Rnd()
    If u < (m - a) / (b - a) Then
        RandTriangular = a + Sqr(u * (b - a) * (m - a))
    Else
        RandTriangular = b - Sqr((1 - u) * (b - a) * (b - m))
    End If
End Function

' Beta-PERT (lambda = 4): Beta(alfa, beta) muestreada como X/(X+Y), X~Gamma(alfa), Y~Gamma(beta).
Private Function RandPERT(ByVal a As Double, ByVal m As Double, ByVal b As Double) As Double
    Dim al As Double, be As Double, x As Double, y As Double
    If b <= a Then
        RandPERT = a
        Exit Function
    End If
    al = 1 + 4 * (m - a) / (b - a)
    be = 1 + 4 * (b - m) / (b - a)
    x = RandGamma(al)
    y = RandGamma(be)
    RandPERT = a + (b - a) * x / (x + y)
End Function

' Gamma(k, 1) por el metodo de Marsaglia-Tsang.
Private Function RandGamma(ByVal k As Double) As Double
    Dim d As Double, cc As Double, x As Double, v As Double, u As Double
    If k < 1 Then
        RandGamma = RandGamma(k + 1) * U01() ^ (1 / k)
        Exit Function
    End If
    d = k - 1 / 3
    cc = 1 / Sqr(9 * d)
    Do
        Do
            x = RandNormal(0, 1)
            v = 1 + cc * x
        Loop While v <= 0
        v = v * v * v
        u = U01()
        If u < 1 - 0.0331 * x * x * x * x Then Exit Do
        If Log(u) < 0.5 * x * x + d * (1 - v + Log(v)) Then Exit Do
    Loop
    RandGamma = d * v
End Function

' Normal por Box-Muller.
Private Function RandNormal(ByVal mu As Double, ByVal sigma As Double) As Double
    RandNormal = mu + sigma * Sqr(-2 * Log(U01())) * Cos(DOS_PI * Rnd())
End Function

' LogNormal parametrizada con la media y desviacion estandar de la variable.
Private Function RandLogNormal(ByVal m As Double, ByVal sd As Double) As Double
    Dim s2 As Double
    s2 = Log(1 + (sd / m) ^ 2)
    RandLogNormal = Exp(RandNormal(Log(m) - s2 / 2, Sqr(s2)))
End Function

' Exponencial parametrizada con la media (lambda = 1 / media).
Private Function RandExponencial(ByVal media As Double) As Double
    RandExponencial = -media * Log(1 - Rnd())
End Function

Private Function RandWeibull(ByVal forma As Double, ByVal escala As Double) As Double
    RandWeibull = escala * (-Log(1 - Rnd())) ^ (1 / forma)
End Function


' ======================================================================
'  ESTADISTICA
' ======================================================================

Private Sub Columna(m() As Double, ByVal j As Long, ByVal N As Long, dst() As Double)
    Dim i As Long
    ReDim dst(1 To N)
    For i = 1 To N
        dst(i) = m(i, j)
    Next i
End Sub

Private Sub CopiaOrdenada(src() As Double, ByVal N As Long, dst() As Double)
    Dim i As Long
    ReDim dst(1 To N)
    For i = 1 To N
        dst(i) = src(i)
    Next i
    QuickSort dst, 1, N
End Sub

' QuickSort: recursion sobre la particion menor para limitar la profundidad de pila.
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

' Igual que QuickSort pero arrastra un vector de indices.
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

' Percentil con interpolacion lineal (mismo criterio que PERCENTIL.INC). p en 0..100.
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

Private Function Media(a() As Double, ByVal N As Long) As Double
    Dim i As Long, s As Double
    For i = 1 To N
        s = s + a(i)
    Next i
    Media = s / N
End Function

Private Function DesvEst(a() As Double, ByVal N As Long, ByVal m As Double) As Double
    Dim i As Long, s As Double
    If N < 2 Then Exit Function
    For i = 1 To N
        s = s + (a(i) - m) * (a(i) - m)
    Next i
    DesvEst = Sqr(s / (N - 1))
End Function

Private Function FraccionCero(a() As Double, ByVal N As Long) As Double
    Dim i As Long, k As Long
    For i = 1 To N
        If a(i) = 0 Then k = k + 1
    Next i
    FraccionCero = k / N
End Function

' Rangos promedio (empates = promedio de posiciones). ix = indices ordenados por valor.
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
    ma = Media(a, N)
    mb = Media(b, N)
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

' Sensibilidad de cada riesgo respecto del total de una dimension (costo o plazo).
' Resultado ordenado de mayor a menor |swing|.
Private Sub CalcularSensibilidad(m() As Double, tot() As Double, ByVal N As Long, r() As TRiesgo, _
                                 ByVal nR As Long, ByVal esCosto As Boolean, sens() As TSens, nS As Long)
    Dim rkTot() As Double, ixTot() As Long, x() As Double, rk() As Double, ix() As Long
    Dim i As Long, j As Long, nDec As Long, tiene As Boolean
    Dim sumR2 As Double, sb As Double, sa As Double, mTot As Double
    Dim a As Long, b As Long, tmpI As Long, tmpK As Double
    Dim ord() As Long, clave() As Double, copia() As TSens

    nS = 0
    ReDim sens(1 To nR)
    RangosPromedio tot, N, rkTot, ixTot
    mTot = Media(tot, N)
    nDec = N \ 10
    If nDec < 1 Then nDec = 1

    For j = 1 To nR
        If esCosto Then
            tiene = (r(j).DistC > 0)
        Else
            tiene = (r(j).DistT > 0)
        End If
        If tiene Then
            gRiesgo = j
            Columna m, j, N, x
            nS = nS + 1
            sens(nS).Idx = j
            sens(nS).Media = Media(x, N)
            RangosPromedio x, N, rk, ix
            If x(ix(1)) < x(ix(N)) Then
                sens(nS).Rho = Pearson(rk, rkTot, N)
                sb = 0
                sa = 0
                For i = 1 To nDec
                    sb = sb + tot(ix(i))
                    sa = sa + tot(ix(N - nDec + i))
                Next i
                sens(nS).BajoMedia = sb / nDec
                sens(nS).AltoMedia = sa / nDec
                sens(nS).Swing = sens(nS).AltoMedia - sens(nS).BajoMedia
            Else
                ' riesgo constante (o que nunca ocurre): no aporta variabilidad
                sens(nS).Rho = 0
                sens(nS).BajoMedia = mTot
                sens(nS).AltoMedia = mTot
                sens(nS).Swing = 0
            End If
            sumR2 = sumR2 + sens(nS).Rho * sens(nS).Rho
        End If
    Next j
    gRiesgo = 0

    For j = 1 To nS
        If sumR2 > 0 Then sens(j).Contrib = sens(j).Rho * sens(j).Rho / sumR2
    Next j

    ' Orden por |swing| descendente: se ordena un vector de indices (insercion,
    ' maximo 50 riesgos) y luego se copian los campos uno a uno.
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
    dst.Media = src.Media
    dst.Rho = src.Rho
    dst.Contrib = src.Contrib
    dst.BajoMedia = src.BajoMedia
    dst.AltoMedia = src.AltoMedia
    dst.Swing = src.Swing
End Sub

' ======================================================================
'  HOJAS DE SALIDA
' ======================================================================

Private Sub EscribirResultados(sC() As Double, sT() As Double, ByVal N As Long, ByVal nR As Long, _
                               ByVal semTxt As String, ByVal baseC As Double, ByVal baseT As Double)
    Dim ws As Worksheet, pcts As Variant, a() As Variant, hdr() As Variant
    Dim k As Long, nc As Long, p As Long, hayBase As Boolean
    Dim mC As Double, mT As Double, dC As Double, dT As Double, vC As Double, vT As Double

    Set ws = shRes
    PrepararHoja ws
    PonerTitulo ws, U("RESULTADOS \u2014 SIMULACI\u00D3N MONTECARLO DE RIESGOS"), _
        "Fecha: " & Format$(Now, "dd/mm/yyyy hh:mm") & "   |   Iteraciones: " & Format$(N, "#,##0") & _
        "   |   Semilla: " & semTxt & "   |   Riesgos activos: " & nR
    hayBase = (baseC <> 0 Or baseT <> 0)
    If hayBase Then nc = 5 Else nc = 3

    ' --- 1. Percentiles ---
    Seccion ws.Range("B5"), "1. TABLA DE PERCENTILES"
    ReDim hdr(1 To 1, 1 To nc)
    hdr(1, 1) = "PERCENTIL"
    hdr(1, 2) = "IMPACTO COSTO (S/)"
    hdr(1, 3) = U("IMPACTO PLAZO (d\u00EDas)")
    If hayBase Then
        hdr(1, 4) = "COSTO TOTAL (S/)" & vbLf & "base + impacto"
        hdr(1, 5) = U("PLAZO TOTAL (d\u00EDas)") & vbLf & "base + impacto"
    End If
    ws.Range("B6").Resize(1, nc).Value = hdr
    Encabezado ws.Range("B6").Resize(1, nc)

    pcts = Array(0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100)
    ReDim a(1 To 13, 1 To nc)
    For k = 0 To 12
        p = pcts(k)
        vC = Percentil(sC, N, p)
        vT = Percentil(sT, N, p)
        a(k + 1, 1) = EtiquetaP(p)
        a(k + 1, 2) = vC
        a(k + 1, 3) = vT
        If hayBase Then
            a(k + 1, 4) = baseC + vC
            a(k + 1, 5) = baseT + vT
        End If
    Next k
    ws.Range("B7").Resize(13, nc).Value = a
    Cuerpo ws.Range("B7").Resize(13, nc)
    ws.Range("C7:C19").NumberFormat = "#,##0"
    ws.Range("D7:D19").NumberFormat = "#,##0.0"
    If hayBase Then
        ws.Range("E7:E19").NumberFormat = "#,##0"
        ws.Range("F7:F19").NumberFormat = "#,##0.0"
    End If
    For k = 0 To 12
        Select Case pcts(k)
            Case 10: Resaltar ws.Range("B7").Offset(k, 0).Resize(1, nc), RGB(225, 245, 238)
            Case 50: Resaltar ws.Range("B7").Offset(k, 0).Resize(1, nc), RGB(250, 236, 231)
            Case 80: Resaltar ws.Range("B7").Offset(k, 0).Resize(1, nc), RGB(238, 237, 254)
            Case 90: Resaltar ws.Range("B7").Offset(k, 0).Resize(1, nc), RGB(250, 238, 218)
        End Select
    Next k

    ' --- 2. Estadisticas ---
    mC = Media(sC, N)
    mT = Media(sT, N)
    dC = DesvEst(sC, N, mC)
    dT = DesvEst(sT, N, mT)
    Seccion ws.Range("B21"), U("2. ESTAD\u00CDSTICAS DEL IMPACTO")
    ws.Range("B22:D22").Value = Array(U("ESTAD\u00CDSTICA"), "IMPACTO COSTO (S/)", U("IMPACTO PLAZO (d\u00EDas)"))
    Encabezado ws.Range("B22:D22")
    ReDim a(1 To 6, 1 To 3)
    a(1, 1) = "Media (valor esperado)": a(1, 2) = mC: a(1, 3) = mT
    a(2, 1) = U("Desviaci\u00F3n est\u00E1ndar"): a(2, 2) = dC: a(2, 3) = dT
    a(3, 1) = U("Coeficiente de variaci\u00F3n"): a(3, 2) = CoefVar(dC, mC): a(3, 3) = CoefVar(dT, mT)
    a(4, 1) = U("M\u00EDnimo"): a(4, 2) = sC(1): a(4, 3) = sT(1)
    a(5, 1) = U("M\u00E1ximo"): a(5, 2) = sC(N): a(5, 3) = sT(N)
    a(6, 1) = "Probabilidad de impacto = 0": a(6, 2) = FraccionCero(sC, N): a(6, 3) = FraccionCero(sT, N)
    ws.Range("B23:D28").Value = a
    Cuerpo ws.Range("B23:D28")
    ws.Range("C23:C28").NumberFormat = "#,##0"
    ws.Range("D23:D28").NumberFormat = "#,##0.0"
    ws.Range("C25:D25").NumberFormat = "0.0%"
    ws.Range("C28:D28").NumberFormat = "0.0%"

    ' --- 3. Contingencias ---
    Seccion ws.Range("B30"), "3. CONTINGENCIAS RECOMENDADAS"
    If hayBase Then nc = 7 Else nc = 5
    ReDim hdr(1 To 1, 1 To nc)
    hdr(1, 1) = "NIVEL DE CONFIANZA"
    hdr(1, 2) = "COSTO: impacto Pxx" & vbLf & "(S/)"
    hdr(1, 3) = "PLAZO: impacto Pxx" & vbLf & U("(d\u00EDas)")
    hdr(1, 4) = U("COSTO: Pxx \u2212 Media") & vbLf & "(S/)"
    hdr(1, 5) = U("PLAZO: Pxx \u2212 Media") & vbLf & U("(d\u00EDas)")
    If hayBase Then
        hdr(1, 6) = "COSTO: % sobre" & vbLf & "costo base"
        hdr(1, 7) = "PLAZO: % sobre" & vbLf & "plazo base"
    End If
    ws.Range("B31").Resize(1, nc).Value = hdr
    Encabezado ws.Range("B31").Resize(1, nc)
    pcts = Array(50, 80, 90)
    ReDim a(1 To 3, 1 To nc)
    For k = 0 To 2
        p = pcts(k)
        vC = Percentil(sC, N, p)
        vT = Percentil(sT, N, p)
        a(k + 1, 1) = EtiquetaP(p)
        a(k + 1, 2) = vC
        a(k + 1, 3) = vT
        a(k + 1, 4) = vC - mC
        a(k + 1, 5) = vT - mT
        If hayBase Then
            If baseC > 0 Then a(k + 1, 6) = vC / baseC Else a(k + 1, 6) = "-"
            If baseT > 0 Then a(k + 1, 7) = vT / baseT Else a(k + 1, 7) = "-"
        End If
    Next k
    ws.Range("B32").Resize(3, nc).Value = a
    Cuerpo ws.Range("B32").Resize(3, nc)
    ws.Range("C32:C34,E32:E34").NumberFormat = "#,##0"
    ws.Range("D32:D34,F32:F34").NumberFormat = "#,##0.0"
    If hayBase Then ws.Range("G32:H34").NumberFormat = "0.0%"
    Resaltar ws.Range("B33").Resize(1, nc), RGB(238, 237, 254)
    With ws.Range("B36")
        .Value = U("Contingencia recomendada = impacto P80: monto (S/) y d\u00EDas a reservar sobre el presupuesto y plazo base. " & _
                   "'Pxx \u2212 Media' = holgura adicional respecto del valor esperado.")
        .Font.Italic = True
        .Font.Color = RGB(95, 94, 90)
    End With

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 30
    ws.Columns("C:H").ColumnWidth = 18
End Sub

Private Sub EscribirCurvaS(sC() As Double, sT() As Double, ByVal N As Long, ByVal hayC As Boolean, ByVal hayT As Boolean)
    Dim ws As Worksheet, a() As Variant, k As Long

    Set ws = shCurva
    PrepararHoja ws
    PonerTitulo ws, U("CURVA S \u2014 PROBABILIDAD ACUMULADA"), _
        U("Probabilidad de que el impacto total sea menor o igual al valor indicado.")
    ws.Range("B4:D4").Value = Array("PROBABILIDAD" & vbLf & "ACUMULADA", "COSTO (S/)", U("PLAZO (d\u00EDas)"))
    Encabezado ws.Range("B4:D4")
    ReDim a(1 To 21, 1 To 3)
    For k = 0 To 20
        a(k + 1, 1) = k * 5 / 100
        a(k + 1, 2) = Percentil(sC, N, k * 5)
        a(k + 1, 3) = Percentil(sT, N, k * 5)
    Next k
    ws.Range("B5:D25").Value = a
    Cuerpo ws.Range("B5:D25")
    ws.Range("B5:B25").NumberFormat = "0%"
    ws.Range("B5:B25").HorizontalAlignment = xlCenter
    ws.Range("C5:C25").NumberFormat = "#,##0"
    ws.Range("D5:D25").NumberFormat = "#,##0.0"
    Resaltar ws.Range("B15:D15"), RGB(250, 236, 231)   ' P50
    Resaltar ws.Range("B21:D21"), RGB(238, 237, 254)   ' P80
    Resaltar ws.Range("B23:D23"), RGB(250, 238, 218)   ' P90

    EscribirHistograma ws, 28, sC, N, "COSTO (S/)", "#,##0", hayC
    EscribirHistograma ws, 52, sT, N, U("PLAZO (d\u00EDas)"), "#,##0.0", hayT

    If hayC Then
        GraficoCurvaS ws, ws.Range("C5:C25"), ws.Range("B5:B25"), U("Curva S \u2014 Impacto en COSTO (S/)"), _
                      "Costo (S/)", RGB(216, 90, 48), ws.Range("I2"), _
                      Percentil(sC, N, 50), Percentil(sC, N, 80), "#,##0", sC(1)
        GraficoHistograma ws, ws.Range("E30:E49"), ws.Range("F30:F49"), _
                          U("Histograma \u2014 Impacto en COSTO (S/)"), RGB(216, 90, 48), ws.Range("I40"), "#,##0"
    End If
    If hayT Then
        GraficoCurvaS ws, ws.Range("D5:D25"), ws.Range("B5:B25"), U("Curva S \u2014 Impacto en PLAZO (d\u00EDas)"), _
                      U("Plazo (d\u00EDas)"), RGB(24, 95, 165), ws.Range("I21"), _
                      Percentil(sT, N, 50), Percentil(sT, N, 80), "#,##0.0", sT(1)
        GraficoHistograma ws, ws.Range("E54:E73"), ws.Range("F54:F73"), _
                          U("Histograma \u2014 Impacto en PLAZO (d\u00EDas)"), RGB(24, 95, 165), ws.Range("I59"), "#,##0.0"
    End If

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B:G").ColumnWidth = 15
    ws.Columns("H").ColumnWidth = 3
End Sub

' Tabla de frecuencias (N_CLASES clases) a partir de la fila fila0.
Private Sub EscribirHistograma(ByVal ws As Worksheet, ByVal fila0 As Long, s() As Double, ByVal N As Long, _
                               ByVal dimTxt As String, ByVal fmt As String, ByVal hay As Boolean)
    Dim frec() As Long, a() As Variant, k As Long, i As Long, mn As Double, ancho As Double

    Seccion ws.Cells(fila0, 2), "HISTOGRAMA DE " & dimTxt
    If Not hay Then
        ws.Cells(fila0 + 1, 2).Value = "Sin variabilidad: no hay riesgos activos con impacto en esta dimensi" & ChrW$(243) & "n."
        Exit Sub
    End If

    ReDim frec(1 To N_CLASES)
    mn = s(1)
    ancho = (s(N) - s(1)) / N_CLASES
    For i = 1 To N
        If ancho > 0 Then k = Int((s(i) - mn) / ancho) + 1 Else k = 1
        If k > N_CLASES Then k = N_CLASES
        If k < 1 Then k = 1
        frec(k) = frec(k) + 1
    Next i

    ws.Cells(fila0 + 1, 2).Resize(1, 6).Value = Array("CLASE", "DESDE", "HASTA", "MARCA DE CLASE", "FRECUENCIA", "FRECUENCIA (%)")
    Encabezado ws.Cells(fila0 + 1, 2).Resize(1, 6)
    ReDim a(1 To N_CLASES, 1 To 6)
    For k = 1 To N_CLASES
        a(k, 1) = k
        a(k, 2) = mn + (k - 1) * ancho
        a(k, 3) = mn + k * ancho
        a(k, 4) = mn + (k - 0.5) * ancho
        a(k, 5) = frec(k)
        a(k, 6) = frec(k) / N
    Next k
    With ws.Cells(fila0 + 2, 2).Resize(N_CLASES, 6)
        .Value = a
    End With
    Cuerpo ws.Cells(fila0 + 2, 2).Resize(N_CLASES, 6)
    ws.Cells(fila0 + 2, 2).Resize(N_CLASES, 1).HorizontalAlignment = xlCenter
    ws.Cells(fila0 + 2, 3).Resize(N_CLASES, 3).NumberFormat = fmt
    ws.Cells(fila0 + 2, 6).Resize(N_CLASES, 1).NumberFormat = "#,##0"
    ws.Cells(fila0 + 2, 7).Resize(N_CLASES, 1).NumberFormat = "0.0%"
End Sub

Private Sub EscribirTornado(c() As Double, t() As Double, totC() As Double, totT() As Double, _
                            ByVal N As Long, r() As TRiesgo, ByVal nR As Long)
    Dim ws As Worksheet, fila As Long

    Set ws = shTornado
    PrepararHoja ws
    PonerTitulo ws, U("TORNADO \u2014 SENSIBILIDAD DEL TOTAL A CADA RIESGO"), _
        U("Orden: mayor swing primero. Spearman = correlaci\u00F3n de rangos riesgo vs. total. " & _
          "Swing = media del total cuando el riesgo est\u00E1 en su 10% superior \u2212 media cuando est\u00E1 en su 10% inferior.")
    fila = BloqueTornado(ws, 5, c, totC, N, r, nR, True)
    fila = BloqueTornado(ws, fila + 2, t, totT, N, r, nR, False)

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 5
    ws.Columns("C").ColumnWidth = 34
    ws.Columns("D:K").ColumnWidth = 15
    ws.Columns("L").ColumnWidth = 3
End Sub

' Escribe la tabla y el grafico de tornado de una dimension. Devuelve la ultima fila ocupada.
Private Function BloqueTornado(ByVal ws As Worksheet, ByVal fila As Long, m() As Double, tot() As Double, _
                               ByVal N As Long, r() As TRiesgo, ByVal nR As Long, ByVal esCosto As Boolean) As Long
    Dim sens() As TSens, nS As Long, a() As Variant, k As Long, nChart As Long
    Dim mTot As Double, dimTxt As String, fmt As String, color As Long
    Dim co As ChartObject, ultima As Long

    If esCosto Then
        dimTxt = "COSTO (S/)"
        fmt = "#,##0"
        color = RGB(216, 90, 48)
    Else
        dimTxt = U("PLAZO (d\u00EDas)")
        fmt = "#,##0.0"
        color = RGB(24, 95, 165)
    End If

    Seccion ws.Cells(fila, 2), "TORNADO DE " & dimTxt
    CalcularSensibilidad m, tot, N, r, nR, esCosto, sens, nS
    If nS = 0 Then
        ws.Cells(fila + 1, 2).Value = "No hay riesgos activos con impacto en esta dimensi" & ChrW$(243) & "n."
        BloqueTornado = fila + 1
        Exit Function
    End If

    mTot = Media(tot, N)
    ws.Cells(fila + 1, 2).Resize(1, 10).Value = Array("#", "RIESGO", "IMPACTO MEDIO" & vbLf & "del riesgo", _
        "SPEARMAN" & vbLf & "(rho)", U("CONTRIBUCI\u00D3N" & vbLf & "A LA VARIANZA"), _
        "TOTAL MEDIO" & vbLf & "riesgo en 10% inf.", "TOTAL MEDIO" & vbLf & "riesgo en 10% sup.", "SWING", _
        U("\u0394 vs media" & vbLf & "(10% inferior)"), U("\u0394 vs media" & vbLf & "(10% superior)"))
    Encabezado ws.Cells(fila + 1, 2).Resize(1, 10)

    ReDim a(1 To nS, 1 To 10)
    nChart = 0
    For k = 1 To nS
        a(k, 1) = k
        a(k, 2) = r(sens(k).Idx).Nombre
        a(k, 3) = sens(k).Media
        a(k, 4) = sens(k).Rho
        a(k, 5) = sens(k).Contrib
        a(k, 6) = sens(k).BajoMedia
        a(k, 7) = sens(k).AltoMedia
        a(k, 8) = sens(k).Swing
        a(k, 9) = sens(k).BajoMedia - mTot
        a(k, 10) = sens(k).AltoMedia - mTot
        If Abs(sens(k).Swing) > 0 Then nChart = k
    Next k
    ws.Cells(fila + 2, 2).Resize(nS, 10).Value = a
    Cuerpo ws.Cells(fila + 2, 2).Resize(nS, 10)
    ws.Cells(fila + 2, 2).Resize(nS, 1).HorizontalAlignment = xlCenter
    ws.Cells(fila + 2, 4).Resize(nS, 1).NumberFormat = fmt
    ws.Cells(fila + 2, 5).Resize(nS, 1).NumberFormat = "0.00"
    ws.Cells(fila + 2, 6).Resize(nS, 1).NumberFormat = "0.0%"
    ws.Cells(fila + 2, 7).Resize(nS, 5).NumberFormat = fmt
    ultima = fila + 1 + nS

    If nChart > 0 And Not gSinGraficos Then
        Set co = GraficoTornado(ws, ws.Cells(fila + 2, 3).Resize(nChart, 1), ws.Cells(fila + 2, 10).Resize(nChart, 1), _
                                ws.Cells(fila + 2, 11).Resize(nChart, 1), U("Tornado \u2014 ") & dimTxt, color, _
                                ws.Cells(fila, 13), nChart, fmt)
        Do While ws.Cells(ultima, 1).Top < co.Top + co.Height
            ultima = ultima + 1
        Loop
    End If
    BloqueTornado = ultima
End Function

Private Sub EscribirRangos(c() As Double, t() As Double, sC() As Double, sT() As Double, ByVal N As Long, _
                           r() As TRiesgo, ByVal nR As Long, occ() As Long)
    Dim ws As Worksheet, a() As Variant, esPlazo() As Boolean
    Dim j As Long, k As Long, nFil As Long, x() As Double

    Set ws = shRangos
    PrepararHoja ws
    PonerTitulo ws, "TABLA DE RANGOS POR RIESGO", _
        U("Estad\u00EDsticos sobre las ") & Format$(N, "#,##0") & _
        U(" iteraciones (incluye los escenarios en que el riesgo no ocurre, con impacto 0).")
    ws.Range("B4:N4").Value = Array("RIESGO", U("DIMENSI\u00D3N"), "UNIDAD", U("PROB. OCURRENCIA") & vbLf & "(dato)", _
        "FRECUENCIA" & vbLf & "OBSERVADA", U("M\u00CDNIMO"), "P10", "P25", "P50", "P75", "P90", U("M\u00C1XIMO"), "PROMEDIO")
    Encabezado ws.Range("B4:N4")

    nFil = 2
    For j = 1 To nR
        If r(j).DistC > 0 Then nFil = nFil + 1
        If r(j).DistT > 0 Then nFil = nFil + 1
    Next j
    ReDim a(1 To nFil, 1 To 13)
    ReDim esPlazo(1 To nFil)

    k = 0
    For j = 1 To nR
        If r(j).DistC > 0 Then
            k = k + 1
            Columna c, j, N, x
            QuickSort x, 1, N
            FilaRango a, k, r(j).Nombre, "Costo", "S/", r(j).Prob, occ(j) / N, x, N
        End If
        If r(j).DistT > 0 Then
            k = k + 1
            Columna t, j, N, x
            QuickSort x, 1, N
            FilaRango a, k, r(j).Nombre, "Plazo", U("d\u00EDas"), r(j).Prob, occ(j) / N, x, N
            esPlazo(k) = True
        End If
    Next j
    k = k + 1
    FilaRango a, k, "TOTAL COSTO", "Costo", "S/", "-", 1 - FraccionCero(sC, N), sC, N
    k = k + 1
    FilaRango a, k, "TOTAL PLAZO", "Plazo", U("d\u00EDas"), "-", 1 - FraccionCero(sT, N), sT, N
    esPlazo(k) = True

    ws.Range("B5").Resize(nFil, 13).Value = a
    Cuerpo ws.Range("B5").Resize(nFil, 13)
    ws.Range("C5").Resize(nFil, 2).HorizontalAlignment = xlCenter
    ws.Range("E5").Resize(nFil, 2).NumberFormat = "0.0%"
    ws.Range("E5").Resize(nFil, 2).HorizontalAlignment = xlCenter
    For k = 1 To nFil
        If esPlazo(k) Then
            ws.Range("G5").Offset(k - 1, 0).Resize(1, 8).NumberFormat = "#,##0.0"
        Else
            ws.Range("G5").Offset(k - 1, 0).Resize(1, 8).NumberFormat = "#,##0"
        End If
    Next k
    Resaltar ws.Range("B5").Offset(nFil - 2, 0).Resize(1, 13), RGB(225, 245, 238)
    Resaltar ws.Range("B5").Offset(nFil - 1, 0).Resize(1, 13), RGB(230, 241, 251)

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 36
    ws.Columns("C:F").ColumnWidth = 13
    ws.Columns("G:N").ColumnWidth = 13
End Sub

Private Sub FilaRango(a() As Variant, ByVal k As Long, ByVal nombre As String, ByVal dimTxt As String, _
                      ByVal unidad As String, ByVal prob As Variant, ByVal frec As Double, _
                      s() As Double, ByVal N As Long)
    a(k, 1) = nombre
    a(k, 2) = dimTxt
    a(k, 3) = unidad
    a(k, 4) = prob
    a(k, 5) = frec
    a(k, 6) = s(1)
    a(k, 7) = Percentil(s, N, 10)
    a(k, 8) = Percentil(s, N, 25)
    a(k, 9) = Percentil(s, N, 50)
    a(k, 10) = Percentil(s, N, 75)
    a(k, 11) = Percentil(s, N, 90)
    a(k, 12) = s(N)
    a(k, 13) = Media(s, N)
End Sub

Private Sub EscribirSimulacion(c() As Double, t() As Double, totC() As Double, totT() As Double, _
                               ByVal N As Long, r() As TRiesgo, ByVal nR As Long)
    Dim ws As Worksheet, h() As Variant, a() As Variant, esC() As Boolean
    Dim nShow As Long, nCol As Long, col As Long, i As Long, j As Long

    Set ws = shSim
    PrepararHoja ws
    nShow = N
    If nShow > MAX_FILAS_SIM Then nShow = MAX_FILAS_SIM
    PonerTitulo ws, U("SIMULACI\u00D3N \u2014 DATOS DE LAS PRIMERAS ") & Format$(nShow, "#,##0") & " ITERACIONES", _
        U("C: = impacto en costo (S/)   |   T: = impacto en plazo (d\u00EDas) de cada riesgo en la iteraci\u00F3n.")

    nCol = 3
    For j = 1 To nR
        If r(j).DistC > 0 Then nCol = nCol + 1
        If r(j).DistT > 0 Then nCol = nCol + 1
    Next j
    ReDim h(1 To 1, 1 To nCol)
    ReDim esC(1 To nCol)
    ReDim a(1 To nShow, 1 To nCol)
    h(1, 1) = "ITER"
    h(1, 2) = "TOTAL COSTO (S/)"
    h(1, 3) = U("TOTAL PLAZO (d\u00EDas)")
    esC(2) = True
    For i = 1 To nShow
        a(i, 1) = i
        a(i, 2) = totC(i)
        a(i, 3) = totT(i)
    Next i
    col = 3
    For j = 1 To nR
        If r(j).DistC > 0 Then
            col = col + 1
            h(1, col) = "C: " & r(j).Nombre
            esC(col) = True
            For i = 1 To nShow
                a(i, col) = c(i, j)
            Next i
        End If
        If r(j).DistT > 0 Then
            col = col + 1
            h(1, col) = "T: " & r(j).Nombre
            For i = 1 To nShow
                a(i, col) = t(i, j)
            Next i
        End If
    Next j

    ws.Range("B4").Resize(1, nCol).Value = h
    Encabezado ws.Range("B4").Resize(1, nCol)
    ws.Rows(4).RowHeight = 45
    ws.Range("B5").Resize(nShow, nCol).Value = a
    With ws.Range("B5").Resize(nShow, nCol)
        .Borders.LineStyle = xlContinuous
        .Borders.Color = RGB(208, 206, 198)
    End With
    For col = 2 To nCol
        If esC(col) Then
            ws.Range("B5").Offset(0, col - 1).Resize(nShow, 1).NumberFormat = "#,##0"
        Else
            ws.Range("B5").Offset(0, col - 1).Resize(nShow, 1).NumberFormat = "#,##0.0"
        End If
    Next col
    ws.Range("B5").Resize(nShow, 1).HorizontalAlignment = xlCenter

    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B").ColumnWidth = 8
    ws.Range("C1").Resize(1, nCol - 1).EntireColumn.ColumnWidth = 16
End Sub


' ======================================================================
'  GRAFICOS
' ======================================================================

Private Sub GraficoCurvaS(ByVal ws As Worksheet, ByVal rx As Range, ByVal ry As Range, ByVal titulo As String, _
                          ByVal ejeX As String, ByVal color As Long, ByVal pos As Range, _
                          ByVal v50 As Double, ByVal v80 As Double, ByVal fmt As String, ByVal vMin As Double)
    If gSinGraficos Then Exit Sub
    Dim co As ChartObject, ch As Chart, s As Series
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, 480, 270)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = rx
    s.Values = ry
    s.Name = titulo
    ch.ChartType = xlXYScatterSmoothNoMarkers
    s.Format.Line.ForeColor.RGB = color
    s.Format.Line.Weight = 2.25

    LineaReferencia ch, v50, 0.5, "P50", fmt, vMin, RGB(95, 94, 90)
    LineaReferencia ch, v80, 0.8, "P80", fmt, vMin, RGB(83, 74, 183)

    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.HasLegend = False
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
End Sub

' Linea punteada: desde (xMin, y) hasta (x, y) y luego hasta (x, 0), con etiqueta.
Private Sub LineaReferencia(ByVal ch As Chart, ByVal x As Double, ByVal y As Double, ByVal etiqueta As String, _
                            ByVal fmt As String, ByVal xMin As Double, ByVal color As Long)
    Dim s As Series
    Set s = ch.SeriesCollection.NewSeries
    s.ChartType = xlXYScatterLinesNoMarkers
    s.Name = etiqueta
    s.XValues = Array(xMin, x, x)
    s.Values = Array(y, y, 0)
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
    If gSinGraficos Then Exit Sub
    Dim co As ChartObject, ch As Chart, s As Series
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, 480, 270)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    Set s = ch.SeriesCollection.NewSeries
    s.Values = rVal
    s.XValues = rCat
    s.Name = "Frecuencia"
    ch.ChartType = xlColumnClustered
    s.Format.Fill.ForeColor.RGB = color
    ch.ChartGroups(1).GapWidth = 10
    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.HasLegend = False
    ch.Axes(xlCategory).TickLabels.NumberFormat = fmt
    ch.Axes(xlValue).HasTitle = True
    ch.Axes(xlValue).AxisTitle.Text = "Frecuencia (iteraciones)"
End Sub

Private Function GraficoTornado(ByVal ws As Worksheet, ByVal rCat As Range, ByVal rInf As Range, ByVal rSup As Range, _
                                ByVal titulo As String, ByVal color As Long, ByVal pos As Range, _
                                ByVal nBarras As Long, ByVal fmt As String) As ChartObject
    Dim co As ChartObject, ch As Chart, s As Series
    Set co = ws.ChartObjects.Add(pos.Left, pos.Top, 520, 110 + 28 * nBarras)
    Set ch = co.Chart
    Do While ch.SeriesCollection.Count > 0
        ch.SeriesCollection(1).Delete
    Loop
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = rCat
    s.Values = rInf
    s.Name = "Riesgo en su 10% inferior"
    Set s = ch.SeriesCollection.NewSeries
    s.XValues = rCat
    s.Values = rSup
    s.Name = "Riesgo en su 10% superior"
    ch.ChartType = xlBarClustered
    ch.SeriesCollection(1).Format.Fill.ForeColor.RGB = RGB(157, 195, 230)
    ch.SeriesCollection(2).Format.Fill.ForeColor.RGB = color
    ch.ChartGroups(1).Overlap = 100
    ch.ChartGroups(1).GapWidth = 40
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
    ch.HasTitle = True
    ch.ChartTitle.Text = titulo
    ch.ChartTitle.Font.Size = 12
    ch.HasLegend = True
    ch.Legend.Position = xlLegendPositionBottom
    Set GraficoTornado = co
End Function


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
    Titulo = U("Simulaci\u00F3n Montecarlo")
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

Private Function NumOr(ByVal v As Variant, ByVal defecto As Double) As Double
    If EsNum(v) Then NumOr = CDbl(v) Else NumOr = defecto
End Function

Private Function CoefVar(ByVal d As Double, ByVal m As Double) As Variant
    If m = 0 Then CoefVar = "-" Else CoefVar = d / Abs(m)
End Function

Private Function EtiquetaP(ByVal p As Long) As String
    Select Case p
        Case 0: EtiquetaP = U("P0 (m\u00EDnimo)")
        Case 10: EtiquetaP = "P10 (optimista)"
        Case 50: EtiquetaP = "P50 (mediana)"
        Case 80: EtiquetaP = "P80 (recomendado)"
        Case 90: EtiquetaP = "P90 (conservador)"
        Case 100: EtiquetaP = U("P100 (m\u00E1ximo)")
        Case Else: EtiquetaP = "P" & p
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

Private Sub PonerTitulo(ByVal ws As Worksheet, ByVal texto As String, ByVal subt As String)
    With ws.Range("B2")
        .Value = texto
        .Font.Bold = True
        .Font.Size = 14
        .Font.Color = RGB(15, 110, 86)
    End With
    ws.Rows(2).RowHeight = 22
    If Len(subt) > 0 Then
        With ws.Range("B3")
            .Value = subt
            .Font.Italic = True
            .Font.Color = RGB(95, 94, 90)
        End With
    End If
End Sub

Private Sub Seccion(ByVal c As Range, ByVal texto As String)
    c.Value = texto
    c.Font.Bold = True
    c.Font.Size = 11
    c.Font.Color = RGB(15, 110, 86)
End Sub

Private Sub Encabezado(ByVal rng As Range)
    With rng
        .Interior.Color = RGB(15, 110, 86)
        .Font.Color = RGB(255, 255, 255)
        .Font.Bold = True
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .WrapText = True
        .Borders.LineStyle = xlContinuous
        .Borders.Color = RGB(208, 206, 198)
    End With
    rng.Rows(1).RowHeight = 32
End Sub

Private Sub Cuerpo(ByVal rng As Range)
    Dim k As Long
    With rng
        .Interior.Color = RGB(255, 255, 255)
        .Borders.LineStyle = xlContinuous
        .Borders.Color = RGB(208, 206, 198)
        .VerticalAlignment = xlCenter
    End With
    For k = 2 To rng.Rows.Count Step 2
        rng.Rows(k).Interior.Color = RGB(241, 239, 232)
    Next k
End Sub

Private Sub Resaltar(ByVal rng As Range, ByVal color As Long)
    rng.Interior.Color = color
    rng.Font.Bold = True
End Sub

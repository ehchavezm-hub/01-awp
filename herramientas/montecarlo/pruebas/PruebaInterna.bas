
' ======================================================================
'  SOLO PRUEBAS (se agrega al modulo unicamente en el libro de prueba)
' ======================================================================

Public Function PruebaInterna(ByVal N As Long, ByVal semilla As Double) As String
    Dim r() As TRiesgo, nR As Long, dummy As Single
    Dim c() As Double, t() As Double, totC() As Double, totT() As Double, occ() As Long
    Dim sC() As Double, sT() As Double, sens() As TSens, nS As Long, res As String, k As Long
    ReDim r(1 To 5)
    nR = 5
    r(1).Nombre = "Ingenieria": r(1).Prob = 1: r(1).DistT = D_TRIANGULAR: r(1).T1 = 7: r(1).T2 = 14: r(1).T3 = 28
    r(2).Nombre = "Precios": r(2).Prob = 1: r(2).DistC = D_NORMAL: r(2).C1 = 50000: r(2).C2 = 25000
    r(3).Nombre = "Geotecnia": r(3).Prob = 0.35: r(3).DistC = D_PERT: r(3).C1 = 30000: r(3).C2 = 80000: r(3).C3 = 200000
    r(3).DistT = D_PERT: r(3).T1 = 10: r(3).T2 = 25: r(3).T3 = 60
    r(4).Nombre = "Huelga": r(4).Prob = 0.2: r(4).DistT = D_TRIANGULAR: r(4).T1 = 5: r(4).T2 = 15: r(4).T3 = 45
    r(5).Nombre = "Permisos": r(5).Prob = 1: r(5).DistT = D_UNIFORME: r(5).T1 = 10: r(5).T2 = 40
    dummy = Rnd(-1)
    Randomize semilla
    Simular r, nR, N, c, t, totC, totT, occ
    CopiaOrdenada totC, N, sC
    CopiaOrdenada totT, N, sT
    res = "C50=" & Percentil(sC, N, 50) & "|C80=" & Percentil(sC, N, 80) & "|C90=" & Percentil(sC, N, 90) & _
          "|T50=" & Percentil(sT, N, 50) & "|T80=" & Percentil(sT, N, 80) & "|T90=" & Percentil(sT, N, 90) & _
          "|Cmean=" & Media(sC, N) & "|Tmean=" & Media(sT, N) & "|occ3=" & occ(3) / N & "|occ4=" & occ(4) / N
    CalcularSensibilidad c, totC, N, r, nR, True, sens, nS
    For k = 1 To nS
        res = res & "|SC" & k & "=" & r(sens(k).Idx).Nombre & ":" & sens(k).Rho & ":" & sens(k).Swing & ":" & sens(k).Contrib
    Next k
    CalcularSensibilidad t, totT, N, r, nR, False, sens, nS
    For k = 1 To nS
        res = res & "|ST" & k & "=" & r(sens(k).Idx).Nombre & ":" & sens(k).Rho & ":" & sens(k).Swing & ":" & sens(k).Contrib
    Next k
    PruebaInterna = res
End Function

' Media y desviacion de N muestras de una distribucion.
Public Function PruebaDist(ByVal d As Long, ByVal p1 As Double, ByVal p2 As Double, ByVal p3 As Double, _
                           ByVal N As Long) As String
    Dim x() As Double, i As Long, m As Double, dummy As Single
    ReDim x(1 To N)
    dummy = Rnd(-1)
    Randomize 777
    For i = 1 To N
        x(i) = Muestra(d, p1, p2, p3)
    Next i
    m = Media(x, N)
    QuickSort x, 1, N
    PruebaDist = m & "|" & DesvEst(x, N, m) & "|" & x(1) & "|" & x(N) & "|" & Percentil(x, N, 50)
End Function

' Casos borde: constantes, probabilidad 0 y 1, y distribuciones restantes.
Public Function PruebaBordes() As String
    Dim r() As TRiesgo, nR As Long, N As Long, dummy As Single
    Dim c() As Double, t() As Double, totC() As Double, totT() As Double, occ() As Long
    Dim sC() As Double, sT() As Double, sens() As TSens, nS As Long, res As String
    ReDim r(1 To 6)
    nR = 6
    N = 2000
    r(1).Nombre = "TriConst": r(1).Prob = 1: r(1).DistT = D_TRIANGULAR: r(1).T1 = 5: r(1).T2 = 5: r(1).T3 = 5
    r(2).Nombre = "UniConst": r(2).Prob = 1: r(2).DistC = D_UNIFORME: r(2).C1 = 3: r(2).C2 = 3
    r(3).Nombre = "Prob0": r(3).Prob = 0: r(3).DistC = D_NORMAL: r(3).C1 = 1000: r(3).C2 = 100
    r(4).Nombre = "Expo": r(4).Prob = 1: r(4).DistT = D_EXPONENCIAL: r(4).T1 = 10
    r(5).Nombre = "Weib": r(5).Prob = 1: r(5).DistC = D_WEIBULL: r(5).C1 = 2: r(5).C2 = 10
    r(6).Nombre = "PertConst": r(6).Prob = 0.5: r(6).DistC = D_PERT: r(6).C1 = 7: r(6).C2 = 7: r(6).C3 = 7
    dummy = Rnd(-1)
    Randomize 1
    Simular r, nR, N, c, t, totC, totT, occ
    CopiaOrdenada totC, N, sC
    CopiaOrdenada totT, N, sT
    CalcularSensibilidad c, totC, N, r, nR, True, sens, nS
    res = "nSC=" & nS & "|top=" & r(sens(1).Idx).Nombre & "|swing3=" & sens(nS).Swing
    CalcularSensibilidad t, totT, N, r, nR, False, sens, nS
    res = res & "|nST=" & nS & "|topT=" & r(sens(1).Idx).Nombre & "|Tmin=" & sT(1) & "|occ3=" & occ(3) & "|occ6=" & occ(6)
    res = res & "|Cmin=" & sC(1) & "|P0=" & Percentil(sC, N, 0) & "|P100=" & Percentil(sC, N, 100)
    PruebaBordes = res
End Function

Public Function PruebaParse() As String
    Dim r() As TRiesgo, nR As Long, errs As String, ok As Boolean, k As Long, s As String
    On Error GoTo EH
    ok = ParseRiesgos(r, nR, errs, False)
    s = "ok=" & ok & "|nR=" & nR & "|errs=" & errs
    For k = 1 To nR
        s = s & "|" & r(k).Nombre & ":" & r(k).Prob & ":" & r(k).DistC & ":" & r(k).C1 & ":" & r(k).DistT & ":" & r(k).T1 & ":" & r(k).T3
    Next k
    PruebaParse = s
    Exit Function
EH:
    PruebaParse = "ERR " & Err.Number & ": " & Err.Description & "|errs=" & errs
End Function

' Parser sobre un rango dado (LibreOffice no implementa ListObjects).
Public Function PruebaParseRango(ByVal direccion As String) As String
    Dim r() As TRiesgo, nR As Long, errs As String, ok As Boolean, k As Long, s As String
    On Error GoTo EH
    ok = ParseRiesgosDe(shParam.Range(direccion), r, nR, errs, True)
    s = "ok=" & ok & "|nR=" & nR & "|errs=" & Replace(errs, vbLf, " / ")
    For k = 1 To nR
        s = s & "|" & r(k).Nombre & ":" & r(k).Prob & ":" & r(k).DistC & ":" & r(k).C1 & ":" & r(k).DistT & ":" & r(k).T1 & ":" & r(k).T3
    Next k
    PruebaParseRango = s
    Exit Function
EH:
    PruebaParseRango = "ERR " & Err.Number & ": " & Err.Description & "|errs=" & errs
End Function

' Escribe datos invalidos en filas vacias de la tabla para probar la validacion.
Public Function PruebaDatosMalos() As String
    With shParam
        .Range("C18").Value = "Riesgo con moda fuera de rango"
        .Range("D18").Value = "SI"
        .Range("F18").Value = "TRIANGULAR": .Range("G18").Value = 10: .Range("H18").Value = 50: .Range("I18").Value = 20
        .Range("C19").Value = "Probabilidad mala"
        .Range("E19").Value = 1.5
        .Range("J19").Value = "NORMAL": .Range("K19").Value = 10: .Range("L19").Value = 0
        .Range("C20").Value = "Sin distribucion"
        .Range("C21").Value = "Inactivo con errores"
        .Range("D21").Value = "NO"
        .Range("F21").Value = "XYZ"
        .Range("C22").Value = "Distribucion desconocida"
        .Range("J22").Value = "GAMMA"
        .Range("C23").Value = "Falta parametro"
        .Range("F23").Value = "LOGNORMAL": .Range("G23").Value = 100
        .Range("C24").Value = "Constante valida"
        .Range("J24").Value = "TRIANGULAR": .Range("K24").Value = 5: .Range("L24").Value = 5: .Range("M24").Value = 5
    End With
    PruebaDatosMalos = PruebaParseRango("B12:N61") & "|rojoG18=" & (shParam.Range("G18").Interior.Color = RGB(255, 199, 206)) & _
        "|rojoE19=" & (shParam.Range("E19").Interior.Color = RGB(255, 199, 206)) & _
        "|amarilloC24=" & (shParam.Range("C24").Interior.Color = RGB(255, 242, 204))
End Function

' Pipeline completo de salida (sin MsgBox) usando el rango de la tabla.
Public Function PruebaSalidas(ByVal N As Long) As String
    Dim r() As TRiesgo, nR As Long, errs As String, dummy As Single
    Dim c() As Double, t() As Double, totC() As Double, totT() As Double, occ() As Long
    Dim sC() As Double, sT() As Double
    On Error GoTo EH
    gSinGraficos = True
    gEtapa = "parse"
    ParseRiesgosDe shParam.Range("B12:N61"), r, nR, errs, False
    dummy = Rnd(-1): Randomize 12345
    gEtapa = "simular": Simular r, nR, N, c, t, totC, totT, occ
    CopiaOrdenada totC, N, sC
    CopiaOrdenada totT, N, sT
    gEtapa = "RESULTADOS": EscribirResultados sC, sT, N, nR, "12345", 1500000, 180
    gEtapa = "CURVA_S": EscribirCurvaS sC, sT, N, True, True
    gEtapa = "TORNADO": EscribirTornado c, t, totC, totT, N, r, nR
    gEtapa = "RANGOS": EscribirRangos c, t, sC, sT, N, r, nR, occ
    gEtapa = "SIMULACION": EscribirSimulacion c, t, totC, totT, N, r, nR
    PruebaSalidas = "OK charts=" & shCurva.ChartObjects.Count & "/" & shTornado.ChartObjects.Count
    Exit Function
EH:
    PruebaSalidas = "ERR en " & gEtapa & " " & Err.Number & ": " & Err.Description
End Function

' Diagnostico: que parte de la API de graficos soporta LibreOffice.
Public Function PruebaGrafico() As String
    Dim co As Object, ch As Object, s As Object, paso As String
    On Error GoTo EH
    paso = "ChartObjects.Add": Set co = shCurva.ChartObjects.Add(100, 100, 300, 200)
    paso = "Chart": Set ch = co.Chart
    paso = "SeriesCollection.NewSeries": Set s = ch.SeriesCollection.NewSeries
    paso = "Series.XValues": s.XValues = shCurva.Range("C5:C25")
    PruebaGrafico = "OK"
    Exit Function
EH:
    PruebaGrafico = "falla en " & paso & ": " & Err.Description
End Function

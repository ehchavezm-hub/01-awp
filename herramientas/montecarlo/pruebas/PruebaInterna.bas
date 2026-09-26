

' ======================================================================
'  SOLO PRUEBAS (se agrega al modulo unicamente en el libro de prueba)
'  LibreOffice no implementa ListObjects: las tablas se leen como rangos
'  cuyas direcciones inserta build_xlsm.py.
' ======================================================================

Private Function PrRango(ByVal cual As String) As Range
    Select Case cual
        Case "R_CUERPO": Set PrRango = hjParametros.Range("{{R_CUERPO}}")
        Case "R_ENC": Set PrRango = hjParametros.Range("{{R_ENC}}")
        Case "D_CUERPO": Set PrRango = hjParametros.Range("{{D_CUERPO}}")
        Case "D_ENC": Set PrRango = hjParametros.Range("{{D_ENC}}")
        Case "E_CUERPO": Set PrRango = hjParametros.Range("{{E_CUERPO}}")
        Case "E_ENC": Set PrRango = hjParametros.Range("{{E_ENC}}")
    End Select
End Function

Private Function PrLeer(ByRef errs As String, ByRef nErr As Long) As Boolean
    PrLeer = LeerModeloDe(PrRango("R_CUERPO"), PrRango("R_ENC"), PrRango("D_CUERPO"), PrRango("D_ENC"), _
                          PrRango("E_CUERPO"), PrRango("E_ENC"), False, errs, nErr)
End Function

Private Function PrNum(ByVal x As Double) As String
    PrNum = Replace(CStr(x), ",", ".")
End Function

Private Function PrResumen() As String
    Dim d As Long, s() As Double, r As Long, vmeS As Double, res As String, g As Long
    For d = 1 To gND
        Ordenados d, False, s
        vmeS = 0
        For r = 1 To gNR
            vmeS = vmeS + VME(r, d)
        Next r
        res = res & "|" & gD(d).Clave & "=" & PrNum(EstMedia(s, gN)) & ";" & PrNum(Percentil(s, gN, 50)) & ";" & _
              PrNum(Percentil(s, gN, 80)) & ";" & PrNum(Percentil(s, gN, 90)) & ";" & PrNum(vmeS)
    Next d
    For g = 1 To gNG
        res = res & "|G_" & gGrupoNom(g) & "=" & PrNum(gGrupoObj(g)) & ";" & PrNum(gGrupoLog(g)) & ";" & gGrupoN(g)
    Next g
    PrResumen = "NR=" & gNR & "|ND=" & gND & "|NEST=" & gNEstim & "|NADV=" & gNAdv & res
End Function

Private Sub PrColActivo(ByVal prefijo As String, ByVal valor As String)
    Dim cuerpo As Range, enc As Variant, cId As Long, cAct As Long, i As Long
    Set cuerpo = PrRango("R_CUERPO")
    enc = PrRango("R_ENC").Value
    cId = ColEnc(enc, "ID")
    cAct = ColEnc(enc, "ACTIVO")
    For i = 1 To cuerpo.Rows.Count
        If Left$(Txt(cuerpo.Cells(i, cId).Value), Len(prefijo)) = prefijo Then cuerpo.Cells(i, cAct).Value = valor
    Next i
End Sub

Private Sub PrCelda(ByVal id As String, ByVal columna As String, ByVal valor As Variant)
    Dim cuerpo As Range, enc As Variant, cId As Long, c As Long, i As Long
    Set cuerpo = PrRango("R_CUERPO")
    enc = PrRango("R_ENC").Value
    cId = ColEnc(enc, "ID")
    c = ColEnc(enc, columna)
    For i = 1 To cuerpo.Rows.Count
        If Txt(cuerpo.Cells(i, cId).Value) = id Then
            If IsEmpty(valor) Then cuerpo.Cells(i, c).ClearContents Else cuerpo.Cells(i, c).Value = valor
            Exit Sub
        End If
    Next i
End Sub

' 1) Generador: primeros valores con estado 12345 x 6 y con Semilla = 12345.
Public Function PruebaGenerador() As String
    Dim k As Long, res As String
    FijarEstadoGenerador 12345, 12345, 12345, 12345, 12345, 12345
    For k = 1 To 10
        res = res & PrNum(Aleatorio()) & ";"
    Next k
    SembrarGenerador 12345
    res = res & "|"
    For k = 1 To 3
        res = res & PrNum(Aleatorio()) & ";"
    Next k
    PruebaGenerador = res
End Function

' 2) Una distribucion: media, desviacion, minimo, maximo, media teorica y frecuencias de 0..5.
Public Function PruebaDist(ByVal cod As Long, ByVal a As Variant, ByVal b As Variant, ByVal c As Variant, _
                           ByVal e As Variant, ByVal N As Long) As String
    Dim crudo(1 To 4) As Variant, p(1 To 4) As Double, colP(1 To 1, 1 To 4) As Long, errs As String, nErr As Long
    Dim x() As Double, i As Long, k As Long, m As Double, f(0 To 5) As Long, res As String
    ReDim gDiscV(1 To 1, 1 To 1)
    ReDim gDiscF(1 To 1, 1 To 1)
    crudo(1) = a: crudo(2) = b: crudo(3) = c: crudo(4) = e
    For k = 1 To 4
        colP(1, k) = k
    Next k
    If Not ValidarDistribucion(cod, crudo, "", errs, nErr, p, 1, 1, hjParametros.Range("A1:D1"), 1, colP, 1, False) Then
        PruebaDist = "ERROR " & errs
        Exit Function
    End If
    SembrarGenerador 777
    ReDim x(1 To N)
    For i = 1 To N
        x(i) = Muestra(cod, p(1), p(2), p(3), p(4), 1, 1)
        If x(i) = Int(x(i)) And x(i) >= 0 And x(i) <= 5 Then f(CLng(x(i))) = f(CLng(x(i))) + 1
    Next i
    m = EstMedia(x, N)
    QuickSort x, 1, N
    res = PrNum(m) & "|" & PrNum(EstDesv(x, N, m)) & "|" & PrNum(x(1)) & "|" & PrNum(x(N)) & "|" & _
          PrNum(DistMediaTeorica(cod, p(1), p(2), p(3), p(4), 1, 1)) & "|" & PrNum(p(1)) & ";" & PrNum(p(3)) & "|"
    For k = 0 To 5
        res = res & PrNum(f(k) / N) & ";"
    Next k
    PruebaDist = res
End Function

' 3) Modelo leido de la hoja: REAL, REAL_INDEP (sin grupos) o EJEMPLOS.
Public Function PruebaModelo(ByVal N As Long, ByVal semilla As Double, ByVal modo As String) As String
    Dim errs As String, nErr As Long, t0 As Double, r As Long
    On Error GoTo EH
    If modo = "EJEMPLOS" Then
        PrColActivo "R-", "NO"
        PrColActivo "EJ-", "SI"
    Else
        PrColActivo "R-", "SI"
        PrColActivo "EJ-", "NO"
    End If
    hjParametros.Range("Iteraciones").Value = N
    hjParametros.Range("Semilla").Value = semilla
    If Not PrLeer(errs, nErr) Then
        PruebaModelo = "ERROR " & errs
        Exit Function
    End If
    If modo = "REAL_INDEP" Then
        For r = 1 To gNR
            gR(r).Grupo = ""
        Next r
    End If
    gSinGraficos = True
    t0 = Timer
    NucleoSimulacion
    PruebaModelo = PrResumen() & "|T=" & PrNum(Timer - t0)
    Exit Function
EH:
    PruebaModelo = "ERROR " & Err.Number & ": " & Err.Description & " (" & gEtapa & ")"
End Function

' 4) Escritura de todas las hojas de salida (sin graficos).
Public Function PruebaSalidas(ByVal N As Long) As String
    Dim errs As String, nErr As Long
    On Error GoTo EH
    PrColActivo "R-", "SI"
    PrColActivo "EJ-", "NO"
    PrCelda "R-01", "PROB_RESIDUAL", 0.2
    PrCelda "R-01", "COSTO_RESPUESTA", 150000
    PrCelda "R-14", "FACTOR_IMPACTO_RESIDUAL", 0.5
    PrCelda "R-14", "COSTO_RESPUESTA", 300000
    PrCelda "R-14", "ESTRATEGIA", "MITIGAR"
    hjParametros.Range("Iteraciones").Value = N
    hjParametros.Range("Semilla").Value = 12345
    If Not PrLeer(errs, nErr) Then
        PruebaSalidas = "ERROR " & errs
        Exit Function
    End If
    gSinGraficos = True
    gEtapa = "nucleo": NucleoSimulacion
    gEtapa = "RESULTADOS": EscribirResultados
    gEtapa = "CURVA_S": EscribirCurvaS
    gEtapa = "TORNADO": EscribirTornado
    gEtapa = "RANGOS": EscribirRangos
    gEtapa = "MATRIZ": EscribirMatriz
    gEtapa = "COMPARACION": EscribirComparacion
    gEtapa = "SIMULACION": EscribirSimulacion
    PruebaSalidas = "OK|" & PrResumen() & "|HAYDESP=" & gHayDespues & "|CRESP=" & PrNum(gCostoRespTotal)
    Exit Function
EH:
    PruebaSalidas = "ERROR " & Err.Number & ": " & Err.Description & " (" & gEtapa & ")"
End Function

' Modelo en memoria de nR riesgos y una dimension COSTO.
Private Sub PrMemoria(ByVal nR As Long, ByVal N As Long)
    Dim r As Long
    gNR = nR
    gND = 1
    gN = N
    gNivel = 0.8
    gSemillaFija = True
    gSemilla = 4242
    gHayDespues = False
    gCostoRespTotal = 0
    gDimCosto = 1
    ReDim gD(1 To 1)
    gD(1).Clave = "COSTO": gD(1).Nombre = "Costo": gD(1).Unidad = "S/": gD(1).Formato = "#,##0"
    ReDim gR(1 To nR)
    ReDim gDist(1 To nR, 1 To 1)
    ReDim gPar(1 To nR, 1 To 1, 1 To 4)
    ReDim gDiscV(1 To nR, 1 To 1)
    ReDim gDiscF(1 To nR, 1 To 1)
    For r = 1 To nR
        gR(r).Id = "M" & r
        gR(r).Tipo = "AMENAZA"
        gR(r).Signo = 1
        gR(r).Prob = 1
        gR(r).ProbRes = 1
        gR(r).FactorRes = 1
    Next r
End Sub

Private Sub PrDist(ByVal r As Long, ByVal cod As Long, ByVal a As Double, ByVal b As Double, ByVal c As Double)
    gDist(r, 1) = cod
    gPar(r, 1, 1) = a
    gPar(r, 1, 2) = b
    gPar(r, 1, 3) = c
End Sub

' 5) Casos en memoria: correlacion, oportunidad y escenario despues.
Public Function PruebaMemoria(ByVal caso As String) As String
    Dim s() As Double, sd() As Double, m1 As Double, m2 As Double
    On Error GoTo EH
    gSinGraficos = True
    Select Case caso
        Case "CORREL"
            PrMemoria 2, 20000
            PrDist 1, D_NORMAL, 1000, 200, 0
            PrDist 2, D_TRIANGULAR, 0, 300, 1000
            gR(1).Grupo = "G": gR(1).Rho = 0.6
            gR(2).Grupo = "G": gR(2).Rho = 0.6
            NucleoSimulacion
            Dim xa() As Double, xb() As Double, ra() As Double, rb() As Double, ixa() As Long
            ColumnaRiesgo 1, 1, gN, xa
            ColumnaRiesgo 2, 1, gN, xb
            RangosPromedio xa, gN, ra, ixa
            RangosPromedio xb, gN, rb, ixa
            PruebaMemoria = "OBJ=0.6|LOG=" & PrNum(gGrupoLog(1)) & "|NG=" & gNG & "|N1=" & gGrupoN(1) & _
                "|SPEARMAN_DIRECTO=" & PrNum(Pearson(ra, rb, gN)) & "|X1=" & PrNum(xa(1)) & ";" & PrNum(xa(2)) & "|X2=" & PrNum(xb(1)) & ";" & PrNum(xb(2))
        Case "OPORT"
            PrMemoria 2, 50000
            PrDist 1, D_PERT, 100, 200, 400
            PrDist 2, D_PERT, 50, 100, 150
            gR(1).Prob = 0.5: gR(2).Prob = 0.4
            NucleoSimulacion
            Ordenados 1, False, s
            m1 = EstMedia(s, gN)
            gR(2).Tipo = "OPORTUNIDAD": gR(2).Signo = -1
            NucleoSimulacion
            Ordenados 1, False, s
            m2 = EstMedia(s, gN)
            gR(2).Signo = 1
            PruebaMemoria = "M_AMENAZA=" & PrNum(m1) & "|M_OPORT=" & PrNum(m2) & "|DIF=" & PrNum(m1 - m2) & _
                            "|DOS_VME=" & PrNum(2 * 0.4 * 100)
        Case "DESPUES"
            PrMemoria 3, 20000
            PrDist 1, D_PERT, 100, 200, 400
            PrDist 2, D_TRIANGULAR, 50, 80, 300
            PrDist 3, D_NORMAL, 500, 100, 0
            gR(1).ProbRes = 0: gR(1).CostoResp = 1000: gR(1).TieneRespuesta = True
            gR(2).ProbRes = 0: gR(2).CostoResp = 2000: gR(2).TieneRespuesta = True
            gR(3).ProbRes = 0: gR(3).TieneRespuesta = True
            gHayDespues = True
            gCostoRespTotal = 3000
            NucleoSimulacion
            Ordenados 1, True, sd
            PruebaMemoria = "P80_DESPUES=" & PrNum(Percentil(sd, gN, 80)) & "|MIN=" & PrNum(sd(1)) & "|MAX=" & PrNum(sd(gN))
    End Select
    Exit Function
EH:
    PruebaMemoria = "ERROR " & Err.Number & ": " & Err.Description & " (" & gEtapa & ")"
End Function

' 6) Casos borde leyendo la hoja.
Public Function PruebaBordes() As String
    Dim errs As String, nErr As Long, res As String, ok As Boolean, r As Long, d As Long
    Dim origen As Range, destino As Range, k As Long, nC As Long, vme1 As Double, vme2 As Double
    On Error GoTo EH
    PrColActivo "R-", "SI"
    PrColActivo "EJ-", "NO"
    hjParametros.Range("Iteraciones").Value = 2000
    ' Min = Max, probabilidad 0 y 1
    PrCelda "R-01", "DIST_COSTO", "TRIANGULAR"
    PrCelda "R-01", "COSTO_P1", 5
    PrCelda "R-01", "COSTO_P2", 5
    PrCelda "R-01", "COSTO_P3", 5
    PrCelda "R-02", "PROBABILIDAD", 0
    PrCelda "R-03", "PROBABILIDAD", 1
    ok = PrLeer(errs, nErr)
    gSinGraficos = True
    If ok Then NucleoSimulacion
    res = "BORDES_OK=" & ok & "|NR=" & gNR & "|OCC_R02=" & gOcc(2) & "|OCC_R03=" & gOcc(3)
    For r = 1 To gNR
        vme1 = vme1 + VME(r, 1)
    Next r
    ' Columnas reordenadas: se copia la tabla invirtiendo el orden de las columnas
    Set origen = hjParametros.Range(PrRango("R_ENC"), PrRango("R_CUERPO"))
    nC = origen.Columns.Count
    Set destino = hjParametros.Range("CA1").Resize(origen.Rows.Count, nC)
    For k = 1 To nC
        destino.Columns(nC - k + 1).Value = origen.Columns(k).Value
    Next k
    ok = LeerModeloDe(destino.Offset(1, 0).Resize(destino.Rows.Count - 1, nC), destino.Rows(1), PrRango("D_CUERPO"), _
                      PrRango("D_ENC"), PrRango("E_CUERPO"), PrRango("E_ENC"), False, errs, nErr)
    For r = 1 To gNR
        vme2 = vme2 + VME(r, 1)
    Next r
    res = res & "|REORDEN_OK=" & ok & "|NR2=" & gNR & "|VME_IGUAL=" & (Abs(vme1 - vme2) < 0.0001)
    destino.ClearContents
    ' Dimension desactivada
    PrRango("D_CUERPO").Cells(4, ColEnc(PrRango("D_ENC").Value, "ACTIVA")).Value = "NO"
    ok = PrLeer(errs, nErr)
    If ok Then NucleoSimulacion
    res = res & "|DESACT_OK=" & ok & "|ND=" & gND
    PrRango("D_CUERPO").Cells(4, ColEnc(PrRango("D_ENC").Value, "ACTIVA")).Value = "SI"
    ' Riesgo sin ninguna distribucion
    PrCelda "R-04", "DIST_COSTO", Empty
    ok = PrLeer(errs, nErr)
    res = res & "|SIN_DIST_ERR=" & (Not ok And InStr(1, errs, "al menos una distribuci") > 0)
    PrCelda "R-04", "DIST_COSTO", "PERT"
    ' Solo EJEMPLO inactivos
    PrColActivo "R-", "NO"
    ok = PrLeer(errs, nErr)
    res = res & "|SIN_ACTIVOS_ERR=" & (Not ok And InStr(1, errs, "No hay riesgos activos") > 0)
    PrColActivo "R-", "SI"
    PruebaBordes = res
    Exit Function
EH:
    PruebaBordes = "ERROR " & Err.Number & ": " & Err.Description & " | " & res
End Function

' 7) Una quinta dimension agregada en la hoja (sin tocar el codigo).
Public Function PruebaQuintaDimension() As String
    Dim errs As String, nErr As Long, encR As Range, cuerpoR As Range, nC As Long, i As Long, k As Long
    Dim cD As Range, eD As Variant, ok As Boolean, cId As Long
    On Error GoTo EH
    PrColActivo "R-", "SI"
    PrColActivo "EJ-", "NO"
    hjParametros.Range("Iteraciones").Value = 2000
    Set cD = PrRango("D_CUERPO")
    eD = PrRango("D_ENC").Value
    cD.Cells(5, ColEnc(eD, "CLAVE")).Value = "CALIDAD"
    cD.Cells(5, ColEnc(eD, "NOMBRE")).Value = "Calidad (no conformidades)"
    cD.Cells(5, ColEnc(eD, "UNIDAD")).Value = "NCR"
    cD.Cells(5, ColEnc(eD, "FORMATO")).Value = "#,##0.0"
    cD.Cells(5, ColEnc(eD, "ACTIVA")).Value = "SI"
    Set encR = PrRango("R_ENC")
    Set cuerpoR = PrRango("R_CUERPO")
    nC = encR.Columns.Count
    encR.Cells(1, nC + 1).Resize(1, 5).Value = Array("DIST_CALIDAD", "CALIDAD_P1", "CALIDAD_P2", "CALIDAD_P3", "CALIDAD_P4")
    cId = ColEnc(encR.Value, "ID")
    For i = 1 To cuerpoR.Rows.Count
        k = 0
        Select Case Txt(cuerpoR.Cells(i, cId).Value)
            Case "R-06", "R-07", "R-08": k = 1
        End Select
        If k = 1 Then
            cuerpoR.Cells(i, nC + 1).Value = "POISSON"
            cuerpoR.Cells(i, nC + 2).Value = 3
        End If
    Next i
    ok = LeerModeloDe(cuerpoR.Resize(, nC + 5), encR.Resize(, nC + 5), PrRango("D_CUERPO"), PrRango("D_ENC"), _
                      PrRango("E_CUERPO"), PrRango("E_ENC"), False, errs, nErr)
    If Not ok Then
        PruebaQuintaDimension = "ERROR " & errs
        Exit Function
    End If
    gSinGraficos = True
    NucleoSimulacion
    PruebaQuintaDimension = PrResumen()
    Exit Function
EH:
    PruebaQuintaDimension = "ERROR " & Err.Number & ": " & Err.Description
End Function

' 8) Validacion con datos erroneos en filas libres.
Public Function PruebaValidacion() As String
    Dim cuerpo As Range, enc As Variant, f As Long, errs As String, nErr As Long, ok As Boolean
    On Error GoTo EH
    Set cuerpo = PrRango("R_CUERPO")
    enc = PrRango("R_ENC").Value
    f = 40
    cuerpo.Cells(f, ColEnc(enc, "ID")).Value = "X-1"
    cuerpo.Cells(f, ColEnc(enc, "NOMBRE DEL RIESGO")).Value = "Moda fuera de rango"
    cuerpo.Cells(f, ColEnc(enc, "ACTIVO")).Value = "SI"
    cuerpo.Cells(f, ColEnc(enc, "PROBABILIDAD")).Value = 0.3
    cuerpo.Cells(f, ColEnc(enc, "DIST_COSTO")).Value = "PERT"
    cuerpo.Cells(f, ColEnc(enc, "COSTO_P1")).Value = 10
    cuerpo.Cells(f, ColEnc(enc, "COSTO_P2")).Value = 50
    cuerpo.Cells(f, ColEnc(enc, "COSTO_P3")).Value = 20
    cuerpo.Cells(f + 1, ColEnc(enc, "ID")).Value = "X-2"
    cuerpo.Cells(f + 1, ColEnc(enc, "NOMBRE DEL RIESGO")).Value = "Probabilidad mala y DISCRETA que no suma 1"
    cuerpo.Cells(f + 1, ColEnc(enc, "PROBABILIDAD")).Value = 1.5
    cuerpo.Cells(f + 1, ColEnc(enc, "DIST_PLAZO")).Value = "DISCRETA"
    cuerpo.Cells(f + 1, ColEnc(enc, "PLAZO_P1")).Value = "0;10;20"
    cuerpo.Cells(f + 1, ColEnc(enc, "PLAZO_P2")).Value = "0.5;0.3;0.1"
    cuerpo.Cells(f + 2, ColEnc(enc, "ID")).Value = "X-3"
    cuerpo.Cells(f + 2, ColEnc(enc, "NOMBRE DEL RIESGO")).Value = "Distribucion desconocida y rho fuera de rango"
    cuerpo.Cells(f + 2, ColEnc(enc, "DIST_ING_CAMPO")).Value = "GAMMA2"
    cuerpo.Cells(f + 2, ColEnc(enc, "GRUPO_CORRELACION")).Value = "X"
    cuerpo.Cells(f + 2, ColEnc(enc, "RHO_GRUPO")).Value = 1.2
    cuerpo.Cells(f + 3, ColEnc(enc, "ID")).Value = "X-4"
    cuerpo.Cells(f + 3, ColEnc(enc, "NOMBRE DEL RIESGO")).Value = "PARETO sin media"
    cuerpo.Cells(f + 3, ColEnc(enc, "DIST_COSTO")).Value = "PARETO"
    cuerpo.Cells(f + 3, ColEnc(enc, "COSTO_P1")).Value = 0.8
    cuerpo.Cells(f + 3, ColEnc(enc, "COSTO_P2")).Value = 100
    cuerpo.Cells(f + 4, ColEnc(enc, "ID")).Value = "X-5"
    cuerpo.Cells(f + 4, ColEnc(enc, "NOMBRE DEL RIESGO")).Value = "Inactivo con errores"
    cuerpo.Cells(f + 4, ColEnc(enc, "ACTIVO")).Value = "NO"
    cuerpo.Cells(f + 4, ColEnc(enc, "DIST_COSTO")).Value = "XYZ"
    ok = LeerModeloDe(cuerpo, PrRango("R_ENC"), PrRango("D_CUERPO"), PrRango("D_ENC"), _
                      PrRango("E_CUERPO"), PrRango("E_ENC"), True, errs, nErr)
    PruebaValidacion = "OK=" & ok & "|NERR=" & nErr & "|ROJO=" & _
        (cuerpo.Cells(f, ColEnc(enc, "COSTO_P2")).Interior.Color = COLOR_ERROR) & "|ERRS=" & Replace(errs, vbLf, " / ") & _
        "|ADV=" & Replace(gAdvert, vbLf, " / ")
    cuerpo.Rows(f).Resize(5).ClearContents
    Exit Function
EH:
    PruebaValidacion = "ERROR " & Err.Number & ": " & Err.Description
End Function

Public Function PruebaDiag(ByVal nn As Long, ByVal rr As Long) As String
    Dim paso As String
    On Error GoTo EH
    gN = nn: gNR = rr: gND = 1
    paso = "gM": ReDim gM(1 To gN, 1 To gNR, 1 To gND)
    paso = "gM asignar": gM(5, 2, 1) = 3
    paso = "gOcc": ReDim gOcc(1 To gNR)
    paso = "local3d"
    Dim x() As Double
    ReDim x(1 To gN, 1 To gNR, 1 To gND)
    PruebaDiag = "OK"
    Exit Function
EH:
    PruebaDiag = "falla en " & paso & ": " & Err.Description
End Function

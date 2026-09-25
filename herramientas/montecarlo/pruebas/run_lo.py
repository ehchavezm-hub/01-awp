"""Ejecuta funciones del modulo VBA dentro de LibreOffice (modo compatibilidad VBA)."""
import subprocess, time, sys, os, uno
from com.sun.star.beans import PropertyValue

def pv(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p

def main(path, calls):
    proc = subprocess.Popen(["soffice", "--headless", "--norestore", "--nologo",
        "--accept=socket,host=localhost,port=2002;urp;"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ctx = None
    for _ in range(60):
        try:
            local = uno.getComponentContext()
            res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
            ctx = res.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"); break
        except Exception:
            time.sleep(1)
    desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(path)), "_blank", 0,
                                    (pv("Hidden", True), pv("MacroExecutionMode", 4)))
    libs = doc.BasicLibraries
    print("Bibliotecas Basic:", libs.getElementNames())
    for ln in libs.getElementNames():
        lib = libs.getByName(ln)
        print(" ", ln, "->", lib.getElementNames())
    sp = doc.getScriptProvider()
    out = []
    for name, args in calls:
        url = "vnd.sun.star.script:VBAProject.MonteCarlo.%s?language=Basic&location=document" % name
        t0 = time.time()
        try:
            r = sp.getScript(url).invoke(tuple(args), (), ())[0]
        except Exception as e:
            r = "EXCEPCION: %s" % e
        out.append(r)
        print("%s%s [%.1fs] => %s" % (name, tuple(args), time.time() - t0, r))
    if os.environ.get('SAVE_AS'):
        doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(os.environ['SAVE_AS'])), (pv('FilterName', 'Calc MS Excel 2007 XML'),))
    doc.close(True)
    try: desk.terminate()
    except Exception: pass
    proc.wait(timeout=30)
    return out

if __name__ == "__main__":
    main(sys.argv[1], [("PruebaBordes", [])])

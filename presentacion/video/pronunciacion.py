"""Respelación fonética para la voz sintética (español latinoamericano).

El modelo lee con reglas del español: las siglas se deletrean como se dicen en voz alta
y los términos en inglés se escriben como los pronuncia un hablante latinoamericano.
Solo afecta al audio; los subtítulos usan el texto original.
"""
import re

# Frases más largas primero para que no las corte una regla más corta.
REGLAS = [
    ("Construction Industry Institute", "constrácshon índastri ínstitiut"),
    ("Lean Construction Institute", "lin constrácshon ínstitiut"),
    ("Advanced Work Packaging", "advánst uork pákeyin"),
    ("Construction Work Package", "constrácshon uork pákech"),
    ("Construction Work Area", "constrácshon uork éria"),
    ("Engineering Work Package", "enyiníring uork pákech"),
    ("Procurement Work Package", "procíurment uork pákech"),
    ("Procurement Work Number", "procíurment uork námber"),
    ("Installation Work Package", "instaléishon uork pákech"),
    ("System Work Package", "sístem uork pákech"),
    ("Turnover Packages", "térnouver pákeches"),
    ("Turnover Package", "térnouver pákech"),
    ("Information Management", "informéishon mánashment"),
    ("Workface Planning", "uórkfeis plánin"),
    ("Workface Planner", "uórkfeis pláner"),
    ("Path of Construction", "paz of constrácshon"),
    ("Construction Manager", "constrácshon mánayer"),
    ("Lean Construction", "lin constrácshon"),
    ("Front End Loading", "front end lóuding"),
    ("Insight AWP", "ínsait a doble u pe"),
    ("Pack Track", "pak trak"),
    ("look ahead", "luk ajéd"),
    ("Champion", "chámpion"),
    ("backlog", "báklog"),
    ("software", "sóftuer"),
    ("coach", "couch"),
    ("dossier", "dosier"),
    ("Lean", "lin"),
    ("tres D", "tres de"),
]

SIGLAS = {
    "AWP": "a doble u pe", "CWA": "ce doble u a", "CWP": "ce doble u pe", "EWP": "e doble u pe",
    "PWP": "pe doble u pe", "IWP": "i doble u pe", "SWP": "ese doble u pe", "WFP": "doble u efe pe",
    "POC": "pe o ce", "CII": "ce i i", "COAA": "ce o a a", "FEL": "fel", "FEED": "fid",
    "WBS": "doble u be ese", "EPC": "e pe ce",
}


def pronunciar(texto):
    for original, dicho in REGLAS:
        texto = re.sub(rf"\b{re.escape(original)}\b", dicho, texto)
    for sigla, dicho in SIGLAS.items():
        texto = re.sub(rf"\b{sigla}s?\b", dicho, texto)
    return texto

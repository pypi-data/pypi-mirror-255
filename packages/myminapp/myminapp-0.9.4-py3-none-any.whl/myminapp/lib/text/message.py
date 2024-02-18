# -*- coding: utf-8 -*-
"""
myminapp

In this file message texts are specified. Currently supported languages
are English (default) and German.

Use method get_text via wrapper method helper.mtext to get the text
for a code, optionally including variable content given as arguments.

For more information see myminapp manual.
"""

from myminapp.appdef import LANG

# ------------------
# Message log levels
# ------------------
ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"
DEBUG = "DEBUG"

# --------------------------------------
# Message codes related to the log level
# --------------------------------------
ERROR_CODES = [1,
             101, 105, 111, 112, 115, 116, 119, 123, 131, 132, 141, 143,
             201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
             211, 212, 213, 214, 215, 216, 221,
             501, 502, 503, 504, 505,
             902]

WARNING_CODES = [2, 106, 121, 222, 223]

DEBUG_CODES = [3, 107, 130, 140]

EN = {

    # ----------------
    # General (0 - 49)
    # ----------------
    0:"OK",
    1:"Error: %s",
    2:"Warning: %s",
    3:"No data",

    # -------------------------------
    # Application process (100 - 199)
    # -------------------------------
    100:"Application instance '%s' was started with process ID %i.",
    101:"Process %i cannot be run: %s",
    102:"Process %i will be terminated. Signal number: %i.",
    103:"State: %s",
    104:'Info: %s',
    105:"Error: %s",
    106:"Warning: %s",
    107:"Debug: %s",
    108:"Scheduler started (%s).",

    110:"Added command '%s' to the cache.",
    111:"Cannot find the configuration for command '%s'.",
    112:"Detected an incorrect configuration for command '%s'.",
    113:"Closing commands in the cache...",
    114:"Closed command '%s'.",
    115:"Could not close command '%s': %s",
    116:"Error when closing commands: %s",
    117:"Closed commands.",
    118:"Closing schedulers...",
    119:"Error when closing schedulers: %s",
    120:"Closed schedulers.",
    121:"Timeout when closing schedulers.",
    122:"Closing monitor...",
    123:"Error when closing monitor: %s",
    124:"Closed monitor.",

    130:"Request '%s' performed in %i ms: Number of result entries: %i "\
                                "(%i OK, %i errors, %i warnings).",
    131:"Request failed: %s",
    132:"Invalid result code at command '%s', entry #%i: %i",

    140:"%s, %s, action #%i performed.",
    141:"%s, %s, action #%i failed: %s",
    142:"%s, %s, action #%i discarded.",
    143:"%s, %s, invalid action number from scheduler: %i",

    150:"Appserver %s. Stop with Ctrl+C.",
    151:"Appserver received stop request...",

    # --------------------
    # Commands (200 - 499)
    # --------------------
    200:"Command '%s' performed in %i ms: Number of result entries: %i "\
                                "(%i OK, %i errors, %i warnings).",
    201:"Command failed: %s",
    202:"Missing command.",
    203:"Unsupported command: %s",
    204:"Missing parameter(s) for command '%s': %s",
    205:"Unsupported parameter for command '%s': %s",
    206:"No entry with matching parameters.",
    207:"Unconfigured device name: %s",
    208:"Unsupported device class: %s",
    209:"Unsupported or deviating category for device '%s': %s",
    210:"Unsupported device brand: %s",
    211:"Unknown defintion part: %s (%s)",
    212:"Unsupported chart type: %s",
    213:"Unsupported type for command '%s': %s",
    214:"Only with device category '%s' supported type for command '%s': %s",
    215:"Invalid value for parameter '%s' at command '%s': %s",
    216:"Command name '%s' or COMMAND_DEFSET configuration invalid.",

    221:"Error at command '%s', entry #%i: %s, trace: %s",
    222:"Warning at command '%s', entry #%i: %s, trace: %s",
    223:"No data at command '%s', entry #%i: %s, trace: %s",

    # -------------------
    # Devices (500 - 799)
    # -------------------
    501:"Invalid set value: %s",
    502:"Invalid set parameter for category '%s': %s",
    503:"Unsupported device brand for device '%s': %s",
    504:"Missing specification for device class '%s'",
    505:"Missing parameter '%s' for device class specification '%s'",

    # ---------------------
    # Utilities (800 - 999)
    # ---------------------
    900:"Created logger '%s' with handler(s): %s",
    901:"Logger '%s' is closed.",
    902:"Logger '%s' could not be closed regularly: %s",

}

DE = {

    # ----------------
    # General (0 - 49)
    # ----------------
    0:'OK',
    1:"Fehler: %s",
    2:"Warnung: %s",
    3:"Keine Daten",

    # -------------------------------
    # Application process (100 - 199)
    # -------------------------------
    100:"Applikationsinstanz '%s' wurde mit Prozess-ID %i gestartet.",
    101:"Prozess %i kann nicht ausgeführt werden: %s",
    102:"Prozess %i wird beendet. Signal-Nummer: %i.",
    103:"Status: %s",
    104:'Info: %s',
    105:"Fehler: %s",
    106:"Warnung: %s",
    107:"Debug: %s",
    108:"Scheduler gestartet (%s).",

    110:"Command '%s' dem Cache hinzugefügt.",
    111:"Kann die Konfiguration für Command '%s' nicht finden.",
    112:"Fehlerhafte Konfiguration für Command '%s' festgestellt.",
    113:"Schließe Commands im Cache...",
    114:"Command '%s' geschlossen.",
    115:"Konnte Command '%s' nicht schließen: %s",
    116:"Fehler beim Schließen der Commands: %s",
    117:"Commands geschlossen.",
    118:"Schließe Scheduler...",
    119:"Fehler beim Schließen der Scheduler: %s",
    120:"Scheduler geschlossen.",
    121:"Timeout beim Schließen der Scheduler.",
    122:"Schließe Monitor...",
    123:"Fehler beim Schließen des Monitors: %s",
    124:"Monitor geschlossen.",

    130:"Anfrage '%s' bearbeitet in %i ms. Anzahl Resultateinträge: %i "\
                                "(%i OK, %i Fehler, %i Warnungen).",
    131:"Anfrage fehlgeschlagen: %s",
    132:"Ungültiger Resultcode bei Command '%s', Eintrag #%i: %i",

    140:"%s, %s, Aktion #%i ausgeführt.",
    141:"%s, %s, Aktion #%i fehlgeschlagen: %s",
    142:"%s, %s, Aktion #%i verworfen.",
    143:"%s, %s, ungültige Aktionsnummer vom Scheduler: %i",

    150:"Appserver %s. Beenden mit Strg+C.",
    151:"Appserver hat Stop-Anfrage erhalten...",

    # --------------------
    # Commands (200 - 499)
    # --------------------
    200:"Command '%s' bearbeitet in %i ms. Anzahl Resultateinträge: %i "\
                                "(%i OK, %i Fehler, %i Warnungen).",
    201:"Command fehlgeschlagen: %s",
    202:"Fehlender Command.",
    203:"Nicht unterstützter Command: %s",
    204:"Fehlende(r) Parameter für Command '%s': %s",
    205:"Nicht unterstützter Parameter für Command '%s': %s",
    206:"Kein Eintrag mit übereinstimmenden Parametern.",
    207:"Nicht konfigurierter Device-Name: %s",
    208:"Nicht unterstützte Device-Klasse: %s",
    209:"Nicht unterstützte oder abweichende Kategorie für Device '%s': %s",
    210:"Nicht unterstützte Device-Marke: %s",
    211:"Unbekannter Definitionsbestandteil: %s (%s)",
    212:"Nicht unterstützter Chart-Typ: %s",
    213:"Nicht unterstützter Typ für Command '%s': %s",
    214:"Nur mit Device-Kategorie '%s' unterstützter Typ für Command '%s': %s",
    215:"Ungültiger Wert für Parameter '%s' bei Command '%s': %s",
    216:"Command-Name '%s' oder COMMAND_DEFSET-Konfiguration ungültig.",

    221:"Fehler bei Command '%s', Eintrag #%i: %s, Trace: %s",
    222:"Warnung bei Command '%s', Eintrag #%i: %s, Trace: %s",
    223:"Keine Daten bei Command  '%s', entry #%i: %s, trace: %s",

    # -------------------
    # Devices (500 - 799)
    # -------------------
    501:"Ungültiger Set-Wert: %s",
    502:"Ungültiger Set-Parameter für Kategorie '%s': %s",
    503:"Nicht unterstützte Device-Marke für Device-Klasse '%s': %s",
    504:"Fehlende Spezifikation für Device-Klasse '%s'",
    505:"Fehlender Parameter '%s' für Device-Klassen-Spezifikation '%s'",

    # ---------------------
    # Utilities (800 - 999)
    # ---------------------
    900:"Logger '%s' erstellt mit Handler(n): %s",
    901:"Logger '%s' wird geschlossen.",
    902:"Logger '%s' konnte nicht regulär geschlossen werden: %s",

}

def get_text(code:int, *args):
    """Gets a text matching the given code and the configured language.

    Args:
        code (int): Message code.
        *args (tuple): Optional variable arguments.
    
    Returns:
       str: The message text or None if not found.
    """
    text = None
    # -----------------------
    # Non default language(s)
    # -----------------------
    if LANG == 'de':
        text = DE.get(code)
    #elif...
    # ----------------
    # Default language
    # ----------------
    if text is None:
        text = EN.get(code)
    # -------------
    # Optional args
    # -------------
    if text is not None:
        if args is not None:
            text = text % (args)
    # ------
    # Return
    # ------
    return text

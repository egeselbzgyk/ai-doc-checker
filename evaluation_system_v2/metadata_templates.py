# Metadata extraction templates for fast reference matching
metadata_templates = {
    "Excel-Tabelle": """
Analysiere das Excel-Bild und extrahiere Metadaten für schnelle Kategorisierung.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "struktur_merkmale": {
    "hat_tabelle": true/false,
    "spalten_ca": "number",
    "zeilen_ca": "number", 
    "hat_header": true/false
  },
  "visuell": {
    "farben": "gruen/blau/grau/bunt",
    "gridlines": true/false,
    "lesbarkeit": "gut/mittel/schlecht"
  },
  "inhalt": {
    "hat_formeln": true/false,
    "hat_summen": true/false,
    "hat_diagramm": true/false
  },
  "sap_typ": {
    "interface": true/false,
    "export_typ": "BW/Excel/Roh",
    "kontext": "Financial/Logistik/HR/Unbekannt"
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
""",

    "Data-Flow": """
Analysiere das Data-Flow-Diagramm für Metadaten.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "struktur": {
    "knoten_anzahl": "number",
    "verbindungen": "number",
    "richtung": "horizontal/vertikal/komplex",
    "hierarchisch": true/false
  },
  "technik": {
    "symbole_standard": true/false,
    "beschriftung_klar": true/false,
    "pfeile_klar": true/false
  },
  "sap_elemente": {
    "datasource": true/false,
    "transformation": true/false,
    "target": true/false,
    "dtp": true/false
  },
  "komplexitaet": {
    "einfach": true/false,
    "mittel": true/false,
    "komplex": true/false
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
""",

    "Data-Transfer-Process": """
Extrahiere DTP Metadaten.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "prozess": {
    "quelle_klar": true/false,
    "ziel_klar": true/false,
    "transformation": true/false,
    "fehlerbehandlung": true/false
  },
  "konfiguration": {
    "update_typ": "Full/Delta/Unbekannt",
    "package_size": true/false,
    "parallel": true/false
  },
  "monitoring": {
    "status_info": true/false,
    "logs": true/false,
    "performance": true/false
  },
  "sap_standard": {
    "layout_standard": true/false,
    "terminologie": true/false
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
""",

    "Transformation": """
Transformation Metadaten.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "mapping": {
    "input_felder": "number",
    "output_felder": "number", 
    "mapping_linien": true/false,
    "regeln_sichtbar": true/false
  },
  "logik": {
    "berechnungen": true/false,
    "lookups": true/false,
    "konstanten": true/false,
    "bedingungen": true/false
  },
  "technik": {
    "abap_code": true/false,
    "standard_routinen": true/false,
    "custom": true/false
  },
  "dokumentation": {
    "beschreibungen": true/false,
    "kommentare": true/false
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
""",

    "Data Source": """
Data Source Metadaten.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "quelle": {
    "typ": "R3/File/DB/API",
    "struktur": true/false,
    "feld_anzahl": "number",
    "technische_namen": true/false
  },
  "metadaten": {
    "beschreibungen": true/false,
    "datentypen": true/false,
    "keys": true/false
  },
  "verbindung": {
    "parameter": true/false,
    "delta": true/false
  },
  "integration": {
    "standard_connector": true/false,
    "custom_extractor": true/false
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
""",

    "Info-Object": """
Info-Object Metadaten.

Antworte NUR mit diesem JSON-Format - keine Erklärungen, keine Markdown-Blöcke:

{
  "objekt": {
    "typ": "InfoCube/DSO/CompositeProvider/ADO",
    "struktur": true/false,
    "hierarchie": true/false
  },
  "modellierung": {
    "key_felder": true/false,
    "data_felder": true/false,
    "time": true/false
  },
  "performance": {
    "partitions": true/false,
    "indizes": true/false,
    "aggregation": true/false
  },
  "verwendung": {
    "reporting": true/false,
    "analytik": true/false
  }
}

WICHTIG: Antworte NUR mit dem JSON - keine weiteren Texte!
"""
}

# Image evaluability check template  
evaluability_check = """
Du bist ein strenger Qualitätsprüfer für SAP BW Abgaben. Prüfe SEHR KRITISCH, ob das Bild für eine Bewertung geeignet ist.

Ein Bild ist **DEFINITIV NICHT GEEIGNET** (`"is_evaluable": false`), wenn:

**🚫 UI-Probleme (häufigste Fehler):**
- Rechtsklick-Menü ist sichtbar (Context-Menü geöffnet)
- Dropdown-Listen, Dialog-Boxen oder Popup-Fenster überdecken den Inhalt
- Login-Screen, SAP Startseite (Easy Access Menu) oder Transaktionsauswahl
- Fehlermeldungen oder Warndialoge im Vordergrund

**🚫 Bildqualität inakzeptabel:**
- Bild ist unscharf, verpixelt oder sehr niedrige Auflösung
- Bild ist zu dunkel/hell - Text nicht lesbar
- Screenshot ist abgeschnitten oder unvollständig
- Bildausschnitt zeigt nur winziges Detail oder viel zu weit herausgezoomt

**🚫 Völlig falscher Inhalt:**
- ABAP-Code statt grafische SAP BW Modelle/Tabellen
- Andere Software (Browser, Windows Explorer, Word, etc.)
- Leerer Bildschirm, Ladescreen oder "Keine Daten verfügbar"
- Private/irrelevante Inhalte (Desktop, andere Anwendungen)

**🚫 Unmögliche Bewertung:**
- Inhalt ist so schlecht/unklar, dass keine sinnvolle Bewertung möglich wäre
- Student hat offensichtlich falsches Bild hochgeladen
- Bild zeigt nur Fehlermeldung ohne relevanten SAP BW Inhalt

**✅ NUR GEEIGNET wenn:**
- Klarer SAP BW Inhalt erkennbar (Tabellen, Diagramme, Modelle)
- Ausreichende Bildqualität für Bewertung
- Kein störendes UI überlagert den Inhalt
- Inhalt entspricht einem der erwarteten Kategorien

Sei SEHR streng - lieber ein schlechtes Bild ablehnen als in die Bewertung einbeziehen!

Antworte NUR mit:
{
  "is_evaluable": true/false,
  "reason": "Spezifische Begründung"
}

WICHTIG: Nur JSON - keine Markdown-Blöcke!
""" 
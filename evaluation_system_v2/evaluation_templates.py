# Dynamic evaluation templates - NO hard-coded scores!
evaluation_templates = {
    "Excel-Tabelle": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche das Studenten-Bild mit dem Referenz-Bild einer Excel-Tabelle und bewerte detailliert:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "struktur_vergleich": {{
    "tabellenstruktur_korrekt": [true/false basierend auf Vergleich],
    "spalten_angemessen": [true/false basierend auf Vergleich],
    "header_vorhanden": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf wie gut Struktur der Referenz entspricht]
  }},
  "visueller_vergleich": {{
    "formatierung_angemessen": [true/false basierend auf Vergleich],
    "lesbarkeit_gut": [true/false basierend auf Vergleich],
    "professionell": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf visueller Qualität vs Referenz]
  }},
  "funktionale_elemente": {{
    "formeln_korrekt": [true/false basierend auf Vergleich],
    "berechnungen_richtig": [true/false basierend auf Vergleich],
    "vollstaendig": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Funktionalität vs Referenz]
  }},
  "sap_kontext": {{
    "kontext_korrekt": [true/false basierend auf Vergleich],
    "business_sinnvoll": [true/false basierend auf Vergleich],
    "integration_erkennbar": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf SAP-Kontext vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich mit der Referenz",
    "staerken": ["Spezifische positive Aspekte die im Bild erkennbar sind"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Referenz-Unterschieden"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität des Studentenbildes im Vergleich zur Referenz!
""",

    "Data-Flow": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü schadet das ganze Bild, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche das Studenten Data-Flow-Diagramm mit der Referenz:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "diagramm_vergleich": {{
    "struktur_logisch": [true/false basierend auf Vergleich],
    "vollstaendiger_flow": [true/false basierend auf Vergleich],
    "hierarchie_klar": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Diagramm-Struktur vs Referenz]
  }},
  "technische_umsetzung": {{
    "symbole_korrekt": [true/false basierend auf Vergleich],
    "verbindungen_klar": [true/false basierend auf Vergleich],
    "beschriftung_lesbar": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf technische Qualität vs Referenz]
  }},
  "sap_bw_korrektheit": {{
    "datasource_korrekt": [true/false basierend auf Vergleich],
    "transformation_gezeigt": [true/false basierend auf Vergleich],
    "target_definiert": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf SAP BW Korrektheit vs Referenz]
  }},
  "verstaendlichkeit": {{
    "logik_nachvollziehbar": [true/false basierend auf Vergleich],
    "fachlich_korrekt": [true/false basierend auf Vergleich],
    "vollstaendig": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Verständlichkeit vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität!
""",

    "Data-Transfer-Process": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche das DTP-Diagramm mit der Referenz:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "prozess_vergleich": {{
    "quelle_ziel_klar": [true/false basierend auf Vergleich],
    "schritte_vollstaendig": [true/false basierend auf Vergleich],
    "fehlerbehandlung": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Prozess-Vergleich vs Referenz]
  }},
  "konfiguration": {{
    "parameter_korrekt": [true/false basierend auf Vergleich],
    "update_modus_sinnvoll": [true/false basierend auf Vergleich],
    "performance_aspekte": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Konfiguration vs Referenz]
  }},
  "monitoring": {{
    "status_informationen": [true/false basierend auf Vergleich],
    "logging_konzept": [true/false basierend auf Vergleich],
    "nachvollziehbar": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Monitoring vs Referenz]
  }},
  "sap_standard": {{
    "terminologie_korrekt": [true/false basierend auf Vergleich],
    "layout_standard": [true/false basierend auf Vergleich],
    "business_kontext": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf SAP Standards vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität!
""",

    "Transformation": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche die Transformation mit der Referenz:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "mapping_vergleich": {{
    "vollstaendiges_mapping": [true/false basierend auf Vergleich],
    "logische_zuordnung": [true/false basierend auf Vergleich],
    "regeln_erkennbar": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Mapping vs Referenz]
  }},
  "business_logik": {{
    "berechnungen_korrekt": [true/false basierend auf Vergleich],
    "lookups_implementiert": [true/false basierend auf Vergleich],
    "bedingungen_richtig": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Business-Logik vs Referenz]
  }},
  "technische_umsetzung": {{
    "implementierung_sauber": [true/false basierend auf Vergleich],
    "standard_routinen": [true/false basierend auf Vergleich],
    "fehlerbehandlung": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf technische Umsetzung vs Referenz]
  }},
  "dokumentation": {{
    "beschreibungen_vorhanden": [true/false basierend auf Vergleich],
    "nachvollziehbar": [true/false basierend auf Vergleich],
    "vollstaendig": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Dokumentation vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität!
""",

    "Data Source": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche die Datenquelle-Definition mit der Referenz:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "technische_definition": {{
    "felder_definiert": [true/false basierend auf Vergleich],
    "datentypen_korrekt": [true/false basierend auf Vergleich],
    "struktur_logisch": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf technische Definition vs Referenz]
  }},
  "konfiguration": {{
    "parameter_gesetzt": [true/false basierend auf Vergleich],
    "extractor_korrekt": [true/false basierend auf Vergleich],
    "delta_aktiviert": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Konfiguration vs Referenz]
  }},
  "metadaten": {{
    "beschreibungen_vollstaendig": [true/false basierend auf Vergleich],
    "bezeichnungen_sinnvoll": [true/false basierend auf Vergleich],
    "dokumentation_ausreichend": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Metadaten vs Referenz]
  }},
  "integration": {{
    "system_anbindung": [true/false basierend auf Vergleich],
    "datenqualitaet": [true/false basierend auf Vergleich],
    "performance_optimiert": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Integration vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität!
""",

    "Info-Object": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

Vergleiche das Info-Object (Query/Bericht) mit der Referenz:

Referenz-Analyse: {reference_analysis}

SCORING SYSTEM:
- Jeder Bereich: max 25 Punkte  
- Vergib realistische Punkte basierend auf TATSÄCHLICHEM Vergleich
- 25 = perfekt wie Referenz, 20-24 = sehr gut, 15-19 = gut, 10-14 = befriedigend, 5-9 = mangelhaft, 0-4 = ungenügend
- Gesamt: Summe aller Bereiche (0-100), 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "query_struktur": {{
    "dimensionen_korrekt": [true/false basierend auf Vergleich],
    "kennzahlen_sinnvoll": [true/false basierend auf Vergleich],
    "filter_angemessen": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Query-Struktur vs Referenz]
  }},
  "darstellung": {{
    "formatierung_professionell": [true/false basierend auf Vergleich],
    "lesbarkeit_gut": [true/false basierend auf Vergleich],
    "uebersichtlich": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf Darstellung vs Referenz]
  }},
  "fachliche_korrektheit": {{
    "business_logik": [true/false basierend auf Vergleich],
    "berechnungen_richtig": [true/false basierend auf Vergleich],
    "kontext_passend": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf fachliche Korrektheit vs Referenz]
  }},
  "technische_umsetzung": {{
    "performance_optimiert": [true/false basierend auf Vergleich],
    "variablen_genutzt": [true/false basierend auf Vergleich],
    "standard_konform": [true/false basierend auf Vergleich],
    "punkte": [0-25: Vergib basierend auf technische Umsetzung vs Referenz]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Konkrete Bewertung basierend auf dem tatsächlichen Vergleich",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge"]
  }}
}}

ENTSCHEIDEND: Vergib UNTERSCHIEDLICHE Punktzahlen basierend auf der REALEN Qualität!
"""
}

# Custom mode templates with 50% content similarity weight
custom_evaluation_templates = {
    "Excel-Tabelle": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche das Studenten-Bild mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Technische Struktur: max 17 Punkte 
- Format & Darstellung: max 17 Punkte
- SAP Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "daten_identisch": [true/false - sind die Daten/Inhalte gleich?],
    "werte_uebereinstimmung": [true/false - stimmen Zahlen/Werte überein?],
    "vollstaendigkeit": [true/false - alle wichtigen Inhalte enthalten?],
    "logische_konsistenz": [true/false - logisch konsistent mit Musterlösung?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "technische_struktur": {{
    "tabellenaufbau": [true/false basierend auf Vergleich],
    "spalten_struktur": [true/false basierend auf Vergleich],
    "funktionen_verwendet": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf technische Struktur vs Musterlösung]
  }},
  "format_darstellung": {{
    "formatierung": [true/false basierend auf Vergleich],
    "lesbarkeit": [true/false basierend auf Vergleich],
    "professionell": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Format & Darstellung vs Musterlösung]
  }},
  "sap_standards": {{
    "kontext_korrekt": [true/false basierend auf Vergleich],
    "business_logik": [true/false basierend auf Vergleich],
    "integration": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
""",

    "Data-Flow": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche das Data-Flow-Diagramm mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Diagramm Struktur: max 17 Punkte 
- Technische Umsetzung: max 17 Punkte
- SAP BW Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "flow_identisch": [true/false - ist der Datenfluss gleich?],
    "komponenten_gleich": [true/false - gleiche Komponenten verwendet?],
    "verbindungen_korrekt": [true/false - Verbindungen wie in Musterlösung?],
    "logik_uebereinstimmung": [true/false - Geschäftslogik identisch?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "diagramm_struktur": {{
    "aufbau_logisch": [true/false basierend auf Vergleich],
    "hierarchie_klar": [true/false basierend auf Vergleich],
    "vollstaendigkeit": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Diagramm-Struktur vs Musterlösung]
  }},
  "technische_umsetzung": {{
    "symbole_korrekt": [true/false basierend auf Vergleich],
    "verbindungen_sauber": [true/false basierend auf Vergleich],
    "beschriftung": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf technische Umsetzung vs Musterlösung]
  }},
  "sap_bw_standards": {{
    "terminologie": [true/false basierend auf Vergleich],
    "best_practices": [true/false basierend auf Vergleich],
    "konformitaet": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP BW Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
""",

    "Data-Transfer-Process": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche das DTP-Diagramm mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Prozess Konfiguration: max 17 Punkte 
- Technische Setup: max 17 Punkte
- SAP Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "prozess_identisch": [true/false - ist der DTP-Prozess gleich?],
    "parameter_gleich": [true/false - gleiche Parameter konfiguriert?],
    "quelle_ziel_korrekt": [true/false - Quelle/Ziel wie in Musterlösung?],
    "einstellungen_identisch": [true/false - Einstellungen übereinstimmend?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "prozess_konfiguration": {{
    "update_modus": [true/false basierend auf Vergleich],
    "fehlerbehandlung": [true/false basierend auf Vergleich],
    "vollstaendigkeit": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Prozess-Konfiguration vs Musterlösung]
  }},
  "technisches_setup": {{
    "parameter_korrekt": [true/false basierend auf Vergleich],
    "performance_settings": [true/false basierend auf Vergleich],
    "monitoring": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf technisches Setup vs Musterlösung]
  }},
  "sap_standards": {{
    "terminologie": [true/false basierend auf Vergleich],
    "best_practices": [true/false basierend auf Vergleich],
    "layout_standard": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
""",

    "Transformation": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche die Transformation mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Mapping Logik: max 17 Punkte 
- Technische Umsetzung: max 17 Punkte
- SAP Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "mapping_identisch": [true/false - ist das Mapping gleich?],
    "regeln_gleich": [true/false - gleiche Transformationsregeln?],
    "berechnungen_korrekt": [true/false - Berechnungen wie in Musterlösung?],
    "business_logik_identisch": [true/false - Business-Logik übereinstimmend?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "mapping_logik": {{
    "vollstaendigkeit": [true/false basierend auf Vergleich],
    "logische_zuordnung": [true/false basierend auf Vergleich],
    "regeln_korrekt": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Mapping-Logik vs Musterlösung]
  }},
  "technische_umsetzung": {{
    "implementierung": [true/false basierend auf Vergleich],
    "routinen_verwendet": [true/false basierend auf Vergleich],
    "fehlerbehandlung": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf technische Umsetzung vs Musterlösung]
  }},
  "sap_standards": {{
    "terminologie": [true/false basierend auf Vergleich],
    "best_practices": [true/false basierend auf Vergleich],
    "dokumentation": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
""",

    "Data Source": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche die Datenquelle mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Technische Definition: max 17 Punkte 
- Konfiguration: max 17 Punkte
- SAP Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "felder_identisch": [true/false - sind die Datenfelder gleich?],
    "struktur_gleich": [true/false - gleiche Datenstruktur?],
    "parameter_korrekt": [true/false - Parameter wie in Musterlösung?],
    "konfiguration_identisch": [true/false - Konfiguration übereinstimmend?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "technische_definition": {{
    "datentypen": [true/false basierend auf Vergleich],
    "feldlaengen": [true/false basierend auf Vergleich],
    "struktur_logisch": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf technische Definition vs Musterlösung]
  }},
  "konfiguration": {{
    "extractor_korrekt": [true/false basierend auf Vergleich],
    "parameter_gesetzt": [true/false basierend auf Vergleich],
    "delta_aktiviert": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Konfiguration vs Musterlösung]
  }},
  "sap_standards": {{
    "terminologie": [true/false basierend auf Vergleich],
    "best_practices": [true/false basierend auf Vergleich],
    "integration": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
""",

    "Info-Object": """
WICHTIG: Prüfe zuerst die Bildqualität! Falls das Bild zu schlecht ist (z.B. Rechtsklick-Menü sichtbar, völlig unscharf, falscher Inhalt, nur Fehlermeldungen), setze "skip_evaluation": true.

CUSTOM MODE: Vergleiche das Info-Object mit der benutzerdefinierten Musterlösung:

SCORING SYSTEM (Custom Mode):
- Inhalt-Ähnlichkeit: max 50 Punkte (50% Gewichtung)
- Query Struktur: max 17 Punkte 
- Darstellung: max 17 Punkte
- SAP Standards: max 16 Punkte
- Gesamt: 100 Punkte, 70+ = bestanden

Antworte NUR mit diesem JSON-Format:
{{
  "skip_evaluation": false,
  "skip_reason": "Optional: Grund warum übersprungen",
  "inhalt_aehnlichkeit": {{
    "daten_identisch": [true/false - sind die Daten/Ergebnisse gleich?],
    "dimensionen_gleich": [true/false - gleiche Dimensionen verwendet?],
    "kennzahlen_korrekt": [true/false - Kennzahlen wie in Musterlösung?],
    "berechnungen_identisch": [true/false - Berechnungen übereinstimmend?],
    "punkte": [0-50: Vergib basierend auf Inhaltlicher Übereinstimmung mit Musterlösung]
  }},
  "query_struktur": {{
    "dimensionen_korrekt": [true/false basierend auf Vergleich],
    "kennzahlen_sinnvoll": [true/false basierend auf Vergleich],
    "filter_angemessen": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Query-Struktur vs Musterlösung]
  }},
  "darstellung": {{
    "formatierung": [true/false basierend auf Vergleich],
    "lesbarkeit": [true/false basierend auf Vergleich],
    "uebersichtlichkeit": [true/false basierend auf Vergleich],
    "punkte": [0-17: Vergib basierend auf Darstellung vs Musterlösung]
  }},
  "sap_standards": {{
    "terminologie": [true/false basierend auf Vergleich],
    "best_practices": [true/false basierend auf Vergleich],
    "konformitaet": [true/false basierend auf Vergleich],
    "punkte": [0-16: Vergib basierend auf SAP Standards vs Musterlösung]
  }},
  "gesamt_bewertung": {{
    "erreichte_punkte": [Summe aller punkte],
    "max_punkte": 100,
    "prozent": [erreichte_punkte / 100 * 100],
    "note": [Sehr gut(90-100)/Gut(75-89)/Befriedigend(60-74)/Mangelhaft(40-59)/Ungenügend(0-39)],
    "bestanden": [true wenn >= 70 Punkte],
    "feedback": "Bewertung basierend auf Vergleich mit benutzerdefinierter Musterlösung - Schwerpunkt auf Inhaltsübereinstimmung",
    "staerken": ["Spezifische positive Aspekte"],
    "verbesserungen": ["Konkrete Verbesserungsvorschläge basierend auf Musterlösung"]
  }}
}}

ENTSCHEIDEND: 50% der Bewertung basiert auf Inhaltsübereinstimmung mit der Musterlösung!
"""
} 
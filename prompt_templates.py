prompt_templates = {
    "Excel-Tabelle": """
Analysiere das Bild einer Excel-Tabelle und gib folgende Bewertungskriterien als JSON zurück:
{
  "struktur_qualitaet": {
    "hat_tabellenstruktur": true/false,
    "spalten_anzahl": "geschätzte Anzahl (1-20+)",
    "zeilen_anzahl": "geschätzte Anzahl (1-100+)",
    "hat_kopfzeile": true/false,
    "score": 0-10
  },
  "visueller_aufbau": {
    "farbschema": "grün/blau/grau/bunt",
    "gridlines_sichtbar": true/false,
    "text_lesbarkeit": "gut/mittel/schlecht",
    "score": 0-10
  },
  "funktionale_elemente": {
    "formeln_vorhanden": true/false,
    "summen_berechnung": true/false,
    "diagramme_enthalten": true/false,
    "filter_aktiviert": true/false,
    "score": 0-10
  },
  "sap_kontext": {
    "sap_interface_erkennbar": true/false,
    "daten_typ": "BW Query/Excel Export/Rohdaten",
    "business_kontext": "Financial/Logistik/HR/Unbekannt",
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "verbesserungsvorschlaege": ["Erste Zeile als Header", "Bessere Formatierung", "Mehr Übersichtlichkeit"]
}
""",

    "Data-Flow": """
Analysiere das Data-Flow-Diagramm und bewerte nach folgenden Kriterien:
{
  "diagramm_struktur": {
    "knoten_anzahl": "geschätzte Anzahl (2-20+)",
    "verbindungen_anzahl": "geschätzte Anzahl (1-30+)",
    "flow_richtung": "links-rechts/oben-unten/komplex",
    "hierarchie_erkennbar": true/false,
    "score": 0-10
  },
  "technische_qualitaet": {
    "symbole_korrekt": true/false,
    "beschriftung_lesbar": true/false,
    "pfeile_eindeutig": true/false,
    "gruppierung_logisch": true/false,
    "score": 0-10
  },
  "sap_bw_elemente": {
    "datasource_vorhanden": true/false,
    "transformation_sichtbar": true/false,
    "target_definiert": true/false,
    "dtp_prozesse": true/false,
    "score": 0-10
  },
  "verstaendlichkeit": {
    "logischer_aufbau": true/false,
    "vollstaendiger_flow": true/false,
    "technische_details": "zu wenig/angemessen/zu viel",
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "kritische_punkte": ["Fehlende Beschriftung", "Unklare Datenrichtung", "Inkompletter Flow"]
}
""",

    "Data-Transfer-Process": """
Bewerte das Data Transfer Process (DTP) Diagramm:
{
  "prozess_definition": {
    "quelle_erkennbar": true/false,
    "ziel_definiert": true/false,
    "transformation_zwischenschritt": true/false,
    "fehlerbehandlung_sichtbar": true/false,
    "score": 0-10
  },
  "technische_konfiguration": {
    "update_modus": "Full/Delta/Unbekannt",
    "package_size_angegeben": true/false,
    "parallele_verarbeitung": true/false,
    "filter_bedingungen": true/false,
    "score": 0-10
  },
  "monitoring_aspekte": {
    "status_informationen": true/false,
    "fehler_logs": true/false,
    "performance_daten": true/false,
    "schedule_info": true/false,
    "score": 0-10
  },
  "sap_konformitaet": {
    "standard_sap_layout": true/false,
    "korrekte_terminologie": true/false,
    "business_kontext": "Data Warehouse/Real-time/Batch",
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "optimierungsmoeglichkeiten": ["Bessere Dokumentation", "Klarere Prozessschritte", "Vollständige Konfiguration"]
}
""",

    "Transformation": """
Analysiere die Transformation und bewerte die Vollständigkeit:
{
  "mapping_struktur": {
    "eingabe_felder": "geschätzte Anzahl (1-50+)",
    "ausgabe_felder": "geschätzte Anzahl (1-50+)",
    "mapping_linien_sichtbar": true/false,
    "transformation_regeln": true/false,
    "score": 0-10
  },
  "business_logik": {
    "berechnungen_vorhanden": true/false,
    "lookup_tabellen": true/false,
    "konstante_werte": true/false,
    "bedingte_logik": true/false,
    "score": 0-10
  },
  "technische_implementierung": {
    "abap_code_sichtbar": true/false,
    "standard_routinen": true/false,
    "custom_entwicklung": true/false,
    "fehlerbehandlung": true/false,
    "score": 0-10
  },
  "dokumentation_qualitaet": {
    "feld_beschreibungen": true/false,
    "business_zweck_klar": true/false,
    "technische_kommentare": true/false,
    "test_daten_beispiele": true/false,
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "verbesserungsbedarfe": ["Mehr Dokumentation", "Klarere Logik", "Vollständiges Mapping"]
}
""",

    "Data Source": """
Bewerte die Datenquelle-Definition:
{
  "datenquelle_typ": {
    "quelle_art": "SAP R/3/File/Database/API",
    "struktur_definition": true/false,
    "feld_anzahl": "geschätzte Anzahl (1-100+)",
    "technische_namen": true/false,
    "score": 0-10
  },
  "metadaten_qualitaet": {
    "feld_beschreibungen": true/false,
    "datentypen_definiert": true/false,
    "key_felder_markiert": true/false,
    "business_bedeutung": true/false,
    "score": 0-10
  },
  "konnektivitaet": {
    "verbindungs_parameter": true/false,
    "authentifizierung": true/false,
    "delta_mechanismus": true/false,
    "fehlerbehandlung": true/false,
    "score": 0-10
  },
  "sap_bw_integration": {
    "standard_sap_connector": true/false,
    "custom_extractor": true/false,
    "transfer_struktur": true/false,
    "business_content": true/false,
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "kritische_aspekte": ["Fehlende Metadaten", "Unklare Datenherkunft", "Mangelhafte Integration"]
}
""",

    "Info-Object": """
Bewerte das Info-Objekt (InfoCube, DSO, etc.):
{
  "objekt_definition": {
    "objekt_typ": "InfoCube/DSO/CompositeProvider/ADO",
    "feld_struktur": true/false,
    "dimension_hierarchie": true/false,
    "business_kontext": "klar/unklar",
    "score": 0-10
  },
  "technische_modellierung": {
    "key_felder_definiert": true/false,
    "data_felder_strukturiert": true/false,
    "time_eigenschaften": true/false,
    "unit_of_measure": true/false,
    "score": 0-10
  },
  "performance_aspekte": {
    "partitionierung": true/false,
    "indizierung": true/false,
    "aggregation_ebenen": true/false,
    "compression": true/false,
    "score": 0-10
  },
  "business_verwendung": {
    "reporting_zweck": true/false,
    "analytische_funktionen": true/false,
    "self_service_geeignet": true/false,
    "governance_konform": true/false,
    "score": 0-10
  },
  "gesamt_score": 0-10,
  "optimierungspotentiale": ["Bessere Modellierung", "Performance Tuning", "Klarere Business Logik"]
}
"""
}

# Comparison template for Aufgabe 4
comparison_prompt = """
Vergleiche das Student-Bild mit dem Referenz-Bild (Musterlösung) in der Kategorie {category}.

Student-Bild Analyse:
{student_analysis}

Referenz-Bild (Musterlösung):
{reference_analysis}

Gib einen detaillierten Vergleich als JSON zurück:
{
  "kategorie_uebereinstimmung": {
    "richtige_kategorie": true/false,
    "sicherheit": 0-100,
    "erklaerung": "Warum passt/passt nicht die Kategorie"
  },
  "inhaltlicher_vergleich": {
    "strukturelle_aehnlichkeit": 0-100,
    "fachliche_korrektheit": 0-100,
    "vollstaendigkeit": 0-100,
    "technische_qualitaet": 0-100
  },
  "bewertung_details": {
    "starke_punkte": ["Was gut gemacht wurde"],
    "schwache_punkte": ["Was verbessert werden könnte"],
    "fehlende_elemente": ["Was komplett fehlt"],
    "besonders_gut": ["Herausragende Aspekte"]
  },
  "gesamt_bewertung": {
    "punkte": 0-100,
    "note": "1.0-5.0",
    "feedback": "Zusammenfassendes Feedback für den Studenten"
  },
  "verbesserungsempfehlungen": [
    "Konkrete Schritte zur Verbesserung"
  ]
}
"""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

INK = "17222D"
TEAL = "173D4F"
COPPER = "A65D3B"
CREAM = "F7F1E3"
PALE = "E8F1EF"
GREY = "D9D9D9"
WHITE = "FFFFFF"


SCENES = [
    {
        "number": 1,
        "title": "Der fehlende Morgen",
        "meta": "45 Minuten  |  Platz der fehlenden Glocke",
        "goal": "Menschen retten, die Zeitlücke körperlich zeigen und die erste belastbare Spur ausgeben.",
        "opening": "Die Welt springt vom Montag in den Mittwoch. Eine Tram fährt an, sieht die am Dienstag ausgehobene Baugrube zu spät und hängt nach der Notbremsung über dem Abgrund.",
        "truths": [
            "Die Quittung nennt Morgen & Söhne und Vertrag 7/7.",
            "Blaues Archivwachs und Mios Tinte verbinden Unfall, Tessa und Linie 7.",
            "Die Papiermotte reagiert auf vier resonierende Zeitanker, nicht auf vorherbestimmte Held*innen.",
        ],
        "moves": [
            "Tram kippt nach drei Spotlight-Wechseln; Rettung gelingt dann mit Stress als Preis.",
            "Taktwächter*innen schützen die Uhr statt der Menschen.",
            "Bei Fear: Ausrüstung verlieren, Aufmerksamkeit +1 oder Quittung gerät in Gefahr.",
        ],
        "countdown": "Endgültiger Vertrag +1 bei deutlichem Scheitern. Erhöhte Aufmerksamkeit +1 bei öffentlicher Gewalt oder verlorenen Beweisen.",
        "transition": "Die Glocke schlägt dreizehnmal. Die Motte flüstert: Findet Tessa, bevor die Nulluhr uns schließt.",
        "cut": "Rettung als eine gemeinsame Aktion entscheiden, Quittung und blaues Wachs automatisch sichern, direkt zum Markt schneiden.",
        "never": "Nicht kürzen: Die Körper haben den Dienstag erlebt; nur das bewusste Erinnern fehlt.",
    },
    {
        "number": 2,
        "title": "Markt ohne Gestern",
        "meta": "50 Minuten  |  Genossenschaftsmarkt",
        "goal": "Fraktionen sichtbar machen und mindestens einen Zugang zum Archiv gewinnen.",
        "opening": "Mittwochsbrot liegt zum Montagspreis aus. Niemand kann erklären, wohin Lieferung, Lohn und ein ganzer Arbeitstag verschwanden.",
        "truths": [
            "Jori: Tessa versteckte Beweise im Archiv; eine geschützte Transportzelle existiert.",
            "Orsino: Die Nulluhr macht den Vertrag endgültig.",
            "Voss: Ein Vertragsbruch kann Zeit zurückschlagen, doch sie kennt nur Vertrag oder Chaos.",
        ],
        "moves": [
            "Händler*in vergisst ein Kind; Orsino streicht einen Namen aus der Liste.",
            "Voss verlangt Verantwortung für Unruhe; Jori verlangt konkrete Solidarität.",
            "Linie 7 erscheint nur als Spiegelung im Regen.",
        ],
        "countdown": "Gemeinsamer Takt +1 bei Schutz ohne Gegenleistung. Erhöhte Aufmerksamkeit +1 bei Drohung, Gewalt oder öffentlich verlorenen Beweisen.",
        "transition": "Mitgliedssiegel, Durchsuchungsbescheid oder Vertragsnadel öffnen den Weg unter das Amt für Wochentage.",
        "cut": "Nur zwei Gesprächsinseln spielen. Die unterstützte Fraktion liefert Zugang und nennt Tessas Archivspur.",
        "never": "Nicht kürzen: Jede Fraktion soll einen verständlichen Wunsch und eine reale Angst bekommen.",
    },
    {
        "number": 3,
        "title": "Archiv der kleinen Wahrheiten",
        "meta": "55 Minuten  |  Unter dem Amt für Wochentage",
        "goal": "Vertragskern, Tessa und den geheimen Bahnsteig der Linie 7 lokalisieren.",
        "opening": "Hinter der Amtstür beginnt ein Regalwald auf Messingschienen. Papiermotten tragen Wahrheiten dorthin, wo niemand vernünftigerweise nach ihnen sucht.",
        "truths": [
            "Der rohe Dienstag liegt noch als Pfand unter dem Kalenderwerk.",
            "Exportiert werden nur Zeit-Zinsen: Regeneration, Möglichkeiten und Lebensjahre.",
            "Der Vertrag hat sechs Siegel; Linie 7 führt über Depot Null nach Nachmorgen.",
        ],
        "moves": [
            "Indexschwarm + zwei Taktwächter*innen; Rückzug bei geöffnetem Indexrad oder öffentlichen Beweisen.",
            "Eine verdrängte Wahrheit beruhigt den Schwarm.",
            "Fear: Regal verschiebt eine Zone, trennt eine Figur oder gefährdet das blaue Wachs.",
        ],
        "countdown": "Endgültiger Vertrag +1, wenn Tessas Botschaft verloren geht oder der Zugang versiegelt bleibt. Aufmerksamkeit +1 bei lautem Einbruch.",
        "transition": "Quittung auf blaues Wachs: Tessas Aufnahme erklingt, der Fahrplan erscheint und der Kanalsteg wird zum Bahnsteig.",
        "cut": "Nach der ersten passenden Wahrheit öffnet sich das Indexrad. Tessas Botschaft vollständig ausgeben; Kampf abbrechen.",
        "never": "Nicht kürzen: Rohzeit bleibt, Zeit-Zinsen gehen. Diese Unterscheidung trägt das Finale.",
    },
    {
        "number": 4,
        "title": "Fahrt nach Nachmorgen",
        "meta": "50 Minuten  |  Linie 7  |  Ende Abend 1",
        "goal": "Persönliche Einsätze zeigen, Herr Pünktlich begegnen und Nachmorgen erreichen.",
        "opening": "Die Tram fährt durch Erinnerungen, Möglichkeiten und verlorene Minuten. Draußen zieht Veyra vorbei, obwohl die Schienen längst aufgehört haben, in der Stadt zu liegen.",
        "truths": [
            "Herr Pünktlich ist ein magischer Vertragsparasit, kein Angestellter des Konsortiums.",
            "Er verlangt Beweise dafür, dass Reisende an einem Dienstag existierten.",
            "Gewaltsames Entfernen würde die Schutzmagie der Linie aufreißen.",
        ],
        "moves": [
            "Eine offene Waggonfrage je Figur: geschenkter Tag, fehlende Zeit oder abgelegte Pflicht.",
            "Bei Gewalt erscheinen zwei Minutenzehrer; Zugehörigkeit kann Herr Pünktlich zweifeln lassen.",
            "Fear: Entgleisung +1 oder Figur in den nächsten Waggon trennen.",
        ],
        "countdown": "Entgleisung Linie 7 hat 3 Segmente. Bei Vollendung löst sich ein Waggon; Rettung kostet Zeit oder Ressourcen.",
        "transition": "Die Tram durchbricht eine weiße Wand. Ein endloser Dienstagnachmittag liegt dahinter: Ihr seid spät. Natürlich seid ihr das.",
        "cut": "Eine Waggonfrage pro Figur, Herr Pünktlich sozial lösen, Entgleisung nur als letzte gemeinsame Reaktion.",
        "never": "Nicht kürzen: Mindestens eine persönliche Antwort pro Figur und der Blick auf Nachmorgen.",
    },
    {
        "number": 5,
        "title": "Menschen aus Minuten",
        "meta": "50 Minuten  |  Nachmorgen",
        "goal": "Betroffene kennenlernen, Tessa finden und die dritte Möglichkeit eröffnen.",
        "opening": "Nachmorgen ist kein leeres Gefängnis. Zwischen unzugestellten Briefen stehen Küchen, Werkstätten und ein Plenum der Menschen, die Veyra aus ihrer Zeit geschrieben hat.",
        "truths": [
            "Die Rückwelle ist gebundene Rohzeit und kann mit einem Verteilungsplan entschärft werden.",
            "Bereits exportierte Zeit-Zinsen kehren nicht zurück.",
            "Das Ritual der Gemeinsamen Minute verhindert, dass eine Einzelpartei Dienstag besitzt.",
        ],
        "moves": [
            "Lio bittet um einen wichtigen Tag; Arbeiter*innen brauchen Vorräte.",
            "Tessa warnt vor einer Rückkehr, die Nachmorgen auslöscht.",
            "Bei Härte oder Eile: Vertragsagent*innen finden die Gruppe oder der Endpreis steigt.",
        ],
        "countdown": "Gemeinsamer Takt +1 bei geteilter Zeit oder Vorräten. Ein langer Rest erhöht Endgültiger Vertrag um 2.",
        "transition": "Tessa zeigt den sicheren Rückweg und erklärt, warum Kalenderwerk und Nulluhr gleichzeitig politisch und magisch besetzt werden müssen.",
        "cut": "Lio, Vorratswahl und Plenum als Montage. Tessas Erklärung und das Ritual vollständig spielen.",
        "never": "Nicht kürzen: Nachmorgen besitzt Gesellschaft und eigene Interessen; es ist keine Kulisse für Veyras Rettung.",
    },
    {
        "number": 6,
        "title": "Besetzung des Kalenderwerks",
        "meta": "50 Minuten  |  Kalenderwerk",
        "goal": "Menge schützen, Maschinen stoppen und den Zugang zum Chronotresor öffnen.",
        "opening": "Der Gemeinsame Takt besetzt die Druckerei. Voss bringt die Stadtwache, Orsino aktiviert die Stanzen, und jede Maschine behauptet, nur ihre Zuständigkeit zu erfüllen.",
        "truths": [
            "Drei Fronten mit je 3 Fortschritt: Menge, Maschinen, Voss.",
            "Gewalt gegen Stadtwache erhöht Gefahr Menge; Schutz und öffentliche Beweise schaffen Fortschritt.",
            "Der Zugang öffnet spätestens nach fünf fiktionalen Runden - mit Kosten statt Sackgasse.",
        ],
        "moves": [
            "Nach je zwei Spieler*innen-Spotlights folgt eine GM-Reaktion.",
            "Maschinen stanzen neue Zeit-Zinsen; bei Gefahr erscheinen Papierknechte.",
            "Voss kann verhandeln, räumen lassen oder den Verwaltungsschacht öffnen.",
        ],
        "countdown": "Maschinengefahr: Nulluhr +1. Mengegefahr: Kollateralschaden und Jori isoliert. Gemeinsamer Takt kann automatischen Fortschritt geben.",
        "transition": "Der Verwaltungsschacht führt hinab in die fünf Räume des Chronotresors.",
        "cut": "Alle Fronten zu einer gemeinsamen 4-Segment-Challenge verbinden. Eine Entscheidung muss Voss betreffen.",
        "never": "Nicht kürzen: Schutz der Menschen ist gleichwertig mit Sabotage und Verhandlung.",
    },
    {
        "number": 7,
        "title": "Der Chronotresor",
        "meta": "60 Minuten  |  Unter der Nulluhr",
        "goal": "Drei Siegel durch Entscheidungen lösen und Ressourcen für das Finale setzen.",
        "opening": "Der Tresor ist Reifekammer und Pfandhaus, keine Lagerhalle. Hinter Glas wächst ein Dienstag, aus dem Maschinen fortwährend Zukunftszinsen schneiden.",
        "truths": [
            "Orsinos Bilanz trennt Rohzeit und exportierte Zeit-Zinsen.",
            "Der Dienstag wurde nie vollständig aus Veyra ausgeführt.",
            "Ein blinder Vertragsbruch öffnet das Pfand; Verteilung macht die Rückwelle beherrschbar.",
        ],
        "moves": [
            "Räume als Fragen spielen: Wert, private Erinnerung, Wahrheit, Zustimmung und Eigentum.",
            "Keine Tür verlangt eine bestimmte Probe; eine ehrliche Entscheidung verändert ein Siegel.",
            "Fear: Stress, Nulluhr +1, Rückwelle +1 oder eine Klausel bindet Objekt beziehungsweise Zone.",
        ],
        "countdown": "Endgültiger Vertrag steigt bei blindem Brechen, langem Zögern oder vollständigem Scheitern. Öffentliche Bilanz kann eine Fraktion ohne Probe überzeugen.",
        "transition": "Wenn drei Siegel beantwortet sind, öffnet sich der Kernraum. Die Nulluhr zeigt sechs mögliche Zukünfte.",
        "cut": "Jeden Raum als eine konkrete Frage stellen; nach drei tragfähigen Antworten direkt in den Kernraum wechseln.",
        "never": "Nicht kürzen: Bilanzbuch und die Trennung zwischen Pfand und Zinsen müssen verständlich sein.",
    },
    {
        "number": 8,
        "title": "Wem gehört die Zeit",
        "meta": "50 Minuten  |  Kernraum der Nulluhr",
        "goal": "Eigentum, Verteilung und Zustimmung entscheiden; danach konkrete Folgen zeigen.",
        "opening": "Die Nulluhr entfaltet sechs Zeiger. Über der Stadt erscheinen geordnete Armut, chaotische Freiheit, privatisierte Unsterblichkeit und erschöpfte Fürsorge. Dienstag verlangt Beteiligung.",
        "truths": [
            "Angriff, Umdeutung, Verhandlung, Schutz und Ritual sind gleichwertige Fortschrittspfade.",
            "Bei 0 HP, vier umgedeuteten Siegeln oder überzeugt/entmachtetem Orsino wird die Ordnung verhandelt.",
            "Ein voller Countdown beendet nicht das Spiel, sondern erhöht den gemeinsamen Preis.",
        ],
        "moves": [
            "Nach vollständigem Umlauf: Endgültiger Vertrag +1, falls kein Erfolg gegen die Nulluhr erzielt wurde.",
            "Fear für Zukunft schneiden, Montag für immer oder eine vertraglich gebundene Zone.",
            "Bei Severe Damage höchstens einmal je Runde Rückwelle +1.",
        ],
        "countdown": "Endgültiger Vertrag entscheidet über Preis und Reichweite des Endes, nicht darüber, ob die Gruppe überhaupt entscheiden darf.",
        "transition": "Epilog: Wer entscheidet künftig, wer erhält Zeit zurück, welche Beziehung bleibt beschädigt und was tut jede Figur am ersten freien Dienstag?",
        "cut": "Sobald Nulluhr 4 HP oder weniger hat, vier Siegel umgedeutet sind oder Orsino fällt, direkt zur Eigentumsentscheidung wechseln.",
        "never": "Nicht kürzen: Die Gruppe benennt eine Ordnung und deren konkrete Folgen für Betroffene.",
    },
]


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color=COPPER, size="8"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:color"), color)


def font_run(run, size=7.6, bold=False, color=INK, name="Aptos"):
    run.bold = bold
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.insert(0, r_fonts)
    r_fonts.set(qn("w:ascii"), name)
    r_fonts.set(qn("w:hAnsi"), name)


def add_compact_paragraph(cell, label, text, size=8.4, after=1.8):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.0
    font_run(p.add_run(label), size=size, bold=True, color=COPPER, name="Georgia")
    font_run(p.add_run(text), size=size)
    return p


def add_bullets(cell, label, items):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0.8)
    font_run(p.add_run(label), size=8.35, bold=True, color=COPPER, name="Georgia")
    for item in items:
        b = cell.add_paragraph()
        b.paragraph_format.left_indent = Cm(0.25)
        b.paragraph_format.first_line_indent = Cm(-0.18)
        b.paragraph_format.space_before = Pt(0)
        b.paragraph_format.space_after = Pt(0.4)
        b.paragraph_format.line_spacing = 1.0
        font_run(b.add_run("• "), size=8.2, bold=True, color=TEAL)
        font_run(b.add_run(item), size=8.15)


def add_card(doc, scene, card_index):
    outer = doc.add_table(rows=1, cols=1)
    outer.alignment = WD_TABLE_ALIGNMENT.CENTER
    outer.autofit = False
    cell = outer.cell(0, 0)
    cell.width = Cm(18.6)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    set_cell_shading(cell, CREAM if card_index % 2 == 0 else PALE)
    set_cell_margins(cell, top=95, start=130, bottom=90, end=130)
    set_cell_border(cell)

    header = cell.add_table(rows=1, cols=2)
    header.alignment = WD_TABLE_ALIGNMENT.CENTER
    header.autofit = False
    h1, h2 = header.rows[0].cells
    h1.width = Cm(11.6)
    h2.width = Cm(6.4)
    for hc in (h1, h2):
        set_cell_shading(hc, TEAL)
        set_cell_margins(hc, top=65, start=90, bottom=65, end=90)
    p = h1.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    font_run(p.add_run(f"Szene {scene['number']}  {scene['title']}"), size=13.2, bold=True, color=WHITE, name="Georgia")
    p = h2.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(0)
    font_run(p.add_run(scene["meta"]), size=8.0, bold=True, color=WHITE)

    add_compact_paragraph(cell, "Ziel  ", scene["goal"], size=8.55, after=2.0)
    add_compact_paragraph(cell, "Einstieg  ", scene["opening"], size=8.4, after=2.2)

    body = cell.add_table(rows=1, cols=2)
    body.alignment = WD_TABLE_ALIGNMENT.CENTER
    body.autofit = False
    left, right = body.rows[0].cells
    left.width = Cm(9.15)
    right.width = Cm(8.85)
    for bc in (left, right):
        set_cell_margins(bc, top=45, start=70, bottom=45, end=70)
    add_bullets(left, "Unverzichtbare Informationen", scene["truths"])
    add_bullets(right, "GM Reaktionen", scene["moves"])

    add_compact_paragraph(cell, "Countdown  ", scene["countdown"], size=8.15, after=1.2)
    add_compact_paragraph(cell, "Übergang  ", scene["transition"], size=8.15, after=1.2)
    add_compact_paragraph(cell, "Notkürzung  ", scene["cut"], size=8.15, after=1.2)
    add_compact_paragraph(cell, "Nicht kürzen  ", scene["never"].removeprefix("Nicht kürzen: "), size=8.15, after=0)

    row_pr = outer.rows[0]._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    row_pr.append(cant_split)
    outer.rows[0].height = Cm(12.45)
    outer.rows[0].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST


def add_cut_line(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(1.5)
    font_run(p.add_run("✂  · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·  ✂"), size=7.0, color="777777")


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21)
    sec.top_margin = Cm(0.75)
    sec.bottom_margin = Cm(0.75)
    sec.left_margin = Cm(1.0)
    sec.right_margin = Cm(1.0)
    sec.header_distance = Cm(0.2)
    sec.footer_distance = Cm(0.25)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(8.4)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(1)
    normal.paragraph_format.line_spacing = 1.0

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    font_run(footer.add_run("Die Stadt die den Dienstag verkaufte  •  Szenenkarten  •  Fassung 1.0"), size=6.5, color="666666")

    for i, scene in enumerate(SCENES):
        add_card(doc, scene, i)
        if i % 2 == 0:
            add_cut_line(doc)
        elif i != len(SCENES) - 1:
            doc.add_page_break()

    path = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Szenenkarten_v1_0.docx"
    doc.save(path)
    print(path)


if __name__ == "__main__":
    build()

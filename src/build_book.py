from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.shape import WD_INLINE_SHAPE
import textwrap, os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
ASSET = ROOT / 'work' / 'assets'
OUT.mkdir(exist_ok=True)

INK = '17222D'; BLUE = '173D4F'; TEAL = '2F6F73'; COPPER = 'A65D3B';
GOLD = 'C79A3B'; CREAM = 'F5EEDB'; PALE = 'E8F1EF'; RED = '8A3848'; GREY='D9D9D9'

def font(size=26):
    try: return ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', size)
    except: return ImageFont.load_default()

def make_maps():
    # Crop the portrait illustration without distortion for the title-page panel.
    cover=Image.open(ASSET/'cover.png').convert('RGB')
    cw,ch=cover.size; y=max(0,(ch-cw)//3)
    cover.crop((0,y,cw,y+cw)).save(ASSET/'cover_crop.png',quality=95)
    # City map
    W,H=1800,1200
    im=Image.new('RGB',(W,H),'#F5EEDB'); d=ImageDraw.Draw(im)
    d.rectangle((40,40,W-40,H-40), outline='#173D4F', width=10)
    # river and tram ring
    d.line([(0,900),(350,820),(650,860),(980,760),(1320,830),(1800,710)], fill='#87B8C0', width=120)
    d.ellipse((210,150,1550,1040), outline='#C79A3B', width=28)
    nodes={
      '1 Platz der fehlenden Glocke':(870,360),'2 Amt für Wochentage':(1240,300),
      '3 Genossenschaftsmarkt':(470,350),'4 Archiv der kleinen Wahrheiten':(340,680),
      '5 Kalenderwerk':(910,720),'6 Viertel Nachmorgen':(1410,650),
      '7 Depot Null':(1130,930),'8 Rathaus der Möglichkeiten':(700,520)}
    for label,(x,y) in nodes.items():
        d.ellipse((x-46,y-46,x+46,y+46), fill='#A65D3B', outline='#17222D', width=5)
        n=label.split()[0]; d.text((x-10,y-18),n,font=font(30),fill='white')
        lines=textwrap.wrap(' '.join(label.split()[1:]),24)
        for j,line in enumerate(lines): d.text((x+58,y-22+j*34),line,font=font(27),fill='#17222D')
    d.text((70,65),'Veyra  schematische Stadtkarte',font=font(46),fill='#173D4F')
    d.text((70,1120),'Linien sind erzählerische Wege, keine Meterangaben. Der Fluss heißt Vielleicht.',font=font(26),fill='#4A4A4A')
    im.save(ASSET/'map_city.png')

    # Archive encounter map
    im=Image.new('RGB',(1600,1100),'#F5EEDB'); d=ImageDraw.Draw(im)
    d.rectangle((100,100,1500,1000), fill='#E5D8B9', outline='#173D4F', width=12)
    for x in range(260,1400,230):
        d.rectangle((x,220,x+70,820), fill='#845B3E', outline='#17222D', width=4)
    d.rectangle((610,90,990,260),fill='#B9D5D1',outline='#173D4F',width=7)
    d.ellipse((700,420,900,620),fill='#C79A3B',outline='#17222D',width=7)
    d.rectangle((100,850,1500,1000),fill='#7FA9AE',outline='#173D4F',width=7)
    d.text((120,25),'Archiv der kleinen Wahrheiten',font=font(50),fill='#173D4F')
    labels=[((650,120),'Lesesaal'),((650,650),'Regalgang'),((680,900),'Kanalsteg'),((1020,500),'Rollleiter'),((690,480),'Indexrad')]
    for (x,y),t in labels: d.text((x,y),t,font=font(30),fill='#17222D')
    d.text((115,1020),'Zonen: Eingang | Regalwald | Indexrad | Lesesaal | Kanalsteg',font=font(27),fill='#4A4A4A')
    im.save(ASSET/'map_archive.png')

    # Vault flow map
    im=Image.new('RGB',(1600,1100),'#F5EEDB'); d=ImageDraw.Draw(im)
    d.text((90,45),'Chronotresor  Weg der Rückgabe',font=font(48),fill='#173D4F')
    rooms=[(120,230,450,480,'A  Schleuse'),(630,130,970,390,'B  Pfandkammer'),(1120,230,1480,500,'C  Bilanzsaal'),
           (270,650,620,930,'D  Dienstag'),(820,620,1240,960,'E  Nulluhr')]
    for x1,y1,x2,y2,t in rooms:
        d.rounded_rectangle((x1,y1,x2,y2),radius=35,fill='#E8F1EF',outline='#173D4F',width=8)
        d.text((x1+35,(y1+y2)//2-20),t,font=font(34),fill='#17222D')
    for a,b in [((450,350),(630,260)),((970,260),(1120,350)),((1300,500),(1100,620)),((820,790),(620,790)),((450,480),(440,650))]:
        d.line([a,b],fill='#A65D3B',width=18)
    d.text((90,1000),'Jede Tür verlangt eine Entscheidung, keine bestimmte Probe. Sehr revolutionär für eine Tür.',font=font(25),fill='#4A4A4A')
    illustrated_vault = ASSET/'map_vault_illustrated_v2_0.png'
    if illustrated_vault.exists():
        Image.open(illustrated_vault).convert('RGB').save(ASSET/'map_vault.png', optimize=True)
    else:
        im.save(ASSET/'map_vault.png')

def set_cell_shading(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)

def set_cell_border(cell, color=GREY, size='6'):
    tcPr=cell._tc.get_or_add_tcPr(); borders=tcPr.first_child_found_in('w:tcBorders')
    if borders is None: borders=OxmlElement('w:tcBorders'); tcPr.append(borders)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el=OxmlElement('w:'+edge); el.set(qn('w:val'),'single'); el.set(qn('w:sz'),size); el.set(qn('w:color'),color); borders.append(el)

def add_table(doc, headers, rows, widths=None, size=8.5):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=True
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=str(h); set_cell_shading(c,BLUE); set_cell_border(c)
        c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for r in c.paragraphs[0].runs: r.font.bold=True; r.font.color.rgb=RGBColor(255,255,255); r.font.size=Pt(size)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text=str(v); set_cell_border(cells[i]); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri%2: set_cell_shading(cells[i],PALE)
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(0)
                for r in p.runs: r.font.size=Pt(size)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t

def heading(doc,text,level=1):
    p=doc.add_heading(text,level=level)
    p.paragraph_format.keep_with_next=True
    return p

def para(doc,text='',boldlead=None,style=None):
    p=doc.add_paragraph(style=style)
    if boldlead:
        r=p.add_run(boldlead); r.bold=True
    p.add_run(text)
    return p

def bullets(doc,items):
    for x in items: para(doc,x,style='List Bullet')

def page(doc): doc.add_page_break()

def stat(doc,name,role,diff,thresholds,hp,stress,atk,damage,range_,motives,features,portrait=None):
    heading(doc,name,2)
    if portrait:
        panel=doc.add_table(rows=1,cols=2)
        panel.alignment=WD_TABLE_ALIGNMENT.CENTER
        panel.autofit=False
        left,right=panel.rows[0].cells
        left.width=Cm(3.6); right.width=Cm(12.4)
        left.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        right.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        left_p=left.paragraphs[0]; left_p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        left_p.paragraph_format.space_after=Pt(0)
        left_p.add_run().add_picture(str(ASSET/portrait),width=Cm(3.25))
        right_p=right.paragraphs[0]
        right_p.paragraph_format.space_after=Pt(0)
        lead=right_p.add_run('Rolle und Taktik: '); lead.bold=True
        right_p.add_run(f'{role}. {motives}')
        tblPr=panel._tbl.tblPr
        borders=OxmlElement('w:tblBorders')
        for edge in ('top','left','bottom','right','insideH','insideV'):
            el=OxmlElement(f'w:{edge}'); el.set(qn('w:val'),'nil'); borders.append(el)
        tblPr.append(borders)
        cant_split=OxmlElement('w:cantSplit'); panel.rows[0]._tr.get_or_add_trPr().append(cant_split)
    else:
        para(doc,f'{role}. {motives}',boldlead='Rolle und Taktik: ')
    add_table(doc,['Schwierigkeit','Schwellen','HP','Stress','Angriff','Schaden','Reichweite'],[[diff,thresholds,hp,stress,atk,damage,range_]],[2.6,2.3,1.0,1.4,1.5,2.4,2.8],8)
    for title,kind,txt in features:
        para(doc,txt,boldlead=f'{title} – {kind}: ')

def handout_title(doc,n,title):
    page(doc); p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(f'SPIELERHANDOUT {n}'); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=RGBColor.from_string(COPPER)
    h=doc.add_heading(title,0); h.alignment=WD_ALIGN_PARAGRAPH.CENTER

def image_handout(doc,n,title,filename,caption):
    handout_title(doc,n,title)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ASSET/filename),width=Cm(17.2))
    para(doc,caption,style=None).alignment=WD_ALIGN_PARAGRAPH.CENTER

def build():
    make_maps(); doc=Document()
    sec=doc.sections[0]; sec.page_height=Cm(29.7); sec.page_width=Cm(21); sec.top_margin=Cm(1.7); sec.bottom_margin=Cm(1.6); sec.left_margin=Cm(1.7); sec.right_margin=Cm(1.7)
    styles=doc.styles
    styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(9.4); styles['Normal'].font.color.rgb=RGBColor.from_string(INK)
    styles['Normal'].paragraph_format.space_after=Pt(5); styles['Normal'].paragraph_format.line_spacing=1.08
    for s,size,col in [('Title',34,INK),('Subtitle',15,TEAL),('Heading 1',22,BLUE),('Heading 2',15,COPPER),('Heading 3',11,TEAL)]:
        styles[s].font.name='Georgia'; styles[s].font.size=Pt(size); styles[s].font.color.rgb=RGBColor.from_string(col); styles[s].font.bold=True
    styles['Title'].font.color.rgb=RGBColor(0,0,0)
    for nm in ['Heading 1','Heading 2','Heading 3']:
        styles[nm].paragraph_format.space_before=Pt(10); styles[nm].paragraph_format.space_after=Pt(5); styles[nm].paragraph_format.keep_with_next=True
    styles['List Bullet'].font.size=Pt(9.2); styles['List Bullet'].paragraph_format.space_after=Pt(2)
    # footer
    for s in doc.sections:
        f=s.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER
        f.add_run('Die Stadt die den Dienstag verkaufte   •   Daggerheart Abenteuer   •   ').font.size=Pt(8)
        fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); f._p.append(fld)

    # Cover
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ASSET/'cover_crop.png'),width=Cm(17.5))
    t=doc.add_paragraph(style='Title'); t.alignment=WD_ALIGN_PARAGRAPH.CENTER; t.add_run('Die Stadt die den Dienstag verkaufte')
    st=doc.add_paragraph(style='Subtitle'); st.alignment=WD_ALIGN_PARAGRAPH.CENTER; st.add_run('Ein Daggerheart Abenteuer für vier Charaktere auf Stufe 1')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('Zwei Spielabende à vier Stunden   •   Acht Szenen   •   Mit One Shot Variante').italic=True
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('Fassung 1.8   November 2026').font.size=Pt(8)
    page(doc)

    heading(doc,'So benutzt du dieses Heft',1)
    para(doc,'Dieses Abenteuer führt vier Figuren auf Stufe 1 durch Veyra, eine solidarische Metropole, deren Magistrat den Dienstag an ein überzeitliches Konsortium verpfändet hat. Seitdem springt die Stadt jeden Montag direkt in den Mittwoch. Erinnerungen, Löhne, Pflegezeiten und politische Entscheidungen verschwinden dabei nicht gleichmäßig: Wer wenig Macht besitzt, verliert am meisten. Die Gruppe kann den geraubten Tag zurückholen, ihn neu verteilen oder die Woche grundsätzlich abschaffen. Letzteres ist mechanisch nicht vorgesehen, aber moralisch verdächtig attraktiv.')
    para(doc,'Das Heft ist für zwei Abende von jeweils vier Stunden gebaut. Jede Szene nennt Ziel, Kernfrage, Hinweise, Proben, GM Moves, Countdown Folgen und eine harte Schnittmarke. Kämpfe sind vermeidbar; Gegner*innen haben Motive und Auswege. Die Geschichte funktioniert mit beliebigen vier Stufe 1 Figuren. Vier Rollenanker helfen, vorhandene Figuren in Veyra zu verknüpfen.',boldlead='Versprechen an die Spielleitung: ')
    heading(doc,'Sicherheitsrahmen',2)
    para(doc,'Besprecht vor Spielbeginn Linien und Schleier. Mögliche sensible Themen sind Arbeitsausbeutung, Gedächtnisverlust, staatliche Gewalt, Verschuldung, verschwundene Angehörige und Zeitdruck. Nutzt ein offenes Stoppsignal, Pausen und nach jedem Abend ein kurzes Debriefing. Niemand schuldet einer Fiktion Unbehagen; auch keine Fiktion mit hübscher Straßenbahn.')
    heading(doc,'Inhalt und Navigation',2)
    add_table(doc,['Abschnitt','Nutzen am Tisch'],[
      ['1 Vorbereitung','Prämisse, Figurenanker, Regelkern, Zeitplan'],['2 Veyra','Wahrheiten, Fraktionen, Zeitlogik'],['3 Acht Szenen','Vollständiger Ablauf beider Spielabende'],['4 Personen','NSC Dossiers und Beziehungen'],['5 Gefahren','Gegner*innen, Environment, Balancing'],['6 Werkzeuge','Countdowns, Karten, Hinweise, Enden'],['7 Varianten','Vier Stunden One Shot und Skalierung'],['8 Handouts','Direkt druckbare Spielmaterialien'],['9 Prüfung','Regel, Balance, Zeit und Konsistenz']], [5,11])
    heading(doc,'Daggerheart Kompatibilität',2)
    para(doc,'Entwickelt und geprüft gegen das Daggerheart System Reference Document 2.0 vom 25. August 2026. Daggerheart ist ein Warenzeichen von Critical Role LLC und wird unter der Darrington Press Community Gaming License verwendet. Dieses unabhängige Fanwerk ist nicht offiziell unterstützt. Alle Abenteuertexte, Figuren und eigenen Profile sind Originalmaterial. Die Regelzusammenfassung ersetzt kein Grundregelwerk.')

    page(doc); heading(doc,'1 Vorbereitung',1)
    heading(doc,'Die Prämisse in neun Sätzen',2)
    bullets(doc,[
      'Vor sieben Jahren verhinderte Veyra einen Staatsbankrott, indem der Magistrat einen Wochentag an das Chronokonsortium Morgen & Söhne verkaufte.',
      'Der Vertrag nahm den Dienstag aus Kalendern, bewussten Tagesrhythmen und öffentlicher Erinnerung; die Körper durchleben ihn weiterhin, doch nur Menschen mit biografischen Zeitankern bemerken die mentale Lücke.',
      'Der rohe Dienstag bleibt als Pfand im Chronotresor gebunden; das Konsortium exportiert nur seine abgeschöpften Zinsen als handelbare Lebenszeit.',
      'Bürgermeisterin Elian Voss glaubt, der Vertrag habe die Stadt gerettet und ein Bruch würde alte Schulden als Zeitsturm zurückwerfen.',
      'Die Archivarin Tessa Quendel hat Beweise gesammelt, wurde aber in den Zwischenraum Nachmorgen verschoben.',
      'Die Straßenbahnlinie 7 fährt unter einem Erinnerungsfilter durch diesen Zwischenraum; nur eine kleine Schutzzelle kennt ihre ganze Route.',
      'Der Gewerkschaftsbund Der Gemeinsame Takt plant während der Hundertsten Nulluhr, der hundertsten Vertragsprüfung seit der Neuvermessung, eine Besetzung des Kalenderwerks.',
      'Das Konsortium will den Vertrag dauerhaft machen, sobald sechs Siegel am Nulluhrwerk geschlossen sind.',
      'Die Figuren entscheiden nicht nur, ob Dienstag zurückkehrt, sondern wem Zeit gehören darf.'
    ])
    heading(doc,'Vier Rollenanker für beliebige Figuren',2)
    add_table(doc,['Anker','Verbindung','Einstiegsfrage'],[
      ['Die Erinnerungsträger*in','Besitzt einen Gegenstand aus einem Dienstag.','Wessen Stimme hörst du, wenn die Uhr 2:17 schlägt?'],
      ['Die Schuldner*in','Eine nahestehende Person hat Lebenszeit an Morgen & Söhne verloren.','Was hast du versprochen, bevor du die Rechnung kanntest?'],
      ['Die Stadtverbundene','Kennt Veyras Dächer, Kanäle oder Dienstwege.','Welche Nachbar*innenschaft würde dich trotz allem verstecken?'],
      ['Die Zweifler*in','Hat einmal vom Vertrag profitiert.','Welche bequeme Lüge möchtest du nicht mehr glauben?']], [3.4,6,6.4])
    para(doc,'Jede Figur wählt einen anderen Anker. Ergänzt als Gruppe zwei Verbindungen: Wer hat gemeinsam gegen eine Räumung gestanden? Wer schuldet wem eine ehrliche Antwort? Jede Figur startet mit 2 Hope; die GM startet regelgemäß mit 4 Fear für vier Spieler*innen.',boldlead='Startressourcen: ')
    heading(doc,'Acht Stunden am Tisch',2)
    add_table(doc,['Zeit','Szene','Kern','Schnitt'],[
      ['Abend 1  0:00–0:20','Auftakt','Rahmen, Anker, erste Störung','Die Glocke schlägt Montag 24:00'],
      ['0:20–1:05','1 Der fehlende Morgen','Unmöglicher Mittwoch, Rettung','Die Quittung spricht'],
      ['1:05–1:55','2 Markt ohne Gestern','Ermittlung und Fraktionen','Linie 7 wird sichtbar'],
      ['1:55–2:05','Pause','—','—'],
      ['2:05–3:00','3 Archiv der Wahrheiten','Heist oder Verhandlung','Tessas Botschaft'],
      ['3:00–3:50','4 Fahrt nach Nachmorgen','Mobiler Konflikt','Ankunft im gestohlenen Tag'],
      ['3:50–4:00','Cliffhanger','Enthüllung','Der Dienstag bittet um Hilfe'],
      ['Abend 2  0:00–0:15','Rückblick','Sterne und Wünsche','Countdown steht'],
      ['0:15–1:05','5 Menschen aus Minuten','Erkundung, Tessa','Preis der Rückgabe'],
      ['1:05–1:55','6 Besetzung des Werks','Sozialer Mehrfrontenkonflikt','Zugang zum Tresor'],
      ['1:55–2:05','Pause','—','—'],
      ['2:05–3:05','7 Chronotresor','Drei Prüfungen','Nulluhr erwacht'],
      ['3:05–3:45','8 Wem gehört die Zeit','Finale und Entscheidung','Ende wählen'],
      ['3:45–4:00','Epiloge','Folgen und Debrief','Letzte Frage']], [3,4.8,6.4,3.2],8)

    page(doc); heading(doc,'2 Veyra und die Logik der fehlenden Zeit',1)
    para(doc,'Veyra ist eine terrassierte Kanalstadt mit genossenschaftlichen Märkten, begrünten Dächern und einer Verwaltung, die jeden revolutionären Impuls zuverlässig in Formular 88b umwandelt. Magie funktioniert hier durch öffentliche Übereinkünfte: Fahrpläne, Kalender und Verträge sind buchstäblich wirksam, solange genug Menschen an ihnen teilnehmen oder zu ihrer Teilnahme gezwungen werden.')
    heading(doc,'Sechs feste Wahrheiten',2)
    bullets(doc,[
      'Dienstag existiert weiterhin als Rohzeit im Zwischenraum Nachmorgen und als Pfand im Chronotresor; er wurde nicht vernichtet oder vollständig exportiert, sondern enteignet.',
      'Veyra durchlebt den Dienstag in administrativer Trance. Menschen führen Routinen und unmittelbare Schutzhandlungen aus; akute unbeaufsichtigte Gefahren werden durch Vertragsmagie gesichert. Danach bleibt subjektiv nur ein Herzschlag.',
      'Erinnerungen an Dienstage werden als Traum, déjà vu oder Verwaltungspanne umgedeutet. Biografische Anker können die Verdrängung durchbrechen.',
      'Morgen & Söhne exportiert nicht den rohen Tag, sondern Zeit-Zinsen: abgeschöpfte Lebensjahre, Regeneration und ungenutzte Möglichkeiten.',
      'Ein Vertragsbruch setzt das in Veyra gebundene Rohzeit-Pfand frei. Ohne neue gemeinsame Ordnung trifft die Rückwelle zuerst die am stärksten belasteten Viertel.',
      'Keine Einzelperson besitzt die eine richtige Lösung. Das Finale verlangt Zustimmung, Konflikt und Verantwortung.'
    ])
    heading(doc,'Zeitlogik im Spiel',2)
    add_table(doc,['Frage','Verbindliche Antwort'],[
      ['Warum bemerken die Figuren die Lücke?','Ihre Rollenanker resonieren gemeinsam mit Tessas illegaler Dienstagsquittung.'],
      ['Warum jetzt?','Vor einhundert Wochen - knapp zwei Jahren - erzwang ein Fürsorgestreik öffentliche Kontrolle; Morgen & Söhne beantwortete ihn mit der Neuvermessung und verlagerte die wöchentliche Prüfungshoheit vom Magistrat auf die Nulluhr. Nun steht die hundertste, endgültige Vollstreckungsprüfung an.'],
      ['Was geschieht körperlich?','Die Stadt handelt am Dienstag in administrativer Trance weiter. Fürsorge, Notfallreaktionen und Gefahrenabwehr geschehen, doch Erinnerung und frei verfügbare Zeit werden abgeschöpft.'],
      ['Was wird exportiert?','Nur Zeit-Zinsen verlassen Veyra. Der rohe Dienstag bleibt als systemische Kaution im Chronotresor und in Nachmorgen gebunden.'],
      ['Warum können NSC Dienstag sagen?','Nach Berührung eines Ankers, im Archiv, in Linie 7 oder in Nachmorgen. Außerhalb setzt Verdrängung nach einer Szene wieder ein.'],
      ['Kann man in Nachmorgen ruhen?','Ja, einmal kurz. Ein langer Rest kostet zwei Segmente auf Endgültiger Vertrag.'],
      ['Was geschieht bei Verzögerung?','Countdowns verändern Positionen und Preise; sie beenden die Geschichte nicht automatisch.'],
      ['Was ist eine Minute dort?','In Nachmorgen vergeht Stadtzeit nicht. Die Nulluhr zählt Vertragsfortschritt, keine physikalischen Minuten.']], [4.5,11.5])
    heading(doc,'Fraktionen',2)
    add_table(doc,['Fraktion','Will','Fürchtet','Bietet'],[
      ['Morgen & Söhne','Dauervertrag und exportierbare Zeit-Zinsen','Öffentliche Einsicht in Rohzeit-Pfand und Bilanz','Sicherheit, Bestechung, perfekte Pünktlichkeit'],
      ['Gemeinsamer Takt','Zeit als Gemeingut','Dass Chaos den Autoritären nutzt','Streiknetz, Schutz, Massenmacht'],
      ['Magistrat','Stabilität und Gesichtswahrung','Schuldenrückwelle, Aufstand','Zugang, Verwaltungsmagie, Legitimität'],
      ['Nachmorgen Kollektiv','Existenzrecht für die Vergessenen','Zwangsrückführung','Verborgene Wege, gespeicherte Erinnerungen']], [3.4,4.8,4.6,3.2],8)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ASSET/'map_city_illustrated_v1_5.png'),width=Cm(16.5))
    para(doc,'Abbildung 1  Veyra. Oberirdische Orte, unterirdische Räume und der Zwischenraum Nachmorgen sind getrennt markiert; Linie 7 zeigt die geheime erzählerische Route.',style=None).alignment=WD_ALIGN_PARAGRAPH.CENTER

    page(doc); heading(doc,'3 Die acht Szenen',1)
    heading(doc,'Szene 1 Der fehlende Morgen',2)
    para(doc,'Ort: Platz der fehlenden Glocke. Dauer: 45 Minuten. Ziel: Die Lücke körperlich erfahrbar machen, eine Rettung ermöglichen und die erste Spur ausgeben.')
    para(doc,'Lies oder paraphrasiere: Montagabend. Regen glänzt auf den Schienen. Die große Uhr hebt den Zeiger - und die Welt stolpert. Marktstände sind leerer, Bärte länger, eine am ausgelöschten Dienstag ausgehobene Baugrube gähnt im Pflaster. Eine Tram fährt an, als wäre die Strecke frei. Dann sieht die Fahrperson den Abgrund, reißt die Bremse und Metall kreischt. Ein versiegelter Wasserhahn trägt frisches Vertragswachs; der Eintopf daneben ist kalt, aber nicht verbrannt. Eine Pflegekraft hat wunde Hände und keine Erinnerung an ihre Schicht. Über dem Platz hängt ein Banner: Willkommen am Mittwoch. Niemand versteht, wo der gestrige Tag geblieben ist. Das ist das Beunruhigende.')
    heading(doc,'Situation und Entscheidungen',3)
    bullets(doc,[
      'Beim Sprung in den Mittwoch fährt eine zuvor sicher abgestellte Tram an. Fahrer*in Mio Kest hat die am Dienstag ausgehobene und abgesicherte Baugrube nicht im bewussten Gedächtnis, erkennt den Abgrund zu spät und bremst abrupt. Die Vorderachse hängt über der Kante; drei Fahrgäste und Mio sind gefährdet.',
      'Am Geländer klebt eine quittungsartige Papiermotte mit dem Datum Dienstag, 14. Herbstmond. Mio hat sie um 23:58 Uhr im Auftrag Tessas dort platziert; sie reagiert auf vier gemeinsam resonierende Zeitanker, nicht auf bestimmte Namen.',
      'Zwei Taktwächter*innen sichern nicht Menschen, sondern die Uhr. Eine Figur erkennt: Sie erwarten die Störung.'
    ])
    para(doc,'Rettung als Fortschritts-Countdown mit 4 Segmenten. Sinnvolle Aktionen gegen Schwierigkeit 10–12 füllen bei Erfolg 1 Segment; ein kritischer Erfolg 2. Bei Erfolg mit Fear folgt ein Preis: Stress, verlorene Ausrüstung, neue Gefahr oder Countdown Erhöhte Aufmerksamkeit +1. Bei Fehlschlag bleibt ein Hinweis zugänglich. Nach drei Spotlight-Wechseln kippt die Tram: alle Passagier*innen werden gerettet, aber jede rettende Figur markiert 1 Stress und die Wachleute nehmen die Quittung.',boldlead='Mechanik: ')
    para(doc,'Hinweise: Die Quittung nennt Morgen & Söhne und Vertrag 7/7. Mio behauptet zunächst, sich nur bruchstückhaft an die Haltestelle Nachmorgen zu erinnern; tatsächlich schützt dey die Route. Unter der Tram liegt blaues Archivwachs. Wer Mio Vertrauen schenkt, bemerkt dieselbe Tinte an deren Handschuh wie an der Papiermotte.')
    para(doc,'Harter Schnitt: Sobald zwei Hinweise gesichert und die Rettung entschieden ist, lässt du die Glocke dreizehnmal schlagen. Die Papiermotte flüstert: Findet Tessa, bevor die Nulluhr uns schließt.')

    heading(doc,'Szene 2 Markt ohne Gestern',2)
    para(doc,'Ort: Genossenschaftsmarkt. Dauer: 50 Minuten. Ziel: Fraktionen vorstellen, zwei von drei Zugängen zum Archiv gewinnen und Haltung provozieren.')
    para(doc,'Der Markt verkauft Mittwochsbrot zum Montagspreis; niemand kann erklären, wo die fehlende Lieferung blieb. Drei Gesprächsinseln laufen parallel: Gewerkschafterin Jori Venn sammelt Zeug*innen, Vertragsagent Orsino Vale kauft Erinnerungsstücke, und Bürgermeisterin Voss hält eine improvisierte Pressekonferenz.')
    para(doc,'Jori verteilt das Flugblatt des Gemeinsamen Takts (Handout 8). Die handschriftliche Warnung vor Schicht 3 zeigt, dass Morgen & Söhne den Streik bereits infiltriert hat. Wer Jori nicht nur um Zugang bittet, sondern Schutz für die gefährdeten Arbeiter*innen organisiert, erhält ihr Mitgliedssiegel ohne Probe und füllt Gemeinsamer Takt +1.')
    add_table(doc,['Insel','Was sie will','Was sie preisgibt','Probe oder Preis'],[
      ['Jori','Öffentliche Zusage gegen den Vertrag','Tessa versteckte Beweise im Archiv; eine geschützte Transportzelle existiert','Presence 11 oder konkrete Hilfe beim Streik'],
      ['Orsino','Die Quittung und Namen der Wissenden','Der Vertrag wird bei Nulluhr endgültig','Presence/Finesse 12; Erfolg kann Handel statt Täuschung sein'],
      ['Voss','Panik vermeiden','Ein Bruch kann Zeit zurückschlagen','Knowledge 12 oder mit Widerspruch leben']], [3,4,4.8,4.2],8)
    para(doc,'Zugänge: Joris Mitgliedssiegel; Voss’ vorläufiger Durchsuchungsbescheid; Orsinos Vertragsnadel; oder ein selbst entwickelter Weg. Zwei Zugänge machen Szene 3 leicht (Schwierigkeit 10), einer normal (12), keiner riskant (14).')
    para(doc,'GM Moves: Eine Händler*in vergisst ein Kind; Orsino lässt einen Namen aus der öffentlichen Liste streichen; Voss fordert die Gruppe auf, Verantwortung für Unruhe zu übernehmen; Linie 7 erscheint nur als Spiegelbild im Regen und verschwindet, sobald jemand direkt hinsieht.')

    heading(doc,'Szene 3 Archiv der kleinen Wahrheiten',2)
    para(doc,'Ort: Unter dem Amt für Wochentage. Dauer: 55 Minuten. Ziel: Vertragskern, Tessa und Linie 7 lokalisieren. Dies ist Erkundung, Heist, Verhandlung oder kurzer Kampf.')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ASSET/'map_archive_illustrated_v1_0.png'),width=Cm(16.6))
    para(doc,'Schnittillustration mit Spielzonen: Eingang links, Regalwald in der Mitte, Indexrad im Zentrum, Lesesaal oben und Kanalsteg am unteren Bildrand. Zonen statt Raster; der Wechsel in eine benachbarte Zone ist innerhalb eines Spotlights möglich.',style=None).alignment=WD_ALIGN_PARAGRAPH.CENTER
    bullets(doc,[
      'Lesesaal: Protokoll der Notabstimmung. Voss stimmte unter erpresserischer Drohung zu; vier Sitze waren bereits von Morgen & Söhne gekauft.',
      'Formularschublade: Formular 88b (Handout 9) klassifiziert gemeldete Existenzlücken als Phantomschmerz oder Zeitausgleich. Die Stempel zeigen: Das Amt kannte die Ausfälle und verwaltete sie als individuelle Beschwerden.',
      'Regalwald: Die Indexschwärmer verteidigen falsch einsortierte Wahrheiten. Man kann sie besänftigen, indem man einen verdrängten Fakt laut ausspricht.',
      'Indexrad: Drei Scheiben auf Arbeit, Erinnerung und Fürsorge ausrichten. Jede passende Deutung funktioniert; kein Rätselwortzwang.',
      'Kanalsteg: Geheimer Bahnsteig. Tessas phonographische Botschaft und der Fahrplan erscheinen, sobald jemand die Quittung auf das blaue Wachs legt. Der Erinnerungsfilter verbirgt die Linie vor Menschen ohne Dienstagsanker; Depot Null wird von Morgen & Söhne überwacht.'
    ])
    para(doc,'Tessas Botschaft: Der Dienstag lebt. Das Konsortium verkauft nur seine Zinsen; der rohe Tag liegt noch als Pfand unter dem Kalenderwerk. Der Vertrag hat sechs Siegel. Drei liegen in Menschen, drei im Nulluhrwerk. Brecht sie nicht blind. Gebt dem Tag eine Form, die niemand besitzen kann.')
    para(doc,'Konflikt: 1 Indexschwarm plus 2 Taktwächter*innen. Für vier Stufe-1-Figuren ist dies ein Standardkonflikt; die Gegner*innen ziehen sich zurück, sobald das Indexrad geöffnet ist oder jemand Beweise öffentlich überträgt.')

    page(doc); heading(doc,'Szene 4 Fahrt nach Nachmorgen',2)
    para(doc,'Ort: Linie 7. Dauer: 50 Minuten. Ziel: Übergang, persönliche Wahrheiten und ein bewegter Konflikt. Ende des ersten Abends.')
    para(doc,'Die Linie ist kein offenes Geheimnis. Derselbe kognitive Filter, der Dienstagserinnerungen tilgt, lässt sie wie eine gewöhnliche Tram oder bloße Spiegelung erscheinen. Sie manifestiert sich nur bei Regen, an verborgenen Halten oder für Menschen mit resonierenden Zeitankern. Mio, Tessa und wenige Versorger*innen bilden eine abgeschottete Schutzzelle; Jori kennt nur Gerüchte. Eine offene politische Nutzung würde Depot Null, Nachmorgen und alle Passagier*innen dem Konsortium ausliefern.')
    para(doc,'Die Linie 7 besteht aus drei Waggons: Erinnerungen, Möglichkeiten, verlorene Minuten. Jede Figur beantwortet in einem anderen Waggon eine Frage: Was würdest du mit einem geschenkten Tag tun? Wem hast du zu wenig Zeit gegeben? Welche Pflicht würdest du gern ablegen? Für eine offene Antwort erhält die Figur 1 Hope oder löscht 1 Stress.')
    para(doc,'Der Fahrkartenkontrolleur Herr Pünktlich ist kein Angestellter des Konsortiums, sondern ein unbeirrbarer magischer Parasit des Vertrages, der sich als Vertragsecho an das Schienennetz geklammert hat. Mio duldet ihn zähneknirschend, weil jeder gewaltsame Entfernungsversuch die Schutzmagie der Linie aufreißen und das Konsortium alarmieren würde. Er verlangt keinen Fahrschein, sondern den Beweis, dass die Reisenden an einem Dienstag existiert haben. Akzeptiere Gegenstände, Geschichten, Beziehungen, Widerspruch oder eine gelungene Aktion. Gewalt ruft zwei Minutenzehrer herbei; ein Gespräch kann ihn zum ersten Zweifel bringen.')
    para(doc,'Environment: Entgleisende Erinnerung, Schwierigkeit 12. Bei jedem Fear-Ergebnis rückt Entgleisung +1. Bei 3 Segmenten löst sich ein Waggon. Die Gruppe kann ihn retten (4 Fortschritt), evakuieren oder loslassen; jede Wahl prägt eine Endfrage.')
    para(doc,'Cliffhanger: Die Tram bricht durch eine weiße Wand. Dahinter liegt Veyra im goldenen Licht eines endlosen Dienstagnachmittags. Tausende Vergessene leben zwischen nicht zugestellten Briefen. Eine Person aus der Vergangenheit einer Figur tritt vor und sagt: Ihr seid spät. Natürlich seid ihr das.')

    heading(doc,'Szene 5 Menschen aus Minuten',2)
    para(doc,'Ort: Nachmorgen. Dauer: 50 Minuten. Ziel: Tessa finden, Stakes vermenschlichen und den sicheren Rückweg lernen.')
    para(doc,'Nachmorgen ist kein Gefängnis ohne Gesellschaft. Die Vergessenen haben Küchen, Werkstätten und ein Plenum aufgebaut. Manche wollen zurück, manche nicht. Tessa Quendel pflegt im Haus der ungesagten Sätze ein Gedächtnisbeet: Pflanzen wachsen aus ehrlich benannten Verlusten.')
    add_table(doc,['Begegnung','Wahl','Folge'],[
      ['Kind Lio sammelt Geburtstage','Einen eigenen wichtigen Tag erzählen oder abweisen','Erzählung: 1 Hope und Lios Schlüssel; Abweisung: Vertragsagent*innen finden die Gruppe'],
      ['Zeitkranke Arbeiter*innen','Vorräte teilen oder für den Rückweg sparen','Teilen: Gemeinsamer Takt +1; sparen: einmalig automatische Tresorflucht'],
      ['Tessa','Ihre Warnung ernst nehmen oder sofort zum Werk drängen','Zuhören: Ritual der Gemeinsamen Minute; drängen: 20 Minuten gewonnen, Endpreis steigt']], [4,6,6],8)
    para(doc,'Lio zeigt den Notizzettel der verlorenen Geburtstage (Handout 10). Durchgestrichene Namen bezeichnen keine Toten, sondern Menschen, deren Geburtstag in einem abgeschöpften Dienstag lag und aus Veyras bewusster Zeit verschwand. Wer den eigenen Geburtstag oder einen anderen wichtigen Tag ergänzt, bestätigt Lios Gegenarchiv und erhält die in der Tabelle genannte Belohnung.')
    para(doc,'Ritual der Gemeinsamen Minute: Im Finale können alle vier Figuren gleichzeitig je 1 Hope ausgeben. Dann darf keine Einzelpartei den Dienstag besitzen; entfernt ein gefülltes Segment von Endgültiger Vertrag und öffnet das Ende Gemeingut.')
    para(doc,'Tessa bestätigt: Mio schmuggelte die Papiermotte nach Veyra und platzierte sie am Geländer. Die Motte suchte keine vorherbestimmten Held*innen, sondern vier gleichzeitig resonierende Zeitanker. Tessa hielt selbst Jori die volle Route vor, weil eine kompromittierte Gewerkschaftsstruktur Depot Null gefährdet hätte.')
    para(doc,'Wahrheit: Die Rückwelle ist nicht unvermeidlich. Sie besteht aus dem weiterhin in Veyra gebundenen Rohzeit-Pfand und entsteht, wenn dieses ohne Verteilungsplan freigesetzt wird. Bereits exportierte Zeit-Zinsen kehren nicht zurück. Der Magistrat kennt nur die zwei Optionen Vertrag oder Chaos, weil das Konsortium alle dritten Möglichkeiten aus den Akten redigierte.')

    heading(doc,'Szene 6 Besetzung des Kalenderwerks',2)
    para(doc,'Ort: Kalenderwerk. Dauer: 50 Minuten. Ziel: Drei parallele Fronten lösen und den Zugang zum Chronotresor sichern.')
    para(doc,'Jori und der Gemeinsame Takt besetzen die Druckerei. Voss bringt Stadtwache, will aber verhandeln. Orsino aktiviert die automatischen Wochentagsstanzen, die neue Zeit-Zinsen aus dem Rohzeit-Pfand pressen. Lege drei Fortschrittsleisten mit je 3 Segmenten aus: Menge schützen, Maschinen stoppen, Voss überzeugen. Jede Aktion betrifft eine Leiste; kluge Teamaktionen dürfen zwei betreffen.')
    add_table(doc,['Front','Bei 3 Fortschritt','Bei 3 Gefahr'],[
      ['Menge','Streikende halten einen sicheren Korridor','Panik; 1 Kollateralschaden und Jori wird isoliert'],
      ['Maschinen','Keine neuen Vertragssiegel','Nulluhr +1 und 2 Papierknechte erscheinen'],
      ['Voss','Sie öffnet den Verwaltungsschacht','Sie befiehlt Räumung, bereut es aber sofort']], [3.5,6.2,6.3],8)
    para(doc,'Spotlight-Regel: Nach je zwei Spieler*innen-Spotlights folgt eine GM-Reaktion, früher bei Fear oder goldener Gelegenheit. Gewalt gegen Stadtwache füllt Gefahr Menge; Schutzhandlungen, öffentliche Beweise und konkrete Verhandlung füllen Fortschritt. Der Zugang öffnet sich spätestens nach fünf Runden der Fiktion – mit Kosten statt Sackgasse.')

    heading(doc,'Szene 7 Der Chronotresor',2)
    para(doc,'Ort: Unter der Nulluhr. Dauer: 60 Minuten. Ziel: Drei Siegel durch Entscheidungen lösen; Ressourcen fürs Finale setzen.')
    para(doc,'Der Chronotresor ist keine Lagerhalle voller bereits verkaufter Lebenszeit, sondern Reifekammer und Pfandhaus. Im Kern bleibt der rohe Dienstag gebunden. Die Stanzen schöpfen daraus Regeneration, Möglichkeiten und Lebensjahre als Zinsen ab; nur diese Derivate werden in andere Dimensionen exportiert. Ein Vertragsbruch öffnet das Rohzeit-Pfand und erzeugt deshalb eine lokale Rückwelle.')
    para(doc,'Im Bilanzsaal liegt Orsinos Bilanzbuch offen (Handout 11). Die getrennten Spalten Rohzeit und Zeit-Zinsen belegen, dass der Dienstag nie vollständig aus Veyra ausgeführt wurde. Wer den Auszug öffentlich macht, kann in Szene 8 einmal eine Fraktion ohne Probe davon überzeugen, dass Vertragstreue und Wahrheit nicht dasselbe sind.')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ASSET/'map_vault.png'),width=Cm(15.8))
    add_table(doc,['Raum','Frage','Mögliche Lösung','Preis bei Scheitern/Fear'],[
      ['A Schleuse','Was ist Zeit wert?','Etwas Wertvolles anbieten, Wertlogik verweigern, System überladen','1 Stress oder Nulluhr +1'],
      ['B Pfandkammer','Welche Erinnerung bleibt privat?','Eine Erinnerung schützen und eine teilen','Temporär Vulnerable oder Erinnerung als GM Move'],
      ['C Bilanzsaal','Wer trägt die Schulden?','Bilanz umschreiben, Verantwortliche benennen, kollektive Haftung ablehnen','Papierknechte oder Vertrag +1'],
      ['D Dienstag','Darf ein Tag Nein sagen?','Den personifizierten Dienstag als Beteiligten anerkennen','Ohne Zustimmung ist Gemeingut Ende gesperrt'],
      ['E Nulluhr','Welche Ordnung folgt?','Mindestens zwei Fraktionen auf einen Grundsatz verpflichten','Finale beginnt mit zusätzlichem Fear Move']], [2.7,4,5.2,4.1],7.8)
    para(doc,'Keine Tür verlangt eine konkrete Probe. Wenn eine Aktion riskant und folgenreich ist, nutze Schwierigkeit 12; bei starker Vorbereitung 10, bei direktem Widerstand 14. Jedes gelöste Siegel entfernt 1 HP von der Nulluhr oder deaktiviert ein Feature nach Wahl.')

    page(doc); heading(doc,'Szene 8 Wem gehört die Zeit',2)
    para(doc,'Ort: Bilanzsaal und Stadt zugleich. Dauer: 40 Minuten plus Epilog. Ziel: Finale als Kampf, Verhandlung oder Ritual; Entscheidung ohne falsche Binärlogik.')
    para(doc,'Orsino setzt das letzte Siegel. Die Nulluhr entfaltet sechs Zeiger und zeigt über der Stadt mögliche Zukünfte: geordnete Armut, chaotische Freiheit, privatisierte Unsterblichkeit, erschöpfte Fürsorge. Der Dienstag erscheint als vielstimmige Person und verlangt Beteiligung.')
    heading(doc,'Finalmechanik',3)
    bullets(doc,[
      'Nulluhr startet mit den verbleibenden HP und Features. Endgültiger Vertrag steht wie geführt. GM startet Szene 8 mit aktueller Fear, höchstens 8.',
      'Eine Figur kann die Nulluhr angreifen, ein Siegel umdeuten, eine Fraktion überzeugen, Menschen schützen oder das Ritual vorbereiten.',
      'Nach jedem vollständigen Umlauf durch die Gruppe tickt Endgültiger Vertrag +1, sofern niemand mindestens einen Erfolg gegen die Nulluhr erzielte.',
      'Bei vollem Countdown ist der Vertrag rechtskräftig, aber nicht das Abenteuer vorbei: Das Ende Vertrag mit Rissen tritt ein oder die Gruppe zahlt einen drastischen gemeinsamen Preis, um ein anderes Ende zu öffnen.',
      'Sobald die Nulluhr 0 HP hat, vier Siegel umgedeutet sind oder Orsino überzeugt/entmachtet wurde, wählt die Gruppe eine Ordnung und verhandelt ihre Bedingungen.'
    ])
    heading(doc,'Epilogfragen',3)
    bullets(doc,['Welche öffentliche Einrichtung trägt als erste den Namen Dienstag?','Wer erhält Zeit zurück, ohne dafür Dankbarkeit zu schulden?','Welche Beziehung wurde repariert, welche nicht?','Was tut jede Figur am ersten freien Dienstag?'])

    page(doc); heading(doc,'4 NSC Dossiers',1)
    dossiers=[
      ('Tessa Quendel','npc_tessa.png','Archivarin, sie/ihr','Wache Augen, tintengefleckte Hände, Mantel voller Randnotizen.','Zeit muss erinnerbar und gemeinsam verhandelbar sein.','Dass die Rückkehr Nachmorgen auslöscht.','Spricht präzise, korrigiert sich öffentlich, lacht an falschen Stellen.','Kennt das Ritual; gab Mio die auf vier resonierende Anker geprägte Papiermotte und hält die volle Route selbst vor Jori geheim.','Frage: Welche Wahrheit hast du aus Fürsorge versteckt?'),
      ('Jori Venn','npc_jori.png','Straßenbahnmechanikerin, sie/ihr','Kupferprothese, ölverschmierte Festkleidung.','Die Ausbeutung sichtbar machen und das Werk demokratisieren.','Dass spontane Wut die Schwächsten trifft.','Kurze Sätze, konkrete Aufgaben, herzlicher schwarzer Humor.','Kann Massen bewegen; ihr Bruder lebt in Nachmorgen. Sie weiß von einer Versorgungszelle, aber nicht von Route oder Fahrplan der Linie 7.','Frage: Wann wird Schutz zur Bevormundung?'),
      ('Elian Voss','npc_elian.png','Bürgermeisterin, sie/keine Präferenz','Müde Eleganz, sieben bewusst unterschiedliche Uhren.','Veyra zusammenhalten und ihre alte Entscheidung rechtfertigen.','Ein Chaos, in dem Reiche fliehen und Arme zahlen.','Verhandelt wie eine Haushaltsdebatte; sagt selten ich.','Wurde erpresst, verschwieg aber Alternativen. Kann Verbündete werden.','Frage: Was müsste sie öffentlich eingestehen?'),
      ('Orsino Vale','npc_orsino.png','Vertragsagent, er/ihm','Makelloser weißer Anzug, Schatten fünf Sekunden verspätet.','Beweisen, dass alles einen Preis und jeder Preis eine Eigentümer*in hat.','Unentgeltliche Solidarität; sie macht seine Magie unberechenbar.','Höflich, nie laut, beantwortet Gefühle mit Klauseln.','Ist selbst aus verkauften Lebensjahren zusammengesetzt; kann Befreiung wählen.','Frage: Ist eine Person verantwortlich für das System, das sie erschuf?'),
      ('Mio Kest','npc_mio.png','Fahrer*in Linie 7, dey/deren','Messingbrille, Fahrscheinlocher wie ein Dirigierstab.','Passagier*innen sicher zwischen den Tagen bewegen.','Die Linie zu verlieren, die Nachmorgen versorgt.','Erklärt Kosmologie als Nahverkehrsproblem.','Kennt jeden geheimen Halt; schmuggelte Tessas Papiermotte nach Veyra und platzierte sie um 23:58 Uhr am Geländer.','Frage: Welcher Umweg ist ein Zuhause?'),
      ('Dienstag','npc_dienstag.png','enteigneter Wochentag, keine festen Pronomen','Erscheint als wechselnder Chor vieler Alter und Körper.','Selbstbestimmung, Erinnerung und eine Rolle ohne Eigentum.','Als Ressource gerettet zu werden.','Vollendet Sätze, die Menschen aus Müdigkeit abbrachen.','Kann sich in Stadtzeit verteilen, wenn vier Stimmen zustimmen.','Frage: Was bedeutet Freiheit für etwas, das alle benutzen?')]
    for name,portrait,role,look,want,fear,voice,secret,q in dossiers:
        if name in ('Elian Voss','Mio Kest'):
            page(doc)
        heading(doc,name,2)
        pic=doc.add_paragraph(); pic.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.space_after=Pt(4)
        pic.add_run().add_picture(str(ASSET/portrait),width=Cm(4.5))
        para(doc,f'{role}. {look}')
        add_table(doc,['Will','Fürchtet','Stimme'],[[want,fear,voice]],[5.3,5.3,5.3],8)
        para(doc,secret,boldlead='Spielwert: '); para(doc,q,boldlead='Leitfrage: ')

    page(doc); heading(doc,'5 Gegner*innen und Environment',1)
    para(doc,'Alle Profile sind eigene Tier-1-Entwürfe. Richtwert ist Schwierigkeit 11, Angriff +1 und Damage Thresholds etwa 7/12. Solo-Profile sind widerstandsfähiger; Minions schwächer. Passe Fiktion vor Zahlen an: Gegner*innen fliehen, verhandeln und kapitulieren. Ein Standardkonflikt für vier Stufe-1-Figuren enthält etwa 2–4 Gegner*innen, nicht die gesamte kommunale Bürokratie auf einmal.')
    stat(doc,'Taktwächter*in','Standard',11,'7 / 12',4,2,'+1','1d8+3 phy','Very Close','Schützen Uhren, isolieren Zeug*innen, vermeiden Öffentlichkeit.',[
      ('Synchroner Schritt','Passiv','Wenn eine zweite Taktwache dasselbe Ziel im selben GM Turn angreift, erhält ihr Angriff +1.'),
      ('Festhalten','Aktion','Angriff gegen ein Ziel in Melee. Bei Erfolg 1d6+2 phy und Restrained, bis es sich mit einer Aktion befreit.'),
      ('Dienst nach Vorschrift','Reaktion','Wenn öffentliche Beweise präsentiert werden, markiert die Wache 1 Stress oder senkt ihre Waffe. Bei vollem Stress zieht sie sich zurück.')], 'enemy_taktwaechter.png')
    stat(doc,'Indexschwarm','Horde',10,'6 / 11',5,1,'+0','1d6+2 mag','Close','Verdeckt falsch einsortierte Wahrheiten und jagt laute Gewissheiten.',[
      ('Viele Zettel','Passiv','Solange der Schwarm mindestens 3 HP hat, erleidet er durch Angriffe höchstens 2 HP auf einmal.'),
      ('Papierkanten','Aktion','Alle Ziele in Very Close machen Agility Reaction Roll 10; bei Fehlschlag 1d6+2 mag.'),
      ('Wahre Einordnung','Reaktion','Wer eine verdrängte Wahrheit nennt, kann Presence 10 würfeln; bei Erfolg verliert der Schwarm 1 HP und wird kurz Harmless.')], 'enemy_indexschwarm.png')
    page(doc)
    stat(doc,'Minutenzehrer','Skulk',12,'6 / 11',3,2,'+2','1d8+2 mag','Very Close','Stehlen unbeobachtete Augenblicke, trennen Nachzügler*innen.',[
      ('Zwischen den Blicken','Passiv','Nach einem Fear-Ergebnis darf der Zehrer in Close Reichweite versetzen.'),
      ('Zeitbiss','Aktion','Bei Erfolg Schaden und Ziel markiert 1 Stress; falls kein Stress frei, zusätzlich 1 HP.'),
      ('Geliehener Augenblick','Fear','Gib 1 Fear aus: Unterbrich nach einer Spieler*innenaktion und bewege oder greife einmal an.')], 'enemy_minutenzehrer.png')
    stat(doc,'Papierknecht','Minion',9,'—',1,0,'+0','3 phy','Melee','Stempeln, blockieren, werden bei Widerspruch nervös.',[
      ('Minion','Passiv','Jeder erfolgreiche Angriff besiegt den Papierknecht; Schaden durch einen Knecht verursacht höchstens 1 HP.'),
      ('Formularlawine','Aktion','Ein Ziel in Very Close wird Vulnerable, bis es eine plausible Zuständigkeit nennt oder handelt.')], 'enemy_papierknecht.png')
    page(doc)
    stat(doc,'Herr Pünktlich','Social Bruiser',12,'8 / 14',6,3,'+1','1d10+2 mag','Close','Kontrolliert Zugehörigkeit, sehnt sich nach einem eigenen Ziel.',[
      ('Fahrkarten bitte','Aktion','Ein Ziel muss eine Dienstagserinnerung anbieten oder Presence/Knowledge 12 würfeln; bei Fehlschlag 1 Stress und Restrained durch Lochungen.'),
      ('Anschluss verpasst','Fear','Gib 1 Fear aus: Entgleisung +1 oder trenne eine Figur in den nächsten Waggon.'),
      ('Erster Zweifel','Reaktion','Wenn jemand ihm bedingungslose Zugehörigkeit anbietet, verliert er 2 Stress. Bei vollem Stress wechselt er die Seite.')], 'enemy_herr_puenktlich.png')
    stat(doc,'Orsino Vale','Leader',13,'8 / 15',7,4,'+2','1d10+3 mag','Far','Verhandelt unter Druck, benutzt andere als Klauseln, will nicht allein sein.',[
      ('Kleingedrucktes','Passiv','Einmal pro GM Turn kann Orsino Schaden um 1 HP reduzieren, wenn ein verbündeter Papierknecht in Close stattdessen besiegt wird.'),
      ('Bindende Klausel','Aktion','Angriff gegen ein Ziel in Far. Bei Erfolg Schaden und Ziel kann bis zum Ende seines nächsten Spotlights keine Hope ausgeben.'),
      ('Eigentumsvorbehalt','Fear','Gib 1 Fear aus: Markiere ein Objekt oder eine Zone als vertraglich gebunden. Benutzung erfordert 1 Stress oder eine Aktion gegen Schwierigkeit 12.'),
      ('Unbezahlbar','Reaktion','Ein Akt ohne erwartete Gegenleistung markiert Orsino 1 Stress. Bei vollem Stress muss er fliehen, kapitulieren oder seine Herkunft offenlegen.')], 'npc_orsino.png')
    page(doc)
    stat(doc,'Die Nulluhr','Solo',14,'9 / 16',10,4,'+2','1d12+3 mag','Far','Schließt Möglichkeiten, verteilt Lasten nach Zahlungsfähigkeit, vollendet den Vertrag.',[
      ('Relentless 2','Passiv','Kann bis zu zweimal pro GM Turn ins Spotlight gesetzt werden; Fear wird normal ausgegeben.'),
      ('Sechs Zeiger','Passiv','Bei 7/4/1 verbleibenden HP verliert die Uhr je einen Zeiger und die GM wählt: -1 Difficulty oder ein Feature fällt aus.'),
      ('Zukunft schneiden','Aktion','Angriff gegen bis zu zwei Ziele in Close zueinander; je Ziel separat würfeln, 1d10+2 mag.'),
      ('Montag für immer','Fear','Gib 1 Fear aus: Endgültiger Vertrag +1. Eine Figur kann sofort 1 Hope ausgeben und eine passende Erinnerung erzählen, um dies zu verhindern.'),
      ('Rücklauf','Reaktion','Wenn Severe Damage erlitten wird, Environment Rückwelle +1. Diese Reaktion höchstens einmal pro Runde der Fiktion.')], 'enemy_nulluhr.png')
    heading(doc,'Environment Die entgleisende Woche',2)
    para(doc,'Tier 1, Schwierigkeit 12. Impulse: Wege wiederholen, Menschen aus Szenen schneiden, Montag und Mittwoch überblenden, Uhren widersprechen lassen.')
    bullets(doc,['Passiv Zeitversatz: Bei einem Fear-Ergebnis kann die GM statt Fear zu nehmen Entgleisung +1 markieren.','Aktion Falscher Bahnsteig: Eine Figur wird von der Gruppe getrennt und sieht eine gewünschte Zukunft; sie kehrt zurück, wenn sie einen Preis ablehnt oder eine Aktion Schwierigkeit 11 schafft.','Fear Feature Rückwärtssturz: 1 Fear, alle in einer gefährlichen Zone machen Agility Reaction Roll 12; Fehlschlag 1d8+2 mag und 1 Stress.'])

    page(doc); heading(doc,'6 Countdowns und Leitungswerkzeuge',1)
    add_table(doc,['Countdown','Segmente','Start','Tickt wenn','Bei Vollendung'],[
      ['Endgültiger Vertrag','6','1','Szenen 1, 4, 6 oder 7 scheitern deutlich; langer Rest; Nulluhr Feature','Vertrag tritt in Kraft, andere Enden brauchen großen Preis'],
      ['Erhöhte Aufmerksamkeit','4','0','öffentliche Gewalt, Beweise verloren, wiederholte Fear Moves','Wachen kennen Gesichter; +1 Difficulty beim Werk, bis öffentlich unterstützt'],
      ['Entgleisung Linie 7','3','0','Fear in Szene 4 oder ignorierte Gefahr','Waggon löst sich; Rettung kostet Zeit oder Ressourcen'],
      ['Gemeinsamer Takt','4','1','Solidarität, Wahrheit, Schutz ohne Gegenleistung','Stadtgesellschaft trägt ein Ende; einmal 2 Fortschritt automatisch']], [3.8,2,2,5,5],7.8)
    heading(doc,'Countdown Praxis',2)
    para(doc,'Zeige alle Leisten offen. Sage vor riskanten Würfen, welcher Countdown betroffen sein kann. Ein Tick ist eine Folge, kein Urteil über Spielstil. Entferne Segmente, wenn die Gruppe strukturell handelt: Beweise verbreitet, Bündnisse schließt oder Verantwortung übernimmt. Countdowns dürfen Druck machen, aber keine kreative Lösung heimlich entwerten.')
    heading(doc,'Hinweismatrix ohne Sackgassen',2)
    add_table(doc,['Enthüllung','Quelle A','Quelle B','Quelle C'],[
      ['Dienstag existiert','Quittung Szene 1','Jori Szene 2','Indexrad Szene 3'],
      ['Nulluhr zählt Vertragsprüfungen','Orsino Szene 2','Tessas Botschaft','Neuvermessungsnachtrag im Archiv'],
      ['Stadt handelt in Trance','Unmöglicher Mittwoch','Voss Szene 2','Formular 88b Szene 3'],
      ['Rohzeit bleibt, Zinsen gehen','Tessa Szene 3','Tessa Szene 5','Orsinos Bilanzbuch Szene 7'],
      ['Linie 7 wird geschützt','Mios Tinte Szene 1','Joris Teilwissen','Tessa Szene 5'],
      ['Rückwelle ist verteilbar','Tessa Szene 5','Bilanzsaal Szene 7','Dienstag Szene 8'],
      ['Morgen & Söhne kaufte Stimmen','Archivprotokoll','Bilanzbuch Randnotizen','Voss gesteht'],
      ['Gemeingut ist möglich','Ritual Szene 5','Takt Countdown voll','Dienstags Zustimmung']], [4.5,4,4,4],8)
    heading(doc,'Improvisationsregeln',2)
    bullets(doc,['Bei einer plausiblen neuen Route: Ja, und ordne sie einer bestehenden Szene oder Front zu.','Bei verpasstem Hinweis: Gib ihn mit Komplikation, nicht mit Stillstand.','Bei frühem Angriff auf Orsino: Er kann verlieren; die Nulluhr und Eigentumslogik bleiben.','Bei Misstrauen gegen Tessa: Ihre Beweise sind prüfbar, ihre Wertung ist nicht sakrosankt.','Bei vollständigem Rückzug: Zeige die nächste Konsequenz und frage, was die Figuren schützen möchten.'])

    page(doc); heading(doc,'7 Mögliche Enden',1)
    endings=[
      ('Der Dienstag als Gemeingut','Ritual bekannt oder Gemeinsamer Takt voll; Zustimmung des Dienstags.','Das Rohzeit-Pfand wird über Stadtversammlungen, Pflege- und Erholungsfonds verteilt. Bereits exportierte Zeit-Zinsen bleiben Gegenstand späterer Reparationen. Nachmorgen erhält Autonomie und Übergänge.','Jede Figur gibt 1 Hope oder markiert 1 Stress; die erste Woche ist chaotisch, aber gemeinsam getragen.'),
      ('Rückgabe an den Kalender','Nulluhr besiegt und Verteilungsplan benannt.','Das Rohzeit-Pfand kehrt als normaler Dienstag zurück. Erinnerungen fluten zurück; exportierte Zeit-Zinsen kehren nicht automatisch heim und müssen politisch zurückgefordert werden.','Eine Figur opfert einen persönlichen Zeitanker, damit die Rückwelle langsam einsetzt.'),
      ('Nachmorgen bleibt frei','Kollektiv konsultiert und ein sicherer Übergang geschaffen.','Die Stadt behält die Sechstagewoche, löst die Exportklauseln, zahlt Reparationen und erkennt Nachmorgen mitsamt Rohzeit-Pfand als autonome Nachbarzeit an.','Veyra verliert wirtschaftliche Vorteile; der Konflikt wird politisch, nicht kosmisch.'),
      ('Der Vertrag mit Rissen','Countdown voll oder bewusster Kompromiss.','Morgen & Söhne behält Dienstag, aber Arbeitsschutz, Rückkehrrecht und öffentliche Kontrolle werden in die Klauseln gezwungen.','Das Eigentumsprinzip bleibt. Orsino nennt dies Vernunft; niemand muss ihm zustimmen.'),
      ('Die offene Woche','Dienstag stimmt zu; mindestens drei Fraktionen akzeptieren Ungewissheit.','Die sieben Tage lösen sich in lokale Rhythmen. Kalender werden Empfehlungen, Fürsorgezeiten verbindliche Gemeingüter.','Magische Systeme, die auf zentraler Zeit beruhen, fallen vorübergehend aus. Veyra erfindet sich neu; erstaunlicherweise kommt die Müllabfuhr trotzdem.')]
    for name,req,outcome,cost in endings:
        heading(doc,name,2); para(doc,req,boldlead='Öffnung: '); para(doc,outcome,boldlead='Folge: '); para(doc,cost,boldlead='Preis: ')
    heading(doc,'Enden kombinieren',2)
    para(doc,'Die Gruppe darf Elemente verbinden, wenn sie Verantwortung und Verteilung konkret benennt. Frage immer: Wer entscheidet? Wer trägt Kosten? Welche Stimme fehlt? Ein bittersüßes Ende ist willkommen; ein zynisches Ende ist nicht automatisch erwachsener. Zynismus ist oft nur Hoffnung mit einem schlecht sitzenden Schnurrbart.')

    page(doc); heading(doc,'8 One Shot Variante in vier Stunden',1)
    para(doc,'Diese Fassung verdichtet das Abenteuer, ohne die Kernentscheidung zu entfernen. Starte mit der Tramrettung, lass Mio Tessas aufgezeichnete Botschaft überbringen und kombiniere Archiv sowie Linie 7. Nutze nur die Countdowns Endgültiger Vertrag (4 Segmente, Start 1) und Gemeinsamer Takt (3 Segmente, Start 0).')
    add_table(doc,['Zeit','Block','Behalten','Streichen oder montieren'],[
      ['0:00–0:20','Anker und fehlender Morgen','Rettung, Quittung, Voss','Markt als zwei schnelle Fragen'],
      ['0:20–1:05','Archivbahnsteig','Indexrad, Tessas Enthüllung','Archivkampf nur bei aktivem Wunsch'],
      ['1:05–1:35','Linie 7','Eine Waggonfrage je Figur, Herr Pünktlich','Entgleisung auf 2 Segmente'],
      ['1:35–1:45','Pause','—','—'],
      ['1:45–2:25','Nachmorgen','Kollektiv, Ritual, Dienstag','Lio und Vorratswahl als Montage'],
      ['2:25–3:05','Kalenderwerk','Eine gemeinsame 4-Segment-Challenge','Drei Fronten zusammenlegen'],
      ['3:05–3:45','Nulluhr','Solo mit 8 HP; zwei Siegel','Chronotresor als drei Fragen'],
      ['3:45–4:00','Ende','Entscheidung und eine Epilogfrage je Figur','Keine zusätzliche Szene']], [3,4.5,4.5,4],8)
    heading(doc,'One Shot Balance',2)
    bullets(doc,['Start mit 3 Hope pro Figur und 4 Fear für die GM.','Höchstens ein voller Kampf vor dem Finale.','Nulluhr: 8 HP, Stress 3, Schwellen 8/14; deaktiviere Rücklauf.','Jeder gelöste Siegelpunkt verursacht 2 direkten Fortschritt gegen die Nulluhr, ohne Schaden zu würfeln.','Bei Zeitknappheit springe direkt zur Entscheidung, sobald die Nulluhr 4 HP oder weniger hat.'])

    page(doc); heading(doc,'9 Skalierung und Prüfung',1)
    heading(doc,'Skalierung',2)
    add_table(doc,['Gruppe','Anpassung'],[
      ['3 Figuren','Entferne je Konflikt eine Standardgegner*in; Nulluhr 8 HP; GM startet mit 3 Fear.'],
      ['4 Figuren','Profile wie gedruckt; GM startet mit 4 Fear.'],
      ['5 Figuren','Füge 2 Papierknechte oder 1 Standardgegner*in hinzu; Nulluhr 12 HP; GM startet mit 5 Fear.'],
      ['Unerfahrene Gruppe','Schwierigkeiten meist 10–12; Konsequenzen zuerst als Stress, Position oder Countdown.'],
      ['Taktische Gruppe','Mehr Zonenreaktionen und Ziele; nicht bloß HP erhöhen.']], [4.2,11.8],8)
    heading(doc,'Regelprüfung',2)
    add_table(doc,['Prüfpunkt','Ergebnis'],[
      ['Duality und GM Moves','Hope/Fear-Ergebnisse erzeugen erzählerische Folgen; GM würfelt d20 nur für Gegner*innen.'],
      ['Fear Ökonomie','Start 1 Fear pro Figur; Features nennen Kosten; Obergrenze 12 bleibt bestehen.'],
      ['Spotlight','Keine Initiative. Spotlight wechselt fiktional; Relentless erlaubt zusätzliche Solo-Aktivierung.'],
      ['Tier 1 Werte','Basis Difficulty 11; Angriffe meist +0 bis +2; Schaden im empfohlenen Bereich 1d6+2 bis 1d12+4.'],
      ['Damage','Gegner*innen verwenden HP und Schwellen; Papierknechte sind ausdrücklich Minions.'],
      ['Countdowns','Fortschritt und Konsequenzen sind offen; tick up/down wird konsistent als Segmente markieren/entfernen beschrieben.'],
      ['Conditions','Vulnerable und Restrained werden nur verwendet, wenn die Fiktion Dauer und Aufhebung nennt.']], [4.4,11.6],8)
    heading(doc,'Balanceprüfung',2)
    bullets(doc,['Kein Pflichtkampf. Drei mögliche Konflikte vor dem Finale, empfohlen höchstens zwei tatsächlich ausspielen.','Standardbegegnung Szene 3: effektive Gegneraktivierungen 2–3 pro GM Turn, Fluchtbedingung inklusive.','Nulluhr ist Solo, aber durch Siegel abschwächbar; soziale und rituelle Aktionen sind gleichwertige Fortschrittspfade.','Direkter HP-Verlust ist seltene harte Folge. Stress, Position, Trennung und Countdown dominieren.','Ein voller Countdown erzeugt ein schwierigeres Ende, keinen automatischen Totalverlust.'])
    heading(doc,'Zeitprüfung',2)
    para(doc,'Die acht Szenen umfassen 355 Minuten Netto-Spielzeit plus 20 Minuten Pausen, 20 Minuten Rahmung/Rückblick und 25 Minuten Epiloge sowie Puffer. Harte Schnittmarken verhindern, dass Ermittlungen die zweite Hälfte verschlucken. Werden 15 Minuten überzogen, kürze zuerst einen Kampf, dann eine Reise-Montage; nie die finale Entscheidung.')
    heading(doc,'Konsistenzprüfung',2)
    bullets(doc,['Hundertste Nulluhr, sechs Siegel und sieben verkaufte Jahre sind unterschiedliche Größen: Seit der Neuvermessung vor einhundert Wochen zählt die Nulluhr genau eine Vollstreckungsprüfung pro Woche. Die anstehende Prüfung ist daher die hundertste.','Veyra durchlebt Dienstage in administrativer Trance: Routinen, Fürsorge und Gefahrenabwehr laufen weiter; Erinnerung, Regeneration und frei verfügbare Zeit werden abgeschöpft. Die Gefahr an der Baugrube entsteht erst beim Sprung in den Mittwoch, als das bewusste Wissen über die dienstägliche Baustelle fehlt.','Der rohe Dienstag bleibt als Pfand in Veyra. Exportiert werden ausschließlich Zeit-Zinsen; deshalb kann nur das Rohzeit-Pfand als Rückwelle zurückschlagen.','Tessa wurde vor neun Monaten verschoben. Sie erreicht Veyra über Mio, die geschützte Linie 7 und eine auf vier resonierende Zeitanker geprägte Papiermotte.','Linie 7 wird vom Erinnerungsfilter verborgen, manifestiert sich nur unter Bedingungen und bleibt durch Zellstruktur sowie die Bewachung von Depot Null politisch schwer nutzbar. Herr Pünktlich ist kein Konsortiumsangestellter, sondern ein an das Schienennetz gebundenes Vertragsecho, das Mio nicht gefahrlos entfernen kann.','Voss ist verantwortlich, aber nicht alleinige Antagonistin; ihre Erpressung entschuldigt nicht die Vertuschung.','Nachmorgen vergeht außerhalb normaler Stadtzeit, dennoch zählt die Nulluhr als vertraglicher Prozess.','Dienstag ist Person und Infrastruktur zugleich; Zustimmung ersetzt nicht die Zustimmung der betroffenen Menschen.'])

    # Handouts
    handout_title(doc,1,'Die Dienstagsquittung')
    para(doc,'MORGEN & SÖHNE  Handel mit verlässlicher Zukunft')
    para(doc,'Empfangen von: Stadt Veyra')
    para(doc,'Gegenstand: Ein wiederkehrender Zeitraum von Sonnenaufgang bis Sonnenaufgang, im öffentlichen Kalender zwischen Montag und Mittwoch gelegen.')
    para(doc,'Vergütung: Aufschub sämtlicher kommunaler Verbindlichkeiten um sieben Jahre; Stabilisierung der Stadtzeit; diskrete Entlastung von Erinnerung und akuter physischer Gefährdung.')
    para(doc,'Eigentumsvorbehalt: Der veräußerte Zeitraum verbleibt als Rohzeit-Pfand in Veyra. Erinnerungen, Regeneration und ungenutzte Möglichkeiten dürfen als Zeit-Zinsen abgeschöpft und exportiert werden.')
    para(doc,'Status: Sechs von sechs Siegeln ausstehend. Endgültige Vollstreckung zur Hundertsten Nulluhr.')
    para(doc,'Handschriftlicher Zusatz: Wenn ihr vier das lesen könnt, hat die Stadt euch noch nicht ganz vergessen. Mio brachte mich hindurch. Linie 7. Blaues Wachs. Frag nach Tessa. — TQ')

    handout_title(doc,2,'Fahrplan der Linie 7')
    add_table(doc,['Halt','Abfahrt','Hinweis'],[
      ['Platz der fehlenden Glocke','Montag 24:00','Nur bei Regen und Ankerresonanz sichtbar'],['Archiv der kleinen Wahrheiten','Zwischen zwei Sätzen','Blaues Wachs vorzeigen'],['Verlorene Minuten','Wenn niemand hinsieht','Nicht aussteigen, wenn du dich selbst rufen hörst'],['Nachmorgen','Dienstag 14:17','Endstation und Anfang']], [6,4,6],9)
    para(doc,'Beförderungsbedingungen: Niemand wird wegen fehlender Zahlungsfähigkeit zurückgelassen. Erinnerungen sind kein gültiges Zahlungsmittel. Die Route darf nicht öffentlich verbreitet werden: Depot Null wird überwacht, und Sichtbarkeit gefährdet Nachmorgen. Beschwerden bitte an die Fahrer*innen; Beschwerden über die Existenz der Linie bitte an die Wirklichkeit.')

    handout_title(doc,3,'Protokoll der Notabstimmung')
    para(doc,'Auszug aus Sitzung 441 des Magistrats, sieben Jahre zuvor.')
    bullets(doc,['Anwesend: 11 Sitze. Offen erklärte Interessenkonflikte: 0. Tatsächliche Zahl später nachgewiesener Zahlungen durch Morgen & Söhne: 4.','Antrag Voss: Vertrag ablehnen; solidarischen Schuldenschnitt mit den Kanalstädten verhandeln. Ergebnis: 5 zu 6 abgelehnt.','Antrag Sitz 7: Dienstag veräußern. Ergebnis: 7 zu 4 angenommen.','Späterer Nachtrag 34, vor einhundert Wochen - knapp zwei Jahren - nach dem Fürsorgestreik: Die Neuvermessung überträgt die wöchentliche Prüfungshoheit vom Magistrat auf die Nulluhr. Die erste Prüfung folgt eine Woche nach der Neuvermessung; die anstehende Nulluhr ist Prüfung einhundert.','Randnotiz Tessa Quendel: Die Alternative wurde aus der öffentlichen Fassung entfernt. Ich bewahre die ursprüngliche Seite.'])

    handout_title(doc,4,'Tessas Botschaft')
    para(doc,'Der Dienstag ist nicht fort. Sein roher Zeitraum liegt noch als Pfand in Veyra; nur seine Zinsen werden exportiert. Er ist dort, wo Systeme alles ablegen, was ihre Bilanz stört. Menschen leben dort. Manche wollen zurück. Manche wollen in Ruhe gelassen werden. Alle verdienen eine Stimme.')
    para(doc,'Brecht die Nulluhr nicht, bevor ihr wisst, wohin ihre Zeit fließt. Sechs Siegel halten den Vertrag: Besitz, Schuld, Schweigen, Gehorsam, Alternativlosigkeit und Eile. Jedes kann mit Gewalt gebrochen werden. Keines muss.')
    para(doc,'Wenn ihr nur den Kalender repariert, repariert ihr vielleicht auch die Ordnung, die ihn verkauft hat.')

    handout_title(doc,5,'Die sechs Siegel')
    add_table(doc,['Siegel','Frage','Notizen'],[
      ['Besitz','Kann Zeit jemandem gehören?','____________________________'],['Schuld','Wer soll zahlen?','____________________________'],['Schweigen','Welche Wahrheit wird öffentlich?','____________________________'],['Gehorsam','Wessen Befehl endet hier?','____________________________'],['Alternativlosigkeit','Welche dritte Möglichkeit entsteht?','____________________________'],['Eile','Was verdient trotz Druck Beratung?','____________________________']], [4,6,6],9)

    handout_title(doc,6,'Offene Countdowns')
    for name,n in [('ENDGÜLTIGER VERTRAG',6),('ERHÖHTE AUFMERKSAMKEIT',4),('ENTGLEISUNG LINIE 7',3),('GEMEINSAMER TAKT',4)]:
        p=doc.add_paragraph(); p.add_run(name).bold=True
        p.add_run('   ' + '  '.join(['○']*n)).font.size=Pt(22)
        para(doc,'Auslöser und Folgen stehen im Spielleitungsheft. Markiert offen und besprecht jede Veränderung.')

    handout_title(doc,7,'Karte von Veyra')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ASSET/'map_city_players_v1_0.png'),width=Cm(17))
    para(doc,'Öffentliche Stadtkarte. Wege sind erzählerisch, nicht maßstäblich; manche Straßen folgen eher einer guten Geschichte als der Geometrie.',style=None).alignment=WD_ALIGN_PARAGRAPH.CENTER

    image_handout(doc,8,'Flugblatt des Gemeinsamen Takts','handout_common_beat.jpg','Ausgabeort: Szene 2 Markt ohne Gestern. Die Warnung vor Schicht 3 ist handschriftlich ergänzt.')
    image_handout(doc,9,'Formular 88b zur Meldung temporärer Existenzlücken','handout_form_88b.jpg','Fundort: Szene 3 Archiv der kleinen Wahrheiten, Formularschublade.')
    image_handout(doc,10,'Lios Notizzettel der verlorenen Geburtstage','handout_lio_birthdays.jpg','Ausgabeort: Szene 5 Menschen aus Minuten. Lio bewahrt Daten, an die Veyra sich nicht erinnern darf.')
    image_handout(doc,11,'Auszug aus Orsinos Bilanzbuch','handout_orsino_ledger.jpg','Fundort: Szene 7 Chronotresor, Bilanzsaal. Rohzeit und Zeit-Zinsen stehen in getrennten Konten.')

    page(doc); heading(doc,'Leitungsschnellreferenz',1)
    add_table(doc,['Wenn …','Dann …'],[
      ['die Gruppe festhängt','Gib den wichtigsten Hinweis durch eine Konsequenz; frage, welche Kosten sie akzeptiert.'],['ein Kampf zu lang wird','Lass Motive sichtbar werden, biete Rückzug, Kapitulation oder ein verändertes Ziel.'],['Fear sich stapelt','Gib es für Features, Environment und Spotlight aus; horte nicht bis zum Finale.'],['Zeit knapp wird','Schneide Reise, nicht Entscheidung; fasse Nebenkonflikte als Montage zusammen.'],['eine kreative Lösung überrascht','Ordne sie einer Front oder einem Siegel zu und gib echten Fortschritt.'],['das Ende unklar ist','Frage: Wer entscheidet, wer zahlt, wer fehlt? Dann beschreibe konkrete Folgen.']], [5,11],8.5)
    heading(doc,'Szenen in einem Satz',2)
    bullets(doc,['1 Rette Menschen und entdecke die Lücke.','2 Triff Fraktionen und beschaffe Zugang.','3 Finde Vertrag, Tessa und Linie 7.','4 Fahre durch Erinnerungen nach Nachmorgen.','5 Lerne die Betroffenen und eine dritte Möglichkeit kennen.','6 Halte drei Fronten im Kalenderwerk.','7 Löse sechs Siegel als Entscheidungen.','8 Streite, kämpfe oder ritualisiere um die Eigentumsfrage.'])
    heading(doc,'Letzter Blick vor dem Spiel',2)
    bullets(doc,['Vier Rollenanker verteilt','Sicherheitswerkzeuge vereinbart','4 Fear bereitgelegt','Countdowns sichtbar','Handouts 1–11 getrennt und szenenweise sortiert','Karten griffbereit','Pause und harte Schnittzeiten notiert','Ein Dienstag im Kalender freigehalten – rein vorsorglich'])

    path=OUT/'Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft.docx'
    doc.save(path)
    print(path)

if __name__=='__main__': build()

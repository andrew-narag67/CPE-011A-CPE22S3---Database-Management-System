# ==========================================
# SECTION 6: PDF DESIGN & STYLES (REPORTLAB)
# ==========================================
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.platypus import Image as RLImage

def _pdf_colors():
    return dict(
        BORD = colors.HexColor("#D0D7E3"),
        BLU  = colors.HexColor(TIP_BLUE),
        GOLD = colors.HexColor(TIP_GOLD),
        LITE = colors.HexColor(TIP_LIGHT),
        MUTE = colors.HexColor(TIP_MUTED),
        RED  = colors.HexColor(TIP_RED),
        GRN  = colors.HexColor(TIP_GREEN),
        DARK = colors.HexColor(TIP_DARK),
    )

def _pdf_styles(C):
    S = getSampleStyleSheet()
    def sty(name, **kw):
        return ParagraphStyle(name, parent=S["Normal"], **kw)
    return dict(
        TITLE = sty("T",  fontName="Helvetica-Bold", fontSize=16, textColor=C["BLU"],  alignment=TA_CENTER),
        SUB   = sty("S",  fontName="Helvetica",       fontSize=9,  textColor=C["MUTE"], alignment=TA_CENTER),
        SEC   = sty("H",  fontName="Helvetica-Bold",  fontSize=11, textColor=C["BLU"],  spaceBefore=10, spaceAfter=4),
        SMALL = sty("Sm", fontName="Helvetica",       fontSize=8,  textColor=C["MUTE"]),
        BODY  = sty("B",  fontName="Helvetica",       fontSize=9,  textColor=C["DARK"]),
        BOLD  = sty("Bd", fontName="Helvetica-Bold",  fontSize=9,  textColor=C["DARK"]),
        FOOT  = sty("Ft", fontName="Helvetica",       fontSize=7,  textColor=C["MUTE"], alignment=TA_CENTER),
    )

def _tbl_style(hdr_color, alt, BORD):
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  hdr_color),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, alt]),
        ("BOX",           (0,0),(-1,-1), 0.5, BORD),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORD),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ])

# ==========================================
# SECTION 7: PDF REPORT GENERATION
# ==========================================
def _pdf_header(story, C, ST, subtitle):
    logo_cell = ""
    if os.path.exists(LOGO_PATH):
        try: logo_cell = RLImage(LOGO_PATH, width=20*mm, height=20*mm)
        except: pass
    title_block = [
        Paragraph("TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES", ST["SUB"]),
        Paragraph("Student Clinical Database System", ST["TITLE"]),
        Paragraph(subtitle, ST["SUB"]),
    ]
    ht = Table([[logo_cell, title_block]], colWidths=[26*mm, None])
    story.append(ht)
    story.append(HRFlowable(width="100%", thickness=4, color=C["GOLD"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C["BLU"], spaceAfter=5))

def _pdf_footer(story, C, ST):
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=C["GOLD"]))
    story.append(Paragraph("SCDS | TIP School Clinic", ST["FOOT"]))

def gen_clinic_report(path, by="System"):
    C, ST, d = _pdf_colors(), _pdf_styles(_pdf_colors()), db_report()
    doc = SimpleDocTemplate(path, pagesize=A4)
    story = []
    _pdf_header(story, C, ST, "Summary Health Report")
    
    # Overview Stats Table
    summary = Table([["Total Students", "Total Consultations"], [str(d["ts"]), str(d["tc"])]], colWidths=[85*mm, 85*mm])
    summary.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),C["BLU"]), ("TEXTCOLOR",(0,0),(-1,0),colors.white), ("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(summary)
    
    _pdf_footer(story, C, ST)
    doc.build(story); return path

# ==========================================
# SECTION 8: UI GLOBAL STYLESHEET (GSS)
# ==========================================
GSS = f"""
QWidget {{ font-family:'Segoe UI',Arial; font-size:13px; background-color:{TIP_LIGHT}; color:{TIP_DARK}; }}
QLineEdit, QTextEdit {{ border:1.5px solid {TIP_BORD}; border-radius:6px; padding:5px; background:white; }}
QPushButton {{ background:{TIP_BLUE}; color:white; border-radius:6px; padding:8px; font-weight:bold; }}
QPushButton:hover {{ background:#00216b; }}
QPushButton#gold {{ background:{TIP_GOLD}; color:{TIP_DARK}; }}
QHeaderView::section {{ background:{TIP_BLUE}; color:white; font-weight:bold; }}
QTabWidget::pane {{ border:1.5px solid {TIP_BORD}; }}
"""

# ==========================================
# SECTION 9: PYQT5 UI HELPERS
# ==========================================
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def banner(title, sub=""):
    f = QFrame(); f.setFixedHeight(70 if sub else 54); f.setStyleSheet(f"background:{TIP_BLUE};")
    lay = QHBoxLayout(f)
    if os.path.exists(LOGO_PATH):
        lbl = QLabel(); lbl.setPixmap(QPixmap(LOGO_PATH).scaled(40,40,Qt.KeepAspectRatio)); lay.addWidget(lbl)
    col = QVBoxLayout()
    t = QLabel(title); t.setStyleSheet("color:white; font-size:16px; font-weight:bold;"); col.addWidget(t)
    if sub:
        s = QLabel(sub); s.setStyleSheet(f"color:{TIP_GOLD}; font-size:10px;"); col.addWidget(s)
    lay.addLayout(col); lay.addStretch(); return f

def gold_bar():
    f = QFrame(); f.setFixedHeight(3); f.setStyleSheet(f"background:{TIP_GOLD};"); return f

def stat_card(val, lbl, color=TIP_BLUE):
    f = QFrame(); f.setStyleSheet(f"background:white; border:1px solid {TIP_BORD}; border-radius:8px;")
    lay = QVBoxLayout(f)
    v = QLabel(val); v.setStyleSheet(f"color:{color}; font-size:24px; font-weight:bold;"); v.setAlignment(Qt.AlignCenter)
    l = QLabel(lbl); l.setStyleSheet(f"color:{TIP_MUTED}; font-size:10px;"); l.setAlignment(Qt.AlignCenter)
    lay.addWidget(v); lay.addWidget(l); return f
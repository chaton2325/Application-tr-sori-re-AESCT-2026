# -*- coding: utf-8 -*-
"""Génération des documents PDF de l'AESCT (charte orange / rouge)."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from datetime import datetime
import io

# --- Charte graphique AESCT ---
ORANGE = colors.HexColor('#ea580c')
ORANGE_LIGHT = colors.HexColor('#fff1e5')
ORANGE_PALE = colors.HexColor('#fff8f1')
RED = colors.HexColor('#dc2626')
RED_DARK = colors.HexColor('#991b1b')
BROWN_DARK = colors.HexColor('#431407')
MUTED = colors.HexColor('#9a6a55')
BORDER = colors.HexColor('#fed7aa')

PAGE_W, PAGE_H = A4

MONTHS_FR = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
    7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}

# --- Styles de paragraphes ---
STYLE_TITLE = ParagraphStyle(
    'ReportTitle', fontName='Helvetica-Bold', fontSize=17, leading=22,
    textColor=BROWN_DARK, alignment=TA_CENTER, spaceAfter=4
)
STYLE_SUBTITLE = ParagraphStyle(
    'ReportSubtitle', fontName='Helvetica', fontSize=10.5, leading=14,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=12
)
STYLE_CELL = ParagraphStyle(
    'Cell', fontName='Helvetica', fontSize=9, textColor=BROWN_DARK, leading=12
)
STYLE_CELL_RIGHT = ParagraphStyle(
    'CellRight', parent=STYLE_CELL, alignment=TA_RIGHT
)


def _fmt_amount(value):
    """1234.5 -> '1 234,50 TND'"""
    s = f"{float(value):,.2f}".replace(',', ' ').replace('.', ',')
    return f"{s} TND"


def _draw_page_frame(canvas, doc, subtitle):
    """En-tête et pied de page dessinés sur chaque page."""
    canvas.saveState()

    # --- Bandeau d'en-tête dégradé orange -> rouge (simulé par bandes) ---
    band_h = 2.6 * cm
    steps = 60
    for i in range(steps):
        t = i / (steps - 1)
        r = 0.976 + (0.863 - 0.976) * t   # #f97316 -> #dc2626
        g = 0.451 + (0.149 - 0.451) * t
        b = 0.086 + (0.149 - 0.086) * t
        canvas.setFillColorRGB(r, g, b)
        x = (PAGE_W / steps) * i
        canvas.rect(x, PAGE_H - band_h, PAGE_W / steps + 1, band_h, stroke=0, fill=1)

    # Liseré rouge foncé sous le bandeau
    canvas.setFillColor(RED_DARK)
    canvas.rect(0, PAGE_H - band_h - 0.12 * cm, PAGE_W, 0.12 * cm, stroke=0, fill=1)

    # Logo "AESCT" dans un cadre blanc arrondi
    canvas.setFillColor(colors.white)
    canvas.roundRect(1.5 * cm, PAGE_H - 2.15 * cm, 1.7 * cm, 1.7 * cm, 0.25 * cm, stroke=0, fill=1)
    canvas.setFillColor(RED)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawCentredString(2.35 * cm, PAGE_H - 1.4 * cm, "AESCT")

    # Nom de l'association
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 19)
    canvas.drawString(3.6 * cm, PAGE_H - 1.35 * cm, "AESCT")
    canvas.setFont('Helvetica', 10)
    canvas.drawString(3.6 * cm, PAGE_H - 1.85 * cm, "Association AESCT — Service Trésorerie")

    # Sous-titre du document, à droite
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawRightString(PAGE_W - 1.5 * cm, PAGE_H - 1.6 * cm, subtitle)

    # --- Pied de page ---
    canvas.setStrokeColor(ORANGE)
    canvas.setLineWidth(1.2)
    canvas.line(1.5 * cm, 1.6 * cm, PAGE_W - 1.5 * cm, 1.6 * cm)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.5 * cm, 1.15 * cm,
                      f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    canvas.drawCentredString(PAGE_W / 2, 1.15 * cm, "AESCT — Application de Trésorerie")
    canvas.setFillColor(RED)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawRightString(PAGE_W - 1.5 * cm, 1.15 * cm, f"Page {doc.page}")

    canvas.restoreState()


def _build_doc(buffer, subtitle):
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=3.6 * cm, bottomMargin=2.2 * cm,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        title=f"AESCT - {subtitle}"
    )
    on_page = lambda c, d: _draw_page_frame(c, d, subtitle)
    return doc, on_page


def _base_table_style(n_rows):
    """Style commun : en-tête orange, lignes alternées crème, total rouge."""
    style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), ORANGE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9.5),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), BROWN_DARK),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Quadrillage discret
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
        ('BOX', (0, 0), (-1, -1), 0.8, ORANGE),
        # Ligne de total
        ('BACKGROUND', (0, -1), (-1, -1), RED),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
    ]
    # Lignes alternées (hors en-tête et total)
    for row in range(1, n_rows - 1):
        if row % 2 == 0:
            style.append(('BACKGROUND', (0, row), (-1, row), ORANGE_PALE))
        else:
            style.append(('BACKGROUND', (0, row), (-1, row), colors.white))
    return TableStyle(style)


def _summary_card(items):
    """Petit encadré récapitulatif (libellé / valeur)."""
    rows = [[Paragraph(f"<b>{label}</b>", STYLE_CELL), Paragraph(value, STYLE_CELL_RIGHT)]
            for label, value in items]
    table = Table(rows, colWidths=[9 * cm, 9 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ORANGE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table


# =====================================================================
# Reçu de versement
# =====================================================================
def generate_receipt_pdf(member_name, amount, date, reason):
    buffer = io.BytesIO()
    doc, on_page = _build_doc(buffer, "Reçu de versement")
    story = []

    story.append(Paragraph("Reçu de versement officiel", STYLE_TITLE))
    story.append(Paragraph("Ce document atteste du versement décrit ci-dessous.", STYLE_SUBTITLE))
    story.append(Spacer(1, 0.3 * cm))

    story.append(_summary_card([
        ("Date du versement", str(date)),
        ("Bénéficiaire", str(member_name)),
        ("Motif", str(reason)),
    ]))
    story.append(Spacer(1, 0.7 * cm))

    # Montant mis en avant
    amount_table = Table(
        [[Paragraph("<b>MONTANT VERSÉ</b>",
                    ParagraphStyle('AmtLabel', fontName='Helvetica-Bold', fontSize=10,
                                   textColor=colors.white, alignment=TA_CENTER)),
          ],
         [Paragraph(f"<b>{_fmt_amount(amount)}</b>",
                    ParagraphStyle('AmtValue', fontName='Helvetica-Bold', fontSize=22,
                                   textColor=RED_DARK, alignment=TA_CENTER, leading=28)),
          ]],
        colWidths=[10 * cm]
    )
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RED),
        ('BACKGROUND', (0, 1), (0, 1), ORANGE_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, RED),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 1), (-1, 1), 14),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    wrapper = Table([[amount_table]], colWidths=[18 * cm])
    wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(wrapper)
    story.append(Spacer(1, 1.6 * cm))

    # Zone de signature
    sig = Table(
        [[Paragraph("Signature du Trésorier",
                    ParagraphStyle('Sig', fontName='Helvetica-Oblique', fontSize=9,
                                   textColor=MUTED, alignment=TA_CENTER))],
         [Spacer(1, 2.2 * cm)]],
        colWidths=[6.5 * cm]
    )
    sig.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, ORANGE),
        ('BACKGROUND', (0, 0), (-1, 0), ORANGE_LIGHT),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ]))
    sig_wrapper = Table([[sig]], colWidths=[18 * cm])
    sig_wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT')]))
    story.append(sig_wrapper)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer


# =====================================================================
# Rapport des contributions (cause / collecte)
# =====================================================================
def generate_contributions_report_pdf(cause_name, contributions, total_collected):
    buffer = io.BytesIO()
    doc, on_page = _build_doc(buffer, "Rapport des contributions")
    story = []

    story.append(Paragraph(f"Rapport des Contributions — {cause_name}", STYLE_TITLE))
    story.append(Paragraph(
        f"Détail des contributions enregistrées pour la cause « {cause_name} »",
        STYLE_SUBTITLE
    ))

    story.append(_summary_card([
        ("Nombre de contributions", str(len(contributions))),
        ("Total collecté", _fmt_amount(total_collected)),
    ]))
    story.append(Spacer(1, 0.5 * cm))

    data = [['Date', 'Contributeur', 'Montant', 'Notes']]
    for c in contributions:
        data.append([
            c.date_paid.strftime('%d/%m/%Y'),
            Paragraph(c.member.full_name, STYLE_CELL),
            _fmt_amount(c.amount),
            Paragraph(c.notes or '—', STYLE_CELL),
        ])
    data.append(['', 'TOTAL COLLECTÉ', _fmt_amount(total_collected), ''])

    table = Table(data, colWidths=[2.6 * cm, 5.4 * cm, 3.6 * cm, 6.4 * cm], repeatRows=1)
    style = _base_table_style(len(data))
    style.add('ALIGN', (0, 0), (0, -1), 'CENTER')
    style.add('ALIGN', (2, 0), (2, -1), 'RIGHT')
    table.setStyle(style)
    story.append(table)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer


# =====================================================================
# Rapport mensuel des cotisations
# =====================================================================
def generate_cotisations_report_pdf(month, year, cotisations, total_collected):
    buffer = io.BytesIO()
    doc, on_page = _build_doc(buffer, "Rapport des cotisations")
    story = []

    month_name = MONTHS_FR.get(int(month), str(month))
    story.append(Paragraph(f"Rapport des Cotisations — {month_name} {year}", STYLE_TITLE))
    story.append(Paragraph(
        f"État des cotisations des adhérents pour la période {month_name} {year}",
        STYLE_SUBTITLE
    ))

    total_expected = sum(float(c.amount_expected) for c in cotisations)
    story.append(_summary_card([
        ("Nombre de versements", str(len(cotisations))),
        ("Total attendu", _fmt_amount(total_expected)),
        ("Total collecté", _fmt_amount(total_collected)),
    ]))
    story.append(Spacer(1, 0.5 * cm))

    data = [['Adhérent', 'Attendu', 'Versé', 'Reliquat', 'Date']]
    for c in cotisations:
        balance = float(c.amount_expected) - float(c.amount_paid)
        data.append([
            Paragraph(c.member.full_name, STYLE_CELL),
            _fmt_amount(c.amount_expected),
            _fmt_amount(c.amount_paid),
            _fmt_amount(balance) if balance > 0 else '—',
            c.date_paid.strftime('%d/%m/%Y'),
        ])
    data.append(['TOTAL', '', _fmt_amount(total_collected), '', ''])

    table = Table(data, colWidths=[5.6 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm], repeatRows=1)
    style = _base_table_style(len(data))
    style.add('ALIGN', (1, 0), (3, -1), 'RIGHT')
    style.add('ALIGN', (4, 0), (4, -1), 'CENTER')
    table.setStyle(style)
    story.append(table)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer

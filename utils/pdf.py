# -*- coding: utf-8 -*-
"""Génération des documents PDF de l'AESCT (charte orange / rouge)."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
)
from datetime import datetime
from collections import defaultdict
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
GREEN = colors.HexColor('#16a34a')
GREEN_DARK = colors.HexColor('#166534')
GREEN_LIGHT = colors.HexColor('#f0fdf4')

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
STYLE_SECTION = ParagraphStyle(
    'SectionHeader', fontName='Helvetica-Bold', fontSize=12.5, leading=16,
    textColor=colors.white, alignment=TA_LEFT
)
STYLE_SECTION_SUB = ParagraphStyle(
    'SectionHeaderSub', fontName='Helvetica', fontSize=8.5, leading=11,
    textColor=colors.white, alignment=TA_LEFT
)
STYLE_EMPTY = ParagraphStyle(
    'EmptyState', fontName='Helvetica-Oblique', fontSize=9.5, leading=13,
    textColor=MUTED, alignment=TA_CENTER
)
STYLE_TOTAL_LABEL = ParagraphStyle(
    'TotalLabel', fontName='Helvetica-Bold', fontSize=9.5, leading=12,
    textColor=colors.white, alignment=TA_RIGHT
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


def _section_banner(title, subtitle, color=ORANGE, icon=None):
    """Bandeau de titre de section (pleine largeur, coloré)."""
    label = f"{icon}  {title}" if icon else title
    cell = Paragraph(f"<b>{label}</b>", STYLE_SECTION)
    rows = [[cell]]
    if subtitle:
        rows.append([Paragraph(subtitle, STYLE_SECTION_SUB)])
    table = Table(rows, colWidths=[18 * cm])
    style = [
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2 if subtitle else 7),
    ]
    if subtitle:
        style.append(('TOPPADDING', (0, 1), (-1, 1), 0))
        style.append(('BOTTOMPADDING', (0, 1), (-1, 1), 7))
    table.setStyle(TableStyle(style))
    return table


def _empty_state(text):
    """Message discret pour une section sans opérations."""
    table = Table([[Paragraph(text, STYLE_EMPTY)]], colWidths=[18 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ORANGE_PALE),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    return table


def _solde_box(label, amount):
    """Grand encadré mettant en avant le solde net (vert si positif, rouge sinon)."""
    positive = amount >= 0
    main_color = GREEN if positive else RED
    bg_color = GREEN_LIGHT if positive else ORANGE_LIGHT
    text_color = GREEN_DARK if positive else RED_DARK
    sign = '+' if positive else ''
    table = Table(
        [[Paragraph(f"<b>{label}</b>",
                    ParagraphStyle('SoldeLabel', fontName='Helvetica-Bold', fontSize=11,
                                   textColor=colors.white, alignment=TA_CENTER))],
         [Paragraph(f"<b>{sign}{_fmt_amount(amount)}</b>",
                    ParagraphStyle('SoldeValue', fontName='Helvetica-Bold', fontSize=26,
                                   textColor=text_color, alignment=TA_CENTER, leading=32))]],
        colWidths=[18 * cm]
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), main_color),
        ('BACKGROUND', (0, 1), (-1, 1), bg_color),
        ('BOX', (0, 0), (-1, -1), 1.2, main_color),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, 1), 16),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 16),
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
def generate_contributions_report_pdf(cause_name, contributions, total_collected,
                                       income_entries=None, expense_entries=None,
                                       balance=None, overall_balance=None):
    income_entries = income_entries or []
    expense_entries = expense_entries or []

    buffer = io.BytesIO()
    doc, on_page = _build_doc(buffer, "Rapport des contributions")
    story = []

    story.append(Paragraph(f"Rapport des Contributions — {cause_name}", STYLE_TITLE))
    story.append(Paragraph(
        f"Détail des contributions et des opérations rattachées à la cause « {cause_name} »",
        STYLE_SUBTITLE
    ))

    summary_items = [
        ("Nombre de contributions", str(len(contributions))),
        ("Total collecté (contributions)", _fmt_amount(total_collected)),
    ]
    if balance is not None:
        summary_items.append(("Encaissements liés", _fmt_amount(balance['income_linked'])))
        summary_items.append(("Décaissements liés", _fmt_amount(balance['expense_linked'])))
    story.append(_summary_card(summary_items))
    story.append(Spacer(1, 0.5 * cm))

    data = [['Date', 'Contributeur', 'Montant', 'Notes']]
    for c in contributions:
        data.append([
            c.date_paid.strftime('%d/%m/%Y'),
            Paragraph(c.member.full_name, STYLE_CELL),
            _fmt_amount(c.amount),
            Paragraph(c.notes or '—', STYLE_CELL),
        ])
    data.append(['', Paragraph('TOTAL COLLECTÉ', STYLE_TOTAL_LABEL), _fmt_amount(total_collected), ''])

    table = Table(data, colWidths=[2.6 * cm, 5.4 * cm, 3.6 * cm, 6.4 * cm], repeatRows=1)
    style = _base_table_style(len(data))
    style.add('ALIGN', (0, 0), (0, -1), 'CENTER')
    style.add('ALIGN', (2, 0), (2, -1), 'RIGHT')
    table.setStyle(style)
    story.append(table)
    story.append(Spacer(1, 0.7 * cm))

    # --- Opérations rattachées à la cause ---
    if income_entries or expense_entries:
        story.append(_section_banner(
            "Opérations rattachées",
            f"{len(income_entries)} encaissement(s) — {len(expense_entries)} décaissement(s)",
            color=ORANGE
        ))
        story.append(Spacer(1, 0.15 * cm))

        linked_data = [['Date', 'Type', 'Libellé', 'Montant']]
        for e in income_entries:
            linked_data.append([
                e.date.strftime('%d/%m/%Y'),
                Paragraph('<font color="#16a34a"><b>Encaissement</b></font>', STYLE_CELL),
                Paragraph(e.label or '—', STYLE_CELL),
                _fmt_amount(e.amount),
            ])
        for e in expense_entries:
            linked_data.append([
                e.date.strftime('%d/%m/%Y'),
                Paragraph('<font color="#dc2626"><b>Décaissement</b></font>', STYLE_CELL),
                Paragraph(e.label or '—', STYLE_CELL),
                _fmt_amount(e.amount),
            ])
        linked_data.append(['', '', Paragraph('SOLDE (contrib. + encaiss. − décaiss.)', STYLE_TOTAL_LABEL),
                             _fmt_amount(balance['balance'] if balance else 0)])

        table2 = Table(linked_data, colWidths=[2.6 * cm, 3.6 * cm, 8.2 * cm, 3.6 * cm], repeatRows=1)
        style2 = _base_table_style(len(linked_data))
        style2.add('ALIGN', (0, 0), (0, -1), 'CENTER')
        style2.add('ALIGN', (3, 0), (3, -1), 'RIGHT')
        table2.setStyle(style2)
        story.append(table2)
        story.append(Spacer(1, 0.7 * cm))

    # --- Solde de la cause et solde général ---
    if balance is not None:
        block = [_solde_box("SOLDE DE LA CAUSE (contributions + encaissements − décaissements)", balance['balance'])]
        if balance['balance'] < 0:
            block.append(Spacer(1, 0.25 * cm))
            block.append(Paragraph(
                "⚠ Solde négatif : les décaissements rattachés à cette cause dépassent les sommes "
                "collectées pour elle. Le manque est financé par le solde général de la trésorerie.",
                STYLE_EMPTY
            ))
        story.append(KeepTogether(block))
        story.append(Spacer(1, 0.6 * cm))

    if overall_balance is not None:
        story.append(KeepTogether([_solde_box("SOLDE GÉNÉRAL DE LA TRÉSORERIE (à ce jour)", overall_balance)]))

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


# =====================================================================
# Bilan mensuel global (toutes les opérations de la plateforme)
# =====================================================================
def generate_monthly_bilan_pdf(month, year, income_entries, expense_entries, cotisations, contributions,
                                overall_balance=None):
    """Bilan complet d'un mois : encaissements, décaissements, cotisations et contributions."""
    buffer = io.BytesIO()
    month_name = MONTHS_FR.get(int(month), str(month))
    doc, on_page = _build_doc(buffer, f"Bilan Mensuel — {month_name} {year}")
    story = []

    total_income = sum(float(e.amount) for e in income_entries)
    total_expense = sum(float(e.amount) for e in expense_entries)
    total_cotisations = sum(float(c.amount_paid) for c in cotisations)
    total_contributions = sum(float(c.amount) for c in contributions)
    total_in = total_income + total_cotisations + total_contributions
    total_out = total_expense
    solde = total_in - total_out
    nb_ops = len(income_entries) + len(expense_entries) + len(cotisations) + len(contributions)

    # --- En-tête ---
    story.append(Paragraph(f"Bilan Mensuel Global — {month_name} {year}", STYLE_TITLE))
    story.append(Paragraph(
        "Récapitulatif complet de toutes les opérations de la plateforme : "
        "encaissements, décaissements, cotisations et contributions.",
        STYLE_SUBTITLE
    ))

    story.append(_summary_card([
        ("Total encaissements (trésorerie)", _fmt_amount(total_income)),
        ("Total décaissements (trésorerie)", _fmt_amount(total_expense)),
        ("Total cotisations encaissées", _fmt_amount(total_cotisations)),
        ("Total contributions aux causes", _fmt_amount(total_contributions)),
        ("Total général des entrées", _fmt_amount(total_in)),
        ("Nombre total d'opérations", str(nb_ops)),
    ]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(KeepTogether([_solde_box("SOLDE NET DU MOIS (Entrées − Sorties)", solde)]))
    story.append(Spacer(1, 0.9 * cm))

    # --- Section : Encaissements ---
    story.append(_section_banner(
        "1. Encaissements", f"Opérations de trésorerie de type entrée — {len(income_entries)} opération(s)",
        color=GREEN, icon='+'
    ))
    story.append(Spacer(1, 0.15 * cm))
    if income_entries:
        data = [['Date', 'Réf.', 'Libellé', 'Catégorie', 'Cause / Collecte', 'Montant']]
        for e in income_entries:
            data.append([
                e.date.strftime('%d/%m/%Y'),
                e.ref or '—',
                Paragraph(e.label or '—', STYLE_CELL),
                Paragraph(e.category.name if e.category else '—', STYLE_CELL),
                Paragraph(e.cause.name if e.cause else '—', STYLE_CELL),
                _fmt_amount(e.amount),
            ])
        data.append(['', '', '', '', Paragraph('TOTAL', STYLE_TOTAL_LABEL), _fmt_amount(total_income)])
        table = Table(data, colWidths=[2.1 * cm, 2.1 * cm, 4.6 * cm, 3 * cm, 3.2 * cm, 3 * cm], repeatRows=1)
        style = _base_table_style(len(data))
        style.add('BACKGROUND', (0, -1), (-1, -1), GREEN)
        style.add('ALIGN', (0, 0), (1, -1), 'CENTER')
        style.add('ALIGN', (5, 0), (5, -1), 'RIGHT')
        table.setStyle(style)
        story.append(table)
    else:
        story.append(_empty_state("Aucun encaissement enregistré pour cette période."))
    story.append(Spacer(1, 0.7 * cm))

    # --- Section : Décaissements ---
    story.append(_section_banner(
        "2. Décaissements", f"Opérations de trésorerie de type sortie — {len(expense_entries)} opération(s)",
        color=RED, icon='−'
    ))
    story.append(Spacer(1, 0.15 * cm))
    if expense_entries:
        data = [['Date', 'Réf.', 'Libellé', 'Catégorie', 'Cause / Collecte', 'Montant']]
        for e in expense_entries:
            data.append([
                e.date.strftime('%d/%m/%Y'),
                e.ref or '—',
                Paragraph(e.label or '—', STYLE_CELL),
                Paragraph(e.category.name if e.category else '—', STYLE_CELL),
                Paragraph(e.cause.name if e.cause else '—', STYLE_CELL),
                _fmt_amount(e.amount),
            ])
        data.append(['', '', '', '', Paragraph('TOTAL', STYLE_TOTAL_LABEL), _fmt_amount(total_expense)])
        table = Table(data, colWidths=[2.1 * cm, 2.1 * cm, 4.6 * cm, 3 * cm, 3.2 * cm, 3 * cm], repeatRows=1)
        style = _base_table_style(len(data))
        style.add('ALIGN', (0, 0), (1, -1), 'CENTER')
        style.add('ALIGN', (5, 0), (5, -1), 'RIGHT')
        table.setStyle(style)
        story.append(table)
    else:
        story.append(_empty_state("Aucun décaissement enregistré pour cette période."))
    story.append(Spacer(1, 0.7 * cm))

    # --- Section : Cotisations ---
    story.append(_section_banner(
        "3. Cotisations des adhérents", f"Versements de cotisations du mois — {len(cotisations)} versement(s)",
        color=ORANGE
    ))
    story.append(Spacer(1, 0.15 * cm))
    if cotisations:
        data = [['Adhérent', 'Attendu', 'Versé', 'Reliquat', 'Date']]
        for c in cotisations:
            balance = float(c.amount_expected) - float(c.amount_paid)
            data.append([
                Paragraph(c.member.full_name if c.member else '—', STYLE_CELL),
                _fmt_amount(c.amount_expected),
                _fmt_amount(c.amount_paid),
                _fmt_amount(balance) if balance > 0 else '—',
                c.date_paid.strftime('%d/%m/%Y'),
            ])
        data.append(['TOTAL', '', _fmt_amount(total_cotisations), '', ''])
        table = Table(data, colWidths=[5.6 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm], repeatRows=1)
        style = _base_table_style(len(data))
        style.add('ALIGN', (1, 0), (3, -1), 'RIGHT')
        style.add('ALIGN', (4, 0), (4, -1), 'CENTER')
        table.setStyle(style)
        story.append(table)
    else:
        story.append(_empty_state("Aucune cotisation enregistrée pour cette période."))
    story.append(Spacer(1, 0.7 * cm))

    # --- Section : Contributions aux causes ---
    story.append(_section_banner(
        "4. Contributions aux causes", f"Collectes pour les causes actives — {len(contributions)} contribution(s)",
        color=ORANGE
    ))
    story.append(Spacer(1, 0.15 * cm))
    if contributions:
        data = [['Date', 'Cause', 'Contributeur', 'Montant', 'Notes']]
        for c in contributions:
            data.append([
                c.date_paid.strftime('%d/%m/%Y'),
                Paragraph(c.cause.name if c.cause else '—', STYLE_CELL),
                Paragraph(c.member.full_name if c.member else '—', STYLE_CELL),
                _fmt_amount(c.amount),
                Paragraph(c.notes or '—', STYLE_CELL),
            ])
        data.append(['', '', 'TOTAL', _fmt_amount(total_contributions), ''])
        table = Table(data, colWidths=[2.4 * cm, 4 * cm, 4.6 * cm, 3 * cm, 4 * cm], repeatRows=1)
        style = _base_table_style(len(data))
        style.add('ALIGN', (0, 0), (0, -1), 'CENTER')
        style.add('ALIGN', (3, 0), (3, -1), 'RIGHT')
        table.setStyle(style)
        story.append(table)
    else:
        story.append(_empty_state("Aucune contribution enregistrée pour cette période."))
    story.append(Spacer(1, 0.7 * cm))

    # --- Section : Bilan par cause / collecte ---
    cause_stats = defaultdict(lambda: {'name': None, 'contrib': 0.0, 'income': 0.0, 'expense': 0.0})
    for c in contributions:
        if c.cause:
            s = cause_stats[c.cause.id]
            s['name'] = c.cause.name
            s['contrib'] += float(c.amount)
    for e in income_entries:
        if e.cause:
            s = cause_stats[e.cause.id]
            s['name'] = e.cause.name
            s['income'] += float(e.amount)
    for e in expense_entries:
        if e.cause:
            s = cause_stats[e.cause.id]
            s['name'] = e.cause.name
            s['expense'] += float(e.amount)

    story.append(_section_banner(
        "5. Bilan par cause / collecte",
        f"Surplus ou déficit du mois pour chaque cause ayant eu des mouvements — {len(cause_stats)} cause(s) concernée(s)",
        color=ORANGE
    ))
    story.append(Spacer(1, 0.15 * cm))
    if cause_stats:
        data = [['Cause / Collecte', 'Contributions', 'Encaiss. liés', 'Décaiss. liés', 'Solde du mois']]
        any_deficit = False
        total_contrib_all = total_income_all = total_expense_all = 0.0
        for s in sorted(cause_stats.values(), key=lambda x: x['name'] or ''):
            cause_solde = s['contrib'] + s['income'] - s['expense']
            total_contrib_all += s['contrib']
            total_income_all += s['income']
            total_expense_all += s['expense']
            if cause_solde < 0:
                any_deficit = True
            solde_style = STYLE_CELL_RIGHT if cause_solde >= 0 else ParagraphStyle(
                'CauseDeficit', parent=STYLE_CELL_RIGHT, textColor=RED_DARK, fontName='Helvetica-Bold'
            )
            data.append([
                Paragraph(s['name'] or '—', STYLE_CELL),
                _fmt_amount(s['contrib']),
                _fmt_amount(s['income']),
                _fmt_amount(s['expense']),
                Paragraph(('+' if cause_solde >= 0 else '') + _fmt_amount(cause_solde), solde_style),
            ])
        total_solde_all = total_contrib_all + total_income_all - total_expense_all
        data.append([
            'TOTAL',
            _fmt_amount(total_contrib_all),
            _fmt_amount(total_income_all),
            _fmt_amount(total_expense_all),
            ('+' if total_solde_all >= 0 else '') + _fmt_amount(total_solde_all),
        ])
        table = Table(data, colWidths=[5 * cm, 3.4 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm], repeatRows=1)
        style = _base_table_style(len(data))
        style.add('ALIGN', (1, 0), (4, -1), 'RIGHT')
        table.setStyle(style)
        story.append(table)
        if any_deficit:
            story.append(Spacer(1, 0.25 * cm))
            story.append(Paragraph(
                "⚠ Une cause en solde négatif a dépensé plus que ce qui lui a été collecté ce mois-ci "
                "(contributions + encaissements liés). Ce manque est financé par le solde général de la trésorerie.",
                STYLE_EMPTY
            ))
    else:
        story.append(_empty_state("Aucune cause / collecte n'a eu de mouvement ce mois-ci."))

    # --- Solde général de la trésorerie (à ce jour) ---
    if overall_balance is not None:
        story.append(KeepTogether([
            Spacer(1, 0.9 * cm),
            _solde_box("SOLDE GÉNÉRAL DE LA TRÉSORERIE (toutes opérations, à ce jour)", overall_balance),
        ]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer

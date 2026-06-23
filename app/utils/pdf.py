from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io

def generate_receipt_pdf(member_name, amount, date, reason):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(10.5*cm, 28*cm, "ASSOCIATION TRÉSORERIE")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(10.5*cm, 27.5*cm, "Reçu de versement officiel")
    
    p.line(2*cm, 27*cm, 19*cm, 27*cm)
    
    # Content
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, 25*cm, f"Date: {date}")
    p.drawString(2*cm, 24*cm, f"Bénéficiaire: {member_name}")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2*cm, 22*cm, f"Montant: {amount} €")
    
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, 21*cm, f"Motif: {reason}")
    
    # Signature placeholder
    p.rect(13*cm, 18*cm, 5*cm, 3*cm)
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(13.5*cm, 18.5*cm, "Signature Trésorier")
    
    p.setFont("Helvetica", 8)
    p.drawCentredString(10.5*cm, 2*cm, "Généré automatiquement par Association Trésorerie")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def generate_contributions_report_pdf(cause_name, contributions, total_collected):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(10.5*cm, 28*cm, f"Rapport des Contributions - {cause_name}")
    
    # Create table data
    data = [['Date', 'Contributeur', 'Montant', 'Notes']]
    for c in contributions:
        data.append([c.date_paid.strftime('%d/%m/%Y'), c.member.full_name, f"{float(c.amount):.2f} €", c.notes or ''])
    
    # Add Total row
    data.append(['', 'Total', f"{float(total_collected):.2f} €", ''])
    
    # Create table
    table = Table(data, colWidths=[2.5*cm, 5*cm, 3*cm, 6*cm])
    
    # Add style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    
    # Draw table
    table.wrapOn(p, 0, 0)
    table.drawOn(p, 2*cm, 20*cm)
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def generate_cotisations_report_pdf(month, year, cotisations, total_collected):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(10.5*cm, 28*cm, f"Rapport des Cotisations - {month}/{year}")
    
    # Create table data
    data = [['Adhérent', 'Attendu', 'Versé', 'Date']]
    for c in cotisations:
        data.append([c.member.full_name, f"{float(c.amount_expected):.2f} €", f"{float(c.amount_paid):.2f} €", c.date_paid.strftime('%d/%m/%Y')])
    
    # Add Total row
    data.append(['Total', '', f"{float(total_collected):.2f} €", ''])
    
    # Create table
    table = Table(data, colWidths=[6*cm, 3*cm, 3*cm, 4*cm])
    
    # Add style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    
    # Draw table
    table.wrapOn(p, 0, 0)
    table.drawOn(p, 2*cm, 20*cm)
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

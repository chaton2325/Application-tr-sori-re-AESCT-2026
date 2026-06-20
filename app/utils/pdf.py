from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
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

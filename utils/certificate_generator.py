from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

def generate_certificate_pdf(user, course, certificate):
    filename = f'certificate_{certificate.certificate_id}.pdf'
    filepath = os.path.join('static/certificates', filename)
    
    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.rect(0.5*inch, 0.5*inch, width-inch, height-inch, stroke=1, fill=0)
    
    c.setFillColor(colors.HexColor('#3498DB'))
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width/2, height-2*inch, "CERTIFICATE")
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height-2.7*inch, "OF COMPLETION")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-3.5*inch, "This is to certify that")
    
    c.setFillColor(colors.HexColor('#E74C3C'))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height-4.2*inch, user.full_name)
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-4.9*inch, "has successfully completed the course")
    
    c.setFillColor(colors.HexColor('#3498DB'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-5.6*inch, course.title)
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica", 14)
    date_str = certificate.issued_at.strftime("%B %d, %Y")
    c.drawCentredString(width/2, height-6.5*inch, f"Issued on: {date_str}")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-7*inch, f"Certificate ID: {certificate.certificate_id}")
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 0.8*inch, "This certificate verifies the successful completion of the course requirements")
    
    c.save()
    
    return filepath

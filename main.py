import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask import Flask, request, jsonify, send_file, render_template_string
import json

app = Flask(__name__)

class InvoiceGenerator:
    def __init__(self):
        self.invoice_counter = 312
        
    def number_to_words(self, num):
        """Convert number to words in Indian format"""
        if num == 0:
            return "Zero"
        
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_hundreds(n):
            result = ''
            if n >= 100:
                result += ones[n // 100] + ' Hundred '
                n %= 100
            if n >= 20:
                result += tens[n // 10] + ' '
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + ' '
                return result.strip()
            if n > 0:
                result += ones[n] + ' '
            return result.strip()
        
        if num < 1000:
            return convert_hundreds(num) + ' Rupees Only'
        elif num < 100000:
            thousands = num // 1000
            remainder = num % 1000
            result = convert_hundreds(thousands) + ' Thousand'
            if remainder > 0:
                result += ', ' + convert_hundreds(remainder)
            return result + ' Rupees Only'
        elif num < 10000000:
            lakhs = num // 100000
            remainder = num % 100000
            result = convert_hundreds(lakhs) + ' Lakh'
            if remainder >= 1000:
                thousands = remainder // 1000
                remainder = remainder % 1000
                result += ', ' + convert_hundreds(thousands) + ' Thousand'
            if remainder > 0:
                result += ', ' + convert_hundreds(remainder)
            return result + ' Rupees Only'
        else:
            crores = num // 10000000
            remainder = num % 10000000
            result = convert_hundreds(crores) + ' Crore'
            if remainder >= 100000:
                lakhs = remainder // 100000
                remainder = remainder % 100000
                result += ', ' + convert_hundreds(lakhs) + ' Lakh'
            if remainder >= 1000:
                thousands = remainder // 1000
                remainder = remainder % 1000
                result += ', ' + convert_hundreds(thousands) + ' Thousand'
            if remainder > 0:
                result += ', ' + convert_hundreds(remainder)
            return result + ' Rupees Only'
    
    def format_currency(self, amount):
        """Format amount as Pakistani Rupees"""
        return f"Rs{amount:,.2f}".replace(',', ',')
    
    def format_date(self, date_str):
        """Format date as DD-MM-YYYY"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except:
            return date_str
    
    def generate_pdf(self, invoice_data, filename=None):
        """Generate PDF invoice with 14 blank lines at the top"""
        if not filename:
            filename = f"Invoice_{self.invoice_counter}.pdf"
        
        # Calculate totals
        quantity = float(invoice_data['quantity'])
        unit_price = float(invoice_data['unit_price'])
        total_price = quantity * unit_price
        
        # Create PDF document with custom margins to accommodate top space
        doc = SimpleDocTemplate(
            filename, 
            pagesize=A4, 
            topMargin=0.5*inch,  # Reduced top margin since we're adding space manually
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Add 14 blank lines at the top (each line approximately 14 points)
        # 14 lines × 14 points = 196 points ≈ 2.72 inches
        story.append(Spacer(1, 14 * 14))
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=5
        )
        
        # Title
        story.append(Paragraph("Invoice", title_style))
        
        # Submission date
        submission_date = datetime.now().strftime('%d/%m/%Y')
        story.append(Paragraph(f"Submitted on: {submission_date}", header_style))
        story.append(Spacer(1, 20))
        
        # Invoice details section - create a table for better alignment
        invoice_details_data = [
            [
                Paragraph("<b>Invoice for</b><br/>Mr Adnan - A.L.U INTERNATIONAL", normal_style),
                Paragraph("<b>Payable to</b><br/>A.T COMMODITIES", normal_style),
                Paragraph(f"<b>Invoice #</b><br/>{self.invoice_counter}", normal_style)
            ]
        ]
        
        details_table = Table(invoice_details_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 25))
        
        # Main invoice table
        table_data = [
            ['Description', 'Delivery Date', 'Qty (M/TON)', 'Unit Price', 'Total Price'],
            [
                f"Coal ({invoice_data['vehicle_number']})",
                self.format_date(invoice_data['delivery_date']),
                f"{quantity:.3f}",
                self.format_currency(unit_price),
                self.format_currency(total_price)
            ]
        ]
        
        main_table = Table(table_data, colWidths=[2.2*inch, 1.3*inch, 1.1*inch, 1.2*inch, 1.2*inch])
        main_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            # Data row styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 30))
        
        # Total amount - right aligned
        total_table_data = [
            ['', self.format_currency(total_price)]
        ]
        
        total_table = Table(total_table_data, colWidths=[5.5*inch, 1.5*inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(total_table)
        story.append(Spacer(1, 15))
        
        # Amount in words - right aligned
        amount_words = self.number_to_words(int(total_price))
        words_table_data = [
            ['', amount_words]
        ]
        
        words_table = Table(words_table_data, colWidths=[4*inch, 3*inch])
        words_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(words_table)
        
        # Build PDF
        doc.build(story)
        
        # Increment invoice counter
        self.invoice_counter += 1
        
        return filename

# Initialize invoice generator
invoice_gen = InvoiceGenerator()

# HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Invoice Generator</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
            color: #555;
        }
        input, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            border-color: #4CAF50;
            outline: none;
        }
        button { 
            background-color: #4CAF50; 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
            width: 100%;
            margin-top: 20px;
        }
        button:hover { 
            background-color: #45a049; 
        }
        .form-row { 
            display: flex; 
            gap: 20px; 
        }
        .form-row .form-group { 
            flex: 1; 
        }
        .info-box {
            background-color: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .info-box h3 {
            margin-top: 0;
            color: #0066cc;
        }
        @media (max-width: 600px) {
            .form-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Invoice Generator</h1>
        
        <div class="info-box">
            <h3>📄 PDF Features</h3>
            <ul>
                <li>✅ 14 blank lines reserved at top of PDF</li>
                <li>✅ A4 paper size format</li>
                <li>✅ Professional invoice layout</li>
                <li>✅ Auto-incrementing invoice numbers</li>
            </ul>
        </div>
        
        <form method="POST" action="/generate_invoice">
            <div class="form-row">
                <div class="form-group">
                    <label for="delivery_date">📅 Delivery Date:</label>
                    <input type="date" id="delivery_date" name="delivery_date" required>
                </div>
                <div class="form-group">
                    <label for="vehicle_number">🚛 Vehicle Number:</label>
                    <input type="text" id="vehicle_number" name="vehicle_number" placeholder="e.g., JW-1237" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="quantity">⚖️ Quantity (M/TON):</label>
                    <input type="number" id="quantity" name="quantity" step="0.001" placeholder="e.g., 40.330" required>
                </div>
                <div class="form-group">
                    <label for="unit_price">💰 Unit Price (Rs):</label>
                    <input type="number" id="unit_price" name="unit_price" step="0.01" placeholder="e.g., 39500" required>
                </div>
            </div>
            
            <button type="submit">🎯 Generate Invoice PDF</button>
        </form>
    </div>

    <script>
        // Set today's date as default
        document.getElementById('delivery_date').valueAsDate = new Date();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the HTML form"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    """Generate and return PDF invoice"""
    try:
        # Get form data
        invoice_data = {
            'delivery_date': request.form.get('delivery_date'),
            'vehicle_number': request.form.get('vehicle_number'),
            'quantity': request.form.get('quantity'),
            'unit_price': request.form.get('unit_price')
        }
        
        # Validate required fields
        if not all(invoice_data.values()):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Generate PDF
        filename = f"Invoice_{invoice_gen.invoice_counter}.pdf"
        pdf_path = invoice_gen.generate_pdf(invoice_data, filename)
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate_invoice():
    """API endpoint for generating invoice"""
    try:
        # Get JSON data
        invoice_data = request.get_json()
        
        # Validate required fields
        required_fields = ['delivery_date', 'vehicle_number', 'quantity', 'unit_price']
        if not all(field in invoice_data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate PDF
        filename = f"Invoice_{invoice_gen.invoice_counter}.pdf"
        pdf_path = invoice_gen.generate_pdf(invoice_data, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}',
            'invoice_number': invoice_gen.invoice_counter - 1
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF file"""
    try:
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# CLI function for standalone usage
def generate_invoice_cli():
    """Command line interface for invoice generation"""
    print("=== Invoice Generator ===")
    print("📄 Note: PDF will have 14 blank lines at the top")
    print("\nEnter invoice details:")
    
    delivery_date = input("📅 Delivery Date (YYYY-MM-DD): ")
    vehicle_number = input("🚛 Vehicle Number: ")
    quantity = float(input("⚖️ Quantity (M/TON): "))
    unit_price = float(input("💰 Unit Price (Rs): "))
    
    invoice_data = {
        'delivery_date': delivery_date,
        'vehicle_number': vehicle_number,
        'quantity': quantity,
        'unit_price': unit_price
    }
    
    filename = invoice_gen.generate_pdf(invoice_data)
    print(f"\n✅ Invoice generated successfully: {filename}")
    print(f"📋 Invoice Number: {invoice_gen.invoice_counter - 1}")
    print(f"💰 Total Amount: Rs{quantity * unit_price:,.2f}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        # Run CLI version
        generate_invoice_cli()
    else:
        # Run Flask web server
        print("🚀 Starting Invoice Generator Web Server...")
        print("📄 Features: 14 blank lines at top + A4 format")
        print("🌐 Visit http://localhost:5000 to access the form")
        print("📡 API endpoint: http://localhost:5000/api/generate")
        app.run(debug=True, host='0.0.0.0', port=5000)

Here's a comprehensive README for your Invoice Generator repository:

```markdown
# Invoice Generator for A.L.U International

A Flask-based web application for generating professional invoices with automatic numbering and PDF export features.

## Key Features
- ✅ **Automated PDF Generation**: Creates ready-to-print invoices in A4 format
- 📄 **Pre-formatted Top Space**: Reserves 14 blank lines at the top of each invoice
- 🔢 **Auto-incrementing Invoice Numbers**: Starts from #312 and increments automatically
- 💰 **Currency Conversion**: Converts amounts to words in Indian numbering format
- 🌐 **Multiple Interfaces**: 
  - Web form with responsive design
  - REST API endpoint
  - Command-line interface (CLI)
- 📦 **Self-contained**: Single-file implementation with minimal dependencies

## Technical Specifications
- **Paper Format**: A4 (210 × 297 mm)
- **Top Margin**: 14 blank lines reserved for manual stamping/processing
- **Invoice Elements**:
  - Company details (A.L.U INTERNATIONAL and A.T COMMODITIES)
  - Vehicle number integration
  - Delivery date formatting (DD-MM-YYYY)
  - Quantity and unit price calculations
  - Total amount in figures and words
  - Automatic submission date

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/inamansari-92/Invoice-gen-A.L.U.git
   cd Invoice-gen-A.L.U
   ```

2. Install dependencies:
   ```bash
   pip install flask reportlab
   ```

## Usage
### Web Interface (Recommended)
```bash
python main.py
```
Access the form at: http://localhost:5000

![Form Screenshot](https://via.placeholder.com/800x600?text=Invoice+Generator+Form)

### Command Line Interface (CLI)
```bash
python main.py cli
```
Follow the prompts to enter invoice details.

### API Endpoint
POST to `/api/generate` with JSON payload:
```json
{
  "delivery_date": "2023-12-31",
  "vehicle_number": "JW-1234",
  "quantity": 42.5,
  "unit_price": 39500
}
```
Response includes download URL:
```json
{
  "success": true,
  "filename": "Invoice_312.pdf",
  "download_url": "/download/Invoice_312.pdf",
  "invoice_number": 312
}
```

## Code Structure
`main.py` contains:
1. **Flask Application** (Web server)
2. **InvoiceGenerator Class** with:
   - PDF generation using ReportLab
   - Currency-to-words conversion
   - Date formatting utilities
3. **Three Access Methods**:
   - Web form (`/`)
   - Form submission handler (`/generate_invoice`)
   - API endpoint (`/api/generate`)
4. **CLI Interface** for terminal usage

## Special Feature: Top Margin
The generator reserves **14 blank lines** at the top of each PDF to accommodate:
- Company letterhead
- Stamps
- Manual processing marks
- Additional annotations

## Sample Invoice Output
![Invoice Sample](https://via.placeholder.com/600x800?text=Invoice+with+14+blank+lines+at+top)

## Customization
To modify the template:
1. Update the `HTML_TEMPLATE` variable for form changes
2. Adjust styles in `generate_pdf()` method:
   - `title_style`
   - `header_style`
   - Table dimensions and colors
3. Modify static text (company names) in the `generate_pdf` method

## Requirements
- Python 3.7+
- Packages: `Flask`, `ReportLab`

## License
MIT License - Free for commercial and personal use
```

This README includes:

1. Clear project description and key features
2. Technical specifications of the invoice format
3. Installation and setup instructions
4. Multiple usage methods (web, CLI, API)
5. Code structure overview
6. Explanation of the 14-line top margin feature
7. Customization guidance
8. Requirements and license information

The placeholder images can be replaced with actual screenshots once you add them to your repository. Consider adding:
1. `screenshot-form.png` - Web form interface
2. `screenshot-invoice.png` - Generated PDF sample

"""PDF export service for financial summaries."""

from datetime import datetime
from io import BytesIO
from typing import Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from src.models.financial import FinancialSummary
from src.storage.s3_service import s3_service


class PDFExportService:
    """Service for generating PDF documents from financial summaries."""
    
    def __init__(self):
        """Initialize PDF export service."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            )
    
    def generate_financial_summary_pdf(
        self,
        summary: FinancialSummary
    ) -> bytes:
        """
        Generate PDF document from financial summary.
        
        Args:
            summary: FinancialSummary object
            
        Returns:
            PDF content as bytes
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12
        )
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("Financial Summary Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Enterprise information
        enterprise_info = [
            ["Enterprise Name:", summary.enterprise_name],
            ["Enterprise ID:", summary.enterprise_id],
            ["Report Date:", summary.summary_date.strftime("%B %d, %Y")],
            ["Period Covered:", summary.period_covered]
        ]
        
        info_table = Table(enterprise_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Financial Overview
        elements.append(Paragraph("Financial Overview", heading_style))
        
        financial_data = [
            ["Metric", "Amount (₹)", ""],
            ["Total Revenue", f"{summary.total_revenue:,.2f}", ""],
            ["Total Expenses", f"{summary.total_expenses:,.2f}", ""],
            ["Net Profit", f"{summary.net_profit:,.2f}", 
             "Profit" if summary.net_profit >= 0 else "Loss"],
            ["Profit Margin", f"{summary.profit_margin:.2f}%", ""]
        ]
        
        financial_table = Table(financial_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(financial_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Cash Flow Status
        elements.append(Paragraph("Cash Flow Status", heading_style))
        
        cash_flow_data = [
            ["Current Cash Balance", f"₹{summary.current_cash_balance:,.2f}"]
        ]
        
        # Add cash flow projection if available
        if summary.cash_flow_projection:
            projection = summary.cash_flow_projection
            if projection.get("has_shortfall"):
                cash_flow_data.append([
                    "Cash Flow Alert",
                    f"Shortfall projected in month {projection.get('shortfall_month', 'N/A')}"
                ])
            else:
                cash_flow_data.append([
                    "Cash Flow Projection",
                    f"Healthy for next {projection.get('months', 3)} months"
                ])
        
        cash_table = Table(cash_flow_data, colWidths=[2.5 * inch, 3.5 * inch])
        cash_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(cash_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Creditworthiness Assessment
        elements.append(Paragraph("Creditworthiness Assessment", heading_style))
        
        cw = summary.creditworthiness
        creditworthiness_data = [
            ["Overall Score", f"{cw.score:.1f}/100"],
            ["Debt-to-Income Ratio", f"{cw.indicators.debt_to_income_ratio:.2f}%"],
            ["Revenue Stability", f"{cw.indicators.revenue_stability_score:.2f}/1.0"],
            ["Cash Flow Health", cw.indicators.cash_flow_health],
            ["Assessment", cw.indicators.overall_assessment]
        ]
        
        cw_table = Table(creditworthiness_data, colWidths=[2.5 * inch, 3.5 * inch])
        cw_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(cw_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        if cw.recommendations:
            elements.append(Paragraph("Recommendations", heading_style))
            for i, rec in enumerate(cw.recommendations, 1):
                rec_text = Paragraph(f"{i}. {rec}", normal_style)
                elements.append(rec_text)
                elements.append(Spacer(1, 0.1 * inch))
        
        # Simple Language Explanations
        if summary.explanations:
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("Understanding Your Metrics", heading_style))
            
            for metric, explanation in summary.explanations.items():
                metric_para = Paragraph(f"<b>{metric}:</b> {explanation}", normal_style)
                elements.append(metric_para)
                elements.append(Spacer(1, 0.1 * inch))
        
        # Footer
        elements.append(Spacer(1, 0.3 * inch))
        footer_text = (
            "<i>This financial summary is generated by GramSaarthi AI for informational purposes. "
            "Please consult with financial advisors for detailed analysis.</i>"
        )
        footer = Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def export_and_upload(
        self,
        summary: FinancialSummary,
        date: Optional[datetime] = None
    ) -> str:
        """
        Generate PDF and upload to S3.
        
        Args:
            summary: FinancialSummary object
            date: Optional date for the summary (defaults to current date)
            
        Returns:
            S3 presigned URL for the PDF
        """
        # Generate PDF
        pdf_bytes = self.generate_financial_summary_pdf(summary)
        
        # Upload to S3
        s3_key = s3_service.upload_financial_summary(
            enterprise_id=summary.enterprise_id,
            pdf_data=pdf_bytes,
            date=date
        )
        
        # Generate presigned URL (valid for 24 hours)
        url = s3_service.get_financial_summary_url(
            enterprise_id=summary.enterprise_id,
            date=date,
            expiration=86400
        )
        
        return url


# Global service instance
pdf_export_service = PDFExportService() if REPORTLAB_AVAILABLE else None

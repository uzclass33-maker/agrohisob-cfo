"""
AgroHisob CFO - Professional PDF Report Generator
Generates high-grade, print-ready, A4 multi-page Bank Dossier PDF documents using ReportLab.
Includes custom running headers/footers, dynamic page numbering, financial tables, and complete Uzbek Latin text.
"""

from io import BytesIO
import os
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.reporting.report_schemas import CreditDossierData


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page count and professional headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Skip headers on cover page
        if self._pageNumber > 1:
            # Header
            self.drawString(
                36, 
                800, 
                "AgroHisob CFO — Agrobiznes Moliyaviy Tahlili va Kreditga Tayyorgarlik Dosyesi"
            )
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, 792, 559, 792)

            # Footer
            self.line(36, 45, 559, 45)
            self.drawString(
                36, 
                32, 
                "Maxfiy axborot — Faqat vakolatli kredit anderraytingi va moliyaviy tahlil uchun"
            )
            page_text = f"Sahifa {self._pageNumber} / {page_count}"
            self.drawRightString(559, 32, page_text)
        
        self.restoreState()


class PDFReportGenerator:
    """Enterprise-grade PDF Dossier generator for AgroHisob CFO."""

    @classmethod
    def generate_dossier_pdf(cls, dossier: CreditDossierData, output_path: str = None) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=45,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()
        
        # Color Palette
        PRIMARY_NAVY = colors.HexColor("#0f172a")
        EMERALD_ACCENT = colors.HexColor("#059669")
        TEXT_MUTED = colors.HexColor("#475569")
        BORDER_GRAY = colors.HexColor("#cbd5e1")
        BG_LIGHT = colors.HexColor("#f8fafc")

        # Custom Typography Styles
        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=PRIMARY_NAVY,
            alignment=TA_LEFT
        )
        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=TEXT_MUTED,
            alignment=TA_LEFT
        )
        h1_style = ParagraphStyle(
            'SectionH1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=PRIMARY_NAVY,
            spaceAfter=6,
            keepWithNext=True
        )
        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=EMERALD_ACCENT,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        )
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1e293b")
        )
        body_bold = ParagraphStyle(
            'BodyBoldCustom',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        body_right = ParagraphStyle(
            'BodyRightCustom',
            parent=body_style,
            alignment=TA_RIGHT
        )
        disclaimer_style = ParagraphStyle(
            'DisclaimerCustom',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b")
        )

        elements: List[Any] = []

        # =========================================================================
        # SECTION 1: COVER PAGE
        # =========================================================================
        elements.append(Spacer(1, 25))
        # Top Badge
        badge_data = [[
            Paragraph("<font color='#059669'><b>AGROHISOB CFO</b></font> | Agrobiznes Moliyaviy Tahlil Platformasi", body_style)
        ]]
        t_badge = Table(badge_data, colWidths=[523])
        t_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#a7f3d0")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_badge)
        elements.append(Spacer(1, 40))

        elements.append(Paragraph("AGROBIZNES MOLIYAVIY TAHLILI VA KREDITGA TAYYORGARLIK DOSYESI", title_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Tijorat banklari va moliya institutlari kredit anderraytingiga taqdim etish uchun mustaqil moliyaviy hisobot va 12 oylik kassa prognozi.",
            subtitle_style
        ))
        elements.append(Spacer(1, 30))

        # Organization Card on Cover
        prof = dossier.credit_profile
        cover_meta = [
            [Paragraph("<b>Arizachi Korxona:</b>", body_style), Paragraph(dossier.organization_name, body_bold)],
            [Paragraph("<b>Tashkiliy-huquqiy shakli:</b>", body_style), Paragraph(prof.organization_type, body_style)],
            [Paragraph("<b>Faoliyat hududi:</b>", body_style), Paragraph(f"{prof.region}, {prof.district}", body_style)],
            [Paragraph("<b>STIR (INN):</b>", body_style), Paragraph(prof.inn or "Mavjud emas", body_style)],
            [Paragraph("<b>Ekin maydoni / Faoliyat:</b>", body_style), Paragraph(f"{prof.land_hectares} gektar | {prof.business_activity}", body_style)],
            [Paragraph("<b>So'ralayotgan kredit:</b>", body_style), Paragraph(f"<b>{prof.requested_loan_amount_uzs:,.2f} UZS</b> ({prof.proposed_term_months} oy, {prof.proposed_annual_interest_rate_pct}% stavka)", body_style)],
            [Paragraph("<b>Dosye ID / Generatsiya:</b>", body_style), Paragraph(f"{dossier.dossier_id} | {dossier.generation_timestamp}", body_style)],
            [Paragraph("<b>Ma'lumotlar manbasi:</b>", body_style), Paragraph(dossier.data_sources_and_assumptions.get("data_source_mode", "STANDART"), body_style)],
        ]
        t_meta = Table(cover_meta, colWidths=[160, 363])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 40))

        # Readiness Banner on Cover
        ra = dossier.readiness_assessment
        readiness_color = colors.HexColor("#059669") if ra.readiness_score >= 70 else colors.HexColor("#d97706")
        readiness_box = [
            [
                Paragraph(f"<b>Kreditga Tayyorgarlik Bahosi: {ra.readiness_score}/100</b>", ParagraphStyle('B1', parent=body_bold, textColor=readiness_color, fontSize=11)),
                Paragraph(f"<b>Holat:</b> {ra.status_label_uz}", ParagraphStyle('B2', parent=body_style, textColor=PRIMARY_NAVY))
            ]
        ]
        t_readiness = Table(readiness_box, colWidths=[240, 283])
        t_readiness.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 1, readiness_color),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_readiness)
        elements.append(Spacer(1, 50))

        elements.append(Paragraph(
            "<b>Maxfiylik eslatmasi:</b> Ushbu dosye maxfiy tijorat ma'lumotlarini o'z ichiga oladi va faqat kredit arizasini ko'rib chiquvchi vakolatli shaxslarga mo'ljallangan.",
            disclaimer_style
        ))
        elements.append(PageBreak())

        # =========================================================================
        # SECTION 2: EXECUTIVE SUMMARY & READINESS SCORECARD
        # =========================================================================
        elements.append(Paragraph("1. Ijroiya Xulosa va Tayyorgarlik Reytingi", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        hist = dossier.historical_summary
        fc = dossier.forecast_summary
        db = dossier.debt_dscr_summary

        kpi_table_data = [
            [
                Paragraph("<b>Ko'rsatkich</b>", body_bold),
                Paragraph("<b>Tarixiy Davr (12 oy)</b>", body_bold),
                Paragraph("<b>Prognoz Davri (12 oy)</b>", body_bold),
                Paragraph("<b>Izoh / Baho</b>", body_bold)
            ],
            [
                Paragraph("Yalpi Pul Tushumlari", body_style),
                Paragraph(f"{hist['total_inflows']:,.0f} UZS", body_right),
                Paragraph(f"{fc['total_annual_inflows']:,.0f} UZS", body_right),
                Paragraph("Mavsumiy daromad tushumi", body_style)
            ],
            [
                Paragraph("Jami Pul Chiqimlari", body_style),
                Paragraph(f"{hist['total_outflows']:,.0f} UZS", body_right),
                Paragraph(f"{fc['total_annual_outflows']:,.0f} UZS", body_right),
                Paragraph("Opex va qarz xizmati", body_style)
            ],
            [
                Paragraph("Sof Kassa Oqimi (Net)", body_style),
                Paragraph(f"<b>{hist['net_cash_flow']:,.0f} UZS</b>", body_right),
                Paragraph(f"<b>{fc['net_annual_cash_flow']:,.0f} UZS</b>", body_right),
                Paragraph("Yillik sof likvidlik o'sishi", body_style)
            ],
            [
                Paragraph("Yakuniy Kassa Qoldig'i", body_style),
                Paragraph(f"{hist['final_closing_balance']:,.0f} UZS", body_right),
                Paragraph(f"{fc['final_closing_balance']:,.0f} UZS", body_right),
                Paragraph("Davr oxiridagi likvidlik", body_style)
            ],
            [
                Paragraph("DSCR Qoplash Koeffitsienti", body_style),
                Paragraph("—", body_right),
                Paragraph(f"<b>{db['combined_dscr'] or db['standalone_dscr'] or 0:.2f}x</b>", body_right),
                Paragraph("Yangi kredit hisobga olinganda", body_style)
            ],
            [
                Paragraph("Kassa Uzilishi Oylari", body_style),
                Paragraph("0 oy", body_right),
                Paragraph(f"{fc['months_in_deficit']} oy ({fc['lowest_cash_month']})", body_right),
                Paragraph("Bahorgi ekin ekish davri", body_style)
            ],
        ]
        t_kpi = Table(kpi_table_data, colWidths=[150, 120, 120, 133])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 10))

        # Strengths & Risks side-by-side
        elements.append(Paragraph("Moliyaviy Imkoniyatlar va Asosiy Xatarlar", h2_style))
        str_bullets = "<br/>".join([f"• {s}" for s in ra.key_strengths_uz])
        rsk_bullets = "<br/>".join([f"• {r}" for r in ra.identified_risks_uz])
        
        swot_data = [
            [Paragraph("<b>Asosiy Ustunliklar:</b>", body_bold), Paragraph("<b>E'tibor Talab Qiluvchi Xatarlar:</b>", body_bold)],
            [Paragraph(str_bullets, body_style), Paragraph(rsk_bullets, body_style)]
        ]
        t_swot = Table(swot_data, colWidths=[260, 263])
        t_swot.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#ecfdf5")),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#fff1f2")),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#f0fdf4")),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor("#fff5f5")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(t_swot)
        elements.append(Spacer(1, 15))

        # =========================================================================
        # SECTION 3: ORGANIZATION PROFILE & FINANCING REQUEST
        # =========================================================================
        elements.append(Paragraph("2. Korxona Profili va Moliyalashtirish So'rovi", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        req_data = [
            [Paragraph("<b>So'ralayotgan Summa:</b>", body_style), Paragraph(f"<b>{prof.requested_loan_amount_uzs:,.2f} UZS</b>", body_bold),
             Paragraph("<b>Kredit Maqsadi:</b>", body_style), Paragraph(prof.loan_purpose.value, body_style)],
            [Paragraph("<b>Taklif etilayotgan Muddat:</b>", body_style), Paragraph(f"{prof.proposed_term_months} oy", body_style),
             Paragraph("<b>Imtiyozli Davr:</b>", body_style), Paragraph(f"{prof.grace_period_months} oy", body_style)],
            [Paragraph("<b>Mo'ljallangan Foiz Stavkasi:</b>", body_style), Paragraph(f"{prof.proposed_annual_interest_rate_pct}% yillik", body_style),
             Paragraph("<b>Qaytarish Tuzilmasi:</b>", body_style), Paragraph(prof.repayment_structure, body_style)],
            [Paragraph("<b>Kutilayotgan Ajratish Sanasi:</b>", body_style), Paragraph(prof.expected_disbursement_date, body_style),
             Paragraph("<b>Mijozlar Segmenti:</b>", body_style), Paragraph(prof.customer_segments, body_style)],
        ]
        t_req = Table(req_data, colWidths=[120, 140, 120, 143])
        t_req.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_req)
        elements.append(Spacer(1, 15))

        # =========================================================================
        # SECTION 4: HISTORICAL CASH-FLOW PERFORMANCE
        # =========================================================================
        elements.append(Paragraph("3. Tarixiy Kassa Oqimlari Tahlili (So'nggi 12 oy)", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        hist_table = [
            [
                Paragraph("<b>Oy</b>", body_bold),
                Paragraph("<b>Boshlang'ich</b>", body_bold),
                Paragraph("<b>Tushumlar</b>", body_bold),
                Paragraph("<b>Chiqimlar</b>", body_bold),
                Paragraph("<b>Sof Oqim</b>", body_bold),
                Paragraph("<b>Yakuniy Balans</b>", body_bold)
            ]
        ]
        for m in hist["monthly_data"]:
            hist_table.append([
                Paragraph(m["month_name"], body_style),
                Paragraph(f"{m['opening_balance']:,.0f}", body_right),
                Paragraph(f"{m['inflows']:,.0f}", body_right),
                Paragraph(f"{m['outflows']:,.0f}", body_right),
                Paragraph(f"{m['net_cash_flow']:,.0f}", body_right),
                Paragraph(f"<b>{m['closing_balance']:,.0f}</b>", body_right),
            ])
        t_hist = Table(hist_table, colWidths=[80, 88, 88, 88, 88, 91])
        t_hist.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_hist)
        elements.append(PageBreak())

        # =========================================================================
        # SECTION 5: TWELVE-MONTH SEASONAL FORECAST
        # =========================================================================
        elements.append(Paragraph("4. 12 Oylik Mavsumiy Kassa Prognozi (2026)", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        elements.append(Paragraph(
            "Deterministik agrar tsikl: Bahorgi ekishda xarajatlar tushumlardan ustun bo'lib, hosil terimi oylarida (Iyun-Noyabr) asosiy likvidlik shakllanadi.",
            subtitle_style
        ))
        elements.append(Spacer(1, 6))

        fc_table = [
            [
                Paragraph("<b>Oy</b>", body_bold),
                Paragraph("<b>Boshlang'ich</b>", body_bold),
                Paragraph("<b>Tushum</b>", body_bold),
                Paragraph("<b>Opex</b>", body_bold),
                Paragraph("<b>Qarz Xizmati</b>", body_bold),
                Paragraph("<b>CFADS</b>", body_bold),
                Paragraph("<b>Yakuniy Balans</b>", body_bold)
            ]
        ]
        for m in fc["monthly_forecast"]:
            fc_table.append([
                Paragraph(m["month_name"], body_style),
                Paragraph(f"{m['opening_balance']:,.0f}", body_right),
                Paragraph(f"{m['inflows']:,.0f}", body_right),
                Paragraph(f"{m['operating_outflows']:,.0f}", body_right),
                Paragraph(f"{m['debt_service']:,.0f}", body_right),
                Paragraph(f"{m['cfads']:,.0f}", body_right),
                Paragraph(f"<b>{m['closing_balance']:,.0f}</b>", body_right),
            ])
        t_fc = Table(fc_table, colWidths=[75, 74, 74, 74, 74, 74, 78])
        t_fc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_fc)
        elements.append(Spacer(1, 15))

        # =========================================================================
        # SECTION 6: DEBT & DSCR REPAYMENT ANALYSIS
        # =========================================================================
        elements.append(Paragraph("5. Qarzga Xizmat Ko'rsatish va DSCR Tahlili", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        dscr_summary_text = (
            f"<b>DSCR Hisoblash Formulasi:</b> DSCR = CFADS / Jami Qarz Xizmati<br/>"
            f"Yillik CFADS (Operatsion oqim): <b>{fc['total_annual_inflows'] - (fc['total_annual_outflows'] - db['existing_annual_debt_service']):,.2f} UZS</b><br/>"
            f"Mavjud yillik kredit xizmati: <b>{db['existing_annual_debt_service']:,.2f} UZS</b> | Yangi kredit 1-yil xizmati: <b>{db['first_year_new_loan_service']:,.2f} UZS</b><br/>"
            f"Birlashtirilgan yillik DSCR: <b>{db['combined_dscr'] or 'Qarzsiz'}x</b> (Standart me'yor: &ge; 1.25x)"
        )
        elements.append(Paragraph(dscr_summary_text, body_style))
        elements.append(Spacer(1, 8))

        # Amortization Table Preview (First 6 months)
        elements.append(Paragraph("So'ralayotgan Kredit Amortizatsiyasi Dastlabki 6 Oyi:", h2_style))
        amort_table = [
            [
                Paragraph("<b>Davr</b>", body_bold),
                Paragraph("<b>Sana</b>", body_bold),
                Paragraph("<b>Boshlang'ich Qarz</b>", body_bold),
                Paragraph("<b>Asosiy Qarz</b>", body_bold),
                Paragraph("<b>Foiz</b>", body_bold),
                Paragraph("<b>Jami To'lov</b>", body_bold),
                Paragraph("<b>Qoldiq Qarz</b>", body_bold)
            ]
        ]
        for row in db["amortization_schedule"][:6]:
            amort_table.append([
                Paragraph(str(row["period"]), body_style),
                Paragraph(row["date"], body_style),
                Paragraph(f"{row['opening_principal']:,.0f}", body_right),
                Paragraph(f"{row['principal_paid']:,.0f}", body_right),
                Paragraph(f"{row['interest_paid']:,.0f}", body_right),
                Paragraph(f"{row['total_payment']:,.0f}", body_right),
                Paragraph(f"<b>{row['remaining_principal']:,.0f}</b>", body_right),
            ])
        t_amort = Table(amort_table, colWidths=[40, 75, 80, 80, 75, 85, 88])
        t_amort.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_amort)
        elements.append(PageBreak())

        # =========================================================================
        # SECTION 7: STRESS-TEST & SCENARIO ANALYSIS
        # =========================================================================
        elements.append(Paragraph("6. Xatarlar va Ssenariylar Simulyatsiyasi", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        sc_data = dossier.risks_scenarios_summary
        sc_table = [
            [
                Paragraph("<b>Ssenariy</b>", body_bold),
                Paragraph("<b>Tushumlar O'zgarishi</b>", body_bold),
                Paragraph("<b>Xarajatlar O'zgarishi</b>", body_bold),
                Paragraph("<b>Yakuniy Kassa</b>", body_bold),
                Paragraph("<b>DSCR</b>", body_bold),
                Paragraph("<b>Taqchillik Oylari</b>", body_bold)
            ],
            [
                Paragraph("<b>Baza Ssenariysi</b>", body_style),
                Paragraph("0%", body_style),
                Paragraph("0%", body_style),
                Paragraph(f"{sc_data['base']['closing_balance']:,.0f} UZS", body_right),
                Paragraph(f"{sc_data['base']['dscr'] or 0:.2f}x", body_style),
                Paragraph(f"{sc_data['base']['deficits']} oy", body_style)
            ],
            [
                Paragraph("<b>Optimistik Ssenariy</b>", body_style),
                Paragraph("+20% (hosil ko'p)", body_style),
                Paragraph("-10% (resurs tejam)", body_style),
                Paragraph(f"{sc_data['optimistic']['closing_balance']:,.0f} UZS", body_right),
                Paragraph(f"{sc_data['optimistic']['dscr'] or 0:.2f}x", body_style),
                Paragraph(f"{sc_data['optimistic']['deficits']} oy", body_style)
            ],
            [
                Paragraph("<b>Pessimistik Ssenariy</b>", body_style),
                Paragraph("-20% (narx tushishi)", body_style),
                Paragraph("+15% (yoqilg'i oshishi)", body_style),
                Paragraph(f"{sc_data['pessimistic']['closing_balance']:,.0f} UZS", body_right),
                Paragraph(f"{sc_data['pessimistic']['dscr'] or 0:.2f}x", body_style),
                Paragraph(f"{sc_data['pessimistic']['deficits']} oy", body_style)
            ],
        ]
        t_sc = Table(sc_table, colWidths=[100, 95, 95, 95, 68, 70])
        t_sc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_sc)
        elements.append(Spacer(1, 15))

        # =========================================================================
        # SECTION 8: DOCUMENT CHECKLIST & LEGAL DISCLAIMER
        # =========================================================================
        elements.append(Paragraph("7. Hujjatlar Nazorat Ro'yxati va Metodologiya", h1_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=EMERALD_ACCENT, spaceAfter=8))
        
        chk_table = [
            [
                Paragraph("<b>Hujjat / Ma'lumot Nomi</b>", body_bold),
                Paragraph("<b>Kategoriya</b>", body_bold),
                Paragraph("<b>Holat</b>", body_bold),
                Paragraph("<b>Ahamiyati</b>", body_bold)
            ]
        ]
        for item in dossier.checklist.items:
            status_color = "#059669" if item.status.value == "AVAILABLE" else "#d97706"
            chk_table.append([
                Paragraph(item.title_uz, body_style),
                Paragraph(item.category_title_uz, body_style),
                Paragraph(f"<font color='{status_color}'><b>{item.status.value}</b></font>", body_style),
                Paragraph("Majburiy" if item.is_critical else "Ixtiyoriy", body_style)
            ])
        t_chk = Table(chk_table, colWidths=[180, 150, 110, 83])
        t_chk.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_chk)
        elements.append(Spacer(1, 15))

        # Regulatory Disclaimer Box
        disc_box = [[Paragraph(f"<b>HUQUQIY CHEKLOV VA DIQQAT:</b><br/>{dossier.regulatory_disclaimer_uz}", disclaimer_style)]]
        t_disc = Table(disc_box, colWidths=[523])
        t_disc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fecaca")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t_disc)

        # Build PDF with two-pass canvas
        doc.build(elements, canvasmaker=NumberedCanvas)
        
        pdf_bytes = buffer.getvalue()
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        return pdf_bytes

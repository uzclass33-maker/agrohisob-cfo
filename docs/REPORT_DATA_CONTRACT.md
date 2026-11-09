# AGROHISOB CFO — KREDIT DOSYESI MA'LUMOTLAR SHARTNOMASI (REPORT DATA CONTRACT)

## 1. Kirish
Mazkur hujjat `CreditDossierData` kanonik shartnomasining JSON spetsifikatsiyasi va uning frontend UI, PDF hamda Excel generatorlari o'rtasidagi to'liq muvofiqligini belgilaydi.

---

## 2. Pydantic Kanonik Strukturasi

```json
{
  "dossier_id": "dos-181e9f9f1c",
  "organization_id": "scenario-small-farmer",
  "organization_name": "Andijon Baraka Fermer Xo'jaligi",
  "generation_timestamp": "2026-11-09 05:06:38 UTC",
  "calculation_version": "5.0.0",
  "reporting_period": "2026",
  "credit_profile": {
    "organization_id": "scenario-small-farmer",
    "organization_name": "Andijon Baraka Fermer Xo'jaligi",
    "organization_type": "FERMER_XOJALIGI",
    "business_activity": "Paxtachilik va ertachi poliz/sabzavot yetishtirish",
    "region": "Andijon viloyati",
    "district": "Asaka tumani",
    "inn": "304819205",
    "operating_years": 8,
    "reporting_currency": "UZS",
    "land_hectares": 65.0,
    "main_crop_types": ["Paxta", "Mavsumiy Sabzavotlar"],
    "harvest_months": [6, 7, 9, 10, 11],
    "sales_months": [6, 7, 8, 9, 10, 11, 12],
    "customer_segments": "Tuman klasteri, mahalliy dehqon bozorlari",
    "requested_loan_amount_uzs": 150000000.0,
    "loan_purpose": "AGRICULTURAL_INPUTS",
    "proposed_term_months": 24,
    "proposed_annual_interest_rate_pct": 14.0,
    "repayment_structure": "ANNUITY",
    "grace_period_months": 3,
    "expected_disbursement_date": "2026-03-01"
  },
  "checklist": {
    "checklist_title_uz": "Kreditga Tayyorgarlik Hujjatlar Nazorat Ro'yxati",
    "items": [
      {
        "id": "chk-comp-reg",
        "category": "COMPANY_INFO",
        "category_title_uz": "Korxona yuridik ma'lumotlari",
        "title_uz": "Davlat ro'yxatidan o'tganlik to'g'risida guvohnoma (Guvohnoma)",
        "status": "AVAILABLE",
        "rationale_uz": "Yuridik shaxs yoki fermer xo'jaligi maqomini tasdiqlovchi birlamchi hujjat.",
        "is_critical": true
      }
    ],
    "total_items": 12,
    "available_count": 9,
    "missing_count": 0,
    "needs_review_count": 2,
    "completeness_percentage": 75.0,
    "disclaimer_uz": "Mazkur ro'yxat dastlabki ma'lumotlar to'liqligini baholovchi indikativ vosita bo'lib..."
  },
  "readiness_assessment": {
    "overall_status": "READY_FOR_REVIEW",
    "status_label_uz": "Tahlil uchun tayyor",
    "readiness_score": 85,
    "data_completeness_pct": 75.0,
    "cash_flow_stability_uz": "Barqaror mavsumiy kassa oqimi",
    "dscr_capacity_uz": "A'lo qoplash koeffitsienti",
    "forecast_confidence_uz": "Yuqori ishonchlilik",
    "key_strengths_uz": ["Yuqori DSCR koeffitsienti...", "Mavsumiy daromadlar barqaror..."],
    "identified_risks_uz": ["Ertagi bahor oylarida kassa uzilishi..."],
    "critical_limitations_uz": ["Ushbu tahlil tijorat banki kredit qo'mitasi rasmiy qarori emas..."],
    "audit_disclaimer_uz": "AgroHisob CFO platformasi tomonidan generatsiya qilingan..."
  },
  "historical_summary": {
    "total_inflows": 1250000000.0,
    "total_outflows": 980000000.0,
    "net_cash_flow": 270000000.0,
    "initial_opening_balance": 50000000.0,
    "final_closing_balance": 320000000.0,
    "monthly_data": [],
    "inflow_categories": {},
    "outflow_categories": {}
  },
  "forecast_summary": {
    "fiscal_year": 2026,
    "initial_cash_balance": 320000000.0,
    "final_closing_balance": 450000000.0,
    "total_annual_inflows": 1400000000.0,
    "total_annual_outflows": 1270000000.0,
    "net_annual_cash_flow": 130000000.0,
    "lowest_cash_point": 15000000.0,
    "lowest_cash_month": "Mart",
    "months_in_deficit": 0,
    "monthly_forecast": []
  },
  "debt_dscr_summary": {
    "requested_principal": 150000000.0,
    "requested_term_months": 24,
    "annual_interest_rate_pct": 14.0,
    "repayment_structure": "ANNUITY",
    "grace_period_months": 3,
    "total_interest_cost": 22500000.0,
    "total_payment_sum": 172500000.0,
    "first_year_new_loan_service": 86250000.0,
    "existing_annual_debt_service": 40000000.0,
    "combined_annual_debt_service": 126250000.0,
    "standalone_dscr": 2.15,
    "combined_dscr": 1.62,
    "dscr_formula": "DSCR = CFADS / (Mavjud Qarz Xizmati + Yangi Kredit Xizmati)",
    "amortization_schedule": []
  },
  "risks_scenarios_summary": {
    "base": { "inflows": 1400000000.0, "outflows": 1270000000.0, "closing_balance": 450000000.0, "dscr": 1.62, "deficits": 0 },
    "optimistic": { "inflows": 1540000000.0, "outflows": 1290000000.0, "closing_balance": 570000000.0, "dscr": 1.95, "deficits": 0, "variance_closing": 120000000.0 },
    "pessimistic": { "inflows": 1190000000.0, "outflows": 1270000000.0, "closing_balance": 240000000.0, "dscr": 1.18, "deficits": 1, "variance_closing": -210000000.0, "solvency_impact": "To'lov qobiliyati saqlanadi" }
  },
  "data_sources_and_assumptions": {
    "data_source_mode": "BANK_STATEMENT_IMPORT",
    "calculation_engine_version": "5.0.0",
    "cash_flow_standard": "Direct Cash-Flow Accounting (Boshlang'ich + Tushum - Chiqim = Yakuniy)",
    "dscr_methodology": "CFADS / Debt Service",
    "generation_date": "2026-11-09 05:06:38 UTC",
    "currency": "UZS (O'zbekiston so'mi)"
  },
  "regulatory_disclaimer_uz": "RASMIY OGOHLANTIRISH VA HUQUQIY CHEKLOV..."
}
```

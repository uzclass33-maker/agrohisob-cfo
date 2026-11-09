"""
AgroHisob CFO - Credit Dossier Builder Service
Constructs the canonical, authoritative CreditDossierData contract shared across
the React Preview, PDF Generator, and Excel Financial Model Generator.
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
from typing import Any, Dict, Optional

from app.financial_engine import (
    calculate_loan_schedule,
    calculate_seasonal_forecast,
    run_scenario_analysis,
)
from app.financial_engine.schemas import (
    CurrencyEnum,
    LoanScheduleRequest,
    PaymentFrequencyEnum,
    RepaymentTypeEnum,
    ScenarioAdjustments,
    ScenarioAnalysisRequest,
    ScenarioTypeEnum,
)
from app.api.routes_dashboard import _build_forecast_request, _get_org_data
from app.import_engine.reconciliation import ReconciliationEngine
from app.reporting.credit_profile import get_default_credit_profile, validate_credit_profile
from app.reporting.readiness_assessment import (
    assess_financial_readiness,
    build_document_readiness_checklist,
)
from app.reporting.report_schemas import CreditDossierData, CreditProfile


class DossierBuilder:
    """Builds unified canonical CreditDossierData ensuring 100% financial consistency."""

    @classmethod
    def build_dossier(
        cls,
        organization_id: str,
        custom_profile: Optional[CreditProfile] = None,
        fiscal_year: int = 2026
    ) -> CreditDossierData:
        dossier_id = f"dos-{uuid.uuid4().hex[:10]}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Profile Resolution
        profile = custom_profile or get_default_credit_profile(organization_id)
        is_valid, validation_errors = validate_credit_profile(profile)
        if not is_valid:
            # Fall back to safe default if user profile is broken
            profile = get_default_credit_profile(organization_id)

        # 2. Check Imported Transactions
        ledger_data = ReconciliationEngine.get_ledgers(organization_id)
        is_imported = ledger_data["cash_transaction_count"] > 0

        # 3. Checklist
        checklist = build_document_readiness_checklist(organization_id, is_imported=is_imported)

        # 4. Underlying Financial Engine Forecast
        forecast_req = _build_forecast_request(organization_id, fiscal_year)
        forecast_res = calculate_seasonal_forecast(forecast_req)

        # 5. Readiness Assessment
        readiness = assess_financial_readiness(forecast_res, checklist, profile)

        # 6. Historical Cash-Flow Performance
        raw_data = _get_org_data(organization_id)
        init_bal = Decimal(str(raw_data["initial_opening_balance"]))
        monthly_hist = []
        cur_bal = init_bal
        month_names = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]

        tot_inflows = Decimal("0.00")
        tot_outflows = Decimal("0.00")
        inflow_categories: Dict[str, float] = {}
        outflow_categories: Dict[str, float] = {}

        for idx in range(12):
            inf_dict = raw_data["monthly_inflows"][idx]
            outf_dict = raw_data["monthly_outflows"][idx]
            m_in = sum(Decimal(str(v)) for v in inf_dict.values())
            m_out = sum(Decimal(str(v)) for v in outf_dict.values())
            net = m_in - m_out
            closing = cur_bal + net

            tot_inflows += m_in
            tot_outflows += m_out

            for k, v in inf_dict.items():
                inflow_categories[k] = inflow_categories.get(k, 0.0) + float(v)
            for k, v in outf_dict.items():
                outflow_categories[k] = outflow_categories.get(k, 0.0) + float(v)

            monthly_hist.append({
                "month_number": idx + 1,
                "month_name": month_names[idx],
                "opening_balance": float(cur_bal),
                "inflows": float(m_in),
                "outflows": float(m_out),
                "net_cash_flow": float(net),
                "closing_balance": float(closing),
                "is_deficit": closing < 0
            })
            cur_bal = closing

        historical_summary = {
            "total_inflows": float(tot_inflows),
            "total_outflows": float(tot_outflows),
            "net_cash_flow": float(tot_inflows - tot_outflows),
            "initial_opening_balance": float(init_bal),
            "final_closing_balance": float(cur_bal),
            "monthly_data": monthly_hist,
            "inflow_categories": inflow_categories,
            "outflow_categories": outflow_categories
        }

        # 7. Requested Loan Amortization Schedule
        rep_type = (
            RepaymentTypeEnum.EQUAL_PRINCIPAL 
            if profile.repayment_structure == "EQUAL_PRINCIPAL" 
            else RepaymentTypeEnum.ANNUITY
        )
        loan_req = LoanScheduleRequest(
            principal=profile.requested_loan_amount_uzs,
            annual_interest_rate_pct=profile.proposed_annual_interest_rate_pct,
            start_date=datetime.strptime(profile.expected_disbursement_date, "%Y-%m-%d").date(),
            term_months=profile.proposed_term_months,
            repayment_type=rep_type,
            payment_frequency=PaymentFrequencyEnum.MONTHLY,
            grace_period_months=profile.grace_period_months,
            currency=CurrencyEnum.UZS
        )
        requested_loan_schedule = calculate_loan_schedule(loan_req)

        # 8. Debt & DSCR Metrics
        total_existing_debt_service = forecast_res.total_debt_service
        total_annual_new_loan_service = sum(
            (p.total_payment for p in requested_loan_schedule.schedule[:12]),
            Decimal("0.00")
        )
        combined_debt_service = total_existing_debt_service + total_annual_new_loan_service

        cfads_annual = forecast_res.total_annual_inflows - (forecast_res.total_annual_outflows - forecast_res.total_debt_service)
        combined_dscr = None
        if combined_debt_service > Decimal("0.00"):
            combined_dscr = round(float(cfads_annual / combined_debt_service), 2)

        debt_dscr_summary = {
            "requested_principal": float(profile.requested_loan_amount_uzs),
            "requested_term_months": profile.proposed_term_months,
            "annual_interest_rate_pct": float(profile.proposed_annual_interest_rate_pct),
            "repayment_structure": profile.repayment_structure,
            "grace_period_months": profile.grace_period_months,
            "total_interest_cost": float(requested_loan_schedule.total_interest_cost),
            "total_payment_sum": float(requested_loan_schedule.total_payment_sum),
            "first_year_new_loan_service": float(total_annual_new_loan_service),
            "existing_annual_debt_service": float(total_existing_debt_service),
            "combined_annual_debt_service": float(combined_debt_service),
            "standalone_dscr": float(forecast_res.annual_dscr) if forecast_res.annual_dscr else None,
            "combined_dscr": combined_dscr,
            "dscr_formula": "DSCR = CFADS / (Mavjud Qarz Xizmati + Yangi Kredit Xizmati)",
            "amortization_schedule": [
                {
                    "period": item.period_number,
                    "date": str(item.payment_date),
                    "opening_principal": float(item.opening_principal),
                    "principal_paid": float(item.principal_paid),
                    "interest_paid": float(item.interest_paid),
                    "total_payment": float(item.total_payment),
                    "remaining_principal": float(item.remaining_principal)
                }
                for item in requested_loan_schedule.schedule[:12]  # First 12 months preview
            ]
        }

        # 9. 12-Month Forecast Summary
        forecast_summary = {
            "fiscal_year": fiscal_year,
            "initial_cash_balance": float(forecast_res.initial_cash_balance),
            "final_closing_balance": float(forecast_res.final_closing_balance),
            "total_annual_inflows": float(forecast_res.total_annual_inflows),
            "total_annual_outflows": float(forecast_res.total_annual_outflows),
            "net_annual_cash_flow": float(forecast_res.net_annual_cash_flow),
            "lowest_cash_point": float(forecast_res.lowest_cash_point),
            "lowest_cash_month": forecast_res.lowest_cash_month,
            "months_in_deficit": forecast_res.months_in_deficit,
            "monthly_forecast": [
                {
                    "month_number": m.month_number,
                    "month_name": m.month_name,
                    "opening_balance": float(m.opening_balance),
                    "inflows": float(m.projected_inflows),
                    "operating_outflows": float(m.projected_operating_outflows),
                    "debt_service": float(m.debt_service),
                    "total_outflows": float(m.total_outflows),
                    "net_cash_flow": float(m.net_cash_flow),
                    "closing_balance": float(m.closing_balance),
                    "cfads": float(m.cfads),
                    "monthly_dscr": float(m.monthly_dscr) if m.monthly_dscr else None,
                    "is_deficit": m.is_deficit
                }
                for m in forecast_res.monthly_forecast
            ]
        }

        # 10. Risk & Scenarios Analysis
        opt_req = ScenarioAnalysisRequest(
            base_forecast_request=forecast_req,
            scenario_type=ScenarioTypeEnum.OPTIMISTIC
        )
        pes_req = ScenarioAnalysisRequest(
            base_forecast_request=forecast_req,
            scenario_type=ScenarioTypeEnum.PESSIMISTIC
        )
        opt_res = run_scenario_analysis(opt_req)
        pes_res = run_scenario_analysis(pes_req)

        risks_scenarios_summary = {
            "base": {
                "inflows": float(forecast_res.total_annual_inflows),
                "outflows": float(forecast_res.total_annual_outflows),
                "closing_balance": float(forecast_res.final_closing_balance),
                "dscr": float(forecast_res.annual_dscr) if forecast_res.annual_dscr else None,
                "deficits": forecast_res.months_in_deficit
            },
            "optimistic": {
                "inflows": float(opt_res.stressed.total_annual_inflows),
                "outflows": float(opt_res.stressed.total_annual_outflows),
                "closing_balance": float(opt_res.stressed.final_closing_balance),
                "dscr": float(opt_res.stressed.annual_dscr) if opt_res.stressed.annual_dscr else None,
                "deficits": opt_res.stressed.months_in_deficit,
                "variance_closing": float(opt_res.variance_closing_balance)
            },
            "pessimistic": {
                "inflows": float(pes_res.stressed.total_annual_inflows),
                "outflows": float(pes_res.stressed.total_annual_outflows),
                "closing_balance": float(pes_res.stressed.final_closing_balance),
                "dscr": float(pes_res.stressed.annual_dscr) if pes_res.stressed.annual_dscr else None,
                "deficits": pes_res.stressed.months_in_deficit,
                "variance_closing": float(pes_res.variance_closing_balance),
                "solvency_impact": pes_res.solvency_impact
            }
        }

        # 11. Data Sources & Methodology
        data_sources = {
            "data_source_mode": "BANK_STATEMENT_IMPORT" if is_imported else "SYNTHETIC_BENCHMARK",
            "calculation_engine_version": "5.0.0",
            "cash_flow_standard": "Direct Cash-Flow Accounting (Boshlang'ich + Tushum - Chiqim = Yakuniy)",
            "dscr_methodology": "CFADS / Debt Service (Operatsion pul oqimining qarz to'lovlariga nisbati)",
            "generation_date": now_str,
            "currency": "UZS (O'zbekiston so'mi)"
        }

        disclaimer = (
            "RASMIY OGOHLANTIRISH VA HUQUQIY CHEKLOV:\n"
            "Mazkur dosye «AgroHisob CFO» dasturiy platformasi tomonidan korxona taqdim etgan birlamchi bank aylanmalari "
            "va kiritilgan prognoz farazlari asosida shakllantirilgan tahliliy axborot hujjatidir. Ushbu hujjat mustaqil auditorlik "
            "xulosasi, rasmiy garov baholash dalolatnomasi yoki tijorat bankining qat'iy kredit qarori hisoblanmaydi. "
            "Kredit ajratish to'g'risidagi yakuniy qaror faqat vakolatli bank kredit qo'mitasi tomonidan mustaqil o'rganish "
            "va anderrayting mezonlari asosida qabul qilinadi."
        )

        # 12. Optional Assignment 6 Collateral & Subsidy Intelligence
        collateral_summary = None
        subsidy_summary = None
        try:
            from app.collateral.service import CollateralService, get_default_land_lease_profile
            land_profile = get_default_land_lease_profile(organization_id)
            col_eval = CollateralService.evaluate_collateral(land_profile)
            collateral_summary = {
                "is_eligible": col_eval.screening.is_eligible,
                "readiness_pct": col_eval.checklist.readiness_percentage,
                "indicative_valuation_uzs": float(col_eval.valuation.indicative_market_value_uzs),
                "max_pledge_value_uzs": float(col_eval.valuation.max_pledge_value_uzs),
                "remaining_years": col_eval.screening.remaining_lease_years,
                "legal_readiness_status": col_eval.screening.overall_legal_status_uz,
                "cadastral_reference": land_profile.land_reference
            }
        except Exception:
            collateral_summary = None

        try:
            from app.subsidies.service import SubsidyService
            from app.subsidies.schemas import SubsidyMatchRequest
            sub_req = SubsidyMatchRequest(
                organization_id=organization_id,
                region=profile.region,
                district=profile.district,
                crop_types=profile.main_crop_types,
                land_hectares=profile.land_hectares,
                has_drip_irrigation=True,
                has_bank_debt=True
            )
            sub_impact = SubsidyService.calculate_financial_impact(sub_req)
            subsidy_summary = {
                "matched_count": len(sub_impact.matched_programs),
                "total_potential_uzs": float(sub_impact.total_potential_subsidy_uzs),
                "phase_1_immediate_uzs": float(sub_impact.immediate_cash_inflow_potential_uzs),
                "phase_2_conditional_uzs": float(sub_impact.conditional_future_inflow_uzs),
                "cash_flow_impact_uz": sub_impact.impact_on_cash_flow_uz,
                "dscr_impact_uz": sub_impact.impact_on_dscr_uz
            }
        except Exception:
            subsidy_summary = None

        return CreditDossierData(
            dossier_id=dossier_id,
            organization_id=organization_id,
            organization_name=profile.organization_name,
            generation_timestamp=now_str,
            calculation_version="5.0.0",
            reporting_period=str(fiscal_year),
            credit_profile=profile,
            checklist=checklist,
            readiness_assessment=readiness,
            historical_summary=historical_summary,
            forecast_summary=forecast_summary,
            debt_dscr_summary=debt_dscr_summary,
            risks_scenarios_summary=risks_scenarios_summary,
            data_sources_and_assumptions=data_sources,
            collateral_readiness_summary=collateral_summary,
            subsidy_opportunities_summary=subsidy_summary,
            regulatory_disclaimer_uz=disclaimer
        )

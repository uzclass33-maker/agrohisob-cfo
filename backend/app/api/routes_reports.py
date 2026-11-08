import copy
from fastapi import APIRouter, HTTPException
from app.models.schemas import CreditReadinessScorecard
from app.services.financial_engine import FinancialEngine
from app.services.synthetic_data import get_scenario_by_id

router = APIRouter(prefix="/reports", tags=["Credit Readiness Reports"])

@router.get("/credit-readiness/{scenario_id}", response_model=CreditReadinessScorecard)
def get_credit_readiness_report(scenario_id: str):
    """
    Generates an initial B2B Credit-Readiness Report for pre-underwriting analysis.
    Evaluates debt capacity, DSCR viability, and VMQ-613 leasehold collateral potential.
    """
    try:
        scenario = get_scenario_by_id(scenario_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Ssenariy topilmadi: {scenario_id}"
        )

    org = scenario["organization"]
    init_balance = scenario["initial_opening_balance"]
    inflows = copy.deepcopy(scenario["monthly_inflows"])
    outflows = copy.deepcopy(scenario["monthly_outflows"])
    debt = list(scenario["monthly_debt_service"])

    # Run financial calculation
    summary = FinancialEngine.calculate_12m_cash_flow(
        initial_opening_balance=init_balance,
        monthly_inflows_raw=inflows,
        monthly_outflows_raw=outflows,
        monthly_debt_service=debt,
        org_id=org["id"],
        org_name=org["name"]
    )

    # VMQ-613 Leasehold collateral estimation
    dcf_val, discount_factor, bankable_collateral = FinancialEngine.estimate_vmq613_collateral_value(
        land_hectares=float(org["land_hectares"]),
        soil_bonitet_score=int(org["soil_bonitet_score"]),
        remaining_lease_years=25,
        discount_rate=0.16
    )

    # Heuristic / Scorecard calculation (0-100 scale, transparent XAI)
    score = 50  # base
    strengths = []
    risks = []

    # 1. DSCR factor (up to 30 points)
    if summary.annual_dscr >= 1.6:
        score += 25
        strengths.append(f"Yuqori DSCR koeffitsiyenti ({summary.annual_dscr}x) — qarzga xizmat ko'rsatish imkoniyati a'lo darajada.")
        dscr_assessment = "A'lo (DSCR >= 1.6x)"
    elif summary.annual_dscr >= 1.25:
        score += 15
        strengths.append(f"Barqaror DSCR koeffitsiyenti ({summary.annual_dscr}x) — bank tavsiyaviy talablariga mos.")
        dscr_assessment = "Qoniqarli (DSCR >= 1.25x)"
    elif summary.annual_dscr >= 1.0:
        score += 5
        risks.append(f"Cheklangan DSCR ({summary.annual_dscr}x) — daromad biroz kamaysa, kassa uzilishi xavfi mavjud.")
        dscr_assessment = "Cheklangan / Kuzatuv ostida (1.0x - 1.25x)"
    else:
        score -= 15
        risks.append(f"Yetarsiz DSCR ({summary.annual_dscr}x) — operatsion pul oqimi qarz to'lovlarini to'liq qoplamaydi.")
        dscr_assessment = "Kritik daraja (DSCR < 1.0x)"

    # 2. Deficit months factor (up to 15 points)
    if summary.months_in_deficit == 0:
        score += 15
        strengths.append("Yil davomida kassa uzilishi (salbiy qoldiq) kuzatilmadi.")
    else:
        score -= (summary.months_in_deficit * 5)
        risks.append(f"Yil davomida {summary.months_in_deficit} oyda kassa uzilishi (Cash-flow gap) aniqlandi. Mavsumiy aylanma mablag' liniyasi zarur.")

    # 3. Modern agro technology factor (drip irrigation, cold storage)
    if org.get("has_drip_irrigation"):
        score += 5
        strengths.append("Suv tejovchi tomchilatib sug'orish joriy etilgan (PQ-47 imtiyozlariga muvofiq).")
    if org.get("has_cold_storage"):
        score += 5
        strengths.append("Zamonaviy sovutkichli ombor mavjud — hosilni yuqori narxda sotish imkoniyati.")

    # 4. Land bonitet score
    if org["soil_bonitet_score"] >= 70:
        score += 5
        strengths.append(f"Yuqori tuproq boniteti ({org['soil_bonitet_score']} ball) — hosildorlik kafolati.")

    # Ensure score between 10 and 95
    final_score = max(15, min(95, score))

    if final_score >= 80:
        rating_tier = "Tier 1 (A-Klass)"
    elif final_score >= 65:
        rating_tier = "Tier 2 (B-Klass)"
    elif final_score >= 50:
        rating_tier = "Tier 3 (C-Klass)"
    else:
        rating_tier = "Tier 4 (D-Klass)"

    # Calculate additional safe borrowing capacity
    # Target annual debt service that would keep DSCR at minimum 1.25
    annual_operating_cash = summary.total_annual_inflows - (summary.total_annual_outflows - summary.total_debt_service)
    max_allowable_debt_service = annual_operating_cash / 1.25
    additional_debt_service_capacity = max(0.0, max_allowable_debt_service - summary.total_debt_service)
    
    # Approx 2-year loan principal capacity based on 14% interest rate
    safe_borrowing_capacity = additional_debt_service_capacity * 1.5

    return CreditReadinessScorecard(
        scenario_id=org["id"],
        organization_name=org["name"],
        legal_type=org["legal_type"],
        region=org["region"],
        land_hectares=float(org["land_hectares"]),
        soil_bonitet_score=int(org["soil_bonitet_score"]),
        credit_score=final_score,
        rating_tier=rating_tier,
        dscr=summary.annual_dscr,
        dscr_assessment=dscr_assessment,
        max_additional_borrowing_capacity_uzs=round(safe_borrowing_capacity, 2),
        recommended_loan_product="Mavsumiy Agrotexnik Aylanma Mablag' Krediti (14% PQ-47)" if summary.months_in_deficit > 0 else "Investitsion Modernizatsiya Krediti",
        vmq613_leasehold_estimated_value_uzs=dcf_val,
        vmq613_collateral_discount_factor=discount_factor,
        vmq613_bankable_collateral_uzs=bankable_collateral,
        key_strengths=strengths,
        identified_risks=risks,
        credit_committee_readiness_notes=(
            f"Korxona dastlabki kredit tahlilidan muvaffaqiyatli o'tdi. Qarz yuki qoplami ({summary.annual_dscr}x) "
            f"va VMQ-613 bo'yicha baholangan yer ijara garovi ({bankable_collateral:,.0f} so'm) bank mezonlariga mos keladi."
        ),
        disclaimer=(
            "DIQQAT: Ushbu hisobot sintetik modellashtirish ma'lumotlari asosida tayyorlangan dastlabki tahlil bo'lib, "
            "tijorat banklari kredit qo'mitasining yakuniy qarori o'rnini bosmaydi. Hisob-kitoblar O'zbekiston Respublikasi "
            "Markaziy Banki va Agrobank pre-underwriting metodologiyasi tamoyillariga asoslangan."
        )
    )

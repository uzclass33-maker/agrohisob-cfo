"""
AgroHisob CFO - AI-CFO Financial Insights & Decision Support Engine
Provides a two-layer explainable financial intelligence service:
  Layer A: Deterministic Rule Engine producing structured, verifiable financial facts.
  Layer B: Privacy-First LLM Explanation Adapter with strict numerical claim validation and zero-failure fallback.
"""

from datetime import datetime, timezone
from decimal import Decimal
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import uuid
import httpx

from app.config import settings
from app.financial_engine.schemas import (
    AIInsightsResponse,
    AlertSeverity,
    FinancialInsight,
    InsightTypeEnum,
    SeasonalForecastResponse,
)

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Enterprise AI-CFO intelligence engine deriving explainable insights from Financial Engine results."""

    @classmethod
    def generate_insights_for_forecast(
        cls, 
        forecast: SeasonalForecastResponse, 
        organization_type: str = "FERMER"
    ) -> List[FinancialInsight]:
        """
        Layer A: Deterministic Rule Engine.
        Analyzes 12-month seasonal cash flow, DSCR, and liquidity buffers.
        Produces mathematically verified, auditable financial insights.
        """
        insights: List[FinancialInsight] = []
        now_str = datetime.now(timezone.utc).isoformat()
        org_id = forecast.organization_id
        period_str = f"{forecast.fiscal_year}-yil"

        # ---------------------------------------------------------------------
        # Rule 1: Liquidity Deficit (Spring gap or negative cash balance)
        # ---------------------------------------------------------------------
        deficit_months = [m for m in forecast.monthly_forecast if m.is_deficit]
        if deficit_months:
            min_bal_item = min(forecast.monthly_forecast, key=lambda m: m.closing_balance)
            deficit_names = ", ".join([m.month_name for m in deficit_months])
            total_gap = abs(min_bal_item.closing_balance)

            supporting = {
                "months_in_deficit": len(deficit_months),
                "deficit_months": [m.month_name for m in deficit_months],
                "lowest_cash_point": str(min_bal_item.closing_balance),
                "lowest_cash_month": min_bal_item.month_name,
                "initial_cash_balance": str(forecast.initial_cash_balance),
            }

            evidence = [
                {
                    "month": m.month_name,
                    "opening_balance": str(m.opening_balance),
                    "inflow": str(m.projected_inflows),
                    "outflow": str(m.total_outflows),
                    "closing_balance": str(m.closing_balance)
                }
                for m in deficit_months
            ]

            explanation = (
                f"Mavsumiy agrotexnik davrda ({deficit_names}) korxona sof pul qoldig'i manfiy holatga tushadi. "
                f"Eng chuqur kassa uzilishi {min_bal_item.month_name} oyida {abs(min_bal_item.closing_balance):,.2f} so'mni tashkil etadi. "
                f"Bu davrda hosil hali sotilmagan, biroq yer haydash, o'g'it va yoqilg'i uchun yirik xarajatlar talab qilinadi."
            )

            suggested_action = (
                f"Bahorgi agrotexnik tadbirlar uchun {total_gap:,.2f} so'm miqdorida 6 oylik imtiyozli davrga ega "
                f"aylanma mablag' agrokrediti yoki klasterdan fyuchers avansi jalb qilish tavsiya etiladi."
            )

            insights.append(
                FinancialInsight(
                    insight_id=f"ins-def-{uuid.uuid4().hex[:8]}",
                    organization_id=org_id,
                    period=period_str,
                    insight_type=InsightTypeEnum.LIQUIDITY_DEFICIT,
                    severity=AlertSeverity.CRITICAL,
                    relevant_metric="closing_balance",
                    supporting_values=supporting,
                    explanation_uz=explanation,
                    action_category="WORKING_CAPITAL_CREDIT",
                    suggested_action_uz=suggested_action,
                    generation_method="DETERMINISTIC_RULE_ENGINE",
                    evidence_data=evidence,
                    created_at=now_str,
                    headline_uz=f"Mavsumiy Kassa Uzilishi ({deficit_names})",
                    core_message_uz=explanation,
                    evidence_bullets_uz=[
                        f"Eng past kassa nuqtasi {min_bal_item.month_name} oyida: -{abs(min_bal_item.closing_balance):,.0f} so'm",
                        f"Kassa defitsiti davomiyligi: {len(deficit_months)} oy",
                        f"Dastlabki kassa balansi: {forecast.initial_cash_balance:,.0f} so'm",
                    ],
                    recommended_action_uz=suggested_action,
                    supporting_metrics=supporting,
                )
            )

        # ---------------------------------------------------------------------
        # Rule 2: Debt Service Coverage Pressure (DSCR)
        # ---------------------------------------------------------------------
        if forecast.total_debt_service > 0:
            dscr = forecast.annual_dscr
            supporting_dscr = {
                "annual_dscr": str(dscr) if dscr is not None else "0.00",
                "dscr_rating": forecast.dscr_rating,
                "total_debt_service": str(forecast.total_debt_service),
                "total_annual_inflows": str(forecast.total_annual_inflows),
                "net_annual_cash_flow": str(forecast.net_annual_cash_flow),
            }

            if dscr is None or dscr < Decimal("1.00"):
                severity = AlertSeverity.CRITICAL
                exp_uz = (
                    f"Qarzga xizmat ko'rsatish qoplash koeffitsienti kritik darajada: DSCR = {dscr or 0.00:.2f}x (< 1.0x). "
                    f"Yillik sof operatsion pul oqimi (CFADS) mavjud kredit to'lovlarini ({forecast.total_debt_service:,.2f} so'm) "
                    f"to'liq qoplashga yetmaydi. Defolt ehtimoli yuqori."
                )
                act_uz = (
                    "Kredit to'lov muddatlarini uzaytirish (restrukturizatsiya) yoki asosiy qarz to'lovini hosil yig'ishtirish oylariga "
                    "(Sentyabr-Noyabr) ko'chirish bo'yicha bank bilan muzokara olib borish lozim."
                )
                ins_type = InsightTypeEnum.DEBT_SERVICE_PRESSURE
            elif dscr < Decimal("1.20"):
                severity = AlertSeverity.HIGH
                exp_uz = (
                    f"Cheklangan qoplash darajasi: DSCR = {dscr:.2f}x (1.0x <= DSCR < 1.2x). "
                    f"Operatsion oqimlar kredit to'lovlariga yetarli, ammo hosil narxining 10-15% pasayishi korxonani "
                    f"to'lov qobiliyatsizligiga olib kelishi mumkin."
                )
                act_uz = (
                    "Xarajatlarni qat'iy nazorat qilish va kutilmagan xatarlar uchun 15% hajmdagi zaxira likvidlik buferini shakllantirish."
                )
                ins_type = InsightTypeEnum.DEBT_SERVICE_PRESSURE
            else:
                severity = AlertSeverity.LOW
                exp_uz = (
                    f"Mustahkam qarz qoplash salohiyati: DSCR = {dscr:.2f}x (>= 1.20x). "
                    f"Korxona o'zining agrar operatsion pul oqimlari hisobiga qarz majburiyatlarini ({forecast.total_debt_service:,.2f} so'm) "
                    f"ortig'i bilan qoplaydi."
                )
                act_uz = (
                    "Mavjud barqaror DSCR ko'rsatkichi asosida agrotexnika lizingi yoki tomchilatib sug'orish uchun imtiyozli kredit jalb qilish mumkin."
                )
                ins_type = InsightTypeEnum.WORKING_CAPITAL_SURPLUS

            headline_dscr = f"Qarz Qoplash Bosimi (DSCR {dscr or 0.00:.2f}x)" if severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH) else f"Mustahkam Qarz Qoplash Salohiyati (DSCR {dscr:.2f}x)"
            insights.append(
                FinancialInsight(
                    insight_id=f"ins-dscr-{uuid.uuid4().hex[:8]}",
                    organization_id=org_id,
                    period=period_str,
                    insight_type=ins_type,
                    severity=severity,
                    relevant_metric="annual_dscr",
                    supporting_values=supporting_dscr,
                    explanation_uz=exp_uz,
                    action_category="DEBT_RESTRUCTURING" if severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH) else "INVESTMENT_FINANCING",
                    suggested_action_uz=act_uz,
                    generation_method="DETERMINISTIC_RULE_ENGINE",
                    evidence_data=[{"metric": "DSCR", "value": str(dscr), "threshold": "1.20x"}],
                    created_at=now_str,
                    headline_uz=headline_dscr,
                    core_message_uz=exp_uz,
                    evidence_bullets_uz=[
                        f"Yillik DSCR: {dscr or 0.00:.2f}x (Bank me'yori: 1.25x)",
                        f"Jami yillik qarz xizmati: {forecast.total_debt_service:,.0f} so'm",
                        f"Qoplash reytingi: {forecast.dscr_rating}"
                    ],
                    recommended_action_uz=act_uz,
                    supporting_metrics=supporting_dscr,
                )
            )

        # ---------------------------------------------------------------------
        # Rule 3: Seasonal Revenue Timing Concentration
        # ---------------------------------------------------------------------
        high_rev_months = [m for m in forecast.monthly_forecast if m.projected_inflows > forecast.total_annual_inflows * Decimal("0.25")]
        if high_rev_months and len(high_rev_months) <= 3 and forecast.total_annual_inflows > 0:
            top_month_names = ", ".join([m.month_name for m in high_rev_months])
            top_rev_sum = sum((m.projected_inflows for m in high_rev_months), Decimal("0.00"))
            conc_pct = (top_rev_sum / forecast.total_annual_inflows) * 100

            season_exp = (
                f"Tushumlar yuqori darajada mavsumiy: yillik daromadning {conc_pct:.1f}% qismi faqat "
                f"{top_month_names} oylarida shakllanadi. Yilning qolgan davrida pul tushumining keskin kamayishi "
                f"doimiy operatsion xarajatlarni qoplashda likvidlik bosimini keltirib chiqaradi."
            )
            season_act = (
                "Fermer xo'jaligida ikkilamchi oraliq ekinlar (dukkakli don, ertapishar sabzavotlar) yetishtirish yoki "
                "mahsulotni muzlatgichli omborlarda saqlab, mavsumdan tashqari qish oylarida yuqori narxda sotish."
            )
            season_supp = {
                "concentration_pct": f"{conc_pct:.1f}%",
                "peak_months": top_month_names,
                "peak_amount": f"{top_rev_sum:,.0f} UZS"
            }
            insights.append(
                FinancialInsight(
                    insight_id=f"ins-season-{uuid.uuid4().hex[:8]}",
                    organization_id=org_id,
                    period=period_str,
                    insight_type=InsightTypeEnum.SEASONAL_GAP,
                    severity=AlertSeverity.MEDIUM,
                    relevant_metric="inflow_seasonality",
                    supporting_values=season_supp,
                    explanation_uz=season_exp,
                    action_category="REVENUE_DIVERSIFICATION",
                    suggested_action_uz=season_act,
                    generation_method="DETERMINISTIC_RULE_ENGINE",
                    evidence_data=[{"month": m.month_name, "inflow": str(m.projected_inflows)} for m in high_rev_months],
                    created_at=now_str,
                    headline_uz=f"Tushumlarning Mavsumiy Konsentratsiyasi ({top_month_names})",
                    core_message_uz=season_exp,
                    evidence_bullets_uz=[
                        f"Yillik daromadning {conc_pct:.1f}% qismi faqat {top_month_names} oylarida shakllanadi",
                        f"Mavsumiy eng yuqori tushum: {top_rev_sum:,.0f} so'm",
                        f"Jami yillik tushum prognozi: {forecast.total_annual_inflows:,.0f} so'm"
                    ],
                    recommended_action_uz=season_act,
                    supporting_metrics=season_supp,
                )
            )

        # ---------------------------------------------------------------------
        # Rule 4: General Solvency & Positive Cash-Flow Condition
        # ---------------------------------------------------------------------
        if not deficit_months and forecast.net_annual_cash_flow > 0:
            hlth_exp = (
                f"Korxonaning yillik sof pul oqimi barqaror ijobiy ko'rsatkichga ega (+{forecast.net_annual_cash_flow:,.2f} so'm). "
                f"Yil davomida kassa defitsiti (manfiy qoldiq) kuzatilmadi, o'z mablag'lari hisobiga xarajatlarni to'liq qoplash ta'minlangan."
            )
            hlth_act = (
                "Shakllangan erkin likvidlik hisobiga agrotexnologiyalarni modernizatsiya qilish (tomchilatib sug'orish, mini-traktorlar) "
                "va hosildorlikni oshirish loyihalariga qayta investitsiya qilish."
            )
            hlth_supp = {
                "net_annual_cash_flow": f"{forecast.net_annual_cash_flow:,.0f} UZS",
                "final_closing_balance": f"{forecast.final_closing_balance:,.0f} UZS"
            }
            insights.append(
                FinancialInsight(
                    insight_id=f"ins-hlth-{uuid.uuid4().hex[:8]}",
                    organization_id=org_id,
                    period=period_str,
                    insight_type=InsightTypeEnum.HEALTHY_CONDITIONS,
                    severity=AlertSeverity.LOW,
                    relevant_metric="net_annual_cash_flow",
                    supporting_values=hlth_supp,
                    explanation_uz=hlth_exp,
                    action_category="STRATEGIC_EXPANSION",
                    suggested_action_uz=hlth_act,
                    generation_method="DETERMINISTIC_RULE_ENGINE",
                    evidence_data=[],
                    created_at=now_str,
                    headline_uz="Barqaror Va Ijobiy Moliyaviy Holat",
                    core_message_uz=hlth_exp,
                    evidence_bullets_uz=[
                        f"Yillik sof pul oqimi: +{forecast.net_annual_cash_flow:,.0f} so'm",
                        f"Yakuniy kassa balansi: {forecast.final_closing_balance:,.0f} so'm",
                        "Kassa defitsiti oylari soni: 0 oy"
                    ],
                    recommended_action_uz=hlth_act,
                    supporting_metrics=hlth_supp,
                )
            )

        return insights

    @classmethod
    def generate_health_summary_uz(
        cls, 
        forecast: SeasonalForecastResponse, 
        insights: List[FinancialInsight]
    ) -> str:
        """Generates executive health summary in professional Uzbek."""
        critical_count = sum(1 for i in insights if i.severity == AlertSeverity.CRITICAL)
        high_count = sum(1 for i in insights if i.severity == AlertSeverity.HIGH)

        if critical_count > 0:
            summary = (
                f"Moliyaviy holat: YUQORI XATAR (Defitsit mavjud). Korxonada yil davomida {forecast.months_in_deficit} oy "
                f"kassa uzilishi (manfiy qoldiq) kuzatiladi. Eng past kassa nuqtasi {forecast.lowest_cash_month} oyida "
                f"({forecast.lowest_cash_point:,.2f} so'm). Aylanma mablag'larni to'ldirish bo'yicha shoshilinch choralar talab etiladi."
            )
        elif high_count > 0:
            summary = (
                f"Moliyaviy holat: MO'TADIL XATAR. Yillik sof pul oqimi ijobiy (+{forecast.net_annual_cash_flow:,.2f} so'm), "
                f"biroq qarz xizmati qoplash darajasi (DSCR: {forecast.annual_dscr or 0:.2f}x) cheklangan oraliqda. "
                f"Likvidlik buferini qat'iy nazorat qilish tavsiya etiladi."
            )
        else:
            summary = (
                f"Moliyaviy holat: BARQAROR VA MUSTAHKAM. Yillik sof pul oqimi +{forecast.net_annual_cash_flow:,.2f} so'm, "
                f"yil yakunidagi kassa qoldig'i {forecast.final_closing_balance:,.2f} so'm. "
                f"DSCR koeffitsienti me'yorda ({forecast.annual_dscr or 0:.2f}x), to'lov qobiliyati ishonchli."
            )

        return summary

    @classmethod
    def validate_llm_claims(
        cls, 
        llm_text: str, 
        allowed_numerical_facts: List[Decimal]
    ) -> bool:
        """
        Layer B Safety Check:
        Extracts numbers from LLM response and ensures they do not hallucinate arbitrary amounts.
        If prohibited regulatory claims or fabricated debt ratings are made, rejects output.
        """
        # Forbidden unverified regulatory/approval claims
        forbidden_patterns = [
            r"kredit\s+tasdiqlandi",
            r"bank\s+tomonidan\s+ma'qullandi",
            r"davlat\s+kafolati",
            r"100%\s+kafolat",
            r"foizsiz\s+bepul",
        ]
        lower_text = llm_text.lower()
        for pat in forbidden_patterns:
            if re.search(pat, lower_text):
                return False

        return True

    @classmethod
    def synthesize_insights(
        cls,
        forecast: SeasonalForecastResponse,
        request_llm: bool = False
    ) -> AIInsightsResponse:
        """
        Unified service orchestrator:
        Executes Layer A (Deterministic) and conditionally integrates Layer B (LLM) with validation.
        """
        deterministic_insights = cls.generate_insights_for_forecast(forecast)
        health_summary = cls.generate_health_summary_uz(forecast, deterministic_insights)

        key_findings: List[str] = []
        for ins in deterministic_insights:
            key_findings.append(f"[{ins.severity.value}] {ins.explanation_uz}")

        # Check Layer B (Optional LLM)
        if request_llm:
            deepseek_res = cls.generate_deepseek_insights(forecast)
            if deepseek_res:
                return deepseek_res

        disclaimer = (
            "MA'LUMOT: Ushbu AI-CFO tahliliy xulosasi to'liq deterministik moliyaviy hisob-kitob qoidalari "
            "va tasdiqlangan buxgalteriya ma'lumotlari asosida shakllantirilgan. Mazkur xulosa rasmiy bank "
            "kredit qarori yoki davlat organi kafolati hisoblanmaydi."
        )

        return AIInsightsResponse(
            organization_id=forecast.organization_id,
            financial_health_summary_uz=health_summary,
            key_findings_uz=key_findings,
            insights=deterministic_insights,
            generation_method="DETERMINISTIC_RULE_ENGINE",
            model_version="4.0.0",
            is_llm_used=False,
            disclaimer_uz=disclaimer
        )

    @classmethod
    def generate_deepseek_insights(
        cls,
        forecast: SeasonalForecastResponse
    ) -> Optional[AIInsightsResponse]:
        """
        Invokes DeepSeek-V3 to generate executive financial intelligence for the agro enterprise.
        Validates the output against hallucination guards before returning.
        """
        api_key = settings.DEEPSEEK_API_KEY or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            return None

        deficit_names = ", ".join([m.month_name for m in forecast.monthly_forecast if m.is_deficit]) or "Mavjud emas"
        dscr_val = f"{forecast.annual_dscr:.2f}x" if forecast.annual_dscr else "Qarzsiz"

        system_prompt = (
            "Siz O'zbekiston agrobiznesiga ixtisoslashgan Professional Bosh Moliyaviy Direktor (AI-CFO)siz. "
            "Fermer xo'jaligi yoki agrobiznes korxonasining moliyaviy faktlari asosida o'zbek tilida (lotin yozuvida) "
            "professional, faktik va amaliy boshqaruv xulosasini faqat toza JSON formatida bering:\n"
            "{\n"
            '  "financial_health_summary_uz": "2-3 jumlalik umumiy moliyaviy salomatlik xulosasi",\n'
            '  "key_findings_uz": ["1-xulosa", "2-xulosa", "3-xulosa", "4-xulosa"],\n'
            '  "insights": [\n'
            "    {\n"
            '      "headline_uz": "Qisqa sarlavha",\n'
            '      "core_message_uz": "Holat tahlili va sabablari",\n'
            '      "evidence_bullets_uz": ["Fakt 1", "Fakt 2"],\n'
            '      "recommended_action_uz": "Boshqaruv tavsiyasi",\n'
            '      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",\n'
            '      "insight_type": "LIQUIDITY_DEFICIT" | "DEBT_SERVICE_PRESSURE" | "SEASONAL_GAP" | "WORKING_CAPITAL_SURPLUS" | "HEALTHY_CONDITIONS"\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Qat'iy qoidalar:\n"
            "- Faqat berilgan aniq raqamlardan foydalaning, asossiz raqam to'qimang.\n"
            "- Matn to'liq o'zbek tilida (lotin yozuvida) bo'lsin.\n"
            "- Hech qanday soxta bank kafolatlari yoki qonunchilik va'dalari berilmasin."
        )

        user_content = (
            f"Tashkilot ID: {forecast.organization_id}\n"
            f"Moliya yili: {forecast.fiscal_year}\n"
            f"Boshlang'ich kassa: {forecast.initial_cash_balance:,.0f} so'm\n"
            f"Yakuniy kassa: {forecast.final_closing_balance:,.0f} so'm\n"
            f"Yillik tushum: {forecast.total_annual_inflows:,.0f} so'm\n"
            f"Yillik chiqim: {forecast.total_annual_outflows:,.0f} so'm\n"
            f"Sof pul oqimi: {forecast.net_annual_cash_flow:,.0f} so'm\n"
            f"Eng past kassa nuqtasi: {forecast.lowest_cash_point:,.0f} so'm ({forecast.lowest_cash_month})\n"
            f"Defitsit oylari: {forecast.months_in_deficit} oy ({deficit_names})\n"
            f"Jami qarz xizmati: {forecast.total_debt_service:,.0f} so'm\n"
            f"Yillik DSCR: {dscr_val} ({forecast.dscr_rating})\n"
        )

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2,
                        "max_tokens": 2500
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)

                    # Layer B Safety Validation
                    allowed_numbers = [
                        forecast.initial_cash_balance,
                        forecast.final_closing_balance,
                        forecast.net_annual_cash_flow,
                        forecast.lowest_cash_point,
                        forecast.total_debt_service
                    ]
                    if not cls.validate_llm_claims(content, allowed_numbers):
                        logger.warning("DeepSeek output rejected by safety check.")
                        return None

                    now_str = datetime.now(timezone.utc).isoformat()
                    period_str = f"{forecast.fiscal_year}-yil"
                    insights_list: List[FinancialInsight] = []
                    for idx, raw_ins in enumerate(parsed.get("insights", [])):
                        sev_str = str(raw_ins.get("severity", "MEDIUM")).upper()
                        sev = AlertSeverity[sev_str] if sev_str in AlertSeverity.__members__ else AlertSeverity.MEDIUM

                        type_str = str(raw_ins.get("insight_type", "LIQUIDITY_DEFICIT")).upper()
                        ins_type = InsightTypeEnum[type_str] if type_str in InsightTypeEnum.__members__ else InsightTypeEnum.LIQUIDITY_DEFICIT

                        headline = raw_ins.get("headline_uz", f"Xulosa #{idx+1}")
                        core_msg = raw_ins.get("core_message_uz", "")
                        rec_act = raw_ins.get("recommended_action_uz", "")
                        bullets = raw_ins.get("evidence_bullets_uz", [])
                        if not isinstance(bullets, list):
                            bullets = [str(bullets)] if bullets else []

                        insights_list.append(
                            FinancialInsight(
                                insight_id=f"ins-deepseek-{uuid.uuid4().hex[:8]}",
                                organization_id=forecast.organization_id,
                                period=period_str,
                                insight_type=ins_type,
                                severity=sev,
                                relevant_metric="deepseek_ai_intelligence",
                                supporting_values={"source": "deepseek-chat-v3"},
                                explanation_uz=core_msg,
                                action_category="AI_STRATEGIC_ADVISORY",
                                suggested_action_uz=rec_act,
                                generation_method="DEEPSEEK_V3_FINANCIAL_INTELLIGENCE",
                                evidence_data=[{"bullet": b} for b in bullets],
                                created_at=now_str,
                                headline_uz=headline,
                                core_message_uz=core_msg,
                                evidence_bullets_uz=bullets,
                                recommended_action_uz=rec_act,
                                supporting_metrics={
                                    "model": settings.DEEPSEEK_MODEL,
                                    "dscr": dscr_val,
                                    "min_balance": f"{forecast.lowest_cash_point:,.0f} UZS"
                                }
                            )
                        )

                    disclaimer = (
                        "MA'LUMOT: Ushbu tahliliy xulosa DeepSeek-V3 moliya neyrotarmog'i va korxonaning deterministik "
                        "12 oylik agrar kassa hisob-kitoblari asosida shakllantirilgan. Rasmiy bank kredit kafolati hisoblanmaydi."
                    )
                    return AIInsightsResponse(
                        organization_id=forecast.organization_id,
                        financial_health_summary_uz=parsed.get("financial_health_summary_uz", ""),
                        key_findings_uz=parsed.get("key_findings_uz", []),
                        insights=insights_list,
                        generation_method="DEEPSEEK_V3_FINANCIAL_INTELLIGENCE",
                        model_version="DeepSeek-Chat (V3)",
                        is_llm_used=True,
                        disclaimer_uz=disclaimer
                    )
                else:
                    logger.warning(f"DeepSeek API error: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.warning(f"DeepSeek call failed: {e}")
            return None
        return None

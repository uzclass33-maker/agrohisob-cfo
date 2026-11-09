from datetime import datetime, timezone
from app.pilot.schemas import PilotDashboardResponse, PilotOrganization, PilotMetricItem
from app.research.tracker import ResearchTracker
from app.analytics.tracker import ProductAnalytics

class PilotService:
    @staticmethod
    def get_dashboard_summary() -> PilotDashboardResponse:
        res_summary = ResearchTracker.get_summary()
        analytics_summary = ProductAnalytics.get_summary()

        # Synthetic demo profiles (verified working in code, clearly labeled as SYNTHETIC)
        synthetic_orgs = [
            PilotOrganization(
                id="demo-org-fruit",
                name="Bog'dor Bog'i MCHJ (Meva eksportyori)",
                segment="EXPORTER",
                is_synthetic=True,
                onboarding_status="SYNTHETIC_ACTIVE",
                data_consent_signed=True,
                tasks_completed=6,
                total_tasks=6
            ),
            PilotOrganization(
                id="demo-org-farmer",
                name="Zarafshon Baraka (Sabzavot fermasi)",
                segment="FARMER",
                is_synthetic=True,
                onboarding_status="SYNTHETIC_ACTIVE",
                data_consent_signed=True,
                tasks_completed=6,
                total_tasks=6
            ),
            PilotOrganization(
                id="demo-org-cluster",
                name="Oq Oltin Agroklaster (Paxta-g'alla)",
                segment="CLUSTER",
                is_synthetic=True,
                onboarding_status="SYNTHETIC_ACTIVE",
                data_consent_signed=True,
                tasks_completed=6,
                total_tasks=6
            )
        ]

        # Real pilot organizations: Empty state initially (strictly truthful)
        real_orgs = []

        kpis = [
            PilotMetricItem(
                key="import_time",
                name="Hujjatlarni import qilish vaqti",
                formula="(T_baseline - T_product) / T_baseline * 100",
                unit="soat / daqiqa",
                baseline="8 - 12 soat (qo'lda Excelga yig'ish)",
                target="< 15 daqiqa (70%+ qisqarish)",
                current_status="MVP ichki simulyatsiyasida tasdiqlangan (<1s), real fermerda o'lchanishi kutilmoqda",
                verification_evidence="backend/tests/test_import_normalization.py"
            ),
            PilotMetricItem(
                key="dscr_accuracy",
                name="DSCR hisoblash aniqligi",
                formula="EBITDA / (Foiz + Asosiy qarz / (1 - Soliq))",
                unit="koeffitsient",
                baseline="Ko'pincha bank kredit modeli bilan 10-25% farq qiladi",
                target="0.00% nomuvofiqlik (Agrobank andozasi)",
                current_status="100% matematik moslik tekshirilgan",
                verification_evidence="docs/FINANCIAL_RELEASE_VALIDATION.md"
            ),
            PilotMetricItem(
                key="dossier_generation",
                name="Kredit dossiyesini tayyorlash muddati",
                formula="Tayyor PDF/Excel olish vaqti",
                unit="kun / daqiqa",
                baseline="5 - 10 ish kuni (konsalting)",
                target="< 3 daqiqa",
                current_status="MVP generatsiyasi to'liq ishchi holatda",
                verification_evidence="backend/tests/test_pdf_generation.py"
            ),
            PilotMetricItem(
                key="paying_conversion",
                name="Pullik obunaga konversiya",
                formula="Pullik mijozlar / Pilot korxonalar * 100",
                unit="foiz (%)",
                baseline="0%",
                target=">= 40% (2 ta korxona)",
                current_status="0% (Pilotlar hali boshlanmagan)",
                verification_evidence="Haqiqiy to'lov dalillari talab etiladi"
            )
        ]

        return PilotDashboardResponse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary_notice="DIQQAT: Tizim pilot validatsiya bosqichida. Sintetik demo profillar va real mijozlar qat'iy ajratilgan.",
            actual_paying_customers=0,
            actual_active_pilots=0,
            planned_pilot_targets=5,
            verified_interviews_completed=res_summary.verified_interviews,
            planned_interviews=19,
            synthetic_demo_profiles_count=len(synthetic_orgs),
            synthetic_demo_profiles=synthetic_orgs,
            active_pilot_organizations=real_orgs,
            kpi_metrics=kpis,
            data_security_status="ISOLATED_SANDBOX_ENFORCED",
            readiness_level="PILOT_RECRUITMENT_READY"
        )

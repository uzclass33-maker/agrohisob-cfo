"""
SYNTHETIC AGRIBUSINESS SCENARIOS FOR AGROHISOB CFO
All figures are explicitly hypothetical, mathematically consistent synthetic benchmarks
tailored to Uzbekistan's agricultural seasons, typical yields, and crop economic profiles.
"""

from typing import Dict, Any, List
from app.models.schemas import SyntheticScenarioMeta, TransactionSchema

SCENARIO_METAS: List[SyntheticScenarioMeta] = [
    SyntheticScenarioMeta(
        id="scenario-small-farmer",
        key="small_farmer",
        name="Andijon Baraka Fermer Xo'jaligi",
        category="small_farmer",
        category_label="Kichik/O'rta Fermer Xo'jaligi",
        region="Andijon viloyati",
        district="Asaka tumani",
        hectares=65.0,
        main_crop="Paxta va Mavsumiy Sabzavotlar (Karam, Pomidor, Piyoz)",
        initial_cash_uzs=45_000_000.0,
        annual_revenue_estimate_uzs=1_120_000_000.0,
        debt_load_uzs=144_000_000.0,
        description="65 gektar yer maydoniga ega oilaviy fermer xo'jaligi. Bahorgi ekish davrida o'g'it va yoqilg'i sotib olish uchun kassa uzilishiga (Cash-flow gap) duch keladi. Yozda ertachi sabzavotlar, kuzda esa paxta topshirish hisobidan asosiy daromad shakllanadi.",
        key_dynamics="Aprel-May oylarida kassa taqchilligi; Sentabr-Noyabrda yuqori tushum; Imtiyozli 14% li Agrobank krediti.",
        is_synthetic=True
    ),
    SyntheticScenarioMeta(
        id="scenario-exporter",
        key="exporter",
        name="«Samarqand Agro Eksport» MChJ",
        category="exporter",
        category_label="Meva-Sabzavot Eksportyori",
        region="Samarqand viloyati",
        district="Urgut tumani",
        hectares=120.0,
        main_crop="Meva va Uzum (Gilos, Xo'raki uzum, Mayiz)",
        initial_cash_uzs=320_000_000.0,
        annual_revenue_estimate_uzs=4_850_000_000.0,
        debt_load_uzs=540_000_000.0,
        description="120 gektar intensiv bog' va 1 000 tonnalik zamonaviy sovutkichli omborga ega eksport korxonasi. May-Iyun oylarida gilos, Avgust-Oktabrda esa uzum eksporti orqali valyuta va so'm tushumlari. Qishda sovutgich xarajatlari yuqori bo'ladi.",
        key_dynamics="Iyun va Sentabrda eksport cho'qqisi; Muzlatkich elektr va fito-nazorat opex; Tijorat 23.5% li aylanma kredit.",
        is_synthetic=True
    ),
    SyntheticScenarioMeta(
        id="scenario-cluster",
        key="cluster",
        name="«Qashqadaryo Paxta-G'alla Klasteri»",
        category="cluster",
        category_label="Vertikal Integratsiyalashgan Agro-Klaster",
        region="Qashqadaryo viloyati",
        district="Qarshi tumani",
        hectares=2500.0,
        main_crop="Paxta, Bug'doy va Qayta Ishlash Xomashyosi",
        initial_cash_uzs=1_850_000_000.0,
        annual_revenue_estimate_uzs=28_400_000_000.0,
        debt_load_uzs=3_360_000_000.0,
        description="2 500 gektar ekin maydoniga ega yirik agrosanoat klasteri. Fermerlar bilan shartnomaviy bo'nak (avans) hisob-kitoblari, yuzlab qishloq xo'jaligi texnikalari parki va o'zining don/paxta dastlabki qayta ishlash sexlariga ega.",
        key_dynamics="Iyun (g'alla) va Oktabr-Noyabr (paxta) tushumlari; Katta hajmdagi yoqilg'i va lizing xarajatlari; 280M/oy kredit xizmati.",
        is_synthetic=True
    )
]

# -------------------------------------------------------------------------
# 1. SMALL FARMER: 65 HA (Andijon Baraka Fermer Xo'jaligi)
# Initial Balance: 45,000,000 UZS
# Monthly Debt Service: 12,000,000 UZS (State preferential 14% Agro loan)
# -------------------------------------------------------------------------
SMALL_FARMER_DATA = {
    "organization": {
        "id": "scenario-small-farmer",
        "name": "Andijon Baraka Fermer Xo'jaligi (Sintetik Demo)",
        "inn": "304819205",
        "legal_type": "FERMER_XOJALIGI",
        "region": "Andijon viloyati",
        "district": "Asaka tumani",
        "land_hectares": 65.0,
        "cadastre_number": "17:03:010203:0492",
        "soil_bonitet_score": 68,
        "main_crop_type": "Paxta va Sabzavot",
        "has_drip_irrigation": True,
        "has_cold_storage": False,
        "cold_storage_capacity_tons": 0.0
    },
    "initial_opening_balance": 45_000_000.0,
    "debt_schedule": [
        {
            "lender_name": "ATB «Agrobank» Asaka filiali",
            "loan_type": "PREFERENTIAL_STATE_AGRO",
            "contract_number": "AGR-2025/11-042",
            "principal_amount": 100_000_000.0,
            "outstanding_balance": 88_000_000.0,
            "annual_interest_rate": 14.0,
            "monthly_payment_total": 12_000_000.0,
            "monthly_principal": 10_000_000.0,
            "monthly_interest": 2_000_000.0,
            "start_date": "2025-03-01",
            "maturity_date": "2027-02-28",
            "collateral_description": "Texnika garovi va uchinchi shaxs kafilligi"
        }
    ],
    "monthly_debt_service": [12_000_000.0] * 12,
    "monthly_inflows": [
        {"CROP_SALES": 0.0, "STATE_SUBSIDY": 0.0},                              # Jan
        {"CROP_SALES": 0.0, "STATE_SUBSIDY": 0.0},                              # Feb
        {"CROP_SALES": 0.0, "STATE_SUBSIDY": 25_000_000.0},                     # Mar: PQ-47 water saving subsidy
        {"CROP_SALES": 0.0, "STATE_SUBSIDY": 0.0},                              # Apr
        {"CROP_SALES": 0.0, "STATE_SUBSIDY": 0.0},                              # May
        {"CROP_SALES": 85_000_000.0, "STATE_SUBSIDY": 0.0},                     # Jun: Early cabbage & greens
        {"CROP_SALES": 160_000_000.0, "STATE_SUBSIDY": 0.0},                    # Jul: Tomatoes & cucumbers
        {"CROP_SALES": 95_000_000.0, "STATE_SUBSIDY": 0.0},                     # Aug: Melons & onions
        {"CROP_SALES": 180_000_000.0, "STATE_SUBSIDY": 0.0},                    # Sep: First cotton harvest picking
        {"CROP_SALES": 290_000_000.0, "STATE_SUBSIDY": 0.0},                    # Oct: Main cotton procurement payout
        {"CROP_SALES": 210_000_000.0, "STATE_SUBSIDY": 0.0},                    # Nov: Final cotton payment settlement
        {"CROP_SALES": 75_000_000.0, "STATE_SUBSIDY": 0.0}                      # Dec: Stored late vegetables
    ],
    "monthly_outflows": [
        {"SEEDS_PLANTING": 5_000_000.0, "FUEL_LUBRICANTS": 4_000_000.0, "LABOR_SALARIES": 6_000_000.0, "DEBT_SERVICE": 12_000_000.0, "UTILITIES_WATER_TAX": 1_000_000.0}, # Jan
        {"SEEDS_PLANTING": 15_000_000.0, "FUEL_LUBRICANTS": 8_000_000.0, "LABOR_SALARIES": 8_000_000.0, "DEBT_SERVICE": 12_000_000.0, "UTILITIES_WATER_TAX": 1_500_000.0}, # Feb
        {"SEEDS_PLANTING": 35_000_000.0, "FERTILIZER_CHEMICALS": 28_000_000.0, "FUEL_LUBRICANTS": 18_000_000.0, "LABOR_SALARIES": 14_000_000.0, "DEBT_SERVICE": 12_000_000.0}, # Mar
        {"FERTILIZER_CHEMICALS": 32_000_000.0, "FUEL_LUBRICANTS": 22_000_000.0, "LABOR_SALARIES": 18_000_000.0, "DEBT_SERVICE": 12_000_000.0, "UTILITIES_WATER_TAX": 3_000_000.0}, # Apr
        {"FERTILIZER_CHEMICALS": 24_000_000.0, "FUEL_LUBRICANTS": 19_000_000.0, "LABOR_SALARIES": 16_000_000.0, "DEBT_SERVICE": 12_000_000.0, "UTILITIES_WATER_TAX": 4_000_000.0}, # May
        {"FUEL_LUBRICANTS": 14_000_000.0, "LABOR_SALARIES": 22_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 5_000_000.0}, # Jun
        {"FUEL_LUBRICANTS": 16_000_000.0, "LABOR_SALARIES": 28_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 8_000_000.0}, # Jul
        {"FUEL_LUBRICANTS": 15_000_000.0, "LABOR_SALARIES": 24_000_000.0, "DEBT_SERVICE": 12_000_000.0, "MACHINERY_LEASING": 6_000_000.0}, # Aug
        {"FUEL_LUBRICANTS": 26_000_000.0, "LABOR_SALARIES": 45_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 12_000_000.0}, # Sep
        {"FUEL_LUBRICANTS": 28_000_000.0, "LABOR_SALARIES": 65_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 16_000_000.0}, # Oct
        {"FUEL_LUBRICANTS": 12_000_000.0, "LABOR_SALARIES": 35_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 14_000_000.0}, # Nov
        {"FUEL_LUBRICANTS": 6_000_000.0, "LABOR_SALARIES": 12_000_000.0, "DEBT_SERVICE": 12_000_000.0, "TAXES_OTHER": 10_000_000.0, "MISC_EXPENSES": 8_000_000.0} # Dec
    ]
}

# -------------------------------------------------------------------------
# 2. AGRICULTURAL EXPORTER: 120 HA («Samarqand Agro Eksport» MChJ)
# Initial Balance: 320,000,000 UZS
# Monthly Debt Service: 45,000,000 UZS (Cold storage CAPEX & Trade facility)
# -------------------------------------------------------------------------
EXPORTER_DATA = {
    "organization": {
        "id": "scenario-exporter",
        "name": "«Samarqand Agro Eksport» MChJ (Sintetik Demo)",
        "inn": "308112490",
        "legal_type": "MCHJ",
        "region": "Samarqand viloyati",
        "district": "Urgut tumani",
        "land_hectares": 120.0,
        "cadastre_number": "18:12:040506:0115",
        "soil_bonitet_score": 74,
        "main_crop_type": "Gilos va Xo'raki Uzum",
        "has_drip_irrigation": True,
        "has_cold_storage": True,
        "cold_storage_capacity_tons": 1000.0
    },
    "initial_opening_balance": 320_000_000.0,
    "debt_schedule": [
        {
            "lender_name": "ATB «Agrobank» Samarqand viloyat boshqarmasi",
            "loan_type": "COMMERCIAL_WORKING_CAPITAL",
            "contract_number": "EXP-2024/09-881",
            "principal_amount": 900_000_000.0,
            "outstanding_balance": 620_000_000.0,
            "annual_interest_rate": 23.5,
            "monthly_payment_total": 45_000_000.0,
            "monthly_principal": 35_000_000.0,
            "monthly_interest": 10_000_000.0,
            "start_date": "2024-09-15",
            "maturity_date": "2027-09-15",
            "collateral_description": "Muzlatkichli ombor binosi va kadastr ijara huquqi"
        }
    ],
    "monthly_debt_service": [45_000_000.0] * 12,
    "monthly_inflows": [
        {"CROP_SALES": 120_000_000.0, "EXPORT_PROCEEDS": 0.0},                   # Jan (Winter stored grapes)
        {"CROP_SALES": 90_000_000.0, "EXPORT_PROCEEDS": 0.0},                    # Feb (Winter stored grapes)
        {"CROP_SALES": 40_000_000.0, "EXPORT_PROCEEDS": 0.0},                    # Mar
        {"CROP_SALES": 0.0, "EXPORT_PROCEEDS": 0.0},                             # Apr
        {"CROP_SALES": 180_000_000.0, "EXPORT_PROCEEDS": 250_000_000.0},         # May (Early sweet cherry export)
        {"CROP_SALES": 220_000_000.0, "EXPORT_PROCEEDS": 780_000_000.0},         # Jun (Peak cherry export contracts)
        {"CROP_SALES": 150_000_000.0, "EXPORT_PROCEEDS": 310_000_000.0},         # Jul (Apricot & early grapes)
        {"CROP_SALES": 240_000_000.0, "EXPORT_PROCEEDS": 690_000_000.0},         # Aug (Table grapes - Husayni, Rizamat)
        {"CROP_SALES": 280_000_000.0, "EXPORT_PROCEEDS": 890_000_000.0},         # Sep (Peak grape export to CIS/Gulf)
        {"CROP_SALES": 190_000_000.0, "EXPORT_PROCEEDS": 420_000_000.0},         # Oct (Late grapes & cold chain loading)
        {"CROP_SALES": 90_000_000.0, "EXPORT_PROCEEDS": 0.0},                    # Nov
        {"CROP_SALES": 80_000_000.0, "EXPORT_PROCEEDS": 0.0}                     # Dec
    ],
    "monthly_outflows": [
        {"COLD_STORAGE_OPEX": 25_000_000.0, "LABOR_SALARIES": 35_000_000.0, "DEBT_SERVICE": 45_000_000.0, "UTILITIES_WATER_TAX": 8_000_000.0}, # Jan
        {"COLD_STORAGE_OPEX": 24_000_000.0, "LABOR_SALARIES": 35_000_000.0, "DEBT_SERVICE": 45_000_000.0, "UTILITIES_WATER_TAX": 8_000_000.0}, # Feb
        {"FERTILIZER_CHEMICALS": 65_000_000.0, "LABOR_SALARIES": 48_000_000.0, "DEBT_SERVICE": 45_000_000.0, "FUEL_LUBRICANTS": 22_000_000.0}, # Mar
        {"FERTILIZER_CHEMICALS": 75_000_000.0, "LABOR_SALARIES": 55_000_000.0, "DEBT_SERVICE": 45_000_000.0, "FUEL_LUBRICANTS": 26_000_000.0}, # Apr
        {"LABOR_SALARIES": 120_000_000.0, "FUEL_LUBRICANTS": 42_000_000.0, "DEBT_SERVICE": 45_000_000.0, "MISC_EXPENSES": 38_000_000.0}, # May (Packaging & sorting)
        {"LABOR_SALARIES": 180_000_000.0, "FUEL_LUBRICANTS": 65_000_000.0, "DEBT_SERVICE": 45_000_000.0, "MISC_EXPENSES": 95_000_000.0}, # Jun (Export packaging & logistics)
        {"COLD_STORAGE_OPEX": 30_000_000.0, "LABOR_SALARIES": 75_000_000.0, "DEBT_SERVICE": 45_000_000.0, "FUEL_LUBRICANTS": 35_000_000.0}, # Jul
        {"COLD_STORAGE_OPEX": 35_000_000.0, "LABOR_SALARIES": 160_000_000.0, "DEBT_SERVICE": 45_000_000.0, "MISC_EXPENSES": 85_000_000.0}, # Aug
        {"COLD_STORAGE_OPEX": 38_000_000.0, "LABOR_SALARIES": 195_000_000.0, "DEBT_SERVICE": 45_000_000.0, "MISC_EXPENSES": 110_000_000.0}, # Sep
        {"COLD_STORAGE_OPEX": 32_000_000.0, "LABOR_SALARIES": 110_000_000.0, "DEBT_SERVICE": 45_000_000.0, "TAXES_OTHER": 42_000_000.0}, # Oct
        {"COLD_STORAGE_OPEX": 28_000_000.0, "LABOR_SALARIES": 45_000_000.0, "DEBT_SERVICE": 45_000_000.0, "TAXES_OTHER": 25_000_000.0}, # Nov
        {"COLD_STORAGE_OPEX": 26_000_000.0, "LABOR_SALARIES": 40_000_000.0, "DEBT_SERVICE": 45_000_000.0, "TAXES_OTHER": 20_000_000.0}  # Dec
    ]
}

# -------------------------------------------------------------------------
# 3. AGRICULTURAL CLUSTER: 2,500 HA («Qashqadaryo Paxta-G'alla Klasteri»)
# Initial Balance: 1,850,000,000 UZS
# Monthly Debt Service: 280,000,000 UZS (Integrated Agrobank Syndicate Loan)
# -------------------------------------------------------------------------
CLUSTER_DATA = {
    "organization": {
        "id": "scenario-cluster",
        "name": "«Qashqadaryo Paxta-G'alla Klasteri» (Sintetik Demo)",
        "inn": "301994821",
        "legal_type": "AGRO_KLASTER",
        "region": "Qashqadaryo viloyati",
        "district": "Qarshi tumani",
        "land_hectares": 2500.0,
        "cadastre_number": "19:08:020101:0012",
        "soil_bonitet_score": 71,
        "main_crop_type": "Paxta va Bug'doy Klasteri",
        "has_drip_irrigation": True,
        "has_cold_storage": False,
        "cold_storage_capacity_tons": 0.0
    },
    "initial_opening_balance": 1_850_000_000.0,
    "debt_schedule": [
        {
            "lender_name": "ATB «Agrobank» Bosh Ofisi (Sindikat kredit)",
            "loan_type": "PREFERENTIAL_STATE_AGRO",
            "contract_number": "KLS-2024/05-001",
            "principal_amount": 5_500_000_000.0,
            "outstanding_balance": 3_900_000_000.0,
            "annual_interest_rate": 14.0,
            "monthly_payment_total": 280_000_000.0,
            "monthly_principal": 235_000_000.0,
            "monthly_interest": 45_000_000.0,
            "start_date": "2024-05-01",
            "maturity_date": "2028-04-30",
            "collateral_description": "Klaster paxtani qayta ishlash zavodi va 2 500 ga yer ijara huquqi"
        }
    ],
    "monthly_debt_service": [280_000_000.0] * 12,
    "monthly_inflows": [
        {"CROP_SALES": 450_000_000.0, "STATE_SUBSIDY": 0.0},                      # Jan (Textile/lint settlements)
        {"CROP_SALES": 380_000_000.0, "STATE_SUBSIDY": 0.0},                      # Feb
        {"CROP_SALES": 200_000_000.0, "STATE_SUBSIDY": 350_000_000.0},            # Mar (PQ-47 Drip irrigation grant)
        {"CROP_SALES": 150_000_000.0, "STATE_SUBSIDY": 0.0},                      # Apr
        {"CROP_SALES": 100_000_000.0, "STATE_SUBSIDY": 0.0},                      # May
        {"CROP_SALES": 3_800_000_000.0, "STATE_SUBSIDY": 0.0},                    # Jun (G'alla / Wheat harvest sales)
        {"CROP_SALES": 4_200_000_000.0, "STATE_SUBSIDY": 0.0},                    # Jul (Final wheat procurement)
        {"CROP_SALES": 850_000_000.0, "STATE_SUBSIDY": 0.0},                      # Aug
        {"CROP_SALES": 2_100_000_000.0, "STATE_SUBSIDY": 0.0},                    # Sep (Early cotton ginning)
        {"CROP_SALES": 6_900_000_000.0, "STATE_SUBSIDY": 0.0},                    # Oct (Main raw cotton procurement)
        {"CROP_SALES": 5_400_000_000.0, "STATE_SUBSIDY": 0.0},                    # Nov (Cotton lint & textile revenue)
        {"CROP_SALES": 2_800_000_000.0, "STATE_SUBSIDY": 0.0}                     # Dec (Year-end textile contracts)
    ],
    "monthly_outflows": [
        {"MACHINERY_LEASING": 120_000_000.0, "LABOR_SALARIES": 240_000_000.0, "DEBT_SERVICE": 280_000_000.0, "FUEL_LUBRICANTS": 80_000_000.0}, # Jan
        {"MACHINERY_LEASING": 120_000_000.0, "LABOR_SALARIES": 240_000_000.0, "DEBT_SERVICE": 280_000_000.0, "FUEL_LUBRICANTS": 140_000_000.0}, # Feb
        {"SEEDS_PLANTING": 580_000_000.0, "FERTILIZER_CHEMICALS": 720_000_000.0, "FUEL_LUBRICANTS": 360_000_000.0, "LABOR_SALARIES": 380_000_000.0, "DEBT_SERVICE": 280_000_000.0}, # Mar
        {"FERTILIZER_CHEMICALS": 680_000_000.0, "FUEL_LUBRICANTS": 410_000_000.0, "LABOR_SALARIES": 420_000_000.0, "DEBT_SERVICE": 280_000_000.0, "UTILITIES_WATER_TAX": 60_000_000.0}, # Apr
        {"FERTILIZER_CHEMICALS": 550_000_000.0, "FUEL_LUBRICANTS": 380_000_000.0, "LABOR_SALARIES": 450_000_000.0, "DEBT_SERVICE": 280_000_000.0, "UTILITIES_WATER_TAX": 80_000_000.0}, # May
        {"FUEL_LUBRICANTS": 520_000_000.0, "LABOR_SALARIES": 680_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 180_000_000.0, "MACHINERY_LEASING": 120_000_000.0}, # Jun (Harvest)
        {"FUEL_LUBRICANTS": 490_000_000.0, "LABOR_SALARIES": 710_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 240_000_000.0, "MACHINERY_LEASING": 120_000_000.0}, # Jul
        {"FUEL_LUBRICANTS": 310_000_000.0, "LABOR_SALARIES": 380_000_000.0, "DEBT_SERVICE": 280_000_000.0, "FERTILIZER_CHEMICALS": 420_000_000.0}, # Aug
        {"FUEL_LUBRICANTS": 620_000_000.0, "LABOR_SALARIES": 1_250_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 150_000_000.0}, # Sep
        {"FUEL_LUBRICANTS": 780_000_000.0, "LABOR_SALARIES": 1_850_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 380_000_000.0}, # Oct
        {"FUEL_LUBRICANTS": 450_000_000.0, "LABOR_SALARIES": 1_120_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 290_000_000.0}, # Nov
        {"FUEL_LUBRICANTS": 160_000_000.0, "LABOR_SALARIES": 420_000_000.0, "DEBT_SERVICE": 280_000_000.0, "TAXES_OTHER": 210_000_000.0, "MISC_EXPENSES": 150_000_000.0} # Dec
    ]
}

SCENARIOS_MAP: Dict[str, Dict[str, Any]] = {
    "scenario-small-farmer": SMALL_FARMER_DATA,
    "scenario-exporter": EXPORTER_DATA,
    "scenario-cluster": CLUSTER_DATA
}

def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    if scenario_id in SCENARIOS_MAP:
        return SCENARIOS_MAP[scenario_id]
    # Key-based lookup fallback
    for k, v in SCENARIOS_MAP.items():
        if v["organization"]["id"] == scenario_id or k.endswith(scenario_id):
            return v
    raise KeyError(f"Scenario with ID '{scenario_id}' not found.")

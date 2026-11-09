"""
AgroHisob CFO - Classification Knowledge Base & Dictionaries
Houses MXIK (IKPU) prefix dictionaries, multi-lingual keyword patterns, and counterparty heuristics.
"""

from typing import Dict, List, Tuple
from app.import_engine.schemas import AgroFinancialCategory


# Category human-readable names in Uzbek (Latin)
CATEGORY_NAMES_UZ: Dict[AgroFinancialCategory, str] = {
    AgroFinancialCategory.CROP_SALES_GRAIN: "G'alla va don mahsulotlari sotuvi",
    AgroFinancialCategory.CROP_SALES_COTTON: "Paxta xomashyosi sotuvi (Klaster)",
    AgroFinancialCategory.CROP_SALES_HORTICULTURE: "Bog'dorchilik va sabzavotlar sotuvi",
    AgroFinancialCategory.FERTILIZER_CHEMICALS: "Mineral o'g'itlar va agroximiya",
    AgroFinancialCategory.FUEL_LUBRICANTS: "Yoqilg'i va moylash materiallari (Dizel/GSM)",
    AgroFinancialCategory.SEEDS_SEEDLINGS: "Urug'lik va ko'chatlar",
    AgroFinancialCategory.MACHINERY_SERVICES: "Texnika ijarasi va mexanizatsiya xizmatlari",
    AgroFinancialCategory.LABOR_PAYROLL: "Ish haqi va mavsumiy terimchilar xarajatlari",
    AgroFinancialCategory.IRRIGATION_WATER: "Sug'orish suvi va melioratsiya to'lovlari",
    AgroFinancialCategory.LAND_LEASE: "Yer ijarasi va kadastr to'lovlari",
    AgroFinancialCategory.INSURANCE_AGRO: "Qishloq xo'jaligi hosil va mulk sug'urtasi",
    AgroFinancialCategory.TAXES_DUTIES: "Yagona yer solig'i va majburiy to'lovlar",
    AgroFinancialCategory.DEBT_SERVICE: "Bank krediti qaytarish va foiz xarajatlari",
    AgroFinancialCategory.SUBSIDY_GRANTS: "Davlat subsidiyalari va imtiyozli grantlar",
    AgroFinancialCategory.OTHER_OPERATING_EXPENSES: "Boshqa operatsion agroxarajatlar",
    AgroFinancialCategory.OTHER_OPERATING_INCOME: "Boshqa operatsion tushumlar",
    AgroFinancialCategory.UNCATEGORIZED_EXPENSE: "Tasniflanmagan xarajat (tekshirish talab)",
    AgroFinancialCategory.UNCATEGORIZED_INCOME: "Tasniflanmagan kirim (tekshirish talab)",
}


# Tier 1: MXIK (IKPU) code prefixes mapped to category
MXIK_PREFIX_MAP: Dict[str, Tuple[AgroFinancialCategory, float]] = {
    # Crop Sales - Grain
    "01.11": (AgroFinancialCategory.CROP_SALES_GRAIN, 0.98),
    "0111": (AgroFinancialCategory.CROP_SALES_GRAIN, 0.98),
    
    # Crop Sales - Cotton
    "01.16": (AgroFinancialCategory.CROP_SALES_COTTON, 0.98),
    "0116": (AgroFinancialCategory.CROP_SALES_COTTON, 0.98),

    # Crop Sales - Horticulture / Fruits / Vegetables
    "01.13": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "0113": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "01.21": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "0121": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "01.24": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "0124": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "01.25": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),
    "0125": (AgroFinancialCategory.CROP_SALES_HORTICULTURE, 0.95),

    # Seeds & Seedlings
    "01.64": (AgroFinancialCategory.SEEDS_SEEDLINGS, 0.95),
    "0164": (AgroFinancialCategory.SEEDS_SEEDLINGS, 0.95),

    # Fertilizers & Agrochemistry
    "20.15": (AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.98),
    "2015": (AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.98),
    "20.20": (AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    "2020": (AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),

    # Fuel & Lubricants
    "19.20": (AgroFinancialCategory.FUEL_LUBRICANTS, 0.98),
    "1920": (AgroFinancialCategory.FUEL_LUBRICANTS, 0.98),

    # Machinery & Agrotechnical Services
    "01.61": (AgroFinancialCategory.MACHINERY_SERVICES, 0.95),
    "0161": (AgroFinancialCategory.MACHINERY_SERVICES, 0.95),
    "68.20": (AgroFinancialCategory.MACHINERY_SERVICES, 0.90),
    "6820": (AgroFinancialCategory.MACHINERY_SERVICES, 0.90),
    "77.31": (AgroFinancialCategory.MACHINERY_SERVICES, 0.95),
    "7731": (AgroFinancialCategory.MACHINERY_SERVICES, 0.95),

    # Irrigation & Water
    "36.00": (AgroFinancialCategory.IRRIGATION_WATER, 0.95),
    "3600": (AgroFinancialCategory.IRRIGATION_WATER, 0.95),

    # Agricultural Insurance
    "65.12": (AgroFinancialCategory.INSURANCE_AGRO, 0.95),
    "6512": (AgroFinancialCategory.INSURANCE_AGRO, 0.95),

    # Taxes & Mandatory State Payments
    "84.11": (AgroFinancialCategory.TAXES_DUTIES, 0.95),
    "8411": (AgroFinancialCategory.TAXES_DUTIES, 0.95),

    # Banking & Debt Service
    "64.19": (AgroFinancialCategory.DEBT_SERVICE, 0.95),
    "6419": (AgroFinancialCategory.DEBT_SERVICE, 0.95),
}


# Tier 2: Keyword Heuristics
KEYWORD_RULES: List[Tuple[AgroFinancialCategory, List[str], float]] = [
    (
        AgroFinancialCategory.FERTILIZER_CHEMICALS,
        [
            "o'g'it", "ogit", "o‘g‘it", "удобрение", "azot", "азот", "ammofos", "аммофос",
            "karbamid", "карбамид", "selitra", "селитра", "фосфор", "kaliy", "калий",
            "gerbitsid", "гербицид", "pestitsid", "пестицид", "defoliant", "дефолиант",
            "ximikat", "химикат", "kimyoviy", "mineral o'g'it", "минеральные удобрения"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.FUEL_LUBRICANTS,
        [
            "yoqilg'i", "yoqilgi", "yoqilg‘i", "dizel", "дизель", "solyarka", "солярка",
            "benzin", "бензин", "gsm", "гсм", "moy", "автол", "avtol", "yoqilg'i-moylash",
            "топливо", "дизтопливо", "oil", "petrol", "yoqilg'i quyish"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.SEEDS_SEEDLINGS,
        [
            "urug'", "urug", "urug‘", "семена", "chigit", "чигит", "urug'lik", "ko'chat",
            "kochet", "саженцы", "don urug'i", "elita urug'", "gibrid urug'"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.MACHINERY_SERVICES,
        [
            "traktor", "трактор", "kombayn", "комбайн", "haydash", "yer haydash",
            "kultivatsiya", "культивация", "plug", "плуг", "zapchast", "запчасть",
            "ehtiyot qism", "mtp", "мтп", "remont", "remont xizmati", "agrotexnik xizmat",
            "texnika ijarasi", "mexanizatsiya"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.LABOR_PAYROLL,
        [
            "ish haqi", "oylik", "zarplata", "зарплата", "maosh", "mehnat haqi",
            "terim puli", "paxta terimi", "avans ishchi", "ishchilar", "fzp", "фзп"
        ],
        0.92
    ),
    (
        AgroFinancialCategory.IRRIGATION_WATER,
        [
            "suv", "nasos", "вода", "irrigatsiya", "ирригация", "suv xo'jaligi",
            "suv yetkazib berish", "ariq", "kanal", "nasos stansiyasi", "suv solig'i"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.LAND_LEASE,
        [
            "ijara", "kadastr", "yer ijarasi", "аренда земли", "кадастр", "yer fondi"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.TAXES_DUTIES,
        [
            "soliq", "налог", "yagona yer solig'i", "yer solig'i", "ndfl", "ндфл",
            "daromad solig'i", "davlat boji", "penya soliq", "soliq boshqarmasi"
        ],
        0.92
    ),
    (
        AgroFinancialCategory.DEBT_SERVICE,
        [
            "kredit", "кредит", "kredit foizi", "foiz to'lovi", "ssuda", "ссуда",
            "asosiy qarz", "bank komissiyasi", "kredit so'ndirish", "protsent"
        ],
        0.92
    ),
    (
        AgroFinancialCategory.SUBSIDY_GRANTS,
        [
            "subsidiya", "субсидия", "davlat granti", "grant", "kompensatsiya",
            "tomchilatib sug'orish subsidiyasi", "subsidiyalar"
        ],
        0.92
    ),
    (
        AgroFinancialCategory.CROP_SALES_GRAIN,
        [
            "bug'doy", "g'alla", "don", "arpa", "пшеница", "зерно", "bug'doy tushumi",
            "don qabul", "hosil sotish don", "g'alla sotuvi"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.CROP_SALES_COTTON,
        [
            "paxta", "хлопок", "paxta xomashyosi", "klasterga paxta", "paxta tushumi",
            "chigit sotuvi", "paxta tolasi", "xomashyo tushumi"
        ],
        0.90
    ),
    (
        AgroFinancialCategory.CROP_SALES_HORTICULTURE,
        [
            "sabzavot", "meva", "pomidor", "bodring", "olma", "uzum", "kartoshka",
            "piyoz", "tarvuz", "qovun", "овощи", "фрукты", "bog'dorchilik", "issiqxona"
        ],
        0.90
    )
]


# Tier 3: Counterparty known entity mapping
COUNTERPARTY_RULES: List[Tuple[str, AgroFinancialCategory, float]] = [
    ("farg'onaazot", AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    ("navoiyazot", AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    ("maxam-chirchiq", AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    ("dehqonobod", AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    ("agrokimyo", AgroFinancialCategory.FERTILIZER_CHEMICALS, 0.95),
    ("o'zbekneftgaz", AgroFinancialCategory.FUEL_LUBRICANTS, 0.95),
    ("uzbekneftegaz", AgroFinancialCategory.FUEL_LUBRICANTS, 0.95),
    ("ung petro", AgroFinancialCategory.FUEL_LUBRICANTS, 0.95),
    ("neftebaza", AgroFinancialCategory.FUEL_LUBRICANTS, 0.95),
    ("lukoil", AgroFinancialCategory.FUEL_LUBRICANTS, 0.95),
    ("agrobank", AgroFinancialCategory.DEBT_SERVICE, 0.90),
    ("qishloq qurilish bank", AgroFinancialCategory.DEBT_SERVICE, 0.90),
    ("biznesni rivojlantirish", AgroFinancialCategory.DEBT_SERVICE, 0.90),
    ("mikrokreditbank", AgroFinancialCategory.DEBT_SERVICE, 0.90),
    ("ipak yo'li", AgroFinancialCategory.DEBT_SERVICE, 0.85),
    ("suv ta'minot", AgroFinancialCategory.IRRIGATION_WATER, 0.92),
    ("suv xo'jaligi", AgroFinancialCategory.IRRIGATION_WATER, 0.92),
]

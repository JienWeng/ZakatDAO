# Zakat types configuration
ZAKAT_TYPES = [
    {"id": 1, "name": "Zakat Pendapatan", "description": "Income Zakat"},
    {"id": 2, "name": "Zakat Perniagaan", "description": "Business Zakat"},
    {"id": 3, "name": "Zakat Simpanan", "description": "Savings Zakat"},
]

ZAKAT_TYPES_BY_ID = {t["id"]: t for t in ZAKAT_TYPES}

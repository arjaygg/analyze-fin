"""
Category taxonomy and Philippine merchant mappings.

Contains:
- CATEGORIES: Category definitions with descriptions and keywords
- MERCHANT_MAPPING: 100+ pre-mapped Philippine merchants
- get_category(): Look up category for a merchant
- get_normalized_name(): Get proper-cased merchant name
"""

# Category definitions with descriptions and keywords
CATEGORIES: dict[str, dict] = {
    "Food & Dining": {
        "description": "Restaurants, fast food, cafes, food delivery",
        "keywords": ["food", "restaurant", "cafe", "dining", "eat", "meal"],
    },
    "Shopping": {
        "description": "Online shopping, retail, e-commerce",
        "keywords": ["shop", "store", "mall", "retail", "buy", "purchase"],
    },
    "Transportation": {
        "description": "Ride-hailing, taxi, fuel, parking, public transit",
        "keywords": ["grab", "taxi", "fuel", "gas", "parking", "transport"],
    },
    "Bills & Utilities": {
        "description": "Electricity, water, internet, phone bills",
        "keywords": ["bill", "electric", "water", "internet", "phone", "utility"],
    },
    "Entertainment": {
        "description": "Movies, streaming, games, events",
        "keywords": ["movie", "cinema", "netflix", "spotify", "game", "concert"],
    },
    "Health & Wellness": {
        "description": "Pharmacies, clinics, hospitals, fitness",
        "keywords": ["pharmacy", "hospital", "clinic", "doctor", "gym", "fitness"],
    },
    "Personal Care": {
        "description": "Salon, spa, beauty products",
        "keywords": ["salon", "spa", "beauty", "hair", "nail", "skincare"],
    },
    "Education": {
        "description": "Tuition, books, courses, training",
        "keywords": ["school", "university", "course", "tuition", "book", "education"],
    },
    "Travel": {
        "description": "Airlines, hotels, vacation bookings",
        "keywords": ["airline", "hotel", "travel", "flight", "vacation", "booking"],
    },
    "Groceries": {
        "description": "Supermarkets, grocery stores, wet markets",
        "keywords": ["grocery", "supermarket", "market", "puregold", "robinsons"],
    },
    "Financial Services": {
        "description": "Bank fees, insurance, investments",
        "keywords": ["bank", "insurance", "invest", "fee", "charge", "interest"],
    },
    "Government": {
        "description": "SSS, PhilHealth, Pag-IBIG, taxes, permits",
        "keywords": ["sss", "philhealth", "pagibig", "bir", "tax", "government"],
    },
    "Transfers": {
        "description": "Money transfers between accounts",
        "keywords": ["transfer", "send", "receive", "remit"],
    },
    "Cash": {
        "description": "ATM withdrawals, cash in/out",
        "keywords": ["atm", "cash", "withdraw", "deposit"],
    },
    "Uncategorized": {
        "description": "Transactions pending categorization",
        "keywords": [],
    },
}

# Pre-mapped Philippine merchants
# Keys are UPPERCASE for case-insensitive matching
MERCHANT_MAPPING: dict[str, dict] = {
    # Food & Dining - Fast Food
    "JOLLIBEE": {"normalized": "Jollibee", "category": "Food & Dining"},
    "MCDONALDS": {"normalized": "McDonald's", "category": "Food & Dining"},
    "MCDONALD'S": {"normalized": "McDonald's", "category": "Food & Dining"},
    "MCDO": {"normalized": "McDonald's", "category": "Food & Dining"},
    "KFC": {"normalized": "KFC", "category": "Food & Dining"},
    "CHOWKING": {"normalized": "Chowking", "category": "Food & Dining"},
    "GREENWICH": {"normalized": "Greenwich", "category": "Food & Dining"},
    "MANG INASAL": {"normalized": "Mang Inasal", "category": "Food & Dining"},
    "BONCHON": {"normalized": "Bonchon", "category": "Food & Dining"},
    "WENDY'S": {"normalized": "Wendy's", "category": "Food & Dining"},
    "WENDYS": {"normalized": "Wendy's", "category": "Food & Dining"},
    "BURGER KING": {"normalized": "Burger King", "category": "Food & Dining"},
    "SUBWAY": {"normalized": "Subway", "category": "Food & Dining"},
    "ARMY NAVY": {"normalized": "Army Navy", "category": "Food & Dining"},
    "POTATO CORNER": {"normalized": "Potato Corner", "category": "Food & Dining"},
    "MINISTOP": {"normalized": "Ministop", "category": "Food & Dining"},

    # Food & Dining - Coffee
    "STARBUCKS": {"normalized": "Starbucks", "category": "Food & Dining"},
    "COFFEE BEAN": {"normalized": "Coffee Bean", "category": "Food & Dining"},
    "TIM HORTONS": {"normalized": "Tim Hortons", "category": "Food & Dining"},
    "DUNKIN": {"normalized": "Dunkin'", "category": "Food & Dining"},
    "DUNKIN DONUTS": {"normalized": "Dunkin'", "category": "Food & Dining"},
    "GONG CHA": {"normalized": "Gong Cha", "category": "Food & Dining"},
    "COCO": {"normalized": "CoCo", "category": "Food & Dining"},
    "TIGER SUGAR": {"normalized": "Tiger Sugar", "category": "Food & Dining"},

    # Food & Dining - Delivery
    "GRABFOOD": {"normalized": "GrabFood", "category": "Food & Dining"},
    "GRAB FOOD": {"normalized": "GrabFood", "category": "Food & Dining"},
    "FOODPANDA": {"normalized": "FoodPanda", "category": "Food & Dining"},
    "FOOD PANDA": {"normalized": "FoodPanda", "category": "Food & Dining"},

    # Food & Dining - Restaurants
    "YELLOW CAB": {"normalized": "Yellow Cab", "category": "Food & Dining"},
    "SHAKEYS": {"normalized": "Shakey's", "category": "Food & Dining"},
    "SHAKEY'S": {"normalized": "Shakey's", "category": "Food & Dining"},
    "PIZZA HUT": {"normalized": "Pizza Hut", "category": "Food & Dining"},
    "MAX'S": {"normalized": "Max's", "category": "Food & Dining"},
    "MAXS": {"normalized": "Max's", "category": "Food & Dining"},
    "ARISTOCRAT": {"normalized": "Aristocrat", "category": "Food & Dining"},
    "GOLDILOCKS": {"normalized": "Goldilocks", "category": "Food & Dining"},
    "RED RIBBON": {"normalized": "Red Ribbon", "category": "Food & Dining"},
    "KRISPY KREME": {"normalized": "Krispy Kreme", "category": "Food & Dining"},

    # Convenience Stores
    "7-ELEVEN": {"normalized": "7-Eleven", "category": "Food & Dining"},
    "7 ELEVEN": {"normalized": "7-Eleven", "category": "Food & Dining"},
    "FAMILY MART": {"normalized": "Family Mart", "category": "Food & Dining"},
    "FAMILYMART": {"normalized": "Family Mart", "category": "Food & Dining"},
    "ALFAMART": {"normalized": "Alfamart", "category": "Food & Dining"},

    # Shopping - Online
    "LAZADA": {"normalized": "Lazada", "category": "Shopping"},
    "SHOPEE": {"normalized": "Shopee", "category": "Shopping"},
    "ZALORA": {"normalized": "Zalora", "category": "Shopping"},
    "SHEIN": {"normalized": "Shein", "category": "Shopping"},
    "TEMU": {"normalized": "Temu", "category": "Shopping"},

    # Shopping - Malls/Department Stores
    "SM": {"normalized": "SM", "category": "Shopping"},
    "SM STORE": {"normalized": "SM Store", "category": "Shopping"},
    "SM DEPARTMENT": {"normalized": "SM Department Store", "category": "Shopping"},
    "ROBINSONS": {"normalized": "Robinsons", "category": "Shopping"},
    "ROBINSONS DEPARTMENT": {"normalized": "Robinsons Department Store", "category": "Shopping"},
    "LANDMARK": {"normalized": "Landmark", "category": "Shopping"},
    "RUSTANS": {"normalized": "Rustan's", "category": "Shopping"},
    "RUSTAN'S": {"normalized": "Rustan's", "category": "Shopping"},
    "UNIQLO": {"normalized": "Uniqlo", "category": "Shopping"},
    "H&M": {"normalized": "H&M", "category": "Shopping"},
    "ZARA": {"normalized": "Zara", "category": "Shopping"},
    "PENSHOPPE": {"normalized": "Penshoppe", "category": "Shopping"},
    "BENCH": {"normalized": "Bench", "category": "Shopping"},
    "NATIONAL BOOKSTORE": {"normalized": "National Bookstore", "category": "Shopping"},

    # Transportation
    "GRAB": {"normalized": "Grab", "category": "Transportation"},
    "GRAB RIDE": {"normalized": "Grab", "category": "Transportation"},
    "GRABCAR": {"normalized": "GrabCar", "category": "Transportation"},
    "ANGKAS": {"normalized": "Angkas", "category": "Transportation"},
    "JOYRIDE": {"normalized": "JoyRide", "category": "Transportation"},
    "MOVE IT": {"normalized": "Move It", "category": "Transportation"},
    "SHELL": {"normalized": "Shell", "category": "Transportation"},
    "PETRON": {"normalized": "Petron", "category": "Transportation"},
    "CALTEX": {"normalized": "Caltex", "category": "Transportation"},
    "PHOENIX": {"normalized": "Phoenix", "category": "Transportation"},
    "SEAOIL": {"normalized": "Seaoil", "category": "Transportation"},
    "LTO": {"normalized": "LTO", "category": "Transportation"},
    "LTFRB": {"normalized": "LTFRB", "category": "Transportation"},
    "AUTOSWEEP": {"normalized": "Autosweep", "category": "Transportation"},
    "EASYTRIP": {"normalized": "Easytrip", "category": "Transportation"},
    "BEEP": {"normalized": "Beep Card", "category": "Transportation"},

    # Bills & Utilities
    "MERALCO": {"normalized": "Meralco", "category": "Bills & Utilities"},
    "MANILA WATER": {"normalized": "Manila Water", "category": "Bills & Utilities"},
    "MAYNILAD": {"normalized": "Maynilad", "category": "Bills & Utilities"},
    "PLDT": {"normalized": "PLDT", "category": "Bills & Utilities"},
    "GLOBE": {"normalized": "Globe", "category": "Bills & Utilities"},
    "GLOBE TELECOM": {"normalized": "Globe Telecom", "category": "Bills & Utilities"},
    "SMART": {"normalized": "Smart", "category": "Bills & Utilities"},
    "SMART COMMUNICATIONS": {"normalized": "Smart Communications", "category": "Bills & Utilities"},
    "CONVERGE": {"normalized": "Converge", "category": "Bills & Utilities"},
    "DITO": {"normalized": "DITO", "category": "Bills & Utilities"},
    "SKY CABLE": {"normalized": "Sky Cable", "category": "Bills & Utilities"},
    "CIGNAL": {"normalized": "Cignal", "category": "Bills & Utilities"},

    # Entertainment
    "NETFLIX": {"normalized": "Netflix", "category": "Entertainment"},
    "SPOTIFY": {"normalized": "Spotify", "category": "Entertainment"},
    "YOUTUBE": {"normalized": "YouTube Premium", "category": "Entertainment"},
    "DISNEY": {"normalized": "Disney+", "category": "Entertainment"},
    "HBO": {"normalized": "HBO Go", "category": "Entertainment"},
    "VIVO": {"normalized": "VivaMax", "category": "Entertainment"},
    "VIVAMAX": {"normalized": "VivaMax", "category": "Entertainment"},
    "SM CINEMA": {"normalized": "SM Cinema", "category": "Entertainment"},
    "AYALA CINEMA": {"normalized": "Ayala Cinemas", "category": "Entertainment"},
    "IMAX": {"normalized": "IMAX", "category": "Entertainment"},

    # Health & Wellness
    "MERCURY DRUG": {"normalized": "Mercury Drug", "category": "Health & Wellness"},
    "WATSONS": {"normalized": "Watsons", "category": "Health & Wellness"},
    "SOUTHSTAR DRUG": {"normalized": "Southstar Drug", "category": "Health & Wellness"},
    "ROSE PHARMACY": {"normalized": "Rose Pharmacy", "category": "Health & Wellness"},
    "GENERIKA": {"normalized": "Generika", "category": "Health & Wellness"},
    "ANYTIME FITNESS": {"normalized": "Anytime Fitness", "category": "Health & Wellness"},
    "GOLD'S GYM": {"normalized": "Gold's Gym", "category": "Health & Wellness"},
    "FITNESS FIRST": {"normalized": "Fitness First", "category": "Health & Wellness"},

    # Groceries
    "PUREGOLD": {"normalized": "Puregold", "category": "Groceries"},
    "WALTER MART": {"normalized": "Walter Mart", "category": "Groceries"},
    "WALTERMART": {"normalized": "Walter Mart", "category": "Groceries"},
    "METRO": {"normalized": "Metro", "category": "Groceries"},
    "SAVEMORE": {"normalized": "Savemore", "category": "Groceries"},
    "S&R": {"normalized": "S&R", "category": "Groceries"},
    "SNR": {"normalized": "S&R", "category": "Groceries"},
    "LANDERS": {"normalized": "Landers", "category": "Groceries"},
    "ROBINSONS SUPERMARKET": {"normalized": "Robinsons Supermarket", "category": "Groceries"},
    "SM SUPERMARKET": {"normalized": "SM Supermarket", "category": "Groceries"},

    # Government
    "SSS": {"normalized": "SSS", "category": "Government"},
    "PHILHEALTH": {"normalized": "PhilHealth", "category": "Government"},
    "PAGIBIG": {"normalized": "Pag-IBIG", "category": "Government"},
    "PAG-IBIG": {"normalized": "Pag-IBIG", "category": "Government"},
    "BIR": {"normalized": "BIR", "category": "Government"},
    "NBI": {"normalized": "NBI", "category": "Government"},
    "DFA": {"normalized": "DFA", "category": "Government"},
    "PSA": {"normalized": "PSA", "category": "Government"},

    # Financial Services
    "BPI": {"normalized": "BPI", "category": "Financial Services"},
    "BDO": {"normalized": "BDO", "category": "Financial Services"},
    "METROBANK": {"normalized": "Metrobank", "category": "Financial Services"},
    "LANDBANK": {"normalized": "Landbank", "category": "Financial Services"},
    "PNB": {"normalized": "PNB", "category": "Financial Services"},
    "GCASH": {"normalized": "GCash", "category": "Financial Services"},
    "MAYA": {"normalized": "Maya", "category": "Financial Services"},
    "PAYMAYA": {"normalized": "Maya", "category": "Financial Services"},
    "COINS.PH": {"normalized": "Coins.ph", "category": "Financial Services"},
    "COINSPH": {"normalized": "Coins.ph", "category": "Financial Services"},

    # Travel
    "CEBU PACIFIC": {"normalized": "Cebu Pacific", "category": "Travel"},
    "PHILIPPINE AIRLINES": {"normalized": "Philippine Airlines", "category": "Travel"},
    "PAL": {"normalized": "Philippine Airlines", "category": "Travel"},
    "AIRASIA": {"normalized": "AirAsia", "category": "Travel"},
    "AGODA": {"normalized": "Agoda", "category": "Travel"},
    "BOOKING.COM": {"normalized": "Booking.com", "category": "Travel"},
    "AIRBNB": {"normalized": "Airbnb", "category": "Travel"},

    # Cash
    "ATM": {"normalized": "ATM Withdrawal", "category": "Cash"},
    "ATM WITHDRAWAL": {"normalized": "ATM Withdrawal", "category": "Cash"},
    "CASH IN": {"normalized": "Cash In", "category": "Cash"},
    "CASH OUT": {"normalized": "Cash Out", "category": "Cash"},
}


def get_category(merchant_name: str) -> str | None:
    """Get category for a merchant name.

    Args:
        merchant_name: Raw merchant name from transaction

    Returns:
        Category name or None if not found
    """
    normalized_key = merchant_name.upper().strip()

    # Direct lookup
    if normalized_key in MERCHANT_MAPPING:
        return MERCHANT_MAPPING[normalized_key]["category"]

    # Partial match - check if merchant contains any known merchant name
    for key in MERCHANT_MAPPING:
        if key in normalized_key or normalized_key in key:
            return MERCHANT_MAPPING[key]["category"]

    return None


def get_normalized_name(merchant_name: str) -> str | None:
    """Get properly-cased merchant name.

    Args:
        merchant_name: Raw merchant name from transaction

    Returns:
        Normalized/proper-cased name or None if not found
    """
    normalized_key = merchant_name.upper().strip()

    # Direct lookup
    if normalized_key in MERCHANT_MAPPING:
        return MERCHANT_MAPPING[normalized_key]["normalized"]

    # Partial match
    for key in MERCHANT_MAPPING:
        if key in normalized_key or normalized_key in key:
            return MERCHANT_MAPPING[key]["normalized"]

    return None

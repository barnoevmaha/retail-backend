"""Predefined category -> size systems.

Single source of truth for which sizes a given category should offer.
Extend by adding a new system to SIZE_SYSTEMS and a keyword rule to SYSTEMS_BY_KEYWORD.
"""

SIZE_SYSTEMS = {
    "apparel": ["XS", "S", "M", "L", "XL", "XXL"],
    "trousers": ["28", "30", "32", "34", "36", "38", "40", "42"],
    "shoes": ["39", "40", "41", "42", "43", "44", "45"],
    "accessories": ["One Size"],
}

# category keyword -> size system name (first match wins)
SYSTEMS_BY_KEYWORD = [
    ("shirt", "apparel"),
    ("t-shirt", "apparel"),
    ("tshirt", "apparel"),
    ("tee", "apparel"),
    ("sweatshirt", "apparel"),
    ("sweat", "apparel"),
    ("hoodie", "apparel"),
    ("hoody", "apparel"),
    ("jacket", "apparel"),
    ("coat", "apparel"),
    ("blazer", "apparel"),
    ("top", "apparel"),
    ("polo", "apparel"),
    ("trousers", "trousers"),
    ("trouser", "trousers"),
    ("jeans", "trousers"),
    ("jean", "trousers"),
    ("pants", "trousers"),
    ("pant", "trousers"),
    ("shoes", "shoes"),
    ("shoe", "shoes"),
    ("sneaker", "shoes"),
    ("sneakers", "shoes"),
    ("boots", "shoes"),
    ("boot", "shoes"),
    ("sandals", "shoes"),
    ("sandal", "shoes"),
    ("loafers", "shoes"),
    ("loafer", "shoes"),
    ("caps", "accessories"),
    ("cap", "accessories"),
    ("hat", "accessories"),
    ("hats", "accessories"),
    ("belt", "accessories"),
    ("accessories", "accessories"),
    ("accessory", "accessories"),
]


def system_for_category(name: str | None, slug: str | None = None) -> str | None:
    haystack = " ".join([s.lower() for s in [name, slug] if s])
    for keyword, system in SYSTEMS_BY_KEYWORD:
        if keyword in haystack:
            return system
    return None


def sizes_for_system(system: str | None) -> list[str]:
    return list(SIZE_SYSTEMS.get(system or "", []))
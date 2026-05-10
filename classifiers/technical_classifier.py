"""
Technical classifier for gelato ingredients.
Maps Leagel commercial categories → unified technical categories.
Based on product behavior in the recipe (not brand naming).
"""

# ---------------------------------------------------------------
# Mapping: Leagel section heading → (technical_category_slug, physical_form_slug)
# ---------------------------------------------------------------
SECTION_MAP = {
    # --- BASE ---
    "basi latte":               ("base", "powder"),
    "basi frutta":              ("base", "powder"),
    "basi special":             ("base", "powder"),
    "gelato soft":              ("base", "powder"),
    "i love soia":              ("base", "powder"),
    "fruitube®":                ("base", "powder"),
    "kefir":                    ("base", "powder"),
    "gelato al cioccolato":     ("base", "powder"),

    # --- NEUTRO / ADDITIVO ---
    "neutri":                   ("neutral", "powder"),
    "integratori":              ("improver", "powder"),

    # --- PREPARATO COMPLETO (base + pasta already balanced) ---
    "zhero":                    ("complete_mix", "powder"),
    "easy crema":               ("complete_mix", "paste"),
    "easy frutta":              ("complete_mix", "powder"),
    "fruity & veggy":           ("complete_mix", "powder"),
    "& veggy":                  ("complete_mix", "powder"),  # split heading in markdown
    "fruity":                   ("complete_mix", "powder"),
    "vegg":                     ("complete_mix", "powder"),

    # --- PASTA ---
    "fruitcub3":                ("paste", "semi_solid"),
    "specialità e preparati aromatizzanti": ("flavoring", "liquid"),
    "linea gold":               ("paste", "paste"),   # mostly pastes; variegato visciola handled by name
    "paste crema":              ("paste", "paste"),
    "paste frutta":             ("paste", "paste"),
    "paste crema e frutta":     ("paste", "paste"),   # pastry section

    # --- VARIEGATURA ---
    "variegati crema":          ("variegate", "cream"),
    "loveria®":                 ("variegate", "cream"),
    "cremino gelato by loveria": ("variegate", "cream"),
    "variegati frutta":         ("variegate", "cream"),

    # --- COPERTURA ---
    "stickaway®":               ("coating", "liquid"),
    "pastrycover":              ("coating", "cream"),

    # --- INCLUSIONE ---
    "crumble":                  ("inclusion", "granular"),
    "granelle":                 ("inclusion", "granular"),

    # --- PASTICCERIA ---
    "cremosette®":              ("paste", "cream"),
    "stabilizzanti":            ("neutral", "powder"),
    "glasse a specchio":        ("glaze", "liquid"),

    # --- HO.RE.CA. ---
    "topping":                  ("topping", "liquid"),
    "sciroppi per granita":     ("syrup", "liquid"),
    "ristorazione":             ("complete_mix", "powder"),

    # --- PRONI SPECIFIC ---
    "polveri":                  ("complete_mix", "powder"),
    "speedy":                   ("complete_mix", "powder"),
    "cialde":                   ("inclusion", "granular"),

    # --- RUBICONE SPECIFIC ---
    "cremini":                  ("variegate", "cream"),
    "fitgelato":                ("complete_mix", "powder"),

    # --- SPECIAL ---
    "profumi per gelato":       ("flavoring", "spray"),
}

# ---------------------------------------------------------------
# Override by product name keyword (higher priority than section)
# ---------------------------------------------------------------
NAME_OVERRIDES = {
    "variegat": "variegate",
    "loveria":  "variegate",
    "topping":  "topping",
    "crumble":  "inclusion",
    "granella": "inclusion",
    "granelone": "inclusion",
    "stickaway": "coating",
    "glassa":   "glaze",
    "sciroppo": "syrup",
    "chutney":  "variegate",  # Chutney are fruit sauces used like variegature
    "copertura": "coating",   # "Copertura al Cioccolato" = coating product
    "stracciatella": "coating",
    "speedy":   "complete_mix",
    "salsa":    "variegate",
    "polpa":    "paste",
    "base":     "base",
    "pasta":    "paste",
    "cremino":  "variegate",
}

# ---------------------------------------------------------------
# Tags derived from section context
# ---------------------------------------------------------------
SECTION_TAGS = {
    "zhero":        ["sugar_free", "lactose_free", "gluten_free"],
    "i love soia":  ["lactose_free"],
    "kefir":        ["gluten_free"],
    "fruitube®":    ["gluten_free"],
    "fruity & veggy": ["vegan", "plant_based", "gluten_free"],
    "easy frutta":  ["gluten_free"],
    "loveria®":     [],
    "linea gold":   ["premium"],
}

# Tags derived from product name keywords
NAME_TAGS = {
    " dop":         "dop",
    " d.o.p":       "dop",
    " igp":         "igp",
    " i.g.p":       "igp",
    "vegan":        "vegan",
    "plant":        "plant_based",
    "protein":      "high_protein",
    "pistacchio":   "pistacchio",
    "nocciola":     "nocciola",
}

# ---------------------------------------------------------------
# Behavior defaults per technical category
# ---------------------------------------------------------------
BEHAVIOR_DEFAULTS = {
    "base": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": False,
        "structural_function": True,
        "texture_function": False,
        "contains_pieces": False,
    },
    "neutral": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": False,
        "structural_function": True,
        "texture_function": False,
        "contains_pieces": False,
    },
    "improver": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": False,
        "structural_function": True,
        "texture_function": True,
        "contains_pieces": False,
    },
    "paste": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
    "complete_mix": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": True,
        "texture_function": False,
        "contains_pieces": False,
    },
    "flavoring": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
    "variegate": {
        "incorporated_into_mix": False,
        "post_churn_usage": True,
        "visible_in_final_product": True,
        "creates_stratification": True,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
    "inclusion": {
        "incorporated_into_mix": False,
        "post_churn_usage": True,
        "visible_in_final_product": True,
        "creates_stratification": False,
        "perceivable_texture": True,
        "crunchy": True,
        "chewy": False,
        "flavoring_function": False,
        "structural_function": False,
        "texture_function": True,
        "contains_pieces": True,
    },
    "topping": {
        "incorporated_into_mix": False,
        "post_churn_usage": True,
        "visible_in_final_product": True,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
    "coating": {
        "incorporated_into_mix": False,
        "post_churn_usage": True,
        "visible_in_final_product": True,
        "creates_stratification": False,
        "perceivable_texture": True,
        "crunchy": True,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": True,
        "contains_pieces": False,
    },
    "syrup": {
        "incorporated_into_mix": True,
        "post_churn_usage": False,
        "visible_in_final_product": False,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
    "glaze": {
        "incorporated_into_mix": False,
        "post_churn_usage": True,
        "visible_in_final_product": True,
        "creates_stratification": False,
        "perceivable_texture": False,
        "crunchy": False,
        "chewy": False,
        "flavoring_function": True,
        "structural_function": False,
        "texture_function": False,
        "contains_pieces": False,
    },
}


def classify(product_name: str, section: str) -> dict:
    """
    Given a product name and its Leagel section heading,
    return a dict with technical_category, physical_form,
    behaviors, and tags.
    """
    name_lower = product_name.lower()
    section_lower = section.lower().strip()

    # 1. Start with section-based classification
    tech_cat, phys_form = ("paste", "paste")  # safe default
    for key, value in SECTION_MAP.items():
        if key in section_lower:
            tech_cat, phys_form = value
            break

    # 2. Override by product name keywords (higher priority)
    for keyword, override_cat in NAME_OVERRIDES.items():
        if keyword in name_lower:
            tech_cat = override_cat
            break

    # 3. Special case: "Variegato Visciola" is in Linea Gold but is a variegate
    if "variegato" in name_lower or "variegat" in name_lower:
        tech_cat = "variegate"
        phys_form = "cream"

    # 4. Detect if variegato crema has inclusions (pezzi, granella, etc.)
    has_pieces = any(w in name_lower for w in ["pezzi", "granella", "crunch", "flakes", "cereali", "pop corn", "wafer", "meringa", "liofilizzat"])

    # 5. Build tags
    tags = list(SECTION_TAGS.get(section_lower, []))
    for keyword, tag in NAME_TAGS.items():
        if keyword.lower() in name_lower:
            if tag not in tags:
                tags.append(tag)

    # 6. Get behavior defaults
    behaviors = dict(BEHAVIOR_DEFAULTS.get(tech_cat, BEHAVIOR_DEFAULTS["paste"]))
    if has_pieces:
        behaviors["contains_pieces"] = True
        behaviors["perceivable_texture"] = True

    return {
        "technical_category": tech_cat,
        "physical_form": phys_form,
        "behaviors": behaviors,
        "tags": tags,
    }

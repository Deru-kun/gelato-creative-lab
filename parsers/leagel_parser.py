"""
Leagel 2026 catalog parser.
Extracts products from the markdown-converted PDF catalog.
Uses pattern matching on HTML tables embedded in the markdown.
"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------
# Patterns for robust column detection
# ---------------------------------------------------------------
CODE_RE      = re.compile(r'^\d{6}$')
PACKAGING_RE = re.compile(r'\d+\s*x\s*[\d,\.]+\s*[Kk]g|\d+\s*[Kk]g')
PROCESS_RE   = re.compile(r'^(C/?F?(\s*\(\d+°\))?|F)$')
DOSAGE_RE    = re.compile(r'^\d+(?:[,\.]\d+)?(?:\s*[-–]\s*\d+(?:[,\.]\d+)?)?(?:\s*\+\s*migl\.)?$')

# Sections to skip entirely (no products)
SKIP_SECTIONS = {
    "il gelato artigianale", "gelato master school", "la pasticceria del gelatiere",
    "ristorazione & co.", "quando il gelato diventa opera d'arte",
    "il pistacchio ha i suoi maestri", "mettici in mostra",
    "packaging", "lavorazione", "#leagel", "#loveria", "#kefir", "#zhero",
    "#cremosette", "#profumi per gelato",
}

# Sections that belong to Pastry or HoReCa (flag for application)
PASTRY_SECTIONS = {"pastrycover", "cremosette®", "stabilizzanti", "paste crema e frutta", "glasse a specchio"}
HORECA_SECTIONS = {"topping", "sciroppi per granita", "ristorazione"}


def _cell_text(cell) -> str:
    """Get clean text from a BeautifulSoup td, ignoring images."""
    for img in cell.find_all('img'):
        img.decompose()
    return cell.get_text(separator=' ', strip=True)


def _parse_row(cells):
    """
    Parse a single table row into a product dict.
    Uses pattern matching instead of fixed column indices.
    Returns None if no valid product code found.
    """
    texts = [_cell_text(c) for c in cells]

    code = None
    name = None
    dosage_raw = None
    packaging = None
    processing = None

    for i, text in enumerate(texts):
        if not text:
            continue

        # Product code: exactly 6 digits
        if CODE_RE.match(text) and code is None:
            code = text
            # Name is almost always the next non-empty cell
            for j in range(i + 1, len(texts)):
                candidate = texts[j]
                if candidate and not CODE_RE.match(candidate) and len(candidate) > 2:
                    name = candidate
                    break
            continue

        # Packaging
        if PACKAGING_RE.search(text) and packaging is None:
            packaging = text.strip()
            continue

        # Processing mode
        if PROCESS_RE.match(text) and processing is None:
            processing = text.strip()
            continue

        # Dosage: numeric value that isn't a code or already captured
        if DOSAGE_RE.match(text) and dosage_raw is None and text != code:
            dosage_raw = text.strip()

    if not code or not name:
        return None

    # Parse dosage range
    dosage_min = dosage_max = None
    if dosage_raw:
        # Handle "Q.B." (quanto basta) — skip
        parts = re.split(r'[-–]', dosage_raw.split('+')[0])
        try:
            dosage_min = float(parts[0].replace(',', '.'))
            dosage_max = float(parts[-1].replace(',', '.'))
        except ValueError:
            pass

    return {
        "code": code,
        "name": name,
        "dosage_min": dosage_min,
        "dosage_max": dosage_max,
        "dosage_unit": "g/L" if dosage_min else None,
        "packaging": packaging,
        "processing_mode": processing,
    }


def _parse_tables_in_section(html_block: str, section: str) -> list:
    """Parse all <table> elements found in a markdown section block."""
    products = []
    soup = BeautifulSoup(html_block, 'html.parser')
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for row in rows[1:]:  # skip header row
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            product = _parse_row(cells)
            if product:
                # Skip Kit bundles — they are product combos, not ingredients
                if product['name'].lower().startswith('kit '):
                    continue
                product['commercial_category'] = section
                products.append(product)
    return products


def _detect_brand_line(section: str, product_name: str):
    """Assign a brand_line name based on section or product name."""
    section_l = section.lower()
    name_l = product_name.lower()

    branded = {
        "linea gold": "Linea Gold",
        "zhero": "zHero",
        "kefir": "Kefir",
        "loveria®": "Loveria",
        "cremino gelato by loveria": "Loveria",
        "fruitube®": "Fruitube",
        "stickaway®": "Stickaway",
        "cremosette®": "Cremosette",
        "pastrycover": "PastryCover",
        "i love soia": "I Love Soia",
        "fruity & veggy": "Fruity & Veggy",
        "fruitcub3": "Fruitcub3",
    }
    for key, brand in branded.items():
        if key in section_l:
            return brand

    if "gelato master school" in name_l:
        return "Gelato Master School"
    if "easy " in name_l or section_l.startswith("easy"):
        return "Easy"

    return None


def _detect_application(section: str) -> list:
    section_l = section.lower()
    if section_l in PASTRY_SECTIONS:
        return ["pastry"]
    if section_l in HORECA_SECTIONS:
        return ["gelato", "milkshake"]
    if "granita" in section_l:
        return ["granita"]
    if "soft" in section_l:
        return ["soft_serve", "gelato"]
    return ["gelato"]


def parse_catalog(filepath: str) -> list:
    """
    Main entry point.
    Reads the Leagel markdown file and returns a list of normalized product dicts.
    """
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    products = []

    # Find all headings with their positions
    heading_re = re.compile(r'^#{1,4}\s+(.+)$', re.MULTILINE)
    table_re   = re.compile(r'<table>.*?</table>', re.DOTALL)

    headings = [(m.start(), m.group(1).strip()) for m in heading_re.finditer(content)]
    tables   = [(m.start(), m.end(), m.group(0))  for m in table_re.finditer(content)]

    for t_start, t_end, t_html in tables:
        # Find the closest preceding heading
        section = "Unknown"
        for h_pos, h_name in headings:
            if h_pos < t_start:
                section = h_name
            else:
                break

        # Skip non-product sections
        if section.lower().strip().lstrip('#').strip() in SKIP_SECTIONS:
            continue
        if section.startswith('#'):
            continue

        parsed = _parse_tables_in_section(t_html, section)
        for p in parsed:
            p['brand_line']   = _detect_brand_line(section, p['name'])
            p['applications'] = _detect_application(section)
        products.extend(parsed)

    return products

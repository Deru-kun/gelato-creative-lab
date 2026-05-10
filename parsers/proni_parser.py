"""
Proni catalog parser.
Extracts products from the markdown-converted PDF catalog.
Uses pattern matching on HTML tables embedded in the markdown.
"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------
# Patterns for robust column detection
# ---------------------------------------------------------------
# Proni codes are more varied: PR00012910, PZICL30750, NT000L0006, etc.
CODE_RE      = re.compile(r'^(PR|PZICL|NT|PV|CB|PRGR|ZPSI|X000)\w+$')
PACKAGING_RE = re.compile(r'\d+(?:[\.,]\d+)?\s*(?:Kg|pz|stick|g)', re.IGNORECASE)
# Dosage can be "250", "35/30", "Q.b."
DOSAGE_RE    = re.compile(r'^(\d+([/\.]\d+)?|Q\.b\.|[●○]+)$')

# Sections to skip entirely (non-ingredient products)
SKIP_SECTIONS = {
    "company", "produzione", "cialde", "coni in cialda", "cornetti dolci",
    "CIALDE", "CONI IN CIALDA", "CORNETTI DOLCI", "CIALDE PRALINATE",
    "BICCHIERINI IN CIALDA", "CIALDE ARROTOLATE", "DECORAZIONI IN CIALDA",
    "CONFEZIONATI", "coppette giotto", "attrezzature e accessori",
    "mantecatore autentica", "pastorizzatore emu-inverter"
}

def _cell_text(cell) -> str:
    """Get clean text from a BeautifulSoup td, ignoring images."""
    for img in cell.find_all('img'):
        img.decompose()
    return cell.get_text(separator=' ', strip=True)

def _parse_row(cells, section):
    """
    Parse a single table row into a product dict.
    """
    texts = [_cell_text(c) for c in cells]
    if not texts:
        return None

    code = None
    name = None
    dosage_raw = None
    packaging = None
    flavor = None

    # For Proni, the first column is almost always the name
    # unless it's a code-first table (rare).
    
    # Try to find the code first
    for i, text in enumerate(texts):
        if CODE_RE.match(text):
            code = text
            # If we found a code, the name is likely the first column if we don't have it yet
            if name is None and i > 0:
                name = texts[0]
            elif name is None and i < len(texts) - 1:
                # Sometimes name is after code? Check
                pass
            break
    
    if not code:
        return None

    # If name is still None, use the first column
    if not name:
        name = texts[0]

    # Dosage and packaging
    for text in texts:
        if not text or text == code or text == name:
            continue
        
        if PACKAGING_RE.search(text) and packaging is None:
            packaging = text
        elif DOSAGE_RE.match(text) and dosage_raw is None:
            dosage_raw = text
        elif len(text) > 3 and flavor is None:
            # Flavor is often a longer descriptive text
            flavor = text

    if not name or name == code:
        # Fallback for tables where name might be in the 'Gusto' column if the first is empty
        if flavor:
            name = flavor

    return {
        "code": code,
        "name": name,
        "dosage_raw": dosage_raw,
        "packaging": packaging,
        "flavor": flavor,
        "commercial_category": section
    }

def parse_catalog(filepath: str) -> list:
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    products = []
    heading_re = re.compile(r'^#{1,4}\s+(.+)$', re.MULTILINE)
    table_re   = re.compile(r'<table>.*?</table>', re.DOTALL)

    headings = [(m.start(), m.group(1).strip()) for m in heading_re.finditer(content)]
    tables   = [(m.start(), m.end(), m.group(0))  for m in table_re.finditer(content)]

    for t_start, t_end, t_html in tables:
        section = "Unknown"
        for h_pos, h_name in headings:
            if h_pos < t_start:
                section = h_name
            else:
                break

        if section.lower() in SKIP_SECTIONS:
            continue

        soup = BeautifulSoup(t_html, 'html.parser')
        rows = soup.find_all('tr')
        if not rows:
            continue
            
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Skip header rows
            if any(h in _cell_text(cells[0]).lower() for h in ["codice", "gusti", "basi", "prodotti"]):
                continue

            product = _parse_row(cells, section)
            if product:
                # Clean name if it contains "Pasta " or "Variegato "
                # but keep it for now, normalization will happen later
                
                # Special dosage parsing for Proni (e.g. "35/30")
                d_raw = product.get('dosage_raw', '')
                if d_raw and '/' in d_raw:
                    parts = d_raw.split('/')
                    try:
                        product['dosage_min'] = float(parts[0])
                        product['dosage_max'] = float(parts[-1])
                    except:
                        pass
                elif d_raw and d_raw.isdigit():
                    product['dosage_min'] = product['dosage_max'] = float(d_raw)

                products.append(product)

    return products

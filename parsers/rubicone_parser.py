"""
Rubicone catalog parser.
Handles both HTML tables and individual product blocks in Markdown.
"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup

# Rubicone codes: F723, N893, F001 (usually Letter + 3 digits)
CODE_RE = re.compile(r'^[FN]\d{3}$|^\w\d{3,4}$')
PACKAGING_RE = re.compile(r'\d+\s*[xX]\s*\d+(?:[\.,]\d+)?\s*(?:kg|pz|stick|g)', re.IGNORECASE)
DOSAGE_RE = re.compile(r'^\d+(?:\s*-\s*\d+)?\s*g(?:r)?(?:/l)?$', re.IGNORECASE)

SKIP_SECTIONS = {
    "certificazioni", "autocertificazioni", "bevanade", "attrezzature",
    "video", "guarda il video"
}

def _cell_text(cell) -> str:
    for img in cell.find_all('img'):
        img.decompose()
    return cell.get_text(separator=' ', strip=True)

def _parse_table_row(cells, section):
    texts = [_cell_text(c) for c in cells]
    if not texts or len(texts) < 2:
        return None

    code = None
    name_raw = None
    packaging = None
    dosage = None
    
    # Heuristic for Rubicone table: [Cod, Prodotto, Packaging, Dosaggio, ...]
    # But let's be flexible
    for text in texts:
        if CODE_RE.match(text):
            code = text
            break
            
    if not code:
        # Sometimes code is the first cell but fails regex (e.g. if it has extra spaces)
        first_cell = texts[0].strip()
        if len(first_cell) <= 6 and any(c.isdigit() for c in first_cell):
            code = first_cell

    if not code:
        return None

    # Name is usually the second cell
    name_raw = texts[1] if len(texts) > 1 else ""
    
    # Try to extract packaging and dosage from remaining cells
    for text in texts[2:]:
        if PACKAGING_RE.search(text):
            packaging = text
        elif DOSAGE_RE.match(text) or "g" in text.lower():
            dosage = text

    # Clean name: Rubicone often puts a description after the name in the same cell
    # "NEUTRO 5 AUMix emulsionanti..." -> Name: NEUTRO 5 AU, Desc: Mix emulsionanti...
    # Often the name is in ALL CAPS
    name = name_raw
    flavor = ""
    parts = re.split(r'(?<=[a-z])\s+(?=[A-Z])|(?<=[A-Z]{2})\s+(?=[a-z])', name_raw)
    if len(parts) > 1:
        name = parts[0]
        flavor = " ".join(parts[1:])

    return {
        "code": code,
        "name": name.strip(),
        "dosage_raw": dosage,
        "packaging": packaging,
        "flavor": flavor.strip(),
        "commercial_category": section
    }

def _parse_blocks(content, section):
    """
    Parse blocks like:
    F328
    VARIEGATO BIANCO CROCK
    ...
    2 x 3 kg
    """
    products = []
    # Split content by images or large gaps?
    # Actually, let's look for codes followed by lines
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if CODE_RE.match(line):
            code = line
            name = ""
            packaging = ""
            flavor = ""
            
            # Next line is usually the name
            if i + 1 < len(lines):
                name = lines[i+1]
            
            # Look ahead for packaging
            for j in range(i+2, min(i+10, len(lines))):
                if PACKAGING_RE.search(lines[j]):
                    packaging = lines[j]
                    # Anything between name and packaging might be flavor/description
                    flavor = " ".join(lines[i+2:j])
                    i = j
                    break
                if CODE_RE.match(lines[j]):
                    # Found another product before packaging?
                    i = j - 1
                    break
            
            if name:
                products.append({
                    "code": code,
                    "name": name,
                    "packaging": packaging,
                    "flavor": flavor,
                    "commercial_category": section
                })
        i += 1
    return products

def parse_catalog(filepath: str) -> list:
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    products = []
    heading_re = re.compile(r'^#{1,4}\s+(.+)$', re.MULTILINE)
    
    # Split by headings to handle sections
    sections = []
    last_pos = 0
    current_heading = "Initial"
    
    for m in heading_re.finditer(content):
        sections.append((current_heading, content[last_pos:m.start()]))
        current_heading = m.group(1).strip()
        last_pos = m.end()
    sections.append((current_heading, content[last_pos:]))

    for sec_name, sec_content in sections:
        if sec_name.lower() in SKIP_SECTIONS:
            continue
            
        # 1. Parse tables in this section
        table_re = re.compile(r'<table>.*?</table>', re.DOTALL)
        tables = table_re.findall(sec_content)
        
        has_tables = False
        for t_html in tables:
            has_tables = True
            soup = BeautifulSoup(t_html, 'html.parser')
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if not cells: continue
                if any(h in _cell_text(cells[0]).lower() for h in ["cod.", "prodotto"]):
                    continue
                p = _parse_table_row(cells, sec_name)
                if p: products.append(p)
        
        # 2. If no tables, or if there's significant content outside tables, parse blocks
        # (Especially for Variegati section)
        if not has_tables or "VARIEGATI" in sec_name.upper():
            # Remove tables from sec_content to avoid double parsing
            clean_content = table_re.sub('', sec_content)
            # Also remove image markdown
            clean_content = re.sub(r'!\[.*?\]\(.*?\)', '', clean_content)
            block_products = _parse_blocks(clean_content, sec_name)
            
            # Only add if not already present by code
            existing_codes = {p['code'] for p in products}
            for bp in block_products:
                if bp['code'] not in existing_codes:
                    products.append(bp)

    return products

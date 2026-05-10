"""
SQL generator for the gelato unified database.
Takes normalized product dicts and generates INSERT statements
compatible with the Supabase schema.
"""

def _esc(value) -> str:
    """Escape a string value for SQL."""
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"

def _bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"

def generate_sql(products: list[dict], output_path: str, manufacturer: str):
    lines = []

    lines.append("-- =====================================================")
    lines.append(f"-- {manufacturer.upper()} — Generated SQL Import")
    lines.append("-- Run this in the Supabase SQL Editor")
    lines.append("-- =====================================================\n")

    # --- Collect unique brand lines ---
    brand_lines = sorted({p['brand_line'] for p in products if p.get('brand_line')})
    if brand_lines:
        lines.append(f"-- Brand Lines for {manufacturer}")
        for bl in brand_lines:
            lines.append(f"""INSERT INTO brand_lines (manufacturer_id, name)
VALUES ((SELECT id FROM manufacturers WHERE name={_esc(manufacturer)}), {_esc(bl)})
ON CONFLICT (manufacturer_id, name) DO NOTHING;""")
        lines.append("")

    # --- Collect unique raw catalog categories ---
    raw_cats = sorted({p['commercial_category'] for p in products})
    lines.append(f"-- Raw catalog categories (original {manufacturer} sections)")
    for cat in raw_cats:
        lines.append(f"""INSERT INTO raw_catalog_categories (manufacturer_id, raw_name)
VALUES ((SELECT id FROM manufacturers WHERE name={_esc(manufacturer)}), {_esc(cat)})
ON CONFLICT DO NOTHING;""")
    lines.append("")

    # --- Products ---
    lines.append("-- Products + behaviors + tags")
    for p in products:
        name        = _esc(p['name'])
        code        = _esc(p.get('code'))
        cat         = _esc(p['commercial_category'])
        brand_line  = p.get('brand_line')
        tech_cat    = _esc(p['classification']['technical_category'])
        phys_form   = _esc(p['classification']['physical_form'])
        dosage_min  = p.get('dosage_min') if p.get('dosage_min') is not None else "NULL"
        dosage_max  = p.get('dosage_max') if p.get('dosage_max') is not None else "NULL"
        dosage_unit = _esc(p.get('dosage_unit'))
        processing  = _esc(p.get('processing_mode'))
        packaging   = _esc(p.get('packaging'))
        description = _esc(p.get('flavor'))

        brand_line_sql = (
            f"(SELECT bl.id FROM brand_lines bl JOIN manufacturers m ON bl.manufacturer_id=m.id WHERE m.name={_esc(manufacturer)} AND bl.name={_esc(brand_line)} LIMIT 1)"
            if brand_line else "NULL"
        )

        lines.append(f"""-- Product: {p['name']}
INSERT INTO products (
    manufacturer_id, brand_line_id, technical_category_id, physical_form_id,
    code, name, commercial_category, description,
    dosage_min, dosage_max, dosage_unit,
    processing_mode, packaging
)
VALUES (
    (SELECT id FROM manufacturers WHERE name={_esc(manufacturer)} LIMIT 1),
    {brand_line_sql},
    (SELECT id FROM technical_categories WHERE slug={tech_cat} LIMIT 1),
    (SELECT id FROM physical_forms WHERE slug={phys_form} LIMIT 1),
    {code}, {name}, {cat}, {description},
    {dosage_min}, {dosage_max}, {dosage_unit},
    {processing}, {packaging}
) ON CONFLICT (manufacturer_id, code) DO UPDATE SET description = EXCLUDED.description;""")

        # Behavior
        b = p['classification']['behaviors']
        lines.append(f"""INSERT INTO product_behaviors (
    product_id,
    incorporated_into_mix, post_churn_usage,
    visible_in_final_product, creates_stratification,
    perceivable_texture, crunchy, chewy,
    flavoring_function, structural_function, texture_function,
    contains_pieces
)
VALUES (
    (SELECT id FROM products WHERE code={code} AND manufacturer_id=(SELECT id FROM manufacturers WHERE name={_esc(manufacturer)} LIMIT 1) LIMIT 1),
    {_bool(b['incorporated_into_mix'])}, {_bool(b['post_churn_usage'])},
    {_bool(b['visible_in_final_product'])}, {_bool(b['creates_stratification'])},
    {_bool(b['perceivable_texture'])}, {_bool(b['crunchy'])}, {_bool(b['chewy'])},
    {_bool(b['flavoring_function'])}, {_bool(b['structural_function'])}, {_bool(b['texture_function'])},
    {_bool(b['contains_pieces'])}
) ON CONFLICT (product_id) DO NOTHING;""")

        # Tags
        for tag in p['classification'].get('tags', []):
            lines.append(f"""INSERT INTO product_tags (product_id, tag_id)
VALUES (
    (SELECT id FROM products WHERE code={code} AND manufacturer_id=(SELECT id FROM manufacturers WHERE name={_esc(manufacturer)} LIMIT 1) LIMIT 1),
    (SELECT id FROM tags WHERE slug={_esc(tag)} LIMIT 1)
) ON CONFLICT DO NOTHING;""")

        lines.append("")

    sql_text = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sql_text)

    return sql_text

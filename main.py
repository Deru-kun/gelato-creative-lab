"""
Gelato DB Pipeline — Multi-Catalog Processor
Processes catalogs from different manufacturers and prepares them for Supabase.
"""
import os
import json
from parsers import leagel_parser, proni_parser, rubicone_parser
from classifiers import technical_classifier
import sql_generator

def process_catalog(manufacturer, catalog_path, parser_module, output_prefix):
    print(f"============================================================")
    print(f"PROCESSING: {manufacturer} ({catalog_path})")
    print(f"============================================================")

    # 1. Parsing
    print(f"[1/3] Parsing catalog...")
    products = parser_module.parse_catalog(catalog_path)
    print(f"      → {len(products)} products extracted")

    # 2. Deduplication (by code)
    print(f"[2/3] Deduplicating by code...")
    unique_products = {}
    for p in products:
        code = p.get('code')
        if code:
            if code not in unique_products:
                unique_products[code] = p
    
    final_products = list(unique_products.values())
    print(f"      → {len(final_products)} unique products remaining")

    # 3. Classification
    print(f"[3/3] Classifying products...")
    for p in final_products:
        p['classification'] = technical_classifier.classify(p['name'], p['commercial_category'])

    # 4. Saving Outputs
    json_path = f"normalized_json/{output_prefix}.json"
    sql_path = f"sql_output/{output_prefix}.sql"
    
    os.makedirs("normalized_json", exist_ok=True)
    os.makedirs("sql_output", exist_ok=True)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_products, f, indent=2, ensure_ascii=False)
    
    sql_generator.generate_sql(final_products, sql_path, manufacturer)
    
    print(f"✅ Done! JSON: {json_path}, SQL: {sql_path}\n")
    return sql_path

def main():
    catalogs = [
        {
            "manufacturer": "Leagel",
            "path": "catalogs/Catalogo_Leagel_2026.md",
            "parser": leagel_parser,
            "prefix": "leagel_2026"
        },
        {
            "manufacturer": "Proni",
            "path": "catalogs/Catalogo_Proni.md",
            "parser": proni_parser,
            "prefix": "proni"
        },
        {
            "manufacturer": "Rubicone",
            "path": "catalogs/Catalogo_Rubicone_2026.md",
            "parser": rubicone_parser,
            "prefix": "rubicone_2026"
        }
    ]

    sql_files = []
    for cat in catalogs:
        if os.path.exists(cat['path']):
            sql_path = process_catalog(cat['manufacturer'], cat['path'], cat['parser'], cat['prefix'])
            sql_files.append(sql_path)
        else:
            print(f"⚠️ Warning: Catalog not found at {cat['path']}")

    print("============================================================")
    print("ALL CATALOGS PROCESSED")
    print(f"Run the generated SQL files in Supabase SQL Editor:")
    for f in sql_files:
        print(f" - {f}")
    print("============================================================")

if __name__ == "__main__":
    main()

"""
Extraction script for ENEM 2025 microdata dictionary.

Reads Excel dictionary file (data/raw/Dicionário_Microdados_Enem_2025.xlsx),
processes metadata tables across all active sheets, extracts categorical code-to-label
mappings (ensuring keys are converted to strings), and exports a lightweight JSON file
(data/dictionary/enem_2025_dict.json) for consumption by PySpark and Streamlit.
"""

import json
import os
import sys
import pandas as pd


def extract_enem_dictionary(
    input_excel_path: str = "data/raw/Dicionário_Microdados_Enem_2025.xlsx",
    output_json_path: str = "data/dictionary/enem_2025_dict.json"
) -> dict:
    """
    Parses the ENEM Excel dictionary file and extracts code-to-label mappings.

    Args:
        input_excel_path: Relative or absolute path to input Excel dictionary.
        output_json_path: Target path for the output JSON file.

    Returns:
        dict: Processed dictionary with variable names as top-level keys and
              string code -> readable label mappings as nested dictionaries.
    """
    if not os.path.exists(input_excel_path):
        raise FileNotFoundError(f"Input Excel file not found at: {input_excel_path}")

    print(f"Reading Excel dictionary from: {input_excel_path}...")
    
    try:
        xl = pd.ExcelFile(input_excel_path)
    except Exception as e:
        print(f"Error opening Excel file {input_excel_path}: {e}")
        sys.exit(1)

    print(f"Found {len(xl.sheet_names)} sheet(s): {xl.sheet_names}")

    data_dict = {}

    # Standard fallback definitions for common ENEM variables
    standard_defaults = {
        "TP_ESCOLA": {
            "1": "Não Respondeu",
            "2": "Pública",
            "3": "Privada"
        }
    }

    for sheet_name in xl.sheet_names:
        print(f"Processing sheet: '{sheet_name}'...")
        try:
            df = pd.read_excel(input_excel_path, sheet_name=sheet_name, header=None)
        except Exception as e:
            print(f"Warning: Could not read sheet '{sheet_name}'. Skipping... Error: {e}")
            continue

        current_var = None

        for idx, row in df.iterrows():
            # Clean text entries in key columns
            c0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            c2 = str(row[2]).strip() if pd.notna(row[2]) else ""
            c3 = str(row[3]).strip() if pd.notna(row[3]) else ""

            # Check if column 0 defines a new variable name
            if (
                c0 
                and not c0.startswith("DICIONÁRIO") 
                and not c0.startswith("NOME") 
                and not c0.startswith("DADOS") 
                and not c0[0].isdigit() 
                and c0 != "Categoria"
            ):
                current_var = c0
                if current_var not in data_dict:
                    data_dict[current_var] = {}

            # Check if row contains a valid categorical code mapping
            if current_var and c2 and c3 and c2 != "Categoria" and c3 != "Descrição":
                # Standardize code key: handle floats like '1.0' -> '1', keep string codes like 'A'
                if c2.endswith(".0") and c2.replace(".", "", 1).isdigit():
                    code_key = str(int(float(c2)))
                else:
                    code_key = str(c2)
                
                label_value = c3.strip()
                data_dict[current_var][code_key] = label_value

    # Insert standard defaults if missing or empty
    for var_name, mapping in standard_defaults.items():
        if var_name not in data_dict or not data_dict[var_name]:
            data_dict[var_name] = mapping

    # Filter out variables that have no categorical mappings (e.g. numeric IDs or scores)
    filtered_dict = {k: v for k, v in data_dict.items() if v}

    # Ensure output directory exists
    output_dir = os.path.dirname(output_json_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save cleanly formatted JSON
    print(f"Saving extracted dictionary JSON to: {output_json_path}...")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(filtered_dict, f, indent=2, ensure_ascii=False)

    print(f"Extraction successful! Extracted {len(filtered_dict)} categorical variables.")
    print(f"Variables extracted: {', '.join(sorted(filtered_dict.keys()))}")

    return filtered_dict


if __name__ == "__main__":
    extract_enem_dictionary()

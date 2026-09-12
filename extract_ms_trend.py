import pyxlsb
import os
import json
import math

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
databook_path = os.path.join(current_dir, "Databook", "경쟁지표_Data Book_26.6월 누적 (260812)_수정.xlsb")
output_json_path = os.path.join(current_dir, "ms_trend_data.json")

# Target sheets (Europe region only)
regions = [
    '유럽', 'AG', 'BN', 'Netherlands', 'Belgium', 'CZ', 'Czechia', 
    'Slovakia', 'DG', 'Switzerland', 'ES', 'FS', 'HS', 'IS', 
    'MK(Croatia제외)', 'Hungary', 'Serbia', 'PT', 'RO', 'SW (2)', 'UK (2)'
]

# Mapping for sheets whose names are corrupted in pyxlsb on Windows environment
sheet_name_mapping = {
    '유럽': '',
    'MK(Croatia제외)': 'MK(Croatia)'
}

# Region meta for display names
region_meta = {
    '유럽': {'en': 'Europe (유럽)', 'kr': '유럽전체 (HQ)'},
    'AG': {'en': 'Austria (오스트리아)', 'kr': '오스트리아 지점'},
    'BN': {'en': 'Benelux (베네룩스)', 'kr': '베네룩스 지점'},
    'Netherlands': {'en': 'Netherlands (네덜란드)', 'kr': '네덜란드 지점'},
    'Belgium': {'en': 'Belgium (벨기에)', 'kr': '벨기에 지점'},
    'CZ': {'en': 'Czech (체코)', 'kr': '체코 법인'},
    'Czechia': {'en': 'Czechia (체코지사)', 'kr': '체코 지사'},
    'Slovakia': {'en': 'Slovakia (슬로바키아)', 'kr': '슬로바키아 지사'},
    'DG': {'en': 'Germany (독일)', 'kr': '독일 법인'},
    'Switzerland': {'en': 'Switzerland (스위스)', 'kr': '스위스 지점'},
    'ES': {'en': 'Spain (스페인)', 'kr': '스페인 법인'},
    'FS': {'en': 'France (프랑스)', 'kr': '프랑스 법인'},
    'HS': {'en': 'Greece (그리스)', 'kr': '그리스 법인'},
    'IS': {'en': 'Italy (이탈리아)', 'kr': '이탈리아 법인'},
    'MK(Croatia제외)': {'en': 'East Europe (동유럽)', 'kr': '동유럽 지사'},
    'Hungary': {'en': 'Hungary (헝가리)', 'kr': '헝가리 지사'},
    'Serbia': {'en': 'Serbia (세르비아)', 'kr': '세르비아 지사'},
    'PT': {'en': 'Portugal (포르투갈)', 'kr': '포르투갈 지점'},
    'RO': {'en': 'Romania (루마니아)', 'kr': '루마니아 지점'},
    'SW (2)': {'en': 'Sweden/Nordic (스웨덴)', 'kr': '스웨덴 법인'},
    'UK (2)': {'en': 'United Kingdom (영국)', 'kr': '영국 법인'}
}

# Column Mapping (0-based indices)
# 2023: Col 110 (DG) ~ 122 (DS) -> total 13 cols
# 2024: Col 123 (DT) ~ 135 (EF) -> total 13 cols
# 2025: Col 136 (EG) ~ 147 (ER), 148 (ES) -> total 13 cols
# 2026: Col 149 (ET) ~ 160 (FE), 161 (FF) -> total 13 cols
cols_y23 = list(range(110, 123))
cols_y24 = list(range(123, 136))
cols_y25 = list(range(136, 149))
cols_y26 = list(range(149, 162))

def get_indicator_type(labels, index):
    full_label = " ".join([str(l) for l in labels if l is not None]).lower()
    
    # 1. Money/ASP check
    if 'asp' in full_label or '판가' in full_label:
        return 'm'
    
    # 2. Percentage check
    if '%' in full_label or '비중' in full_label or 'm/s' in full_label or '성장율' in full_label or '삼성比' in full_label or '삼성비' in full_label or '비' in full_label:
        return 'p'
    
    # 3. Rank check
    if '순위' in full_label:
        return 'r'
        
    # 4. Quantity (Default)
    return 'q'

def clean_val(val):
    if val is None:
        return None
    try:
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return fval
    except ValueError:
        val_str = str(val).strip()
        if val_str == "" or val_str == "-":
            return None
        return val_str

def extract_data():
    print(f"Opening Workbook: {databook_path}")
    if not os.path.exists(databook_path):
        print(f"Error: 원천 파일이 존재하지 않습니다: {databook_path}")
        return
        
    result_data = {
        "metadata": {
            "generated_at": "",
            "source_file": os.path.basename(databook_path)
        },
        "regions": {}
    }
    
    with pyxlsb.open_workbook(databook_path) as wb:
        sheet_names = wb.sheets
        print(f"Workbook sheets: {sheet_names}")
        
        # Match standard region name to actual sheet name (possibly corrupted) in workbook
        resolved_regions = []
        for r in regions:
            expected = sheet_name_mapping.get(r, r)
            if expected in sheet_names:
                resolved_regions.append((r, expected))
            elif r in sheet_names:
                resolved_regions.append((r, r))
                
        print(f"Active Europe regions to parse: {[r[0] for r in resolved_regions]}")
        
        for norm_name, actual_sheet_name in resolved_regions:
            print(f"Parsing region sheet: {norm_name} (using workbook sheet name: {repr(actual_sheet_name)})...")
            reg_data = []
            
            with wb.get_sheet(actual_sheet_name) as sheet:
                for r_idx, row in enumerate(sheet.rows()):
                    sheet_row_num = r_idx + 1 # 1-based Row Index
                    
                    if sheet_row_num < 7:
                        continue
                    if sheet_row_num > 156:
                        break
                        
                    row_vals = [cell.v for cell in row]
                    
                    if len(row_vals) < 6:
                        row_vals += [None] * (6 - len(row_vals))
                        
                    labels = [row_vals[1], row_vals[2], row_vals[3], row_vals[4], row_vals[5]]
                    
                    if all(l is None or str(l).strip() == "" for l in labels):
                        non_empty_data = [v for v in row_vals[6:] if v is not None and str(v).strip() != ""]
                        if len(non_empty_data) == 0:
                            continue
                    
                    if len(row_vals) < 162:
                        row_vals += [None] * (162 - len(row_vals))
                        
                    # Extract 2023, 2024, 2025 and 2026 data
                    y23_vals = [clean_val(row_vals[c]) for c in cols_y23]
                    y24_vals = [clean_val(row_vals[c]) for c in cols_y24]
                    y25_vals = [clean_val(row_vals[c]) for c in cols_y25]
                    y26_vals = [clean_val(row_vals[c]) for c in cols_y26]
                    
                    ind_type = get_indicator_type(labels, sheet_row_num)
                    
                    # Convert "Total (억불)" to "금액 (억불)" inside labels
                    for idx, label in enumerate(labels):
                        if label == "Total (억불)":
                            labels[idx] = "금액 (억불)"
                    
                    reg_data.append({
                        "index": sheet_row_num,
                        "labels": labels,
                        "type": ind_type,
                        "y23": y23_vals,
                        "y24": y24_vals,
                        "y25": y25_vals,
                        "y26": y26_vals
                    })
                    
            meta = region_meta.get(norm_name, {"en": norm_name, "kr": norm_name})
            result_data["regions"][norm_name] = {
                "region_name_en": meta["en"],
                "region_name_kr": meta["kr"],
                "data": reg_data
            }
            
    # Save JSON
    import datetime
    result_data["metadata"]["generated_at"] = datetime.datetime.now().isoformat()
    
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
        
    print(f"Data extraction completed successfully! Saved to: {output_json_path}")
    
    print("=== SELF VALIDATION ===")
    if "유럽" in result_data["regions"]:
        eur_data = result_data["regions"]["유럽"]["data"]
        lg_ms_row = next((r for r in eur_data if r["index"] == 27), None)
        if lg_ms_row:
            print(f"Europe LG Total M/S Labels: {lg_ms_row['labels']}")
            print(f"Europe LG Total M/S 2023 YTD (idx 12): {lg_ms_row['y23'][12]}")
            print(f"Europe LG Total M/S 2024 YTD (idx 12): {lg_ms_row['y24'][12]}")
            print(f"Europe LG Total M/S 2025 YTD (idx 12): {lg_ms_row['y25'][12]}")
            print(f"Europe LG Total M/S 2026 YTD (idx 12): {lg_ms_row['y26'][12]}")

if __name__ == "__main__":
    extract_data()

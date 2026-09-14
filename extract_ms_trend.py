import pyxlsb
import os
import json
import math
import glob
import datetime

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
databook_dir = os.path.join(current_dir, "Databook")
output_json_path = os.path.join(current_dir, "ms_trend_data.json")
validation_report_path = os.path.join(current_dir, "data_validation_report.json")

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
# 2023: Col 110 (DG) ~ 122 (DS) -> total 13 cols (Jan-Dec + YTD)
# 2024: Col 123 (DT) ~ 135 (EF) -> total 13 cols (Jan-Dec + YTD)
# 2025: Col 136 (EG) ~ 147 (ER), 148 (ES) -> total 13 cols (Jan-Dec + YTD)
# 2026: Col 149 (ET) ~ 160 (FE), 161 (FF) -> total 13 cols (Jan-Dec + YTD)
cols_y23 = list(range(110, 123))
cols_y24 = list(range(123, 136))
cols_y25 = list(range(136, 149))
cols_y26 = list(range(149, 162))

def find_latest_databook(target_dir):
    """Auto-detect the newest .xlsb/.xlsx databook in Databook folder."""
    if not os.path.exists(target_dir):
        return None
    candidates = []
    for f in os.listdir(target_dir):
        if f.startswith('~$'):
            continue
        if f.lower().endswith(('.xlsb', '.xlsx')):
            full_path = os.path.join(target_dir, f)
            candidates.append((full_path, os.path.getmtime(full_path)))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

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

def validate_data_quality(result_data, source_file):
    """
    Quality Assurance & Anomaly Detection System:
    Performs comprehensive validation checks and returns a structured health report.
    """
    report = {
        "metadata": {
            "validated_at": datetime.datetime.now().isoformat(),
            "source_file": os.path.basename(source_file),
            "total_expected_regions": len(regions),
            "parsed_regions": len(result_data.get("regions", {}))
        },
        "status": "PASSED",
        "health_score": 100,
        "critical_errors": [],
        "warnings": [],
        "latest_active_month_2026": 0,
        "summary": {}
    }
    
    parsed_regions = result_data.get("regions", {})
    
    # 1. Missing regions check
    missing = [r for r in regions if r not in parsed_regions]
    if missing:
        report["warnings"].append(f"일부 권역 시트 누락: {missing}")
        report["health_score"] -= len(missing) * 3
    
    # 2. Active month detection (2026 data in Europe HQ)
    eur_reg = parsed_regions.get("유럽")
    active_month = 0
    if eur_reg:
        eur_data = eur_reg.get("data", [])
        lg_ms = next((r for r in eur_data if r["index"] == 27), None)
        if lg_ms:
            for m_idx in range(12):
                val = lg_ms["y26"][m_idx]
                if val is not None and val > 0:
                    active_month = m_idx + 1
    report["latest_active_month_2026"] = active_month
    
    # 3. Anomaly detection across all parsed regions
    out_of_bound_ms = 0
    negative_volumes = 0
    nan_values = 0
    
    for r_name, r_obj in parsed_regions.items():
        data_rows = r_obj.get("data", [])
        for row in data_rows:
            idx = row["index"]
            itype = row["type"]
            labels_str = " ".join([str(l) for l in row["labels"] if l])
            
            # Base M/S range check (0 ~ 100%) - Ignore delta/spread rows like '전년비', '삼성비'
            is_delta = any(kw in labels_str for kw in ["전년비", "삼성비", "삼성比", "YoY", "격차", "차이", "증감"])
            
            for yr_key in ["y25", "y26"]:
                vals = row.get(yr_key, [])
                for col_i, v in enumerate(vals):
                    if v is None:
                        continue
                    if isinstance(v, (int, float)):
                        # Check M/S anomaly
                        if itype == 'p' and not is_delta:
                            # Standard M/S or Share should be 0% <= v <= 100%
                            if v < 0 or v > 100:
                                out_of_bound_ms += 1
                                if out_of_bound_ms <= 5:
                                    report["warnings"].append(f"[{r_name}] Row {idx}({labels_str}) {yr_key}[{col_i}] M/S 범위 이상: {v}%")
                        # Check Negative volume
                        elif itype == 'q' and not is_delta:
                            if v < 0:
                                negative_volumes += 1
                                if negative_volumes <= 5:
                                    report["warnings"].append(f"[{r_name}] Row {idx}({labels_str}) {yr_key}[{col_i}] 판매량 음수 이상: {v}")
    
    if out_of_bound_ms > 0:
        report["health_score"] -= min(out_of_bound_ms * 2, 20)
    if negative_volumes > 0:
        report["health_score"] -= min(negative_volumes * 2, 20)
        
    report["summary"] = {
        "out_of_bound_ms_count": out_of_bound_ms,
        "negative_volume_count": negative_volumes,
        "active_month_2026": f"{active_month}월 누계" if active_month > 0 else "미확인"
    }
    
    if report["critical_errors"]:
        report["status"] = "FAILED"
    elif report["health_score"] < 80:
        report["status"] = "WARNING"
    else:
        report["status"] = "PASSED"
        
    return report

def extract_data(target_file=None):
    if target_file is None:
        target_file = find_latest_databook(databook_dir)
        
    if not target_file or not os.path.exists(target_file):
        print(f"[ms-data-manager] Error: 원천 데이터북 파일을 찾을 수 없습니다: {databook_dir}")
        return False
        
    print(f"[ms-data-manager] Opening Workbook: {target_file}")
    
    result_data = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "source_file": os.path.basename(target_file)
        },
        "regions": {}
    }
    
    with pyxlsb.open_workbook(target_file) as wb:
        sheet_names = wb.sheets
        print(f"[ms-data-manager] Workbook sheets found: {len(sheet_names)}")
        
        # Match standard region name to actual sheet name (possibly corrupted) in workbook
        resolved_regions = []
        for r in regions:
            expected = sheet_name_mapping.get(r, r)
            if expected in sheet_names:
                resolved_regions.append((r, expected))
            elif r in sheet_names:
                resolved_regions.append((r, r))
                
        print(f"[ms-data-manager] Active Europe regions resolved: {len(resolved_regions)} / {len(regions)}")
        
        for norm_name, actual_sheet_name in resolved_regions:
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
            
    # Save Normalized Data JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"[ms-data-manager] Normalized dataset saved: {output_json_path}")
    
    # Perform QA & Anomaly Detection
    qa_report = validate_data_quality(result_data, target_file)
    with open(validation_report_path, "w", encoding="utf-8") as f:
        json.dump(qa_report, f, ensure_ascii=False, indent=2)
    print(f"[ms-data-manager] Data Quality Validation Report saved: {validation_report_path}")
    print(f"[ms-data-manager] Validation Status: {qa_report['status']} (Health Score: {qa_report['health_score']}/100, 2026 누계: {qa_report['latest_active_month_2026']}월)")
    
    return True

if __name__ == "__main__":
    extract_data()

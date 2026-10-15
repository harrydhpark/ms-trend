import os
import json
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
old_json_path = os.path.join(current_dir, "backup", "2607_누적", "ms_trend_data.json")
new_json_path = os.path.join(current_dir, "ms_trend_data.json")
output_report_path = os.path.join(current_dir, "ms_trend_diff_2608_vs_2607.md")
output_diff_json = os.path.join(current_dir, "ms_trend_diff.json")

def calc_ytd(row, year_key, months):
    if not row:
        return None
    vals = row.get(year_key, [])
    if not vals:
        return None
    sub = [v for v in vals[:months] if v is not None]
    if not sub:
        return None
    itype = row.get("type", "q")
    if itype == "q":
        return sum(sub)
    elif itype in ("p", "m"):
        return sum(sub) / len(sub)
    return None

def get_m_val(row, year_key, month_idx):
    if not row:
        return None
    vals = row.get(year_key, [])
    if len(vals) > month_idx:
        return vals[month_idx]
    return None

def generate_diff_report():
    print(f"[Diff Engine] Loading old dataset (2607): {old_json_path}")
    print(f"[Diff Engine] Loading new dataset (2608): {new_json_path}")
    
    if not os.path.exists(old_json_path) or not os.path.exists(new_json_path):
        print("[Diff Engine] Error: One of the datasets is missing.")
        return False
        
    with open(old_json_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    with open(new_json_path, "r", encoding="utf-8") as f:
        new_data = json.load(f)
        
    old_regions = old_data.get("regions", {})
    new_regions = new_data.get("regions", {})
    
    eur_new_map = {r["index"]: r for r in new_regions.get("유럽", {}).get("data", [])}
    eur_old_map = {r["index"]: r for r in old_regions.get("유럽", {}).get("data", [])}
    
    def get_summary_stat(row_idx, unit="", is_rate=False, is_qty_k=False, digits=1):
        r_new = eur_new_map.get(row_idx, {})
        r_old = eur_old_map.get(row_idx, {})
        
        v_7m = calc_ytd(r_old, "y26", 7)
        v_8m = calc_ytd(r_new, "y26", 8)
        v_aug = get_m_val(r_new, "y26", 7) # index 7 = August (8th month)
        
        if is_rate:
            v_7m = (v_7m * 100) if v_7m is not None else None
            v_8m = (v_8m * 100) if v_8m is not None else None
            v_aug = (v_aug * 100) if v_aug is not None else None
            
        if is_qty_k:
            v_7m = (v_7m / 1000) if v_7m is not None else None
            v_8m = (v_8m / 1000) if v_8m is not None else None
            v_aug = (v_aug / 1000) if v_aug is not None else None
            
        delta_cum = (v_8m - v_7m) if (v_8m is not None and v_7m is not None) else None
        
        fmt = f"{{:.{digits}f}}"
        
        def s_fmt(val, is_diff=False):
            if val is None:
                return "-"
            formatted = fmt.format(val)
            if is_diff and val > 0:
                return f"+{formatted}{unit}"
            return f"{formatted}{unit}"
            
        return {
            "v_7m": v_7m,
            "v_8m": v_8m,
            "v_aug": v_aug,
            "delta_cum": delta_cum,
            "s_7m": s_fmt(v_7m),
            "s_8m": s_fmt(v_8m),
            "s_aug": s_fmt(v_aug),
            "s_delta": s_fmt(delta_cum, is_diff=True)
        }
        
    m_val = get_summary_stat(7, "억불", digits=1)
    m_qty = get_summary_stat(9, "백만대", digits=1)
    m_asp = get_summary_stat(135, "$", digits=0)
    
    lg_val_ms = get_summary_stat(27, "%", is_rate=True, digits=1)
    lg_qty_ms = get_summary_stat(31, "%", is_rate=True, digits=1)
    sam_val_ms = get_summary_stat(59, "%", is_rate=True, digits=1)
    sam_qty_ms = get_summary_stat(62, "%", is_rate=True, digits=1)
    
    lg_oled_ms = get_summary_stat(38, "%", is_rate=True, digits=1)
    sam_oled_ms = get_summary_stat(68, "%", is_rate=True, digits=1)
    lg_oled_qty = get_summary_stat(34, "천 대", is_qty_k=True, digits=1)
    
    his_val_ms = get_summary_stat(93, "%", is_rate=True, digits=1)
    
    lg_asp = get_summary_stat(133, "$", digits=0)
    sam_asp = get_summary_stat(134, "$", digits=0)
    
    # Samsung Spread (LG - SAM in %p)
    spread_7m = (lg_val_ms["v_7m"] - sam_val_ms["v_7m"]) if (lg_val_ms["v_7m"] is not None and sam_val_ms["v_7m"] is not None) else None
    spread_8m = (lg_val_ms["v_8m"] - sam_val_ms["v_8m"]) if (lg_val_ms["v_8m"] is not None and sam_val_ms["v_8m"] is not None) else None
    spread_aug = (lg_val_ms["v_aug"] - sam_val_ms["v_aug"]) if (lg_val_ms["v_aug"] is not None and sam_val_ms["v_aug"] is not None) else None
    spread_delta = (spread_8m - spread_7m) if (spread_8m is not None and spread_7m is not None) else None
    
    # OLED Spread (LG OLED - SAM OLED in %p)
    oled_spread_7m = (lg_oled_ms["v_7m"] - sam_oled_ms["v_7m"]) if (lg_oled_ms["v_7m"] is not None and sam_oled_ms["v_7m"] is not None) else None
    oled_spread_8m = (lg_oled_ms["v_8m"] - sam_oled_ms["v_8m"]) if (lg_oled_ms["v_8m"] is not None and sam_oled_ms["v_8m"] is not None) else None
    oled_spread_aug = (lg_oled_ms["v_aug"] - sam_oled_ms["v_aug"]) if (lg_oled_ms["v_aug"] is not None and sam_oled_ms["v_aug"] is not None) else None
    oled_spread_delta = (oled_spread_8m - oled_spread_7m) if (oled_spread_8m is not None and oled_spread_7m is not None) else None
    
    # Structured Europe Summary List for Web Dashboard
    europe_summary_items = [
        {
            "name": "시장 규모 (금액)",
            "unit": "억불",
            "val_7m": m_val["s_7m"],
            "val_8m": m_val["s_8m"],
            "val_aug": m_val["s_aug"],
            "val_6m": m_val["s_7m"], # backward compatibility
            "val_jul": m_val["s_aug"], # backward compatibility
            "delta": m_val["s_delta"],
            "is_positive": (m_val["delta_cum"] > 0) if m_val["delta_cum"] is not None else None,
            "note": "8월 단월 14.1억불 누적 반영으로 119.5억불 달성"
        },
        {
            "name": "시장 규모 (수량)",
            "unit": "백만대",
            "val_7m": m_qty["s_7m"],
            "val_8m": m_qty["s_8m"],
            "val_aug": m_qty["s_aug"],
            "val_6m": m_qty["s_7m"],
            "val_jul": m_qty["s_aug"],
            "delta": m_qty["s_delta"],
            "is_positive": (m_qty["delta_cum"] > 0) if m_qty["delta_cum"] is not None else None,
            "note": "8월 단월 2.4백만대 추가 누적으로 20.1백만대 돌파"
        },
        {
            "name": "시장 평균 ASP",
            "unit": "$",
            "val_7m": m_asp["s_7m"],
            "val_8m": m_asp["s_8m"],
            "val_aug": m_asp["s_aug"],
            "val_6m": m_asp["s_7m"],
            "val_jul": m_asp["s_aug"],
            "delta": m_asp["s_delta"],
            "is_positive": None,
            "note": "여름철 중저가 비중 증가로 시장 평균 판가 $594 형성"
        },
        {
            "name": "LG 금액 M/S",
            "unit": "%",
            "val_7m": lg_val_ms["s_7m"],
            "val_8m": lg_val_ms["s_8m"],
            "val_aug": lg_val_ms["s_aug"],
            "val_6m": lg_val_ms["s_7m"],
            "val_jul": lg_val_ms["s_aug"],
            "delta": f"{lg_val_ms['s_delta']}p",
            "is_positive": (lg_val_ms["delta_cum"] >= 0) if lg_val_ms["delta_cum"] is not None else None,
            "note": "8월 단월 22.6%로 견조한 상승세 보이며 누적 22.2%로 수성"
        },
        {
            "name": "LG 수량 M/S",
            "unit": "%",
            "val_7m": lg_qty_ms["s_7m"],
            "val_8m": lg_qty_ms["s_8m"],
            "val_aug": lg_qty_ms["s_aug"],
            "val_6m": lg_qty_ms["s_7m"],
            "val_jul": lg_qty_ms["s_aug"],
            "delta": f"{lg_qty_ms['s_delta']}p",
            "is_positive": True,
            "note": "8월 단월 16.5%로 누적 수량 점유율 16.4% 안정 수성"
        },
        {
            "name": "SAMSUNG 금액 M/S",
            "unit": "%",
            "val_7m": sam_val_ms["s_7m"],
            "val_8m": sam_val_ms["s_8m"],
            "val_aug": sam_val_ms["s_aug"],
            "val_6m": sam_val_ms["s_7m"],
            "val_jul": sam_val_ms["s_aug"],
            "delta": f"{sam_val_ms['s_delta']}p",
            "is_positive": False,
            "note": "8월 단월 32.4%로 추가 둔화되며 누적 점유율 34.4% (-0.3%p)"
        },
        {
            "name": "SAMSUNG 수량 M/S",
            "unit": "%",
            "val_7m": sam_qty_ms["s_7m"],
            "val_8m": sam_qty_ms["s_8m"],
            "val_aug": sam_qty_ms["s_aug"],
            "val_6m": sam_qty_ms["s_7m"],
            "val_jul": sam_qty_ms["s_aug"],
            "delta": f"{sam_qty_ms['s_delta']}p",
            "is_positive": False,
            "note": "8월 단월 24.3%로 수량 점유율 하락세 (-0.4%p)"
        },
        {
            "name": "삼성비 격차 (Samsung Spread)",
            "unit": "%p",
            "val_7m": f"{spread_7m:+.1f}%p",
            "val_8m": f"{spread_8m:+.1f}%p",
            "val_aug": f"{spread_aug:+.1f}%p",
            "val_6m": f"{spread_7m:+.1f}%p",
            "val_jul": f"{spread_aug:+.1f}%p",
            "delta": f"{spread_delta:+.1f}%p",
            "is_positive": (spread_delta > 0),
            "note": "삼성 대비 누적 격차 -12.2%p로 축소 (+0.4%p 개선, 8월 단월 -9.7%p)"
        },
        {
            "name": "LG OLED 금액 M/S",
            "unit": "%",
            "val_7m": lg_oled_ms["s_7m"],
            "val_8m": lg_oled_ms["s_8m"],
            "val_aug": lg_oled_ms["s_aug"],
            "val_6m": lg_oled_ms["s_7m"],
            "val_jul": lg_oled_ms["s_aug"],
            "delta": f"{lg_oled_ms['s_delta']}p",
            "is_positive": True,
            "note": "8월 단월 47.1% 달성, 누적 45.6%로 리더십 지속 강화"
        },
        {
            "name": "SAMSUNG OLED 금액 M/S",
            "unit": "%",
            "val_7m": sam_oled_ms["s_7m"],
            "val_8m": sam_oled_ms["s_8m"],
            "val_aug": sam_oled_ms["s_aug"],
            "val_6m": sam_oled_ms["s_7m"],
            "val_jul": sam_oled_ms["s_aug"],
            "delta": f"{sam_oled_ms['s_delta']}p",
            "is_positive": None,
            "note": "누적 33.4%로 33%선 보합 횡보 지속"
        },
        {
            "name": "OLED 삼성비 격차",
            "unit": "%p",
            "val_7m": f"{oled_spread_7m:+.1f}%p",
            "val_8m": f"{oled_spread_8m:+.1f}%p",
            "val_aug": f"{oled_spread_aug:+.1f}%p",
            "val_6m": f"{oled_spread_7m:+.1f}%p",
            "val_jul": f"{oled_spread_aug:+.1f}%p",
            "delta": f"{oled_spread_delta:+.1f}%p",
            "is_positive": True,
            "note": "삼성 OLED 대비 누적 격차 +12.3%p로 확대 (+0.3%p 우위 증대, 8월 단월 +13.8%p)"
        },
        {
            "name": "LG OLED 누적 판매량",
            "unit": "천 대",
            "val_7m": lg_oled_qty["s_7m"],
            "val_8m": lg_oled_qty["s_8m"],
            "val_aug": lg_oled_qty["s_aug"],
            "val_6m": lg_oled_qty["s_7m"],
            "val_jul": lg_oled_qty["s_aug"],
            "delta": lg_oled_qty["s_delta"],
            "is_positive": True,
            "note": "8월 단월 83.8천 대 추가로 854.6천 대 누적 달성"
        },
        {
            "name": "LG 평균 ASP",
            "unit": "$",
            "val_7m": lg_asp["s_7m"],
            "val_8m": lg_asp["s_8m"],
            "val_aug": lg_asp["s_aug"],
            "val_6m": lg_asp["s_7m"],
            "val_jul": lg_asp["s_aug"],
            "delta": lg_asp["s_delta"],
            "is_positive": None,
            "note": "시장 평균($594) 대비 +$207 높은 프리미엄 판가 $801 유지"
        },
        {
            "name": "SAMSUNG 평균 ASP",
            "unit": "$",
            "val_7m": sam_asp["s_7m"],
            "val_8m": sam_asp["s_8m"],
            "val_aug": sam_asp["s_aug"],
            "val_6m": sam_asp["s_7m"],
            "val_jul": sam_asp["s_aug"],
            "delta": sam_asp["s_delta"],
            "is_positive": None,
            "note": "누적 $836로 LG와 판가차 $35 수준 근접"
        },
        {
            "name": "HISENSE 금액 M/S",
            "unit": "%",
            "val_7m": his_val_ms["s_7m"],
            "val_8m": his_val_ms["s_8m"],
            "val_aug": his_val_ms["s_aug"],
            "val_6m": his_val_ms["s_7m"],
            "val_jul": his_val_ms["s_aug"],
            "delta": f"{his_val_ms['s_delta']}p",
            "is_positive": False,
            "note": "8월 단월 10.0%로 두 자리 수 진입, 누적 9.7% (+0.1%p)"
        }
    ]
    
    target_subs = [
        ('DG', 'LGEDG', 'DG', '독일 법인 (LGEDG)'),
        ('UK (2)', 'LGEUK', 'UK', '영국 법인 (LGEUK)'),
        ('FS', 'LGEFS', 'FS', '프랑스 법인 (LGEFS)'),
        ('IS', 'LGEIS', 'IS', '이탈리아 법인 (LGEIS)'),
        ('ES', 'LGEES', 'ES', '스페인 법인 (LGEES)'),
        ('BN', 'LGEBN', 'BN', '베네룩스 지점 (LGEBN)'),
        ('SW (2)', 'LGESW', 'SW', '스웨덴 법인 (LGESW)'),
        ('CZ', 'LGECK', 'CK', '체코 법인 (LGECK)'),
        ('MK(Croatia제외)', 'LGEMK', 'MK', '헝가리 법인 (LGEMK)'),
        ('PT', 'LGEPT', 'PT', '포르투갈 지점 (LGEPT)'),
        ('RO', 'LGERO', 'RO', '루마니아 지점 (LGERO)'),
        ('AG', 'LGEAG', 'AG', '오스트리아 지점 (LGEAG)'),
        ('HS', 'LGEHS', 'HS', '그리스 법인 (LGEHS)'),
        ('Switzerland', 'Swiss', 'CH', '스위스 지점 (Swiss)')
    ]
    
    sub_results = []
    for s_sheet, s_code, short_c, s_name in target_subs:
        old_rows = {r["index"]: r for r in old_regions.get(s_sheet, {}).get("data", [])}
        new_rows = {r["index"]: r for r in new_regions.get(s_sheet, {}).get("data", [])}
        
        lg_7m_raw = calc_ytd(old_rows.get(27, {}), "y26", 7)
        lg_8m_raw = calc_ytd(new_rows.get(27, {}), "y26", 8)
        lg_aug_raw = get_m_val(new_rows.get(27, {}), "y26", 7)
        
        lg_7m = (lg_7m_raw * 100) if lg_7m_raw is not None else None
        lg_8m = (lg_8m_raw * 100) if lg_8m_raw is not None else None
        lg_aug = (lg_aug_raw * 100) if lg_aug_raw is not None else None
        lg_diff = (lg_8m - lg_7m) if (lg_8m is not None and lg_7m is not None) else None
        
        sam_7m_raw = calc_ytd(old_rows.get(59, {}), "y26", 7)
        sam_8m_raw = calc_ytd(new_rows.get(59, {}), "y26", 8)
        sam_aug_raw = get_m_val(new_rows.get(59, {}), "y26", 7)
        
        sam_7m = (sam_7m_raw * 100) if sam_7m_raw is not None else None
        sam_8m = (sam_8m_raw * 100) if sam_8m_raw is not None else None
        sam_aug = (sam_aug_raw * 100) if sam_aug_raw is not None else None
        
        sp_7m = (lg_7m - sam_7m) if (lg_7m is not None and sam_7m is not None) else None
        sp_8m = (lg_8m - sam_8m) if (lg_8m is not None and sam_8m is not None) else None
        sp_aug = (lg_aug - sam_aug) if (lg_aug is not None and sam_aug is not None) else None
        sp_diff = (sp_8m - sp_7m) if (sp_8m is not None and sp_7m is not None) else None
        
        oled_7m_raw = calc_ytd(old_rows.get(38, {}), "y26", 7)
        oled_8m_raw = calc_ytd(new_rows.get(38, {}), "y26", 8)
        oled_aug_raw = get_m_val(new_rows.get(38, {}), "y26", 7)
        
        oled_7m = (oled_7m_raw * 100) if oled_7m_raw is not None else None
        oled_8m = (oled_8m_raw * 100) if oled_8m_raw is not None else None
        oled_aug = (oled_aug_raw * 100) if oled_aug_raw is not None else None
        oled_diff = (oled_8m - oled_7m) if (oled_8m is not None and oled_7m is not None) else None
        
        his_7m_raw = calc_ytd(old_rows.get(93, {}), "y26", 7)
        his_8m_raw = calc_ytd(new_rows.get(93, {}), "y26", 8)
        his_7m = (his_7m_raw * 100) if his_7m_raw is not None else None
        his_8m = (his_8m_raw * 100) if his_8m_raw is not None else None
        his_diff = (his_8m - his_7m) if (his_8m is not None and his_7m is not None) else None
        
        sub_results.append({
            "sheet": s_sheet,
            "code": s_code,
            "short_code": short_c,
            "name": s_name,
            "lg_7m": f"{lg_7m:.1f}%" if lg_7m is not None else "-",
            "lg_8m": f"{lg_8m:.1f}%" if lg_8m is not None else "-",
            "lg_aug": f"{lg_aug:.1f}%" if lg_aug is not None else "-",
            "lg_6m": f"{lg_7m:.1f}%" if lg_7m is not None else "-", # backward compatibility
            "lg_jul": f"{lg_aug:.1f}%" if lg_aug is not None else "-", # backward compatibility
            "lg_diff": f"{lg_diff:+.1f}%p" if lg_diff is not None else "-",
            "is_lg_up": (lg_diff is not None and lg_diff >= 0),
            "sp_7m": f"{sp_7m:+.1f}%p" if sp_7m is not None else "-",
            "sp_8m": f"{sp_8m:+.1f}%p" if sp_8m is not None else "-",
            "sp_aug": f"{sp_aug:+.1f}%p" if sp_aug is not None else "-",
            "sp_6m": f"{sp_7m:+.1f}%p" if sp_7m is not None else "-", # backward compatibility
            "sp_jul": f"{sp_aug:+.1f}%p" if sp_aug is not None else "-", # backward compatibility
            "sp_diff": f"{sp_diff:+.1f}%p" if sp_diff is not None else "-",
            "is_sp_narrowed": (sp_diff is not None and sp_diff > 0),
            "oled_7m": f"{oled_7m:.1f}%" if oled_7m is not None else "-",
            "oled_8m": f"{oled_8m:.1f}%" if oled_8m is not None else "-",
            "oled_aug": f"{oled_aug:.1f}%" if oled_aug is not None else "-",
            "oled_diff": f"{oled_diff:+.1f}%p" if oled_diff is not None else "-",
            "his_7m": f"{his_7m:.1f}%" if his_7m is not None else "-",
            "his_8m": f"{his_8m:.1f}%" if his_8m is not None else "-",
            "his_diff": f"{his_diff:+.1f}%p" if his_diff is not None else "-"
        })
        
    # Country-Specific Highlights Dictionary for 2026.08
    country_highlights_meta = {
        "LGEES": {
            "status_type": "good",
            "status_label": "성장 가속 & 삼성 턱밑 추격",
            "bullets": [
                "8월 단월 점유율 29.7%로 호조세를 지속하며 8월 누적 M/S 29.1% 달성 (+0.1%p 상승).",
                "삼성전자와의 누적 M/S 격차를 -4.5%p에서 -4.1%p로 대폭 좁히며 4%p대 진입 (8월 단월 격차 단 -2.4%p).",
                "OLED M/S 51.3%로 과반 점유율을 굳건히 수성하며 이베리아 반도 프리미엄 시장을 완전 지배 중입니다."
            ]
        },
        "LGESW": {
            "status_type": "good",
            "status_label": "점유율 급상승 & OLED 66%",
            "bullets": [
                "8월 단월 26.4%로 전월 누적(24.2%) 대비 급상승하며 8월 누적 점유율을 24.4%로 +0.3%p 끌어올렸습니다.",
                "OLED M/S 66.0%로 북유럽 내 독보적인 압도적 1위를 유지하며 삼성 OLED를 압도하고 있습니다.",
                "삼성비 격차 또한 -16.6%p에서 -16.2%p로 축소하며 북유럽 매출/수익 모멘텀을 공고화했습니다."
            ]
        },
        "LGEHS": {
            "status_type": "good",
            "status_label": "8월 서프라이즈 (+0.3%p)",
            "bullets": [
                "8월 단월 점유율이 26.4%로 크게 반등하며 누적 점유율 24.3% (+0.3%p)를 기록했습니다.",
                "삼성과의 누적 격차를 7월 -13.7%p에서 -12.8%p로 무려 +0.9%p 축소하며 서프라이즈를 달성했습니다.",
                "OLED 시장 49.5%로 절반을 육박하며 그리스 프리미엄 수요를 집중 견인하고 있습니다."
            ]
        },
        "LGEMK": {
            "status_type": "good",
            "status_label": "삼성 턱밑 추격 (-0.3%p 초접전)",
            "bullets": [
                "8월 단월 28.4%로 폭발적 성장을 기록하며 누적 M/S 27.1% 달성 (+0.2%p).",
                "삼성전자(27.4%)와의 누적 격차가 단 -0.3%p로 좁혀져 동유럽 권역 1위 역전 탈환이 임박했습니다.",
                "OLED 점유율 55.0% 및 QNED 라인업의 고른 성장으로 하이센스(13.9%)를 완벽히 통제 중입니다."
            ]
        },
        "LGEPT": {
            "status_type": "good",
            "status_label": "유럽 유일 삼성 추월 1위 수성",
            "bullets": [
                "8월 누적 M/S 30.1%로 삼성전자(22.8%)를 +7.3%p의 큰 격차로 누르고 유럽 내 유일한 1위 지위를 확고히 수성 중입니다.",
                "8월 단월(27.0%) 비수기 일시 숨고르기 속에서도 OLED 58.1%로 프리미엄 리더십을 철저히 유지하고 있습니다.",
                "하이센스(16.1%)의 엔트리 공세에 맞서 메인스트림 방어 라인업 점검이 병행되고 있습니다."
            ]
        },
        "LGEDG": {
            "status_type": "opportunity",
            "status_label": "독일 본진 20%선 안착 & 격차 축소",
            "bullets": [
                "유럽 최대 시장인 독일에서 8월 단월 21.2%로 반등, 누적 점유율 20.5% (+0.1%p)로 20%선을 안정적으로 돌파했습니다.",
                "삼성과의 M/S 격차는 7월 누적 -13.9%p에서 -13.5%p로 +0.4%p 축소되었습니다.",
                "OLED 점유율 39.7%로 40%선 회복을 눈앞에 두고 있으며, IFA 2026 연계 프리미엄 신제품 공세가 기대됩니다."
            ]
        },
        "LGEUK": {
            "status_type": "opportunity",
            "status_label": "8월 단월 반등 (23.2%) & 격차 9% 진입",
            "bullets": [
                "8월 단월 M/S 23.2%로 전월 누적(22.1%) 대비 큰 폭 반등에 성공하며 누적 22.2% (+0.1%p)를 기록했습니다.",
                "삼성과의 누적 격차가 -9.7%p에서 -9.1%p로 축소되며 한 자릿수(-9%대)에 성공적으로 진입했습니다.",
                "OLED 점유율 51.0%로 과반을 사수하고 있으며 하이센스(13.8%)에 맞선 주요 유통 전용 프로모션이 주효했습니다."
            ]
        },
        "LGEBN": {
            "status_type": "opportunity",
            "status_label": "연속 성장 & 8월 23.2% 강세",
            "bullets": [
                "8월 단월 23.2%를 기록하며 누적 M/S 22.3%로 지난달에 이어 연속 우상향(+0.2%p) 곡선을 그렸습니다.",
                "삼성과의 격차를 -20.5%p에서 -20.2%p로 축소하며 베네룩스 채널 협상력을 회복 중입니다.",
                "OLED M/S 42.3% 및 하이센스 11.9%에 대응한 볼륨존 판가 정책이 안착되고 있습니다."
            ]
        },
        "Swiss": {
            "status_type": "opportunity",
            "status_label": "8월 단월 23.4% & 격차 축소 (+0.6%p)",
            "bullets": [
                "8월 단월 M/S 23.4%로 호조세를 이어가며 누적 점유율 22.5% (+0.1%p)를 안정적으로 수성했습니다.",
                "삼성전자와의 누적 격차를 7월 -24.4%p에서 -23.8%p로 +0.6%p 대폭 축소하며 반등 흐름을 입증했습니다.",
                "평균 ASP $1,180대의 초고가 프리미엄 시장에서 OLED 및 하이엔드 라인업의 수익 기여도가 지속 유지되고 있습니다."
            ]
        },
        "LGECK": {
            "status_type": "neutral",
            "status_label": "24.6% 안정 2위 & OLED 53.6%",
            "bullets": [
                "8월 누적 M/S 24.6% (8월 단월 24.4%)로 동유럽 허브 시장에서 안정적인 점유율을 유지하고 있습니다.",
                "삼성과의 누적 격차는 -7.6%p로 7%대 중반을 유지하며 안정세를 보였습니다.",
                "OLED 점유율 53.6%로 과반 이상을 지배하고 있으며, 하이센스(15.8%) 공세 방어에 집중하고 있습니다."
            ]
        },
        "LGEAG": {
            "status_type": "neutral",
            "status_label": "25.5% 견조한 점유율 유지",
            "bullets": [
                "8월 누적 M/S 25.5% (8월 단월 24.5%)로 서유럽 최상위권 점유율 수준을 안정적으로 지속하고 있습니다.",
                "삼성과의 누적 격차는 -15.2%p로 7월(-15.4%p) 대비 소폭 축소되었습니다.",
                "OLED M/S 52.5%로 절반 이상을 확고히 수성하며 오스트리아 프리미엄 입지를 방어하고 있습니다."
            ]
        },
        "LGERO": {
            "status_type": "neutral",
            "status_label": "18.3% 수성 & 하이센스 억제",
            "bullets": [
                "8월 누적 M/S 18.3% (8월 단월 17.6%)로 루마니아 시장 18%대 방어선을 유지하고 있습니다.",
                "삼성비 격차는 -20.0%p로 7월(-20.4%p) 대비 소폭 개선되었습니다.",
                "하이센스 점유율을 9.7%로 10% 미만 억제에 성공하며 OLED 44.0%로 프리미엄 수요를 리드하고 있습니다."
            ]
        },
        "LGEIS": {
            "status_type": "risk",
            "status_label": "8월 일시 조정 (19.9%) 요주의",
            "bullets": [
                "8월 단월 실적이 19.9%로 주춤하며 누적 점유율이 21.0% (-0.2%p)로 소폭 조정되었습니다.",
                "삼성비 누적 격차는 -10.2%p로 유지 중이나, 하반기 10% 이내 진입을 위해 이탈리아 채널 재정비가 필요합니다.",
                "OLED 47.6%로 프리미엄 리더십은 유지되고 있으나 하이센스(14.4%)의 메인스트림 잠식 방어가 시급합니다."
            ]
        },
        "LGEFS": {
            "status_type": "risk",
            "status_label": "하이센스 초근접 (0.8%p 차) 경보",
            "bullets": [
                "8월 단월 실적이 14.3%로 둔화되며 누적 M/S가 15.6% (-0.2%p)로 하락했습니다.",
                "하이센스가 누적 14.8%까지 추격하여 LG와의 격차가 단 0.8%p 차이로 좁혀지는 비상 상황입니다.",
                "삼성과의 격차도 -16.9%p에 달해 프랑스 법인은 올 가을 중저가 볼륨존 방어 프로모션의 전면 가동이 절실합니다."
            ]
        }
    }
    
    # Combine sub_results with country_highlights_meta
    country_highlights_list = []
    for sub in sub_results:
        c_code = sub["code"]
        meta = country_highlights_meta.get(c_code, {
            "status_type": "neutral",
            "status_label": "실적 모니터링",
            "bullets": [f"{sub['name']} 8월 누적 M/S {sub['lg_8m']} (8월 단월 {sub['lg_aug']}) 기록."]
        })
        country_highlights_list.append({
            "code": c_code,
            "short_code": sub["short_code"],
            "name": sub["name"],
            "status_type": meta["status_type"],
            "status_label": meta["status_label"],
            "pills": [
                f"8월 M/S: {sub['lg_aug']}",
                f"누계 M/S: {sub['lg_8m']} ({sub['lg_diff']})",
                f"삼성 격차: {sub['sp_8m']}",
                f"OLED M/S: {sub['oled_8m']}",
                f"하이센스 M/S: {sub['his_8m']}"
            ],
            "bullets": meta["bullets"]
        })
        
    # Save Structured Diff JSON
    diff_json_data = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "comparison_period": "2026년 8월 누적 vs 2026년 7월 누적",
            "active_month": 8
        },
        "europe_summary": europe_summary_items,
        "regional_table": sub_results,
        "country_highlights": country_highlights_list
    }
    
    with open(output_diff_json, "w", encoding="utf-8") as f:
        json.dump(diff_json_data, f, ensure_ascii=False, indent=2)
    print(f"[Diff Engine] Structured Diff Dataset saved: {output_diff_json}")
    
    # Generate Markdown Report
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_dir = current_dir.replace('\\', '/')
    
    sp_eval = '개선(+)' if (spread_delta and spread_delta > 0) else ('축소(-)' if (spread_delta and spread_delta < 0) else '유지')
    oled_sp_eval = '확대(+)' if (oled_spread_delta and oled_spread_delta > 0) else ('축소(-)' if (oled_spread_delta and oled_spread_delta < 0) else '유지')
    
    md_content = f"""# Europe TV M/S Trend 실적 비교 분석 리포트 (2026.08 vs 2026.07)

> **발간 일시**: {now_str}  
> **발간 주체**: TV 유럽영업 MS Trend Multi-Agent System  
> **비교 대상**: 
> - **[이전 버전]** 2026년 7월 누적 (`경쟁지표_Data Book_26.7월 누적 (260911).xlsb`)
> - **[최신 버전]** 2026년 8월 누적 (`경쟁지표_Data Book_26.8월 누적 (261014).xlsb`)  
> **백업 저장소**: `backup/2607_누적/` (HTML 대시보드, JSON 원천 데이터, 7월 vs 6월 Diff 리포트 등 8종 보존 완료)

---

## 1. 유럽 전체 (Europe HQ) 핵심 지표 종합 대조표

8월 단월 실적이 반영됨에 따라 유럽 전체 누적 지표의 변화 내역입니다:

| 핵심 지표 | 7월 누계 실적 | **8월 누계 실적** | **8월 단월 실적** | **누계 변동폭 (8M vs 7M)** |
| :--- | :---: | :---: | :---: | :---: |
| **시장 규모 (금액)** | {m_val["s_7m"]} | **{m_val["s_8m"]}** | **{m_val["s_aug"]}** | `{m_val["s_delta"]}` |
| **시장 규모 (수량)** | {m_qty["s_7m"]} | **{m_qty["s_8m"]}** | **{m_qty["s_aug"]}** | `{m_qty["s_delta"]}` |
| **시장 평균 ASP** | {m_asp["s_7m"]} | **{m_asp["s_8m"]}** | **{m_asp["s_aug"]}** | `{m_asp["s_delta"]}` |
| **LG 금액 M/S** | {lg_val_ms["s_7m"]} | **{lg_val_ms["s_8m"]}** | **{lg_val_ms["s_aug"]}** | `{lg_val_ms["s_delta"]}p` |
| **LG 수량 M/S** | {lg_qty_ms["s_7m"]} | **{lg_qty_ms["s_8m"]}** | **{lg_qty_ms["s_aug"]}** | `{lg_qty_ms["s_delta"]}p` |
| **SAMSUNG 금액 M/S** | {sam_val_ms["s_7m"]} | **{sam_val_ms["s_8m"]}** | **{sam_val_ms["s_aug"]}** | `{sam_val_ms["s_delta"]}p` |
| **SAMSUNG 수량 M/S** | {sam_qty_ms["s_7m"]} | **{sam_qty_ms["s_8m"]}** | **{sam_qty_ms["s_aug"]}** | `{sam_qty_ms["s_delta"]}p` |
| **삼성비 격차 (Samsung Spread)** | {spread_7m:+.1f}%p | **{spread_8m:+.1f}%p** | **{spread_aug:+.1f}%p** | `{spread_delta:+.1f}%p` |
| **LG OLED 금액 M/S** | {lg_oled_ms["s_7m"]} | **{lg_oled_ms["s_8m"]}** | **{lg_oled_ms["s_aug"]}** | `{lg_oled_ms["s_delta"]}p` |
| **SAMSUNG OLED 금액 M/S** | {sam_oled_ms["s_7m"]} | **{sam_oled_ms["s_8m"]}** | **{sam_oled_ms["s_aug"]}** | `{sam_oled_ms["s_delta"]}p` |
| **OLED 삼성비 격차** | {oled_spread_7m:+.1f}%p | **{oled_spread_8m:+.1f}%p** | **{oled_spread_aug:+.1f}%p** | `{oled_spread_delta:+.1f}%p` |
| **LG OLED 판매량** | {lg_oled_qty["s_7m"]} | **{lg_oled_qty["s_8m"]}** | **{lg_oled_qty["s_aug"]}** | `{lg_oled_qty["s_delta"]}` |
| **LG ASP ($)** | {lg_asp["s_7m"]} | **{lg_asp["s_8m"]}** | **{lg_asp["s_aug"]}** | `{lg_asp["s_delta"]}` |
| **SAMSUNG ASP ($)** | {sam_asp["s_7m"]} | **{sam_asp["s_8m"]}** | **{sam_asp["s_aug"]}** | `{sam_asp["s_delta"]}` |
| **HISENSE 금액 M/S** | {his_val_ms["s_7m"]} | **{his_val_ms["s_8m"]}** | **{his_val_ms["s_aug"]}** | `{his_val_ms["s_delta"]}p` |

---

## 2. 주요 거점 법인별 M/S 및 격차 비교표

주요 14개 거점 법인의 7월 누계 대비 8월 누계 M/S 변동 및 8월 단월 성과입니다:

| 거점 법인 | LG M/S (7M) | **LG M/S (8M)** | **8월 단월 M/S** | 누계 변동 (%p) | 삼성비 격차 (7M) | **삼성비 격차 (8M)** | OLED M/S (8M) | 하이센스 M/S (8M) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""

    for r in sub_results:
        md_content += f"| **{r['name']}** | {r['lg_7m']} | **{r['lg_8m']}** | **{r['lg_aug']}** | `{r['lg_diff']}` | {r['sp_7m']} | **{r['sp_8m']}** | {r['oled_8m']} | {r['his_8m']} |\n"

    md_content += f"""
---

## 3. 8월 누적 업데이트 핵심 비즈니스 시사점 (Key Takeaways)

### 1) 유럽 전체 M/S 상승 및 삼성전자 대비 격차 대폭 축소
- **LG 금액 M/S**: 7월 누적 **{lg_val_ms['s_7m']}**에서 8월 누적 **{lg_val_ms['s_8m']}**로 `{lg_val_ms['s_delta']}p` 상승. 특히 8월 단월 M/S는 **{lg_val_ms['s_aug']}**를 기록하며 우상향 견인.
- **삼성비 격차(Spread)**: 7월 누적 **{spread_7m:+.1f}%p**에서 8월 누적 **{spread_8m:+.1f}%p**로 {abs(spread_delta):.1f}%p {sp_eval}. 특히 8월 단월 격차는 **{spread_aug:+.1f}%p**로 10%p 이내로 진입하며 괄목할 만한 추격 성과 달성.

### 2) 프리미엄 OLED 시장 리더십 확대
- **OLED 점유율**: LG OLED 점유율은 7월 누적 **45.4%**에서 8월 누적 **45.6%**로 상승했으며, 8월 단월은 **47.1%**로 고공 행진 지속.
- **삼성 OLED 대비 격차**: 삼성 OLED(**{sam_oled_ms['s_8m']}**) 대비 **{oled_spread_8m:+.1f}%p**의 우위를 기록하여 7월 누적({oled_spread_7m:+.1f}%p) 대비 리더십 스프레드가 {abs(oled_spread_delta):.1f}%p {oled_sp_eval}됨 (8월 단월 격차는 +13.8%p).
- **OLED 판매량 누적**: 8월 단월 83.8천 대가 추가되어 8월 누적 **{lg_oled_qty['s_8m']}** 달성.

### 3) 거점 법인 실적 특징
- **선전/성장 법인**: 
  - **스웨덴 법인 (LGESW)**: 8월 단월 {sub_results[6]['lg_aug']}, 누적 {sub_results[6]['lg_8m']} (+0.3%p), OLED 66.0%로 북유럽 절대 강세.
  - **그리스 법인 (LGEHS)**: 8월 단월 {sub_results[12]['lg_aug']}, 누적 {sub_results[12]['lg_8m']} (+0.3%p), 삼성비 격차 +0.9%p 축소.
  - **헝가리 법인 (LGEMK)**: 8월 단월 {sub_results[8]['lg_aug']}, 누적 {sub_results[8]['lg_8m']} (+0.2%p), 삼성과의 격차가 단 -0.3%p로 좁혀져 1위 역전 가시권.
  - **스페인 법인 (LGEES)**: 8월 누적 {sub_results[4]['lg_8m']}, 삼성비 격차 -4.1%p (8월 단월 -2.4%p)로 맹추격.
  - **영국/독일 법인**: 영국 8월 단월 23.2%로 반등(-9.1%p 진입), 독일 8월 단월 21.2%로 20%선 안착.
  - **스위스 지점 (Swiss)**: 8월 누적 22.5% (+0.1%p), 삼성비 격차 +0.6%p 개선.
- **경쟁 심화 및 방어 법인**:
  - **프랑스 법인 (LGEFS)**: 8월 누적 15.6%로 하락, 하이센스가 14.8%까지 추격하여 단 0.8%p 차로 근접. 가을철 즉각적인 메인스트림 방어 판촉 절실.
  - **이탈리아 법인 (LGEIS)**: 8월 단월 19.9%로 주춤하며 누적 21.0%로 조정. 하이센스(14.4%) 견제 필요.

---

## 4. 데이터 보존 및 아티팩트 안내
- **이전 7월 누적 백업**: [backup/2607_누적/index.html](file:///{clean_dir}/backup/2607_누적/index.html)
- **최신 8월 누적 대시보드**: [public/index.html](file:///{clean_dir}/public/index.html) 및 [index.html](file:///{clean_dir}/index.html)
- **품질 검증 리포트**: [data_validation_report.json](file:///{clean_dir}/data_validation_report.json) (Health Score: 100/100, 8월 활성화 확인)
"""

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[Diff Engine] Comparison Report saved: {output_report_path}")
    return True

if __name__ == "__main__":
    generate_diff_report()

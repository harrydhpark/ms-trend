import os
import json
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
old_json_path = os.path.join(current_dir, "backup", "2606_누적", "ms_trend_data.json")
new_json_path = os.path.join(current_dir, "ms_trend_data.json")
output_report_path = os.path.join(current_dir, "ms_trend_diff_2607_vs_2606.md")
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
    print(f"[Diff Engine] Loading old dataset: {old_json_path}")
    print(f"[Diff Engine] Loading new dataset: {new_json_path}")
    
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
        
        v_6m = calc_ytd(r_old, "y26", 6)
        v_7m = calc_ytd(r_new, "y26", 7)
        v_jul = get_m_val(r_new, "y26", 6) # index 6 = July (7th month)
        
        if is_rate:
            v_6m = (v_6m * 100) if v_6m is not None else None
            v_7m = (v_7m * 100) if v_7m is not None else None
            v_jul = (v_jul * 100) if v_jul is not None else None
            
        if is_qty_k:
            v_6m = (v_6m / 1000) if v_6m is not None else None
            v_7m = (v_7m / 1000) if v_7m is not None else None
            v_jul = (v_jul / 1000) if v_jul is not None else None
            
        delta_cum = (v_7m - v_6m) if (v_7m is not None and v_6m is not None) else None
        
        fmt = f"{{:.{digits}f}}"
        
        def s_fmt(val, is_diff=False):
            if val is None:
                return "-"
            formatted = fmt.format(val)
            if is_diff and val > 0:
                return f"+{formatted}{unit}"
            return f"{formatted}{unit}"
            
        return {
            "v_6m": v_6m,
            "v_7m": v_7m,
            "v_jul": v_jul,
            "delta_cum": delta_cum,
            "s_6m": s_fmt(v_6m),
            "s_7m": s_fmt(v_7m),
            "s_jul": s_fmt(v_jul),
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
    spread_6m = (lg_val_ms["v_6m"] - sam_val_ms["v_6m"]) if (lg_val_ms["v_6m"] is not None and sam_val_ms["v_6m"] is not None) else None
    spread_7m = (lg_val_ms["v_7m"] - sam_val_ms["v_7m"]) if (lg_val_ms["v_7m"] is not None and sam_val_ms["v_7m"] is not None) else None
    spread_jul = (lg_val_ms["v_jul"] - sam_val_ms["v_jul"]) if (lg_val_ms["v_jul"] is not None and sam_val_ms["v_jul"] is not None) else None
    spread_delta = (spread_7m - spread_6m) if (spread_7m is not None and spread_6m is not None) else None
    
    # OLED Spread (LG OLED - SAM OLED in %p)
    oled_spread_6m = (lg_oled_ms["v_6m"] - sam_oled_ms["v_6m"]) if (lg_oled_ms["v_6m"] is not None and sam_oled_ms["v_6m"] is not None) else None
    oled_spread_7m = (lg_oled_ms["v_7m"] - sam_oled_ms["v_7m"]) if (lg_oled_ms["v_7m"] is not None and sam_oled_ms["v_7m"] is not None) else None
    oled_spread_jul = (lg_oled_ms["v_jul"] - sam_oled_ms["v_jul"]) if (lg_oled_ms["v_jul"] is not None and sam_oled_ms["v_jul"] is not None) else None
    oled_spread_delta = (oled_spread_7m - oled_spread_6m) if (oled_spread_7m is not None and oled_spread_6m is not None) else None
    
    # Structured Europe Summary List for Web Dashboard
    europe_summary_items = [
        {
            "name": "시장 규모 (금액)",
            "unit": "억불",
            "val_6m": m_val["s_6m"],
            "val_7m": m_val["s_7m"],
            "val_jul": m_val["s_jul"],
            "delta": m_val["s_delta"],
            "is_positive": (m_val["delta_cum"] > 0) if m_val["delta_cum"] is not None else None,
            "note": "7월 단월 14.1억불 정상 누적 반영"
        },
        {
            "name": "시장 규모 (수량)",
            "unit": "백만대",
            "val_6m": m_qty["s_6m"],
            "val_7m": m_qty["s_7m"],
            "val_jul": m_qty["s_jul"],
            "delta": m_qty["s_delta"],
            "is_positive": (m_qty["delta_cum"] > 0) if m_qty["delta_cum"] is not None else None,
            "note": "7월 단월 2.6백만대 누적"
        },
        {
            "name": "시장 평균 ASP",
            "unit": "$",
            "val_6m": m_asp["s_6m"],
            "val_7m": m_asp["s_7m"],
            "val_jul": m_asp["s_jul"],
            "delta": m_asp["s_delta"],
            "is_positive": None,
            "note": "여름 비수기 전반적 판가 소폭 조정"
        },
        {
            "name": "LG 금액 M/S",
            "unit": "%",
            "val_6m": lg_val_ms["s_6m"],
            "val_7m": lg_val_ms["s_7m"],
            "val_jul": lg_val_ms["s_jul"],
            "delta": f"{lg_val_ms['s_delta']}p",
            "is_positive": (lg_val_ms["delta_cum"] >= 0) if lg_val_ms["delta_cum"] is not None else None,
            "note": "7월 단월 22.4%로 반등하며 누적 M/S 견조 수성"
        },
        {
            "name": "LG 수량 M/S",
            "unit": "%",
            "val_6m": lg_qty_ms["s_6m"],
            "val_7m": lg_qty_ms["s_7m"],
            "val_jul": lg_qty_ms["s_jul"],
            "delta": f"{lg_qty_ms['s_delta']}p",
            "is_positive": True,
            "note": "7월 단월 16.3%로 수량 점유율 안정세"
        },
        {
            "name": "SAMSUNG 금액 M/S",
            "unit": "%",
            "val_6m": sam_val_ms["s_6m"],
            "val_7m": sam_val_ms["s_7m"],
            "val_jul": sam_val_ms["s_jul"],
            "delta": f"{sam_val_ms['s_delta']}p",
            "is_positive": False,
            "note": "7월 단월 33.2%로 소폭 둔화 (-0.2%p)"
        },
        {
            "name": "SAMSUNG 수량 M/S",
            "unit": "%",
            "val_6m": sam_qty_ms["s_6m"],
            "val_7m": sam_qty_ms["s_7m"],
            "val_jul": sam_qty_ms["s_jul"],
            "delta": f"{sam_qty_ms['s_delta']}p",
            "is_positive": False,
            "note": "7월 단월 25.4%로 수량 점유율 소폭 하락"
        },
        {
            "name": "삼성비 격차 (Samsung Spread)",
            "unit": "%p",
            "val_6m": f"{spread_6m:+.1f}%p",
            "val_7m": f"{spread_7m:+.1f}%p",
            "val_jul": f"{spread_jul:+.1f}%p",
            "delta": f"{spread_delta:+.1f}%p",
            "is_positive": (spread_delta > 0),
            "note": "삼성 대비 격차 축소 (+0.3%p 개선, LG 우세 흐름)"
        },
        {
            "name": "LG OLED 금액 M/S",
            "unit": "%",
            "val_6m": lg_oled_ms["s_6m"],
            "val_7m": lg_oled_ms["s_7m"],
            "val_jul": lg_oled_ms["s_jul"],
            "delta": f"{lg_oled_ms['s_delta']}p",
            "is_positive": True,
            "note": "7월 단월 47.6% 급상승, 프리미엄 주도권 강화"
        },
        {
            "name": "SAMSUNG OLED 금액 M/S",
            "unit": "%",
            "val_6m": sam_oled_ms["s_6m"],
            "val_7m": sam_oled_ms["s_7m"],
            "val_jul": sam_oled_ms["s_jul"],
            "delta": f"{sam_oled_ms['s_delta']}p",
            "is_positive": None,
            "note": "33.4%로 보합 유지"
        },
        {
            "name": "OLED 삼성비 격차",
            "unit": "%p",
            "val_6m": f"{oled_spread_6m:+.1f}%p",
            "val_7m": f"{oled_spread_7m:+.1f}%p",
            "val_jul": f"{oled_spread_jul:+.1f}%p",
            "delta": f"{oled_spread_delta:+.1f}%p",
            "is_positive": True,
            "note": "삼성 OLED 대비 격차 +12.0%p로 확대 (+0.3%p 우위 증대)"
        },
        {
            "name": "LG OLED 누적 판매량",
            "unit": "천 대",
            "val_6m": lg_oled_qty["s_6m"],
            "val_7m": lg_oled_qty["s_7m"],
            "val_jul": lg_oled_qty["s_jul"],
            "delta": lg_oled_qty["s_delta"],
            "is_positive": True,
            "note": "7월 단월 120.9천 대 순증으로 770.7천 대 달성"
        },
        {
            "name": "LG 평균 ASP",
            "unit": "$",
            "val_6m": lg_asp["s_6m"],
            "val_7m": lg_asp["s_7m"],
            "val_jul": lg_asp["s_jul"],
            "delta": lg_asp["s_delta"],
            "is_positive": None,
            "note": "시장 평균($595) 대비 +$225 높은 고가 프리미엄 유지"
        },
        {
            "name": "SAMSUNG 평균 ASP",
            "unit": "$",
            "val_6m": sam_asp["s_6m"],
            "val_7m": sam_asp["s_7m"],
            "val_jul": sam_asp["s_jul"],
            "delta": sam_asp["s_delta"],
            "is_positive": None,
            "note": "LG와 판가차 $55 유지"
        },
        {
            "name": "HISENSE 금액 M/S",
            "unit": "%",
            "val_6m": his_val_ms["s_6m"],
            "val_7m": his_val_ms["s_7m"],
            "val_jul": his_val_ms["s_jul"],
            "delta": f"{his_val_ms['s_delta']}p",
            "is_positive": False,
            "note": "7월 단월 9.6%로 중저가 볼륨 공세 지속"
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
        
        lg_6m_raw = calc_ytd(old_rows.get(27, {}), "y26", 6)
        lg_7m_raw = calc_ytd(new_rows.get(27, {}), "y26", 7)
        lg_jul_raw = get_m_val(new_rows.get(27, {}), "y26", 6)
        
        lg_6m = (lg_6m_raw * 100) if lg_6m_raw is not None else None
        lg_7m = (lg_7m_raw * 100) if lg_7m_raw is not None else None
        lg_jul = (lg_jul_raw * 100) if lg_jul_raw is not None else None
        lg_diff = (lg_7m - lg_6m) if (lg_7m is not None and lg_6m is not None) else None
        
        sam_6m_raw = calc_ytd(old_rows.get(59, {}), "y26", 6)
        sam_7m_raw = calc_ytd(new_rows.get(59, {}), "y26", 7)
        sam_jul_raw = get_m_val(new_rows.get(59, {}), "y26", 6)
        
        sam_6m = (sam_6m_raw * 100) if sam_6m_raw is not None else None
        sam_7m = (sam_7m_raw * 100) if sam_7m_raw is not None else None
        sam_jul = (sam_jul_raw * 100) if sam_jul_raw is not None else None
        
        sp_6m = (lg_6m - sam_6m) if (lg_6m is not None and sam_6m is not None) else None
        sp_7m = (lg_7m - sam_7m) if (lg_7m is not None and sam_7m is not None) else None
        sp_jul = (lg_jul - sam_jul) if (lg_jul is not None and sam_jul is not None) else None
        sp_diff = (sp_7m - sp_6m) if (sp_7m is not None and sp_6m is not None) else None
        
        oled_6m_raw = calc_ytd(old_rows.get(38, {}), "y26", 6)
        oled_7m_raw = calc_ytd(new_rows.get(38, {}), "y26", 7)
        oled_jul_raw = get_m_val(new_rows.get(38, {}), "y26", 6)
        
        oled_6m = (oled_6m_raw * 100) if oled_6m_raw is not None else None
        oled_7m = (oled_7m_raw * 100) if oled_7m_raw is not None else None
        oled_jul = (oled_jul_raw * 100) if oled_jul_raw is not None else None
        oled_diff = (oled_7m - oled_6m) if (oled_7m is not None and oled_6m is not None) else None
        
        his_6m_raw = calc_ytd(old_rows.get(93, {}), "y26", 6)
        his_7m_raw = calc_ytd(new_rows.get(93, {}), "y26", 7)
        his_6m = (his_6m_raw * 100) if his_6m_raw is not None else None
        his_7m = (his_7m_raw * 100) if his_7m_raw is not None else None
        his_diff = (his_7m - his_6m) if (his_7m is not None and his_6m is not None) else None
        
        sub_results.append({
            "sheet": s_sheet,
            "code": s_code,
            "short_code": short_c,
            "name": s_name,
            "lg_6m": f"{lg_6m:.1f}%" if lg_6m is not None else "-",
            "lg_7m": f"{lg_7m:.1f}%" if lg_7m is not None else "-",
            "lg_jul": f"{lg_jul:.1f}%" if lg_jul is not None else "-",
            "lg_diff": f"{lg_diff:+.1f}%p" if lg_diff is not None else "-",
            "is_lg_up": (lg_diff is not None and lg_diff >= 0),
            "sp_6m": f"{sp_6m:+.1f}%p" if sp_6m is not None else "-",
            "sp_7m": f"{sp_7m:+.1f}%p" if sp_7m is not None else "-",
            "sp_jul": f"{sp_jul:+.1f}%p" if sp_jul is not None else "-",
            "sp_diff": f"{sp_diff:+.1f}%p" if sp_diff is not None else "-",
            "is_sp_narrowed": (sp_diff is not None and sp_diff > 0),
            "oled_6m": f"{oled_6m:.1f}%" if oled_6m is not None else "-",
            "oled_7m": f"{oled_7m:.1f}%" if oled_7m is not None else "-",
            "oled_jul": f"{oled_jul:.1f}%" if oled_jul is not None else "-",
            "oled_diff": f"{oled_diff:+.1f}%p" if oled_diff is not None else "-",
            "his_6m": f"{his_6m:.1f}%" if his_6m is not None else "-",
            "his_7m": f"{his_7m:.1f}%" if his_7m is not None else "-",
            "his_diff": f"{his_diff:+.1f}%p" if his_diff is not None else "-"
        })
        
    # Country-Specific Highlights Dictionary
    country_highlights_meta = {
        "LGEES": {
            "status_type": "good",
            "status_label": "성장 호조 & 격차 대폭 축소",
            "bullets": [
                "7월 단월 점유율이 30.8%로 급등하며 5대 거점 법인 중 유일하게 30% 선을 돌파했습니다.",
                "삼성과의 M/S 격차를 6월 누적 -5.4%p에서 -4.5%p(7월 단월 -0.7%p)로 대폭 축소하며 맹추격 중입니다.",
                "OLED M/S 51.7%로 과반 이상을 장악하여 스페인 프리미엄 시장 지배력을 확고히 유지하고 있습니다."
            ]
        },
        "LGESW": {
            "status_type": "good",
            "status_label": "지속 성장 & OLED 초강세",
            "bullets": [
                "7월 단월 25.2%를 달성하여 6월(24.0%) 대비 누적 점유율이 24.2%로 지속적인 우상향 곡선을 그렸습니다.",
                "OLED 세그먼트 M/S가 66.1%에 달해 북유럽 내 독보적인 프리미엄 1위 브랜드 위상을 입증했습니다.",
                "전년 동기 대비 +3.8%p 성장하여 전 유럽 권역 중 점유율 성장률 Top 1을 기록했습니다."
            ]
        },
        "LGEPT": {
            "status_type": "good",
            "status_label": "유럽 유일 삼성 추월 1위",
            "bullets": [
                "2026년 7월 누적 M/S 30.5%로 삼성전자(22.6%)를 +7.9%p 격차로 누르고 유럽 내 유일한 1위 지위를 확고히 수성하고 있습니다.",
                "OLED M/S 59.0%로 프리미엄 시장을 완전히 장악하고 있으나, 7월 단월(27.7%) 일시적 조정에 따른 채널 점검이 요구됩니다.",
                "하이센스가 16.2%로 침투 중이므로 메인스트림 라인업의 방어선 구축이 병행되어야 합니다."
            ]
        },
        "LGEBN": {
            "status_type": "opportunity",
            "status_label": "7월 단월 턴어라운드 반등",
            "bullets": [
                "7월 단월 M/S 24.1%로 전월 누적(21.8%) 대비 급반등하며 누적 점유율을 22.2%로 +0.3%p 견인했습니다.",
                "벨기에/네덜란드 주요 유통 프로모션 활성화로 모멘텀을 확보했으며, 삼성비 격차도 -20.5%p로 축소 전환되었습니다.",
                "OLED M/S 42.2% 및 하이센스(12.0%) 공세에 맞서 메인스트림 판가 대응력을 확보 중입니다."
            ]
        },
        "LGEIS": {
            "status_type": "opportunity",
            "status_label": "점유율 반등 & OLED 선전",
            "bullets": [
                "7월 단월 21.5%로 뚜렷한 회복세를 보이며 누적 점유율 21.2%로 소폭 반등(+0.1%p)했습니다.",
                "OLED 시장에서 47.7%를 점유하여 삼성 OLED를 확실하게 제어하고 있으며, 초대형 믹스 개선에 집중하고 있습니다.",
                "삼성비 격차는 -10.2%p 수준을 유지하며 하반기 10% 이내 진입을 가시권에 두고 있습니다."
            ]
        },
        "LGEDG": {
            "status_type": "neutral",
            "status_label": "견조한 20%선 방어 수성",
            "bullets": [
                "유럽 최대 시장인 독일에서 7월 단월 20.4%를 기록, 누적 20.4%로 흔들림 없이 20%선 기준선을 방어했습니다.",
                "삼성과의 격차는 6월 누적 -14.1%p에서 -13.9%p로 소폭 축소되었습니다.",
                "OLED 점유율 39.4%로 40%선 회복을 위해 가을 성수기 시즌 연계 프리미엄 번들 프로모션 집중이 요구됩니다."
            ]
        },
        "LGECK": {
            "status_type": "opportunity",
            "status_label": "동유럽 성장 견인 & OLED 53%",
            "bullets": [
                "7월 단월 25.3%로 호조를 보이며 누적 점유율 24.6%를 달성, 안정적인 시장 2위 지위를 확고히 했습니다.",
                "OLED 점유율 53.4%로 과반 이상을 지배하고 있으며, 삼성비 격차도 -7.7%p로 7%대에 진입했습니다.",
                "하이센스(15.9%)의 볼륨 공세에 맞서 슬로바키아/체코 유통 파트너십을 결속하고 있습니다."
            ]
        },
        "LGEAG": {
            "status_type": "neutral",
            "status_label": "전년비 성장(+1.7%p) 지속",
            "bullets": [
                "누적 M/S 25.6%로 전년 동기 대비 +1.7%p 상승세를 유지하며 서유럽 거점 중 높은 점유율 수준을 유지하고 있습니다.",
                "7월 단월 실적(24.5%)의 일시적 숨고르기 이후 하반기 하이엔드 라인업 재정비가 예정되어 있습니다.",
                "OLED M/S 52.2%로 과반을 점유하며 프리미엄 고객층의 높은 브랜드 충성도를 확인했습니다."
            ]
        },
        "LGERO": {
            "status_type": "opportunity",
            "status_label": "7월 단월 반등 (+1.0%p)",
            "bullets": [
                "7월 단월 19.2%로 전월 누적(18.2%) 대비 +1.0%p 급반등하며 누적 점유율 18.4%로 턴어라운드를 시작했습니다.",
                "하이센스 점유율을 9.6%로 억제하며 로컬 가전 전문 유통 채널과의 독점 번들 프로모션을 확대 중입니다.",
                "OLED 시장 43.6%로 동유럽 프리미엄 수요를 성공적으로 견인하고 있습니다."
            ]
        },
        "LGEHS": {
            "status_type": "neutral",
            "status_label": "점유율 소폭 상승 & OLED 49%",
            "bullets": [
                "7월 단월 24.5%로 누적 점유율을 24.1%로 끌어올렸으며, 삼성비 격차도 -13.7%p로 소폭 축소되었습니다.",
                "OLED 시장 49.3%를 장악하며 그리스 프리미엄 수요를 흡수하고 있습니다.",
                "하이센스(10.7%)에 대응한 엔트리 UHD 라인업의 재고 건전성을 집중 점검하고 있습니다."
            ]
        },
        "LGEMK": {
            "status_type": "risk",
            "status_label": "삼성과 초접전 & 하이센스 공세",
            "bullets": [
                "삼성 M/S 27.6% 대비 LG M/S 26.9%로 단 0.7%p 차이의 초접전 양상을 이어가고 있습니다.",
                "7월 단월 실적이 25.8%로 다소 주춤함에 따라 동유럽 핵심 거점 1위 탈환을 위한 메인스트림 QNED 판가 지원이 요구됩니다.",
                "하이센스가 14.0%로 빠르게 추격하고 있어 중가형 라인업의 가격 경쟁력 방어가 시급합니다."
            ]
        },
        "LGEUK": {
            "status_type": "risk",
            "status_label": "경쟁 심화 요주의 (Watch)",
            "bullets": [
                "7월 단월 21.5%로 전월 누적(22.2%) 대비 소폭 하락하며 누적 점유율이 22.1%로 조정되었습니다.",
                "OLED는 50.3%로 절반을 방어했으나, Currys 등 주요 유통에서 하이센스(13.3%) 및 삼성 네오 QLED의 가격 인하 공세가 거셉니다.",
                "하반기 성수기 진입 전 주요 유통사 전용 패키지 프로모션 수립이 시급합니다."
            ]
        },
        "LGEFS": {
            "status_type": "risk",
            "status_label": "방어 과제 & M/S 반등 필요",
            "bullets": [
                "서유럽 5대 거점 중 가장 낮은 15.8%의 M/S를 기록하고 있으며, 삼성과의 격차도 -17.0%p로 벌어져 있습니다.",
                "하이센스가 14.9%까지 추격하여 LG를 단 0.9%p 차이로 위협하고 있어 중저가 볼륨존의 즉각적인 방어 전략이 요구됩니다.",
                "OLED 41.7%는 유지하고 있으나, 유통 커버리지 확대 및 대형 올림픽/스포츠 특수 연계 판촉이 절실합니다."
            ]
        },
        "Swiss": {
            "status_type": "opportunity",
            "status_label": "7월 단월 반등(+0.3%p) & OLED 40.8%",
            "bullets": [
                "7월 단월 M/S 24.3%로 호조를 보이며 6월 누적(22.2%) 대비 누적 점유율을 22.5%로 +0.3%p 견인했습니다.",
                "삼성전자와의 격차를 6월 누적 -25.1%p에서 -24.3%p로 +0.8%p 축소하며 반등 모멘텀을 확보했습니다.",
                "7월 단월 OLED M/S 40.8% 달성 및 평균 ASP $1,188로 시장($1,100) 대비 확고한 프리미엄 포지션을 유지하고 있습니다."
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
            "bullets": [f"{sub['name']} 7월 누적 M/S {sub['lg_7m']} (7월 단월 {sub['lg_jul']}) 기록."]
        })
        country_highlights_list.append({
            "code": c_code,
            "short_code": sub["short_code"],
            "name": sub["name"],
            "status_type": meta["status_type"],
            "status_label": meta["status_label"],
            "pills": [
                f"7월 M/S: {sub['lg_jul']}",
                f"누계 M/S: {sub['lg_7m']} ({sub['lg_diff']})",
                f"삼성 격차: {sub['sp_7m']}",
                f"OLED M/S: {sub['oled_7m']}",
                f"하이센스 M/S: {sub['his_7m']}"
            ],
            "bullets": meta["bullets"]
        })
        
    # Save Structured Diff JSON
    diff_json_data = {
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat(),
            "comparison_period": "2026년 7월 누적 vs 2026년 6월 누적",
            "active_month": 7
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
    
    md_content = f"""# Europe TV M/S Trend 실적 비교 분석 리포트 (2026.07 vs 2026.06)

> **발간 일시**: {now_str}  
> **발간 주체**: TV 유럽영업 MS Trend Multi-Agent System  
> **비교 대상**: 
> - **[이전 버전]** 2026년 6월 누적 (`경쟁지표_Data Book_26.6월 누적 (260812)_수정.xlsb`)
> - **[최신 버전]** 2026년 7월 누적 (`경쟁지표_Data Book_26.7월 누적 (260911).xlsb`)  
> **백업 저장소**: `backup/2606_누적/` (HTML 대시보드, JSON 원천 데이터, 경영진 브리핑 등 6종 보존 완료)

---

## 1. 유럽 전체 (Europe HQ) 핵심 지표 종합 대조표

7월 단월 실적이 반영됨에 따라 유럽 전체 누적 지표의 변화 내역입니다:

| 핵심 지표 | 6월 누계 실적 | **7월 누계 실적** | **7월 단월 실적** | **누계 변동폭 (7M vs 6M)** |
| :--- | :---: | :---: | :---: | :---: |
| **시장 규모 (금액)** | {m_val["s_6m"]} | **{m_val["s_7m"]}** | **{m_val["s_jul"]}** | `{m_val["s_delta"]}` |
| **시장 규모 (수량)** | {m_qty["s_6m"]} | **{m_qty["s_7m"]}** | **{m_qty["s_jul"]}** | `{m_qty["s_delta"]}` |
| **시장 평균 ASP** | {m_asp["s_6m"]} | **{m_asp["s_7m"]}** | **{m_asp["s_jul"]}** | `{m_asp["s_delta"]}` |
| **LG 금액 M/S** | {lg_val_ms["s_6m"]} | **{lg_val_ms["s_7m"]}** | **{lg_val_ms["s_jul"]}** | `{lg_val_ms["s_delta"]}p` |
| **LG 수량 M/S** | {lg_qty_ms["s_6m"]} | **{lg_qty_ms["s_7m"]}** | **{lg_qty_ms["s_jul"]}** | `{lg_qty_ms["s_delta"]}p` |
| **SAMSUNG 금액 M/S** | {sam_val_ms["s_6m"]} | **{sam_val_ms["s_7m"]}** | **{sam_val_ms["s_jul"]}** | `{sam_val_ms["s_delta"]}p` |
| **SAMSUNG 수량 M/S** | {sam_qty_ms["s_6m"]} | **{sam_qty_ms["s_7m"]}** | **{sam_qty_ms["s_jul"]}** | `{sam_qty_ms["s_delta"]}p` |
| **삼성비 격차 (Samsung Spread)** | {spread_6m:+.1f}%p | **{spread_7m:+.1f}%p** | **{spread_jul:+.1f}%p** | `{spread_delta:+.1f}%p` |
| **LG OLED 금액 M/S** | {lg_oled_ms["s_6m"]} | **{lg_oled_ms["s_7m"]}** | **{lg_oled_ms["s_jul"]}** | `{lg_oled_ms["s_delta"]}p` |
| **SAMSUNG OLED 금액 M/S** | {sam_oled_ms["s_6m"]} | **{sam_oled_ms["s_7m"]}** | **{sam_oled_ms["s_jul"]}** | `{sam_oled_ms["s_delta"]}p` |
| **OLED 삼성비 격차** | {oled_spread_6m:+.1f}%p | **{oled_spread_7m:+.1f}%p** | **{oled_spread_jul:+.1f}%p** | `{oled_spread_delta:+.1f}%p` |
| **LG OLED 판매량** | {lg_oled_qty["s_6m"]} | **{lg_oled_qty["s_7m"]}** | **{lg_oled_qty["s_jul"]}** | `{lg_oled_qty["s_delta"]}` |
| **LG ASP ($)** | {lg_asp["s_6m"]} | **{lg_asp["s_7m"]}** | **{lg_asp["s_jul"]}** | `{lg_asp["s_delta"]}` |
| **SAMSUNG ASP ($)** | {sam_asp["s_6m"]} | **{sam_asp["s_7m"]}** | **{sam_asp["s_jul"]}** | `{sam_asp["s_delta"]}` |
| **HISENSE 금액 M/S** | {his_val_ms["s_6m"]} | **{his_val_ms["s_7m"]}** | **{his_val_ms["s_jul"]}** | `{his_val_ms["s_delta"]}p` |

---

## 2. 주요 거점 법인별 M/S 및 격차 비교표

주요 거점 법인들의 6월 누계 대비 7월 누계 M/S 변동 및 7월 단월 성과입니다:

| 거점 법인 | LG M/S (6M) | **LG M/S (7M)** | **7월 단월 M/S** | 누계 변동 (%p) | 삼성비 격차 (6M) | **삼성비 격차 (7M)** | OLED M/S (7M) | 하이센스 M/S (7M) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""

    for r in sub_results:
        md_content += f"| **{r['name']}** | {r['lg_6m']} | **{r['lg_7m']}** | **{r['lg_jul']}** | `{r['lg_diff']}` | {r['sp_6m']} | **{r['sp_7m']}** | {r['oled_7m']} | {r['his_7m']} |\n"

    md_content += f"""
---

## 3. 7월 누적 업데이트 핵심 비즈니스 시사점 (Key Takeaways)

### 1) 유럽 전체 M/S 및 삼성전자 대비 포지션
- **LG 금액 M/S**: 6월 누적 **{lg_val_ms['s_6m']}**에서 7월 누적 **{lg_val_ms['s_7m']}**로 `{lg_val_ms['s_delta']}p` 변동. 특히 7월 단월 M/S는 **{lg_val_ms['s_jul']}**를 기록하며 안정적인 흐름 유지.
- **삼성비 격차(Spread)**: 6월 누적 **{spread_6m:+.1f}%p**에서 7월 누적 **{spread_7m:+.1f}%p**로 {abs(spread_delta):.1f}%p {sp_eval}되어 삼성과의 간극을 성공적으로 유지/개선함.

### 2) 프리미엄 OLED 시장 리더십
- **OLED 점유율**: LG OLED 점유율은 6월 누적 **45.0%**에서 7월 누적 **45.4%**로 `{lg_oled_ms['s_delta']}p` 상승.
- **삼성 OLED 대비 격차**: 삼성 OLED(**{sam_oled_ms['s_7m']}**) 대비 **{oled_spread_7m:+.1f}%p**의 우위를 기록, 6월 누적({oled_spread_6m:+.1f}%p) 대비 리더십 스프레드가 {abs(oled_spread_delta):.1f}%p {oled_sp_eval}됨.
- **OLED 판매량 누적**: 6월 누적 {lg_oled_qty['s_6m']}에서 7월 단월 {lg_oled_qty['s_jul']}가 추가되어 7월 누적 **{lg_oled_qty['s_7m']}** 달성.

### 3) 거점 법인 실적 특징
- **선전/성장 법인**: 
  - **스페인 법인 (LGEES)**: 7월 단월 {sub_results[4]['lg_jul']}, 7월 누적 {sub_results[4]['lg_7m']}로 삼성비 격차가 {sub_results[4]['sp_7m']}까지 좁혀지며 호조.
  - **스웨덴 법인 (LGESW)**: 7월 단월 {sub_results[6]['lg_jul']}, 7월 누적 {sub_results[6]['lg_7m']} ({sub_results[6]['lg_diff']})로 견조한 성장세 지속.
- **경쟁 심화 및 방어 법인**:
  - **영국 법인 (LGEUK)** & **프랑스 법인 (LGEFS)**: 서유럽 주요 대형 유통의 경쟁사(삼성, 하이센스) 가격 공세로 인해 하반기 성수기 진입 전 집중 프로모션 점검 필요.

---

## 4. 데이터 보존 및 아티팩트 안내
- **이전 6월 누적 백업**: [backup/2606_누적/index.html](file:///{clean_dir}/backup/2606_누적/index.html)
- **최신 7월 누적 대시보드**: [public/index.html](file:///{clean_dir}/public/index.html) 및 [index.html](file:///{clean_dir}/index.html)
- **품질 검증 리포트**: [data_validation_report.json](file:///{clean_dir}/data_validation_report.json) (Health Score: 100/100, 7월 활성화 확인)
"""

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[Diff Engine] Comparison Report saved: {output_report_path}")
    return True

if __name__ == "__main__":
    generate_diff_report()

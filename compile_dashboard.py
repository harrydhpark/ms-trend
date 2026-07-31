import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
json_data_path = os.path.join(current_dir, "ms_trend_data.json")
output_html_path = os.path.join(current_dir, "public", "index.html")

def build_html():
    if not os.path.exists(json_data_path):
        print(f"Error: JSON 데이터가 존재하지 않습니다: {json_data_path}")
        return
        
    print(f"Loading data from: {json_data_path}")
    with open(json_data_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        
    # Ensure the public directory exists
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        
    # Serialize to insert into HTML
    serialized_data = json.dumps(json_data, ensure_ascii=False, indent=2)
    
    html_template = """<!DOCTYPE html>
<html class="light" lang="ko">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>Executive Portal | LGE Europe TV MS Trend Dashboard</title>
    <script src="portal-topbar.js"></script>
    
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&amp;family=Noto+Sans+KR:wght@300;400;500;700&amp;family=JetBrains+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
    
    <script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "primary": "#051c2c",
                        "on-primary": "#ffffff",
                        "secondary": "#a50034",
                        "surface": "#f6faff",
                        "surface-variant": "#ebf5ff",
                        "outline": "#73777d",
                        "outline-variant": "#c3c7cc",
                        "error": "#e11d48",
                        "background": "#ffffff",
                        "primary-hover": "#860027",
                        "teal-accent": "#00a3a3",
                        "crimson-accent": "#e11d48"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem"
                    },
                    "fontFamily": {
                        "headline": ["\"Source Serif 4\"", "serif"],
                        "body": ["Inter", "Noto Sans KR", "sans-serif"],
                        "mono": ["JetBrains Mono", "monospace"]
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Inter', 'Noto Sans KR', sans-serif; background-color: #f6faff; color: #051c2c; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Source Serif 4', serif; }
        .sidebar-item.active { background-color: rgba(255, 255, 255, 0.1); border-right: 4px solid #ffffff; }
        .country-node.active > button { background-color: rgba(255, 255, 255, 0.05); color: #ffffff; }
        html, body { overflow-x: hidden; width: 100%; }
        .sticky-col { position: sticky; left: 0; background-color: #ffffff; z-index: 10; }
        .sticky-col-header { position: sticky; left: 0; z-index: 20; }
        .table-container { position: relative; overflow-x: auto; }
        th { position: sticky; top: 0; background-color: #051c2c; color: #ffffff; z-index: 15; }
        .font-mono-data { font-family: 'JetBrains Mono', monospace; }
        
        /* Robust colors definition to guarantee visibility even during tailwind lag */
        .bg-primary { background-color: #051c2c !important; }
        .text-white { color: #ffffff !important; }
        .text-white\/70 { color: rgba(255, 255, 255, 0.7) !important; }
        .text-white\/50 { color: rgba(255, 255, 255, 0.5) !important; }
        .text-white\/40 { color: rgba(255, 255, 255, 0.4) !important; }
        .bg-secondary { background-color: #a50034 !important; }
        .text-secondary { color: #a50034 !important; }
        .bg-teal-accent { background-color: #00a3a3 !important; }
        .text-teal-accent { color: #00a3a3 !important; }
        
        /* Accordion style */
        .accordion-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }
        .accordion-content.open {
            max-height: 500px;
            transition: max-height 0.3s ease-in;
        }
    </style>
</head>
<body class="flex min-h-screen">
    <!-- Sidebar Navigation -->
    <aside class="w-72 bg-primary text-white fixed h-screen flex flex-col z-50 shadow-lg">
        <div class="p-8 border-b border-white/10 flex-shrink-0">
            <div class="flex items-center gap-2.5 mb-2">
                <!-- Inline SVG Bar Chart Icon to avoid material font render lag issue -->
                <svg class="w-6 h-6 text-white/80" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125z"></path>
                </svg>
                <h1 class="text-xl font-bold tracking-tight">TV M/S Dashboard</h1>
            </div>
            <p class="text-[10px] text-white/50 uppercase tracking-[0.2em] font-medium">EUROPE TV M/S & TREND</p>
        </div>
        
        <nav class="flex-1 py-6 space-y-4 overflow-y-auto" id="sidebar-nav">
            <!-- Sidebar Groups will be injected by JavaScript -->
        </nav>
        
        <div class="p-8 border-t border-white/10 bg-black/10 flex flex-col gap-1 text-[10px] text-white/40 font-sans tracking-tight leading-relaxed flex-shrink-0">
            <p class="font-bold text-white/50 text-[11px] mb-1">System Admin</p>
            <p class="text-white/60">Harry Park</p>
            <p><a href="mailto:harry.park@lge.com" class="hover:text-white text-white/50 underline decoration-white/20 transition-all">harry.park@lge.com</a></p>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="ml-72 flex-1 flex flex-col min-h-screen min-w-0">
        <!-- Top Bar Header -->
        <header class="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-12 sticky top-0 z-40">
            <div class="flex items-center gap-6">
                <span class="text-xs font-bold tracking-widest text-slate-400 uppercase">Europe TV MS Trend</span>
                <div class="h-4 w-px bg-slate-200"></div>
                <p class="text-sm font-semibold text-primary" id="page-indicator">로딩 중...</p>
            </div>
            <div class="flex items-center gap-6">
                <!-- Year Selector Tabs -->
                <div class="flex bg-slate-100 p-1 rounded">
                    <button class="px-4 py-1.5 text-xs font-bold rounded transition-all bg-primary text-white" id="tab-2026" onclick="setYear(2026)">2026년 실적</button>
                    <button class="px-4 py-1.5 text-xs font-bold rounded transition-all text-slate-600 hover:text-primary" id="tab-2025" onclick="setYear(2025)">2025년 실적</button>
                </div>
                <div class="h-8 w-px bg-slate-200"></div>
                <div class="text-right">
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Data Source</p>
                    <p class="text-sm font-bold text-secondary">M/S Databook (26.5월)</p>
                </div>
            </div>
        </header>

        <!-- View Container -->
        <div class="p-12 w-full flex-1 flex flex-col gap-10">
            <!-- Welcome Banner -->
            <div class="bg-primary text-white p-8 rounded-lg shadow-md relative overflow-hidden flex-shrink-0">
                <div class="relative z-10">
                    <h2 class="text-3xl font-headline font-bold mb-3" id="banner-title">유럽 TV M/S & 경쟁 현황 포털</h2>
                    <p class="text-xs text-white/70 leading-relaxed max-w-4xl" id="banner-desc">본 포털은 유럽 주요 지사의 TV 시장 규모, 경쟁사 브랜드별 M/S(삼성, 소니, 하이센스, 필립스) 및 주요 판가(ASP/API) 트렌드를 모니터링합니다. 좌측 지사 목록에서 아코디언 메뉴를 통해 특정 법인을 선택하면 엑셀 원천 데이터가 대시보드 테이블에 동적으로 렌더링됩니다.</p>
                </div>
                <div class="absolute -right-24 -bottom-24 w-80 h-80 bg-white/5 rounded-full blur-2xl pointer-events-none"></div>
            </div>

            <!-- KPI Cards Section -->
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 flex-shrink-0" id="kpi-cards-grid">
                <!-- Cards injected here -->
            </div>

            <!-- Table Selection Menu (Tabs) -->
            <div class="flex border-b border-slate-200 gap-2 flex-shrink-0">
                <button id="tab-btn-market" class="px-6 py-2.5 text-sm font-bold border-b-2 border-secondary text-primary transition-all" onclick="switchTableTab('market')">시장 지표 (Market Size & Share)</button>
                <button id="tab-btn-comp-lg" class="px-6 py-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-primary transition-all" onclick="switchTableTab('comp-lg')">경쟁 현황 M/S (LG)</button>
                <button id="tab-btn-comp-other" class="px-6 py-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-primary transition-all" onclick="switchTableTab('comp-other')">경쟁 현황 M/S (경쟁사)</button>
                <button id="tab-btn-asp" class="px-6 py-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-primary transition-all" onclick="switchTableTab('asp')">ASP & API 트렌드 (ASP & API Trend)</button>
            </div>

            <!-- Data Tables Section -->
            <div class="flex flex-col gap-8">
                <!-- Table 1: Market -->
                <div id="section-market" class="bg-white border border-slate-200 rounded-lg shadow-sm p-6">
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-3">
                            <span class="h-5 w-1 bg-primary"></span>
                            <h4 class="text-lg font-headline font-bold text-primary">시장 규모 및 세그먼트 비중 (Market Size & Share)</h4>
                        </div>
                        <span class="text-xs text-slate-400 font-medium">단위: 억불(USD 100M), 백만대(1M ea), 비율(%)</span>
                    </div>
                    <div class="table-container border border-slate-100 rounded">
                        <table class="min-w-full border-collapse text-left text-xs" id="table-market">
                            <!-- Injected by JS -->
                        </table>
                    </div>
                </div>

                <!-- Table 2: Competition MS (LG) -->
                <div id="section-comp-lg" class="bg-white border border-slate-200 rounded-lg shadow-sm p-6 hidden">
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-3">
                            <span class="h-5 w-1 bg-secondary"></span>
                            <h4 class="text-lg font-headline font-bold text-primary">브랜드별 경쟁 현황 M/S (LG)</h4>
                        </div>
                        <span class="text-xs text-slate-400 font-medium">단위: M/S 및 격차(%), 판매량(천 대/1K ea)</span>
                    </div>
                    <div class="table-container border border-slate-100 rounded">
                        <table class="min-w-full border-collapse text-left text-xs" id="table-comp-lg">
                            <!-- Injected by JS -->
                        </table>
                    </div>
                </div>

                <!-- Table 3: Competition MS (Other Brands) -->
                <div id="section-comp-other" class="bg-white border border-slate-200 rounded-lg shadow-sm p-6 hidden">
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-3">
                            <span class="h-5 w-1 bg-indigo-600"></span>
                            <h4 class="text-lg font-headline font-bold text-primary">브랜드별 경쟁 현황 M/S (경쟁사)</h4>
                        </div>
                        <span class="text-xs text-slate-400 font-medium">단위: M/S 및 격차(%), 판매량(천 대/1K ea)</span>
                    </div>
                    <div class="table-container border border-slate-100 rounded">
                        <table class="min-w-full border-collapse text-left text-xs" id="table-comp-other">
                            <!-- Injected by JS -->
                        </table>
                    </div>
                </div>

                <!-- Table 4: ASP & API -->
                <div id="section-asp" class="bg-white border border-slate-200 rounded-lg shadow-sm p-6 hidden">
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-3">
                            <span class="h-5 w-1 bg-teal-600"></span>
                            <h4 class="text-lg font-headline font-bold text-primary">ASP & API 트렌드 (ASP & API Trend)</h4>
                        </div>
                        <span class="text-xs text-slate-400 font-medium">단위: ASP($/USD), API(index)</span>
                    </div>
                    <div class="table-container border border-slate-100 rounded">
                        <table class="min-w-full border-collapse text-left text-xs" id="table-asp">
                            <!-- Injected by JS -->
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Embed Data & Business Logic -->
    <script>
        const dashboardData = /*DASHBOARD_DATA_PLACEHOLDER*/;
        
        const regionMeta = {
            'EU': { en: 'Europe (유럽)', kr: '유럽 전체 (Europe)', sheet: '유럽' },
            'LGEAG': { en: 'Austria (오스트리아)', kr: '오스트리아 지점', sheet: 'AG' },
            'LGEBN': { en: 'Benelux (베네룩스)', kr: '베네룩스 지점', sheet: 'BN' },
            'Netherlands': { en: 'Netherlands (네덜란드)', kr: '네덜란드 지점', sheet: 'Netherlands' },
            'Belgium': { en: 'Belgium (벨기에)', kr: '벨기에 지점', sheet: 'Belgium' },
            'LGECK': { en: 'Czech (체코)', kr: '체코 법인', sheet: 'CZ' },
            'Czechia': { en: 'Czechia (체코지사)', kr: '체코 지사', sheet: 'Czechia' },
            'Slovakia': { en: 'Slovakia (슬로바키아)', kr: '슬로바키아 지사', sheet: 'Slovakia' },
            'LGEDG': { en: 'Germany (독일)', kr: '독일 법인', sheet: 'DG' },
            'Swiss': { en: 'Switzerland (스위스)', kr: '스위스 지점', sheet: 'Switzerland' },
            'LGEES': { en: 'Spain (스페인)', kr: '스페인 법인', sheet: 'ES' },
            'LGEFS': { en: 'France (프랑스)', kr: '프랑스 법인', sheet: 'FS' },
            'LGEHS': { en: 'Greece (그리스)', kr: '그리스 법인', sheet: 'HS' },
            'LGEIS': { en: 'Italy (이탈리아)', kr: '이탈리아 법인', sheet: 'IS' },
            'LGEMK': { en: 'Hungary (헝가리)', kr: '헝가리 법인', sheet: 'MK(Croatia제외)' },
            'Hungary': { en: 'Hungary (헝가리)', kr: '헝가리 지사', sheet: 'Hungary' },
            'Serbia': { en: 'Serbia (세르비아)', kr: '세르비아 지사', sheet: 'Serbia' },
            'LGEPT': { en: 'Portugal (포르투갈)', kr: '포르투갈 지점', sheet: 'PT' },
            'LGERO': { en: 'Romania (루마니아)', kr: '루마니아 지점', sheet: 'RO' },
            'LGESW': { en: 'Sweden (스웨덴)', kr: '스웨덴 법인', sheet: 'SW (2)' },
            'LGEUK': { en: 'United Kingdom (영국)', kr: '영국 법인', sheet: 'UK (2)' }
        };
        
        const sidebarMenu = [
            { code: 'EU', isAccordion: false },
            { code: 'LGEAG', isAccordion: false },
            { code: 'LGEBN', isAccordion: true, subItems: ['Netherlands', 'Belgium'] },
            { code: 'LGECK', isAccordion: true, subItems: ['Czechia', 'Slovakia'] },
            { code: 'LGEDG', isAccordion: false },
            { code: 'Swiss', isAccordion: false },
            { code: 'LGEES', isAccordion: false },
            { code: 'LGEFS', isAccordion: false },
            { code: 'LGEHS', isAccordion: false },
            { code: 'LGEIS', isAccordion: false },
            { code: 'LGEMK', isAccordion: true, subItems: ['Hungary', 'Serbia'] },
            { code: 'LGEPT', isAccordion: false },
            { code: 'LGERO', isAccordion: false },
            { code: 'LGESW', isAccordion: false },
            { code: 'LGEUK', isAccordion: false }
        ];

        let currentRegion = 'EU';
        let currentYear = 2026;
        let currentTableTab = 'market';
        let openAccordions = { 'LGEBN': false, 'LGECK': false, 'LGEMK': false };

        const colHeaders = [
            "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월", "YTD"
        ];

        // Recalculation mapping to overwrite '전년비' row arrays to compute '전년비 M/S 격차(단순 차이)' dynamically
        const msYoYMapping = {
            30: 27, // LG 금액 M/S -> parent LG 금액 M/S
            33: 31, // LG 수량 M/S -> parent LG 수량 M/S
            61: 59, // Samsung 금액 M/S -> parent Samsung 금액 M/S
            63: 62, // Samsung 수량 M/S -> parent Samsung 수량 M/S
            80: 78, // Sony 금액 M/S -> parent Sony 금액 M/S
            82: 81, // Sony 수량 M/S -> parent Sony 수량 M/S
            95: 93, // Hisense 금액 M/S -> parent Hisense 금액 M/S
            108: 106 // Philips M/S
        };

        // Recalculate M/S YoY changes as simple difference (cur - prev) in %p as requested
        const calcRate = (cur, prev) => {
            if (cur === null || prev === null || isNaN(cur) || isNaN(prev)) return null;
            return cur - prev;
        };

        // Format cell values based on labels and indicator types (All decimal numbers unified to 1 decimal place)
        function formatVal(val, type, label = '', rowIndex = null) {
            if (val === null || val === undefined || isNaN(val)) return '-';
            
            const fullLabel = label.toLowerCase();
            
            // Percentage Formatting
            if (type === 'p') {
                // If the indicator is an API Index, format as round integer instead of percentage
                if (fullLabel.includes('api') || fullLabel.includes('index')) {
                    return Math.round(val).toLocaleString();
                }
                return (val * 100).toFixed(1) + '%';
            }
            
            // Money (ASP) Formatting
            if (type === 'm') {
                return '$' + Math.round(val).toLocaleString();
            }
            
            // Quantity (Scale Adjustment)
            if (type === 'q') {
                if (fullLabel.includes('억불') || fullLabel.includes('금액')) {
                    return val.toFixed(1);
                }
                if (fullLabel.includes('백만대') || fullLabel.includes('수량')) {
                    return val.toFixed(1);
                }
                if (fullLabel.includes('천 대') || fullLabel.includes('천대')) {
                    return val.toFixed(1);
                }
                return Math.round(val).toLocaleString();
            }
            
            // Rank
            if (type === 'r') {
                return Math.round(val) + '위';
            }
            
            if (typeof val === 'number') {
                return val.toFixed(1);
            }
            return val.toLocaleString();
        }

        // Format YoY Differences
        function formatYoY(val, type, label = '') {
            if (val === null || val === undefined || isNaN(val)) return '-';
            
            const sign = val > 0 ? '+' : '';
            const fullLabel = label.toLowerCase();
            
            if (type === 'p') {
                if (fullLabel.includes('api') || fullLabel.includes('index')) {
                    return sign + Math.round(val).toLocaleString();
                }
                return sign + (val * 100).toFixed(1) + '%p';
            }
            if (type === 'm') {
                return sign + '$' + Math.round(val).toLocaleString();
            }
            if (type === 'q') {
                if (fullLabel.includes('억불') || fullLabel.includes('금액')) {
                    return sign + val.toFixed(1);
                }
                if (fullLabel.includes('백만대') || fullLabel.includes('수량')) {
                    return sign + val.toFixed(1);
                }
                if (fullLabel.includes('천 대') || fullLabel.includes('천대')) {
                    return sign + val.toFixed(1);
                }
            }
            if (type === 'r') {
                const rankDiff = -val;
                return (rankDiff > 0 ? '+' : '') + rankDiff;
            }
            if (typeof val === 'number') {
                return sign + val.toFixed(1);
            }
            return sign + Math.round(val).toLocaleString();
        }

        // Color highlighting for YoY values
        function getYoYColorClass(val, type, label = '') {
            if (val === null || val === undefined || isNaN(val) || val === 0) return '';
            
            let isPositive = val > 0;
            if (type === 'r') {
                isPositive = val < 0;
            }
            return isPositive ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold';
        }

        // Indent & label text formatter
        function getRowDisplayNameAndIndent(labels) {
            let indent = 0;
            let text = '';
            for (let i = 4; i >= 0; i--) {
                if (labels[i] !== null && labels[i] !== undefined && String(labels[i]).trim() !== '') {
                    const cleanLabel = String(labels[i]).trim();
                    if (cleanLabel !== "") {
                        indent = i;
                        text = cleanLabel;
                        break;
                    }
                }
            }
            return { text, indent };
        }

        // Find how many months have active data in the current year
        function getActiveMonthsCount(valArray) {
            if (!valArray) return 12;
            for (let m = 11; m >= 0; m--) {
                if (valArray[m] !== null && valArray[m] !== 0) {
                    return m + 1;
                }
            }
            return 12;
        }

        // Calculate YTD sums/averages dynamically to prevent scale mismatch in YoY
        function getDynamicYTD(row, yearKey) {
            // Overwrite YTD calculation for M/S YoY indicators using parental M/S YTD (simple diff: cur - prev)
            if (msYoYMapping[row.index]) {
                const parentIdx = msYoYMapping[row.index];
                const sheetName = regionMeta[currentRegion].sheet;
                const allRegionRows = (dashboardData.regions[sheetName] && dashboardData.regions[sheetName].data) ? dashboardData.regions[sheetName].data : [];
                const parentRow = allRegionRows.find(r => r.index === parentIdx);
                if (parentRow) {
                    const parentYtd = getDynamicYTD(parentRow, yearKey);
                    if (parentYtd.val !== null && parentYtd.prevVal !== null) {
                        const val = parentYtd.val - parentYtd.prevVal;
                        let prevVal = null;
                        const prevYearKey = yearKey === 'y26' ? 'y25' : 'y24';
                        const parentPrevYtd = getDynamicYTD(parentRow, prevYearKey);
                        if (parentPrevYtd.val !== null && parentPrevYtd.prevVal !== null) {
                            prevVal = parentPrevYtd.val - parentPrevYtd.prevVal;
                        }
                        const diff = (val !== null && prevVal !== null) ? (val - prevVal) : null;
                        return { val, prevVal, diff };
                    }
                }
                return { val: null, prevVal: null, diff: null };
            }

            const valArray = row[yearKey];
            const prevYearKey = yearKey === 'y26' ? 'y25' : 'y24';
            const prevValArray = row[prevYearKey];
            
            if (!valArray || !prevValArray) {
                return { val: null, prevVal: null, diff: null };
            }
            
            const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
            
            if (activeMonths === 12) {
                const val = valArray[12];
                const prevVal = prevValArray[12];
                const diff = (val !== null && prevVal !== null) ? (val - prevVal) : null;
                return { val, prevVal, diff };
            }
            
            const type = row.type;
            const rowIndex = row.index;
            
            const getAverage = (arr, months) => {
                let sumVal = 0;
                let count = 0;
                for (let i = 0; i < months; i++) {
                    if (arr[i] !== null) {
                        sumVal += arr[i];
                        count++;
                    }
                }
                return count > 0 ? (sumVal / count) : null;
            };
            
            const getSum = (arr, months) => {
                let sumVal = 0;
                let count = 0;
                for (let i = 0; i < months; i++) {
                    if (arr[i] !== null) {
                        sumVal += arr[i];
                        count++;
                    }
                }
                return count > 0 ? sumVal : null;
            };
            
            let val = valArray[12];
            let prevVal = prevValArray[12];
            
            if (type === 'q') {
                val = getSum(valArray, activeMonths);
                prevVal = getSum(prevValArray, activeMonths);
            } else if (type === 'p' || type === 'm') {
                val = getAverage(valArray, activeMonths);
                prevVal = getAverage(prevValArray, activeMonths);
            } else {
                val = valArray[12];
                prevVal = prevValArray[12];
            }
            
            const diff = (val !== null && prevVal !== null) ? (val - prevVal) : null;
            return { val, prevVal, diff };
        }

        // Overwrite YoY values dynamically for display tables
        function preCalculateAllMsYoY(rows) {
            Object.entries(msYoYMapping).forEach(([yoyIdxStr, parentIdx]) => {
                const yoyIdx = parseInt(yoyIdxStr);
                const yoyRow = rows.find(r => r.index === yoyIdx);
                const parentRow = rows.find(r => r.index === parentIdx);
                
                if (yoyRow && parentRow) {
                    const years = ['y26', 'y25', 'y24', 'y23'];
                    years.forEach(yr => {
                        const parentCur = parentRow[yr];
                        let prevYr = '';
                        if (yr === 'y26') prevYr = 'y25';
                        else if (yr === 'y25') prevYr = 'y24';
                        else if (yr === 'y24') prevYr = 'y23';
                        
                        const parentPrev = prevYr ? parentRow[prevYr] : null;
                        
                        if (parentCur) {
                            if (!yoyRow[yr]) yoyRow[yr] = new Array(13).fill(null);
                            for (let c = 0; c < 12; c++) {
                                const curVal = parentCur[c];
                                const prevVal = parentPrev ? parentPrev[c] : null;
                                yoyRow[yr][c] = calcRate(curVal, prevVal);
                            }
                        }
                    });
                }
            });
        }

        // Toggle Accordions
        window.toggleAccordion = function(code) {
            openAccordions[code] = !openAccordions[code];
            renderSidebar();
        };

        // Render Sidebar Menu
        function renderSidebar() {
            const nav = document.getElementById('sidebar-nav');
            nav.innerHTML = '';
            
            const groupHeader = document.createElement('div');
            groupHeader.className = "px-8 py-2 text-[10px] font-bold text-white/40 uppercase tracking-widest mb-1";
            groupHeader.innerText = "REGION: EUROPE";
            nav.appendChild(groupHeader);
            
            const groupContent = document.createElement('div');
            groupContent.className = "space-y-0.5";
            
            sidebarMenu.forEach(item => {
                const meta = regionMeta[item.code];
                if (!meta) return;
                
                if (item.isAccordion) {
                    const isOpen = openAccordions[item.code];
                    const arrowIcon = isOpen ? 'expand_more' : 'chevron_right';
                    
                    const accordionWrapper = document.createElement('div');
                    accordionWrapper.className = "w-full flex flex-col";
                    
                    const rowDiv = document.createElement('div');
                    rowDiv.className = "w-full flex items-center justify-between hover:bg-white/5 transition-all relative group";
                    
                    const mainBtn = document.createElement('button');
                    mainBtn.className = "flex-1 flex items-center px-8 py-2.5 text-left text-white/70 hover:text-white transition-all text-xs font-medium sidebar-btn-" + item.code;
                    
                    if (currentRegion === item.code) {
                        mainBtn.className += " active bg-white/10 text-white font-bold border-r-4 border-r-white";
                    }
                    
                    const shortCode = item.code.replace('LGE', '');
                    mainBtn.innerHTML = `
                        <span class="flex items-center gap-2.5">
                            <span class="text-[9px] font-mono font-bold bg-white/10 text-white/80 px-1.5 py-0.5 rounded border border-white/10 uppercase tracking-wider">${shortCode}</span>
                            <span>${meta.en.split(' (')[0]}</span>
                        </span>
                    `;
                    mainBtn.onclick = () => selectRegion(item.code);
                    rowDiv.appendChild(mainBtn);
                    
                    const toggleBtn = document.createElement('button');
                    toggleBtn.className = "px-4 py-2.5 text-white/40 hover:text-white transition-all flex items-center justify-center border-l border-white/5 self-stretch";
                    toggleBtn.innerHTML = `<span class="material-symbols-outlined text-[16px]">${arrowIcon}</span>`;
                    toggleBtn.onclick = (e) => {
                        e.stopPropagation();
                        toggleAccordion(item.code);
                    };
                    rowDiv.appendChild(toggleBtn);
                    
                    accordionWrapper.appendChild(rowDiv);
                    
                    const subContent = document.createElement('div');
                    subContent.className = `accordion-content ${isOpen ? 'open' : ''}`;
                    
                    item.subItems.forEach(subCode => {
                        const subMeta = regionMeta[subCode];
                        if (!subMeta) return;
                        
                        const subBtn = document.createElement('button');
                        subBtn.className = "w-full flex items-center pl-16 pr-8 py-2 text-left text-white/60 hover:text-white hover:bg-white/5 transition-all text-[11px] font-normal sidebar-btn-" + subCode;
                        
                        if (currentRegion === subCode) {
                            subBtn.className += " active bg-white/10 text-white font-bold border-r-4 border-r-white";
                        }
                        
                        subBtn.innerHTML = `
                            <span class="flex items-center gap-2">
                                <span class="text-[8px] text-white/40 font-mono">└</span>
                                <span>${subMeta.en.split(' (')[0]}</span>
                            </span>
                        `;
                        subBtn.onclick = () => selectRegion(subCode);
                        subContent.appendChild(subBtn);
                    });
                    
                    accordionWrapper.appendChild(subContent);
                    groupContent.appendChild(accordionWrapper);
                    
                } else {
                    const btn = document.createElement('button');
                    btn.className = "w-full flex items-center px-8 py-2.5 text-left text-white/70 hover:text-white hover:bg-white/5 transition-all text-xs font-medium sidebar-btn-" + item.code;
                    
                    if (currentRegion === item.code) {
                        btn.className += " active bg-white/10 text-white font-bold border-r-4 border-r-white";
                    }
                    
                    const shortCode = item.code.replace('LGE', '');
                    btn.innerHTML = `
                        <span class="flex items-center gap-2.5">
                            <span class="text-[9px] font-mono font-bold bg-white/10 text-white/80 px-1.5 py-0.5 rounded border border-white/10 uppercase tracking-wider">${shortCode}</span>
                            <span>${meta.en.split(' (')[0]}</span>
                        </span>
                    `;
                    btn.onclick = () => selectRegion(item.code);
                    groupContent.appendChild(btn);
                }
            });
            
            nav.appendChild(groupContent);
            
            document.querySelectorAll('.accordion-content').forEach(el => {
                if (el.classList.contains('open')) {
                    el.style.maxHeight = el.scrollHeight + "px";
                } else {
                    el.style.maxHeight = "0px";
                }
            });
        }

        function selectRegion(code) {
            currentRegion = code;
            
            sidebarMenu.forEach(item => {
                if (item.isAccordion && item.subItems.includes(code)) {
                    openAccordions[item.code] = true;
                }
            });
            
            renderSidebar();
            updateView();
        }

        function setYear(year) {
            currentYear = year;
            
            document.getElementById('tab-2026').className = year === 2026 ? "px-4 py-1.5 text-xs font-bold rounded transition-all bg-primary text-white" : "px-4 py-1.5 text-xs font-bold rounded transition-all text-slate-600 hover:text-primary";
            document.getElementById('tab-2025').className = year === 2025 ? "px-4 py-1.5 text-xs font-bold rounded transition-all bg-primary text-white" : "px-4 py-1.5 text-xs font-bold rounded transition-all text-slate-600 hover:text-primary";
            
            updateView();
        }

        window.switchTableTab = function(tabName) {
            currentTableTab = tabName;
            
            document.getElementById('section-market').classList.toggle('hidden', tabName !== 'market');
            document.getElementById('section-comp-lg').classList.toggle('hidden', tabName !== 'comp-lg');
            document.getElementById('section-comp-other').classList.toggle('hidden', tabName !== 'comp-other');
            document.getElementById('section-asp').classList.toggle('hidden', tabName !== 'asp');
            
            const tabs = ['market', 'comp-lg', 'comp-other', 'asp'];
            tabs.forEach(t => {
                const btn = document.getElementById('tab-btn-' + t);
                if (btn) {
                    if (t === tabName) {
                        btn.className = "px-6 py-2.5 text-sm font-bold border-b-2 border-secondary text-primary transition-all";
                    } else {
                        btn.className = "px-6 py-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-primary transition-all";
                    }
                }
            });
        };

        // Expand/Collapse Row toggle
        window.toggleSubRows = function(rowIndex) {
            const subRows = document.getElementsByClassName('sub-row-' + rowIndex);
            const icon = document.getElementById('icon-' + rowIndex);
            
            Array.from(subRows).forEach(row => {
                row.classList.toggle('hidden');
            });
            
            if (icon) {
                if (icon.innerText === '▶') {
                    icon.innerText = '▼';
                } else {
                    icon.innerText = '▶';
                }
            }
        };

        // Update the complete dashboard view
        function updateView() {
            const meta = regionMeta[currentRegion];
            document.getElementById('page-indicator').innerText = `${meta.kr} TV 경쟁지표 대시보드`;
            document.getElementById('banner-title').innerText = `${meta.kr} TV 경쟁지표 & M/S 모니터링`;
            
            const sheetName = meta.sheet;
            const rows = (dashboardData.regions[sheetName] && dashboardData.regions[sheetName].data) ? dashboardData.regions[sheetName].data : [];
            
            // Pre-calculate M/S YoY changes using parental M/S rows
            preCalculateAllMsYoY(rows);
            
            // 1. Render Summary Cards
            renderSummaryCards(rows);
            
            // 2. Filter Rows for Tables
            const marketRows = rows.filter(r => r.index >= 7 && r.index <= 19);
            const compLgRows = rows.filter(r => r.index >= 27 && r.index <= 58);
            const compOtherRows = rows.filter(r => r.index >= 59 && r.index <= 131);
            const aspRows = rows.filter(r => r.index >= 132 && r.index <= 151);
            
            renderTable('table-market', marketRows);
            renderTable('table-comp-lg', compLgRows);
            renderTable('table-comp-other', compOtherRows);
            renderTable('table-asp', aspRows);
        }

        // Summary YTD Card Renderer
        function renderSummaryCards(rows) {
            const grid = document.getElementById('kpi-cards-grid');
            grid.innerHTML = '';
            
            // 1. First Card: 시장 금액 규모(억불) [Row 7, fixed y25 annual vs y24 annual, added YoY unit]
            const row7 = rows.find(r => r.index === 7);
            let card1Html = '';
            if (row7) {
                const val25 = row7.y25 ? row7.y25[12] : null;
                const val24 = row7.y24 ? row7.y24[12] : null;
                const diff = (val25 !== null && val24 !== null) ? (val25 - val24) : null;
                
                const valStr = formatVal(val25, row7.type, '시장 금액 규모(억불)', 7);
                const diffStr = (diff !== null) ? (diff > 0 ? '+' : '') + diff.toFixed(1) + '억불' : '-';
                const yoyColor = getYoYColorClass(diff, row7.type, '시장 금액 규모(억불)');
                
                card1Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-teal-accent">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">시장 금액 규모(억불)</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">25년 연간</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${yoyColor}">YoY: ${diffStr}</span>
                        </div>
                    </div>
                `;
            }
            
            // 2. Second Card: LG 금액 M/S [Row 27, show Samsung Gap instead of YoY]
            const row27 = rows.find(r => r.index === 27);
            const row29 = rows.find(r => r.index === 29); // LG 삼성비 격차 Row 29
            let card2Html = '';
            if (row27) {
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const { val } = getDynamicYTD(row27, yearKey);
                
                let samGapVal = null;
                if (row29) {
                    const samGapYtd = getDynamicYTD(row29, yearKey);
                    samGapVal = samGapYtd.val;
                }
                
                const valStr = formatVal(val, row27.type, 'LG 금액 M/S', 27);
                let samGapStr = '-';
                let samGapColor = '';
                if (samGapVal !== null) {
                    const sign = samGapVal > 0 ? '+' : '';
                    samGapStr = sign + (samGapVal * 100).toFixed(1) + '%';
                    samGapColor = samGapVal > 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold';
                }
                
                const valArray = row27[yearKey];
                const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
                const periodLabel = activeMonths === 12 ? 'YTD (12월 누적)' : `YTD (${activeMonths}월 누적)`;
                
                card2Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-secondary">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">LG 금액 M/S</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">${periodLabel}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${samGapColor}">삼성비 격차: ${samGapStr}</span>
                        </div>
                    </div>
                `;
            }
            
            // 3. Third Card: LG OLED 금액 M/S [Row 38, show Samsung Gap instead of YoY]
            const row38 = rows.find(r => r.index === 38);
            const row68 = rows.find(r => r.index === 68); // SAMSUNG OLED M/S Row 68
            let card3Html = '';
            if (row38) {
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const { val } = getDynamicYTD(row38, yearKey);
                
                let samOledVal = null;
                if (row68) {
                    const samOledYtd = getDynamicYTD(row68, yearKey);
                    samOledVal = samOledYtd.val;
                }
                
                let samGapVal = null;
                if (val !== null && samOledVal !== null) {
                    samGapVal = val - samOledVal;
                }
                
                const valStr = formatVal(val, 'p', 'LG OLED 금액 M/S', 38);
                let samGapStr = '-';
                let samGapColor = '';
                if (samGapVal !== null) {
                    const sign = samGapVal > 0 ? '+' : '';
                    samGapStr = sign + (samGapVal * 100).toFixed(1) + '%';
                    samGapColor = samGapVal > 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold';
                }
                
                const valArray = row38[yearKey];
                const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
                const periodLabel = activeMonths === 12 ? 'YTD (12월 누적)' : `YTD (${activeMonths}월 누적)`;
                
                card3Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-secondary">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">LG OLED 금액 M/S</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">${periodLabel}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${samGapColor}">삼성비 격차: ${samGapStr}</span>
                        </div>
                    </div>
                `;
            }
            
            // 4. Fourth Card: LG OLED 판매(천 대) [Row 34, modified title & added YoY unit]
            const row34 = rows.find(r => r.index === 34);
            let card4Html = '';
            if (row34) {
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const { val, prevVal, diff } = getDynamicYTD(row34, yearKey);
                
                const valStr = formatVal(val / 1000, row34.type, 'LG OLED 판매(천 대)', 34);
                const yoyDiffStr = (diff !== null) ? (diff/1000 > 0 ? '+' : '') + (diff/1000).toFixed(1) + '천 대' : '-';
                const yoyColor = getYoYColorClass(diff / 1000, row34.type, 'LG OLED 판매(천 대)');
                
                const valArray = row34[yearKey];
                const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
                const periodLabel = activeMonths === 12 ? 'YTD (12월 누적)' : `YTD (${activeMonths}월 누적)`;
                
                card4Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-teal-accent">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">LG OLED 판매(천 대)</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">${periodLabel}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${yoyColor}">YoY: ${yoyDiffStr}</span>
                        </div>
                    </div>
                `;
            }
            
            // 5. Fifth Card: LG ASP ($) [Row 133]
            const row133 = rows.find(r => r.index === 133);
            let card5Html = '';
            if (row133) {
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const { val, prevVal, diff } = getDynamicYTD(row133, yearKey);
                
                const valStr = formatVal(val, row133.type, 'LG ASP ($)', 133);
                let yoyDiffStr = '-';
                let yoyColor = '';
                if (diff !== null) {
                    yoyDiffStr = formatYoY(diff, row133.type, 'LG ASP ($)');
                    yoyColor = getYoYColorClass(diff, row133.type, 'LG ASP ($)');
                }
                
                const valArray = row133[yearKey];
                const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
                const periodLabel = activeMonths === 12 ? 'YTD (12월 누적)' : `YTD (${activeMonths}월 누적)`;
                
                card5Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-teal-accent">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">LG ASP ($)</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">${periodLabel}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${yoyColor}">YoY: ${yoyDiffStr}</span>
                        </div>
                    </div>
                `;
            }
            
            // 6. Sixth Card: 시장 ASP ($) [Row 135]
            const row135 = rows.find(r => r.index === 135);
            let card6Html = '';
            if (row135) {
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const { val, prevVal, diff } = getDynamicYTD(row135, yearKey);
                
                const valStr = formatVal(val, row135.type, '시장 ASP ($)', 135);
                let yoyDiffStr = '-';
                let yoyColor = '';
                if (diff !== null) {
                    yoyDiffStr = formatYoY(diff, row135.type, '시장 ASP ($)');
                    yoyColor = getYoYColorClass(diff, row135.type, '시장 ASP ($)');
                }
                
                const valArray = row135[yearKey];
                const activeMonths = yearKey === 'y26' ? getActiveMonthsCount(valArray) : 12;
                const periodLabel = activeMonths === 12 ? 'YTD (12월 누적)' : `YTD (${activeMonths}월 누적)`;
                
                card6Html = `
                    <div class="bg-white p-5 rounded border border-slate-200 hover:shadow-md transition-all flex flex-col justify-between border-l-4 border-l-teal-accent">
                        <div class="flex flex-col gap-1.5 items-start">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">시장 ASP ($)</span>
                            <span class="text-2xl font-bold text-primary font-headline tracking-tight">${valStr}</span>
                            <span class="text-[10px] text-slate-500 font-semibold bg-slate-50 px-2 py-0.5 rounded">${periodLabel}</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border border-slate-100 mt-0.5 ${yoyColor}">YoY: ${yoyDiffStr}</span>
                        </div>
                    </div>
                `;
            }
            
            grid.innerHTML = card1Html + card2Html + card3Html + card4Html + card5Html + card6Html;
        }

        // Main Table Renderer
        function renderTable(tableId, rows) {
            const table = document.getElementById(tableId);
            if (!table) return;
            table.innerHTML = '';
            
            // Force percentage type for 75" M/S rows (Fixing 0 without decimal % issue)
            const percentRowIndices = [45, 72, 87, 100, 113];
            rows.forEach(r => {
                if (percentRowIndices.includes(r.index)) {
                    r.type = 'p';
                }
            });
            
            // Force percentage type for API Index rows (to force YTD 동기 평균)
            const apiIndexRows = [132, 136, 140, 144, 148];
            rows.forEach(r => {
                if (apiIndexRows.includes(r.index)) {
                    r.type = 'p';
                }
            });
            
            // Force Money type for ASP rows (to force YTD 동기 평균)
            const aspValueRows = [133, 134, 135, 137, 138, 139, 141, 142, 143, 145, 146, 147, 149, 150, 151];
            rows.forEach(r => {
                if (aspValueRows.includes(r.index)) {
                    r.type = 'm';
                }
            });
            
            // Extract the global active months count from the complete region dataset to avoid filter omissions
            let globalActiveMonths = 12;
            const meta = regionMeta[currentRegion];
            let allRegionRows = [];
            if (meta) {
                const sheetName = meta.sheet;
                allRegionRows = (dashboardData.regions[sheetName] && dashboardData.regions[sheetName].data) ? dashboardData.regions[sheetName].data : [];
                const refRow = allRegionRows.find(r => r.index === 7);
                if (refRow && refRow['y26']) {
                    globalActiveMonths = getActiveMonthsCount(refRow['y26']);
                }
            }
            
            // List of row indices that should have historical 3-year sub-rows
            const historicalRowIndices = [
                7, 9, 11, 13, 14, 15, 17, 19,
                27, 31, 34, 35, 36, 38, 41, 43, 45, 49, 53, 55, 57, // Removed Row 37
                59, 62, 64, 65, 66, 68, 70, 71, 72, 74, 76, 77, // Removed Row 67
                78, 81, 83, 85, 86, 87, 89, 91, 92,
                93, 96, 98, 99, 100, 102, 104, 105,
                106, 109, 111, 112, 113, 115, 117, 118,
                // ASP & API 지표군 일괄 추가
                132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151
            ];
            
            let html = '<thead><tr>';
            html += '<th class="sticky-col-header text-left px-4 py-3 bg-primary text-white font-bold" style="min-width: 280px; left: 0;">지표 (Indicator)</th>';
            colHeaders.forEach(h => {
                const bgClass = h === 'YTD' ? 'bg-slate-800' : 'bg-primary';
                html += `<th class="text-center px-2 py-3 ${bgClass} text-white font-bold">${h}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            let lastBrand = '';
            
            rows.forEach((row, idx) => {
                let { text, indent } = getRowDisplayNameAndIndent(row.labels);
                if (!text) return;
                
                // Hide other non-requested weight rows in Market table
                if (tableId === 'table-market' && (row.index === 16 || row.index === 18)) {
                    return;
                }
                
                // Skip non-requested rows in LG table
                if (tableId === 'table-comp-lg') {
                    // Added Row 37 (8K LCD 판매) to skipped rows list
                    const skipLgIndices = [28, 37, 39, 40, 47, 48, 51, 52];
                    if (skipLgIndices.includes(row.index)) {
                        return;
                    }
                }
                
                // Skip non-requested rows in Competitors table SONY (중복)
                if (tableId === 'table-comp-other') {
                    // Added Row 67 (SAMSUNG 8K LCD 판매) to skipped rows list
                    const skipCompIndices = [
                        60, 67, 69, 73, 75,
                        79, 84, 88, 90,
                        94, 97, 101, 103,
                        107, 110, 114, 116,
                        119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131
                    ];
                    if (skipCompIndices.includes(row.index)) {
                        return;
                    }
                }
                
                // Category Header insertion for Competitor brands
                if (tableId === 'table-comp-other') {
                    let currentBrand = '';
                    if (row.index >= 59 && row.index <= 77) currentBrand = 'SAMSUNG (삼성)';
                    else if (row.index >= 78 && row.index <= 92) currentBrand = 'SONY (소니)';
                    else if (row.index >= 93 && row.index <= 105) currentBrand = 'HISENSE (하이센스)';
                    else if (row.index >= 106 && row.index <= 118) currentBrand = 'PHILIPS (필립스)';
                    
                    if (currentBrand && currentBrand !== lastBrand) {
                        html += `<tr class="bg-slate-100 border-y border-slate-200"><td colspan="14" class="px-4 py-2.5 font-bold text-slate-800 text-xs tracking-wider uppercase">${currentBrand}</td></tr>`;
                        lastBrand = currentBrand;
                    }
                }
                
                // Override display names and indents to fully align main, growth, and weight metrics
                // 1. Market Size & Share
                if (row.index === 7) { text = "금액 (억불)"; indent = 1; }
                else if (row.index === 8) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 9) { text = "수량 (백만대)"; indent = 1; }
                else if (row.index === 10) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 11) { text = "1천불↑ (백만대)"; indent = 1; }
                else if (row.index === 12) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 13) { text = "OLED 비중 (금액)"; indent = 1; }
                else if (row.index === 14) { text = "UHD 비중 (금액)"; indent = 1; }
                else if (row.index === 15) { text = '75"↑(UHD+OLED) 비중 (금액)'; indent = 1; }
                else if (row.index === 17) { text = "2천불↑ 비중 (금액)"; indent = 1; }
                else if (row.index === 19) { text = "1천불↑ 비중 (금액)"; indent = 1; }
                
                // 2. LG Competition MS
                else if (row.index === 27) { text = "금액 M/S"; indent = 1; }
                else if (row.index === 29) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 30) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 31) { text = "수량 M/S"; indent = 1; }
                else if (row.index === 32) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 33) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 34) { text = "OLED 판매 (천 대)"; indent = 1; }
                else if (row.index === 35) { text = "OLED 비중 (금액비중)"; indent = 1; }
                else if (row.index === 36) { text = "QNED 판매 (천 대)"; indent = 1; }
                else if (row.index === 38) { text = "OLED M/S"; indent = 1; }
                else if (row.index === 41) { text = "UHD LCD M/S (OLED 제외)"; indent = 1; }
                else if (row.index === 42) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 43) { text = "FHD M/S"; indent = 1; }
                else if (row.index === 44) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 45) { text = '75"↑(UHD+OLED)'; indent = 1; }
                else if (row.index === 46) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 49) { text = "2천불↑ M/S"; indent = 1; }
                else if (row.index === 50) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 53) { text = "1천불↑ M/S"; indent = 1; }
                else if (row.index === 54) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 55) { text = "OLED 비중(1천불↑) (금액비중)"; indent = 1; }
                else if (row.index === 56) { text = "└ 삼성比"; indent = 1; }
                else if (row.index === 57) { text = "750불↓ M/S"; indent = 1; }
                else if (row.index === 58) { text = "└ 삼성比"; indent = 1; }

                // 3. Competitors SAMSUNG
                else if (row.index === 59) { text = "금액 M/S"; indent = 1; }
                else if (row.index === 61) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 62) { text = "수량 M/S"; indent = 1; }
                else if (row.index === 63) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 64) { text = "OLED 판매 (천 대)"; indent = 1; }
                else if (row.index === 65) { text = "Q-LED 판매 (천 대)"; indent = 1; }
                else if (row.index === 66) { text = "Neo Q-LED 판매 (천 대)"; indent = 1; }
                else if (row.index === 68) { text = "OLED M/S"; indent = 1; }
                else if (row.index === 70) { text = "UHD LCD M/S (OLED 제외)"; indent = 1; }
                else if (row.index === 71) { text = "FHD M/S"; indent = 1; }
                else if (row.index === 72) { text = '75"↑(UHD+OLED)'; indent = 1; }
                else if (row.index === 74) { text = "2천불↑ M/S"; indent = 1; }
                else if (row.index === 76) { text = "1천불↑ M/S"; indent = 1; }
                else if (row.index === 77) { text = "750불↓ M/S"; indent = 1; }
                
                // Competitors SONY
                else if (row.index === 78) { text = "금액 M/S"; indent = 1; }
                else if (row.index === 80) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 81) { text = "수량 M/S"; indent = 1; }
                else if (row.index === 82) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 83) { text = "OLED M/S"; indent = 1; }
                else if (row.index === 85) { text = "UHD LCD M/S (OLED 제외)"; indent = 1; }
                else if (row.index === 86) { text = "FHD M/S"; indent = 1; }
                else if (row.index === 87) { text = '75"↑(UHD+OLED)'; indent = 1; }
                else if (row.index === 89) { text = "2천불↑ M/S"; indent = 1; }
                else if (row.index === 91) { text = "1천불↑ M/S"; indent = 1; }
                else if (row.index === 92) { text = "750불↓ M/S"; indent = 1; }
                
                // Competitors HISENSE
                else if (row.index === 93) { text = "금액 M/S"; indent = 1; }
                else if (row.index === 95) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 96) { text = "OLED M/S"; indent = 1; }
                else if (row.index === 98) { text = "UHD LCD M/S (OLED 제외)"; indent = 1; }
                else if (row.index === 99) { text = "FHD M/S"; indent = 1; }
                else if (row.index === 100) { text = '75"↑(UHD+OLED)'; indent = 1; }
                else if (row.index === 102) { text = "2천불↑ M/S"; indent = 1; }
                else if (row.index === 104) { text = "1천불↑ M/S"; indent = 1; }
                else if (row.index === 105) { text = "750불↓ M/S"; indent = 1; }
                
                // Competitors PHILIPS
                else if (row.index === 106) { text = "금액 M/S"; indent = 1; }
                else if (row.index === 108) { text = "└ 전년비"; indent = 1; }
                else if (row.index === 109) { text = "OLED M/S"; indent = 1; }
                else if (row.index === 111) { text = "UHD LCD M/S (OLED 제외)"; indent = 1; }
                else if (row.index === 112) { text = "FHD M/S"; indent = 1; }
                else if (row.index === 113) { text = '75"↑(UHD+OLED)'; indent = 1; }
                else if (row.index === 115) { text = "2천불↑ M/S"; indent = 1; }
                else if (row.index === 117) { text = "1천불↑ M/S"; indent = 1; }
                else if (row.index === 118) { text = "750불↓ M/S"; indent = 1; }
                
                // 4. ASP & API 트렌드
                else if (row.index === 132) { text = "LTV API (OLED 포함)"; indent = 1; }
                else if (row.index === 133) { text = "└ LG ASP ($)"; indent = 1; }
                else if (row.index === 134) { text = "└ SS ASP ($)"; indent = 1; }
                else if (row.index === 135) { text = "└ 시장 ASP ($)"; indent = 1; }
                else if (row.index === 136) { text = "LTV API (OLED 제외)"; indent = 1; }
                else if (row.index === 137) { text = "└ LG ASP ($)"; indent = 1; }
                else if (row.index === 138) { text = "└ SS ASP ($)"; indent = 1; }
                else if (row.index === 139) { text = "└ 시장 ASP ($)"; indent = 1; }
                else if (row.index === 140) { text = "OLED API"; indent = 1; }
                else if (row.index === 141) { text = "└ LG ASP ($)"; indent = 1; }
                else if (row.index === 142) { text = "└ SS ASP ($)"; indent = 1; }
                else if (row.index === 143) { text = "└ 시장 ASP ($)"; indent = 1; }
                else if (row.index === 144) { text = "UHD LCD API (OLED 제외)"; indent = 1; }
                else if (row.index === 145) { text = "└ LG ASP ($)"; indent = 1; }
                else if (row.index === 146) { text = "└ SS ASP ($)"; indent = 1; }
                else if (row.index === 147) { text = "└ 시장 ASP ($)"; indent = 1; }
                else if (row.index === 148) { text = "FHD LCD API"; indent = 1; }
                else if (row.index === 149) { text = "└ LG ASP ($)"; indent = 1; }
                else if (row.index === 150) { text = "└ SS ASP ($)"; indent = 1; }
                else if (row.index === 151) { text = "└ 시장 ASP ($)"; indent = 1; }
                
                const yearKey = currentYear === 2026 ? 'y26' : 'y25';
                const prevYearKey = currentYear === 2026 ? 'y25' : 'y24';
                
                const valArray = row[yearKey];
                const prevValArray = row[prevYearKey];
                
                const indentClass = `pl-${indent * 4 + 4}`;
                const isSubIndicator = text.includes("삼성比") || text.includes("전년비") || text.includes("순위");
                const isHistoricalSubrow = historicalRowIndices.includes(row.index);
                const hasSubRows = isHistoricalSubrow && !isSubIndicator;
                
                // Clearly contrast sub indicators (slate-500) vs main metrics (slate-800)
                const textStyle = isSubIndicator 
                    ? 'font-normal text-slate-500 text-[11px]' 
                    : ((indent === 0 || indent === 1) ? 'font-medium text-slate-800 text-[11px]' : 'text-slate-500 text-[11px]');
                
                const trBg = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50';
                
                const cursorStyle = hasSubRows ? 'cursor-pointer hover:bg-slate-100/70' : 'cursor-default';
                const clickEvent = hasSubRows ? `onclick="toggleSubRows('${row.index}')"` : '';
                
                html += `<tr class="${trBg} ${cursorStyle} border-b border-slate-100" ${clickEvent}>`;
                html += `<td class="sticky-col px-4 py-2 border-r border-slate-100 ${indentClass} ${textStyle}" style="min-width: 280px; left:0;">`;
                if (hasSubRows) {
                    html += `<span class="mr-1.5 inline-block text-[8px] text-slate-400 select-none transition-transform" id="icon-${row.index}">▶</span>`;
                } else {
                    html += `<span class="mr-1.5 inline-block w-2 select-none"></span>`;
                }
                html += `${text}</td>`;
                
                // Get current year's active months based on global standard
                const currentActiveMonths = yearKey === 'y26' ? globalActiveMonths : 12;
                const isVolMetric = [34, 36, 37, 64, 65, 66, 67].includes(row.index);
                
                for (let c = 0; c < 12; c++) {
                    let val = valArray ? valArray[c] : null;
                    
                    // Empty future months with no data instead of rendering 0.0 or -100.0%
                    if (yearKey === 'y26' && c >= currentActiveMonths) {
                        val = null;
                    }
                    
                    // Unified scale adjustment to render 'K ea' (1/1000) for OLED/QNED quantity metrics
                    if (val !== null && isVolMetric) {
                        val = val / 1000;
                    }
                    
                    const valStr = formatVal(val, row.type, text, row.index);
                    html += `<td class="text-right px-2 py-2 border-r border-slate-100 font-mono-data ${textStyle}">${valStr}</td>`;
                }
                
                let { val: ytdVal, prevVal: ytdPrevVal, diff: ytdDiff } = getDynamicYTD(row, yearKey);
                if (ytdVal !== null && isVolMetric) ytdVal = ytdVal / 1000;
                if (ytdPrevVal !== null && isVolMetric) ytdPrevVal = ytdPrevVal / 1000;
                if (ytdDiff !== null && isVolMetric) ytdDiff = ytdDiff / 1000;
                
                const ytdValStr = formatVal(ytdVal, row.type, text, row.index);
                html += `<td class="text-right px-2 py-2 border-r border-slate-100 font-mono-data bg-slate-50 font-bold ${textStyle}">${ytdValStr}</td>`;
                html += '</tr>';
                
                // DYNAMIC INSERTION: If LG OLED M/S (Row 38) in LG table, insert custom └ 삼성比 row
                if (tableId === 'table-comp-lg' && row.index === 38) {
                    const childTextStyle = 'font-normal text-slate-500 text-[11px]';
                    const childIndentClass = 'pl-8';
                    const bgClass = 'bg-white';
                    
                    // Retrieve SAMSUNG OLED M/S (Row 68) to calculate the difference
                    const samOledRow = allRegionRows.find(r => r.index === 68);
                    
                    html += `<tr class="${bgClass} border-b border-slate-100">`;
                    html += `<td class="sticky-col px-4 py-2 border-r border-slate-100 ${childIndentClass} ${childTextStyle}" style="min-width: 280px; left:0;"><span class="mr-1.5 inline-block w-2 select-none"></span>└ 삼성比</td>`;
                    
                    for (let c = 0; c < 12; c++) {
                        let curVal = valArray ? valArray[c] : null;
                        let samVal = (samOledRow && samOledRow[yearKey]) ? samOledRow[yearKey][c] : null;
                        
                        if (yearKey === 'y26' && c >= currentActiveMonths) {
                            curVal = null;
                            samVal = null;
                        }
                        
                        const diffVal = calcRate(curVal, samVal);
                        const valStr = formatVal(diffVal, 'p', '└ 삼성比', 38);
                        html += `<td class="text-right px-2 py-2 border-r border-slate-100 font-mono-data ${childTextStyle}">${valStr}</td>`;
                    }
                    
                    // YTD Gap calculation for OLED M/S 삼성비
                    let ytdDiffVal = null;
                    if (samOledRow) {
                        const lgYtd = getDynamicYTD(row, yearKey);
                        const samYtd = getDynamicYTD(samOledRow, yearKey);
                        if (lgYtd.val !== null && samYtd.val !== null) {
                            ytdDiffVal = lgYtd.val - samYtd.val;
                        }
                    }
                    const ytdValStr = formatVal(ytdDiffVal, 'p', '└ 삼성比', 38);
                    html += `<td class="text-right px-2 py-2 border-r border-slate-100 font-mono-data bg-slate-50 font-bold ${childTextStyle}">${ytdValStr}</td>`;
                    html += '</tr>';
                }
                
                if (hasSubRows) {
                    const subRowClass = `sub-row-${row.index}`;
                    const childIndentClass = `pl-${indent * 4 + 12}`;
                    const childTextStyle = 'text-slate-400 font-normal italic text-[10px] bg-slate-50/30';
                    
                    // Specific customization for 3-year historical rows
                    const subYears = [
                        { key: prevYearKey, label: (currentYear - 1).toString().substring(2) + '년' },
                        { key: currentYear === 2026 ? 'y24' : 'y23', label: (currentYear - 2).toString().substring(2) + '년' },
                        { key: currentYear === 2026 ? 'y23' : 'y22', label: (currentYear - 3).toString().substring(2) + '년' }
                    ];
                    
                    const getSum = (arr, months) => {
                        let s = 0; let c = 0;
                        for (let i = 0; i < months; i++) {
                            if (arr && arr[i] !== null) { s += arr[i]; c++; }
                        }
                        return c > 0 ? s : null;
                    };
                    
                    const getAverage = (arr, months) => {
                        let s = 0; let c = 0;
                        for (let i = 0; i < months; i++) {
                            if (arr && arr[i] !== null) { s += arr[i]; c++; }
                        }
                        return c > 0 ? (s / c) : null;
                        
                    };
                    
                    subYears.forEach(subYr => {
                        const subYearValArray = row[subYr.key];
                        
                        html += `<tr class="${subRowClass} hidden bg-slate-50/20 border-b border-slate-50">`;
                        html += `<td class="sticky-col px-4 py-1.5 border-r border-slate-100 ${childIndentClass} ${childTextStyle}" style="min-width: 280px; left:0;">└ ${subYr.label}</td>`;
                        
                        for (let c = 0; c < 12; c++) {
                            let val = subYearValArray ? subYearValArray[c] : null;
                            if (val !== null && isVolMetric) {
                                val = val / 1000;
                            }
                            const valStr = formatVal(val, row.type, text, row.index);
                            html += `<td class="text-right px-2 py-1.5 border-r border-slate-100 font-mono-data ${childTextStyle}">${valStr}</td>`;
                        }
                        
                        let ytdVal = null;
                        if (subYearValArray) {
                            if (currentActiveMonths === 12) {
                                ytdVal = subYearValArray[12];
                            } else {
                                if (row.type === 'p' || row.type === 'm') {
                                    ytdVal = getAverage(subYearValArray, currentActiveMonths);
                                } else {
                                    ytdVal = getSum(subYearValArray, currentActiveMonths);
                                }
                            }
                        }
                        if (ytdVal !== null && isVolMetric) {
                            ytdVal = ytdVal / 1000;
                        }
                        const ytdValStr = formatVal(ytdVal, row.type, text, row.index);
                        html += `<td class="text-right px-2 py-1.5 border-r border-slate-100 font-mono-data bg-slate-50/30 font-semibold ${childTextStyle}">${ytdValStr}</td>`;
                        html += '</tr>';
                    });
                }
            });
            
            html += '</tbody>';
            table.innerHTML = html;
        }

        // Initialize Dashboard
        renderSidebar();
        updateView();
    </script>
</body>
</html>
"""
    
    # Replace placeholder with serialized json data
    compiled_html = html_template.replace("/*DASHBOARD_DATA_PLACEHOLDER*/", serialized_data)
    
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(compiled_html)
        
    print(f"Dashboard HTML compiled successfully! Generated file: {output_html_path}")

if __name__ == "__main__":
    build_html()

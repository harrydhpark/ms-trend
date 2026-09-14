import os
import sys
import argparse
import datetime
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import extract_ms_trend
import analyze_ms_trend
import compile_dashboard
import generate_ms_trend_diff

def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65 + "\n")

def run_step_dm(target_file=None):
    print_header("[Step 1/3] Data Manager Agent (ms-data-manager)")
    success = extract_ms_trend.extract_data(target_file)
    if not success:
        print("[ERROR] Data extraction failed!")
        return False
        
    validation_path = os.path.join(current_dir, "data_validation_report.json")
    if os.path.exists(validation_path):
        with open(validation_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        status = report.get("status", "UNKNOWN")
        score = report.get("health_score", 0)
        active_m = report.get("latest_active_month_2026", 0)
        print(f"\n[QA Summary] Status: {status} | Health Score: {score}/100 | Active: {active_m}월 누계")
        if status == "FAILED":
            print("[CRITICAL ERROR] Data quality check failed! Aborting pipeline.")
            return False
    return True

def run_step_mia():
    print_header("[Step 2/3] Market Insight Analyst Agent (ms-insight-analyst)")
    success = analyze_ms_trend.analyze_market()
    if not success:
        print("[ERROR] Market analytics failed!")
        return False
    print("\n[MIA Summary] Generated ms_trend_insights.json & ms_trend_executive_insights.md successfully.")
    return True

def run_step_dd():
    print_header("[Step 3/3] Dashboard Developer Agent (ms-dashboard-dev)")
    compile_dashboard.build_html()
    print("\n[DD Summary] Generated public/index.html & index.html with AI Summary Widget successfully.")
    return True

def run_step_diff():
    print_header("[Optional Step] Version Diff & Comparison Engine")
    success = generate_ms_trend_diff.generate_diff_report()
    if success:
        print("\n[Diff Summary] Generated ms_trend_diff_2607_vs_2606.md successfully.")
    return success

def main():
    parser = argparse.ArgumentParser(description="LGE Europe TV MS Trend Multi-Agent System Pipeline")
    parser.add_argument(
        "--step", 
        choices=["all", "dm", "mia", "dd", "diff"], 
        default="all", 
        help="Pipeline step to run: all (default), dm (data manager), mia (market analyst), dd (dashboard dev), diff (version comparison)"
    )
    parser.add_argument("--file", default=None, help="Path to specific Databook .xlsb file")
    args = parser.parse_args()
    
    start_time = datetime.datetime.now()
    print_header("LGE Europe TV MS Trend Multi-Agent Pipeline Started")
    print(f"Timestamp: {start_time.isoformat()}")
    print(f"Target Step: {args.step.upper()}")
    
    if args.step in ("all", "dm"):
        if not run_step_dm(args.file):
            sys.exit(1)
            
    if args.step in ("all", "mia"):
        if not run_step_mia():
            sys.exit(1)
            
    if args.step in ("all", "diff"):
        run_step_diff()
        
    if args.step in ("all", "dd"):
        run_step_dd()
        
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print_header(f"Multi-Agent Pipeline Finished Successfully in {elapsed:.1f}s")

if __name__ == "__main__":
    main()

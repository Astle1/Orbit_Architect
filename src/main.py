import sys
import os
import argparse
from extract_orbit import extract_dependencies
from evaluate_graph import load_graph, load_rules, evaluate
from compile_rules import compile_architecture
from remediate_agent import generate_remediation

def main():
    parser = argparse.ArgumentParser(description="Orbit Architect Pipeline")
    parser.add_argument("--reindex", action="store_true", help="Run Orbit indexing before extraction")
    args = parser.parse_args()

    print("=== ORBIT ARCHITECT PIPELINE ===")
    
    # Paths
    architecture_md = "architecture.md"
    rules_json = "rules.json"
    edges_csv = "edges.csv"
    report_json = "violation_report.json"
    comment_md = "mr_comment.md"
    
    # Phase 3: Compile rules
    print("\n[1/4] Compiling Architecture Documentation...")
    if not os.path.exists(architecture_md):
        print(f"FATAL: {architecture_md} not found.")
        sys.exit(1)
    compile_architecture(architecture_md, rules_json)
    
    # Phase 1: Extract Orbit Data
    print("\n[2/4] Extracting Orbit Dependency Graph...")
    success = extract_dependencies(edges_csv, reindex=args.reindex)
    if not success:
        print("FATAL: Failed to extract Orbit data. Are glab and orbit installed?")
        sys.exit(1)
    
    # Phase 2: Evaluate Graph
    print("\n[3/4] Evaluating Dependency Constraints (NetworkX)...")
    G = load_graph(edges_csv)
    rules = load_rules(rules_json)
    
    if not G or not rules:
        print("FATAL: Failed to load graph or rules.")
        sys.exit(1)
        
    report = evaluate(G, rules, report_json)
    
    # Phase 4/5: Generate MR Comment
    print("\n[4/4] Generating Remediation & MR Comment...")
    generate_remediation(report_json, comment_md)
    print("\n=== FINAL GITLAB MR COMMENT ===")
    sys.stdout.reconfigure(encoding='utf-8')
    with open(comment_md, 'r', encoding='utf-8') as f:
        print(f.read())
    print("===============================")
    
    if report.get("violation"):
        # Pipeline fails because architecture is violated
        sys.exit(1)
    else:
        print("Architecture verified successfully. Pipeline passes.")
        sys.exit(0)

if __name__ == "__main__":
    main()

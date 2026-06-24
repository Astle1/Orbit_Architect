import networkx as nx
import json
import csv
import sys
import argparse

def load_graph(edges_csv):
    G = nx.DiGraph()
    try:
        with open(edges_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                G.add_edge(row['source_file'], row['target_file'])
        print(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        return G
    except FileNotFoundError:
        print(f"Error: {edges_csv} not found.", file=sys.stderr)
        return None

def load_rules(rules_json):
    try:
        with open(rules_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {rules_json} not found.", file=sys.stderr)
        return None

def evaluate(graph, rules, output_json="violation_report.json"):
    print("Evaluating graph against architectural rules...")
    
    violation_report = {
        "violation": False,
        "violations": [],
        "total_rules": len(rules.get("rules", []))
    }
    
    for rule in rules.get("rules", []):
        if rule.get("type") == "forbidden":
            source_prefix = rule.get("from")
            target_prefix = rule.get("to")
            
            source_nodes = [n for n in graph.nodes if n.startswith(source_prefix)]
            target_nodes = [n for n in graph.nodes if n.startswith(target_prefix)]
            
            rule_violated = False
            for s in source_nodes:
                for t in target_nodes:
                    if nx.has_path(graph, s, t):
                        shortest_path = nx.shortest_path(graph, s, t)
                        print(f"VIOLATION FOUND: Path from {s} to {t} via {shortest_path}")
                        violation_report["violations"].append({
                            "severity": rule.get("severity", "medium").lower(),
                            "rule_type": "forbidden_dependency",
                            "source": source_prefix,
                            "target": target_prefix,
                            "path": shortest_path,
                            "rule": rule
                        })
                        rule_violated = True
                        break
                if rule_violated:
                    break
                        
        elif rule.get("type") == "allowed_set":
            source_prefix = rule.get("from")
            allowed_prefixes = rule.get("allowed", [])
            
            source_nodes = [n for n in graph.nodes if n.startswith(source_prefix)]
            
            rule_violated = False
            for s in source_nodes:
                for s_out, target in graph.out_edges(s):
                    # It's an internal import if it starts with the same source prefix
                    if target.startswith(source_prefix):
                        continue
                        
                    # Check if target is in the allowed set
                    is_allowed = False
                    for allowed_prefix in allowed_prefixes:
                        if target.startswith(allowed_prefix):
                            is_allowed = True
                            break
                            
                    if not is_allowed:
                        print(f"VIOLATION FOUND: {s} depends on unauthorized module {target}")
                        violation_report["violations"].append({
                            "severity": rule.get("severity", "medium").lower(),
                            "rule_type": "allowed_dependency_set",
                            "source": source_prefix,
                            "target": target,
                            "path": [s, target],
                            "rule": rule
                        })
                        rule_violated = True
                        break
                if rule_violated:
                    break

    if not violation_report["violations"]:
        print("Architecture verified. No violations found.")
    else:
        violation_report["violation"] = True
        print(f"Architecture violated. {len(violation_report['violations'])} violations found.")
        
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(violation_report, f, indent=2)
    print(f"Violation report saved to {output_json}")
    return violation_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--edges", default="edges.csv")
    parser.add_argument("--rules", default="rules.json")
    parser.add_argument("--out", default="violation_report.json")
    args = parser.parse_args()
    
    G = load_graph(args.edges)
    rules = load_rules(args.rules)
    
    if G and rules:
        evaluate(G, rules, args.out)

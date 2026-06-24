import json
import sys
import argparse

def generate_remediation(violation_json, output_md="mr_comment.md"):
    print(f"Generating remediation from {violation_json}...")
    try:
        with open(violation_json, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        violations = report.get("violations", [])
        total_rules = report.get("total_rules", 0)
        
        if not report.get("violation"):
            summary = f"""# Orbit Architect Report

Architecture documentation was compiled into {total_rules} executable constraints.

GitLab Orbit extracted repository relationships from the AST graph.

Orbit Architect evaluated those relationships against architectural policy.

**Repository Status: ✅ PASSED**

0 architectural violations detected.
Merge may proceed."""
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(summary)
            print("Passed report generated.")
            return True
        
        # Tally severities
        crit = sum(1 for v in violations if v.get("severity", "medium").upper() == "CRITICAL")
        high = sum(1 for v in violations if v.get("severity", "medium").upper() == "HIGH")
        med = sum(1 for v in violations if v.get("severity", "medium").upper() == "MEDIUM")
        
        md_comments = []
        
        # Add Summary Header
        summary = f"""# Orbit Architect Report

Architecture documentation was compiled into {total_rules} executable constraints.

GitLab Orbit extracted repository relationships from the AST graph.

Orbit Architect evaluated those relationships against architectural policy.

**Repository Status: ❌ FAILED**

{len(violations)} architectural violations detected.
Merge should not proceed until critical violations are resolved.

❌ Critical: {crit}
⚠️ High: {high}
⚠️ Medium: {med}"""
        md_comments.append(summary)
        
        for idx, v in enumerate(violations):
            path = v.get("path", [])
            rule = v.get("rule", {})
            
            # Determine Severity Formatting
            severity = v.get("severity", "medium").upper()
            if severity == "CRITICAL":
                severity_header = "❌ CRITICAL VIOLATION"
            elif severity == "HIGH":
                severity_header = "⚠️ HIGH VIOLATION"
            elif severity == "LOW":
                severity_header = "ℹ️ LOW VIOLATION"
            else:
                severity_header = "⚠️ MEDIUM VIOLATION"
                
            # Construct dependency path text
            path_str = " \u2192 ".join(path)
            
            # Construct Mermaid graph
            mermaid_lines = ["```mermaid", "graph LR"]
            for i in range(len(path) - 1):
                node_a_raw = path[i]
                node_b_raw = path[i+1]
                
                node_a_id = node_a_raw.replace('/', '_').replace('.', '_').replace('-', '_')
                node_b_id = node_b_raw.replace('/', '_').replace('.', '_').replace('-', '_')
                
                mermaid_lines.append(f'    {node_a_id}["{node_a_raw}"] --> {node_b_id}["{node_b_raw}"]')
                mermaid_lines.append(f"    style {node_a_id} stroke:#f66,stroke-width:2px")
                mermaid_lines.append(f"    style {node_b_id} stroke:#f66,stroke-width:2px")
            mermaid_lines.append("```")
            mermaid_str = "\n".join(mermaid_lines)
            
            # Format rule text
            original_rule_text = rule.get('original_text', 'Unknown Rule')
            if rule.get("type") == "allowed_set":
                allowed_list = "\n".join([f"- {a.capitalize()}" for a in rule.get("allowed", [])])
                rule_display = f"{original_rule_text}\n{allowed_list}"
            else:
                rule_display = original_rule_text
            
            # Provide intelligent defaults based on rule type
            if rule.get("type") == "forbidden":
                if len(path) == 2:
                    impact_text = f"{rule.get('from')} directly depends on {rule.get('to')}."
                else:
                    impact_text = f"{rule.get('from')} is now transitively coupled to {rule.get('to')}."
                
                why_text = f"The {rule.get('from')} module should communicate through abstractions rather than direct structural coupling to {rule.get('to')}."
                refactor_text = "Introduce an abstraction boundary or intermediate service to decouple these domains."
            else:
                impact_text = f"An unauthorized dependency was introduced in {rule.get('from')}."
                why_text = f"The {rule.get('from')} module operates under a strict Allowed Dependency Set."
                refactor_text = "Remove the unauthorized import or update the architecture documentation if this is an intentional structural shift."
            
            # Construct markdown comment following exact Phase 2 specs
            md_comment = f"""{severity_header}

Rule (ARCH-00{idx+1}):
{rule_display}

Violation Path:
{path_str}

Impact:
{impact_text}

Why This Rule Exists:
{why_text}

Suggested Refactor:
{refactor_text}

Mermaid Graph:
{mermaid_str}"""
            md_comments.append(md_comment)

        with open(output_md, 'w', encoding='utf-8') as f:
            f.write("\n\n---\n\n".join(md_comments))
            
        print(f"Remediation markdown written to {output_md}")
        return True
        
    except FileNotFoundError:
        print(f"Error: {violation_json} not found.", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="violation_report.json")
    parser.add_argument("--out", default="mr_comment.md")
    args = parser.parse_args()
    
    generate_remediation(args.input, args.out)

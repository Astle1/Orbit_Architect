import json
import sys
import argparse
import re

def compile_architecture(markdown_file, output_json="rules.json"):
    print(f"Compiling rules from {markdown_file}...")
    rules = {"rules": []}
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_rule = {}
        in_allowed_list = False
        allowed_targets = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("RULE:"):
                # Parse rule on the next lines
                i += 1
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                rule_text = lines[i].strip()
                
                # Check for "Forbidden"
                forbidden_match = re.search(r'(?i)([\w]+)\s+must\s+never\s+depend\s+on\s+([\w]+)', rule_text)
                # Check for "Allowed Set"
                allowed_match = re.search(r'(?i)([\w]+)\s+may\s+only\s+depend\s+on:', rule_text)
                
                if forbidden_match:
                    current_rule = {
                        "type": "forbidden",
                        "from": forbidden_match.group(1).lower(),
                        "to": forbidden_match.group(2).lower(),
                        "original_text": rule_text,
                        "severity": "medium" # default
                    }
                elif allowed_match:
                    current_rule = {
                        "type": "allowed_set",
                        "from": allowed_match.group(1).lower(),
                        "allowed": [],
                        "original_text": rule_text,
                        "severity": "medium"
                    }
                    in_allowed_list = True
                    
            elif in_allowed_list and line.startswith("*"):
                target = line.replace("*", "").strip().lower()
                current_rule["allowed"].append(target)
                
            elif line.startswith("SEVERITY:"):
                in_allowed_list = False
                i += 1
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                severity_text = lines[i].strip().lower()
                if severity_text in ["critical", "high", "medium", "low"]:
                    current_rule["severity"] = severity_text
                
                if current_rule:
                    rules["rules"].append(current_rule)
                    if current_rule["type"] == "forbidden":
                        print(f"Compiled Rule: {current_rule['from']} -> {current_rule['to']} is FORBIDDEN ({current_rule['severity']})")
                    elif current_rule["type"] == "allowed_set":
                        print(f"Compiled Rule: {current_rule['from']} may only depend on {current_rule['allowed']} ({current_rule['severity']})")
                    current_rule = {}
                    
            i += 1
            
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2)
            
        print(f"Rules compiled to {output_json}")
        return True
    except FileNotFoundError:
        print(f"Error: {markdown_file} not found.", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="architecture.md")
    parser.add_argument("--out", default="rules.json")
    args = parser.parse_args()
    
    compile_architecture(args.input, args.out)

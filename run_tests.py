import os
import subprocess

tests = [
    {
        "name": "Test Case 0: Clean Architecture",
        "rules": """RULE:
Frontend may only depend on:
* Utils

SEVERITY:
high

RULE:
Utils may only depend on:
* Services

SEVERITY:
high

RULE:
Services may only depend on:
* Database

SEVERITY:
high
"""
    },
    {
        "name": "Test Case 1: Forbidden Dependency (Transitive Block)",
        "rules": """RULE:
Frontend must never depend on Database

SEVERITY:
critical
"""
    },
    {
        "name": "Test Case 2: Forbidden Dependency (Direct Block)",
        "rules": """RULE:
Services must never depend on Database

SEVERITY:
critical
"""
    },
    {
        "name": "Test Case 3: Forbidden Dependency (Allowed/No violation)",
        "rules": """RULE:
Frontend must never depend on External

SEVERITY:
medium
"""
    },
    {
        "name": "Test Case 4: Allowed Set Semantics (Direct vs Transitive)",
        "rules": """RULE:
Frontend may only depend on:
* Utils

SEVERITY:
high
"""
    },
    {
        "name": "Test Case 5: Allowed Dependency Set (Violation)",
        "rules": """RULE:
Frontend may only depend on:
* Services

SEVERITY:
high
"""
    },
    {
        "name": "Test Case 6: Multiple Simultaneous Violations",
        "rules": """RULE:
Frontend must never depend on Database

SEVERITY:
critical

RULE:
Utils must never depend on Database

SEVERITY:
critical
"""
    }
]

with open("test_results.txt", "w", encoding='utf-8') as res_file:
    for i, test in enumerate(tests):
        res_file.write(f"=== {test['name']} ===\n")
        with open("architecture.md", "w", encoding='utf-8') as f:
            f.write(test["rules"])
        
        result = subprocess.run(["python", "src/main.py"], capture_output=True, text=True, encoding='utf-8')
        res_file.write(f"Exit Code: {result.returncode}\n")
        res_file.write("Output:\n")
        res_file.write(result.stdout)
        res_file.write(result.stderr)
        res_file.write("\n" + "="*40 + "\n\n")

print("All tests completed. See test_results.txt.")

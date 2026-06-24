import csv
import sys
import subprocess
import os

def get_target_repo_path():
    """Deterministically find the target git repository path."""
    if os.path.exists(".git"):
        return os.path.abspath(os.getcwd())
    for d in os.listdir("."):
        if os.path.isdir(d) and os.path.exists(os.path.join(d, ".git")):
            return os.path.abspath(d)
    return os.path.abspath(os.getcwd())

def extract_dependencies(output_csv="edges.csv", reindex=False):
    print("Extracting Orbit Dependency Graph...")
    
    target_repo = get_target_repo_path()
    # Normalize path for SQLite comparison to avoid backslash escape issues
    target_repo_sqlite = target_repo.replace('\\', '/')
    print(f"Target repository for Orbit: {target_repo}")
    
    if reindex:
        print("Running 'glab orbit local index .'...")
        try:
            # We run index in the target_repo directory to ensure correct repo_path is captured
            result = subprocess.run(["glab", "orbit", "local", "index", "."], cwd=target_repo, check=True, capture_output=True, text=True)
            print("Indexing complete.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to run glab orbit local index: {e.stderr}", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("FATAL: 'glab' executable not found in PATH.", file=sys.stderr)
            return False

    query = f"""
        SELECT f.path AS source_file, def.file_path AS target_file
        FROM gl_file f
        JOIN gl_edge e1 ON f.id = e1.source_id
        JOIN gl_imported_symbol sym ON e1.target_id = sym.id
        JOIN gl_edge e2 ON sym.id = e2.source_id
        JOIN gl_definition def ON e2.target_id = def.id
        JOIN _orbit_manifest m ON f.project_id = m.project_id
        WHERE e1.relationship_kind = 'IMPORTS' 
          AND e2.relationship_kind = 'IMPORTS'
          AND (m.repo_path = '{target_repo}' OR m.repo_path = '{target_repo_sqlite}')
    """
    
    print("Executing Orbit SQL extraction...")
    try:
        # Run sql
        result = subprocess.run(
            ["glab", "orbit", "local", "sql", query],
            check=True,
            capture_output=True,
            text=True
        )
        
        # The output of glab orbit local sql is likely a table format or CSV depending on glab version.
        # Often CLI sql tools output ascii tables. If it's CSV-like or we need to parse it,
        # let's write a robust parser, or ask glab for json/csv if supported.
        # Assuming the output is space/pipe delimited based on REAL_ORBIT_VALIDATION.md:
        # source_file                     | target_file
        # --------------------------------+----------------------------
        # frontend/ui.ts                  | utils/bridge.ts
        
        lines = result.stdout.strip().split('\n')
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["source_file", "target_file"])
            for line in lines:
                if '|' in line and 'source_file' not in line and '---' not in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2:
                        src = parts[0]
                        tgt = parts[1]
                        writer.writerow([src, tgt])
                        
        print(f"Successfully extracted {len(lines)-2 if len(lines) > 2 else 0} edges to {output_csv}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Orbit SQL: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("FATAL: 'glab' executable not found in PATH.", file=sys.stderr)
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="edges.csv")
    parser.add_argument("--reindex", action="store_true", help="Run 'glab orbit local index .' before extracting")
    args = parser.parse_args()
    
    extract_dependencies(args.out, args.reindex)

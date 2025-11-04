import ast
from collections import defaultdict

def analyze_code(code: str, language: str = "python"):
    findings = []

    if language.lower() != "python":
        findings.append({'type': 'info', 'message': 'Local analyzer currently supports Python only.', 'line': None})
        return findings

    lines = code.splitlines()

    for i, line in enumerate(lines, start=1):
        if len(line) > 100:
            findings.append({'type': 'style', 'message': f'Line {i} too long ({len(line)} chars).', 'line': i})
        if line.rstrip('\n').endswith(' '):
            findings.append({'type': 'style', 'message': 'Trailing whitespace.', 'line': i})
        if '\t' in line:
            findings.append({'type': 'style', 'message': 'Tab found — use spaces.', 'line': i})
        if 'TODO' in line or 'FIXME' in line:
            findings.append({'type': 'info', 'message': 'TODO/FIXME found.', 'line': i})

    try:
        tree = ast.parse(code)
    except Exception as e:
        findings.append({'type': 'bug', 'message': f'Parse error: {e}', 'line': None})
        return findings

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                findings.append({'type': 'style', 'message': f'Missing docstring in {node.name}.', 'line': node.lineno})
            if len(node.args.args) > 5:
                findings.append({'type': 'style', 'message': f'{node.name} has too many args.', 'line': node.lineno})

    return findings

def format_findings(findings):
    if not findings:
        return "No issues found."
    return "\n".join(f"[{f['type'].upper()}] Line {f.get('line', '?')}: {f['message']}" for f in findings)

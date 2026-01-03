# apps/code-analyst-agent/app/utils/patterns.py
import ast

DESIGN_PATTERNS = {
    "factory": ["__call__", "create", "build"],
    "singleton": ["__new__", "instance"],
    "observer": ["notify", "subscribe", "unsubscribe"],
    "decorator": ["__call__", "wraps"],
}

def detect_patterns(code: str):
    tree = ast.parse(code)
    names = {n.name for n in ast.walk(tree) if hasattr(n, "name")}

    matches = [p for p, triggers in DESIGN_PATTERNS.items() if set(triggers) & names]
    return matches or ["none_detected"]

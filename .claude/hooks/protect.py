#!/usr/bin/env python3
"""PreToolUse hook: refuse writes to the frozen paths of this program.

The repository root is `$CLAUDE_PROJECT_DIR` when the harness sets it, else the
nearest ancestor of the current directory (or of a path the tool call names) that
holds `space/FROZEN`. That file lists path prefixes relative to the root, one per
line; `#` starts a comment, and a line starting with `!` is an exception: a path
under it is allowed even when a frozen prefix also covers it. Without the file
nothing is frozen, so Phase 0 can create everything. Exit 2 denies the call and
the message on stderr goes back to the model.

Example FROZEN:
    submodules/EICrecon
    !submodules/EICrecon/src/detectors/ZDC
    configs/datasets.yaml
"""
import json
import os
import re
import sys

WRITE_OPERATORS = re.compile(
    r'(>>?|\btee\b|\bsed\s+-i\S*|\brm\b|\bmv\b|\bcp\b|\btouch\b|\btruncate\b|\bln\b|\brmdir\b|\bgit\s+checkout\b|\bgit\s+reset\b|\bgit\s+clean\b)([^;&|]*)'
)
PATH_TOKEN = re.compile(r'(?:^|[\s"\'=])((?:/|\./|\.\./)?[^\s"\'<>|;&=]+/[^\s"\'<>|;&]*|[^\s"\'<>|;&=]+\.[A-Za-z0-9]+)')


def read_frozen(root):
    """(frozen prefixes, allowed prefixes) from <root>/space/FROZEN, or None."""
    try:
        with open(os.path.join(root, "space", "FROZEN")) as f:
            lines = [line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")]
    except OSError:
        return None
    frozen = [line.rstrip("/") for line in lines if not line.startswith("!")]
    allowed = [line[1:].strip().rstrip("/") for line in lines if line.startswith("!")]
    return (frozen, allowed) if frozen else None


def find_root(paths):
    """The project dir, else the first ancestor of cwd or of a named path holding the marker."""
    candidates = []
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        candidates.append(os.environ["CLAUDE_PROJECT_DIR"])
    for start in [os.getcwd()] + [os.path.dirname(os.path.abspath(p)) for p in paths]:
        d = start
        while True:
            candidates.append(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    seen = set()
    for root in candidates:
        if root in seen:
            continue
        seen.add(root)
        rules = read_frozen(root)
        if rules:
            return root, rules
    return None, None


def is_frozen(path, root, rules):
    """True when `path` (any form) lies under a frozen prefix and under no allowed one."""
    frozen, allowed = rules
    rel = os.path.relpath(os.path.abspath(os.path.join(os.getcwd(), path)), root)
    if rel.startswith(".."):
        return False
    under = lambda prefix: rel == prefix or rel.startswith(prefix + "/")
    if any(under(p) for p in allowed):
        return False
    return any(under(p) for p in frozen)


def deny(what):
    sys.stderr.write(
        f"protect: '{what}' is frozen (space/FROZEN; zdc-setup.md, Frozen after Phase 0). "
        "A needed change there is a question in space/QUESTIONS.md, never an edit.\n"
    )
    sys.exit(2)


def main():
    try:
        call = json.load(sys.stdin)
    except Exception:
        return
    tool = call.get("tool_name", "")
    args = call.get("tool_input", {}) or {}

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = args.get("file_path") or args.get("notebook_path") or ""
        if not path:
            return
        root, rules = find_root([path])
        if rules and is_frozen(path, root, rules):
            deny(path)
    elif tool == "Bash":
        command = args.get("command", "") or ""
        tokens = PATH_TOKEN.findall(command)
        root, rules = find_root(tokens)
        if not rules:
            return
        for match in WRITE_OPERATORS.finditer(command):
            operator, rest = match.group(1), match.group(2)
            targets = PATH_TOKEN.findall(rest)
            if operator in ("mv", "cp") and targets:
                targets = targets[-1:]
            for target in targets:
                if is_frozen(target, root, rules):
                    deny(command)


if __name__ == "__main__":
    main()

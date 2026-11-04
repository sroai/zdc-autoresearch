#!/usr/bin/env python3
"""PreToolUse hook: deny writes to the frozen inputs of a CV campaign.

The campaign folder is `$CLAUDE_PROJECT_DIR` when the harness sets it, else the
current directory, else any ancestor of a path the tool call names. The folder's
`space/FROZEN` lists the frozen path prefixes, one per line (`#` starts a comment).
Without that file nothing is frozen, so Step 0 can create the inputs. Exit 2 denies
the call and the message on stderr goes back to the model.
"""
import json
import os
import re
import sys

WRITE_OPERATORS = re.compile(
    r'(>>?|\btee\b|\bsed\s+-i\S*|\brm\b|\bmv\b|\bcp\b|\btouch\b|\btruncate\b|\bln\b|\brmdir\b)([^;&|]*)'
)
ABSOLUTE_PATH = re.compile(r'(?:^|[\s"\'=])(/[^\s"\'<>|;&]+)')


def read_marker(folder):
    """The frozen prefixes listed in <folder>/space/FROZEN, or None."""
    try:
        with open(os.path.join(folder, "space", "FROZEN")) as f:
            prefixes = [line.strip().rstrip("/") for line in f
                        if line.strip() and not line.startswith("#")]
    except OSError:
        return None
    return prefixes or None


def find_prefixes(paths):
    """Look for the marker in the project dir, the cwd, then up from every named path."""
    roots = []
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        roots.append(os.environ["CLAUDE_PROJECT_DIR"])
    roots.append(os.getcwd())
    for p in paths:
        d = os.path.dirname(os.path.abspath(p))
        while True:
            roots.append(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    seen = set()
    for root in roots:
        if root in seen:
            continue
        seen.add(root)
        prefixes = read_marker(root)
        if prefixes:
            return prefixes
    return None


def frozen_pattern(prefixes):
    """A frozen prefix matches as a path, never as a word: a bare folder name (`corpus`,
    `targets`) needs a slash after it, so prose such as "five targets carry" in a heredoc
    does not trip the hook; a file or nested path (`claims.yaml`, `cv/STYLE.md`) matches
    whole. The Bash branch also denies a bare folder name as the whole target of a write."""
    parts = []
    for p in prefixes:
        esc = re.escape(p)
        if "/" in p or "." in p:
            parts.append(r'(?:^|[\s"\'=/])' + esc + r'(?=[\s"\'/]|$)')
        else:
            parts.append(r'(?:^|[\s"\'=/])' + esc + r'(?=/)')
    return re.compile("|".join(parts))


def bare_target(rest, prefixes):
    """The first token of a write's operand (or the destination of mv/cp), unquoted."""
    tokens = rest.split()
    token = tokens[0] if tokens else ""
    return token.strip("\"'").rstrip("/") in prefixes


def deny(what):
    sys.stderr.write(
        f"protect: '{what}' is frozen (space/FROZEN; optimize.md, Files). "
        "A needed change is a question in space/QUESTIONS.md, never an edit.\n"
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
        prefixes = find_prefixes([path] if path else [])
        if prefixes and frozen_pattern(prefixes).search(path):
            deny(path)
    elif tool == "Bash":
        command = args.get("command", "") or ""
        prefixes = find_prefixes(ABSOLUTE_PATH.findall(command))
        if not prefixes:
            return
        frozen = frozen_pattern(prefixes)
        for match in WRITE_OPERATORS.finditer(command):
            operator, rest = match.group(1), match.group(2)
            if operator in ("mv", "cp"):
                tokens = rest.split()
                rest = tokens[-1] if tokens else ""
            if frozen.search(rest) or bare_target(rest, prefixes):
                deny(command)


if __name__ == "__main__":
    main()

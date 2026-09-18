"""Verificateur statique minimal pour Pine Script.

Ne remplace pas le compilateur TradingView. Attrape les fautes qui coutent
le plus cher a decouvrir dans l'editeur : parentheses non fermees,
indentation incoherente, declaration de fonction dans un bloc, appel de
plot() hors de la portee globale.
"""
from __future__ import annotations

import re
import sys


def strip_code(line: str) -> str:
    out, i, in_str = [], 0, None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in "\"'":
            in_str = ch
            i += 1
            continue
        if ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def check(path: str) -> list[str]:
    errs: list[str] = []
    lines = open(path, encoding="utf-8").read().splitlines()
    bal, stmt_start = 0, None
    global_only = ("plot(", "plotshape(", "plotchar(", "bgcolor(", "hline(",
                   "fill(", "alertcondition(", "indicator(", "strategy(", "input.")
    for i, raw in enumerate(lines, 1):
        code = strip_code(raw)
        if not code.strip():
            continue
        indent = len(code) - len(code.lstrip())
        if bal == 0:
            stmt_start = i
            for g in global_only:
                if code.lstrip().startswith(g) and indent > 0:
                    errs.append(f"L{i}: '{g}' doit etre au niveau global (indente de {indent})")
            if re.match(r"^\s+\w+\s*\([^)]*\)\s*=>", code):
                errs.append(f"L{i}: declaration de fonction dans un bloc (interdit en Pine)")
        bal += code.count("(") - code.count(")")
        bal += code.count("[") - code.count("]")
        if bal < 0:
            errs.append(f"L{i}: parenthese fermante en trop")
            bal = 0
    if bal != 0:
        errs.append(f"fin de fichier : {bal} parenthese(s) non fermee(s), "
                    f"derniere instruction commencee L{stmt_start}")

    src = "\n".join(strip_code(l) for l in lines)
    if not re.search(r"^//@version=\d", open(path, encoding="utf-8").read(), re.M):
        errs.append("directive //@version manquante")
    for kw in ("indicator(", "strategy("):
        if kw in src:
            break
    else:
        errs.append("ni indicator() ni strategy() trouve")
    # reassignation sans := sur une variable var
    declared = set(re.findall(r"^var\s+\w+\s+(\w+)\s*=", src, re.M))
    for i, raw in enumerate(lines, 1):
        code = strip_code(raw)
        m = re.match(r"^\s+(\w+)\s*=\s*[^=]", code)
        if m and m.group(1) in declared:
            errs.append(f"L{i}: '{m.group(1)}' est un var, utiliser ':=' et non '='")
    return errs


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        e = check(p)
        print(f"=== {p} ===")
        if e:
            bad += len(e)
            for x in e:
                print("  ANOMALIE:", x)
        else:
            print("  aucune anomalie detectee")
    sys.exit(1 if bad else 0)

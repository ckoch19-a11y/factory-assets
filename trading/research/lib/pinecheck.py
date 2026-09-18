"""Verificateur statique pour Pine Script v6.

Ne remplace pas le compilateur TradingView, qui n'est pas accessible hors du
navigateur. Attrape les fautes qui font perdre le plus de temps dans
l'editeur, et refuse de signaler ce dont il n'est pas sur : un faux positif
coute plus cher qu'un controle manquant.
"""
from __future__ import annotations

import re
import sys

# Espaces de noms et identifiants globaux de Pine v6 utilises par ce projet.
NAMESPACES = {
    "ta", "math", "str", "array", "matrix", "map", "color", "table", "label",
    "line", "box", "polyline", "strategy", "input", "timeframe", "syminfo",
    "barstate", "session", "request", "ticker", "chart", "currency", "dayofweek",
    "display", "extend", "format", "hline", "location", "order", "plot",
    "position", "scale", "shape", "size", "text", "xloc", "yloc", "font",
    "adjustment", "backadjustment", "settlement", "earnings", "dividends",
    "splits", "runtime", "log", "alert", "time",
}
GLOBAL_FUNCS = {
    "plot", "plotshape", "plotchar", "plotarrow", "plotbar", "plotcandle",
    "bgcolor", "barcolor", "fill", "hline", "alertcondition", "indicator",
    "strategy", "library", "nz", "na", "int", "float", "bool", "string",
    "color", "max", "min", "abs", "timestamp", "time", "time_close", "input",
    "alert", "label", "line", "box", "table", "array", "log", "runtime",
}
GLOBAL_ONLY = ("plot(", "plotshape(", "plotchar(", "plotarrow(", "plotbar(",
               "plotcandle(", "bgcolor(", "barcolor(", "fill(", "hline(",
               "alertcondition(", "indicator(", "strategy(", "library(")


def strip_code(line: str) -> str:
    """Retire chaines litterales et commentaires, garde la structure."""
    out, i, in_str = [], 0, None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                out.append(" ")
                i += 2
                continue
            if ch == in_str:
                in_str = None
            out.append(" ")
            i += 1
            continue
        if ch in "\"'":
            in_str = ch
            out.append(" ")
            i += 1
            continue
        if ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def _indent(raw: str) -> int:
    """Indentation mesuree sur la ligne brute.

    strip_code remplace chaque caractere de chaine par une espace : mesurer
    l'indentation sur sa sortie donnerait un resultat faux des qu'une ligne
    commence par une chaine litterale.
    """
    return len(raw) - len(raw.lstrip())


def check(path: str) -> list[str]:
    errs: list[str] = []
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    codes = [strip_code(l) for l in lines]

    # -- directive et type de script --------------------------------------
    if not re.search(r"^//@version=6\s*$", text, re.M):
        errs.append("directive //@version=6 absente ou mal ecrite")
    if not any(re.match(r"^(indicator|strategy|library)\s*\(", c) for c in codes):
        errs.append("aucun appel indicator() / strategy() / library() au niveau global")

    # -- tabulations : Pine les refuse dans l'indentation ------------------
    for i, l in enumerate(lines, 1):
        if l[:len(l) - len(l.lstrip())].count("\t"):
            errs.append(f"L{i}: tabulation dans l'indentation (Pine exige des espaces)")

    # -- caracteres non ASCII hors chaines et commentaires -----------------
    for i, c in enumerate(codes, 1):
        for ch in c:
            if ord(ch) > 127:
                errs.append(f"L{i}: caractere non ASCII '{ch}' dans le code "
                            f"(autorise seulement dans les chaines et commentaires)")
                break

    # -- equilibrage des parentheses sur instructions completes ------------
    bal, start = 0, None
    for i, c in enumerate(codes, 1):
        if not c.strip():
            continue
        if bal == 0:
            start = i
        bal += c.count("(") - c.count(")") + c.count("[") - c.count("]")
        if bal < 0:
            errs.append(f"L{i}: parenthese ou crochet fermant en trop")
            bal = 0
    if bal != 0:
        errs.append(f"fin de fichier : {bal} parenthese(s) non fermee(s), "
                    f"instruction commencee L{start}")

    # -- appels reserves au niveau global ----------------------------------
    bal = 0
    for i, c in enumerate(codes, 1):
        if not c.strip():
            continue
        if bal == 0:
            indent = _indent(lines[i - 1])
            for g in GLOBAL_ONLY:
                if c.lstrip().startswith(g) and indent > 0:
                    errs.append(f"L{i}: '{g[:-1]}()' doit etre au niveau global "
                                f"(indente de {indent} espaces)")
        bal += c.count("(") - c.count(")") + c.count("[") - c.count("]")
        bal = max(bal, 0)

    # -- declaration de fonction dans un bloc -------------------------------
    for i, c in enumerate(codes, 1):
        if re.match(r"^\s+[\w.]+\s*\([^()]*\)\s*=>", c):
            errs.append(f"L{i}: declaration de fonction indentee "
                        f"(Pine n'accepte les fonctions qu'au niveau global)")

    # -- 'var' doit etre au niveau global ----------------------------------
    for i, c in enumerate(codes, 1):
        if re.match(r"^\s+var(ip)?\s+", c):
            errs.append(f"L{i}: 'var' declare dans un bloc indente")

    # -- bloc if/else/for/while sans corps indente -------------------------
    for i, c in enumerate(codes[:-1], 1):
        s = c.rstrip()
        if re.match(r"^\s*(if|else if|else|for|while|switch)\b.*$", s) and not s.endswith("=>"):
            if re.match(r"^\s*(if|else if|for|while|switch)\b", s) and "?" in s and ":" in s:
                continue  # ternaire sur la meme ligne
            ind = _indent(lines[i - 1])
            nxt = next((j for j in range(i, len(codes)) if codes[j].strip()), None)
            if nxt is not None and _indent(lines[nxt]) <= ind:
                errs.append(f"L{i}: bloc '{s.strip()[:28]}' sans corps plus indente")

    # -- indentation des lignes de continuation ----------------------------
    # Regle Pine : une ligne qui prolonge l'instruction precedente doit etre
    # indentee d'un nombre d'espaces qui n'est PAS un multiple de quatre,
    # sinon l'interpreteur la lit comme un nouveau bloc.
    bal = 0
    for i, c in enumerate(codes, 1):
        if not c.strip():
            continue
        if bal > 0:
            ind = _indent(lines[i - 1])
            if ind % 4 == 0:
                errs.append(f"L{i}: ligne de continuation indentee de {ind} espaces "
                            f"(multiple de 4 : Pine y verra un nouveau bloc)")
        bal += c.count("(") - c.count(")") + c.count("[") - c.count("]")
        bal = max(bal, 0)

    # -- ':=' sur un nom jamais declare ------------------------------------
    declared = set(re.findall(r"\b(?:var|varip)?\s*(?:int|float|bool|string|color|table|label|line|box|array)?\s*(\w+)\s*=(?!=)", "\n".join(codes)))
    declared |= set(re.findall(r"^(\w+)\s*=(?!=)", "\n".join(codes), re.M))
    declared |= set(re.findall(r"\b(\w+)\s*\([^()]*\)\s*=>", "\n".join(codes)))
    for i, c in enumerate(codes, 1):
        m = re.match(r"^\s*(\w+)\s*:=", c)
        if m and m.group(1) not in declared:
            errs.append(f"L{i}: ':=' sur '{m.group(1)}' qui n'est jamais declare")

    # -- reaffectation d'un 'var' avec '=' au lieu de ':=' -----------------
    varnames = set(re.findall(r"^var(?:ip)?\s+\w+\s+(\w+)\s*=", "\n".join(codes), re.M))
    for i, c in enumerate(codes, 1):
        m = re.match(r"^\s+(\w+)\s*=(?!=)", c)
        if m and m.group(1) in varnames:
            errs.append(f"L{i}: '{m.group(1)}' est un 'var', il faut ':=' et non '='")

    # -- regles propres a Pine v6 ------------------------------------------
    # 1. Un booleen ne peut plus valoir na : na(), nz() et fixnan() refusent
    #    un argument booleen.
    bool_names = set(re.findall(r"^\s*(?:var(?:ip)?\s+)?bool\s+(\w+)\s*=", "\n".join(codes), re.M))
    bool_names |= set(re.findall(r"^(\w+)\s*=\s*input\.bool\(", "\n".join(codes), re.M))
    for i, c in enumerate(codes, 1):
        for fn in ("na", "nz", "fixnan"):
            for arg in re.findall(rf"\b{fn}\s*\(\s*(\w+)", c):
                if arg in bool_names:
                    errs.append(f"L{i}: {fn}() applique au booleen '{arg}' "
                                f"(interdit en v6 : un bool ne peut plus valoir na)")

    # 2. Plus de cast implicite nombre -> booleen : 'if x' sur un nombre doit
    #    devenir 'if x != 0'.
    num_names = set(re.findall(r"^\s*(?:var(?:ip)?\s+)?(?:int|float)\s+(\w+)\s*=", "\n".join(codes), re.M))
    num_names |= set(re.findall(r"^(\w+)\s*=\s*input\.(?:int|float)\(", "\n".join(codes), re.M))
    for i, c in enumerate(codes, 1):
        m = re.match(r"^\s*(?:if|else if|while)\s+(?:not\s+)?(\w+)\s*$", c.rstrip())
        if m and m.group(1) in num_names:
            errs.append(f"L{i}: 'if {m.group(1)}' teste un nombre "
                        f"(v6 exige une comparaison explicite, ex. '!= 0')")

    # 3. 'and'/'or' sont a evaluation paresseuse : un appel ta.* place a droite
    #    peut ne jamais s'executer, ce qui fausse les series a etat.
    for i, c in enumerate(codes, 1):
        if re.search(r"\b(and|or)\b[^\n]*\bta\.\w+\s*\(", c):
            errs.append(f"L{i}: appel 'ta.*' a droite d'un 'and'/'or' "
                        f"(evaluation paresseuse en v6 : sortir l'appel au niveau global)")

    # -- division entiere involontaire -------------------------------------
    # En Pine, int / int donne un int : 141 / 291 vaut 0, pas 0,48. C'est une
    # faute silencieuse - le script compile et affiche un resultat faux.
    joined = "\n".join(codes)
    int_names = set(re.findall(r"^\s*(?:var(?:ip)?\s+)?int\s+(\w+)\s*=", joined, re.M))
    int_names |= set(re.findall(r"^(\w+)\s*=\s*input\.int\(", joined, re.M))
    int_names |= {"bar_index", "nWin", "nLoss"} & int_names
    float_names = set(re.findall(r"^\s*(?:var(?:ip)?\s+)?float\s+(\w+)\s*=", joined, re.M))
    float_names |= set(re.findall(r"^(\w+)\s*=\s*input\.float\(", joined, re.M))
    for i, c in enumerate(codes, 1):
        for m in re.finditer(r"\b(\w+)\s*/\s*(\w+)\b", c):
            a, b = m.group(1), m.group(2)
            if a not in int_names or b not in int_names:
                continue
            # '100.0 * nWin / nT' est deja promu en flottant par la gauche :
            # on ne signale que si rien de flottant ne precede la division.
            avant = c[:m.start()]
            promu = re.search(r"\d+\.\d", avant) or any(
                re.search(rf"\b{re.escape(f)}\b", avant) for f in float_names)
            if not promu:
                errs.append(f"L{i}: '{a} / {b}' divise deux entiers "
                            f"(Pine tronque le resultat ; multiplier par 1.0 d'abord)")

    # -- espace de noms inconnu --------------------------------------------
    for i, c in enumerate(codes, 1):
        # on ne controle que la racine de la chaine : strategy.opentrades.x()
        # est un espace de noms imbrique parfaitement valide
        for ns in re.findall(r"\b([a-z_]\w*)(?:\.\w+)+\s*\(", c):
            if ns not in NAMESPACES and ns not in declared:
                errs.append(f"L{i}: espace de noms inconnu '{ns}.'")
    return errs


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        e = check(p)
        print(f"=== {p} ===")
        if e:
            total += len(e)
            for x in e:
                print("  ANOMALIE :", x)
        else:
            print("  aucune anomalie detectee")
    print(f"\n{total} anomalie(s) au total.")
    sys.exit(1 if total else 0)

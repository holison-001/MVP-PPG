"""Schematic display conventions; preserve explicit ratings as separate fields."""
import re


def normalize_value(ref, value, mpn=""):
    family = re.match(r"[A-Za-z]+", ref)
    family = family.group() if family else ""
    ratings = {}
    if family in {"R", "C"}:
        for field, pattern, suffix in [
            ("Voltage", r"(\d+(?:\.\d+)?)\s*V\b", " V"),
            ("Tolerance", r"(\d+(?:\.\d+)?)\s*%", "%"),
            ("Dielectric", r"\b(X[578][RS]|C0G|NP0)\b", ""),
        ]:
            match = re.search(pattern, value)
            if match:
                ratings[field] = match.group(1) + suffix
        number = r"(\d+(?:\.\d+)?)"
        if family == "R":
            match = re.match(r"^\s*" + number + r"\s*([kKMm]?)(?:\s*(?:Ω|ohms?|R))?", value)
            if match:
                value = match.group(1) + " " + match.group(2).replace("K", "k") + "Ω"
        else:
            match = re.match(r"^\s*" + number + r"\s*([pnuµμm]?)F", value)
            if match:
                prefix = match.group(2).replace("u", "µ").replace("μ", "µ")
                value = match.group(1) + " " + prefix + "F"
    elif family in {"U", "D", "FB", "Q"} and mpn:
        value = mpn
    return value, ratings

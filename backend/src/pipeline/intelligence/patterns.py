import re

def build_patterns(mpn: str):
    # JSON-safe patterns (double-escaped backslashes)
    exact = f"\\\\b{mpn}\\\\b"
    spaced = "\\\\b" + "\\s*".join(list(mpn)) + "\\\\b"
    date_code = "\\\\b[0-9O]{2}\\\\s*[0-9O]{2}\\\\b|\\\\b[0-9O]{3,4}\\\\b"
    lot_code = "\\\\b[0-9A-Z]{2,10}\\\\b"

    return {
        "part_code": f"{exact}|{spaced}",
        "date_code": date_code,
        "lot_code": lot_code
    }

def normalize_package(desc: str, img: str = "") -> str:
    text = f"{desc} {img}".lower()
    m = re.search(r"(lqfp|qfn|bga|soic|tssop|tsop|dip)[-_ ]?(\d+)", text)
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    return "Unknown"

def logo_from_oem(oem: str) -> str:
    o = (oem or "").lower()
    if "stmicro" in o:
        return "ST"
    if "texas instruments" in o or o.strip() == "ti":
        return "TI"
    if "winbond" in o:
        return "WINB"
    if "microchip" in o or "atmel" in o:
        return "MICROCHIP"
    if "on semi" in o or "on semiconductor" in o:
        return "ONSEMI"
    if "nexperia" in o:
        return "NEXP"
    return (oem or "")[:4].upper()
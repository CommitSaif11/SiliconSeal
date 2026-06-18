from fastapi import APIRouter, HTTPException, Depends
import json

from engine.kb_loader import load_raw_kb, validate_entry, KB_FILE
from pipeline.intelligence.mouser_service import fetch_ic
from pipeline.intelligence.patterns import build_patterns, normalize_package, logo_from_oem
from core.auth import require_admin

router = APIRouter()


def _upsert_kb_entry(entry: dict):
    kb = load_raw_kb()
    validate_entry(entry)

    pid = entry.get("part_id")
    if not pid:
        raise ValueError("KB entry missing part_id")

    updated = False
    for i, e in enumerate(kb):
        if e.get("part_id") == pid:
            kb[i] = entry
            updated = True
            break
    if not updated:
        kb.append(entry)

    KB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with KB_FILE.open("w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    return {"updated": updated, "count": len(kb)}


@router.post("/admin/kb/enrich-and-save")
async def enrich_and_save(part: str, _user: dict = Depends(require_admin)):
    data = fetch_ic(part)
    if not data:
        raise HTTPException(status_code=404, detail="IC not found in Mouser")

    mpn = data.get("ManufacturerPartNumber", "")
    oem = data.get("Manufacturer", "")
    desc = data.get("Description", "")
    img = data.get("ImagePath", "")

    if not mpn or not oem:
        raise HTTPException(status_code=400, detail="Incomplete Mouser response (missing MPN or Manufacturer)")

    pkg = normalize_package(desc, img)
    logo_hint = logo_from_oem(oem)
    patterns = build_patterns(mpn)

    entry = {
        "part_id": mpn.lower(),
        "oem": oem,
        "part_number": mpn,
        "package": pkg,
        "logo_hint": logo_hint,
        "patterns": patterns
    }

    try:
        result = _upsert_kb_entry(entry)
        return {
            "status": "success",
            "operation": "update" if result["updated"] else "insert",
            "kb_count": result["count"],
            "saved_part_id": entry["part_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save KB entry: {e}")

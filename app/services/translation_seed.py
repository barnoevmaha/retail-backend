import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.translation import Translation

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "seed_translations.json"


def ensure_translations_seeded(db: Session) -> int:
    """Insert missing seed translations and heal rows stuck on the English key.

    Rows where every language equals the key are provider-outage artifacts
    (the fallback never got a real translation and is never retried). Curated
    seed keys are restored from the seed file, anything else is deleted so the
    next sync re-translates it.
    """
    if not SEED_FILE.exists():
        logger.warning("Seed translations file not found: %s", SEED_FILE)
        return 0
    seed = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    seed_by_key = {r["key"]: r for r in seed}

    stuck = (
        db.query(Translation)
        .filter(
            Translation.en == Translation.ru,
            Translation.ru == Translation.uz,
            Translation.en == Translation.key,
        )
        .all()
    )
    healed = purged = 0
    for row in stuck:
        curated = seed_by_key.get(row.key)
        if curated and curated["en"] == curated["ru"] == curated["uz"]:
            continue  # intentionally identical in every language
        if curated:
            row.en, row.ru, row.uz = curated["en"], curated["ru"], curated["uz"]
            healed += 1
        else:
            db.delete(row)
            purged += 1
    if healed or purged:
        logger.info("Translation heal: %d restored, %d purged for re-translation", healed, purged)

    existing = db.query(Translation.key).filter(Translation.key.in_(seed_by_key)).all()
    existing_keys = {k[0] for k in existing}
    added = 0
    for rec in seed:
        if rec["key"] in existing_keys:
            continue
        db.add(Translation(key=rec["key"], en=rec["en"], ru=rec["ru"], uz=rec["uz"]))
        added += 1
    if added:
        logger.info("Seeded %d translation(s)", added)
    return added

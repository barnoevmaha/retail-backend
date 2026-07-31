import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.translation import Translation

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "seed_translations.json"


def ensure_translations_seeded(db: Session) -> int:
    """Insert seed translations (the project's existing dictionaries) that are missing."""
    if not SEED_FILE.exists():
        logger.warning("Seed translations file not found: %s", SEED_FILE)
        return 0
    seed = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    existing = db.query(Translation.key).filter(Translation.key.in_([r["key"] for r in seed])).all()
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

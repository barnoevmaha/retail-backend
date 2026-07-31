from sqlalchemy.orm import Session

from app.models.translation import Translation


class TranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_many(self, keys: list[str]) -> dict[str, Translation]:
        if not keys:
            return {}
        rows = self.db.query(Translation).filter(Translation.key.in_(keys)).all()
        return {r.key: r for r in rows}

    def get_all(self) -> list[Translation]:
        return self.db.query(Translation).order_by(Translation.key).all()

    def upsert_many(self, records: list[dict]) -> list[Translation]:
        """records: [{key, en, ru, uz}] — insert new rows, update existing ones."""
        saved = []
        for rec in records:
            row = self.db.query(Translation).filter(Translation.key == rec["key"]).first()
            if row:
                row.en = rec["en"]
                row.ru = rec["ru"]
                row.uz = rec["uz"]
            else:
                row = Translation(**rec)
                self.db.add(row)
            saved.append(row)
        self.db.commit()
        return saved

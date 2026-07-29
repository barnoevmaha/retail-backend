from sqlalchemy.orm import Session

from app.models.setting import Setting


class SettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> str | None:
        s = self.db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else None

    def set(self, key: str, value: str) -> Setting:
        s = self.db.query(Setting).filter(Setting.key == key).first()
        if s:
            s.value = value
        else:
            s = Setting(key=key, value=value)
            self.db.add(s)
        self.db.commit()
        return s

    def all(self) -> list[Setting]:
        return self.db.query(Setting).all()

    def get_many(self, prefix: str = "") -> dict:
        query = self.db.query(Setting)
        if prefix:
            query = query.filter(Setting.key.like(f"{prefix}%"))
        return {s.key: s.value for s in query.all()}

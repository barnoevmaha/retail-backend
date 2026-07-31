class TranslationCache:
    """In-memory translation store — checked before the database on every lookup."""

    def __init__(self):
        self._data: dict[str, dict] = {}

    def prime(self, rows: list) -> None:
        self._data = {r.key: {"key": r.key, "en": r.en, "ru": r.ru, "uz": r.uz} for r in rows}

    def get_many(self, keys: list[str]) -> tuple[dict[str, dict], list[str]]:
        found, missing = {}, []
        for key in keys:
            entry = self._data.get(key)
            if entry is None:
                missing.append(key)
            else:
                found[key] = entry
        return found, missing

    def set_many(self, entries: dict[str, dict]) -> None:
        self._data.update(entries)

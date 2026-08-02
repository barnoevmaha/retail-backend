import re
import unicodedata
from collections.abc import Callable

MAX_SLUG_LEN = 120

_CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ў": "o", "қ": "q", "ғ": "g", "ҳ": "h",
}
_CYRILLIC_RE = re.compile("[" + "".join(_CYRILLIC) + "".join(k.upper() for k in _CYRILLIC) + "]")


def slugify(text: str) -> str:
    """URL-safe slug: lowercase latin, non-alphanumeric runs -> '-', apostrophes dropped."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = _CYRILLIC_RE.sub(lambda m: _CYRILLIC.get(m.group(0).lower(), ""), text)
    text = text.replace("'", "").replace("\u02bb", "")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return slug.strip("-")


def unique_slug(base: str, exists: Callable[[str], bool], max_len: int = MAX_SLUG_LEN) -> str:
    """Append -2, -3, ... until the slug is free. Never exceeds max_len."""
    base = base[:max_len].rstrip("-")
    if not exists(base):
        return base
    i = 2
    while True:
        suffix = f"-{i}"
        candidate = f"{base[:max_len - len(suffix)]}{suffix}"
        if not exists(candidate):
            return candidate
        i += 1

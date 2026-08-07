import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_BYTES = settings.max_upload_size_bytes
CHUNK = 64 * 1024
MAGIC_HEAD = 16

_JPEG = b"\xff\xd8\xff"
_PNG = b"\x89PNG\r\n\x1a\n"
_RIFF = b"RIFF"
_WEBP = b"WEBP"
_ALLOWED = {"jpg", "png", "webp"}


def _detect(head: bytes) -> str | None:
    if len(head) < 12:
        return None
    if head.startswith(_JPEG):
        return "jpg"
    if head.startswith(_PNG):
        return "png"
    if head[:4] == _RIFF and head[8:12] == _WEBP:
        return "webp"
    return None


def save_uploaded_image(file: UploadFile) -> str:
    """Validate magic bytes and save an uploaded image; return /uploads URL.

    Never trusts the filename extension or Content-Type header. Reads in
    chunks so a malicious oversized file is rejected without loading it all
    into memory. Filename is a fresh uuid + the extension of the detected
    format, so nothing client-controlled is ever used as a path segment.
    """
    head = file.file.read(MAGIC_HEAD)
    ext = _detect(head)
    if not ext:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: JPEG, PNG, WebP.",
        )

    filename = f"{uuid.uuid4().hex}.{ext}"
    dst = UPLOAD_DIR / filename
    total = 0
    with open(dst, "wb") as out:
        out.write(head)
        total += len(head)
        while chunk := file.file.read(CHUNK):
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                out.close()
                dst.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
                )
            out.write(chunk)
    return f"/uploads/{filename}"
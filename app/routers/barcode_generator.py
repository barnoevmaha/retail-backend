from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, Response

from app.utils.barcode import generate_barcode, validate_barcode, barcode_svg, barcode_label_html

router = APIRouter(prefix="/api/barcodes", tags=["barcodes"])


@router.get("/generate")
def generate(barcode: str | None = None):
    code = barcode if barcode and validate_barcode(barcode) else generate_barcode()
    return {"barcode": code, "valid": validate_barcode(code)}


@router.get("/svg")
def barcode_svg_endpoint(
    code: str = Query("2000000000000"),
    height: int = Query(60),
    label: bool = Query(True),
):
    svg = barcode_svg(code, height, label)
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/label", response_class=HTMLResponse)
def barcode_label(
    code: str = Query("2000000000000"),
    product: str = Query(""),
    price: str = Query(""),
):
    html = barcode_label_html(code, product, price)
    return HTMLResponse(content=html)


@router.get("/download")
def barcode_download(
    code: str = Query("2000000000000"),
    height: int = Query(60),
):
    svg = barcode_svg(code, height, label=True)
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Content-Disposition": f'attachment; filename="barcode-{code}.svg"'})

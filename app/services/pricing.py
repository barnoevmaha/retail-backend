FREE_DELIVERY_OVER = 500.0
DELIVERY_FEE = 10.0


def delivery_fee_for(subtotal: float) -> float:
    return 0.0 if subtotal >= FREE_DELIVERY_OVER else DELIVERY_FEE
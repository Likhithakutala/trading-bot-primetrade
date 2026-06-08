from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}'. Use something like BTCUSDT or 1000PEPEUSDT.")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return t


def validate_quantity(quantity: str) -> str:
    try:
        q = Decimal(str(quantity))
        if q <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        return str(q)
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")


def validate_price(price: str) -> str:
    try:
        p = Decimal(str(price))
        if p <= 0:
            raise ValidationError("Price must be greater than 0.")
        return str(p)
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")


def validate_stop_price(stop_price: str) -> str:
    return validate_price(stop_price)

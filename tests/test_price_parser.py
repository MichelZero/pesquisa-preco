from app import normalize_price_text


def test_normalize_price_text_with_currency_and_thousands():
    assert normalize_price_text("R$ 7.500,00") == 7500.0


def test_normalize_price_text_with_decimal_separator():
    assert normalize_price_text("1.299,90") == 1299.9


def test_normalize_price_text_without_cents():
    assert normalize_price_text("7500") == 7500.0

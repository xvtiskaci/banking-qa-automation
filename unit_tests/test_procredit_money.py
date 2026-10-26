import pytest

from utils.ProcreditMoney import parse_gel_amount


@pytest.mark.unit
@pytest.mark.parametrize('display,expected', [
    ('10.00 GEL', '10.00'),
    ('0.00 ₾', '0.00'),
    ('1 234,56 GEL', '1234.56'),
    ('1,234.56 GEL', '1234.56'),
    ('10.00\nGEL', '10.00'),
])
def test_parse_gel_amount(display, expected):
    assert str(parse_gel_amount(display)) == expected


@pytest.mark.unit
def test_rejects_empty_balance():
    with pytest.raises(ValueError):
        parse_gel_amount('GEL')

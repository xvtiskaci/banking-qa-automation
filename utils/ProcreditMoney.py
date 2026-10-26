import re
from decimal import Decimal, InvalidOperation


def parse_gel_amount(value: str) -> Decimal:
    text = str(value).replace('\u00a0', '').replace('\u202f', '').replace(' ', '')
    match = re.search(r'-?[\d][\d,.]*', text)
    if match is None:
        raise ValueError('No numeric balance found')
    number = match.group(0)
    if ',' in number and '.' in number:
        if number.rfind('.') > number.rfind(','):
            number = number.replace(',', '')
        else:
            number = number.replace('.', '').replace(',', '.')
    elif ',' in number:
        number = number.replace(',', '.')
    try:
        return Decimal(number)
    except InvalidOperation as exc:
        raise ValueError('Invalid displayed balance format') from exc

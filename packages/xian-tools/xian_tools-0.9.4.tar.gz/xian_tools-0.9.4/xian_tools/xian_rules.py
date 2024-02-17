import re


def kwargs_are_formatted(k: dict):
    for k in k.keys():
        if not identifier_is_formatted(k):
            return False
    return True


def identifier_is_formatted(s: str):
    try:
        iden = re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', s)
        if iden is None:
            return False
        return True
    except TypeError:
        return False


def number_is_formatted(i: int):
    if type(i) != int:
        return False
    if i < 0:
        return False
    return True


def key_is_formatted(s: str):
    try:
        int(s, 16)
        if len(s) != 64:
            return False
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def cid_id_formated(s: str):
    return isinstance(s, str)


TRANSACTION_PAYLOAD_RULES = {
    'sender': key_is_formatted,
    'nonce': number_is_formatted,
    'stamps_supplied': number_is_formatted,
    'contract': identifier_is_formatted,
    'function': identifier_is_formatted,
    'kwargs': kwargs_are_formatted,
    'chain_id': cid_id_formated
}

import os
import random
import string


env: str = os.environ.get('ENV')


def generate_auth_code() -> str:
    """
    Generates authorization code
    :return: default auth code or generated one
    :rtype: str
    """
    if env == 'test':
        return '1111'
    if env == 'deploy':
        size: int = 4
        digits: str = string.digits
        return ''.join(random.choice(digits) for r in range(size))


def generate_invite_code() -> str:
    """
    Generates invite code
    :return: generated invite code
    :rtype: str
    """
    size: int = 6
    chars_upper: str = string.ascii_uppercase
    digits: str = string.digits
    return ''.join(random.choice(chars_upper + digits) for r in range(size))



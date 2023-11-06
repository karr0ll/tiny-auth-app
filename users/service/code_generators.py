import os
import random
import string

from dotenv import load_dotenv


def generate_invite_code() -> str:
    load_dotenv()
    size: int = int(os.environ.get('INVITE_CODE_SIZE'))
    chars_upper: str = string.ascii_uppercase
    digits: str = string.digits
    return ''.join(random.choice(chars_upper + digits) for r in range(size))


def generate_auth_code() -> str:
    load_dotenv()
    size: int = int(os.environ.get('AUTH_CODE_SIZE'))
    digits: str = string.digits
    return ''.join(random.choice(digits) for r in range(size))

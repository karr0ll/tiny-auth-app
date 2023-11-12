import os
import time

from smsaero import SmsAero

env = os.environ.get('ENV')


def send_auth_code(phone: str, auth_code: str) -> None:
    """
    Function to send auth code.
    If env == 'test' does nothing,
    Else calls SmsAero method to send code to accepted number
    :param phone: phone number
    :type phone: str
    :param auth_code: authorization code
    :type auth_code: str
    :return: None
    :rtype: None
    """
    if env == 'test':
        time.sleep(2)
    if env == 'deploy':
        sms_aero_email = os.environ.get('SMSAERO_EMAIL')
        api_key = os.environ.get('SMSAERO_API_KEY')
        app = SmsAero(sms_aero_email, api_key)
        send_code = app.send(phone, auth_code)




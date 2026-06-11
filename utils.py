from kavenegar import *
from django.conf import settings


def normalize_ir_phone(phone: str) -> str:
    phone = phone.strip()

    # remove + if exists
    if phone.startswith('+'):
        phone = phone[1:]

    # 989xxxxxxxxx → 09xxxxxxxxx
    if phone.startswith('98') and len(phone) == 12:
        phone = '0' + phone[2:]

    # 9xxxxxxxxx → 09xxxxxxxxx
    if phone.startswith('9') and len(phone) == 10:
        phone = '0' + phone

    # final validation
    if not phone.startswith('09') or len(phone) != 11:
        raise ValueError("Invalid Iranian phone number")

    return phone

########################################################################

def send_otp_code(phone, code):

    phone = normalize_ir_phone(phone)

    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)

        params = {
            'receptor': phone,
            'template': 'template',
            'token': code,
            'type': 'sms'
        }

        response = api.verify_lookup(params)
        print("SMS Response:", response)
        return response

    except APIException as e:
        print("Kavenegar APIException:", e)
        raise

    except HTTPException as e:
        print("Kavenegar HTTPException:", e)
        raise

    except Exception as e:
        print("GENERAL OTP ERROR:", e)
        raise
#######################################################################

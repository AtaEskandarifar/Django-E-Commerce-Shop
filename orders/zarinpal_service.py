import requests
from django.conf import settings
import logging
##########################################################################################################

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# ZARINPAL CONFIG
# --------------------------------------------------------------------
if settings.ZARINPAL_SANDBOX:
    REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    STARTPAY_URL = "https://sandbox.zarinpal.com/pg/StartPay/"
else:
    REQUEST_URL = "https://payment.zarinpal.com/pg/v4/payment/request.json"
    VERIFY_URL = "https://payment.zarinpal.com/pg/v4/payment/verify.json"
    STARTPAY_URL = "https://payment.zarinpal.com/pg/StartPay/"

# --------------------------------------------------------------------
# INITIATE PAYMENT
# --------------------------------------------------------------------
def initiate_payment(amount, description, callback_url,
                     email=None, mobile=None, order_id=None):

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount),
        "currency": "IRR",
        "description": description,
        "callback_url": callback_url,
    }

    # Metadata overrides Panel settings
    metadata = {"auto_verify": False, "order_id": str(order_id) if order_id else "N/A"}

    if email:
        metadata["email"] = email

    if mobile:
        metadata["mobile"] = mobile

    if order_id:
        metadata["order_id"] = str(order_id)

    payload["metadata"] = metadata

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            REQUEST_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"ZarinPal initiate-payment connection error: {e}")
        raise Exception("خطا در اتصال به درگاه پرداخت. لطفا دوباره تلاش کنید.")

    # Handle invalid JSON or empty body safely
    try:
        result = response.json()
    except ValueError:
        logger.error(f"Invalid JSON from ZarinPal on initiate_payment: {response.text}")
        raise Exception("پاسخ نامعتبر از درگاه پرداخت دریافت شد.")

    logger.info(f"ZarinPal initiate_payment response: {result}")

    data = result.get("data")
    errors = result.get("errors")

    # Successful initiation
    if data and data.get("code") == 100:
        authority = data["authority"]
        return f"{STARTPAY_URL}{authority}", authority

    # Return meaningful errors
    error_message = ""
    if errors:
        error_message = errors.get("message", "")
    else:
        error_message = str(result)

    raise Exception(f"ZarinPal error: {error_message}")


# --------------------------------------------------------------------
# VERIFY PAYMENT
# --------------------------------------------------------------------
def verify_payment(amount, authority):

    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount),
        "authority": authority,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            VERIFY_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"ZarinPal verify-payment connection error: {e}")
        return False, None

    try:
        result = response.json()
    except ValueError:
        logger.error(f"Invalid JSON from ZarinPal on verify_payment: {response.text}")
        return False, None

    logger.info(f"ZarinPal verify_payment response: {result}")

    data = result.get("data")
    errors = result.get("errors")

    if errors:
        logger.warning(f"ZarinPal verify errors: {errors}")

    # Verification success
    if data and data.get("code") in [100, 101]:
        return True, data.get("ref_id")

    return False, None
##########################################################################################################

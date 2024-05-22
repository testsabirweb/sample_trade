from urllib.parse import parse_qs, urlparse
import pyotp
import requests
from fyers_apiv3 import fyersModel
import base64
import time as time_module
from custom_logger import log_path, logger

from my_secrets import CLIENT_ID, FY_ID, PIN, REDIRECT_URI, SECRET_KEY, TOTP_KEY


def auto_login():
    def get_encoded_string(string):
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    # Initial session for OTP and PIN verification
    ses = requests.Session()

    # Step 1: Send Login OTP
    otp_response = ses.post(
        "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2",
        json={"fy_id": get_encoded_string(FY_ID), "app_id": "2"},
    ).json()
    if "request_key" not in otp_response:
        return "Failed to initiate OTP"

    # Wait to ensure OTP is valid
    # Adjust based on OTP generation and validation timing
    time_module.sleep(2)

    # Step 2: Verify OTP
    verified_otp_response = ses.post(
        "https://api-t2.fyers.in/vagator/v2/verify_otp",
        json={
            "request_key": otp_response["request_key"],
            "otp": pyotp.TOTP(TOTP_KEY).now(),
        },
    ).json()
    if "request_key" not in verified_otp_response:
        return "Failed to verify OTP"

    # Step 3: Verify PIN
    verified_pin_response = ses.post(
        "https://api-t2.fyers.in/vagator/v2/verify_pin_v2",
        json={
            "request_key": verified_otp_response["request_key"],
            "identity_type": "pin",
            "identifier": get_encoded_string(PIN),
        },
    ).json()
    if (
        "data" not in verified_pin_response
        or "access_token" not in verified_pin_response["data"]
    ):
        return "Failed to verify PIN"

    # Update session headers for further requests
    ses.headers.update(
        {"Authorization": f"Bearer {verified_pin_response['data']['access_token']}"}
    )

    # Request to obtain auth_code (simulating redirect flow)
    response = ses.post(
        "https://api-t1.fyers.in/api/v3/token",
        json={
            "fyers_id": FY_ID,
            "app_id": CLIENT_ID[:-4],
            "redirect_uri": REDIRECT_URI,
            "appType": "100",
            "code_challenge": "",
            "state": "None",
            "scope": "",
            "nonce": "",
            "response_type": "code",
            "create_cookie": True,
        },
    ).json()
    if "Url" not in response:
        return "Failed to obtain auth code URL"

    # Extract auth_code from URL
    auth_code = parse_qs(urlparse(response["Url"]).query)["auth_code"][0]

    # Initialize session with the Fyers API to obtain access token
    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code",
    )
    session.set_token(auth_code)
    token_response = session.generate_token()
    if "access_token" not in token_response:
        return "Failed to generate access token"

    access_token = token_response["access_token"]
    logger.warning(f"Access Token:{access_token}")
    return access_token


access_token = auto_login()
# Initialize FyersModel with obtained access token for API calls
fyers = fyersModel.FyersModel(
    client_id=CLIENT_ID, token=access_token, log_path=log_path
)
# Full access token including the client ID
full_access_token = f"{CLIENT_ID}:{access_token}"

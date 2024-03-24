from datetime import datetime, timedelta

import pyotp


def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=5)
    request.session['otp_valid_date'] = str(valid_date)
    print(otp, valid_date)
    print(f"Your one time password if {otp} is valid until {valid_date}")

import random
import time

otp_storage = {}

def send_otp(phone):
    otp = random.randint(1000, 9999)
    otp_storage[phone] = {'otp': otp, 'timestamp': time.time()}
    print(f"Sending OTP {otp} to {phone} (simulated)")

def verify_otp(phone, otp_input):
    record = otp_storage.get(phone)
    if not record:
        print("No OTP sent to this phone.")
        return False
    # Expiry 5 mins (300 seconds)
    if time.time() - record['timestamp'] > 300:
        print("OTP expired.")
        del otp_storage[phone]
        return False
    if record['otp'] == otp_input:
        print("OTP verified!")
        del otp_storage[phone]
        return True
    else:
        print("Incorrect OTP.")
        return False

# Demo
phone = input("Enter phone number: ")
send_otp(phone)
otp_input = int(input("Enter OTP: "))
verify_otp(phone, otp_input)
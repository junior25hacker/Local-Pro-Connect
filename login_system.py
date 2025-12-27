users = {
    "1234567890": {"password": "pass123", "verified": False}
}

def login_password(phone, password):
    user = users.get(phone)
    if user and user['password'] == password:
        print(f"Logged in with password as {phone}")
        return True
    print("Invalid phone or password.")
    return False

def login_otp(phone):
    send_otp(phone)
    otp_input = int(input("Enter OTP: "))
    if verify_otp(phone, otp_input):
        print(f"Logged in with OTP as {phone}")
        return True
    return False

# Demo flow
choice = input("Login with (1) Password or (2) OTP? ")
phone = input("Phone number: ")
if choice == "1":
    password = input("Password: ")
    login_password(phone, password)
elif choice == "2":
    login_otp(phone)
else:
    print("Invalid option.")
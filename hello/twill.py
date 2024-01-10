import os

from twilio.rest import Client

TWILIO_AUTH_TOKEN="aec886ce05ecc4c452fb8e2bd9d597c0"

account_sid = "AC1c212ff94e5933ca18c31a4f4ba5c8dd"
auth_token = ["aec886ce05ecc4c452fb8e2bd9d597c0"]
verify_sid = "VA7cb6a82fb856a0042ee70bef767258a6"
verified_number = "+12627702354"

client = Client(account_sid, auth_token)

print(client)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
    .create(to=verified_number, channel="sms")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_number, code=otp_code)
print(verification_check.status)
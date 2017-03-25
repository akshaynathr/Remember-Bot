from twilio.rest import TwilioRestClient

# Find these values at https://twilio.com/user/account
account_sid = "AC79a57942257a6971c9e00f018213ea13"
auth_token = "e05746ebfe373d2e2686b903608d7916"

client = TwilioRestClient(account_sid, auth_token)
t="+917012848971"


def sendSms(To,text):
    message = client.messages.create(to=To, from_="+12515817329",body=text)

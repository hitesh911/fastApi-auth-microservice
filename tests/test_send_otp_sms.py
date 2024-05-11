from preprocessor import loadProject
from dotenv import load_dotenv
load_dotenv()
loadProject()

from app.utils.third_party_apis import send_otp_sms

print(send_otp_sms("123456","73446567"))

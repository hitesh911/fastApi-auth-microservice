import requests , os

def send_otp_sms(otp:str,numbers:str):
    headers = {
        "authorization":f'{os.getenv("F2SMS_AUTHORIZATION")}',
        "Content-Type":"application/json"
        }
    body = {
        "route" : f'{os.getenv("ROUTE")}',
        "sender_id" : "MYEOTP",
        "message" : "165726",
        "variables_values" : f"{otp}",
        "numbers" : f"{numbers}",
        "flash" : 0
        }
    # saving money with dev mode 
    if(bool(int(os.getenv("DEV_MODE")))):
        return {"return":True}
    res = requests.post(os.getenv("F2SMS_URI"),json=body,headers=headers)
    return res.json()
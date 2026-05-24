from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests, base64, datetime

from starlette.staticfiles import StaticFiles


app = FastAPI()

# Point to your templates directory
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("donation.html", {"request": request})

def get_access_token(consumer_key, consumer_secret):
    auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}"
        # "Content-Type": "application/x-www-form-urlencoded"
    }
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    res = requests.get(url, headers=headers)
    return res.json()["access_token"]

class DonationRequest(BaseModel):
    amount: int
    phone_number: str

# @app.post("/donate")
# def donate(data: DonationRequest):
#     amount = data.amount
#     phone_number = data.phone_number
    # ... rest of your STK Push logic


@app.post("/donate")
def donate(data: DonationRequest):
    token = get_access_token("XIBkEqbNALALIJs1QXkeCldNxddGYtodyigMb1JEcuP9Ac90", "BvpLzWhArdNc4ZYLIrOHVvplVA8obKjdLAOHRJPv4GAv4UI55crm3haAWl3VFOyD")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    shortcode = "174379"
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": data.amount,
        "PartyA": data.phone_number,
        "PartyB": shortcode,
        "PhoneNumber": data.phone_number,
        "CallBackURL": "https://yourdomain.com/callback",
        "AccountReference": "AlphaCharity",
        "TransactionDesc": "Donation"
    }

    res = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    return res.json()


# @app.post("/donate")
# def donate(amount: int, phone_number: str):
#     token = get_access_token("XIBkEqbNALALIJs1QXkeCldNxddGYtodyigMb1JEcuP9Ac90", "BvpLzWhArdNc4ZYLIrOHVvplVA8obKjdLAOHRJPv4GAv4UI55crm3haAWl3VFOyD")
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "BusinessShortCode": "174379",
#         "Password": "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919+IgGLMmWiDuPOtyuFBGFdPgTYBMKIu4/edLRJjKa+Fc6Pb/JJhTMRPXT7rbrR8fnuKn/iJMTBE3Q3z3yCrAsP5psviSj6GDuYrqKVbYKWVoV+CcIh/fuI7vbQ5+0Hq926ZAIcH+N0Aw2yPKpzL8NT0jdE6QQ+1zuDzEqNlllaN+ILyyav2op/LkIr4MXBK0bMSfPZ5dgi47FHEv1Au4YJ152TvhPAlX0fp+SXPK6Zyc0UYi/+iz4LgNs6ni/qc0tgb1NuBuKlHsZW0xDQ6kieHePvE7guA==",
#         # "Password": base64.b64encode(f"174379{YOUR_PASSKEY}{datetime.now().strftime('%Y%m%d%H%M%S')}".encode()).decode(),
#         "Timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": amount,
#         "PartyA": phone_number,
#         "PartyB": "174379",
#         "PhoneNumber": phone_number,
#         "CallBackURL": "https://yourdomain.com/callback",
#         "AccountReference": "AlphaCharity",
#         "TransactionDesc": "Donation"
#     }
#     res = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
#     return res.json()

@app.post("/callback")
async def mpesa_callback(data: dict):
    # Handle the callback data here (e.g., save to database)
    print(data)
    return {"status": "success"}
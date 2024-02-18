import requests

def usd_to_inr(amount):
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    conversion_rate = data['rates']['INR']
    return amount * conversion_rate

def inr_to_usd(amount):
    url = "https://api.exchangerate-api.com/v4/latest/INR"
    response = requests.get(url)
    data = response.json()
    conversion_rate = data['rates']['USD']
    return amount * conversion_rate
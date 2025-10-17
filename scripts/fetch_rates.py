import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_freddie_rates():
    url = "https://www.freddiemac.com/pmms/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find rates in the HTML (adjust selectors as needed)
    rate_table = soup.find('table', {'class': 'table-rates'})
    thirty_yr = float(rate_table.find('td', text='30-Year Fixed-Rate Mortgage').find_next('td').text.strip('%'))
    
    return {
        "CONV": thirty_yr,
        "FHA": thirty_yr + 0.5,
        "ITIN": thirty_yr + 1.25,
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    rates = get_freddie_rates()
    with open('rates.json', 'w') as f:
        json.dump(rates, f, indent=2)

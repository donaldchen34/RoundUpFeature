from pathlib import Path
import plaid
import json
from datetime import date


PLAID_CLIENT_ID = ''
PLAID_SECRET = ''
PLAID_ENV = 'development'

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      environment=PLAID_ENV, api_version='2019-05-29')

def roundup(number):
    if round(number) == number:
        return 0

    x = round(number)
    if number < 250: #Round to nearest one
        rounded_num = x if x > number else x + 1
        return round(rounded_num - number,2)
    else: #Round to the nearest 5
        round_to = 5
        remainder = round_to - (x % round_to)
        rounded_num = x + remainder
        return round(rounded_num - number,2)



accountDataPath = Path('accounts.json')

if not accountDataPath.is_file():
    print("No file")

# Compare dates
Bad = ['Transfer', 'Payment', 'Financial']
save_amt = 0

with open(accountDataPath) as f:
    data = json.load(f)
    today = date.today().strftime('%Y-%m-%d')
    for account in data['accounts']:
        total_spent = 0
        if today != account['last_date_rounded_up']:
            response = client.Transactions.get(account['access_token'],
                                    start_date= account['last_date_rounded_up'],
                                    end_date= today)


            for transaction in response['transactions']:
                if not any(category in transaction['category'] for category in Bad):
                    total_spent += transaction['amount']
                    save_amt += roundup(transaction['amount'])
                    print(transaction['amount'], roundup(transaction['amount']))

        d0 = date.fromisoformat(today)
        d1 = date.fromisoformat(account['last_date_rounded_up'])

        account['last_date_rounded_up'] = today
        account['total_saved'] += round(save_amt,2)
        print('Bank account:', account['name'],
              ' Total Spent:', round(total_spent,2),
              ' Amount you should save:', round(save_amt,2),
              ' Days passed since last save:', (d0 - d1).days)


with open(accountDataPath, 'w') as outfile:
    json.dump(data, outfile, indent=4)


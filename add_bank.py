#Copyright from plaid quickstart
#Taken from https://github.com/plaid/quickstart
#add_bank.ejs is index.ejs and is also taken from plaid

import os
import plaid
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from pathlib import Path
import datetime
import dateutil.relativedelta

app = Flask(__name__)


PLAID_CLIENT_ID = ''
PLAID_SECRET = ''
PLAID_PUBLIC_KEY = ''
PLAID_ENV = 'development'
PLAID_PRODUCTS = 'transactions'

PLAID_COUNTRY_CODES = 'US,CA,GB,FR,ES'


client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      #public_key=PLAID_PUBLIC_KEY,
                      environment=PLAID_ENV, api_version='2019-05-29')

@app.route('/')
def index():
  return render_template(
    'add_bank.ejs',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    plaid_country_codes=PLAID_COUNTRY_CODES,
  )


@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    global access_token
    public_token = request.form['public_token']
    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))

    pretty_print_response(exchange_response)

    access_token = exchange_response['access_token']

    accountDataPath = Path('accounts.json')

    #Check if file exists -> If not create new file with get_accoutns
    #1   If file does exist -> check for access_token
    #2       If access_token -> exists -> cancel
    #3           else get_accounts and write and save to new json file
    #
    #   Maybe get_accounts first and check individually for each bank_name and access_token

    #1
    if not accountDataPath.is_file():
        response = client.Accounts.get(access_token)
        accounts = {'accounts': [account for account in get_accounts(response['accounts'], access_token)]}
        with open(accountDataPath, 'w') as outfile:
            json.dump(accounts,outfile,indent=4)

    #2
    access_token_found = False

    with open(accountDataPath) as f:
        data = json.load(f)
        for account in data['accounts']:
            if access_token == account['access_token']:
                access_token_found = False
                break

    #3
    if not access_token_found:
        response = client.Accounts.get(access_token)
        accounts = {'accounts': [account for account in get_accounts(response['accounts'], access_token)]}
        data['accounts'].extend(accounts['accounts'])
        with open(accountDataPath, 'w') as outfile:
            json.dump(data,outfile,indent=4)

    pretty_print_response(data)

    return jsonify(data) if data != None else jsonify(exchange_response)


@app.route('/test', methods = ['GET'])
def test():
    return jsonify({})


def get_accounts(accounts,access_token):
    response = []
    for account in accounts:
        newAccount = { 'name': account['official_name'] if account['official_name'] != None else account['name'],
                        'access_token': access_token,
                        'last_date_rounded_up': (datetime.datetime.now().date() - dateutil.relativedelta.relativedelta(
                            months=1)).strftime('%Y-%m-%d'),
                        'total_saved': 0
                    }
        response.append(newAccount)

    return response

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5555), debug= True)

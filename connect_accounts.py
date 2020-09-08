
from dotenv import load_dotenv
import os
import stripe
import time

successfulAccount = {
  'type': "custom",
  'country': "GB",
  'requested_capabilities': ["card_payments", "transfers"], # If you don't use on_behalf_of then you won't need card_payments.
  'tos_acceptance': {
    'date': int(time.time()),
    'ip': "1.1.1.1",
    'user_agent': "Chrome"
  },
  'business_type': "company",
  'business_profile': {
    'product_description': "Supplier 1",
    'mcc': 7922,
  },
  'company': {
    'name': "Subsonic",
    # // https://stripe.com/docs/connect/testing#test-verification-addresses
    'address': {
      'line1': "address_full_match", # passes address check
      'city': "London",
      'country': "GB",
      'postal_code': "E145AB",
    },
    'phone': "+447492029321",
    'tax_id': "123123123",
  },
  'external_account': {
    'object': "bank_account",
    'country': "GB",
    'currency': "GBP",
    # More account numbers for simulating payouts failing: https://stripe.com/docs/connect/testing#payouts
    'account_number': "00012345",
    'routing_number': "108800",
  }
}

ceo = {
  #  https://stripe.com/docs/connect/testing#test-verification-addresses
  'address': {
    'line1': "address_full_match", # passes address check
    'city': "London",
    'country': "GB",
    'postal_code': "E145AB",
  },
  # 1901-01-01 passes verification checks. https://stripe.com/docs/connect/testing#test-dobs
  'dob': {
    'day': 1,
    'month': 1,
    'year': 1901,
  },
  'email': "mike@brewer.com",
  'phone': "+447492029321",
  'first_name': "Mike",
  'last_name': "Brewer",
  'relationship': {
    'title': "CEO",
    'representative': True,
    'executive': True,
    'director': True,
    'owner': True,
    'percent_ownership': 100,
  }
};

# You can create accounts adhoc through the dashboard

def createUkAccount(name):
  account = stripe.Account.create(**{**successfulAccount, 'company': {**successfulAccount['company'], 'name': name}})
  stripe.Account.create_person(account.id, **ceo)
  stripe.Account.modify(account.id,
    company = {
      'directors_provided': True,
      'owners_provided': True,
      'executives_provided': True,
    },
  )
  return account

def wait_for_accounts_verified(*accounts):
  for account in accounts:
    a = stripe.Account.retrieve(account.id)
    if a['requirements']['disabled_reason']:
      time.sleep(2)
      wait_for_accounts_verified(*accounts)

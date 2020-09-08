from dotenv import load_dotenv
import os
import stripe
import time
from connect_accounts import createUkAccount, wait_for_accounts_verified

load_dotenv(dotenv_path='./.env')
stripeApiKey = os.getenv("STRIPE_API_KEY")
stripe.api_key = stripeApiKey

# In real life this is a one-off step done adhoc via the Dashboard!
supplier_1 = createUkAccount('Supplier 1')
supplier_2 = createUkAccount('Supplier 2')

# Take the payment (same as today)
payment_intent = stripe.PaymentIntent.create(
  amount = 10000,
  currency = "gbp",
  payment_method_types = ["card"],
  payment_method = "pm_card_gb", # Test card!
  confirm = True,
	# on_behalf_of=supplier_1.id     # This can be used to change the Merchant of Record to be Supplier 1.
)

def calculatePlatformMargin():
	return 300 # Your logic goes here!!

print(payment_intent)
charge_id = payment_intent['charges']['data'][0]['id']
supplier_1_transfer = stripe.Transfer.create(
	amount = 5000 - calculatePlatformMargin(),
	currency = "gbp",
	destination = supplier_1.id,
	source_transaction = charge_id # This allows you to do the transfer immediately, before the funds become 'available' in your Stripe balance
)

# Seperate charges and transfers Docs: https://stripe.com/docs/connect/charges-transfers

supplier_2_transfer = stripe.Transfer.create(
	amount = 5000 - calculatePlatformMargin(),
	currency = "gbp",
	destination = supplier_2.id,
	source_transaction = charge_id # This allows you to do the transfer immediately, before the funds become 'available' in your Stripe balance
)

# Refund supplier 2's part of the transaction
stripe.Refund.create(
  charge = charge_id,
	amount = 5000
)

# Claw back funds from supplier 2's Stripe account, since they are still there, this succeeds.
stripe.Transfer.create_reversal(
  supplier_2_transfer.id,
  amount=supplier_2_transfer.amount,
)

# Can only payout to accounts that have been fully verified (passed KYC)
wait_for_accounts_verified(supplier_1)

# Partially payout Supplier 1 to their physical bank account. This can only be done once the funds are settled.
# https://stripe.com/docs/connect/payouts
stripe.Payout.create(amount=3000, currency="gbp", stripe_account=supplier_1.id)

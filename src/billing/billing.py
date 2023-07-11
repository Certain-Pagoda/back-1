import stripe
from fastapi import Request

from os import getenv
from datetime import datetime
import uuid
from src.models.dynamoDB.users import User

stripe.api_key = getenv("STRIPE_API_KEY")

BASE_URL_MAIN = getenv("BASE_URL_MAIN")
STRIPE_WEBHOOK_SECRET = getenv("STRIPE_WEBHOOK_SECRET")

#templates = Jinja2Templates(directory="templates/stripe")

def get_price_max_resources(
        lookup_key: str
        ):
    """ parse price resource limits
    """
    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        expand=['data.product']
    )
    print(prices) 

    resource_limits = {}
    for resource in limits:
        if resource.type.endswith("_int"):
            key = resource.type[:-4]
            value = int(resource.value)
        elif resource.type.endswith("_float"):
            key = resource.type[:-6]
            value = float(resource.value)
        else:
            key = resource.type
            value = resource.value
        resource_limits[key] = value

    return resource_limits

def customer_portal(
        username: str
        ):
    """ Create a customer portal session
    """
    user = User.get(username)
    customer_id = user.customer_id
    if customer_id is None:
        raise Exception("Customer not found")

    ## Get the latest details from stripe
    customer_details = stripe.Customer.retrieve(customer_id)
    print("Customer details: ", customer_details)

    return_url = BASE_URL_MAIN
    portal_session = stripe.billing_portal.Session.create(
        customer=customer_details,
        return_url=return_url,
    )
    print("Portal session created: ", portal_session.url)
    return portal_session.url

def create_customer(
        username: str,
    ):
    """ Create a customer in stripe and add the customer to the database
    """
    user = User.get(username)
    if user is None:
        raise Exception("User not found")

    if user.customer_id is None:
        customer = stripe.Customer.create(name=user.username)
        print("\n\n------------------------------")
        print("Customer created: ", customer)
        print("\n\n------------------------------")
        
        User(username).update(actions=[
                User.customer_id.set(customer.id),
            ]
        )
    else:
        raise Exception("Customer already exists")

    return customer

def create_checkout_session(
        lookup_key: str,
        username: str,
        ):
    """ Given a lookup key, create a checkout session
    - if the user is not subcribed to any products it'll create a session for the first product
    - if the user is subcribed to a product, it'll upgrade/downgrade the subscription 
    """
    user = User.get(username)
    if user is None:
        raise Exception("User not found")
    print("User found: ", user)
    
    ## Retrieve price
    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        expand=['data.product']
    )
    print("Prices found: ", prices)

    ## Check if the customer exists and get customer data
    try:
        customer = create_customer(user.username)
        print("Customer created: ", customer)

    except Exception as e:
        customer = stripe.Customer.retrieve(user.customer_id)
        print("Customer found: ", customer)

    ## Check if the user has an active subscription
    if user.subscription_id is not None:
        ## User already has an active subscription, update it and return a customer portal url
        ## Get the subscription object from stripe to have the best info
        subscription = stripe.Subscription.retrieve(user.subscription_id)
        print(f"\n\nSubscription found: {subscription}\n\n")

        ## Update the subscription
        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=False,
            items=[
                {
                    'id': subscription['items']['data'][0].id,
                    'price': prices.data[0].id,
                },
            ],
        )
        return customer_portal(user)

    else:
        print("Subscription not found")
        ## create checkout session
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            customer = customer.id,
            success_url= BASE_URL_MAIN + '?session_id={CHECKOUT_SESSION_ID}',
            allow_promotion_codes=True
        )

        print("Checkout session created: ", checkout_session.url)
        print("Checkout session created: ", checkout_session)

        return checkout_session.url

def process_price(event):
    """ Process a new proce creation webhook
    - this is a rare event that runs only when a new price is created/updated/deleted
    - Plans max resources are set via the metadata field in the stripe dashboard

    TODO: process the incoming proce and modify on the fly all limits to users instead of saving all in the database
    """
     
    print("--------------- Processing price created event---------------")
    event_data = event['data']['object']
    product = event_data['product']
    
    stripe_prices = stripe.Price.list(product=product)
    print("Prices in stripe: ", len(stripe_prices.data))
    
    ## Sync product prices
    for price in stripe_prices.data:
        print("Processing price: ", price['id'])
        ## Create a limits dict

    ## Scan all users and update the limits
    return True

def process_customer(event):
    """ process Client creation, update, delte
    """ 
    print("--------------- Processing client event---------------")
    customer_data = event['data']['object']
    
    ## Check if the customer already exists
    user = [u for u in User.scan(User.customer_id == customer_data['id'])]
    if len(user) == 0:
        print("Customer not found in database")
        raise Exception("Customer not found in database")
    
    ## Setup customer info in the user document

    #if customer is None:
    #    print("Customer not found in database")
    #    customer = Customers(
    #            id=customer_data['id'],
    #            created_at=datetime.fromtimestamp(customer_data['created']),
    #            )
    #    ses.add(customer)
    #    
    #else:
    #    print("Customer already exists in database")

    #ses.commit()
    return True

def process_subscription(event):

    print("--------------- Processing subscription event---------------")
    print("Event: ", event)

    event_data = event['data']['object']
    customer_id = event_data['customer']
    user = [u for u in User.scan(User.customer_id == customer_id)]
    if len(user) != 1:
        print("Customer not found or multiple customers found in database")
        raise Exception("Customer not found or multiple customers found in database")

    user = user[0]
    ## This model does not allow a user to have more than one subscription
    ## Setup so the user always keeps the latest subscription
    #customer_subscriptions = stripe.Subscription.list(customer=user.billing_customer_id, status='all')
    customer_subscriptions = stripe.Subscription.list(customer=user.customer_id, status='all')
    
    ## Process all subscriptions
    for sub in customer_subscriptions:
        print("Processing subscription: ", sub['id'])
        ## Single item subscriptions always
        price = sub['items']['data'][0]['price']
        
        ##Update user
        User(user.username).update(actions=[
            User.subscription_id.set(sub['id']),
            User.subscription_status.set(sub['status']),
            User.subscription_created_at.set(datetime.fromtimestamp(sub['created'])),
            User.subscription_current_period_start.set(datetime.fromtimestamp(sub['current_period_start'])),
            User.subscription_current_period_end.set(datetime.fromtimestamp(sub['current_period_end'])),
            ]
        )

    return True

async def stripe_webhook(
        request: Request,
        stripe_signature: str, 
    ):
    """ Stripe webhook endpoint
    """
    print(f"----------------- Webhook received -----------------")
    webhook_secret = STRIPE_WEBHOOK_SECRET
    try:
        request_data = await request.body()

    except Exception as e:
        print(e)
        raise Exception("Invalid payload")

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        if stripe_signature is None:
            raise Exception("Message not signed")

        print("Stripe signature: ", stripe_signature)
        event = stripe.Webhook.construct_event(
        payload=request_data, sig_header=stripe_signature, secret=webhook_secret)
        data = event['data']

        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']

    else:
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']
    print('------> event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')

    elif event_type == 'customer.created':
        print('Customer created')
        process_customer(event)

    elif event_type == 'customer.updated':
        print('Customer created')
        process_customer(event)

    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
        print('Subscription created %s', event)
        process_subscription(event)

    elif event_type == 'customer.subscription.updated':
        print('Subscription updated %s', event.id)
        process_subscription(event)

    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        print('Subscription deleted: %s', event.id)
        process_subscription(event)
        
    elif event_type == 'price.created':
        print('Price created: %s', event.id)
        process_price(event)

    elif event_type == 'price.updated':
        print('Price updated: %s', event.id)
        process_price(event)

    elif event_type == 'price.deleted':
        print('Price deleted: %s', event.id)
        process_price(event)

    return {'status': 'success'}

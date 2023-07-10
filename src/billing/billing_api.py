from fastapi import FastAPI, Depends, APIRouter, HTTPException, Request, BackgroundTasks, Header
import json
from src.auth.auth_functions import get_current_user

from src.billing.billing import stripe_webhook, create_checkout_session

router = APIRouter(
        tags=["billing"],
        )

@router.post("/billing/stripe/webhook")
async def POST_stripe_webhook(
        request: Request,
        stripe_signature: str = Header(default=None), 
    ):
    """ Get chekcout page for stripe
    """
    return await stripe_webhook(request, stripe_signature)

@router.get("/billing/stripe/checkout")
def GET_stripe_checkout(
        user = Depends(get_current_user)
        ):
    """ Get chekcout page for stripe
    """
    price_lookup_key = "1_EURO_PLAN"
    return create_checkout_session(price_lookup_key, user.username)
